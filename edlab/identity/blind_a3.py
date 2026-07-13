"""ARCHITECTURE HEAD V3 -- RETIRED (D-058). PRESERVED UNCHANGED. DO NOT PATCH. DO NOT USE.

Superseded by edlab/identity/blind_a4.py (docs/ARCHITECTURE_HEAD_V4_SPEC.md). It is kept because the record of a
failed observer is evidence, and because the way it failed is the most useful thing this project has learned:
it made timing phase-invariant by taking the MEDIAN OVER ALL STRIKE PHASES -- integrating the nuisance out -- and
thereby integrated out the signal too, going blind to a delay edit on a gated path.

---- original header follows ----

ARCHITECTURE HEAD V3 -- A_TOPO / A_TAU / G, on FULL-CYCLE phase tomography.

WHY V3 EXISTS (D-056). V2 failed prospectively for three reasons, and all three were design errors, not tolerances:

  1. THE NULL COULD NOT FIRE. V2's delay estimator struck at phases (0,15,30,45) and took the earliest onset. The
     development phase-null tested phases (0,15,30,45) -- THE SAME FOUR NUMBERS. The estimator's sampling grid and
     the null's test grid COINCIDED, so the certificate measured the estimator's agreement with itself and reported
     a delay deviation of ZERO. On held-out phases (7,22,37,52) every delay moved 214 -> 222 and A called a pure
     phase shift DIFFERENT.
     V3 REMOVES THE FREE CHOICE ENTIRELY: it strikes at EVERY phase 0..T-1 of the inferred fundamental period. An
     estimator with no free phase parameter cannot have its null selected to match it. `assert_exhaustive_phases`
     makes this executable: the null contract asserts the strike schedule IS the full cycle, not a subset of it.

  2. LOCAL CONFOUNDING BECAME GLOBAL IGNORANCE. V2 returned INDETERMINATE if ANY intervention was confounded --
     abstaining while holding the correct graph, with complete coverage. Its own contract said a confounded locus
     is EXCLUDED from the evidence. V3 grades EVERY piece of evidence VALID / CONFOUNDED / MISSING, builds the
     graph from the VALID evidence, and abstains ONLY when a preregistered COVERAGE requirement is unmet.

  3. TOPOLOGY AND TIMING WERE THE SAME NUMBER. A handoff that MOVES a component preserves connectivity and changes
     path length. V2 had one verdict for both and had to call it DIFFERENT, which is true of the timing and false
     of the topology. V3 reports them SEPARATELY:
         A_TOPO -- nodes, directed edges, excitatory/inhibitory role, redundancy, dependency structure, modulo
                   graph isomorphism.  NO DELAYS ENTER IT.
         A_TAU  -- the delay structure of those edges, relative to the inferred clock.
         G      -- geometry: positions, spacings, routes.  G NEVER LEAKS INTO A_TOPO.

PHASE-SHIFT INVARIANCE IS NOW A THEOREM, NOT A HOPE. Settling a circuit `phi` extra steps and then striking at
phase p is identical to striking the unshifted circuit at phase (phi + p) mod T. Because V3 strikes at ALL p in
0..T-1, the SET of strike phases is the whole cycle either way, so the MULTISET of per-phase responses is
identical -- a global phase shift merely permutes the phase LABELS. Every summary V3 builds (median, quantiles,
min, max, effect probability) is a function of that multiset, hence exactly invariant. `assert_phase_invariance`
proves it on known cases.
"""

from __future__ import annotations

import numpy as np

from ..substrates.life.fast import step

OBS = 480             # > the longest causal delay plus a full new steady state. NEVER compare unequal windows.
TAIL = 120            # an EXACT number of grid periods: the periodic average carries no sampling noise
RESETTLE = 1200       # let the world finish reacting before judging "did this ablation shatter it?"
OCC_THRESH = 0.25     # occupancy over one period: stationary matter is far above, a glider track far below
MERGE_GAP = 4         # FROZEN on development (D-055): a gun's internal fragments are <= 4 apart, adjacent guns 5
MARGIN = 2
HOLD = 10
MIN_CELLS = 4
SITE = 10             # radius of the "did the ablation build a new machine WHERE THE OLD ONE STOOD?" check
MAX_PERIOD = 240
EPS = 1e-9


