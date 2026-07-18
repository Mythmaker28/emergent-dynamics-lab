# CRD-02 PHYSICAL-TRANSFER AUDIT

Conducted for the record. The instrument FAILED at development (gate G5), so this audit does not authorize a
freeze; it documents whether the *architecture* could transfer, to inform the next iteration.

## Requirements of the selected contract (P1 — separate referenced episodes, difference-in-differences)

| requirement | classification | note |
|---|---|---|
| active uptake / response observable | **already observable** | the droplet's measured output |
| simultaneous reference observable, per episode | **requires new PASSIVE observable** | a co-located sensor or neighbouring region sharing the environmental drift; passive, no state access |
| common external-field history | already observable | the environmental disturbance is shared by construction |
| spatial reference region | requires new passive observable | a symmetric non-responsive region |
| timing synchronisation (fixed active/sham schedule) | already available | separate episodes in time |
| repeated sham and active schedules | already available | ordinary protocol |
| **simultaneous intervention AND non-intervention on one object** | **NOT REQUIRED** | the two episodes are separated in time — **G14 satisfied** |

## G14 — physical plausibility

**PASS.** Unlike CRD-01, the paired-episode contract never requires the same object to be probed and unprobed at
the same instant. The control is a *separate episode* of the same object plus a *co-recorded passive reference*.
No oracle twin. This is the intended advance over CRD-01.

## Transfer verdict (architecture)

`MAPPING_REQUIRES_NEW_PASSIVE_OBSERVABLE` — a co-located reference channel with finite coupling, delay, bandwidth
and contamination risk. It is physically plausible and is **not** an oracle. The passive observable is *proposed*,
not added to the droplet engine in this mission.

## But the instrument is not transfer-ready

The architecture is plausible; the *instrument* fails development (G5). A real reference region that leaks even
~12% of the response (κ = 0.12) would cause a silent ~21% attenuation the instrument cannot detect. On a droplet,
a neighbouring region is *more* contamination-prone than this benchmark assumes (diffusive coupling, shared
supply). So the passive-observable transfer must not be attempted until the contamination floor is lowered —
which likely requires an **independently-scaled reference** (a second reference of known different coupling), not
a tuning of the estimator.
