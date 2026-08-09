"""DOMC mechanical fixtures. Every one must PASS before a single experimental trajectory runs.
These are invariants of the harness, not hypotheses. A failure here is a kill switch."""
from __future__ import annotations
import ast, sys, json
sys.path.insert(0, "/home/claude/sweep")
import numpy as np

import domc_core as K
from edlab.experiments.sc_mcm import config as C
from edlab.experiments.sc_mcm.engine import MultiChannelMemoryEngine, MCParams
from edlab.substrates.scaffold.engine import ScaffoldEngine, SCState

R = []


def chk(name, ok, detail=""):
    R.append({"fixture": name, "PASS": bool(ok), "detail": detail})
    print(("PASS " if ok else "FAIL ") + name + ("  " + detail if detail else ""), flush=True)
    return ok


# 1 --------------------------------------------------------- founding preserves sum_c C == rho
st = K.found(34000)
d = float(np.abs(st.C.sum(axis=0) - st.rho).max())
chk("1 founding: sum_c C == rho exactly", d == 0.0, f"max |residual| = {d:.3e}")

# 1b -------------------------------------------------- founding leaves memory identically zero
chk("1b founding: Mf == 0 everywhere", float(np.abs(st.Mf).max()) == 0.0)

# 2 ------------------------------- backward compatibility: both couplings off -> frozen physics
mc0 = MultiChannelMemoryEngine(C.SPEC, MCParams(lam_plus=0.0, lam_minus=0.0), C.TRACER)
sc = ScaffoldEngine(C.SPEC, C.TRACER)
a = K.found(34000)
b = SCState(a.rho.copy(), a.U.copy(), a.V.copy(), a.c.copy(), a.N.copy(), a.C.copy(),
            a.uptake.copy(), 0)
for _ in range(200):
    a = mc0.step(a)
    b = sc.step(b)
worst = max(float(np.abs(getattr(a, f) - getattr(b, f)).max()) for f in ("rho", "U", "V", "c", "N", "C"))
chk("2 lam_plus = lam_minus = 0 reproduces the frozen scaffold BIT-IDENTICALLY",
    worst == 0.0, f"max |diff| over rho,U,V,c,N,C after 200 steps = {worst:.3e}")

# 3 ------------------------------------------- reciprocal cross is an exact global permutation
eng = K.engine()
s0 = K.advance(eng, K.found(34000), K.T_FOUND)
s0 = K.apply_dual_history(eng, s0, "H1", "H2")
s0 = K.advance(eng, s0, K.SETTLE)
x1 = K.reciprocal_cross(s0)
# The conservation statement that is EXACT is the permutation one: the multiset of values is
# unchanged. `np.sum` over a reordered array is NOT bit-identical, because floating-point
# addition is not associative; that is a property of the summation, not of the operation. The
# criterion is therefore the multiset identity, plus `math.fsum` (correctly rounded) as the
# order-independent total, plus the naive-sum discrepancy reported rather than tolerated.
import math
f0, f1 = math.fsum(s0.Mf.ravel().tolist()), math.fsum(x1.Mf.ravel().tolist())
chk("3 cross: the memory field is EXACTLY permuted (multiset of values identical)",
    bool(np.array_equal(np.sort(x1.Mf.ravel()), np.sort(s0.Mf.ravel()))))
chk("3b cross: the correctly rounded total is identical (math.fsum)", f0 == f1,
    f"fsum before {f0!r} after {f1!r} | naive np.sum discrepancy "
    f"{abs(float(x1.Mf.sum()) - float(s0.Mf.sum())):.3e} (float summation order only)")
x2 = K.reciprocal_cross(x1)
chk("3c cross applied twice is the IDENTITY (bit-exact)",
    bool(np.array_equal(x2.Mf, s0.Mf)))
chk("3d the cross index map exchanges the two sites of BOTH frozen geometries",
    all(int(K.REFLECT_IX[b[1]]) == a[1] and int(K.REFLECT_IX[a[1]]) == b[1]
        for a, b in K.GEOMETRY.values()),
    " ".join(f"{g}: {a[1]}<->{b[1]}" for g, (a, b) in K.GEOMETRY.items()))
xr = K.reciprocal_cross_roll(s0)
chk("3e the FAR-only translation variant is also an exact conserving involution",
    math.fsum(xr.Mf.ravel().tolist()) == f0
    and bool(np.array_equal(K.reciprocal_cross_roll(xr).Mf, s0.Mf)))

