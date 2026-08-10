"""Independent verifier for EXACT_TWIN_NATIVE_BOUNDARY_FLUX_CONFIRMATION_00.

Re-derives every load-bearing claim of the report from the committed checkpoints and the
executable, without reading the audit scripts' own conclusions, then compares. No target
contrast is computed anywhere. No held-out artefact is opened.
"""
from __future__ import annotations
import sys, os, ast, json, hashlib, pickle
from collections import Counter
sys.path.insert(0, "/home/claude/sweep")
sys.path.insert(0, "/home/claude/sweep/DOMC")
sys.path.insert(0, "/home/claude/sweep/PPAI")
sys.path.insert(0, "/home/claude/sweep/ETPC")
import numpy as np
import etpc_core as E
import ppai_engine as PE
from edlab.substrates.scaffold.engine import lap

ROWS, OK = [], True
DEV = (61000, 61001, 61002, 61003)
CK = "/home/claude/sweep/ETNBFC/checkpoints"


def chk(name, cond, detail=""):
    global OK
    OK &= bool(cond)
    ROWS.append({"check": name, "PASS": bool(cond), "detail": detail})


B0 = json.load(open("etnbfc_b0.json"))
C0 = json.load(open("etnbfc_c0.json"))
BM = json.load(open("etnbfc_boundary_mask_inventory.json"))
ETPC = {b["seed"]: b for b in pickle.load(open("/home/claude/sweep/ETPC/etpc_PRIMARY.pkl", "rb"))}
states = {s: E.load(f"{CK}/dev_FAR_{s}.npz") for s in DEV}

# ---------------------------------------------------------------- V1 durable raw evidence
chk("V1 every development checkpoint is a committed file with a committed hash manifest",
    all(os.path.exists(f"{CK}/dev_FAR_{s}.npz") and os.path.exists(f"{CK}/dev_FAR_{s}.npz.hash.json")
        for s in DEV), "no tempfile.mkdtemp() path is relied on")
bad = []
for s in DEV:
    h = json.load(open(f"{CK}/dev_FAR_{s}.npz.hash.json"))
    if h["archive_sha256"] != hashlib.sha256(open(f"{CK}/dev_FAR_{s}.npz", "rb").read()).hexdigest():
        bad.append(s)
chk("V1b each checkpoint archive matches its recorded sha256", not bad, f"mismatched = {bad}")

# ---------------------------------------------------------------- V2 bit-exact cross-session replay
mis = [s for s in DEV
       if E.logical_hash(states[s], E.runtime_manifest())[0] != ETPC[s]["checkpoint_logical_hash"]]
chk("V2 replayed founding checkpoints hash bit-identically to ETPC's committed hashes",
    not mis, f"seeds differing = {mis}")

# ---------------------------------------------------------------- V3 canonical semantics
src = open("/home/claude/sweep/PPAI/ppai_engine.py").read()
srcsc = open("/home/claude/sweep/edlab/substrates/scaffold/engine.py").read()
chk("V3 Mf is built as rho * intensive", "Mf = rho * newm" in src)
chk("V3b Mf transport is written in telescoping divergence form",
    "dM += -(gm - np.roll(gm, 1, axis))" in src)
chk("V3c the stencil carries no grid spacing, so every cell has unit measure",
    "dx" not in srcsc and "4.0 * X)" in srcsc)
chk("V3d the intensive coordinate is clipped to [-1, 1] before Mf is rebuilt",
    "np.clip(mk, -1.0, 1.0) * alive" in src)
viol = []
for s in DEV:
    st = states[s]
    alive = st.rho > 1e-4
    if (np.abs(st.Mf[0]) > st.rho + 0.0).any():
        viol.append(("C1", s))
    if (st.Mf[0][~alive] != 0.0).any():
        viol.append(("C2", s))
chk("V3e the two joint domain constraints hold exactly in every committed checkpoint",
    not viol, "C1: |Mf[0]| <= rho ; C2: Mf[0] == 0 exactly where rho <= 1e-4; "
              f"violations = {viol}")

# ---------------------------------------------------------------- V4 exact support is empty
tot, per = 0, []
for s in DEV:
    st = states[s]
    mem, _ = E.members(st)
    (ya, xa), (yb, xb) = mem["A"], mem["B"]
    ca = Counter(st.rho[y, x].tobytes() for y, x in zip(ya, xa))
    cb = Counter(st.rho[y, x].tobytes() for y, x in zip(yb, xb))
    n = sum((ca & cb).values())
    tot += n
    per.append({"seed": s, "n_A": len(ya), "n_B": len(yb), "exact_pairs": n})
chk("V4 the exact byte-matched A-B common support is EMPTY in every development block",
    tot == 0, f"{per}")
dupes = []
for s in DEV:
    c = Counter(v.tobytes() for v in states[s].rho.ravel())
    dupes.append((s, states[s].rho.size, len(c), sum(v for v in c.values() if v > 1)))
chk("V4b rho takes a distinct float64 value at EVERY cell of every grid",
    all(size == distinct and rep == 0 for _, size, distinct, rep in dupes),
    f"(seed, cells, distinct values, cells sharing a repeat) = {dupes}")

# ---------------------------------------------------------------- V5 how far from a match
ulps = []
for s in DEV:
    st = states[s]
    mem, _ = E.members(st)
    (ya, xa), (yb, xb) = mem["A"], mem["B"]
    A = st.rho[ya, xa].astype(np.float64)
    Bv = st.rho[yb, xb].astype(np.float64)
    ia = A.view(np.int64)
    ib = Bv.view(np.int64)
    ulps.append(int(np.min(np.abs(ia[:, None] - ib[None, :]))))
