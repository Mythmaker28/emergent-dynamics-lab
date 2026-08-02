# INTERVENTIONAL-INDIVIDUALITY-00 — Stage B report

## Disposition

**DEV_FEASIBILITY_FAIL**

The complete frozen DEV family contains no LawSpec region meeting the preregistered replication rule: at least two
of four `BOUNDED_ACTIVE_TURNOVER_CANDIDATE` worlds in each of the two neutral initial-condition classes. This is a
Stage-B feasibility result only. It is not evidence for or against individuality, autonomy, memory, ownership,
reproduction or life, and it does not authorize Stage C.

## Bound execution

- Accepted Stage-A parent: `b0dbab7674816ebdf3f3f911694b2744ca4bfc76`.
- B0 qualification commit: `93f4a42d8972d2d4b9f8da6f1dc3c8161dc3c045`.
- One-shot preflight authorization commit: `ecf3347ff5e3ceac1970ee4ca8ce186a70fdb337`.
- Final manifest SHA-256: `194e082f9d3809f2531912d825480fad5b683dbe9d9fceec8050260fe493dd50`.
- Excluding-field manifest seal: `5681f02b746dc024ea5e1c96d7e8ff83934d96493edf4e9a441e8222909ef3ae`.
- Family: full Cartesian grid over `kappa_m={0.03,0.08}`,
  `resource_diffusivity={0.04,0.12}`, and `k_on={0.15,0.45}`.
- Initial conditions: bounded hash soup and generic compact fluctuations, with no organism template.
- Enrollment: 8 laws × 2 IC classes × 4 original-world replicates = 64 worlds.
- Lattice/horizon: `12×12`, 160 updates, every-step sampling.
- Exactly one runner invocation was made. There was no retry, replacement, adaptive extension or threshold change.

All 64 shards ended `COMPLETE`. Every step retained byte-identical deterministic replay and the frozen scalar
reference criterion. The final-root verifier accepted all 64 shards. No numerical, manipulation, instrumentation or
tracking-invalid status occurred.

## Complete regime atlas summary

The machine-readable classification preserves the full nine-class atlas. Counts below are `soup / compact` for the
classes that occurred; every omitted class has count `0 / 0`.

| Law | Candidate | Persistent no turnover | Static shell/crystal | Dissolved | Empty/gas | Region passes |
|---|---:|---:|---:|---:|---:|---:|
| L000 | 1 / 0 | 1 / 3 | 2 / 0 | 0 / 1 | 0 / 0 | No |
| L001 | 1 / 0 | 3 / 4 | 0 / 0 | 0 / 0 | 0 / 0 | No |
| L002 | 0 / 0 | 3 / 2 | 1 / 0 | 0 / 0 | 0 / 2 | No |
| L003 | 0 / 0 | 4 / 4 | 0 / 0 | 0 / 0 | 0 / 0 | No |
| L004 | 1 / 0 | 0 / 1 | 2 / 1 | 1 / 2 | 0 / 0 | No |
| L005 | 2 / 1 | 2 / 1 | 0 / 1 | 0 / 1 | 0 / 0 | No |
| L006 | 2 / 1 | 0 / 1 | 1 / 0 | 1 / 2 | 0 / 0 | No |
| L007 | 2 / 0 | 0 / 1 | 2 / 1 | 0 / 2 | 0 / 0 | No |

Across all worlds: 30 `PERSISTENT_NO_TURNOVER`, 11 `STATIC_CRYSTAL_OR_SHELL`, 10 `DISSOLVED`, 2 `EMPTY_OR_GAS`,
and 11 individual `BOUNDED_ACTIVE_TURNOVER_CANDIDATE` classifications. There were no `PERCOLATED`,
`ACTIVE_UNBOUNDED`, `TURNOVER_WITHOUT_PERSISTENCE`, or `TRACKING_UNRESOLVED` worlds. The 11 isolated candidate
worlds cannot be promoted or subset-selected: no law reached the fixed two-of-four minimum in both IC classes.

## Independent raw-only reproduction

The independent reproducer imported only the Python standard library and NumPy. It consumed the committed
manifest, allowed shard identity/integrity fields and `physics.npz`; it did not read `online.json`, the production
classification, atlas, report, engine, instrumentation or runner source at runtime.

Two clean-process outputs and the production classification are byte-identical:

`7b7cf200fd6cc7ccfbd77b19de0ca1231df22c1d2d9ab5d7548828df7c3ed14e`

The final raw root contains 195 files and 549,527,367 bytes. Its root-manifest SHA-256 is
`07428729da7b7d60a3493d9ee1fb8ec31ab0d7b870b5d9fdb54095ededff63cf`. The raw-only reviewer verified 64 unique
physics hashes; its ordered shard-binding aggregate is
`298f86ee06182ad180e3110bc09bbe34d5c95e31bc9b0aa7a7e0a3e7a9e71927`.

## Failure-mode table

| Gate | Observed result | Consequence |
|---|---|---|
| B0 passivity/tracker/tracer qualification | 88 focused synthetic tests pass after durable independent parity tests | Measurement stack admitted for this family |
| Frozen source/environment/manifest bindings | Exact hashes, external digest and both loaders pass | One-shot execution admitted |
| Stage-A numerical and conservation invariants | 64/64 complete; no numerical-invalid shard | `MANIPULATION_OR_NUMERICAL_INVALID` not triggered |
| Instrumentation and tracking integrity | No invalid or unresolved world | `REVISE_INSTRUMENTATION` not triggered |
| Candidate-world occurrence | 11/64 worlds | Descriptive only; no world selection permitted |
| Candidate-region replication | 0/8 laws pass both IC-class minima | `DEV_FEASIBILITY_FAIL` compelled |

## Claim boundary and next action

Four replicates per law/IC are a fixed feasibility screen, not a reliable probability estimate. The negative region
gate must not be rescued by selecting the 11 surviving worlds, changing the writer, expanding the family, relaxing
thresholds or opening a causal intervention. Bond-field persistence remains ordinary substrate dynamics, not memory.

Exact next action: human review of this completed Stage-B package only. Stage C remains closed.
