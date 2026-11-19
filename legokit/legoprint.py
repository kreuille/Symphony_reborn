#!/usr/bin/env python3
"""legoprint : numéro de set LEGO -> STL et 3MF prêts à trancher (Bambu Studio), un jeu de plateaux par couleur.

Pièces gérées : Brick / Plate / Tile N x M (voir legoset.py). Les autres pièces du set sont listées mais pas générées.
Usage : python3 legoprint.py 10698 --out kit_10698/ [--bed 256 256] [--tol 0.1] [--colors "Black,Red"]
"""
import argparse, csv, io, os, re, zipfile
from collections import defaultdict
import numpy as np
import legokit as K, legoset as S

PLATE_H = 3.2
KIND = {'Brick': (K.BRICK_H, True), 'Plate': (PLATE_H, True), 'Tile': (PLATE_H, False)}   # hauteur, plots

def piece_shells(kind, w, d, tol):
    h, studs = KIND[kind]
    return K.brick_shells(d, w, tol, studs, h)        # grand côté (d) le long de X

def layout(items, bed, gap=3.0, margin=5.0):
    """items : [(kind, w, d)] avec w <= d. Rangement en étagères. -> liste de plateaux, chacun [(item, x, y)]."""
    items = sorted(items, key=lambda it: (-it[1], -it[2], it[0]))
    plates, cur, x, y, rowh = [], [], margin, margin, 0.0
    for it in items:
        W, D = it[2] * K.PITCH, it[1] * K.PITCH
        if x + W > bed[0] - margin: x, y, rowh = margin, y + rowh + gap, 0.0
        if y + D > bed[1] - margin:
            plates.append(cur); cur, x, y, rowh = [], margin, margin, 0.0
        cur.append((it, x, y)); x += W + gap; rowh = max(rowh, D)
    if cur: plates.append(cur)
    return plates

def _fmt(v): return f'{v:.4f}'.rstrip('0').rstrip('.')

def write_3mf(path, plate, color_name, rgb, tol):
    """Un objet par type de pièce (volumes fermés indépendants), un item par exemplaire placé sur le plateau."""
    cache, objs, items = {}, [], []
    for (kind, w, d), x, y in plate:
        if (kind, w, d) not in cache:
            oid = len(cache) + 2; cache[(kind, w, d)] = oid
            V, T = [], []
            for shell in piece_shells(kind, w, d, tol):          # sommets fusionnés shell par shell
                u, inv = np.unique(np.round(shell.reshape(-1, 3), 5), axis=0, return_inverse=True)
                T += (inv.reshape(-1, 3) + len(V)).tolist(); V += u.tolist()
            v = ''.join(f'<vertex x="{_fmt(a)}" y="{_fmt(b)}" z="{_fmt(c)}"/>' for a, b, c in V)
            t = ''.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in T)
            objs.append(f'<object id="{oid}" type="model" pid="1" pindex="0" name="{kind} {w}x{d}">'
                        f'<mesh><vertices>{v}</vertices><triangles>{t}</triangles></mesh></object>')
        items.append(f'<item objectid="{cache[(kind, w, d)]}" transform="1 0 0 0 1 0 0 0 1 {_fmt(x)} {_fmt(y)} 0"/>')
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
    tris = [np.concatenate(piece_shells(*it, tol)) + [x, y, 0] for it, x, y in plate]
    K.write_stl(path, np.concatenate(tris))

def slug(s): return re.sub(r'[^A-Za-z0-9]+', '_', s).strip('_')

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('set'); ap.add_argument('--out'); ap.add_argument('--cache')
    ap.add_argument('--bed', type=float, nargs=2, default=[256, 256], metavar=('X', 'Y'), help='plateau en mm (X1/P1/A1 : 256 256 ; A1 mini : 180 180)')
    ap.add_argument('--tol', type=float, default=0.1, help='jeu par côté en mm')
    ap.add_argument('--colors', help='couleurs à générer, séparées par des virgules (défaut : toutes)')
    ap.add_argument('--spares', action='store_true')
    a = ap.parse_args()
    cache = S.cache_dir(a.cache); s = S.find_set(cache, a.set)
    if not s: raise SystemExit(f'set {a.set} introuvable')
    inv = S.inventory(cache, s['set_num'], a.spares)
    out = a.out or 'kit_' + s['set_num']
    want = {c.strip().lower() for c in a.colors.split(',')} if a.colors else None
    rows, total_plates = print_kit(inv, out, tuple(a.bed), a.tol, want)
    skipped = sum(r['quantite'] for r in inv if r['imprimable'] != 'oui')
    print(f"\n{s['set_num']} {s['name']} : {sum(r[1] for r in rows)} pièces générées sur {total_plates} plateaux ; "
          f'{skipped} pièces non gérées (voir legoset.py) -> {out}/')

def print_kit(inv, out, bed, tol, want=None, quiet=False):
    """inv : lignes d'inventaire (voir legoset.inventory) ; écrit un dossier par couleur. -> (résumé par couleur, nb de plateaux)."""
    os.makedirs(out, exist_ok=True)
    by = defaultdict(list)
    for r in inv:
        if r['imprimable'] == 'oui' and (not want or r['couleur'].lower() in want): by[r['couleur']].append(r)
    rows, total_plates = [], 0
    for color, L in sorted(by.items()):
        items = [(r['type'], *map(int, r['plots'].split('x'))) for r in L for _ in range(r['quantite'])]
        plates = layout(items, tuple(bed))
        d = f'{out}/{slug(color)}'; os.makedirs(d, exist_ok=True)
        for n, p in enumerate(plates, 1):
            write_3mf(f'{d}/{slug(color)}_{n:02d}.3mf', p, color, L[0]['rgb'], tol)
            write_plate_stl(f'{d}/{slug(color)}_{n:02d}.stl', p, tol)
        total_plates += len(plates); rows.append((color, len(items), len(plates)))
        if not quiet: print(f'{color:<22} {len(items):>4} pièces -> {len(plates)} plateau(x)')
    with open(f'{out}/resume.csv', 'w', newline='', encoding='utf-8') as f:
        c = csv.writer(f); c.writerow(['couleur', 'pieces', 'plateaux']); c.writerows(rows)
    return rows, total_plates

if __name__ == '__main__':
    main()
