# EXP-MA-00 — the two mechanisms fight each other (2026-07-12)

R8 fails, and for a reason that is worth more than the failure: **cohesion and demixing compete for the same flux.**
Both A and B are moved by one transport term. Turn the shared attractant up enough to hold a droplet together and it
overwhelms the mutual repulsion, so the interior stays mixed. Turn the repulsion up enough to structure the interior
and it tears the droplet apart. Across the whole frozen domain, **0 of 32 laws are both localized and demixed** —
the two properties are mutually exclusive, not merely hard to co-locate.

The `lam = 0` negative control is what makes this airtight. At the laws that localize, switching demixing **off
entirely** changes nothing measurable (R8-A 1.32 vs 1.42; R8-B 0.21 vs 0.19). The multistability mechanism I built
the substrate around is, in the only regime where entities exist, **inert**. I preregistered that control precisely
so I could not talk myself past this, and it did its job.

## What went right for once
Every metric fired before I trusted it. The demixing index is *proven* to score a synthetic Janus droplet above 0.3
and a mixed droplet at ~0; it scored the real entities at a median of 0.012. The R8 gates are *proven* to separate
distinct individuals and to reject interchangeable ones, including the case that matters most — an arm that always
produces an entity of the **wrong** identity must score **zero** identity recovery. After four criteria this session
that could not fire, none of the fifteen used here shares that defect.

## Where I did not overreach
This does not show multistable substrates can't work. It shows *this* one can't, because I coupled cohesion and
internal structure to the **same** degree of freedom and they compete. The obvious repair — give the interior its own
non-competing degree of freedom, so that structuring it costs the droplet no cohesion — is a **different substrate**,
not a patch, and I did not add it after seeing the failure. That is the rule.

Seven substrates, seven negatives, nothing promoted. But the failures are getting sharper: this one died at R8 on a
mechanism-level contradiction I can state in one sentence, before a single causal unit was run.
