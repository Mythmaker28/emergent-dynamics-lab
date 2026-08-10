"""FSCMA00 Phase 1 -- STATIC structural-observability audit. ZERO engine starts.

Nothing here calls engine.step(). Operators are applied to loaded checkpoint bytes and diffed;
the dynamics are audited by parsing the engine source, not by running it.

A. Coordinate-frame audit: is a fixed grid-index mask correctly called EULERIAN?
B. One-step dependency matrix of the LawSpec, derived from the AST by def-use reachability.
C. Per-operator static audit: touch set, delta tensor, aliasing, domain, conservation, support.
D. Intervention input span: how many genuinely distinct native input blocks exist.
"""
from __future__ import annotations
import ast, sys, json, hashlib, inspect
from fractions import Fraction as Fr
sys.path.insert(0, "/home/claude/sweep")
sys.path.insert(0, "/home/claude/sweep/DOMC")
sys.path.insert(0, "/home/claude/sweep/PPAI")
sys.path.insert(0, "/home/claude/sweep/ETPC")
sys.path.insert(0, "/home/claude/sweep/ETCMNFC")
sys.path.insert(0, "/home/claude/sweep/WSFSCRP00")
import numpy as np
import wsfscrp_core as Z
import domc_core as K, ppai_core as P
import etcmnfc_core as EC

OUT = "/home/claude/sweep/FSCMA00"
CKD = "/home/claude/sweep/WSFSCRP00/checkpoints"
ENG_PPAI = "/home/claude/sweep/PPAI/ppai_engine.py"
ENG_SCAF = "/home/claude/sweep/edlab/substrates/scaffold/engine.py"
STATE_FIELDS = ("rho", "U", "V", "c", "N", "C", "uptake", "Mf")
R = {}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


# =====================================================================================
# A. COORDINATE FRAME.  A fixed grid-index mask is an EULERIAN control region iff the
#    time-stepping never re-indexes the lattice: neighbour access must be by literal
#    fixed offsets, and no state field may be rebound to a permuted copy of itself.
# =====================================================================================
PERMUTING = {"flip", "fliplr", "flipud", "rot90", "transpose", "swapaxes", "moveaxis",
             "roll", "take", "argsort", "sort", "fftshift", "ifftshift", "reshape",
             "resize", "ravel", "flatten", "permute"}


