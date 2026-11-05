#!/usr/bin/env python3
"""Analyse d'une reconstruction COLMAP d'un retrait d'otoscope dans un fantôme.

Compare les positions de caméra reconstruites (images.txt, modèle exporté en texte) à la trajectoire
vraie du banc, après recalage global avec facteur d'échelle (Sim(3)). Mesure :
  - la fraction d'images recalées,
  - l'échelle globale (mm par unité COLMAP),
  - l'erreur de trajectoire après recalage (RMS 3D, axiale, latérale),
  - l'erreur de longueur de bout en bout,
  - la dérive d'échelle locale (rapport de cordes sur des fenêtres glissantes).

Dépendance : numpy.

Usage :
  python3 analyse_colmap.py --images images.txt --verite verite.csv --fps 30
  python3 analyse_colmap.py --images images.txt --vitesse 5 --fps 30 --longueur 25      (trajet rectiligne)
  python3 analyse_colmap.py --demo                                                       (test sur données simulées)

verite.csv : colonnes « image,x,y,z » (mm), une ligne par image extraite, indexée comme dans les noms
de fichiers (frame_000123.png -> 123). Pour un trajet rectiligne, --vitesse et --longueur suffisent.
Les noms d'images doivent finir par un numéro.
"""
import argparse
import os
import re
import sys
import tempfile
import numpy as np


def lire_images_txt(chemin):
    """Retourne {indice_image: centre_camera (3,)} pour les images recalées."""
    centres = {}
    with open(chemin) as f:
        lignes = [l for l in f if l.strip() and not l.startswith("#")]
    for l in lignes[0::2]:
        p = l.split()
        qw, qx, qy, qz = map(float, p[1:5])
        t = np.array(list(map(float, p[5:8])))
        R = np.array([
            [1-2*(qy*qy+qz*qz), 2*(qx*qy-qz*qw), 2*(qx*qz+qy*qw)],
            [2*(qx*qy+qz*qw), 1-2*(qx*qx+qz*qz), 2*(qy*qz-qx*qw)],
            [2*(qx*qz-qy*qw), 2*(qy*qz+qx*qw), 1-2*(qx*qx+qy*qy)]])
        m = re.findall(r"(\d+)", os.path.basename(p[9]))
        if not m:
            continue
        centres[int(m[-1])] = -R.T @ t
    return centres


def lire_verite(chemin):
    d = np.loadtxt(chemin, delimiter=",", skiprows=1)
    return {int(r[0]): r[1:4] for r in d}


def verite_rectiligne(vitesse, fps, longueur):
    n = int(longueur/vitesse*fps)
    return {i: np.array([0.0, 0.0, -vitesse*i/fps]) for i in range(n)}


def umeyama(A, B):
    mA, mB = A.mean(0), B.mean(0)
    Ac, Bc = A-mA, B-mB
    U, D, Vt = np.linalg.svd(Bc.T@Ac/len(A))
    S = np.eye(3)
    if np.linalg.det(U)*np.linalg.det(Vt) < 0:
        S[2, 2] = -1
    R = U@S@Vt
    s = np.trace(np.diag(D)@S)/np.mean(np.sum(Ac**2, 1))
    return s, R, mB-s*R@mA


