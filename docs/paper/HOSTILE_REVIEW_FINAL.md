# HOSTILE FINAL REVIEW (deliverable 14) — internal, rejection-oriented
1. **Hidden oracle contracts.** Arm O consumes truth contracts BY DESIGN (conditional arm) and issues 0
   points; the blind arm used_truth = 0 on both hold-outs. Point provenance is recorded. RESOLVED.
2. **Stable-bias theorem assumptions.** Prop 1 needs only that contamination has a direction collinear with
   the response scale — exactly the `c_i = q(1−β_i)` model; Prop 2 needs only equal sampling distributions.
   No hidden assumption. RESOLVED.
3. **Prospective reuse.** The N=5000 NASI and N=10000 PC hold-outs are each executed once; distinct seed
   namespaces; committed before execution. The burned hold-outs are used only as named regressions.
   RESOLVED.
4. **Set vs point conflation.** Kept strictly separate: SET verdict PASS (marginal), POINT verdict WITHDRAWN.
   The figure keeps false-zero (Panel A) and point-error (Panel B) on separate axes. RESOLVED.
5. **Conditional vs marginal coverage.** We report BOTH and state the set claim is MARGINAL EMPIRICAL, with
   conditional coverage 0.80–0.92 on the stable-contamination direction surfaced explicitly. RESOLVED
   (claim-narrowing).
6. **FHN inflation.** FHN is structural only; no quantitative point claim. RESOLVED.
7. **Droplet overinterpretation.** Stated as a negative passive-observability example that realizes Prop 1;
   explicitly not identity/life/turnover and not a claim about all future substrates. RESOLVED.
8. **Duplicated evidence.** Independent replication does not import the operational instruments; it reaches
   DIFFERENT numbers (0.939 vs 0.986 for NASI; overlap 120/120 for point intervals) — not a copy. RESOLVED.
9. **Figure denominators.** Panel B shows exact k/n per regime with binomial CIs, a 5% line, global 26/127,
   catastrophic 0/127. No denominator hidden. RESOLVED.
10. **Docker reproducibility.** Determinism, freeze and cache-poison verified; Docker/CI NOT run in sandbox
    → CLEAN REPRODUCTION marked INCOMPLETE, not PASS. RESOLVED (honest).
11. **Selective reporting of zero catastrophic errors.** We explicitly refuse to treat zero-catastrophic as
    success: the point claim is WITHDRAWN because coverage failed at 95%, independently of the (favourable)
    catastrophic count. RESOLVED.

## Publication-blocking items: NONE for the set-valued/theory scope.
Blocking for any POINT claim (correctly withdrawn) and for PEER-REVIEW-READY status (Docker/CI not executed;
no external human review).
