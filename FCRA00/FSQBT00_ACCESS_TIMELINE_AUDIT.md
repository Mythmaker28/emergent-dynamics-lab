# FSQBT00_ACCESS_TIMELINE_AUDIT

## Seed 70000 diagnostic start

{
 "probe_command_timestamp_UTC": "2026-08-11T01:02:33.137Z",
 "probe_requestId": "req_011Cdv4PLmUgJP4okcMnp7KA",
 "probe_when": "after FCRA00-parent commit 1 (master freeze b9f25a23), before FSQBT00 commit 2",
 "probe_construction": "K.set_geometry('FAR'); found(70000); advance(T_FOUND); apply_dual_history(HIST_H, HIST_L) [alloc 0]; advance(SETTLE)",
 "probe_reads": [
  "Z.t0_masks(st) -> printed only eligible=yes (construction admissibility, connected-components of rho>0.30; the SAME predicate used in construction, NOT a response outcome)",
  "wall-clock timing of founder+settle and of 400 e.step calls"
 ],
 "probe_did_NOT_read": [
  "q_channels / X_A / X_B",
  "any delta vs a sham",
  "M2 / margin",
  "any P2/e2 score",
  "any R0/R1/R2/I1/I2",
  "any threshold TAU",
  "any reader value on the stepped state (cur was discarded)"
 ],
 "files_created_by_probe": "none (in-memory only; no npz, no series, no score persisted)",
 "seed_70000_status": "CONSUMED and excluded from the FSQBT00 panel (queue N=65100 avoided it)",
 "DIAGNOSTIC_START_STATUS": "ONE_UNAUTHORIZED_START__NO_SCIENTIFIC_OUTCOME_OPENED_PROVEN",
 "consequence": "weakens FSQBT00 protocol conformity (a diagnostic start was spent against a budget of 0) but does NOT by itself contaminate the later sealed 24 active rows: no response outcome was opened, and seed 70000 never entered the panel."
}

**DIAGNOSTIC_START_STATUS = ONE_UNAUTHORIZED_START__NO_SCIENTIFIC_OUTCOME_OPENED_PROVEN**

The exact probe command was recovered from the session transcript (timestamp and requestId above). It constructed seed 70000 and stepped it 400 times to measure wall-clock, then discarded the state. Its only non-timing read was `t0_masks`, the construction-admissibility predicate (connected components of `rho>0.30`), which is identical to the check used to accept or reject a constructed candidate and carries no response information. No reader series, delta, M2, score, quotient or threshold was computed, printed or persisted. Because no scientific outcome was opened and seed 70000 never entered the sealed panel, the deviation is a genuine protocol-conformity breach (one unauthorized diagnostic start) that does not contaminate the 24 sealed active rows.
