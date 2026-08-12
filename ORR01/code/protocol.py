"""ORR01 frozen protocol. Paired comparison, additive control against the repaired LawSpec."""
from __future__ import annotations
import json, time
import numpy as np
import guard, lattice as LAT, lawspec_v2 as V2, observe, gates as G

OUT, RAW = "/home/claude/ORR01/out", "/home/claude/ORR01/raw"

# ---------------- the point, fixed ANALYTICALLY, no calibration
POINT = dict(L=36, CAP=16, S0=3, phi=0.20, omega=0.05, muX=0.004, muY=0.0,
             kX=1.0, kY=0.0, p_hop_X=0.10263340389897246, p_hop_Y=0.10263340389897246)
POINT_PROVENANCE = ("the analytic winner of the MCM01 frozen selection rule (muX = 0.004, "
    "phi = 0.20, ell_X = 2.5). It is reused unchanged so that the additive control reproduces "
    "a configuration already measured, and because the repair introduces NO new parameter: the "
    "exchange reuses phi as its rate and S0 as its set-point. No calibration block is therefore "
    "run and none is needed.")
G0 = LAT.G_body_about_organiser(POINT["p_hop_X"], POINT["p_hop_Y"], POINT["muX"])["G0"]

X_SEED = 4
T_FORM_MAX = 1250          # 5 / muX
T_MAINT = 9000             # see the justification in the pre-freeze plan
HORIZON = T_FORM_MAX + T_MAINT
N_FORM, U_FORM, K_FORM = 30, 3.0, 50
N_KEEP, FRAC_MIN, RUN_MAX = 50, 0.95, 250
FREE_MIN, OCC_TOL = 0.5, 0.05
SAMPLE_EVERY = 100
SEEDS_CONF = (5001, 5002, 5003, 5004, 5005, 5006)
SEEDS_CTRL = (7001, 7002)
CONFIRM_REQUIRED = 5

TH = G.Thresholds(T_FORM_MAX=T_FORM_MAX, T_MAINT=T_MAINT, N_FORM=N_FORM, U_FORM=U_FORM,
                  K_FORM=K_FORM, N_KEEP=N_KEEP, FRAC_MIN=FRAC_MIN, RUN_MAX=RUN_MAX, G0=G0,
                  FREE_MIN=FREE_MIN, OCC_TOL=OCC_TOL)

ARMS = {
 "ADDITIVE_CONTROL": dict(lawspec=V2.LAWSPEC_V1_ADDITIVE, rng_mode="split_feed_stream",
    exchangeable=V2.EXCHANGEABLE_DEFAULT, insert_mode="reservoir", organiser=True,
    predicted="OCCUPANCY_RATCHET"),
 "REPAIRED": dict(lawspec=V2.LAWSPEC_V2_EXCHANGE, rng_mode="split_feed_stream",
    exchangeable=V2.EXCHANGEABLE_DEFAULT, insert_mode="reservoir", organiser=True,
    predicted="MAINTENANCE_ACHIEVED"),
}
CONTROLS = {
 "NO_ORGANISER_V2": dict(lawspec=V2.LAWSPEC_V2_EXCHANGE, rng_mode="split_feed_stream",
    exchangeable=V2.EXCHANGEABLE_DEFAULT, insert_mode="reservoir", organiser=False,
    predicted="NO_FORMATION",
    rationale="n_X = 0 is an exact invariant manifold; nothing may appear"),
 "WASHOUT_POOL_INCLUDES_BODY": dict(lawspec=V2.LAWSPEC_V2_EXCHANGE,
    rng_mode="split_feed_stream", exchangeable=V2.EXCHANGEABLE_WITH_BODY,
    insert_mode="reservoir", organiser=True, predicted=None,
    rationale="the exclusion of the body from the exchangeable pool is the one modelling "
              "choice the repair makes; this control removes it, adding a washout death term, "
              "so the result cannot rest on the exclusion"),
 "SHAM_REINSERT": dict(lawspec=V2.LAWSPEC_V2_EXCHANGE, rng_mode="split_feed_stream",
    exchangeable=V2.EXCHANGEABLE_DEFAULT, insert_mode="sham_reinsert", organiser=True,
    predicted="MATERIAL_COLLAPSE",
    rationale="occupancy is conserved exactly, as in the repair, but nothing is renewed. "
              "Isolates renewal from the mere conservation of occupancy"),
 "NO_EXCHANGE_AT_ALL": dict(lawspec=V2.LAWSPEC_V2_EXCHANGE, rng_mode="split_feed_stream",
    exchangeable=V2.EXCHANGEABLE_DEFAULT, insert_mode="reservoir", organiser=True, phi=0.0,
    predicted="MATERIAL_COLLAPSE",
    rationale="phi = 0 switches the exchange off entirely; the resource is consumed and never "
              "renewed"),
}

def spec_for(**over):
    d = dict(POINT); d.update(over); return V2.spec_with(**d)

