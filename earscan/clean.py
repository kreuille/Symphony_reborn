"""Nettoyage 3D du maillage : retirer le plan de support et le fond, isoler l'oreille, boucher, lisser."""
from __future__ import annotations

import numpy as np
import trimesh


def largest_component(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    parts = mesh.split(only_watertight=False)
    return max(parts, key=lambda m: len(m.faces)) if parts else mesh


def fit_ground_plane(mesh: trimesh.Trimesh, tol_mm: float = 1.0, iters: int = 400, seed: int = 0):
    """Plan dominant (table, support) par RANSAC sur les sommets. Renvoie (origine, normale vers l'oreille).

    Le côté « oreille » est celui où se trouve la géométrie hors plan la plus importante. À n'utiliser
    que sans marqueur : avec marqueur, le plan est connu avec plus de fiabilité.
    """
    v = np.asarray(trimesh.sample.sample_surface(mesh, 30000, seed=seed)[0])  # pondéré par l'aire
    rng = np.random.default_rng(seed)
    best, best_n = None, -1
    for _ in range(iters):
        a, b, c = v[rng.choice(len(v), 3, replace=False)]
        n = np.cross(b - a, c - a)
        norm = np.linalg.norm(n)
        if norm < 1e-9:
            continue
        n /= norm
        inl = int((np.abs((v - a) @ n) < tol_mm).sum())
        if inl > best_n:
            best, best_n = (a, n), inl
    a, n = best
    inliers = np.abs((v - a) @ n) < tol_mm
    n = np.linalg.svd(v[inliers] - v[inliers].mean(0))[2][-1]       # affinage sur les inliers
    origin = v[inliers].mean(0)
    h = (v - origin) @ n
    if (h > 3 * tol_mm).sum() < (h < -3 * tol_mm).sum():
        n = -n
    return origin, n


def cut_plane(mesh: trimesh.Trimesh, origin, up, margin_mm: float = 1.0) -> trimesh.Trimesh:
    """Garde ce qui est au-dessus du plan, relevé de `margin_mm` (retire table et support)."""
    up = np.asarray(up, float)
    up = up / np.linalg.norm(up)
    # slice_faces_plane évite la dépendance à shapely de slice_mesh_plane (utile seulement pour le capuchon).
    v, f, _ = trimesh.intersections.slice_faces_plane(
        mesh.vertices, mesh.faces, up, np.asarray(origin) + up * margin_mm)
    return trimesh.Trimesh(v, f, process=True)


def crop_radius(mesh: trimesh.Trimesh, center, radius_mm: float) -> trimesh.Trimesh:
    keep = np.linalg.norm(mesh.triangles_center - np.asarray(center), axis=1) <= radius_mm
    out = mesh.copy()
    out.update_faces(keep)
    out.remove_unreferenced_vertices()
    return out


def close_boundaries(mesh: trimesh.Trimesh, max_loop: int = 20000) -> trimesh.Trimesh:
    """Bouche chaque contour ouvert par un éventail de triangles (adapté à une coupe plane)."""
    from trimesh import grouping
    edges = mesh.edges_sorted
    idx = grouping.group_rows(edges, require_count=1)
    if len(idx) == 0:
        return mesh
    nxt: dict[int, list[int]] = {}
    for a, b in mesh.edges[idx]:
        nxt.setdefault(int(a), []).append(int(b))
    verts = mesh.vertices.tolist()
    faces = mesh.faces.tolist()
    seen: set[int] = set()
    for start in list(nxt):
        if start in seen:
            continue
        loop, cur = [start], start
        while True:
            seen.add(cur)
            outs = [n for n in nxt.get(cur, []) if n not in seen or n == start]
            if not outs:
                break
            cur = outs[0]
            if cur == start:
                break
            loop.append(cur)
            if len(loop) > max_loop:
                break
        if cur != start or len(loop) < 3:
            continue
        c = len(verts)
        verts.append(np.mean([verts[i] for i in loop], axis=0).tolist())
        for a, b in zip(loop, loop[1:] + loop[:1]):
            faces.append([b, a, c])      # sens inverse de l'arête existante a -> b
    return trimesh.Trimesh(verts, faces, process=True)


def smooth(mesh: trimesh.Trimesh, iterations: int = 10) -> trimesh.Trimesh:
    """Lissage de Taubin (retrait du bruit sans faire rétrécir l'objet)."""
    if iterations <= 0:
        return mesh
    out = mesh.copy()
    trimesh.smoothing.filter_taubin(out, iterations=iterations)
    return out


def clean_ear(mesh: trimesh.Trimesh, origin=None, up=None, center=None, margin_mm: float = 1.0,
              radius_mm: float | None = None, smooth_iters: int = 10, close: bool = True) -> trimesh.Trimesh:
    """Isole l'oreille. Sans plan (origin/up) le plan dominant est cherché automatiquement.

    1. coupe au-dessus du plan (retire table et fond) ; 2. plus grande composante ; 3. rayon autour de
    `center` (marqueur) ou du centre de la composante ; 4. lissage ; 5. fermeture des contours.
    """
    if origin is None or up is None:
        origin, up = fit_ground_plane(mesh)
    m = largest_component(cut_plane(mesh, origin, up, margin_mm))
    if radius_mm is not None:
        c = np.asarray(center) if center is not None else m.vertices.mean(0)
        m = largest_component(crop_radius(m, c, radius_mm))
    m = smooth(m, smooth_iters)
    if close:
        m = close_boundaries(m)
    m.remove_unreferenced_vertices()
    return m
