#!/usr/bin/env python3
"""legobuild : numéro de set -> modèle à construire avec les briques et couleurs de CE set (aucune pièce en plus).

Pour les boîtes de briques en vrac (ex. 10698) qui n'ont pas de modèle LDraw : on choisit une forme (sphère, cône, cylindre,
tore, pyramide, ou un STL/OBJ), l'outil cherche la plus grande taille réalisable avec l'inventaire, la monte brique par brique
(joints décalés), répartit les couleurs, puis écrit :
  modele.ldr                  modèle LDraw (une étape par rangée de briques)
  notice.html / notice.pdf    notice de montage (legonotice.py)
  pieces_utilisees.csv, pieces_restantes.csv
  kit/<Couleur>/*.3mf, *.stl  plateaux d'impression des seules pièces utilisées (legoprint.py)
Usage : python3 legobuild.py 10698 --shape sphere --out build_10698/
"""
import argparse, colorsys, csv, math, os, sys
from collections import Counter, defaultdict
import numpy as np
import legokit as K, legoset as S

LDU, LDU_H = 20, 24                                   # pas et hauteur de brique en unités LDraw

def top_colors(inv, n, trans=False):
    """Noms des n couleurs les plus abondantes en briques (en cellules). n=0 : toutes."""
    cells = Counter()
    for r in inv:
        if r['type'] == 'Brick' and r['imprimable'] == 'oui' and (trans or not r['transparent']):
            a, b = map(int, r['plots'].split('x')); cells[r['couleur'].lower()] += a * b * r['quantite']
    return {c for c, _ in cells.most_common(n or None)}

def supply_from(inv, colors=None):
    """-> {(a,b): {(couleur, color_id, rgb, part_num): quantité}} pour les briques (a <= b)."""
    sup = defaultdict(dict)
    for r in inv:
        if r['type'] != 'Brick' or r['imprimable'] != 'oui': continue
        if colors and r['couleur'].lower() not in colors: continue
        a, b = map(int, r['plots'].split('x'))
        key = (r['couleur'], r['color_id'], r['rgb'], r['part_num'])
        sup[(a, b)][key] = sup[(a, b)].get(key, 0) + r['quantite']
    return sup

def pack_layer_limited(mask, parity, count):
    """Glouton comme legokit.pack_layer mais avec un stock par taille. -> (briques, nb de cellules non couvertes)."""
    if parity:
        L, miss = pack_layer_limited(mask.T, 0, count)
        return [(j, i, d, w) for i, j, w, d in L], miss
    nx, ny = mask.shape
    free = mask.copy(); out, miss = [], 0
    sizes = sorted({(a, b) for a, b in count}, key=lambda s: -s[0] * s[1])
    cands = [c for s in sizes for c in ((s, s[::-1]) if s[0] != s[1] else (s,))]
    cands.sort(key=lambda c: (-c[0] * c[1], c[0] < c[1]))
    for j in range(ny):
        for i in range(nx):
            if not free[i, j]: continue
            for w, d in cands:
                key = (min(w, d), max(w, d))
                if count[key] > 0 and i + w <= nx and j + d <= ny and free[i:i+w, j:j+d].all():
                    free[i:i+w, j:j+d] = False; out.append((i, j, w, d)); count[key] -= 1; break
            else:
                free[i, j] = False; miss += 1
    return out, miss

def plan(vox, sup):
    """Monte `vox` avec le stock. -> (couches, cellules manquantes). Les briques flottantes sont retirées."""
    count = {s: sum(q.values()) for s, q in sup.items()}
    count = Counter(count)
    layers, miss = [], 0
    for k in range(vox.shape[2]):
        L, m = pack_layer_limited(vox[:, :, k], k % 2, count)
        layers.append([(i, j, k, w, d) for i, j, w, d in L]); miss += m
    return layers, miss

def palette(sup):
    """Couleurs triées pour former un dégradé vertical : teintes d'abord, puis neutres du clair au sombre."""
    cols = {}
    for q in sup.values():
        for (name, cid, rgb, pn) in q: cols[name] = rgb
    def key(item):
        r, g, b = (int(item[1][i:i+2], 16) / 255 for i in (0, 2, 4))
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        return (1, -v, 0) if s < 0.18 else (0, h, -v)
    return [n for n, _ in sorted(cols.items(), key=key)]

def assign_colors(layers, sup, nz):
    """Une couleur par brique : bande de hauteur voulue, sinon la couleur la plus proche encore en stock pour cette taille."""
    pal = palette(sup); idx = {n: i for i, n in enumerate(pal)}
    rem = {s: dict(q) for s, q in sup.items()}
    out = []
    for L in layers:
        row = []
        for (i, j, k, w, d) in L:
            s = (min(w, d), max(w, d))
            target = (k + .5) / nz * len(pal)
            key = min((c for c, n in rem[s].items() if n > 0), key=lambda c: (abs(idx[c[0]] + .5 - target), -rem[s][c]))
            rem[s][key] -= 1; row.append((i, j, k, w, d, key))
        out.append(row)
    return out, rem

def ldraw_color(lib, color_id, rgb):
    """Code LDraw de la couleur : l'id Rebrickable s'il désigne la même teinte dans LDConfig, sinon couleur directe."""
    want = tuple(int(rgb[i:i+2], 16) for i in (0, 2, 4))
    if lib is not None:
        near = lambda c: tuple(round(255 * x) for x in c[0]) == want
        if color_id in lib.colors and near(lib.colors[color_id]): return color_id
        for code, c in lib.colors.items():
            if near(c): return code
    return 0x2000000 + int(rgb, 16)

