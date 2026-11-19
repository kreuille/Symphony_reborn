"""Tests hors ligne : python3 test_legopart.py"""
import os, tempfile
import numpy as np
import legopart as LP, legoprint as P, legonotice as N

def box_dat(dx, dy, dz, cw=False):
    """Boîte [0,dx]x[0,dy]x[0,dz] en LDU : 6 quadrilatères, faces extérieures CCW (ou CW)."""
    q = [[(0,0,0),(0,dy,0),(dx,dy,0),(dx,0,0)], [(0,0,dz),(dx,0,dz),(dx,dy,dz),(0,dy,dz)],
         [(0,0,0),(0,0,dz),(0,dy,dz),(0,dy,0)], [(dx,0,0),(dx,dy,0),(dx,dy,dz),(dx,0,dz)],
         [(0,0,0),(dx,0,0),(dx,0,dz),(0,0,dz)], [(0,dy,0),(0,dy,dz),(dx,dy,dz),(dx,dy,0)]]
    if cw: q = [f[::-1] for f in q]
    return ''.join('4 16 ' + ' '.join(str(c) for p in f for c in p) + '\n' for f in q)

def make_lib(d):
    os.makedirs(f'{d}/parts'); os.makedirs(f'{d}/p')
    open(f'{d}/LDConfig.ldr', 'w').write('0 !COLOUR Red CODE 4 VALUE #C91A09 EDGE #333333\n')
    W = lambda n, txt: open(f'{d}/parts/{n}.dat', 'w').write(txt)
    W('9001', '0 Test Block\n0 BFC CERTIFY CCW\n' + box_dat(20, 24, 20))
    W('9002', '0 Mirrored\n0 BFC CERTIFY CCW\n1 16 20 0 0 -1 0 0 0 1 0 0 0 1 9001.dat\n')
    W('9003', '0 Inverted\n0 BFC CERTIFY CCW\n0 BFC INVERTNEXT\n1 16 0 0 0 1 0 0 0 1 0 0 0 1 9001.dat\n')
    W('9004', '0 Clockwise\n0 BFC CERTIFY CW\n' + box_dat(20, 24, 20, cw=True))
    W('9005', '0 Thin Slab\n0 BFC CERTIFY CCW\n' + box_dat(4, 40, 20))              # 4 LDU d'épaisseur, dressée sur sa tranche
    W('9006', '0 Plate 1 x 1\n0 BFC CERTIFY CCW\n' + box_dat(20, 8, 20))
    W('9007base', '0 Base\n0 BFC CERTIFY CCW\n' + box_dat(20, 24, 20))

def test_bfc_winding():
    with tempfile.TemporaryDirectory() as d:
        make_lib(d); lib = N.Library(d)
        v = {n: LP.volume(LP.solid(lib, n + '.dat')) for n in ('9001', '9002', '9003', '9004')}
        assert abs(v['9001'] - 20*24*20) < 1e-6                       # positif : faces vers l'extérieur
        assert abs(v['9002'] - v['9001']) < 1e-6                      # miroir : le sens est corrigé
        assert abs(v['9004'] - v['9001']) < 1e-6                      # BFC CW normalisé
        assert abs(v['9003'] + v['9001']) < 1e-6                      # INVERTNEXT inverse volontairement

def test_ldraw_mesh_units_and_orientation():
    with tempfile.TemporaryDirectory() as d:
        make_lib(d); lib = N.Library(d)
        T = LP.ldraw_mesh(lib, '9001.dat', 'Widget')
        lo, hi = T.reshape(-1, 3).min(0), T.reshape(-1, 3).max(0)
        assert np.allclose(lo, 0) and np.allclose(hi, [8, 8, 9.6])    # 20 LDU = 8 mm ; 24 LDU = 9.6 mm ; Z vers le haut
        assert abs(LP.volume(T) - 20*24*20*0.4**3) < 1e-6
        S = LP.ldraw_mesh(lib, '9005.dat', 'Widget')                  # tranche mince : se couche sur sa grande face
        assert S[:, :, 2].max() < 2.0 and S[:, :, 0].max() > 15
        C = LP.ldraw_mesh(lib, '9006.dat', 'Plate 1 x 1', tol=0.1)    # pièce emboîtable : retrait de 0,2 mm sur l'emprise
        assert abs(C[:, :, 0].min() - 0.1) < 1e-9 and abs(C[:, :, 0].max() - 7.9) < 1e-9     # largeur 7,8 mm, centrée
        assert abs(C[:, :, 2].max() - 3.2) < 1e-9
        N0 = LP.ldraw_mesh(lib, '9006.dat', 'Plate 1 x 1', tol=0)
        assert abs(N0[:, :, 0].max() - 8.0) < 1e-9

def test_resolve_and_skip():
    with tempfile.TemporaryDirectory() as d:
        make_lib(d); lib = N.Library(d)
        assert LP.resolve(lib, '9001') == '9001.dat'
        assert LP.resolve(lib, '9001pb77') == '9001.dat'              # impression -> pièce de base par regex
        assert LP.resolve(lib, '5555x', {'5555x': '9007base'}) == '9007base.dat'     # relation Rebrickable
        assert LP.resolve(lib, '123456') is None
        assert LP.printable_kind('Sticker Sheet for Set 40468-1') and LP.printable_kind('Brick 2 x 4') is None

def test_print_kit_mixed():
    inv = [dict(couleur='Red', rgb='C91A09', part_num='3001', nom='Brick 2 x 4', quantite=2, imprimable='oui', type='Brick', plots='2x4'),
           dict(couleur='Red', rgb='C91A09', part_num='9001', nom='Widget', quantite=3, imprimable='non', type='', plots=''),
           dict(couleur='Red', rgb='C91A09', part_num='7777', nom='Mystery', quantite=1, imprimable='non', type='', plots=''),
           dict(couleur='Red', rgb='C91A09', part_num='1111', nom='Sticker Sheet', quantite=1, imprimable='non', type='', plots='')]
    with tempfile.TemporaryDirectory() as d:
        make_lib(d + '/ld'); lib = N.Library(d + '/ld')
        res = P.print_kit(inv, d + '/out', (256, 256), 0.1, lib=lib, quiet=True)
        assert (res['param'], res['ldraw'], res['plates']) == (2, 3, 1)
        assert {(s[0], s[3]) for s in res['skipped']} == {('7777', 'absente de LDraw'), ('1111', 'autocollant / papier')}
        assert os.path.getsize(d + '/out/Red/Red_01.3mf') > 1000 and os.path.exists(d + '/out/non_generees.csv')
        res0 = P.print_kit(inv, d + '/o2', (256, 256), 0.1, lib=None, quiet=True)      # sans LDraw : paramétrique seul
        assert (res0['param'], res0['ldraw']) == (2, 0)

if __name__ == '__main__':
    for n, f in list(globals().items()):
        if n.startswith('test_'): f(); print('ok', n)
