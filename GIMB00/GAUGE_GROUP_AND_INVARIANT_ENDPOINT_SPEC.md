# GAUGE_GROUP_AND_INVARIANT_ENDPOINT_SPEC

## Why an ambiguity exists at all

The two scored regions are produced by the inherited detector as an **unordered pair** and then
serialized by sorting site-id lists. Sorting is deterministic, but the order it produces carries no
physics: it depends on which blob happens to contain the lexicographically smallest lattice index,
hence on blob shape. FSCMA00 demonstrated empirically that a different admissible serialization
changes the reported rank verdict, and that a seed-parity rule predicting the serialization failed
on 1 founder of 6.

## The exact group

Per founder, the pair (A_b, B_b) may be exchanged once. The exchange is shared across every scored
time, every arm and every dose of that founder, because the two masks are fixed at t0 and are the
same objects for every arm. The group is therefore `{+1,-1}^F` acting by

    delta_A <-> delta_B    equivalently    u -> u,  v -> -v

A per-time, per-operator or per-row sign would be a strictly larger group than the physical
ambiguity, and would discard real relative-sign information. It is forbidden as a gauge and used
only as a labelled diagnostic.

## What is invariant

* `u` exactly.
* `||v||^2` exactly.
* `v OUTER v` on a **whole-founder multi-arm block** exactly.
* `D_Q` between whole-founder blocks exactly.

## What is NOT invariant, and therefore may never carry a claim

* the sign of `v`;
* which region is called A;
* any statement of the form "history H acts more on A than on B";
* any per-row sign chosen independently inside a multi-arm comparison.

## Completeness

`(u, V OUTER V)` where `V` is the whole-founder concatenation of its `v` blocks is a **complete**
invariant of the block: `V OUTER V` determines `V` up to one global sign, which is exactly the
gauge. Oracle test Q0E verifies this reconstruction numerically.
