# FUTURE-PROSPECTIVE-MEASUREMENT-FEASIBILITY-AND-ROUTE-SELECTION-01R — review journal

Complete record per Part I §11 (R1–R3): every finding, including any judged invalid, with the reason;
every correction; every withdrawal; and the exact package digest each verdict was issued against.

## 1. Packages and digests

| Checkpoint | Commit | `REPORT.md` sha256 | Bytes |
|---|---|---|---|
| 1 — frozen Part I | `f4bf11e4d2a7f7b4704fcd884e050bc94dce91cc` | `b704ccff9d3bd38d608fba2aed2cadad7d2caee53c98e20feea46dc3df74a340` | 34,848 |
| 2 — bridge, spec, routes, preliminary decision | *this branch* | `76561445ebefdca3811353ddf0d1ed15d90a4a996c85baafda970008f869dc68` | 71,995 |
| 3/4 — reviewer corrections and seal | *this branch* | recorded in `DECISION.json` | 95,243 |

Round-1 verdicts were issued against the 71,995-byte package (`76561445…`), the bridge module
(`ecb0a03d…`), its 160-test suite and `/tmp/r1_design.py` — and against no other. Part I is a byte-exact
34,848-byte prefix of every later version.

## 2. Charters

- **Reviewer A — engine, measurement and provenance.** Verify every claimed channel against source;
  attack float/mask/morphology cross-binding, constant provenance, anchor fail-closed behaviour and the
  bridge threat model; detect any scientific interpretation of mechanical smoke data.
- **Reviewer B — route selection and statistics.** Attack fresh-law-frame independence; hunt hidden
  Stage-B tuning; recompute every power and MDE result; attack Route-E denominators and negative
  decisions; attack Route-G symmetry, equivalence, intervention and ownership claims; enforce the same
  deferral standard for E and G; challenge any selection of F.

Both worked independently and concurrently; neither saw the other's findings.

## 3. Round 1 — verdicts

| Reviewer | Verdict | Findings |
|---|---|---|
| A | **FAIL** | A1–A19 — 1 BLOCKER, 8 MAJOR, 10 MINOR |
| B | **FAIL** | B1–B26 — 6 BLOCKER, 11 MAJOR, 9 MINOR |

**45 findings. None judged invalid.** Nineteen withdrawals W1–W19 follow in report Part III §III.3;
every finding maps to one of them.

### 3.1 Blockers

| ID | Finding | Disposition |
|---|---|---|
| **B1** | The lattice transpose `T` is an **exact symmetry** of the engine update (no per-axis parameter exists anywhere in `LatticeBondSpec`; every face expression is identical for both axes). The axis-nematic bond order parameter `Q = mean(b[0]) − mean(b[1])` satisfies `Q∘T = −Q`. This falsifies the frozen Part I §5 `U` row and voids the Route-G rejection | **ACCEPTED** → W1, W2. Independently re-verified by the author: `max |T(stepᵏ(s)) − stepᵏ(T s)| = 5.6e-17`; `max |Q + Q∘T| = 2.2e-16`; entity-local `Q = −0.0978` on 11 axis-0 and 12 axis-1 internal faces |
| **A1 / B2** | The Route-E law frame is **not a probability distribution**: (B2) bounds only the product `ε̂_b·k̂_on`, and the resolvability principle was not applied to either factor; the region has infinite Lebesgue measure | **ACCEPTED** → W3. N2/N3/N4 `PASS` withdrawn |
| **B3** | `w = 0.10`'s justification is self-refuted by the report's own `L₂ = 36` (both arms expressible at `w = 0.1708`) | **ACCEPTED** → W4 |
| **B4** | `R = 6` rests on four undeclared effect sizes (`p = 0.9`, `p = 0.3`, `0.95`, `0.10`); relaxing 0.95 → 0.94 selects `R = 4` and `N = 832` | **ACCEPTED** → W5 |
| **B5** | `L₂ = 36` has no stated power; actual power at the primary's own MDEs is 0.333 and 0.347 | **ACCEPTED** → W6. N11 `PASS` withdrawn |
| **B6** | `H`, the lattice shape and the wall-clock ceiling are never given numeric values, so the "frozen" frame defers three outcome-determining constants — the asymmetric deferral Part I §8 forbids | **ACCEPTED** → W7 |

### 3.2 Major and minor findings