# ------------------------------------------------------------------ clock inference (raw trajectory only)
def infer_period(g0: np.ndarray, max_period: int = MAX_PERIOD) -> int:
    """The FUNDAMENTAL period of the settled trajectory, from raw cell states alone. Harmonic ambiguity is
    resolved by construction: we return the SMALLEST T with state(T) == state(0), so a harmonic (2T, 3T, ...)
    can never be reported. If no exact period exists the circuit is not settled and must not be certified."""
    g = g0.copy()
    for t in range(1, max_period + 1):
        g = step(g)
        if np.array_equal(g, g0):
            return t
    raise AssertionError("no exact period within MAX_PERIOD: the circuit is not settled and cannot be certified")


def assert_exhaustive_phases(T: int, phases) -> None:
    """THE INDEPENDENT-NULL CONTRACT, made executable.

    V2's phase null was drawn from the same four numbers as V2's strike schedule, so it could not fire. The fix is
    not a better null -- it is an estimator with NO FREE PHASE CHOICE. Assert that the strike schedule is the FULL
    CYCLE. If it is, no null can be 'selected to match it', because there is nothing left to select."""
    if tuple(phases) != tuple(range(T)):
        raise AssertionError(
            f"strike schedule is a SUBSET of the cycle ({len(phases)} of {T} phases). V2 died of exactly this: a "
            f"selected strike grid whose null was drawn from the same grid. The schedule must be exhaustive.")


def _line_run(g0, steps, out_row, box=None, hold=0):
    g = g0.copy()
    out = np.empty((steps + 1, g.shape[1]), dtype=np.int32)
    out[0] = g[out_row]
    for t in range(steps):
        if box is not None and t < hold:
            r0, r1, c0, c1 = box
            g[r0:r1, c0:c1] = 0
        g = step(g)
        out[t + 1] = g[out_row]
    return out


def _state_after(g0, steps, box=None, hold=0):
    g = g0.copy()
    for t in range(steps):
        if box is not None and t < hold:
            r0, r1, c0, c1 = box
            g[r0:r1, c0:c1] = 0
        g = step(g)
    return g


def _clusters_1d(cols, gap=6):
    out, cur = [], []
    for c in sorted(cols):
        if cur and c - cur[-1] > gap:
            out.append(cur)
            cur = []
        cur.append(c)
    if cur:
        out.append(cur)
    return out


# ------------------------------------------------------------------ component discovery (raw frames only)
def occupancy(g0, T):
    g = g0.copy()
    acc = np.zeros(g0.shape, float)
    for _ in range(T):
        acc += g
        g = step(g)
    return acc / T


def stationary_mask(g0, T):
    return occupancy(g0, T) >= OCC_THRESH


def _components_of(mask, row_hi):
    m = mask.copy()
    m[row_hi:, :] = False
    H, W = m.shape
    seen = np.zeros_like(m, bool)
    frags = []
    for r in range(H):
        for c in range(W):
            if m[r, c] and not seen[r, c]:
                st, cells = [(r, c)], []
                seen[r, c] = True
                while st:
                    y, x = st.pop()
                    cells.append((y, x))
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = y + dy, x + dx
                            if 0 <= ny < H and 0 <= nx < W and m[ny, nx] and not seen[ny, nx]:
                                seen[ny, nx] = True
                                st.append((ny, nx))
                frags.append(cells)
    boxes = [(min(y for y, _ in f), max(y for y, _ in f), min(x for _, x in f), max(x for _, x in f), len(f))
             for f in frags]
    merged, used = [], set()
    for i, b in enumerate(boxes):
        if i in used:
            continue
        cur, n = list(b[:4]), b[4]
        used.add(i)
        changed = True
        while changed:
            changed = False
            for j, o in enumerate(boxes):
                if j in used:
                    continue
                if (o[0] <= cur[1] + MERGE_GAP and cur[0] <= o[1] + MERGE_GAP
                        and o[2] <= cur[3] + MERGE_GAP and cur[2] <= o[3] + MERGE_GAP):
                    cur = [min(cur[0], o[0]), max(cur[1], o[1]), min(cur[2], o[2]), max(cur[3], o[3])]
                    n += o[4]
                    used.add(j)
                    changed = True
        if n >= MIN_CELLS:
            merged.append(tuple(cur))
    return sorted(merged)


