"""Tests : python3 test_legokit.py"""
import os, tempfile
from collections import Counter
import numpy as np
import legokit as L

def watertight(t):
    e = Counter()
    for tri in np.round(t, 4):
        for a, b in ((0, 1), (1, 2), (2, 0)): e[(tuple(tri[a]), tuple(tri[b]))] += 1
    return all(n == 1 and e.get((b, a), 0) == 1 for (a, b), n in e.items())

def test_primitives_closed():
    assert watertight(L._box(0, 0, 0, 1, 2, 3))
    assert watertight(L._tube(0, 0, 0, 1, 2)) and watertight(L._tube(0, 0, 0, 1, 2, 1))

def test_brick_dimensions():
    m = L.brick_mesh(2, 4, tol=0.1).reshape(-1, 3)
    lo, hi = m.min(0), m.max(0)
    assert np.allclose(lo, [0.1, 0.1, 0], atol=1e-6)
    assert np.allclose(hi, [2*8-0.1, 4*8-0.1, 9.6+1.8], atol=1e-6)   # 15.8 x 31.8 x (9.6 + plot 1.8)

def test_voxelize_cube_and_cylinder():
    cube = L._box(0, 0, 0, 40, 24, 19.2)
    v = L.voxelize_mesh(cube, 5)
    assert v.shape == (5, 3, 2) and v.all()
    cyl = L._tube(0, 0, 0, 40, 30, 0, 48)
    v = L.voxelize_mesh(cyl, 12)
    assert len({int(v[:, :, k].sum()) for k in range(v.shape[2])}) == 1 and v.sum() > 0

def test_pack_covers_exactly_and_staggers():
    v = L.shape_voxels('sphere', 12)
    lay = L.pack(v)
    for k, layer in enumerate(lay):
        cover = np.zeros(v.shape[:2], int)
        for i, j, _, w, d in layer: cover[i:i+w, j:j+d] += 1
        assert (cover == v[:, :, k]).all()                 # chaque cellule couverte une seule fois
    assert L.components(lay) == 1 or L.components(L.prune_floating(lay)[0]) == 1

def test_export_files():
    with tempfile.TemporaryDirectory() as out:
        lay, _ = L.prune_floating(L.pack(L.shape_voxels('torus', 14)))
        counts, n = L.export_kit(lay, 14, 14, out, (220, 220), 0.1)
        for f in ('parts.csv', 'notice.html', 'assemble_apercu.stl', 'plateaux/plateau_01.stl'):
            assert os.path.getsize(f'{out}/{f}') > 0
        assert sum(counts.values()) == sum(map(len, lay))

if __name__ == '__main__':
    for n, f in list(globals().items()):
        if n.startswith('test_'): f(); print('ok', n)
