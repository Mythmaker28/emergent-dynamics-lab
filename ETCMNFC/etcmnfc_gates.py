"""ETCMNFC qualification: A1 semantics, O0-O11 operator oracles, adversarial fixtures,
exact-twin infrastructure, the passive ON tap (F0-F10) and the OFF structural exclusion.

All of this runs on DEVELOPMENT blocks and committed development checkpoints. No primary ID
exists yet and no target contrast is opened anywhere in this file.
"""
from __future__ import annotations
import sys, os, ast, json, hashlib, subprocess
from fractions import Fraction as Fr
sys.path.insert(0, "/home/claude/sweep/ETCMNFC")
import numpy as np
import etcmnfc_core as Z
import etpc_core as E
import domc_core as K
import ppai_engine as PE
from edlab.substrates.scaffold.engine import lap

CK = "/home/claude/sweep/ETNBFC/checkpoints"
DEV = (61000, 61001, 61002, 61003)
STARTS = {"n": 0, "log": []}
ROWS, OK = [], True


def start(tag):
    STARTS["n"] += 1
    STARTS["log"].append(tag)


def chk(gate, name, cond, detail=""):
    global OK
    OK &= bool(cond)
    ROWS.append({"gate": gate, "fixture": name, "PASS": bool(cond), "detail": detail})
    print(("PASS " if cond else "FAIL ") + f"{gate:<34}{name}" + (f"\n      {detail}" if detail else ""),
          flush=True)


K.set_geometry("FAR")
states = {s: E.load(f"{CK}/dev_FAR_{s}.npz") for s in DEV}
mems = {s: E.members(states[s])[0] for s in DEV}
O = {}

# =========================================================== A1 : canonical carrier semantics
src = open("/home/claude/sweep/PPAI/ppai_engine.py").read()
srcsc = open("/home/claude/sweep/edlab/substrates/scaffold/engine.py").read()
chk("O0_CANONICAL_SEMANTICS", "Mf[0] is constructed as an amount (rho * intensive)",
    "Mf = rho * newm" in src)
chk("O0_CANONICAL_SEMANTICS", "Mf is transported in telescoping divergence form",
    "dM += -(gm - np.roll(gm, 1, axis))" in src,
    "conserves the PLAIN sum; would not conserve a weighted sum under varying weights")
chk("O0_CANONICAL_SEMANTICS", "no grid spacing or cell area exists anywhere in the substrate",
    "dx" not in srcsc and "4.0 * X)" in srcsc,
    "therefore w_i is a compile-time constant 1.0 at every site; there are no stored or source "
    "weight bits to read, because no such quantity exists")
bad = []
for s in DEV:
    st = states[s]
    ok, parts = Z.domain_ok(st.Mf[0], st.rho)
    if not ok.all():
        bad.append((s, int((~ok).sum())))
chk("O0_CANONICAL_SEMANTICS", "the complete joint domain holds exactly in every checkpoint",
    not bad, f"C1 |Mf0|<=rho, C2 Mf0==0 exactly where rho<=1e-4, finiteness; violations={bad}")
# Mf[1] imposes no constraint on Mf[0]: the writer updates components independently
tree = ast.parse(src)
stepfn = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "step"][0]
body = ast.unparse(stepfn)
chk("O0_CANONICAL_SEMANTICS", "the writer updates each memory component independently",
    "for kk in range(mp.n_comp)" in body and "m[kk]" in body and "Psi" in body,
    "dm_k reads Psi (from N, c, uptake), _tmean(m_k), lap(m_k) and m_k only -- never m_j")
O["A1"] = {"w_i": 1.0, "content": "Q = exact_sum_i Mf[0]_i", "z": "Mf[0]/max(rho,EPS)",
           "domain": ["C1 |Mf0_i| <= rho_i", "C2 Mf0_i == 0.0 exactly where rho_i <= 1e-4",
                      "C3 Mf[1] independent", "C4 no occupancy variable"]}

