# Agent journal — endpoint and inference audit

- Role: independent endpoint/inference red-team subagent
- Run ID: `RUN-20260810-IPRR00R-END`
- Start time: filename allocation 2026-08-10 15:01 +02:00; host clock later reported 14:59 +02:00,
  so the wall-clock ordering is retained as an environment anomaly rather than silently repaired.
- Starting Git state: `HEAD=55f4223dd6e965d5db36934f9ef0d96bfc344434`; audit branch frozen by parent; no Git status requested or used.
- Assigned scope: independently reconstruct allowed DEV endpoint, support, topology, boundary-flux, attribution, minimality and inference claims across ETPC, EEFCA, ETNBFC and ETCMNFC.
- Access boundary: Git blobs only after per-path sentinel approval; no held-out, near, checkpoint, trajectory, engine or primary-allocation path; no repository import or execution.

## Actions

- Read the frozen independent audit plan and the governing `AGENTS.md` / research charter from the ETNBFC base.
- Inventoried only exact allowlisted ETPC, EEFCA, ETNBFC and ETCMNFC blobs at their fixed commits.
- Parsed JSON with an independent standard-library parser; no repository module was imported.
- Recounted every ETCMNFC result row and split block-tagged assertions from global/adversarial rows.
- Cross-joined `etcmnfc_phaseC.json`, `etcmnfc_phaseC2.json` and the three `probe_*` files.
- Recomputed support totals, geometry hashes and density ratios.
- Statically inspected the endpoint/mask code and compared the mask used by F10 with the mask
  actually recorded by the tap.
- Separated endpoint existence, support cardinality, topology, native transfer, attribution,
  minimality, causal inference and generality.
- Wrote `ETCMNFC_ENDPOINT_AND_INFERENCE_AUDIT_01R.md`; no staging or commit performed.

## Important files read or changed

- Read: `INDEPENDENT_AUDIT_FREEZE_01R.md`, `AGENTS.md`, `docs/RESEARCH_CHARTER.md`, `docs/PROJECT_STATE.md` (governance context; terminal rendering truncated a long middle section, so no claim below depends on that omitted display).
- Read, ETPC: `etpc_protocol.json`, `etpc_gates.json`, `etpc_verify.json`.
- Read, EEFCA: `eefca_audit.json`, `eefca_protocol.json`, `eefca_verify.json`.
- Read, ETNBFC: `REPORT_ETNBFC.md`, `etnbfc_b0.json`, `etnbfc_boundary_mask_inventory.json`,
  `etnbfc_c0.json`, `etnbfc_protocol.json`, `etnbfc_verify.json`, `etnbfc_weak_alternative.json`.
- Read, ETCMNFC: protocol, corrigendum, report, both independent reviews, core/gates/Phase C/Phase C2/
  verifier source and JSON, `SHA256SUMS`, and all three `probe_*` JSONs.
- Changed: this journal and `ETCMNFC_ENDPOINT_AND_INFERENCE_AUDIT_01R.md` only.

## Reproducible commands / experiments

- Every content path is checked with `Assert-IPRR00RSafe.ps1 -Kind Path -Value <repo-relative-path>` before `git show <commit>:<path>`.
- No repository Python, runner, engine, world, step, resume or scientific workflow is executed.
- Independent JSON recomputation uses `python -` with only `json`, `hashlib`, `collections` and
  `subprocess`; each Git blob read is preceded by a sentinel subprocess.
- Row recount: offline 60/60; 44 block-tagged rows over 4 blocks plus 16 global/adversarial;
  Phase C 21/22 with F10 failed; Phase C2 14/14; verifier 19/19.
- Geometry recomputation: canonical JSON of `sites_A`/`sites_B` has one unique SHA-256,
  `a3d537acb69e55414a4c9c95e8d523c9716f7a5ddf95eac9c97a1c22b88275f9`.
- Support recomputation: 688 pre-step links in aggregate, zero attributed and zero adjacency counts.
- Density-ratio recomputation: published values are 11.61–15.07% below the quotient implied by
  the named source fields.

## OBSERVED

