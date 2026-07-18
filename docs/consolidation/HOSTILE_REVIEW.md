# HOSTILE REVIEW (goal: reject the sign-safe consolidation)

| # | attack | finding | disposition |
|---|---|---|---|
| 1 | The 40/40 bracket claim contradicts the amplification failure | RESOLVED: every 40/40 regime had ≥1 clean anchor; boundary confirmed (no anchor → one-sided, sign-set) | audit committed; no coding error |
| 2 | The repair just renames the same buggy rule | REFUTED: instrument never uses max-amplitude by default; emits NON_IDENTIFIABLE/bounds; 0 invalid in 1600+ trials | resolved |
| 3 | Sign contract is inferred circularly from the amplitudes | the sign/anchor flags are DECLARED inputs, never derived from the amplitude ordering; instrument returns NON_IDENTIFIABLE without them | resolved |
| 4 | Theorems are code-fitted, not proved | T6-E impossibility has a symbolic construction (q'=2q with matched β'); T6-A/B/C/D property-tested 400× each | resolved |
| 5 | Prospective was peeked/tuned | split committed at 8b77031 before fitting; frozen at 09016d7; hash-gated; opened once | resolved |
| 6 | Second replication shares code | replicate2.py imports numpy only, not signsafe; 20/20 status agreement | resolved |
| 7 | Coverage cherry-picked levels | safety metric is confident-exclusion frequency = 0 across all sign regimes and all (m,s) | resolved |
| 8 | "Three references minimal" overclaim | sensitivity shows m=2 sometimes identifies, m≥2s+1 needed; claim reframed to diversity + sparsity, not raw count | narrowed |
| 9 | Cross-substrate quantitative claim | FHN clean recovery 0.86 (calibration bias diagnosed: pre-window not at rest); claim scoped to STRUCTURAL transfer (S2) | narrowed |
| 10 | One-command rebuild doesn't exist | `make reproduce-paper` runs 6 checks incl. freeze verification + stale-cache rejection; PASS from disk; Dockerfile pinned | resolved (container not executed in this sandbox — noted) |

## Residual load-bearing limitations (honest)
- The one-command pipeline was validated from the working checkout; the **Docker image was not built/executed**
  in this environment (no container runtime). The Dockerfile is provided and pinned but unverified end-to-end.
- No external human review (required for PEER-REVIEW SUBMISSION READY).
- FHN quantitative accuracy is substrate-specific; only structural identifiability transfers.
- The historical CRD-03 frozen instrument still carries the sign bug (documented, not patched — the sign-safe
  instrument is a separate module).

## Verdict of the hostile review
No unresolved contradiction remains in the sign-safe result. The load-bearing safety property (never a confident
exclusion of the truth) holds across development, a fresh prospective split, an independent reimplementation, and
adversarial sign/sparsity regimes. Remaining items are scoping and packaging, not correctness.
