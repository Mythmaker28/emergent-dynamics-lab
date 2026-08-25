"""OMLDCT02 — the design recomputation, run before world 1 and changing nothing.

Section 10 requires the exact cost accounting to be recomputed. It was, and it disagrees with what
OMLDCT01 disclosed. OMLDCT01 published P(reaching 41 pairs) = 0.5063 and P(under-accrual) = 0.4937.
Those numbers are reproduced here EXACTLY — and they turn out to describe a campaign limited by the
LENGTH OF ITS SEED LIST, not by the frozen 512-arm-instance ceiling. Under the ceiling alone the
probability is essentially 1. The frozen design quantities do not move; the candidate list does.
"""
from __future__ import annotations
import json, os, sys, datetime
import numpy as np

REPO = os.environ.get("OMLDCT02_REPO", "/home/claude/edl")
sys.path.insert(0, os.path.join(REPO, "OMLDCT02", "code"))
import omldct02_hashes as H

T_HORIZON = 11000
LATEST_ALLOWED_TRIGGER = 6500
PREFIX_LIMIT = LATEST_ALLOWED_TRIGGER + 1          # 6501
TARGET_VALID_PAIRED_BLOCKS = 41                    # frozen, unchanged
MAX_PRIMARY_ARM_INSTANCES = 512                    # frozen, unchanged
MC_SEED = 20260826                                 # fixed, so this file is reproducible
MC_TRIALS = 20000
MC_BLOCK = 1400

# The empirical LAW_C_MCTT01 outcome distribution, from the 256 developmental worlds TLMR01 ran.
# These are DEVELOPMENTAL data used only to SIZE the design, exactly as the parent handoff sized it.
# No OMLDCT01 pilot outcome enters here.
N_LAW_C_WORLDS = 256
TM_ADMISSIBLE = [479, 547, 580, 603, 606, 658, 683, 697, 720, 728, 840, 903, 928, 942,
                 1062, 1135, 1204, 1334, 1418, 2017, 2348, 2379]      # 22 triggered and carried
TM_TRIGGERED_NOT_CARRIED = [490, 639, 1497, 1959]                      # 4
N_NO_TRIGGER = N_LAW_C_WORLDS - len(TM_ADMISSIBLE) - len(TM_TRIGGERED_NOT_CARRIED)   # 230

def cost_admissible(tm):
    """one common prefix to t_m, then two full-horizon arms."""
    return (tm + 1) / T_HORIZON + 2 * (T_HORIZON - tm - 1) / T_HORIZON

def cost_triggered_not_carried(tm):
    """the prefix is paid; no arm is ever created."""
    return (tm + 1) / T_HORIZON

def cost_no_trigger():
    """the prefix runs only to the frozen deadline, because a candidate after it cannot trigger."""
    return PREFIX_LIMIT / T_HORIZON

def simulate(n_base_cap, ceiling=MAX_PRIMARY_ARM_INSTANCES, trials=MC_TRIALS, block=MC_BLOCK,
             mc_seed=MC_SEED):
    """Vectorised. A seed may only be STARTED when the cost already spent plus the largest cost a
    single seed can incur still fits under the ceiling, so the ceiling is never breached."""
    rng = np.random.default_rng(mc_seed)
    na, nn = len(TM_ADMISSIBLE), len(TM_TRIGGERED_NOT_CARRIED)
    u = rng.integers(0, N_LAW_C_WORLDS, size=(trials, block))
    ia = rng.integers(0, na, size=(trials, block)); inn = rng.integers(0, nn, size=(trials, block))
    tma = np.asarray(TM_ADMISSIBLE)[ia]; tmn = np.asarray(TM_TRIGGERED_NOT_CARRIED)[inn]
    c = np.full(u.shape, cost_no_trigger())
    adm = u < na; nc = (u >= na) & (u < na + nn)
    c[adm] = ((tma + 1) / T_HORIZON + 2 * (T_HORIZON - tma - 1) / T_HORIZON)[adm]
    c[nc] = ((tmn + 1) / T_HORIZON)[nc]
    cum = np.cumsum(c, axis=1); pairs = np.cumsum(adm, axis=1)
    idx = np.arange(block)[None, :]
    startable = (cum - c + 2.0 <= ceiling) & (idx < n_base_cap)
    stop_resource = np.where(~startable, idx, block).min(axis=1)
    stop_target = np.where(pairs >= TARGET_VALID_PAIRED_BLOCKS, idx, block).min(axis=1)
    reached = stop_target < stop_resource
    seeds_used = np.minimum(stop_target + 1, stop_resource)
    cost_used = np.where(reached, cum[np.arange(trials), np.minimum(stop_target, block - 1)],
                         np.where(stop_resource > 0,
                                  cum[np.arange(trials), np.maximum(stop_resource - 1, 0)], 0.0))
    return {"P_reaching_target": float(reached.mean()),
            "P_under_accrual": float(1 - reached.mean()),
            "seeds_used_mean": float(seeds_used.mean()),
            "seeds_used_p99": float(np.percentile(seeds_used, 99)),
            "seeds_used_p99_99": float(np.percentile(seeds_used, 99.99)),
            "seeds_used_max": int(seeds_used.max()),
            "instances_used_mean": float(cost_used.mean()),
            "instances_used_max": float(cost_used.max())}

