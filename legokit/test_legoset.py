"""Tests hors ligne : python3 test_legoset.py"""
import csv, gzip, os, tempfile
import legoset as S

def w(d, name, header, rows):
    with gzip.open(f'{d}/{name}.csv.gz', 'wt', newline='') as f:
        c = csv.writer(f); c.writerow(header); c.writerows(rows)

def test_classify():
    assert S.classify('Brick 2 x 4') == ('Brick', 2, 4) and S.classify('Plate 8 x 2') == ('Plate', 2, 8)
    assert S.classify('Tile 1 x 4 with Groove') == ('Tile', 1, 4)
    assert S.classify('Brick Sloped 45° 2 x 2') is None and S.classify('Plate 1 x 2 with Handle') is None

def test_inventory():
    with tempfile.TemporaryDirectory() as d:
        w(d, 'colors', 'id,name,rgb,is_trans'.split(','), [(0, 'Black', '05131D', 'False'), (4, 'Red', 'C91A09', 'False')])
        w(d, 'sets', 'set_num,name,year,num_parts'.split(','), [('1-1', 'Test', 2020, 7)])
        w(d, 'inventories', 'id,version,set_num'.split(','), [(1, 1, '1-1'), (2, 2, '1-1')])
        w(d, 'inventory_parts', 'inventory_id,part_num,color_id,quantity,is_spare'.split(','),
          [(1, '3001', 0, 99, 'False'), (2, '3001', 0, 4, 'False'), (2, '3001', 4, 2, 'False'),
           (2, '3040', 4, 1, 'False'), (2, '3001', 0, 1, 'True')])
        w(d, 'parts', 'part_num,name'.split(','), [('3001', 'Brick 2 x 4'), ('3040', 'Brick Sloped 45° 2 x 1')])
        assert S.find_set(d, '1')['name'] == 'Test'
        inv = S.inventory(d, '1-1')                         # dernière version, sans pièces de rechange
        q = {(r['couleur'], r['part_num']): (r['quantite'], r['imprimable']) for r in inv}
        assert q == {('Black', '3001'): (4, 'oui'), ('Red', '3001'): (2, 'oui'), ('Red', '3040'): (1, 'non')}

if __name__ == '__main__':
    for n, f in list(globals().items()):
        if n.startswith('test_'): f(); print('ok', n)