def discover_components(g0, out_row, T):
    return _components_of(stationary_mask(g0, T), out_row)


# ================================================================== evidence grading (VALID / CONFOUNDED / MISSING)
def grade_intervention(g0, box, T, out_row, comps=None):
    """§3.4. A whole-component ablation is admissible ONLY if it removed the component and DID NOT BUILD A NEW ONE.

    D-055 measured this the hard way: a 5x5 tile cleared inside a Gosper gun does not DELETE it, it MUTILATES it
    into a different working emitter. So an ablation must be checked for three things, and any failure marks the
    evidence CONFOUNDED -- excluded from the graph, but NOT fatal to it (D-056 failure 2):
      EFFICACY      it actually removed live matter (a silent no-op is not evidence of anything);
      NON-SHATTER   the world returns to an exactly periodic state;
      NO NEW MACHINE  no stationary matter appears where none stood before. If the intervention BUILDS something,
                    the graph we would infer is the graph of a system that never existed.
    """
    r0, r1, c0, c1 = box
    H, W = g0.shape
    b = (max(0, r0 - MARGIN), min(H, r1 + 1 + MARGIN), max(0, c0 - MARGIN), min(W, c1 + 1 + MARGIN))
    touched = int(g0[b[0]:b[1], b[2]:b[3]].sum())
    if touched == 0:
        return b, "CONFOUNDED", "NO_OP: the ablation removed no live matter", None

    # SPECIFICITY (SS3.4): the ablation must be of a WHOLE discovered component, never of a fragment.
    # This is the D-055 lesson made structural. A 5x5 tile cleared inside a Gosper gun does not DELETE the gun;
    # it MUTILATES it into a different working emitter that fires a stream down a NEW diagonal. A graph inferred
    # from such an intervention is the graph of a system that never existed. The check is not "did something odd
    # happen afterwards" -- it is "was this ever a legitimate intervention at all".
    if comps is None:
        comps = _components_of(stationary_mask(g0, T), out_row)
    if tuple(box) not in {tuple(c) for c in comps}:
        overlap = [c for c in comps if not (c[1] < box[0] or box[1] < c[0] or c[3] < box[2] or box[3] < c[2])]
        return b, "CONFOUNDED", (f"PARTIAL COMPONENT: the box {tuple(box)} is not a whole discovered component "
                                 f"(it cuts into {overlap}). Ablating a fragment MUTILATES the component into a "
                                 f"different machine instead of removing it."), None

    end = _state_after(_state_after(g0, OBS, box=b, hold=HOLD), RESETTLE)
    try:
        T2 = infer_period(end)
    except AssertionError:
        return b, "CONFOUNDED", "SHATTERED: the world never returns to a periodic state", None

    before = stationary_mask(g0, T)
    after = stationary_mask(end, T2)

    # NO NEW MACHINE *IN SITU*. The rule must catch MUTILATION -- an ablation that leaves a mutant emitter where
    # the component stood -- and must NOT catch the component's genuine DOWNSTREAM CONSEQUENCES. Removing a gun
    # that was shielding a channel legitimately lets a stream travel on and form a new collision elsewhere; that
    # is the causal effect we are trying to MEASURE, not an artefact of the probe. So the check is local to the
    # ablation site. (First draft checked the whole grid and flagged both real inhibitor ablations as
    # CONFOUNDED -- and border debris from a re-routed stream as a "new machine". An over-strict validity rule
    # is just abstention wearing a lab coat.)
    site = np.zeros_like(after)
    site[max(0, b[0] - SITE):b[1] + SITE, max(0, b[2] - SITE):b[3] + SITE] = True
    new = after & ~_dilate(before, 2) & site
    if int(new.sum()) >= MIN_CELLS:
        ys, xs = np.nonzero(new)
        return b, "CONFOUNDED", (f"MUTILATION: the ablation left {int(new.sum())} cells of NEW stationary matter "
                                 f"at the site ({int(ys.mean())},{int(xs.mean())}) -- it replaced the component "
                                 f"rather than removing it"), after
    return b, "VALID", "ok", after


