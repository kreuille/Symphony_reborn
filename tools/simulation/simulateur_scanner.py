#!/usr/bin/env python3
"""Simulateur du scanner à anneau laser (tête A) : dérive de pose selon la source d'axe.

Dépendance : numpy seulement.
Usage : python3 simulateur_scanner.py [--graines 10] [--biais-gyro 0.05] [--sortie fichier.txt]

Ce que le simulateur fait
-------------------------
1. Construit un conduit synthétique : ligne centrale 3D avec deux coudes, rayon décroissant
   (conicité), section elliptique, micro-relief optionnel.
2. Simule un retrait manuel de la sonde (vitesse variable, décalage latéral, inclinaison et
   roulis aléatoires) et le lancer de rayons de l'anneau laser sur la paroi (30 images/s).
3. Reconstruit la pose avec quatre configurations, qui ne diffèrent que par la source d'axe :
     ref : poses vraies (contrôle du lancer de rayons, bruit de mesure seul)
     E   : axe fourni par un codeur (borne haute, banc motorisé)
     V   : axe par odométrie visuelle (hypothèse : bruit et erreur d'échelle)
     T   : suivi externe de la poignée (pose absolue, bruit + erreur d'étalonnage main-pointe)
     I   : aucun capteur d'axe, recalage de surface seul (ICP simplifié)
   Toutes sauf T et ref utilisent un gyroscope pour l'orientation et un recalage de l'anneau
   sur un modèle local lisse de la surface déjà reconstruite pour la position latérale.
4. Mesure l'erreur de pose (axiale, latérale, orientation) et l'erreur du nuage de points
   reconstruit par rapport à la surface exacte du conduit.

Limites : conduit synthétique, bruits gaussiens, valeurs de capteurs en hypothèse. Les résultats
donnent des ordres de grandeur et des classements, pas des performances démontrées.
"""
import argparse
import sys
import time
import numpy as np

DEG = np.pi/180.0

# ----------------------------------------------------------------------------
# Rotations
# ----------------------------------------------------------------------------
def exp_so3(w):
    th = np.linalg.norm(w)
    if th < 1e-12:
        return np.eye(3)
    k = w/th
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + np.sin(th)*K + (1-np.cos(th))*(K@K)

def log_so3(R):
    c = np.clip((np.trace(R)-1)/2, -1, 1)
    th = np.arccos(c)
    if th < 1e-12:
        return np.zeros(3)
    w = np.array([R[2, 1]-R[1, 2], R[0, 2]-R[2, 0], R[1, 0]-R[0, 1]])
    return th/(2*np.sin(th))*w

def smooth(x):
    x = np.clip(x, 0, 1)
    return x*x*(3-2*x)

# ----------------------------------------------------------------------------
# Conduit synthétique
# ----------------------------------------------------------------------------
PRESETS = {
    # nom: (rayon au méat, rayon à 30 mm, ellipticité, amplitude relief mm)
    "realiste":       (4.8, 3.0, 0.08, 0.0),
    "quasi_cylindre": (3.6, 3.2, 0.02, 0.0),
    "relief":         (4.8, 3.0, 0.08, 0.02),   # hypothèse : micro-relief de peau
    # variantes sans coudes, pour isoler l'effet de l'axe de celui des coudes
    "droit_conique":  (4.8, 3.0, 0.08, 0.0),
    "droit_cylindre": (3.6, 3.4, 0.02, 0.0),
}
SANS_COUDES = ("droit_conique", "droit_cylindre")

