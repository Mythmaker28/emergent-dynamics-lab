"""LCI-CAUSAL-TURNOVER-PREREG-03 — DEV turnover runner (resumable; NO new prospective family, NO confirmatory seed).

Runs ONLY on DEV seeds (50001-50010). Per seed:
  (1) STORAGE block — VERBATIM from the sealed confirm-02 pipeline (C1c engine, K=3 targets size>=45 pairwise>=24,
      simultaneous local Gaussian nutrient histories) -> rest snapshot S0, storage feats, memory-write matrix Cm.
  (2) REST causal assay — the FROZEN confirm-02 `nm.measure` battery (probe uniform 0.25x5, N-standardise, horizon
      40, bijective + fixed-mask readout) on branches {intact, sham, ablate, erase_j, erase_ablate_j}.
  (3) TURNOVER — NEUTRAL (no drive, no behavioural probe), C1c UNCHANGED, memory writing LEFT ACTIVE
      (justified in PROTOCOL Phase 4C), run on the UNPERTURBED world with per-target PASSIVE material tracers and
      the BIJECTIVE tracker. Records M_i, P_i, G every REC_CADENCE steps with explicit MERGE/SPLIT/LOST/AMBIGUOUS
      censorship. Deep snapshot = first pre-declared step where all 3 are ALIVE + distinct + non-fusing
      (coverage < cap) + each M_i <= 0.25. If not reached before TURN_CAP -> FEASIBILITY INVALID (reason recorded).
  (4) DEEP causal assay — the SAME frozen `nm.measure` battery at the deep snapshot (same probe/horizon/gates).
  (5) PASSIVE-DECAY NULL — a parallel eta_w=0 (no new writing) world to matched depth; deep memory feature
      separation own-vs-neighbour, as a diagnostic to distinguish passive copy from any reconstruction.

This runner opens NO new prospective family. It runs NO confirmatory seed. DEV only. Engine frozen (no physics
change on the main line; the ablation and no-write engines are pre-existing counterfactual variants).
"""
import sys, os, json, importlib.util
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
def _load(name, fn):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
cc = _load("cc", "causal_confirm.py")
nm = _load("nm", "nonmerging_confirm.py")
bt = _load("bt", "bijective_tracker.py")
mt = _load("mt", "material_tracer.py")
te = _load("te", "turnover_event_evidence.py")

from edlab.substrates.scaffold.observables import detect
from edlab.experiments.sc_mcm import config as C
from edlab.experiments.sc_mcm.engine import MCParams

K = cc.K; N = cc.N; N0 = cc.N0; DET = C.DET; GRID = N * N

# ---------------- frozen turnover constants (DEV; pre-declared, pre-data) ----------------
M_TARGET = 0.25             # per-droplet deep material retention threshold (deeper than the legacy 0.35)
TURN_CAP = 1500             # max turnover steps; else FEASIBILITY INVALID
REC_CADENCE = 10            # record M_i/P_i/G every REC_CADENCE steps
COVER_CAP = nm.COVER_CAP    # 0.15 giant-component fraction
THETA = nm.THETA            # 0.10 bijective tracker overlap threshold
C1c = dict(eta_w=0.015, eta_d1=0.35, eta_d2=0.006, k_exp=1.0)
MEM_NOWRITE = MCParams(lam_plus=0.25, lam_minus=0.15, eta_w=0.0, eta_d1=0.35, eta_d2=0.006, k_exp=1.0)


def phen(st, e):
    reg = cc.mask(e)
    return dict(size=int(e.size), mass=float(e.mass), rg=float(e.rg),
                uptake=float(e.specific_uptake), mean_sig=float(e.mean_sig),
                janus=float(e.phenotype[4]), radial_u=float(e.phenotype[3]),
                interface=float(e.phenotype[2]), mean_c=float(st.c[reg].mean()))


def mem_stats(st, reg):
    m1 = st.Mf[0][reg] / np.maximum(st.rho[reg], 1e-9); m2 = st.Mf[1][reg] / np.maximum(st.rho[reg], 1e-9)
    return dict(m1=float(m1.mean()), m2=float(m2.mean()),
                mplus=float(np.tanh(m1 + m2).mean()), mminus=float(np.tanh(m1 - m2).mean()))


