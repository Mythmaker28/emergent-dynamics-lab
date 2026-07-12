# EXP-MO-00 — the substrate had no entities, and I nearly reported a triumph (2026-07-12)

I built a motile polar substrate, qualified it (persistent! motile at 0.95 cells/step! complete constituent
turnover!), validated the instrument (INTACT 27/27 robust, SCRAMBLED 0/27 — a perfect separation, the exact result
the whole project has been chasing), and was one commit away from running GATE-0 on it.

**All of it was an artefact.** The "entity" was 4096 of 4096 cells — the entire lattice. The active phase is a
Fisher-KPP front: it either invades everything or dies. The periodic centroid of a domain-filling field is
ill-defined; it jitters, and my tracker dutifully reported that jitter as motility at 0.95 cells/step. I even built
a theory on top of the artefact — "it's a traveling wave, the pattern outruns its material" — and used that theory
to set the tracker gate.

The thing that killed it was **R5**, which I had written down *earlier in the same session*: every intervention must
carry an executable assertion that it changed its intended variable. A support that fills the domain overlaps its own
translate, so displacing it cannot conserve mass. The assertion fired on the first real unit. Without it I would have
reported INTACT 27/27 vs SCRAMBLED 0/27 as GATE-0 passing, and gone on to a law search on a substrate with no entities.

## What I actually got wrong
I designed for the *sophisticated* prerequisite — is organization load-bearing? — and never checked the *elementary*
one: **is there a localized structure at all?** Both failure modes of this substrate (space-filling, extinct) contain
zero individuals, and both will happily produce persistence, motility and turnover numbers if you point a detector at
them. R7 now goes in front of GATE-0.

## Where I stopped
Two declared grids, 21 parameter points, no localized regime. Localizing it needs a cohesion term. That is a rescue
mechanism and I did not add it. Substrate retired at qualification, before any law search — cost: one session,
not two months. That is what the gates are for.

Five substrates, five negatives, nothing promoted. The gates are getting cheaper and firing earlier, which is the
only kind of progress this project has actually made.
