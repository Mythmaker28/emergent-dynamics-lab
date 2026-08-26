"""EVCS01 §5 — the campaign sizing instrument.

Two independent campaigns in this programme were frozen with single-digit power and duly failed:

    FIMRCC01   P(k >= 2 | n = 50, observed locked-daughter rate 1/256) = 0.0165
    OMLDCT02   P(41 pairs | ceiling 512, realised admissible rate)     = 0.076

Neither was bad luck. In both, a pair target and a cost ceiling were frozen independently and never
checked against each other. This file exists so that cannot happen silently again: it takes an
empirical ledger of (cost, admissible) outcomes and answers, by bootstrap over that ledger, what
ceiling a target actually needs — and it refuses to hand back a ceiling that is below the target's
own median cost without saying so out loud.

Everything here is a SAMPLING-YIELD quantity: how many worlds a pair costs. None of it is the paired
duration or exposure endpoint, and none of it touches the owner's rule that fewer than 41 pairs may
not be interpreted using the paired p-values. That rule is untouched.
"""
from __future__ import annotations
import json, os, sys
import numpy as np

REPO = os.environ.get("EVCS01_REPO", "/home/claude/edl")
BOOTSTRAP_SEED = 20260826          # frozen; the instrument is deterministic
DEFAULT_REPLICATES = 20000

# The sizing rate OMLDCT02's design actually used, and what it cost. Recorded as a fixed fact so a
# future campaign cannot reach for it again without seeing this next to it.
TLMR01_DEVELOPMENTAL_SIZING = {
    "source": "the 256 developmental LAW_C_MCTT01 worlds, per OMLDCT02_DESIGN_RECOMPUTED.json",
    "n_worlds": 256, "n_admissible": 22, "n_triggered_not_carried": 4, "n_no_trigger": 230,
    "implied_admissible_rate": 22 / 256,
    "NOT_EXCHANGEABLE_WITH_THE_PROSPECTIVE_LEDGER": {
        "expected_admissible_in_805_seeds_at_the_sizing_rate": 805 * 22 / 256,
        "observed": 33,
        "binomial_tail_P_X_le_33": None,     # filled by load(); needs scipy
        "trigger_rate_sizing": 26 / 256, "trigger_rate_realised": 52 / 805,
        "carried_given_triggered_sizing": 22 / 26, "carried_given_triggered_realised": 33 / 52,
        "WHY_IT_CANNOT_BE_DIAGNOSED": "the 256 developmental archives no longer exist in this "
            "container, so the most likely explanation — that 'carried' meant something laxer "
            "before the E3 qualification rule was rebuilt during OMLDCT01 — cannot be checked. "
            "What survives is the conclusion: do not size from that set.",
    },
    "DO_NOT_SIZE_FROM_THIS": True,
}


def load_ledger(path=None):
    """(cost, admissible) per seed, from the frozen prospective ledger."""
    path = path or f"{REPO}/OMLDCT02/work/OMLDCT02_SEALED_LEDGER.jsonl"
    rows = [json.loads(l) for l in open(path) if l.strip()]
    cost = np.array([r["instance_cost"] for r in rows], float)
    adm = np.array([bool(r.get("ADMISSIBLE")) for r in rows], bool)
    return cost, adm, path


def cost_to_reach(cost, adm, target, replicates=DEFAULT_REPLICATES, seed=BOOTSTRAP_SEED):
    """bootstrap distribution of the arm-instance cost of accruing `target` valid pairs."""
    rng = np.random.default_rng(seed)
    n = len(cost)
    out = np.empty(replicates)
    for i in range(replicates):
        c = 0.0
        k = 0
        while k < target:
            j = rng.integers(0, n)
            c += cost[j]
            if adm[j]:
                k += 1
        out[i] = c
    return out


def p_reach(cost, adm, target, ceiling, replicates=DEFAULT_REPLICATES, seed=BOOTSTRAP_SEED):
    """P(accruing `target` pairs before `ceiling` arm-instances is exhausted)."""
    rng = np.random.default_rng(seed)
    n = len(cost)
    hit = 0
    for _ in range(replicates):
        c = 0.0
        k = 0
        while k < target:
            j = rng.integers(0, n)
            if c + cost[j] > ceiling:
                break
            c += cost[j]
            if adm[j]:
                k += 1
        if k >= target:
            hit += 1
    return hit / replicates


