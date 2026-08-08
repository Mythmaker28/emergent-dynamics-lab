"""LCI-CAUSAL-NONMERGING-CONFIRM-02 — corrected non-fusing behavioural causal runner (frozen; resumable).

Corrects LCI-CAUSAL-CONFIRMATION-01 per the merge-incident audit:
  - PROBE: uniform amp=0.25 for dur=5 (cumulative injection 1.25xN0). Selected by DEV GEOMETRY ONLY
    (geom_char.py): horizon-stable margin, max grid coverage ~3.4% << 15% cap, 3 distinct components, 3 alive,
    no MERGE/SPLIT/LOST/AMBIGUOUS on all DEV worlds. The causal effect was NOT consulted to pick it.
  - N STANDARDISATION (reset N:=N0), NOT a "washout": residual removed by construction; paired contrast cancels
    any remainder. No natural-washout survival gate.
  - PRIMARY individual readout = uptake integrated on the component followed by the BIJECTIVE one-to-one tracker
    (bijective_tracker.py), which censors MERGE/SPLIT/LOST/AMBIGUOUS instead of double-counting.
  - FIXED-MASK readout kept as a tracker-free CONVERGENT control (G5), not primary identity.
  - WORLD-LEVEL censorship: if ANY of the 3 targets is censored (or coverage>=cap, or <3 distinct) in ANY
    contrast branch {intact, erase x3, sham}, the WORLD is G0-INVALID for primary analysis (never keep only the
    survivors; record reason+step; counts against feasibility). All seeds appear in the raw.
  - Readout is honestly a DIRECTLY-COUPLED uptake (g ∝ N·ρ·(1+λ₊·m₊)); the paired contrast is what makes it causal.
  - No transplant (removed this mission). Storage block verbatim from the sealed pipeline for G1/G2.

Branches per seed: intact | erase_j (j=1..K) | sham | ablate | erase_ablate_j (ablation manipulation check).
"""
import sys, json, os, itertools, importlib.util
import numpy as np
cc_spec = importlib.util.spec_from_file_location("cc", os.path.join(os.path.dirname(__file__), "causal_confirm.py"))
cc = importlib.util.module_from_spec(cc_spec); cc_spec.loader.exec_module(cc)
bt_spec = importlib.util.spec_from_file_location("bt", os.path.join(os.path.dirname(__file__), "bijective_tracker.py"))
bt = importlib.util.module_from_spec(bt_spec); bt_spec.loader.exec_module(bt)
from edlab.substrates.scaffold.observables import detect
from edlab.experiments.sc_mcm import config as C

K = cc.K; N = cc.N; DET = C.DET; N0 = cc.N0; GRID = N * N

# ---------------- FROZEN CONFIRM-02 behavioural constants (geometry-selected; pre-data) ----------------
PROBE_MODE = "uniform"
STIM_AMP = 0.25          # amplitude added to N per step (uniform, common to all targets)
STIM_DUR = 5             # number of stimulus steps  -> cumulative injection 1.25 * N0
HORIZON = 40             # behavioural horizon; readout = integrated uptake over [1,HORIZON]
SETTLE_STD = 40          # N-standardisation settle before the probe (post reset N:=N0)
COVER_CAP = 0.15         # G0 giant-component cap (fraction of grid)
THETA = cc.TRACK_THETA   # 0.10 (bijective tracker overlap threshold; = sealed tracker theta)

