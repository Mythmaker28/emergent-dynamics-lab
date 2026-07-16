"""LCI-CAUSAL-TURNOVER-PRESEAL-REPAIR-03A — DEV mechanistic diagnostics (NO prospective, NO 54xxx).

Per feasible DEV seed, at the deep snapshot (M_i<=0.25):
  D  algebraic direct-coupling prediction: predicted own-effect fraction = <lam+*m+/(1+lam+*m+)> in the target
     region vs observed own/intact. Tells whether the interventional effect is JUST the algebraic multiplier.
  B  eta_w=0 (post-history no new writing): deep m+ amplitude -> passive carry-over/decay (NOT reconstruction).
  C  up_ref=0 (global reference ablated): deep m+ amplitude (+ deep causal assay on first seeds) -> global channel.
  E  copy_disabled (Mf+=g*m ablated): deep m+ amplitude + M_i -> is passive copy NECESSARY to sustain memory?
  L/P/E/G scope features for own-dose decode (distributed-access hypothesis; own-dose decoded by analyze).
Resumable; writes after each seed. DEV seeds only.
"""
import sys, os, json, importlib.util
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
def _load(n, f):
    s = importlib.util.spec_from_file_location(n, os.path.join(HERE, f)); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
cc = _load("cc", "causal_confirm.py"); nm = _load("nm", "nonmerging_confirm.py")
bt = _load("bt", "bijective_tracker.py"); mt = _load("mt", "material_tracer.py")
run = _load("run", "turnover_dev_runner.py"); de = _load("de", "turnover_diag_engine.py")
from edlab.substrates.scaffold.observables import detect
from edlab.experiments.sc_mcm import config as C
from edlab.experiments.sc_mcm.engine import MCParams
K = cc.K; N = cc.N; N0 = cc.N0; DET = C.DET; GRID = N * N
LAMP = 0.25
C1c = dict(eta_w=0.015, eta_d1=0.35, eta_d2=0.006, k_exp=1.0)
MEM = MCParams(lam_plus=0.25, lam_minus=0.15, **C1c)
MEM_ETAW0 = MCParams(lam_plus=0.25, lam_minus=0.15, eta_w=0.0, eta_d1=0.35, eta_d2=0.006, k_exp=1.0)


def to_S0(seed):
    eng = cc.build(cc.MEM_INTACT)
    st = cc.seed_world(seed)
    for _ in range(cc.WARM): st = eng.step(st)
    T = cc.pick(sorted(detect(st, DET), key=lambda e: -e.size))
    if len(T) < K: return None
    rng = np.random.default_rng(seed)
    cents = [e.centroid for e in T]; sigs = [max(3.0, e.rg * 0.8) for e in T]
    pts = [cc.patch(*cents[i], sigs[i]) for i in range(K)]
    hist = [(float(rng.uniform(cc.AMP_LO, cc.AMP_HI)), float(rng.uniform(cc.AMP_LO, cc.AMP_HI))) for _ in range(K)]
    dose = [a + b for a, b in hist]
    sS = st.copy()
    for ph in (0, 1):
        amps = [hist[i][ph] for i in range(K)]
        for _ in range(cc.PHASE):
            for i in range(K): sS.N = sS.N + amps[i] * pts[i]
            sS = eng.step(sS)
    for _ in range(cc.SETTLE): sS = eng.step(sS)
    return dict(eng=eng, S0=sS.copy(), cents=cents, reg0=cc.region_masks(sS.copy(), cents)[0], dose=dose)


