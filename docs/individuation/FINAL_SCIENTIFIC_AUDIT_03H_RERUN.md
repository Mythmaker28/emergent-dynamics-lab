# Final scientific audit 03H rerun

## Verdict

**READY.**

This audit was performed on branch `audit/lci-causal-turnover-final-seal-03h-rerun`, starting from exact commit
`7f005bca81e1a8bbd03ca9aa8f7d114931a686a9` with exact parent
`23b6e9b3c667705158af833c1cf8458a03c8fb66`.

The audit was limited to scientific reproducibility, protocol freeze, and registered-execution provenance. No
`54xxx` seed was instantiated or executed. No prospective output directory, completed human permission record,
prospective raw file, checkpoint, or result existed before the seal, and the unfilled permission template remains
invalid.

## Audit results

1. **Commit and checkout — PASS.** `git fsck --full` passed. The target is one commit over the stated parent, with
   38 changed files. The isolated checkout was clean before audit-only files were added.
2. **No prospective execution — PASS.** All remote refs were checked for
   `results/LCI-TURNOVER-PROSPECTIVE-03G`, `seed_54xxx` turnover outputs, and completed 03G prospective permission
   records. None were found. Only the committed DEV seed `50001` chain exists.
3. **Canonical authority — PASS.** `TURNOVER_CANONICAL_INDEX_03G.json` identifies exactly one path for each of 16
   roles and explicitly marks 03C and 03E paths superseded.
4. **Production chain — PASS.** The production runner connects manifest, seal, permission record, real seed
   executor, journal, raw publication, raw manifest, family closure, analyzer, report, and certificate.
5. **Frozen lifecycle — PASS.** The state machine contains `CREATED`, `AUTHORIZED`, `PRIMARY_RUNNING`,
   `PRIMARY_CLOSED`, `RESERVE_DECIDED`, optional `RESERVE_RUNNING`, `FAMILY_CLOSED`, `ANALYZED`, and `CERTIFIED`.
   The committed DEV sequence is:
   `CREATE -> AUTHORIZE -> START_PRIMARY -> SEED_STARTED -> SEED_COMPLETED -> CLOSE_PRIMARY -> DECIDE_RESERVE -> CLOSE_FAMILY -> RECORD_ANALYSIS -> CERTIFY`.
6. **Repeat and resume — PASS.** A second ordinary invocation in the declared DEV canonical directory was refused.
   Explicit resume returned the existing certified result. Synthetic interrupted execution resumed only the
   incomplete seed; changing the permission-record identity caused `resume binding mismatch`.
7. **Pre-engine bindings — PASS.** Before importing `turnover_engine_03g`, the runner verifies the execution
   manifest SHA-256 and Git blob, every protected code/analysis file SHA-256 and Git blob, the environment lock,
   exact runtime identity, seed-family hash, seal hash, and permission bindings.
8. **Reserve blinding — PASS.** The ledger receives only the seven feasibility projection fields. Scientific
   payloads remain in canonical raw records and are not read by reserve selection. The analyzer refuses any state
   before `FAMILY_CLOSED`.
9. **Analyzer — PASS.** Closed-family requirement, raw-manifest hashes, missing/incomplete raw refusal, duplicate
   world refusal, grouped original-world inference, Outcome E below the minimum, ownership/local-exclusion/causal
   gates, one reachable A–F result, and raw-digest traces were verified.
10. **Access scopes — PASS.** Frozen dimensions are `L=11`, `N=11`, `P=33`, `E=24`, `Gm=18`, `Gf=29`, and
    `B=8`. `Gf[:,0:11]` is exactly equal to `L`. No 32,768-variable primary decoder remains.
11. **Primary scientific gate — PASS.** A positive primary result requires
    `G_OWN_PERM AND G_LOCAL_EXCLUSION AND G_CAUSAL`; feeding effect alone is insufficient.
12. **A–F fixtures — PASS.** All six synthetic outcomes passed through the same production runner, raw validator,
    analyzer, and certificate writer.
13. **Authoritative environment — PASS.** A fresh Windows AMD64 CPython 3.12.10 virtual environment installed the
    committed lock exactly and reported NumPy 2.2.6, SciPy 1.15.3, and Matplotlib 3.10.9.
14. **DEV reproduction — PASS.** The exact real seed executor reproduced seed `50001` byte-for-byte in 23.111
    seconds. The registered DEV chain refused fresh replay and verified on explicit resume:
    - journal tip: `e79cfc4f33cbd788fe1109d43b83d20ef4d6f4d4d295f8a3aad24203cd4fadf0`
    - raw SHA-256: `a43817bb72f62c8a2b0f9f1fa919579840e249546e260d2ebbeea10fa9663df6`
    - certificate SHA-256: `cffe379a6c41e71bc849db98ea5a7c8649b709ea12f87fa2cc793cb49ee87b5f`
15. **Family power — PASS.** The committed deterministic calculation returned
    `0.9245190233241044`. Independent adaptive and Gauss-Jacobi quadrature returned
    `0.924519023325582`; absolute difference `1.48e-12`, well inside the repository's frozen numerical comparison
    criterion.

## Validation summary

- Turnover 03G end-to-end: 7/7 tests passed, including all A–F fixtures.
- Turnover 03E compatibility checks: 18/18 passed.
- Turnover 03C tests: 9/9 passed.
- Bijective tracker: 10/10 passed.
- Material tracer: 6/6 passed, including exact zero physical feedback and deterministic repetition.
- Protected implementation compilation: passed.
- Production static self-check: passed without importing or initializing the engine.
- Final seal verifier: passed.
- Unfilled permission template: refused before creating the prospective run directory.

## Decision-tree note

The structured tree is not a total partition for arbitrary Boolean inputs: the combination
`G_LOCAL_EXCLUSION=true` and `DISTRIBUTED_ENV=true` can overlap outcomes. That combination is unreachable from the
frozen statistics because local exclusion requires `L` to beat both `E` and `Gm`, while distributed access
requires at least one of those comparisons not to favor `L`. All 24 scientifically reachable assignments selected
exactly one outcome, and the runtime fails closed if an impossible combination is supplied.

## Final seal

- Path: `docs/individuation/FINAL_SEAL_MANIFEST_03G.json`
- Canonical format: UTF-8, LF, sorted keys, compact separators, trailing LF, no self-reference
- SHA-256: `536cf0351bd65e6fc7efafb2d4a5acc86b99e244abe69c1bbcd8baad04022f62`
- State: sealed, awaiting a separate human permission record

The unfilled template at `docs/individuation/HUMAN_AUTHORIZATION_TEMPLATE_03G.json` binds this exact seal but has
empty operator, time, identifier, and approval fields and both authorization booleans set to false.

## Remaining scientific limitations

- Outcome F and local-ownership conclusions are limited to the frozen 24-dimensional `E` and 18-dimensional `Gm`
  summaries; finer distributed encodings can remain invisible.
- The family-power value is a prior-predictive feasibility calculation, not a guarantee that 18 valid worlds will
  be obtained. If the minimum is missed, Outcome E is mandatory and the scientific question remains unanswered.
- The DEV seed `50001` produced feasibility Outcome E and is not scientific evidence about the prospective family.
- The registered-directory control does not attempt to prevent execution of modified open-source copies; such
  copies are outside the registered prospective execution.

## Exact next authorized action

Human review may fill a separate copy of the unfilled permission template. Until then, do not run the prospective
command and do not instantiate any seed in `54001-54096`.
