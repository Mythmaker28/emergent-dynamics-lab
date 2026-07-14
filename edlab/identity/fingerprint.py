"""THE CAUSAL-RESPONSE FINGERPRINT. A fixed coordinate system, not an observer.

    A measurement coordinate system must not adapt to the entity being compared.

That sentence is the whole design. The active planner (G6) is prospectively qualified and is **switched off here**,
deliberately: it chooses a different intervention sequence for each world, which is exactly what made it efficient
and exactly what would make two entities' fingerprints incomparable. Every system receives the SAME battery, in the
same order, at the same amplitudes, durations and relative timings, with the same normalization. No probe is ever
selected in response to what a system did.

WHAT MAY ENTER THE FINGERPRINT (mission SS2):
    provenance-valid, time-resolved responses of the DECLARED BEHAVIOURAL OUTPUT
    the input-output behaviour the repertoire can actually reach
    standardized perturbation-response curves
    directly observed recovery dynamics (does a transient perturbation leave a permanent mark?)
    explicitly recorded uncertainty and missing coverage

WHAT MAY NOT, ON PAIN OF THE WHOLE EXERCISE BEING WORTHLESS:
    transducer-class labels; selected lag sets; model complexity; DELAYED_STATIC / FINITE_HISTORY / any such name;
    inferred minimal architecture; evaluator-supplied component identities; active-planner sequences; tracker IDs.

    A REDUNDANT LAG MUST NOT CREATE A FINGERPRINT DIFFERENCE WHEN ALL MEASURED RESPONSES ARE IDENTICAL.

That is the D-069 defect, and this file's exclusion list is the only thing standing between it and a false
DIFFERENCE. The exclusion is not an assumption: `exp_gt_fp.py` contains a must-fail control that ADDS the class
label back and shows the false difference reappear. If that control does not fire, the exclusion is decoration.

THE FINGERPRINT NEVER SAYS "SAME". Its verdicts are INDISTINGUISHABLE_UNDER_REPERTOIRE / DIFFERENT /
INDETERMINATE. Two systems that no admissible probe can separate are an EQUIVALENCE CLASS, not one individual.
"""

from __future__ import annotations

import numpy as np

from .provenance import Episode, ProvenanceError, run_episode, pulse_episode

# ---------------------------------------------------------------- FROZEN CONSTANTS (identical for every system)
CLK_P = 8              # a declared SUBSTRATE constant. NOT inferred per system: an inferred quantity would make the
                       # coordinate system adapt to the thing it measures.
T_OBS = 200            # every episode is exactly this long, for every system, in both arms
T_PROBE = 80           # probes begin here: after settle, and with room for the longest channel's response
W_RESP = 96            # the response window read after each probe onset. It MUST outlast the longest response:
                       # at W_RESP = 32 the far channel's own latency (up to 56) exceeded the window, so a response
                       # that was merely STILL IN FLIGHT at the window's end was recorded as PERMANENT. That is the
                       # memory signature contaminated by impatience -- the same error as D-067's fixed margin,
                       # arriving from the other end of the trace.
D_HOLD = 6             # sustained-probe duration
W_ALIGN = 40           # the onset-aligned block, READ FROM THE EPISODE -- never zero-padded. Padding a short
                       # response to a fixed length makes the PADDING, not the behaviour, carry the difference:
                       # two systems with different latencies then get different amounts of zero and are called
                       # different for it. Measured in development: d(AND, AND-with-a-longer-channel) = 0.0946,
                       # entirely an artefact of my own array.
TAIL = 16              # persistence is judged on the last TAIL samples of the window, long after any transient
COVERAGE_FLOOR = 0.5   # below this, no distance verdict may be issued at all


