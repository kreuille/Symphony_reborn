#!/usr/bin/env python3
"""legoprint : numéro de set LEGO -> STL et 3MF prêts à trancher (Bambu Studio), un jeu de plateaux par couleur.

Pièces gérées : Brick / Plate / Tile N x M (voir legoset.py). Les autres pièces du set sont listées mais pas générées.
Usage : python3 legoprint.py 10698 --out kit_10698/ [--bed 256 256] [--tol 0.1] [--colors "Black,Red"]
"""
import argparse, csv, io, os, re, zipfile
from collections import defaultdict
import numpy as np
import legokit as K, legoset as S, legopart as LP

PLATE_H = 3.2
KIND = {'Brick': (K.BRICK_H, True), 'Plate': (PLATE_H, True), 'Tile': (PLATE_H, False)}   # hauteur, plots

def piece_shells(kind, w, d, tol):
    h, studs = KIND[kind]
    return K.brick_shells(d, w, tol, studs, h)        # grand côté (d) le long de X

class Piece:
    """Pièce prête à poser sur un plateau : emprise W x D (mm), volumes fermés (`shells`) et nom."""
    def __init__(self, key, name, W, D, shells):
        self.key, self.name, self.W, self.D, self._shells = key, name, W, D, shells
    def shells(self):
        if callable(self._shells): self._shells = self._shells()
        return self._shells

def as_piece(it, tol=0.1):
    """(type, w, d) -> Piece paramétrique ; une Piece est renvoyée telle quelle."""
    if isinstance(it, Piece): return it
    kind, w, d = it
    return Piece(f'{kind} {w}x{d}', f'{kind} {w}x{d}', d * K.PITCH, w * K.PITCH, lambda: piece_shells(kind, w, d, tol))

def ldraw_piece(lib, part_num, name, tol, relations=None):
    """Piece issue de la géométrie LDraw, ou None (absente de la bibliothèque, ou non imprimable)."""
    ref = LP.resolve(lib, part_num, relations)
    T = LP.ldraw_mesh(lib, ref, name, tol) if ref else None
    if T is None: return None
    return Piece(f'{part_num}', f'{part_num} {name}'[:60], float(T[:, :, 0].max()), float(T[:, :, 1].max()), [T])

def layout(items, bed, gap=3.0, margin=5.0):
    """items : tuples (type, w, d) ou Piece. Rangement en étagères. -> liste de plateaux, chacun [(Piece, x, y)]."""
    items = sorted((as_piece(it) for it in items), key=lambda it: (-it.D, -it.W, it.key))
    for it in items:
        if it.W > bed[0] - 2 * margin or it.D > bed[1] - 2 * margin:
            raise ValueError(f'{it.name} ({it.W:.0f} x {it.D:.0f} mm) est plus grande que le plateau')
    plates, cur, x, y, rowh = [], [], margin, margin, 0.0
    for it in items:
        if x + it.W > bed[0] - margin: x, y, rowh = margin, y + rowh + gap, 0.0
        if y + it.D > bed[1] - margin:
            plates.append(cur); cur, x, y, rowh = [], margin, margin, 0.0
        cur.append((it, x, y)); x += it.W + gap; rowh = max(rowh, it.D)
    if cur: plates.append(cur)
    return plates

def _fmt(v): return f'{v:.4f}'.rstrip('0').rstrip('.')

def write_3mf(path, plate, color_name, rgb, tol):
    """Un objet par type de pièce (volumes fermés indépendants), un item par exemplaire placé sur le plateau."""
    cache, objs, items = {}, [], []
    for it, x, y in plate:
        pc = as_piece(it, tol)
        if pc.key not in cache:
            oid = len(cache) + 2; cache[pc.key] = oid
            V, T = [], []
            for shell in pc.shells():                            # sommets fusionnés shell par shell
                u, inv = np.unique(np.round(shell.reshape(-1, 3), 5), axis=0, return_inverse=True)
                T += (inv.reshape(-1, 3) + len(V)).tolist(); V += u.tolist()
            v = ''.join(f'<vertex x="{_fmt(a)}" y="{_fmt(b)}" z="{_fmt(c)}"/>' for a, b, c in V)
            t = ''.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in T)
            nm = pc.name.replace('&', '&amp;').replace('<', '&lt;').replace('"', '&quot;')
            objs.append(f'<object id="{oid}" type="model" pid="1" pindex="0" name="{nm}">'
                        f'<mesh><vertices>{v}</vertices><triangles>{t}</triangles></mesh></object>')
        items.append(f'<item objectid="{cache[pc.key]}" transform="1 0 0 0 1 0 0 0 1 {_fmt(x)} {_fmt(y)} 0"/>')
    model = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><resources>'
             f'<basematerials id="1"><base name="{color_name}" displaycolor="#{rgb}"/></basematerials>'
             + ''.join(objs) + '</resources><build>' + ''.join(items) + '</build></model>')
    ct = ('<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', ct); z.writestr('_rels/.rels', rels); z.writestr('3D/3dmodel.model', model)

