"""Tests : python3 test_legoprint.py"""
import os, tempfile, zipfile
import xml.etree.ElementTree as ET
import numpy as np
import legoprint as P

NS = {'m': 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}

def read_3mf(path):
    root = ET.fromstring(zipfile.ZipFile(path).read('3D/3dmodel.model'))
    objs = {}
    for o in root.find('m:resources', NS).findall('m:object', NS):
        V = np.array([[float(v.get(k)) for k in 'xyz'] for v in o.iter('{%s}vertex' % NS['m'])])
        T = np.array([[int(t.get(k)) for k in ('v1', 'v2', 'v3')] for t in o.iter('{%s}triangle' % NS['m'])])
        objs[o.get('id')] = (V, T)
    items = [(i.get('objectid'), [float(x) for x in i.get('transform').split()]) for i in root.find('m:build', NS)]
    return root, objs, items

def test_layout_in_bed_no_overlap():
    items = [('Brick', 2, 4)] * 40 + [('Plate', 1, 12)] * 6 + [('Tile', 1, 1)] * 30
    bed = (180, 180)
    plates = P.layout(items, bed)
    assert sum(map(len, plates)) == len(items) and len(plates) > 1
    for p in plates:
        boxes = [(x, y, x + it.W, y + it.D) for it, x, y in p]
        assert all(b[0] >= 0 and b[1] >= 0 and b[2] <= bed[0] and b[3] <= bed[1] for b in boxes)
        for i, a in enumerate(boxes):
            for b in boxes[i+1:]: assert a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1]

def test_3mf_roundtrip():
    plate = [(('Brick', 2, 4), 5, 5), (('Plate', 1, 2), 60, 5), (('Tile', 1, 1), 5, 40), (('Brick', 2, 4), 60, 40)]
    with tempfile.TemporaryDirectory() as d:
        f = f'{d}/x.3mf'; P.write_3mf(f, plate, 'Red', 'C91A09', 0.1)
        root, objs, items = read_3mf(f)
        assert len(items) == 4 and len(objs) == 3                 # 3 types de pièces, 4 exemplaires
        for oid, (V, T) in objs.items(): assert T.max() < len(V)
        zs = {n: (V[:, 2].max()) for n, (V, T) in zip(['b', 'p', 't'], objs.values())}
        assert abs(zs['b'] - (9.6 + 1.8)) < 1e-3                  # brique avec plot
        assert abs(zs['p'] - (3.2 + 1.8)) < 1e-3                  # plaque
        assert abs(zs['t'] - 3.2) < 1e-3                          # tuile : pas de plot
        V = objs['2'][0]; assert abs(V[:, 0].max() - (4*8 - 0.1)) < 1e-3 and abs(V[:, 1].max() - (2*8 - 0.1)) < 1e-3
        assert items[1][1][-3:-1] == [60.0, 5.0]
        assert root.find('m:resources/m:basematerials/m:base', NS).get('displaycolor') == '#C91A09'

if __name__ == '__main__':
    for n, f in list(globals().items()):
        if n.startswith('test_'): f(); print('ok', n)
