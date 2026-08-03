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

## Part II — READ LEDGER, ROUTE DESIGNS, COMPARISON, PRELIMINARY DECISION

*Part I above is frozen. This part is appended without altering a byte of it.*

### II.0 Read ledger

Every read performed for this mission, by exact path. No directory listing, glob, wildcard,
`git status`, `git ls-tree -r`, `find`, `rg --files`, broad grep, tree-wide listing, archive-on-tree
or listing-then-filter was used at any point.

| # | Object | Extent read | Purpose |
|---|---|---|---|
| 1 | `d293eaf994fa77d4c63fbf14f72d10da377a523d` (commit) | commit header only | ancestry, authorization |
| 2 | `10034eaa0bd8f2c32278959db96ae0095f737298` (commit) | commit header only | parent verification |
| 3 | `refs/heads/main` | ref value only | preservation record |
| 4 | `docs/individuation/FUTURE_PROSPECTIVE_READINESS_ARCHITECTURE_00_REPORT.md` | bytes 0–12,729 (frozen Part I), sha256 `819cb49cc09ec72d46aace4eb4599f799a575c1f8e7ca6c6577bb4907830df3d` | carry forward gates, ladder, firewall, selection rule |
| 5 | `docs/individuation/FUTURE_PROSPECTIVE_READINESS_ARCHITECTURE_00_DECISION.json` | full (24,427 B) | terminal disposition, route dispositions |
| 6 | `docs/individuation/FUTURE_PROSPECTIVE_READINESS_ARCHITECTURE_00_ROADMAP.md` | full (8,234 B) | prior roadmap |
| 7 | `docs/individuation/FUTURE_PROSPECTIVE_READINESS_ARCHITECTURE_00_REVIEW_JOURNAL.md` | full (18,056 B) | reviewer findings, Route E failure reasons |
| 8 | `docs/individuation/FUTURE_PROSPECTIVE_READINESS_ARCHITECTURE_00_HUMAN_REVIEW.md` | full (10,528 B) | accepted supersessions |
| 9 | tracker-repair human review; lifecycle 01R report / qualification / human review; runner-stack requalification report / qualification / human review; owned-pipeline report / qualification / human review | aggregate dispositions and limitation registers only | facts 3.3.17–3.3.22, 3.4.23–3.4.26 |
| 10 | `edlab/substrates/lattice_bond/lifecycle.py` | structural read: `TerminalState`, `_KNOWN_EVENT_KINDS`, `_ONSET_EVENT_KINDS`, `_TERMINAL_EVENT_STATES`, `_ERROR_PRECEDENCE`, `LifecycleTerminalRecord`, `LifecycleRunClosure` | competing-risk scaffold for G4/G7/G19 |
| 11 | `edlab/substrates/lattice_bond/instrumentation.py` | structural read: `EventKind`, `Regime`, `DetectorSpec`, `DetectedComponent`, `TrackerSpec`, `TrackPoint`, `TrackRecord`, `TrackEvent`, `TrackingResult`, `ComponentDiagnostics`, `TrackMetrics`, `TrackObservation`, `RegimeThresholds`, `WorldMetrics`, `advance_passive_tracer` signature | available observables, turnover-evidence channel, threshold inventory |
| 12 | `edlab/substrates/lattice_bond/future_lifecycle_owned_pipeline.py` | public API and limitation register (carried forward from the accepted owned-pipeline mission) | G28 compatibility |

**Not read in this mission:** `edlab/substrates/lattice_bond/engine.py` (not on the permitted list);
any per-world table, even where embedded in an otherwise-permitted document; any shard, manifest,
world name, trajectory, candidate, checkpoint, autopsy input, `results/` directory, historical
scientific runner, Stage-B source, prospective namespace, Kovacs material or global index.

**Not executed:** engine, tracker, simulation, sweep, pilot family, seed creation, or any power
simulation consuming historical observations.

**Computation performed:** one deterministic analytic script under `/tmp`
(`/tmp/arch01_power.py`), consuming only design targets declared in this document — Clopper–Pearson
intervals, binomial power, and normal-approximation equivalence sample sizes. It reads no data file
of any kind. Its outputs are reproduced inline below.

---

### II.1 Route E — replication density (revised)

#### II.1.1 Why Route E was returned, and what changed

Architecture 00 returned Route E for reframing on two independent grounds, both recorded in its
review journal:

- **G11 / cadence (blocker B-F1).** The rejection of the empty-right-detector-frame path was a
  *conjunction* — empty right frame **and** non-unit cadence. A prospectively declared schedule cannot
  control frame emptiness, so every world in which the entity disappeared was routed to *global*
  rejection. Disappearance is precisely the outcome an honest denominator must retain. Architecture 00
  recorded this as "the survivorship trapdoor is reopened through the cadence door".
- **G1 / estimand (findings A1, A2, A6).** Route E's hypothesis `H_X` was that persistence and
  material turnover are *mutually exclusive*. That hypothesis is falsified eleven times by the very
  record Route E cited (fact 3.1.2). Route E also declared no sampling density, no minimum detectable
  measure and no decision rule, which made its `EXCLUSION_CONFIRMED` arm an unpowered null.

Both grounds are now addressable. The cadence blocker is **closed** by the tracker repair, the
lifecycle 01R requalification (mandatory `sampled_frames`, no schedule-free path), the runner-stack
requalification and the accepted owned pipeline (facts 3.3.17–3.3.20). The estimand ground is
addressed by abandoning `H_X` entirely and replacing it with a prevalence question (C3).

#### II.1.2 Question and estimand