def main():
    p_adm = len(TM_ADMISSIBLE) / N_LAW_C_WORLDS
    mean_cost = (p_adm * float(np.mean([cost_admissible(t) for t in TM_ADMISSIBLE]))
                 + len(TM_TRIGGERED_NOT_CARRIED) / N_LAW_C_WORLDS
                   * float(np.mean([cost_triggered_not_carried(t) for t in TM_TRIGGERED_NOT_CARRIED]))
                 + N_NO_TRIGGER / N_LAW_C_WORLDS * cost_no_trigger())
    old = simulate(474)
    new = simulate(1024)
    unlimited = simulate(10 ** 9)
    doc = {
     "MISSION": "OMLDCT02", "SECTION": "design recomputation, before world 1",
     "GENERATED_UTC": datetime.datetime.now(datetime.timezone.utc).isoformat(),
     "GENERATOR": "OMLDCT02/code/omldct02_design.py — deterministic, MC_SEED fixed in the file",
     "FROZEN_AND_UNCHANGED": {
       "TARGET_VALID_PAIRED_BLOCKS": TARGET_VALID_PAIRED_BLOCKS,
       "MAX_PRIMARY_ARM_INSTANCES": MAX_PRIMARY_ARM_INSTANCES,
       "ONE_ARM_INSTANCE": "one full-horizon world-equivalent of engine work, T = 11000",
       "T_HORIZON": T_HORIZON, "LATEST_ALLOWED_TRIGGER": LATEST_ALLOWED_TRIGGER},
     "COST_MODEL": {
       "admissible": "prefix to t_m, then two full-horizon arms: (t_m+1)/T + 2(T-t_m-1)/T",
       "triggered_not_carried": "prefix only: (t_m+1)/T — no arm is ever created",
       "no_trigger": f"prefix to the frozen deadline only: {PREFIX_LIMIT}/T = {cost_no_trigger():.4f}",
       "prefix_truncation_justification":
         "a maturation candidate after LATEST_ALLOWED_TRIGGER fails the frozen deadline gate, so a "
         "world with no candidate by that step can never trigger. This uses the frozen rule and "
         "changes no definition.",
       "mean_instances_per_base_seed": round(mean_cost, 5),
       "p_admissible_per_seed": round(p_adm, 5)},
     "SIZING_DATA": {
       "source": "the 256 developmental LAW_C_MCTT01 worlds TLMR01 ran",
       "n_worlds": N_LAW_C_WORLDS, "n_admissible": len(TM_ADMISSIBLE),
       "n_triggered_not_carried": len(TM_TRIGGERED_NOT_CARRIED), "n_no_trigger": N_NO_TRIGGER,
       "NO_OMLDCT01_PILOT_OUTCOME_ENTERS_THIS":
         "the four pre-C2 pilot outcomes are DEVELOPMENTAL_PILOT_DIAGNOSTIC and are excluded from "
         "power, seed selection, thresholds and every estimate. This sizing uses only the same "
         "developmental data the parent handoff used."},
     "MONTE_CARLO": {"seed": MC_SEED, "trials": MC_TRIALS,
                     "ceiling_never_breached_by_construction": True},
     "WHAT_OMLDCT01_DISCLOSED": {"P_reaching_41_pairs": 0.5063, "P_under_accrual": 0.4937},
     "RECOMPUTED_AT_A_474_SEED_LIST": old,
     "RECOMPUTED_AT_THE_1024_SEED_LIST": new,
     "RECOMPUTED_WITH_THE_INSTANCE_CEILING_ALONE": unlimited,
     "THE_FINDING": {
       "what": "OMLDCT01's disclosed 0.5063 is reproduced here at 474 seeds and is therefore "
               "correct — but it measures the wrong constraint. It is the probability of reaching "
               "41 pairs before the SEED LIST runs out, not before the frozen 512-instance ceiling "
               "does. With the ceiling alone the probability is essentially 1 and the largest "
               "number of seeds any simulated campaign consumed was "
               f"{unlimited['seeds_used_max']}.",
       "why_it_matters": "a 474-long list stops the campaign roughly half the time for a reason "
                         "that is not in the frozen design at all. That is an implementation "
                         "shortfall, not a power limitation.",
       "what_changes": "the candidate list length only. OMLDCT02 freezes 1024 base seeds so that "
                       "the frozen ceiling is what binds.",
       "what_does_not_change": "the target of 41 valid paired blocks, the 512-arm-instance "
                               "ceiling, the endpoints, the test, the alpha, the direction, the "
                               "combination rule, the zero treatment and the claim ceiling.",
       "residual_under_accrual_risk": round(new["P_under_accrual"], 5),
       "and_it_is_disclosed_not_used_to_change_the_design": True},
     "N_BASE_FROZEN": 1024, "N_RESERVE_FROZEN": 6,
     "RESERVE_BASIS": "MAX_TECHNICAL_RESERVES = 6 in the committed parent handoff. Technical only: "
                      "a technical retry reuses the identical seed and arm; a scientific "
                      "non-trigger consumes its seed and is never replaced.",
     "WORLDS_RUN": 0,
    }
    doc["DESIGN_CONTENT_HASH"] = H.content_digest(doc)
    json.dump(doc, open(f"{REPO}/OMLDCT02/out/OMLDCT02_DESIGN_RECOMPUTED.json", "w"), indent=1)
    print(f"mean instances per base seed = {mean_cost:.4f}")
    print(f"474-seed list : P(41 pairs) = {old['P_reaching_target']:.4f}   (OMLDCT01 disclosed 0.5063)")
    print(f"1024-seed list: P(41 pairs) = {new['P_reaching_target']:.5f}")
    print(f"ceiling alone : P(41 pairs) = {unlimited['P_reaching_target']:.5f}  max seeds {unlimited['seeds_used_max']}")
    print("DESIGN_CONTENT_HASH =", doc["DESIGN_CONTENT_HASH"])

if __name__ == "__main__":
    main()