class Canal:
    DS = 0.1
    S0 = -10.0
    W = 40   # demi-fenêtre de recherche du point de ligne centrale le plus proche

    def __init__(self, nom):
        r0, r1, e0, amp = PRESETS[nom]
        self.nom = nom
        s = np.arange(self.S0, 45.0, self.DS)
        self.s = s
        n = len(s)
        k_coude = 0.0 if nom in SANS_COUDES else 1.0
        phi = k_coude*(0.5*smooth((s-6)/8) - 0.45*smooth((s-16)/8))
        psi = k_coude*(0.22*smooth((s-10)/8) - 0.18*smooth((s-20)/8))
        T = np.stack([np.cos(psi)*np.cos(phi), np.cos(psi)*np.sin(phi), np.sin(psi)], 1)
        c = np.zeros((n, 3))
        for i in range(n-1):
            c[i+1] = c[i] + T[i]*self.DS
        N = np.zeros((n, 3))
        a = np.array([0.0, 0.0, 1.0])
        N[0] = a - (a@T[0])*T[0]
        N[0] /= np.linalg.norm(N[0])
        for i in range(n-1):
            v = N[i] - (N[i]@T[i+1])*T[i+1]
            N[i+1] = v/np.linalg.norm(v)
        B = np.cross(T, N)
        self.c, self.T, self.N, self.B = c, T, N, B
        sc = np.clip(s, 0, 30)
        self.R = r0 + (r1-r0)*sc/30.0
        self.e = np.full(n, e0)
        self.phie = 0.3 + 0.04*s
        self.amp, self.lam = amp, 1.5

    def interp_frame(self, sp):
        x = (sp-self.S0)/self.DS
        i = int(np.floor(x))
        w = x-i
        c = (1-w)*self.c[i] + w*self.c[i+1]
        T = (1-w)*self.T[i] + w*self.T[i+1]
        T /= np.linalg.norm(T)
        N = (1-w)*self.N[i] + w*self.N[i+1]
        N -= (N@T)*T
        N /= np.linalg.norm(N)
        return c, T, N, np.cross(T, N)

    def index(self, s):
        return np.clip(np.round((np.asarray(s)-self.S0)/self.DS).astype(int), 0, len(self.s)-1)

    def g(self, pts, base):
        """Fonction implicite : positive hors du conduit, négative dedans (mm, distance radiale)."""
        off = np.arange(-self.W, self.W+1)
        idx = np.clip(base[:, None]+off[None, :], 0, len(self.s)-1)
        C = self.c[idx]
        d2 = np.sum((pts[:, None, :]-C)**2, axis=2)
        j = np.argmin(d2, axis=1)
        i = idx[np.arange(len(pts)), j]
        q = pts - self.c[i]
        u = np.sum(q*self.T[i], 1)
        qp = q - u[:, None]*self.T[i]
        rho = np.linalg.norm(qp, axis=1)
        th = np.arctan2(np.sum(qp*self.B[i], 1), np.sum(qp*self.N[i], 1))
        r = self.R[i]*(1+self.e[i]*np.cos(2*(th-self.phie[i])))
        if self.amp:
            r = r + self.amp*np.cos(2*np.pi*self.s[i]/self.lam)
        return rho - r

    def distance(self, pts, base):
        """Distance signée approchée à la surface : g / |grad g|."""
        h = 0.01
        g0 = self.g(pts, base)
        gr = []
        for k in range(3):
            p2 = pts.copy()
            p2[:, k] += h
            gr.append((self.g(p2, base)-g0)/h)
        gn = np.linalg.norm(np.stack(gr, 1), axis=1)
        return g0/np.maximum(gn, 1e-6)

# ----------------------------------------------------------------------------
# Vérité terrain : retrait manuel et mesure de l'anneau
# ----------------------------------------------------------------------------
def ar1(rng, n, rho, sigma):
    x = np.zeros(n)
    s = sigma*np.sqrt(1-rho**2)
    for k in range(1, n):
        x[k] = rho*x[k-1] + s*rng.standard_normal()
    return x

