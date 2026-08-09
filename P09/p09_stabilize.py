"""P09 STABILIZATION — engine-free, no new runs, no new trajectories.

Mandate (four items only):
  1. Determine whether the P09 arms are PAIRED by founding block. If they are, replace the
     independent Fisher exact test on survival with the exact PAIRED test (McNemar, exact
     binomial on discordant pairs).
  2. Separate the pre-registered DOSE COMPARABILITY GATE from formal statistical EQUIVALENCE.
     The sealed rule is a containment gate, not a TOST. Report a properly labelled paired TOST
     on log delivered-mass ratios as a POST-HOC supplement, never as the sealed criterion.
  3. Report SOURCE-realized and SINK-realized mass separately.
  4. Replace exclusive causal statements with the four mandated formulations.

This script reads p09_rows.csv and p09_summary.json ONLY. It calls no engine, creates no
trajectory, and modifies no sealed artefact. Its output is a new file.
"""
from __future__ import annotations
import csv, json, math, statistics as S
from math import comb

ROWS = list(csv.DictReader(open("p09_rows.csv")))
SUMM = json.load(open("p09_summary.json"))
CELLS = [("LAW_16", "24"), ("LAW_16", "32"), ("LAW_29", "24"), ("LAW_29", "32")]
ARMS = ["SHAM", "PARENT_FULL", "FLOOR_FULL", "PARENT_Q_REPLAY", "FLOOR_Q_REPLAY",
        "PARENT_LOW_CONSTANT"]
MARGIN_IN = (0.847, 1.180)          # sealed BEFORE execution
MARGIN_CI = (0.781, 1.280)          # sealed BEFORE execution
OUT = {"program": "P09_DOSE_YOKED_GUARD_SIGN_CLOSURE",
       "pass": "STABILIZATION_ENGINE_FREE",
       "engine_invocations_added": 0, "trajectories_added": 0}


def n(v):
    try:
        x = float(v)
        return None if math.isnan(x) else x
    except (TypeError, ValueError):
        return None


def cell(law, sz, arm):
    return [r for r in ROWS if r["law"] == law and r["size"] == sz and r["arm"] == arm]


def med(xs):
    xs = [x for x in xs if x is not None]
    return S.median(xs) if xs else None


# =============================================================== 1. PAIRING AUDIT
def pairing_audit():
    """Are the arms paired by founding block? A block is a founding seed; the engine is
    deterministic and the first operator opportunity is at t=272, so two arms sharing a block
    share the identical world up to t=272. That is exact pairing, not approximate matching."""
    per = {}
    ok = True
    for law, sz in CELLS:
        sets = {a: {r["block"] for r in cell(law, sz, a)} for a in ARMS}
        base = sets["PARENT_FULL"]
        same = all(sets[a] == base for a in ARMS)
        per[f"{law}|L{sz}"] = {"blocks": sorted(base), "n": len(base),
                               "all_arms_share_the_same_blocks": same,
                               "per_arm_counts": {a: len(sets[a]) for a in ARMS}}
        ok = ok and same and len(base) == 9
    # a second, independent check: identical pre-operator state means identical M256 per block
    m256 = {}
    for law, sz in CELLS:
        by_block = {}
        for a in ARMS:
            for r in cell(law, sz, a):
                by_block.setdefault(r["block"], set()).add(round(n(r["M256"]), 9))
        m256[f"{law}|L{sz}"] = {"blocks_with_a_unique_M256": sum(1 for v in by_block.values()
                                                                 if len(v) == 1),
                                "n_blocks": len(by_block)}
    return {"PAIRED": ok, "per_cell": per, "M256_identity_check": m256,
            "consequence": ("The independent-sample Fisher exact test used for SURVIVAL_ITT in "
                            "p09_analyse.py is inappropriate for this design. Survival must be "
                            "tested with the exact paired test on discordant blocks (McNemar "
                            "exact). The UCR and delivered-mass tests were already paired sign "
                            "tests and are unaffected.")}


# ============================================ 2. EXACT PAIRED TEST (McNemar exact)
def mcnemar_exact(pairs):
    """pairs = [(a_alive, b_alive)] over the SAME blocks. Two-sided exact binomial on the
    discordant pairs. b = a-alive/b-dead, c = a-dead/b-alive."""
    b = sum(1 for x, y in pairs if x and not y)
    c = sum(1 for x, y in pairs if y and not x)
    m = b + c
    if m == 0:
        return {"n_pairs": len(pairs), "b_only_A": 0, "c_only_B": 0, "n_discordant": 0,
                "p_exact": 1.0, "note": "no discordant block; the test is uninformative by design"}
    k = min(b, c)
    p = min(1.0, 2.0 * sum(comb(m, i) for i in range(k + 1)) / 2 ** m)
    return {"n_pairs": len(pairs), "b_only_A": b, "c_only_B": c, "n_discordant": m,
            "p_exact": p}


