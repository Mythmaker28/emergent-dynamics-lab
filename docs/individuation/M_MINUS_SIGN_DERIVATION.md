# M_MINUS sign derivation

Mission: `COUNTERFACTUAL-HISTORY-MECHANISM-RECONCILIATION-00`

Parent result: `ea6e6a0ab2ccc3e94eba364ddb459088c96d6033`
Verdict: **the frozen negative orientation is a convention/theory error in the intended two-timescale scalar interpretation.** The exact nonlinear spatial engine does not furnish an amplitude-only sign theorem, but its observed component decomposition agrees with the corrected positive orientation. This is a theory correction, not a discovery.

## Exact update implemented by the engine

Let `Mf_k = rho m_k`. Each step first transports `rho` and `Mf_k` with the same donor face flux. If superscript `T` denotes the transported fields,

`m_k^T(x) = Mf_k^T(x) / max(rho^T(x), eps)`.

Growth inherits the local intensive value:

`Mf_k^G = Mf_k^T + g m_k^T = (rho^T + g) m_k^T`.

The common death multiplier is then applied to both `rho` and `Mf`, so neither growth inheritance nor uniform death changes the intensive `m_k`. The engine next computes

`Psi_t(x) = tanh(k_exp [N_t(x) - c_t(x)] + k_up [uptake_t(x) - up_ref_t])`,

where `up_ref_t` is the mean uptake over alive cells. Its exact intensive-memory update is

`m_{k,t+1}(x) = alive(x) clip(m_k^T(x) + dt alive(x) [eta_w Psi_t(x) - eta_dk m_k^T(x) + eta_t (Tmean(m_k^T)(x) - m_k^T(x)) + D_m Lap(m_k^T)(x)], -1, 1)`.

The readouts are

- `m_plus = tanh(m1 + m2)` for uptake;
- `m_minus = tanh(m1 - m2)` for attractant production.

Frozen parameters used by the parent experiment are `dt=0.1`, `eta_w=0.015`, `eta_d1=0.35`, `eta_d2=0.006`, `eta_t=0.010`, `D_m=0.010`, `k_exp=1.0`, `k_up=1.0`, `lam_plus=0.25`, and `lam_minus=0.15`.

## Homogeneous scalar recurrence

For the minimal theory check, omit transport gradients, templating, diffusion, clipping, and the endogenous transformation from applied amplitude to `Psi`. Let the scalar episode input be `x_t`. Then

`m_{k,t+1} = q_k m_{k,t} + w x_t`,

with `q_k = 1 - dt eta_dk` and `w = dt eta_w`. Thus `q1=0.965`, `q2=0.9994`, and `w=0.0015`.

For first episode amplitude `a`, second episode amplitude `b`, episode duration `T=60`, post-history settle `S=120`, and common initial value `m_k(0)`, define

`A_T(q) = (1 - q^T) / (1 - q)`.

The closed form after both episodes and settle is

`m_k(a,b) = q_k^(2T+S) m_k(0) + w A_T(q_k) [a q_k^(T+S) + b q_k^S]`.

For EARLY `(h,l)` versus LATE `(l,h)`, with `Delta=h-l>0`, the unchanged EARLY-minus-LATE contrast is

`delta m_k = m_k(h,l) - m_k(l,h)`

`= w Delta A_T(q_k) q_k^S (q_k^T - 1)`

`= -w Delta q_k^S (1-q_k^T)^2 / (1-q_k) < 0`.

Both components are therefore individually lower for EARLY. The order sign of their difference depends on which negative response is larger:

`delta(m1-m2) = delta m1 - delta m2`.

With the frozen rates and `Delta=0.01`:

| quantity | scalar value |
|---|---:|
| `delta m1` | `-4.6377041581e-06` |
| `delta m2` | `-2.9102795171e-05` |
| `delta(m1-m2)` before `tanh` | `+2.4465091013e-05` |
| factorial `m_minus` order after `tanh` | `+2.4464801452e-05` |
| factorial `m_plus` order after `tanh` | `-3.3740094135e-05` |

The slow component retains the first episode through the long settle far more strongly than the fast component. Its negative EARLY-minus-LATE contrast dominates, so subtracting `m2` makes the `m_minus` contrast positive. Low and high dose have the same `Delta=0.01`, hence the same scalar sign and nearly the same scalar magnitude.

The iterative scalar recurrence matches this closed form with maximum absolute error below `6e-18`. It does not initialize a world or read a feeding outcome.

## Reconciliation with the frozen data

At the frozen deep pre-probe checkpoint across the 17 complete original worlds:

- `m1` order: mean `+1.67857e-05`, 95% t interval `[-1.57586e-05, +4.93299e-05]`;
- `m2` order: mean `-0.00388338`, interval `[-0.00451043, -0.00325634]`, 17/17 negative;
- `m_plus` order: mean `-0.00361610`, interval `[-0.00425625, -0.00297595]`, 17/17 negative;
- `m_minus` order: mean `+0.00366789`, interval `[+0.00306355, +0.00427224]`, 17/17 positive.

That decomposition is exactly the qualitative mechanism exposed by the corrected scalar recurrence: the slow `m2` order response dominates `m1`, making `m1-m2` positive. The observed magnitude is not predicted by the toy recurrence because the real `Psi` is endogenous and the field is transported, spatially coupled, and measured on an evolving body.

## Exact classification

1. The frozen negative `m_minus` orientation was **not mathematically justified** by the intended two-timescale scalar theory.
2. Keeping the frozen EARLY-minus-LATE contrast unchanged, the reduced recurrence predicts a **positive** orientation. This is a convention/theoretical correction, not a post-outcome sign flip.
3. From the exact spatial equations and amplitudes alone, the sign is **not globally identifiable without the trajectory**, because `Psi`, transport, spatial operators, clipping, survival, and the readout mask are endogenous.
4. The same-manifest observations support a small positive order-sensitive state, but order feeding remains unestablished. Therefore the sign correction does not establish order memory, local ownership, or a causal landscape.