def gen_truth(canal, rng, P):
    dt, nf, nr, Bz = P["dt"], P["nframes"], P["nrays"], P["B"]
    xv = ar1(rng, nf, 0.95, 1.0)
    v = P["v0"]*(1+0.3*xv)
    sp = np.zeros(nf)
    sp[0] = P["s_start"]
    for k in range(1, nf):
        sp[k] = sp[k-1] - v[k-1]*dt
    nf_eff = int(np.argmax(sp < P["s_end"])) if np.any(sp < P["s_end"]) else nf
    nf_eff = nf_eff if nf_eff > 0 else nf
    sp = sp[:nf_eff]
    nf = nf_eff
    rho_l = 1-dt/0.5
    lat = np.stack([ar1(rng, nf, rho_l, 0.3), ar1(rng, nf, rho_l, 0.3)], 1)
    lat = np.clip(lat, -0.8, 0.8)
    tilt = np.stack([ar1(rng, nf, rho_l, P["tilt"]*DEG), ar1(rng, nf, rho_l, P["tilt"]*DEG)], 1)
    roll = ar1(rng, nf, 1-dt/2.0, 20*DEG)
    O = np.zeros((nf, 3)); R = np.zeros((nf, 3, 3)); Tt = np.zeros((nf, 3))
    for k in range(nf):
        c, T, N, B = canal.interp_frame(sp[k])
        O[k] = c + lat[k, 0]*N + lat[k, 1]*B
        F = np.stack([N, B, T], 1)
        R[k] = F @ exp_so3(np.array([0, 0, roll[k]])) @ exp_so3(np.array([tilt[k, 0], 0, 0])) @ exp_so3(np.array([0, tilt[k, 1], 0]))
        Tt[k] = T
    # lancer de rayons de l'anneau (origine sur l'axe de la sonde à la distance B)
    al = 2*np.pi*np.arange(nr)/nr
    dloc = np.stack([np.cos(al), np.sin(al), np.zeros(nr)], 1)
    org = O + np.einsum('kij,j->ki', R, np.array([0, 0, Bz]))
    dirs = np.einsum('kij,rj->kri', R, dloc)
    base = np.repeat(canal.index(sp+Bz), nr)
    lo = np.zeros((nf, nr)); hi = np.full((nf, nr), 12.0)
    for _ in range(30):
        mid = 0.5*(lo+hi)
        pts = (org[:, None, :] + mid[:, :, None]*dirs).reshape(-1, 3)
        gv = canal.g(pts, base).reshape(nf, nr)
        inside = gv < 0
        lo = np.where(inside, mid, lo)
        hi = np.where(inside, hi, mid)
    rho_true = 0.5*(lo+hi)
    rho_meas = rho_true + P["sigma_m"]*rng.standard_normal((nf, nr))
    return dict(sp=sp, O=O, R=R, T=Tt, rho=rho_meas, alpha=al, nf=nf, nr=nr, dt=dt)

# ----------------------------------------------------------------------------
# Capteurs et estimation
# ----------------------------------------------------------------------------
def local_ring(tr, Bz):
    r, a = tr["rho"], tr["alpha"][None, :]
    return np.stack([r*np.cos(a), r*np.sin(a), np.full_like(r, Bz)], 2)   # (F, Rn, 3)

def gyro_orientation(tr, rng, P):
    nf, dt = tr["nf"], tr["dt"]
    Rt = tr["R"]
    bias = P["gyro_bias"]*DEG*rng.standard_normal(3)
    arw = P["gyro_arw"]*DEG
    Re = np.zeros_like(Rt); Re[0] = Rt[0]
    for k in range(1, nf):
        dth = log_so3(Rt[k-1].T @ Rt[k])
        meas = dth + bias*dt + arw*np.sqrt(dt)*rng.standard_normal(3)
        Re[k] = Re[k-1] @ exp_so3(meas)
    return Re

HARM = 4   # nombre d'harmoniques azimutales du modèle local de surface

def basis(th):
    cols = [np.ones_like(th)]
    for h in range(1, HARM+1):
        cols += [np.cos(h*th), np.sin(h*th)]
    return np.stack(cols, 1)

def fit_model(local):
    rho = np.hypot(local[:, 0], local[:, 1])
    th = np.arctan2(local[:, 1], local[:, 0])
    return rho, th