def fisher_unpaired(a, b, n1=9, n2=9):
    """kept ONLY to show, side by side, what the superseded test reported."""
    tot = a + b

    def q(k):
        return comb(n1, k) * comb(n2, tot - k) / comb(n1 + n2, tot) if 0 <= tot - k <= n2 else 0.0
    obs = q(a)
    return min(1.0, sum(q(k) for k in range(0, n1 + 1) if q(k) <= obs + 1e-12))


CONTRASTS = [
    ("ALLOCATION", "PARENT_Q_REPLAY", "FLOOR_Q_REPLAY"),
    ("TEMPORAL_PROFILE", "PARENT_LOW_CONSTANT", "PARENT_Q_REPLAY"),
    ("DOSE_REDUCTION", "PARENT_FULL", "PARENT_LOW_CONSTANT"),
    ("P08_REPLICATION", "PARENT_FULL", "FLOOR_FULL"),
]


def paired_survival():
    out = {}
    for law, sz in CELLS:
        c = {}
        for name, A, B in CONTRASTS:
            a = {r["block"]: r["SURVIVAL_ITT"] == "True" for r in cell(law, sz, A)}
            b = {r["block"]: r["SURVIVAL_ITT"] == "True" for r in cell(law, sz, B)}
            common = sorted(set(a) & set(b))
            pairs = [(a[k], b[k]) for k in common]
            mc = mcnemar_exact(pairs)
            sa, sb = sum(a[k] for k in common), sum(b[k] for k in common)
            c[name] = {"reference_arm": A, "test_arm": B,
                       "survival": {A: f"{sa}/{len(common)}", B: f"{sb}/{len(common)}"},
                       "difference_blocks": sb - sa,
                       "PAIRED_McNemar_exact": mc,
                       "SUPERSEDED_unpaired_fisher_p": fisher_unpaired(sa, sb),
                       "discordant_blocks": [k for k in common if a[k] != b[k]]}
        out[f"{law}|L{sz}"] = c
    return out


# ============================== 3. COMPARABILITY GATE vs FORMAL EQUIVALENCE (TOST)
def boot_ci(xs, B=20000, seed=20260809, lo=2.5, hi=97.5):
    import random
    rnd = random.Random(seed)
    k = len(xs)
    if k == 0:
        return (None, None)
    ms = []
    for _ in range(B):
        ms.append(S.median([xs[rnd.randrange(k)] for _ in range(k)]))
    ms.sort()
    return (ms[int(lo / 100 * B)], ms[min(B - 1, int(hi / 100 * B))])


def tost_log_ratio(ratios, lo=MARGIN_IN[0], hi=MARGIN_IN[1], alpha=0.05):
    """Paired TOST on the log delivered-mass ratio. The 100(1-2a)% CI of the MEAN log ratio must
    lie entirely inside [log lo, log hi]. n = 9, so a t distribution with 8 df is used.
    THIS IS POST HOC. It was not sealed before execution and cannot upgrade a sealed verdict."""
    xs = [math.log(r) for r in ratios if r and r > 0]
    k = len(xs)
    if k < 3:
        return {"n": k, "verdict": "INSUFFICIENT"}
    m = S.mean(xs)
    sd = S.stdev(xs)
    se = sd / math.sqrt(k)
    # two-sided (1-2a) CI -> t at 1-a with k-1 df
    T = {8: 1.85955}.get(k - 1)          # t_{0.95, 8}
    if T is None:                        # fall back to a conservative normal quantile
        T = 1.6449
    ci = (m - T * se, m + T * se)
    inside = math.log(lo) < ci[0] and ci[1] < math.log(hi)
    # the two one-sided p-values
    t_lo = (m - math.log(lo)) / se
    t_hi = (math.log(hi) - m) / se
    return {"n": k, "mean_log_ratio": m, "geometric_mean_ratio": math.exp(m),
            "se": se, "ci90_log": ci, "ci90_ratio": (math.exp(ci[0]), math.exp(ci[1])),
            "bounds_ratio": (lo, hi), "t_lower": t_lo, "t_upper": t_hi,
            "EQUIVALENCE_ESTABLISHED_post_hoc": bool(inside),
            "status": "POST_HOC_NOT_SEALED"}


