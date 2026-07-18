# INTERVENTIONAL-INDIVIDUALITY-00 Stage-B raw-only developmental autopsy — pre-raw adversarial review

- Role: independent adversarial reviewer
- Run ID: `RUN-20260719-0100-II00-B-AUTOPSY-REDTEAM`
- Start: 2026-07-19 01:00:00 +02:00
- End: in progress
- Branch: `codex/interventional-individuality-00-stage-b-autopsy`
- Starting HEAD: `c31bf27ea80a6a3dcc60d0ec5380f668358671ff`
- Starting Git state: new plan, allowlist and journal directory untracked; no autopsy result root present in the inspected status
- Assigned scope: attack the pre-raw analysis plan, source firewall, estimands, event definitions, reconstruction, observational mechanism/actionability logic, censoring and outcome precedence; edit only this journal
- Immutable scientific disposition: `DEV_FEASIBILITY_FAIL`
- Prohibited in this review: opening any `physics.npz`, detailed trajectory, `online.json`, shard manifest, Stage-B report, engine, instrumentation, runner, scientific analyzer, checkpoint or world

## Exact source firewall used

I read `AGENTS.md` and then only the five explicitly authorized files below. The narrower assignment-specific firewall superseded the operating contract's normal request to traverse other durable scientific records.

| Input | SHA-256 at review | Bytes |
|---|---|---:|
| `docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B_AUTOPSY_ANALYSIS_PLAN.json` | `a507ee9b0a3724cb9ddbd76a206256354b09bd2cf8ab4f9e26f370661664de0a` | 15,136 |
| `docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B_AUTOPSY_SOURCE_ALLOWLIST.json` | `cbe9cf46e7bf2da4c91682013bb1f11544377389626d2a9103b4ae662a4b8a20` | 9,408 |
| `docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B1_MANIFEST.json` | `194e082f9d3809f2531912d825480fad5b683dbe9d9fceec8050260fe493dd50` | 6,851 |
| `results/INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-DEV/root_manifest.json` | `07428729da7b7d60a3493d9ee1fb8ec31ab0d7b870b5d9fdb54095ededff63cf` | 11,506 |
| `docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B_CLASSIFICATION.json` | `7b7cf200fd6cc7ccfbd77b19de0ca1231df22c1d2d9ab5d7548828df7c3ed14e` | 15,436 |

The allowlist names 64 unique physics paths in exact manifest world order. I verified only the strings. I did not stat, hash, list, open or load any named physics file.

## OBSERVED

- The plan preserves `DEV_FEASIBILITY_FAIL`, keeps all 64 original worlds, declares the candidate subset non-populational, prohibits Stage C and freezes many useful descriptive fields before raw inspection.
- The root manifest binds only each shard manifest's SHA-256/bytes/status/world ID. It does not directly expose a `physics.npz` hash, byte count or array inventory.
- The plan and allowlist list physics paths and a count, but no per-physics digest or accepted-parent Git-blob identity.
- Two of the eleven committed candidate worlds have multiple candidate track IDs: `L006__soup__r02` has `[0,1,2]` and `L007__soup__r02` has `[3,6]`.
- `frozen_manifest_values.sampled_detector_frames` is `[0,159]`, while the trajectory definitions require every detector frame from 0 through 159.
- Several output fields have no semantic definition: `candidate_episode_terminal`, `terminal_state`, `formation_opportunity`, `maintenance_opportunity` and the track-to-world `primary_developmental_pathway` aggregation.

## Binding findings and exact plan-only corrections

### 1. BLOCKER — the physics inputs are not cryptographically addressable under the declared firewall

The plan cannot prove that any opened NPZ is the Stage-B shard bound by the root manifest. The root binds a forbidden shard manifest; the shard manifest is the missing link that binds `physics.npz`. A path list and accepted-parent string do not make the runtime bytes self-authenticating.

Required correction before raw:

- bind an ordered 64-row physics inventory with exact `world_id`, repo-relative path, byte count and expected content identity;
- obtain the identity without scientific inspection either by predeclaring the exact Git blob object at accepted parent `c31bf27...` and requiring `git hash-object`/tree equality before NPZ loading, or by a narrowly authorized metadata-only extraction of the already-bound physics SHA-256/bytes from all shard manifests followed by a new sealed plan checkpoint;
- bind the expected exact NPZ array-name/shape/dtype inventory per world, or bind one closed layout plus an identity that covers each archive;
- fail before NumPy access on any missing, extra, symlinked, substituted or mismatched file.

Do not solve this by trusting the current working-tree path or by opening a shard manifest after physics outcomes are visible.

