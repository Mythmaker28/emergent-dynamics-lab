"""THE ADMISSION LAYER (mission Phase 0). A SEPARATE controller. Architecture head V4 is NOT touched.

WHY IT EXISTS (D-060). V4 declares a component-separation limit of 4 cells and never checks that the data respect
it. Handed a case below the limit -- an E1 relief placed one row from a gun -- it silently MERGED the two into one
component and emitted a confident DIFFERENT. A confident verdict on a case the instrument cannot resolve is a
FABRICATED CERTAINTY, and the observability contract forbids it.

THE HARD PART, AND WHY THE OBVIOUS CHECK DOES NOT WORK. You cannot detect an unresolved merge by LOOKING at the
stationary mask. Two components 2 cells apart merge into one blob, and no amount of staring at that blob tells you
it was two -- that is exactly what "below the resolution limit" MEANS. A geometric check here is circular.

SO ADMISSION IS CAUSAL, NOT GEOMETRIC.

    A discovered component is ATOMIC if no PROPER SUB-PART of it can be cleanly ablated to a DIFFERENT effect.

Ablate each connected sub-fragment of a candidate component on its own:
  * for a genuine single component (a Gosper gun), a sub-fragment ablation MUTILATES it -- it builds a new emitter
    -- or destroys it entirely, reproducing the whole component's effect. Either way, no clean sub-part with a
    DISTINCT causal role exists.
  * for a MERGED blob (gun + relief eater), the relief is a sub-fragment whose clean ablation has a causal effect
    the whole blob does not have (removing the relief OPENS the channel; removing the blob leaves it dead). The
    blob is therefore NOT atomic, and the case is OUT_OF_SCOPE.

This uses only observable, intervention-derived quantities. No hidden label is read anywhere.

Admission returns exactly one of: ADMITTED / OUT_OF_SCOPE / INSUFFICIENT_COVERAGE / CONFOUNDED / INDETERMINATE.
**An A / S / F decision is INVALID unless admission returns ADMITTED.**
"""

from __future__ import annotations

import hashlib
import os
import pickle

import numpy as np

from ..substrates.life.fast import step
from .blind_a4 import (infer_period, stationary_mask, discover_components, _grade, _ablate,
                       OBS, TAIL, MERGE_GAP, MIN_VALID_FRAC, MIN_CELLS, EPS, HOLD, MARGIN)

MIN_PERIODS_OBSERVED = 6      # the observation window must span >= this many INFERRED clock periods
MIN_EDGE_STRIKES = 2          # no edge may rest on a single strike (a criterion that fires once is an anecdote)
RESETTLE = 1200               # a sub-part ablation must leave a world that RETURNS TO A PERIODIC STATE

ADMITTED = "ADMITTED"
OUT_OF_SCOPE = "OUT_OF_SCOPE"
INSUFFICIENT_COVERAGE = "INSUFFICIENT_COVERAGE"
CONFOUNDED = "CONFOUNDED"
INDETERMINATE = "INDETERMINATE"


def _fragments(mask, box):
    """Connected sub-fragments of the stationary mask INSIDE a candidate component's box, with NO merging."""
    r0, r1, c0, c1 = box
    sub = np.zeros_like(mask)
    sub[r0:r1 + 1, c0:c1 + 1] = mask[r0:r1 + 1, c0:c1 + 1]
    seen = np.zeros_like(sub, bool)
    out = []
    for r in range(r0, r1 + 1):
        for c in range(c0, c1 + 1):
            if sub[r, c] and not seen[r, c]:
                st, cells = [(r, c)], []
                seen[r, c] = True
                while st:
                    y, x = st.pop()
                    cells.append((y, x))
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = y + dy, x + dx
                            if (r0 <= ny <= r1 and c0 <= nx <= c1 and sub[ny, nx] and not seen[ny, nx]):
                                seen[ny, nx] = True
                                st.append((ny, nx))
                if len(cells) >= MIN_CELLS:
                    out.append((min(y for y, _ in cells), max(y for y, _ in cells),
                                min(x for _, x in cells), max(x for _, x in cells)))
    return out


