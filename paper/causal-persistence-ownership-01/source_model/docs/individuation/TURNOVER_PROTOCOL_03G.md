# Authoritative turnover PRESEAL protocol 03G

Status: **implemented, not sealed, not human-authorized, not prospectively executed**.

This protocol supersedes 03C and 03E for any future turnover execution. Their history remains committed. No
`54001-54096` seed has been run by this repair.

## Question and claim boundary

Does passive-copy C1c preserve target-specific graded causal information through deep material turnover, and is
that information stored in the frozen target-local memory representation rather than recoverable from a nearest
neighbour, target-memory-excluded environment, target-memory-removed global summary, or body baseline?

The experiment does not test or claim identity, individual memory, reproduction, heredity, evolution, life, agency,
or active reconstruction.

## One executable chain

`seal -> authorization -> runner -> ledger -> raw records -> raw manifest -> analyzer -> gates -> A-F outcome -> certificate`

Every stage consumes an artifact produced by the preceding stage:

1. `turnover_runner_03g.py` parses and hashes the seal and execution manifest.
2. Every protected working file is checked against both its Git blob and SHA-256 before engine import.
3. The authorization binds the exact seal, manifest, runner, analyzer, environment, family, phrase, and canonical
   run directory.
4. `turnover_ledger_03g.py` atomically creates the sole canonical ledger and advances the frozen state machine.
5. `turnover_engine_03g.py` executes the actual C1c seed path.
6. Each raw world is validated and atomically published under `LCI-TURNOVER-RAW-03G-v1`.
7. The ledger records each raw hash and the feasibility-only reserve projection.
8. The family closes with a hash-bound raw manifest.
9. `turnover_analyzer_03g.py` accepts only a closed ledger and validated raw files.
10. The analyzer imports and evaluates `TURNOVER_DECISION_TREE_03G.json`, writes the machine certificate and human
    report, and the ledger advances through `ANALYZED` to `CERTIFIED`.

The prospective CLI has no user-specified seed list or run directory.

## Runtime seal and authorization

The future final seal must use schema `LCI-TURNOVER-SEAL-03G-v1`. It must bind:

- the exact execution-manifest Git blob and SHA-256;
- every manifest-protected file's Git blob and SHA-256, bound directly or by the canonical protected-map digest;
- the environment-lock SHA-256;
- the seed-family SHA-256.

The runner aborts before engine import or initialization if any field differs. The future human authorization must
bind the same values plus the runner and analyzer blobs, authorization ID, approver, UTC timestamp, canonical run
directory, and exact phrase:

`I AUTHORIZE ONE PROSPECTIVE EXECUTION OF LCI-CAUSAL-TURNOVER-PRESEAL-03G FINAL_SEAL_SHA256=<FINAL_SEAL_SHA256>`

No valid authorization or final seal exists in this repair.

## Honest one-execution threat model

The guarantee is one authorized execution in the declared canonical run directory. A second ordinary fresh
invocation is atomically refused; resume is explicit and requires the same complete binding. Completed seeds and
raw files cannot be overwritten or rerun.

An actor who copies and modifies an open-source repository cannot be technically prevented from running a fork.
Such a run has a different repository-instance record and an untrusted ledger and is not the sealed prospective
execution. The hash chain, anchor, raw hashes, and repository-instance evidence make ordinary replay or copied
execution detectable afterward; they are not a DRM claim.

## Ledger finite-state machine

`CREATED -> AUTHORIZED -> PRIMARY_RUNNING -> PRIMARY_CLOSED -> RESERVE_DECIDED ->`
`RESERVE_RUNNING (only if activated) -> FAMILY_CLOSED -> ANALYZED -> CERTIFIED`.

Seed start/resume/completion events may occur only in the corresponding running state. The ledger rejects skipped
or reversed states, reserve-before-primary, analysis-before-family-close, changed binding, invalid seed order,
post-certificate writes, duplicate completion, event reorder, retained-entry modification, and ledger truncation
relative to the atomic anchor.

A crash after seed start may resume the same deterministic seed. A crash after atomic raw publication but before
ledger completion revalidates and records the existing raw file without overwriting or rerunning it.

## Family and reserve

Primary `54001-54050`; reserve `54051-54096`; hard cap 96; minimum valid original worlds 18. Primary is always
completed first. Reserve activation and stopping use only:

`seed, eligible, deep_reached, rest_assay_valid, deep_assay_valid, valid, reason`.

No label, feature, effect, decoder, gate, or outcome field is available to activation. Reserve runs in ascending
order and stops at the first record reaching 18 valid worlds or at seed 54096.

## Raw schema and event evidence

Each world stores seed/world ID, eligibility/G0 fields, histories and target IDs, material tracer trajectory and
`M_i`, tracker/event evidence, L/N/P/E/Gm/Gf/B, rest/deep intervention batteries, lambda-plus-only controls,
censoring, snapshot time, and seal/code/environment bindings.

Fission, transient fragmentation, merge, loss, death, and ambiguity remain distinct persisted event classes.
Censored worlds never re-enter the valid family.

## Frozen access scopes

| scope | definition | dimensions | role |
|---|---|---:|---|
| L | exact target memory | 11 | primary |
| N | geometrically nearest-neighbour memory | 11 | exclusion control |
| P | L plus deterministically ordered neighbour memories | 33 | diagnostic |
| E | 8 fields x 3 annuli with target m1/m2 masked | 24 | exclusion control |
| Gm | global low-dimensional summary with target memory removed | 18 | exclusion control |
| Gf | exact concatenation `L || Gm` | 29 | diagnostic only |
| B | target body/environment baseline without memory label | 8 | exclusion control |

`Gf[0:11]` equals L byte-for-byte. Gf cannot be a comparator that L must outperform. E/Gm cannot exclude every
possible fine, non-radial, or high-frequency distributed encoding; Outcome F concerns only the frozen detectable
access classes.

## Frozen grouped inference and causal gate

- original world is the inferential unit;
- outer leave-one-original-world-out predictions;
- training-fold scaling only;
- ridge lambda = 1;
- duplicate-world content rejection;
- uncertainty over fixed original-world fold losses, with no bootstrap model refit;
- 1,000 within-world label permutations, seed 20260715, p < 0.05;
- G-LOCAL-EXCLUSION requires L lower held-out loss than N, E, Gm, and B, with paired world-level lower 95% bound > 0;
- G-CAUSAL requires own positive, own > sham, own > neighbour intervention, lambda-plus-only collapse with
  lambda-minus fixed at 0.15, fixed-mask directional consistency, and at least 18 valid worlds.

Primary support requires exactly:

`G_OWN_PERM AND G_LOCAL_EXCLUSION AND G_CAUSAL`.

A feeding effect alone cannot select Outcome A.

## Outcomes

The executable tree is `TURNOVER_DECISION_TREE_03G.json`. It selects exactly one:

- A: target-local own information and causal expression;
- B: causal effect without ownership;
- C: local stored trace without causal expression;
- D: both fail;
- E: feasibility failure;
- F: target-memory-excluded environmental/global access explains history.

Active reconstruction is never an observed result; B/D can only motivate separate future work.

## Platform

Authoritative prospective platform: CPython 3.12.10, Windows, AMD64, with the complete installable
`TURNOVER_ENVIRONMENT_LOCK_03G.txt`. Linux is not claimed as byte-identically reproduced by 03G.
