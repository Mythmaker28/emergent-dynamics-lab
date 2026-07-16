"""LCI-CAUSAL-TURNOVER-PRESEAL-REPAIR-03E — synthetic/static tests for the six material blockers.

Runs with NO engine, NO 54xxx seed, NO real authorization. Exit 0 iff all pass.
    PYTHONPATH=. python experiments/individuation/test_turnover_preseal_03e.py
"""
from __future__ import annotations
import importlib.util, os, sys, json, tempfile, pathlib
import numpy as np

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)))
def _load(n, f):
    s = importlib.util.spec_from_file_location(n, os.path.join(HERE, f)); m = importlib.util.module_from_spec(s)
    sys.modules[n] = m; s.loader.exec_module(m); return m

sf = _load("turnover_scope_features_03e", "turnover_scope_features_03e.py")
stat = _load("turnover_statistics_03e", "turnover_statistics_03e.py")
led = _load("turnover_execution_ledger", "turnover_execution_ledger.py")
pw = _load("turnover_power_regen", "turnover_power_regen.py")

FAIL = []
def check(name, ok, extra=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name} {extra}")
    if not ok: FAIL.append(name)


def test_B3_low_dim_scopes():
    class S: pass
    rng = np.random.default_rng(0); n = 64
    st = S(); st.rho = np.abs(rng.normal(0.5, 0.2, (n, n))); st.U = rng.random((n, n)); st.V = rng.random((n, n))
    st.c = rng.random((n, n)); st.N = rng.random((n, n)); st.uptake = rng.random((n, n)); st.Mf = rng.normal(0, .3, (2, n, n))
    regs = [np.zeros((n, n), bool) for _ in range(3)]
    for r, (cy, cx) in zip(regs, [(16, 16), (16, 48), (48, 32)]): r[cy - 3:cy + 3, cx - 3:cx + 3] = True
    b = sf.extract_scope_bundle_03e(st, regs, [(16, 16), (16, 48), (48, 32)])
    dims = b["dims"]
    check("B3 E/Gm/Gf all <= 24 predictors", all(dims[s] <= 24 for s in ("E", "Gm", "Gf")), str(dims))
    check("B3 gated scopes exclude Gf (nests L)", "Gf" not in b["gated_scopes"] and "Gm" in b["gated_scopes"])
    check("B3 no label/cohort fields in scope bundle", (not b["label_fields_present"]) and (not b["diagnostic_cohorts_present"]))


def _syn(local, rng):
    NW, K = 18, 3
    worlds = np.repeat(np.arange(NW), K); own = rng.uniform(0.01, 0.07, NW * K)
    def col(v): return np.column_stack([v + rng.normal(0, .005, len(own)), *[rng.normal(0, 1, len(own)) for _ in range(10)]])
    M = {"L": col(own if local else rng.normal(0, .02, len(own))),
         "N": col(rng.uniform(0.01, 0.07, len(own))),
         "E": rng.normal(0, 1, (len(own), 24)), "Gm": rng.normal(0, 1, (len(own), 18)),
         "B": rng.normal(0, 1, (len(own), 8)), "Gf": rng.normal(0, 1, (len(own), 18))}
    M["P"] = np.column_stack([M["L"], M["N"], rng.normal(0, 1, (len(own), 11))])
    return M, own, worlds


def test_B2_ownership_gates():
    rng = np.random.default_rng(1)
    M, own, w = _syn(True, rng); o = stat.evaluate_ownership_03e(M, own, w)
    check("B2 local: G_OWN_PERM pass", o["G_OWN_PERM"]["pass"], f"p={o['G_OWN_PERM']['perm_null_p']:.4f}")
    check("B2 local: G_LOCAL_EXCLUSION pass", o["G_LOCAL_EXCLUSION"]["pass"])
    M0, own0, w0 = _syn(False, rng); o0 = stat.evaluate_ownership_03e(M0, own0, w0)
    check("B2 null: gates fail", (not o0["G_OWN_PERM"]["pass"]) and (not o0["G_LOCAL_EXCLUSION"]["pass"]))


def test_B2_duplicate_world():
    rng = np.random.default_rng(2); M, own, w = _syn(True, rng)
    dup = {k: np.vstack([M[k], M[k][w == 0]]) for k in M}
    w3 = np.concatenate([w, [999, 999, 999]]); own3 = np.concatenate([own, own[w == 0]])
    raised = False
    try: stat.evaluate_ownership_03e(dup, own3, w3)
    except AssertionError: raised = True
    check("B2 duplicate-world content rejected", raised)


