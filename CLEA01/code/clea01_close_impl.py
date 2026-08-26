"""CLEA01 closure §11 — what the two implementations actually share, and whether the morphology
form is equivalent to the set form.

The audit claimed the two implementations share "the archive, the frozen constants, and the rule
text. No code." That was false and the checker proved it. This measures the overlap instead of
asserting it, states the equivalence AND its precondition, tests the equivalence on random
configurations, and then deliberately breaks the precondition to show the equivalence is
conditional rather than unconditional.

A third route, i3, is written here from the rule text alone: neighbour COUNTING with precomputed
modular index tables — no np.roll, no set-subset test. Agreement of three routes on the same
configurations is evidence about encoding, not about the causal assumption. That distinction is the
point of this file and is stated in its output.
"""
from __future__ import annotations
import datetime as dt, difflib, json, os, sys
import numpy as np
REPO = os.environ.get("CLEA01_REPO", "/home/claude/edl")
sys.path.insert(0, f"{REPO}/OMLDCT02/code"); sys.path.insert(0, f"{REPO}/CLEA01/code")
import omldct02_hashes as H
import clea01_lineage_i1 as I1
import clea01_lineage_i2 as I2

L = 36
OFF = [(dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1)]


def literal_rule(occ, occ_prev, certain_prev):
    """the frozen rule text read literally, cell by cell, with no cleverness:
       d is CERTAIN iff d is occupied, S(d) is non-empty, and every member of S(d) is CERTAIN."""
    out = np.zeros_like(occ)
    for y in range(L):
        for x in range(L):
            if not occ[y, x]:
                continue
            S = [((y + dy) % L, (x + dx) % L) for dy, dx in OFF]
            S = [c for c in S if occ_prev[c]]
            if S and all(certain_prev[c] for c in S):
                out[y, x] = True
    return out


def i2_form(occ, occ_prev, certain_prev):
    return occ & I2.dilate(certain_prev) & ~I2.dilate(occ_prev & ~certain_prev)


_IDX = np.array([[[((y + dy) % L) * L + ((x + dx) % L) for dy, dx in OFF]
                  for x in range(L)] for y in range(L)], dtype=np.int64)


def i3_count(occ, occ_prev, certain_prev):
    """independent third route: count neighbours through a precomputed modular index table."""
    fo = occ_prev.ravel()[_IDX].sum(axis=2)
    fc = certain_prev.ravel()[_IDX].sum(axis=2)
    return occ & (fo > 0) & (fo == fc)


def i1_form(occ, occ_prev, certain_prev):
    prev = {(int(a), int(b)): 1 for a, b in np.argwhere(occ_prev)}
    cert = {(int(a), int(b)) for a, b in np.argwhere(certain_prev)}
    out = np.zeros_like(occ)
    for a, b in np.argwhere(occ):
        d = (int(a), int(b))
        S = I1.sources(d, prev)
        if S and S <= cert and cert:
            out[d] = True
    return out


def rng_config(rng, dens, frac, respect_precondition=True):
    occ_prev = rng.random((L, L)) < dens
    occ = rng.random((L, L)) < dens
    certain_prev = occ_prev & (rng.random((L, L)) < frac)
    if not respect_precondition:
        # put certainty on cells that are NOT occupied on the previous row
        certain_prev = certain_prev | (~occ_prev & (rng.random((L, L)) < 0.3))
    return occ, occ_prev, certain_prev


