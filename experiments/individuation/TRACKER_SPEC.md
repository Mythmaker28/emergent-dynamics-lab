# Frozen multi-droplet longitudinal tracker spec (frozen BEFORE any prospective)

Extends the TCA-01 single-entity tracker to multiple co-existing droplets. Uses ONLY geometry; never reads a
history coordinate, a label, the turnover fraction M, or any future response.

- **Detection** each frame: connected components of {ρ > 0.30·ρ_max}, ≥12 cells (frozen `SCDetectionSpec`),
  periodic connectivity; circular centroid.
- **Matching cadence:** every 5 integration steps.
- **Assignment:** greedy maximum periodic **mask-overlap** between consecutive detection sets; a track keeps
  the current-frame component with the largest overlap fraction; overlap threshold θ = 0.1. One-to-one
  (a component may be claimed by at most one track; highest overlap wins).
- **Birth/lifecycle:** tracks are seeded at drive-onset from the selected targets; a track that finds no
  component with overlap ≥ θ is **censored** (lost) from that point — never reassigned to a distant component
  (this is the anti-teleport rule that fixed the V4 incident).
- **No use of h/label/M:** matching depends only on spatial overlap of ρ masks.
- **Tracker-independence check (mandatory):** every headline number is recomputed with the naive
  "largest-overlap-only" and reported; conclusions must not depend on the tracker.

Spec frozen; any change requires a new spec file and invalidates prospective runs made under this one.
