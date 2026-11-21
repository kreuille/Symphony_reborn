"""Mesure d'erreur d'un maillage par rapport à un maillage de référence (exigences E2 à E4)."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import trimesh
from scipy.spatial import cKDTree


@dataclass(frozen=True)
class Report:
    rms: float          # mm, écart maillage -> référence après recalage rigide
    mean: float
    p95: float
    max: float
    scale: float        # facteur de similitude qui rapproche le maillage de la référence (1 = parfait)
    scale_error: float  # |scale - 1|
    transform: np.ndarray  # 4x4, maillage -> référence


def _kabsch(src: np.ndarray, dst: np.ndarray, with_scale: bool = False):
    mu_s, mu_d = src.mean(0), dst.mean(0)
    S, D = src - mu_s, dst - mu_d
    U, sig, Vt = np.linalg.svd(D.T @ S)
    d = np.sign(np.linalg.det(U @ Vt))
    E = np.diag([1, 1, d])
    R = U @ E @ Vt
    s = float((sig * np.array([1, 1, d])).sum() / (S ** 2).sum()) if with_scale else 1.0
    t = mu_d - s * R @ mu_s
    return s, R, t


def _closest(ref: trimesh.Trimesh, pts: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Point le plus proche sur la surface (exact, lent : réservé à la finition et au résultat)."""
    q, d, _ = trimesh.proximity.closest_point(ref, pts)
    return q, d


class _Dense:
    """Référence échantillonnée densément + KD-tree : correspondances rapides pour l'ICP."""

    def __init__(self, ref: trimesh.Trimesh, n: int, seed: int):
        pts, _ = trimesh.sample.sample_surface(ref, n, seed=seed)
        self.pts = np.asarray(pts)
        self.tree = cKDTree(self.pts)

    def closest(self, q: np.ndarray):
        d, i = self.tree.query(q)
        return self.pts[i], d


def _initial_candidates(src: np.ndarray, dst: np.ndarray):
    """Quatre alignements d'axes principaux (rotations propres) comme points de départ de l'ICP."""
    def axes(p):
        c = p.mean(0)
        _, _, vt = np.linalg.svd(p - c, full_matrices=False)
        A = vt.T
        if np.linalg.det(A) < 0:  # base directe, sinon aucune rotation propre n'est possible
            A[:, 2] *= -1
        return c, A
    cs, As = axes(src)
    cd, Ad = axes(dst)
    for signs in ([1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]):
        R = Ad @ np.diag(signs) @ As.T
        yield R, cd - R @ cs


def _icp(src: np.ndarray, closest, R0, t0, iters: int, with_scale: bool, trim: float, s0: float = 1.0):
    s, R, t = s0, R0, t0
    for _ in range(iters):
        q, d = closest(s * src @ R.T + t)
        keep = d <= np.quantile(d, trim) if trim < 1.0 else slice(None)
        s2, R2, t2 = _kabsch(src[keep], q[keep], with_scale)
        done = np.allclose(R2, R, atol=1e-9) and np.allclose(t2, t, atol=1e-9) and abs(s2 - s) < 1e-10
        s, R, t = s2, R2, t2
        if done:
            break
    return s, R, t


def _trimmed_rms(d: np.ndarray, trim: float) -> float:
    return float(np.sqrt(np.mean(np.sort(d)[: max(1, int(len(d) * trim))] ** 2)))


def evaluate(mesh: trimesh.Trimesh, reference: trimesh.Trimesh, n_points: int = 10000,
             iters: int = 60, trim: float = 1.0, seed: int = 0) -> Report:
    """Recale `mesh` sur `reference` (ICP rigide, en mm) et mesure l'écart point -> surface.

    `trim` < 1 ignore les points les plus éloignés (scan partiel). La référence doit être en mm.
    L'écart final est une distance exacte point -> triangle, pas une distance entre échantillons.
    """
    rng = np.random.default_rng(seed)
    src = np.asarray(trimesh.sample.sample_surface(mesh, n_points, seed=int(rng.integers(1 << 31)))[0])
    dense = _Dense(reference, 10 * n_points, int(rng.integers(1 << 31)))

    best = None
    for R0, t0 in _initial_candidates(src, dense.pts[:: 10]):
        _, R, t = _icp(src, dense.closest, R0, t0, iters, False, trim)
        score = _trimmed_rms(dense.closest(src @ R.T + t)[1], trim)
        if best is None or score < best[0]:
            best = (score, R, t)
    _, R, t = best
    _, R, t = _icp(src, lambda p: _closest(reference, p), R, t, 3, False, trim)  # finition exacte

    d = _closest(reference, src @ R.T + t)[1]
    s, _, _ = _icp(src, dense.closest, R, t, 30, True, trim)
    T = np.eye(4)
    T[:3, :3], T[:3, 3] = R, t
    return Report(float(np.sqrt(np.mean(d ** 2))), float(d.mean()), float(np.percentile(d, 95)),
                  float(d.max()), float(s), float(abs(s - 1.0)), T)
