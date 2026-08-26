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

# ---------------------------------------------------------------------------------------------
# C3 CORRECTION, after the independent checker. The C1/C2 version of this file computed a single
# REQUIRED_CEILING as the 95th percentile of the cost to reach the target CONDITIONAL ON THE
# ADMISSIBLE RATE BEING EXACTLY THE LEDGER'S RATE. The checker showed that is not a 95% ceiling:
# propagating the rate's own sampling uncertainty, a campaign freezing 785 attains about 85%, not
# 95%. That is, in milder form, the exact error this instrument exists to prevent — treating a
# finite-sample yield estimate as a known parameter, which is what made 22/256 look usable.
#
# Both ceilings are now returned. The rate-uncertain one is the one a successor should freeze.
# The C1/C2 code is preserved in git at 2c80d6d and db4b60d; nothing is rewritten.
# evcs01_measure.py is NOT touched: the composition is a measurement and stays frozen.
# ---------------------------------------------------------------------------------------------

# The sizing rate OMLDCT02's design actually used, and what it cost. Recorded as a fixed fact so a
# future campaign cannot reach for it again without seeing this next to it.
TLMR01_DEVELOPMENTAL_SIZING = {
    "source": "the 256 developmental LAW_C_MCTT01 worlds, per OMLDCT02_DESIGN_RECOMPUTED.json",
    "n_worlds": 256, "n_admissible": 22, "n_triggered_not_carried": 4, "n_no_trigger": 230,
    "implied_admissible_rate": 22 / 256,
    "NOT_EXCHANGEABLE_WITH_THE_PROSPECTIVE_LEDGER": {
        "expected_admissible_in_805_seeds_at_the_sizing_rate": 805 * 22 / 256,
        "observed": 33,
        "binomial_tail_P_X_le_33": 4.163814e-07,
        "THAT_TAIL_IS_THE_WRONG_EVIDENCE_AND_IS_KEPT_ONLY_TO_BE_CORRECTED":
            "it treats the 256-world estimate as a known parameter. The checker was right. The "
            "correct two-sample comparison of [[22, 234], [33, 772]] gives Fisher exact "
            "p = 0.008710 and chi-square with continuity correction p = 0.007734. The conclusion "
            "survives comfortably; the strength attached to it was overstated by about 2.1e4.",
        "fisher_exact_two_sample_p": 0.008710,
        "chi2_continuity_corrected_p": 0.007734,
        "wilson_95_CI_sizing": [0.0574, 0.1267],
        "wilson_95_CI_realised": [0.0293, 0.0570],
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


def cost_to_reach_rate_uncertain(cost, adm, target, replicates=DEFAULT_REPLICATES,
                                 seed=BOOTSTRAP_SEED):
    """the same bootstrap, but the admissible RATE is drawn from its own Jeffreys posterior on each
    replicate instead of being held at the ledger's point estimate. Costs are still resampled from
    the two empirical pools, so only the yield uncertainty is added."""
    rng = np.random.default_rng(seed)
    ca = cost[adm]
    cn = cost[~adm]
    a = float(adm.sum()) + 0.5
    b = float((~adm).sum()) + 0.5
    out = np.empty(replicates)
    for i in range(replicates):
        p = rng.beta(a, b)
        c = 0.0
        k = 0
        while k < target:
            if rng.random() < p:
                c += ca[rng.integers(0, len(ca))]
                k += 1
            else:
                c += cn[rng.integers(0, len(cn))]
        out[i] = c
    return out


def p_reach_rate_uncertain(cost, adm, target, ceiling, replicates=DEFAULT_REPLICATES,
                           seed=BOOTSTRAP_SEED):
    """P(reaching `target` within `ceiling`) with the admissible rate drawn from its own Jeffreys
    posterior on each replicate, instead of held at the ledger's point estimate."""
    rng = np.random.default_rng(seed)
    ca = cost[adm]
    cn = cost[~adm]
    a = float(adm.sum()) + 0.5
    b = float((~adm).sum()) + 0.5
    hit = 0
    for _ in range(replicates):
        p = rng.beta(a, b)
        c = 0.0
        k = 0
        while k < target:
            adm_draw = rng.random() < p
            step = ca[rng.integers(0, len(ca))] if adm_draw else cn[rng.integers(0, len(cn))]
            if c + step > ceiling:
                break
            c += step
            if adm_draw:
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
        # C3 fix, checker finding 23: the frozen artefact used to record "caller-supplied" and so
        # did not name its own input. Name it, and prove it is the same ledger.
        _c, _a, src = load_ledger()
        if not (len(_c) == len(cost) and float(_c.sum()) == float(np.asarray(cost).sum())):
            src = "caller-supplied (NOT the committed ledger)"
    d = cost_to_reach(cost, adm, target, replicates)
    du = cost_to_reach_rate_uncertain(cost, adm, target, replicates)
    ceiling = float(np.percentile(d, confidence * 100))
    ceiling_u = float(np.percentile(du, confidence * 100))
    p50 = float(np.percentile(d, 50))
    rate = float(adm.mean())
    k = int(adm.sum())
    n = int(len(adm))
    try:
        from scipy.stats import beta as _bt
        wilson = [float(_bt.ppf(0.025, k, n - k + 1)), float(_bt.ppf(0.975, k + 1, n - k))]
    except Exception:
        wilson = None
    return {
        "LEDGER": src, "n_seeds": int(len(cost)),
        "admissible": int(adm.sum()), "admissible_rate": rate,
        "cost_per_admissible_pair": float(cost.sum() / adm.sum()),
        "admissible_rate_95_CI": wilson,
        "TARGET_PAIRS": target, "CONFIDENCE": confidence,
        "REQUIRED_CEILING_IF_THE_RATE_WERE_KNOWN_EXACTLY": ceiling,
        "REQUIRED_CEILING": ceiling_u,
        "WHICH_CEILING_TO_FREEZE": "REQUIRED_CEILING, the rate-uncertain one. The other is what "
            "this instrument returned at C1/C2 and it is optimistic: it conditions on the ledger's "
            "rate being the truth. The checker showed a campaign freezing the optimistic value "
            "attains about 85 per cent, not 95. Corrected at C3.",
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


# The checker judged the original ten to be five real tests, two duplicates, two near-unfailable
# and one tautology. That judgement is accepted. The originals are kept unchanged so the C1 freeze
# is not rewritten; the weak ones are marked, and four discriminating tests are added below.
WEAK_TESTS_PER_THE_CHECKER = {
    "a ceiling of 512 for 41 pairs is REFUSED by the instrument": "duplicate of test 6",
    "a ceiling of 800 for 41 pairs is not refused": "near-unfailable",
    "the TLMR01 developmental rate is more than 1.8x the realised rate": "half hard-coded",
    "sizing from TLMR01 is flagged DO_NOT_SIZE_FROM_THIS": "tautology — reads a literal",
}

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
    # --- added at C3, all data-dependent and all able to fail ---
    ("the rate-uncertain ceiling exceeds the rate-known ceiling",
     lambda s: s["REQUIRED_CEILING"] > s["REQUIRED_CEILING_IF_THE_RATE_WERE_KNOWN_EXACTLY"]),
    ("the rate-uncertain ceiling for 41 pairs is between 830 and 960",
     lambda s: 830 <= s["REQUIRED_CEILING"] <= 960),
    ("the rate-known ceiling attains well under 95 percent once the rate is uncertain",
     lambda s: s["_p_at_known_ceiling_rate_uncertain"] < 0.90),
    ("the ledger names itself rather than reporting caller-supplied",
     lambda s: s["LEDGER"].endswith("OMLDCT02_SEALED_LEDGER.jsonl")),
]


def run_self_tests(replicates=DEFAULT_REPLICATES):
    cost, adm, _ = load_ledger()
    s = size_campaign(41, 0.95, cost, adm, replicates)
    s["_p512"] = p_reach(cost, adm, 41, 512, replicates)
    s["_refuse512"] = refuse_or_warn(512, s)
    s["_refuse800"] = refuse_or_warn(800, s)
    s["_p_at_known_ceiling_rate_uncertain"] = p_reach_rate_uncertain(
        cost, adm, 41, s["REQUIRED_CEILING_IF_THE_RATE_WERE_KNOWN_EXACTLY"], replicates)
    # C3 fix, checker finding 23: this used to mutate the module dict only if scipy imported,
    # which made SIZING_CONTENT_HASH environment-dependent. The values are now literals.
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