def run_config(tr, cfg, rng, P):
    nf, nr, Bz = tr["nf"], tr["nr"], P["B"]
    Ot, Rt, Tt = tr["O"], tr["R"], tr["T"]
    loc = local_ring(tr, Bz)
    if cfg == "ref":
        pe, Re = Ot.copy(), Rt.copy()
    elif cfg == "T":
        Re = np.zeros_like(Rt)
        pe = np.zeros_like(Ot)
        he = P["trk_handeye"]*rng.standard_normal(3)
        drift = np.stack([ar1(rng, nf, 1-tr["dt"]/1.0, P["trk_drift"]) for _ in range(3)], 1)
        for k in range(nf):
            Re[k] = Rt[k] @ exp_so3(P["trk_rot"]*DEG*rng.standard_normal(3))
            pe[k] = Ot[k] + he + drift[k] + P["trk_pos"]*rng.standard_normal(3)
    else:
        Re = gyro_orientation(tr, rng, P)
        pe = np.zeros_like(Ot)
        K0, K = P["k0"], P["kmodel"]
        scale = P["vo_scale"]*rng.standard_normal()
        sig_ax = {"E": P["enc_sigma"], "V": P["vo_sigma"], "I": P["icp_prior_ax"]}[cfg]
        sig_lat = P["lat_prior"]
        q = np.zeros((nf, nr, 3))
        steps = []
        for k in range(nf):
            if k < K0:
                pe[k] = Ot[k]
                if k > 0:
                    steps.append((pe[k]-pe[k-1]) @ Re[k][:, 2])
                q[k] = pe[k] + loc[k] @ Re[k].T
                continue
            if cfg == "E":
                dz = (Ot[k]-Ot[k-1]) @ Rt[k][:, 2] + P["enc_sigma"]*rng.standard_normal()
            elif cfg == "V":
                dz = (Ot[k]-Ot[k-1]) @ Rt[k][:, 2]*(1+scale) + P["vo_sigma"]*rng.standard_normal()
            else:
                dz = float(np.mean(steps[-3:]))
            ppred = pe[k-1] + Re[k][:, 2]*dz
            # modèle local lisse de la surface déjà reconstruite
            prev = q[max(0, k-K):k].reshape(-1, 3)
            lp = (prev - ppred) @ Re[k]
            rho, th = fit_model(lp)
            zz = lp[:, 2]-Bz
            b = basis(th)
            cols = [b*(zz[:, None]**o) for o in range(P["ordre"]+1)]
            Phi = np.concatenate(cols, 1)
            A = Phi.T@Phi + 1e-6*np.eye(Phi.shape[1])
            coef = np.linalg.solve(A, Phi.T@rho).reshape(P["ordre"]+1, 2*HARM+1)
            new0 = loc[k]
            def resid(dl):
                p = new0 + dl
                r_ = np.hypot(p[:, 0], p[:, 1]); t_ = np.arctan2(p[:, 1], p[:, 0])
                bb = basis(t_)
                zr = p[:, 2]-Bz
                return r_ - sum((bb@coef[o])*zr**o for o in range(P["ordre"]+1))
            dl = np.zeros(3)
            sp_ = np.array([sig_lat, sig_lat, sig_ax])
            for _ in range(3):
                r0 = resid(dl)
                J = np.zeros((nr, 3))
                for j in range(3):
                    e = np.zeros(3); e[j] = 0.01
                    J[:, j] = (resid(dl+e)-r0)/0.01
                Aw = J.T@J/P["sigma_m"]**2 + np.diag(1/sp_**2)
                bw = -(J.T@r0/P["sigma_m"]**2 + dl/sp_**2)
                dl = dl + np.linalg.solve(Aw, bw)
            pe[k] = ppred + Re[k] @ dl
            steps.append((pe[k]-pe[k-1]) @ Re[k][:, 2])
            q[k] = pe[k] + loc[k] @ Re[k].T
    q = pe[:, None, :] + np.einsum('kij,krj->kri', Re, loc)
    return pe, Re, q

def metriques(canal, tr, pe, Re, q, P):
    nf, nr = tr["nf"], tr["nr"]
    base = np.repeat(canal.index(tr["sp"]+P["B"]), nr)
    d = canal.distance(q.reshape(-1, 3), base)
    perr = pe - tr["O"]
    ax = np.sum(perr*tr["T"], 1)
    lat = np.linalg.norm(perr - ax[:, None]*tr["T"], axis=1)
    orient = np.array([np.linalg.norm(log_so3(tr["R"][k].T@Re[k])) for k in range(nf)])/DEG
    return dict(rms=np.sqrt(np.mean(d**2)), p95=np.percentile(np.abs(d), 95),
                ax_fin=abs(ax[-1]), ax_rms=np.sqrt(np.mean(ax**2)),
                lat_rms=np.sqrt(np.mean(lat**2)), or_fin=orient[-1])

KM, ORD = 4, 0


