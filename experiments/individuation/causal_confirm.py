"""LCI-CAUSAL-CONFIRMATION-01 — non-confounded behavioural causal runner (frozen protocol; resumable).

Two blocks per seed/world:

(1) STORAGE block — VERBATIM from exp1_prospective.py (frozen C1c engine, K=3 targets size>=45 pairwise>=24,
    simultaneous local Gaussian nutrient histories, 11-D memory features read in place, memory-write &
    behavioural influence matrices Cm/Cu). Output schema is a superset of exp1_prospective_raw.json so
    exp1_reaudit.py consumes it directly for K2a (storage/readout replication) and C-K1.

(2) BEHAVIOURAL CAUSAL block — the NEW, non-confounded test. From the common post-history snapshot S0 we
    build counterfactual BRANCHES that share body+environment and differ ONLY by a local do-intervention on
    the memory field, then STANDARDISE the nutrient stimulus (N:=N0 uniform; N-only, does not touch rho/m/c),
    a fixed washout, a COMMON uniform stimulus, and a fixed-horizon integrated behavioural readout (nutrient
    consumed by each tracked droplet + growth). Residual nutrient is common-mode across intact vs erase and is
    removed between droplets by the N-standardisation, so a surviving own-history behavioural signal that
    (a) disappears when the target's memory is erased, (b) does NOT disappear when a neighbour's is erased,
    (c) collapses under readout ablation, (d) is unaffected by the sham, is attributable to the STORED MEMORY
    and not to environmental residue. No new physics: only field reads, an N reset, existing ablation, a
    uniform nutrient probe, and local memory zeroing.

Branches (per seed): A intact | B sham (erase empty patch) | E ablation (lam_plus=lam_minus=0) |
    X_j erase droplet j's memory (j=1..K; gives erase-target for i=j and erase-neighbour for i!=j) |
    F inert memory (m frozen at written value) | + un-standardised doublets A_res, X_j^res for the
    reset<->erase double dissociation. NO-DRIVE counterfactual baseline also measured.
"""
import sys, json, os, itertools
import numpy as np
from edlab.experiments.sc_mcm.engine import MultiChannelMemoryEngine, MCParams
from edlab.experiments.sc_mcm import config as C
from edlab.experiments.sc_iom.engine import IOMState
from edlab.substrates.scaffold.observables import detect

# ---------------- FROZEN storage constants (identical to exp1_prospective.py) ----------------
C1c = dict(eta_w=0.015, eta_d1=0.35, eta_d2=0.006, k_exp=1.0)
N = C.SPEC.size; N0 = C.SPEC.N0
K = 3; SEP = 24.0; MINSIZE = 45; WARM = 800; PHASE = 60; AMP_LO = 0.005; AMP_HI = 0.035
LAM_PLUS = 0.25; LAM_MINUS = 0.15

# ---------------- FROZEN behavioural-causal constants (pre-declared, this mission) ----------------
SETTLE = C.SETTLE            # 120 — post-drive settle to the common snapshot S0
WASHOUT_B = 40              # post-standardisation transient-settle steps before the common stimulus
WASHOUT_LONG = 200         # long natural washout (NO N reset) — residual ΔN decays to <~1% N0 (DEV curve) → G3 "survives washout"
STIM_AMP = 0.50            # uniform common nutrient stimulus amplitude (frozen PROBE amp)
STIM_DUR = 15              # stimulus duration (frozen PROBE dur)
HORIZON = 120             # behavioural measurement horizon after stimulus onset (frozen PROBE_HORIZON)
TRACK_THETA = 0.1          # frozen overlap tracker threshold (TRACKER_SPEC)
TRACK_CADENCE = 1          # integrate every step (finer than the 5-step matching cadence, geometry-only)

def build(mem): return MultiChannelMemoryEngine(C.SPEC, mem, C.TRACER)
MEM_INTACT = MCParams(lam_plus=LAM_PLUS, lam_minus=LAM_MINUS, **C1c)
MEM_ABLATE = MCParams(lam_plus=0.0,      lam_minus=0.0,       **C1c)

