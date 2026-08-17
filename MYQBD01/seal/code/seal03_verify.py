"""MYQBD01 FINAL SEAL §16 — main-operator INDEPENDENT verification of the reviewer's confirmed
defects. Nothing is adjudicated on the reviewer's word. Re-derived from raw bytes and source.

No engine. Read-only.
"""
from __future__ import annotations
import ast, glob, json, os, re
import numpy as np

RAW = "/home/claude/OBFOR01/raw"
OUT = "/home/claude/MYQBD01/seal/out"
BURN_IN, HORIZON, S0, PHI = 2000, 11000, 3, 0.2
R = {}


def series(p):
    z = np.load(p, allow_pickle=True)
    f = [str(x) for x in z["fields"]]
    return z, f, z["series"]


mob = sorted(glob.glob(f"{RAW}/M__*.npz"))
sta = sorted(glob.glob(f"{RAW}/S__*.npz"))

# ---------- F10: with kY = 0, does any Y birth ever occur? ----------
nY_always_one, org_always_one, tot_steps = True, True, 0
for p in mob + sta:
    z, f, s = series(p)
    nY = s[:, f.index("N_Y")]
    noc = s[:, f.index("n_org_cells")]
    tot_steps += nY.size
    nY_always_one &= bool(np.all(nY == 1))
    org_always_one &= bool(np.all(noc == 1))
R["F10_N_Y_IDENTICALLY_ONE"] = {"all_arms": nY_always_one, "n_org_cells_always_1": org_always_one,
                                "steps_checked": tot_steps,
                                "reading": "kY = 0 => no Y birth in any arm; the founder is the "
                                           "only Y that ever exists"}

# ---------- F16: effective SY mean-reversion at the organiser cell (static arms) ----------
slopes = []
for p in sta:
    z, f, s = series(p)
    y = s[BURN_IN:HORIZON, f.index("nSY_at_org")].astype(float)
    d = np.diff(y)
    x = S0 - y[:-1]
    slopes.append(float(np.dot(x - x.mean(), d - d.mean()) / np.dot(x - x.mean(), x - x.mean())))
R["F16_SY_MEAN_REVERSION"] = {"per_arm_slopes_static": slopes,
                              "mean": float(np.mean(slopes)), "sd": float(np.std(slopes, ddof=1)),
                              "claimed_phi": PHI,
                              "ratio_measured_over_claimed": float(np.mean(slopes) / PHI)}

# ---------- F17: depletion conditional on a birth being possible ----------
un, co, cc = [], [], []
for p in mob:
    z, f, s = series(p)
    w = s[BURN_IN:HORIZON]
    nsy = w[:, f.index("nSY_at_org")].astype(float)
    cy = w[:, f.index("cand_Y_at_org")].astype(float)
    m = cy >= 1
    un.append(nsy.mean()); co.append(nsy[m].mean()); cc.append(cy[m].mean())
R["F17_DEPLETION"] = {"uncond_mean_nSY_mobile": float(np.mean(un)),
                      "uncond_depletion_pct": 100.0 / float(np.mean(un)),
                      "cond_mean_nSY_given_candY_ge_1": float(np.mean(co)),
                      "cond_mean_candY_given_ge_1": float(np.mean(cc)),
                      "cond_depletion_pct": 100.0 / float(np.mean(co))}

# ---------- F20: mean candidate pool ----------
cy_all, nx_all, q_all = [], [], []
for p in mob:
    z, f, s = series(p)
    w = s[BURN_IN:HORIZON]
    cy_all.append(w[:, f.index("cand_Y_at_org")].mean())
    nx_all.append(w[:, f.index("u_nX_at_org")].mean())
    q_all.append(w[:, f.index("Q")].mean())
R["F20_POOL"] = {"mean_cand_Y_at_org_mobile": float(np.mean(cy_all)),
                 "c_box_used": 3, "ratio_c_box_over_mean": 3.0 / float(np.mean(cy_all)),
                 "mean_u_nX_at_org": float(np.mean(nx_all)),
                 "mean_Q_mobile": float(np.mean(q_all)),
                 "witness_exposure_c_times_nX": 12, "ratio_witness_over_meanQ":
                     12.0 / float(np.mean(q_all))}