def _bat(own_v, sham_v, neigh_v, ap_v, fixed_v):
    K = 3; intact = {"tracked": [1.0] * K, "fixed": [1.0] * K}
    erase = [{"tracked": [1.0 - (own_v if j == i else neigh_v) for i in range(K)],
              "fixed": [1.0 - (fixed_v if j == i else 0) for i in range(K)]} for j in range(K)]
    return {"intact": intact, "sham": {"tracked": [1.0 - sham_v] * K}, "erase": erase,
            "ablate_plus": {"tracked": [0.3] * K},
            "erase_ablate_plus": [{"tracked": [0.3 - (ap_v if j == i else 0) for i in range(K)]} for j in range(K)]}


def test_B2_causal_gate():
    rng = np.random.default_rng(3)
    gp = stat.causal_expression_gate([_bat(0.2 + rng.normal(0, .01), 0, 0, 0.02, 0.2) for _ in range(18)], 18)
    check("B2 causal pass-case", gp["pass"])
    gf = stat.causal_expression_gate([_bat(0.004 + rng.normal(0, .01), 0, 0, 0.02, 0.0) for _ in range(18)], 18)
    check("B2 causal fail-case (own~0)", not gf["pass"])


def test_B1_ledger():
    d = pathlib.Path(tempfile.mkdtemp()) / "run"
    start = dict(authorization_id="A1", final_seal_sha256="a" * 64, execution_manifest_git_blob="b" * 64,
                 code_hashes={"x": "1"}, environment_hash="c" * 64, seed_family={"p": "54001-54050"})
    check("B1 fresh start", led.start_or_resume(d, start)["mode"] == "fresh")
    r = d / "s.json"; r.write_text('{"seed":54001}'); led.record_seed(d, 54001, r, {"valid": True})
    check("B1 chain verifies", led.verify_chain(d)["verified"])
    check("B1 resume same binding", led.start_or_resume(d, start)["mode"] == "resume")
    bad = dict(start); bad["authorization_id"] = "OTHER"
    try: led.start_or_resume(d, bad); check("B1 reject different auth", False)
    except led.LedgerError: check("B1 reject different auth", True)
    try: led.record_seed(d, 54001, r, {"valid": True}); check("B1 reject rerun completed", False)
    except led.LedgerError: check("B1 reject rerun completed", True)
    lp = d / led.LEDGER_NAME; lines = lp.read_text().splitlines()
    o = json.loads(lines[1]); o["feasibility_projection"] = {"valid": False}
    lines[1] = json.dumps(o, sort_keys=True); lp.write_text("\n".join(lines) + "\n")
    try: led.verify_chain(d); check("B1 tamper detected", False)
    except led.LedgerError: check("B1 tamper detected", True)


def test_B1_authorization():
    ok = dict(authorized=True, one_execution_only=True, final_seal_sha256="a" * 64,
              execution_manifest_git_blob="b" * 64, approval_phrase="P", authorization_id="X",
              approved_by="Y", approved_at_utc="Z")
    led.validate_authorization(ok, "a" * 64, "b" * 64, "P")
    ok2 = dict(ok); ok2["final_seal_sha256"] = "WRONG"
    try: led.validate_authorization(ok2, "a" * 64, "b" * 64, "P"); check("B1 reject unbound final-seal", False)
    except led.LedgerError: check("B1 reject unbound final-seal", True)


def test_B5_power():
    p96 = pw.prob_at_least(18, 96); p50 = pw.prob_at_least(18, 50)
    check("B5 P>=18@96 == 0.924519", abs(p96 - 0.924519023326) < 1e-6, f"{p96:.9f}")
    check("B5 P>=18@50 == 0.570904", abs(p50 - 0.570903754176) < 1e-6, f"{p50:.9f}")


if __name__ == "__main__":
    print("=== LCI-CAUSAL-TURNOVER-PRESEAL-REPAIR-03E tests ===")
    for t in (test_B3_low_dim_scopes, test_B2_ownership_gates, test_B2_duplicate_world,
              test_B2_causal_gate, test_B1_ledger, test_B1_authorization, test_B5_power):
        t()
    print(f"\n{'ALL PASS' if not FAIL else 'FAILURES: ' + ', '.join(FAIL)}")
    raise SystemExit(1 if FAIL else 0)
