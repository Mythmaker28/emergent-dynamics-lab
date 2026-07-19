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

## APPENDED CODE-ONLY PRE-RAW IMPLEMENTATION AUDIT — 2026-07-19 02:03:12 +02:00

This was a separate code-only gate after the static-plan PASS. I inspected only the three control files, `analysis/interventional_individuality_stage_b_autopsy.py`, and `analysis/test_interventional_individuality_stage_b_autopsy.py`. I did not open the independent reproducer, any `physics.npz`, Stage-B report, detailed result, forbidden engine/analyzer source, checkpoint or world.

### Exact inspected hashes

| File | SHA-256 at code audit |
|---|---|
| frozen plan | `1088478a5e17ea8169143fe20715783cb0727a93727d9f6516313fbe37c5c0f9` |
| current source allowlist | `c8af265d28b898025b989025ddcf8c39f99c5fe5c48d03113ce7a410ba9ef670` |
| current reconstruction protocol | `ab47ac077924f146197e27b26f8bb5fa42d691460d5d72c945687942b4e6bbd0` |
| primary analyzer | `8b539349565da48222457886ca14543de81f5d28fa484e376b6cfecf47bc845c` |
| focused synthetic tests | `14f35ba9549e5164f49692ec25744d8fefb7e2cdfde84f73d474ceab0566a55a` |

Focused command:

`C:/Users/tommy/Documents/ising v3/.venv/Scripts/python.exe -m pytest -q analysis/test_interventional_individuality_stage_b_autopsy.py`

Observed result: `50 passed in 0.29s`.

### OBSERVED strengths

- The module is engine-free and import-time inert. The detector, association, tracker, cohort update, classifier precedence, same-track developmental summary, canonical serialization and exclusive partial-root publication substantially follow the frozen specification.
- The safe NPZ loader uses `allow_pickle=False`, checks the central-directory inventory before NumPy, and rejects duplicate, nested/traversal, object, structured and nonnative members.
- Synthetic tests cover periodic detector seam/winding behavior, association ties, tracker ID allocation and collapse/many-to-many ambiguity, cohort conservation/bounds/no clipping, candidate boundary values, all classifier branches, outcome precedence, anti-stitching, representative ties, terminal gaps/dissolution/censoring, no-episode zeros and zero-baseline unavailability.

### Binding blockers

1. **The controls are no longer sealed together.** The committed plan still binds protocol `a6304828...` and allowlist `3b86f655...`, while the implementation worktree contains protocol `ab47ac07...` and allowlist `c8af265d...`. The changes add a colon/drive archive rejection, exact fingerprint/trajectory-class encodings, a test journal path and the comparison command. They are reasonable code-only clarifications, but `load_controls` must correctly reject them under the old plan. The final corrected controls must be rehashed, rebound in the plan, recommitted and re-audited before raw.

2. **The destructive-signature law-span gate can be manufactured by an unqualified subtype.** In `build_analysis`, `destructive_laws` is computed from the union of dissolution and high-exchange support, even when only one subtype reaches nine worlds. I ran a deterministic in-memory counterexample: nine dissolution-support worlds across only three laws plus two high-exchange worlds from an unqualified subtype across two other laws produced `qualified=True` and five reported laws. The four-law actionability span must be computed from the support set that actually qualifies: the sole qualifying subtype, or the qualifying common intersection when both subtypes are required to coincide. Add the counterexample as a regression test.

3. **The scientific-read firewall has a substitution window.** `verify_inputs_before_arrays` allowlist-checks and hashes each physics path, closes it, and later `process_world` reopens the path through direct `safe_load_npz`/`numpy.load`. This is not one guarded read of the authenticated bytes and permits path-content substitution between verification and parsing. Pass authenticated bytes or an authenticated open handle into the safe loader, or reverify the exact bytes after parsing before any result is accepted. The same principle applies to controls: `build_package` captures control bytes, but `main` rereads plan/protocol/allowlist after analysis to populate `COMPLETE.json`; use the captured hashes or require unchanged-byte identity before publication.

4. **Output and comparison paths are not fail-closed to the allowlist.** `--output-root`, both `--compare-only` roots and `--qualification` accept arbitrary paths. Comparison reads files directly, does not reject symlink/reparse roots or extra/missing package members as a closed inventory, and does not independently validate each `COMPLETE.json` file/hash inventory before writing `QUALIFICATION.json`. Enforce the exact authorized primary, independent and qualification paths with the same normalized/reparse-aware guard and validate both closed packages.

5. **The runtime report asserts an unchecked pytest version.** The code verifies interpreter, Python, NumPy and byte order, but emits `pytest: 8.4.2` without querying it. Either validate the installed version exactly or remove it from the runtime gate/schema through a resealed amendment.

