"""RPP97 — the capability test. Runs BEFORE any archive is opened.

A statistic that has never been shown able to take the value contradicting the hypothesis is not
a test. So S1 is exercised on three synthetic bodies whose answer is known by construction:

  (a) core-depleted -> S1 must be > 0   the mechanism's signature
  (b) core-enriched -> S1 must be < 0   THE REFUTING VALUE; this is the one that matters
  (c) uniform       -> S1 must be ~ 0

If (b) does not come out negative the statistic cannot express the refuting observation, and the
measurement is not performed.
"""
from __future__ import annotations
import os, sys, json, subprocess
import numpy as np
REPO = os.environ.get("TBRT02_REPO", "/home/claude/edl")
sys.path.insert(0, os.path.join(REPO, "RPP97/code"))
import rpp97_stats as S


def disc_body(radius, cen=(18, 18)):
    return [((cen[0] + dy) % S.L, (cen[1] + dx) % S.L)
            for dy in range(-radius, radius + 1) for dx in range(-radius, radius + 1)
            if dy * dy + dx * dx <= radius * radius], cen


def run():
    out = {"MISSION": "RPP97", "SECTION": "capability test, run before any archive is opened",
           "STATUS_OF_THE_MISSION": "POST_HOC — see RPP97_STATEMENT.md section 0",
           "GENERATED_UTC": subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%S+00:00"],
                                           capture_output=True, text=True).stdout.strip(),
           "MIN_CELLS_FOR_S1": S.MIN_CELLS_FOR_S1, "DISC_AREA_READ": S.DISC_AREA,
           "LATTICE_CELLS": S.LATTICE_CELLS, "CORE_R": S.CORE_R, "CASES": {}}
    for radius in (2, 3, 5):
        cells, cen = disc_body(radius)
        d = np.array([S.dist2(c, cen) for c in cells], dtype=np.float64)
        rmax = d.max() if d.max() > 0 else 1.0
        out["CASES"][f"radius_{radius}_ncells_{len(cells)}"] = {
            "a_core_depleted": S.S1(cells, d / rmax * 100.0, cen),
            "b_core_enriched": S.S1(cells, (1.0 - d / rmax) * 100.0, cen),
            "c_uniform": S.S1(cells, np.full(len(cells), 50.0), cen)}
    v = out["CASES"]
    out["a_positive_everywhere"] = all(c["a_core_depleted"] > 0 for c in v.values())
    out["b_NEGATIVE_everywhere"] = all(c["b_core_enriched"] < 0 for c in v.values())
    out["c_zero_everywhere"] = all(abs(c["c_uniform"]) < 1e-12 for c in v.values())
    out["S1_CAN_EXPRESS_THE_REFUTING_OBSERVATION"] = out["b_NEGATIVE_everywhere"]
    out["S1_IS_NOT_SIGN_LOCKED"] = out["a_positive_everywhere"] and out["b_NEGATIVE_everywhere"]
    out["S2_two_signed_check"] = {"depleted_neighbourhood": S.S2(10, 6000),
                                  "enriched_neighbourhood": S.S2(800, 6000)}
    out["S2_IS_NOT_SIGN_LOCKED"] = (out["S2_two_signed_check"]["depleted_neighbourhood"] < 0
                                    and out["S2_two_signed_check"]["enriched_neighbourhood"] > 0)
    out["MEASUREMENT_MAY_PROCEED"] = out["S1_IS_NOT_SIGN_LOCKED"] and out["c_zero_everywhere"] \
        and out["S2_IS_NOT_SIGN_LOCKED"]
    out["NO_ARCHIVE_WAS_OPENED_TO_PRODUCE_THIS_FILE"] = True
    return out


if __name__ == "__main__":
    print(json.dumps(run(), indent=1))
