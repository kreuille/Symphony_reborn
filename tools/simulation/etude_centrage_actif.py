#!/usr/bin/env python3
"""Centrage actif sans contact : un actionneur latéral en bout de sonde annule le décentrage mesuré.

Le décentrage est le centre de l'anneau laser dans le repère de la sonde (mesuré à chaque image).
Perturbation de la main : décalage latéral aléatoire de 0,3 mm (écart-type), corrélé sur 0,5 s.
Boucle : intégrateur à bande passante réglable, bruit de mesure de 0,01 mm, course de +/- 1 mm.
Suivi du centre avec axe par codeur, retrait à vitesse constante (3 mm/s), tête mobile compensée par gyroscope.

Usage : python3 etude_centrage_actif.py [--graines 4]
"""
import argparse
import types
import numpy as np
import simulateur_scanner as S


def run(bande, inclinaison, graines, course=1.0):
    a = types.SimpleNamespace(biais_gyro=0.05, inclinaison=inclinaison, mouvement="lisse", vitesse=3.0, latence_suivi=0.0,
                              desynchro=0.0, occultation=0, bruit_suivi=0.04, erreur_main_pointe=0.05,
                              tete_mm=1.5, tete_deg=1.5, compensation_tete="oui", glissement_clip=0.1,
                              aberrants=0.0, decentrage=0.3, variation_vitesse=0.0,
                              bande_centrage=bande, course_centrage=course)
    P = S.parametres(a)
    canal = S.Canal("realiste")
    rms, dec = [], []
    for g in range(graines):
        tr = S.gen_truth(canal, np.random.default_rng(1000+g), P)
        pe, Re, q = S.run_config(tr, "Ec", np.random.default_rng(5000+g), P)
        rms.append(S.metriques(canal, tr, pe, Re, q, P)["rms"])
        dec.append(np.sqrt(np.mean(np.sum(tr["lat"]**2, 1)/2)))
    return float(np.mean(rms)), float(np.mean(dec))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graines", type=int, default=4)
    ap.add_argument("--sortie", default=None)
    args = ap.parse_args()
    L = ["Conduit avec coudes, mouvement lissé, retrait à 3 mm/s constant, tête mobile 1,5 mm / 1,5° (gyroscope sur la tête), %d graines." % args.graines,
         "Perturbation de la main : décalage latéral de 0,3 mm (écart-type). Suivi du centre, axe par codeur. RMS du nuage (mm), décentrage résiduel RMS (mm par axe).", "",
         "%-26s %-12s | %-8s %-12s" % ("Bande passante de la boucle", "Inclinaison", "RMS", "Décentrage")]
    for incl in (2.0, 0.5, 0.3):
        for bande in (0.0, 0.5, 1.0, 2.0, 4.0):
            rms, dec = run(bande, incl, args.graines)
            nom = "sans centrage actif" if bande == 0 else "%.1f Hz" % bande
            L.append("%-26s %-12s | %-8.3f %-12.3f" % (nom, "%.1f°" % incl, rms, dec))
            print(L[-1], flush=True)
    if args.sortie:
        open(args.sortie, "w").write("\n".join(L)+"\n")


if __name__ == "__main__":
    main()