# ---------------------------------------------------------------- the two access arms
def battery(machine_cells: dict, arm: str) -> list:
    """THE FIXED PROBE BATTERY. Identical types, amplitudes, durations and relative timings for every system.

    `machine_cells` supplies only the ADDRESSES the arm is allowed to touch. It supplies no component identity, no
    label and no ground truth: an address is where you may put a pipette, not what the thing is.

    RICH arm      -- the full legal ground-truth repertoire: the global drive, the entity's external supply line,
                     and every internal state variable (registers, the write-enable).
    DROPLET arm   -- ONLY what the unchanged beta = 0.10 scaffold substrate actually permits: perturbation of the
                     EXTERNAL fields. Nothing internal. See docs/DROPLET_ACCESS_EQUIVALENCE.md. There is no droplet
                     analogue of clamping a register, so there is no register clamp here.
    """
    drive = machine_cells["drive"]              # the global exogenous drive  (droplet: the nutrient/attractant field)
    supply = machine_cells["supply"]            # the entity's external supply line (droplet: a local bolus)
    probes = [
        # (name, kind, cell, value, hold)
        ("drive_high", "sustained", drive, 1, D_HOLD),
        ("drive_low", "sustained", drive, 0, D_HOLD),
        ("drive_pulse_up", "pulse", drive, 1, 1),
        ("drive_pulse_down", "pulse", drive, 0, 1),
        ("supply_pulse_up", "pulse", supply, 1, 1),
        ("supply_pulse_down", "pulse", supply, 0, 1),
    ]
    if arm == "rich":
        for k, cell in enumerate(machine_cells.get("internal", [])):
            probes.append((f"internal{k}_high", "sustained", cell, 1, T_OBS))
            probes.append((f"internal{k}_low", "sustained", cell, 0, T_OBS))
    elif arm != "droplet":
        raise ValueError(f"unknown arm {arm!r}")
    return probes


# ---------------------------------------------------------------- acquisition
def _row(base: Episode, ep: Episode, out_cell, t0: int) -> dict:
    """One provenance-valid response row: what the DECLARED OUTPUT did, read from the episode at real timestamps."""
    lo, hi = T_PROBE + t0, T_PROBE + t0 + W_RESP
    if hi > base.T or hi > ep.T:
        raise ProvenanceError(f"response window [{lo},{hi}) does not fit inside the episode (T={base.T}). "
                              f"A window that does not exist is not a measurement.")
    obs = np.array([ep.sample(out_cell, t) for t in range(lo, hi)], dtype=np.uint8)
    bas = np.array([base.sample(out_cell, t) for t in range(lo, hi)], dtype=np.uint8)
    dev = (obs != bas).astype(np.uint8)
    nz = np.nonzero(dev)[0]
    onset = int(nz[0]) if len(nz) else None

    # TWO LANDMARKS, FOR TWO DIFFERENT SITUATIONS. I first used one for both and broke the thing that worked.
    #
    #   A ROW THAT RESPONDED is aligned to its own RESPONSE ONSET. The response shape is what the probe revealed,
    #   and reading it from the onset makes it invariant to the entity's internal latency.
    #
    #   A ROW THAT DID NOT RESPOND has no onset, and aligning it to the window start lets the latency leak in: it
    #   then carries the baseline output as seen from the EXPERIMENTER'S clock, shifted by exactly the internal
    #   delay. Measured: a channel lengthened by a detour scored d = 0.087 against its own twin -- a false
    #   DIFFERENCE produced entirely by where I chose to start reading. Such a row is aligned instead to the
    #   entity's OWN first rising edge: a behavioural landmark. In a droplet you do not know an entity's internal
    #   delay and you have no business assuming it.
    #
    # Using the rising edge for BOTH was worse (d = 0.154), because `ref` wraps inside the window while `onset`
    # does not, so their difference is invariant only modulo a period. The landmark must match the question.
    rise = [i for i in range(1, len(bas)) if bas[i] == 1 and bas[i - 1] == 0]
    ref = (onset if onset is not None else (rise[0] if rise else 0))
    a_lo = lo + ref
    if a_lo + W_ALIGN > ep.T:
        raise ProvenanceError(f"the aligned block [{a_lo},{a_lo + W_ALIGN}) runs past the episode (T={ep.T})")
    a_obs = np.array([ep.sample(out_cell, t) for t in range(a_lo, a_lo + W_ALIGN)], dtype=np.uint8)
    a_bas = np.array([base.sample(out_cell, t) for t in range(a_lo, a_lo + W_ALIGN)], dtype=np.uint8)
    a_dev = (a_obs != a_bas).astype(np.uint8)

    if onset is None:
        return {"aligned": a_dev, "absolute": a_obs, "latency": None,
                "persistent": 0, "recovery": None, "responded": 0}
    # MEMORY = a TRANSIENT perturbation with a PERMANENT mark. Judged on the window's TAIL -- long after the
    # longest latency and the longest transient -- so that "still responding" is never mistaken for "changed
    # forever". Nothing else in this substrate produces it.
    persistent = int(dev[-TAIL:].any())
    recovery = None if persistent else int(nz[-1] - onset + 1)
    # THE ABSOLUTE RESPONSE, not merely the deviation. A deviation-only fingerprint is BLIND TO OUTPUT INVERSION:
    # AND(clk,1) = clk and XOR(clk,1) = NOT clk deviate from their own baselines on exactly the same steps, in
    # opposite directions, so their deviation patterns are IDENTICAL. Measured in development: d(AND, XOR) = 0.0000.
    return {"aligned": a_dev, "absolute": a_obs, "latency": onset - ref, "persistent": persistent,
            "recovery": recovery, "responded": 1}