def _match_entity(ents, mask):
    return max(ents, key=lambda e: int((cc.mask(e) & mask).sum()), default=None)


def turnover(S0, cents, reg0, eng, record=True, cap=TURN_CAP):
    """Neutral turnover on the UNPERTURBED world with per-target passive tracers + bijective tracker.
    Returns trajectory, first-censor events, persisted event evidence, and the deep snapshot.

    When a censoring event occurs, the world is invalid at that first step. The engine is nevertheless advanced
    for exactly five additional evidence-only frames so a persistent fission can be distinguished from transient
    fragmentation and a local mass collapse (death) from tracking loss. No daughter or replacement component is
    selected as a continuation, and the follow-up cannot restore feasibility.
    """
    Sturn, base = mt.seed_tracers(S0, reg0)
    mt.assert_no_feed_collision(eng.tracer, base, cap + 2)
    tr = bt.BijectiveTracker(theta=THETA)
    tr.seed([m.copy() for m in reg0], 0)
    traj = []; first_censor = {}; deep = None; event_evidence = []
    for t in range(1, cap + 1):
        Sturn = eng.step(Sturn)
        ents = detect(Sturn, DET); emasks = [cc.mask(e) for e in ents]; esz = [int(m.sum()) for m in emasks]
        parent_masks = [tr.tracks[i].mask.copy() for i in range(K)]
        ev = tr.update(emasks, t)
        for tid, stt in ev.items(): first_censor.setdefault(int(tid), (t, stt))
        alive = [tr.tracks[i].status == bt.ALIVE for i in range(K)]
        cov = (max(esz) / GRID) if esz else 0.0
        regs_now = [tr.tracks[i].mask if alive[i] else None for i in range(K)]
        rec = (t % REC_CADENCE == 0)
        mat = mt.read_material(Sturn, base, regs_now) if (rec or all(alive)) else None
        if record and rec:
            per = []
            for i in range(K):
                if not alive[i]: per.append(None); continue
                e = _match_entity(ents, regs_now[i])
                per.append(dict(M=mat[i], P=phen(Sturn, e) if e is not None else None,
                                mem=mem_stats(Sturn, regs_now[i])))
            up_al = Sturn.uptake[Sturn.rho > 1e-4]
            traj.append(dict(t=t, cov=float(cov), alive=[bool(a) for a in alive],
                             up_ref=float(up_al.mean()) if up_al.size else 0.0,
                             world_mean_up=float(Sturn.uptake.mean()), per=per))
        # ---- deep-snapshot rule (first pre-declared feasible instant) ----
        if deep is None and all(alive) and cov < COVER_CAP and not first_censor and mat is not None \
           and all(mat[i] is not None and np.isfinite(mat[i]["M"]) and mat[i]["M"] <= M_TARGET for i in range(K)):
            ents_here = ents
            matched = [_match_entity(ents_here, regs_now[i]) for i in range(K)]
            if all(e is not None for e in matched):
                deep = dict(step=t, S=Sturn.copy(), regs=[regs_now[i].copy() for i in range(K)],
                            cents=[[float(x) for x in e.centroid] for e in matched],
                            M=[float(mat[i]["M"]) for i in range(K)])
                break
        # ---- early exit: any censor makes the deep snapshot unreachable (all-3-valid gate) ----
        if first_censor and deep is None:
            diag = mt.read_material(Sturn, base, regs_now)
            traj.append(dict(t=t, cov=float(cov), alive=[bool(a) for a in alive], censor_exit=True,
                             up_ref=float('nan'), world_mean_up=float('nan'),
                             per=[(dict(M=diag[i]) if alive[i] else None) for i in range(K)]))
            active = []
            for tid, raw_status in ev.items():
                rec_ev, state_ev = te.start_event(
                    raw_status, int(tid), t, parent_masks, emasks, Sturn.rho
                )
                active.append((rec_ev, state_ev))
            for dt_evidence in range(1, te.CONFIRM_FRAMES + 1):
                Sturn = eng.step(Sturn)
                comps_follow = [cc.mask(e) for e in detect(Sturn, DET)]
                for rec_ev, state_ev in active:
                    te.append_followup(
                        rec_ev, state_ev, t + dt_evidence, comps_follow, Sturn.rho
                    )
            event_evidence.extend(te.finalize(rec_ev) for rec_ev, _ in active)
            break
    return dict(base=base, traj=traj, first_censor={str(k): v for k, v in first_censor.items()},
                event_evidence=event_evidence, deep=deep)