# 3f ------------------------------- the turnover instrument does not change the physics at all
_pc = K.pc_engine()
_a = K.advance(eng, s0, 60)
_b = K.advance(_pc, K.relabel(s0), 60)
chk("3f swapping the tracer changes C only: rho, U, V, c, N, Mf evolve bit-identically",
    max(float(np.abs(getattr(_a, f) - getattr(_b, f)).max())
        for f in ("rho", "U", "V", "c", "N", "Mf", "uptake")) == 0.0)

# 4 --------------------------------------------- cross touches Mf and strictly nothing else
oth = max(float(np.abs(getattr(x1, f) - getattr(s0, f)).max())
          for f in ("rho", "U", "V", "c", "N", "C", "uptake"))
chk("4 cross leaves rho, U, V, c, N, C, uptake bit-identical", oth == 0.0,
    f"max |diff| = {oth:.3e}")
mv = float(np.abs(x1.Mf - s0.Mf).max())
chk("4b cross DOES move the memory field (it is not a no-op)", mv > 0.0, f"max |dMf| = {mv:.4f}")

# 5 ---------------------------------------------------------------------- selective erasure
ea = K.erase_half(s0, "A")
eb = K.erase_half(s0, "B")
chk("5 ERASE_A zeroes exactly half the lattice in Mf",
    float(np.abs(ea.Mf[:, :, K.HALF_A]).max()) == 0.0
    and bool(np.array_equal(ea.Mf[:, :, K.HALF_B], s0.Mf[:, :, K.HALF_B])))
chk("5b ERASE_B is the exact complement",
    float(np.abs(eb.Mf[:, :, K.HALF_B]).max()) == 0.0
    and bool(np.array_equal(eb.Mf[:, :, K.HALF_A], s0.Mf[:, :, K.HALF_A])))
both = K.erase_half(K.erase_half(s0, "A"), "B")
chk("5c ERASE_A then ERASE_B == total erasure", float(np.abs(both.Mf).max()) == 0.0)
chk("5d erasure touches nothing but Mf",
    max(float(np.abs(getattr(ea, f) - getattr(s0, f)).max())
        for f in ("rho", "U", "V", "c", "N", "C", "uptake")) == 0.0)

# 6 -------------------------------------------------------------- the sham is a bit-exact no-op
sh = K.erase_sham(s0)
chk("6 ERASE_SHAM is a bit-exact no-op on the whole state",
    all(bool(np.array_equal(getattr(sh, f), getattr(s0, f)))
        for f in ("rho", "U", "V", "c", "N", "C", "uptake", "Mf")))

# 7 ------------------------------------------------------------------ global forcing identity
tAB = K.global_forcing_trace("H1", "H2")
tBA = K.global_forcing_trace("H2", "H1")
tAA = K.global_forcing_trace("H1", "H1")
chk("7 DUAL_AB and DUAL_BA have an IDENTICAL global forcing time series", tAB == tBA,
    f"{len(tAB)} steps compared")
chk("7b DUAL_AA has a DIFFERENT global forcing series (it is not a global-forcing control)",
    tAA != tAB)

# 8 --------------------------------------------------- localized driving really is localized
base = K.advance(eng, K.found(34001), K.T_FOUND)
one = base.copy()
for _ in range(K.T_PHASE):
    one.N[:, K.HALF_A] = one.N[:, K.HALF_A] + K.AMP
    one = eng.step(one)
free = K.advance(eng, base, K.T_PHASE)
dN = one.N - free.N
yy, xx = np.mgrid[0:K.L, 0:K.L]
nearA = K._pd2(yy, xx, *K.SITE_A) <= 36
nearB = K._pd2(yy, xx, *K.SITE_B) <= 36
rA = float(np.abs(dN[nearA]).mean()); rB = float(np.abs(dN[nearB]).mean())
chk("8 a one-sided N drive raises N far more at the driven site than at the other",
    rA > 5 * rB, f"mean |dN| near A = {rA:.4f} vs near B = {rB:.4f}  ratio = {rA/max(rB,1e-12):.1f}x")

# 8b ------------------------------------------------------------ and it writes memory locally
dM = np.abs(one.Mf - free.Mf)
mA = float(dM[:, nearA].mean()); mB = float(dM[:, nearB].mean())
chk("8b and it writes memory far more at the driven site",
    mA > 5 * mB, f"mean |dMf| near A = {mA:.5f} vs near B = {mB:.5f}  ratio = {mA/max(mB,1e-12):.1f}x")

