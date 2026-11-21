"""Ligne de commande : python -m earscan {reconstruct,evaluate} ..."""
from __future__ import annotations

import argparse
import json

import trimesh

from .evaluate import evaluate
from .pipeline import reconstruct


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

    e = sub.add_parser("evaluate", help="écart d'un maillage à une référence (mm)")
    e.add_argument("mesh")
    e.add_argument("reference")
    e.add_argument("--trim", type=float, default=1.0, help="fraction de points retenue (scan partiel < 1)")

    a = p.parse_args(argv)
    if a.cmd == "reconstruct":
        out = reconstruct(a.images, a.out, a.marker_id, a.marker_size_mm, a.colmap, a.cpu,
                          a.sparse_only, a.dictionary)
        print(json.dumps(out, indent=2))
    else:
        rep = evaluate(trimesh.load(a.mesh, force="mesh"), trimesh.load(a.reference, force="mesh"),
                       trim=a.trim)
        print(json.dumps({k: (v.tolist() if hasattr(v, "tolist") else v) for k, v in rep.__dict__.items()},
                         indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