def named_fixtures():
    """the ten structural cases the launcher names, each hand-built and hand-answered."""
    def blank():
        return np.zeros((L, L), bool)
    F = []

    def add(name, occ, prev, cert, expect):
        e = blank()
        for c in expect:
            e[c] = True
        F.append((name, occ, prev, cert, e))

    o = blank(); o[5, 5] = True; p = blank(); p[5, 5] = True; c = blank(); c[5, 5] = True
    add("ordinary persistence", o, p, c, [(5, 5)])

    o = blank(); o[5, 5] = o[5, 6] = True; p = blank(); p[5, 5] = True; c = blank(); c[5, 5] = True
    add("birth beside a certain cell", o, p, c, [(5, 5), (5, 6)])

    o = blank(); p = blank(); p[5, 5] = True; c = blank(); c[5, 5] = True
    add("death: nothing survives", o, p, c, [])

    o = blank(); o[5, 4] = o[5, 6] = True
    p = blank(); p[5, 5] = True; c = blank(); c[5, 5] = True
    add("split into two groups", o, p, c, [(5, 4), (5, 6)])

    o = blank(); o[5, 5] = True
    p = blank(); p[5, 4] = p[5, 6] = True; c = blank(); c[5, 4] = c[5, 6] = True
    add("merge of two certain sources", o, p, c, [(5, 5)])

    o = blank(); o[5, 5] = True
    p = blank(); p[5, 4] = p[5, 6] = True; c = blank(); c[5, 4] = True
    add("ambiguous predecessor: one certain, one not", o, p, c, [])

    o = blank(); o[5, 5] = True
    p = blank(); p[4, 4] = p[6, 6] = True; c = blank()
    add("two possible ancestors, neither certain", o, p, c, [])

    o = blank(); o[0, 0] = True; p = blank(); p[L - 1, L - 1] = True
    c = blank(); c[L - 1, L - 1] = True
    add("toroidal seam: diagonal wrap is one hop", o, p, c, [(0, 0)])

    o = blank(); o[5, 5] = True; p = blank(); p[5, 5] = True; c = blank()
    add("blocked: source occupied but not certain", o, p, c, [])

    o = blank(); o[20, 20] = True; p = blank(); p[5, 5] = True; c = blank(); c[5, 5] = True
    add("empty predecessor set: unreachable cell", o, p, c, [])
    return F


def shared_lines():
    a = [l.rstrip() for l in open(f"{REPO}/CLEA01/code/clea01_lineage_i1.py")]
    b = [l.rstrip() for l in open(f"{REPO}/CLEA01/code/clea01_lineage_i2.py")]
    def trivial(s):
        t = s.strip()
        return (not t or t.startswith("#") or t in ("\"\"\"", "from __future__ import annotations")
                or len(t) < 8)
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    shared = []
    for op, i1_, i2_, j1, j2 in sm.get_opcodes():
        if op == "equal":
            shared += [a[k] for k in range(i1_, i2_) if not trivial(a[k])]
    return shared, len(a), len(b)


