#!/usr/bin/env python3
"""Fusion adaptative (filtre de Kalman) du suivi du centre de la lumière et du suivi externe.

Chaque axe a deux états : l'erreur de l'estime (marche aléatoire) et l'erreur lente du suivi externe (processus à
mémoire de 2 s : glissement du clip, dérive, biais main-pointe). L'amplitude de l'erreur du suivi est adaptée en ligne
d'après la cohérence des innovations (NIS). Paramètres fixes dans tous les scénarios : dérive de l'estime 0,01 mm par
image, amplitude initiale de l'erreur du suivi 0,1 mm, mémoire 2 s, bruit du suivi 0,04 mm, adaptation lente.
Comparaison avec le suivi du centre seul, le suivi externe seul et deux gains fixes de recalage.

Usage : python3 etude_fusion_adaptative.py [--graines 4] [--sortie fichier.txt]
"""
import argparse
import types
import numpy as np
import simulateur_scanner as S

MOTOR = dict(inclinaison=0.3, vitesse=3.0, decentrage=0.05, variation_vitesse=0.0)
LIBRE = dict(inclinaison=2.0, vitesse=5.0, decentrage=0.3, variation_vitesse=0.3)
SCEN = [
    ("Motorisé, tête immobile", MOTOR, dict(tete=0.0, glissement=0.1, occ=0, ab=0.0)),
    ("Motorisé, tête mobile, clip glissant de 0,1 mm", MOTOR, dict(tete=1.5, glissement=0.1, occ=0, ab=0.0)),
    ("Motorisé, tête mobile, clip glissant de 0,3 mm", MOTOR, dict(tete=1.5, glissement=0.3, occ=0, ab=0.0)),
    ("Motorisé, tête mobile, clip 0,1 mm, deux occultations", MOTOR, dict(tete=1.5, glissement=0.1, occ=2, ab=0.0)),
    ("Motorisé, tête mobile, clip 0,1 mm, aberrants 3 %", MOTOR, dict(tete=1.5, glissement=0.1, occ=0, ab=0.03)),
    ("Main libre, tête mobile, clip glissant de 0,1 mm", LIBRE, dict(tete=1.5, glissement=0.1, occ=0, ab=0.0)),
    ("Main libre, tête mobile, clip glissant de 0,3 mm", LIBRE, dict(tete=1.5, glissement=0.3, occ=0, ab=0.0)),
]


def run(cfg, mec, sc, mode, gain, graines):
    a = types.SimpleNamespace(biais_gyro=0.05, mouvement="lisse", latence_suivi=0.0, desynchro=0.0,
                              occultation=sc["occ"], bruit_suivi=0.04, erreur_main_pointe=0.05,
                              tete_mm=sc["tete"], tete_deg=sc["tete"], compensation_tete="oui",
                              glissement_clip=sc["glissement"], aberrants=sc["ab"], **mec)
    P = S.parametres(a)
    P["fus_mode"], P["fus_pos"] = mode, gain
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
    L = ["Conduit avec coudes, mouvement lissé, %d graines. RMS du nuage (mm)." % args.graines, "",
         "%-56s | %-11s | %-10s | %-12s | %-13s | %s" % ("Scénario", "Centre seul", "Suivi seul", "Fusion g=0,3", "Fusion g=0,01", "Kalman adaptatif")]
    for nom, mec, sc in SCEN:
        v = [run("Ec", mec, sc, "fixe", 0.3, args.graines), run("T", mec, sc, "fixe", 0.3, args.graines),
             run("F", mec, sc, "fixe", 0.3, args.graines), run("F", mec, sc, "fixe", 0.01, args.graines),
             run("F", mec, sc, "kalman", 0.0, args.graines)]
        L.append("%-56s | %-11.3f | %-10.3f | %-12.3f | %-13.3f | %.3f" % (nom, *v))
        print(L[-1], flush=True)
    if args.sortie:
        open(args.sortie, "w").write("\n".join(L)+"\n")


if __name__ == "__main__":
    main()
