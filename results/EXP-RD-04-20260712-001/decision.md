# EXP-RD-04 — DECISION: CANDIDATE WITHDRAWN. Classical Gray-Scott RETIRED.

Protocol SHA `c08a2cc6b1d8233c75db5352b1728a6944f2cd7d`, frozen at `f9da63d` **before any run**.
Law 14 only (frozen; no new laws). Seeds 14001–14040, entirely unseen. Enrolled **40/40**, censored 0.
`sham == control` bit-for-bit 40/40. Scrambled cargo verified to match the intact cargo's low-order statistics
exactly in 40/40. Non-entity source found in 40/40. No threshold changed, no composite, no post-hoc null redesign.

## Result

| arm | AUDITED_ROBUST (all 9 observer settings) | rate | Wilson 95 % |
|---|---|---|---|
| **INTACT** (the entity) | 17/40 | **42.5 %** | [28.5 %, 57.8 %] |
| **NULL-SC** (scrambled cargo) | 19/40 | **47.5 %** | [32.9 %, 62.5 %] |
| NULL-NE (non-entity cargo) | 0/40 | 0.0 % | [0.0 %, 8.8 %] |
| NULL-NE-M (non-entity, mass-matched) | 0/40 | 0.0 % | [0.0 %, 8.8 %] |
| null pooled | 19/120 | 15.8 % | [10.4 %, 23.4 %] |

Ambient-target control (CONTROL scored at the destination): fires 3/40 = 7.5 % [2.6 %, 19.9 %].

## Frozen decision rule
- **S1** `p_intact > 0` → 42.5 % → **PASS**
- **S2** Newcombe 95 % LB of (`p_intact` − `p_null_pooled`) > 0.10 → LB = **+0.108** → **PASS**
- **S3** exact McNemar, INTACT vs NULL-SC, paired → b = 1, c = 3, **both = 16**, **p = 0.625** → **FAIL**

All three were required. **The candidate is WITHDRAWN and classical Gray-Scott is RETIRED.**

## What actually happened
The **scrambled cargo re-establishes slightly MORE often than the intact entity** (47.5 % vs 42.5 %; 16 of the 20
units succeed under *both*). The scrambled cargo carries the identical total U mass, identical total V mass,
identical per-cohort mass, the identical multiset of per-cell values, to the identical destination, with the
identical support geometry and the identical displacement magnitude — and **its internal spatial organization has
been destroyed**.

Therefore the "causal re-establishment of a persistent individual" was, all along, **the delivery of a sufficient
quantity of V-rich material to a receptive site**. Gray-Scott simply regrows a spot from any adequate lump of
reagent. The *organization* of the transported matter contributes **nothing measurable** — the point estimate is
in fact negative. Every downstream property we had verified (continued cohort turnover, no old-site regeneration,
observer robustness across 9 settings, ambient null clean) is satisfied **just as well by a scrambled lump**. Those
checks were real, but they were never checks on *individuality*.

## The methodological defect this exposes (applies to the whole project)
**S2 passed only as an artefact of pooling.** NULL-NE and NULL-NE-M score 0/40 by construction — a non-entity region
contains almost no V, so nothing can regrow whatever you do to it. Pooling them with NULL-SC diluted the floor from
47.5 % to 15.8 % and made a dead candidate clear a 0.10 margin. **The pooled floor was the wrong statistic; the
matched, organization-destroying null was the right one.** I preregistered both, so the rule caught it — but only
because S3 existed. Had I preregistered S2 alone, I would have reported a false positive.

The same weakness was present in **every causal stage of this project**. Our PLACEBO always displaced a *non-candidate,
low-V* support — i.e. it was a NULL-NE-class null, a straw man. **No stage before EXP-RD-04 ever tested a positive
against a cargo that had the right matter but the wrong organization.** The EXP-FL-02 "survivors" and the EXP-RD-02/03
candidates were never subjected to the only null that could distinguish an individual from a lump.

**Permanent change to the stack (binding on all future substrates): the scrambled-cargo null is a required arm of
every causal intervention, and no re-establishment claim may be made without it.**
