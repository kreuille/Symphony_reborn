"""Génère un marqueur ArUco en SVG à taille exacte (mm), avec zone blanche, prêt à imprimer.

    python -m earscan.make_marker --id 7 --size-mm 20 --out earscan/marker_7_20mm.svg
"""
from __future__ import annotations

import argparse

import cv2
import numpy as np


def marker_bits(marker_id: int, dictionary: str = "DICT_4X4_50") -> np.ndarray:
    """Grille de cellules (1 = noir) bordure noire comprise, ex. 6x6 pour un 4x4."""
    d = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, dictionary))
    n = d.markerSize + 2
    img = cv2.aruco.generateImageMarker(d, marker_id, n, borderBits=1)
    return (img < 128).astype(int)


def marker_svg(marker_id: int, size_mm: float, quiet_mm: float = 5.0, dictionary: str = "DICT_4X4_50") -> str:
    bits = marker_bits(marker_id, dictionary)
    n = bits.shape[0]
    cell = size_mm / n
    total = size_mm + 2 * quiet_mm
    rects = "".join(
        f'<rect x="{quiet_mm + x * cell:.4f}" y="{quiet_mm + y * cell:.4f}" width="{cell:.4f}" height="{cell:.4f}"/>'
        for y in range(n) for x in range(n) if bits[y, x])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{total}mm" height="{total}mm" '
            f'viewBox="0 0 {total} {total}"><rect width="{total}" height="{total}" fill="white"/>'
            f'<g fill="black">{rects}</g></svg>\n')


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--id", type=int, required=True)
    p.add_argument("--size-mm", type=float, default=20.0, help="côté du carré noir")
    p.add_argument("--quiet-mm", type=float, default=5.0, help="marge blanche autour")
    p.add_argument("--dictionary", default="DICT_4X4_50")
    p.add_argument("--out", required=True)
    a = p.parse_args()
    open(a.out, "w").write(marker_svg(a.id, a.size_mm, a.quiet_mm, a.dictionary))


if __name__ == "__main__":
    main()