def _effect(g0, box, out_row, T, out_nodes=None, base=None):
    """The causal effect of ablating `box`, as a persistent-drift signature over the WHOLE OUTPUT LINE.

    NOT projected onto the discovered output nodes, and that distinction is the whole point. A merged blob's
    ablation removes the gun AND the gate together, so the channel stays dead and its output column is never
    discovered at all. Projecting a sub-fragment's effect onto the node list the merged ablation produced would
    therefore SHOW NOTHING -- the blob hides the very output that would expose it. The first draft did exactly
    that and admitted the merged case. The signature must be taken on the raw line."""
    b, line, _after, st = _grade(g0, stationary_mask(g0, T), box, out_row, T)
    if st != "VALID":
        return st, None
    # NON-SHATTERING. A sub-part whose removal SHATTERS the world is not evidence that the component was two
    # components -- it is evidence that the component was a dynamic equilibrium. The collision remnant left by
    # two mutually-annihilating streams is exactly that: ablate half of it and the balance breaks and a stream
    # leaks, but there was never a second COMPONENT hiding inside it. Without this check the atomicity test
    # refused every cross-inhibitor circuit -- including the crown case, which V4 resolves correctly.
    g = g0.copy()
    for t in range(OBS):
        if t < HOLD:
            g[b[0]:b[1], b[2]:b[3]] = 0
        g = step(g)
    for _ in range(RESETTLE):
        g = step(g)
    try:
        infer_period(g)
    except AssertionError:
        return "SHATTERED", None
    if base is None:
        base, gg = np.empty((OBS + 1, g0.shape[1]), dtype=np.int32), g0.copy()
        base[0] = gg[out_row]
        for t in range(OBS):
            gg = step(gg)
            base[t + 1] = gg[out_row]
    drift = (line - base)[-TAIL:].mean(0)                 # persistent drift, per output-line COLUMN
    hits = [(int(c), 1 if drift[c] > EPS else -1) for c in np.nonzero(np.abs(drift) > EPS)[0]]
    # cluster adjacent columns so that a stream two columns wide is one effect, not two
    sig, cur = [], []
    for c, s in hits:
        if cur and (c - cur[-1][0] > 6 or s != cur[-1][1]):
            sig.append((int(np.mean([x for x, _ in cur])), cur[0][1]))
            cur = []
        cur.append((c, s))
    if cur:
        sig.append((int(np.mean([x for x, _ in cur])), cur[0][1]))
    return "VALID", tuple(sig)


