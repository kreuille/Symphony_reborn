"""Lecture d'un modèle COLMAP au format texte (cameras.txt, images.txt)."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class Camera:
    id: int
    model: str
    width: int
    height: int
    params: tuple[float, ...]


@dataclass(frozen=True)
class Image:
    id: int
    qvec: tuple[float, float, float, float]  # (w, x, y, z), monde -> caméra
    tvec: tuple[float, float, float]
    camera_id: int
    name: str


def read_cameras_text(path: str | Path) -> dict[int, Camera]:
    cameras: dict[int, Camera] = {}
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        f = line.split()
        cameras[int(f[0])] = Camera(int(f[0]), f[1], int(f[2]), int(f[3]),
                                    tuple(float(v) for v in f[4:]))
    return cameras


def read_images_text(path: str | Path) -> dict[int, Image]:
    """images.txt : deux lignes par image (pose, puis points 2D ; la seconde peut être vide)."""
    raw = [l for l in Path(path).read_text().splitlines() if not l.startswith("#")]
    images: dict[int, Image] = {}
    for header in raw[0::2]:
        f = header.split()
        if not f:
            continue
        images[int(f[0])] = Image(
            int(f[0]),
            tuple(float(v) for v in f[1:5]),
            tuple(float(v) for v in f[5:8]),
            int(f[8]),
            " ".join(f[9:]),
        )
    return images


def qvec_to_rotmat(q) -> np.ndarray:
    w, x, y, z = q
    return np.array([
        [1 - 2 * y * y - 2 * z * z, 2 * x * y - 2 * w * z, 2 * x * z + 2 * w * y],
        [2 * x * y + 2 * w * z, 1 - 2 * x * x - 2 * z * z, 2 * y * z - 2 * w * x],
        [2 * x * z - 2 * w * y, 2 * y * z + 2 * w * x, 1 - 2 * x * x - 2 * y * y],
    ])


def intrinsics(camera: Camera) -> tuple[np.ndarray, np.ndarray]:
    """Matrice K et coefficients de distorsion (convention OpenCV k1, k2, p1, p2)."""
    p = camera.params
    m = camera.model
    if m == "SIMPLE_PINHOLE":
        fx = fy = p[0]; cx, cy = p[1], p[2]; dist = [0, 0, 0, 0]
    elif m == "PINHOLE":
        fx, fy, cx, cy = p[:4]; dist = [0, 0, 0, 0]
    elif m == "SIMPLE_RADIAL":
        fx = fy = p[0]; cx, cy = p[1], p[2]; dist = [p[3], 0, 0, 0]
    elif m == "RADIAL":
        fx = fy = p[0]; cx, cy = p[1], p[2]; dist = [p[3], p[4], 0, 0]
    elif m == "OPENCV":
        fx, fy, cx, cy = p[:4]; dist = [p[4], p[5], p[6], p[7]]
    else:
        raise ValueError(f"modèle de caméra COLMAP non géré : {m}")
    K = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1.0]])
    return K, np.array(dist, dtype=float)