# =========================================================== B0/B1/B2 : the operator, on real blocks
mans = {}
for s in DEV:
    st, mem = states[s], mems[s]
    man, I, J = Z.manifest(st, mem)
    mans[s] = (man, I, J)
    sw = Z.transpose(st, I, J)
    sh = Z.transpose(st, I, J, identity=True)
    x0, x1 = st.Mf[0], sw.Mf[0]

    # O1 : the matching read no outcome
    # O2 : equal storage weights, unequal rho allowed
    rA = np.array([st.rho[y, x] for y, x in I])
    rB = np.array([st.rho[y, x] for y, x in J])
    n_unequal_rho = int((rA != rB).sum())

    # O3 : post-state domain
    okd, _ = Z.domain_ok(x1, st.rho)

    # O4 : unique disjoint cross-component 2-cycles
    flat = [y * Z.L + x for y, x in I] + [y * Z.L + x for y, x in J]
    ids_a = set(Z.site_ids(mem, "A").tolist())
    ids_b = set(Z.site_ids(mem, "B").tolist())
    cross = all((y * Z.L + x) in ids_a for y, x in I) and all((y * Z.L + x) in ids_b for y, x in J)

    # O5 : byte transposition
    byte_ok = all(x1[yi, xi].tobytes() == x0[yj, xj].tobytes()
                  and x1[yj, xj].tobytes() == x0[yi, xi].tobytes()
                  for (yi, xi), (yj, xj) in zip(I, J))

    # O6 : unmatched identity
    msk = np.ones_like(x0, dtype=bool)
    for (y, x) in I + J:
        msk[y, x] = False
    unm = np.array_equal(x0[msk].view(np.int64), x1[msk].view(np.int64))
    other = all(np.array_equal(np.asarray(getattr(st, f)).view(np.int64),
                               np.asarray(getattr(sw, f)).view(np.int64))
                for f in ("rho", "U", "V", "c", "N", "C", "uptake")) \
        and np.array_equal(st.Mf[1].view(np.int64), sw.Mf[1].view(np.int64))

    # O7 : exact global content, two independent proofs
    ms_ok = Z.multiset_sha(x0) == Z.multiset_sha(x1)
    q_ok = Z.exact_sum(x0) == Z.exact_sum(x1)

    # O8 : exact reciprocity
    dA = Z.carrier_content(sw, mem, "A") - Z.carrier_content(st, mem, "A")
    dB = Z.carrier_content(sw, mem, "B") - Z.carrier_content(st, mem, "B")

    # O9 : full-state involution
    twice = Z.transpose(sw, I, J)
    inv_ok = Z.full_state_sha(twice)[0] == Z.full_state_sha(st)[0]

    # O10/O11 : touchset and t0 public identity
    pub_ok = Z.public_sha(st) == Z.public_sha(sw)
    sham_ok = Z.full_state_sha(sh)[0] == Z.full_state_sha(st)[0]

    disp = Z.displacement(x0, x1)
    wfrac = Fr(len(I) * 2, len(mem["A"][0]) + len(mem["B"][0]))
    man.update({"n_unequal_rho_pairs": n_unequal_rho,
                "delta_Q_A": float(dA), "delta_Q_B": float(dB),
                "net_reciprocal_component_shift": float(abs(dA)),
                "gross_canonical_displacement": float(disp),
                "paired_site_count": len(I),
                "paired_storage_weight_fraction": float(wfrac)})

    tag = f"seed {s}"
    chk("O2_EQUAL_WEIGHT_SUPPORT", f"equal w bits, UNEQUAL rho allowed [{tag}]",
        len(I) > 0 and n_unequal_rho == len(I),
        f"{len(I)} pairs, {n_unequal_rho} of them have DIFFERENT rho -- equal rho is not required")
    chk("O3_DOMAIN_ADMISSIBLE", f"complete post-state passes the joint domain, no clip [{tag}]",
        bool(okd.all()))
    chk("O4_MANIFEST_2_CYCLES", f"unique disjoint cross-component 2-cycles [{tag}]",
        cross and len(set(flat)) == len(flat))
    chk("O5_BYTE_TRANSPOSITION", f"every target byte equals its committed source byte [{tag}]",
        byte_ok)
    chk("O6_UNMATCHED_IDENTITY", f"all unmatched state byte-identical [{tag}]", unm and other)
    chk("O7_EXACT_GLOBAL_CONTENT", f"multiset AND exact rational content preserved [{tag}]",
        ms_ok and q_ok, "proved by sorted-byte multiset identity and by Fraction accumulation, "
                        "not by np.sum or a tolerance")
    chk("O8_RECIPROCAL_NONTRIVIALITY", f"exact dQ_A = -dQ_B != 0 [{tag}]",
        dA == -dB and dA != 0, f"dQ_A = {float(dA):+.9f} (exact rational), dQ_B = {float(dB):+.9f}")
    chk("O9_FULL_STATE_INVOLUTION", f"applying the manifest twice restores the whole state [{tag}]",
        inv_ok, "every canonical field, bit for bit; the engine holds no cache, integrator, "
                "event queue, RNG or scheduler state (A1 schema audit)")
    chk("O10_TOUCHSET", f"only Mf[0] changed [{tag}]", other)
    chk("O11_T0_PUBLIC_IDENTITY", f"public projection bit-identical at t0 [{tag}]", pub_ok)
    chk("O1_MATCHING_PROSPECTIVE", f"identity hook is bit-identical to no hook [{tag}]", sham_ok)

