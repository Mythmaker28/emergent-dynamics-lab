# IPRR00R freeze amendment 2 — audit-amendment path closure

- Date: 2026-08-10
- Scope: audit infrastructure only
- Scientific scope expansion: **none**
- Held-out/near-held-out scope expansion: **none**
- Engine, runner, world, trajectory or primary authorization: **none**

## Trigger

During independent verification of the already-created audit-only archive, the external sentinel correctly denied
`INDEPENDENT_AUDIT_FREEZE_01R_AMENDMENT_1.md`: the file was part of the audit package but its exact ordinary L0
audit filename had not been added to `read_allowlist`. The verifier stopped before opening or extracting that entry.
This is a closed-default infrastructure omission, not scientific evidence and not permission to weaken the sentinel.

## Exact correction

The external `IPRR00R_ALLOWLIST.json` is expanded by exactly two literal audit-document paths:

```text
INDEPENDENT_AUDIT_FREEZE_01R_AMENDMENT_1.md
INDEPENDENT_AUDIT_FREEZE_01R_AMENDMENT_2.md
```

No wildcard, scientific family, raw-state path or result path is added. The second literal permits this amendment to
be included in the final audit-only package without another self-referential allowlist omission.

- prior allowlist SHA-256:
  `FF704DCE4F3AB81D2916D9418BC6B19AA50759B8395CB9F0B93EE97AED06A5A7`
- corrected allowlist SHA-256:
  `556CE44B1BD4156F045F86E3FAF0956282346166889FBA1E4BA029336CB8CC27`
- command/path sentinel SHA-256 (unchanged from amendment 1):
  `A0E618F6BA638BE1457BD420DF19FCC80A590D8000F6699AE3E2F3CC9C5052BF`

## Requalification before resumed extraction

- positive path probe for amendment 1: `PASS`
- positive path probe for amendment 2: `PASS`
- held-out path negative probe: `PASS` (denied)
- repository-runner command negative probe: `PASS` (denied)

Package verification may resume only after this amendment is committed. The access classification remains L1 from
the earlier name exposure; no L2, L3 or L4 event is introduced by this correction.
