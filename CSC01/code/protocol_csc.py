"""CSC01 protocol. Every threshold comes from localization_gate.yaml; none is written here."""
from __future__ import annotations

import ast
import inspect
import json
import sys
import time

import numpy as np

sys.path.insert(0, "/home/claude/ORR01/code")
sys.path.insert(0, "/home/claude/CSC01/code")

import kinetics as K             # noqa: E402
import observe as OBS            # noqa: E402
import protocol as ORR           # noqa: E402  (only for the frozen POINT; nothing is run)

import gatelib as GL             # noqa: E402
import guard_csc as GC           # noqa: E402
import lawspec_v3 as V3          # noqa: E402
import spatial as SP             # noqa: E402

OUT, RAW = "/home/claude/CSC01/out", "/home/claude/CSC01/raw"
SPEC = GL.load()
SPEC["_p_hop"] = ORR.POINT["p_hop_X"]
SPEC["_mu"] = ORR.POINT["muX"]
POINT = dict(ORR.POINT)                       # the frozen ORR01 design point, reused unchanged
X_SEED = ORR.X_SEED

G_ = SPEC["geometry"]
W_ = SPEC["window"]
CORE_R = float(G_["core_radius_cells"])
ELL = float(G_["ell_X_reference"])


def spec_for(**over):
    d = dict(POINT)
    d.update(over)
    return V3.V2.spec_with(**d)


# ------------------------------------------------------------------ the AST audit of axis 4
FORBIDDEN_TOKENS = ("gate", "PASS", "classification", "classify", "score", "verdict", "result",
                    "posthoc", "Online", "success", "threshold", "spec", "yaml")
ALLOWED_SELF_ATTRS = {"n", "sp", "rng", "rng_feed", "lam", "cohesion", "L", "step",
                      "deaths_avoided_estimate", "rec", "lawspec", "rng_mode", "exchangeable",
                      "insert_mode", "flux_in", "flux_out", "displaced", "removed_waste",
                      "_decay_core", "free", "occ"}


def audit_no_score_reading(func=V3.WorldV3._decay_core):
    """Static audit: the mechanism's operator may read species fields and frozen Spec constants,
    and nothing that carries an outcome."""
    src = inspect.getsource(func)
    src = "\n".join(l[4:] if l.startswith("    ") else l for l in src.splitlines())
    tree = ast.parse(src)
    names, self_attrs, subs = set(), set(), set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
        if isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name) and node.value.id == "self":
                self_attrs.add(node.attr)
            else:
                names.add(node.attr)
        if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
            subs.add(node.slice.value)
    bad_tokens = sorted(n for n in (names | self_attrs)
                        if any(t.lower() in str(n).lower() for t in FORBIDDEN_TOKENS))
    bad_attrs = sorted(a for a in self_attrs if a not in ALLOWED_SELF_ATTRS)
    bad_species = sorted(s for s in subs if isinstance(s, str) and s not in K.ALL_OCC)
    ok = not bad_tokens and not bad_attrs and not bad_species
    return {"PASS": bool(ok), "self_attributes_read": sorted(self_attrs),
            "species_subscripts": sorted(str(s) for s in subs),
            "forbidden_tokens_found": bad_tokens,
            "undeclared_self_attributes": bad_attrs,
            "undeclared_species": bad_species,
            "audited": "%s.%s" % (func.__qualname__.split(".")[0], func.__name__)}


# ------------------------------------------------------------------ frame record
def frame_record(w):
    fr = SP.frame_report(w.n["X"], w.n["Y"], ELL)
    fr.pop("_labels")
    fr.pop("_comp")
    rec = {"step": int(w.step), "N_X": int(fr["N_X"]), "r50": fr["r50"], "r80": fr["r80"],
           "Rg": fr["Rg_pairwise"], "any_component_wraps": bool(fr["any_component_wraps"]),
           "organiser_y": int(fr["organiser_y"]), "organiser_x": int(fr["organiser_x"]),
           "main_mass_fraction": fr["main_mass_fraction"],
           "n_eff_components": fr["n_eff_components"], "n_components": int(fr["n_components"]),
           "main_N_X": int(fr["main_N_X"]),
           "main_geodesic_diameter": int(fr["main_geodesic_diameter"])}
    cy, cx = fr["centre_y"], fr["centre_x"]
    if isinstance(cy, (int, np.integer)):
        rec["centre_y"], rec["centre_x"] = int(cy), int(cx)
        nX = w.n["X"]
        rec["core_fraction"] = SP.mass_within(nX, cy, cx, CORE_R) / max(float(nX.sum()), 1e-9)
        d = SP.dist_field(w.L, cy, cx)
        ball = d <= CORE_R
        free = np.maximum(w.sp.CAP - w.occ(), 0)
        rec["core_free_mean"] = float(free[ball].mean())
    else:
        rec["centre_y"] = rec["centre_x"] = -1
        rec["core_fraction"] = float("nan")
        rec["core_free_mean"] = float("nan")
    return rec