chk("V5 the nearest A-B rho pair is astronomically far in ULPs (not a near miss)",
    min(ulps) > 10 ** 12, f"minimum ULP distance per block = {ulps}")

# ---------------------------------------------------------------- V6 boundary mask disjointness
d = []
for s in DEV:
    st = states[s]
    mem, _ = E.members(st)
    alive = st.rho > 1e-4
    bnd = np.zeros_like(alive)
    for ax in (-2, -1):
        for sh in (1, -1):
            bnd |= alive & ~np.roll(alive, sh, ax)
    comp = np.zeros_like(alive)
    for k in ("A", "B"):
        ys, xs = mem[k]
        comp[ys, xs] = True
    d.append((s, int(bnd.sum()), int(comp.sum()), int((bnd & comp).sum())))
chk("V6 EEFCA's boundary-mask conclusion holds under an EXACT inventory (not the withdrawn "
    "incommensurability argument)", all(x[3] == 0 for x in d),
    f"(seed, boundary cells, component cells, intersection) = {d}")
chk("V6b the corrigendum records the withdrawal of the incommensurability argument",
    "retiré" in open("EEFCA_CORRIGENDUM.md", encoding="utf-8").read()
    and "incommensurab" in open("EEFCA_CORRIGENDUM.md", encoding="utf-8").read().lower())

# ---------------------------------------------------------------- V7 gain-zero has no face ledger
tr = ast.parse(src)
ft = [n for n in ast.walk(tr) if isinstance(n, ast.FunctionDef) and n.name == "_face_transport"][0]
zero_branch_returns_lap = any(
    isinstance(n, ast.If) and "gain == 0.0" in ast.unparse(n.test)
    and any("return lap(X)" in ast.unparse(b) for b in n.body) for n in ast.walk(ft))
chk("V7 the executable returns the fused lap() stencil at native gain zero",
    zero_branch_returns_lap, "established by AST, not by reading")

X = states[DEV[0]].c.copy()
one = np.ones_like(X)


def face_form(Xf, kf_field):
    out = np.zeros_like(Xf)
    faces = {}
    for axis in (-2, -1):
        kf = 0.5 * (kf_field + np.roll(kf_field, -1, axis))
        fl = kf * (np.roll(Xf, -1, axis) - Xf)
        faces[axis] = fl
        out += fl - np.roll(fl, 1, axis)
    return out, faces


ff, _ = face_form(X, one)
lp = lap(X)
chk("V7b a kappa==1 face ledger does NOT reproduce lap() bit for bit, so an OFF-arm ledger "
    "would have to be reconstructed", not np.array_equal(ff.view(np.uint8), lp.view(np.uint8)),
    f"cells differing = {int((ff != lp).sum())}/{X.size}, "
    f"max |diff| = {float(np.abs(ff - lp).max()):.3e}")

kz = PE.kappa(PE.z_field(states[DEV[0]]), 1.0 / 3.0)
on, onf = face_form(X, kz)
rec = np.zeros_like(X)
for axis in (-2, -1):
    rec += onf[axis] - np.roll(onf[axis], 1, axis)
chk("V7c in the ON arms the face ledger DOES reconstruct its own divergence bit for bit",
    np.array_equal(rec.view(np.uint8), on.view(np.uint8)))

# ---------------------------------------------------------------- V8 scope discipline
chk("V8 no held-out artefact was created or read",
    not any(os.path.exists(p) for p in
            ("/home/claude/sweep/ETPC/etpc_HELDOUT.pkl", "heldout.pkl",
             "checkpoints/dev_NEAR_62000.npz"))
    and not any(f.startswith("dev_NEAR") or "62" in f for f in os.listdir(CK)),
    f"checkpoint dir contains only {sorted(os.listdir(CK))[:4]} ...")
starts = B0["engine_starts"]["n"] + C0["engine_starts"]["n"]
chk("V8b total engine starts are within the qualification cap of 24", starts <= 24,
    f"total = {starts} (B0 {B0['engine_starts']['n']} + C0 {C0['engine_starts']['n']})")
chk("V8c only development-exposed seeds were advanced",
    all(s in (61000, 61001, 61002, 61003)
        for tag in B0["engine_starts"]["log"] + C0["engine_starts"]["log"]
        for s in [int(tag.split("_")[-1])]))
txt = open("REPORT_ETNBFC.md", encoding="utf-8").read()
chk("V8d the report does not claim an effect or an absence of effect",
    "NOT_TESTED" in txt and "pas d'effet" not in txt.replace("« pas d'effet »", ""))

# ---------------------------------------------------------------- V9 the weak alternative is only recorded
w = json.load(open("etnbfc_weak_alternative.json"))
chk("V9 the inequality-admissible alternative was measured but NOT used as the operator",
    all(r["exact_rho_match_pairs"] == 0 for r in w)
    and "n'a pas été utilisée" in txt,
    f"admissible fraction per block = {[round(r['admissible_pairs_frac_of_all_ij'],3) for r in w]}")

json.dump({"rows": ROWS, "n": len(ROWS), "n_pass": sum(r["PASS"] for r in ROWS),
           "ALL_PASS": OK, "engine_starts_this_programme": starts},
          open("etnbfc_verify.json", "w"), indent=1)
for r in ROWS:
    print(("PASS " if r["PASS"] else "FAIL ") + r["check"]
          + (f"\n        [{r['detail']}]" if r["detail"] else ""))
print(f"\n{sum(r['PASS'] for r in ROWS)}/{len(ROWS)} verification checks passed; "
      f"engine starts = {starts}")