### 2. BLOCKER — `frozen_before_physics_open` is an assertion, not a durable gate

The plan and allowlist are untracked at this review point. No analysis implementation, synthetic qualification, source hash or independent implementation is bound. The primary and independent programs could diverge or be revised after raw access.

Required correction:

1. commit/push the corrected plan and allowlist;
2. implement both analyzers and tests without opening physics;
3. bind exact plan, allowlist, primary source, independent source, tests, Python, NumPy, platform and byte order in a pre-raw qualification artifact or external seal;
4. require synthetic qualification and an independent static audit at that exact checkpoint;
5. confirm both output roots and their `.partial` siblings are absent;
6. only then authorize one primary and one independent raw read.

### 3. BLOCKER — the self-contained classification reconstruction is not exact enough

Phrases such as “exact frozen score,” “retain ambiguity,” “advect q,” and “exact frozen nine-class precedence” do not specify an implementable independent algorithm. Since engine, instrumentation, runner and prior reproducer sources are forbidden, the plan itself must close every degree of freedom needed for byte identity.

Required correction: add a normative reconstruction appendix/object defining at least:

- detector unseen-set traversal, neighbour order, LIFO/push-time lifted-coordinate assignment, winding test, component ordering and every floating reduction order;
- exact raw/dilated IoU definitions, dilation topology, periodic distance, area ratio, complete edge qualification inequalities, score equation/order, tie margin, mutual-best selection, ambiguity edges and selection/event ordering;
- continuation/split/merge/appearance/dissolution/collapse/temporary-contact rules, track-ID assignment, parent ordering, lookahead and unresolved propagation;
- face-axis/source/target conventions, state-to-ledger time alignment, internal/boundary face masks and every sum/division order;
- cohort divergence equation, split/merge lineage convention, initialization rule, tolerance derived from operations, conservation/domain gates and no clipping;
- exact track summaries, missing-frame treatment, candidate-ID ordering, all nine classifier branches in precedence order and exact law/IC aggregation;
- exact canonical classification schema so parity cannot be achieved by copying committed labels.

The committed classification may be hash-checked at process start, but its world regimes and candidate IDs must remain quarantined until the raw reconstruction has been serialized and hashed. Only then may parity and the fixed eleven-world descriptive subset be evaluated.

### 4. BLOCKER — developmental milestones may be stitched across unrelated tracks

The pathway rules currently progress if any track supplies bounded activity and any track supplies turnover. This can manufacture an apparent formation→activation→turnover→persistence sequence that no track or genealogy followed. Multiple candidate tracks make the missing rule material, not hypothetical.

Required correction:

- define a track-coherent or genealogy-coherent pathway and state whether parent/child tracks may carry milestones across split/merge;
- if genealogy continuity is allowed, freeze the exact DAG traversal, cohort inheritance/reinitialization and tie ordering;
- compute every track pathway first, retain all of them, then define the world pathway by an explicit deterministic aggregation such as the maximum achieved ordered stage with stable tie-breaking;
- for candidate-world coherence, define whether the class is based on all committed candidate tracks, a multiset, a worst/best track, or one exact deterministic representative; never silently select a visually convenient track;
- define every `first_*`, `last_*`, episode count, terminal-alive and terminal-state field as track-level or world-level with exact min/max/any/all aggregation.

### 5. BLOCKER — terminal/censoring and episode semantics are incomplete

`candidate_episode_terminal`, `terminal_state` labels, `formation_opportunity` and `maintenance_opportunity` are emitted but undefined. `terminal_freeze_onset` does not say whether all observations through frame 159 must remain below both thresholds, how gaps are handled, or how multiple terminal tracks combine. “Observed/span frames” is ambiguous. A “brief” episode is undefined when no episode exists.

Required correction:

- replace `[0,159]` with an explicit inclusive detector-frame range `0..159` and bind ledger row `t` to the transition from state `t` to `t+1`;
- state whether both `observed_frames>=80` and `span_frames>=80` are required;
- define consecutive episode continuity, gaps, unresolved frames, null/no-episode values, terminal observation and `candidate_episode_terminal` exactly;
- define terminal-state predicates and their precedence, including empty suffix, per-track/world freeze, persistent active window and persistent other;
- define right censoring separately for track and world and prohibit reading it as future success;
- rename “formation quartiles”: the proposed 40/80/40 bins are not quartiles. Use `formation_time_bin` with those exact intervals, or freeze genuine equal quartiles;
- explain that the extra 32-frame stable-episode rule is a new exploratory descriptor, not a Stage-B gate.

### 6. BLOCKER — the estimands mix statistical units and introduce unjustified pairing

