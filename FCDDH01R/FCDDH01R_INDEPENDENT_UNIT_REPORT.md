# FCDDH01R — independent unit report

An independent reading of the FCDDH01R record, performed offline against committed Git objects and
prepared evidence only. **Zero engine starts. Zero decodes. Zero new data.**

## Mandate and separation

This unit did not run the simulator, did not add a row, did not open the hold-out, did not refit,
did not change a threshold, and performed no remote repository operation. Its verification path
imports only `json`, `os`, `sys` and `fractions` and reads only JSON evidence, so it **provably
cannot** import, construct or advance the simulation runner. Start and raw-advance ledgers were
hashed before and after: 2736 WAL records, 240 charged starts, 240 raw advance sequences, byte
identity preserved, totals unchanged.

One deterministic verification decode was authorised. **None was spent.** The committed evidence
already contains an independent production-vs-reference recomputation (96/96 rows on M₂², 96/96 on
gauge, 48/48 on TAU, at rel 1e-9 / abs 1e-30), and the gate ladder was re-derived instead by exact
rational arithmetic over the committed certified enclosures. A second decode for ceremony is
forbidden.

## What was checked, and what it showed

**Repository.** Every reported commit prefix resolves uniquely. The chain
`93f13f45 → e77ef550 → 1936efde → 7dd098ea → b52b1eae → 2b152a2a → fc1b41f8 → ffbda326` is linear
and merge-free (0 merge commits). The reported order
`b52b1eae → 2b152a2a → fc1b41f8 → ffbda326` is confirmed from the exact objects. `main` matches the
committed audit value exactly and does not contain the child subtree.

**Worktree against C7.** All 6307 paths of the C7 `FCDDH01R/` subtree are present on disk and
re-hash byte-identical to their committed blobs; 0 mismatches, 0 missing. An initial `git diff-index`
against a freshly `read-tree`-populated index reported everything modified — a stat-cache artefact of
an index with no stat information, not content drift. The direct blob re-hash is the controlling
evidence, and it is clean.

**Record state.** `SP` — C7 present with 19 prepared but uncommitted worktree items: the eight
analysis reports (each duplicated byte-identically under `_work/`), the pre-numerical access ledger,
and two stale phase locks. No prepared file overlaps any name created by this closure, so nothing is
ambiguous and nothing was overwritten.

**Gate ladder.** Ten of the twelve gates were independently re-derived from the committed exact
rationals and **agree with the committed ladder on every one**: D1 ✓, D2 ✓, D3 ✓, D4 ✗, D5 ✗, D6 ✓,
D7 ✓, D8 ✗, D9 ✓, D10 ✓. D0 is a structural anchor and D11 is an AST source audit; both are accepted
from their committed reports rather than re-derived numerically.

**D4.** `upper(‖X̄_D‖) = 5.695567518165154e-04` and `lower(A_X̄) = 2.924046708945949e-03`. The
certified intervals are disjoint and one-ulp tight (widths 2⁻²⁰⁰ and 731/2⁻¹⁹⁸ respectively), so the
verdict is a **certified strict failure**, not UNRESOLVED, and no rounding of point values can change
it.

**D5 and D8.** Both fail on materiality, not on sign. Across all 48 full-axis pairs: 0 sign
reversals, 48 material-margin failures. D8's sign clause passes 12/12; its material clause passes
0/12. `Σ_b J[b; v_D[−b]] = 0` against a predeclared 10/12.

**Not three results.** D4, D5 and D8 all consume the same inherited TAU-propagated bounds. Reporting
them as three independent negatives would triple-count one fact.

## Two corrections this unit records

1. **`min alignment²` is `0.9992776839495647`, which is not `≥ 0.999278`.** It is below that
   six-decimal figure by 3.16e-07. The certified statement is `≥ 0.999277`. Rounding a value to six
   decimals and then asserting `≥` against the rounded figure overstates it. No gate depends on this
   — D6's threshold is 0.80 — but the record should not carry an unsupported inequality.

2. **`FCDDH01R_DEPENDENCY_FIREWALL_REPORT.md` is stale for four engineering modules.** Committed at
   C3 and never re-issued, it still lists the generation-1 digests of `DURABLE_PHASE_SUPERVISOR.py`,
   `EXACT_ONCE_PHASE_STATE_MACHINE.py`, `fr_dex.py` and `fr_dummy.py`. Its sixteen scientific module
   hashes remain byte-correct at C7. The C3 file is not edited; corrected values are recorded
   append-only.

