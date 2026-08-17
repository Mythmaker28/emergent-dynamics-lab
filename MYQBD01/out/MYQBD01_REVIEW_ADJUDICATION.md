# MYQBD01 — main-operator adjudication of the seal review

```
REVIEWER_VERDICT = CANDIDATE_DISPOSITION_SUPPORTED
FINDINGS         = 32
ACCEPTED         = 29   ACCEPTED_WITH_QUALIFICATION = 3   REJECTED = 0
REPAIRED         = 16   RECORDED = 3   CARRIED_TO_SUCCESSOR = 1   NO_ACTION = 12
LOAD_BEARING_DEFECTS = 0
DISPOSITION_CHANGED  = NO
```

Every finding was re-derived by the operator before being ruled on. Where the
operator's own numbers differ from the reviewer's (F05), the divergence is reported
rather than resolved by preference.

| ID | attack | severity | reviewer | operator ruling | action |
|---|---|---|---|---|---|
| F01 | A1 | LOAD_BEARING | ATTACK_REFUTED | ACCEPTED | NO_ACTION_REQUIRED |
| F02 | A1 | COSMETIC | DEFECT_CONFIRMED | ACCEPTED | REPAIRED_IN_THE_SINGLE_SEAL_COMMIT |
| F03 | A1 | COSMETIC | DEFECT_CONFIRMED | ACCEPTED | REPAIRED_IN_THE_SINGLE_SEAL_COMMIT |
| F04 | A2 | SUBSTANTIVE | ATTACK_REFUTED | ACCEPTED | NO_ACTION_REQUIRED |
| F05 | A2 | SUBSTANTIVE | DEFECT_CONFIRMED | ACCEPTED_WITH_QUALIFICATION | REPAIRED_IN_THE_SINGLE_SEAL_COMMIT |
| F06 | A3 | LOAD_BEARING | ATTACK_REFUTED | ACCEPTED | NO_ACTION_REQUIRED |
| F07 | A4 | LOAD_BEARING | ATTACK_REFUTED | ACCEPTED | NO_ACTION_REQUIRED |
| F08 | A4 | SUBSTANTIVE | DEFECT_CONFIRMED | ACCEPTED | REPAIRED_IN_THE_SINGLE_SEAL_COMMIT |
| F09 | A4 | SUBSTANTIVE | DEFECT_CONFIRMED | ACCEPTED | REPAIRED_IN_THE_SINGLE_SEAL_COMMIT |
| F10 | A4 | SUBSTANTIVE | DEFECT_CONFIRMED | ACCEPTED | REPAIRED_IN_THE_SINGLE_SEAL_COMMIT |
| F11 | A4 | SUBSTANTIVE | DEFECT_PLAUSIBLE | ACCEPTED_WITH_QUALIFICATION | CARRIED_TO_THE_SUCCESSOR_HANDOFF |
| F12 | A5 | SUBSTANTIVE | ATTACK_REFUTED | ACCEPTED | NO_ACTION_REQUIRED |
| F13 | A5 | SUBSTANTIVE | DEFECT_CONFIRMED | ACCEPTED_WITH_QUALIFICATION | REPAIRED_IN_THE_SINGLE_SEAL_COMMIT |
| F14 | A6 | LOAD_BEARING | ATTACK_REFUTED | ACCEPTED | NO_ACTION_REQUIRED |
| F15 | A6 | SUBSTANTIVE | DEFECT_CONFIRMED | ACCEPTED | REPAIRED_IN_THE_SINGLE_SEAL_COMMIT |
| F16 | A7 | SUBSTANTIVE | DEFECT_CONFIRMED | ACCEPTED | REPAIRED_IN_THE_SINGLE_SEAL_COMMIT |
| F17 | A7 | SUBSTANTIVE | DEFECT_CONFIRMED | ACCEPTED | REPAIRED_IN_THE_SINGLE_SEAL_COMMIT |
| F18 | A7 | COSMETIC | ATTACK_REFUTED | ACCEPTED | NO_ACTION_REQUIRED |
| F19 | A8 | LOAD_BEARING | ATTACK_REFUTED | ACCEPTED | NO_ACTION_REQUIRED |
| F20 | A8 | SUBSTANTIVE | DEFECT_CONFIRMED | ACCEPTED | REPAIRED_IN_THE_SINGLE_SEAL_COMMIT |
| F21 | A8 | SUBSTANTIVE | ATTACK_REFUTED | ACCEPTED | REPAIRED_IN_THE_SINGLE_SEAL_COMMIT |
| F22 | A9 | SUBSTANTIVE | ATTACK_REFUTED | ACCEPTED | NO_ACTION_REQUIRED |
| F23 | A9 | SUBSTANTIVE | DEFECT_CONFIRMED | ACCEPTED | REPAIRED_IN_THE_SINGLE_SEAL_COMMIT |
| F24 | A10 | LOAD_BEARING | ATTACK_REFUTED | ACCEPTED | NO_ACTION_REQUIRED |
| F25 | A10 | SUBSTANTIVE | DEFECT_CONFIRMED | ACCEPTED | REPAIRED_IN_THE_SINGLE_SEAL_COMMIT |
| F26 | A11 | SUBSTANTIVE | ATTACK_REFUTED | ACCEPTED | NO_ACTION_REQUIRED |
| F27 | A12 | SUBSTANTIVE | DEFECT_CONFIRMED | ACCEPTED | REPAIRED_IN_THE_SINGLE_SEAL_COMMIT |
| F28 | A12 | SUBSTANTIVE | DEFECT_CONFIRMED | ACCEPTED | RECORDED_NOT_REPAIRABLE |
| F29 | A12 | COSMETIC | DEFECT_CONFIRMED | ACCEPTED | RECORDED_NOT_REPAIRABLE |
| F30 | A12 | SUBSTANTIVE | ATTACK_REFUTED | ACCEPTED | NO_ACTION_REQUIRED |
| F31 | A12 | SUBSTANTIVE | DEFECT_CONFIRMED | ACCEPTED | RECORDED_NOT_REPAIRABLE |
| F32 | A11 | COSMETIC | DEFECT_CONFIRMED | ACCEPTED | REPAIRED_IN_THE_SINGLE_SEAL_COMMIT |

