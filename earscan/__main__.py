"""Ligne de commande : python -m earscan {reconstruct,evaluate} ..."""
from __future__ import annotations

import argparse
import json

import trimesh

from .clean import clean_ear
from .evaluate import evaluate
from .pipeline import reconstruct
from .segment import write_masks


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="earscan", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("reconstruct", help="images -> maillage en mm (COLMAP requis)")
    r.add_argument("images", help="dossier des images de capture")
    r.add_argument("--out", required=True, help="dossier de sortie")
    r.add_argument("--marker-id", type=int, required=True, help="identifiant ArUco du marqueur d'échelle")
    r.add_argument("--marker-size-mm", type=float, required=True, help="côté du carré noir, en mm")
    r.add_argument("--dictionary", default="DICT_4X4_50")
    r.add_argument("--colmap", default="colmap", help="exécutable COLMAP")
    r.add_argument("--cpu", action="store_true", help="SIFT sur CPU")
    r.add_argument("--sparse-only", action="store_true", help="poses + échelle seulement (sans CUDA)")
    r.add_argument("--mask", choices=["background", "grabcut"], help="détourer l'oreille dans les photos")
    r.add_argument("--no-crop", action="store_true", help="ne pas retirer plan et fond du maillage")
    r.add_argument("--roi-radius-mm", type=float, help="ne garder que le disque de ce rayon autour du marqueur")
    r.add_argument("--smooth", type=int, default=10, help="itérations de lissage (0 = aucun)")
    r.add_argument("--poisson-trim", type=float, help="seuil de découpe du maillage de Poisson (défaut COLMAP : 7)")

    m = sub.add_parser("masks", help="écrit les masques de détourage et leurs aperçus, sans reconstruire")
    m.add_argument("images")
    m.add_argument("--out", required=True)
    m.add_argument("--method", choices=["background", "grabcut"], default="background")
    m.add_argument("--marker-id", type=int, help="garder le marqueur dans les masques")

    c = sub.add_parser("clean", help="nettoie un maillage déjà reconstruit (plan, fond, îlots, lissage)")
    c.add_argument("mesh")
    c.add_argument("--out", required=True)
    c.add_argument("--report", help="report.json d'une reconstruction : donne le plan du marqueur")
    c.add_argument("--roi-radius-mm", type=float)
    c.add_argument("--smooth", type=int, default=10)
    c.add_argument("--margin-mm", type=float, default=1.0, help="hauteur coupée au-dessus du plan")

    e = sub.add_parser("evaluate", help="écart d'un maillage à une référence (mm)")
    e.add_argument("mesh")
    e.add_argument("reference")
    e.add_argument("--trim", type=float, default=1.0, help="fraction de points retenue (scan partiel < 1)")

    a = p.parse_args(argv)
    if a.cmd == "reconstruct":
        out = reconstruct(a.images, a.out, a.marker_id, a.marker_size_mm, a.colmap, a.cpu,
                          a.sparse_only, a.dictionary, a.mask, not a.no_crop, a.roi_radius_mm,
                          a.smooth, a.poisson_trim)
        print(json.dumps(out, indent=2))
    elif a.cmd == "masks":
        from pathlib import Path
        n = write_masks(a.images, a.out, a.method, a.marker_id, preview_dir=Path(a.out) / "preview")
        print(f"{n} masques dans {a.out} ; aperçus dans {Path(a.out) / 'preview'}")
    elif a.cmd == "clean":
        origin = up = None
        if a.report:
            rep = json.load(open(a.report))
            origin, up = rep.get("plane_origin_mm"), rep.get("plane_up")
        mesh = trimesh.load(a.mesh, force="mesh")
        out = clean_ear(mesh, origin, up, center=origin, margin_mm=a.margin_mm,
                        radius_mm=a.roi_radius_mm, smooth_iters=a.smooth)
        out.export(a.out)
        print(f"{len(mesh.faces)} -> {len(out.faces)} faces ; étanche : {out.is_watertight} ; "
              f"dimensions (mm) : {[round(float(v), 1) for v in out.extents]}")
    else:
        rep = evaluate(trimesh.load(a.mesh, force="mesh"), trimesh.load(a.reference, force="mesh"),
                       trim=a.trim)
        print(json.dumps({k: (v.tolist() if hasattr(v, "tolist") else v) for k, v in rep.__dict__.items()},
                         indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
