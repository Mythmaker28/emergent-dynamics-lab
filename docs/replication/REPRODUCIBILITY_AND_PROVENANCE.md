# REPRODUCIBILITY & PROVENANCE (Phase B/C status)

## Implemented
- Content-derived deterministic seeds (no process-salted `hash()`); fresh `PYTHONPYCACHEPREFIX` each run; direct
  `py_compile` from disk; freeze manifests hash-verified (v00 6/6, CRD-01 4/4, CRD-03 4/4); out-of-tree git index.
- Independent replication reproduces from `numpy` only; blocked-OU verified to 1e-15 vs literal recurrence.

## Not yet implemented (consolidation gaps — why publication is not top-tier)
- `make reproduce-paper` one-command clean rebuild with a pinned container (Dockerfile/Nix) — NOT built.
- Deliberate stale-cache-rejection tests as a standing suite — partially covered ad hoc, not packaged.
- Full figure-generation pipeline binding every displayed number to a generated artifact — NOT built.

These gaps, plus the T6 retraction and the FHN quantitative gap, keep the status below peer-review-ready.
