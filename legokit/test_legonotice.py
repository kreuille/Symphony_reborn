"""Tests hors ligne : python3 test_legonotice.py"""
import json, os, re, tempfile
import numpy as np
import legonotice as N

MPD = """0 FILE main.ldr
1 4 0 0 0 1 0 0 0 1 0 0 0 1 sub.ldr
0 STEP
1 1 0 -24 0 1 0 0 0 1 0 0 0 1 3001.dat
1 16 40 -24 0 1 0 0 0 1 0 0 0 1 3024.dat
0 STEP
0 FILE sub.ldr
1 16 0 0 0 1 0 0 0 1 0 0 0 1 3001.dat
0 STEP
1 16 0 0 20 1 0 0 0 1 0 0 0 1 3001.dat
"""

def make_lib(d):
    os.makedirs(f'{d}/parts'); os.makedirs(f'{d}/p')
    open(f'{d}/LDConfig.ldr', 'w').write('0 !COLOUR Blue CODE 1 VALUE #0055BF EDGE #333333\n0 !COLOUR Red CODE 4 VALUE #C91A09 EDGE #333333\n'
                                          '0 !COLOUR Clear CODE 47 VALUE #FCFCFC EDGE #C3C3C3 ALPHA 128\n')
    open(f'{d}/p/box.dat', 'w').write('0 box\n3 16 0 0 0 20 0 0 0 -8 0\n4 16 0 0 0 1 0 0 1 0 1 0 0 1\n2 24 0 0 0 1 0 0\n')
    open(f'{d}/parts/3001.dat', 'w').write('0 Brick  2 x  4\n1 16 0 0 0 1 0 0 0 1 0 0 0 1 box.dat\n')
    open(f'{d}/parts/3024.dat', 'w').write('0 Plate  1 x  1\n1 16 0 0 0 1 0 0 0 1 0 0 0 1 box.dat\n')

def test_parse_and_steps():
    models, first, custom = N.parse_model(MPD)
    assert not custom and first == 'main.ldr' and set(models) == {'main.ldr', 'sub.ldr'}
    steps = []; N.expand(models, first, np.eye(4), 15, steps)
    # sous-modèle d'abord (2 étapes), puis les 2 étapes du parent... étape parent 1 = sous-modèle (aucune pièce propre) + rien
    assert [len(s) for s in steps] == [1, 1, 2]
    assert steps[0][0][2] == 4 and steps[1][0][2] == 4         # couleur 4 héritée du sous-modèle (16 -> 4)
    assert steps[2][0][2] == 1 and steps[2][1][2] == 15        # couleur explicite 1 ; 16 -> couleur par défaut 15
    assert abs(steps[1][0][1][2, 3] - 20) < 1e-9               # transformation composée

def test_library_and_build():
    with tempfile.TemporaryDirectory() as d:
        make_lib(d); lib = N.Library(d)
        T, C, L = lib.flat('3001.dat'); assert T.shape == (3, 3, 3) and L.shape == (1, 2, 3) and set(C) == {16}
        assert lib.name('3001.dat') == 'Brick 2 x 4' and lib.color(47)[1] < 0.6 and lib.color(4)[0][0] > 0.7
        models, first, custom = N.parse_model(MPD)
        out = f'{d}/n.html'
        ns, ni, nm, size = N.write_notice(out, models, first, lib, 'Test <x>')
        assert (ns, ni, nm) == (3, 4, 2) and size > 1000
        html = open(out, encoding='utf-8').read()
        data = json.loads(re.search(r'const D = (\{.*?\});\n', html, re.S).group(1))
        assert len(data['steps']) == 3 and data['steps'][2][0][4] == 1      # Brick 2 x 4 : imprimable
        assert data['radius'] > 0 and 'Test &lt;x>' in html
        assert len(data['fit']) == 3 and data['title'] == 'Test <x>'        # cadrage cumulatif pour le mode PDF
        assert data['fit'][0][3] <= data['fit'][2][3] and 'printroot' in html


def test_embedded_part():
    mpd = MPD + "0 FILE parts/9999.dat\n0 Custom Thing\n0 !LDRAW_ORG Unofficial_Part UPDATE 2020-01\n1 16 0 0 0 1 0 0 0 1 0 0 0 1 box.dat\n"
    mpd = mpd.replace("3024.dat", "9999.dat", 1)
    with tempfile.TemporaryDirectory() as d:
        make_lib(d); lib = N.Library(d)
        models, first, custom = N.parse_model(mpd)
        assert set(custom) == {'parts/9999.dat'} and 'parts/9999.dat' not in models
        ns, ni, nm, _ = N.write_notice(f'{d}/n.html', models, first, lib, 't', custom)
        assert (ns, ni, nm) == (3, 4, 2)                           # 9999.dat est une pièce, pas un sous-modèle
        assert lib.name('9999.dat') == 'Custom Thing'

if __name__ == '__main__':
    for n, f in list(globals().items()):
        if n.startswith('test_'): f(); print('ok', n)
