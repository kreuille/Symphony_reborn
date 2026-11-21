"""Détourage de l'oreille dans les photos : masques pour COLMAP (noir = ignoré).

Deux méthodes sans modèle appris :
- `background` : fond uni (papier mat bleu ou vert). Le fond est estimé sur les bords de l'image ; tout ce qui
  s'en écarte en couleur est gardé. Fiable si le fond est vraiment uniforme.
- `grabcut` : GrabCut initialisé par un rectangle central ; plus tolérant, moins fiable.
"""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from .scale import detect_markers

IMG_EXT = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"}


def _largest_blob_filled(mask: np.ndarray) -> np.ndarray:
    n, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    if n <= 1:
        return mask
    keep = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    out = (labels == keep).astype(np.uint8) * 255
    contours, _ = cv2.findContours(out, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(out, contours, -1, 255, thickness=cv2.FILLED)   # comble les trous intérieurs
    return out


def segment_background(img: np.ndarray, thresh: float = 25.0, border_frac: float = 0.05) -> np.ndarray:
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    h, w = lab.shape[:2]
    b = max(2, int(min(h, w) * border_frac))
    border = np.concatenate([lab[:b].reshape(-1, 3), lab[-b:].reshape(-1, 3),
                             lab[:, :b].reshape(-1, 3), lab[:, -b:].reshape(-1, 3)])
    bg = np.median(border, axis=0)
    dist = np.linalg.norm(lab - bg, axis=2)
    mask = (dist > thresh).astype(np.uint8) * 255
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    return _largest_blob_filled(mask)


def segment_grabcut(img: np.ndarray, rect_frac: float = 0.7, iters: int = 5, max_side: int = 640) -> np.ndarray:
    h, w = img.shape[:2]
    f = min(1.0, max_side / max(h, w))
    small = cv2.resize(img, (int(w * f), int(h * f)), interpolation=cv2.INTER_AREA) if f < 1 else img
    sh, sw = small.shape[:2]
    mx, my = int(sw * (1 - rect_frac) / 2), int(sh * (1 - rect_frac) / 2)
    rect = (mx, my, sw - 2 * mx, sh - 2 * my)
    gc = np.zeros(small.shape[:2], np.uint8)
    cv2.grabCut(small, gc, rect, np.zeros((1, 65)), np.zeros((1, 65)), iters, cv2.GC_INIT_WITH_RECT)
    m = np.where((gc == cv2.GC_FGD) | (gc == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
    m = _largest_blob_filled(m)
    return cv2.resize(m, (w, h), interpolation=cv2.INTER_NEAREST) if f < 1 else m


def add_marker(mask: np.ndarray, img: np.ndarray, marker_id: int, dictionary: str, grow: float = 1.6) -> np.ndarray:
    """Ajoute le marqueur (agrandi) au masque : il aide COLMAP à recaler les images."""
    c = detect_markers(img, dictionary).get(marker_id)
    if c is None:
        return mask
    center = c.mean(axis=0)
    poly = (center + (c - center) * grow).astype(np.int32)
    out = mask.copy()
    cv2.fillConvexPoly(out, poly, 255)
    return out


def write_masks(images_dir: str | Path, masks_dir: str | Path, method: str = "background",
                marker_id: int | None = None, dictionary: str = "DICT_4X4_50",
                preview_dir: str | Path | None = None, **kw) -> int:
    """Écrit `<image>.png` (convention COLMAP) pour chaque image ; renvoie leur nombre.

    `preview_dir` reçoit des aperçus (hors masque assombri) pour contrôler le détourage à l'œil.
    """
    fn = {"background": segment_background, "grabcut": segment_grabcut}[method]
    images_dir, masks_dir = Path(images_dir), Path(masks_dir)
    n = 0
    for path in sorted(images_dir.rglob("*")):
        if path.suffix.lower() not in IMG_EXT:
            continue
        img = cv2.imread(str(path))
        if img is None:
            continue
        mask = fn(img, **kw)
        if marker_id is not None:
            mask = add_marker(mask, img, marker_id, dictionary)
        rel = path.relative_to(images_dir)
        out = masks_dir / (str(rel) + ".png")
        out.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(out), mask)
        if preview_dir is not None:
            prev = (img * 0.25 + img * 0.75 * (mask[..., None] > 0)).astype(np.uint8)
            pout = Path(preview_dir) / (str(rel.with_suffix("")) + ".jpg")
            pout.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(pout), cv2.resize(prev, None, fx=0.4, fy=0.4) if max(prev.shape) > 1200 else prev)
        n += 1
    return n
