# CRD-03 PHYSICAL-TRANSFER AUDIT

Conducted before freeze. Classifies each measurement the selected contract (ARM A + B: redundant references +
signed interventions) requires against the frozen droplet substrate.

| required channel | classification | note |
|---|---|---|
| active response observable | **already available** | the droplet's measured uptake/output |
| N>=3 reference channels with DISTINCT drift couplings | **requires new passive observables** | e.g. a global field sensor, a symmetric non-responsive region, a background-uptake channel, a neighbouring droplet — each with a *different* coupling to the shared environmental drift |
| common external-field history | already available | the environmental disturbance is shared by construction |
| distinct coupling magnitudes across references | **requires new passive observables** | the identifiability engine needs the couplings to differ (collinear references abstain, G3) |
| signed interventions +u, -u | **signed-intervention mapping plausible** | apply the intervention with both polarities in separate episodes; no oracle needed |
| unprobed / baseline episode | already available | a sham episode, as in CRD-02 |
| complementary non-responsive region (ARM C) | derivable passively (optional) | a region predicted not to carry the response; advisory only |
| absolute response-scale anchor | **physically unavailable on ctrans** | `ABSOLUTE_SCALE_UNAVAILABLE`; common-mode contamination stays a lower-bound direction |

## Verdicts

- Reference diversity: `MAPPING_REQUIRES_NEW_PASSIVE_OBSERVABLE` — the instrument needs **multiple** passive
  references with **distinct** drift couplings. On a droplet these are plausible (spatially separated sensors
  couple differently to a drift gradient) but are not currently instrumented.
- Signed interventions: `SIGNED_INTERVENTION_MAPPING_PLAUSIBLE`.
- Physical plausibility (G15): **PASS** — no simultaneous probed/unprobed clone, no oracle state.

**Overall transfer verdict: `MAPPING_REQUIRES_NEW_PASSIVE_OBSERVABLE`.** The design is physically plausible and
oracle-free, but requires co-recording several passive references of *different* drift coupling. The absolute
scale needed to close the common-mode direction is unavailable, so common-mode reference contamination remains a
declared lower-bound limitation on any droplet transfer. Passive observables are *proposed*, not added to the
droplet engine in this mission.