Accepted in full and mapped as follows. A2 → W19 (`backend` unbound in the root); A3, A4, B24 → W10
(three decorative constant justifications); A5 → W11 (the ungated `open_owned_analysis_access` remains
reachable); A6 → W12 ("no mutant survives" is false — the anchor-check ordering is unpinned); A7, B17 →
W13 (the residual series is selectively presented; the fixture runs `min_cells = 1` on a 0.449
background and never approaches E-2's 0.05); A8, B12 → W9 (IC-B contradicts itself by 2×); A9 → W14
(the track↔component join is never persisted); A10 → W19 (the gradient-flow identity fails on the
closed boundary `m = m_max`); A11 → W19 (MB-L8 mis-states its field list); A12 → W19 (a directory copy
replays); A13 → W19 (untyped `ValueError`/`ArithmeticError`, poisoned directory); A14 → W19 (unreachable
`mass == 0` arm carrying an unjustified convention); A15 → W19 (four root fields protected only by a
hash tripwire, which Part I §7 M-A8 refuses); A16, B19 → W15 (MDE grid artefacts: exact roots 0.6404
and 0.02984); A17, B20 → W19 (the resolvability inequality must be strict; `H > 4`); A18 → W19
(Part II contradicts Part I on `unique_score_margin`); A19a → W19 (the ledger header contradicts its own
conclusion); A19b → W19 (the bridge binds mass-weighted morphology, the tracker consumes binarised
morphology, and they differ); A19c → W19 (shared-environment control misclassified as a derived
channel); B7 → W19 (estimand/estimator conflation); B8 → W16 (`Δ₁`'s gloss is false under the design's
own attenuation: `p = 0.485` yields `Δ = 0.10`); B9 → W8 (`Δf = ⌊H/64⌋`'s 64 is unjustified and N9
cannot be rebutted); B10 → W19 (the resolvability principle applied selectively); B11 → W19
(uniform/log-uniform convention contradicted by the frame's own table, concentrating `κ̂` on fast
transport); B13 → W19 (E-3's doubling origin ambiguous; its censoring mode absent from the
discriminators); B14 → W19 (operating characteristics are attrition-free although N7 requires them
under attrition); B15 → W15 (the ineligibility floor is a bare 50% at the wrong unit); B16 → W19
(`cohort_residual_fraction` restates itself; its sensitivity set has no decision mapping); B18 → W15
(the indifference region is **twice**, not four times, the achieved full width); B21 → W19 (`validate`
is a predicate over the initial state, not parameters; a mid-run `ArithmeticError` is an undeclared
exit); B22 → W18 (the Route-G column is not binary); B23 → W17 (a fabricated cross-reference to a
Part I §8 `N-A` category that does not exist); B25 → W15 ("complete" replacement vs a 5% convention);
B26 → W19 (no affirmative Route-F analysis, so a stop cannot be adjudicated if E falls).

### 3.3 Findings judged invalid

**None.**

### 3.4 What the reviewers could not break

Reviewer A reproduced 646 tests, the node-ID digest `76c0da8d…`, and 441/130/100% coverage exactly;
confirmed Part I §3, §4 and §6 line by line against source; confirmed the `(0.1, 0.8]` interval is
exactly right at both endpoints and pinned by tests; confirmed the mask/float cross-binding is enforced
**semantically**, with the pipeline's detector reproducing the handed mask bit-for-bit; independently
re-derived the gradient-flow factorisation and confirmed it on the interior; and could not defeat the
anchor gate on any receipt-forgery variant — absent receipt, valid reference with wrong digest, correct
digest with bogus reference, forged digest with a permissive verifier, and a single mask byte flip all
refuse, the last with a semantic error and no digest involved. Reviewer B reproduced every statistic
through an independent Clopper–Pearson implementation, agreeing to 4.9e-13, and confirmed
`LatticeBondSpec.__post_init__` and `LatticeBondState.validate` are pure outcome-blind predicates.

## 4. Corrections applied

Nineteen withdrawals, W1–W19, in report Part III §III.3. Per Part I §11 each is a **withdrawal**, not a
rewording; the original text stands in Part II. No limitation was deleted in order to pass. Two
corrections run **against** the author's own position and in favour of the route the author rejected:
W1 and W2 restore Route G by falsifying a capability row the author froze.

The Route-E frame defect (W3) was **not repaired in-mission**, although the repair is obvious and
in-allowlist. Repairing a frozen frame under review pressure — fixing parameters after seeing the
objection — is the precise failure mode this programme was already destroyed by once. It is routed to
the successor with the repair named.

## 5. Governance record

- Part I was never modified; byte-exact prefix verified at checkpoints 1, 2 and 4.
- No accepted source or test was modified: exactly two files were added, and the sha256 of every
  pre-existing file was recomputed and matched.
- No gate was averaged, weighted, scored or traded. The §II.8 table is void under W2 and W18; the
  disposition rests on Part I §15, §10.6 and §10.4, each stated separately.
- No backup route was named: Part I §10.3 requires a backup to pass all fifteen gates independently.
- The author's preliminary decision (`PROSPECTIVE_ROUTE_SELECTED`, Route E) was **overturned by
  review**. That is recorded as the outcome, not softened.
- A required deviation from frozen Part I is declared, not glossed: §5's `U` row is false. Under
  Part I §15 that alone forces `MEASUREMENT_FEASIBILITY_REVISE`.
- Round 2 was not run. `MEASUREMENT_FEASIBILITY_REVISE` does not require reviewer `PASS` — Part I §10.6
  makes PASS/PASS a precondition of `PROSPECTIVE_ROUTE_SELECTED` only, and that is not claimed. A
  second round against a package whose central capability row is known false would test nothing.
