# PAPER STRATEGY DECISION (LRCPS01 §2)

**DECISION = `COMPANION_PAPER`**

## Preconditions tested for a V3 extension

- `named_persistence_V1_V2_package_present` = `False`
- `named_persistence_V1_V2_paths_found` = `[]`
- `candidate_shares_estimand_with_an_existing_manuscript` = `False`
- `candidate_shares_source_data_with_an_existing_manuscript` = `False`

## Rule applied

A V3 extension requires (a) the named persistence V1/V2 manuscript package to be mechanically present in the repository, and (b) a demonstrated overlap of estimand or source data with it. Precondition (a) fails: no file in the repository, tracked or untracked, is that package. Extending a document that is not present cannot be done mechanically and would have to be done from memory, which this mission forbids. Precondition (b) also fails against the three manuscripts that ARE present: they estimate a scalar causal-response magnitude q on contaminated reference channels from synthetic hold-outs, and cite no OBFOR01/ORR01/OBTC02 archive. The two questions are disjoint. Therefore: companion paper.

## Manuscripts that are present in the repository

- `docs/paper/MANUSCRIPT.md` — "Set-Valued Causal Metrology under Drift and Reference Contamination" (1441 words, sha256 `2d2e0cae7d010b61…`)
  - estimand: scalar causal-response magnitude q read on contaminated reference channels
- `docs/consolidation/SET_IDENTIFICATION_MANUSCRIPT.md` — "SET-IDENTIFICATION MANUSCRIPT (repaired T6)" (513 words, sha256 `72ce3b8a91b14e40…`)
  - estimand: scalar causal-response magnitude q read on contaminated reference channels
- `docs/replication/THEOREM_MANUSCRIPT.md` — "CRD IDENTIFIABILITY — THEOREM MANUSCRIPT (independent treatment)" (584 words, sha256 `513f55b5835dcbcf…`)
  - estimand: scalar causal-response magnitude q read on contaminated reference channels

## Candidate estimand of this paper

the steady-state radial extent r80 of the X field around a source of fixed full-capacity strength, and its dependence on source mobility, in the frozen ORR01/LawSpec-v2 lattice

The two estimands are disjoint: one is a scalar causal-response magnitude read on
contaminated reference channels of a synthetic measurement model; the other is a spatial
extent of a lattice field around a source. No datum, no figure and no theorem is shared.

## Absent package

NAMED_PERSISTENCE_V1_V2_PACKAGE = NOT_PRESENT_IN_REPOSITORY. No comparison, overlap figure or continuity claim is made against it. Its absence is reported, not worked around.

## Consequences

1. The companion paper carries its own abstract, introduction, methods, results and discussion.
2. It cites the set-valued causal metrology manuscripts as prior work of the same laboratory, not as a parent.
3. No sentence, figure or table is inherited from them; §13 will audit this mechanically.
4. No claim of continuity with an absent V1/V2 package is made anywhere in the manuscript.