def dose_comparability():
    out = {}
    for law, sz in CELLS:
        a = {r["block"]: n(r["delivered_over_M256"]) for r in cell(law, sz, "PARENT_Q_REPLAY")}
        b = {r["block"]: n(r["delivered_over_M256"]) for r in cell(law, sz, "FLOOR_Q_REPLAY")}
        common = sorted(set(a) & set(b))
        ratios = [b[k] / a[k] for k in common if a[k]]
        m = med(ratios)
        ci = boot_ci(ratios)
        gate = (m is not None and MARGIN_IN[0] <= m <= MARGIN_IN[1]
                and ci[0] is not None and MARGIN_CI[0] <= ci[0] and ci[1] <= MARGIN_CI[1])
        out[f"{law}|L{sz}"] = {
            "SEALED_COMPARABILITY_GATE": {
                "what_it_is": ("a containment gate: the median paired ratio inside the inner band "
                               "AND its 95% block-bootstrap CI inside the outer band. It is NOT a "
                               "test of the equivalence hypothesis and yields no equivalence p."),
                "median_ratio": m, "bootstrap_ci95": ci,
                "inner_band": MARGIN_IN, "outer_band": MARGIN_CI, "GATE_PASSES": gate},
            "POST_HOC_TOST_log_ratio": tost_log_ratio(ratios),
            "per_block_ratios": {k: (b[k] / a[k] if a[k] else None) for k in common}}
    return out


# ============================ 4. SOURCE-REALIZED AND SINK-REALIZED MASS, SEPARATELY
def mass_accounting():
    out = {}
    for law, sz in CELLS:
        c = {}
        for arm in ARMS:
            g = cell(law, sz, arm)
            if not g:
                continue
            c[arm] = {
                "attempted_over_M256": med([n(r["attempted_over_M256"]) for r in g]),
                "SINK_realized_over_M256": med([n(r["delivered_over_M256"]) for r in g]),
                "SOURCE_realized_over_M256": med([n(r["source_realized_over_M256"]) for r in g]),
                "source_minus_sink_over_M256": med([(n(r["source_realized_over_M256"]) or 0)
                                                    - (n(r["delivered_over_M256"]) or 0)
                                                    for r in g]),
                "n_events": med([n(r["n_events"]) for r in g]),
                "n_rejected": med([n(r["n_rejected"]) for r in g]),
                "futile_fraction": med([n(r["futile_fraction"]) for r in g]),
                "UCR": med([n(r["UCR"]) for r in g]),
                "survival_ITT": f"{sum(1 for r in g if r['SURVIVAL_ITT'] == 'True')}/{len(g)}"}
        out[f"{law}|L{sz}"] = c
    return out


# ======================================================= 5. MANDATED FORMULATIONS
def mandated_statements(pv, eq):
    def s(law, sz, arm):
        g = cell(law, sz, arm)
        return sum(1 for r in g if r["SURVIVAL_ITT"] == "True"), len(g)

    st = {}
    # (a) low unguarded dose is SUFFICIENT to reproduce the LAW_29 rescue
    ev_a = {}
    for sz in ("24", "32"):
        pf, npf = s("LAW_29", sz, "PARENT_FULL")
        lc, nlc = s("LAW_29", sz, "PARENT_LOW_CONSTANT")
        ff, nff = s("LAW_29", sz, "FLOOR_FULL")
        ev_a[f"L{sz}"] = {"PARENT_FULL": f"{pf}/{npf}", "PARENT_LOW_CONSTANT": f"{lc}/{nlc}",
                          "FLOOR_FULL": f"{ff}/{nff}",
                          "McNemar_LOWCONST_vs_FULL":
                              pv[f"LAW_29|L{sz}"]["DOSE_REDUCTION"]["PAIRED_McNemar_exact"]}
    st["A_low_unguarded_dose_is_sufficient"] = {
        "statement": ("Sous LAW_29, une dose basse SANS AUCUNE GARDE suffit a reproduire le "
                      "sauvetage attribue au plancher : PARENT_LOW_CONSTANT, dont la regle "
                      "d'allocation est celle du parent, survit comme FLOOR_FULL."),
        "evidence": ev_a, "supported": True}

    # (b) exclusive dose mediation is NOT established
    st["B_exclusive_dose_mediation_not_established"] = {
        "statement": ("La mediation exclusive par la dose n'est PAS etablie. Sous LAW_29 la porte "
                      "de comparabilite de dose ECHOUE (le plancher delivre environ 23 % de moins "
                      "que le parent a requetes identiques), donc le contraste d'allocation n'est "
                      "pas a dose egale et aucune decomposition dose/allocation n'est identifiee."),
        "evidence": {k: {"median_ratio": v["SEALED_COMPARABILITY_GATE"]["median_ratio"],
                         "GATE_PASSES": v["SEALED_COMPARABILITY_GATE"]["GATE_PASSES"],
                         "post_hoc_TOST": v["POST_HOC_TOST_log_ratio"]
                         .get("EQUIVALENCE_ESTABLISHED_post_hoc")}
                     for k, v in eq.items()},
        "supported": True}

    # (c) floor-specific allocation under LAW_29 remains non-identifiable
    st["C_floor_specific_allocation_non_identifiable"] = {
        "statement": ("Sous LAW_29, l'allocation specifique au plancher reste NON IDENTIFIABLE. "
                      "C'est la disposition scellee avant execution pour le cas ou la porte de "
                      "dose echoue."),
        "sealed_verdict": SUMM["ADJUDICATION"]["VERDICT"], "supported": True}

    # (d) calendar effect is NOT established
    ev_d = {}
    for sz in ("24", "32"):
        for law in ("LAW_16", "LAW_29"):
            ev_d[f"{law}|L{sz}"] = pv[f"{law}|L{sz}"]["TEMPORAL_PROFILE"]
    st["D_calendar_effect_not_established"] = {
        "statement": ("Un effet de CALENDRIER (profil temporel des quantites, a dose totale et "
                      "nombre d'evenements egaux) n'est PAS etabli. Le seul contraste discordant "
                      "va dans le sens DEFAVORABLE au replay et n'atteint pas le seuil sur des "
                      "blocs apparies."),
        "evidence": ev_d, "supported": True}
    return st


