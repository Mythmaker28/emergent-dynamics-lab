# Journal — EXP-SC-INDIVIDUAL-ORGANIZATIONAL-MEMORY-00

- Role: primary scientific execution agent (interactive; isolated branch). Base 709f963 (HSI final).
- First mission authorized to modify physics: added a bounded experience-written memory field m=(m1,m2).

## OBSERVED
- Backward-compat exact: lam_m=0 -> base fields bit-identical to frozen (dev 0.0); eta_w=lam_m=0 -> m==0.
- Memory causal: erase changes probe response 49.9x (dev)/50.6x (prosp) clone ceiling; ablation (lam_m=0)=0.
- Transplant transfers response 5.6x/5.5x clone. Survives turnover (M~0.15). Storage eff dim ~11.
- Order WRITTEN (m1-m2 ~0.46) but NOT read out (order->response 0.022 ~ clone).
- Readout ~1-D: response->net-dose R2 0.95/0.97; response->full-4D-history R2 0.24/0.55; memfield indiv AUC 0.57.

## INFERRED
- Mechanism is a genuine causal, erasable, transplantable, turnover-surviving, continuous experience
  memory, but the single scalar coupling tanh(m1+m2) bottlenecks read-out to ~1 dimension (net dose) ->
  does NOT individuate trajectories. HISTORY-CLASS memory, not identity.

## HYPOTHESIS / FALSIFIER
- H: a single-scalar-coupled memory cannot individuate regardless of writing richness.
- Falsifier: response->full-history R2 >= 0.6 and memfield individuation AUC >= 0.7 on prospective. Not met.

## DECISION
- VERDICT PASS - HISTORY-CLASS MEMORY ONLY. Gates fail: G5 (order readout), G11 (individuation).
- NEXT-PROJECT: higher-dimensional / multi-coupled memory (match high-cardinality writing with readout);
  do not merely add persistence; no mechanism added here. QUANTUM NOT USED.
- HMC prospective SEALED; SC-PILOT + EXP-SC-01 BLOCKED.

## ENVIRONMENT
- create-only mount / stale locks / no background jobs: resumable runners + lock-free plumbing + /tmp
  compute + bash-heredoc edits. See memory [[ising-v3-git-mount-workaround]].