def seed_world(seed):
    s = C.seed_state(C.SPEC, C.TRACER, seed, "random")
    return IOMState(s.rho, s.U, s.V, s.c, s.N, s.C, s.uptake, np.zeros((2, N, N)), 0)
def pdist(a, b):
    d = np.abs(np.array(a) - np.array(b)); d = np.minimum(d, N - d); return float(np.hypot(*d))
def patch(cy, cx, sig):
    ys, xs = np.mgrid[0:N, 0:N]
    dy = np.minimum(np.abs(ys - cy), N - np.abs(ys - cy)); dx = np.minimum(np.abs(xs - cx), N - np.abs(xs - cx))
    return np.exp(-(dy**2 + dx**2) / (2 * sig**2))
def mask(e):
    m = np.zeros((N, N), bool); m[e.cells[:, 0], e.cells[:, 1]] = True; return m
def feats(s, e):
    reg = mask(e); m1 = s.Mf[0][reg] / np.maximum(s.rho[reg], 1e-9); m2 = s.Mf[1][reg] / np.maximum(s.rho[reg], 1e-9)
    f = []
    for v in (m1, m2): f += [float(v.mean()), float(v.std()), float(np.percentile(v, 10)), float(np.percentile(v, 50)), float(np.percentile(v, 90))]
    f.append(float((m1 - m2).std())); return f
def pick(ents):
    ch = []
    for e in sorted(ents, key=lambda e: -e.size):
        if e.size < MINSIZE: continue
        if all(pdist(e.centroid, o.centroid) >= SEP for o in ch): ch.append(e)
        if len(ch) >= K: break
    return ch
def nearest(c, es): return min(es, key=lambda e: pdist(e.centroid, c))
def overlap(m, e):
    em = mask(e); return (m & em).sum() / max(1, m.sum())

# ---------------- behavioural branch measurement ----------------
def region_masks(st, cents):
    ents = sorted(detect(st, C.DET), key=lambda e: -e.size)
    return [mask(nearest(c, ents)) for c in cents], ents

def empty_patch_mask(st, cents):
    """A control region of ~droplet size on empty space (rho<threshold), far from every target, for the sham."""
    occupied = st.rho > 0.30 * C.SPEC.rho_max
    ys, xs = np.mgrid[0:N, 0:N]
    # farthest-from-any-target empty cell as centre
    dmin = np.full((N, N), 1e9)
    for cy, cx in cents:
        dy = np.minimum(np.abs(ys - cy), N - np.abs(ys - cy)); dx = np.minimum(np.abs(xs - cx), N - np.abs(xs - cx))
        dmin = np.minimum(dmin, np.hypot(dy, dx))
    dmin[occupied] = -1
    cy, cx = np.unravel_index(np.argmax(dmin), dmin.shape)
    dy = np.minimum(np.abs(ys - cy), N - np.abs(ys - cy)); dx = np.minimum(np.abs(xs - cx), N - np.abs(xs - cx))
    return (np.hypot(dy, dx) <= 4.0) & (~occupied)

