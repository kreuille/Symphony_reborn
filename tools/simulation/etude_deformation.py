#!/usr/bin/env python3
"""Compromis centrage / déformation du conduit pour une sonde auto-centrée au contact.

Modèle mécanique volontairement simple (valeurs d'entrée en HYPOTHÈSE, à mesurer) :
  - N points de contact élastiques, de raideur radiale k_f chacun (N/mm), pressés contre la paroi.
  - Raideur radiale locale du conduit k_t (N/mm). En série : fraction de l'interférence transmise à la paroi
    eta = k_f / (k_f + k_t). La paroi est repoussée de eta x (r_collerette - r_paroi) là où la collerette dépasse.
  - Perturbation latérale de la main F_d (N). Décentrage latéral = max(plancher, F_d / (N x k_f)).
Le simulateur reconstruit le conduit déformé (suivi du centre, axe par codeur) et compare au conduit non déformé.

Usage : python3 etude_deformation.py [--graines 4]
"""
import argparse
import types
import numpy as np
import simulateur_scanner as S


def run(sigma_dec, eta, r_f, graines):
    a = types.SimpleNamespace(biais_gyro=0.05, inclinaison=0.3, mouvement="lisse", vitesse=3.0, latence_suivi=0.0,
                              desynchro=0.0, occultation=0, bruit_suivi=0.04, erreur_main_pointe=0.05,
                              tete_mm=1.5, tete_deg=1.5, compensation_tete="oui", glissement_clip=0.1,
                              aberrants=0.0, decentrage=sigma_dec, variation_vitesse=0.0)
    P = S.parametres(a)
    P["deform_eta"], P["deform_rf"] = eta, r_f
    canal = S.Canal("realiste")
    rms, bias = [], []
    for g in range(graines):
        tr = S.gen_truth(canal, np.random.default_rng(1000+g), P)
        pe, Re, q = S.run_config(tr, "Ec", np.random.default_rng(5000+g), P)
        m = S.metriques(canal, tr, pe, Re, q, P)
        rms.append(m["rms"]); bias.append(m["biais"])
    return float(np.mean(rms)), float(np.mean(bias))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graines", type=int, default=4)
    ap.add_argument("--sortie", default=None)
    args = ap.parse_args()
    N, F_d, plancher, r_f = 3, 0.05, 0.03, 5.2
    L = ["Conduit avec coudes (rayon 4,8 à 3,0 mm), collerette de rayon libre %.1f mm, %d contacts, perturbation latérale %.2f N, plancher de décentrage %.2f mm." % (r_f, N, F_d, plancher),
         "Suivi du centre, axe par codeur, mouvement lissé, tête mobile compensée par gyroscope. Moyenne sur %d graines." % args.graines, "",
         "%-8s %-12s %-10s | %-14s %-10s %-14s" % ("k_f", "décentrage", "k_t", "eta", "biais (mm)", "RMS vs non déformé")]
    ref = run(0.3, 0.0, r_f, args.graines)
    L.append("Référence sans centrage ni contact (décentrage 0,3 mm, inclinaison 0,3°, vitesse constante) : RMS %.3f mm" % ref[0])
    L.append("")
    for kt in (0.5, 2.0):
        for kf in (0.02, 0.05, 0.1, 0.2, 0.5, 1.0):
            sd = max(plancher, F_d/(N*kf))
            eta = kf/(kf+kt)
            rms, bias = run(sd, eta, r_f, args.graines)
            L.append("%-8.2f %-12.3f %-10.1f | %-14.3f %-10.3f %-14.3f" % (kf, sd, kt, eta, bias, rms))
            print(L[-1], flush=True)
    if args.sortie:
        open(args.sortie, "w").write("\n".join(L)+"\n")
    print("\n".join(L[:5]))


if __name__ == "__main__":
    main()