def analyser(centres, verite, fenetre=5.0):
    idx = sorted(set(centres) & set(verite))
    res = {"images_verite": len(verite), "images_recalees": len(idx)}
    res["fraction_recalee"] = len(idx)/max(len(verite), 1)
    if len(idx) < 10:
        res["erreur"] = "moins de 10 images recalées : analyse impossible"
        return res
    C = np.array([centres[i] for i in idx])
    T = np.array([verite[i] for i in idx])
    s, R, t = umeyama(C, T)
    Ca = s*(C@R.T)+t
    d = Ca-T
    tang = np.gradient(T, axis=0)
    tang /= np.maximum(np.linalg.norm(tang, axis=1)[:, None], 1e-12)
    ax = np.sum(d*tang, 1)
    lat = np.linalg.norm(d-ax[:, None]*tang, axis=1)
    res.update(echelle_mm_par_unite=s,
               rms_3d_mm=float(np.sqrt(np.mean(np.sum(d**2, 1)))),
               rms_axial_mm=float(np.sqrt(np.mean(ax**2))),
               rms_lateral_mm=float(np.sqrt(np.mean(lat**2))))
    Lv = np.linalg.norm(T[-1]-T[0])
    Le = np.linalg.norm(Ca[-1]-Ca[0])
    res["longueur_vraie_mm"] = float(Lv)
    res["erreur_longueur_mm"] = float(Le-Lv)
    res["erreur_longueur_pct"] = float(100*(Le-Lv)/Lv)
    # dérive d'échelle locale : rapport des cordes sur des fenêtres de longueur `fenetre`
    rap = []
    for i in range(len(idx)):
        j = i+1
        while j < len(idx) and np.linalg.norm(T[j]-T[i]) < fenetre:
            j += 1
        if j >= len(idx):
            break
        rap.append(np.linalg.norm(Ca[j]-Ca[i])/np.linalg.norm(T[j]-T[i]))
    if rap:
        rap = np.array(rap)
        res["derive_locale_max_pct"] = float(100*np.max(np.abs(rap-1)))
        res["derive_locale_rms_pct"] = float(100*np.sqrt(np.mean((rap-1)**2)))
    return res


def afficher(res):
    lib = [("images_verite", "images de référence"), ("images_recalees", "images recalées"),
           ("fraction_recalee", "fraction recalée"), ("echelle_mm_par_unite", "échelle (mm par unité COLMAP)"),
           ("rms_3d_mm", "RMS 3D après recalage Sim(3) (mm)"), ("rms_axial_mm", "RMS axial (mm)"),
           ("rms_lateral_mm", "RMS latéral (mm)"), ("longueur_vraie_mm", "longueur vraie (mm)"),
           ("erreur_longueur_mm", "erreur de longueur (mm)"), ("erreur_longueur_pct", "erreur de longueur (%)"),
           ("derive_locale_max_pct", "dérive d'échelle locale, maximum (%)"),
           ("derive_locale_rms_pct", "dérive d'échelle locale, RMS (%)"), ("erreur", "erreur")]
    for k, l in lib:
        if k in res:
            v = res[k]
            print("%-42s %s" % (l, ("%.4g" % v) if isinstance(v, float) else v))


def demo():
    """Simule un modèle COLMAP : échelle inconnue, dérive d'échelle de 1 %, bruit, images manquantes."""
    rng = np.random.default_rng(1)
    fps, v, L = 30.0, 5.0, 25.0
    verite = verite_rectiligne(v, fps, L)
    n = len(verite)
    k0 = 0.37          # mm par unité COLMAP (inconnu en pratique)
    drift = 0.01       # la dérive d'échelle atteint 1 % en fin de trajet
    lignes = ["# modèle simulé"]
    for i in range(n):
        if rng.random() < 0.08:
            continue
        T = verite[i]
        s_ = -T[2]
        pos = np.array([rng.normal(0, 0.03), rng.normal(0, 0.03), T[2]*(1+drift*s_/L)])/k0
        # caméra alignée sur l'axe : R = identité, t = -C
        t = -pos
        lignes.append("%d 1 0 0 0 %.6f %.6f %.6f 1 frame_%06d.png" % (i+1, t[0], t[1], t[2], i))
        lignes.append("0 0 -1")
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write("\n".join(lignes)+"\n")
        nom = f.name
    print("Démo : échelle vraie %.3f mm/unité, dérive d'échelle injectée 1 %%, 8 %% d'images non recalées\n" % k0)
    afficher(analyser(lire_images_txt(nom), verite))
    os.remove(nom)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images")
    ap.add_argument("--verite")
    ap.add_argument("--vitesse", type=float)
    ap.add_argument("--fps", type=float, default=30.0)
    ap.add_argument("--longueur", type=float)
    ap.add_argument("--fenetre", type=float, default=5.0, help="fenêtre de dérive locale, mm")
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()
    if a.demo:
        demo()
        return
    if not a.images:
        sys.exit("--images est requis (ou --demo)")
    if a.verite:
        v = lire_verite(a.verite)
    elif a.vitesse and a.longueur:
        v = verite_rectiligne(a.vitesse, a.fps, a.longueur)
    else:
        sys.exit("fournir --verite, ou --vitesse et --longueur")
    afficher(analyser(lire_images_txt(a.images), v, a.fenetre))


if __name__ == "__main__":
    main()