def acquire(world, world_id: str, cells: dict, out_cell, arm: str) -> dict:
    """Run the fixed battery. Every probe, every phase offset, in the frozen order, for every system alike."""
    probes = battery(cells, arm)
    base = run_episode(world, world_id, "fp-base", {}, T_OBS)
    rows, n_valid, n_total, n_vacuous = {}, 0, 0, 0
    for (name, kind, cell, val, hold) in probes:
        rows[name] = []
        for t0 in range(CLK_P):                          # EVERY phase offset -- the battery does not choose one
            n_total += 1
            at = T_PROBE + t0
            try:
                if kind == "pulse":
                    ep = pulse_episode(world, world_id, f"fp-{name}-{t0}", cell, val, at, T_OBS)
                else:
                    ep = _sustained(world, world_id, f"fp-{name}-{t0}", cell, val, at, hold)
            except ProvenanceError:
                rows[name].append(None)                  # the probe did not take: recorded as MISSING, never as 0
                n_vacuous += 1
                continue
            rows[name].append(_row(base, ep, out_cell, t0))
            n_valid += 1
    n_resp = sum(1 for name in rows for r in rows[name] if r is not None and r["responded"])
    return {"rows": rows, "n_valid": n_valid, "n_total": n_total, "n_vacuous": n_vacuous,
            "coverage": n_valid / max(n_total, 1),
            # RESPONSIVENESS is not coverage. Every probe may take, and the system may still say nothing: a
            # saturated OR gate is stuck high and no external perturbation moves it. Its fingerprint is all
            # zeros, and an all-zero fingerprint would silently match every other silent system. That is not an
            # identity; it is an absence of evidence, and it is reported as one.
            "responsive": n_resp / max(n_valid, 1), "n_responded": n_resp,
            "probes": [p[0] for p in probes], "arm": arm}


def _sustained(world, world_id, eid, cell, val, at, hold) -> Episode:
    """A clamp held for `hold` steps beginning at `at`. Non-vacuity is asserted: the cell must actually hold it."""
    g = world.window_clamp(cell, val, at, hold, T_OBS)
    if g.shape[0] != T_OBS:
        raise ProvenanceError(f"{eid}: asked for {T_OBS} samples, received {g.shape[0]}")
    held = g[at:at + hold, cell[0], cell[1]]
    if not np.all(held == val):
        raise ProvenanceError(f"{eid}: clamp {cell} -> {val} DID NOT TAKE")
    return Episode(world_id, eid, {cell: val}, hold, T_OBS, g, (), "sustained")