`B_conditional_maintenance` says “among worlds/tracks,” so its denominator is not defined. Track counts are post-formation, variable multiplicity, and not independent original-world units. Soup and compact replicate numbers are not declared matched random pairs; subtracting same-index worlds can imply a pairing the initializer does not establish.

Required correction:

- define separate world-level estimands with original world as denominator and nested track-level descriptive tables with no inferential weight;
- for world-level maintenance, freeze `any`, `all`, maximum-stage or another exact aggregation over tracks;
- define zero-denominator/null handling and always print numerator and denominator;
- replace the 32 “paired” differences with law-stratified unpaired soup-minus-compact fractions/summaries, or explicitly prove a shared-randomness pairing from the frozen initializer and label any index-matched display noninferential;
- define `formation_opportunity` and `maintenance_opportunity` as exact booleans/counts and never combine their denominators.

### 7. BLOCKER — the proposed “mechanism” signatures do not identify mechanisms

The trajectories are observational conditional descriptions. Uniqueness among four chosen signatures cannot establish causation or exclusion. Two rules have additional defects:

- `COMPACT_PREMATURE_FREEZE` counts the low-activity/low-energy terminal window that defines `FROZEN` as evidence for the cause of freezing. That disjunct is tautological. The bond-saturation/CV alternatives lack a frozen pre-onset window and aggregation.
- `DESTRUCTIVE_TRANSITION_PROXIMITY` joins temporal proximity and elevated exchange with `OR`; these are distinct explanations. It lacks a pre-candidate window, zero/empty-median rule, track/world aggregation and noncandidate comparison. High exchange can be maintenance rather than destruction.

Required correction:

- rename the section `observational_signatures_consistent_with` and define `ACTIONABLE...` as permission only to preregister a future non-causal diagnostic design, never as a mechanism finding or Stage C authorization;
- remove the tautological freeze disjunct and freeze an antecedent window ending strictly before freeze onset for bond saturation/CVs;
- split transition proximity and exchange elevation into separate signatures, or require both; define windows, denominators, zero handling and world aggregation;
- report candidate-conditioned signatures as selected-on-outcome descriptions and compare them descriptively against all eligible noncandidate tracks/worlds before calling them explanatory;
- enumerate competing observationally equivalent explanations and return `RAW_INSUFFICIENT` when the raw data cannot exclude them.

### 8. REVISE — actionability/outcome precedence is not complete or mutually exclusive

The plan does not define the result when audit passes, candidates exist, diagnostics are complete, coherence is true, but zero eligible signatures pass or one passes in fewer than four laws. “Multiple incompatible signatures” has no compatibility matrix. Missing a required array is both a layout failure (`AUDIT_INVALID`) and a `RAW_INSUFFICIENT` condition.

Required correction: freeze a total boolean decision table. At minimum:

- any required binding/key/layout/type/finite/replay/reconstruction failure → `AUDIT_INVALID`;
- a valid raw package that lacks only a predeclared optional mechanistic observable, has a zero/undefined required denominator, or leaves the listed explanations observationally equivalent → `RAW_INSUFFICIENT`;
- transient majority or incoherent candidates → `TRANSIENT_OR_HETEROGENEOUS_CANDIDATES` regardless of a coincident signature;
- define whether any two eligible signatures count as heterogeneous, or bind an explicit compatibility matrix;
- exactly one complete, coherent, nontransient observational signature meeting all span rules → `ACTIONABLE_DEVELOPMENTAL_HYPOTHESIS` with the non-causal claim limit;
- explicitly route zero-signature, sub-span, no-candidate and all denominator-edge cases.

### 9. REVISE — several metric names exceed the persisted quantity

`resource_exchange_per_mass` uses only `ledger__resource_natural`; it is not total resource exchange if other persisted resource channels exist. Boundary orientation, periodic seam handling, internal-face uniqueness and state/ledger alignment are not specified. Ratio behavior at zero mass/pre-candidate median is unstated.

Required correction:

- rename it `resource_natural_exchange_per_mass` unless all existing resource-flow channels are explicitly included;
- specify axis-major face ownership, forward/reverse orientation, periodic boundary masks, unique internal faces and exact summation order;
- define mass-zero, empty-support, no-internal-face and zero-baseline ratios as explicit null/false/error cases rather than output-dependent epsilons;
- distinguish coordinate seam crossing from winding exactly as planned, and never infer a mechanism from seam incidence.

### 10. REVISE — output schemas, numerical reproducibility and publication are open