**Q-E.** Under a newly and prospectively generated design, at what rate does the conjunction of
*persistence* and *independently verified complete material turnover* reproduce across laws,
replicates and initial-condition classes?

**Primary estimand (six attributes, per §5).**

1. **Population.** Laws drawn i.i.d. from a declared sampling frame `F`: the set of substrate law
   configurations that the engine's own validation accepts, with each free parameter assigned a
   declared distribution over its *mechanically admissible* range. Bounds are justified by mechanical
   admissibility alone. Draws come from a single committed PRNG stream whose seed is published in the
   preregistration before any run. The exact field-by-field enumeration of the law space is deferred
   to the preregistration mission, which is authorized to read the engine source under its own
   declared allowlist; this architecture freezes only the *rule* by which the frame may be defined.
2. **Unit of analysis.** The **law**. This is a declared change of unit away from the entity (G22);
   see §II.1.9.
3. **Condition.** None. Route E is observational over the law frame: no intervention exists and none
   is introduced.
4. **Outcome.** Binary per law: *majority-instantiating in both initial-condition classes* — see
   §II.1.4 for the world-level primitive and §II.1.5 for the law-level criterion.
5. **Intercurrent-event strategy.** Composite/treatment-policy. Every enrolled world produces exactly
   one of the five lifecycle terminal states per track (`DISSOLVED_DETECTED_TRACK`,
   `SPLIT_INTO_TRACKS`, `MERGED_INTO_TRACK`, `UNRESOLVED_HANDOFF`, `RIGHT_CENSORED_AT_HORIZON`). A
   world in which no track satisfies the conjunction — for any reason, including dissolution, split,
   merge, unresolved handoff, acquisition failure or mechanical ineligibility — scores **0**. Nothing
   is excluded. See §II.1.6.
6. **Summary measure.** `Δ` = the proportion of enrolled laws scoring 1, over the enrolled
   denominator `L`, with a two-sided 95% Clopper–Pearson interval.

#### II.1.3 Enrolment, allocation and denominator

| Element | Value | Note |
|---|---|---|
| Laws enrolled, `L` | **60** | fixed before any run |
| Initial-condition classes, `C` | **2**, crossed within law | each law is run in both classes |
| Replicates per law × class, `R` | **6** | independent seeds from the committed stream |
| Enrolled worlds, `N = L·C·R` | **720** | fixed at allocation |

- **Pre-enrolment eligibility.** A drawn law that the engine's own validator rejects is discarded
  **before** enrolment and replaced from the same PRNG stream. This is mechanical validity only, is
  blind to every outcome, and occurs before the denominator is fixed. The number of pre-enrolment
  mechanical rejections is reported.
- **Post-enrolment.** No replacement, no retry, no re-seeding, no top-up, ever (D2). All 720 worlds
  appear in the denominator with their observed terminal outcomes.
- **Initial-condition classes** are defined by a mechanical property of the initial state, disjoint,
  each generated by a declared procedure, fixed before any draw, and defined without reference to any
  outcome. Their exact definitions are deferred to preregistration under the same constraint as the
  law frame.

#### II.1.4 The world-level primitive: the conjunction, with no free empirical thresholds

This is the core of the revision. Architecture 00's regime classifier exposes **seven** free numeric
thresholds (`RegimeThresholds`: `min_persistence_frames`, `max_area_fraction`,
`min_bounded_fraction`, `min_activity_per_mass`, `min_energy_throughput_per_mass`,
`min_turnover_fraction`, `min_post_turnover_frames`). Every one of them would, if inherited, be a
G3/G16 violation, because there is no admissible source for their values other than the closed family.
Route E therefore does **not** use the regime classifier. It defines the conjunction directly, using
only booleans, self-normalisation and logical floors.

A world scores **1** if and only if at least one track `t` satisfies all four of the following.

- **E-1 — Entity-like (boolean, no threshold).** At every sampled frame at which `t` is observed, its
  detected component is non-percolating and does not wrap the torus in either axis
  (`percolated == False`, `wraps_y == False`, `wraps_x == False`). These are booleans produced by the
  detector; no magnitude is compared to any number.
- **E-2 — Complete verified turnover (logical floor, not an empirical threshold).** A labelled matter
  cohort is initialised on `t`'s component at `t`'s first observed frame and advected by
  `advance_passive_tracer` through the engine's own gross matter flows. Let `T_complete(t)` be the
  first sampled frame at which the cohort mass remaining inside `t`'s component falls to `≤ ε` of the
  component mass, where **`ε` is the declared numerical tolerance of the tracer integration, not an
  empirical threshold**. "Turnover" therefore means *complete replacement of the original material*,
  which is a logical endpoint, not a tunable fraction. If the cohort never reaches this state before
  the horizon, `T_complete(t)` is undefined and E-2 fails.
- **E-3 — Persistence beyond one full replacement (self-normalising).** `t` is continuously observed
  from its first observed frame to at least frame `2 · T_complete(t)`, measured **in that track's own
  units**. The multiplier **2** is the smallest integer strictly greater than 1 and is declared as a
  logical floor: persistence must outlast one complete material replacement. No cross-world, cross-law
  or historical timescale enters.
- **E-4 — Admissible terminal state.** `t`'s lifecycle terminal state is `RIGHT_CENSORED_AT_HORIZON`,
  i.e. it was still present when the declared horizon was reached. Tracks terminating in
  `DISSOLVED_DETECTED_TRACK`, `SPLIT_INTO_TRACKS`, `MERGED_INTO_TRACK` or `UNRESOLVED_HANDOFF` before
  satisfying E-3 do **not** satisfy the conjunction — and their worlds score 0 rather than being
  removed.

