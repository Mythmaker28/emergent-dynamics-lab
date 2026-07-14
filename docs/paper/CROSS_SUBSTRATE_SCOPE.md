# CROSS-SUBSTRATE SCOPE (deliverable 7)
`CROSS-SUBSTRATE: STRUCTURAL PASS`

FitzHugh–Nagumo (non-exponential spike-and-recovery profile) SUPPORTS, empirically:
* structural identified-set propagation (the T6 inequalities apply to any known response profile);
* no false exact-zero under low SNR (0 false {0} on the FHN audit);
* honest widening under ill-conditioning / finite-window bias (75/75 widen-or-cover);
* contamination-class logic (attenuate / amplify / clean-anchor / sparse) transfers.

It does NOT support:
* general quantitative point recovery;
* universal calibration;
* substrate-independent point accuracy.

Therefore the title, abstract and conclusion assert STRUCTURAL, not quantitative, generality: the
identifiability *classes* and the no-false-zero property transfer across substrates; the numerical value of
`q` remains substrate- and instrumentation-specific. Evidence: `docs/noise_aware/REPLICATION_AND_FHN.md`
(structural coverage 0.984, false-zero 0). Claim 9 of `FINAL_CLAIM_TABLE.md`.