# ------------------------------------------------------------------ arms
def arms(lam):
    return {
        "C0_NO_CHANGE": dict(cohesion=None, lam=0.0, organiser=True,
                             predicted="LOCALISED_BUT_NOT_COHESIVE"),
        "C3_NEIGHBOUR_PROTECTED_DECAY": dict(cohesion=V3.C3, lam=lam, organiser=True,
                                             predicted=None),
    }


def controls(lam):
    return {
        "NO_ORGANISER": dict(cohesion=V3.C3, lam=lam, organiser=False,
                             predicted="NO_FORMATION",
                             rationale="n_X = 0 is an exact invariant manifold; the mechanism "
                                       "only lowers a death probability and cannot create X"),
        "LAMBDA_ZERO": dict(cohesion=V3.C3, lam=0.0, organiser=True,
                            predicted="LOCALISED_BUT_NOT_COHESIVE",
                            rationale="the mechanism switched off by its own parameter. It must "
                                      "reproduce the reference arm, which isolates lambda as "
                                      "the only cause of any difference"),
    }


def run_arm(cls, tag, cfg, seed, n1tab, audit_pass, horizon=None):
    sp = spec_for()
    rec = OBS.Recorder()
    w = V3.fresh_world(seed, sp, lawspec=V3.V2.LAWSPEC_V2_EXCHANGE,
                       rng_mode="split_feed_stream", exchangeable=V3.V2.EXCHANGEABLE_DEFAULT,
                       insert_mode="reservoir", rec=rec,
                       cohesion=cfg["cohesion"], lam=cfg["lam"])
    if cfg["organiser"]:
        V3.seed_one_organiser(w, X_SEED)
    rng0 = json.loads(json.dumps(w.rng.bit_generator.state, default=str))
    online = GL.OnlineGate(SPEC, seed, no_score_reading=audit_pass)
    frames, n1thr, corefree = [], {}, {}
    F = OBS.Recorder.FIELDS
    H = int(horizon or W_["HORIZON"])

    def per_step(ww):
        r = rec.rows[-1]
        online.step(r[F.index("N_X")], r[F.index("N_Y")], r[F.index("u_nX_at_org")],
                    r[F.index("free_at_org")], r[F.index("O_total")],
                    r[F.index("deaths_X")], r[F.index("accepted_births_X")])
        if ww.step % W_["SAMPLE_EVERY"] == 0:
            fr = frame_record(ww)
            frames.append(fr)
            t = GL.n1_q01_r80(n1tab, fr["N_X"]) if fr["N_X"] > 0 else float("nan")
            n1thr[fr["step"]] = t
            corefree[fr["step"]] = fr["core_free_mean"]
            online.frame(fr, t, fr["core_free_mean"])

    t0 = time.time()
    with GC.start(cls, tag, H):
        GC.advance(w, H, per_step=per_step)
    wall = time.time() - t0
    arr = rec.array()
    np.savez_compressed("%s/%s.npz" % (RAW, tag.replace("/", "__")), series=arr,
                        fields=np.array(F), nX_final=w.n["X"], nY_final=w.n["Y"],
                        nSX_final=w.n["SX"], nSY_final=w.n["SY"], nWX_final=w.n["WX"],
                        nWY_final=w.n["WY"])
    on = online.result()
    ph = GL.posthoc_gate(SPEC, arr, list(F), frames, n1thr, corefree, seed,
                         no_score_reading=audit_pass)
    cmp_ = GL.compare(on, ph)
    o = arr[:, F.index("O_total")]
    return {"class": cls, "tag": tag, "seed": seed, "arm": {k: str(v) for k, v in cfg.items()},
            "lambda": cfg["lam"], "cohesion": str(cfg["cohesion"]),
            "spec": sp.as_dict(), "wall_seconds": wall, "steps": int(w.step),
            "raw_npz": tag.replace("/", "__") + ".npz",
            "rng_state_initial": rng0,
            "rng_state_final": json.loads(json.dumps(w.rng.bit_generator.state, default=str)),
            "gate_online": on, "gate_posthoc": ph, "GATES_AGREE": cmp_["AGREE"],
            "gate_differences": cmp_["differences"],
            "classification": ph["classification"], "PASS": bool(ph["PASS"]),
            "occupancy": {"O_first": float(o[0]), "O_last": float(o[-1]),
                          "drift": float(abs(o[-1] - o[0]) / max(o[0], 1)),
                          "exactly_constant": bool(o.std() == 0.0)},
            "N_X": {"max": float(arr[:, F.index("N_X")].max()),
                    "final": float(arr[-1, F.index("N_X")]),
                    "window_mean": float(arr[W_["T_FORM_MAX"]:, F.index("N_X")].mean())},
            "state_hash_final": w.state_hash(),
            "frames": frames}