Free numeric constants in the entire primitive: **`ε` (numerical tolerance) and the integer 2**. No
other number is compared to any observable. This is the concrete answer to G3/G16 and it is the single
largest difference between this Route E and the one Architecture 00 rejected.

#### II.1.5 Law-level criterion and the prespecified density curve

Within each law × IC-class cell (`R = 6` worlds), let `k_cell` be the number of worlds scoring 1.

- **Cell positive** iff `k_cell ≥ 4` — a *strict majority* of the cell. Majority is the canonical
  prior-free split ("more likely than not") and is justified by decision relevance, not by data
  (P2a): a law that instantiates the conjunction less than half the time cannot provision a downstream
  entity-level family within any bounded budget.
- **Law positive** iff **both** IC-class cells are positive.
- `Δ̂ = (number of positive laws) / 60`.

The law-level criterion is an *operational* definition, and its operating characteristics are
prespecified rather than hidden. For a cell whose true per-world success probability is `p`:

| true `p` | P(cell positive) | P(law positive) = P(cell)² |
|---|---|---|
| 0.10 | 0.00127 | 0.0000016 |
| 0.30 | 0.0705 | 0.00497 |
| 0.50 | 0.3438 | 0.1182 |
| 0.70 | 0.7443 | 0.5540 |
| 0.90 | 0.9842 | 0.9686 |

`Δ` is therefore explicitly the density of **majority-instantiating** laws under `R = 6`, not the
latent proportion of laws with `p > 1/2`. The table is reported with the result so that the
attenuation is visible rather than implicit.

**Prespecified density curve.** In addition to the primary `Δ` at the majority threshold, the full
monotone curve `Δ(t)` for `t ∈ {1/6, 2/6, 3/6, 4/6, 5/6, 6/6}` is reported, together with `Δ_any`
(≥1 world positive in each class) and `Δ_all` (6/6 in each class). **All** thresholds are reported;
**only** `t = 4/6` is confirmatory. This removes any possibility of post-hoc threshold selection while
retaining the information.

#### II.1.6 Edge events, competing risks and the absence of a trapdoor

The lifecycle contract assigns **exactly one** terminal state per track from an exhaustive set of
five, and its global-rejection mechanism fires only on *contract* violations — schema, schedule,
digest, duplicate-id, out-of-schedule point and similar (`_ERROR_PRECEDENCE`). This distinction is
what closes the Architecture-00 trapdoor:

- `DISSOLVED_DETECTED_TRACK`, `SPLIT_INTO_TRACKS`, `MERGED_INTO_TRACK`, `UNRESOLVED_HANDOFF`,
  `RIGHT_CENSORED_AT_HORIZON` are **outcomes**. They never remove a world from the denominator.
- Global rejection is reserved for **software-integrity faults**. A family in which global rejection
  fires is not analysed at all; it is a failed family, reported as such, and not silently pruned.
- Disappearance at non-unit cadence is now an ordinary `DISSOLVED_DETECTED_TRACK` outcome, not a
  global rejection (fact 3.3.18). This is the specific repair that makes Route E admissible.
- Every terminal state is reported as a count over the enrolled 720 worlds, so that a null can be
  read against the full competing-risk profile.

#### II.1.7 Decision rule (numeric)

With `Δ₀ = 0.10`, `L = 60`, two-sided 95% Clopper–Pearson:

| Decision | Rule | Realised region |
|---|---|---|
| `POSITIVE` | CP lower bound on `Δ` **>** `Δ₀` | `k ≥ 12` (CP lower at 12/60 = 0.1078) |
| `NEGATIVE` | CP upper bound on `Δ` **<** `Δ₀` | `k ≤ 1` (CP upper at 1/60 = 0.0894) |
| `INDETERMINATE` | otherwise | `2 ≤ k ≤ 11` |

The three regions partition the outcome space and the indeterminate region is non-empty (P5).

**Justification of `Δ₀ = 0.10`, independent of the closed family (P2).** Two independent arguments
converge:

- *(P2a, decision relevance.)* Below one law in ten, the conjunction is not a reproducible property of
  the law frame in any sense that would change what the program does next.
- *(P2b, logical/provisioning floor.)* A downstream entity-level family needs at least one
  instantiating law. Obtaining one with 95% assurance by screening `L'` laws requires
  `Δ ≥ 1 − 0.05^(1/L')`. For `L' = 30`, that is `Δ ≥ 0.0950`; for `L' = 20`, `Δ ≥ 0.1391`. `Δ₀ = 0.10`
  sits at the boundary of a 30-law screening budget, which is the largest screening budget this
  program can declare while remaining bounded.

Neither argument uses 11/64, 0/8, `M_MINUS`, or any other closed-family quantity (G16, G32).

#### II.1.8 Power, MDE and two-sided adequacy

Computed analytically in `/tmp/arch01_power.py` from the design targets above and nothing else.

| Quantity | Value |
|---|---|
| Type I of the `POSITIVE` arm at the boundary `Δ = Δ₀` | **0.0146** |
| **MDE at 80% power** | **`Δ = 0.240`** (power 0.808) |
| Power at `Δ = 0.25` | 0.852 |
| Power at `Δ = 0.30` | 0.971 |
| Power at `Δ = 0.35` | 0.996 |
| Power at `Δ = 0.20` | 0.551 (declared inadequate; falls in the indeterminate design region) |
| `NEGATIVE` arm | attainable at `k ∈ {0, 1}`; CP upper `= 0.0596` and `0.0894` |
| Worst-case precision (half-width of the 95% CP interval) | ≤ 0.163 across `k ∈ [0, 60]` |