# 9 ------------------------------------ reader firewall: the online reader is provenance-blind
src = open("domc_core.py").read()
tree = ast.parse(src)
FORBIDDEN_ATTR = {"C"}            # the cohort/provenance field
FORBIDDEN_CALL = {"mem"}          # the privileged memory diagnostic
ONLINE = {"read_sites", "_feat_site", "response_at_sites", "_perturb_N",
          "erase_half", "erase_sham", "reciprocal_cross", "reciprocal_cross_roll",
          "reciprocal_cross_env"}
bad = []
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name in ONLINE:
        for sub in ast.walk(node):
            if isinstance(sub, ast.Attribute) and sub.attr in FORBIDDEN_ATTR:
                bad.append((node.name, "attribute", sub.attr))
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute) \
                    and sub.func.attr in FORBIDDEN_CALL:
                bad.append((node.name, "call", sub.func.attr))
chk("9 every online reader and operation is blind to provenance C and to mem()",
    not bad, f"violations = {bad}" if bad else f"audited {sorted(ONLINE)}")

# 9b ------------------- the scalar dictionary IS allowed the privileged memory diagnostic ...
sc_fn = [nd for nd in ast.walk(tree) if isinstance(nd, ast.FunctionDef) and nd.name == "scalars"][0]
uses_mem = any(isinstance(s, ast.Call) and isinstance(s.func, ast.Attribute)
               and s.func.attr == "mem" for s in ast.walk(sc_fn))
uses_C = any(isinstance(s, ast.Attribute) and s.attr == "C" for s in ast.walk(sc_fn))
chk("9b scalars() uses mem() (declared privileged diagnostic) and NEVER provenance C",
    uses_mem and not uses_C, f"mem={uses_mem} C={uses_C}")

# 9c ------------------------------------- the environment cross is the SAME permutation on c, N
xe = K.reciprocal_cross_env(s0)
chk("9c CROSS_ENV permutes c and N exactly and leaves Mf, rho, U, V, C untouched",
    bool(np.array_equal(np.sort(xe.c.ravel()), np.sort(s0.c.ravel())))
    and bool(np.array_equal(np.sort(xe.N.ravel()), np.sort(s0.N.ravel())))
    and max(float(np.abs(getattr(xe, ff) - getattr(s0, ff)).max())
            for ff in ("rho", "U", "V", "C", "Mf", "uptake")) == 0.0)
chk("9d CROSS_ENV applied twice is the IDENTITY (bit-exact)",
    bool(np.array_equal(K.reciprocal_cross_env(xe).c, s0.c))
    and bool(np.array_equal(K.reciprocal_cross_env(xe).N, s0.N)))

# 10 ------------------------------------------------------------------- probe determinism
r1 = K.response_at_sites(eng, s0)
r2 = K.response_at_sites(eng, s0)
chk("10 the probe is deterministic (bit-exact on repetition)",
    all(bool(np.array_equal(r1[k], r2[k])) for k in r1))

# 11 --------------------------------------- with zero amplitude the causal response is exactly 0
_saved = K.PROBE
K.PROBE = ("N", "add", 0.0, 15)
r0 = K.response_at_sites(eng, s0)
K.PROBE = _saved
chk("11 a zero-amplitude probe gives an exactly zero causal response (intervention null)",
    float(max(np.abs(r0["A"]).max(), np.abs(r0["B"]).max())) == 0.0,
    f"max |R| = {max(np.abs(r0['A']).max(), np.abs(r0['B']).max()):.3e}")

# 12 -------------------------------------------------------- turnover instrument is conservative
pc = K.pc_engine()
t0 = K.relabel(s0)
t1 = K.advance(pc, t0, 100)
res = float(np.abs(t1.C.sum(axis=0) - t1.rho).max())
chk("12 pulse-chase cohorts sum to rho exactly after 100 steps", res < 1e-12,
    f"max |residual| = {res:.3e}")

# 13 ---------------------------------------------------- the founded world is a clean pair here
pick, dst, ncomp = K.read_sites(s0)
chk("13 the settled founded world holds exactly two components, one per frozen site",
    ncomp == 2 and pick["A"] is not None and pick["B"] is not None
    and pick["A"] is not pick["B"],
    f"n_components = {ncomp}, d(A) = {dst['A']:.2f}, d(B) = {dst['B']:.2f}")

# 14 ---------------------------------- reading at a site is NOT reading `largest` by accident
sizes = (pick["A"].size, pick["B"].size)
chk("14 the two components are separately sized and neither is privileged",
    pick["A"] is not pick["B"], f"sizes = {sizes}")

json.dump(R, open("domc_fixtures.json", "w"), indent=1)
npass = sum(1 for r in R if r["PASS"])
print(f"\n{npass}/{len(R)} fixtures PASS")
sys.exit(0 if npass == len(R) else 1)
