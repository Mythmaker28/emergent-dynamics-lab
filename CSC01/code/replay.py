"""CSC01 — bit-exact replay of an ORR01 arm.

WHAT THIS IS, AND WHAT IT IS NOT
--------------------------------
ORR01 recorded, per arm, the full 29-field scalar series over all 10250 steps and the final
fields of all six species, but only the LAST THREE of its 102 component samples. The spatial
history is therefore absent from the saved raw, while the *state* that produced it is fully
determined by the saved seed, the frozen engine and the frozen protocol.

A replay re-derives that history. It opens no new start in the ORR01 budget, uses no new seed,
draws no new random number that ORR01 did not already draw, and can change no outcome. It is a
DETERMINISTIC DECOMPRESSION of raw already recorded — but only if it is proved to be one. The
proof is mechanical and is run for every arm:

    * the replayed 10250 x 29 series must equal the recorded array EXACTLY (np.array_equal on
      float64, no tolerance), and
    * the six replayed final integer fields must equal the recorded ones EXACTLY.

If both hold, every spatial observable computed here is a measurable function of the recorded
raw state, and Question A remains raw-only. If either fails for an arm, that arm's replay is
DISCARDED and the arm is analysed from the true raw alone.

The replay adds ONE thing to the ORR01 per-step callback: it copies the integer fields into a
buffer. Copying reads the state and consumes no randomness, so it cannot perturb the trajectory
— and the bit-exactness test is what establishes that, rather than the argument.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

import numpy as np

sys.path.insert(0, "/home/claude/ORR01/code")

import kinetics as K            # noqa: E402
import lawspec_v2 as V2         # noqa: E402
import observe                  # noqa: E402
import protocol as P            # noqa: E402

import guard_csc as GC          # noqa: E402

ORR01_RAW = "/home/claude/ORR01/raw"
SPECIES = ("X", "Y", "SX", "SY", "WX", "WY")


def _cfg_for(tag):
    """Recover the exact arm configuration ORR01 used, from the frozen protocol tables."""
    _, name, seedtok = tag.split("/")
    seed = int(seedtok.replace("seed", ""))
    cfg = dict(P.ARMS[name]) if name in P.ARMS else dict(P.CONTROLS[name])
    return name, seed, cfg


def replay(tag, every, keep_species=SPECIES, verbose=False):
    """Re-run the arm `tag` (e.g. 'conf/REPAIRED/seed5001') and return
       {'series', 'final', 'frames', 'steps'} where frames[s] is a dict of L x L int arrays."""
    name, seed, cfg = _cfg_for(tag)
    sp = P.spec_for(**({"phi": cfg["phi"]} if "phi" in cfg else {}))
    rec = observe.Recorder()
    w = V2.fresh_world(seed, sp, lawspec=cfg["lawspec"], rng_mode=cfg["rng_mode"],
                       exchangeable=cfg["exchangeable"], insert_mode=cfg["insert_mode"], rec=rec)
    if cfg["organiser"]:
        V2.seed_one_organiser(w, P.X_SEED)

    frames, steps = {}, []

    def per_step(ww):
        if ww.step % every == 0:
            frames[ww.step] = {s: ww.n[s].copy() for s in keep_species}
            steps.append(ww.step)

    with GC.start("raw_replay", tag, P.HORIZON):
        GC.advance(w, P.HORIZON, per_step=per_step)

    return {"series": rec.array(),
            "final": {s: w.n[s].copy() for s in SPECIES},
            "frames": frames, "steps": steps, "seed": seed, "arm": name, "L": w.L,
            "state_hash_final": w.state_hash()}


def recorded(tag):
    f = os.path.join(ORR01_RAW, tag.replace("/", "__") + ".npz")
    d = np.load(f, allow_pickle=True)
    return {"series": d["series"], "fields": [str(x) for x in d["fields"]],
            "final": {s: d["n%s_final" % s] for s in SPECIES}}


def verify(tag, every=25, verbose=True):
    """Replay and prove bit-exactness. Returns (ok, report, payload)."""
    got = replay(tag, every)
    ref = recorded(tag)
    series_equal = bool(np.array_equal(got["series"], ref["series"]))
    fields_equal = {s: bool(np.array_equal(got["final"][s], ref["final"][s])) for s in SPECIES}
    ok = series_equal and all(fields_equal.values())
    h = hashlib.sha256()
    h.update(np.ascontiguousarray(ref["series"]).tobytes())
    rep = {"tag": tag, "series_shape": list(got["series"].shape),
           "series_bit_identical": series_equal,
           "final_fields_bit_identical": fields_equal,
           "REPLAY_IS_DETERMINISTIC_DECOMPRESSION": ok,
           "recorded_series_sha256": h.hexdigest(),
           "n_frames": len(got["frames"]), "frame_every": every}
    if verbose:
        print(json.dumps(rep, indent=1))
    return ok, rep, got


if __name__ == "__main__":
    t = sys.argv[1] if len(sys.argv) > 1 else "conf/REPAIRED/seed5001"
    e = int(sys.argv[2]) if len(sys.argv) > 2 else 25
    ok, rep, _ = verify(t, e)
    print("OK" if ok else "MISMATCH")