def run_to(engine, S0, reg0, nsteps):
    """Step `engine` from S0 (with per-target tracers + bijective tracker) exactly nsteps. Return end state,
    per-track alive/regions, M_i, and per-region m+ amplitude."""
    S, base = mt.seed_tracers(S0, reg0)
    tr = bt.BijectiveTracker(theta=nm.THETA); tr.seed([m.copy() for m in reg0], 0)
    censor = {}
    for t in range(1, nsteps + 1):
        S = engine.step(S); emasks = [cc.mask(e) for e in detect(S, DET)]
        ev = tr.update(emasks, t)
        for tid, sv in ev.items(): censor.setdefault(int(tid), (t, sv))
    alive = [tr.tracks[i].status == bt.ALIVE for i in range(K)]
    regs = [tr.tracks[i].mask if alive[i] else None for i in range(K)]
    mat = mt.read_material(S, base, regs)
    mplus = []
    for i in range(K):
        if regs[i] is None: mplus.append(None); continue
        m = S.Mf[:, regs[i]] / np.maximum(S.rho[regs[i]], 1e-9)
        mplus.append(float(np.tanh(m[0] + m[1]).mean()))
    return dict(S=S, alive=alive, regs=regs, M=[(mat[i]["M"] if mat[i] else None) for i in range(K)],
                mplus=mplus, censor=censor)


def scope_feats(S, cents, regs):
    """L/P/E/G low-dim features for own-dose decode. regs = per-target masks at deep."""
    def mreg(mask):
        m = S.Mf[:, mask] / np.maximum(S.rho[mask], 1e-9)
        return float(np.tanh(m[0] + m[1]).mean()), float(m[0].mean()), float(m[1].mean())
    occ = S.rho > 0.30
    mfull = S.Mf / np.maximum(S.rho, 1e-9)[None]
    world_mplus = float(np.tanh(mfull[0] + mfull[1])[occ].mean()) if occ.any() else 0.0
    outside = occ.copy()
    for r in regs:
        if r is not None: outside &= ~r
    env_mplus = float(np.tanh(mfull[0] + mfull[1])[outside].mean()) if outside.any() else 0.0
    up_alive = S.uptake[S.rho > 1e-4]; up_ref = float(up_alive.mean()) if up_alive.size else 0.0
    L, P, E, G = [], [], [], []
    for i in range(K):
        if regs[i] is None:
            L.append(None); P.append(None); E.append(None); G.append(None); continue
        mp_i, m1_i, m2_i = mreg(regs[i])
        neigh = [mreg(regs[j])[0] for j in range(K) if j != i and regs[j] is not None]
        Nreg = float(S.N[regs[i]].mean()); creg = float(S.c[regs[i]].mean())
        L.append([mp_i, m1_i, m2_i])                                    # target memory only
        P.append([mp_i, m1_i, m2_i] + neigh + [0.0] * (2 - len(neigh)))  # target + neighbour m+
        E.append([Nreg, creg, up_ref, env_mplus])                        # environment, target memory NOT used
        G.append([world_mplus, up_ref, float(S.uptake.mean())])          # global/world summary
    return dict(L=L, P=P, E=E, G=G)


def algebraic_D(intact_eng, Sdeep, cents, regs_deep):
    """Predicted own fraction from direct coupling: <lam+*m+/(1+lam+*m+)> at probe start in the target region."""
    st = Sdeep.copy(); st.N = np.full_like(st.N, N0)
    for _ in range(nm.SETTLE_STD): st = intact_eng.step(st)
    out = []
    for i in range(K):
        if regs_deep[i] is None: out.append(None); continue
        m = st.Mf[:, regs_deep[i]] / np.maximum(st.rho[regs_deep[i]], 1e-9)
        mp = np.tanh(m[0] + m[1]); frac = LAMP * mp / (1.0 + LAMP * mp)
        out.append(float(frac.mean()))
    return out


