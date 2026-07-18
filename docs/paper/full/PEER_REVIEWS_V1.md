# Simulated Peer Reviews — Manuscript V1 (three independent reviewers)

## Reviewer 1 — Artificial Life / theory (hostile)
**Recommendation:** Major revision.
**Summary.** The paper reports that an *engineered* internal coordinate in a simulated droplet is causal,
transplantable, and turnover-surviving, and honestly disclaims individuation. The falsification-ladder framing and
the tracker correction are the real contributions; the ``memory'' itself is hand-built and unsurprising.
**Major concerns.**
1. *Novelty.* The mechanism is engineered ($m_+$/$m_-$ readouts, two leaky integrators). There is no emergence.
   The paper must not let ``organizational memory'' connote anything beyond ``a designed integrator that is not
   destroyed by turnover.'' State the novelty (evaluation methodology) up front and stop implying otherwise.
2. *Individuality.* The central claim is carefully hedged, but the title and abstract still risk being read as an
   individuality result. Because $h_1$ is global, this is a claim about the *world's* history, not the droplet's.
   Make the non-individuation explicit in the title or first sentence.
3. *Substrate dependence.* Everything is one simulator with one parameter set. The ``architecture vs substrate''
   caveat is welcome but under-argued; provide at least a qualitative argument for what would transfer.
4. *Conceptual inflation.* Words like ``experience,'' ``memory,'' and ``organizational'' are doing heavy lifting.
   Define them operationally at first use or replace them.
**Minor.** The six-hypothesis list is good but buried; promote it. Figure 1 is a schematic — say so in the caption.
**Confidence:** High (I work in ALife theory).

## Reviewer 2 — Statistics / reproducibility (hostile)
**Recommendation:** Minor-to-major revision (methods are unusually careful; a few gaps remain).
**Summary.** The statistical hygiene is better than typical for this literature: grouped leave-history-out, sealed
hashed prospective families, bootstrap CIs, and an explicit kill-switch. The leakage correction ($0.57\to0.19$) is
exemplary. My concerns are about residual degrees of freedom.
**Major concerns.**
1. *Tracker post-selection.* The longitudinal tracker was developed after seeing the incident trajectory (seed
   38501). Certification on disjoint seeds 38502--38504 is the right move, but the tracker's single free parameter
   ($\theta=0.1$) and the overlap rule could still have been tuned. State explicitly that $\theta$ was fixed before
   the hold-out and report sensitivity to $\theta$.
2. *Multiple comparisons.* Nine experiments, several coordinates, multiple checkpoints. Even with preregistration,
   the family-wise error deserves a sentence. The ladder is sequential, but say so and quantify.
3. *Small $n$ at depth.* $n=12$ histories at deep turnover is thin; the $h_1$ certification survives (lower bound
   $0.97$) but the reader must be told the CI is over 12 donor groups, not 36 rows.
4. *Marginal rank gate.* $\sigma_2/\sigma_1=0.283$ vs $0.30$ is reported honestly, but the manuscript should state
   whether the gate threshold was itself preregistered (it was) and resist any temptation to reinterpret it.
**Minor.** Define $R^2$ (done). Report the exact bootstrap count. Give the shuffled-null distribution, not just the mean.
**Confidence:** High.

## Reviewer 3 — Protocell / synthetic biology (hostile)
**Recommendation:** Major revision.
**Summary.** As a physics/biology object the droplet is a caricature; the paper knows this. My worry is over-reach
toward biological relevance and under-engagement with real protocell memory.
**Major concerns.**
1. *Biological relevance.* The connection to real active droplets and condensates
   (Zwicker; Brangwynne; Hyman) is asserted, not argued. Either strengthen the mapping (what in the model
   corresponds to what in a coacervate?) or downgrade the claim to ``inspired by.''
2. *Passive copying vs reconstruction.* The growth rule copies local memory into new material; calling any part of
   this ``inheritance'' is misleading even with the caveat. Consider removing ``inheritance'' entirely.
3. *Missing chemistry.* Real durable cellular memory is bistable/epigenetic (toggle switches, hysteresis). The
   manuscript now cites these but should more forcefully frame the $h_2$ failure as the *expected* consequence of
   using linear averaging instead of bistability.
4. *Turnover realism.* The pulse-chase is idealized. State that ``turnover'' here is a bookkeeping construct on a
   passive cohort field, not a chemical exchange process.
**Minor.** ``Viable'' is used loosely; define it (localized, single connected entity above a size threshold).
**Confidence:** Medium-high.
