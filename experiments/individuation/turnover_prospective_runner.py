"""LCI-CAUSAL-TURNOVER-PRESEAL-REPAIR-03A — FROZEN prospective runner (54001-54096). ⚠ NOT AUTHORIZED TO RUN.

Resolves red-team points 1, 4, 6:
  (1) accepts ONLY the sealed prospective family 54001-54096 (DEV runner stays locked to 50xxx). A hard
      AUTHORIZATION GUARD blocks execution until Tommy sets TP03A_PROSPECTIVE_AUTHORIZED to the sealed token.
  (4) primary manipulation check = lambda_plus-ONLY ablation (lambda_minus kept); the full both-zero ablation is
      recorded separately, never conflated.
  (6) PERSISTS, per feasible world at the deep snapshot: 11-D target memory features (L), the L/P/E/G scope
      features, centroids (for the GEOMETRIC neighbour), M_i and dose — so the frozen ownership/access analysis
      (turnover_ownership_analyze.py) needs no re-run and CAN test environment/global ownership.

Reuses the validated frozen components (storage block, turnover(), bijective tracker, material tracer,
nm.measure). --selfcheck 50002 validates the schema on ONE DEV seed WITHOUT touching any 54xxx seed.
"""
import sys, os, json, importlib.util
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
def _load(n, f):
    s = importlib.util.spec_from_file_location(n, os.path.join(HERE, f)); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
cc = _load("cc", "causal_confirm.py"); nm = _load("nm", "nonmerging_confirm.py")
run = _load("run", "turnover_dev_runner.py"); diag = _load("diag", "turnover_dev_diagnostics.py")
from edlab.substrates.scaffold.observables import detect
from edlab.experiments.sc_mcm import config as C
from edlab.experiments.sc_mcm.engine import MCParams
K = cc.K; N = cc.N; DET = C.DET
C1c = dict(eta_w=0.015, eta_d1=0.35, eta_d2=0.006, k_exp=1.0)

SEED_ALLOWLIST = range(54001, 54097)          # frozen prospective family (cap 96)
RESERVE = range(54097, 54121)                  # endpoint-blinded reserve (activate only on geometric-eligibility trigger)
AUTH_TOKEN_ENV = "TP03A_PROSPECTIVE_AUTHORIZED"
SEALED_TOKEN = "TOMMY-GO::design/lci-causal-turnover-preseal-repair-03a"  # must match after human authorization

# lambda_plus-ONLY ablation (red-team point 4): lam_minus KEPT at 0.15
MEM_ABLATE_PLUS = MCParams(lam_plus=0.0, lam_minus=0.15, **C1c)


def _storage_to_S0(seed, eng, rng):
    st = cc.seed_world(seed)
    for _ in range(cc.WARM): st = eng.step(st)
    T = cc.pick(sorted(detect(st, DET), key=lambda e: -e.size))
    if len(T) < K: return None
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
    return dict(S0=sS.copy(), cents=cents, dose=dose, hist=hist)


def run_seed(seed):
    eng = cc.build(cc.MEM_INTACT); eng_abl_full = cc.build(cc.MEM_ABLATE); eng_abl_plus = cc.build(MEM_ABLATE_PLUS)
    rng = np.random.default_rng(seed)
    base = _storage_to_S0(seed, eng, rng)
    if base is None: return dict(seed=seed, eligible=False, reason="fewer_than_K_eligible")
    S0 = base["S0"]; cents = base["cents"]; dose = base["dose"]
    reg0, _ = cc.region_masks(S0, cents); empty = cc.empty_patch_mask(S0, cents)
    def battery(S, cts, regs, e_full, e_plus, eng_):
        return dict(intact=nm.measure(S, cts, eng_, None), sham=nm.measure(S, cts, eng_, empty if S is S0 else cc.empty_patch_mask(S, cts)),
                    ablate_full=nm.measure(S, cts, e_full, None), ablate_plus=nm.measure(S, cts, e_plus, None),
                    erase=[nm.measure(S, cts, eng_, regs[j]) for j in range(K)],
                    erase_ablate_plus=[nm.measure(S, cts, e_plus, regs[j]) for j in range(K)])
    rest = battery(S0, cents, reg0, eng_abl_full, eng_abl_plus, eng)
    tov = run.turnover(S0, cents, reg0, eng, record=True)
    res = dict(seed=seed, eligible=True, dose=dose, cents=[[float(x) for x in c] for c in cents],
               rest_beh=rest, feasible=bool(tov["deep"] is not None))
    if tov["deep"] is None:
        res["deep_reason"] = ("tracker:" + ";".join(f"{k}:{v[1]}@{v[0]}" for k, v in tov["first_censor"].items())) if tov["first_censor"] else "cap_reached"
        return res
    d = tov["deep"]; Sd = d["S"]; regs_d = d["regs"]; cents_d = d["cents"]
    res["deep"] = dict(step=d["step"], M=d["M"],
                       beh=battery(Sd, cents_d, regs_d, eng_abl_full, eng_abl_plus, eng),
                       feat11=[cc.feats(Sd, cc.nearest(c, sorted(detect(Sd, DET), key=lambda e: -e.size))) for c in cents_d],
                       scopes=diag.scope_feats(Sd, cents_d, regs_d), cents=cents_d)
    return res


def _authorized():
    return os.environ.get(AUTH_TOKEN_ENV, "") == SEALED_TOKEN


def main():
    args = sys.argv[1:]
    if args[:1] == ["--selfcheck"]:
        s = int(args[1]) if len(args) > 1 else 50002
        if s not in (50002, 50004, 50005, 50007):
            raise SystemExit("selfcheck runs only a DEV feasible seed (50002/50004/50005/50007); NOT prospective.")
        r = run_seed(s)
        ok = r.get("feasible") and "scopes" in r["deep"] and "ablate_plus" in r["deep"]["beh"]
        print(f"[selfcheck seed {s}] feasible={r.get('feasible')} persists_scopes={('scopes' in r.get('deep',{}))} "
              f"lam+_ablation={'ablate_plus' in r.get('deep',{}).get('beh',{})} -> {'SCHEMA OK' if ok else 'FAIL'}")
        return
    out = args[0]; seeds = [int(x) for x in args[1:]]
    bad = [s for s in seeds if s not in SEED_ALLOWLIST and s not in RESERVE]
    if bad:
        raise SystemExit(f"REFUSED: {bad} not in sealed family 54001-54096 (+reserve 54097-54120).")
    if not _authorized():
        raise SystemExit("⛔ NOT AUTHORIZED FOR PROSPECTIVE RUN. This runner is frozen pending Tommy's GO. "
                         f"Set {AUTH_TOKEN_ENV} to the sealed token only AFTER explicit authorization + fresh-agent audit.")
    data = json.load(open(out)) if os.path.exists(out) else []
    done = {d["seed"] for d in data}
    for s in seeds:
        if s in done: print("skip", s); continue
        r = run_seed(s); data.append(r); json.dump(data, open(out, "w"))
        print(f"seed {s}: eligible={r.get('eligible')} feasible={r.get('feasible')}")


if __name__ == "__main__":
    main()
