"""AXMAT00 — offline methods review of the inherited A_X materiality rule.

Imports: json, os, sys, hashlib, statistics, fractions ONLY.
No simulator, no production analysis function, no numpy, no engine path.
Every scientific input passes through Validator.load(); active-response and
full-field objects are refused by exact basename and by path fragment.
"""
import json, os, sys, hashlib
from fractions import Fraction as F

BASE = "/mnt/user-data/uploads/ising v3/FCDDH01R"

DENY_BASENAMES = {
    "FCDDH01R_DISCOVERY_MATERIALITY_AND_LEVERAGE_REPORT.json",
    "FCDDH01R_DISCOVERY_LOAO_AXIS_ARBITRATION.json",
    "FCDDH01R_DISCOVERY_INTERACTION_AND_ORBIT_TABLE.json",
    "FCDDH01R_DISCOVERY_CONTRASTS.json",
    "FCDDH01R_DISCOVERY_ALL_ROWS_AND_CONTRASTS.json",
    "FCDDH01R_DISCOVERY_GATE_LADDER.json",
    "FCDDH01R_DISCOVERY_COOPTIMAL_GAUGE_REPORT.json",
    "FCDDH01R_DISCOVERY_PRODUCTION_REFERENCE_RECOMPUTATION.json",
    "FCDDH01R_DISCOVERY_ACTIVE_RAW_LOCK.json",
    "FCDDH01R_DISCOVERY_ACTIVE_RAW_MANIFEST.json",
    "DISCOVERY_ACTIVE_RAW_MANIFEST.json",
}
DENY_FRAGMENTS = ("ACTIVE_RAW_ARCHIVE", "DISCOVERY_PANEL/", "FULL_FIELD", "_ACTIVE_")
DENY_SUFFIXES = (".npz", ".npy")

ALLOW_BASENAMES = {
    "FCDDH01R_DISCOVERY_THRESHOLD_LOCK.json",     # pre-active, committed at fc1b41f8
    "FCDDH01R_DISCOVERY_TWIN_SHAM_ORACLE.json",   # sham-derived
    "FCDDH01R_DISCOVERY_PANEL_LOCK.json",         # pre-active design lock
    "EXACT_INTERACTION_COEFFICIENT_MAP.json",
    "EXACT_TAU_PROPAGATION_CERTIFICATE.json",
    "EXACT_FACTOR_AND_ANCESTRY_GRAPH_SPEC.json",
    "REAL_PHASE_COMMAND_PAYLOAD_IDENTITY_REPORT.json",
    "CANONICAL_FIELD_SCHEMA.txt",
    "FROZEN_ESTIMAND_AND_UNIT_LEDGER.md",
    "P2_GAUGE_AND_COOPTIMALITY_SPEC.md",
    "FCDDH01R_MASTER_FREEZE.md",
    "PARENT_BASIS_NUMERICAL_CERTIFICATE.json",
    "FCRA00_FACT_AND_CLAIM_BINDER.json",
    "PREANALYSIS_ORACLE_REPORT.json",
    "FCDDH01R_SCIENTIFIC_OBJECT_IDENTITY_MANIFEST.json",
    "RANDOMIZATION_LICENSE.json",
    "DISCOVERY_HOLDOUT_ROLE_QUEUES.json",
    "FCDDH01R_NAMESPACE_AND_ROLE_QUEUES.json",
}

class ActiveDataDependencyDetected(Exception):
    pass

