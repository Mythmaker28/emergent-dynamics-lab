"""LCI-CAUSAL-CONFIRMATION-01 — Phase-0 empirical probe (DEV seeds only, no prospective seeds).
Quantifies (1) the residual-nutrient/attractant confound at readout and its washout curve,
(2) whether a *standardized* memory->behaviour effect exists (transplant into common body, neutral
settle) and whether it collapses under readout ablation. Uses the FROZEN individuation protocol
constants; no new physics — only field reads, a washout, a field reset, and existing ablation.
"""
import sys, numpy as np
from edlab.experiments.sc_mcm.engine import MultiChannelMemoryEngine, MCParams
from edlab.experiments.sc_mcm import config as C
from edlab.experiments.sc_iom.engine import IOMState
from edlab.substrates.scaffold.observables import detect

C1c = dict(eta_w=0.015, eta_d1=0.35, eta_d2=0.006, k_exp=1.0)
N = C.SPEC.size; N0 = C.SPEC.N0
K = 3; SEP = 24.0; MINSIZE = 45; WARM = 800; PHASE = 60; AMP_LO = 0.005; AMP_HI = 0.035
MC_INTACT = MCParams(lam_plus=0.25, lam_minus=0.15, **C1c)
MC_ABL    = MCParams(lam_plus=0.0,  lam_minus=0.0,  **C1c)

def build(mc): return MultiChannelMemoryEngine(C.SPEC, mc, C.TRACER)
def seed_world(seed):
    s = C.seed_state(C.SPEC, C.TRACER, seed, "random")
    return IOMState(s.rho, s.U, s.V, s.c, s.N, s.C, s.uptake, np.zeros((2, N, N)), 0)
def pdist(a, b):
    d = np.abs(np.array(a) - np.array(b)); d = np.minimum(d, N - d); return float(np.hypot(*d))
def patch(cy, cx, sig):
    ys, xs = np.mgrid[0:N, 0:N]
    dy = np.minimum(np.abs(ys - cy), N - np.abs(ys - cy)); dx = np.minimum(np.abs(xs - cx), N - np.abs(xs - cx))
    return np.exp(-(dy**2 + dx**2) / (2 * sig**2))
def emask(e):
    m = np.zeros((N, N), bool); m[e.cells[:, 0], e.cells[:, 1]] = True; return m
def pick(ents):
    ch = []
    for e in sorted(ents, key=lambda e: -e.size):
        if e.size < MINSIZE: continue
        if all(pdist(e.centroid, o.centroid) >= SEP for o in ch): ch.append(e)
        if len(ch) >= K: break
    return ch
def nearest(c, es): return min(es, key=lambda e: pdist(e.centroid, c))
def region_mem(st, reg):
    m1 = st.Mf[0][reg] / np.maximum(st.rho[reg], 1e-9); m2 = st.Mf[1][reg] / np.maximum(st.rho[reg], 1e-9)
    return float(m1.mean()), float(m2.mean())

def run(seed):
    eng = build(MC_INTACT); st = seed_world(seed)
    for _ in range(WARM): st = eng.step(st)
    T = pick(sorted(detect(st, C.DET), key=lambda e: -e.size))
    if len(T) < K: return None
    cents = [e.centroid for e in T]; sigs = [max(3.0, e.rg * 0.8) for e in T]
    pts = [patch(*cents[i], sigs[i]) for i in range(K)]
    rng = np.random.default_rng(seed)
    hist = [(float(rng.uniform(AMP_LO, AMP_HI)), float(rng.uniform(AMP_LO, AMP_HI))) for _ in range(K)]
    dose = [a1 + a2 for a1, a2 in hist]; order = [a2 - a1 for a1, a2 in hist]

    # DRIVEN branch (simultaneous) and NO-DRIVE counterfactual, from the SAME warmed state
    sD = st.copy(); sND = st.copy()
    for ph in (0, 1):
        amps = [hist[i][ph] for i in range(K)]
        for _ in range(PHASE):
            for i in range(K): sD.N = sD.N + amps[i] * pts[i]
            sD = eng.step(sD)
    for _ in range(2 * PHASE): sND = eng.step(sND)
    for _ in range(C.SETTLE): sD = eng.step(sD); sND = eng.step(sND)

    entsD = sorted(detect(sD, C.DET), key=lambda e: -e.size)
    regs = [emask(nearest(c, entsD)) for c in cents]

    # (1) residual confound at readout (settle=120) vs no-drive, per droplet
    rows = []
    for i, reg in enumerate(regs):
        mp = sum(region_mem(sD, reg))                       # stored memory m_plus (m1+m2)
        resN = float((sD.N - sND.N)[reg].mean())            # residual nutrient above counterfactual
        resc = float((sD.c - sND.c)[reg].mean())            # residual attractant
        dupt = float((sD.uptake - sND.uptake)[reg].mean())  # in-place behavioural signal (confounded)
        rows.append((seed, i, dose[i], order[i], mp, resN, resc, dupt))

    # washout curve: residual ΔN in regions as function of extra steps
    wcs = {}
    aD = sD.copy(); aND = sND.copy()
    for W in (0, 120, 300, 600, 1000):
        if W > 0:
            for _ in range(W - (max([0]+[w for w in wcs]) if wcs else 0)):
                aD = eng.step(aD); aND = eng.step(aND)
        wcs[W] = float(np.mean([ (aD.N - aND.N)[reg].mean() for reg in regs ]))

    # (2) standardized behaviour: transplant each droplet's region-mean memory into a COMMON erased body,
    #     neutral settle, read specific_uptake + mean_c. Intact vs ablation (should collapse).
    def common_body():
        b = sND.copy(); e = nearest(cents[0], sorted(detect(b, C.DET), key=lambda e:-e.size))
        b.Mf = np.zeros_like(b.Mf); return b, emask(e)
    def transplant_read(engine, donor_m, settle=80):
        b, bmask = common_body()
        b.Mf[0][bmask] = b.rho[bmask] * donor_m[0]; b.Mf[1][bmask] = b.rho[bmask] * donor_m[1]
        for _ in range(settle): b = engine.step(b)
        es = detect(b, C.DET)
        if not es: return None
        e = max(es, key=lambda e: e.size); reg = emask(e)
        return e.specific_uptake, float(b.c[reg].mean())
    eng_abl = build(MC_ABL)
    tp = []
    base = transplant_read(eng, (0.0, 0.0))
    for i, reg in enumerate(regs):
        dm = region_mem(sD, reg)
        ri = transplant_read(eng, dm); ra = transplant_read(eng_abl, dm)
        tp.append((seed, i, dose[i], order[i], dm[0] + dm[1], dm[0] - dm[1],
                   ri[0], ri[1], ra[0], ra[1], base[0], base[1]))
    return rows, wcs, tp

