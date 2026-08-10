# NEXT_HANDOFF — GAUGE_INVARIANT_MODE_BASIS_00 (GIMB00)

Successor to FIXED_SUPPORT_CAUSAL_MODE_ARBITRATION_00 (FSCMA00).

    TOMMY_ACTION_REQUIRED      = false
    TOMMY_GIT_ACTION_REQUIRED  = false
    PARENT_PROGRAMME           = FSCMA00
    PARENT_LABEL               = H2_SECOND_MODE_CONFIRMED_HELD_OUT
    INHERITED_STOP_LABELS      = none

## What FSCMA00 settled, and what it broke

Settled:

* The parent WSFSCRP00 Q2 numbers are exactly correct. Certified in rational arithmetic.
* The environmental operator excites a mode that no carrier operator can reach. Preregistered,
  confirmed on outcome-unseen founders, near-orthogonal (≈85°), one-dimensional, dose-linear.
* The carrier repertoire's own internal dimension is at least two once the channel gauge is fixed.

Broken, and this is the load-bearing item for the successor:

* The endpoint's channel labels are **not gauge-fixed by construction**. The canonical
  sorted-site-id rule is deterministic but physically arbitrary, and in this panel it is
  confounded with history order and geometry class through seed parity.
* Every cross-founder statement in this line — including the parent's headline rank result — is
  therefore gauge-dependent unless a gauge is fixed first, and FSCMA00's own P3 showed that the
  obvious a-priori gauge (seed parity) is wrong for 1 founder in 6.

## The one thing GIMB00 should do

Replace the gauged endpoint with a **gauge-invariant** one, and re-derive the mode structure in it.

The natural candidates are already in hand and cost nothing to compute from stored rows:

1. `s = δ_A + δ_B` — invariant under channel exchange by construction.
2. `|d| = |δ_A − δ_B|` or `d ⊗ d` — equivariant made invariant.
3. The unordered-pair symmetric functions of `(δ_A, δ_B)` at each scored time.

    SUGGESTED_WORKDIR   = /home/claude/sweep/GIMB00
    SUGGESTED_BRANCH    = dev/gauge-invariant-mode-basis-00
    EXECUTION_MODE      = ONE_EXECUTOR_SEQUENTIAL

## Required first phase — zero engine starts

All of the following is computable from rows already stored in
`FSCMA00_LOCKED_RAW_CELL_SCORES.json`, `fscma_probe_raw.json` and the parent `wsfscrp_q01.json`:

* Re-run the rank analysis in each of the three invariant coordinates above and report whether the
  two-mode structure (operator axis, stratum axis) survives, collapses, or splits further.
* State explicitly whether the environmental mode remains separated in an invariant coordinate.
  If the separation is carried entirely by `s`, say so: that is a *smaller* claim than
  "a second mode", and it should be labelled `ENVIRONMENTAL_COMMON_MODE_ONLY`.
* Decide whether the parent's Q2 gate should be restated in the invariant coordinate. Do **not**
  rewrite the parent; append.

## Required second phase — the confound, not the mode

The panel's defect is that geometry class ≡ history order ≡ seed parity. Any successor that wants
a geometry claim must break it:

* Generate a fresh candidate queue in which geometry class and history order are **crossed**, not
  aliased — four cells, not two.
* Minimum: 4 ancestry clusters per cell.
* Until that exists, no statement of the form "NEAR founders respond differently from FAR
  founders" is licensed anywhere in this line, and the FSCMA00 second carrier mode must be
  described as a *founder-stratum* effect of unresolved origin, never as a geometry effect.

## Budget guidance

    MAX_PROBE_ENGINE_STARTS   = 0     # phase one is offline; this is not a suggestion
    MAX_LOCKED_ENGINE_STARTS  = 96    # phase two only, and only if phase one licenses it
    MAX_TOTAL                 = 96
    NEW_LAWSPEC / ENGINE_EQUATION_CHANGE / NEW_STATE_VARIABLE_OR_TRACER   = false
    FIXED_SUPPORT_READER_CHANGE                                          = false
    CONFIRMATORY_OR_POPULATION_CLAIM                                     = false
    PUSH_AUTHORIZED = false   DRAFT_PR_AUTHORIZED = false

Namespaces `62000–62009` remain reserved and unread. `64000–64011` are now fully outcome-exposed
and must not be reused for any held-out role.

## What a successor must not do

* Must not rewrite FSCMA00 or WSFSCRP00 outputs. Corrigenda and claim ledgers are append-only.
* Must not treat the FSCMA00 gauge as physics. It is a convention chosen to make cross-founder
  comparison possible, and its only justification is that two independent rules selected it.
* Must not report the environmental result as a life, agency, identity or memory claim. It is a
  statement about the dimension of a causal response set on a fixed dev panel, nothing more.
