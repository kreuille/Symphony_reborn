import cv2
import numpy as np
import pytest
import trimesh
from scipy.spatial.transform import Rotation

from earscan.colmap_io import qvec_to_rotmat, read_cameras_text, read_images_text
from earscan.evaluate import evaluate
from earscan.pipeline import build_commands, clean_mesh
from earscan.scale import ScaleError, estimate_scale_from_model

W, H, F = 640, 480, 800.0
SIDE_MODEL = 10.0  # côté du marqueur dans le repère (arbitraire) du modèle


def _pose(center):
    """Caméra COLMAP (x droite, y bas, z avant) regardant l'origine."""
    c = np.asarray(center, float)
    z = -c / np.linalg.norm(c)
    x = np.cross([0, 0, -1.0], z)
    x /= np.linalg.norm(x)
    y = np.cross(z, x)
    R = np.vstack([x, y, z])
    return R, -R @ c


def _render(R, t, marker_img):
    h = SIDE_MODEL / 2
    world = np.array([[-h, h, 0], [h, h, 0], [h, -h, 0], [-h, -h, 0]], float)  # HG, HD, BD, BG
    cam = world @ R.T + t
    uv = (cam[:, :2] / cam[:, 2:3]) * F + [W / 2, H / 2]          # convention COLMAP (centre pixel = +0.5)
    dst = (uv - 0.5).astype(np.float32)                            # convention OpenCV
    n = marker_img.shape[0]
    p = 60
    src = np.array([[p, p], [n - p, p], [n - p, n - p], [p, n - p]], np.float32)
    M = cv2.getPerspectiveTransform(src, dst)
    return cv2.warpPerspective(marker_img, M, (W, H), borderValue=128)


def _write_model(tmp_path, centers, marker_id=7, drop_marker=False):
    d = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    m = cv2.aruco.generateImageMarker(d, marker_id, 200)
    m = cv2.copyMakeBorder(m, 60, 60, 60, 60, cv2.BORDER_CONSTANT, value=255)
    imgs = tmp_path / "images"
    imgs.mkdir()
    model = tmp_path / "model"
    model.mkdir()
    (model / "cameras.txt").write_text(f"# c\n1 SIMPLE_RADIAL {W} {H} {F} {W/2} {H/2} 0.0\n")
    lines = ["# images"]
    for i, c in enumerate(centers, 1):
        R, t = _pose(c)
        frame = _render(R, t, m if not drop_marker else np.full_like(m, 255))
        cv2.imwrite(str(imgs / f"{i}.png"), frame)
        q = Rotation.from_matrix(R).as_quat()                      # (x, y, z, w)
        lines.append(f"{i} {q[3]} {q[0]} {q[1]} {q[2]} {t[0]} {t[1]} {t[2]} 1 {i}.png")
        lines.append("")                                           # ligne de points 2D vide
    (model / "images.txt").write_text("\n".join(lines) + "\n")
    return model, imgs


CENTERS = [(15, -20, 25), (-18, -15, 24), (0, 22, 26), (20, 18, 22)]


def test_qvec_roundtrip():
    R = Rotation.from_euler("xyz", [20, -35, 70], degrees=True)
    q = R.as_quat()
    assert np.allclose(qvec_to_rotmat((q[3], q[0], q[1], q[2])), R.as_matrix(), atol=1e-12)


def test_read_model(tmp_path):
    model, _ = _write_model(tmp_path, CENTERS)
    cams, imgs = read_cameras_text(model / "cameras.txt"), read_images_text(model / "images.txt")
    assert cams[1].model == "SIMPLE_RADIAL" and cams[1].width == W
    assert len(imgs) == 4 and imgs[2].name == "2.png"


def test_scale_from_marker(tmp_path):
    model, imgs = _write_model(tmp_path, CENTERS)
    est = estimate_scale_from_model(model, imgs, marker_id=7, marker_size_mm=25.0)
    assert est.n_views == 4
    assert est.scale == pytest.approx(25.0 / SIDE_MODEL, rel=0.01)
    assert est.spread < 0.02


def test_scale_needs_two_views(tmp_path):
    model, imgs = _write_model(tmp_path, CENTERS)
    with pytest.raises(ScaleError):
        estimate_scale_from_model(model, imgs, marker_id=3, marker_size_mm=25.0)  # mauvais identifiant


def test_scale_without_marker(tmp_path):
    model, imgs = _write_model(tmp_path, CENTERS, drop_marker=True)
    with pytest.raises(ScaleError):
        estimate_scale_from_model(model, imgs, marker_id=7, marker_size_mm=25.0)


def _ear_like():
    """Ellipsoïde asymétrique (axes 30, 20, 12 mm) avec une bosse : pas de symétrie qui trompe l'ICP."""
    m = trimesh.creation.icosphere(subdivisions=4)
    v = m.vertices * [30, 20, 12]
    bump = np.exp(-(((v[:, 0] - 18) / 8) ** 2 + ((v[:, 1] - 5) / 8) ** 2 + ((v[:, 2] - 6) / 8) ** 2))
    v = v + m.vertices * (4 * bump)[:, None]
    return trimesh.Trimesh(v, m.faces, process=False)


def _moved(mesh, scale=1.0, noise=0.0, seed=1):
    T = np.eye(4)
    T[:3, :3] = Rotation.from_euler("xyz", [25, -40, 70], degrees=True).as_matrix() * scale
    T[:3, 3] = [12, -7, 30]
    out = mesh.copy()
    out.apply_transform(T)
    if noise:
        out.vertices = out.vertices + np.random.default_rng(seed).normal(0, noise, out.vertices.shape)
    return out


def test_evaluate_identical_surface_after_rigid_motion():
    ref = _ear_like()
    rep = evaluate(_moved(ref), ref)
    assert rep.rms < 0.05 and rep.max < 0.2
    assert rep.scale_error < 0.005


def test_evaluate_measures_noise():
    ref = _ear_like()
    rep = evaluate(_moved(ref, noise=0.3), ref)
    assert 0.2 < rep.rms < 0.4


def test_evaluate_reports_scale_error():
    ref = _ear_like()
    rep = evaluate(_moved(ref, scale=1.03), ref)
    assert rep.scale == pytest.approx(1 / 1.03, rel=0.005)
    assert rep.scale_error == pytest.approx(0.029, abs=0.006)


def test_build_commands_order(tmp_path):
    names = [n for n, _ in build_commands(tmp_path / "img", tmp_path / "w")]
    assert names == ["features", "matching", "mapper", "undistort", "stereo", "fusion", "mesh"]
    names = [n for n, _ in build_commands(tmp_path / "img", tmp_path / "w", sparse_only=True)]
    assert names == ["features", "matching", "mapper"]


def test_clean_mesh_keeps_largest_component():
    big = trimesh.creation.icosphere(subdivisions=3, radius=10)
    small = trimesh.creation.icosphere(subdivisions=1, radius=1)
    small.apply_translation([50, 0, 0])
    cleaned = clean_mesh(trimesh.util.concatenate([big, small]))
    assert len(cleaned.faces) == len(big.faces)
