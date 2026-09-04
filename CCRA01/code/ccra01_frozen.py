#!/usr/bin/env python3
"""CCRA01 — Competing-risks Cause-specific Re-Analysis 01. FROZEN EXECUTABLE.

This file executes CCRA01_PREREGISTRATION.md and decides nothing that the
preregistration did not already decide. Standard library only: no numpy, no scipy.

  python3 ccra01_frozen.py --capability          adversarial capability search, synthetic
                                                 data only, no real data is read
  python3 ccra01_frozen.py --run <file.json>     the frozen analysis of the real dataset

No file is ever written. JSON goes to stdout and nowhere else.

WHY THE MAPPING MERGES FOUR STRINGS INTO TWO CAUSES — see preregistration section 2.
The frozen classifier omldct02_e3_b.py emits its termination string at lines 216-220
after reducing the in-range boolean matrix to two count vectors at line 125:

    rc[i] = number of candidate SUCCESSORS within CORE_R of previous centre i
    cc[j] = number of candidate PREDECESSORS within CORE_R of current centre j

    line 217   rc[cur] == 0                  -> "OUT_OF_RANGE"
    line 218   rc[cur] >  1                  -> "SPLIT_OR_TIE"
    line 219   else: rc[cur]==1 and cc[j]>1  -> "MERGE"
    line 209   the whole world has no rows   -> "NO_COMPONENT_AT_THE_NEXT_STEP"
    line 207   t+1 >= horizon                -> "REACHED_THE_WINDOW_HORIZON"

Two consequences drive the whole design.

(1) OUT_OF_RANGE and NO_COMPONENT_AT_THE_NEXT_STEP are ONE predicate, split by an
    early return. Line 116 of _link_map returns rc = [0]*npv when the next step holds
    no centre at all; without the early return of lines 208-209 an empty world would
    reach line 217 and be called OUT_OF_RANGE. What separates the two strings is a
    GLOBAL property of the world, not a property of the tracked centre — and in the
    SELECTIVE arm the parent's Y has been removed, so the same physical event (the
    daughter's Y is extinguished) changes its string BETWEEN ARMS. They are merged.

(2) MERGE requires cc[j] > 1, hence at least TWO predecessors. When the locked
    daughter is the only component in the world, cc[j] <= 1 for every j, so if
    rc[cur] == 1 then cc[j] == 1 exactly and the link is kept: MERGE is
    ARITHMETICALLY UNREACHABLE. The risk sets are therefore not the same in the two
    arms, cause-specific hazards are not identifiable, and a raw duration contrast is
    not at equal exposure. The ordered composite is built on the one predicate that IS
    available identically in both arms: rc[cur] == 0 versus rc[cur] >= 1.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import random
import sys
from fractions import Fraction

# --------------------------------------------------------------------------- frozen constants

SPEC_VERSION = "CCRA01-FROZEN-1"

ALPHA = Fraction(1, 40)                       # 0.025 one-sided, exact
SIGN_CONVENTION = "SELECTIVE minus SHAM"
N_PAIRS_REQUIRED = 41

# preregistration section 2.5 — the frozen string -> cause mapping
TERMINATION_TO_CAUSE = {
    "OUT_OF_RANGE":                  "NO_LINKABLE_SUCCESSOR",
    "NO_COMPONENT_AT_THE_NEXT_STEP": "NO_LINKABLE_SUCCESSOR",
    "SPLIT_OR_TIE":                  "AMBIGUOUS_CONTINUATION",
    "MERGE":                         "AMBIGUOUS_CONTINUATION",
    "REACHED_THE_WINDOW_HORIZON":    "NO_TERMINATION_OBSERVED",
}

# worst (0) to best (2)
CAUSE_RANK = {
    "NO_LINKABLE_SUCCESSOR":  0,
    "AMBIGUOUS_CONTINUATION": 1,
    "NO_TERMINATION_OBSERVED": 2,
}

ALLOWED_TERMINATIONS = frozenset(TERMINATION_TO_CAUSE)

REQUIRED_FIELDS = (
    "index", "t_m",
    "SELECTIVE_duration", "SHAM_duration",
    "SELECTIVE_exposure", "SHAM_exposure",
    "log_duration_difference", "log_exposure_difference",
    "SELECTIVE_termination", "SHAM_termination",
)

# --------------------------------------------------------------------------- exact statistics


def exact_upper_tail(m: int, k: int) -> Fraction:
    """P(K >= k) for K ~ Binomial(m, 1/2), exact rational. No floating point."""
    if m < 0 or k < 0 or k > m:
        raise ValueError("exact_upper_tail: k must lie in [0, m]")
    return Fraction(sum(math.comb(m, i) for i in range(k, m + 1)), 1 << m)


def resolution_floor(alpha: Fraction = ALPHA) -> int:
    """Smallest m for which the test CAN cross its threshold: min m with 2^-m <= alpha.

    Below this many discordant pairs the design is incapable of rejecting whatever the
    data are, and the preregistered outcome is NON_CONCLUANT, never NEGATIF."""
    m = 1
    while Fraction(1, 1 << m) > alpha:
        m += 1
        if m > 4096:                                    # unreachable for any sane alpha
            raise RuntimeError("resolution_floor did not converge")
    return m


def critical_k(m: int, alpha: Fraction = ALPHA):
    """Smallest k with P(K >= k) <= alpha, or None when no k attains alpha."""
    for k in range(0, m + 1):
        if exact_upper_tail(m, k) <= alpha:
            return k
    return None


# --------------------------------------------------------------------------- the composite


def cause_of(termination: str) -> str:
    return TERMINATION_TO_CAUSE[termination]


def outcome_of(termination: str, duration: int):
    """The ordered composite of preregistration 3.2: (rank, duration), higher is better."""
    return (CAUSE_RANK[TERMINATION_TO_CAUSE[termination]], int(duration))


def compare_outcomes(sel, sham) -> int:
    """+1 SELECTIVE better, -1 SELECTIVE worse, 0 tie. Lexicographic: rank, then duration."""
    if sel[0] != sham[0]:
        return 1 if sel[0] > sham[0] else -1
    if sel[1] != sham[1]:
        return 1 if sel[1] > sham[1] else -1
    return 0


def score_pairs(records, tiebreak="duration"):
    """Turn records into per-pair win/loss/tie. tiebreak selects the layer under the rank.

    'duration' is the primary, frozen choice. 'exposure' is secondary analysis S1 and is
    explicitly NON-confirmatory."""
    key_sel = "SELECTIVE_" + tiebreak
    key_sham = "SHAM_" + tiebreak
    out = []
    for r in records:
        sel = outcome_of(r["SELECTIVE_termination"], r[key_sel])
        sham = outcome_of(r["SHAM_termination"], r[key_sham])
        w = compare_outcomes(sel, sham)
        out.append({
            "index": r["index"],
            "SELECTIVE_cause": cause_of(r["SELECTIVE_termination"]),
            "SHAM_cause": cause_of(r["SHAM_termination"]),
            "SELECTIVE_rank": sel[0], "SHAM_rank": sham[0],
            "rank_decided": sel[0] != sham[0],
            "W": w,
        })
    return out


def sign_test(scored, alpha: Fraction = ALPHA):
    """Exact paired sign test, one-sided in the preregistered direction theta > 0."""
    losses = sum(1 for s in scored if s["W"] == -1)     # SELECTIVE worse
    wins = sum(1 for s in scored if s["W"] == 1)        # SELECTIVE better
    ties = sum(1 for s in scored if s["W"] == 0)
    m = losses + wins
    floor_m = resolution_floor(alpha)
    p = exact_upper_tail(m, losses) if m > 0 else None
    kc = critical_k(m, alpha) if m > 0 else None
    return {
        "n_pairs": len(scored),
        "n_selective_worse": losses,
        "n_selective_better": wins,
        "n_ties": ties,
        "m_discordant": m,
        "resolution_floor_m": floor_m,
        "DESIGN_COULD_HAVE_REJECTED": m >= floor_m,
        "k_critical_at_alpha": kc,
        "p_one_sided_exact": (f"{p.numerator}/{p.denominator}" if p is not None else None),
        "p_one_sided_float": (float(p) if p is not None else None),
        "alpha_exact": f"{alpha.numerator}/{alpha.denominator}",
        "alpha_float": float(alpha),
        "CROSSES_THRESHOLD": bool(m >= floor_m and p is not None and p <= alpha),
        "net_theta_hat": ((losses - wins) / len(scored)) if scored else None,
    }


# --------------------------------------------------------------------------- integrity


def integrity_checks(records):
    """Preregistration section 5, I2..I6. Campaign-level only: never drops a pair."""
    fails = []
    seen = set()
    for r in records:
        idx = r.get("index", "<missing index>")
        for f in REQUIRED_FIELDS:                                              # I2
            if f not in r:
                fails.append({"check": "I2_SCHEMA", "index": idx, "detail": f"missing field {f}"})
        if any(f not in r for f in REQUIRED_FIELDS):
            continue
        if idx in seen:                                                        # I6
            fails.append({"check": "I6_DUPLICATE_INDEX", "index": idx, "detail": "index repeated"})
        seen.add(idx)
        for arm in ("SELECTIVE", "SHAM"):
            term = r[arm + "_termination"]
            if term not in ALLOWED_TERMINATIONS:                               # I3
                fails.append({"check": "I3_UNKNOWN_TERMINATION", "index": idx,
                              "detail": f"{arm}_termination = {term!r}"})
            d, e = r[arm + "_duration"], r[arm + "_exposure"]
            if not isinstance(d, int) or not isinstance(e, int) or isinstance(d, bool):
                fails.append({"check": "I4_NOT_AN_INTEGER", "index": idx,
                              "detail": f"{arm} duration/exposure must be integers"})
                continue
            if d < 0 or e < 0:                                                 # I4
                fails.append({"check": "I4_NEGATIVE", "index": idx,
                              "detail": f"{arm} duration={d} exposure={e}"})
            elif e < d + 1:                                                    # I5
                # differential invariant derived from the classifier, not from the data:
                # n_rows_in_interval == duration + 1 (e3_b line 236) and every row adds
                # at least 1 to the exposure (lines 196, 222-223), so exposure >= duration+1.
                fails.append({"check": "I5_EXPOSURE_INVARIANT", "index": idx,
                              "detail": f"{arm}: exposure {e} < duration+1 {d + 1}"})
    return fails


# --------------------------------------------------------------------------- descriptive


def descriptive(records):
    """Secondary analyses S2, S3, S4. Reported, never tested, never confirmatory."""
    by_string = {arm: {} for arm in ("SELECTIVE", "SHAM")}
    by_cause = {arm: {} for arm in ("SELECTIVE", "SHAM")}
    for r in records:
        for arm in ("SELECTIVE", "SHAM"):
            t = r[arm + "_termination"]
            by_string[arm][t] = by_string[arm].get(t, 0) + 1
            c = TERMINATION_TO_CAUSE[t]
            by_cause[arm][c] = by_cause[arm].get(c, 0) + 1
    scored = score_pairs(records, "duration")
    return {
        "S2_termination_string_by_arm": by_string,
        "S3_cause_by_arm": by_cause,
        "S4_pairs_decided_by_rank_alone": sum(1 for s in scored if s["rank_decided"]),
        "S4_pairs_decided_by_the_duration_tiebreak":
            sum(1 for s in scored if not s["rank_decided"] and s["W"] != 0),
        "S4_pairs_fully_tied": sum(1 for s in scored if s["W"] == 0),
        "NOTE": "S2, S3 and S4 are descriptive. They cannot create or cancel the primary "
                "conclusion. In particular the split between OUT_OF_RANGE and "
                "NO_COMPONENT_AT_THE_NEXT_STEP inside S2 is arm-dependent by construction "
                "(preregistration 2.3) and must not be read as two causes.",
    }


# --------------------------------------------------------------------------- the decision


def decide(records):
    """The full frozen decision. Returns the result document."""
    fails = integrity_checks(records)
    if fails:
        return {
            "TERMINAL": "NON_CONCLUANT",
            "REASON": "TECHNICAL_INVALIDITY",
            "INTEGRITY_FAILURES": fails,
            "PRIMARY": None,
            "CLAIM": "Aucune revendication dans aucune direction.",
        }

    scored = score_pairs(records, "duration")
    primary = sign_test(scored)

    if not primary["DESIGN_COULD_HAVE_REJECTED"]:
        terminal, reason = "NON_CONCLUANT", "BELOW_THE_RESOLUTION_FLOOR"
        claim = ("Le design ne pouvait pas franchir son seuil avec ce nombre de paires "
                 "discordantes. Aucune revendication dans aucune direction.")
    elif primary["CROSSES_THRESHOLD"]:
        terminal, reason = "CONFIRMATOIRE", "THRESHOLD_CROSSED_IN_THE_PREREGISTERED_DIRECTION"
        claim = ("Sur ces 41 paires appariees, l'issue de l'intervalle d'identite de la fille "
                 "verrouillee, mesuree par le composite ordonne arm-symetrique, est "
                 "significativement pire dans le bras SELECTIVE que dans le bras SHAM, au seuil "
                 "unilateral exact de 0,025. Rien de plus.")
    else:
        terminal, reason = "NEGATIF", "THRESHOLD_NOT_CROSSED_AT_ADEQUATE_RESOLUTION"
        claim = ("Un critere gele a ete execute et n'a pas ete franchi, a une resolution "
                 "demontree suffisante pour qu'il put l'etre. Aucune revendication "
                 "d'equivalence ni d'absence d'effet.")

    secondary = sign_test(score_pairs(records, "exposure"))
    secondary["NOTE"] = "S1, secondaire, NON confirmatoire."

    return {
        "TERMINAL": terminal,
        "REASON": reason,
        "CLAIM": claim,
        "INTEGRITY_FAILURES": [],
        "PRIMARY": primary,
        "S1_exposure_tiebreak": secondary,
        "DESCRIPTIVE": descriptive(records),
        "PER_PAIR_SCORES": scored,
    }


def ledger_block():
    return {
        "REPRODUCTION_STATUS": "NOT_TESTED",
        "HEREDITY_STATUS": "NOT_TESTED",
        "H3_STATUS": "NOT_TESTED",
        "AUTONOMOUS_COHESION_STATUS": "NOT_ESTABLISHED",
        "ARCHITECTURE_CHANGE_NECESSITY": "NOT_ESTABLISHED",
        "WHAT_THIS_TEST_DOES_NOT_SAY": [
            "rien sur une capacite de la fille verrouillee",
            "rien sur un mecanisme",
            "rien sur les hasards cause-specifiques par canal, non identifiables ici",
            "rien sur la duree en tant que grandeur",
            "rien hors de ce jeu de parametres gele",
            "rien sur le bras DISPLACED",
        ],
    }


# --------------------------------------------------------------------------- synthetic data
# Everything below fabricates its own data. No real dataset is ever touched here.

_STRINGS_RANK0 = ("OUT_OF_RANGE", "NO_COMPONENT_AT_THE_NEXT_STEP")
_STRINGS_RANK1 = ("SPLIT_OR_TIE", "MERGE")


def _mk(index, sel_term, sel_dur, sham_term, sham_dur):
    """One synthetic record honouring the invariant exposure >= duration + 1 (I5)."""
    rec = {"index": index, "t_m": 1000 + index}
    for arm, term, dur in (("SELECTIVE", sel_term, sel_dur), ("SHAM", sham_term, sham_dur)):
        rec[arm + "_termination"] = term
        rec[arm + "_duration"] = int(dur)
        rec[arm + "_exposure"] = int(dur) + 1 + 3 * int(dur)      # any value >= duration+1
    for f in ("log_duration_difference", "log_exposure_difference"):
        rec[f] = 0.0                                              # unused by this estimand
    return rec


def synth_alternative(rng, n=N_PAIRS_REQUIRED, p_worse=0.80):
    """C1: a generating rule KNOWN to permit crossing. SELECTIVE is systematically worse."""
    recs = []
    for i in range(n):
        sham_term = rng.choice(_STRINGS_RANK1)
        sham_dur = rng.randint(120, 400)
        if rng.random() < p_worse:
            sel_term = rng.choice(_STRINGS_RANK0)                  # rank 0 beats rank 1: worse
            sel_dur = rng.randint(0, 60)
        else:
            sel_term = rng.choice(_STRINGS_RANK1)
            sel_dur = sham_dur + rng.randint(1, 80)                # strictly better
        recs.append(_mk(i, sel_term, sel_dur, sham_term, sham_dur))
    return recs


def synth_exchangeable(rng, n=N_PAIRS_REQUIRED):
    """A dataset drawn so the two arms are exchangeable: identical law, drawn independently."""
    def draw():
        if rng.random() < 0.45:
            return rng.choice(_STRINGS_RANK0), rng.randint(0, 250)
        return rng.choice(_STRINGS_RANK1), rng.randint(0, 250)
    recs = []
    for i in range(n):
        st, sd = draw()
        ht, hd = draw()
        recs.append(_mk(i, st, sd, ht, hd))
    return recs


def permute_arm_labels(recs, rng):
    """The null construction: swap the two arms of each pair independently with prob 1/2."""
    out = []
    for r in recs:
        q = dict(r)
        if rng.random() < 0.5:
            for f in ("termination", "duration", "exposure"):
                q["SELECTIVE_" + f], q["SHAM_" + f] = r["SHAM_" + f], r["SELECTIVE_" + f]
        out.append(q)
    return out


def apply_merge_artifact(recs, rng, degrade_rank=False):
    """C3: remove the MERGE channel from the SELECTIVE arm ONLY, as the frozen classifier does
    when the locked daughter is the world's only component (e3_b lines 116, 125, 219).

    The interval that would have ended by MERGE instead continues and ends later.
    degrade_rank=False: it ends later at rank 1 -> pure duration inflation, the artifact that
                        invalidates a raw duration or log-duration contrast.
    degrade_rank=True : the later channel may be rank 0 -> reported as a diagnostic only,
                        since preregistration 3.4 places this inside the TOTAL effect.
    """
    out = []
    for r in recs:
        q = dict(r)
        if q["SELECTIVE_termination"] == "MERGE":
            extra = rng.randint(1, 120)                          # it terminates strictly later
            newdur = q["SELECTIVE_duration"] + extra
            if degrade_rank and rng.random() < 0.5:
                q["SELECTIVE_termination"] = rng.choice(_STRINGS_RANK0)
            else:
                q["SELECTIVE_termination"] = "SPLIT_OR_TIE"
            q["SELECTIVE_duration"] = newdur
            q["SELECTIVE_exposure"] = newdur + 1 + 3 * newdur
        out.append(q)
    return out


def apply_arm_dependent_renaming(recs):
    """C5: the artifact of preregistration 2.3. In the SELECTIVE arm ONLY, every OUT_OF_RANGE
    becomes NO_COMPONENT_AT_THE_NEXT_STEP — the same physical event relabelled because the
    parent's Y is gone and the world is empty. The decision must not move at all."""
    out = []
    for r in recs:
        q = dict(r)
        if q["SELECTIVE_termination"] == "OUT_OF_RANGE":
            q["SELECTIVE_termination"] = "NO_COMPONENT_AT_THE_NEXT_STEP"
        out.append(q)
    return out


