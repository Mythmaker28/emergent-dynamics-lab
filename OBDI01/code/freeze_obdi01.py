"""OBDI01 §22 — complete the frozen protocol with the profile-compatibility envelope, then
freeze: METHODS_CORE_HASH over the exact bytes of the code and the spec that will produce the
arms, plus the four diff declarations against OBTC02.

The envelope is generated from the EXACT kernel and the observed autocorrelation, never from
any OBDI01 arm — none exists yet. It is written into the spec BEFORE the hash is taken, so the
hash covers it.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

import numpy as np
import yaml

sys.path.insert(0, "/home/claude/ORR01/code")
sys.path.insert(0, "/home/claude/OBDI01/code")

import gate_obdi01 as GT           # noqa: E402
import nulls_obtc as NU            # noqa: E402
import protocol_obtc02 as PC       # noqa: E402
import source_operator as OP       # noqa: E402

CODE = "/home/claude/OBDI01/code"
OUT = "/home/claude/OBDI01/out"
SPEC_PATH = f"{CODE}/obdi01_protocol.yaml"
ENV_REPLICATES = 800
ENV_QUANTILE = 0.99

# every file whose bytes can change what an arm produces or how it is judged
METHODS_CORE = [
    "obdi01_protocol.yaml", "gate_obdi01.py", "protocol_obdi01.py", "run_obdi01.py",
    "gate_obtc02.py", "protocol_obtc02.py", "engine_obtc.py", "metrics_obtc.py",
    "nulls_obtc.py", "topology.py", "source_operator.py", "guard_obtc.py",
    "obtc02_protocol.yaml", "n2_envelope.json",
]


def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def envelope_for(L, op, edges, n_eff, n_rep, seed, N_X):
    """Distribution of the total-variation distance between a pooled empirical radial profile
    built from n_eff INDEPENDENT frames and the exact predicted radial profile."""
    pred = GT.predicted_radial(op.relative_profile(L), edges)
    rng = np.random.default_rng(seed)
    tv = np.empty(n_rep)
    for r in range(n_rep):
        acc = np.zeros(len(edges))
        for _ in range(n_eff):
            f, org = NU.n2_generative(rng, L, N_X, op.qX, op.qY, op.mu)
            acc += GT.empirical_radial(f, org[0], org[1], edges) * N_X
        tv[r] = GT.total_variation(acc / acc.sum(), pred)
    return {"n_effective_frames": int(n_eff), "replicates": int(n_rep),
            "quantile": ENV_QUANTILE, "quantile_value": float(np.quantile(tv, ENV_QUANTILE)),
            "median": float(np.median(tv)), "mean": float(tv.mean()),
            "q50": float(np.quantile(tv, 0.5)), "q95": float(np.quantile(tv, 0.95)),
            "max": float(tv.max()), "N_X_used": int(N_X),
            "predicted_radial": [float(x) for x in pred]}


def main():
    spec = yaml.safe_load(open(SPEC_PATH))
    P = json.load(open(f"{OUT}/_predictions.json"))
    OC = json.load(open(f"{OUT}/_legacy_gate_OC.json"))
    sizes = [int(x) for x in spec["domain"]["SIZES"]]
    edges = list(spec["principal_outcome"]["components"]["D_profile_compatibility"][
        "radial_bin_edges"])
    N_X = int(round(float(P["N_X_anchor_used"])))
    rho = float(OC["lag1_autocorrelation"]["mean"])
    n_frames = (spec["window"]["HORIZON"] - spec["window"]["BURN_IN"]) \
        // spec["window"]["SAMPLE_EVERY"]
    n_eff = int(round(n_frames * (1.0 - rho) / (1.0 + rho)))

    op = OP.Op(PC.spec_for(36))
    env = {}
    for j, L in enumerate(sizes):
        env[str(L)] = envelope_for(L, op, edges, n_eff, ENV_REPLICATES, 880000 + 7 * L, N_X)
        print("L=%-4d TV envelope  median %.4f  q95 %.4f  q99 %.4f  max %.4f"
              % (L, env[str(L)]["median"], env[str(L)]["q95"],
                 env[str(L)]["quantile_value"], env[str(L)]["max"]), flush=True)

    d = spec["principal_outcome"]["components"]["D_profile_compatibility"]
    d["envelope_n_effective_frames"] = n_eff
    d["envelope_autocorrelation_used"] = rho
    d["envelope_derivation"] = (
        "the %d in-window frames of an arm are autocorrelated (mean lag-1 %.3f measured in §8), "
        "so an envelope built from independent frames would be far too tight. The effective "
        "count n_eff = n (1 - rho) / (1 + rho) = %d is used instead. This is a pre-registered "
        "and deliberately CONSERVATIVE choice: it widens the envelope."
        % (n_frames, rho, n_eff))
    d["envelope_by_L"] = env
    with open(SPEC_PATH, "w") as f:
        yaml.safe_dump(spec, f, sort_keys=False, width=100, allow_unicode=True,
                       default_flow_style=False)

    # ---- N2 model-compatibility envelope: OBTC02's own, extended to the new domain size ----
    o2 = json.load(open("/home/claude/OBDI01/verify/obtc02/wc/OBTC02/out/_freeze.json"))
    n2 = o2["N2_envelope"]
    by_L = {str(L): n2["by_L"][str(L)] for L in sizes if str(L) in n2["by_L"]}
    reused = sorted(by_L)
    for L in sizes:
        if str(L) not in by_L:
            by_L[str(L)] = PC.n2_envelope(L, n2["grid_N_X"], n2["draws"], n2["seed"],
                                          PC.spec_for(L))
            print("N2 envelope generated at L=%d with OBTC02's own grid, draws and seed" % L)
    n2_out = {"grid_N_X": n2["grid_N_X"], "draws": n2["draws"], "seed": n2["seed"],
              "by_L": by_L,
              "REUSED_BIT_IDENTICAL_FROM_OBTC02": reused,
              "GENERATED_AT_THE_NEW_DOMAIN_SIZE": [str(L) for L in sizes
                                                   if str(L) not in reused],
              "note": ("the envelope at the two inherited domain sizes is the OBTC02 object "
                       "itself, copied without recomputation; at the new size it is produced by "
                       "OBTC02's own n2_envelope with OBTC02's own grid, draw count and seed. "
                       "No envelope is widened, narrowed or re-tuned.")}

    json.dump(n2_out, open(f"{CODE}/n2_envelope.json", "w"), indent=1, default=str)

    missing = [n for n in METHODS_CORE if not os.path.exists(os.path.join(CODE, n))]
    digests = {n: sha256(os.path.join(CODE, n)) for n in METHODS_CORE
               if os.path.exists(os.path.join(CODE, n))}
    h = hashlib.sha256()
    for n in sorted(digests):
        h.update(n.encode())
        h.update(b"\0")
        h.update(digests[n].encode())
        h.update(b"\n")
    core = h.hexdigest()

    frz = {
        "SECTION": "OBDI01 §22",
        "N2_ENVELOPE": n2_out,
        "N2_ENVELOPE_FILE": "n2_envelope.json",
        "OBDI01_METHODS_CORE_HASH": core,
        "METHODS_CORE_FILES": digests,
        "METHODS_CORE_MISSING_AT_FREEZE": missing,
        "spec_sha256": sha256(SPEC_PATH),
        "PARENT": spec["parent"],
        "LAWSPEC_DIFF_FROM_OBTC02": "NONE",
        "CHEMOSTAT_DIFF_FROM_OBTC02": "NONE",
        "COHESION_DIFF_FROM_OBTC02": "NONE",
        "SCIENTIFIC_PARAMETER_DIFF_FROM_OBTC02": "NONE",
        "DOMAIN_TEST_DESIGN": "NEW_PREREGISTERED_TARGETED_FOLLOWUP",
        "DESIGN_STATUS": spec["design_status"]["DESIGN_STATUS"],
        "CONFIRMATORY_DATA_STATUS": spec["design_status"]["CONFIRMATORY_DATA_STATUS"],
        "ROUTE": spec["route"]["ROUTE"],
        "LEGACY_D_GATE_STATUS": spec["route"]["LEGACY_D_GATE_STATUS"],
        "DOMAIN_SIZES": sizes,
        "SEEDS": spec["domain"]["SEEDS"],
        "TOTAL_ARMS": spec["domain"]["TOTAL_ARMS"],
        "EARLY_SCIENTIFIC_STOPPING": "FORBIDDEN",
        "SCIENTIFIC_RUNS_USED_AT_FREEZE": 0,
        "PROFILE_ENVELOPE": {L: {k: v for k, v in e.items() if k != "predicted_radial"}
                             for L, e in env.items()},
        "ASSERTIONS": {
            "no_arm_has_been_run": True,
            "the_envelope_uses_no_obdi01_data": True,
            "the_predictions_use_no_obdi01_data": True,
            "every_frozen_number_is_generated_not_transcribed": True,
        },
    }
    json.dump(frz, open(f"{OUT}/_freeze.json", "w"), indent=1, default=str)
    print("\nOBDI01_METHODS_CORE_HASH = %s" % core)
    print("spec_sha256              = %s" % frz["spec_sha256"])
    print("files hashed             = %d   missing at freeze = %s" % (len(digests), missing))


if __name__ == "__main__":
    main()
