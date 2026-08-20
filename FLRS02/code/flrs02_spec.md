# FLRS02 — what the two checkers SHARE and what they must NOT share

SHARED (raw inputs and frozen definitions only):
  - the PQEC01 .npz archives
  - the frozen protocol constants (L, CORE_R, muX) read from OBTC02/code/obtc02_protocol.yaml
  - the six-state definition and the seven success conditions, frozen in
    FLRS02_FUNCTIONAL_CRITERION.json before any outcome was inspected
  - the response-fraction band T_50 / T_primary / T_80 / T_90

NOT SHARED (each checker implements these independently):
  - state-sequence construction          A: python loop        B: vectorised np.select
  - S-episode extraction                 A: running-index loop B: np.diff on a boolean mask
  - connected components of Y cells      A: union-find         B: BFS queue
  - toroidal centroid                    A: anchored offsets   B: complex circular mean
  - X-plane reconstruction               A: single cumsum      B: direct partial sum per event
  - local X aggregation                  A: boolean disc mask  B: precomputed distance table

REQUIRED EXACT AGREEMENT (FLRS02 §14):
  world classification, geometric S timing, functional-duration qualification,
  P-before-function ordering, joint success counts.