6. **The focused suite does not yet satisfy the plan's own pre-raw fixture list.** No test exercises casefold, backslash, `..`, symlink or Windows reparse firewall rejection; `validate_raw_arrays` state/finite/neutral-scale/reference/matter/energy identities; exact output schemas; exclusive/no-overwrite partial-root behavior; closed package comparison; or the eligible mechanism law-span logic. Detector weighted lifted geometry and association qualification boundaries also lack direct parity fixtures. Passing 50 current cases is therefore necessary but not sufficient.

7. **Compact-precursor availability needs an exact tested implementation.** Bond availability is initialized permanently true, and low-heterogeneity availability checks only `len(pre) >= 8`, not whether any eight-frame consecutive pre-onset observation window exists. This conflicts with the plan's incomplete-window-to-unavailable rule when a track has gaps. Freeze the intended bond eight-frame opportunity rule if needed, detect consecutive-window availability independently of precursor values, and add missing-frame fixtures.

### INFERRED

The core reconstruction is close, but the present checkpoint can change the selected autopsy outcome and cannot yet prove that parsed raw bytes are the authenticated bytes. The stale embedded hashes independently make the current runner fail closed. These are pre-raw repairable code/control issues and do not license inspecting outcomes, changing thresholds or altering `DEV_FEASIBILITY_FAIL`.

### WHAT WOULD FALSIFY THESE BLOCKERS?

- A corrected law-span regression must return the destructive signature false for the constructed three-law qualifying support, regardless of extra worlds in an unqualified subtype.
- A guarded-load test must demonstrate that changing or redirecting a shard after authentication cannot reach NumPy or publication.
- Firewall and publication fixtures must reject every unauthorized/reparse/dotdot/case variant and any pre-existing, incomplete or internally inconsistent package root.
- The final plan must embed the exact final protocol and allowlist hashes, and the exact code/tests checkpoint must pass the expanded focused suite and another static audit.

### Code-only disposition

**`BINDING_BLOCKERS — NO PASS_CODE_FOR_RAW — DO NOT OPEN physics.npz`**

Exact next authorized action: repair only the primary analyzer/tests and code-only controls, run the expanded synthetic suite, reseal the final plan/protocol/allowlist and request another code-only adversarial audit. Raw execution remains unauthorized.

- Code-audit end: 2026-07-19 02:03:12 +02:00
- HEAD during audit: `168b86c`
- Physics/raw access: none

## APPENDED SECOND CODE-ONLY PRE-RAW AUDIT — 2026-07-19 02:29:00 +02:00

This append-only review supersedes the earlier implementation blockers only for the exact final hashes below. It inspected the final plan, protocol, allowlist, primary analyzer/tests, independently structured reproducer and its journal. It did not open, stat, parse or reconstruct any `physics.npz`, scientific world, result report, engine source, checkpoint, enrollment manifest or shard manifest.

### Role, scope and Git state

- Role/run ID: independent adversarial code reviewer, `RUN-20260719-0100-II00-B-AUTOPSY-REDTEAM`.
- Review interval: second code-only pass begun after the 02:03 blocker report; final audit ended `2026-07-19 02:29:00 +02:00`.
- Starting and ending HEAD: `168b86c83db22999025b34a5e93aad299529037d` on `codex/interventional-individuality-00-stage-b-autopsy`.
- Git status was intentionally not invoked because this gate prohibited even broad filesystem statting of the scientific shards; the exact reviewed files were hashed directly instead.
- Assigned scope: verify closure of the seven prior blockers, source separation, precursor continuity, root/COMPLETE validation, authenticated-byte loading, TOCTOU closure, destructive-support logic, runtime enforcement, classification reconstruction, synthetic byte parity and provenance claims; then issue only a code-for-raw disposition.

### Exact final reviewed hashes

| File | SHA-256 |
|---|---|
| analysis plan | `3dda24c82936507566e2abe45186876c22c7954d80b8a4af7b75c9e742e91bb9` |
| source allowlist | `75b23538e5c7820d96414696727d65baf4bdccde05b3a41c4e49ae686763061b` |
| reconstruction protocol | `ee7c162755eebbcf57f2ed343c6f5d6bc916b1a971570f4687442cf7f6ff692f` |
| primary analyzer | `d8961cf7e2e9fd2f93b939584d331db97631cb222b5e5064fdb762d736ab23a5` |
| independent reproducer | `fe6e72aa18d9b540220f9f3aae185a6c0baae2da88d5b0b1835dba46c3879667` |
| focused tests | `9aa429f3c1955b94736a42eec8e41fa64550e3c6eeae3d750123cfa384d96dcd` |
| independent reproducer journal | `abd2ffd0dab29fac286c4f6d69510f7ca84bcfcdcc9f212b0abc69b376e70bfb` |

The final plan embeds exactly the final protocol and allowlist hashes and exact control paths above. The accepted parent remains `c31bf27ea80a6a3dcc60d0ec5380f668358671ff`.

### Reproducible code-only validation

