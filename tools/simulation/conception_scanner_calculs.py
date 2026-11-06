#!/usr/bin/env python3
"""Calculs de conception du scanner (tête A, anneau laser) et observabilité de la pose.

Dépendance : numpy seulement. Usage : python3 conception_scanner_calculs.py
Les valeurs d'entrée sont des hypothèses de départ (voir specs/scanner-spec-prototype.md).
"""
import numpy as np

# ---------------------------------------------------------------------------
# 1. Observabilité de la pose par recalage de surface (ICP point-à-plan)
#    Un nouvel anneau laser est recalé contre la surface déjà reconstruite.
#    Surface : r(theta, z) = (R0 - s*z) * (1 + e*cos(2*theta)) + micro-relief éventuel
# ---------------------------------------------------------------------------
def anneau_jacobien(R0, s, e, z0=0.0, relief_amp=0.0, relief_lambda=1.5, n=360):
    th = np.linspace(0, 2*np.pi, n, endpoint=False)
    def r(th, z):
        return (R0 - s*z)*(1 + e*np.cos(2*th)) + relief_amp*np.cos(2*np.pi*z/relief_lambda)
    h = 1e-5
    rr = r(th, z0)
    dr_dth = (r(th+h, z0) - r(th-h, z0))/(2*h)
    dr_dz = (r(th, z0+h) - r(th, z0-h))/(2*h)
    P = np.stack([rr*np.cos(th), rr*np.sin(th), np.full(n, z0)], 1)
    rho_hat = np.stack([np.cos(th), np.sin(th), np.zeros(n)], 1)
    th_hat = np.stack([-np.sin(th), np.cos(th), np.zeros(n)], 1)
    N = rho_hat - (dr_dth/rr)[:, None]*th_hat
    N[:, 2] -= dr_dz
    N /= np.linalg.norm(N, axis=1)[:, None]
    J = np.hstack([N, np.cross(P, N)])          # [tx ty tz | rx ry rz]
    return J

def ecarts_types(J, sigma, garder):
    """Écarts-types des degrés de liberté conservés (indices de [tx ty tz rx ry rz]),
    les autres étant supposés connus (par ex. le roulis, fourni par le gyroscope)."""
    Jg = J[:, garder]
    cov = sigma**2*np.linalg.inv(Jg.T @ Jg)
    return dict(zip(garder, np.sqrt(np.diag(cov))))

def section1(sigma=0.02, pas=0.3, profondeur=30.0, n_points=360):
    M = int(profondeur/pas)
    print("=== 1. Observabilité de la pose par ICP sur un anneau ===")
    print("Hypothèses : rayon moyen 3,5 mm ; %d points par anneau, bruit de mesure %.3f mm indépendant par point ;" % (n_points, sigma))
    print("pas axial %.1f mm, %d anneaux sur %.0f mm ; surface déjà reconstruite supposée parfaite." % (pas, M, profondeur))
    print("(a) orientation connue (gyroscope) : écarts-types par anneau, latéral tx et axial tz (mm), puis tz cumulé en marche aléatoire")
    print("(b) orientation inconnue : écart-type latéral tx (mm) et inclinaison rx (°)")
    print("%-52s | %7s %7s %9s | %7s %9s" % ("Cas", "tx", "tz", "tz cumulé", "tx", "rx"))
    cas = [
        ("Cylindre parfait", dict(s=0.0, e=0.0)),
        ("Conicité 0,02 (1° environ)", dict(s=0.02, e=0.0)),
        ("Conicité 0,05 (3° environ)", dict(s=0.05, e=0.0)),
        ("Conicité 0,05 + ellipticité 5 %", dict(s=0.05, e=0.05)),
        ("Hypothèse : micro-relief 0,03 mm / 1,5 mm", dict(s=0.02, e=0.05, relief_amp=0.03, z0=0.375)),  # pente maximale du relief
    ]
    def fmt(v, unit=1.0, lim=1e3):
        return "%7s" % "inf." if (v is None or v*unit > lim) else "%7.3f" % (v*unit)
    for nom, kw in cas:
        e = kw["e"]
        J = anneau_jacobien(3.5, kw.pop("s"), kw.pop("e"), n=n_points, **kw)
        def sd_de(garder):
            sv = np.linalg.svd(J[:, garder], compute_uv=False)
            if sv.min() < 1e-9:
                return None
            return ecarts_types(J, sigma, garder)
        A = sd_de([0, 1, 2])
        B = sd_de([0, 1, 2, 3, 4] + ([5] if e > 0 else []))
        tz = None if A is None else A[2]
        cum = "%9s" % "inf." if tz is None else "%9.2f" % (tz*np.sqrt(M))
        rxs = "%9s" % "non obs." if (B is None or np.degrees(B[3]) > 45) else "%9.2f" % np.degrees(B[3])
        print("%-52s | %s %s %s | %s %s" % (nom, fmt(A[0] if A else None), fmt(tz), cum, fmt(B[0] if B else None), rxs))
    print("Lecture : sans conicité ni relief, la position axiale n'est pas observable par la surface seule ;")
    print("l'inclinaison est confondue avec un décalage latéral (un anneau incliné et un anneau décalé se ressemblent) ;")
    print("le roulis d'un conduit circulaire est inobservable. Il faut donc une orientation externe (gyroscope, texture vidéo, suivi).")