def _valid(beh_dict):
    b = beh_dict
    return bool(b["intact"]["branch_valid"] and b["sham"]["branch_valid"] and all(b["erase"][j]["branch_valid"] for j in range(K)))


def _own(beh):
    A = beh["intact"]; er = beh["erase"]
    return [float(A["tracked"][i] - er[i]["tracked"][i]) for i in range(K)]


def run_seed(seed):
    eng = cc.build(cc.MEM_INTACT); eng_abl = cc.build(cc.MEM_ABLATE); eng_nw = cc.build(MEM_NOWRITE)
    st = cc.seed_world(seed)
    for _ in range(cc.WARM): st = eng.step(st)
    ents0 = detect(st, DET); n_det = len(ents0)
    T = cc.pick(sorted(ents0, key=lambda e: -e.size))
    if len(T) < K:
        return dict(seed=seed, eligible=False, reason="fewer_than_K_eligible", n_detected=n_det)
    rng = np.random.default_rng(seed)
    cents = [e.centroid for e in T]; sigs = [max(3.0, e.rg * 0.8) for e in T]; sizes = [e.size for e in T]
    pts = [cc.patch(*cents[i], sigs[i]) for i in range(K)]
    hist = [(float(rng.uniform(cc.AMP_LO, cc.AMP_HI)), float(rng.uniform(cc.AMP_LO, cc.AMP_HI))) for _ in range(K)]
    dose = [a + b for a, b in hist]; order = [b - a for a, b in hist]

    # ---- STORAGE block (verbatim structure from the sealed confirm-02 pipeline) ----
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
    entsB = sorted(detect(sB, DET), key=lambda e: -e.size); regs = [cc.mask(cc.nearest(c, entsB)) for c in cents]
    mpB = (sB.Mf[0] + sB.Mf[1]) / np.maximum(sB.rho, 1e-9)
    Cm = np.zeros((K, K))
    for i in range(K):
        sA = st.copy()
        for ph in (0, 1):
            a = hist[i][ph]
            for _ in range(cc.PHASE): sA.N = sA.N + a * pts[i]; sA = eng.step(sA)
        for _ in range(cc.SETTLE): sA = eng.step(sA)
        mpA = (sA.Mf[0] + sA.Mf[1]) / np.maximum(sA.rho, 1e-9); dM = np.abs(mpA - mpB)
        for j in range(K): Cm[i, j] = float(dM[regs[j]].mean())

    # ---- REST snapshot + frozen causal assay ----
    S0 = sS.copy(); reg0, _ = cc.region_masks(S0, cents); empty = cc.empty_patch_mask(S0, cents)
    rest = dict(intact=nm.measure(S0, cents, eng, None), sham=nm.measure(S0, cents, eng, empty),
                ablate=nm.measure(S0, cents, eng_abl, None),
                erase=[nm.measure(S0, cents, eng, reg0[j]) for j in range(K)],
                erase_ablate=[nm.measure(S0, cents, eng_abl, reg0[j]) for j in range(K)])
    rest_g0 = _valid(rest)

    result = dict(seed=seed, eligible=True, n_detected=n_det,
                  cents=[[float(x) for x in c] for c in cents], sizes=sizes, hist=hist,
                  dose=dose, order=order, feat=feat, Cm=Cm.tolist(),
                  rest_g0=bool(rest_g0), rest_own=_own(rest), rest_beh=rest)

    # ---- TURNOVER (writing active, neutral) + passive-decay null ----
    tov = turnover(S0, cents, reg0, eng, record=True)
    result["turnover"] = dict(first_censor=tov["first_censor"], traj=tov["traj"],
                              event_evidence=tov["event_evidence"], n_rec=len(tov["traj"]))
    if tov["deep"] is None:
        # feasibility diagnosis
        last = tov["traj"][-1] if tov["traj"] else None
        reason = "cap_reached_M_above_target"
        if tov["first_censor"]:
            reason = "tracker_event:" + ";".join(f"{k}:{v[1]}@{v[0]}" for k, v in tov["first_censor"].items())
        result["feasible"] = False; result["deep_reason"] = reason
        result["last_M"] = ([r["M"]["M"] if (r and r.get("M")) else None for r in last["per"]] if last else None)
        return result

    result["feasible"] = True
    dstep = tov["deep"]["step"]; Sdeep = tov["deep"]["S"]; regs_deep = tov["deep"]["regs"]; cents_deep = tov["deep"]["cents"]
    empty_d = cc.empty_patch_mask(Sdeep, cents_deep)
    deep_beh = dict(intact=nm.measure(Sdeep, cents_deep, eng, None), sham=nm.measure(Sdeep, cents_deep, eng, empty_d),
                    ablate=nm.measure(Sdeep, cents_deep, eng_abl, None),
                    erase=[nm.measure(Sdeep, cents_deep, eng, regs_deep[j]) for j in range(K)],
                    erase_ablate=[nm.measure(Sdeep, cents_deep, eng_abl, regs_deep[j]) for j in range(K)])
    entsD = sorted(detect(Sdeep, DET), key=lambda e: -e.size)
    feat_deep = [cc.feats(Sdeep, cc.nearest(c, entsD)) for c in cents_deep]
    result["deep"] = dict(step=dstep, M=tov["deep"]["M"], g0_valid=_valid(deep_beh),
                          own=_own(deep_beh), feat=feat_deep, cents=cents_deep, beh=deep_beh)

    # ---- passive-decay null: no-write world to matched depth; deep memory feature separation ----
    tov_nw = turnover(S0, cents, reg0, eng_nw, record=False, cap=dstep)
    if tov_nw["deep"] is not None:
        Snw = tov_nw["deep"]["S"]; regs_nw = tov_nw["deep"]["regs"]; cents_nw = tov_nw["deep"]["cents"]
    else:
        # run the null exactly dstep steps and read whatever survives (diagnostic)
        Snw, base_nw = mt.seed_tracers(S0, reg0)
        tr = bt.BijectiveTracker(theta=THETA); tr.seed([m.copy() for m in reg0], 0)
        for t in range(1, dstep + 1):
            Snw = eng_nw.step(Snw); emasks = [cc.mask(e) for e in detect(Snw, DET)]; tr.update(emasks, t)
        regs_nw = [tr.tracks[i].mask if tr.tracks[i].status == bt.ALIVE else None for i in range(K)]
        cents_nw = cents_deep
    feat_nw = []
    for i in range(K):
        if regs_nw[i] is None: feat_nw.append(None)
        else: feat_nw.append(cc.feats(Snw, cc.nearest(cents_nw[i], sorted(detect(Snw, DET), key=lambda e: -e.size))))
    result["null_nowrite"] = dict(deep_reached=bool(tov_nw["deep"] is not None), feat=feat_nw,
                                  M=(tov_nw["deep"]["M"] if tov_nw["deep"] else None))
    return result


