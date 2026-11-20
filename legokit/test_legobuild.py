"""Tests hors ligne : python3 test_legobuild.py"""
import os, tempfile
from collections import Counter
import numpy as np
import legobuild as B, legokit as K, legonotice as N

def row(color, rgb, size, q, cid=0, trans=False, pn='3001'):
    return dict(couleur=color, color_id=cid, rgb=rgb, transparent=trans, part_num=pn, nom='Brick', quantite=q,
                imprimable='oui', type='Brick', plots=size)

INV = [row('Red', 'C91A09', '2x4', 30, 4, pn='3001'), row('Blue', '0055BF', '2x4', 30, 1, pn='3001'),
       row('Red', 'C91A09', '1x2', 30, 4, pn='3004'), row('Blue', '0055BF', '1x1', 20, 1, pn='3005'),
       row('Clear', 'FCFCFC', '2x2', 50, 47, True, '3003'), dict(row('Red', 'C91A09', '1x2', 5), type='Plate')]

def test_top_colors_and_supply():
    assert B.top_colors(INV, 1) == {'red'} or B.top_colors(INV, 1) == {'blue'}
    assert 'clear' not in B.top_colors(INV, 0) and 'clear' in B.top_colors(INV, 0, True)
    sup = B.supply_from(INV, {'red', 'blue'})
    assert set(sup) == {(2, 4), (1, 2), (1, 1)} and sum(sup[(2, 4)].values()) == 60      # plaques exclues

def test_plan_respects_stock_and_covers():
    sup = B.supply_from(INV, {'red', 'blue'})
    vox = K.shape_voxels('cylinder', 6)
    layers, miss = B.plan(vox, sup)
    assert miss == 0
    used = Counter((min(w, d), max(w, d)) for L in layers for *_, w, d in L)
    assert all(used[s] <= sum(sup[s].values()) for s in used)
    for k, L in enumerate(layers):
        cover = np.zeros(vox.shape[:2], int)
        for i, j, _, w, d in L: cover[i:i+w, j:j+d] += 1
        assert (cover == vox[:, :, k]).all()
    assert B.plan(K.shape_voxels('cylinder', 30), sup)[1] > 0          # trop grand pour le stock -> cellules manquantes

def test_colors_within_stock_and_ldr():
    sup = B.supply_from(INV, {'red', 'blue'})
    layers, _ = B.plan(K.shape_voxels('cylinder', 6), sup)
    layers, _ = K.prune_floating(layers)
    colored, rem = B.assign_colors(layers, sup, len(layers))
    assert all(n >= 0 for q in rem.values() for n in q.values())
    assert {key[0] for row_ in colored for *_, key in row_} == {'Red', 'Blue'}      # dégradé : les deux couleurs servent
    with tempfile.TemporaryDirectory() as d:
        B.write_ldr(f'{d}/m.ldr', colored, 6, 6, None, 'test', chunk=4)
        txt = open(f'{d}/m.ldr').read().splitlines()
        parts = [l.split() for l in txt if l.startswith('1 ')]
        assert len(parts) == sum(map(len, colored)) and all(p[-1].endswith('.dat') for p in parts)
        assert any(p[1] == '38510410' or int(p[1]) >= 0x2000000 for p in parts)    # lib absente -> couleur directe
        assert {p[3] for p in parts} >= {'-24', '-48'}                              # hauteur de rangée 24 LDU
        models, first, custom = N.parse_model('\n'.join(txt))
        steps = []; N.expand(models, first, np.eye(4), 15, steps)
        assert sum(map(len, steps)) == len(parts) and max(map(len, steps)) <= 4     # une étape par paquet de briques
        assert abs(steps[0][0][1][1, 3] + 24) < 1e-9                                # 1re rangée : origine à y=-24

def test_ldraw_color_mapping():
    class Lib: colors = {4: ((201/255, 26/255, 9/255), 1.0), 71: ((0.5, 0.5, 0.5), 1.0)}
    assert B.ldraw_color(Lib, 4, 'C91A09') == 4                       # id Rebrickable = code LDraw, même teinte
    assert B.ldraw_color(Lib, 999, 'C91A09') == 4                     # id différent mais teinte identique
    assert B.ldraw_color(Lib, 4, '123456') == 0x2000000 + 0x123456    # sinon couleur directe

if __name__ == '__main__':
    for n, f in list(globals().items()):
        if n.startswith('test_'): f(); print('ok', n)
