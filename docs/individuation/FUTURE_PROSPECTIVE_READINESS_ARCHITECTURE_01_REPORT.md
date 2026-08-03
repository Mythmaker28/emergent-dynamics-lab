# FUTURE-PROSPECTIVE-READINESS-ARCHITECTURE-01 — report

## Part I — FROZEN EVALUATION PROTOCOL

This part is frozen before any route of this mission is designed, drafted, ranked or preferred. It is
committed alone. The decision in Part II must cite this commit and must be argued against it. Nothing
in Part I may be silently revised: a required deviation is a reason to return `ARCHITECTURE_REVISE`,
not to edit this section.

**No route was designed, drafted, ranked or preferred before this commit.** At the time of this
commit no comparative table, no preliminary decision and no route recommendation exists in this
mission's workspace.

Part I is a **byte-exact prefix** of the final report. Part II is appended after this commit and
never rewrites a byte above the terminator at the end of this part.

---

### 1. Authority and scope

**Authorizing chain (exact).**

| Role | Ref / commit |
|---|---|
| Authorizing human-review branch | `codex/future-lifecycle-owned-pipeline-runner-00-human-review` |
| Authorizing human-review commit (this branch's parent) | `d293eaf994fa77d4c63fbf14f72d10da377a523d` |
| Its parent — sealed owned-pipeline candidate | `10034eaa0bd8f2c32278959db96ae0095f737298` |
| This branch | `codex/future-prospective-readiness-architecture-01` |
| Predecessor architecture | `FUTURE_PROSPECTIVE_READINESS_ARCHITECTURE_00`, terminal disposition `ARCHITECTURE_REVISE`, `NO_ROUTE_SELECTED` |

The authorizing commit records `HUMAN_REVIEW_ACCEPTED`, acceptance of
`OWNED_PIPELINE_RUNNER_00_QUALIFIED`, and authorization of exactly one successor mission:
`FUTURE_PROSPECTIVE_READINESS_ARCHITECTURE_01`. This branch is rooted at that commit so that the
architecture physically contains its own authorization.

**Scope.** Architecture, comparison and decision only.

Not done in this mission: no runner is implemented; no source or test file is modified; no engine,
tracker, simulation, parameter sweep, pilot family or seed is created or executed; no historical raw
scientific data is opened; no preregistration is written; no evidence-root anchoring is performed.

Deterministic analytical power and precision calculations are permitted, executed only under `/tmp`,
consuming **only newly declared design targets**. They consume no historical scientific observation of
any kind. Any calculation that would require a historical estimate is not performed; the corresponding
design parameter is declared as an assumption and labelled as such.

**Forward motion is not mandatory.** This mission may select one route, request revision, or conclude
that the program has no admissible prospective route.

---

### 2. Scientific question (frozen)

The question carried forward from Architecture 00 §2 is unchanged and remains the target of the whole
program:

> **Can an intervention applied to one persistent organizational entity be shown to change that
> entity's own future behaviour, in a way that is not explained by its environment, by a redundant
> copy of its state, or by a relation it participates in — under material turnover, in a prospectively
> declared design, with no selection on outcome?**

Architecture 00 closed with `ARCHITECTURE_REVISE` and no route selected. Two sub-questions were left
explicitly open by that decision, and they are the only two prospective questions this mission is
permitted to compare (together with the affirmative case for stopping):

**Q-E (replication density).** Under a newly and prospectively generated design, at what rate does the
conjunction of *persistence* and *independently verified material turnover* reproduce across laws,
replicates and initial-condition classes?

**Q-G (symmetry-broken internal convention).** Can nominally identical entities in a shared symmetric
environment independently select between two physically equivalent internal conventions, preserve the
selected convention through independently verified material turnover, and exhibit **entity-local
causal ownership** of that convention?

**Q-F (consolidation).** Is the expected epistemic value of stopping and consolidating higher than the
expected epistemic value of the best admissible bounded prospective family?

Q-E and Q-G are different questions and are **not** interchangeable. Q-E is a question about
*reproducibility of a conjunction across a population of laws*. Q-G is a question about *causal
ownership of a state by an entity*. Neither answers the other. A route may not be credited with the
evidential value of the other route's question.

**Explicitly not the question.** "Does the system remember", "do entities survive", "do entities
behave differently", "is there a lineage", "does the software qualify" — all previously answered,
cheap, or non-scientific. None of them may be substituted for the target sentence above.

---

### 3. Frozen facts (carried forward without reinterpretation)

These are recorded as facts, not as evidence to be reanalysed. They may **motivate** questions. They
may **not** set thresholds, priors, parameter bounds, sample sizes or expected effect sizes anywhere in
this mission or in any family it authorizes.

**3.1 From the closed Stage-B family.**

1. Persistence and material turnover are **not known to be mutually exclusive**.
2. **11/64** closed Stage-B worlds exhibited **both**.
3. Those eleven may **not** be dismissed, relabelled, or selected as confirmation.
4. **0/8** laws met the two-of-four minimum in **both** initial-condition classes.
5. Stage B therefore showed **inadequate replication density with initial-condition dependence**.
6. Stage B did **not** prove structural impossibility.
7. The Stage-B family is **closed**: it cannot be reused, tuned against, extended, or mined.
8. The historical `M_MINUS` result **cannot** confirm Route G.

**3.2 Carried forward from Architecture 00 §4.**

9. Causal experience memory has previously been demonstrated **only at a low-dimensional level**.
10. Memory being causal, erasable, transplantable or turnover-resistant is **not sufficient** for
    individuality.
11. Persistent binary state alone is only **low-dimensional causal state**, not individuality.
12. The frozen Stage-B disposition `DEV_FEASIBILITY_FAIL` reflected **structural integrity loss**
    (`SPLIT`, `LOST`), not proof that material turnover is impossible, and does **not** establish
    absence of individuality.
13. Historical survivors may **not** be selected or retried. **Stage C was never authorized.**
14. Local, environmental, redundant and relational ownership were **not identifiable** under the
    previous intervention algebra.
15. The **scaffold architecture STOP remains valid**. The lattice-bond substrate routes around that
    STOP but does **not** silently prove ownership.
16. All Kovacs work remains **independent and closed**.

**3.3 Successor engineering facts (established after Architecture 00; verified in this mission's
preflight from accepted records only).**

17. `LIFECYCLE_REQUALIFICATION_01R_QUALIFIED`: sampled frames are **mandatory**; there is no
    schedule-free path.
18. Disappearance observed at **non-unit cadence** is no longer globally rejected. The Architecture-00
    blocker "empty-right-frame / non-unit-cadence path remains rejected" is **closed**. This is the
    single technical change that reopens Route E for consideration.
19. `RUNNER_STACK_REQUALIFICATION_01_QUALIFIED` is accepted.
20. `OWNED_PIPELINE_RUNNER_00_QUALIFIED` is accepted under human review, with the exact narrow claim:
    within the supported module-level synthetic API, the runner invokes the acquisition source once per
    declared schedule element, persists and re-reads frames and the acquisition ledger, executes
    mandatory tracking and lifecycle validation from that re-read evidence, and blocks `COMPLETE` and
    `AnalysisAccess` unless the complete local evidence set is internally consistent.
21. **No engine and no scientific runner has executed at any point** in this program's engineering
    line.
22. Current infrastructure provides **synthetic mechanical qualification only**. It is not scientific
    evidence (see G12).

**3.4 Accepted limitations that bind every route.**

23. **Package export deferred.** The owned pipeline is reachable only as an exact module-level API,
    not re-exported through `edlab/substrates/lattice_bond/__init__.py`. Direct module import is
    **not** equivalent to package re-export.
24. **OP-L3 threat model.** Local frame and ledger hashes detect ordinary and partial tampering; an
    adversary able to rewrite and consistently re-pin the entire mutable evidence directory is outside
    the locally detectable threat model. Morphology (area, mass, centroid, pixel set, radius of
    gyration) is **not** bound into lifecycle semantics. OP-L3 does **not** prove the pipeline
    scientifically trustworthy.
25. **Independent trust anchor.** Preventing complete internally consistent re-pinning requires an
    independent trust anchor. That anchor may be a secret-backed signature, but it may equally be a
    **public immutable or append-only commitment** (published Git object, transparency log, timestamped
    registry, WORM storage, externally published root digest). The statement "there is no repair
    without a secret" is superseded and may not be relied on.
26. **Physical elapsed time is not authenticated** by the pipeline. Acquisition-source identity is a
    reproducibility binding, not an authority.

---

### 4. Claim ladder (frozen)

Every route must state the **highest rung it can identify** and must explicitly list the rungs it
leaves unsupported. The ladder is carried forward unchanged from Architecture 00 §3; only the *status*
column is updated where a successor engineering decision changed what is now testable.

| Rung | Claim | Status entering this mission |
|---|---|---|
| 1 | A state variable stores past exposure | previously demonstrated at a low-dimensional level |
| 2 | That state causally affects later behaviour | previously demonstrated at a low-dimensional level |
| 3 | The state persists across material turnover | **open**; the closed Stage-B family failed on structural integrity before this could be answered; the cadence blocker that concealed it is now closed |
| 4 | Two entities can be causally addressed separately | **open** |
| 5 | Intervention on A changes A's future differently from B's | **open** |
| 6 | The effect belongs specifically to A rather than its environment, a redundant copy, or a relation | **open — this is the rung that matters** |
| 7 | Evidence supports individual organizational ownership | **open; not reachable by any single family** |

**Vocabulary discipline (frozen).** "Survival", "memory", "lineage", "persistence", "different
responses", "reproducibility" and "convention" are **not** synonyms for individuality and may not be
substituted for rungs 5–7. A route that reaches rung 3 and calls it individuality is inadmissible
regardless of how clean its statistics are.

**Ceiling declaration (frozen).** Each route must state, in one sentence, the maximum claim its
complete success would license, and must state at least one thing that success would **not** establish.
A route whose stated ceiling exceeds what its design can identify fails G25.

---

### 5. Route-independent estimand constraints (frozen)

Every route declares **exactly one primary estimand**, before any design parameter is chosen, in the
following six attributes. All six are mandatory; a missing attribute is a G13 failure.

1. **Population** — the prospectively generated sampling frame, defined without reference to any
   closed-family outcome.
2. **Unit of analysis** — entity, lineage, pair, law, world, or environment. Stated once, fixed, and
   never changed post hoc.
3. **Condition / treatment (or exposure) definition** — including, where relevant, the intervention,
   its target, and its sham/off-target comparators.
4. **Outcome (endpoint) definition** — the exact measured quantity and the exact procedure that
   produces it from pipeline evidence.
5. **Intercurrent-event strategy** — for each of split, merge, lost, disappearance, mechanical
   ineligibility and acquisition failure, the declared strategy (treatment-policy, composite,
   while-alive, principal-stratum or hypothetical), chosen in advance. "Exclude" is **never** an
   admissible strategy for a post-allocation event.
6. **Population-level summary measure** — the exact functional (rate, difference, ratio, density,
   correlation, equivalence margin) computed over the enrolled denominator.

**Additional route-independent constraints.**

- **C1.** The primary estimand must be **computable from the enrolled denominator alone**. If it can
  only be computed on survivors, it is not a primary estimand.
- **C2.** The primary estimand must be **entity-level** unless the route prominently declares the
  change of unit; a lineage-level or population-level estimand may still be recommended, but it may
  **not** be presented as answering the entity-level target question (G22).
- **C3.** The primary estimand may **not** be the hypothesis that persistence and material turnover are
  mutually exclusive. That hypothesis is falsified by fact 3.1.2 and testing it again is an
  inadmissible design.
- **C4.** No component of the estimand — threshold, window, cadence, duration, dose, tolerance — may be
  numerically derived from the closed family (G16).
- **C5.** Secondary and exploratory quantities are permitted and must be labelled as such. They can
  never be promoted after the outcome is observed.
- **C6.** The estimand must be stated in a form that makes both a **positive** and a **negative**
  conclusion expressible. If only one direction is expressible, the route fails G26.
- **C7.** Any claim of *independence* between units must be operationalized as an **equivalence claim
  with a predeclared margin**. Failure to reject dependence is not evidence of independence.
- **C8.** Any claim that a quantity *persists through turnover* requires turnover to be established by
  evidence **independent of the persistence readout** (G6).

---

### 6. Complete gate set (frozen — hard, pass/fail, applied before any comparison)

A route that fails **any** gate is inadmissible. Gates are **not tradeable** against strengths and are
**never averaged**. One fatal gate failure rejects a route.

**6.1 Gates carried forward from Architecture 00 §5 (unchanged in requirement).**

| Gate | Requirement |
|---|---|
| **G1 — Estimand declared** | The route states one exact estimand in advance, and states its unit: entity, lineage, pair or environment. |
| **G2 — No outcome selection** | No filtering to survivors, no replacement of failed units, no retry with nearby seeds, no post-hoc eligibility. |
| **G3 — No historical tuning** | No duration, threshold, cadence, dose or window derived from a previous family's outcomes. |
| **G4 — Competing-risk honesty** | Post-allocation failure is an outcome or competing event, never an exclusion. Any survival-conditioned quantity is declared as such and is not the primary estimand. |
| **G5 — Ownership confrontation** | The route explicitly confronts the environmental, redundant-copy and relational alternatives to entity-ownership. A relabelled version of the rejected environmental port is inadmissible. |
| **G6 — Turnover evidence** | If the route claims turnover, it states what independent evidence establishes that material turnover occurred, separately from the effect being measured. |
| **G7 — Lifecycle exhaustiveness** | Exactly one terminal lifecycle state per track; global rejection on any local violation; no successful subset may redefine the family. |
| **G8 — Stage separation** | Synthetic qualification, feasibility-only qualification, independent prerequisite reproduction and scientific execution are separate families. |
| **G9 — Interpretable failure** | A negative result must remain publishable and interpretable. A route that can only produce a result when it succeeds is inadmissible. |
| **G10 — No engineered answer** | The route states how it avoids building individuality into the substrate, and what independent prerequisite reproduction is required before any individuality claim. |
| **G11 — Cadence honesty** | The route cannot silently enter a rejected or survivorship-generating cadence path. |
| **G12 — Software is not evidence** | Lifecycle qualification, manifests, digests and viewers are engineering artifacts. None of them is scientific evidence for any rung. |

**6.2 Successor gates added by this mission (stricter; mandated by the authorizing brief).**

| Gate | Requirement |
|---|---|
| **G13 — Exact prospective estimand** | All six attributes of §5 are declared before any design parameter is chosen, and before any data of any kind exists. |
| **G14 — Experimental unit and enrolled denominator** | The experimental unit and the exact enrolled denominator are declared, with the exact moment of enrolment and the exact rule that fixes the denominator. |
| **G15 — No outcome-dependent eligibility or replacement** | Eligibility is decided strictly before allocation and strictly without reference to any outcome. Failed units are never replaced, retried, re-seeded or topped up. |
| **G16 — No calibration from the closed family** | No threshold, parameter, timing, cadence, sample size, prior, effect size or bound is derived, fitted, tuned or eyeballed from the closed Stage-B family or its autopsy. |
| **G17 — Independently justified MDE and decision rule** | The route states a **numeric** decision rule and a **minimum detectable effect / precision target justified independently** of the closed family. See §9. **A route that lacks a numeric decision rule or an independently justified detectable-effect target fails.** |
| **G18 — Two-sided adequacy** | The design has adequate power or precision for **both** a positive and a negative conclusion. A design that can only be inconclusive when the effect is absent fails. |
| **G19 — Edge-event handling** | Split, merge, lost and disappearance each have a declared, exhaustive, non-excluding treatment consistent with §5 attribute 5 and with G7. |
| **G20 — Family separation** | Mechanical qualification, feasibility, independent reproduction and scientific execution are distinct families with distinct authorizations. |
| **G21 — No dual-role family** | No single family serves two of those roles, unless a frozen, non-adaptive design justifies it explicitly and in advance. |
| **G22 — Entity-level preservation** | The primary estimand remains entity-level, or the change of unit is declared prominently and the route does not claim to answer the entity-level question. |
| **G23 — No manufactured entity** | No geometry, substrate feature, intervention or initial condition is chosen because it produces the desired entity or the desired answer. Each design choice has a stated justification that is independent of the hoped-for outcome. |
| **G24 — No survivorship or cadence trapdoor** | There is no path — including via global rejection, sampling schedule, detector emptiness, or acquisition failure — by which outcome-bearing units are removed from the denominator. |
| **G25 — Exact claim-ladder ceiling** | The route states the exact highest rung its complete success would license, and at least one thing that success would not establish. |
| **G26 — Informative negative** | A negative result distinguishes between the route's declared distinct causes of a null. It may never be reported as structural impossibility unless a design capable of supporting that claim is independently justified. |
| **G27 — Bounded resource and termination** | The route declares a hard resource ceiling, a run-count bound, and a termination rule that fires without reference to the observed outcome. |
| **G28 — Owned-pipeline compatibility** | The route is operationally executable through the accepted owned synthetic pipeline contract: mandatory `sampled_frames`, acquisition invoked once per schedule element, persisted-and-re-read evidence, mandatory tracking and lifecycle validation, `COMPLETE` and `AnalysisAccess` gated on internal consistency. |
| **G29 — Frozen import** | The exact import mechanism — module-level import with pinned source hash, or authorized package re-export with successor requalification — is frozen before any execution. Ambiguity is a failure. |
| **G30 — External evidence-root anchoring** | The complete run-family evidence root is externally anchored **before** scientific analysis access. Analysis of unanchored results is forbidden; the mechanism fails closed. |
| **G31 — OP-L3 handled** | Every morphology-dependent endpoint states how OP-L3 is handled, i.e. how a fully re-pinned rewrite of the mutable evidence directory would be detected, given that morphology is not bound into lifecycle semantics. |
| **G32 — No historical confirmation** | No historical result — including 11/64, 0/8 and `M_MINUS` — is used as confirmation, as a prior, or as a threshold source for any route. |

**6.3 Crosswalk (successor gate → gate it strengthens).**

| Successor | Strengthens | Nature of the strengthening |
|---|---|---|
| G13 | G1 | adds the six mandatory attributes and the pre-design timing requirement |
| G14 | G1, G4 | adds the enrolled denominator and its fixing rule |
| G15 | G2 | adds explicit no-replacement and no-top-up |
| G16 | G3 | extends the ban to sample size, priors, effect sizes and bounds |
| G17, G18 | *new* | Architecture 00 had **no** quantitative adequacy gate; this is the gate Route E failed on |
| G19 | G7 | makes edge-event handling explicit per event type |
| G20, G21 | G8 | splits stage separation into separation and non-duality |
| G22 | G1 | protects the unit of analysis specifically |
| G23 | G10 | extends from substrate to geometry, intervention and initial conditions |
| G24 | G2, G11 | names the cadence/emptiness/acquisition trapdoor explicitly |
| G25 | claim ladder | makes the ceiling an admissibility condition, not prose |
| G26 | G9 | requires a *differentiating* negative, not merely a publishable one |
| G27 | *new* | bounded cost and outcome-independent termination |
| G28, G29 | *new* | operational executability against the accepted pipeline |
| G30, G31 | G12 | converts the "software is not evidence" principle into an anchoring obligation |
| G32 | G3 | closes the confirmation channel as well as the tuning channel |

No gate may be waived. If a gate is judged inapplicable to a route, the route must state why, and the
inapplicability claim is itself reviewable and may be rejected by either reviewer.

---

### 7. Denominator and no-replacement rules (frozen)

**D1 — Enrolment.** Each route declares the exact instant of enrolment (allocation of a unit to the
family) and the exact rule that fixes the denominator at that instant. The denominator is fixed before
any outcome for that unit exists.

**D2 — No replacement.** A unit that fails, disappears, splits, merges, is lost, or is mechanically
ineligible after enrolment is **never** replaced, re-seeded, retried, substituted or topped up. Its
slot remains in the denominator with its observed terminal outcome.

**D3 — No outcome-dependent eligibility.** Eligibility criteria are evaluated strictly before
enrolment and strictly without reference to any outcome, including any pilot or preview of the
outcome.

**D4 — Failures are outcomes.** Every post-enrolment terminal state is a recorded outcome or a
competing event. "Excluded", "invalid", "not analysable" and "rerun" are not admissible dispositions
for enrolled units. A unit whose acquisition or mechanical validation fails is reported as such and
remains in the denominator; the route declares in advance whether such units are counted against the
primary endpoint (composite strategy) or handled by a declared alternative strategy.

**D5 — Primary analysis population.** The primary analysis is computed over **all enrolled units**.
Any restricted-population analysis (per-protocol analogue, survivor-conditioned, complete-case) is
secondary, is labelled, and must be reported **alongside** the enrolled-denominator estimate, never
instead of it.

**D6 — Unit fixity.** The unit of analysis is declared once and never changed. Aggregation levels
(entity within world within law within initial-condition class) are declared in advance together with
the exact variance/clustering treatment. Analysing at a level other than the declared unit is a
secondary analysis.

**D7 — Denominator audit.** Every reported quantity states its numerator and its denominator
explicitly, as `k / n`, with `n` traceable to the enrolment ledger. A reported proportion without an
explicit enrolled `n` is inadmissible.

**D8 — No global rejection as a denominator filter.** Global rejection on a local lifecycle violation
(G7) is a **family-level** integrity mechanism, not a unit-level filter. A design in which global
rejection is expected to fire for outcome-bearing units is a survivorship trapdoor and fails G24.

---

### 8. Stopping rule (frozen)

**S1 — No optional stopping.** The family runs to its declared bound. Stopping early because a result
looks good, bad, or interesting is forbidden.

**S2 — Predeclared interim analyses only.** If a route uses an interim analysis, it declares in
advance: the exact interim time points, the exact stopping boundaries, and the exact error-spending
function. Unplanned interim looks invalidate the family.

**S3 — Outcome-independent termination.** The termination rule fires on resources, run count or
wall-clock — quantities that are independent of the observed outcome (G27).

**S4 — Hard resource ceiling.** Each route declares a maximum number of runs, a maximum family
duration, and the action taken when the ceiling is reached with the endpoint still indeterminate:
that action is to report `INDETERMINATE` with the achieved precision, not to extend the family.

**S5 — Program-level stop.** This mission returns `STOP_PROSPECTIVE_READINESS` if no route passes all
gates **and** the affirmative case for stopping is established. A stop is never inferred merely from
the failure of the other routes (see §10.5).

**S6 — Firewall stop.** `STOP_ARCHITECTURE_FIREWALL` is automatic and immediate on any firewall
breach or any scientific execution. It is not discretionary.

---

### 9. Power and minimum-detectable-effect requirements (frozen)

**P1 — Numeric decision rule is mandatory.** Every selectable route states a decision rule in numbers:
the statistic, its estimator, the interval or test procedure, the exact thresholds, and the mapping
from the computed value to `POSITIVE` / `NEGATIVE` / `INDETERMINATE`. **A route that lacks a numeric
decision rule fails G17.**

**P2 — MDE justified independently of the closed family.** The minimum detectable effect (or the
precision target, for an estimation-first design) is justified by one or more of:

- **(a) Decision relevance** — the magnitude below which the program would not change what it does or
  what it claims;
- **(b) A logical or mechanical floor** — a magnitude below which the quantity cannot support the
  intended generalization at all (for example, a replication density that cannot support any
  cross-law statement given the declared number of laws);
- **(c) A declared resource-bounded precision target** — stated as a *precision* (interval
  half-width), explicitly **not** as an expected effect size.

Justification by "what we saw before", by 11/64, by 0/8, by `M_MINUS`, or by any Stage-B-derived
quantity is **forbidden** (G16, G32).

**P3 — Operating characteristics declared.** The route declares the nominal type-I error `α`, the
target power `1 − β` at the MDE, and the direction (one- or two-sided) — all before execution.

**P4 — Negative conclusions require an equivalence or precision criterion.** A negative conclusion is
licensed **only** when a predeclared criterion is met: the confidence interval lies entirely within a
predeclared indifference region, or the achieved precision meets the predeclared target and the point
estimate lies below the predeclared floor. **Non-significance alone never supports a negative claim.**

**P5 — The three-way partition is mandatory and the indeterminate zone is non-empty.** `POSITIVE`,
`NEGATIVE` and `INDETERMINATE` partition the outcome space. A design whose indeterminate zone is empty
has hidden its own inadequacy; a design whose indeterminate zone is the whole space is unpowered. Both
fail G18.

**P6 — Multiplicity.** Where a route has more than one confirmatory endpoint, it declares a
hierarchical/gatekeeping order or a family-wise error-control procedure in advance. Exploratory
endpoints are labelled and are never promoted.

**P7 — Clustering.** Where units are nested (entity within world within law within initial-condition
class), the analysis declares the level at which independence is assumed and the exact method used to
account for the remaining dependence. Assuming independence at a level where it is implausible is an
adequacy failure.

**P8 — Computation discipline.** Power and precision computations are analytic/deterministic, executed
under `/tmp`, consume no historical scientific observation, and record every assumption as a declared
design target with its source. Where an unknown nuisance parameter is required, the route declares the
value used **and** reports the sensitivity of the conclusion across a declared range.

**P9 — Assumption honesty.** Every power statement names the assumption that would most damage it if
wrong, and states the consequence.

---

### 10. Route-selection rule (frozen)

1. **Gates first.** Apply all thirty-two gates of §6 to each route. Every failure is recorded with the
   specific gate and the specific reason. **One fatal gate failure rejects the route.** Gates are never
   averaged, weighted, scored or traded.
2. **Dimensions second, without weighting.** Among admissible routes, compare on the frozen comparison
   dimensions (Architecture 00 §6, twenty-two dimensions, carried forward) together with the
   comparative table mandated by the authorizing brief: preserved scientific question; estimand;
   experimental unit; highest claim rung; positive evidential value; negative evidential value;
   MDE/power adequacy; susceptibility to hidden selection; engineering prerequisites; provenance
   requirements; cost and bounded run count; major alternative explanations; fatal falsifier; every
   gate PASS/FAIL; residual ambiguity. **No weighted total is permitted.** The decision is argued from
   the dimensions, not computed from them.
3. **Rung preference.** Prefer the admissible route with the **highest identifiable claim-ladder rung**
   that does **not** change the unit of analysis away from the entity. A route that changes the unit may
   still be recommended, but only if the change is stated prominently and it is not presented as
   solving the original question.
4. **Tie-break.** Where two admissible routes reach the same rung, prefer the one whose **negative
   result is more informative** (§9 P4, G26).
5. **Route F is not a default.** Architecture 00 §9.5 made Route F the default winner. That rule is
   **superseded** by the authorizing brief of this mission: *"Route F is not selected merely because E
   and G fail. A final stop requires its own affirmative argument."* Route F is therefore evaluated
   affirmatively, on its own expected epistemic value, and passes only if consolidation has **higher**
   expected epistemic value than the best admissible bounded prospective family. This supersession is
   recorded here, in the frozen part, before any route is analysed.
6. **No route admissible.** If no route passes all gates and Route F's affirmative case is
   established, the disposition is `STOP_PROSPECTIVE_READINESS`. If no route passes all gates and Route
   F's affirmative case is **not** established, the disposition is `ARCHITECTURE_REVISE`.
7. **Backup.** At most one backup route may be named. A backup must independently pass all thirty-two
   gates. A route that fails any gate may not be named as a backup "with conditions".
8. **Non-criteria.** Novelty, aesthetic appeal, narrative appeal, the operator's stated interest in any
   route, effort already invested, and the desire for forward motion are **not** selection criteria and
   may not appear in the decision argument.
9. **Selection requires both reviewers.** `PROSPECTIVE_ROUTE_SELECTED` requires PASS from both
   independent adversarial reviewers on the **same** final decision package (§12).

---

### 11. Evidence firewall (frozen)

**11.1 Not opened, enumerated, listed, globbed, grepped, hashed or inspected.** Physics shards or shard
names; manifests; world names or per-world rows or per-world metadata; trajectories; candidate records;
reconstructed checkpoints; failed-autopsy inputs; any `results/` directory; historical scientific
runners; Stage-B source; prospective or `54xxx` namespaces; Kovacs raw material; global project
indexes; project-memory searches.

**11.2 Not executed.** The engine; any scientific runner; a tracker on historical or newly generated
physics; an autopsy; a parameter sweep; a feasibility simulation; a pilot family; a power simulation
using historical observations; seed creation.

**11.3 Access discipline.** Exact Git object paths only. Forbidden: directory listings, globs,
wildcards, `git status`, `git ls-tree -r`, `find`, `rg --files`, broad grep, tree-wide name listings,
archive-on-tree, listing-then-filter.

**11.4 Permitted evidence (exact families).** Aggregate architecture, qualification and human-review
records reached by their exact already-declared paths — Architecture 00 report, decision, roadmap,
review journal and human review; the tracker-repair human review; the lifecycle 01R report,
qualification and human review; the runner-stack requalification report, qualification and human
review; the owned-pipeline report, qualification and human review — plus the exact current generic
interface source files: `edlab/substrates/lattice_bond/future_lifecycle_owned_pipeline.py`,
`edlab/substrates/lattice_bond/future_lifecycle_runner.py`,
`edlab/substrates/lattice_bond/lifecycle.py`, `edlab/substrates/lattice_bond/instrumentation.py`,
`edlab/substrates/lattice_bond/__init__.py`, `pyproject.toml`.

**11.5 Per-world tables are not read even when embedded inside an otherwise-permitted report.** Reading
a permitted aggregate document does not authorize reading a per-world table inside it. Where such a
table is encountered, only the aggregate line already carried forward in §3 is used.

**11.6 No historical world may influence route selection.** A complete read ledger, with section or
byte ranges, is maintained in Part II.

**11.7 Breach handling.** Any breach is `STOP_ARCHITECTURE_FIREWALL`, immediately, without completing
the comparison.

---

### 12. Provenance requirements (frozen)

Every selectable route must be compatible with, and must explicitly address, all four of the
following. These are admissibility conditions, not roadmap items.

**V1 — Evidence-root anchoring (G30).** The design must:

1. seal the complete run-family root digest **before** analysis;
2. include the raw acquired-frame evidence required for every morphology-dependent endpoint;
3. commit the root **outside** the mutable run directory;
4. require evidence of successful anchoring **before** scientific analysis access is granted;
5. support a public immutable or append-only method **without requiring a local secret** (fact 3.4.25);
6. provide a fallback if the agent environment cannot push because of proxy 403;
7. **fail closed** — an unanchored family is not analysed.

A primary operational anchoring route and exactly one fallback are chosen in Part II. Anchoring is not
performed in this mission.

**V2 — Frozen import (G29).** Exactly one of the following is frozen in Part II, without ambiguity:
an exact module-level import pinned by source hash, or a separately authorized package re-export with
successor requalification. The exact module import is preferred where it is scientifically and
operationally sufficient; an additional infrastructure mission is not created merely for import
ergonomics. The current state — module-level API only, no package re-export (fact 3.4.23) — is the
baseline against which this choice is made.

**V3 — OP-L3 handling (G31).** Every morphology-dependent endpoint states how a complete, internally
consistent re-pinning of the mutable evidence directory would be detected. Since morphology is not
bound into lifecycle semantics (fact 3.4.24), an endpoint that depends on area, mass, centroid, pixel
set or radius of gyration requires the anchoring of V1 to cover the **raw acquired frames**, not only
the derived records. A route that leaves a morphology-dependent endpoint unanchored fails.

**V4 — Reproducibility bindings are not authority.** Acquisition-source identity, timestamps and
physical elapsed time are reproducibility bindings, not authority (fact 3.4.26). No route may rest a
scientific conclusion on unauthenticated wall-clock time or on source identity alone.

---

### 13. Review rules (frozen)

**R1 — Two independent adversarial reviewers**, launched only **after** the candidate comparison and a
written preliminary decision exist.

- **Reviewer A — scientific design and falsifiability.** Attacks estimands; power and MDE;
  denominators; equivalence claims; alternative hypotheses; the claim ladder; and whether a negative
  result would truly be informative.
- **Reviewer B — selection bias and provenance.** Attacks use of closed-family knowledge; hidden
  tuning; eligibility and replacement; survivorship; initial-condition dependence; symmetry leakage;
  niche and shared-field confounding; evidence-root anchoring; OP-L3; and whether the chosen route is
  genuinely executable.

**R2 — Reviewers may reject the preferred route.** A reviewer verdict is not advisory.

**R3 — Findings are applied additively.** A valid finding is fixed by addition or by withdrawal of the
affected claim — never by weakening a previously stated commitment, and never by deleting a limitation
in order to pass.

**R4 — Withdrawal over patching.** A claim shown to be false or unfalsifiable is **withdrawn**, not
reworded. Withdrawals are recorded in the review journal with the original text.

**R5 — Targeted re-review.** After corrections, both reviewers re-review. `PROSPECTIVE_ROUTE_SELECTED`
requires **PASS from both reviewers on the same final decision package**.

**R6 — Honest failure.** If no route passes after review, the disposition is `ARCHITECTURE_REVISE` or
`STOP_PROSPECTIVE_READINESS`, argued honestly. Selecting a route that a reviewer rejected is
forbidden.

**R7 — Full disclosure.** The review journal records every finding, including those judged invalid,
with the reason for the judgement; every correction; every withdrawal; and the exact package hash each
verdict was issued against.

---

### 14. Terminal-disposition rules (frozen)

Exactly one of:

| Disposition | Meaning and precondition |
|---|---|
| `PROSPECTIVE_ROUTE_SELECTED` | Exactly one primary route named; at most one backup, itself passing all thirty-two gates; both reviewers PASS the same final package. Authorizes **no** implementation and **no** scientific execution. |
| `ARCHITECTURE_REVISE` | No route is selectable on the present evidence, and the affirmative case for stopping is not established; or a required deviation from Part I is discovered; or code or data would be needed to complete the analysis. |
| `STOP_PROSPECTIVE_READINESS` | No route passes all gates **and** Route F's affirmative case is established on its own merits (§10.5). |
| `STOP_ARCHITECTURE_FIREWALL` | Automatic on any firewall breach or any scientific execution (§11.7). Not discretionary. |

**T1.** `PROSPECTIVE_ROUTE_SELECTED` means only that a design route is recommended for later human
review. It authorizes no implementation, no preregistration, no seed allocation and no scientific
execution.

**T2.** After any terminal disposition, the **only** authorized next action is **human review of
Architecture 01**.

**T3.** A disposition that names a route must also name the exact next implementation/preregistration
mission, without beginning it.

**T4.** No disposition may be reached without Part I being an unmodified byte-exact prefix of the
final report. If Part I would have to change, the disposition is `ARCHITECTURE_REVISE`.

---

### 15. Allowed writes (frozen)

Exactly four new documents. No existing file — source, test, configuration or document — is modified.

1. `docs/individuation/FUTURE_PROSPECTIVE_READINESS_ARCHITECTURE_01_REPORT.md`
2. `docs/individuation/FUTURE_PROSPECTIVE_READINESS_ARCHITECTURE_01_DECISION.json`
3. `docs/individuation/FUTURE_PROSPECTIVE_READINESS_ARCHITECTURE_01_ROADMAP.md`
4. `docs/individuation/FUTURE_PROSPECTIVE_READINESS_ARCHITECTURE_01_REVIEW_JOURNAL.md`

Checkpoints: (1) frozen Part I — this commit; (2) candidate routes and preliminary decision;
(3) reviewer corrections; (4) final sealed decision package.

---

*Part II (read ledger, Route E design, Route G design, Route F affirmative case, comparative decision
table, evidence-root anchoring decision, frozen import decision, preliminary decision, independent
adversarial reviews, corrections, final decision and terminal disposition) is appended after this
protocol is committed. This file's state at the pre-analysis commit is the frozen reference.*
