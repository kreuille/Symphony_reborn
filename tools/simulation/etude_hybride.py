#!/usr/bin/env python3
"""Hybride : retrait motorisé avec centrage + suivi externe, par fusion.

Retrait motorisé centré : décentrage 0,05 mm, inclinaison 0,3°, vitesse constante 3 mm/s (HYPOTHÈSES de centrage et
d'alignement non démontrées, voir docs/conception-scanner.md section 8). Conduit avec coudes, mouvement lissé.
Configurations : suivi du centre seul (gyroscope sur la tête), suivi externe seul (clip), fusion avec plusieurs gains
de recalage sur le suivi externe (un gain faible donne plus de poids au suivi du centre).

Usage : python3 etude_hybride.py [--graines 4] [--sortie fichier.txt]
"""
import argparse
import types
import numpy as np
import simulateur_scanner as S

SCEN = [
    ("Tête immobile", dict(tete=0.0, glissement=0.1, occ=0)),
    ("Tête mobile 1,5 mm / 1,5°, clip glissant de 0,1 mm", dict(tete=1.5, glissement=0.1, occ=0)),
    ("Tête mobile, clip glissant de 0,3 mm", dict(tete=1.5, glissement=0.3, occ=0)),
    ("Tête mobile, clip 0,1 mm, deux occultations du suivi", dict(tete=1.5, glissement=0.1, occ=2)),
]
GAINS = [0.3, 0.1, 0.03, 0.01]


def run(cfg, sc, gain, graines):
    a = types.SimpleNamespace(biais_gyro=0.05, inclinaison=0.3, mouvement="lisse", vitesse=3.0, latence_suivi=0.0,
                              desynchro=0.0, occultation=sc["occ"], bruit_suivi=0.04, erreur_main_pointe=0.05,
                              tete_mm=sc["tete"], tete_deg=sc["tete"], compensation_tete="oui",
                              glissement_clip=sc["glissement"], aberrants=0.0, decentrage=0.05, variation_vitesse=0.0)
    P = S.parametres(a)
    P["fus_pos"] = gain
    canal = S.Canal("realiste")
    r = []
    for g in range(graines):
        tr = S.gen_truth(canal, np.random.default_rng(1000+g), P)
        pe, Re, q = S.run_config(tr, cfg, np.random.default_rng(5000+g), P)
        r.append(S.metriques(canal, tr, pe, Re, q, P)["rms"])
    return float(np.mean(r))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graines", type=int, default=4)
    ap.add_argument("--sortie", default=None)
    args = ap.parse_args()
    L = ["Retrait motorisé centré (décentrage 0,05 mm, inclinaison 0,3°, 3 mm/s constant), conduit avec coudes, %d graines. RMS du nuage (mm)." % args.graines, "",
         "%-58s | %-10s | %-10s | %s" % ("Scénario", "Centre seul", "Suivi seul", " | ".join("Fusion g=%.2f" % g for g in GAINS))]
    for nom, sc in SCEN:
        ec = run("Ec", sc, 0.3, args.graines)
        t = run("T", sc, 0.3, args.graines)
        f = [run("F", sc, g, args.graines) for g in GAINS]
        L.append("%-58s | %-10.3f | %-10.3f | %s" % (nom, ec, t, " | ".join("%-13.3f" % x for x in f)))
        print(L[-1], flush=True)
    if args.sortie:
        open(args.sortie, "w").write("\n".join(L)+"\n")


if __name__ == "__main__":
    main()
