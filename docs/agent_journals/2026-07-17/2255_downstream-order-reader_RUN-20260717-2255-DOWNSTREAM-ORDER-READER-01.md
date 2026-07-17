# Agent journal — DOWNSTREAM-ORDER-READER-01 design

- Role: independent downstream-reader causal auditor and preregistration designer
- Run ID: `RUN-20260717-2255-DOWNSTREAM-ORDER-READER-01`
- Start: 2026-07-17 22:55:06 +02:00
- End: 2026-07-17 23:05:33 +02:00
- Starting Git state: clean isolated branch (renamed before commit to `codex/downstream-order-reader-01-design`) at exact accepted source-calibration result `6ae4a0e31d541f7bda1f424cb8682b960c979612`
- Ending Git state: clean dedicated branch at the final design commit after explicit staging and push; primary checkout unchanged
- Scheduled-run lock: not applicable; direct human design-only mission, no experiment launch
- Assigned scope: audit the exact downstream path; choose exactly one non-constitutive observable; freeze perturbation, sign, horizon, `lam_minus=0` ablation, practical margin and complete-world rules; produce a draft and recommendation without new seeds or outcomes.

## Files and evidence read

- `AGENTS.md`, research charter, project state, decision log, experiment/run indexes and the completed D-093 journal.
- `M_MINUS_ORDER_READER_00_PROTOCOL.md`, sign derivation, DEV report and bound result summary.
- Frozen `ScaffoldEngine._face_flux`, `MultiChannelMemoryEngine.step`, `DiagEngine`, no-swap collar implementation and parent exact-clone histories/manifest.
- Statistical-analysis skill instructions.

## Actions

1. Preserved the heavily dirty primary checkout and created a clean no-checkout sparse worktree from exact parent `6ae4a0e`; verified index-tree equality with HEAD.
2. Audited the engine scheduler. Current `m_minus` changes attractant at the end of a step, so the first affected transport is the following step's face flux.
3. Rejected direct `c` amount, feeding, morphology, centroid displacement and a multi-direction battery as the primary endpoint.
4. Selected exactly one observable: mass-specific +x transport from the exact material face flux under a matched local linear `c` ramp.
5. Froze `epsilon_c=0.01`, one source-expression plus one response update, `lam_minus=0` ablation, positive attenuation orientation, `0.0001` practical margin, `0.00005` ablation-equivalence margin, original-world inference, complete-block survival and `n>=18` feasibility.
6. Performed a geometry-only calculation, not a scientific outcome: the integer radius-10 disk has 317 cells and 296 internal +x faces; the proposed arms are nonnegative and add equal total `c`.
7. Wrote the causal audit, preregistration draft and `REVISE` recommendation. No engine history outcome, source world or prospective namespace was opened.
8. Ran the deterministic ramp-geometry assertion and the existing source-reader synthetic/binding suite: geometry PASS; 11 tests passed in 2.53 seconds. These checks initialized no source-world experiment.

## Reproducible design checks

```powershell
git rev-parse HEAD
git write-tree
# Both tree IDs matched before edits.

$py='C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe'
& $py -c "import numpy as np; n=64; R=10; yy,xx=np.indices((n,n)); dy=((yy-32+n//2)%n)-n//2; dx=((xx-32+n//2)%n)-n//2; K=dx*dx+dy*dy<=R*R; G=np.zeros((n,n)); G[K]=dx[K]/R; e=.01; A=[e*K*(1+a*G) for a in (-1,0,1)]; xf=K & np.roll(K,-1,axis=-1); assert K.sum()==317 and xf.sum()==296; assert all(z.min()>=0 for z in A); assert np.allclose([z.sum() for z in A],3.17,atol=1e-12,rtol=1e-10)"
# core cells 317; internal +x faces 296; equal arm totals; nonnegative additions
& $py -m pytest experiments/individuation/test_mminus_order_reader_dev.py -q
# 11 passed in 2.53 s
```

## OBSERVED

- `_face_flux` uses incoming `rho,c`; `q_c` is written only at the end of the update.
- The chemotactic term is `chi(cbar)*dc*rho_up*free_capacity`, plus a `c`-independent diffusion term.
- A direct integrated source contrast cannot determine the later flux because spatial gradients, saturation,
  upwind selection and density enter before transport.
- A multiplicative source-gain probe with `lam_minus=0` is vacuously zero. A common directional `c` probe remains
  responsive under `lam_minus=0` and therefore provides an informative ablation comparison.
- No new scientific outcome was generated.

## INFERRED

- The earliest non-constitutive functional reader is the executed chemotactic face flux, before tracker-derived
  movement, morphology or feeding add further causal layers.
- Higher EARLY source production should increase attractant saturation and attenuate response to a common ramp;
  spatial gradients and density may reverse this, making the sign genuinely falsifiable.
- Mass-specific transport is a physical velocity definition. It is not authorization to regress on, match by or
  otherwise statistically correct post-history body variables.

## HYPOTHESIS

Same-dose EARLY history produces a larger `lam_minus`-dependent attenuation of directional chemotactic transport
than LATE history, with the original-world order contrast exceeding `0.0001` lattice cells per response update.

## WHAT WOULD FALSIFY THIS?

- Source calibration passes but the downstream interval is within the practical null margin;
- the downstream order sign is reversed;
- the order response persists outside the `lam_minus=0` equivalence margin;
- dose levels disagree under the frozen consistency rule;
- or the logger, ramp, clamp, deterministic or complete-world gates fail.

## Failures and dead ends

- Whole-core inward boundary flux was rejected at design stage because the fixed radius-10 core can contain the
  entire body, making boundary-crossing flux a potentially vacuous endpoint.
- Source-gain continuation was rejected because its `lam_minus=0` arm is zero by construction and would repeat the
  constitutive-calibration weakness.
- Feeding, body equalization and post-history covariate correction were excluded by mission and causal scope.

## Decisions, unresolved risks and handoff

- Recommendation: `REVISE`, not GO or STOP.
- The reader/sign/margins are explicit but unsealed. A passive flux logger and synthetic fixtures must qualify
  before any scientific family can be considered.
- The `0.0001` and `0.00005` margins are pre-outcome scientific judgments and require human acceptance.
- No seed numbers are selected. No prospective run, 570xx continuation, feeding endpoint, additional direction,
  longer horizon, decoder, `BODY-EQUALIZATION`, ownership pair or active reconstruction is authorized.
- Exact next action: human review of the single reader, sign and margins; if approved, a separate code-only
  implementation/qualification authorization.
