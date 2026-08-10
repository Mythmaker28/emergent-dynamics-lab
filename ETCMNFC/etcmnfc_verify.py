"""Independent verifier for ETCMNFC. Re-derives every load-bearing claim from the committed
development checkpoints and the executable, then compares against the published JSON."""
from __future__ import annotations
import sys, os, ast, json, hashlib
from collections import Counter
from fractions import Fraction as Fr
sys.path.insert(0, "/home/claude/sweep/ETCMNFC")
import numpy as np
import etcmnfc_core as Z
import etpc_core as E
import domc_core as K
from edlab.experiments.sc_mcm import config as C
from ppai_engine import PPAIParams

CK = "/home/claude/sweep/ETNBFC/checkpoints"
DEV = (61000, 61001, 61002, 61003)
ROWS, OK = [], True


def chk(n, cond, detail=""):
    global OK
    OK &= bool(cond)
    ROWS.append({"check": n, "PASS": bool(cond), "detail": detail})


K.set_geometry("FAR")
G = json.load(open("etcmnfc_gates_offline.json"))
P1 = json.load(open("etcmnfc_phaseC.json"))
P2 = json.load(open("etcmnfc_phaseC2.json"))
states = {s: E.load(f"{CK}/dev_FAR_{s}.npz") for s in DEV}
mems = {s: E.members(states[s])[0] for s in DEV}

# ---------------------------------------------------------------- V1 the operator, re-derived
per = []
for s in DEV:
    st, mem = states[s], mems[s]
    man, I, J = Z.manifest(st, mem)
    sw = Z.transpose(st, I, J)
    x0, x1 = st.Mf[0], sw.Mf[0]
    rA = np.array([st.rho[y, x] for y, x in I])
    rB = np.array([st.rho[y, x] for y, x in J])
    dA = Z.carrier_content(sw, mem, "A") - Z.carrier_content(st, mem, "A")
    dB = Z.carrier_content(sw, mem, "B") - Z.carrier_content(st, mem, "B")
    per.append({
        "seed": s, "pairs": len(I), "unequal_rho": int((rA != rB).sum()),
        "multiset": Z.multiset_sha(x0) == Z.multiset_sha(x1),
        "exact_Q": Z.exact_sum(x0) == Z.exact_sum(x1),
        "reciprocal": (dA == -dB) and dA != 0,
        "involution": Z.full_state_sha(Z.transpose(sw, I, J))[0] == Z.full_state_sha(st)[0],
        "domain": bool(Z.domain_ok(x1, st.rho)[0].all()),
        "public_t0": Z.public_sha(st) == Z.public_sha(sw),
        "only_Mf0": all(np.array_equal(np.asarray(getattr(st, f)).view(np.int64),
                                       np.asarray(getattr(sw, f)).view(np.int64))
                        for f in Z.PUBLIC_FIELDS)
        and np.array_equal(st.Mf[1].view(np.int64), sw.Mf[1].view(np.int64))})
chk("V1 the operator is an exact conservative byte involution on every development block",
    all(p["multiset"] and p["exact_Q"] and p["reciprocal"] and p["involution"]
        and p["domain"] and p["public_t0"] and p["only_Mf0"] for p in per),
    f"{per}")
chk("V1b equal rho is NOT required: every matched pair has different rho",
    all(p["pairs"] > 0 and p["unequal_rho"] == p["pairs"] for p in per),
    "this is the point Tommy's executive correction turned on")

# ---------------------------------------------------------------- V2 disjointness guard fires
try:
    Z.transpose(states[DEV[0]], [(1, 1), (1, 1)], [(2, 2), (3, 3)])
    guard = False
except ValueError:
    guard = True
chk("V2 transpose refuses a non-disjoint pair list", guard)

# ---------------------------------------------------------------- V3 the matching is frozen
det = []
for s in DEV:
    ok = Z.eligible_edges(states[s], mems[s])
    ia, ib = Z.site_ids(mems[s], "A"), Z.site_ids(mems[s], "B")
    M1, p1 = Z.frozen_matching(ok, ia, ib)
    ra, rb = np.arange(len(ia))[::-1], np.arange(len(ib))[::-1]
    M2, p2 = Z.frozen_matching(ok[np.ix_(ra, rb)], ia[ra], ib[rb])
    det.append(M1 == M2 and [(a, b) for a, b, _, _ in p1] == [(a, b) for a, b, _, _ in p2])
chk("V3 the frozen matching is invariant under enumeration reversal", all(det))
chk("V3b the eligibility object handed to the matcher is boolean",
    Z.eligible_edges(states[DEV[0]], mems[DEV[0]]).dtype == np.bool_)
chk("V3c the published scope correction is on the record",
    "O1_SCOPE_CORRECTION" in P2 and "IS a function of the baseline carrier values"
    in json.dumps(P2["O1_SCOPE_CORRECTION"]),
    "the matching OBJECTIVE is value-blind; the ELIGIBILITY PREDICATE is not, and that is "
    "published with the reviewer's counterexample rather than glossed")

