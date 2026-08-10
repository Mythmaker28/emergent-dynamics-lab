# PROJECT EVIDENCE AND CLAIM LEDGER 01R

## Evidence graph

```text
3f8dae8 ETPC
  protocol+code+recorded primary summaries -> public-disc-c claims
        |
        v
de1524b EEFCA (audit only)
  ETPC code+summaries -> non-involution, endpoint substitution, sign non-derivability
        |
        v
d86d248 ETNBFC
  four DEV state packages -> exact-rho matching stop, ON ledger, missing native OFF ledger
        |
        v
c5171b7 ETCMNFC
  same four DEV packages -> raw-byte operator ledger -> first-pass/replacement oracle ledgers
                         -> pre-step topology/attribution/depth summaries -> NOT_IDENTIFIABLE report
```

All four edges are direct-parent ancestry. In every family, the protocol, executable, result JSON and report first
appear together in the result commit. Their internal hash seals verify bytes, but Git does not independently prove a
pre-result temporal freeze. None of the four commits is present on the public remote by branch, tag, release, PR,
exact-SHA search or ancestry of public `main`.

## Vocabulary

Every claim below receives exactly one mission-defined evidence level:

- `VERIFIED_FROM_RAW_ARTIFACT`
- `VERIFIED_FROM_CODE_AND_HASH`
- `REPRODUCED_OFFLINE_WITHOUT_ENGINE`
- `REPORTED_ONLY`
- `NOT_AUDITABLE`
- `CONTRADICTED`

`VERIFIED_FROM_CODE_AND_HASH` means the committed code/JSON/hash relationship was checked; it does **not** mean raw
scientific arrays were independently replayed. `REPORTED_ONLY` is not a polite synonym for PASS.

## Access and provenance

| ID | Claim | Evidence level | Audit disposition |
|---|---|---|---|
| A01 | IPRR00 supplied a reusable scientific verdict | `CONTRADICTED` | The prior attempt is invalid/incomplete by mandate; its reported stop commit is absent from the current local object store. No score or verdict was inherited. |
| A02 | ETPC → EEFCA → ETNBFC → ETCMNFC is the local direct-parent chain | `VERIFIED_FROM_CODE_AND_HASH` | Direct ancestry and one-commit intervals reproduced. |
| A03 | The chain is publicly available on GitHub | `CONTRADICTED` | Structured GitHub and remote-ref audits found none of its commits/refs/tags/releases/PRs on public `main`. |
| A04 | The final package's protocol hashes match their committed protocol bytes | `VERIFIED_FROM_CODE_AND_HASH` | ETCMNFC protocol seal matches; its 18-entry `SHA256SUMS` has zero mismatches but does not cover itself. |
| A05 | ETCMNFC was temporally preregistered in independently verifiable Git history | `REPORTED_ONLY` | Protocol, code, reviews, raw-summary JSON and report are all added in the same final commit. A self-seal cannot prove when it existed. |
| A06 | This reviewer retained blind integrity for the named held-out allocation | `NOT_AUDITABLE` | L1 exposure in commit/protocol metadata. No L2/L3 held-out content evidence was opened. This consequence is local to the dependent held-out audit. |
| A07 | No engine, trajectory or primary-allocation attempt occurred in IPRR00R | `VERIFIED_FROM_CODE_AND_HASH` | Audit commands, sentinel probes and journals show zero such attempt. |

## ETPC

| ID | Claim | Evidence level | Audit disposition |
|---|---|---|---|
| T01 | Exact-twin/checkpoint infrastructure was exercised as recorded | `VERIFIED_FROM_CODE_AND_HASH` | Code, gates, hashes and descendant audits agree; no independent raw replay was permitted here. |
| T02 | The recorded early statistic is realized material–bath flux of c and N | `CONTRADICTED` | `etpc_analyse.py` sums a component-oriented disc statistic of `c`; it contains no face transfer and does not read N. |
| T03 | The ETPC operator satisfied the authorized involution requirement | `CONTRADICTED` | Source applies an additive affine mean transfer; applying it twice is not identity for the observed unequal masses. A gate named involution was passed with literal `True`. |
| T04 | ETPC's disc-c arithmetic/result values are a confirmatory causal result | `CONTRADICTED` | Arithmetic may be internally exact, but both the authorized operator and endpoint were substituted. The blocks are development-only. |
| T05 | A delayed public response was established | `REPORTED_ONLY` | The package itself records `NOT_ESTABLISHED`; no independent result replay was done. |
| T06 | One-sided direction followed from local kappa monotonicity through the disc reader | `CONTRADICTED` | A local derivative does not fix the sign of a spatially aggregated field statistic across a sign-changing Laplacian. |

## EEFCA

