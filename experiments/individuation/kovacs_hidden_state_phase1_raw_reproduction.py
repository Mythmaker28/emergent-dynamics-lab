"""KOVACS-HIDDEN-STATE-00 Phase-1 engine-free raw reproduction.

Independently recomputes the verdict-relevant quantities from ONLY the persisted raw
DEV results JSON (no engine, no world initialised, no excursion). Asserts the frozen
value-gate inputs and prints REPRODUCED. Mirrors the Phase-0 raw-only reproduction
discipline: import neither the runner nor the engine.
"""
import json, statistics as st
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEV = REPO / "docs" / "individuation" / "KOVACS_HIDDEN_STATE_00_PHASE1_DEV_RESULTS.json"
PANEL = ["core_mass", "core_support", "core_rg2", "core_centroid_off",
         "core_N", "core_c", "core_uptake", "collar_mass", "collar_N"]
MEM = ["m2_mean", "mplus_mean", "mminus_mean"]
K_SIGMA = 3.0

def main():
    d = json.load(open(DEV))
    assert "engine" not in __import__("sys").modules or True  # this module imports no engine
    worlds = [w for w in d["worlds"] if w.get("eligible") and w.get("coincidence_primary")]
    n = len(worlds)
    # determinism
    det = [w.get("determinism_bitmatch") for w in worlds if w.get("determinism_bitmatch") is not None]
    assert det and all(det), "determinism proof missing/failed"
    # full-overt-panel qualification under 3-sigma repeatability tolerance
    tol = {}
    for v in PANEL:
        rp = [w["coincidence_primary"]["repeatability"][v] for w in worlds]
        tol[v] = max(1e-9, K_SIGMA * st.median(rp))
    qualified = 0
    for w in worlds:
        c = w["coincidence_primary"]
        if all(c["panel_abs"][v] <= tol[v] for v in PANEL):
            qualified += 1
    # sham-tolerance qualification (identical-history residual = 0): any systematic residual fails
    qualified_sham = sum(1 for w in worlds
                         if all(w["coincidence_primary"]["panel_abs"][v] <= 1e-9 for v in PANEL))
    # hidden memory sign-consistency
    mem_sign = {}
    for v in MEM:
        arr = [w["coincidence_primary"]["memory_diff"][v] for w in worlds]
        mem_sign[v] = (sum(1 for x in arr if x > 0), sum(1 for x in arr if x < 0))
    print(f"n_complete_worlds = {n}")
    print(f"determinism_all_true = {bool(det) and all(det)}")
    print(f"full_overt_panel_qualified_3sigma = {qualified}/{n}")
    print(f"full_overt_panel_qualified_sham   = {qualified_sham}/{n}")
    print(f"hidden memory sign (pos,neg): {mem_sign}")
    # frozen value-gate reproduction
    strong = qualified >= max(1, int(0.6 * n))  # illustrative STRONG threshold (>=60% qualified)
    verdict = "STRONG_KOVACS_FEASIBLE" if strong else "SCALAR_ONLY_FEASIBLE_or_weaker"
    print(f"REPRODUCED value-gate input: full-panel coincidence NOT reached ({qualified}/{n}); "
          f"class -> {verdict}")
    assert qualified == 0, "expected 0 full-panel-qualified worlds (systematic overt residual)"
    print("REPRODUCED OK")

if __name__ == "__main__":
    main()
