# A1R4-VERIFIABLE-CLOSURE-00 — journal

role: Route E integrator · run: A1R4-VERIFIABLE-CLOSURE-00 · start/end 2026-08-04
starting git state: e5049d06e7fba07770f09e22910ae0cec023a16f (A1-R3, disposition REVISE)
ending git state: this commit, on codex/route-e-a1r4-verifiable-closure

## Scope
Engineering only. No scientific run, no scientific seed, no engine campaign, no pilot,
no preregistration, no A2, no merge into main.

## OBSERVED
- Phase 0 passed: bundle and patch sha256 match; commit, parent, tree and patch-id
  (3397a484ebbc98ae9850dd0d799542cd0be126dd) reconstructed identically from both the Git
  range and the .patch file.
- `future_route_e_pre_run_frame.draw_uniform` IS the frozen canonical generator and it is
  already 64-bit. The prompt does NOT conflict with the repository; A1-R2/A1-R3's 4-byte
  loop was the deviation. No STOP_CONTRACT_CONFLICT.
- go1.24.7 linux/amd64 is present, but proxy.golang.org is outside the network allowlist
  and the module cache is empty, so the pinned verifier cannot be reproduced here.
- No frozen exhaustive Route E source allowlist exists in the repository.
- No canonical namespace authority exists in the repository.
- The canonical root algorithms DO exist and are frozen in code
  (`_root_from_document`, `_owned_root_sha256`, `_OWNED_ROOT_FIELDS`), so
  STOP_ROOT_SPEC_UNFROZEN does not apply.

## INFERRED
Internal artefact consistency is recomputable; engine provenance is not. The trust boundary
stays INTERNAL_ARTIFACT_CONSISTENCY_ONLY and the three provenance flags stay false.

## HYPOTHESIS / WHAT WOULD FALSIFY THIS
A hand-written world that passes recomputation falsifies any claim that recomputation
establishes provenance. test_m36 exhibits exactly such a world.

## Failures and dead ends
The verifier build failed on module fetch (403, host not in allowlist). Not worked around:
changing the pinned digest to fit the environment is forbidden and was not done.

## Decisions
Three STOPs declared rather than papered over. A1-R4 cannot reach
READY_FOR_INDEPENDENT_REVIEW because the positive beacon path cannot be exercised.

## Unresolved risks / handoff
Owner decisions required: frozen source allowlist, namespace authority, verifier
provisioning. Next authorized action: independent read-only review of this branch.