class Validator:
    def __init__(self):
        self.accepted = []
        self.refused = []
    def check(self, path):
        b = os.path.basename(path)
        if b in DENY_BASENAMES: return False, f"DENY_BASENAME:{b}"
        if any(f in path for f in DENY_FRAGMENTS): return False, "DENY_PATH_FRAGMENT"
        if path.endswith(DENY_SUFFIXES): return False, "DENY_SUFFIX_NUMERIC_ARRAY"
        if b not in ALLOW_BASENAMES: return False, f"NOT_ON_ALLOWLIST:{b}"
        return True, "ALLOWED"
    def load(self, path, mode="json"):
        ok, why = self.check(path)
        if not ok:
            self.refused.append({"path": path, "reason": why})
            raise ActiveDataDependencyDetected(f"REFUSED {path}: {why}")
        raw = open(path, "rb").read()
        self.accepted.append({"path": path, "basename": os.path.basename(path),
                              "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
        return json.loads(raw.decode()) if mode == "json" else raw.decode()
    def try_load(self, path):
        try:
            self.load(path); return "LOADED"
        except ActiveDataDependencyDetected as e:
            return f"REFUSED ({str(e).split(': ')[-1]})"

def iv(pair):  return (F(pair[0]), F(pair[1]))
def mid(pair): return (pair[0] + pair[1]) / 2

def main():
    V = Validator()
    R = {}

    # ---- negative fixtures: active-response and full-field paths must be refused
    R["negative_fixtures"] = {p: V.try_load(os.path.join(BASE, p)) for p in [
        "FCDDH01R_DISCOVERY_MATERIALITY_AND_LEVERAGE_REPORT.json",
        "FCDDH01R_DISCOVERY_LOAO_AXIS_ARBITRATION.json",
        "FCDDH01R_DISCOVERY_INTERACTION_AND_ORBIT_TABLE.json",
        "FCDDH01R_DISCOVERY_GATE_LADDER.json",
        "_work/DISCOVERY_ACTIVE_RAW_ARCHIVE/CARRIER_1_73000_NEAR_a0.npz",
        "_work/DISCOVERY_PANEL/d_73000_NEAR_a0.npz",
    ]}
    R["negative_fixtures_all_refused"] = all(v.startswith("REFUSED")
                                             for v in R["negative_fixtures"].values())

    # ---- allowed inputs
    thr  = V.load(f"{BASE}/FCDDH01R_DISCOVERY_THRESHOLD_LOCK.json")
    cmap = V.load(f"{BASE}/_work/EXACT_INTERACTION_COEFFICIENT_MAP.json")
    cert = V.load(f"{BASE}/_work/EXACT_TAU_PROPAGATION_CERTIFICATE.json")
    payl = V.load(f"{BASE}/REAL_PHASE_COMMAND_PAYLOAD_IDENTITY_REPORT.json")
    twin = V.load(f"{BASE}/FCDDH01R_DISCOVERY_TWIN_SHAM_ORACLE.json")
    graph= V.load(f"{BASE}/_work/EXACT_FACTOR_AND_ANCESTRY_GRAPH_SPEC.json")

    R["threshold_lock_top_keys"] = list(thr.keys())
    R["threshold_record_keys"]   = list(thr["thresholds"][0].keys())
    R["coefficient_map_keys"]    = list(cmap.keys())
    R["n_thresholds"] = len(thr["thresholds"])
    R["symbolic_to_numeric_map"] = thr.get("symbolic_to_numeric_map")
    R["code_sha256_in_lock"]     = thr.get("code_sha256")
    R["weights_from_payload"]    = payl["invariants_required_identical"]["weights"]
    R["H_GRID"]                  = payl["invariants_required_identical"]["H_GRID"]
    R["dt"]                      = payl["invariants_required_identical"]["dt"]

    # ---- sham series shape (sham evidence only)
    ser = thr["sham_series_and_hashes"]
    k0 = sorted(ser.keys())[0]
    R["sham_series_example_keys"] = list(ser[k0].keys())
    R["sham_series_len_XA"] = len(ser[k0]["XA"])
    R["n_sham_series"] = len(ser)

    R["accepted_inputs"] = V.accepted
    R["refused_inputs"]  = V.refused
    json.dump(R, open("/home/claude/axmat00/out/_stage1.json", "w"), indent=1, default=str)
    for k, v in R.items():
        if k in ("accepted_inputs", "refused_inputs"): continue
        print(k, "=", json.dumps(v, default=str)[:600])
    print("accepted_inputs:", len(V.accepted), " refused_inputs:", len(V.refused))

if __name__ == "__main__":
    main()