# ----------------------------------------------------------------------------
# Essai « scan interne + recalage sur la partie visible de l'extérieur »
# ----------------------------------------------------------------------------
def surface_externe(canal, rng, Lv, sigma_ext, visible=0.5, ds=0.2, ntheta=36):
    """Points de la partie visible du conduit (s de 0 à Lv) vus par un capteur 3D externe."""
    pts = []
    for sv in np.arange(0.0, Lv, ds):
        i = int(canal.index(sv))
        th = 2*np.pi*np.arange(ntheta)/ntheta
        r = canal.R[i]*(1+canal.e[i]*np.cos(2*(th-canal.phie[i])))
        if canal.amp:
            r = r + canal.amp*np.cos(2*np.pi*canal.s[i]/canal.lam)
        P_ = canal.c[i] + r[:, None]*(np.cos(th)[:, None]*canal.N[i] + np.sin(th)[:, None]*canal.B[i])
        pts.append(P_)
    pts = np.concatenate(pts)
    pts = pts[rng.random(len(pts)) < visible]
    return pts + sigma_ext*rng.standard_normal(pts.shape)

def umeyama(A, B):
    mA, mB = A.mean(0), B.mean(0)
    Ac, Bc = A-mA, B-mB
    U, D, Vt = np.linalg.svd(Bc.T@Ac/len(A))
    S = np.eye(3)
    if np.linalg.det(U)*np.linalg.det(Vt) < 0:
        S[2, 2] = -1
    R = U@S@Vt
    s = np.trace(np.diag(D)@S)/np.mean(np.sum(Ac**2, 1))
    return s, R, mB - s*R@mA

def icp_sim3(A, B, iters=40, garde=0.8):
    s, R, t = 1.0, np.eye(3), np.zeros(3)
    cur = A.copy()
    for _ in range(iters):
        d2 = np.sum((cur[:, None, :]-B[None, :, :])**2, 2)
        j = np.argmin(d2, 1)
        dm = d2[np.arange(len(cur)), j]
        keep = dm <= np.quantile(dm, garde)
        si, Ri, ti = umeyama(cur[keep], B[j[keep]])
        cur = si*(cur@Ri.T) + ti
        s, R, t = si*s, Ri@R, si*(Ri@t) + ti
    return s, R, t

def test_externe(args, P):
    P = dict(P); P["s_end"] = -2.5
    out_l = []
    def out(x=""):
        print(x); out_l.append(x)
    out("Essai : scan interne (axe par codeur) avec erreur d'échelle eps, puis correction par la partie visible de l'extérieur")
    out("Partie visible : s de 0 à %.0f mm, 50 %% des points vus, bruit du capteur externe sig_ext (mm), %d graines." % (args.visible, args.graines))
    out("Biais de rayon = distance signée moyenne du nuage à la paroi (mm) : > 0 si le conduit paraît trop large.")
    out("Échelle est./idéale = (échelle trouvée par le recalage) x (1+eps) : 1 = échelle parfaitement corrigée.")
    out("")
    out("%-14s %5s %7s | %-17s | %-17s | %-17s | %6s" % ("Conduit", "eps", "sig_ext", "avant", "recalage Sim(3)", "échelle seule", "éch."))
    out("%-14s %5s %7s | %8s %8s | %8s %8s | %8s %8s | %6s" % ("", "", "", "RMS", "biais", "RMS", "biais", "RMS", "biais", "est/id"))
    for nom in ("droit_conique", "realiste"):
        canal = Canal(nom)
        trs = []
        for g in range(args.graines):
            tr = gen_truth(canal, np.random.default_rng(1000+g), P)
            pe, Re, q = run_config(tr, "E", np.random.default_rng(5000+g), P)
            trs.append((tr, pe, q))
        for eps in (0.0, 0.01, 0.03):
            for sig in (0.1, 0.5):
                M = []
                for g, (tr, pe, q) in enumerate(trs):
                    p0 = tr["O"][0]
                    qs = p0 + (1+eps)*(q-p0)
                    base = np.repeat(canal.index(tr["sp"]+P["B"]), tr["nr"])
                    def mes(pts):
                        d = canal.distance(pts.reshape(-1, 3), base)
                        return np.sqrt(np.mean(d**2)), np.mean(d)
                    ext = surface_externe(canal, np.random.default_rng(9000+g), args.visible, sig)
                    zone = (tr["sp"]+P["B"] <= args.visible)
                    s_, R_, t_ = icp_sim3(qs[zone].reshape(-1, 3), ext)
                    q_sim = s_*(qs.reshape(-1, 3)@R_.T) + t_
                    q_sc = p0 + s_*(qs-p0)
                    M.append(mes(qs) + mes(q_sim) + mes(q_sc) + (s_*(1+eps),))
                m = np.mean(np.array(M), 0)
                out("%-14s %4.0f%% %7.1f | %8.3f %8.3f | %8.3f %8.3f | %8.3f %8.3f | %6.3f" % (nom, eps*100, sig, *m))
    if args.sortie:
        with open(args.sortie, "w") as fh:
            fh.write("\n".join(out_l)+"\n")

