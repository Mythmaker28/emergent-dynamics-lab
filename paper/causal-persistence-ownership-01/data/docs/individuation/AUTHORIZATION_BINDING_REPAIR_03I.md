# Authorization binding repair 03I

Mission: `LCI-TURNOVER-AUTHORIZATION-BINDING-REPAIR-03I`.

- Branch: `repair/lci-turnover-authorization-binding-03i`.
- Exact scientific parent: `7f005bca81e1a8bbd03ca9aa8f7d114931a686a9`.
- Invalidated seal audit: `def070685bf9833a6571766f91c5c7d8a2f8e787`.
- Authorization blocker: `4bf65651d7b5970c6d21f7369f6fc6386c49449f`.
- Retired seal SHA-256: `536cf0351bd65e6fc7efafb2d4a5acc86b99e244abe69c1bbcd8baad04022f62`.
- Retired seal status: **RETIRED — AUTHORIZATION TEMPLATE BINDING DEFECT**.

This is a minimal contract repair. It is not a final seal, valid human authorization, prospective execution, or
scientific result.

## Observed defect

The 03G execution manifest froze a phrase containing the literal text `<FINAL_SEAL_SHA256>`. The runner compared
`approval_phrase` directly with that unexpanded literal and used only the separate legacy `seal_sha256` field.
Consequently the exact phrase accepted by the invalidated audit did not prove that the human wording contained the
calculated final-seal hash.

## Repaired contract

The production manifest now freezes one exact single-line template:

```text
I AUTHORIZE ONE PROSPECTIVE EXECUTION OF LCI-CAUSAL-TURNOVER-PRESEAL-03G FINAL_SEAL_SHA256={final_seal_sha256}
```

The prospective authorization schema is `LCI-TURNOVER-HUMAN-AUTHORIZATION-03G-v2`. It keeps the independent fields
`final_seal_sha256`, `approval_phrase`, `approver`, `authorization_id`, `authorized_at_utc`, and
`one_execution_only`.

Before ledger creation or engine import, the runner:

1. parses the final-seal JSON;
2. calculates SHA-256 from its canonical sorted compact JSON plus the canonical trailing LF;
3. requires `final_seal_sha256` to be exactly 64 lowercase hexadecimal characters and equal that calculation;
4. loads `approval_phrase_template` from the frozen execution manifest;
5. requires exactly one `{final_seal_sha256}` placeholder and no other brace placeholder;
6. substitutes the calculated hash;
7. compares `approval_phrase` exactly, without normalization.

Literal placeholders, wrong hashes, uppercase hashes, wrong lengths, and any case, whitespace, punctuation, or
Unicode difference fail closed.

## Scope preservation

No scientific protocol, seed family, reserve rule, gate, threshold, access scope, statistic, execution lifecycle,
raw schema, A–F decision tree, environment lock, or power calculation changed. The production family remains
exactly `54001-54096`, but no member was executed or initialized.

No `FINAL_SEAL_MANIFEST_03I.json`, final seal, valid human authorization, prospective ledger, prospective raw file,
or prospective directory was created.

## DEV provenance rebinding

The DEV execution manifest includes the changed runner, focused test, authorization template, canonical index, and
PRESEAL candidate in its protected provenance. Those five protected entries changed, so the DEV manifest, DEV
seal, DEV authorization bindings, raw provenance envelope, raw manifest, ledger chain, and analysis certificate
were deterministically rebound.

The already-open seed-50001 scientific payload was replayed through the ledger and analyzer with an injected
executor. Engine import was patched to fail and recorded zero calls.

| Artefact | Before 03I SHA-256 | After 03I SHA-256 | Reason |
|---|---|---|---|
| DEV execution manifest | `a4e41737b3eb2fe516b6d83452ae4a60f6f069cc585ecd008f6f5f15befaaf30` | `26821f0eb8e0c36c7650490171cc9e1ff7499685f4384ad9ac5a14be909ff931` | protected provenance entries changed |
| DEV seal | `764d3d5881c548b64a57c1206465846b1199af233c5cbd4da43552f628383947` | `9563fe67100e1e035da901f15567ceab000dfc18af96254ecb2fe4ed0e526b52` | binds the repaired DEV manifest and protected-map digest |
| DEV raw seed record | `a43817bb72f62c8a2b0f9f1fa919579840e249546e260d2ebbeea10fa9663df6` | `36838a1b2a15e29665bd829bba1d815c66b9dbe804c07bb46495661370c8802e` | provenance bindings changed |
| DEV raw manifest | `acc06908e40ffe0c02c5e0f2a38d7d398fce4e41f73c9aa87e50392e4594f50a` | `d0c7f461812638e8355da6681b3b63091c7446786a45bc9ab50f4bc63821e9e5` | raw-record hash changed |
| DEV ledger | `9e18bfcfd3e090b7b2a52f68b157a88fc05d1efd256686681d318f864410af04` | `acba4ff34a17a74bca6a1994071cf9bc6dba1f3268f8ba428dcad31ab924ac88` | manifest, seal, raw, and repository-instance provenance changed |
| DEV analysis certificate | `cffe379a6c41e71bc849db98ea5a7c8649b709ea12f87fa2cc793cb49ee87b5f` | `cdd89c30d82c7bac09da88aa96e6d05b1044e89b4e66e9aa3019376e7af9229e` | binds the new seal and raw manifest |
| DEV human report | `ebcfab410b6c72de3b1a7a013c2c6806eb03223f8e1fe0e2349c3b4dc7a8a68a` | unchanged | scientific interpretation stayed Outcome E |

The canonical scientific subtree SHA-256 remains
`e2fe64b82fb6f56d0e88be0ef76af199b05a4ff3e6e0d6f5dfac11d8b57a8b2f`; the feasibility subtree SHA-256 remains
`3c0b70d10edab4c3d431764a3963e60fccbe6b7a323c489512dbd4bdad852781`.

## Disposition

The repaired commit may be examined by a fresh narrow auditor. That auditor must issue any new final seal; a
separate human must then supply a v2 authorization bound independently in both the hash field and expanded phrase.
Neither action occurred here.

**Recommendation: READY FOR NARROW RE-AUDIT.**
