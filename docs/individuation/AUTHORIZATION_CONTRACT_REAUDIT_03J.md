# Authorization contract re-audit 03J

Mission: `LCI-TURNOVER-AUTHORIZATION-CONTRACT-REAUDIT-03J`

Verdict: **NOT READY — REPAIR REQUIRED**

Audited commit:
`2b1f45357b0e0be22236e5f73a403cecc27778ea`

Exact parent:
`7f005bca81e1a8bbd03ca9aa8f7d114931a686a9`

This was a narrow authorization-binding and provenance audit. No prospective
engine was instantiated, no 54xxx seed was executed, no prospective directory
was created, and no runner, protocol, analysis, gate, family, feature, or
environment file was modified.

## Blocking findings

### B-03J-01 — committed manifest contains the marker twice

The mission requires the committed execution manifest to contain exactly one
literal format marker:

```text
{final_seal_sha256}
```

The exact UTF-8 bytes of
`docs/individuation/TURNOVER_EXECUTION_MANIFEST_03G.json` contain the marker
twice:

1. `authorization.approval_phrase_template`;
2. `authorization.allowed_placeholder`.

The approval phrase template itself is one exact line and contains one marker,
but the whole committed manifest contains two. This fails Audit 2 as written.
No repair was attempted.

### B-03J-02 — canonical blob coverage is incomplete

The repaired artifacts have these exact Git blobs:

| Artifact | Git blob |
|---|---|
| production runner | `6444fcf8d702da9018472a630f7b8bd86a6d55d1` |
| execution manifest | `c65d8ba80b5961ef32ca37f65c6082c93002b928` |
| authorization template | `50c215877969108861bed6ab4064da672b307c31` |
| focused tests | `dd0341fa335134095a4f3fddce9412e6a955d9a0` |
| reproduction instructions | `6107c29990071ec0ac9906661bf4bd21ec881337` |

The production and DEV protected maps bind the repaired runner, authorization
template, and focused tests. The canonical path index names the execution
manifest. However, no affected canonical index binds the exact execution
manifest blob, and the reproduction instructions are absent from both the
canonical path index and protected maps. Audit 6 therefore cannot be certified.

No authoritative canonical JSON inspected by this audit still contains the
defective blob IDs:

- runner `74aa24de527280aa7652837923faa4c2ae907708`;
- manifest `bbcedfadbc8eb6058b5b0e7fe3b72abe3b67c0fe`;
- template `860ae5e8a8beecad3a1d2b8df9fcf622bb84e787`;
- focused tests `39f54d91499e40a9aab980b43ae8fb0cc9444957`.

## Audit 1 — provenance and diff scope

- Exact tip: PASS.
- Exact single parent: PASS.
- Blocker commit
  `4bf65651d7b5970c6d21f7369f6fc6386c49449f`: fetched, inspectable, and
  documented by the repair; it is a sibling based on the exact parent rather
  than an ancestor of the repair.
- Previous seal audit
  `def070685bf9833a6571766f91c5c7d8a2f8e787`: fetched and inspectable.
- Retired seal raw-byte SHA-256:
  `536cf0351bd65e6fc7efafb2d4a5acc86b99e244abe69c1bbcd8baad04022f62`,
  exact match.
- Retired status: PASS; the repair marks it
  `RETIRED — AUTHORIZATION TEMPLATE BINDING DEFECT`.
- Final seal on repair branch: none.
- Valid human authorization: none.
- Prospective seeds recorded: zero.
- LCI turnover 54xxx result records: none.
- `results/LCI-TURNOVER-PROSPECTIVE-03G`: absent.
- Changed-file count: exactly 22.

All 22 changed files are accounted for:

| Category | Count |
|---|---:|
| runner contract | 1 |
| manifests, templates, PRESEAL, and DEV bindings | 6 |
| focused tests | 1 |
| canonical/project/run/experiment indexes | 4 |
| regenerated DEV provenance artifacts | 5 |
| repair journal, audit evidence, and reproduction instructions | 5 |
| **Total** | **22** |

No scientific engine, analyzer, scope-feature, statistics, tracker, tracer,
event-evidence, protocol, decision-tree, seed-manifest, or raw-schema file
changed.

## Audits 2 and 3 — template and production runner

The phrase string is valid UTF-8, one line, and exactly:

```text
I AUTHORIZE ONE PROSPECTIVE EXECUTION OF LCI-CAUSAL-TURNOVER-PRESEAL-03G FINAL_SEAL_SHA256={final_seal_sha256}
```

The authoritative runner:

1. parses the seal and manifest;
2. computes the canonical seal SHA-256;
3. requires exactly 64 lowercase hexadecimal characters;
4. independently compares `final_seal_sha256` with the calculated hash;
5. substitutes the calculated hash into the frozen phrase template;
6. compares `approval_phrase` exactly, including spaces, case, and punctuation;
7. performs these checks before ledger initialization and before importing
   `turnover_engine_03g`.

The production-runner behavior passes static inspection. The separate
whole-manifest marker-cardinality requirement fails under B-03J-01.

## Audit 4 — independent focused cases

Synthetic seal files and temporary directories only:

- correct calculated hash in the separate field and substituted phrase: PASS;
- literal `{final_seal_sha256}`: rejected;
- literal `<FINAL_SEAL_SHA256>`: rejected;
- wrong hash in phrase: rejected;
- wrong separate hash: rejected;
- missing marker: rejected;
- duplicate marker: rejected;
- uppercase hash: rejected;
- 63-character hash: rejected;
- 65-character hash: rejected;
- altered whitespace: rejected;
- altered case: rejected.

Result: **12/12 expected dispositions**. Every failure occurred before ledger
initialization and engine import, and created no prospective run directory or
file.

## Audit 5 — regressions and DEV trace

| Check | Result |
|---|---|
| focused contract coverage in 03G suite | PASS |
| 03G production integration including A–F | 7/7 PASS |
| 03E frozen regression | 18/18 PASS |
| 03C frozen regression | 9/9 PASS |
| bijective tracker | 10/10 PASS |
| tracer/event checks | 6/6 PASS |
| power regeneration | PASS; probabilities unchanged |
| clean environment and protected map | PASS; 37/37 |
| DEV committed resume in its bound repository instance | PASS; `already_certified`, 10 entries |
| DEV terminal tip | `53dceb8c8ec6118911ffdf0b0357d6894dd4341212f8b27e0ebb92cbaf3e9b29` |

Power values remained:

- `P(N_valid>=18|50) = 0.5709037541746931`;
- `P(N_valid>=18|96) = 0.9245190233241044`.

The DEV seed-50001 payload is scientifically identical:

- scientific subtree equality: true;
- scientific canonical SHA-256:
  `e2fe64b82fb6f56d0e88be0ef76af199b05a4ff3e6e0d6f5dfac11d8b57a8b2f`;
- feasibility subtree equality: true;
- feasibility canonical SHA-256:
  `3c0b70d10edab4c3d431764a3963e60fccbe6b7a323c489512dbd4bdad852781`;
- certificate `outcome` and `gates`: identical;
- human analysis report: byte-identical.

Changed DEV digests trace only to provenance rebinding:

| Artifact | Parent SHA-256 | Repair SHA-256 | Changed content |
|---|---|---|---|
| analysis certificate | `cffe379a6c41e71bc849db98ea5a7c8649b709ea12f87fa2cc793cb49ee87b5f` | `cdd89c30d82c7bac09da88aa96e6d05b1044e89b4e66e9aa3019376e7af9229e` | ledger tip, raw manifest/trace hashes, seal hash |
| ledger anchor | `57aff1112af815d6182a57827d90e3d2d25ac54a72992055e5a833da91e5c92b` | `699a777e5b4d37ce20a10070f7bade0a850c341fc2d35bfa6cb77f3035374750` | tip hash |
| execution ledger | `9e18bfcfd3e090b7b2a52f68b157a88fc05d1efd256686681d318f864410af04` | `acba4ff34a17a74bca6a1994071cf9bc6dba1f3268f8ba428dcad31ab924ac88` | initial binding, chained hashes, provenance references |
| seed 50001 raw record | `a43817bb72f62c8a2b0f9f1fa919579840e249546e260d2ebbeea10fa9663df6` | `36838a1b2a15e29665bd829bba1d815c66b9dbe804c07bb46495661370c8802e` | bindings only |
| raw manifest | `acc06908e40ffe0c02c5e0f2a38d7d398fce4e41f73c9aa87e50392e4594f50a` | `d0c7f461812638e8355da6681b3b63091c7446786a45bc9ab50f4bc63821e9e5` | entry provenance and seal hash |

## Seal disposition

Because every check did not pass:

- `FINAL_SEAL_MANIFEST_03I.json` was not created;
- `HUMAN_AUTHORIZATION_TEMPLATE_03I.json` was not created;
- no new final seal SHA-256 exists;
- the retired seal remains invalid and may not be reused.

Exact next authorized action: make a separate repair that leaves exactly one
`{final_seal_sha256}` occurrence in the whole committed execution manifest and
binds the exact execution-manifest and reproduction-instruction blobs in the
canonical index, then submit that new commit for a fresh narrow re-audit.