def parametres(args):
    return dict(dt=1/30., nframes=400, nrays=72, B=3.5, v0=5.0, s_start=26.0, s_end=2.0,
                sigma_m=0.02, gyro_bias=args.biais_gyro, gyro_arw=0.01,
                enc_sigma=0.005, vo_sigma=0.01, vo_scale=0.003, icp_prior_ax=0.3, lat_prior=0.15,
                trk_pos=0.04, trk_handeye=0.05, trk_drift=0.03, trk_rot=0.1,
                k0=15, kmodel=KM, ordre=ORD, tilt=args.inclinaison)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graines", type=int, default=6)
    ap.add_argument("--biais-gyro", type=float, default=0.05, help="biais résiduel du gyroscope, °/s (écart-type)")
    ap.add_argument("--inclinaison", type=float, default=2.0, help="inclinaison aléatoire de la sonde, écart-type en degrés")
    ap.add_argument("--conduits", default="realiste,droit_conique,droit_cylindre,relief")
    ap.add_argument("--sortie", default=None)
    ap.add_argument("--test-externe", action="store_true", help="essai de recalage sur la partie visible du conduit")
    ap.add_argument("--visible", type=float, default=6.0, help="profondeur visible de l'extérieur, mm")
    args = ap.parse_args()
    P = parametres(args)
    if args.test_externe:
        test_externe(args, P)
        return
    cfgs = ["ref", "E", "V", "T", "I"]
    lignes = []
    def out(s=""):
        print(s); lignes.append(s)
    out("Simulateur du scanner à anneau laser : %d graines, biais gyroscope %.2f °/s, inclinaison de la sonde %.1f°, bruit de mesure %.3f mm"
        % (args.graines, args.biais_gyro, args.inclinaison, P["sigma_m"]))
    out("Moyenne (écart-type) sur les graines. Axe final = erreur de position axiale à la fin du retrait (|mm|).")
    t0 = time.time()
    for nom in args.conduits.split(","):
        canal = Canal(nom)
        res = {c: [] for c in cfgs}
        nfr = []
        for g in range(args.graines):
            rng = np.random.default_rng(1000+g)
            tr = gen_truth(canal, rng, P)
            nfr.append(tr["nf"])
            for c in cfgs:
                rc = np.random.default_rng(5000+g)
                pe, Re, q = run_config(tr, c, rc, P)
                res[c].append(metriques(canal, tr, pe, Re, q, P))
        out("\nConduit « %s » (%d images environ par retrait)" % (nom, int(np.mean(nfr))))
        out("%-6s %17s %13s %15s %15s %15s" % ("Config", "RMS surface (mm)", "95e c. (mm)", "Axe final (mm)", "Latéral RMS", "Orient. fin (°)"))
        lab = {"ref": "poses vraies", "E": "E codeur", "V": "V odom.vis.", "T": "T suivi ext.", "I": "I ICP seul"}
        for c in cfgs:
            m = {k: np.array([r[k] for r in res[c]]) for k in res[c][0]}
            f = lambda k: "%6.3f (%5.3f)" % (m[k].mean(), m[k].std())
            out("%-13s %s %s %s %s %s" % (lab[c], f("rms").rjust(15), f("p95").rjust(13), f("ax_fin").rjust(15), f("lat_rms").rjust(15), f("or_fin").rjust(15)))
    out("\nTemps de calcul : %.0f s" % (time.time()-t0))
    if args.sortie:
        with open(args.sortie, "w") as fh:
            fh.write("\n".join(lignes)+"\n")

if __name__ == "__main__":
    main()
