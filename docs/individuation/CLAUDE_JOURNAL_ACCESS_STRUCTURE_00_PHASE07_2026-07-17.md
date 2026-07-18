# Claude journal — ACCESS-STRUCTURE-00 Phase 0.7 (CORE-SUFFICIENCY-00 DEV pilot) — 2026-07-17

Branch `claude/access-structure-noswap-design-06`, from Phase 0.6B tip `7deeb8e`. DEV-only causal pilot; no
prospective seed; no confirmatory certification. Read the competing Codex Phase 0.6A report (`bf5901a`,
STOP-TRANSPLANT) via `git show`; did not merge.

## Task and reframing
Human accepted 0.6A STOP-TRANSPLANT and 0.6B GO for DEV mechanics only, and reframed to CORE-SUFFICIENCY-00: does the
history-bearing core state remain causally sufficient to alter future feeding when the environment is replaced by a
fixed boundary? Ran the predeclared 2×2 (M_OWN/M_STD × K_COUPLED/K_CLAMPED) under the frozen probe + lam_plus=0 +
up_ref=0, on 50002/50004/50005/50007.

## Verdict: STOP-CORE-SUFFICIENCY

## Decisive findings
- **Task 1 audit is the crux.** The same-seed no-history twin is NOT memory-free: its ambient core m_plus (~0.19–0.34)
  is comparable to the history-laden target (~0.25–0.33). So M_STD (twin-based) swaps history for an on-manifold
  ambient baseline of similar magnitude; the immediate own→std core m_plus change is sign-variable (−0.136…+0.130).
  M_STD changes only Mf on the core (verified), rho/body preserved, non-conservative in extensive memory.
- **Reference reversal (STOP trigger):** world-level tau_coupled reverses sign between the twin reference (negative,
  ~−0.02) and the erase reference (positive, ~+0.15) in ALL 4 worlds.
- **Small, direct-readout-mediated:** twin-referenced tau collapses to 31% under lam_plus=0; up_ref=0 leaves tau
  unchanged (global channel common-mode). Interaction evaluated (NOT asserted): ~10% of tau — clamp doesn't dominate
  the effect, but is not exactly common-mode.
- **Horizon discipline OK:** core m_plus contrast retained 0.59–0.87 to step 40 (coupled and clamped); core stays
  interpretable; slow memory diffusion (D_m=0.01) protects the body-bound memory from the standardized boundary.
- **Differential verification:** nm region-erase reproduces the established ~0.05 own fraction (second oracle).
- 144/144 arms viable across all conditions.

## Corrections made (per human)
- Task 5: "comoving halo ≈4 cells" renamed to DEV perturbation-propagation / influence-decay radius (~4 cells), NOT a
  causal ownership boundary. No radius chosen from feeding.
- Task 6: H_PHASE not dismissed for Markov-ness; relational phase may be encoded in the snapshot. The clamp preserves
  core correlations; M_STD overwrites them (would confound any phase claim). No phase experiment launched.

## What STOP means / doesn't
STOPs the prospective test AS DESIGNED (twin-referenced M_STD is reference-fragile + direct-readout). NOT evidence for
environmental/redundant/relational ownership. The core memory does alter feeding under the clamp (tau_clamped≠0, small,
retained to step 40), but reference-fragile and direct-readout-mediated. The 03G total-memory effect (erase-referenced)
survives the clamp but is a different, already-certified estimand with an off-manifold null. Bounded correction
(redefine the null) is possible but NOT pursued (no flattering arms; a negative DEV result doesn't prove environmental
ownership).

## Deliverables (new Phase 0.7 files; 0.6B preserved)
experiments/individuation/access_structure_noswap_phase07_pilot.py + test_access_structure_noswap_phase07.py (5 pass);
docs/individuation/ACCESS_STRUCTURE_00_PHASE07_CORE_SUFFICIENCY_{REPORT.md,RESULTS.json(+.sha256),PREREG_DRAFT.md,
POWER.md} + this journal. RESULTS.json sha256 82e4bbc9becd91d5cb8a8453f067e9921052405d8d085caa63e0ab9affb5e7f0
(deterministic: 1-world rerun hash stable). Reused verbatim: nm.measure, cc, tdd, DiagEngine, Phase-0.6B clamp
operators. No edits to 0.6B files, transplant operator, Codex/0.6A files, indexes, or certified results. main
f3921a4 untouched.

## Next
Human review of the STOP verdict. If a corrected reference-robust null is authorised, that is a NEW phase; no seed
selected here.