def _naive_string_statistic(recs):
    """A deliberately naive statistic that treats the four strings as four causes: the count of
    pairs where SELECTIVE ends in NO_COMPONENT_AT_THE_NEXT_STEP and SHAM does not. Used only to
    MEASURE the artifact that the frozen mapping avoids."""
    return sum(1 for r in recs
               if r["SELECTIVE_termination"] == "NO_COMPONENT_AT_THE_NEXT_STEP"
               and r["SHAM_termination"] != "NO_COMPONENT_AT_THE_NEXT_STEP")


# --------------------------------------------------------------------------- capability test


def capability():
    checks = []

    # ---- C1: the statistic CAN cross its threshold under a rule known to permit it
    rng = random.Random(20260904)
    alt = synth_alternative(rng)
    d1 = decide(alt)
    c1 = {
        "id": "C1_CAN_CROSS",
        "what": "Sous une regle de generation connue pour le permettre, la statistique doit "
                "franchir son seuil et rendre CONFIRMATOIRE.",
        "n_pairs": len(alt),
        "terminal": d1["TERMINAL"],
        "m_discordant": d1["PRIMARY"]["m_discordant"],
        "k_selective_worse": d1["PRIMARY"]["n_selective_worse"],
        "k_critical": d1["PRIMARY"]["k_critical_at_alpha"],
        "p_one_sided": d1["PRIMARY"]["p_one_sided_float"],
        "PASS": d1["TERMINAL"] == "CONFIRMATOIRE",
    }
    checks.append(c1)

    # ---- C2: it does NOT cross on null data built by permuting arm labels
    rng = random.Random(777001)
    base = synth_exchangeable(rng)
    one_null = permute_arm_labels(base, random.Random(4242))
    d2 = decide(one_null)
    n_rep, n_cross, m_seen = 2000, 0, []
    rp = random.Random(99887766)
    for _ in range(n_rep):
        rec = permute_arm_labels(base, rp)
        res = decide(rec)
        m_seen.append(res["PRIMARY"]["m_discordant"])
        if res["TERMINAL"] == "CONFIRMATOIRE":
            n_cross += 1
    rate = n_cross / n_rep
    c2 = {
        "id": "C2_DOES_NOT_CROSS_UNDER_LABEL_PERMUTATION",
        "what": "Un replicat nul graine doit etre non confirmatoire, et sur 2000 replicats "
                "permutes le taux empirique de franchissement doit rester au voisinage de alpha.",
        "seeded_replicate_terminal": d2["TERMINAL"],
        "seeded_replicate_p": d2["PRIMARY"]["p_one_sided_float"],
        "n_replicates": n_rep,
        "n_crossings": n_cross,
        "empirical_type_I_rate": rate,
        "acceptance_bound": 0.04,
        "alpha": float(ALPHA),
        "min_m_over_replicates": min(m_seen),
        "PASS": d2["TERMINAL"] != "CONFIRMATOIRE" and rate <= 0.04,
    }
    checks.append(c2)

    # ---- C3: adversarial. The MERGE duration-inflation artifact must not manufacture a result
    rng = random.Random(5150)
    exch = synth_exchangeable(rng)
    before = decide(exch)
    art = apply_merge_artifact(exch, random.Random(31337), degrade_rank=False)
    after = decide(art)
    diag = decide(apply_merge_artifact(exch, random.Random(31337), degrade_rank=True))
    n_merge = sum(1 for r in exch if r["SELECTIVE_termination"] == "MERGE")
    c3 = {
        "id": "C3_ADVERSARIAL_MERGE_DURATION_INFLATION",
        "what": "On retire le canal MERGE du seul bras SELECTIVE, en le convertissant en une "
                "terminaison de rang 1 plus tardive. Le programme ne doit PAS rendre "
                "CONFIRMATOIRE dans la direction pre-declaree.",
        "n_selective_MERGE_records_converted": n_merge,
        "terminal_before_the_artifact": before["TERMINAL"],
        "terminal_after_the_artifact": after["TERMINAL"],
        "k_selective_worse_before": before["PRIMARY"]["n_selective_worse"],
        "k_selective_worse_after": after["PRIMARY"]["n_selective_worse"],
        "p_after": after["PRIMARY"]["p_one_sided_float"],
        "DIAGNOSTIC_rank_degrading_variant_terminal": diag["TERMINAL"],
        "DIAGNOSTIC_NOTE": "La variante ou le canal ulterieur peut etre de rang 0 est rapportee "
                           "sans assertion: la preregistration 3.4 la place dans l'effet TOTAL, "
                           "non dans un biais.",
        "PASS": after["TERMINAL"] != "CONFIRMATOIRE",
    }
    checks.append(c3)

    # ---- C4: differential arithmetic. Exact tail against brute-force enumeration.
    mism = []
    for m in range(0, 15):
        for k in range(0, m + 1):
            brute = Fraction(sum(1 for combo in itertools.product((0, 1), repeat=m)
                                 if sum(combo) >= k), 1 << m)
            if brute != exact_upper_tail(m, k):
                mism.append({"m": m, "k": k})
    floor_m = resolution_floor()
    c4 = {
        "id": "C4_EXACT_ARITHMETIC_DIFFERENTIAL",
        "what": "La queue binomiale exacte est recoupee contre une enumeration exhaustive des "
                "2^m sequences de signes. Deux chemins independants vers la meme valeur.",
        "m_range_enumerated": "0..14",
        "n_mismatches": len(mism),
        "resolution_floor_m": floor_m,
        "two_pow_minus_floor": float(Fraction(1, 1 << floor_m)),
        "two_pow_minus_floor_minus_one": float(Fraction(1, 1 << (floor_m - 1))),
        "alpha": float(ALPHA),
        "PASS": (not mism
                 and Fraction(1, 1 << floor_m) <= ALPHA
                 and Fraction(1, 1 << (floor_m - 1)) > ALPHA),
    }
    checks.append(c4)

    # ---- C5: adversarial. Invariance to the arm-dependent renaming of preregistration 2.3
    rng = random.Random(8080808)
    exch2 = synth_exchangeable(rng)
    d_before = decide(exch2)
    d_after = decide(apply_arm_dependent_renaming(exch2))
    fields = ("TERMINAL",)
    same_terminal = all(d_before[f] == d_after[f] for f in fields)
    pf = ("m_discordant", "n_selective_worse", "n_selective_better", "n_ties",
          "p_one_sided_exact", "CROSSES_THRESHOLD")
    same_primary = all(d_before["PRIMARY"][f] == d_after["PRIMARY"][f] for f in pf)
    naive_before = _naive_string_statistic(exch2)
    naive_after = _naive_string_statistic(apply_arm_dependent_renaming(exch2))
    c5 = {
        "id": "C5_ADVERSARIAL_ARM_DEPENDENT_RENAMING",
        "what": "Dans le seul bras SELECTIVE, chaque OUT_OF_RANGE devient "
                "NO_COMPONENT_AT_THE_NEXT_STEP. La decision doit etre identique bit a bit.",
        "terminal_before": d_before["TERMINAL"],
        "terminal_after": d_after["TERMINAL"],
        "primary_identical": same_primary,
        "p_before": d_before["PRIMARY"]["p_one_sided_exact"],
        "p_after": d_after["PRIMARY"]["p_one_sided_exact"],
        "naive_string_statistic_before": naive_before,
        "naive_string_statistic_after": naive_after,
        "MEASURED_ARTIFACT_AVOIDED": naive_after - naive_before,
        "NOTE": "La statistique naive fondee sur les chaines se deplace de "
                f"{naive_after - naive_before} paires sous un pur renommage; la statistique "
                "gelee ne bouge pas.",
        "PASS": same_terminal and same_primary,
    }
    checks.append(c5)

    all_pass = all(c["PASS"] for c in checks)
    return {
        "MISSION": "CCRA01",
        "SECTION": "capability test",
        "SPEC_VERSION": SPEC_VERSION,
        "REAL_DATA_READ": False,
        "DATA_SOURCE": "synthetic, fabricated inside this file by random.Random with fixed seeds",
        "ALPHA": float(ALPHA),
        "CHECKS": checks,
        "N_CHECKS": len(checks),
        "N_PASSED": sum(1 for c in checks if c["PASS"]),
        "CAPABILITY": "PASS" if all_pass else "FAIL",
        "LEGACY_NOTE": "Une condition dont on n'a jamais montre qu'elle peut se declencher n'est "
                       "pas un test. C1 montre qu'elle peut; C2 montre qu'elle ne se declenche "
                       "pas a tort; C3 et C5 montrent qu'elle resiste aux deux artefacts nommes "
                       "dans la preregistration; C4 verifie l'arithmetique par un second chemin.",
    }