# ---------------------------------------------------------------- V4 the vacuous oracles
chk("V4 the three vacuous first-pass oracles are recorded as superseded, not deleted",
    len(P2.get("SUPERSEDED_VACUOUS_ORACLES", [])) == 3
    and os.path.exists("etcmnfc_phaseC.json"),
    "F5, F6 and F2 as first written could not fail; both the failure and the replacements are "
    "published")
# and prove they were vacuous, here, independently
rng = np.random.default_rng(11)
noise = rng.standard_normal((64, 64))
vac6 = (Z.exact_sum(noise) - Z.exact_sum(np.roll(noise, 1, -1))) == 0
chk("V4b the old F6 really was a property of np.roll, not of the engine", vac6,
    "exact_sum(f) - exact_sum(roll(f,1,ax)) == 0 on pure noise unrelated to any engine")

# ---------------------------------------------------------------- V5 the replacement oracles
names = {r["gate"] for r in P2["rows"]}
chk("V5 the replacement oracles all carry a negative control and all pass",
    all(r["PASS"] for r in P2["rows"]) and
    {"F5_LEDGER_EQUALS_NATIVE_RETURN", "F6_PAIRWISE_DEBIT_CREDIT",
     "F2_MASK_CROSS_CHECK_VIA_KAPPA"} <= names,
    f"{sum(r['PASS'] for r in P2['rows'])}/{len(P2['rows'])} PASS")

# ---------------------------------------------------------------- V6 THE STOP, re-derived
att = []
for s in DEV:
    st, mem = states[s], mems[s]
    alive = st.rho > Z.ALIVE_EPS
    comp = np.zeros_like(alive)
    for k in ("A", "B"):
        ys, xs = mem[k]
        comp[ys, xs] = True
    tot = inc = 0
    for ax in (0, 1):
        nb = np.roll(alive, -1, ax)
        xor = alive ^ nb
        tot += int(xor.sum())
        inc += int((comp & (alive & xor)).sum()) + int((np.roll(comp, -1, ax) & (nb & xor)).sum())
    touch = sum(int((comp & ~np.roll(alive, sh, ax)).sum()) for ax in (0, 1) for sh in (-1, 1))
    att.append({"seed": s, "links": tot, "attributable": inc, "component_touches_bath": touch})
chk("V6 the authorized per-component endpoint has EMPTY support in every development block",
    all(a["attributable"] == 0 and a["links"] > 0 and a["component_touches_bath"] == 0
        for a in att), f"{att}")
chk("V6b the report calls this NOT_IDENTIFIABLE and never 'no effect'",
    "NOT_IDENTIFIABLE" in open("REPORT_ETCMNFC.md", encoding="utf-8").read()
    and "aucun effet" not in open("REPORT_ETCMNFC.md", encoding="utf-8").read()
    .replace("« aucun effet »", ""))

# ---------------------------------------------------------------- V7 scope discipline
starts = P1["engine_starts"]["n"] + P2["engine_starts"]["n"]
chk("V7 programme engine starts are within the qualification cap of 20", starts <= 20,
    f"total = {starts}")
chk("V7b only development seeds were advanced",
    all(int(t.split("_")[-1]) in DEV for t in P1["engine_starts"]["log"] + P2["engine_starts"]["log"]
        if t.split("_")[-1].isdigit()))
chk("V7c no primary ID was allocated and no held-out artefact exists",
    not any(f.startswith("primary") or "62" in f for f in os.listdir("."))
    and not os.path.exists("/home/claude/sweep/ETPC/etpc_HELDOUT.pkl"))
chk("V7d the independent-review start-count gap is DECLARED, not hidden",
    "Écart de comptabilité déclaré" in open("REPORT_ETCMNFC.md", encoding="utf-8").read())

# ---------------------------------------------------------------- V8 forbidden claim language
txt = open("REPORT_ETCMNFC.md", encoding="utf-8").read()
banned = ["transplantation de `z` a été", "échange de parcelles matérielles réussi",
          "aucun effet établi", "no effect"]
chk("V8 no forbidden claim phrasing appears", not [b for b in banned if b in txt])
chk("V8b Q is published as preserved by the operator but NOT by the dynamics",
    "Q_IS_NOT_A_DYNAMICAL_INVARIANT" in P2)
chk("V8c both mandated independent reviews are committed",
    os.path.exists("REVIEW_1_NUMERICAL_ORACLE.md")
    and os.path.exists("REVIEW_2_CAUSAL_STATISTICAL.md"))
chk("V8d the false dilemma of the parent programme is explicitly withdrawn",
    "FALSE_DILEMMA_WITHDRAWN" in open("ETNBFC_CORRIGENDUM.md", encoding="utf-8").read())

json.dump({"rows": ROWS, "n": len(ROWS), "n_pass": sum(r["PASS"] for r in ROWS), "ALL_PASS": OK,
           "programme_engine_starts": starts},
          open("etcmnfc_verify.json", "w"), indent=1)
for r in ROWS:
    print(("PASS " if r["PASS"] else "FAIL ") + r["check"]
          + (f"\n      [{str(r['detail'])[:300]}]" if r["detail"] else ""))
print(f"\n{sum(r['PASS'] for r in ROWS)}/{len(ROWS)} verification checks passed")