The design is adequate in **both** directions (G18): it can declare `POSITIVE` at a true density of
0.24 or above with ≥80% power, and it can declare `NEGATIVE` — with a genuine interval criterion, not
a non-significance — whenever at most one law in sixty is majority-instantiating.

**Assumption most damaging if wrong (P9).** The horizon `H`. E-2 and E-3 require the run to be long
enough for a track to reach complete turnover and then survive twice that long. If `H` is too short,
every world is right-censored before `T_complete` and `Δ̂ = 0` for a purely mechanical reason. This is
handled in §II.1.10 and it is the single largest threat to the interpretation of a null.

#### II.1.9 Claim ceiling

Complete success of Route E establishes, at most:

> Within the declared law frame `F`, the conjunction of entity-like persistence and complete verified
> material turnover is majority-instantiated by a proportion `Δ` of laws in both declared
> initial-condition classes, with the stated interval.

That is **claim-ladder rung 3**, at the **law** level, not the entity level. Route E does **not**
establish rung 4, 5, 6 or 7. It does **not** establish that any entity owns any state, that entities
are separately addressable, or that individuality exists. It is a **prevalence and provisioning**
result: it tells the program whether the substrate can supply the entities that any entity-level
experiment would need, and at what rate.

Per G22 and §5 C2, the change of unit from entity to law is declared here, prominently, and Route E is
**not** presented as answering the target question of §2.

#### II.1.10 Informative negative (G26)

A null must distinguish four causes. Each has a prespecified discriminator, declared before execution:

| Cause of a null | Prespecified discriminator |
|---|---|
| **Low replication density** (the scientific answer) | `k ≤ 1`, with the horizon check and the eligibility check below both passing |
| **Initial-condition dependence** | `Δ_any-class − Δ_both-class` and the paired per-class counts, compared by an exact McNemar test on the 60 laws; a large excess of single-class laws indicates IC dependence rather than absence |
| **Mechanical ineligibility** | if more than 50% of the 720 enrolled worlds never produce a non-percolating, non-wrapping detected component at any sampled frame, the family reports `INDETERMINATE — MECHANICAL_INELIGIBILITY` |
| **Inadequate horizon** | if more than 50% of enrolled worlds contain no track reaching `T_complete` before the horizon, the family reports `INDETERMINATE — INADEQUATE_HORIZON` |
| **Inadequate precision** | `2 ≤ k ≤ 11` → `INDETERMINATE` |

The two 50% figures are majority floors, declared in advance, not fitted.

**Structural impossibility is never claimed.** A `NEGATIVE` result is reported as *"the conjunction is
majority-instantiated by fewer than one law in ten of the declared frame"*, and explicitly not as
*"persistence with turnover is impossible"* — a claim this design cannot support and which fact 3.1.6
forbids.

#### II.1.11 Horizon calibration — a separate, endpoint-blind family

`H` cannot be set from the closed family (G16) and cannot be guessed. It is set by a **separate**
mechanical family (G20/G21):

- draws laws from `F` using a **disjoint block** of the committed PRNG stream;
- those laws are **discarded** and may never be enrolled in the scientific family;
- reads **only** the distribution of `T_complete`; the conjunction endpoint, E-3, E-4 and every
  law-level criterion are not computed and not looked at;
- sets `H = 4 · q₉₀(T_complete)`, where the multiplier 4 is a declared logical margin (twice the
  factor-2 requirement of E-3) and `q₉₀` is the 90th percentile in the calibration draw;
- also measures per-run wall-clock cost, which feeds the resource ceiling below.

This is a nuisance-parameter pilot, blind to the endpoint, on discarded units. It is not a feasibility
family, not a scientific family, and produces no scientific claim.

#### II.1.12 Resource ceiling and termination (G27)

- Hard enrolled ceiling: **720 worlds**, plus the calibration draw declared in the preregistration.
- Hard wall-clock ceiling: declared in the preregistration from the calibration family's measured
  per-run cost.
- **Fail-closed authorisation:** if the projected cost of 720 worlds exceeds the declared wall-clock
  ceiling, the scientific family is **not authorised**. The design is **not** shrunk to fit, because
  shrinking `L` after seeing the cost would compromise the declared operating characteristics.
- Termination fires on run count and wall-clock only — quantities independent of the observed outcome
  (S3).
- No interim analysis. The family runs to completion and is analysed once (S1, S2).

#### II.1.13 Independent reproduction stage (G8/G20)

Before any downstream family relies on `Δ`, a separate reproduction family of `L₂ = 20` laws is drawn
from `F` using a third disjoint PRNG block and run by the same code at the same pinned source hash.
Reproduction succeeds if the reproduction family's `Δ̂₂` interval is consistent with the primary
`POSITIVE`/`NEGATIVE` call. This family is authorised separately and is not part of the primary
family's denominator.

#### II.1.14 Engineering prerequisite

E-2 requires a **labelled matter cohort** advected by the engine's gross matter flows. The accepted
owned pipeline persists boolean matter frames only (`_canonical_frame_bytes` canonicalises to
`np.bool_`). A boolean mask cannot distinguish "same material" from "replaced material", so **turnover
evidence cannot be reconstructed from the currently persisted evidence**.

Route E therefore has exactly one engineering prerequisite: a **turnover-evidence channel** — a
second, float-valued cohort field persisted per sampled frame, re-read like the boolean frames, bound
into the acquisition ledger and the completion digest, and covered by the evidence root.

