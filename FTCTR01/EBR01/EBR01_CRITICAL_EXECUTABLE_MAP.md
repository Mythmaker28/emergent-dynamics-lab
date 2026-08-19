# EBR01 — CRITICAL EXECUTABLE MAP

**Static inspection: NOT PERFORMED — there is no recovered source to inspect.**
Nothing was imported. Nothing was executed. Nothing was written from prose.

| gate | object | result |
|---|---|---|
| A | integer per-cell Y occupancy | `NOT_RECOVERED` |
| B | four ordered diffusion sub-shifts | `NOT_RECOVERED` |
| C | one Binomial mover draw per occupied cell / sub-shift | `NOT_RECOVERED` |
| D | sequential state update between sub-shifts | `NOT_RECOVERED` |
| E | toroidal wrapping | `NOT_RECOVERED` |
| F | destination free-capacity calculation | `NOT_RECOVERED` |
| G | destination-capacity refusal | `NOT_RECOVERED` |
| H | `p_hop_Y` constructor-to-scheduler path | `NOT_RECOVERED` |
| I | `muX` decay path | `NOT_RECOVERED` |
| J | `kY` and `muY` birth/death paths | `NOT_RECOVERED` |
| K | `nSY` / candidate-pool semantics | `NOT_RECOVERED` |
| L | X birth acceptance and X decay | `NOT_RECOVERED` |
| M | exact scheduler event order | `NOT_RECOVERED` |
| N | centre-classification rule (Y positions → one vs two centres) | `NOT_RECOVERED` |

**0 of 14 gates satisfied.**

## What was available, and deliberately not used

Three documentary substitutes are physically present and would each have let a careless
operator "satisfy" a gate:

* `LRCPS01_MANUSCRIPT.pdf` and `LRCPS01_SUPPLEMENT.pdf` in `Downloads`;
* `figure_data/fig1_model_and_event_order.json` inside the paper package — literally the event
  order, in machine-readable form;
* `supplement/S1_methods.tex` inside the paper package — the methods section.

None was used. Section 12 forbids exactly this: *reproducing the event order from Figure 1* and
*implementing a binomial walk from review prose* are named prohibitions. A model rebuilt from
`fig1_model_and_event_order.json` would agree with the paper and still be a **new architecture**,
which would void `TAU_SEP = 125`, the `101/250` threshold, the `C3` surrogate and every
developmental observation attached to the old one. Behavioural agreement is not byte recovery.

## The gate that could never have been passed anyway

Even a perfect artefact recovery could not have satisfied gate **N**. The only surviving expected-hash
manifest, `PAPER_SOURCE_BINDING.json`, binds **no centre classifier at all**, and records `PQEC01`
with `files_present: {}` and `sha256: {}` despite 128 raw archives. Under §6 the classifier would be
`FULL_HASH_NOT_AVAILABLE`, and a prefix or a plausible-looking file may not be accepted as final
verification. §8 then applies: `PARTIAL_RECOVERY__CENTRE_CLASSIFIER_MISSING`, and FTCTR01 must not
continue.

That is worth stating plainly: **the recovery route had a ceiling below the pass mark before the
search even began.**
