"""OBTC01 §14 — the freeze, executed BEFORE any informative start."""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, "/home/claude/ORR01/code")
sys.path.insert(0, "/home/claude/OBTC01/code")

import gate_obtc as GT           # noqa: E402
import guard_obtc as GD          # noqa: E402
import protocol_obtc as PC       # noqa: E402
import source_operator as OP     # noqa: E402

CODE = "/home/claude/OBTC01/code"
OUT = "/home/claude/OBTC01/out"
CORE = ("organizer_bound_cloud_protocol.yaml", "gate_obtc.py", "protocol_obtc.py",
        "engine_obtc.py", "metrics_obtc.py", "nulls_obtc.py", "topology.py",
        "source_operator.py", "guard_obtc.py", "audit_obtc.py")
DOCS = ("_provenance_audit.json", "_audit.json", "_metric_dependence.json",
        "OBTC01_VOCABULARY_NOTE.md", "OBTC01_PREFREEZE_PLAN.md")
NX_GRID = (20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 250, 300)
ENV_DRAWS = 200
ENV_SEED = 20260814


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    spec = GT.load()
    t0 = time.time()
    env = {}
    for L in (spec["point"]["L"], spec["point"]["L_large"]):
        env[str(L)] = {str(k): v for k, v in
                       PC.n2_envelope(L, NX_GRID, ENV_DRAWS, ENV_SEED, PC.spec_for(L)).items()}
    print("N2 envelope built in %.0f s" % (time.time() - t0))
    op = OP.Op(PC.spec_for())
    code = {f: sha(os.path.join(CODE, f)) for f in CORE if os.path.exists(os.path.join(CODE, f))}
    docs = {f: sha(os.path.join(OUT, f)) for f in DOCS if os.path.exists(os.path.join(OUT, f))}
    h = hashlib.sha256()
    for f in sorted(code):
        h.update(f.encode()); h.update(code[f].encode())
    h.update(json.dumps(env, sort_keys=True).encode())
    methods_core = h.hexdigest()
    aud = json.load(open(f"{OUT}/_audit.json"))
    prov = json.load(open(f"{OUT}/_provenance_audit.json"))
    out = {
        "FREEZE": 1, "frozen_before": "the first informative start of OBTC01",
        "METHODS_CORE_HASH": methods_core,
        "code_sha256": code, "doc_sha256": docs,
        "spec_sha256": GT.spec_sha256(), "spec": spec,
        "N2_envelope": {"grid_N_X": list(NX_GRID), "draws": ENV_DRAWS, "seed": ENV_SEED,
                        "quantiles": spec["gate"]["MODEL_PREDICTION_COMPATIBILITY"]["quantiles"],
                        "by_L": env,
                        "note": "pre-registered. It is produced by the GENERATIVE null, which "
                                "conditions on nothing that was realised; only the sample size "
                                "is matched."},
        "analytic_predictions": {str(L): op.predictions(L)
                                 for L in (spec["point"]["L"], spec["point"]["L_large"])},
        "GATE_SATISFIABILITY": aud["GATE_SATISFIABILITY"],
        "TOPOLOGICAL_WINDING_TESTS": aud["TOPOLOGICAL_WINDING_TESTS"],
        "ONLINE_POSTHOC_AGREEMENT": aud["ONLINE_POSTHOC_AGREEMENT"],
        "PROTOCOL_ADVERSARIAL_AUDIT": aud["PROTOCOL_ADVERSARIAL_AUDIT"],
        "PROVENANCE_STATUS": prov["PROVENANCE_STATUS"],
        "inherited_head": prov["HEAD"], "inherited_tree": prov["tree"],
        "starts_before_this_freeze": {k: GD.used(k) for k in GD.CAPS},
        "C3_reintroduced": False, "added_cohesion": "NONE",
        "H3_STATUS": "NOT_TESTED", "REPRODUCTION_STATUS": "NOT_TESTED",
        "AUTONOMOUS_COHESION_STATUS": "NOT_ESTABLISHED",
    }
    json.dump(out, open(f"{OUT}/_freeze.json", "w"), indent=1, default=str)
    print("METHODS_CORE_HASH = %s" % methods_core)
    print("spec sha256       = %s" % out["spec_sha256"])
    print("files frozen      = %d code, %d docs" % (len(code), len(docs)))
    print("audit             = %s / %s / %s / %s"
          % (aud["GATE_SATISFIABILITY"], aud["TOPOLOGICAL_WINDING_TESTS"],
             aud["ONLINE_POSTHOC_AGREEMENT"], aud["PROTOCOL_ADVERSARIAL_AUDIT"]))
    print("starts before freeze:", out["starts_before_this_freeze"])
    e = env[str(spec["point"]["L"])]["120"]
    print("envelope at L=36, N_X=120:", json.dumps({k: [round(x, 3) for x in v]
                                                    for k, v in e.items()}))


if __name__ == "__main__":
    main()