This preserves every property of the accepted contract (mandatory `sampled_frames`, acquisition
invoked once per schedule element, persisted-and-re-read evidence, mandatory tracking and lifecycle
validation, `COMPLETE`/`AnalysisAccess` gated on internal consistency) and adds one channel. It is
one bounded engineering mission with its own qualification and human review — not a governance
mission, and not an open-ended programme.

---

### II.2 Route G — symmetry-broken internal convention

Route G is designed here in full, as required, and then evaluated against the frozen gates. The design
is given in complete statistical detail; where a substrate fact is missing, that is stated exactly
rather than papered over.

#### II.2.1 Question and claim ceiling

**Q-G.** Can nominally identical entities in a shared symmetric environment independently select
between two physically equivalent internal conventions, preserve the selected convention through
independently verified material turnover, and exhibit entity-local causal ownership of that
convention?

**Claim ceiling (declared before design, per G25).** Complete Route-G success establishes at most: a
**low-dimensional entity-local causal convention**; **prospective symmetry breaking**; **persistence
through verified turnover**; and **limited local ownership under the tested interventions**. It does
**not** establish rich individuality, autonomy, genome, reproduction, or open-ended identity. Route G
would reach **rung 6** for a single low-dimensional binary state — the rung that matters — and would
not reach rung 7.

#### II.2.2 Endpoint hierarchy (fixed-sequence gatekeeping)

Seven hierarchical endpoints, tested in fixed order at α = 0.05 one-sided (or 0.05 for the
equivalence pairs). Under a fixed sequence no multiplicity adjustment is required; the sequence stops
at the first non-rejection and every later endpoint becomes exploratory.

| # | Endpoint | Statistical form | Design target |
|---|---|---|---|
| **H1** | **Emergence** — the convention is undefined before formation and both signs occur prospectively | exact binomial that both signs are observed | ≥1 of each sign among enrolled entities |
| **H2** | **Symmetry** — no imposed sign predicts the selected sign | TOST equivalence of the population sign frequency to 1/2 | margin `δ_sym = 0.10` → **n ≈ 214 entities** |
| **H3** | **Independence** — co-housed entities select independently | TOST equivalence of within-pair sign concordance to 1/2 | margin `δ_ind = 0.10` → **n ≈ 214 pairs** |
| **H4** | **Persistence through turnover** — the sign is retained across complete verified turnover | one-sided binomial, `H₀: p ≤ 0.5` vs `p = 0.75` | **n ≈ 31 entities that reach complete turnover** |
| **H5** | **Local addressability** — a targeted intervention changes the target and not the co-housed partner | difference-in-differences, partner as internal control, with predeclared sham and off-target arms | not computable (see §II.2.5) |
| **H6** | **Environmental equalisation** — the sign survives equalising or swapping admissible environmental conditions | paired retention rate under swap vs no-swap | not computable |
| **H7** | **Ownership** — entity-local state is preferred over niche, partner-coupled, shared-field and imposed-detector models | predeclared model comparison over the five competing causal models | not computable |

`δ_sym` and `δ_ind` are justified by decision relevance: a systematic deviation larger than 10 points
would be large enough on its own to explain any downstream ownership result, so anything smaller is
not decision-relevant. Sample sizes are from the normal approximation at α = 0.05, power 0.90
(`/tmp/arch01_power.py`).

**Analysis invariance.** All analyses are required to be invariant under global sign exchange: the
label map `(+ ↔ −)` applied to every entity must leave every test statistic unchanged. Label
assignment is frozen before any outcome is read.

#### II.2.3 Operational test battery

- **Symmetry.** The two convention labels must be physically equivalent before selection: no imposed
  sign, orientation, detector convention or environmental cue may predict the selected sign. Required
  evidence: (i) a demonstrated symmetry of the dynamics mapping one convention onto the other;
  (ii) a detector/readout whose own convention is randomised and shown not to predict the outcome;
  (iii) sign-exchange invariance of the analysis code, tested mechanically.
- **Emergence.** The convention must be absent or undefined before formation; selection must occur
  without a signed external instruction; both signs must occur prospectively; and a *population*
  imbalance must not be reported as an *entity-level* convention.
- **Independence.** Co-housed entities in the same environment must be able to select independently.
  Conditional dependence between their choices is quantified, and shared-field, common-niche and
  partner-coupling explanations are each given an explicit alternative model. Non-significance is
  never read as independence: an equivalence margin is used (C7).
- **Persistence and turnover.** The convention must persist across predeclared **complete verified**
  turnover, measured by the same cohort-tracer channel as Route E's E-2 — i.e. **independently of the
  convention readout** (G6, C8). Disappearance, split, merge and loss remain outcomes, never
  exclusions; no survivor-only denominator is permitted.
- **Local addressability.** An intervention must perturb or read one entity without directly setting
  the other. Sham and off-target arms are predeclared. The effect on the targeted entity is
  distinguished from shared-environment change by the partner-as-control contrast.
- **Environmental equalisation.** Equalising or swapping admissible environmental conditions must not
  erase an entity-local convention. Niche inheritance and shared-field memory are explicit alternative
  hypotheses with their own predicted signatures.
- **Ownership.** Five competing causal models are predeclared — entity-local state, niche state,
  partner-coupled state, shared-field state, imposed detector/coordinate convention — each with the
  intervention that discriminates it and the exact evidence pattern required to prefer entity-local
  ownership.

#### II.2.4 What is missing, exactly

Route G's statistical skeleton above is complete. Its **measurement** is not, and cannot be made so
within this mission:

