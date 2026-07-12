# EXP-CH-00 — R7 passes. The first substrate that actually contains entities. (2026-07-12)

Five substrates in, this is the first one to clear the localization gate. Not because I finally found the right
parameters, but because cohesion is **in the equations**: cells secrete an attractant and climb its own gradient.
Aggregation is what the model *does*, not a lucky regime. And the causal control is unambiguous — set `chi0 = 0` and
the participation ratio goes to **1.000**, a perfectly uniform field. The cohesion is caused by the internal field.

R7: 4/32 blind Halton points localized; across 5 seeds, laws 2, 4, 5 hold (5/5, 4/5, 5/5) and **law 18 fails at 3/5**
with PR = 0.152 and 0.153 against a frozen 0.15. I did not move the threshold. Law 18 is rejected.

## Two things I got wrong, again of the same species
1. I claimed the volume-filling factor made `rho <= rho_max` invariant. It didn't: `q` multiplied the *donor* cell,
   not the receiver, and growth wasn't regularized at all. A smoke test hit `rho = 1.408`. The claim was in the
   protocol before it was true in the code.
2. My radius-of-gyration criterion **could not fire**. Global Rg measures the spread of the *ensemble*: a field of 30
   perfectly compact spots scores 23.9 against 26.1 for a uniform field. Any multi-spot localized state fails it by
   construction, no matter how compact its entities are. That is the third time this session I have written a test
   incapable of producing the outcome it was supposed to detect — after the pooled null (a null that cannot fire) and
   the Nyquist-violating cadence (an observer that cannot see).

The pattern is now unmistakable and worth naming: **when I invent a diagnostic, my default failure is to build one
that cannot fire.** So the discipline generalizes: *before using any criterion, construct a synthetic case that MUST
pass it and check that it does.* I did that here — 30 compact spots, which any honest localization test must accept —
and it immediately exposed the broken Rg. That check is now a unit test.

## Where this stands
R7 passed. That is all. It means the substrate contains localized, persistent, turning-over entities whose cohesion
is causally due to the chemotactic field. It says **nothing** about whether their *organization* is load-bearing —
that is GATE-0, and Gray-Scott passed everything up to that point and then died there, with a scrambled lump
outperforming the intact entity. The entities here are 12–32 cells. GATE-0 is next, and it is the only thing
authorized.
