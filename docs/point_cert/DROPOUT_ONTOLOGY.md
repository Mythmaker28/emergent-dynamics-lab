# DROPOUT ONTOLOGY (deliverable 2) — EXP-GT-PC-00
A dropout is an OBSERVATION failure of a reference channel, distinct from a genuinely unresponsive-but-valid
channel. Signatures (each modelled in `pcgen.py`):
* **missing / disconnection** — the channel is pure noise (no profile-aligned signal);
* **gain collapse** — coefficient scaled by ~0.02 (near-zero gain);
* **flatline** — constant value + tiny noise (variance collapse);
* **bandwidth collapse** — the response is heavily low-passed, destroying the profile shape;
* **intermittent** — a random subset of samples replaced by noise;
* **post-calibration / post-intervention** — the channel is valid during calibration, then drops out after
  the intervention onset (calibration transfer fails).

## Admission region and the operational test
The point layer's C2 flags a channel dropout-SUSPECT when the profile fit explains less than `DROP_R2=0.10`
of the channel variance (R² < 0.10): a genuine response of ANY magnitude produces profile-aligned variance,
whereas missing/gain/flatline/bandwidth dropouts do not. A point may not be DETERMINED by a dropout-suspect
channel (unless that channel is externally declared essential).

## Irreducible ambiguity
At low SNR a genuinely tiny valid response and a dropout are not separable from data alone. The instrument
does NOT resolve the ambiguity: it PRESERVES it — the selection-aware set `Q_wide` is widened to include
both the "channel is a dropout" and "channel is a tiny response" hypotheses (via leave-one-reference-out),
and point certification is FORBIDDEN. A small channel is never deleted merely for being inconveniently small.
