"""Mise à l'échelle métrique à partir d'un marqueur ArUco de côté connu.

Les coins du marqueur sont détectés dans chaque image, triangulés avec les poses COLMAP, puis
le côté mesuré dans le repère du modèle donne le facteur d'échelle vers les millimètres.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from .colmap_io import Camera, Image, intrinsics, qvec_to_rotmat, read_cameras_text, read_images_text


class ScaleError(RuntimeError):
    pass


@dataclass(frozen=True)
class ScaleEstimate:
    scale: float                 # facteur à appliquer au modèle pour obtenir des mm
    n_views: int                 # nombre d'images où le marqueur est vu
    side_model: tuple[float, ...]  # 4 côtés dans le repère du modèle
    spread: float                # écart type relatif des 4 côtés (qualité de la triangulation)
    corners: tuple = ()          # 4 coins du marqueur (4x3), repère du modèle
    up: tuple = ()               # normale unitaire du plan du marqueur, orientée vers les caméras


def detect_markers(image_bgr: np.ndarray, dictionary: str = "DICT_4X4_50") -> dict[int, np.ndarray]:
    """Renvoie {id: coins (4, 2)} dans l'ordre haut-gauche, haut-droit, bas-droit, bas-gauche."""
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY) if image_bgr.ndim == 3 else image_bgr
    aruco = cv2.aruco
    params = aruco.DetectorParameters()
    params.cornerRefinementMethod = aruco.CORNER_REFINE_SUBPIX
    detector = aruco.ArucoDetector(aruco.getPredefinedDictionary(getattr(aruco, dictionary)), params)
    corners, ids, _ = detector.detectMarkers(gray)
    if ids is None:
        return {}
    return {int(i): c.reshape(4, 2).astype(float) for i, c in zip(ids.ravel(), corners)}


def triangulate(points_norm: np.ndarray, projections: list[np.ndarray]) -> np.ndarray:
    """Triangulation linéaire (DLT) d'un point vu dans n images. points_norm : (n, 2) normalisés."""
    rows = []
    for (x, y), P in zip(points_norm, projections):
        rows.append(x * P[2] - P[0])
        rows.append(y * P[2] - P[1])
    _, _, vt = np.linalg.svd(np.array(rows))
    X = vt[-1]
    return X[:3] / X[3]


def estimate_scale(images_dir: str | Path, cameras: dict[int, Camera], images: dict[int, Image],
                   marker_id: int, marker_size_mm: float, dictionary: str = "DICT_4X4_50",
                   max_spread: float = 0.05) -> ScaleEstimate:
    obs: list[np.ndarray] = []   # (4, 2) coins normalisés par image
    projs: list[np.ndarray] = []
    centers: list[np.ndarray] = []
    for img in images.values():
        frame = cv2.imread(str(Path(images_dir) / img.name))
        if frame is None:
            continue
        found = detect_markers(frame, dictionary).get(marker_id)
        if found is None:
            continue
        K, dist = intrinsics(cameras[img.camera_id])
        # COLMAP place le centre du premier pixel en (0.5, 0.5), OpenCV en (0, 0).
        pts = (found + 0.5).reshape(-1, 1, 2)
        norm = cv2.undistortPoints(pts, K, dist).reshape(4, 2)
        R = qvec_to_rotmat(img.qvec)
        projs.append(np.hstack([R, np.array(img.tvec).reshape(3, 1)]))
        obs.append(norm)
        centers.append(-R.T @ np.array(img.tvec))
    if len(obs) < 2:
        raise ScaleError(f"marqueur {marker_id} vu dans {len(obs)} image(s) ; il en faut au moins 2")

    corners3d = np.array([triangulate(np.array([o[k] for o in obs]), projs) for k in range(4)])
    sides = np.array([np.linalg.norm(corners3d[k] - corners3d[(k + 1) % 4]) for k in range(4)])
    mean = float(sides.mean())
    spread = float(sides.std() / mean)
    if spread > max_spread:
        raise ScaleError(f"côtés du marqueur incohérents (écart {spread:.1%} > {max_spread:.0%}) : "
                         "marqueur flou, plié ou mal détecté")
    n = np.cross(corners3d[1] - corners3d[0], corners3d[3] - corners3d[0])
    n /= np.linalg.norm(n)
    if (np.mean(centers, axis=0) - corners3d.mean(axis=0)) @ n < 0:
        n = -n
    return ScaleEstimate(marker_size_mm / mean, len(obs), tuple(float(s) for s in sides), spread,
                         tuple(map(tuple, corners3d.tolist())), tuple(n.tolist()))


def estimate_scale_from_model(model_dir: str | Path, images_dir: str | Path, marker_id: int,
                              marker_size_mm: float, **kw) -> ScaleEstimate:
    model_dir = Path(model_dir)
    return estimate_scale(images_dir, read_cameras_text(model_dir / "cameras.txt"),
                          read_images_text(model_dir / "images.txt"), marker_id, marker_size_mm, **kw)