def measure_branch(S0, cents, engine, erase_mask=None, standardize=True, inert=False, washout=WASHOUT_B):
    """Return per-droplet integrated behavioural response over the common stimulus + horizon.
    erase_mask: bool grid whose Mf is zeroed (target/neighbour/empty). standardize: N:=N0 uniform.
    inert: freeze intensive memory m at its written value (m does not write/decay/template during the branch).
    washout: settle steps before the common stimulus (WASHOUT_B standardised, WASHOUT_LONG for natural washout).
    """
    st = S0.copy()
    if erase_mask is not None:
        st.Mf[:, erase_mask] = 0.0
    if standardize:
        st.N = np.full_like(st.N, N0)                 # N-only reset; rho, U, V, c, Mf untouched
    m_frozen = (st.Mf / np.maximum(st.rho, 1e-9)[None]) if inert else None
    def step(s):
        o = engine.step(s)
        if inert: o.Mf = o.rho[None] * m_frozen        # re-impose the frozen intensive memory
        return o
    for _ in range(washout): st = step(st)
    tracks, _ = region_masks(st, cents); alive = [True] * K
    fixed = [t.copy() for t in tracks]                  # geometry-fixed masks (tracker-independent readout, C-K5)
    integ_upt = [0.0] * K; integ_fixed = [0.0] * K; last_mass = [0.0] * K; last_size = [0] * K; last_meanc = [0.0] * K
    for t in range(1, HORIZON + 1):
        if t <= STIM_DUR: st.N = st.N + STIM_AMP        # uniform common stimulus (all droplets, all branches)
        st = step(st)
        ents = detect(st, C.DET)
        for i in range(K):
            integ_fixed[i] += float(st.uptake[fixed[i]].sum())   # fixed initial region — no tracker
            if not alive[i]: continue
            best = max(ents, key=lambda e: overlap(tracks[i], e), default=None)
            if best is None or overlap(tracks[i], best) < TRACK_THETA:
                alive[i] = False; continue
            tracks[i] = mask(best)
            reg = tracks[i]
            integ_upt[i] += float(st.uptake[reg].sum())
            last_mass[i] = float(st.rho[reg].sum()); last_size[i] = int(reg.sum())
            last_meanc[i] = float(st.c[reg].mean())
    return dict(integ_upt=integ_upt, integ_fixed=integ_fixed, mass=last_mass, size=last_size, mean_c=last_meanc, alive=alive)

