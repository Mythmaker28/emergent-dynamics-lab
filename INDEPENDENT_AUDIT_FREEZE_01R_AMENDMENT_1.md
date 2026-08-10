# INDEPENDENT AUDIT FREEZE 01R — Amendment 1

Date: 2026-08-10. Scope: audit-infrastructure correction only.

Before any workflow blob was opened, the GitHub/provenance reviewer found that the external sentinel normalized a
path with PowerShell `.TrimStart('./')`. That API treats its argument as a set of characters, so the valid frozen
path `.github/workflows/nasi-ci.yml` became `github/workflows/nasi-ci.yml` and failed the already-declared
allowlist.

The normalization now removes only one exact leading `./` and explicitly rejects `..` traversal. This does not add
an allowlist entry, change scientific scope, permit repository execution, or weaken a held-out/engine denial. It
restores access to the workflow family already frozen in `INDEPENDENT_AUDIT_FREEZE_01R.md`.

Post-fix probes:

- `.github/workflows/nasi-ci.yml`: allowed;
- `../ETCMNFC/REPORT_ETCMNFC.md`: denied as traversal;
- a synthetic held-out result path: denied;
- corrected sentinel SHA-256: `A0E618F6BA638BE1457BD420DF19FCC80A590D8000F6699AE3E2F3CC9C5052BF`.

No workflow content was opened before this correction was documented and committed.
