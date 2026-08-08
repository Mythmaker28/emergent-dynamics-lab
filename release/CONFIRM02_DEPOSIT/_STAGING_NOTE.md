# Where the deposit is

**The deposit is `deposit/`.** The archive of it is `CONFIRM02_DEPOSIT.tar.gz` (same directory).

Start with `deposit/README.md`.

## Everything else here is scratch

`sources/`, `verification/` and `_probe/` at *this* level are staging copies produced while
extracting artefacts out of git. They are byte-identical to (or subsets of) what is inside
`deposit/`, and they are **not part of the deposit**: they are not listed in
`deposit/SHA256SUMS` and they are not inside the archive.

They were left behind because the working mount used for this pass is create-only — `rm` fails with
`Operation not permitted`, so scratch could not be cleaned up. Delete them by hand if you want:

```powershell
Remove-Item -Recurse -Force "C:\Users\tommy\Documents\ising v3\release\CONFIRM02_DEPOSIT\sources"
Remove-Item -Recurse -Force "C:\Users\tommy\Documents\ising v3\release\CONFIRM02_DEPOSIT\verification"
Remove-Item -Recurse -Force "C:\Users\tommy\Documents\ising v3\release\CONFIRM02_DEPOSIT\_probe"
```

Deleting them does not affect `deposit/` or the archive.

## Integrity

- `deposit/SHA256SUMS` lists 43 files and omits itself, by design.
- Verify the archive externally: its SHA-256 is reported in the pass summary, not stored inside
  itself.

## Author authorisation, 2026-08-08

The release blockers on the copyright holder, the author name and the licence were settled by the
corresponding author on 2026-08-08. The deposit was regenerated: see `deposit/AUTHOR_AUTHORISATION_02.md`
for exactly what was declared, what was *not* declared (affiliation, ORCID), and why approving a
licence is not authorisation to deposit.

- archive SHA-256 before the patch: `f2906941007b0a17258a2b3203d96a82af76149a904456c231dee56db9186543`
- archive SHA-256 after  the patch: `5777309471657fc5811b1eaa09f7f1f6940451f4fbd73b4420421ddb4c71054a`
- provenance ledger: 109 rows, 98 `VERIFIED`, 6 `NOT_FOUND`, 5 `DIFFERS`; seal manifest 8/8 intact.

The deposit **is** now committed to git (branch `dev/route-e-ablation-depth-03` and later), so it is
no longer a single-copy artefact on one disk. **Nothing has been pushed to a public remote, and
nothing has been submitted anywhere** — no Zenodo record created, reserved or published.
