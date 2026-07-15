# Commands to authorize separately (NOT run here)

Nothing below has been executed. No push, tag, DOI, upload, preprint, or journal submission was performed.
These are the exact steps for the operator (Tommy) to run *after* explicit go-ahead and after resolving the
blockers in `VERDICT.md`.

## 0. Prerequisite (resolve blocker #1 first)
Either recover+commit the original inline scoring script, OR accept the committed `reproduction/` package as
canonical and update the manuscript's inline h1/h2 deep values in a **future V4** (do not rewrite V3 history).

## 1. Review the local release branch (already prepared, not pushed)
```
git log --oneline release/organizational-memory-v1 -3
git show --stat release/organizational-memory-v1
python -m reproduction.primary --check          # sanity: conclusions reproduce
```

## 2. Push the branch (only when authorized)
```
git push origin release/organizational-memory-v1
```

## 3. Create the annotated release tag (only when authorized)
```
git tag -a v1.0.0 release/organizational-memory-v1 -m "IsingV3 organizational-memory v1.0.0"
git push origin v1.0.0
```
**Tag linkage.** `v1.0.0` is an annotated tag placed on the tip of `release/organizational-memory-v1`
(itself descended from the V3 science commit 897f81d). A reader arriving at the repository sees the
`v1.0.0` release and its `README_RELEASE.md`, which points to the manuscript PDF, the `reproduction/`
one-command reproduction, and `release/`. `CITATION.cff` carries the same version/commit.

## 4. Zenodo deposit (only when authorized)
- Connect the GitHub repo to Zenodo; creating the GitHub release from tag `v1.0.0` triggers a Zenodo archive.
- Deposit contents = the file set in `release/PUBLIC_RELEASE_TREE.txt` (47 files) with hashes in
  `release/RELEASE_MANIFEST.json`.
- After the DOI is minted, add it to `CITATION.cff` (`doi:` and `identifiers:`) and to the manuscript, then
  cut a `v1.0.1` metadata-only release if desired.

## Guardrails
- Confirm `git remote -v` points to the intended repository before any push.
- `main` must remain untouched; the release branch descends from the paper/V3 line, not from `main`.