| ID | Claim | Evidence level | Audit disposition |
|---|---|---|---|
| E01 | The executed ETPC map is non-involutive | `REPRODUCED_OFFLINE_WITHOUT_ENGINE` | Re-derived from the 2×2 mean map and source; inverse-of-map is not self-inverse. |
| E02 | A mass-weighted conservative involution exists algebraically | `REPRODUCED_OFFLINE_WITHOUT_ENGINE` | The matrix theorem is correct. EEFCA did not establish full-state/domain admissibility of that proposed mean map; it was an algebraic existence result only. |
| E03 | ETPC substituted its endpoint | `VERIFIED_FROM_CODE_AND_HASH` | Direct source inspection confirms disc mean of c rather than native face flux of c and N. |
| E04 | Exact endpoint laterality is derivable | `CONTRADICTED` | Only the first local derivative rung has a fixed sign; the aggregated endpoint lacks a sign theorem. |
| E05 | The opposite-sign mechanism was explained | `REPORTED_ONLY` | No retained spatial fields permit the proposed body/shell decomposition; the explanation remains a hypothesis. |

## ETNBFC

| ID | Claim | Evidence level | Audit disposition |
|---|---|---|---|
| N01 | Exact-rho matching support is zero on the four reported DEV blocks | `REPORTED_ONLY` | Report/JSON/code agree, but the frozen sentinel denied the DEV state-package paths, so no raw recomputation occurred. |
| N02 | Zero exact-rho support proves no conservative byte involution exists | `CONTRADICTED` | Raw-byte transposition with uniform storage weights supplies a counterexample; the parent false dilemma is withdrawn. |
| N03 | The ON native face ledger reproduces its recorded return | `VERIFIED_FROM_CODE_AND_HASH` | Source and committed verifier paths support it; independent raw execution was out of scope. |
| N04 | A native OFF face-event ledger exists at gain zero | `CONTRADICTED` | The reported native branch uses a fused Laplacian and does not materialize individual face events. |
| N05 | Native c/N targets were tested | `CONTRADICTED` | ETNBFC stopped before target contrasts; its correct disposition is `NOT_TESTED`. |

## ETCMNFC operator and oracles

| ID | Claim | Evidence level | Audit disposition |
|---|---|---|---|
| C01 | Disjoint equal-length raw-byte 2-cycles are an exact involution and preserve the raw multiset/plain dyadic sum under uniform weights | `REPRODUCED_OFFLINE_WITHOUT_ENGINE` | Follows directly from out-of-place transposition; independent static tests and brute-force matching audit support the implementation. It is not z transplantation or material motion. |
| C02 | Equal rho is necessary for that byte involution/conservation | `CONTRADICTED` | Equal storage weight is sufficient; rho enters domain admissibility, not the transposition theorem. |
| C03 | `frozen_matching` returns the lexicographically smallest maximum matching deterministically | `REPRODUCED_OFFLINE_WITHOUT_ENGINE` | Independent brute-force comparison passed 19,266 exhaustive unique-ID cases. |
| C04 | The generic transpose guard rejects every malformed pair list | `CONTRADICTED` | Duplicate sites are rejected, but unequal I/J lengths are silently truncated by `zip`, leaving an unmatched extra entry. |
| C05 | The committed ledger contains exactly 60 PASS rows | `VERIFIED_FROM_CODE_AND_HASH` | Independently parsed: 60 rows, 60 stored booleans, gate counts reconciled, manifest hashes recomputed. |
| C06 | “60/60” autonomously proves operator qualification | `CONTRADICTED` | The total mixes redundant unit checks, four identical-geometry rows and misnamed/vacuous gates. Raw DEV arrays were not independently opened. |
| C07 | Four real-block manifests each contain the reported full-support disjoint pairs, unequal rho and reciprocal exact shifts | `REPORTED_ONLY` | JSON manifests are internally consistent and hash-correct; the underlying DEV arrays were inaccessible by the frozen sentinel. Geometry and pair layout are identical across all four. |
| C08 | Three separately defined orientation operators were evaluated | `CONTRADICTED` | Allowed protocol/core/gates expose one operator: transposition of `Mf[0]` over one frozen matching. The pre-freeze audit hypothesis that there were three was erroneous and is withdrawn. |
| C09 | First-pass F2/F5/F6 tested their named properties | `CONTRADICTED` | F2 compared an object to itself; F5 recomputed the same expression; F6 tested permutation invariance of sum under `roll`. All can pass without the named engine property. |
| C10 | Every replacement oracle can reject all structurally relevant corruptions | `CONTRADICTED` | Replacement F2 is not biconditional and accepts distinct corrupted masks; F5 accepts duplicate/extra/unrecognized ledger rows; phase-C2 O1 reruns identical copies. Negative controls prove only the one corruption they contain. |
| C11 | The per-block “identity hook is bit-identical to no hook” gate exercises an engine hook | `CONTRADICTED` | It hashes `transpose(..., identity=True)`, an unconditional copy/no-op; the named integration property is not exercised. |
| C12 | `etcmnfc_verify.py` independently verifies protocol, sums and negative controls | `CONTRADICTED` | It never reads `SHA256SUMS` or the protocol, loads the offline ledger without using it, trusts stored truthy PASS values, and has weak filename/substring scope checks. |
| C13 | Operator passivity/complete-state identity on actual DEV states is independently reproduced here | `NOT_AUDITABLE` | The source path is plausible and recorded results say PASS, but raw state packages were excluded by the frozen sentinel. |

