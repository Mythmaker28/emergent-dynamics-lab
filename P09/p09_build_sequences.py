"""P09 -- build the exogenous requested-quantity sequences from the P08 08B SINK_FLOOR
complete event ledger (320/320 events per block, no sub-sampling), and seal them.

Donor mapping is cyclic between DISTINCT blocks: receiver block k of a size replays donor
block (k+1) mod 9 of the SAME size from 08B. Requests are scaled by M256_receiver /
M256_donor so the sequence is dimensionless with respect to the receiving block's mass.
For every event the four quantities the mandate requires are preserved separately.
"""
from __future__ import annotations
import csv, hashlib, json, math
from pathlib import Path

SRC = Path("../P08/p08b_event_ledger.csv")
SEEDS = 9
OUT = {"source": "P08 08B SINK_FLOOR event ledger, complete (320 events per block)",
       "donor_mapping": "receiver block index k -> donor block index (k+1) mod 9, same size, "
                        "never the same block",
       "scaling": "requested_k = donor realized_sink_k * (M256_receiver / M256_donor)",
       "preserved_per_event": ["WHEN", "SOURCE_REQUESTED", "SINK_REQUESTED",
                               "SOURCE_REALIZED", "SINK_REALIZED"],
       "sequences": {}}

rows = [r for r in csv.DictReader(open(SRC)) if r["arm"] == "SINK_FLOOR"]
by = {}
for r in rows:
    by.setdefault((r["size"], r["block"]), []).append(r)
for k in by:
    by[k].sort(key=lambda r: int(r["time"]))

for size in ("24", "32"):
    blocks = sorted(b for (s, b) in by if s == size)
    for i, donor in enumerate(blocks):
        ev = by[(size, donor)]
        seq = []
        for r in ev:
            seq.append({"WHEN": int(r["time"]),
                        "SINK_REQUESTED": float(r["realized_sink"]),
                        "SOURCE_REQUESTED": float(r["realized_sink"]),
                        "SINK_REALIZED": float(r["realized_sink"]),
                        "SOURCE_REALIZED": float(r["realized_sink"])})
        nz = [s for s in seq if s["SINK_REQUESTED"] > 1e-12]
        OUT["sequences"][f"L{size}|donor_index_{i}"] = {
            "donor_block": donor, "M256_donor": float(ev[0]["M256"]),
            "n_events": len(seq), "n_nonzero": len(nz),
            "total_requested": sum(s["SINK_REQUESTED"] for s in seq),
            "total_over_M256_donor": sum(s["SINK_REQUESTED"] for s in seq)
                                     / float(ev[0]["M256"]),
            "events": seq}

txt = json.dumps(OUT, indent=1, sort_keys=True)
Path("p09_sequences.json").write_text(txt)
h = hashlib.sha256(Path("p09_sequences.json").read_bytes()).hexdigest()
Path("p09_sequences.sha256").write_text(h + "  p09_sequences.json\n")
print(f"SEALED p09_sequences.json  sha256 = {h}")
for k, v in sorted(OUT["sequences"].items()):
    print(f"  {k:<22} donneur={v['donor_block']:<14} n={v['n_events']} "
          f"non-nuls={v['n_nonzero']:>3}  total/M256 = {v['total_over_M256_donor']:.4f}")