# ---------------------------------------------------------------------------
# 2. Dérive d'un accéléromètre MEMS intégré deux fois
# ---------------------------------------------------------------------------
def section2():
    print("\n=== 2. Position axiale par double intégration d'un accéléromètre ===")
    g = 9.81
    print("Erreur = 0,5 * biais * t^2 (biais résiduel après calibration)")
    print("%-18s %12s %12s %12s" % ("Biais résiduel", "t = 0,5 s", "t = 1 s", "t = 2 s"))
    for mg in (0.1, 1, 5):
        b = mg*1e-3*g
        print("%-18s" % ("%.1f mg" % mg), *["%9.2f mm" % (0.5*b*t**2*1000) for t in (0.5, 1, 2)])
    print("Conclusion : l'accéléromètre ne peut pas fournir la position axiale à 0,1 mm.")

# ---------------------------------------------------------------------------
# 3. Géométrie de la tête A : caméra derrière le plan de l'anneau, à la distance B
# ---------------------------------------------------------------------------
def section3(npx=400):
    print("\n=== 3. Géométrie de la tête A (anneau ahead of camera, base B) ===")
    print("Capteur %d px, objectif équidistant dont le champ couvre exactement l'angle requis." % npx)
    print("Rayon de paroi de 2,5 à 6,0 mm (diamètre 5 à 12 mm).")
    print("%-6s %-16s %-14s %-16s %-16s" % ("B mm", "demi-champ req.", "focale px/rad", "mm/px @ r=4", "mm/px @ r=6"))
    for B in (1.5, 2.0, 3.0, 4.0, 5.0):
        rmax = 6.0
        th_max = np.arctan2(rmax, B)
        f = (npx/2)/th_max
        def res(r):
            return (r**2 + B**2)/(B*f)
        print("%-6.1f %-16s %-14.0f %-16.3f %-16.3f" % (B, "%.0f°" % np.degrees(th_max), f, res(4.0), res(6.0)))
    print("Note : champ requis de 2*demi-champ ; au-delà de ~150° l'objectif est très difficile.")

# ---------------------------------------------------------------------------
# 4. Cadence, vitesse de retrait, synchronisation
# ---------------------------------------------------------------------------
def section4():
    print("\n=== 4. Cadence, flou de bouger et synchronisation ===")
    print("Pas axial entre anneaux (mm) = vitesse / cadence de mesure")
    print("%-14s" % "cadence mes.", *["%10s" % ("v=%d mm/s" % v) for v in (3, 5, 10)])
    for fps in (15, 30, 60, 120):
        print("%-14s" % ("%d /s" % fps), *["%10.2f" % (v/fps) for v in (3, 5, 10)])
    print("Flou de bouger = vitesse * temps d'exposition : 10 mm/s * 1 ms = %.0f µm" % (10*1e-3*1000))
    print("Erreur de datation (mm) = vitesse relative * décalage temporel")
    print("%-18s" % "vitesse relative", *["%10s" % ("%.1f ms" % d) for d in (0.5, 1, 5)])
    for v in (10, 50, 100):
        print("%-18s" % ("%d mm/s" % v), *["%10.3f" % (v*d*1e-3) for d in (0.5, 1, 5)])
    print("Flèche d'interpolation entre deux anneaux, rayon de courbure axial 5 mm, pas 0,33 mm : %.4f mm"
          % (0.33**2/(8*5)))

if __name__ == "__main__":
    section1()
    section2()
    section3()
    section4()
