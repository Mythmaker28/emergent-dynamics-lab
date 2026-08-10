# PROJECT_EVIDENCE_AND_CLAIM_LEDGER

Status: `INCOMPLETE_DUE_TO_MANDATORY_STOP`

| Claim | Evidence level | Scientific status | Audit note |
|---|---|---|---|
| The local objects form `3f8dae8 -> de1524b -> d86d248` | `VERIFIED_FROM_CODE_AND_HASH` | `ESTABLISHED` for local Git ancestry only | Verified with `git cat-file`, commit metadata, and `git merge-base --is-ancestor`. |
| The canonical remote default branch is `main` at `f382dbf077699aa65c80328b6519035d1cda4a57` at audit time | `VERIFIED_FROM_CODE_AND_HASH` | `ESTABLISHED` for the observed remote metadata snapshot | Verified with GitHub repository metadata and `git ls-remote --symref`. |
| The announced ETPC, EEFCA, and ETNBFC branch refs are present on the canonical remote | `VERIFIED_FROM_CODE_AND_HASH` | `REFUTED_IN_TESTED_DOMAIN` | Exact remote-ref queries returned no matching refs. |
| `d86d248` exists locally | `VERIFIED_FROM_CODE_AND_HASH` | `ESTABLISHED` locally | The object and commit metadata resolve exactly; it is not thereby independently validated scientifically. |
| ETPC scientific execution and interpretation | `REPORTED_ONLY` | `NOT_ESTABLISHED` by IPRR00 | No raw/content audit was completed. |
| EEFCA scientific corrections | `REPORTED_ONLY` | `NOT_ESTABLISHED` by IPRR00 | No independent content audit was completed. |
| ETNBFC exact-rho blocker | `REPORTED_ONLY` | `NOT_TESTED` by IPRR00 | The blocker was not independently recomputed. |
| ETNBFC OFF-ledger blocker | `REPORTED_ONLY` | `NOT_TESTED` by IPRR00 | The executable paths were not independently audited. |
| Held-out integrity | `NOT_AUDITABLE` | `NOT_ESTABLISHED` by IPRR00 | No content was opened; a forbidden path-name enumeration forced termination before a valid non-access audit could be completed. |

No current project-wide scientific claim is upgraded, downgraded, confirmed, or contradicted by this stopped audit beyond the Git provenance facts above.