def _dilate(mask, r):
    out = mask.copy()
    for _ in range(r):
        m = out.copy()
        m[1:, :] |= out[:-1, :]
        m[:-1, :] |= out[1:, :]
        m[:, 1:] |= out[:, :-1]
        m[:, :-1] |= out[:, 1:]
        out = m
    return out


# ================================================================== FULL-CYCLE phase tomography
def tomography(g0: np.ndarray, out_row: int, region=None) -> dict:
    """Strike at EVERY phase of the inferred fundamental period. No phase is chosen; therefore no null can be
    chosen to match the choice. `region` exists ONLY so that insufficient coverage can be SIMULATED."""
    T = infer_period(g0)
    phases = tuple(range(T))
    assert_exhaustive_phases(T, phases)

    # baselines: ONE long run, sliced. The baseline at phase p IS the trajectory advanced by p.
    long_base = _line_run(g0, OBS + T, out_row)
    base_at = {p: long_base[p:p + OBS + 1] for p in phases}
    states = {}
    g = g0.copy()
    for p in phases:
        states[p] = g.copy()
        g = step(g)

    comps = discover_components(g0, out_row, T)
    if region:
        rl, rh, cl, ch = region
        comps = [b for b in comps if rl <= b[0] and b[1] < rh and cl <= b[2] and b[3] < ch]

    graded = [grade_intervention(g0, b, T, out_row, comps) for b in comps]

    # COMPONENT -> COMPONENT dependency edges. Ablating i and finding that j's matter is GONE is a structural
    # dependency (j exists BECAUSE of i) -- e.g. the stationary remnant that two mutually-annihilating streams
    # leave at their crossing exists only while both guns fire. Without these, "redundancy and dependency
    # structure" (mission SS2) cannot be read at all, and a collision remnant looks like a free-standing part.
    dep = {}
    for i, (b, (bb, status, why, after)) in enumerate(zip(comps, graded)):
        if status != "VALID" or after is None:
            continue
        gone = []
        for j, ob in enumerate(comps):
            if j == i:
                continue
            if not after[ob[0]:ob[1] + 1, ob[2]:ob[3] + 1].any():
                gone.append(j)
        dep[i] = gone

    live_cols = set(np.nonzero(long_base.sum(0))[0])
    resp = {}
    for i, (b, (bb, status, why, _a)) in enumerate(zip(comps, graded)):
        if status != "VALID":
            continue
        per_phase = {}
        for p in phases:
            line = _line_run(states[p], OBS, out_row, box=bb, hold=HOLD)
            d = line - base_at[p]
            per_phase[p] = d
            live_cols |= set(np.nonzero(np.abs(d).sum(0))[0])
        resp[i] = per_phase

    out_nodes = [(min(gp), max(gp)) for gp in _clusters_1d(sorted(live_cols))]

    nodes, edges = [], []
    for i, (b, (bb, status, why, _a)) in enumerate(zip(comps, graded)):
        node = {"id": i, "box": b, "evidence": status, "why": why, "targets": {},
                "destroys": sorted(dep.get(i, []))}
        if status == "VALID":
            for j, (lo, hi) in enumerate(out_nodes):
                onsets, kinds = [], []
                for p in resp[i]:
                    dj = resp[i][p][:, lo:hi + 1].sum(1).astype(float)
                    nz = np.nonzero(np.abs(dj) > EPS)[0]
                    if len(nz) == 0:
                        continue
                    drift = float(dj[-TAIL:].mean())
                    k = "PERSISTENT_DOWN" if drift < -EPS else ("PERSISTENT_UP" if drift > EPS else "TRANSIENT")
                    if k == "TRANSIENT":
                        continue                        # a WIRE: matter in transit, re-supplied by its source
                    onsets.append(int(nz[0]))
                    kinds.append(k)
                if not onsets:
                    continue
                kind = max(set(kinds), key=kinds.count)
                # PHASE-INVARIANT summaries: functions of the MULTISET of per-phase onsets, which a global phase
                # shift can only permute. Not "the earliest onset at four chosen phases" -- that is what died.
                a = np.array(sorted(onsets), float)
                node["targets"][j] = {"kind": kind, "p_effect": len(onsets) / len(phases),
                                      "median": float(np.median(a)), "q25": float(np.quantile(a, .25)),
                                      "q75": float(np.quantile(a, .75)), "min": int(a.min()), "max": int(a.max())}
                edges.append({"src": i, "dst": j, **node["targets"][j]})
        nodes.append(node)

    base_live = {j for j, (lo, hi) in enumerate(out_nodes) if long_base[:, lo:hi + 1].sum() > 0}
    suppressed = set(range(len(out_nodes))) - base_live
    sourced = {e["dst"] for e in edges if e["kind"] == "PERSISTENT_DOWN"}
    explained = {e["dst"] for e in edges if e["kind"] == "PERSISTENT_UP"}
    coverage = {"live_outputs": sorted(base_live), "suppressed_outputs": sorted(suppressed),
                "unsourced_live": sorted(base_live - sourced),
                "unexplained_suppressed": sorted(suppressed - explained),
                "n_components": len(comps),
                "n_valid": sum(1 for g in graded if g[1] == "VALID"),
                "n_confounded": sum(1 for g in graded if g[1] != "VALID"),
                "confounded_reasons": [g[2] for g in graded if g[1] != "VALID"]}
    # PREREGISTERED COVERAGE REQUIREMENT: every LIVE output must have a VALID source, and every SUPPRESSED output
    # must have a VALID inhibitor. Confounded components contribute no edges but are still counted as NODES --
    # "there is a component here whose role I could not test" is itself a discovered fact, and it enters the
    # signature so that two circuits cannot be called SAME while differing in how much is unresolved.
    # PREREGISTERED COVERAGE REQUIREMENT (SS3.3), declared before any case is scored:
    #   * every LIVE output has a VALID source;
    #   * every SUPPRESSED output has a VALID inhibitor;
    #   * every discovered component has VALID ablation evidence.
    # The third clause is what makes SAME honest. A component we could not test might carry an edge we cannot
    # see, so its presence forbids us from certifying IDENTITY -- but it does NOT forbid us from certifying
    # DIFFERENCE, because a difference you can already see is a difference. head_A_TOPO is asymmetric for
    # exactly this reason: DIFFERENT needs sufficient evidence, SAME needs complete evidence.
    # TWO DISTINCT LEVELS OF EVIDENCE, and conflating them is what produced a fabricated certainty:
    #   OUTPUTS_EXPLAINED -- every live output has a VALID source and every suppressed output a VALID inhibitor.
    #                        Without this the graph is INCOMPLETE, and an incomplete graph can fabricate a
    #                        DIFFERENCE just as easily as a sameness: a missing node looks exactly like an absent
    #                        one. So without it, NOTHING may be concluded -- not SAME, and not DIFFERENT either.
    #   COMPLETE          -- additionally, every discovered component was successfully tested. Only this licenses
    #                        SAME, because an untested component could always be carrying an edge we cannot see.
    coverage["outputs_explained"] = (not coverage["unsourced_live"] and not coverage["unexplained_suppressed"])
    coverage["complete"] = coverage["outputs_explained"] and coverage["n_confounded"] == 0
    coverage["met"] = coverage["complete"]

    return {"T": T, "n_out": len(out_nodes), "out_nodes": out_nodes, "nodes": nodes, "edges": edges,
            "coverage": coverage, "phases": len(phases)}