def write_ldr(path, layers, nx, ny, lib, title, chunk=10):
    lines = [f'0 {title}', f'0 Name: {os.path.basename(path)}', '0 Author: legokit', '0 !LICENSE Not redistributable']
    for row in layers:
        for n in range(0, len(row), chunk):
            for (i, j, k, w, d, (name, cid, rgb, pn)) in row[n:n + chunk]:
                x, z, y = (i + w / 2) * LDU, (j + d / 2) * LDU, -LDU_H * (k + 1)
                rot = '1 0 0 0 1 0 0 0 1' if w >= d else '0 0 1 0 1 0 -1 0 0'
                lines.append(f'1 {ldraw_color(lib, cid, rgb)} {x:g} {y:g} {z:g} {rot} {pn}.dat')
            lines.append('0 STEP')
    open(path, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')

def csv_rows(path, rows):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(['couleur', 'piece', 'plots', 'quantite']); w.writerows(rows)

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('set'); ap.add_argument('--out'); ap.add_argument('--cache')
    ap.add_argument('--shape', default='sphere', choices=['sphere', 'cone', 'cylinder', 'torus', 'pyramid'])
    ap.add_argument('--model', help='STL/OBJ à reproduire au lieu d\'une forme (Z = haut)')
    ap.add_argument('--width', type=int, default=40, help='largeur maximale testée, en plots (la taille réalisable est cherchée vers le bas)')
    ap.add_argument('--colors', help='couleurs autorisées, séparées par des virgules (remplace le choix automatique)')
    ap.add_argument('--max-colors', type=int, default=8, help='nombre de couleurs retenues, les plus abondantes (0 = toutes ; défaut 8)')
    ap.add_argument('--trans', action='store_true', help='autoriser les couleurs transparentes')
    ap.add_argument('--ldraw', help='complete.zip LDraw (sinon téléchargé dans le cache) ; sert à la notice')
    ap.add_argument('--bed', type=float, nargs=2, default=[256, 256]); ap.add_argument('--tol', type=float, default=0.1)
    ap.add_argument('--no-notice', action='store_true'); ap.add_argument('--no-print', action='store_true')
    ap.add_argument('--pdf', action='store_true', help='exporte aussi notice.pdf (Chrome/Chromium)')
    a = ap.parse_args()
    cache = S.cache_dir(a.cache); s = S.find_set(cache, a.set)
    if not s: raise SystemExit(f'set {a.set} introuvable')
    inv = S.inventory(cache, s['set_num'])
    want = {c.strip().lower() for c in a.colors.split(',')} if a.colors else top_colors(inv, a.max_colors, a.trans)
    sup = supply_from(inv, want)
    cells = sum(x * y * sum(q.values()) for (x, y), q in sup.items())
    if not cells: raise SystemExit('aucune brique utilisable dans cet inventaire')
    mesh = K.read_mesh(a.model) if a.model else None
    best = None
    for W in range(a.width, 3, -1):
        vox = K.voxelize_mesh(mesh, W) if mesh is not None else K.shape_voxels(a.shape, W)
        if vox.sum() > cells: continue
        layers, miss = plan(vox, sup)
        if miss: continue
        layers, dropped = K.prune_floating(layers)
        if dropped > 0.1 * sum(map(len, layers)) + 2: continue
        best = (W, vox, layers, dropped); break
    if not best: raise SystemExit('aucune taille réalisable avec cet inventaire')
    W, vox, layers, dropped = best
    colored, rem = assign_colors(layers, sup, vox.shape[2])
    out = a.out or 'build_' + s['set_num']; os.makedirs(out, exist_ok=True)
    lib = None
    if not a.no_notice:
        import legonotice as N
        lib = N.get_library(a.ldraw, cache)
    title = f"{s['set_num']} {s['name']} - {a.model and os.path.basename(a.model) or a.shape} {vox.shape[0]}x{vox.shape[1]}x{vox.shape[2]}"
    write_ldr(f'{out}/modele.ldr', colored, vox.shape[0], vox.shape[1], lib, title)
    used = Counter((key[0], key[3], f'{min(w, d)}x{max(w, d)}') for row in colored for (_, _, _, w, d, key) in row)
    csv_rows(f'{out}/pieces_utilisees.csv', sorted((c, p, z, n) for (c, p, z), n in used.items()))
    csv_rows(f'{out}/pieces_restantes.csv', sorted((k[0], k[3], f'{x}x{y}', n) for (x, y), q in rem.items() for k, n in q.items() if n > 0))
    nb = sum(used.values())
    print(f"{title}\n  {nb} briques sur {sum(sum(q.values()) for q in sup.values())} disponibles, "
          f"{len({c for c, _, _ in used})} couleurs, {vox.shape[2]} rangées" + (f', {dropped} brique(s) flottante(s) retirée(s)' if dropped else ''))
    if not a.no_print:
        import legoprint as P
        rows = [dict(couleur=c, rgb=next(r['rgb'] for r in inv if r['couleur'] == c), quantite=n, imprimable='oui', type='Brick', plots=z)
                for (c, p, z), n in used.items()]
        res = P.print_kit(rows, f'{out}/kit', tuple(a.bed), a.tol, quiet=True)
        print(f"  kit à imprimer : {res['plates']} plateaux -> {out}/kit/")
    if not a.no_notice:
        text = open(f'{out}/modele.ldr', encoding='utf-8').read()
        models, first, custom = N.parse_model(text)
        ns, ni, nm, size = N.write_notice(f'{out}/notice.html', models, first, lib, title, custom)
        print(f'  notice : {ns} étapes -> {out}/notice.html')
        if a.pdf: N.export_pdf(f'{out}/notice.html', f'{out}/notice.pdf'); print(f'  PDF -> {out}/notice.pdf')

if __name__ == '__main__':
    main()
