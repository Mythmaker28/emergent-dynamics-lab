"""CHMR — the pulse-restore RESPONSE contrast, computed with the SEALED estimators.

Declared honestly: the HALO_PULSE_RESTORE arm, the G7 gate and the requirement that the future
response be reported are all in the sealed protocol, and the estimators below are imported
unmodified from the sealed `chmr_analyse.py`. What is not in the sealed driver is one extra
paired contrast — HALO_PULSE_RESTORE against MATCHED_SHAM on the response at the END time —
which G7 needs and the sealed driver's loop did not enumerate. Rather than edit a sealed file
and break its hash, it is computed here. No estimator, threshold or margin is changed.
"""
from __future__ import annotations
import sys, json
sys.path.insert(0, "/home/claude/sweep")
import numpy as np
import chmr_analyse as A


def pulse_response(B):
    rows = []
    for b in B:
        r = {"seed": b["seed"]}
        for arm in ("MATCHED_SHAM", "HALO_PULSE_RESTORE", "HALO_CROSS"):
            a = A.resp(b, arm, "A", "response_end")
            bb = A.resp(b, arm, "B", "response_end")
            if a is None or bb is None:
                continue
            r[f"{arm}|signed"] = float((a - bb).mean())
            r[f"{arm}|norm"] = float(np.linalg.norm(a - bb))
        rows.append(r)
    out = {"n": len(rows), "rows": rows}
    for ref in ("HALO_PULSE_RESTORE", "HALO_CROSS"):
        d = [r[f"{ref}|signed"] - r["MATCHED_SHAM|signed"] for r in rows
             if f"{ref}|signed" in r and "MATCHED_SHAM|signed" in r]
        if d:
            out[f"{ref}_minus_MATCHED_signed_response_at_END"] = {
                "median": __import__("statistics").median(d), "ci95": A.boot(d),
                "mean_t_ci95": A.t_ci(d), "sign_test": A.sign_test(d),
                "randomisation_p": A.randomisation_p(d)}
    # the core gap at the END, for the same arms, so the response and the core can be compared
    for arm in ("MATCHED_SHAM", "HALO_PULSE_RESTORE", "HALO_CROSS"):
        v = [A.cplus(b, arm, A.T_END, "A") - A.cplus(b, arm, A.T_END, "B") for b in B
             if A.cplus(b, arm, A.T_END, "A") is not None
             and A.cplus(b, arm, A.T_END, "B") is not None]
        if v:
            out[f"core_gap_END_{arm}"] = {"median": __import__("statistics").median(v),
                                          "ci95": A.boot(v)}
    return out


if __name__ == "__main__":
    out = {}
    for geom, split in (("FAR", "DEV"), ("FAR", "CONF"), ("NEAR", "HELD")):
        B = A.load(geom, split)
        if not B:
            continue
        out[f"{geom}_{split}"] = pulse_response(B)
        v = out[f"{geom}_{split}"]
        print(f"=== {geom}/{split} (n={v['n']}) ===")
        for k in ("HALO_PULSE_RESTORE_minus_MATCHED_signed_response_at_END",
                  "HALO_CROSS_minus_MATCHED_signed_response_at_END"):
            if k in v:
                d = v[k]
                print(f"  {k:52s} median {d['median']:+.4f} CI95 [{d['ci95'][0]:+.4f};"
                      f"{d['ci95'][1]:+.4f}] p={d['sign_test']['p']:.5f} "
                      f"rand p={d['randomisation_p']:.5f}")
        for k in ("core_gap_END_MATCHED_SHAM", "core_gap_END_HALO_PULSE_RESTORE",
                  "core_gap_END_HALO_CROSS"):
            if k in v:
                print(f"  {k:52s} median {v[k]['median']:+.4f} CI95 "
                      f"[{v[k]['ci95'][0]:+.4f};{v[k]['ci95'][1]:+.4f}]")
    json.dump(out, open("chmr_pulse_response.json", "w"), indent=1, default=str)