def size_campaign(target, confidence=0.95, cost=None, adm=None, replicates=DEFAULT_REPLICATES):
    """the instrument. Returns the ceiling that attains `confidence`, and everything a reader needs
    to see that it was not chosen to flatter anyone."""
    if cost is None:
        cost, adm, src = load_ledger()
    else:
        src = "caller-supplied"
    d = cost_to_reach(cost, adm, target, replicates)
    ceiling = float(np.percentile(d, confidence * 100))
    p50 = float(np.percentile(d, 50))
    rate = float(adm.mean())
    return {
        "LEDGER": src, "n_seeds": int(len(cost)),
        "admissible": int(adm.sum()), "admissible_rate": rate,
        "cost_per_admissible_pair": float(cost.sum() / adm.sum()),
        "TARGET_PAIRS": target, "CONFIDENCE": confidence,
        "REQUIRED_CEILING": ceiling,
        "COST_DISTRIBUTION": {f"p{q}": float(np.percentile(d, q)) for q in (5, 25, 50, 75, 90, 95)},
        "MEDIAN_COST": p50,
        "EXPECTED_SEEDS": target / rate if rate else None,
        "BOOTSTRAP_SEED": BOOTSTRAP_SEED, "REPLICATES": replicates,
        "STOP_RULE": "stop on PAIRS, not on cost. The ceiling is a cost bound, not a stopping rule. "
                     "A ceiling that binds must be news, not a result. Pre-register an interim "
                     "re-estimate that may only RAISE the ceiling, never lower the target.",
    }


def refuse_or_warn(proposed_ceiling, sizing):
    """the refusal the launcher requires: a ceiling below the target's own median cost is named."""
    p50 = sizing["MEDIAN_COST"]
    if proposed_ceiling < p50:
        return {"VERDICT": "REFUSED",
                "why": f"a ceiling of {proposed_ceiling:g} is below the median cost {p50:.1f} of "
                       f"accruing {sizing['TARGET_PAIRS']} pairs. More than half of all campaigns "
                       f"under this design end on the ceiling with the target unmet. That is not a "
                       f"risk, it is the expected outcome."}
    if proposed_ceiling < sizing["REQUIRED_CEILING"]:
        return {"VERDICT": "WARNED",
                "why": f"a ceiling of {proposed_ceiling:g} is above the median {p50:.1f} but below "
                       f"the {sizing['CONFIDENCE']:.0%} ceiling {sizing['REQUIRED_CEILING']:.1f}."}
    return {"VERDICT": "OK"}


SELF_TESTS = [
    ("realised admissible rate is 33/805", lambda s: s["admissible"] == 33 and s["n_seeds"] == 805),
    ("cost per admissible pair is 15.47 +- 0.01",
     lambda s: abs(s["cost_per_admissible_pair"] - 15.4718) < 0.01),
    ("P(41 pairs | ceiling 512) is under 0.12", lambda s: s["_p512"] < 0.12),
    ("P(41 pairs | ceiling 512) is over 0.03", lambda s: s["_p512"] > 0.03),
    ("the 95% ceiling for 41 pairs is between 700 and 900",
     lambda s: 700 <= s["REQUIRED_CEILING"] <= 900),
    ("OMLDCT02's frozen ceiling of 512 is below the median cost of its own target",
     lambda s: 512 < s["MEDIAN_COST"]),
    ("a ceiling of 512 for 41 pairs is REFUSED by the instrument",
     lambda s: s["_refuse512"]["VERDICT"] == "REFUSED"),
    ("a ceiling of 800 for 41 pairs is not refused",
     lambda s: s["_refuse800"]["VERDICT"] in ("OK", "WARNED")),
    ("the TLMR01 developmental rate is more than 1.8x the realised rate",
     lambda s: (22 / 256) / s["admissible_rate"] > 1.8),
    ("sizing from TLMR01 is flagged DO_NOT_SIZE_FROM_THIS",
     lambda s: TLMR01_DEVELOPMENTAL_SIZING["DO_NOT_SIZE_FROM_THIS"] is True),
]


def run_self_tests(replicates=DEFAULT_REPLICATES):
    cost, adm, _ = load_ledger()
    s = size_campaign(41, 0.95, cost, adm, replicates)
    s["_p512"] = p_reach(cost, adm, 41, 512, replicates)
    s["_refuse512"] = refuse_or_warn(512, s)
    s["_refuse800"] = refuse_or_warn(800, s)
    try:
        from scipy.stats import binom
        TLMR01_DEVELOPMENTAL_SIZING["NOT_EXCHANGEABLE_WITH_THE_PROSPECTIVE_LEDGER"][
            "binomial_tail_P_X_le_33"] = float(binom.cdf(33, 805, 22 / 256))
    except Exception:
        pass
    results = [{"test": name, "PASS": bool(fn(s))} for name, fn in SELF_TESTS]
    return s, results


if __name__ == "__main__":
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_REPLICATES
    s, res = run_self_tests(reps)
    for r in res:
        print(("PASS  " if r["PASS"] else "FAIL  ") + r["test"])
    print(f"\nALL_SELF_TESTS_PASS = {all(r['PASS'] for r in res)}")
    print(f"required ceiling for 41 pairs at 95% = {s['REQUIRED_CEILING']:.1f}")
    print(f"P(41 | 512) = {s['_p512']:.4f}   median cost = {s['MEDIAN_COST']:.1f}")