# ================================================================== A_TOPO -- causal topology. NO DELAYS. NO GEOMETRY.
def topo_signature(t: dict) -> tuple:
    """Isomorphism-invariant. Output nodes enter ONLY as ordinals; components ONLY through their edge sets and
    roles. NOTHING about position, spacing or delay appears here -- that is the whole point of splitting A.

    The count of CONFOUNDED nodes is part of the signature: "there is one component whose role I could not test"
    is a discovered fact, and two circuits must not be called SAME while differing in how much is unresolved."""
    rows = []
    for n in t["nodes"]:
        if n["evidence"] != "VALID":
            continue                              # a node we could not test contributes NO EDGES -- see coverage
        if not n["targets"] and not n["destroys"]:
            continue                              # CAUSALLY INERT: decoration is not architecture. It must not
                                                  # enter A_TOPO, or G leaks into topology -- the exact error SS2
                                                  # forbids. It is still reported, and it moves M and G.
        rows.append((tuple(sorted((j, tt["kind"]) for j, tt in n["targets"].items())),
                     len(n["destroys"])))          # dependency OUT-DEGREE: isomorphism-invariant, position-free
    return (t["n_out"], tuple(sorted(rows)))


def head_A_TOPO(t1: dict, t2: dict) -> str:
    """SAME / DIFFERENT / INDETERMINATE.

    ASYMMETRIC BY DESIGN (D-056 fix): valid evidence that the resolved parts DIFFER is enough to prove DIFFERENT
    even under partial coverage -- a difference you can see is a difference. But calling two circuits SAME requires
    the coverage requirement to be MET, because an unresolved locus could always be hiding one."""
    if not (t1["coverage"]["outputs_explained"] and t2["coverage"]["outputs_explained"]):
        return "INDETERMINATE"       # the graph is INCOMPLETE. A missing node looks exactly like an absent one,
                                     # so an incomplete graph can fabricate a DIFFERENCE as easily as a sameness.
                                     # Nothing may be concluded. (An earlier draft allowed DIFFERENT here, and a
                                     # deliberately under-covered probe duly reported DIFFERENT -- a fabricated
                                     # certainty produced by the observer's own blindness.)
    if topo_signature(t1) != topo_signature(t2):
        return "DIFFERENT"           # both graphs are complete w.r.t. their outputs, and they disagree
    if not (t1["coverage"]["complete"] and t2["coverage"]["complete"]):
        return "INDETERMINATE"       # signatures agree, but an untested component could hide a difference
    return "SAME"