## Operator notes, per finding

**F01** (A1, ACCEPTED) — Concur. Q event-exactness is the mission's load-bearing identity and it survives an exact residual test.

**F02** (A1, ACCEPTED) — Concur. The executed class is WorldOBTC; citing kinetics.py line numbers named an inherited, not an executed, site.

**F03** (A1, ACCEPTED) — Concur. series is post-increment (1..11000), the ledgers pre-increment (0..10999). Undocumented, now documented.

**F04** (A2, ACCEPTED) — Concur. Arm independence is the premise the whole uncertainty treatment rests on; it holds.

**F05** (A2, ACCEPTED_WITH_QUALIFICATION) — Accepted in substance, NOT in its numbers. My own initial-positive-sequence estimator gives mobile mean 8.4277 and max 24.5556 (M__seed9300015), against the reviewer's 9.1967 and 35.335. Same arm, same conclusion, different estimator. The finding is therefore that IAT is estimator-dependent AND heavy-tailed, and that reporting a bare '~7-9' hides both. Both estimates are recorded; neither is canonised.

**F06** (A3, ACCEPTED) — Concur. Every arm mean is listed; separation is complete and not driven by one arm.

**F07** (A4, ACCEPTED) — Concur, and this is the seal's central result: the most load-bearing attack was pressed hardest and failed. Independently re-derived (SEAL02, SEAL03).

**F08** (A4, ACCEPTED) — Concur and verified: source_substep_ledger is (44000,6) with 4 lattice-coordinate columns, 1038 organiser moves over 373 distinct cells in the arm inspected. Labelling it 'scalar' was wrong. The correct reading STRENGTHENS the record: because the organiser trajectory is recorded, Q_ORGANISER is the founder's exact lineage exposure in the mobile branch too.

**F09** (A4, ACCEPTED) — Concur. A load-bearing boolean returned as a literal from a one-archive inspection is not evidence, even when the conclusion is right. Now derived over all 28 archives with every key enumerated and frames decoded.

**F10** (A4, ACCEPTED) — Concur, and verified independently: N_Y == 1 and n_org_cells == 1 at all 308000 recorded steps. This is a STRONGER ground than non-recording and it belonged in §12.

**F11** (A4, ACCEPTED_WITH_QUALIFICATION) — Accepted as a design point, rejected as a defect in the disposition. Re-instrumented replay of seeds 9300000-9300027 is a RUN, not a recovery from recorded data; it cannot move a disposition about what EXISTING data contain. It is a real improvement to the successor's design and is carried there.

**F12** (A5, ACCEPTED) — Concur. The clamp is inactive at admissible kY, so the first-birth reduction is exact.

**F13** (A5, ACCEPTED_WITH_QUALIFICATION) — Accepted: conditions 7 and 8 are ~2e-4 effects at the discovery scale and were presented without magnitude. Qualified: the classification never rested on them. Magnitudes now recorded.