```powershell
& 'C:/Users/tommy/Documents/ising v3/.venv/Scripts/python.exe' -m py_compile analysis/interventional_individuality_stage_b_autopsy.py analysis/interventional_individuality_stage_b_autopsy_reproduce.py
& 'C:/Users/tommy/Documents/ising v3/.venv/Scripts/python.exe' -m pytest -q analysis/test_interventional_individuality_stage_b_autopsy.py
& 'C:/Users/tommy/Documents/ising v3/.venv/Scripts/python.exe' analysis/interventional_individuality_stage_b_autopsy_reproduce.py --self-test
```

OBSERVED:

- `py_compile`: PASS.
- Focused primary/cross-implementation suite: `87 passed in 1.01s`, with zero failures and zero skips.
- Independent self-test: `SELF_TESTS_PASSED`, 26/26 named umbrella fixtures.
- Deterministic end-to-end empty and persistent synthetic worlds produce canonical-byte-identical world-transition, track-observation and event payloads between the two implementations. Atlas and analysis objects also have explicit cross-implementation canonical-byte parity tests.
- A deterministic mocked Windows reparse attribute test closes the platform privilege gap that previously caused the live symlink fixture to skip.

### OBSERVED blocker closure

1. **Control reseal:** CLOSED. The plan's protocol/allowlist paths and hashes equal the exact final controls.
2. **Destructive law span:** CLOSED. Four-law support comes only from the qualifying destructive subtype, or the at-least-nine overlap when both qualify; the earlier three-law counterexample is a regression fixture.
3. **TOCTOU/authenticated loading:** CLOSED. Both analyzers parse the exact in-memory bytes that pass the second size/SHA-256/Git-blob authentication; a substitution cannot reach NumPy.
4. **Output/compare scope and COMPLETE validation:** CLOSED. Exact primary, independent and qualification literals are enforced before delegation and again at use; reparse/dot-dot/case variants, nonexact inventories, pre-existing roots, hash lies and overwrite attempts fail closed. All eight package members and COMPLETE semantics are validated before qualification.
5. **Runtime gate:** CLOSED. Interpreter, Python, NumPy, pytest and byte order are checked rather than asserted.
6. **Synthetic coverage:** CLOSED for this gate. The final 87-test suite exercises numerical/raw-array identities, detector/tracker/cohort/developmental rules, schema/publication/firewall failures, exact classification aggregation, full zero-count vocabularies and two-implementation parity; the independent 26-fixture suite separately qualifies its implementation.
7. **Compact precursor continuity:** CLOSED. Availability requires a gap-free same-representative pre-freeze history from onset through freeze minus one, with the exact eight-frame and first-16/final-eight obligations; missing/gapped fixtures fail unavailable.

Additional closures:

- The independently structured reproducer imports no project/scientific module and independently rebuilds every classification field, including atlas counts with zeros, candidate regions and disposition, before comparing canonical bytes. It no longer copies committed atlas or candidate-region fields.
- The root-manifest exact authenticated bytes, top/shard schemas, population, disposition, bindings and COMPLETE shard/world set are checked before any scientific shard could be loaded. Enrollment and shard manifests remain unopened.
- No-formation trajectory class is frozen as null and covered by both independent self-tests and end-to-end parity.
- Open-ended package or arbitrary CLI path behavior found during this audit was repaired and is now regression-tested.

### Independent-reproducer provenance limitation

The reproducer journal now discloses an accidental targeted-`rg` incident. Its command was intended for the plan/protocol after the independent mechanics and 21-fixture suite already passed, but the returned output included isolated primary source/test snippets containing already-frozen signature, maintenance and path-validation literals. No raw data, scientific outcome, classification value, result artifact or primary file was deliberately opened. Some later schema/path hardening overlapped those literals.

INFERRED: this prevents describing the reproducer as a pristine clean-room implementation. It does not require a third implementation for this gate because the substantive detector, association, tracking, cohort, classification and developmental mechanics predated the exposure; the source remains separately structured with no shared project imports; the incident is fully disclosed; and direct adversarial synthetic parity now tests both implementations. Final reports must retain this limitation and use “independently structured/recreated,” not an unqualified clean-room claim.

### Scientific and security boundaries

- `DEV_FEASIBILITY_FAIL` remains immutable; this audit authorizes no reinterpretation, candidate selection, threshold change, new seed/family, intervention, causal claim or Stage C.
- No scientific outcome was observed. The later raw run remains one bounded, allowlisted developmental autopsy followed by exact package comparison and human review.
- WHAT WOULD FALSIFY THIS PASS?: any hash/source drift from the table, non-absent authorized output root, runtime mismatch, input-binding/Git-blob/raw-layout/numerical failure, committed classification or candidate-set mismatch, primary-independent byte mismatch, COMPLETE/qualification failure, or firewall violation. Any such event must stop without repair from outcomes.

### Final code-only disposition

**`PASS_CODE_FOR_RAW`**

Exact next authorized action: checkpoint the exact reviewed code-only state and obtain the mission's explicit raw authorization. This journal itself does not open raw, execute the autopsy or authorize any work beyond the single frozen allowlisted run and byte-identity qualification.