1. **No convention observable is defined.** Estimand attribute 4 requires "the exact measured quantity
   and the exact procedure that produces it from pipeline evidence". The observables available from
   the permitted interface are geometric (`area`, `mass`, `centroid_y`, `centroid_x`,
   `radius_gyration`, `cells`, `wraps_y`, `wraps_x`) and diagnostic (`matter_internal_gross`,
   `matter_in_gross`, `matter_out_gross`, `resource_boundary_exchange`, `bond_work_throughput`,
   `mean_internal_bond`, `boundary_face_count`). **None of them is a signed quantity with a symmetry
   partner.** A plausible candidate — the sign of a component-local circulation built from the
   directed gross-flow fields — would require establishing that the dynamics actually possesses the
   corresponding reflection symmetry and that the circulation is non-degenerate. Establishing either
   requires reading the engine source (not permitted in this mission) or executing the engine (not
   permitted in any architecture mission). Declaring the observable *conditionally* would violate G13
   and would open exactly the G23 door — choosing the observable after looking at what produces the
   desired entity.
2. **No intervention algebra exists.** `run_owned_future_pipeline` has no intervention parameter of
   any kind. H5, H6 and H7 — the three endpoints that carry rungs 5 and 6 — cannot be executed, sized
   or even fully specified. Fact 3.2.14 additionally records that local, environmental, redundant and
   relational ownership were *not identifiable* under the previous intervention algebra, so this is
   not a matter of wiring an existing capability.
3. **No multi-entity, environment-symmetric world design exists.** Co-housing, environment
   equalisation and environment swapping are all new substrate-level capabilities.
4. **The enrolled sample size is not computable.** H4 needs ≈31 entities that reach **complete
   verified turnover**. The required enrolment is `31 / P(an enrolled entity reaches complete
   turnover)`. That probability is, exactly, the quantity Route E is designed to estimate. Its
   plausible range spans an order of magnitude in enrolment:

   | if P(complete turnover) were | required enrolment |
   |---|---|
   | 0.50 | ≈ 61 entities |
   | 0.25 | ≈ 121 entities |
   | 0.10 | ≈ 304 entities |
   | 0.05 | ≈ 607 entities |

   Using 11/64 to fill that number in would be a direct G16/G32 violation. There is no other source.

5. **A null would be confounded.** If Route G ran now and found no convention, the result could not be
   distinguished from "there were no entities that persisted through turnover to carry a convention" —
   which is precisely Q-E, unanswered. That is a G26 failure by construction.

#### II.2.5 Route G is logically downstream of Route E

Points 4 and 5 are not incidental. Route G's persistence-through-turnover endpoint *presupposes*
entities that persist through turnover; its enrolment arithmetic *is* Route E's estimand; and its null
is *uninterpretable* until Route E's question is answered. Route G is therefore not a competitor to
Route E at this moment — it is Route E's **successor question**. That is a structural relation, not a
preference.

---

### II.3 Route F — stop and consolidate (evaluated affirmatively)

Route F is evaluated on its own merits, not as the residue of the other two (§10.5).

- **What exact unresolved question would remain?** Q-E and Q-G, both. In particular the program would
  stop without knowing whether its substrate can instantiate persistence-with-turnover at any
  reproducible rate — the prerequisite for every entity-level question it has ever posed.
- **Why could neither E nor G answer it credibly?** This is where Route F's case fails. Route G indeed
  cannot answer its question now (§II.2). But **Route E can answer Q-E credibly**: it has an exact
  prospective estimand, an enrolled denominator of 720 worlds fixed before any run, a conjunction
  primitive with two declared constants and no empirical thresholds, a numeric decision rule, an MDE
  of 0.240 at 80% power, an attainable interval-based negative arm, a competing-risk-honest denominator
  and a prespecified discrimination among the causes of a null. The premise of Route F's affirmative
  case is therefore false.
- **What knowledge is already secure?** That low-dimensional causal experience memory exists; that it
  is not sufficient for individuality; that persistence and turnover are not known to be mutually
  exclusive and co-occurred in 11 of 64 closed worlds; that 0 of 8 laws met the closed family's
  two-of-four criterion in both IC classes; that the closed family showed inadequate replication
  density with IC dependence and did not show structural impossibility; and that the synthetic
  pipeline is mechanically qualified but is not scientific evidence.
- **What claims must be abandoned?** The mutual-exclusivity hypothesis `H_X` (falsified, C3); any
  reading of `DEV_FEASIBILITY_FAIL` as absence of individuality; any use of `M_MINUS` as Route-G
  confirmation; and "there is no repair without a secret" (fact 3.4.25).
- **Temporary or final?** Under Route F's own logic, stopping now would be *temporary*, contingent on
  an external advance — a substrate with a demonstrated symmetry-partnered internal degree of freedom,
  or an intervention algebra with demonstrated local addressability.
- **What future external advance would reopen it?** Exactly those two. Both are engineering advances
  the program can pursue; neither requires stopping first.

**Verdict on Route F.** Consolidation does **not** have higher expected epistemic value than the best
admissible bounded prospective family, because such a family exists, is bounded at 720 enrolled
worlds, and answers the prerequisite question that stopping would leave permanently open. Route F is
therefore **not selected**. It fails its own affirmative test, not a gate.

---

### II.4 Comparative decision table

#### II.4.1 Summary dimensions

