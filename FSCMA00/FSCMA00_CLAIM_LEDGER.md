# FSCMA00 -- claim ledger (append-only)

| # | claim | status | evidence |
|---|---|---|---|
| 1 | The WSFSCRP00 payload archive and all 49 SHA256SUMS entries verify from bytes. | ESTABLISHED | recomputed in-session |
| 2 | The parent's `state_feats` bug provably could not alter Q2, Q0 or Q1. | ESTABLISHED | positional argument: Q2 printed at line 30, crash site line 90, Q0/Q1 in a different file |
| 3 | The parent's Q2 numbers are exactly correct: sigma2/sigma1 = 0.11962171538728941..., sigma2^2/sum = 0.01397555789051734... | ESTABLISHED (exact, certificate-bearing) | independent verifier, Sylvester inertia in exact rational arithmetic; parent float64 correct to ~3e-16 relative |
| 4 | The frac gate fails by a factor 3.578, decided by a single exact inertia count (1 eigenvalue at or above trace/20; 2 required). | ESTABLISHED | no approximation in the decision path |
| 5 | The fixed t0 index masks are correctly called EULERIAN, but not Lagrangian. | ESTABLISHED | AST audit of both engine modules: 27 np.roll calls, all literal unit shifts; zero permuting calls; zero spatial re-indexing; zero rebinds |
| 6 | `rho` depends on `N` within one step and on `Mf` only from the second step. | ESTABLISHED | def-use reachability over the AST; absence in the matrix is a proof of unreachability |
| 7 | The intervention repertoire spans two disjoint native input blocks, {Mf} and {N}. | ESTABLISHED | bytewise touch sets on 6 founders x 6 operators, plus the budget argument |
| 8 | WSFSCRP00 recorded `domain_ok = false` in 6 of 12 TRAIN cells and did not act on it; the failure is C2 on 31-67 dead sites, repaired by the engine within one step. | ESTABLISHED, recorded against the parent | exact off-gate content measured per cell |
| 9 | Geometry class, history order and canonical channel label are one confounded axis in this panel. | ESTABLISHED | `make_founder` seed parity x frozen queue parity, verified in source and in the data |
| 10 | `RANK_ONE_FIXED_SUPPORT_RESPONSE` is an artefact of the ungauged channel label. Gauged, sigma2/sigma1 = 0.3424 and lambda2/trace = 0.1035, so the parent's failing gate passes. | ESTABLISHED | two independent gauge rules agree; certified exactly against the runner-up |
| 11 | H1 (one affine 1-D family) is refuted on the carrier repertoire alone, before any environmental data. | ESTABLISHED | BASIS tube gate fails: O_BASIS = 0.1169 > 0.05, all 12 cells above 0.10 |
| 12 | The environmental operator adds a mode the carrier repertoire cannot reach, confirmed on outcome-unseen founders. | ESTABLISHED (developmental) | P1 and P2 both preregistered and both confirmed; LOCKED OFF = 0.9987 at k=1; common-mode separation x7.3 |
| 13 | The environmental mode is one-dimensional and near-linear in dose. | ESTABLISHED | cosine 0.9996 between +0.50 and +0.25; norm ratio 1.9218 |
| 14 | The mode structure is learnable and transfers: BASIS-fitted per-operator means beat the operator-agnostic baseline in every LOCKED cell. | ESTABLISHED | median L1 ratio 0.0276 |
| 15 | P3 (LOCKED orientation follows seed parity) is REFUTED, 5 of 6. | REFUTED, recorded | founder 64007, cosine -0.9162 |
| 16 | Founder-level fine structure within the environmental arm does not transfer from one BASIS-fitted deviation direction. | ESTABLISHED, limiting | J_ENV at k=1 = 0.9548 |
| 17 | No population or confirmatory claim is made. | BY CONSTRUCTION | `CONFIRMATORY_OR_POPULATION_CLAIM = false`; 12 founders, one substrate, one LawSpec |

## Withdrawn or superseded in this programme

Nothing produced by a parent programme is rewritten. Claim 10 **supersedes the interpretation**
attached to the parent's `RANK_ONE_FIXED_SUPPORT_RESPONSE` label while leaving the parent's numbers
standing exactly as reported -- they are correct, and this programme certifies them.

## Self-defects declared

1. My first orientation objective (minimum absolute weighted residual) can be gamed by collapsing
   the spread rather than making it one-dimensional. I noticed this before using it, checked it
   against an independent hypothesis-free rule, and reported that the two agree. Had they
   disagreed, the enumeration result would have been unusable.
2. My LOCKED seal cost 6 more engine starts than budgeted because stage A did not persist its sham
   forks. Within cap, disclosed above.
3. One PROBE engine start was consumed and discarded by a crash in a diagnostic line before the arm
   was scored. Pre-outcome infrastructure retry 1 of 6.
