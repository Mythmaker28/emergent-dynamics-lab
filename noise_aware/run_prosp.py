"""HASH-GATED PROSPECTIVE RUNNER (chunk). Instrument frozen; feeds it and scores. Deterministic,
content-addressed per-case seeds so chunking cannot change any result. Usage: run_prosp.py START END
"""
from __future__ import annotations
import numpy as np, json, hashlib, sys, os
import nasi, prospgen

FREEZE = "../docs/noise_aware/NASI_FREEZE_MANIFEST.json"
ALPHA = 0.05

def hash_gate():
    man = json.load(open(FREEZE))
    for f, h in man["frozen_files"].items():
        got = hashlib.sha256(open(os.path.join("..", f), "rb").read()).hexdigest()
        assert got == h, f"HASH GATE FAILED for {f}\n got {got}\n exp {h}"
    return man

def score(r, qmag):
    if r.status in nasi.ABSTAIN: return None
    return r.contains(qmag)

def run(start, end):
    man = hash_gate()
    rows = []
    for i in range(start, end):
        cs = prospgen.build(i); q = cs["qmag"]; nz = q > 1e-9
        for arm, ctr in (
            ("O", nasi.Contract(sign=cs["sign_true"], clean_anchor=cs["anchor_true"], sparsity_s=cs["sparsity_true"],
                                provenance={"sign":"benchmark_truth","anchor":"benchmark_truth"})),
            ("B", nasi.Contract(sign=cs["op_sign"], clean_anchor=cs["op_anchor"], sparsity_s=cs["op_sparsity"],
                                provenance={"sign":"sensor_physics" if cs["op_sign"] else None,
                                            "anchor":"intervention_geometry" if cs["op_anchor"] else None}))):
            r = nasi.identify(cs["Y"], cs["p"], cs["lam"], ctr, alpha=ALPHA,
                              rng=np.random.default_rng(prospgen.PROSP_SEED_BASE + i + (0 if arm=="O" else 7)))
            c = score(r, q)
            used_truth = bool(arm=="B" and ((ctr.sign is not None and cs["op_sign"] is None) or
                                            (ctr.clean_anchor and not cs["op_anchor"])))
            rows.append(dict(i=i, arm=arm, stratum=cs["stratum"], band=cs["band"], nf=cs["nf"], m=int(cs["m"]),
                             snr=round(float(cs["snr"]),3), qmag=float(q), nonzero=bool(nz), status=r.status,
                             emit=bool(r.status in nasi.EMITTING),
                             contains=(None if c is None else bool(c)),
                             exact_zero=bool(r.qset==[(0.0,0.0)] and r.status!=nasi.EXACTZERO),
                             invalid_point=bool(r.status==nasi.POINT and c is False),
                             width=(r.width_rel(q) if nz else None), zero_in=bool(r.zero_in),
                             used_truth=used_truth))
    return rows

if __name__ == "__main__":
    start, end = int(sys.argv[1]), int(sys.argv[2])
    rows = run(start, end)
    os.makedirs("../results/EXP-GT-NASI-PROSPECTIVE", exist_ok=True)
    out = f"../results/EXP-GT-NASI-PROSPECTIVE/rows_{start}_{end}.json"
    json.dump(rows, open(out, "w"))
    # immediate stop-rule signal for this chunk
    f0 = sum(1 for r in rows if r["exact_zero"] and r["nonzero"])
    ip = sum(1 for r in rows if r["invalid_point"])
    print(f"chunk [{start},{end}) rows={len(rows)} false_zero_nonzero={f0} invalid_points={ip} -> {out}")
