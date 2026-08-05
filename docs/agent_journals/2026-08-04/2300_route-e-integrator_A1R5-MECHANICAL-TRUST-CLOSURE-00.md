# A1R5-MECHANICAL-TRUST-CLOSURE-00 — journal

role: Route E integrator · start/end 2026-08-04
starting git state: 2cb7a48f05016ffd764c4d11ba7c27eaaff97225 (A1-R4, REVISE)
scope: engineering only. No A2, no pilot, no preregistration, no scientific run.

## OBSERVED
- Phase 0 exact: bundle 18798 / ab1d1ee4..., patch 74488 / 52f90d79..., and
  `git patch-id --stable` = 5adfd957fcab20632d3444974b33b2f8a8517dd8, matching the
  authoritative value. The default `git patch-id` gives 56d9561b... -- the audit used
  --stable, and so did I.
- The eight A1-R4 overclaims are all confirmed. The pattern is a reporting-discipline
  defect: flags set to true for "implemented and unit-tested" where they mean "enforced in
  the path". It produced the A1-R3 independent_admission_verified overclaim too.
- (2**64 - 1) / float(2**64) == 1.0. The declared [0,1) is false; 1024 words round to 1.0.

## INFERRED
Internal artefact consistency is now materially stronger at enrolment, but the trust
boundary is unchanged: no engine provenance is established.

## WHAT WOULD FALSIFY THIS
A pre-depleted fixture passing admission would falsify the enrolment proof. It is now
refused (test_r5_a_pre_depleted_fixture_is_refused).

## Failures and dead ends
The pinned verifier still cannot be built: proxy.golang.org is outside the network
allowlist. The expected digest was not touched.

## Decisions
Three external STOPs remain, so the disposition is STOP, not READY_FOR_INDEPENDENT_REVIEW.
23 of the 41 obligations remain unimplemented and are listed, not disguised.

## Handoff
Owner decisions: RNG mapping (dossier written, option 1 recommended), source authority,
namespace authority, verifier provisioning.