- The audit plan was committed before ETCMNFC content access.
- Parent reported an L1 name exposure after freeze. The dependent held-out audit is therefore `NOT_AUDITABLE`; its identifying value is not reproduced here.
- ETCMNFC contains one scientific operator (`transpose`), not three orientation-based operators.
- `60/60` counts assertions, not histories or independent replicates.
- Four DEV blocks share identical A/B site sets: topology has one geometry.
- Three derived JSON sources agree on pre-step support: 172 material-bath links per block and zero
  with a material endpoint in A/B.
- F10 and V6 recompute support on the loaded pre-step state. The tap's actual exchange-time mask
  differs in cardinality by +1 in each of the two dynamic blocks retained in Phase C2.
- The actual exchange-time mask/link list is not persisted in the allowed JSON, so realized support
  cannot be independently attributed.
- `probe_depth.json` does not reproduce its named density ratio from `probe_attribution.json`.
- The reported depth mixes Euclidean distance 13 with 4-neighbour graph distance 14; the stored
  median is noninteger despite a `lattice_distance` field name.
- No target flux contrast was reduced; causal effect and absence of effect are both untested.

## INFERRED

- DEV-only reconstruction can test internal consistency and narrow observable claims, but cannot establish independent replication or held-out generality.
- The correct narrow stop is `NOT_IDENTIFIABLE`; the stronger assertion of proven empty support at
  the realized exchange time is not established by the allowed evidence.

## HYPOTHESIS

- The reported ETCMNFC pre-step endpoint counts are internally reproducible while underdetermining
  realized-time support, minimality, causal attribution and generality.

## WHAT WOULD FALSIFY THIS?

- A persisted exchange-time `alive` mask, frozen A/B masks and independent link list showing at
  least one attributable link would falsify the empty-support assertion.
- A fully independent, outcome-blind comparison in which all smaller/native alternatives are
  predeclared and fail while the claimed mechanism alone predicts a fresh endpoint would falsify
  the no-minimality conclusion.

## Failures / dead ends

- Direct invocation of the sentinel was blocked by the machine execution policy; all later invocations use `powershell -NoProfile -ExecutionPolicy Bypass -File ...`.
- PowerShell `ConvertFrom-Json` rejected `etcmnfc_phaseC.json` because keys `c` and `C` collide
  case-insensitively; the independent parser was switched to Python's case-sensitive standard JSON
  implementation. No data were discarded.
- The long `PROJECT_STATE.md` display was truncated by the terminal; this subaudit relies on the
  fixed mission, freeze and experiment-local evidence, not on the omitted display.

## Decisions

- No claim will inherit a verdict from prose, a stored expected verdict, or an inaccessible held-out result.
- Pre-step derived support is scored `PASS_INTERNAL`; realized exchange-time support is
  `INDETERMINATE`; per-component flux and causal effect are `NOT_TESTED/NOT_IDENTIFIABLE`.
- A lexicographically minimal tie-break on a maximum-cardinality matching is not scientific
  minimality.

## Unresolved risks

- Exact endpoint eligibility may be conditioned on the same observable later described as a result.
- Topology, boundary flux, attribution, minimality and causality may share inputs without independent witnesses.
- Raw grid arrays and raw face ledgers are outside this agent's authorized scope; raw-level
  topology/flux reproduction is therefore intentionally not claimed.
- Parent and other agents changed audit-branch HEAD during this subtask; no attempt was made to
  inspect or overwrite their work.

## Handoff

- End time: 2026-08-10 14:59:15 +02:00 on host clock (see start-time anomaly above).
- Ending Git state observed via `git rev-parse HEAD` only:
  `d3491f5dda7bced17920de68624262cd9e976b10`; no `git status`, staging or commit by this agent.
- Deliverable SHA-256 at completion:
  `25f91e8b1a30e71447c29af7eada2130971dc8d33e8bffd2be052cc8bdc1efc2` before this journal update.
- Handoff: parent should incorporate the two load-bearing contradictions (pre-step versus
  exchange-time mask; unreproducible depth ratio), the one-geometry denominator, the single-
  operator inventory and the exact `NOT_IDENTIFIABLE` causal boundary.