def measure(S0, cents, engine, erase_mask=None):
    """Corrected branch: N-standardise, settle, probe, integrate uptake on the BIJECTIVELY-tracked component
    and on the FIXED initial mask. Returns per-target readouts + per-step geometry + censorship events."""
    st = S0.copy()
    if erase_mask is not None:
        st.Mf[:, erase_mask] = 0.0
    st.N = np.full_like(st.N, N0)                       # N standardisation (NOT washout)
    for _ in range(SETTLE_STD): st = engine.step(st)
    tracks0, _ = cc.region_masks(st, cents)
    fixed = [t.copy() for t in tracks0]
    tr = bt.BijectiveTracker(theta=THETA)
    seeds_tr = tr.seed(tracks0, 0)
    integ_tracked = [0.0] * K; integ_fixed = [0.0] * K
    last_mass = [0.0] * K; last_size = [0] * K; last_meanc = [0.0] * K
    censor = [None] * K            # (step, status) per target
    max_cov = 0.0; min_distinct = K
    for t in range(1, HORIZON + 1):
        if t <= STIM_DUR:
            st.N = st.N + STIM_AMP                      # uniform common stimulus
        st = engine.step(st)
        ents = detect(st, DET); emasks = [cc.mask(e) for e in ents]; esz = [int(m.sum()) for m in emasks]
        ev = tr.update(emasks, t)
        for tid, status in ev.items():
            if censor[tid] is None: censor[tid] = (t, status)
        # integrate: fixed always; tracked only while the track is ALIVE
        for i in range(K):
            integ_fixed[i] += float(st.uptake[fixed[i]].sum())
            tk = tr.tracks[i]
            if tk.status == bt.ALIVE:
                reg = tk.mask
                integ_tracked[i] += float(st.uptake[reg].sum())
                last_mass[i] = float(st.rho[reg].sum()); last_size[i] = int(reg.sum())
                last_meanc[i] = float(st.c[reg].mean())
        alive = [tk for tk in tr.tracks if tk.status == bt.ALIVE]
        min_distinct = min(min_distinct, len(alive))
        max_cov = max(max_cov, (max(esz) if esz else 0) / GRID)
    summ = tr.summary()
    valid = (summ["alive"] == K and max_cov < COVER_CAP and min_distinct == K)
    return dict(tracked=integ_tracked, fixed=integ_fixed, mass=last_mass, size=last_size, mean_c=last_meanc,
                statuses=[tr.tracks[i].status for i in range(K)], censor=censor,
                max_cov=float(max_cov), min_distinct=int(min_distinct), branch_valid=bool(valid))