## The one parent value that does not verify

`REPORTED_ORIGINAL_FCDDH00_AUTHORIZATION_SHA256 = f4312234…` against
`COMMITTED_ORIGINAL_FCDDH00_AUTHORIZATION_SHA256 = 9dcdd47a…`. Twenty-two declared serializations of
the committed verbatim text reproduce neither digest. The committed FCDDH00 binding already records
that the stored text is the handoff message *as received by the executor*, line-join artefacts
included: characters were lost in delivery, so the two digests cannot be made to agree.

This unit's judgment: the discrepancy is real, it is correctly **not adopted and not claimed
verified**, identity is properly established by content, it touches no normative hash, formula, gate,
code lock, seed role, budget or claim, and it **did not require the programme to stop**. Every other
reported parent value verifies, including 1392/1392 execution-tree paths byte-identical. The final
report must not compress this into "all parent values matched."

## Protocol conformity — this unit's independent judgment

The record is **NONCONFORMANT**, and this unit reaches that conclusion on a slightly stronger footing
than the handoff anticipated.

The handoff allowed that strict stop 5 might be judged inapplicable because DEX0–DEX16 remained
PASS. Reading the committed master freeze §7 directly, that hedge is unnecessary: stop 5's wording is
*"DEX or Q0A–Q0W failed, skipped, vacuous **or repaired after the first billed start**"*. DEX12's and
DEX4's assertions were replaced and DEX17–DEX19 were added at C5, after 48 billed starts. Stop 5 is
triggered on repair, independently of pass status. Stop 11 is triggered directly: frozen source under
the §6 durable-execution gate changed post-start.

**192 sham and active starts followed.** That is not repairable after the fact.

Set against this, the mechanical finding is equally firm: the C4→C5 diff touches **zero** scientific
paths. The four modified modules are the supervisor, the state machine, the DEX driver and the DEX
dummy; the rest is evidence and documentation. `run_id` does not depend on the executor code hash, so
no charged row changed identity and no completed phase could be re-entered under a new one. The
panel, the schedules, the ledgers, the locks, the randomization seed and every analyzer are
byte-identical across the change.

The honest position is the narrow one: **a deterministic descriptive calculation from a
non-conformant campaign.** Neither half of that sentence may be dropped.

## On the generation-1 publication defect

Mechanically, the construction phase is clean: 48 rows, 48 gates, 48 advances, 96 seals, 96
publications, 0 recoveries, 0 skips, 0 duplicates. The 48 monotonicity alerts are a reporter
artefact, correctly diagnosed.

The defect underneath is nonetheless real: a row killed between its first output's `VERIFIED` and its
second output's publication would have been treated as complete on resume. That window did not open.
The correct description is **a latent recovery weakness without observed raw corruption** — and this
unit notes that the reason it was missed is itself the more valuable finding: every DEX row declared
exactly one output, so the harness was blind to row *arity*, and the real phases are the only place
arity is 2. A durability harness must exercise the *shape* of the real row, not only its failure
modes.

## What zero hold-out starts means

It is the correct outcome, not a shortfall. The predeclared stop is that no hold-out opens without a
licensed axis; D4, D5 and D8 failed, so no axis was licensed. Opening the hold-out anyway would have
consumed sixteen irreplaceable fresh ancestries to validate a direction that had already failed its
own discovery gates. The 432 unused starts are closed and non-transferable, and that is the
protocol working.

## Residual limitations this unit will not paper over

* The fold-axis four-pair breakdown was computed but not persisted; only the fold summary survives.
  Recovering it needs a decode, which is out of scope.
* `FCDDH01R_RANDOMIZATION_LICENSE` was never rebuilt at closure as §5 requires. Nothing depends on
  it here, but the field is genuinely absent rather than passing.
* The handoff document itself is absent from the workspace; its declared SHA-256 could not be
  checked and is not claimed verified.
* The prior execution environment is `NOT_OBSERVED` and no claim is made about it.

## Disposition

```
DISCOVERY_ANALYSIS_COMPUTED__AXIS_NOT_LICENSED_D4_D5_D8__ZERO_HOLDOUT_STARTS__PROTOCOL_NONCONFORMANT_POSTSTART_EXECUTOR_REPAIR
```

Independent unit verdict: **the numbers are right, the record is honest about why they do not
license anything, and the campaign should have stopped after construction.**