def write_plate_stl(path, plate, tol):
    tris = [np.concatenate(as_piece(it, tol).shells()) + [x, y, 0] for it, x, y in plate]
    K.write_stl(path, np.concatenate(tris))

def slug(s): return re.sub(r'[^A-Za-z0-9]+', '_', s).strip('_')

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('set'); ap.add_argument('--out'); ap.add_argument('--cache')
    ap.add_argument('--bed', type=float, nargs=2, default=[256, 256], metavar=('X', 'Y'), help='plateau en mm (X1/P1/A1 : 256 256 ; A1 mini : 180 180)')
    ap.add_argument('--tol', type=float, default=0.1, help='jeu par côté en mm')
    ap.add_argument('--colors', help='couleurs à générer, séparées par des virgules (défaut : toutes)')
    ap.add_argument('--spares', action='store_true')
    ap.add_argument('--ldraw', help='complete.zip LDraw (sinon téléchargé dans le cache, ~150 Mo)')
    ap.add_argument('--no-ldraw', action='store_true', help='seulement briques/plaques/tuiles paramétriques (pas de pentes ni de pièces spéciales)')
    a = ap.parse_args()
    cache = S.cache_dir(a.cache); s = S.find_set(cache, a.set)
    if not s: raise SystemExit(f'set {a.set} introuvable')
    inv = S.inventory(cache, s['set_num'], a.spares)
    out = a.out or 'kit_' + s['set_num']
    want = {c.strip().lower() for c in a.colors.split(',')} if a.colors else None
    lib = rel = None
    if not a.no_ldraw:
        import legonotice as N
        lib = N.get_library(a.ldraw, cache); rel = S.relations(cache)
    res = print_kit(inv, out, tuple(a.bed), a.tol, want, lib=lib, relations=rel)
    tot = sum(r['quantite'] for r in inv if not want or r['couleur'].lower() in want)
    print(f"\n{s['set_num']} {s['name']} : {tot} pièces dans l'inventaire\n"
          f"  {res['param']} paramétriques + {res['ldraw']} depuis LDraw = {res['param'] + res['ldraw']} générées sur {res['plates']} plateaux -> {out}/")
    for pn, nm, q, why in res['skipped']: print(f'  non générée : {q} x {pn} {nm} ({why})')

def print_kit(inv, out, bed, tol, want=None, quiet=False, lib=None, relations=None):
    """inv : lignes d'inventaire (voir legoset.inventory) ; écrit un dossier par couleur.
    Briques/plaques/tuiles simples : formes paramétriques ; autres pièces : géométrie LDraw si `lib` est fourni.
    -> dict(rows=[(couleur, pièces, plateaux)], plates, param, ldraw, skipped=[(pièce, nom, quantité, raison)])."""
    os.makedirs(out, exist_ok=True)
    by = defaultdict(list)
    for r in inv:
        if not want or r['couleur'].lower() in want: by[r['couleur']].append(r)
    rows, total_plates, n_param, n_ld, skipped, cache = [], 0, 0, 0, [], {}
    for color, L in sorted(by.items()):
        items = []
        for r in L:
            if r['imprimable'] == 'oui':
                pc = as_piece((r['type'], *map(int, r['plots'].split('x'))), tol); n_param += r['quantite']
            else:
                why = LP.printable_kind(r['nom'])
                if why: skipped.append((r['part_num'], r['nom'], r['quantite'], why)); continue
                if lib is None: skipped.append((r['part_num'], r['nom'], r['quantite'], 'sans LDraw')); continue
                if r['part_num'] not in cache: cache[r['part_num']] = ldraw_piece(lib, r['part_num'], r['nom'], tol, relations)
                pc = cache[r['part_num']]
                if pc is None: skipped.append((r['part_num'], r['nom'], r['quantite'], 'absente de LDraw')); continue
                n_ld += r['quantite']
            items += [pc] * r['quantite']
        if not items: continue
        try: plates = layout(items, tuple(bed))
        except ValueError as e: skipped.append((color, str(e), 1, 'trop grande')); continue
        d = f'{out}/{slug(color)}'; os.makedirs(d, exist_ok=True)
        for n, p in enumerate(plates, 1):
            write_3mf(f'{d}/{slug(color)}_{n:02d}.3mf', p, color, L[0]['rgb'], tol)
            write_plate_stl(f'{d}/{slug(color)}_{n:02d}.stl', p, tol)
        total_plates += len(plates); rows.append((color, len(items), len(plates)))
        if not quiet: print(f'{color:<22} {len(items):>4} pièces -> {len(plates)} plateau(x)')
    with open(f'{out}/resume.csv', 'w', newline='', encoding='utf-8') as f:
        c = csv.writer(f); c.writerow(['couleur', 'pieces', 'plateaux']); c.writerows(rows)
    if skipped:
        with open(f'{out}/non_generees.csv', 'w', newline='', encoding='utf-8') as f:
            c = csv.writer(f); c.writerow(['piece', 'nom', 'quantite', 'raison']); c.writerows(skipped)
    return dict(rows=rows, plates=total_plates, param=n_param, ldraw=n_ld, skipped=skipped)

if __name__ == '__main__':
    main()