## ETCMNFC endpoint/topology

| ID | Claim | Evidence level | Audit disposition |
|---|---|---|---|
| P01 | The committed **pre-step** topology summaries show one connected native-material region containing A and B | `VERIFIED_FROM_CODE_AND_HASH` | Four JSON rows agree; A/B site sets and topology are identical, so effective geometry n=1. |
| P02 | The committed **pre-step** support summary has no material–bath face incident to frozen A/B | `VERIFIED_FROM_CODE_AND_HASH` | Topology/attribution/phase-C JSON agree internally: nonempty body boundary, zero A/B incidence. |
| P03 | F10 evaluates the actual exchange-time mask used by the native tap | `CONTRADICTED` | F10 and the verifier reload the checkpoint and use `st.rho > eps`. The tap records a returned/exchange-time mask with one additional alive cell in each retained dynamic DEV summary. |
| P04 | Native A/B-to-bath support is empty at the **actual exchange** | `NOT_AUDITABLE` | The actual masks/attribution arrays are not retained in allowed JSON. Empty pre-step support makes the claim plausible, not proved. |
| P05 | Per-component attribution of the connected body's exterior is natively identifiable | `CONTRADICTED` | A and B are internal masks in one connected native body; partitioning the exterior between them requires a nonnative rule. |
| P06 | Global connected-body boundary flux is structurally observable by the ON tap | `VERIFIED_FROM_CODE_AND_HASH` | Native face transfers exist as a global ledger. It was not the authorized component endpoint and was not executed as a target. |
| P07 | One-step global reachability is structurally unreachable | `REPORTED_ONLY` | Review prose reports a positive separation/locality bound, but the actual mask and raw spatial witness needed for independent re-derivation were not retained in the allowed set. |
| P08 | The published `component minimum / boundary median` ratios recompute from committed numerator/median | `CONTRADICTED` | All four divisions disagree by 11.6%–15.1%; no committed generator or alternate denominator is supplied. |
| P09 | The joint per-component c/N endpoint is fit for primary execution | `CONTRADICTED` | Pre-step support is empty, exchange-time support is unverified, and outer-boundary ownership is nonnative. `STOP_REASON = JOINT_ENDPOINT_STRUCTURALLY_MISSPECIFIED`. |
| P10 | ETCMNFC tested a primary c/N effect | `CONTRADICTED` | No primary target was executed. Correct value: `ETCMNFC_PRIMARY_C_N = NOT_TESTED`. |

Required endpoint classifications:

```text
NATIVE_COMPONENT_BATH_SUPPORT             = EMPTY_PRE_STEP; NOT_AUDITABLE_AT_EXCHANGE
PER_COMPONENT_OUTER_BOUNDARY_ATTRIBUTION  = NOT_IDENTIFIABLE
GLOBAL_BODY_BATH_FLUX                     = IDENTIFIABLE_AS_GLOBAL_LEDGER; NOT_A_PRIMARY_RESULT
ONE_STEP_GLOBAL_REACHABILITY              = UNRESOLVED_IN_IPRR00R
ETCMNFC_PRIMARY_C_N                       = NOT_TESTED
STOP_REASON                               = JOINT_ENDPOINT_STRUCTURALLY_MISSPECIFIED
```

## Inference

| ID | Claim | Evidence level | Audit disposition |
|---|---|---|---|
| I01 | With deterministic potential responses, allocation sign cancels from the observed D statistic | `REPRODUCED_OFFLINE_WITHOUT_ENGINE` | Substitution into the frozen formula gives `D_b = 0.5 Σ_k s0_bk τ_bk`. |
| I02 | The Fisher enumeration is invalid mathematics | `CONTRADICTED` | It is an exact sharp-null sign-flip test when framed correctly. |
| I03 | The Fisher p-value adds graded magnitude evidence here | `CONTRADICTED` | With n=10 it is essentially a concordance/sign count and is blind to magnitude; minimum two-sided p is 2/1024. |
| I04 | The inverted constant-shift interval is an exact confidence interval for a heterogeneous mean effect | `CONTRADICTED` | It is a compatibility interval under a constant additive-effect model only. |
| I05 | `eta_X` is an observer-error bound | `CONTRADICTED` | A bit-exact observer has no estimated observation error; `eta_X` is a materiality threshold. |
| I06 | The co-primary c/N rule supplies independent confirmation | `CONTRADICTED` | It is a valid intersection-union decision rule, but both outcomes share kappa and are reported strongly anti-correlated; independence is not established. |
| I07 | The allocation bit's evidenced role is blinding | `VERIFIED_FROM_CODE_AND_HASH` | That is its defensible role; no primary allocation/result exists on which to claim randomization-based generalization. |

## What survives

The strongest surviving result is methodological, not causal: a simple equal-weight byte transposition can implement
an exact carrier-array involution, while several named PASS gates and the endpoint time alignment do not establish
what their labels claim. The correct scientific disposition remains **stop before primary; c/N effect not tested**.