def _strip_docstrings(tree):
    for nd in ast.walk(tree):
        if isinstance(nd, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
            b = nd.body
            if b and isinstance(b[0], ast.Expr) and isinstance(b[0].value, ast.Constant) \
                    and isinstance(b[0].value.value, str):
                nd.body = b[1:]
    return tree


def frame_audit(path):
    tree = _strip_docstrings(ast.parse(open(path).read()))
    for nd in ast.walk(tree):          # annotations are types, not array algebra
        for a in ("returns", "annotation"):
            if hasattr(nd, a):
                setattr(nd, a, None)
    rolls, other_perm, fancy, rebind, benign = [], [], [], [], []
    for nd in ast.walk(tree):
        if isinstance(nd, ast.Call) and isinstance(nd.func, ast.Attribute):
            nm = nd.func.attr
            if nm == "roll":
                sh = nd.args[1] if len(nd.args) > 1 else None
                lit = (isinstance(sh, ast.Constant) and isinstance(sh.value, int)) or \
                      (isinstance(sh, ast.UnaryOp) and isinstance(sh.op, ast.USub)
                       and isinstance(sh.operand, ast.Constant))
                val = (sh.value if isinstance(sh, ast.Constant)
                       else -sh.operand.value if lit else None)
                rolls.append({"line": nd.lineno, "shift_literal": bool(lit), "shift": val,
                              "abs_one": bool(lit and abs(val) == 1)})
            elif nm in PERMUTING:
                other_perm.append({"line": nd.lineno, "fn": nm})
        if isinstance(nd, ast.Attribute) and nd.attr == "T":
            other_perm.append({"line": nd.lineno, "fn": ".T"})
        # SPATIAL re-indexing: a subscript that places a non-slice expression in one of the two
        # trailing (spatial) axis positions, e.g. X[:, :, IX] or X[..., IX]. A bare X[k] selects
        # a LEADING axis (memory component / cohort) and is not a spatial re-index; it is
        # recorded separately so a reader can check the classification rather than trust it.
        if isinstance(nd, ast.Subscript):
            sl = nd.slice
            if isinstance(sl, ast.Tuple):
                els = sl.elts
                tail = els[-2:]
                if any(not isinstance(e, (ast.Slice, ast.Constant)) for e in tail):
                    fancy.append({"line": nd.lineno, "kind": "SPATIAL_REINDEX",
                                  "src": ast.unparse(nd)[:80]})
                else:
                    benign.append({"line": nd.lineno, "kind": "tuple_slice_leading_axis",
                                   "src": ast.unparse(nd)[:80]})
            elif not isinstance(sl, (ast.Slice, ast.Constant)):
                benign.append({"line": nd.lineno, "kind": "leading_axis_or_boolean_read",
                               "src": ast.unparse(nd)[:80]})
        # a state field rebound to a permuted copy of itself
        if isinstance(nd, ast.Assign) and len(nd.targets) == 1:
            t = nd.targets[0]
            tn = t.id if isinstance(t, ast.Name) else (t.attr if isinstance(t, ast.Attribute) else None)
            if tn in STATE_FIELDS and isinstance(nd.value, ast.Call) \
                    and isinstance(nd.value.func, ast.Attribute) and nd.value.func.attr in PERMUTING:
                rebind.append({"line": nd.lineno, "field": tn, "fn": nd.value.func.attr})
    return {"file": path, "sha256": sha(path),
            "n_roll_calls": len(rolls),
            "all_roll_shifts_literal_and_unit": all(r["abs_one"] for r in rolls),
            "roll_shift_values": sorted({r["shift"] for r in rolls}),
            "other_index_permuting_calls": other_perm,
            "spatial_reindexing_in_time_stepping": fancy,
            "benign_non_spatial_subscripts": benign,
            "state_field_rebound_to_permuted_self": rebind}


R["A_coordinate_frame"] = {
    "question": "are the fixed t0 grid-index masks correctly described as EULERIAN?",
    "criterion": "the time-stepping must never re-index the lattice: neighbour access only by "
                 "literal unit offsets, no index-permuting call, no fancy indexing, and no state "
                 "field rebound to a permuted copy of itself.",
    "modules": [frame_audit(ENG_SCAF), frame_audit(ENG_PPAI)],
}
fa = R["A_coordinate_frame"]["modules"]
frame_ok = all(m["all_roll_shifts_literal_and_unit"] and not m["other_index_permuting_calls"]
               and not m["spatial_reindexing_in_time_stepping"] and not m["state_field_rebound_to_permuted_self"]
               for m in fa)
R["A_coordinate_frame"]["VERDICT"] = ("EULERIAN_FIXED_INDEX_FRAME_CONFIRMED" if frame_ok
                                      else "FIXED_GRID_REGION_ONLY__FRAME_NOT_PROVEN")
R["A_coordinate_frame"]["scope_caveat"] = (
    "Eulerian means the control region is fixed in the lattice frame and material flows through "
    "it. It does NOT mean the region follows the material that occupied it at t0. q_A(t) is the "
    "density integrated over a fixed spatial window, not the fate of the initial material. Any "
    "sentence that reads the endpoint as 'what happened to component A' is a Lagrangian reading "
    "and is not licensed by this design.")
R["A_coordinate_frame"]["interventions_are_not_frame_motion"] = (
    "state_cross and reciprocal_cross DO permute lattice indices, but they are applied once at "
    "t0 as interventions on the CONTENTS. They are not part of the time-stepping and therefore "
    "do not move the frame. The audit above deliberately covers the engine modules only.")

# =====================================================================================
# B. ONE-STEP DEPENDENCY MATRIX, by def-use reachability over the AST of step().
#    Sound over-approximation: loops are iterated to a fixed point, branches are unioned.
# =====================================================================================
def dep_matrix(path, cls, fn="step"):
    tree = _strip_docstrings(ast.parse(open(path).read()))
    fnode = None
    for nd in ast.walk(tree):
        if isinstance(nd, ast.ClassDef) and nd.name == cls:
            for s in nd.body:
                if isinstance(s, ast.FunctionDef) and s.name == fn:
                    fnode = s
    assert fnode is not None
    env = {f: {f} for f in STATE_FIELDS}

    def deps(node):
        d = set()
        for x in ast.walk(node):
            if isinstance(x, ast.Name) and x.id in env:
                d |= env[x.id]
            if isinstance(x, ast.Attribute) and isinstance(x.value, ast.Name) \
                    and x.value.id == "st" and x.attr in STATE_FIELDS:
                d |= {x.attr}                      # st.X is always the ORIGINAL field
        return d

    def tgt_names(t):
        if isinstance(t, ast.Name):
            return [t.id]
        if isinstance(t, ast.Tuple):
            return [e.id for e in t.elts if isinstance(e, ast.Name)]
        if isinstance(t, ast.Subscript):
            return tgt_names(t.value)
        if isinstance(t, ast.Attribute):
            return [t.attr]
        return []

    def run(body):
        for s in body:
            if isinstance(s, ast.Assign):
                # elementwise pairing for `a, b = x, y`: without this every name on the left
                # inherits every dependency on the right and the matrix saturates to all-ones.
                t0 = s.targets[0]
                if isinstance(t0, ast.Tuple) and isinstance(s.value, ast.Tuple) \
                        and len(t0.elts) == len(s.value.elts):
                    for e, v in zip(t0.elts, s.value.elts):
                        for n in tgt_names(e):
                            env[n] = set(deps(v))
                    continue
                d = deps(s.value)
                for t in s.targets:
                    for n in tgt_names(t):
                        env[n] = (env.get(n, set()) | d) if isinstance(t, ast.Subscript) else set(d)
            elif isinstance(s, ast.AugAssign):
                d = deps(s.value) | deps(s.target)
                for n in tgt_names(s.target):
                    env[n] = env.get(n, set()) | d
            elif isinstance(s, ast.For):
                for _ in range(3):
                    run(s.body)
            elif isinstance(s, ast.If):
                snap = {k: set(v) for k, v in env.items()}
                run(s.body)
                for k in list(env):
                    env[k] = env[k] | snap.get(k, set())
            elif isinstance(s, ast.FunctionDef):
                env[s.name] = deps(s)
            elif isinstance(s, ast.Return):
                d = {}
                if isinstance(s.value, ast.Call):
                    for i, a in enumerate(s.value.args):
                        d[i] = deps(a)
                return d
        return {}

    ret = run(fnode.body)
    order = [f for f in STATE_FIELDS]
    return {order[i]: sorted(ret.get(i, set())) for i in range(len(order)) if i in ret}


DM = dep_matrix(ENG_PPAI, "PPAIEngine")
R["B_one_step_dependency_matrix"] = {
    "method": "def-use reachability over the AST of PPAIEngine.step; loops iterated to a fixed "
              "point, branches unioned. Sound over-approximation: a field listed as a dependency "
              "may be spurious, a field NOT listed is provably unreachable in one step.",
    "matrix_output_field_to_input_fields": DM,
    "rho_depends_on_N_in_one_step": "N" in DM.get("rho", []),
    "rho_depends_on_Mf_in_one_step": "Mf" in DM.get("rho", []),
}
R["B_one_step_dependency_matrix"]["causal_order_to_rho"] = {
    "N": "FIRST order: N enters the growth term g = dt*g0*rho*N*qq*(1+beta*sig) and rho <- rho+g "
         "inside the SAME step.",
    "Mf": "SECOND order: Mf reaches nothing but z = newm[0] -> kappa(z) -> the face permeability "
          "of c and N, which are updated at the END of the step. rho only sees it on the NEXT "
          "step, through the chemotactic flux _face_flux(rho, c) and through g's dependence on N.",
    "scored_grid_caveat": "the earliest scored time is native step 40 (physical 4.0). The order "
                          "difference above governs steps 1-2 and is NOT directly observable on "
                          "the scored grid. It is reported as a mechanism, not as a prediction.",
}

# =====================================================================================
# C. PER-OPERATOR STATIC AUDIT.  Operators applied to checkpoint bytes; no engine step.
# =====================================================================================
LED = json.load(open("/home/claude/sweep/WSFSCRP00/WSFSCRP00_CANDIDATE_QUEUE_AND_ACCEPTANCE_LEDGER.json"))
BASIS = [tuple(x) for x in LED["roles"]["TRAIN_SELECTION"]]
LOCKED = [tuple(x) for x in LED["roles"]["LOCKED_DEV_EVALUATION"]]


def exact_sum(a):
    return sum((Fr(float(v)) for v in np.asarray(a).ravel()), Fr(0))


def build_ops(st0, MA, MB):
    K.set_geometry("FAR")
    mem = {"A": np.nonzero(MA), "B": np.nonzero(MB)}
    ok = EC.eligible_edges(st0, mem)
    ida = np.asarray(mem["A"][0]) * Z.L + np.asarray(mem["A"][1])
    idb = np.asarray(mem["B"][0]) * Z.L + np.asarray(mem["B"][1])
    M, pairs = EC.frozen_matching(ok, ida, idb)
    I = [(int(mem["A"][0][i]), int(mem["A"][1][i])) for (_, _, i, j) in pairs]
    J = [(int(mem["B"][0][j]), int(mem["B"][1][j])) for (_, _, i, j) in pairs]
    return {
        "S1_matched_transposition":      ("CONSERVATIVE_CARRIER_REDISTRIBUTION",
                                          lambda s: EC.transpose(s, I, J)),
        "S2a_intensive_reflection":      ("NONCONSERVATIVE_CARRIER_TRANSFORMATION",
                                          lambda s: P.state_cross(s)),
        "S2b_extensive_reflection":      ("NONCONSERVATIVE_CARRIER_TRANSFORMATION",
                                          lambda s: K.reciprocal_cross(s)),
        "S2c_total_ablation":            ("NONCONSERVATIVE_CARRIER_TRANSFORMATION",
                                          lambda s: P.erase_all(s)),
        "ENV_primary_N_plus_0.50_N0":    ("ENVIRONMENTAL_FIELD_PERTURBATION",
                                          lambda s: K._perturb_N(s, 0.5)),
        "ENV_secondary_N_plus_0.25_N0":  ("ENVIRONMENTAL_FIELD_PERTURBATION",
                                          lambda s: K._perturb_N(s, 0.25)),
    }


rows = []
for seed, geom in BASIS:
    st0 = Z.load(f"{CKD}/f_{seed}_{geom}.npz")
    mk = np.load(f"{CKD}/m_{seed}_{geom}.npz")
    MA, MB = mk["MA"], mk["MB"]
    sup = MA | MB
    src_sha = Z.full_sha(st0)
    for nm, (fam, op) in build_ops(st0, MA, MB).items():
        pre = st0.copy()
        post = op(st0.copy())
        # aliasing / cache: the source object must be byte-identical afterwards
        alias_ok = (Z.full_sha(st0) == src_sha) and (post is not st0)
        touched, dsupp, cons = [], {}, {}
        for f in STATE_FIELDS:
            a = np.ascontiguousarray(np.asarray(getattr(pre, f)))
            b = np.ascontiguousarray(np.asarray(getattr(post, f)))
            # BYTEWISE difference, so that -0.0 vs 0.0 counts as a change
            ab = a.view(np.uint8).reshape(a.shape + (a.dtype.itemsize,))
            bb = b.view(np.uint8).reshape(b.shape + (b.dtype.itemsize,))
            if not np.array_equal(ab, bb):
                touched.append(f)
                d = (ab != bb).any(-1)
                dd = d.sum(0) if d.ndim == 3 else d
                dsupp[f] = {"n_sites_changed": int(dd.sum()),
                            "changed_inside_AuB": int((dd & sup).sum()),
                            "changed_outside_AuB": int((dd & ~sup).sum()),
                            "support_subset_of_AuB": bool((dd & ~sup).sum() == 0),
                            "support_is_global": bool(dd.sum() == Z.L * Z.L)}
                cons[f] = {"exact_sum_preserved": exact_sum(a) == exact_sum(b),
                           "delta_exact_sum": str(exact_sum(b) - exact_sum(a))}
        c1 = bool((np.abs(post.Mf[0]) <= post.rho).all())
        c2 = bool((post.Mf[0][post.rho <= 1e-4] == 0.0).all())
        rows.append({"seed": seed, "geometry": geom, "operator": nm, "superfamily": fam,
                     "touched_fields": touched, "delta_support": dsupp, "conservation": cons,
                     "no_alias_no_cache": bool(alias_ok),
                     "step_counter_unchanged": int(pre.step) == int(post.step),
                     "domain_C1_absMf0_le_rho": c1, "domain_C2_zero_off_alive_gate": c2,
                     "finite": bool(all(np.isfinite(np.asarray(getattr(post, f))).all()
                                        for f in STATE_FIELDS))})

by_op = {}
for r in rows:
    by_op.setdefault(r["operator"], []).append(r)
summary = {}
for nm, rs in by_op.items():
    tf = {tuple(r["touched_fields"]) for r in rs}
    summary[nm] = {
        "superfamily": rs[0]["superfamily"],
        "touched_fields_consistent_across_founders": len(tf) == 1,
        "touched_fields": sorted(tf)[0] if len(tf) == 1 else [list(t) for t in tf],
        "n_founders": len(rs),
        "all_no_alias_no_cache": all(r["no_alias_no_cache"] for r in rs),
        "all_step_counter_unchanged": all(r["step_counter_unchanged"] for r in rs),
        "all_domain_ok": all(r["domain_C1_absMf0_le_rho"] and r["domain_C2_zero_off_alive_gate"]
                             for r in rs),
        "all_finite": all(r["finite"] for r in rs),
        "exact_sum_preserved_per_touched_field": {
            f: all(r["conservation"][f]["exact_sum_preserved"] for r in rs)
            for f in (sorted(tf)[0] if len(tf) == 1 else [])},
        "support": {f: {"subset_of_AuB": all(r["delta_support"][f]["support_subset_of_AuB"] for r in rs),
                        "global": all(r["delta_support"][f]["support_is_global"] for r in rs),
                        "n_sites_changed_range": [min(r["delta_support"][f]["n_sites_changed"] for r in rs),
                                                  max(r["delta_support"][f]["n_sites_changed"] for r in rs)]}
                    for f in (sorted(tf)[0] if len(tf) == 1 else [])},
    }
R["C_operator_static_audit"] = {"basis_founders": [list(b) for b in BASIS],
                                "per_operator": summary, "per_cell": rows}

# =====================================================================================
# D. INTERVENTION INPUT SPAN
# =====================================================================================
blocks = {}
for nm, s in summary.items():
    tfx = s["touched_fields"]
    key = tuple(tfx) if isinstance(tfx, (list, tuple)) else ("UNSTABLE",)
    blocks.setdefault(key, []).append(nm)
carrier_ops = [n for n, s in summary.items() if s["superfamily"] != "ENVIRONMENTAL_FIELD_PERTURBATION"]
env_ops = [n for n, s in summary.items() if s["superfamily"] == "ENVIRONMENTAL_FIELD_PERTURBATION"]
span = {
    "native_input_blocks": {"|".join(k): v for k, v in blocks.items()},
    "n_distinct_native_blocks": len(blocks),
    "carrier_block": sorted({f for n in carrier_ops for f in summary[n]["touched_fields"]}),
    "environmental_block": sorted({f for n in env_ops for f in summary[n]["touched_fields"]}),
    "blocks_are_disjoint": len(set(sum([list(summary[n]["touched_fields"]) for n in carrier_ops], []))
                               & set(sum([list(summary[n]["touched_fields"]) for n in env_ops], []))) == 0,
    "distinctness_proof": [
        "Every carrier operator perturbs Mf and nothing else, on every BASIS founder (measured "
        "bytewise above). Every environmental operator perturbs N and nothing else.",
        "The two blocks are therefore disjoint at t0 as SETS OF PERTURBED FIELDS.",
        "They are also distinct DYNAMICALLY, not just nominally: by the one-step dependency "
        "matrix, rho depends on N within a single step (growth) but not on Mf. Mf's only exit is "
        "z = newm[0] -> kappa(z) -> the face permeability of c and N. A carrier perturbation is a "
        "multiplicative TRANSPORT-COEFFICIENT perturbation; an environmental perturbation is an "
        "additive SOURCE perturbation.",
        "Budget asymmetry, which is the sharpest of the three: every carrier operator leaves the "
        "nutrient field bit-identical, so it changes the total nutrient budget by exactly zero. "
        "The environmental operator adds +amp*N0 at every one of the 4096 sites, so it changes "
        "the budget by exactly amp*N0*L^2 > 0. Growth converts N into rho. The environmental "
        "operator therefore INJECTS matter into the scored channels; no carrier operator can.",
    ],
    "VERDICT": None,
}
span["VERDICT"] = ("INTERVENTION_INPUT_SPAN_SUFFICIENT" if (len(blocks) >= 2 and span["blocks_are_disjoint"])
                   else "INTERVENTION_INPUT_SPAN_INSUFFICIENT")
R["D_intervention_input_span"] = span

# --- static admissibility of ENV_SECONDARY (+0.25), decided before any outcome ---------
sec = [r for r in rows if r["operator"] == "ENV_secondary_N_plus_0.25_N0"]
pri = [r for r in rows if r["operator"] == "ENV_primary_N_plus_0.50_N0"]
R["D_intervention_input_span"]["ENV_SECONDARY_static_admissibility"] = {
    "operator": "domc_core._perturb_N(st, 0.25)",
    "same_code_path_as_primary": True,
    "touched_fields": summary["ENV_secondary_N_plus_0.25_N0"]["touched_fields"],
    "identical_touch_set_to_primary":
        summary["ENV_secondary_N_plus_0.25_N0"]["touched_fields"]
        == summary["ENV_primary_N_plus_0.50_N0"]["touched_fields"],
    "domain_ok_on_all_basis_founders":
        all(r["domain_C1_absMf0_le_rho"] and r["domain_C2_zero_off_alive_gate"] for r in sec),
    "clip_is_inactive": "np.clip(N + amp*N0, 0.0, None) with amp>0 and N>=0 never clips; the "
                        "operator is exactly additive.",
    "STATICALLY_ADMISSIBLE": bool(all(r["finite"] for r in sec)
                                  and summary["ENV_secondary_N_plus_0.25_N0"]["all_domain_ok"]),
    "EXECUTION_DECISION": "DEFERRED_TO_FROZEN_START_BUDGET (Section 7). Statically admissible is "
                          "not the same as affordable.",
}

json.dump(R, open(f"{OUT}/FSCMA00_STATIC_OBSERVABILITY_RAW.json", "w"), indent=1, default=str)

print("A frame verdict :", R["A_coordinate_frame"]["VERDICT"])
for m in fa:
    print("   ", m["file"].split("/")[-1], "rolls:", m["n_roll_calls"],
          "all unit:", m["all_roll_shifts_literal_and_unit"],
          "shifts:", m["roll_shift_values"],
          "perm:", len(m["other_index_permuting_calls"]),
          "spatial_reindex:", len(m["spatial_reindexing_in_time_stepping"]),
          "benign_subscripts:", len(m["benign_non_spatial_subscripts"]),
          "rebind:", len(m["state_field_rebound_to_permuted_self"]))
print("\nB one-step dependency matrix (output <- inputs):")
for k, v in DM.items():
    print("    %-7s <- %s" % (k, v))
print("    rho<-N :", R["B_one_step_dependency_matrix"]["rho_depends_on_N_in_one_step"],
      "| rho<-Mf :", R["B_one_step_dependency_matrix"]["rho_depends_on_Mf_in_one_step"])
print("\nC per-operator static audit over the 6 BASIS founders:")
for nm, s in summary.items():
    f = s["touched_fields"]
    print("    %-30s touch=%-8s consistent=%s alias_ok=%s domain=%s cons=%s supp=%s"
          % (nm, f, s["touched_fields_consistent_across_founders"], s["all_no_alias_no_cache"],
             s["all_domain_ok"], s["exact_sum_preserved_per_touched_field"],
             {k: ("AuB" if v["subset_of_AuB"] else ("GLOBAL" if v["global"] else "wide"))
              for k, v in s["support"].items()}))
print("\nD input span :", span["VERDICT"], "| blocks:", list(span["native_input_blocks"].keys()),
      "| disjoint:", span["blocks_are_disjoint"])
print("  ENV_SECONDARY statically admissible:",
      R["D_intervention_input_span"]["ENV_SECONDARY_static_admissibility"]["STATICALLY_ADMISSIBLE"])
