# CAUSAL-ADDRESSABILITY-ARCHITECTURE-01 — Stage A report

## Disposition

**STOP_ARCHITECTURE.** The exact committed local port is mechanically confined and the natural/open wrapper is a
conservative extension, but the exact committed environmental sample-and-hold port fails three independent binding
gates. It is E-active in the complete state returned by update 1, it removes a common external-probe effect from the
existing global `up_ref` channel, and its target-destination-only substitution constructs a one-sided artificial
boundary with nonzero extensive work. No alternate environmental port was designed or substituted after those
failures.

This is a code-only synthetic architecture stop. It is not a scientific outcome, does not alter any earlier result,
does not authorize Stage B, and does not establish or refute a causal access structure.

## Parent, scope, and firewall

The run starts from accepted parent `9ec894fbeba7ec2974a917a182d152e9d8074431`. Static obligations, the source
allowlist, the exhaustive edge inventory, and the isolated wrapper were committed before fixtures at
`62a3b22dce42d6d858eddc3323fe63685c0b051b`.

Only hash-bound durable documents, frozen engine dependencies, the isolated wrapper, and hand-built deterministic
arrays were opened. The test loader deliberately bypasses `edlab/experiments/__init__.py`, which imports scientific
analyzers. It loaded no scientific analyzer, source world, historical checkpoint, result file, DEV outcome, or seed.
No 500xx/570xx/580xx path, prospective namespace, V5/03G file, merge, or PR was used.

`Y^a(l,e)` uses availability polarity (`1=open`) and only `L0E0/L1E0/L0E1/L1E1`. The later member-directed
`Y_i^k(k_A,k_B)` namespace is absent.

## Exact implementation

`ConservativeAccessEngine` is an isolated diagnostic wrapper around the unchanged frozen MCM engine.

- `plan=None` and natural `L1E1` execution delegate directly to the frozen parent.
- The qualification-only active neutral kernel duplicates the exact frozen update and is byte-identical on the
  deterministic interior and periodic-boundary fixtures for both frozen updates.
- `q_L=0` changes only the target pointwise multiplier from
  `1 + lambda_plus*m_plus` to `1 + lambda_plus*0` during update 1. It neither erases `Mf`, changes `eta_w`, changes
  the state schema, nor persists into update 2.
- `E0` implements the committed preprobe-reference substitution exactly for target-destination transport, toggle
  neighbours, writer neighbours, `c`, `N`, and external `up_ref` numerator/denominator terms. Exogenous `P(t)` is
  explicit in the selected N parent and the target reservoir is not gated.
- Diagnostics are out of band. They include per-face open/selected transport contributions, global extensive
  transport ledgers, writer/global-channel components, probe decomposition, input hashes, and state-schema checks;
  they add no reporter to the simulated state. Per-face and aggregate transport accounting is exact, but the wrapper
  does not establish a complete ordered full-step source/sink/global residual after the earlier binding stops. Raw
  per-face records cover active E0 target-boundary transport open/active/delta aggregation only; stencil stages
  retain aggregate target deltas, and the neutral E1 active path does not emit matched face records.

## Existing-edge inventory and frozen horizon

The exact frozen order is transport; uptake/readout; passive inheritance and death; toggle reaction/diffusion;
memory writer and `up_ref`; `c`; `N`; return.

The environmental parents relevant through the frozen horizon are exhaustive for the committed candidate:

1. boundary `rho,c` and conditional donor `U/rho`, `V/rho`, `C/rho`, `Mf/rho` in material/interface transport;
2. outside post-growth `u,v` in target toggle Laplacians;
3. outside post-growth `m_k` in target writer mean/Laplacian terms;
4. outside current uptake and alive membership in the global `up_ref` numerator and denominator;
5. outside `c` in the target `c` Laplacian;
6. outside post-uptake `N = r_N + P(t) + innovation` in the target N Laplacian.

At update 1, transport reads exact `t0` values, so target uptake is E-invariant. Later stages in that same update read
post-uptake/post-growth environmental values and can change returned `U`, `V`, `Mf`, `c`, and `N`. Those differences
can first reach target uptake during update 2. Therefore the source-derived response-specific horizon is
`H*_uptake=2`, while the complete returned state has `H*_state=1`. A single unqualified first-update invariance claim
is false for the exact port.

## Synthetic qualification

The focused deterministic suite reports `15 passed` (final primary rerun `0.21s`; independent rerun `0.22s`).
Passing tests mean the implementation reproduces the committed arithmetic and exposes its failures; they do not
admit the architecture.