**F14** (A6, ACCEPTED) — Concur. Shared-pool structure verified at source.

**F15** (A6, ACCEPTED) — Concur. Demonstrating non-independence at 1250-5000x the admissible kY is a rhetorical scale, not the mission's scale. The magnitude at kY = 4e-5 is now recorded, and NOT_IDENTIFIABLE is restated as resting on the spatial ground.

**F16** (A7, ACCEPTED) — Concur and verified independently: effective mean-reversion 0.355735 (sd 0.013473 over the 14 static arms) against the claimed phi = 0.20, a factor 1.7787. phi is the OFFER rate, not the replenishment rate. Note the correction moves the error in the CONSERVATIVE direction: recovery is faster than claimed.

**F17** (A7, ACCEPTED) — Concur and verified independently: 101.52% unconditional versus 55.13% conditional on cand_Y >= 1 (E[nSY | cand_Y>=1] = 1.814057). A birth cannot occur when no candidate exists, so the unconditional mean was the wrong denominator.

**F18** (A7, ACCEPTED) — Concur; the earlier internal C1 repair holds.

**F19** (A8, ACCEPTED) — Concur. R = 1.000478048 and the fixed point is non-degenerate.

**F20** (A8, ACCEPTED) — Concur and verified: mean cand_Y_at_org = 0.961651, so c = 3 is 3.12x it, and witness exposure 12 is 3.79x mean Q = 3.169730. 'Q sustained at Q_MAX' was also wrong (the witness uses 12, not 28). A third witness at the arms' OWN measured magnitudes is added: R = 1.000163936 > 1, so non-preclusion no longer rests on any inflated pool.

**F21** (A8, ACCEPTED) — Accepted as a strengthening, and acted on: the measured-magnitude witness is now in the record.

**F22** (A9, ACCEPTED) — Concur. All 28 arms used, no outcome-conditioned inclusion.

**F23** (A9, ACCEPTED) — Concur; same repair as F09. Note the single archive opened was MOBILE, so no static archive entered §12 at all.

**F24** (A10, ACCEPTED) — Concur on the conclusion; the EVIDENCE for it was nonetheless a literal, which is F25.

**F25** (A10, ACCEPTED) — Concur and verified: 0 AST data-access checks existed in the candidate; the requirement was a literal with a comment. A real audit now derives it. The audit immediately caught the seal repair's own read of `frames`, which is disclosed with its justification rather than exempted.

**F26** (A11, ACCEPTED) — Concur. No forbidden claim appears.

**F27** (A12, ACCEPTED) — Concur and verified: 1 of 8 modules. The commit message overstated coverage. The zero-run conclusion is re-grounded on a static import proof that does not depend on the sentinel at all.

**F28** (A12, ACCEPTED) — Concur and verified: 4 seeding entry points exist, 3 are patched; observe.seed_one_organiser is unpatched. The sentinel lives in the inherited PMCR01 tree, which this mission may not rewrite; the gap is recorded, and the static proof makes the zero-run conclusion independent of it.

**F29** (A12, ACCEPTED) — Concur: the witness glob is depth-2 and does not watch the repository tree. Same inherited-tree constraint; recorded, and superseded as a ground by the static proof.

**F30** (A12, ACCEPTED) — Concur; this is now the primary zero-run ground.

**F31** (A12, ACCEPTED) — Concur, and this is the seal's sharpest provenance point. The freeze cannot be retroactively separated without rewriting inherited history, which is forbidden. It is stated openly here and in the final report, and the successor is required to commit its freeze alone. Judged non-load-bearing because the freeze itself declares the mission response-informed and developmental and disclaims blinding, so no claim depends on the ordering.

**F32** (A11, ACCEPTED) — Concur; the seal binding already records the actual tip f88147a and flags decfda5 as superseded.

## Why no defect is load-bearing

every confirmed defect lies in a SUPPORTING CERTIFICATE (a recovery rate, a depletion denominator, a witness pool size, a coverage claim, an evidence loop breadth) or in provenance. None touches the two facts the disposition rests on: (i) no array in any of the 28 archives is position-resolved per step, and decisively kY = 0 so no descendant ever exists; and (ii) the exact operator does not forbid a window at admissible magnitudes. Both were re-derived independently by the operator and both survive. Two corrections (F16, F17) move their numbers in the CONSERVATIVE direction, and two (F10, F21) strengthen the disposition's grounds rather than weakening them.

