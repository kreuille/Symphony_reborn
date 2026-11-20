#!/usr/bin/env python3
"""legopart : pièce LDraw quelconque (pente, support, jante, pneu...) -> maillage prêt à imprimer, en mm.

Chaîne : maillage LDraw aplati avec le sens des faces (BFC) -> conversion LDU -> mm, axe Z = haut -> orientation de
la meilleure face d'appui sur le plateau -> léger retrait du pied (jeu d'impression) pour les pièces qui s'emboîtent.
Limites : la géométrie LDraw est la forme extérieure fidèle, pas une pièce optimisée pour l'impression : des jonctions en T
(3 à 13 % d'arêtes non appariées, que les trancheurs réparent), pas de supports ajoutés (pentes inversées, arches à supporter
dans le trancheur), jeu à calibrer sur un premier essai.
"""
import re
import numpy as np

LDU_MM = 0.4                                   # 20 LDU = 8 mm
CLUTCH = re.compile(r'^(Brick|Plate|Tile|Bracket|Slope)\b', re.I)      # pièces qui s'emboîtent par leurs plots : jeu appliqué
SKIP = re.compile(r'^(Sticker|Paper|Cardboard|Box|Instruction|Duplo Sticker|Sheet)\b', re.I)

def printable_kind(name):
    """None si imprimable, sinon la raison pour laquelle on ne l'imprime pas."""
    if SKIP.match(name): return 'autocollant / papier'
    return None

def solid(lib, ref):
    """Triangles (n,3,3) en coordonnées LDraw, tous orientés vers l'extérieur (BFC)."""
    memo = lib.__dict__.setdefault('solid_memo', {})
    key = lib.find(ref)
    if key is None: return np.zeros((0, 3, 3))
    if key in memo: return memo[key]
    memo[key] = np.zeros((0, 3, 3))                                   # garde-fou contre les boucles
    ccw, inv, out = True, False, []
    for line in lib.read(key).splitlines():
        t = line.split()
        if not t: continue
        try:
            if t[0] == '0':
                if len(t) > 1 and t[1] == 'BFC':
                    o = t[2:]
                    if 'CW' in o: ccw = False
                    if 'CCW' in o: ccw = True
                    if 'INVERTNEXT' in o: inv = True
                continue
            if t[0] == '1' and len(t) >= 15:
                v = [float(x) for x in t[2:14]]
                M, o = np.array(v[3:12]).reshape(3, 3), np.array(v[:3])
                sub = solid(lib, ' '.join(t[14:]))
                flip = (np.linalg.det(M) < 0) != inv; inv = False
                if len(sub):
                    tr = sub @ M.T + o
                    out.append(tr[:, [0, 2, 1]] if flip else tr)
            elif t[0] in ('3', '4'):
                inv = False
                n = 3 if t[0] == '3' else 4
                p = np.array([float(x) for x in t[2:2 + 3 * n]]).reshape(n, 3)
                tr = np.array([p[[0, 1, 2]]] + ([p[[0, 2, 3]]] if n == 4 else []))
                out.append(tr if ccw else tr[:, [0, 2, 1]])
            else:
                inv = False
        except (ValueError, IndexError):
            continue
    memo[key] = np.concatenate(out) if out else np.zeros((0, 3, 3))
    return memo[key]

def _rot_down(d):
    """Rotation qui amène la direction unitaire d vers -Z (la face d'appui regarde vers le bas)."""
    z = np.array([0., 0., -1.]); d = np.asarray(d, float)
    if np.allclose(d, z): return np.eye(3)
    if np.allclose(d, -z): return np.diag([1., -1., -1.])
    ax = np.cross(d, z); ax /= np.linalg.norm(ax)
    K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    return np.eye(3) + K + K @ K                                       # angle = 90°
ORIENT = [_rot_down(d) for d in ([0, 0, -1], [0, 0, 1], [1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0])]

def contact_area(T):
    """Aire des faces orientées vers le bas qui touchent le plateau."""
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); a = np.linalg.norm(n, axis=1) / 2
    z = T[:, :, 2]; zmin = z.min()
    low = (z.max(1) < zmin + 0.05) & (n[:, 2] < -0.98 * np.maximum(2 * a, 1e-12))
    return float(a[low].sum())

def best_orientation(T, keep_upright=0.15):
    """Garde l'orientation d'origine (plots vers le haut : couches parallèles au pied, plots et tubes propres) sauf si elle
    n'offre presque aucune surface d'appui (pneu debout sur sa bande de roulement, pièce ronde...). Alors : la meilleure des 6 poses."""
    scores = [contact_area(T @ R.T) for R in ORIENT]
    best = int(np.argmax(scores))
    return 0 if scores[0] >= keep_upright * scores[best] else best

def ldraw_mesh(lib, ref, name='', tol=0.1):
    """-> triangles (n,3,3) en mm, posés sur Z=0, coin minimal à l'origine, ou None si la pièce n'a pas de géométrie."""
    T = solid(lib, ref)
    if not len(T): return None
    T = T[:, :, [0, 2, 1]] * np.array([1, 1, -1]) * LDU_MM            # (x, y, z)_LDraw -> (x, z, -y) mm : Z vers le haut
    T = T @ ORIENT[best_orientation(T)].T
    T = T - T.reshape(-1, 3).min(0)
    if CLUTCH.match(name) and tol:
        W, D = T[:, :, 0].max(), T[:, :, 1].max()
        sx, sy = max(.5, (W - 2 * tol) / W), max(.5, (D - 2 * tol) / D)
        T = T * np.array([sx, sy, 1.0]) + np.array([(W - W * sx) / 2, (D - D * sy) / 2, 0.0])
    return T

def volume(T):
    """Volume signé (mm³) : positif si toutes les faces sont orientées vers l'extérieur."""
    return float(np.einsum('ij,ij->i', T[:, 0], np.cross(T[:, 1], T[:, 2])).sum() / 6)

def resolve(lib, part_num, relations=None):
    """Référence .dat LDraw pour un numéro de pièce Rebrickable : direct, puis variantes, puis pièce de base (relations)."""
    cands = [part_num]
    if relations:
        cands += [relations[p] for p in cands if p in relations]
    m = re.match(r'^(\d+)[a-z]*', part_num)
    if m: cands += [m.group(0), m.group(1)]
    cands += [re.sub(r'[a-z]+\d*$', '', part_num)]
    for c in cands:
        if c and lib.find(c + '.dat'): return c + '.dat'
    return None