| Dimension | Route E (revised) | Route G | Route F |
|---|---|---|---|
| Preserved scientific question | Q-E: prevalence of persistence ∧ complete verified turnover across the law frame | Q-G: entity-local causal ownership of a symmetry-broken convention | none pursued |
| Estimand | `Δ` = proportion of enrolled laws majority-instantiating the conjunction in both IC classes | hierarchical H1–H7; primary would be sign retention through turnover | n/a |
| Experimental unit | **law** (declared change of unit) | **entity**, with co-housed pair as the independence unit | n/a |
| Highest claim rung | **3** (population level) | **6** (single low-dimensional binary state) | none |
| Positive evidential value | establishes that the substrate reproducibly instantiates the prerequisite phenomenon; provisions every downstream family | would be the first entity-level ownership evidence in the program | none |
| Negative evidential value | high: an interval-based `NEGATIVE` at `k ≤ 1` is a real, publishable result that closes the prerequisite question | **low**: a null is confounded with the unanswered Q-E | consolidation only |
| MDE / power adequacy | MDE 0.240 at 80% power; type I 0.0146; negative arm attainable | **not computable** — enrolment depends on Route E's estimand | n/a |
| Susceptibility to hidden selection | low: denominator fixed at 720 before any run; no post-enrolment exclusion; global rejection reserved for software faults | high and unquantified: convention readout undefined, so symmetry leakage cannot be bounded | n/a |
| Engineering prerequisites | **one** bounded mission: turnover-evidence (cohort) channel | **four or more**: convention observable, intervention algebra, multi-entity symmetric worlds, environment equalisation/swap | none |
| Provenance requirements | evidence root over raw frames + cohort channel; anchoring before analysis | same, plus anchoring of the convention readout | none |
| Cost / bounded run count | **720** enrolled worlds + a declared calibration draw + 20-law reproduction family | unbounded at this time | zero |
| Major alternative explanations | inadequate horizon; mechanical ineligibility; IC dependence; detector artefacts | niche state; partner coupling; shared field; imposed detector convention; population imbalance mistaken for entity convention | n/a |
| Fatal falsifier | `k ≤ 1` of 60 laws with horizon and eligibility checks passing → the conjunction is not reproducible in `F` | both signs never co-occur (H1 fails) → no symmetry breaking to own | n/a |
| Residual ambiguity | `Δ` is an `R`-indexed operational density, attenuated relative to any latent law-level probability (table in §II.1.5) | everything downstream of the undefined observable | whether stopping was premature |

#### II.4.2 Gate-by-gate

`PASS` / `FAIL` / `N-A`. **One fatal gate failure rejects a route.** No averaging, no score.

| Gate | Route E | Route G | Route F |
|---|---|---|---|
| G1 estimand declared | PASS | **FAIL** | N-A |
| G2 no outcome selection | PASS | PASS (design) | N-A |
| G3 no historical tuning | PASS (two declared constants only) | PASS (design) | N-A |
| G4 competing-risk honesty | PASS | PASS (design) | N-A |
| G5 ownership confrontation | PASS by declination (no ownership claim; ceiling rung 3) | PASS (design) | N-A |
| G6 turnover evidence | PASS (cohort tracer, independent of the persistence readout) | PASS (design, same channel) | N-A |
| G7 lifecycle exhaustiveness | PASS | PASS (design) | N-A |
| G8 stage separation | PASS | PASS (design) | N-A |
| G9 interpretable failure | PASS | **FAIL** | N-A |
| G10 no engineered answer | PASS | PASS (design) | N-A |
| G11 cadence honesty | PASS (blocker closed; disappearance is an outcome) | PASS (design) | N-A |
| G12 software is not evidence | PASS | PASS | N-A |
| G13 exact prospective estimand | PASS | **FAIL** — no convention observable definable from permitted evidence | N-A |
| G14 unit and enrolled denominator | PASS (law; 60 laws / 720 worlds) | **FAIL** — enrolment not computable | N-A |
| G15 no outcome-dependent eligibility or replacement | PASS | PASS (design) | N-A |
| G16 no calibration from the closed family | PASS | **FAIL** — the only available source for the missing enrolment number is the closed family | N-A |
| G17 MDE and numeric decision rule | PASS (MDE 0.240 @80%; CP rule) | **FAIL** (derivative of G13) | N-A |
| G18 two-sided adequacy | PASS | **FAIL** | N-A |
| G19 edge-event handling | PASS | PASS (design) | N-A |
| G20 family separation | PASS | PASS (design) | N-A |
| G21 no dual-role family | PASS | PASS (design) | N-A |
| G22 entity-level preservation | PASS **with declared change of unit**; no claim to answer the entity question | PASS | N-A |
| G23 no manufactured entity | PASS | **at risk** — choosing the observable after inspection is the specific hazard | N-A |
| G24 no survivorship or cadence trapdoor | PASS | PASS (design) | N-A |
| G25 exact claim-ladder ceiling | PASS (rung 3, law level) | PASS (rung 6, stated) | N-A |
| G26 informative negative | PASS (four discriminators) | **FAIL** — a null is confounded with Q-E | N-A |
| G27 bounded resource and termination | PASS (720 + calibration + 20; fail-closed on cost) | **FAIL** — prerequisites unbounded | N-A |
| G28 owned-pipeline compatibility | PASS **with one bounded prerequisite** (cohort channel; all five contract properties preserved) | **FAIL** — no intervention or multi-entity capability in the contract | N-A |
| G29 frozen import | PASS (§II.6) | PASS (§II.6) | N-A |
| G30 external anchoring | PASS (§II.5) | PASS (§II.5) | N-A |
| G31 OP-L3 handled | PASS (raw frames + cohort channel inside the root) | PASS in principle; the convention readout would also need covering | N-A |
| G32 no historical confirmation | PASS | PASS (design) — but see G16 | N-A |