| Obligation | Result | Raw diagnostic |
|---|---:|---|
| Natural/open direct delegation | PASS | byte-identical frozen output |
| Forced-neutral active kernel | PASS | byte-identical for two updates and two boundary configurations |
| Local-edge confinement | PASS | first-update target `m_plus -> uptake` only; update 2 reopens |
| Input/persistent-state preservation | PASS | exact input hashes; unchanged IOM state schema |
| First-update target uptake invariance | PASS | maximum absolute difference `0.0` |
| Complete first-returned-state invariance | **FAIL** | `N 1.174760506348349e-4`; `Mf 1.0082892237656821e-5`; `U 3.4383443953123205e-8`; `V 2.553650209347058e-8`; `c 5.1641135812019456e-11` |
| E reaches target uptake at frozen `H*=2` | OBSERVED | maximum absolute difference `3.5574135979822043e-6` |
| Common external `P` through open `up_ref` | OBSERVED | effect `1.0592928753778812e-4` |
| Same common external `P` through selected E0 `up_ref` | **FAIL** | effect `0.0` because `S_B0` is held |
| Transport boundary-contribution accounting | PASS AS NARROW ACCOUNTING | exact aggregate residual `0.0`; per-face residuals no larger than `6.938893903907228e-18` |
| No artificial/quasi-autonomous boundary | **FAIL** | unpaired update-2 pre-`dt` transport-rate ledgers: `rho 0.09139115625597238`, `U 0.06283909247751597`, `V 0.0360285998120397`, `C 0.09139115625597238`, `Mf 0.010953608852929408` |
| Complete ordered full-step source/sink/global identity | **NOT QUALIFIED** | transport contribution accounting is closed; the complete identity was not established after binding stop conditions |

All reduced comparisons use an operation-count `gamma_n` roundoff bound. Byte equality is required wherever no
reduction is involved. No tolerance was selected from fixture outputs. With synthetic `dt=0.1`, the corresponding
unpaired per-step transport work is `rho/C 0.009139115625597239`, `U 0.006283909247751598`,
`V 0.0036028599812039704`, and `Mf 0.0010953608852929408`.

## Why the kill switches bind

### 1. First-update structural inactivity fails

The static requirement cannot be satisfied for the complete returned state. Preprobe references are already stale
when update-1 toggle, writer, and N stages read post-growth neighbours. Making references lazy or delaying E
activation would be a new port, which this mission forbids.

### 2. The environmental arm does not preserve the common probe globally

The N stencil retains common `P(t)` explicitly, but the same external pulse changes current outside uptake. Natural
`up_ref` transmits that change; E0 replaces it with `S_B0`. The probe is therefore not common across arms through all
existing response edges. Replacing `S_B0` with a probe-aware quantity would change the frozen candidate.

### 3. The port constructs a one-sided boundary

Only target-destination reads are substituted; non-target destination increments remain frozen. The resulting
selected-minus-open global extensive transport-rate sums and their `dt`-scaled per-step work are nonzero. The
per-face transport ledger accounts for those contributions numerically, but narrow accounting does not make the
interface paired or conservative. The intervention imposes an artificial directed boundary and triggers the
quasi-autonomy kill switch. Symmetric or paired gating would be a different port.

### 4. Complete full-step accounting remains unqualified

The active E0 target-boundary transport intervention has exact aggregate and raw per-face open/active/delta
accounting, including an operation-derived roundoff bound. That is narrower than the mission's requested complete
ordered full-step source/sink/global identity across growth, death, toggle, writer and clipping, c/N diffusion, and
the reservoir. Stencil stages retain only aggregate target deltas, and neutral-E1 matched face records plus a
complete raw parent/reference/sham log are absent. The complete identity was not established after the first three
binding stop conditions; it cannot be claimed as a qualification success or used to rescue the E port.

## Permitted claims

| Claim | Permitted? | Boundary |
|---|---:|---|
| Natural/open wrapper can reproduce the frozen parent | Yes | synthetic code-only identity |
| The narrow local `m_plus -> uptake` edge can be deleted transiently without erasing state | Yes | mechanical edge qualification only |
| The committed environmental port implements its literal formulas | Yes | literal implementation, not instrument admission |
| The environmental port is a valid orthogonal causal instrument | No | three binding failures |
| The rank-4 availability factorial is scientifically usable | No | environmental coordinate unadmitted |
| Local storage, autonomy, redundancy, synergy, relationality, individuality, or ownership | No | no scientific world or causal outcome was run |
| Prior 03G evidence carries into this architecture | No | nothing is grandfathered |

## Independent review and next action

The independent reviewer reproduced the horizon conflict before fixture outputs and preliminarily found that the
exact candidate compels `STOP_ARCHITECTURE`. The final artifact/claim audit is recorded in its separate journal.

The only next action is human review of this Stage-A stop package. Stage B must not be prepared or executed
automatically. Any lazy-reference, delayed, paired, symmetric, probe-aware, or otherwise altered E construction is a
newly authorized architecture mission, not a repair in this run.
