#!/usr/bin/env python3
"""Exporte en STL un fantôme de conduit auditif (tube creux) à imprimer, à partir des conduits du simulateur.

Usage : python3 exporter_fantome.py --conduit realiste --sortie fantome_coudes.stl [--elargir 1.0] [--longueur 32] [--epaisseur 2.5]

Le conduit est la surface interne ; la paroi extérieure est décalée de l'épaisseur indiquée.
Les deux extrémités sont des couronnes planes (surface fermée, étanche). Unités : mm.
"""
import argparse
import os
import sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "simulation"))
from simulateur_scanner import Canal  # noqa: E402


def anneaux(canal, longueur, ds, ntheta, elargir, ajout):
    s_vals = np.arange(0.0, longueur+1e-9, ds)
    th = 2*np.pi*np.arange(ntheta)/ntheta
    P = np.zeros((len(s_vals), ntheta, 3))
    for a, sv in enumerate(s_vals):
        i = int(canal.index(sv))
        r = canal.R[i]*(1+canal.e[i]*np.cos(2*(th-canal.phie[i]))) + elargir + ajout
        P[a] = canal.c[i] + r[:, None]*(np.cos(th)[:, None]*canal.N[i] + np.sin(th)[:, None]*canal.B[i])
    return P


def triangles(Pin, Pout):
    n_s, n_t, _ = Pin.shape
    tris = []
    for a in range(n_s-1):
        for j in range(n_t):
            j2 = (j+1) % n_t
            # paroi interne (normale vers l'axe) : ordre inversé
            tris.append((Pin[a, j], Pin[a+1, j], Pin[a, j2]))
            tris.append((Pin[a, j2], Pin[a+1, j], Pin[a+1, j2]))
            # paroi externe (normale vers l'extérieur)
            tris.append((Pout[a, j], Pout[a, j2], Pout[a+1, j]))
            tris.append((Pout[a, j2], Pout[a+1, j2], Pout[a+1, j]))
    for a, sens in ((0, 1), (n_s-1, -1)):
        for j in range(n_t):
            j2 = (j+1) % n_t
            if sens == 1:   # extrémité de départ : normale vers -s
                tris.append((Pin[a, j], Pout[a, j2], Pout[a, j]))
                tris.append((Pin[a, j], Pin[a, j2], Pout[a, j2]))
            else:           # extrémité de fin : normale vers +s
                tris.append((Pin[a, j], Pout[a, j], Pout[a, j2]))
                tris.append((Pin[a, j], Pout[a, j2], Pin[a, j2]))
    return np.array(tris)


def triangles_noyau(Pin):
    """Noyau plein (la lumière du conduit) : pour mouler du silicone autour, puis retirer le noyau."""
    n_s, n_t, _ = Pin.shape
    tris = []
    for a in range(n_s-1):
        for j in range(n_t):
            j2 = (j+1) % n_t
            tris.append((Pin[a, j], Pin[a, j2], Pin[a+1, j]))
            tris.append((Pin[a, j2], Pin[a+1, j2], Pin[a+1, j]))
    for a, sens in ((0, 1), (n_s-1, -1)):
        ctr = Pin[a].mean(0)
        for j in range(n_t):
            j2 = (j+1) % n_t
            tris.append((ctr, Pin[a, j2], Pin[a, j]) if sens == 1 else (ctr, Pin[a, j], Pin[a, j2]))
    return np.array(tris)


def ecrire_stl(tris, chemin, nom):
    with open(chemin, "w") as f:
        f.write("solid %s\n" % nom)
        for t in tris:
            n = np.cross(t[1]-t[0], t[2]-t[0])
            nn = np.linalg.norm(n)
            n = n/nn if nn > 0 else n
            f.write(" facet normal %.6e %.6e %.6e\n  outer loop\n" % tuple(n))
            for v in t:
                f.write("   vertex %.5f %.5f %.5f\n" % tuple(v))
            f.write("  endloop\n endfacet\n")
        f.write("endsolid %s\n" % nom)


def verifier_etanche(tris, tol=1e-4):
    """Chaque arête doit être partagée par exactement deux triangles, orientées en sens opposés."""
    cle = lambda v: tuple(np.round(v/tol).astype(np.int64))
    aretes = {}
    for t in tris:
        k = [cle(v) for v in t]
        for a, b in ((0, 1), (1, 2), (2, 0)):
            aretes[(k[a], k[b])] = aretes.get((k[a], k[b]), 0) + 1
    mauvais = 0
    for (a, b), c in aretes.items():
        if c != 1 or aretes.get((b, a), 0) != 1:
            mauvais += 1
    return mauvais


def volume(tris):
    return np.sum(np.einsum('ij,ij->i', tris[:, 0], np.cross(tris[:, 1], tris[:, 2])))/6.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--conduit", default="droit_conique", choices=["droit_cylindre", "droit_conique", "realiste"])
    ap.add_argument("--longueur", type=float, default=32.0, help="longueur du conduit, mm")
    ap.add_argument("--epaisseur", type=float, default=2.5, help="épaisseur de paroi, mm")
    ap.add_argument("--elargir", type=float, default=0.0, help="rayon ajouté au conduit, mm (pour laisser passer la sonde)")
    ap.add_argument("--noyau", action="store_true", help="exporte le noyau plein (la lumière) pour mouler du silicone")
    ap.add_argument("--sortie", required=True)
    args = ap.parse_args()
    canal = Canal(args.conduit)
    Pin = anneaux(canal, args.longueur, 0.5, 72, args.elargir, 0.0)
    Pout = anneaux(canal, args.longueur, 0.5, 72, args.elargir, args.epaisseur)
    tris = triangles_noyau(Pin) if args.noyau else triangles(Pin, Pout)
    ecrire_stl(tris, args.sortie, args.conduit)
    print("%d triangles ; arêtes non étanches : %d ; volume de matière : %.0f mm3 (doit être > 0)"
          % (len(tris), verifier_etanche(tris), volume(tris)))
    rin = np.linalg.norm(Pin[:, :, :] - Pin.mean(1)[:, None, :], axis=2).mean(1)
    print("rayon interne moyen : %.2f mm (entrée) à %.2f mm (fond)" % (rin[0], rin[-1]))


if __name__ == "__main__":
    main()