**Route E:** 0 fatal failures. **Admissible.**
**Route G:** 8 fatal failures (G1, G9, G13, G14, G16, G17/derivative, G18, G26, G27, G28). **Rejected
for now**, on gates, not on merit.
**Route F:** no gate failure; fails the §10.5 affirmative test. **Not selected.**

#### II.4.3 Note on the G28 reading

G28 is read as compatibility with the **contract** — mandatory `sampled_frames`, acquisition invoked
once per schedule element, persisted-and-re-read evidence, mandatory tracking and lifecycle
validation, `COMPLETE`/`AnalysisAccess` gated on internal consistency — not with the current
byte-level implementation. Route E's cohort channel adds a persisted, re-read, digest-bound channel
and preserves all five properties, so it passes. Route G's requirements (intervention algebra,
multi-entity symmetric worlds, environment swap) are not additions inside the contract; they are new
capabilities the contract does not describe. This reading is stated explicitly so that it can be
attacked.

---

### II.5 Evidence-root anchoring design

**Root definition.** The evidence root is a Merkle-style digest over the complete run-family evidence:
every raw acquired frame, the cohort/turnover channel, `ACQUISITION.json`, `OWNED_PIPELINE.json`,
`LIFECYCLE.json` and `COMPLETION.json` for every enrolled world, plus the enrolment ledger, the
committed PRNG seed, the preregistration document hash and the pinned module source hash. Raw frames
are inside the root because OP-L3 leaves morphology unbound (V3).

**Primary anchoring route — operator-pushed Git anchor object.** An annotated tag
`anchor/<family-id>` whose object body carries the root digest, the enrolment ledger digest, the
preregistration hash and the module hash, committed to the repository and **pushed by the operator**
to the public remote. Content-addressed, public, effectively append-only, and requiring **no local
secret** — the operator's own credentials, not a secret embedded in the pipeline. Anchoring evidence
is the remote object id plus a retrieval confirmation, recorded in `ANCHOR.json` **outside** the
mutable run directory.

**Fallback — externally published root digest.** If the agent environment cannot push (proxy 403) and
the operator cannot push either, the root digest is published verbatim to an independent public
append-only venue (a timestamped public post, a transparency log entry, or a Zenodo deposit with a
DOI). `ANCHOR.json` then records the venue, the retrievable URL, the publication timestamp and the
digest as published. A later Zenodo deposit may supersede but never replace the first anchor.

**Fail-closed enforcement.** Analysis access is refused unless: `ANCHOR.json` exists outside the run
directory; the recomputed root equals the anchored digest; and the external reference is present and
non-empty. Absence, mismatch or an unverifiable reference all refuse. This must be enforced **in the
scientific runner's code**, not by convention, and must be covered by that runner's qualification
tests. An unanchored family is not analysed — it is re-anchored or discarded.

**Ordering.** Seal → anchor → verify → *then* analysis access. Anchoring is **not** performed in this
mission.

---

### II.6 Frozen import decision

**Frozen: exact module-level import with a pinned source hash.**

```
from edlab.substrates.lattice_bond.future_lifecycle_owned_pipeline import (
    run_owned_future_pipeline,
    open_owned_analysis_access,
)
```

The scientific runner verifies, at start-up and fail-closed, that the sha256 of the imported module's
source equals the hash pinned in the preregistration. The baseline hash of the currently accepted
module is `cc617f06f517aba7c890b9efbf069b7994696af243fc5a584220411747cae919`; the turnover-evidence
channel mission will change the module, so what is frozen is the **mechanism** — module-level import
plus a pinned hash of whatever version is qualified and human-reviewed — with the pinned value
recorded in the preregistration.

**No package re-export mission is authorised.** A re-export through
`edlab/substrates/lattice_bond/__init__.py` would require a successor requalification of a
byte-pinned file (fact 3.4.23) and would buy only ergonomics. A pinned-hash module import is strictly
stronger for provenance than a namespace re-export, which pins nothing. This satisfies G29 and honours
the instruction not to create an infrastructure mission for import ergonomics.

---

### II.7 Preliminary decision

**Primary route: Route E (revised) — replication density.**
**Backup: none.**

Reasoning, in the order §10 requires:

1. **Gates.** Route E has zero fatal gate failures. Route G has eight. Route F has none but is not a
   prospective route.
2. **Dimensions, unweighted.** Route E is the only route with a computable estimand, a computable
   sample size, an attainable negative arm and a bounded cost.
3. **Rung preference.** Route G reaches a higher rung (6 vs 3) and keeps the entity as the unit — and
   would be preferred **if it were admissible**. It is not, and §10.1 forbids trading a gate failure
   against a strength. Route E's change of unit to the law is declared prominently and Route E is not
   presented as answering the entity-level question.
4. **Tie-break.** Not reached; only one admissible route.
5. **Route F.** Fails its own affirmative test (§II.3).
6. **Backup.** §10.7 requires a backup to pass all thirty-two gates independently. Route G does not.
   Route F is a stop, not a route. **No backup is named.**
7. **Non-criteria.** Route G's novelty and the operator's stated interest in it played no part. Route
   G is rejected on G1, G9, G13, G14, G16, G17, G18, G26, G27 and G28, each with a stated reason, and
   is recorded as the program's **named successor question** whose prerequisites Route E supplies.

**Preliminary terminal disposition:** `PROSPECTIVE_ROUTE_SELECTED` — subject to both adversarial
reviews.
