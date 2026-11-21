"""Chaîne de reconstruction : COLMAP (SfM + MVS), mise à l'échelle par marqueur, nettoyage, export.

La densification (patch_match_stereo) demande COLMAP compilé avec CUDA. Sans GPU, `sparse_only=True`
permet de valider la pose des caméras et l'échelle sans produire de maillage.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import asdict
from pathlib import Path

import trimesh

from .scale import ScaleEstimate, estimate_scale_from_model


def build_commands(images_dir: Path, work: Path, colmap_bin: str = "colmap", cpu: bool = False,
                   sparse_only: bool = False) -> list[tuple[str, list[str]]]:
    """Commandes COLMAP dans l'ordre d'exécution (chaque élément : nom, argv)."""
    db, sparse, dense = work / "database.db", work / "sparse", work / "dense"
    # Options CPU : noms valables pour COLMAP <= 3.11 ; renommés FeatureExtraction/FeatureMatching ensuite.
    cpu_extract = ["--SiftExtraction.use_gpu", "0"] if cpu else []
    cpu_match = ["--SiftMatching.use_gpu", "0"] if cpu else []
    cmds = [
        ("features", [colmap_bin, "feature_extractor", "--database_path", str(db),
                      "--image_path", str(images_dir), "--ImageReader.single_camera", "1",
                      "--ImageReader.camera_model", "SIMPLE_RADIAL", *cpu_extract]),
        ("matching", [colmap_bin, "exhaustive_matcher", "--database_path", str(db), *cpu_match]),
        ("mapper", [colmap_bin, "mapper", "--database_path", str(db),
                    "--image_path", str(images_dir), "--output_path", str(sparse)]),
    ]
    if not sparse_only:
        cmds += [
            ("undistort", [colmap_bin, "image_undistorter", "--image_path", str(images_dir),
                           "--input_path", str(sparse / "0"), "--output_path", str(dense),
                           "--output_type", "COLMAP"]),
            ("stereo", [colmap_bin, "patch_match_stereo", "--workspace_path", str(dense)]),
            ("fusion", [colmap_bin, "stereo_fusion", "--workspace_path", str(dense),
                        "--output_path", str(dense / "fused.ply")]),
            ("mesh", [colmap_bin, "poisson_mesher", "--input_path", str(dense / "fused.ply"),
                      "--output_path", str(dense / "meshed-poisson.ply")]),
        ]
    return cmds


def _largest_model(sparse: Path) -> Path:
    """Parmi les modèles produits par le mapper, celui qui a recalé le plus d'images."""
    models = [d for d in sparse.iterdir() if (d / "images.bin").exists()]
    if not models:
        raise RuntimeError("COLMAP n'a produit aucun modèle : trop peu de recouvrement entre les images ?")
    return max(models, key=lambda d: (d / "images.bin").stat().st_size)


def clean_mesh(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    """Garde la plus grande composante connexe (retire les îlots de fond)."""
    parts = mesh.split(only_watertight=False)
    return max(parts, key=lambda m: len(m.faces)) if parts else mesh


def reconstruct(images_dir: str | Path, out_dir: str | Path, marker_id: int, marker_size_mm: float,
                colmap_bin: str = "colmap", cpu: bool = False, sparse_only: bool = False,
                dictionary: str = "DICT_4X4_50") -> dict:
    images_dir, out_dir = Path(images_dir).resolve(), Path(out_dir).resolve()
    if shutil.which(colmap_bin) is None:
        raise RuntimeError(f"COLMAP introuvable ({colmap_bin}) : installer COLMAP ou donner --colmap")
    work = out_dir / "work"
    (work / "sparse").mkdir(parents=True, exist_ok=True)

    for name, argv in build_commands(images_dir, work, colmap_bin, cpu, sparse_only):
        print(f"[earscan] {name}", flush=True)
        if name == "undistort":  # le modèle utilisé est le plus grand, pas forcément « 0 »
            best = _largest_model(work / "sparse")
            argv[argv.index("--input_path") + 1] = str(best)
        subprocess.run(argv, check=True)
        if name == "mapper":
            best = _largest_model(work / "sparse")
            txt = work / "sparse_txt"
            txt.mkdir(exist_ok=True)
            subprocess.run([colmap_bin, "model_converter", "--input_path", str(best),
                            "--output_path", str(txt), "--output_type", "TXT"], check=True)

    est: ScaleEstimate = estimate_scale_from_model(work / "sparse_txt", images_dir, marker_id,
                                                   marker_size_mm, dictionary=dictionary)
    report = {"scale_to_mm": est.scale, "marker_views": est.n_views,
              "marker_sides_model": est.side_model, "marker_spread": est.spread,
              "sparse_only": sparse_only}
    if not sparse_only:
        mesh = clean_mesh(trimesh.load(work / "dense" / "meshed-poisson.ply", force="mesh"))
        mesh.apply_scale(est.scale)
        mesh.export(out_dir / "ear_mm.ply")
        mesh.export(out_dir / "ear_mm.stl")
        report.update(watertight=bool(mesh.is_watertight), faces=int(len(mesh.faces)),
                      extents_mm=[float(v) for v in mesh.extents])
    (out_dir / "report.json").write_text(json.dumps(report, indent=2))
    return report