def main():
    seeds = [int(x) for x in sys.argv[1:]] or [50001, 50002, 50003, 50004]
    allrows = []; allwc = {}; alltp = []
    for s in seeds:
        r = run(s)
        if r is None: print(f"seed {s}: <K droplets, skip"); continue
        rows, wcs, tp = r; allrows += rows; alltp += tp
        for W, v in wcs.items(): allwc.setdefault(W, []).append(v)
        print(f"seed {s}: ok, doses={[round(x,4) for x in [rr[2] for rr in rows]]}")
    A = np.array([r[2:] for r in allrows], float)  # dose,order,mp,resN,resc,dupt
    dose, order, mp, resN, resc, dupt = A.T
    def pear(a, b):
        a = a - a.mean(); b = b - b.mean()
        return float((a @ b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))
    print("\n==== RESIDUAL CONFOUND at readout (settle=120), n_droplets=", len(A), "====")
    print(f"  N0(ambient)={N0}")
    print(f"  residual ΔN: mean={resN.mean():.4f} ({100*resN.mean()/N0:.1f}% of N0)  range=[{resN.min():.4f},{resN.max():.4f}]")
    print(f"  residual Δc: mean={resc.mean():.4f}  range=[{resc.min():.4f},{resc.max():.4f}]")
    print(f"  stored memory m_plus: mean={mp.mean():.4f} range=[{mp.min():.4f},{mp.max():.4f}]")
    print(f"  in-place Δuptake: mean={dupt.mean():.3e} range=[{dupt.min():.3e},{dupt.max():.3e}]")
    print(f"  corr(dose, residual ΔN)  = {pear(dose,resN):+.3f}   <- residual pathway strength")
    print(f"  corr(dose, stored m_plus)= {pear(dose,mp):+.3f}   <- memory writing")
    print(f"  corr(dose, in-place Δupt)= {pear(dose,dupt):+.3f}")
    print(f"  corr(resN, in-place Δupt)= {pear(resN,dupt):+.3f}   <- is Δuptake driven by residual N?")
    print(f"  corr(m_plus,in-place Δupt)= {pear(mp,dupt):+.3f}")
    # relative magnitude: memory modulation of uptake vs residual-N modulation of uptake
    # uptake ∝ N*(1+lam_plus*m_plus). Δuptake_mem/uptake ≈ lam_plus*Δm_plus ; Δuptake_resN/uptake ≈ ΔN/N
    print(f"  est. fractional uptake modulation: memory≈lam_plus*|m_plus|~{0.25*np.abs(mp).mean():.4f}"
          f"  vs residual≈|ΔN|/N0~{np.abs(resN).mean()/N0:.4f}"
          f"  ratio(residual/memory)~{ (np.abs(resN).mean()/N0)/(0.25*np.abs(mp).mean()+1e-12):.1f}x")
    print("\n==== WASHOUT CURVE: residual ΔN in regions vs extra steps ====")
    for W in sorted(allwc): print(f"  +{W:4d} steps: mean residual ΔN = {np.mean(allwc[W]):+.5f} ({100*np.mean(allwc[W])/N0:+.2f}% N0)")
    T = np.array([r[2:] for r in alltp], float)  # dose,order,mp,mm,ui,ci,ua,ca,ub,cb
    dose2, order2, mp2, mm2, ui, ci, ua, ca, ub, cb = T.T
    print("\n==== STANDARDIZED memory->behaviour (transplant into common body, neutral settle) ====")
    print(f"  base (zero-memory) uptake={ub.mean():.4f}  mean_c={cb.mean():.4f}")
    print(f"  intact  : Δuptake vs base mean={ (ui-ub).mean():+.3e}  Δmean_c mean={(ci-cb).mean():+.3e}")
    print(f"  ablation: Δuptake vs base mean={ (ua-ub).mean():+.3e}  Δmean_c mean={(ca-cb).mean():+.3e}  (should ≈0)")
    print(f"  corr(dose,  intact uptake)= {pear(dose2,ui):+.3f}   corr(order, intact mean_c)= {pear(order2,ci):+.3f}")
    print(f"  corr(dose,  ablat  uptake)= {pear(dose2,ua):+.3f}   corr(order, ablat  mean_c)= {pear(order2,ca):+.3f}  (collapse check)")
    print(f"  corr(m_plus,intact uptake)= {pear(mp2,ui):+.3f}   corr(m_minus,intact mean_c)= {pear(mm2,ci):+.3f}")

if __name__ == "__main__":
    main()