def run_arm(cls, tag, cfg, seed):
    sp = spec_for(**({"phi": cfg["phi"]} if "phi" in cfg else {}))
    rec = observe.Recorder()
    w = V2.fresh_world(seed, sp, lawspec=cfg["lawspec"], rng_mode=cfg["rng_mode"],
                       exchangeable=cfg["exchangeable"], insert_mode=cfg["insert_mode"], rec=rec)
    if cfg["organiser"]:
        V2.seed_one_organiser(w, X_SEED)
    rng0 = json.loads(json.dumps(w.rng.bit_generator.state, default=str))
    gate = G.RuntimeGate(TH)
    comp = []
    F = observe.Recorder.FIELDS
    def per_step(ww):
        r = rec.rows[-1]
        gate.step(r[F.index("N_X")], r[F.index("N_Y")], r[F.index("u_nX_at_org")],
                  r[F.index("c_X_per_org")], r[F.index("free_at_org")], r[F.index("O_total")])
        if ww.step % SAMPLE_EVERY == 0:
            cr = observe.component_report(ww); comp.append(cr)
            gate.sample((cr["main"] or {}).get("N_X"), (cr["main"] or {}).get("wraps", True))
    t0 = time.time()
    with guard.start(cls, tag, HORIZON):
        guard.advance(w, HORIZON, per_step=per_step)
    wall = time.time() - t0
    arr = rec.array()
    np.savez_compressed("%s/%s.npz" % (RAW, tag.replace("/", "__")), series=arr,
        fields=np.array(F), nX_final=w.n["X"], nY_final=w.n["Y"], nSX_final=w.n["SX"],
        nSY_final=w.n["SY"], nWX_final=w.n["WX"], nWY_final=w.n["WY"])
    rt = gate.result()
    ph = G.posthoc_gate(arr, F, TH, comp)
    agree = (rt["classification"] == ph["classification"] and rt["PASS"] == ph["PASS"]
             and rt["formed_at"] == ph["formed_at"])
    o = arr[:, F.index("O_total")]
    return {"class": cls, "tag": tag, "seed": seed, "arm": cfg, "spec": sp.as_dict(),
            "wall_seconds": wall, "steps": int(w.step), "raw_npz": tag.replace("/", "__")+".npz",
            "rng_state_initial": rng0,
            "rng_state_final": json.loads(json.dumps(w.rng.bit_generator.state, default=str)),
            "gate_runtime": rt, "gate_posthoc": ph, "GATES_AGREE": bool(agree),
            "classification": ph["classification"], "PASS": bool(ph["PASS"]),
            "occupancy": {"O_first": float(o[0]), "O_last": float(o[-1]),
                          "O_min": float(o.min()), "O_max": float(o.max()),
                          "drift": float(abs(o[-1]-o[0])/max(o[0],1)),
                          "exactly_constant": bool(o.std() == 0.0)},
            "flux": {"in": float(arr[-1, F.index("flux_in")]),
                     "out": float(arr[-1, F.index("flux_out")]),
                     "displaced": {k: int(v) for k, v in w.displaced.items() if v}},
            "N_X": {"max": float(arr[:, F.index("N_X")].max()),
                    "final": float(arr[-1, F.index("N_X")]),
                    "window_mean": float(arr[T_FORM_MAX:, F.index("N_X")].mean())},
            "component_samples": comp[-3:], "n_component_samples": len(comp)}

def constants():
    return {"POINT": POINT, "POINT_PROVENANCE": POINT_PROVENANCE, "G0_relative_walk": G0,
            "X_SEED": X_SEED, "T_FORM_MAX": T_FORM_MAX, "T_MAINT": T_MAINT, "HORIZON": HORIZON,
            "gate_thresholds": TH.as_dict(), "SAMPLE_EVERY": SAMPLE_EVERY,
            "SEEDS_confirmation": list(SEEDS_CONF), "SEEDS_control": list(SEEDS_CTRL),
            "CONFIRM_REQUIRED": CONFIRM_REQUIRED, "arms": ARMS, "controls": CONTROLS,
            "start_caps": dict(guard.CAPS),
            "no_calibration_block": "the repair introduces no new parameter; the point is the "
                                    "MCM01 analytic winner, reused unchanged",
            "pairing": "each confirmation seed is run in BOTH arms with the same seed and the "
                       "same initial condition, and both arms draw the feed or exchange from a "
                       "second RNG stream so that diffusion, reaction and decay consume the "
                       "first stream identically until the states diverge",
            "sequential_stopping_rule": [
              "1 provenance not self-contained -> STOP", "2 closure indeterminate -> STOP",
              "3 no admissible repair -> STOP", "4 v2 fails an invariance test -> STOP",
              "5 the two gate implementations disagree anywhere -> STOP",
              "6 the additive control does not reproduce the ratchet on the first paired "
              "seed -> STOP",
              "7 the repair does not remove the ratchet on the first paired seed -> STOP",
              "8 no cloud forms in the repaired arm on the first two seeds -> STOP",
              "9 all repaired clouds collapse over the first three seeds -> STOP",
              "10 any logging defect or ledger divergence -> STOP",
              "11 controls run only if at least three confirmation pairs were executed"],
            "success_criterion": "at least %d of %d repaired seeds MAINTENANCE_ACHIEVED AND at "
                                 "least %d of %d additive control seeds NOT "
                                 "MAINTENANCE_ACHIEVED" % (CONFIRM_REQUIRED, len(SEEDS_CONF),
                                                           CONFIRM_REQUIRED, len(SEEDS_CONF)),
            "raw_variables": list(observe.Recorder.FIELDS) + [
              "final fields of all six species", "per-component id, cells, N_X, N_Y, mass, "
              "density, circular centre of mass, radius of gyration, extent, gap to the "
              "periodic image, wrap flag", "escapees", "initial and final RNG state", "seed",
              "full LawSpec", "displaced species counts", "flux in and out"]}