File names alone do not make two implementations comparable. The plan lacks exact top-level/key/row schemas, order, scalar types, null conventions, float operation/reduction order and hashes. Exclusive file creation is not a family-atomic protocol and can leave ambiguous partial evidence.

Required correction:

- freeze a machine-readable schema for all eight files, exact row keys/types/order and canonical finite JSON/JSONL rules;
- bind numerical operations and an operation-derived tolerance before raw; no output-chosen tolerance or rounding;
- require primary and independent roots to be written as absent `.partial` siblings, closed/hash-inventoried, then atomically renamed once; define failure packages and prohibit silent reuse;
- make `COMPLETE.json` bind the plan/allowlist/source/environment/input identities and every output hash/bytes/row count;
- compare primary/independent recomputed classification, world transitions and analysis bytes, and document which large row files require byte identity versus independently recomputed semantic/hash equality.

### 11. REVISE — source-firewall normalization and tests are incomplete

Text fragments such as `edlab/` can be bypassed by Windows separators, case, symlinks or alternate resolved paths. Generic `python` does not bind the environment used for NumPy reductions.

Required correction:

- resolve every input under the repository root, reject symlinks/reparse points and `..`, normalize to lowercase forward-slash repo-relative paths, then exact-match the closed allowlist;
- prohibit directory discovery/globbing and refuse extra/missing physics paths;
- freeze the exact interpreter/environment or enforce equality to a sealed environment object;
- add synthetic tests for case/backslash/traversal/symlink bypass, unauthorized basename, NPZ duplicate/unsafe members, object arrays/pickle, extra keys, nonfinite values, hash mismatch, multi-track milestone stitching, split/merge lineage, no episode, terminal gaps, zero denominators/ratios and every outcome-precedence branch.

## INFERRED

- The proposed autopsy can become a rigorous descriptive decomposition, but the present plan permits implementation-dependent labels and observational stories to be upgraded to “mechanisms.”
- The strongest legitimate product is a complete, raw-reconstructed formation/maintenance trajectory atlas with explicit censoring and observational signatures. It cannot identify a causal mechanism or rescue the Stage-B region failure.
- The two multiple-candidate-track worlds guarantee that unspecified within-world selection would affect coherence and signature counts.

## HYPOTHESIS

A corrected self-contained plan may distinguish descriptive formation failure, activation failure, turnover failure, post-turnover persistence failure and horizon censoring across the complete frozen family. It may not determine which dynamical cause would change those outcomes without a new pre-data intervention design.

## WHAT WOULD FALSIFY THIS?

- A closed reconstruction specification and synthetic fixtures showing exact parity under independently implemented algorithms would falsify the claim that reconstruction is under-specified.
- A pre-raw per-physics identity bound directly to accepted-parent Git objects or sealed metadata would close the raw-authentication blocker.
- An exact lineage/world aggregation tested on multi-track split/merge fixtures would close the milestone-stitching blocker.
- A total outcome truth table and non-tautological antecedent observational signatures would close the actionability-precedence blockers.

## Failures and dead ends

- One combined file read was truncated by the terminal output cap. I did not infer missing plan content from the truncated stream; I reparsed only the already-authorized plan and printed its remaining top-level sections explicitly.
- I intentionally did not follow the allowlist's broader operating-document paths because the assigned pre-raw review imposed a narrower scientific-input firewall.
- No physics path was opened even to compute a digest; this is why the missing binding is reported rather than silently repaired from raw bytes.

## Decisions

- `DEV_FEASIBILITY_FAIL` remains immutable.
- No Stage C, intervention, new family, threshold change, selected-world confirmation or causal claim is admissible.
- The plan must be corrected and independently re-audited before any physics archive is opened.

## Interim disposition and handoff

**`REVISE_PLAN_BEFORE_RAW — DO NOT OPEN physics.npz`**

Exact next authorized action: the primary agent may edit only the plan/allowlist to close the findings above, then request another metadata-only adversarial review. No analyzer implementation should be treated as frozen and no raw read is authorized by this journal.

## APPENDED FINAL NO-RAW RE-AUDIT — 2026-07-19 01:35:15 +02:00

This section appends to, and does not erase, the initial adverse review. The initial `REVISE_PLAN_BEFORE_RAW` disposition was correct for the earlier hashes. The package was revised without opening raw physics and was then re-audited at the exact stable hashes below.