# ---------- F08: source_substep_ledger column semantics ----------
z = np.load(mob[0], allow_pickle=True)
ssl = z["source_substep_ledger"]
L = int(z["nX_final"].shape[0])
coordish = [j for j in range(ssl.shape[1]) if ssl[:, j].min() >= 0 and ssl[:, j].max() < L]
moved = int((ssl[:, 2:4] != ssl[:, 4:6]).any(axis=1).sum()) if ssl.shape[1] >= 6 else -1
cells = int(np.unique(ssl[:, 4:6], axis=0).shape[0]) if ssl.shape[1] >= 6 else -1
src_txt = open("/home/claude/OBFOR01/code/run_obfor01.py").read()
hdr = [ln.strip() for ln in src_txt.splitlines()
       if "source_substep" in ln or "hop_ledger" in ln or "birth_substep" in ln][:8]
R["F08_SUBSTEP_LEDGER"] = {"shape": list(ssl.shape),
                           "columns_within_lattice_range": coordish,
                           "rows_where_org_cell_moved": moved,
                           "distinct_org_cells_visited": cells,
                           "writer_lines": hdr,
                           "IS_POSITION_RESOLVED": len(coordish) >= 4}

# ---------- F05: IAT tail ----------
def iat(x, cap=2000):
    x = x - x.mean()
    n = x.size
    v = float(np.dot(x, x) / n)
    if v <= 0: return 1.0
    s, k = 0.0, 1
    while k < cap:
        g = float(np.dot(x[:-k], x[k:]) / n) / v
        if g <= 0: break
        s += g; k += 1
    return 1 + 2 * s
iats = {}
for p in mob + sta:
    z, f, s = series(p)
    iats[os.path.basename(p)[:-4]] = iat(s[BURN_IN:HORIZON, f.index("Q")].astype(float))
mv = {k: v for k, v in iats.items() if k.startswith("M")}
sv = {k: v for k, v in iats.items() if k.startswith("S")}
R["F05_IAT"] = {"mobile_mean": float(np.mean(list(mv.values()))),
                "mobile_max": max(mv.items(), key=lambda kv: kv[1]),
                "static_mean": float(np.mean(list(sv.values()))),
                "static_max": max(sv.items(), key=lambda kv: kv[1]),
                "mobile_ratio_max_over_mean": max(mv.values()) / float(np.mean(list(mv.values())))}

# ---------- F27 / F28 / F25: static source audits ----------
code = sorted(glob.glob("/home/claude/edl/MYQBD01/code/*.py"))
with_sent = [os.path.basename(p) for p in code
             if re.search(r"SENT\.install|pmcr01_sentinel", open(p).read())]
ast_uses = [os.path.basename(p) for p in code if "ast." in open(p).read()]
seeders = []
for p in ("/home/claude/ORR01/code/kinetics.py", "/home/claude/ORR01/code/observe.py",
          "/home/claude/ORR01/code/lawspec_v2.py", "/home/claude/OBTC02/code/engine_obtc.py"):
    for i, ln in enumerate(open(p).read().splitlines(), 1):
        if ln.startswith("def seed_one_organiser"):
            seeders.append("%s:%d" % (p, i))
sent = open("/home/claude/PMCR01/code/pmcr01_sentinel.py").read()
patched = re.findall(r"(\w+)\.seed_one_organiser\s*=", sent)
R["F27_F28_F25"] = {"MYQBD01_modules": len(code),
                    "modules_installing_sentinel": with_sent,
                    "modules_using_ast": ast_uses,
                    "seed_one_organiser_definitions": seeders,
                    "sentinel_patches_namespaces": patched,
                    "observe_is_patched": "OBS" in patched or "observe" in patched}

json.dump(R, open(f"{OUT}/SEAL03_OPERATOR_VERIFICATION.json", "w"), indent=1, default=str)
for k, v in R.items():
    print("=== %s" % k)
    print(json.dumps(v, indent=1, default=str)[:900])
