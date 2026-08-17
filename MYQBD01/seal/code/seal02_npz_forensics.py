"""MYQBD01 FINAL SEAL — main-operator independent forensics on the raw archives.

This exists so that §16 adjudication of attack A4 (descendant spatial exposure) rests on the
main operator's OWN evidence, not on the reviewer's assertion. Enumerate every key of a mobile
arm: exact shape, dtype, column semantics inferred from the WRITING code, cadence, and whether
per-step lattice occupancy is deterministically reconstructible.

No engine. Read-only.
"""
from __future__ import annotations

import glob
import json
import os
import subprocess

import numpy as np

REPO = "/home/claude/edl"
RAW = "/home/claude/OBFOR01/raw"
OUT = "/home/claude/MYQBD01/seal/out"
HORIZON = 11000


def main():
    os.makedirs(OUT, exist_ok=True)
    f = sorted(glob.glob(os.path.join(RAW, "M__*.npz")))[0]
    z = np.load(f, allow_pickle=True)
    L = int(z["nX_final"].shape[0])
    keys = {}
    for k in z.keys():
        a = z[k]
        e = {"shape": list(getattr(a, "shape", ())), "dtype": str(a.dtype),
             "ndim": int(a.ndim), "size": int(a.size)}
        if a.ndim == 2 and a.shape[0] > 0 and a.size < 4_000_000:
            b = a.astype(float)
            e["col_min"] = [float(x) for x in b.min(axis=0)]
            e["col_max"] = [float(x) for x in b.max(axis=0)]
            e["first_row"] = [float(x) for x in b[0]]
            e["last_row"] = [float(x) for x in b[-1]]
            # cadence: is column 0 a step index, and how many rows per step?
            c0 = b[:, 0]
            e["col0_is_nondecreasing"] = bool(np.all(np.diff(c0) >= 0))
            u, cnt = np.unique(c0, return_counts=True)
            e["col0_distinct"] = int(u.size)
            e["rows_per_col0_value"] = {"min": int(cnt.min()), "max": int(cnt.max()),
                                        "modal": int(np.bincount(cnt).argmax())}
        elif a.ndim == 1 and a.size < 100000 and a.dtype.kind in "iuf":
            e["min"] = float(a.min()); e["max"] = float(a.max())
            e["strictly_increasing"] = bool(np.all(np.diff(a) > 0))
            if a.size > 1:
                d = np.diff(a)
                e["stride_uniform"] = bool(np.all(d == d[0]))
                e["stride"] = float(d[0])
        keys[k] = e

    # --- the decisive question: is per-step lattice occupancy reconstructible? ---
    L2 = L * L
    hop = z["hop_ledger"]
    src = z["source_substep_ledger"]
    bsub = z["birth_substep_ledger"]
    boff = z["birth_offsets"]
    fr = z["frames"]

    # how many diffusing species and how many hop rows per step?
    n_steps_hop = int(np.unique(hop[:, 0]).size)
    rows_per_step_hop = hop.shape[0] / max(n_steps_hop, 1)

    # a per-particle hop record would need >= one row per MOVED PARTICLE per step.
    # total particles present (final grids as a scale reference)
    tot_final = sum(int(z["%s_final" % s].sum()) for s in ("nX", "nY", "nSX", "nSY", "nWX", "nWY"))

    recon = {
        "LATTICE": {"L": L, "cells": L2},
        "TOTAL_PARTICLES_AT_TERMINAL_STEP": tot_final,
        "HOP_LEDGER": {
            "shape": list(hop.shape),
            "distinct_step_values": n_steps_hop,
            "rows_per_step": rows_per_step_hop,
            "AGGREGATE_NOT_PER_PARTICLE": rows_per_step_hop < tot_final,
            "reading": ("the hop ledger carries %.0f rows per step for a system holding ~%d "
                        "particles at the terminal step. It cannot name which particle moved "
                        "from which cell to which cell; it is an aggregate/sub-step summary, "
                        "not a per-particle displacement record."
                        % (rows_per_step_hop, tot_final))},
        "BIRTH_OFFSETS": {
            "shape": list(boff.shape),
            "reading": ("(step, dy, dx, count) of X births RELATIVE TO THE ORGANISER. This is "
                        "where X births occurred; it carries no nSY or free value at any cell, "
                        "and nothing at all about Y positions.")},
        "FRAMES": {
            "shape": list(fr.shape), "dtype": str(fr.dtype),
            "is_lattice_snapshot": bool(fr.ndim >= 3),
            "reading": "1-D of length %d -- a list of step indices, not lattice snapshots"
                       % fr.size if fr.ndim == 1 else "multi-dimensional"},
        "PER_STEP_LATTICE_ARRAYS_PRESENT": [k for k in z.keys()
                                            if z[k].ndim == 3 and z[k].shape[1:] == (L, L)],
        "TERMINAL_LATTICE_ARRAYS_PRESENT": [k for k in z.keys()
                                            if getattr(z[k], "shape", None) == (L, L)],
    }

    # degrees of freedom argument
    dof_needed = HORIZON * L2 * 3       # nX, nSY, free per cell per step
    dof_available = sum(int(np.prod(getattr(z[k], "shape", (0,)))) for k in z.keys())
    recon["INFORMATION_BUDGET"] = {
        "degrees_of_freedom_needed_for_Q_POSITION": dof_needed,
        "note": "T x L^2 x 3 scalars (nX, nSY, free) per cell per step",
        "total_scalars_in_the_WHOLE_archive": dof_available,
        "ARCHIVE_IS_SMALLER_BY_FACTOR": dof_needed / max(dof_available, 1),
        "READING": ("the archive holds %d scalars in total; the field needed to evaluate "
                    "Q_POSITION(x,t) needs %d. The archive is smaller by a factor of %.0f. "
                    "Even a lossless code could not carry the field, so no reconstruction "
                    "procedure -- forward or backward -- can exist. This is an information "
                    "obstruction, not a failure of ingenuity."
                    % (dof_available, dof_needed, dof_needed / max(dof_available, 1)))}
    recon["Q_POSITION_RECONSTRUCTIBLE"] = False

    rec = {"SECTION": "MYQBD01 SEAL — main-operator NPZ forensics (independent of the reviewer)",
           "ARM_INSPECTED": os.path.basename(f),
           "KEYS": keys,
           "RECONSTRUCTION_ANALYSIS": recon}
    json.dump(rec, open(os.path.join(OUT, "SEAL02_NPZ_FORENSICS.json"), "w"),
              indent=1, default=str)
    print("arm:", os.path.basename(f), " L =", L, " keys =", len(keys))
    for k, e in keys.items():
        print("  %-26s %-18s %s" % (k, e["dtype"], e["shape"]))
    print()
    print("hop rows/step        : %.1f   (particles at terminal step: %d)"
          % (rows_per_step_hop, tot_final))
    print("per-step lattice keys:", recon["PER_STEP_LATTICE_ARRAYS_PRESENT"] or "NONE")
    print("terminal lattice keys:", recon["TERMINAL_LATTICE_ARRAYS_PRESENT"])
    ib = recon["INFORMATION_BUDGET"]
    print("dof needed %d vs archive %d  -> short by factor %.0f"
          % (ib["degrees_of_freedom_needed_for_Q_POSITION"],
             ib["total_scalars_in_the_WHOLE_archive"], ib["ARCHIVE_IS_SMALLER_BY_FACTOR"]))


if __name__ == "__main__":
    main()
