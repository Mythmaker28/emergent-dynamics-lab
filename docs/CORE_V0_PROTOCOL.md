# CORE V0 Protocol

## Dynamics

The world is a square torus of side `box_size`. For receiver particle `i` and source `j`, the minimum-image displacement points from `i` to `j`.

- `r < short_range`: linear repulsion with magnitude `-repulsion_strength*(1-r/short_range)`.
- `short_range <= r < interaction_range`: signed receiver/source coefficient multiplied by a triangular radial envelope.
- `r >= interaction_range` or `r=0`: zero pair force.
- semi-implicit Euler: `v <- v + dt*(F-damping*v)` then `x <- (x+dt*v) mod box_size`.

The interaction matrix may be asymmetric, so momentum conservation is not asserted. Float64 is mandatory. The scalar and vectorized paths are compared at:

`abs(F_vectorized-F_reference) <= 1e-12 + 1e-10*abs(F_reference)`.

## Entity detector

At each snapshot, connect particles whose minimum-image Euclidean distance is `<= connection_radius`. Entities are connected components with at least `min_size` particles. This choice can bridge structures through chains and is not a universal individuality definition.

The periodic centroid is a coordinate-wise circular mean. Descriptor geometry is computed from minimum-image offsets around that centroid.

## Phenotype Phi

The current predeclared vector is:

- particle count divided by world particle count;
- type fractions;
- radius of gyration divided by `length_scale`;
- covariance anisotropy `(lambda_max-lambda_min)/(lambda_max+lambda_min)`;
- radial 25/50/75 percentiles divided by `length_scale`;
- center velocity components divided by `speed_scale`;
- RMS velocity dispersion divided by `speed_scale`;
- signed internal circulation divided by `length_scale*speed_scale`.

This vector is invariant to diagnostic IDs, particle order, and global translation. It is not claimed to be rotation invariant because center-velocity components are retained. Raw descriptors and the normalized vector are persisted.

`P(tau)` is `exp(-RMS delta Phi)`. Feature normalization is fixed before screening and is not recalibrated per run.

## Tracker

Candidate edges require only:

- periodic centroid distance `<= max_centroid_distance`;
- size ratio `min(n0,n1)/max(n0,n1) >= min_size_ratio`.

Greedy deterministic association maximizes `size_ratio*exp(-distance/max_distance)`. It does not read diagnostic IDs or final P. All feasible alternatives are retained through split, merge, and `ambiguous_association` events; selected edges log their physical score. Measurements adjacent to complex lineage events require explicit audit before interpretation.

## Controls

Required live controls are:

1. diagnostic ID permutation across multi-step dynamics;
2. static identical motif with disjoint endpoint IDs, expected `P=1`, `M=0`, same lineage;
3. observer cadences `{10,30,60}` and predeclared tracker/detector sensitivity around nominal settings;
4. scalar versus independent vectorized force path;
5. orthogonal material-only and phenotype-only fixtures.

Every kill-switch gate must be green before EXP02 interpretation.

