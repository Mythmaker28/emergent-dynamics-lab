# FCRA00_PROTOCOL_DEVIATIONS

FCRA00 itself introduces **no** deviations: zero engine starts, no seed/state generation, no
checkpoint regeneration, the immutable object and tube untouched, `main` never moved, append-only.

It **records and corrects** two inherited FSQBT00 defects (which it cannot repair, only document):

* **Seed-70000 diagnostic start.** One unauthorized diagnostic engine start (against a budget of 0),
  proven from the transcript to have opened no scientific outcome
  (`ONE_UNAUTHORIZED_START__NO_SCIENTIFIC_OUTCOME_OPENED_PROVEN`). Corrected charged total: **61**.
  `FSQBT00_PROTOCOL_CONFORMITY_STATUS = NONCONFORMANT`; an append-only correction never restores PASS.
* **Full-checkpoint evidence gap.** The FSQBT00 original tip committed only digests of the 12
  full-field checkpoints (`INCOMPLETE_MISSING_FULL_CHECKPOINT_BYTES`). FCRA00 recovered the exact 12
  bytes (12/12 vs committed digests) and committed them on the child branch
  (`CURRENT_CHAIN_EVIDENCE_STATUS = COMPLETE_AFTER_APPEND_ONLY_CHILD_RECOVERY`); this never makes the
  historical FSQBT00 tip self-contained retroactively.

Inherited D0–D4 (from earlier programmes) remain historical facts and are not repaired.