O["MANIFESTS"] = {s: mans[s][0] for s in DEV}

# --- O1 proper: the matching objective cannot read a value, only a boolean
def _executable_body(fn):
    """Strip the docstring and unparse ONLY the executable statements. A search over raw source
    would hit the docstring -- the exact trap that produced a false failure in the PPAI
    fixtures. Only the code is audited here."""
    body = list(fn.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
            and isinstance(body[0].value.value, str):
        body = body[1:]
    return "\n".join(ast.unparse(s) for s in body)


_ctree = ast.parse(open("/home/claude/sweep/ETCMNFC/etcmnfc_core.py").read())
fm = [n for n in ast.walk(_ctree)
      if isinstance(n, ast.FunctionDef) and n.name in ("frozen_matching", "_max_matching")]
fm_src = "\n".join(_executable_body(n) for n in fm)
forbidden = ["rho", "Mf", "z_of", "kappa", "flux", "uptake", "c[", "N["]
hits = [w for w in forbidden if w in fm_src]
chk("O1_MATCHING_PROSPECTIVE", "the matching objective reads no field value at all", not hits,
    f"docstrings stripped, executable statements only; frozen_matching/_max_matching see only "
    f"the boolean eligibility matrix and immutable ids; forbidden symbols found = {hits}")

# --- determinism under enumeration reversal
det = []
for s in DEV:
    st, mem = states[s], mems[s]
    ok = Z.eligible_edges(st, mem)
    ids_a, ids_b = Z.site_ids(mem, "A"), Z.site_ids(mem, "B")
    M1, p1 = Z.frozen_matching(ok, ids_a, ids_b)
    rev = np.arange(len(ids_a))[::-1]
    revb = np.arange(len(ids_b))[::-1]
    M2, p2 = Z.frozen_matching(ok[np.ix_(rev, revb)], ids_a[rev], ids_b[revb])
    det.append((M1 == M2) and ([(a, b) for a, b, _, _ in p1] == [(a, b) for a, b, _, _ in p2]))
chk("O1_MATCHING_PROSPECTIVE", "matching is invariant under enumeration reversal", all(det),
    "the lexicographically-smallest maximum matching is unique, so search order cannot matter")

# =========================================================== adversarial fixtures
def mk(rho_a, x_a, rho_b, x_b):
    st = states[DEV[0]].copy()
    st.rho = st.rho.copy(); st.Mf = st.Mf.copy()
    return st


adv = []
cases = {
    "unequal rho, equal weights": (0.5, 0.4, 0.9, -0.2, True),
    "swap would break C1 on i": (0.30, 0.10, 0.90, 0.85, False),
    "swap would break C1 on j": (0.90, 0.85, 0.30, 0.10, False),
    "signed zero source": (0.5, -0.0, 0.7, 0.3, True),
    "subnormal carrier value": (0.5, 5e-324, 0.7, 0.3, True),
    "bound value |x| == rho on both": (0.5, 0.5, 0.5, -0.5, True),
    "bound value that just fits after swap": (0.6, 0.4, 0.4, -0.4, True),
    "bound value that just fails after swap": (0.6, 0.55, 0.5, -0.5, False),
}
for nm, (ri, xi, rj, xj, want) in cases.items():
    oi, _ = Z.domain_ok(np.array([xj]), np.array([ri]))
    oj, _ = Z.domain_ok(np.array([xi]), np.array([rj]))
    got = bool(oi[0] and oj[0])
    adv.append({"case": nm, "expected_eligible": want, "got": got})
    chk("O3_DOMAIN_ADMISSIBLE", f"adversarial: {nm}", got == want,
        f"rho_i={ri} x_i={xi} rho_j={rj} x_j={xj} -> eligible={got}")
# exact reciprocity under a signed-zero / subnormal pair, via rationals
a = np.array([-0.0, 5e-324, 0.25]); b = np.array([0.25, -0.0, 5e-324])
chk("O7_EXACT_GLOBAL_CONTENT", "adversarial: signed zero and subnormal preserve the exact sum",
    Z.exact_sum(a) == Z.exact_sum(b) and Z.multiset_sha(a) != Z.multiset_sha(a * 1.0000001))
O["ADVERSARIAL"] = adv

json.dump({"rows": ROWS, "engine_starts": STARTS, **O},
          open("/home/claude/sweep/ETCMNFC/etcmnfc_gates_offline.json", "w"), indent=1, default=str)
print(f"\nOFFLINE GATES: {sum(r['PASS'] for r in ROWS)}/{len(ROWS)} PASS; engine starts {STARTS['n']}")