# ---------------------------------------------------------------- normalization (frozen rule)
def canonical(acq: dict, contaminant: dict | None = None) -> dict:
    """THE FINGERPRINT. A frozen normalization, applied identically to every system.

    PHASE INVARIANCE BY QUOTIENT, not by averaging. A global phase shift cyclically PERMUTES the eight
    offset-rows of each probe, so sorting the rows lexicographically is an exact group quotient -- the same move
    that rescued the V4 timing head, and for the same reason. Averaging over phase would integrate out the signal
    along with the nuisance, which is what killed V3.

    LATENCY IS REPORTED, NEVER DISTANCED. Each row is onset-aligned before it enters the vector, so a retimed but
    behaviourally identical system is not thereby a different one. The latencies are carried alongside, in a
    separate field that no distance ever reads.

    `contaminant` is the MUST-FAIL control: it injects description-level quantities (a class label, a lag set) that
    the contract forbids, so that the benchmark can show the false difference reappear.
    """
    blocks, names, lat, pers = [], [], [], []
    for name in acq["probes"]:
        rows = acq["rows"][name]
        good = [r for r in rows if r is not None]
        if not good:
            blocks.append(np.full(2 * W_ALIGN + 1, 255, dtype=np.uint8))  # MISSING: a sentinel, never a zero
            names.append(name)
            continue
        stack = sorted([tuple(r["aligned"].tolist()) + tuple(r["absolute"].tolist()) + (r["persistent"],)
                        for r in good])
        blocks.append(np.concatenate([np.array(row, dtype=np.uint8) for row in stack]))
        names.append(name)
        lat += sorted([r["latency"] for r in good if r["latency"] is not None])
        pers += [r["persistent"] for r in good]
    out = {"blocks": blocks, "names": names, "latencies": lat, "persistence": pers,
           "coverage": acq["coverage"], "responsive": acq["responsive"], "arm": acq["arm"]}
    if contaminant:
        # FORBIDDEN by the contract. Present ONLY so the must-fail control can prove the exclusion is load-bearing.
        out["blocks"] = blocks + [np.frombuffer(str(sorted(contaminant.items())).encode(), dtype=np.uint8)]
        out["names"] = names + ["FORBIDDEN_description_label"]
        out["CONTAMINATED"] = True
    return out


def distance(a: dict, b: dict) -> float:
    """The mean, over PROBE BLOCKS, of each block's normalized Hamming distance.

    Not a Hamming distance over the concatenation. A long probe block would otherwise dominate a short one purely
    by being long, and the coordinate system's weights would be an accident of how many samples each probe happens
    to produce. Per-block normalization makes every probe count once -- which is also what makes the L1 control
    honest: a smuggled class label becomes ONE MORE BLOCK, weighted like any other, instead of a few bytes lost in
    a vector of sixteen hundred.
    """
    if a["names"] != b["names"]:
        raise ValueError("fingerprints from different batteries are not comparable: "
                         f"{set(a['names']) ^ set(b['names'])}")
    ds = []
    for x, y in zip(a["blocks"], b["blocks"]):
        n = max(len(x), len(y))
        x = np.pad(x, (0, n - len(x)), constant_values=255)
        y = np.pad(y, (0, n - len(y)), constant_values=255)
        ds.append((x != y).sum() / n)
    return float(np.mean(ds))


# ---------------------------------------------------------------- the verdict. It never says SAME.
def compare(a: dict, b: dict, r_continuity: float, r_separation: float) -> dict:
    """INDISTINGUISHABLE_UNDER_REPERTOIRE / DIFFERENT / INDETERMINATE.

    There is no SAME. Two systems that no admissible probe can separate form an EQUIVALENCE CLASS; calling them one
    individual would be an assertion the measurement does not license, and the whole programme exists because that
    assertion is easy to make and hard to retract.
    """
    cov = min(a["coverage"], b["coverage"])
    d = distance(a, b)
    if cov < COVERAGE_FLOOR:
        return {"verdict": "INDETERMINATE", "distance": d, "coverage": cov,
                "why": f"probe coverage {cov:.2f} below the frozen floor {COVERAGE_FLOOR}"}
    if a["responsive"] == 0.0 or b["responsive"] == 0.0:
        return {"verdict": "INDETERMINATE", "distance": d, "coverage": cov,
                "responsive": (a["responsive"], b["responsive"]),
                "why": "at least one system answered NOTHING to every probe in this battery. Silence is not a "
                       "fingerprint, and two silent systems are not the same system."}
    if d <= r_continuity:
        return {"verdict": "INDISTINGUISHABLE_UNDER_REPERTOIRE", "distance": d, "coverage": cov,
                "why": "no admissible probe in this battery separated them. This is an equivalence class, "
                       "NOT an identity."}
    if d >= r_separation:
        return {"verdict": "DIFFERENT", "distance": d, "coverage": cov,
                "why": "at least one probe response differs"}
    return {"verdict": "INDETERMINATE", "distance": d, "coverage": cov,
            "why": f"distance {d:.4f} lies between the frozen continuity radius {r_continuity} and the "
                   f"separation radius {r_separation}"}
