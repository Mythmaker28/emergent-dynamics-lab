# Canonical V4.0 source identification

The exact canonical V4 release is the Git object at:

- commit:
  `23b53aee4169deeda30aad2a9dba8587024f8d3d`
- original branch tip:
  `release/organizational-memory-v1`
- commit subject:
  `CANONICAL-REANALYSIS-V4: adopt committed reproducible headline numbers`
- release manifest:
  `canonical/release/RELEASE_MANIFEST_V4.json`

The canonical primary files are:

- manuscript source:
  `canonical/docs/paper/full/ORGANIZATIONAL_MEMORY_FULL_MANUSCRIPT_V4.tex`
- manuscript PDF:
  `canonical/docs/paper/full/ORGANIZATIONAL_MEMORY_FULL_MANUSCRIPT_V4.pdf`
- supplement source:
  `canonical/docs/paper/full/SUPPLEMENT_V4.tex`
- supplement PDF:
  `canonical/docs/paper/full/SUPPLEMENT_V4.pdf`
- claim ledger:
  `canonical/docs/paper/full/CLAIM_LEDGER_V4.md`
- statistical audit:
  `canonical/docs/paper/full/STATISTICAL_REAUDIT_V4.md`
- reproduction package:
  `canonical/reproduction/`
- committed longitudinal raw artifact:
  `canonical/results/observer/tca_holdout_raw.pkl`

All 37 files listed in the V4 release manifest were read directly from Git blob
objects and verify byte-for-byte against the declared SHA-256 values.

The binary archive `V4_0_CANONICAL_BLOB_SNAPSHOT.zip` contains the same exact
blob bytes and has SHA-256:

`39e030ade76d30eedd7c64fee9159396b87797b4e86f0b530dc39bdf71493a85`

Run:

```powershell
python .\verify_v4_0.py
```

Expected result:

`V4.0 SNAPSHOT VERIFICATION: PASS (37/37 manifest files)`