# ================================================================== A_TAU -- causal TIMING, relative to the clock
def tau_signature(t: dict) -> tuple:
    """Delay structure of the edges, in units of the INFERRED clock. Phase-invariant by construction: every summary
    is a function of the multiset of per-phase onsets, which a global phase shift can only permute."""
    rows = []
    for n in t["nodes"]:
        if n["evidence"] != "VALID" or not n["targets"]:
            continue
        rows.append((tuple(sorted((j, tt["kind"]) for j, tt in n["targets"].items())),
                     len(n["destroys"]),
                     tuple(tt["median"] for _, tt in sorted(n["targets"].items()))))
    return tuple(sorted(rows))


def head_A_TAU(t1: dict, t2: dict, tol: float) -> str:
    """Compared ONLY after the topology matches -- a delay difference between two different graphs is meaningless.
    Delays are compared PAIRWISE against the tolerance, never bucketed: 214 and 229 differ by exactly 15, and with
    a tolerance of 15 and floor-quantization they land in buckets 13 and 14 and read DIFFERENT (D-055).
    A bucket boundary is not a tolerance."""
    if head_A_TOPO(t1, t2) == "INDETERMINATE":
        return "INDETERMINATE"
    if topo_signature(t1) != topo_signature(t2):
        return "INDETERMINATE"                   # different graphs: their delays are not comparable
    r1, r2 = tau_signature(t1), tau_signature(t2)
    if len(r1) != len(r2):
        return "INDETERMINATE"
    for (s1, k1, d1), (s2, k2, d2) in zip(r1, r2):
        if s1 != s2 or k1 != k2 or len(d1) != len(d2):
            return "INDETERMINATE"
        if any(abs(x - y) > tol for x, y in zip(d1, d2)):
            return "DIFFERENT"
    return "SAME"