# ---------------- per seed ----------------
def run_seed(seed):
    rng = np.random.default_rng(seed)
    eng = build(MEM_INTACT); eng_abl = build(MEM_ABLATE)
    st = seed_world(seed)
    for _ in range(WARM): st = eng.step(st)
    T = pick(sorted(detect(st, C.DET), key=lambda e: -e.size))
    n_detected = len([e for e in detect(st, C.DET)])
    if len(T) < K:
        return {"seed": seed, "ok": False, "reason": "fewer_than_K_eligible", "n_detected": n_detected}
    cents = [e.centroid for e in T]; sigs = [max(3.0, e.rg * 0.8) for e in T]; sizes = [e.size for e in T]
    pts = [patch(*cents[i], sigs[i]) for i in range(K)]
    hist = [(float(rng.uniform(AMP_LO, AMP_HI)), float(rng.uniform(AMP_LO, AMP_HI))) for _ in range(K)]
    dose = [a1 + a2 for a1, a2 in hist]; order = [a2 - a1 for a1, a2 in hist]

    # ---- STORAGE block (verbatim structure from exp1_prospective) ----
    sS = st.copy()
    for ph in (0, 1):
        amps = [hist[i][ph] for i in range(K)]
        for _ in range(PHASE):
            for i in range(K): sS.N = sS.N + amps[i] * pts[i]
            sS = eng.step(sS)
    for _ in range(SETTLE): sS = eng.step(sS)
    entsS = sorted(detect(sS, C.DET), key=lambda e: -e.size)
    feat = [feats(sS, nearest(c, entsS)) for c in cents]
    # influence matrices (differential vs no-drive baseline)
    sB = st.copy()
    for _ in range(2 * PHASE + SETTLE): sB = eng.step(sB)
    upB = sB.uptake.copy()
    entsB = sorted(detect(sB, C.DET), key=lambda e: -e.size); regs = [mask(nearest(c, entsB)) for c in cents]
    Cm = np.zeros((K, K)); Cu = np.zeros((K, K))
    for i in range(K):
        sA = st.copy()
        for ph in (0, 1):
            a = hist[i][ph]
            for _ in range(PHASE): sA.N = sA.N + a * pts[i]; sA = eng.step(sA)
        for _ in range(SETTLE): sA = eng.step(sA)
        mpA = (sA.Mf[0] + sA.Mf[1]) / np.maximum(sA.rho, 1e-9); dU = np.abs(sA.uptake - upB)
        mpB = (sB.Mf[0] + sB.Mf[1]) / np.maximum(sB.rho, 1e-9); dM = np.abs(mpA - mpB)
        for j in range(K): Cm[i, j] = float(dM[regs[j]].mean()); Cu[i, j] = float(dU[regs[j]].mean())

    # ---- BEHAVIOURAL CAUSAL block ----
    S0 = sS.copy()                                   # common post-history snapshot
    reg0, _ = region_masks(S0, cents)                # target regions at snapshot
    empty = empty_patch_mask(S0, cents)
    # standardised branches
    A  = measure_branch(S0, cents, eng, erase_mask=None,  standardize=True)                 # intact
    Bsham = measure_branch(S0, cents, eng, erase_mask=empty, standardize=True)              # sham
    Eabl = measure_branch(S0, cents, eng_abl, erase_mask=None, standardize=True)            # readout ablation
    Finert = measure_branch(S0, cents, eng, erase_mask=None, standardize=True, inert=True)  # inert memory
    Xstd = [measure_branch(S0, cents, eng, erase_mask=reg0[j], standardize=True) for j in range(K)]  # erase j
    Xabl = [measure_branch(S0, cents, eng_abl, erase_mask=reg0[j], standardize=True) for j in range(K)]  # erase j under ablation (collapse)
    # un-standardised doublet for reset<->erase double dissociation (residual N kept)
    Ares = measure_branch(S0, cents, eng, erase_mask=None, standardize=False)
    Xres = [measure_branch(S0, cents, eng, erase_mask=reg0[j], standardize=False) for j in range(K)]
    # long natural washout (no reset): residual decays away naturally -> "survives washout" (G3)
    Along = measure_branch(S0, cents, eng, erase_mask=None, standardize=False, washout=WASHOUT_LONG)
    Xlong = [measure_branch(S0, cents, eng, erase_mask=reg0[j], standardize=False, washout=WASHOUT_LONG) for j in range(K)]
    # no-drive counterfactual behavioural baseline (from the no-drive world sB, standardised + stimulus)
    ndc = measure_branch(sB, cents, eng, erase_mask=None, standardize=True)

    return {
        "seed": seed, "ok": True, "n_detected": n_detected,
        "cents": [[float(x) for x in c] for c in cents], "sizes": sizes, "hist": hist,
        "dose": dose, "order": order,
        "dists": [pdist(cents[a], cents[b]) for a, b in itertools.combinations(range(K), 2)],
        "feat": feat, "Cm": Cm.tolist(), "Cu": Cu.tolist(),
        # behavioural branches: per-droplet integrated response + survival
        "beh": {
            "intact": A, "sham": Bsham, "ablate": Eabl, "inert": Finert,
            "erase": [Xstd[j] for j in range(K)],       # erase[j] = branch with droplet j's memory erased
            "erase_ablate": [Xabl[j] for j in range(K)], # erase[j] under readout ablation (collapse control)
            "intact_res": Ares, "erase_res": [Xres[j] for j in range(K)],
            "intact_long": Along, "erase_long": [Xlong[j] for j in range(K)],
            "nodrive": ndc,
        },
    }

def main():
    out = sys.argv[1]; seeds = [int(x) for x in sys.argv[2:]]
    data = json.load(open(out)) if os.path.exists(out) else []
    done = {d["seed"] for d in data}
    for s in seeds:
        if s in done: print("skip", s); continue
        r = run_seed(s); data.append(r); json.dump(data, open(out, "w"))
        if r["ok"]:
            A = r["beh"]["intact"]["integ_upt"]; Xi = [r["beh"]["erase"][j]["integ_upt"][j] for j in range(K)]
            eff = [A[i] - Xi[i] for i in range(K)]
            print(f"seed {s}: ok dose={[round(x,3) for x in r['dose']]} "
                  f"eff(A-eraseTarget)={[f'{e:+.3e}' for e in eff]}")
        else:
            print(f"seed {s}: ok=False ({r.get('reason')})")

if __name__ == "__main__":
    main()
