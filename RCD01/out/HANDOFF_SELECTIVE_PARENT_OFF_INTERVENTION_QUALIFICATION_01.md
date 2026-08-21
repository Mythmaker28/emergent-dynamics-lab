# HANDOFF — SELECTIVE PARENT-OFF INTERVENTION QUALIFICATION 01
## Successor to RCD01. ZERO SCIENTIFIC RUNS INITIALLY. DO NOT EXECUTE INSIDE RCD01.

    PARENT             = REPRODUCTION-CRITERION-DESIGN-01
    PARENT_DISPOSITION = MINIMAL_REPRODUCTION_CRITERION_DERIVED__SELECTIVE_INTERVENTION_CAPABILITY_MISSING
    BLOCKER            = GLOBAL_ORGANISER_OFF_ONLY

## Why this successor exists, and why it is not an architecture change

RCD01 derived the minimal reproduction criterion as R0 and R1 and R2. R0 is established
(53 of 192 fresh worlds). R1 is supported as a certified lower bound (25 of 53).
R2 — functional independence — cannot be tested at all, because the only causal intervention
in the engine zeroes the ENTIRE Y field in one operation:

    y = self.n["Y"].copy()
    self.n["Y"] = self.n["Y"] - y
    self.n["WY"] = self.n["WY"] + y

Removing the parent removes the daughter in the same instant. The experiment that would
decide reproduction cannot currently be expressed.

it manipulates the experiment at a declared instant. It adds no term to the autonomous law: between interventions every rate, every candidate rule and every update remains bit-identical. The existing global organiser_off already establishes the precedent and the channel; only the spatial scope changes.

## The job

Add and qualify ONE capability, `selective_organiser_off`:

    at a declared step, remove Y only from the cells belonging to one named spatial centre under the frozen toroidal single-linkage partition, through the same Y->WY channel, conserving occupancy exactly, touching no X and no resource

Change nothing else. The autonomous law between interventions must remain bit-identical.

## Qualification gates, all required before any scientific use

    - bit-identical trajectories when the intervention is not armed
    - occupancy conservation at the intervention step
    - no X molecule moved, created or destroyed
    - no resource field touched
    - the untouched centre's cells provably unaffected at that step
    - a deterministic parent/daughter tie-break declared in advance

The first gate is the decisive one: with the intervention present but NOT armed, a set of
seeds must reproduce their existing FDFLT01 trajectories BIT-FOR-BIT, including the final
state hash. If they do not, the capability has altered the law and must be rejected.

## Two things RCD01 found that this successor must carry

1.  THE PARENT/DAUGHTER RULE HAS AN UNDETERMINED CASE. In world F_B1_i182_s961444860 the two
    components at separation are at toroidal distance 2.5495097568 from the pre-separation
    centroid — both of them, exactly. The rule "the component closest to the pre-separation
    centroid is the parent" is silent. Two independent implementations split the other way.
    Declare a deterministic tie-break BEFORE any experiment that conditions on daughter identity.

2.  EXACT MATERIAL PROVENANCE IS RECOVERABLE AND CHEAP. The engine carries a molecular Tracker
    (engine_obtc.Tracker) recording id, birth_step and birth cell for every X molecule, drawing
    from its own generator. It was never written to the archives. Because every world is
    deterministic in its seed, a REPLAY of the 192 frozen FDFLT01 seeds with the tracker
    persisted would upgrade R1 from CERTIFIED_LOWER_BOUND to EXACT_MATERIAL_PROVENANCE at the
    cost of one re-execution and no new science. RCD01 could not do this because
    NEW_WORLD_CONSTRUCTIONS = 0. Authorize it explicitly if you want R1 exact.

## What must NOT happen

    - no change to any rate, candidate rule, scheduler order or stop rule
    - no new parameter point, no interpolation, no parameter search
    - no reproduction or heredity claim from this mission
    - the FDFLT01 stop at PREMATURE_THIRD_CENTRE censors R3 by construction; changing it
      changes the estimand and must be a declared decision, not a side effect

## After qualification

The one designed experiment is in RCD01_FUTURE_TEST_DESIGN.md: three phases, three controls
(SHAM, GLOBAL_ORGANISER_OFF, PRE_MATURATION_INTERVENTION), primary estimand the population
reproduction rate per seeded world, MAX_PRIMARY_WORLDS = 256, null frozen before the first
world with its derivation. Expected phase-2 worlds at 256: 33.3.
Decision-capable against a 0.02 null down to daughter survival q ~ 0.40; against 0.05 only
for q >= 0.80.

    MINIMAL_REPRODUCTION = NOT_TESTED
    STRONG_SELF_REPRODUCTION = NOT_TESTED
    HEREDITY = NOT_TESTED
