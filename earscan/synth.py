"""Lot d'images synthétiques d'une oreille stylisée, avec cheveux, marqueur ArUco et vérité terrain.

    python -m earscan.synth --out synth/ --views 48 --hair medium --seed 1

Sorties :
  images/view_000.jpg ...        photos simulées (fond bleu uni, ombrage, bruit, flou léger)
  truth/ear_silhouette/*.png     masque de l'oreille entière (cheveux ignorés)
  truth/ear_visible/*.png        oreille visible, cheveux retirés
  truth/hair/*.png               pixels de cheveux
  model/cameras.txt, images.txt  poses exactes au format COLMAP (unités = mm x --model-unit)
  reference_ear_mm.ply           surface de référence de l'oreille, en mm, étanche
  params.json                    paramètres et attendu (échelle à retrouver)

L'oreille est une forme stylisée (hélix, anti-hélix, conque, tragus, lobe) : elle sert à tester la
chaîne, pas à représenter une anatomie réelle. Le rendu est un lancer de triangles Lambert, sans GL.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import numpy as np
import trimesh

HAIR_STRANDS = {"none": 0, "light": 40, "medium": 120, "heavy": 260}
HAIR_COLORS = [(20, 30, 45), (15, 15, 18), (35, 60, 100), (28, 45, 70)]   # BGR : brun, noir, châtain, brun clair
BACKDROP = (160, 90, 30)    # papier bleu (BGR)
SKIN = np.array([140, 165, 225], float)   # BGR
MARKER_ID, MARKER_MM, QUIET_MM = 7, 20.0, 5.0
MARKER_CENTER = np.array([-48.0, -8.0])


def ear_height(u, v):
    """Hauteur (mm) de l'oreille stylisée en (u, v) ; 0 hors de l'oreille. u : largeur, v : hauteur."""
    a = 15.0 + 4.0 * (v + 31.0) / 62.0                       # plus large en haut
    r2 = (u / a) ** 2 + (v / 31.0) ** 2
    inside = r2 < 1.0
    r = np.sqrt(np.clip(r2, 0, 1))
    h = 9.0 * np.sqrt(np.clip(1.0 - r2, 0, None))             # dôme de base
    h += 3.5 * np.exp(-(((1 - r) / 0.09) ** 2)) * inside      # bourrelet de l'hélix
    h -= 5.5 * np.exp(-(((u + 2) / 7.0) ** 2 + ((v + 4) / 9.0) ** 2))   # conque
    h += 2.8 * np.exp(-(((u - 4.5) / 3.2) ** 2)) * np.exp(-(((v - 8) / 14.0) ** 2))   # anti-hélix
    h += 4.5 * np.exp(-(((u + 13) / 3.2) ** 2 + ((v + 6) / 3.2) ** 2))  # tragus
    h += 3.0 * np.exp(-((u / 8.0) ** 2 + ((v + 24) / 6.0) ** 2))        # lobe
    return np.where(inside, np.clip(h, 0.15, None), 0.0)


def ear_mesh(step: float = 0.45) -> trimesh.Trimesh:
    us = np.arange(-20, 20 + step, step)
    vs = np.arange(-32, 32 + step, step)
    U, V = np.meshgrid(us, vs)
    H = ear_height(U, V)
    nu, nv = len(us), len(vs)
    idx = np.arange(nu * nv).reshape(nv, nu)
    faces = []
    for j in range(nv - 1):
        for i in range(nu - 1):
            if (H[j:j + 2, i:i + 2] > 0).all():
                a, b, c, d = idx[j, i], idx[j, i + 1], idx[j + 1, i + 1], idx[j + 1, i]
                faces += [[a, b, c], [a, c, d]]
    m = trimesh.Trimesh(np.c_[U.ravel(), V.ravel(), H.ravel()], faces, process=False)
    m.remove_unreferenced_vertices()
    return m


def _look_at(center, target):
    f = target - center
    f /= np.linalg.norm(f)
    r = np.cross(f, [0, 1.0, 0])
    r /= np.linalg.norm(r)
    d = np.cross(f, r)
    return np.vstack([r, d, f])        # monde -> caméra (x droite, y bas, z avant)


def _hair(rng, n, density_scale=1.0):
    """Mèches 3D : points (k, 3) en mm, épaisseur mm, couleur BGR."""
    out = []
    for _ in range(n):
        u0 = rng.uniform(-19, 19)
        v0 = rng.uniform(28, 38)
        length = rng.uniform(15, 45) * density_scale
        sway, phase, freq = rng.uniform(1, 5), rng.uniform(0, 6.28), rng.uniform(0.6, 1.8)
        drift = rng.uniform(-8, 8)
        t = np.linspace(0, 1, 18)
        u = u0 + sway * np.sin(2 * np.pi * freq * t + phase) + drift * t
        v = v0 - length * t
        z = ear_height(u, v) + rng.uniform(1.0, 3.5) + 3 * (1 - t)
        out.append((np.c_[u, v, z], rng.uniform(0.35, 0.9), HAIR_COLORS[rng.integers(len(HAIR_COLORS))]))
    return out


def _marker_image():
    d = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    m = cv2.aruco.generateImageMarker(d, MARKER_ID, 200)
    return cv2.copyMakeBorder(m, 60, 60, 60, 60, cv2.BORDER_CONSTANT, value=255)


def generate(out_dir: str | Path, views: int = 48, hair: str = "medium", seed: int = 1,
             size: tuple[int, int] = (1280, 960), model_unit: float = 0.1, distance: float = 190.0,
             hair_scale: float = 1.0) -> dict:
    out = Path(out_dir)
    for sub in ("images", "truth/ear_silhouette", "truth/ear_visible", "truth/hair", "model"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    W, H = size
    F = 1.15 * W                                         # focale en pixels
    mesh = ear_mesh()
    v3, faces = mesh.vertices, mesh.faces
    normals = mesh.face_normals
    face_center = v3[faces].mean(axis=1)
    strands = _hair(rng, HAIR_STRANDS[hair], hair_scale)
    skin_texture = 1.0 + 0.05 * rng.standard_normal(len(faces))   # grain de peau, fixe d'une vue à l'autre
    height_dark = 0.78 + 0.22 * np.clip(face_center[:, 2] / 11.0, 0, 1)   # creux plus sombres
    marker = _marker_image()
    hm = MARKER_MM / 2
    mk = np.array([[-hm, hm, 0], [hm, hm, 0], [hm, -hm, 0], [-hm, -hm, 0]]) + [*MARKER_CENTER, 0]
    n_p = 60
    target = np.array([0, 0, 5.0])
    cam_lines, img_lines = [], ["# IMAGE_ID, QW, QX, QY, QZ, TX, TY, TZ, CAMERA_ID, NAME"]

    elevations = [48.0, 72.0]
    per_arc = int(np.ceil(views / len(elevations)))
    k = 0
    for el in elevations:
        for az in np.linspace(-70, 70, per_arc):
            if k >= views:
                break
            e, a = np.radians(el + rng.normal(0, 2)), np.radians(az + rng.normal(0, 2))
            C = distance * rng.uniform(0.92, 1.08) * np.array([np.sin(a) * np.cos(e), -np.cos(a) * np.cos(e), np.sin(e)])
            R = _look_at(C, target)
            t = -R @ C
            K = np.array([[F, 0, W / 2], [0, F, H / 2], [0, 0, 1]])

            def proj(P):
                c = P @ R.T + t
                return (c[:, :2] / c[:, 2:3]) * F + [W / 2 - 0.5, H / 2 - 0.5], c[:, 2]   # convention pixels OpenCV

            img = np.empty((H, W, 3), np.float32)
            img[:] = BACKDROP
            gy, gx = np.mgrid[0:H, 0:W]
            img *= (1.0 - 0.12 * (((gx - W / 2) / W) ** 2 + ((gy - H / 2) / H) ** 2) * 2)[..., None]   # vignettage

            # marqueur sur le plan z = 0
            mk_px, _ = proj(mk)
            src = np.array([[n_p, n_p], [260, n_p], [260, 260], [n_p, 260]], np.float32)
            M = cv2.getPerspectiveTransform(src, mk_px.astype(np.float32))
            warped = cv2.warpPerspective(marker, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=-1)
            pad = np.array([[0, 0], [260 + n_p, 0], [260 + n_p, 260 + n_p], [0, 260 + n_p]], np.float32)
            quiet = np.zeros((H, W), np.uint8)
            cv2.fillConvexPoly(quiet, cv2.perspectiveTransform(pad[None], M)[0].astype(np.int32), 1)
            region = quiet > 0
            img[region] = warped[region][:, None].repeat(3, 1)

            # oreille : triangles triés du plus loin au plus proche
            px, depth = proj(v3)
            order = np.argsort(-depth[faces].mean(axis=1))
            light = np.array([-0.65, 0.45, 0.6]) + 0.25 * (C / np.linalg.norm(C))   # éclairage oblique
            light /= np.linalg.norm(light)
            shade = (0.22 + 0.78 * np.clip(normals @ light, 0, 1)) * height_dark * skin_texture
            silhouette = np.zeros((H, W), np.uint8)
            for fi in order:
                poly = px[faces[fi]].astype(np.int32)
                col = tuple(float(c) for c in SKIN * shade[fi])
                cv2.fillConvexPoly(img, poly, col, lineType=cv2.LINE_AA)
                cv2.fillConvexPoly(silhouette, poly, 255)
            silhouette = cv2.morphologyEx(silhouette, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))

            # cheveux : devant l'oreille (au-dessus de sa surface)
            hair_mask = np.zeros((H, W), np.uint8)
            for pts, thick, col in strands:
                p2, z = proj(pts)
                th = max(1, int(round(thick * F / z.mean())))
                cv2.polylines(img, [p2.astype(np.int32)], False, col, th, cv2.LINE_AA)
                cv2.polylines(hair_mask, [p2.astype(np.int32)], False, 255, th)
            visible = cv2.bitwise_and(silhouette, cv2.bitwise_not(hair_mask))

            img = cv2.GaussianBlur(img, (0, 0), 0.8)
            img = np.clip(img + rng.normal(0, 3.0, img.shape), 0, 255).astype(np.uint8)
            name = f"view_{k:03d}"
            cv2.imwrite(str(out / "images" / f"{name}.jpg"), img, [cv2.IMWRITE_JPEG_QUALITY, 90])
            cv2.imwrite(str(out / "truth/ear_silhouette" / f"{name}.png"), silhouette)
            cv2.imwrite(str(out / "truth/ear_visible" / f"{name}.png"), visible)
            cv2.imwrite(str(out / "truth/hair" / f"{name}.png"), hair_mask)

            q = _quat(R)
            tm = t * model_unit
            img_lines += [f"{k + 1} {q[0]} {q[1]} {q[2]} {q[3]} {tm[0]} {tm[1]} {tm[2]} 1 images/{name}.jpg".replace("images/", ""), ""]
            k += 1

    (out / "model" / "cameras.txt").write_text(f"# c\n1 SIMPLE_RADIAL {W} {H} {F} {W / 2} {H / 2} 0.0\n")
    (out / "model" / "images.txt").write_text("\n".join(img_lines) + "\n")
    mesh.export(out / "reference_ear_mm.ply")
    from .clean import close_boundaries
    close_boundaries(mesh).export(out / "reference_ear_mm.ply")
    params = {"views": k, "hair": hair, "seed": seed, "size": size, "marker_id": MARKER_ID,
              "marker_size_mm": MARKER_MM, "model_unit": model_unit,
              "expected_scale_to_mm": 1.0 / model_unit, "units_in_model": "mm x model_unit"}
    (out / "params.json").write_text(json.dumps(params, indent=2))
    return params


def _quat(R):
    from scipy.spatial.transform import Rotation
    x, y, z, w = Rotation.from_matrix(R).as_quat()
    return w, x, y, z


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", required=True)
    p.add_argument("--views", type=int, default=48)
    p.add_argument("--hair", choices=list(HAIR_STRANDS), default="medium")
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--width", type=int, default=1280)
    p.add_argument("--height", type=int, default=960)
    p.add_argument("--model-unit", type=float, default=0.1,
                   help="unité du modèle COLMAP simulé : 1 mm = cette valeur (échelle à retrouver = 1/valeur)")
    a = p.parse_args(argv)
    print(json.dumps(generate(a.out, a.views, a.hair, a.seed, (a.width, a.height), a.model_unit), indent=2))


if __name__ == "__main__":
    main()
