# POD QUANTUM-OPTION APPENDIX (bounded)

**Exact quantum task considered.** Frame reference-contamination discrimination as a state-discrimination problem:
given the (classical) reference time series, could a small variational or amplitude-encoded circuit on IBM Quantum
distinguish the common-mode contamination direction from a genuine smaller response better than the classical
CRD-03 admission?

**Classical baseline it must beat.** The CRD-03 instrument itself: it already achieves κ ≈ 0.002 detection for
*differential* contamination and is *provably optimal* for *common-mode* (the information is not in the passive
data at all — it is an identifiability limit, not an estimation-efficiency limit).

**Information it would add to the droplet experiment.** None that changes the identifiability. The common-mode
degeneracy is a rank deficiency of the *observation model* `H`; no measurement strategy — classical or quantum —
extracts a component that is absent from the passive observables. A quantum device processes the same contaminated
references and inherits the same null space.

**Whether hardware noise destroys any advantage.** Moot: there is no advantage to destroy. Even in the noiseless
limit, quantum processing cannot invert a rank-deficient classical observation map.

**Terminating result.** The branch terminates here: the obstacle is *observational* (the response and drift share
the field N), not *computational*. Quantum hardware is not warranted. It could only help if it supplied a NEW
physical observable of the droplet — which is an instrumentation question, not a quantum-computing one.

**Verdict.** `QUANTUM OPTION: NOT WARRANTED` — the failure is an identifiability/observability limit; no
information-processing advantage (quantum or classical) can rescue a reference set whose null space already
contains the common-mode direction.
