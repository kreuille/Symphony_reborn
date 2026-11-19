#!/usr/bin/env python3
"""legokit : modèle 3D (STL/OBJ) ou forme procédurale -> kit de briques compatibles LEGO imprimables en 3D.

Chaîne : voxelisation -> découpage en briques (empilement décalé) -> pièces STL
(creuses, plots, tubes, jeu d'impression) -> plateaux d'impression -> notice par couche + liste de pièces.
Dépendance : numpy uniquement.
"""
import argparse, colorsys, csv, html, math, os, struct
from collections import Counter
import numpy as np

# ---------------------------------------------------------------- paramètres LEGO (mm)
PITCH = 8.0          # entraxe des plots
BRICK_H = 9.6        # hauteur d'une brique
STUD_D, STUD_H = 4.8, 1.8
WALL, TOP = 1.5, 1.0
TUBE_OD, TUBE_ID = 6.5, 4.9      # le tube se serre sur le plot (4.8) : ID un peu plus grand
PIN_D = 3.0                      # pion central des briques 1xN
SEG = 24

# ---------------------------------------------------------------- primitives maillées
def _box(x0, y0, z0, x1, y1, z1):
    v = np.array([[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],
                  [x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]], float)
    f = [(0,3,2),(0,2,1),(4,5,6),(4,6,7),(0,1,5),(0,5,4),
         (1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
    return v[np.array(f)]

def _tube(cx, cy, z0, z1, ro, ri=0.0, n=SEG):
    """Cylindre plein (ri=0) ou tube, fermé, normales sortantes."""
    t = np.linspace(0, 2*math.pi, n, endpoint=False)
    c, s = np.cos(t), np.sin(t)
    P = lambda r, z: np.stack([cx + r*c, cy + r*s, np.full(n, z)], 1)
    tris = []
    def ring(r_a, r_b, z, up):  # couronne/disque à la cote z
        for i in range(n):
            j = (i + 1) % n
            if r_b == 0:
                tri = [P(r_a, z)[i], P(r_a, z)[j], [cx, cy, z]]
            else:
                a, b = P(r_a, z), P(r_b, z)
                tris.append(_o([a[i], a[j], b[j]], up)); tri = [a[i], b[j], b[i]]
            tris.append(_o(tri, up))
    def _o(tri, up):
        tri = np.array(tri, float)
        n_z = np.cross(tri[1]-tri[0], tri[2]-tri[0])[2]
        return tri if (n_z > 0) == up else tri[::-1]
    def wall(r, outward):
        a, b = P(r, z0), P(r, z1)
        for i in range(n):
            j = (i + 1) % n
            q1, q2 = [a[i], a[j], b[j]], [a[i], b[j], b[i]]
            if not outward: q1, q2 = q1[::-1], q2[::-1]
            tris.extend([np.array(q1), np.array(q2)])
    ring(ro, ri, z1, True); ring(ro, ri, z0, False); wall(ro, True)
    if ri > 0: wall(ri, False)
    return np.array(tris)

def brick_shells(w, d, tol=0.1, studs=True, height=BRICK_H):
    """Brique w x d plots, creuse, `tol` mm de jeu par côté pour l'impression FDM/résine.
    Renvoie la liste des volumes fermés (qui se chevauchent) dont la pièce est l'union."""
    W, D = w*PITCH - 2*tol, d*PITCH - 2*tol
    x0, y0, H = tol, tol, height
    parts = [_box(x0, y0, H-TOP, x0+W, y0+D, H)]                      # plafond
    t = WALL
    parts += [_box(x0, y0, 0, x0+W, y0+t, H-TOP/2), _box(x0, y0+D-t, 0, x0+W, y0+D, H-TOP/2),
              _box(x0, y0+t/2, 0, x0+t, y0+D-t/2, H-TOP/2), _box(x0+W-t, y0+t/2, 0, x0+W, y0+D-t/2, H-TOP/2)]
    if w >= 2 and d >= 2:                                                # tubes sous la brique
        for i in range(1, w):
            for j in range(1, d):
                parts.append(_tube(i*PITCH, j*PITCH, 0, H-TOP/2, TUBE_OD/2, TUBE_ID/2))
    elif max(w, d) >= 2:                                                 # pions pour 1xN
        for k in range(1, max(w, d)):
            cx, cy = (k*PITCH, d*PITCH/2) if w > 1 else (w*PITCH/2, k*PITCH)
            parts.append(_tube(cx, cy, 0, H-TOP/2, PIN_D/2))
    if studs:
        for i in range(w):
            for j in range(d):
                parts.append(_tube((i+.5)*PITCH, (j+.5)*PITCH, H-TOP/2, H+STUD_H, STUD_D/2))
    return parts

def brick_mesh(*a, **k):
    return np.concatenate(brick_shells(*a, **k))

# ---------------------------------------------------------------- E/S maillages
def write_stl(path, tris):
    tris = np.asarray(tris, np.float32)
    n = np.cross(tris[:,1]-tris[:,0], tris[:,2]-tris[:,0])
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    rec = np.zeros(len(tris), dtype=[('n','<f4',3),('v','<f4',(3,3)),('a','<u2')])
    rec['n'], rec['v'] = n, tris
    with open(path, 'wb') as f:
        f.write(b'legokit'.ljust(80, b' ')); f.write(struct.pack('<I', len(tris))); f.write(rec.tobytes())

def read_mesh(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.obj':
        V, F = [], []
        for line in open(path):
            p = line.split()
            if p[:1] == ['v']: V.append([float(x) for x in p[1:4]])
            elif p[:1] == ['f']:
                idx = [int(q.split('/')[0]) for q in p[1:]]
                idx = [i - 1 if i > 0 else len(V) + i for i in idx]
                F += [(idx[0], idx[k], idx[k+1]) for k in range(1, len(idx)-1)]
        return np.array(V)[np.array(F)]
    data = open(path, 'rb').read()
    if len(data) >= 84 and 84 + struct.unpack('<I', data[80:84])[0]*50 == len(data):   # STL binaire
        n = struct.unpack('<I', data[80:84])[0]
        rec = np.frombuffer(data[84:], dtype=[('n','<f4',3),('v','<f4',(3,3)),('a','<u2')], count=n)
        return rec['v'].astype(float)
    pts = [[float(x) for x in l.split()[1:4]] for l in data.decode(errors='ignore').splitlines()
           if l.strip().startswith('vertex')]
    return np.array(pts).reshape(-1, 3, 3)                                              # STL ASCII

# ---------------------------------------------------------------- voxelisation
def voxelize_mesh(tris, width_studs):
    """Lance un rayon vertical par colonne (nx, ny), remplissage par parité. Axe Z = haut."""
    tris = np.asarray(tris, float)
    lo, hi = tris.reshape(-1, 3).min(0), tris.reshape(-1, 3).max(0)
    scale = width_studs * PITCH / max(hi[0]-lo[0], hi[1]-lo[1])
    T = (tris - lo) * scale
    ext = (hi - lo) * scale
    nx, ny, nz = (max(1, math.ceil(ext[0]/PITCH - 1e-6)), max(1, math.ceil(ext[1]/PITCH - 1e-6)),
                  max(1, round(ext[2]/BRICK_H)))
    hits = {}
    for a, b, c in T:
        i0, i1 = int(max(0, (min(a[0],b[0],c[0])/PITCH) - .5)), int(min(nx-1, (max(a[0],b[0],c[0])/PITCH) - .5) + 1)
        j0, j1 = int(max(0, (min(a[1],b[1],c[1])/PITCH) - .5)), int(min(ny-1, (max(a[1],b[1],c[1])/PITCH) - .5) + 1)
        if i1 < i0 or j1 < j0: continue
        d = (b[1]-c[1])*(a[0]-c[0]) + (c[0]-b[0])*(a[1]-c[1])
        if abs(d) < 1e-12: continue
        I, J = np.meshgrid(np.arange(i0, i1+1), np.arange(j0, j1+1), indexing='ij')
        px, py = (I+.5)*PITCH + 1.37e-3, (J+.5)*PITCH + 2.91e-3   # léger décalage : évite les arêtes de triangles (double comptage)
        l1 = ((b[1]-c[1])*(px-c[0]) + (c[0]-b[0])*(py-c[1])) / d
        l2 = ((c[1]-a[1])*(px-c[0]) + (a[0]-c[0])*(py-c[1])) / d
        l3 = 1 - l1 - l2
        m = (l1 >= 0) & (l2 >= 0) & (l3 >= 0)
        z = l1*a[2] + l2*b[2] + l3*c[2]
        for i, j, zz in zip(I[m], J[m], z[m]): hits.setdefault((i, j), []).append(zz)
    vox = np.zeros((nx, ny, nz), bool)
    zc = (np.arange(nz) + .5) * BRICK_H
    for (i, j), zs in hits.items():
        zs = np.sort(zs)
        vox[i, j] = (np.searchsorted(zs, zc) % 2) == 1
    return vox

def shape_voxels(name, width_studs):
    n = width_studs; nz = max(2, round(n * PITCH / BRICK_H))
    x, y, z = np.meshgrid((np.arange(n)+.5)/n*2-1, (np.arange(n)+.5)/n*2-1, (np.arange(nz)+.5)/nz*2-1, indexing='ij')
    if name == 'sphere': return x**2 + y**2 + z**2 <= 1
    if name == 'cone':   return np.hypot(x, y) <= (1 - z) / 2
    if name == 'torus':  return (np.hypot(x, y) - .6)**2 + z**2 <= .3**2
    if name == 'pyramid': return np.maximum(abs(x), abs(y)) <= (1 - z) / 2
    raise SystemExit(f'forme inconnue : {name}')

# ---------------------------------------------------------------- découpage en briques
DEFAULT_SIZES = [(2,6),(2,4),(2,3),(2,2),(1,6),(1,4),(1,3),(1,2),(1,1)]

def pack_layer(mask, parity, sizes):
    """Glouton : plus grande brique possible à chaque cellule libre, balayage ligne par ligne.
    Les couches impaires sont packées sur le plan transposé : les briques courent dans l'autre sens,
    donc les joints sont décalés d'une couche à l'autre (solidité)."""
    if parity: return [(j, i, d, w) for i, j, w, d in pack_layer(mask.T, 0, sizes)]
    nx, ny = mask.shape
    free = mask.copy(); out = []
    cands = sorted({(a, b) for s in sizes for a, b in (s, s[::-1])}, key=lambda s: (-s[0]*s[1], s[0] < s[1]))
    for j in range(ny):
        for i in range(nx):
            if not free[i, j]: continue
            for w, d in cands:
                if i+w <= nx and j+d <= ny and free[i:i+w, j:j+d].all():
                    free[i:i+w, j:j+d] = False; out.append((i, j, w, d)); break
    return out

def pack(vox, sizes=DEFAULT_SIZES):
    return [[(i, j, k, w, d) for i, j, w, d in pack_layer(vox[:, :, k], k % 2, sizes)] for k in range(vox.shape[2])]

def _labels(layers):
    flat = [b for L in layers for b in L]; par = list(range(len(flat)))
    def find(a):
        while par[a] != a: par[a] = par[par[a]]; a = par[a]
        return a
    idx = {}
    for n, (i, j, k, w, d) in enumerate(flat):
        for x in range(i, i+w):
            for y in range(j, j+d):
                idx[(x, y, k)] = n
                if (x, y, k-1) in idx: par[find(n)] = find(idx[(x, y, k-1)])
    return [find(n) for n in range(len(flat))]

def components(layers):
    """Nombre de morceaux indépendants une fois assemblé (1 = un seul bloc rigide)."""
    return len(set(_labels(layers)))

def prune_floating(layers):
    """Supprime les briques qui ne tiennent pas au bloc principal (contact par arête seulement). -> (couches, nb supprimées)."""
    lab = _labels(layers); main = Counter(lab).most_common(1)[0][0]
    it = iter(lab); out = [[b for b in L if next(it) == main] for L in layers]
    return out, len(lab) - sum(map(len, out))

# ---------------------------------------------------------------- sorties
def plates(counts, bed=(220, 220), gap=3.0, tol=0.1):
    """Rangement en étagères des briques (plots vers le haut) sur des plateaux. -> liste de listes de triangles."""
    items = []
    for (w, d), n in sorted(counts.items(), key=lambda kv: -kv[0][0]*kv[0][1]):
        items += [(w, d)] * n
    res, cur, x, y, rowh = [], [], gap, gap, 0
    def flush():
        nonlocal cur, x, y, rowh
        if cur: res.append(np.concatenate(cur))
        cur, x, y, rowh = [], gap, gap, 0
    cache = {}
    for w, d in items:
        W, D = w*PITCH, d*PITCH
        if x + W + gap > bed[0]: x, y, rowh = gap, y + rowh + gap, 0
        if y + D + gap > bed[1]: flush()
        m = cache.setdefault((w, d), brick_mesh(w, d, tol))
        cur.append(m + [x, y, 0]); x += W + gap; rowh = max(rowh, D)
    flush()
    return res

def layer_svg(layers, k, nx, ny, s=24):
    col = lambda w, d: '#%02x%02x%02x' % tuple(int(255*c) for c in colorsys.hsv_to_rgb(((w*7 + d*3) % 11)/11, .45, .95))
    g = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{nx*s}" height="{ny*s}" viewBox="0 0 {nx*s} {ny*s}">',
         f'<rect width="{nx*s}" height="{ny*s}" fill="#fafafa"/>']
    if k > 0:
        for i, j, _, w, d in layers[k-1]:
            g.append(f'<rect x="{i*s}" y="{j*s}" width="{w*s}" height="{d*s}" fill="#ddd" stroke="#bbb"/>')
    for i, j, _, w, d in layers[k]:
        g.append(f'<rect x="{i*s+1}" y="{j*s+1}" width="{w*s-2}" height="{d*s-2}" rx="3" fill="{col(*sorted((w, d)))}" stroke="#222" stroke-width="1.5"/>')
        for a in range(w):
            for b in range(d): g.append(f'<circle cx="{(i+a+.5)*s}" cy="{(j+b+.5)*s}" r="{s*.2}" fill="none" stroke="#2228"/>')
        g.append(f'<text x="{(i+w/2)*s}" y="{(j+d/2)*s+4}" font-size="11" text-anchor="middle">{min(w,d)}x{max(w,d)}</text>')
    return '\n'.join(g) + '</svg>'

def export_kit(layers, nx, ny, out, bed, tol):
    os.makedirs(out, exist_ok=True)
    counts = Counter((min(w, d), max(w, d)) for L in layers for *_, w, d in L)
    with open(f'{out}/parts.csv', 'w', newline='') as f:
        wr = csv.writer(f); wr.writerow(['piece', 'quantite'])
        for (a, b), n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])): wr.writerow([f'{a}x{b}', n])
    tris = np.concatenate([brick_mesh(w, d, 0.0) + [i*PITCH, j*PITCH, k*BRICK_H] for k, L in enumerate(layers) for i, j, _, w, d in L])
    write_stl(f'{out}/assemble_apercu.stl', tris)
    os.makedirs(f'{out}/plateaux', exist_ok=True)
    pl = plates(counts, bed, tol=tol)
    for n, t in enumerate(pl, 1): write_stl(f'{out}/plateaux/plateau_{n:02d}.stl', t)
    body = ''.join(f'<h2>Couche {k+1} / {len(layers)}</h2>{layer_svg(layers, k, nx, ny)}' for k in range(len(layers)))
    rows = ''.join(f'<tr><td>{a}x{b}</td><td>{n}</td></tr>' for (a, b), n in sorted(counts.items(), key=lambda kv: -kv[1]))
    open(f'{out}/notice.html', 'w').write(
        f'<!doctype html><meta charset=utf-8><title>Notice</title><body style="font-family:sans-serif;max-width:900px;margin:auto">'
        f'<h1>Notice de montage</h1><p>Couches du bas vers le haut ; en gris, la couche précédente.</p>'
        f'<table border=1 cellpadding=4><tr><th>Pièce</th><th>Qté</th></tr>{rows}</table>{body}')
    return counts, len(pl)

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('model', nargs='?', help='fichier .stl ou .obj (Z = haut)')
    ap.add_argument('--shape', choices=['sphere', 'cone', 'torus', 'pyramid'], help='forme procédurale au lieu d\'un fichier')
    ap.add_argument('--width', type=int, default=24, help='largeur max du modèle en plots (défaut 24)')
    ap.add_argument('--out', default='kit_out')
    ap.add_argument('--bed', type=float, nargs=2, default=[220, 220], metavar=('X', 'Y'), help='plateau d\'impression en mm')
    ap.add_argument('--tol', type=float, default=0.1, help='jeu par côté en mm (0.1 FDM, 0.05 résine)')
    ap.add_argument('--keep-floating', action='store_true', help='garde aussi les briques qui ne tiennent pas au bloc principal')
    ap.add_argument('--hollow', action='store_true', help='ne garder que la coque (1 brique d\'épaisseur) : économise du filament')
    a = ap.parse_args()
    if not a.model and not a.shape: ap.error('donner un fichier ou --shape')
    vox = shape_voxels(a.shape, a.width) if a.shape else voxelize_mesh(read_mesh(a.model), a.width)
    if a.hollow:   # coque de 2 voxels d'épaisseur (1 seul serait fragile : contacts par arête)
        def erode(v):
            p = np.pad(v, 1); return p[2:,1:-1,1:-1] & p[:-2,1:-1,1:-1] & p[1:-1,2:,1:-1] & p[1:-1,:-2,1:-1] & p[1:-1,1:-1,2:] & p[1:-1,1:-1,:-2]
        vox = vox & ~erode(erode(vox))
    layers = pack(vox)
    dropped = 0
    if not a.keep_floating: layers, dropped = prune_floating(layers)
    counts, nplates = export_kit(layers, *vox.shape[:2], a.out, tuple(a.bed), a.tol)
    print(f'grille {vox.shape[0]}x{vox.shape[1]}x{vox.shape[2]} | {sum(counts.values())} briques, {len(counts)} références | '
          f'{components(layers)} bloc(s) rigide(s) | {nplates} plateau(x) -> {a.out}/' + (f' | {dropped} brique(s) flottante(s) retirée(s)' if dropped else ''))
    for (x, y), n in sorted(counts.items(), key=lambda kv: -kv[1]): print(f'  {x}x{y}: {n}')

if __name__ == '__main__':
    main()