def run_seed(seed, raw_by_seed, do_assay):
    base = to_S0(seed)
    if base is None: return dict(seed=seed, feasible=False, reason="ineligible")
    eng = base["eng"]; S0 = base["S0"]; cents = base["cents"]; reg0 = base["reg0"]; dose = base["dose"]
    rec = raw_by_seed.get(seed)
    if not (rec and rec.get("feasible")): return dict(seed=seed, feasible=False)
    dstep = rec["deep"]["step"]
    # intact to deep (reproduce deep snapshot state)
    intact = run_to(eng, S0, reg0, dstep)
    regs_deep = intact["regs"]
    # observed own fraction from committed raw
    beh = rec["deep"]["beh"]; A = beh["intact"]["tracked"]; er = beh["erase"]
    obs_own_frac = [float((A[i] - er[i]["tracked"][i]) / A[i]) if A[i] else None for i in range(K)]
    predD = algebraic_D(eng, intact["S"], cents, regs_deep)
    scopes = scope_feats(intact["S"], cents, regs_deep)
    # variants to matched depth
    etaw0 = run_to(cc.build(MEM_ETAW0), S0, reg0, dstep)
    upref0 = run_to(de.DiagEngine(C.SPEC, MEM, C.TRACER, up_ref_zero=True), S0, reg0, dstep)
    copydis = run_to(de.DiagEngine(C.SPEC, MEM, C.TRACER, copy_disabled=True), S0, reg0, dstep)
    res = dict(seed=seed, feasible=True, dstep=dstep, dose=dose,
               obs_own_frac=obs_own_frac, pred_own_frac_D=predD,
               mplus_intact=intact["mplus"], M_intact=intact["M"],
               mplus_etaw0=etaw0["mplus"], mplus_upref0=upref0["mplus"],
               mplus_copydis=copydis["mplus"], M_copydis=copydis["M"],
               copydis_alive=copydis["alive"], scopes=scopes)
    if do_assay:
        # up_ref=0 deep causal assay (confirm global channel does not carry the individuation)
        up_eng = de.DiagEngine(C.SPEC, MEM, C.TRACER, up_ref_zero=True)
        if all(upref0["alive"]):
            cents_u = [[float(x) for x in max(detect(upref0["S"], DET), key=lambda e:(cc.mask(e)&upref0["regs"][i]).sum()).centroid] for i in range(K)]
            regs_u = upref0["regs"]; empty_u = cc.empty_patch_mask(upref0["S"], cents_u)
            ub = dict(intact=nm.measure(upref0["S"], cents_u, up_eng, None),
                      sham=nm.measure(upref0["S"], cents_u, up_eng, empty_u),
                      erase=[nm.measure(upref0["S"], cents_u, up_eng, regs_u[j]) for j in range(K)])
            res["upref0_own"] = [float(ub["intact"]["tracked"][i] - ub["erase"][i]["tracked"][i]) for i in range(K)]
            res["upref0_neigh"] = [float(np.mean([ub["intact"]["tracked"][i] - ub["erase"][j]["tracked"][i] for j in range(K) if j != i])) for i in range(K)]
        else:
            res["upref0_own"] = None
    return res


def main():
    out = sys.argv[1]; seeds = [int(x) for x in sys.argv[2:]]
    if any(s not in range(50001, 50011) for s in seeds):
        raise SystemExit("REFUSED: DEV seeds 50001-50010 only.")
    raw = {r["seed"]: r for r in json.load(open(os.path.join(HERE, "turnover_dev_raw.json")))}
    data = json.load(open(out)) if os.path.exists(out) else []
    done = {d["seed"] for d in data}
    assay_seeds = {50002, 50004}   # up_ref=0 deep causal assay on 2 seeds (confirmatory; expensive)
    for s in seeds:
        if s in done: print("skip", s); continue
        r = run_seed(s, raw, do_assay=(s in assay_seeds)); data.append(r); json.dump(data, open(out, "w"))
        if r.get("feasible"):
            print(f"seed {s}: dstep={r['dstep']} obs_own_frac={[round(x,3) if x else None for x in r['obs_own_frac']]} "
                  f"predD={[round(x,3) if x else None for x in r['pred_own_frac_D']]}")
            print(f"   m+ intact={[round(x,3) if x else None for x in r['mplus_intact']]} etaw0={[round(x,3) if x else None for x in r['mplus_etaw0']]} "
                  f"upref0={[round(x,3) if x else None for x in r['mplus_upref0']]} copydis={[round(x,3) if x else None for x in r['mplus_copydis']]} copydis_alive={r['copydis_alive']}")
            if r.get("upref0_own"): print(f"   up_ref=0 deep own={[round(x,3) for x in r['upref0_own']]} neigh={[round(x,3) for x in r['upref0_neigh']]}")
        else:
            print(f"seed {s}: not feasible")


if __name__ == "__main__":
    main()