def run_seed(seed):
    rng = np.random.default_rng(seed)
    eng = cc.build(cc.MEM_INTACT); eng_abl = cc.build(cc.MEM_ABLATE)
    st = cc.seed_world(seed)
    for _ in range(cc.WARM): st = eng.step(st)
    T = cc.pick(sorted(detect(st, DET), key=lambda e: -e.size))
    n_detected = len([e for e in detect(st, DET)])
    if len(T) < K:
        return {"seed": seed, "eligible": False, "reason": "fewer_than_K_eligible", "n_detected": n_detected}
    cents = [e.centroid for e in T]; sigs = [max(3.0, e.rg * 0.8) for e in T]; sizes = [e.size for e in T]
    pts = [cc.patch(*cents[i], sigs[i]) for i in range(K)]
    hist = [(float(rng.uniform(cc.AMP_LO, cc.AMP_HI)), float(rng.uniform(cc.AMP_LO, cc.AMP_HI))) for _ in range(K)]
    dose = [a1 + a2 for a1, a2 in hist]; order = [a2 - a1 for a1, a2 in hist]
    dists = [cc.pdist(cents[a], cents[b]) for a, b in itertools.combinations(range(K), 2)]

    # ---- STORAGE block (verbatim structure from causal_confirm for G1/G2) ----
    sS = st.copy()
    for ph in (0, 1):
        amps = [hist[i][ph] for i in range(K)]
        for _ in range(cc.PHASE):
            for i in range(K): sS.N = sS.N + amps[i] * pts[i]
            sS = eng.step(sS)
    for _ in range(cc.SETTLE): sS = eng.step(sS)
    entsS = sorted(detect(sS, DET), key=lambda e: -e.size)
    feat = [cc.feats(sS, cc.nearest(c, entsS)) for c in cents]
    sB = st.copy()
    for _ in range(2 * cc.PHASE + cc.SETTLE): sB = eng.step(sB)
    upB = sB.uptake.copy()
    entsB = sorted(detect(sB, DET), key=lambda e: -e.size); regs = [cc.mask(cc.nearest(c, entsB)) for c in cents]
    Cm = np.zeros((K, K)); Cu = np.zeros((K, K))
    for i in range(K):
        sA = st.copy()
        for ph in (0, 1):
            a = hist[i][ph]
            for _ in range(cc.PHASE): sA.N = sA.N + a * pts[i]; sA = eng.step(sA)
        for _ in range(cc.SETTLE): sA = eng.step(sA)
        mpA = (sA.Mf[0] + sA.Mf[1]) / np.maximum(sA.rho, 1e-9); dU = np.abs(sA.uptake - upB)
        mpB = (sB.Mf[0] + sB.Mf[1]) / np.maximum(sB.rho, 1e-9); dM = np.abs(mpA - mpB)
        for j in range(K): Cm[i, j] = float(dM[regs[j]].mean()); Cu[i, j] = float(dU[regs[j]].mean())

    # ---- CORRECTED BEHAVIOURAL block ----
    S0 = sS.copy()
    reg0, _ = cc.region_masks(S0, cents)
    empty = cc.empty_patch_mask(S0, cents)
    A = measure(S0, cents, eng, erase_mask=None)
    Bsham = measure(S0, cents, eng, erase_mask=empty)
    Eabl = measure(S0, cents, eng_abl, erase_mask=None)
    Xstd = [measure(S0, cents, eng, erase_mask=reg0[j]) for j in range(K)]
    Xabl = [measure(S0, cents, eng_abl, erase_mask=reg0[j]) for j in range(K)]

    # ---- WORLD-LEVEL G0 validity: all contrast branches clean ----
    contrast_branches = [A, Bsham] + Xstd
    g0_valid = all(b["branch_valid"] for b in contrast_branches)
    invalid_reason = None
    if not g0_valid:
        bad = []
        if not A["branch_valid"]: bad.append(f"intact({A['statuses']},cov={A['max_cov']:.3f})")
        if not Bsham["branch_valid"]: bad.append("sham")
        for j in range(K):
            if not Xstd[j]["branch_valid"]: bad.append(f"erase{j}")
        invalid_reason = "; ".join(bad)

    return {
        "seed": seed, "eligible": True, "n_detected": n_detected,
        "cents": [[float(x) for x in c] for c in cents], "sizes": sizes, "hist": hist,
        "dose": dose, "order": order, "dists": dists,
        "feat": feat, "Cm": Cm.tolist(), "Cu": Cu.tolist(),
        "g0_valid": bool(g0_valid), "invalid_reason": invalid_reason,
        "max_cov_intact": A["max_cov"], "min_distinct_intact": A["min_distinct"],
        "beh": {"intact": A, "sham": Bsham, "ablate": Eabl,
                "erase": Xstd, "erase_ablate": Xabl},
    }

def main():
    out = sys.argv[1]; seeds = [int(x) for x in sys.argv[2:]]
    data = json.load(open(out)) if os.path.exists(out) else []
    done = {d["seed"] for d in data}
    for s in seeds:
        if s in done: print("skip", s); continue
        r = run_seed(s); data.append(r); json.dump(data, open(out, "w"))
        if not r["eligible"]:
            print(f"seed {s}: INELIGIBLE ({r.get('reason')})")
        else:
            A = r["beh"]["intact"]; er = r["beh"]["erase"]
            own = [A["tracked"][i] - er[i]["tracked"][i] for i in range(K)]
            tag = "G0-VALID" if r["g0_valid"] else f"G0-INVALID[{r['invalid_reason']}]"
            print(f"seed {s}: {tag} cov={r['max_cov_intact']:.3f} own_tracked={[round(x,3) for x in own]}")

if __name__ == "__main__":
    main()