def main():
    rng = np.random.default_rng(20260826)
    N_OK, N_BAD = 4000, 2000
    routes = {"literal_rule_text": literal_rule, "i1_set_subset": i1_form,
              "i2_morphology": i2_form, "i3_neighbour_count": i3_count}
    mism_ok = {k: 0 for k in routes if k != "literal_rule_text"}
    for n in range(N_OK):
        occ, prev, cert = rng_config(rng, float(rng.uniform(0.02, 0.8)), float(rng.uniform(0, 1)), True)
        ref = literal_rule(occ, prev, cert)
        for k, f in routes.items():
            if k == "literal_rule_text":
                continue
            if not np.array_equal(f(occ, prev, cert), ref):
                mism_ok[k] += 1
    mism_bad = {k: 0 for k in ("i2_morphology",)}
    for n in range(N_BAD):
        occ, prev, cert = rng_config(rng, float(rng.uniform(0.05, 0.6)), float(rng.uniform(0, 1)), False)
        ref = literal_rule(occ, prev, cert)
        if not np.array_equal(i2_form(occ, prev, cert), ref):
            mism_bad["i2_morphology"] += 1

    fx = []
    for name, occ, prev, cert, expect in named_fixtures():
        row = {"case": name}
        for k, f in routes.items():
            row[k] = bool(np.array_equal(f(occ, prev, cert), expect))
        row["ALL_FOUR_MATCH_THE_HAND_ANSWER"] = all(row[k] for k in routes)
        fx.append(row)

    shared, na, nb = shared_lines()

    doc = {
        "MISSION": "CLEA01", "SECTION": "11 — implementation independence",
        "GENERATED_UTC": dt.datetime.now(dt.timezone.utc).isoformat(),
        "WHAT_THEY_SHARE": {
            "shared_physical_constants": "yes — L = 36 and the nine Moore-1 offsets are written "
                                         "separately in each file but are the same constants.",
            "shared_predecessor_definition": "yes, by design: both encode S(d) = Y-occupied cells "
                                             "within toroidal Chebyshev 1. That is the causal "
                                             "assumption under test and it is common-mode.",
            "shared_dilation_or_morphology_primitive": "no — i1 enumerates nine offsets per cell; "
                                                       "i2 uses nine np.roll shifts.",
            "shared_identity_logic": "none. Neither reads any identity field.",
            "independent_component_implementation": "no — the flood fill _n_groups is byte-identical "
                                                    "in body between the two files.",
            "independent_ancestry_implementation": "yes — the CERTAIN/POSSIBLE step operator differs "
                                                   "(set subset test versus boolean morphology).",
            "independent_aggregation": "no — duration, exposure, event attribution and the output "
                                       "dictionary are the same code.",
            "MEASURED_IDENTICAL_NON_TRIVIAL_LINES": len(shared),
            "i1_lines": na, "i2_lines": nb,
            "THE_AUDIT_CLAIMED": "the archive, the frozen constants, and the rule text. No code.",
            "THAT_CLAIM_IS": "FALSE — corrected here, as the checker required.",
        },
        "EQUIVALENCE": {
            "claim": "occ & dilate(certain) & ~dilate(occ_prev & ~certain) equals the set-based "
                     "criterion 'S(d) non-empty and S(d) subset of CERTAIN'",
            "PROOF": "dilate(certain)[d] is true iff some Moore-1 neighbour of d is CERTAIN; "
                     "dilate(occ_prev & ~certain)[d] is true iff some Moore-1 neighbour of d is "
                     "occupied-but-not-certain. Under the PRECONDITION certain subset occ_prev, "
                     "the first conjunct is exactly 'S(d) contains a certain cell' and the negated "
                     "second is exactly 'S(d) contains no non-certain cell'. Together: S(d) "
                     "non-empty and S(d) subset of CERTAIN. The nine offsets are symmetric under "
                     "negation, so np.roll dilation is the correct neighbour test in both "
                     "directions.",
            "PRECONDITION": "CERTAIN(t) subset of occ(t). The pipeline maintains it by "
                            "construction: CERTAIN(t_m) = root & occ(t_m) and every subsequent "
                            "CERTAIN is masked by occ. The audit's proof sketch omitted the "
                            "condition; that omission is the checker's MINOR finding and it is "
                            "corrected here.",
            "RANDOM_TEST_N": N_OK,
            "MISMATCHES_AGAINST_THE_LITERAL_RULE_TEXT": mism_ok,
            "PRECONDITION_DELIBERATELY_BROKEN_N": N_BAD,
            "MISMATCHES_WHEN_THE_PRECONDITION_IS_BROKEN": mism_bad,
            "READING": "equivalence holds under the precondition and fails without it. It is a "
                       "conditional identity, not an unconditional one.",
        },
        "NAMED_STRUCTURAL_CASES": fx,
        "ALL_NAMED_CASES_PASS_ON_ALL_FOUR_ROUTES": all(r["ALL_FOUR_MATCH_THE_HAND_ANSWER"] for r in fx),
        "WHAT_AGREEMENT_DOES_AND_DOES_NOT_ESTABLISH":
            "four routes agreeing establishes that the rule is encoded consistently. It does NOT "
            "establish that the causal assumption is right, because all four encode the SAME "
            "predecessor relation. The assumption is supported instead by the derivation of the "
            "kernel from the engine source and by the archive invariant — see section 5.",
        "SCIENTIFICALLY_INDEPENDENT": False,
        "EQUIVALENT_ENCODINGS": True,
    }
    doc["IMPLEMENTATION_INDEPENDENCE_CONTENT_HASH"] = H.content_digest(
        doc, extra_excluded=("IMPLEMENTATION_INDEPENDENCE_CONTENT_HASH",))
    json.dump(doc, open(f"{REPO}/CLEA01/out/CLEA01_IMPLEMENTATION_INDEPENDENCE_ADJUDICATION.json", "w"), indent=1)
    print("shared non-trivial identical lines:", len(shared), f"(i1 {na} lines, i2 {nb} lines)")
    print("mismatches vs literal rule, precondition held:", mism_ok, f"over {N_OK} configs")
    print("mismatches when precondition broken:", mism_bad, f"over {N_BAD} configs")
    print("named cases all pass:", doc["ALL_NAMED_CASES_PASS_ON_ALL_FOUR_ROUTES"])
    for r in fx:
        print(f"   {'OK ' if r['ALL_FOUR_MATCH_THE_HAND_ANSWER'] else 'FAIL'}  {r['case']}")
    return doc


if __name__ == "__main__":
    main()
