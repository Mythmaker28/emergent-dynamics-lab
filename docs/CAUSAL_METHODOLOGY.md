# Causal methodology — binding rules for every substrate from 2026-07-12 (D-036)

Derived from the failure exposed by EXP-RD-04 (D-035), where a dead candidate cleared a preregistered margin
because two nulls that *could not fire* were pooled with the one that could.

## R1 — Never pool qualitatively unequal null arms
Null arms differing in kind (what they hold fixed, what they destroy) are **reported separately, always**, with
their own denominators and Wilson intervals. A pooled "null floor" across unequal arms is forbidden: it is an
average over tests of different hypotheses and it mechanically dilutes the only floor that matters.

## R2 — A null that cannot produce the measured outcome is not a null
Before it is used, every null arm must be shown **capable of producing the outcome being measured**. A null whose
outcome is zero by construction (e.g. displacing a region that contains none of the substance the outcome requires)
is a **straw man**; it may be reported as a sanity control but it carries **no eliminative weight** and may never
enter a decision rule. This capability must be argued in the protocol *before* the run.

## R3 — The decisive null is the organization-destroying null
For any claim of the form "this organized structure did X", the decisive null is a cargo that holds fixed
**everything the outcome could trivially depend on** (support geometry, total material, per-species and per-cohort
mass, the multiset of local scalar values, the distribution of every field's magnitude, the destination, and the
perturbation magnitude) and destroys **only the internal organization** (coherent orientation, cross-field spatial
correlations, spatial arrangement). It is a **mandatory arm** of every causal intervention. No re-establishment
claim may be made without it. The primary statistic is the **paired** comparison intact-vs-scrambled.

## R4 — GATE-0 precedes every law search
A substrate is **rejected before any screening** unless, on a known-organized reference structure, **intact cargo
re-establishes where scrambled cargo does not**. Organization must be *load-bearing* in the substrate, or there is
nothing for an individual to be. Gray-Scott would have failed GATE-0 on day one; the closed Flow-Lenia core almost
certainly would too. Two substrates and several months of screening would have been saved.

## R5 — Interventions must be proven to change their intended variable
Every intervention arm carries **executable assertions** that it did what it claims: SHAM is an exact bitwise
no-op; the intact displacement actually moved the cargo and conserved mass; the scrambled arm provably matches every
declared invariant **and** provably destroyed the declared organization (coherence strictly reduced, cross-field
correlation strictly reduced). Assertions fail loudly. *An operation that cannot fail loudly will eventually fail
silently* — see the tracker no-op (D-032) and the PROJECT_STATE patch no-op (D-035 journal).

## R6 — Observer sensitivity is offline, at fixed physics
Observer perturbations re-observe a **stored trajectory** at a **fixed `t*`** with fixed branches. Any "observer"
knob that also moves enrollment or physics is not an observer knob (D-032).