| Frozen input | SHA-256 at final re-audit |
|---|---|
| `docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B_AUTOPSY_ANALYSIS_PLAN.json` | `1088478a5e17ea8169143fe20715783cb0727a93727d9f6516313fbe37c5c0f9` |
| `docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B_AUTOPSY_SOURCE_ALLOWLIST.json` | `3b86f6559620c7130660b0daec84066a1be0c29657fafd266803e5e28ea431a0` |
| `docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B_AUTOPSY_RECONSTRUCTION_PROTOCOL.json` | `a63048283aeab44f0e39d997dfe049b6f20ccf44ec9a54efcd59d7d595c9eead` |
| `docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B1_MANIFEST.json` | `194e082f9d3809f2531912d825480fad5b683dbe9d9fceec8050260fe493dd50` |
| `results/INTERVENTIONAL-INDIVIDUALITY-00-STAGE-B-DEV/root_manifest.json` | `07428729da7b7d60a3493d9ee1fb8ec31ab0d7b870b5d9fdb54095ededff63cf` |
| `docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B_CLASSIFICATION.json` | `7b7cf200fd6cc7ccfbd77b19de0ca1231df22c1d2d9ab5d7548828df7c3ed14e` |

The plan's embedded reconstruction-protocol and source-allowlist hashes equal the stable file hashes. The 64 exact physics paths remain unique and are bound to the accepted-parent Git tree by 64 blob records with aggregate SHA-256 `ad7e00a713d44568e5e64a695266e66b38a8324db12568786d5ccaa4aff13f71`. This check used Git tree metadata only; no physics archive was opened, statted through a scientific loader, or parsed.

### OBSERVED closure

- The normative protocol now closes the 46-key NPZ inventory, safe archive-loader contract, array dtypes/shapes, state and numerical qualification gates, matter identities, energy-residual gate, detector traversal and lifted geometry, association metrics/reason enum/selection, per-transition track-ID allocation, passive-cohort update, classifier precedence and canonical aggregation order.
- Same-track milestones, deterministic candidate/noncandidate representatives, all-world candidate-episode fields, terminal/censoring rules and world-scoped lifecycle counts are explicit. A no-episode representative yields integer zeros for candidate status, episode count and longest episode, consistently with the output schema.
- World and track denominators are separated. Nominal soup/compact index alignment is explicitly non-matched, noninferential and excluded from decisions.
- Developmental signatures are labelled observational only. Their windows, availability rules and total outcome precedence are frozen. Missing branch-specific diagnostics cannot silently become a preferred result.
- `resource_natural_exchange_per_mass` now names only the persisted natural resource channel. Face orientation, internal/boundary reductions, CVs, seam diagnostics, medians and floating serialization are specified.
- New artifact schema literals, nested analysis/atlas contracts, milestone fingerprints, per-event payloads, qualification comparison and atomic root publication are closed enough for two independent implementations to be tested for byte identity.
- The source firewall now binds its own allowlist hash, rejects unsafe paths/reparse points, and requires exact accepted-parent blob identity before NumPy. The archive gate requires `allow_pickle=False` and rejects unsafe, duplicate or nonnumeric members.

### INFERRED and remaining gates

The revised package is now sufficiently determinate for code-only implementation and synthetic fixture qualification. This is not authorization to open `physics.npz`: the plan, protocol and allowlist are still untracked at this audit point; analyzers and fixtures are not yet implemented, committed, source-hashed, independently statically audited or synthetically qualified; output roots have not yet been checked as absent at an execution checkpoint.

The raw autopsy remains descriptive. Even a unique observational signature may authorize only a fresh pre-data design. It cannot identify a mechanism, alter `DEV_FEASIBILITY_FAIL`, promote a selected subset, open Stage C, or establish individuality.

### WHAT WOULD FALSIFY THIS FINAL STATIC JUDGMENT?

- A synthetic fixture producing different canonical bytes from two faithful implementations would show a remaining normative ambiguity and restore `REVISE_PLAN_BEFORE_RAW`.
- Any source/hash/environment drift, unsafe archive behavior, unauthorized read, non-absent output root, classification mismatch or numerical qualification failure must fail closed before or during the later raw gate.
- Any implementation that imports scientific engine/analyzer code or consults forbidden Stage-B artifacts is outside this judgment.

### Final pre-code disposition

**`PASS_PLAN_FOR_CODE_ONLY_IMPLEMENTATION — NO RAW`**

Exact next authorized action: implement the primary and genuinely independent analyzers plus deterministic synthetic/firewall fixtures at these frozen plan/protocol/allowlist semantics; then commit and independently audit the exact code-only checkpoint. Only a later explicit pre-raw authorization after those gates may permit the one bounded read of the 64 allowlisted physics archives.

- Re-audit end: 2026-07-19 01:35:15 +02:00
- Ending HEAD at re-audit: `c31bf27ea80a6a3dcc60d0ec5380f668358671ff`
- Physics/raw access during both reviews: none