def atomicity(g0, out_row, T, boxes=None, valid_masks=None, n_phases=3) -> dict:
    """CAUSAL ATOMICITY, PHASE-RESOLVED.

    A component is atomic iff no PROPER SUB-PART can be cleanly ablated to an effect DIFFERENT from the whole
    component's -- judged at SEVERAL strike phases, and only at phases where the WHOLE ablation is itself valid.

    THAT LAST CLAUSE IS NOT A DETAIL. My first version judged atomicity at a single phase. At the 6 phases where
    the box-ablation leaves a block behind, the WHOLE-component ablation is invalid, so `whole_effect` is None --
    and every clean sub-fragment then looked "distinct from nothing" and the circuit was declared a merge. The
    admission layer refused four perfectly ordinary phase-shift nulls. **An admission controller that refuses
    valid cases is not conservative; it is broken.** Comparison against an invalid baseline is not evidence.
    """
    from ..substrates.life.fast import step as _st
    mask0 = stationary_mask(g0, T)
    # Assess EXACTLY the components the tomography used. Re-discovering them here ignored the probe region and
    # desynced the validity masks, so a coverage-starved probe was mis-labelled OUT_OF_SCOPE instead of
    # INSUFFICIENT_COVERAGE. Admission must audit the inference that was actually made, not a different one.
    comps = boxes if boxes is not None else discover_components(g0, out_row, T)

    states = {}
    g = g0.copy()
    for p in range(T):
        states[p] = g.copy()
        g = _st(g)

    report, non_atomic = [], []
    for i, box in enumerate(comps):
        vm = valid_masks[i] if valid_masks is not None and i < len(valid_masks) else np.ones(T, bool)
        valid_phases = list(np.nonzero(vm)[0])
        if not valid_phases:
            report.append({"component": box, "n_fragments": 0, "whole_effect": None,
                           "clean_subparts_with_distinct_effect": [], "atomic": True,
                           "note": "no valid strike phase; atomicity not assessable"})
            continue
        pick = [valid_phases[k * len(valid_phases) // n_phases] for k in range(n_phases)]
        frags = _fragments(mask0, box)
        votes = {}
        wholes = []
        for p in pick:
            gp = states[p]
            base = np.empty((OBS + 1, g0.shape[1]), dtype=np.int32)
            gg = gp.copy()
            base[0] = gg[out_row]
            for t in range(OBS):
                gg = _st(gg)
                base[t + 1] = gg[out_row]
            st_w, eff_w = _effect(gp, box, out_row, T, base=base)
            if st_w != "VALID":
                continue                      # the WHOLE ablation is invalid here: no baseline, no comparison
            wholes.append(eff_w)
            if len(frags) <= 1:
                continue
            for f in frags:
                st_f, eff_f = _effect(gp, f, out_row, T, base=base)
                if st_f == "VALID" and eff_f and eff_f != eff_w:
                    votes.setdefault(f, []).append(eff_f)
        splits = [{"fragment": f, "effects": v, "n_phases_confirmed": len(v), "whole_effects": wholes}
                  for f, v in votes.items() if len(v) > len(wholes) / 2]     # MAJORITY of assessable phases
        entry = {"component": box, "n_fragments": len(frags), "whole_effect": wholes[0] if wholes else None,
                 "phases_assessed": len(wholes), "clean_subparts_with_distinct_effect": splits,
                 "atomic": not splits}
        report.append(entry)
        if splits:
            non_atomic.append(box)
    return {"components": report, "non_atomic": non_atomic, "all_atomic": not non_atomic}


_ACACHE = os.path.join("results", "_admit_cache")


def cached_admit(t, g0, out_row, request):
    """Memoised on disk. Admission runs a phase-resolved atomicity sweep (~20 s/circuit). The cache changes
    nothing scientific -- it lets a run resume."""
    os.makedirs(_ACACHE, exist_ok=True)
    # The key MUST include the tomography, not just the grid: a coverage-starved probe uses the SAME grid with a
    # restricted region, and keying on the grid alone silently returned the un-starved verdict. A cache that can
    # answer a question it was never asked is not a cache, it is a bug.
    tkey = (str(out_row) + request + str(t["coverage"]) + str([n["box"] for n in t["nodes"]])
            + str(t["out_nodes"]))
    k = hashlib.sha256(g0.tobytes() + tkey.encode()).hexdigest()[:24]
    fp = os.path.join(_ACACHE, k + ".pkl")
    if os.path.exists(fp):
        return pickle.load(open(fp, "rb"))
    r = admit(t, g0, out_row, request)
    pickle.dump(r, open(fp, "wb"))
    return r


def admit(t: dict, g0: np.ndarray, out_row: int, request: str) -> dict:
    """PROSPECTIVE ADMISSION for one tomography. Observable quantities only; no hidden label is read."""
    checks, verdict = {}, ADMITTED
    T = t["T"]
    cov = t["coverage"]

    # 1. observation duration spans enough inferred clock periods
    checks["observation_periods"] = OBS / T
    if OBS / T < MIN_PERIODS_OBSERVED:
        verdict = OUT_OF_SCOPE
        checks["fail_observation_duration"] = f"{OBS/T:.1f} periods < {MIN_PERIODS_OBSERVED}"

    # 2. the group action is SUPPORTED: the quotient assumes a common cyclic rotation over the FULL cycle, so
    #    the estimator must have struck at every phase. A quotient over a sampled subgroup is not a quotient.
    checks["strike_schedule_exhaustive"] = True
    for n in t["nodes"]:
        if len(n["valid_mask"]) != T:
            checks["strike_schedule_exhaustive"] = False
    if not checks["strike_schedule_exhaustive"]:
        verdict = OUT_OF_SCOPE
        checks["fail_group_action"] = "the phase quotient requires an exhaustive strike schedule"

    # 3. baseline and intervention windows are EXACTLY matched (structural invariant of the tomography)
    checks["windows_matched"] = True

    # 4. per-component valid-strike coverage
    fracs = cov["valid_phase_fracs"]
    checks["valid_phase_fracs"] = fracs
    checks["min_valid_frac_required"] = MIN_VALID_FRAC
    if any(f < MIN_VALID_FRAC for f in fracs):
        verdict = INSUFFICIENT_COVERAGE
        checks["fail_phase_coverage"] = f"a component has only {min(fracs):.2f} valid strike phases"

    # 5. no edge may rest on a single strike
    weak = [(e["src"], e["dst"]) for e in t["edges"]
            if int((e["profile"] >= 0).sum()) < MIN_EDGE_STRIKES]
    checks["edges_on_too_few_strikes"] = weak
    if weak:
        verdict = CONFOUNDED
        checks["fail_single_strike"] = weak

    # 6. causal tomography complete enough for the request
    checks["outputs_explained"] = cov["outputs_explained"]
    checks["complete"] = cov["complete"]
    if not cov["outputs_explained"]:
        verdict = INSUFFICIENT_COVERAGE
        checks["fail_coverage"] = {"unsourced_live": cov["unsourced_live"],
                                   "unexplained_suppressed": cov["unexplained_suppressed"]}

    # 7. CAUSAL ATOMICITY -- the check that catches an unresolved merge. Geometry cannot see it; causation can.
    at = atomicity(g0, out_row, T, boxes=[n["box"] for n in t["nodes"]],
                   valid_masks=[n["valid_mask"] for n in t["nodes"]])
    checks["atomicity"] = {"all_atomic": at["all_atomic"], "non_atomic": at["non_atomic"],
                           "detail": [{k: v for k, v in c.items() if k != "clean_subparts_with_distinct_effect"}
                                      | {"n_clean_distinct_subparts": len(c["clean_subparts_with_distinct_effect"])}
                                      for c in at["components"]]}
    if not at["all_atomic"]:
        verdict = OUT_OF_SCOPE
        checks["fail_atomicity"] = (
            f"component(s) {at['non_atomic']} are NOT causally atomic: a proper sub-part can be cleanly ablated "
            f"to a DIFFERENT effect. They are an unresolved MERGE of parts closer than the certified separation "
            f"limit ({MERGE_GAP} cells), and the instrument cannot say what it merged.")

    return {"verdict": verdict, "request": request, "checks": checks}


def admit_pair(t1, g1, t2, g2, out_row, request) -> dict:
    """Both sides must be admitted. A comparison is only as admissible as its worse half."""
    a1 = cached_admit(t1, g1, out_row, request)
    a2 = cached_admit(t2, g2, out_row, request)
    for v in (OUT_OF_SCOPE, CONFOUNDED, INSUFFICIENT_COVERAGE, INDETERMINATE):
        if a1["verdict"] == v or a2["verdict"] == v:
            return {"verdict": v, "left": a1, "right": a2, "request": request}
    return {"verdict": ADMITTED, "left": a1, "right": a2, "request": request}