# ================================================================== G -- geometric embedding. NEVER identity.
def geom_signature(t: dict) -> tuple:
    """Layout: the SPACINGS of the discovered components and of the output nodes. Translation-invariant by
    construction (spacings, never absolute columns). G is reported separately and is NEVER composited into
    identity: two machines may share A_TOPO and A_TAU and differ in G -- that is a drawing difference."""
    cs = sorted(((b["box"][0] + b["box"][1]) / 2, (b["box"][2] + b["box"][3]) / 2) for b in t["nodes"])
    cgaps = tuple(round(cs[i + 1][1] - cs[i][1]) for i in range(len(cs) - 1))
    rgaps = tuple(round(cs[i + 1][0] - cs[i][0]) for i in range(len(cs) - 1))
    os_ = [(lo + hi) / 2 for lo, hi in t["out_nodes"]]
    ogaps = tuple(round(os_[i + 1] - os_[i]) for i in range(len(os_) - 1))
    return (cgaps, rgaps, ogaps)


def head_G(t1: dict, t2: dict) -> str:
    return "SAME" if geom_signature(t1) == geom_signature(t2) else "DIFFERENT"


# ================================================================== executable invariance proof
def assert_phase_invariance(tomos_by_phase: dict) -> dict:
    """A PURE GLOBAL PHASE SHIFT MUST NOT MOVE A_TOPO, A_TAU OR G. This is the assertion V2 did not have, and its
    absence is exactly why V2 shipped. `tomos_by_phase` maps a settling offset to a tomography of the SAME circuit.
    Every one of them must agree, on every head, with the phase-0 one."""
    ref = tomos_by_phase[sorted(tomos_by_phase)[0]]
    bad = []
    for ph, t in sorted(tomos_by_phase.items()):
        if topo_signature(t) != topo_signature(ref):
            bad.append(f"A_TOPO moved at phase {ph}")
        if tau_signature(t) != tau_signature(ref):
            bad.append(f"A_TAU moved at phase {ph}: {tau_signature(t)} vs {tau_signature(ref)}")
        if geom_signature(t) != geom_signature(ref):
            bad.append(f"G moved at phase {ph}")
    if bad:
        raise AssertionError("PHASE INVARIANCE VIOLATED: " + "; ".join(bad))
    return {"phases_checked": sorted(tomos_by_phase), "verdict": "INVARIANT"}


# ================================================================== resumable cache (§3.1.5)
import hashlib as _hl
import os as _os
import pickle as _pk

CACHE = _os.path.join("results", "_tomo3_cache")


def cached_tomography(g0: np.ndarray, out_row: int, region=None) -> dict:
    """Exhaustive phase coverage is ~10 s per circuit. The cache key is a hash of the SETTLED GRID ITSELF, so it
    cannot accidentally collide across circuits, layouts or phases, and it can never key on a hidden label."""
    _os.makedirs(CACHE, exist_ok=True)
    k = _hl.sha256(g0.tobytes() + str(region).encode() + str(out_row).encode()).hexdigest()[:24]
    fp = _os.path.join(CACHE, k + ".pkl")
    if _os.path.exists(fp):
        with open(fp, "rb") as f:
            return _pk.load(f)
    t = tomography(g0, out_row, region=region)
    with open(fp, "wb") as f:
        _pk.dump(t, f)
    return t