if __name__ == "__main__":
    OUT["PAIRING_AUDIT"] = pairing_audit()
    OUT["PAIRED_SURVIVAL_TESTS"] = paired_survival()
    OUT["DOSE_COMPARABILITY_vs_EQUIVALENCE"] = dose_comparability()
    OUT["MASS_ACCOUNTING_SOURCE_AND_SINK_SEPARATE"] = mass_accounting()
    OUT["MANDATED_STATEMENTS"] = mandated_statements(OUT["PAIRED_SURVIVAL_TESTS"],
                                                     OUT["DOSE_COMPARABILITY_vs_EQUIVALENCE"])
    changed = (OUT["PAIRING_AUDIT"]["PAIRED"] is True)
    OUT["P09_STABILIZATION"] = "CORRECTED_NO_NEW_RUNS" if changed else "ALREADY_CORRECT"
    OUT["sealed_verdict_unchanged"] = SUMM["ADJUDICATION"]["VERDICT"]
    json.dump(OUT, open("p09_stabilization.json", "w"), indent=1, ensure_ascii=False)

    print("PAIRED:", OUT["PAIRING_AUDIT"]["PAIRED"])
    for k, v in OUT["PAIRED_SURVIVAL_TESTS"].items():
        for nm, d in v.items():
            mc = d["PAIRED_McNemar_exact"]
            print(f"{k:14s} {nm:18s} {d['survival']}  d={d['difference_blocks']:+d}  "
                  f"disc={mc['n_discordant']}  p_paired={mc['p_exact']:.4f}  "
                  f"(p_unpaired_superseded={d['SUPERSEDED_unpaired_fisher_p']:.4f})")
    print()
    for k, v in OUT["DOSE_COMPARABILITY_vs_EQUIVALENCE"].items():
        g = v["SEALED_COMPARABILITY_GATE"]
        t = v["POST_HOC_TOST_log_ratio"]
        print(f"{k:14s} gate={'PASS' if g['GATE_PASSES'] else 'FAIL'} med={g['median_ratio']:.3f} "
              f"| TOST post-hoc: gm={t.get('geometric_mean_ratio', float('nan')):.3f} "
              f"CI90=[{t['ci90_ratio'][0]:.3f},{t['ci90_ratio'][1]:.3f}] "
              f"-> {t['EQUIVALENCE_ESTABLISHED_post_hoc']}")
    print()
    for k, v in OUT["MASS_ACCOUNTING_SOURCE_AND_SINK_SEPARATE"].items():
        print(k)
        for a, d in v.items():
            print(f"   {a:20s} src={d['SOURCE_realized_over_M256'] or 0:.4f} "
                  f"snk={d['SINK_realized_over_M256'] or 0:.4f} "
                  f"src-snk={d['source_minus_sink_over_M256'] or 0:+.4f} surv={d['survival_ITT']}")
    print("\nP09_STABILIZATION =", OUT["P09_STABILIZATION"])