# --------------------------------------------------------------------------- run


def load_records(path):
    with open(path) as fh:
        doc = json.load(fh)
    if isinstance(doc, dict):
        if "PER_PAIR" not in doc:
            raise SystemExit(json.dumps(
                {"MISSION": "CCRA01", "TERMINAL": "NON_CONCLUANT",
                 "REASON": "INPUT_HAS_NO_PER_PAIR_FIELD"}, indent=1))
        recs = doc["PER_PAIR"]
    elif isinstance(doc, list):
        recs = doc
    else:
        raise SystemExit(json.dumps(
            {"MISSION": "CCRA01", "TERMINAL": "NON_CONCLUANT",
             "REASON": "INPUT_IS_NEITHER_AN_OBJECT_NOR_A_LIST"}, indent=1))
    return recs


def run(path):
    recs = load_records(path)
    if len(recs) != N_PAIRS_REQUIRED:                                          # I1: hard refusal
        print(json.dumps({
            "MISSION": "CCRA01", "SECTION": "run",
            "TERMINAL": "REFUSED_TO_RUN",
            "REASON": "I1_WRONG_PAIR_COUNT",
            "n_pairs_found": len(recs),
            "n_pairs_required": N_PAIRS_REQUIRED,
            "DETAIL": "La regle de retention gelee retient les 41 paires et n'en ecarte aucune. "
                      "Un fichier qui n'en contient pas exactement 41 n'est pas le jeu gele.",
        }, indent=1))
        sys.exit(2)

    result = decide(recs)
    doc = {
        "MISSION": "CCRA01",
        "SECTION": "frozen run",
        "SPEC_VERSION": SPEC_VERSION,
        "PREREGISTRATION": "CCRA01_PREREGISTRATION.md",
        "SIGN_CONVENTION": SIGN_CONVENTION,
        "ESTIMAND": "theta = P(SELECTIVE strictement pire) - P(SELECTIVE strictement meilleur), "
                    "sur le composite ordonne lexicographique (rang, duree). Effet TOTAL.",
        "PREREGISTERED_DIRECTION": "theta > 0 : SELECTIVE est plus souvent la pire des deux.",
        "TEST": "test des signes apparie, exact, unilateral, alpha = 1/40",
        "MAPPING": TERMINATION_TO_CAUSE,
        "CAUSE_RANK_WORST_TO_BEST": CAUSE_RANK,
        "RETENTION_RULE": "les 41 paires entrent toutes; aucune exclusion conditionnelle a une "
                          "variable realisee apres le traitement",
    }
    doc.update(result)
    doc.update(ledger_block())
    print(json.dumps(doc, indent=1))
    sys.exit(0 if result["TERMINAL"] != "NON_CONCLUANT" else 1)


def main():
    ap = argparse.ArgumentParser(description="CCRA01 frozen analysis. Writes no file.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--capability", action="store_true",
                   help="adversarial capability search on synthetic data only")
    g.add_argument("--run", metavar="FILE.json",
                   help="the frozen analysis of the real 41-pair dataset")
    a = ap.parse_args()
    if a.capability:
        doc = capability()
        print(json.dumps(doc, indent=1))
        sys.exit(0 if doc["CAPABILITY"] == "PASS" else 1)
    run(a.run)


if __name__ == "__main__":
    main()