def main():
    out = sys.argv[1]; seeds = [int(x) for x in sys.argv[2:]]
    ALLOWED = set(range(50001, 50011))
    bad = [s for s in seeds if s not in ALLOWED]
    if bad:
        raise SystemExit(f"REFUSED: seeds {bad} are not DEV seeds 50001-50010. This runner runs NO confirmatory seed.")
    data = json.load(open(out)) if os.path.exists(out) else []
    done = {d["seed"] for d in data}
    for s in seeds:
        if s in done: print("skip", s); continue
        r = run_seed(s); data.append(r); json.dump(data, open(out, "w"))
        if not r["eligible"]:
            print(f"seed {s}: INELIGIBLE ({r.get('reason')})")
        elif not r.get("feasible"):
            print(f"seed {s}: eligible rest_g0={r['rest_g0']} rest_own={[round(x,3) for x in r['rest_own']]} "
                  f"-> FEASIBILITY INVALID ({r.get('deep_reason')}) last_M={r.get('last_M')}")
        else:
            d = r["deep"]
            print(f"seed {s}: FEASIBLE deep@{d['step']} M={[round(x,3) for x in d['M']]} g0={d['g0_valid']} "
                  f"rest_own={[round(x,3) for x in r['rest_own']]} deep_own={[round(x,3) for x in d['own']]}")


if __name__ == "__main__":
    main()
