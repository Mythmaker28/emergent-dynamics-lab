# TAIL-UNCERTAINTY CONTRACT — EXP-GT-CONTINUOUS-FINGERPRINT-01

## The question the guard must answer

| version 00 asked | version 01 must ask |
|---|---|
| **Is the signal still moving?** | **Can the unobserved remainder still change the verdict?** |

A signal may be moving and its remainder be irrelevant (an underdamped tail rings at almost every sample and
carries nothing). A signal may look perfectly still and its remainder be decisive (**a very slow relaxation is
nearly FLAT inside the window and carries the most remainder of all**). The two questions come apart, and v00 died
in that gap.

## The declared contract — properties of the DOMAIN, not of the system being judged

```
TAU_MAX = 80    the slowest ACCESSIBLE relaxation the instrument is qualified for
D_MAX   = 60    the longest ACCESSIBLE transport delay
T_TAIL0 = 84    = D_HOLD + D_MAX. SETTLING MAY NOT BE ASSESSED BEFORE THIS.
L_MAX   = 480   the longest extension over which a remainder may be buried
```

`T_TAIL0` is what defeats the delayed-second-component trap: no causal component may arrive later than the probe's
end plus `D_MAX`, so before `t = 84` a flat response may still have a second cause on the way.

**`TAU_MAX = 80` against a `W = 160` window is deliberate.** At `TAU_MAX = 40` the window is four time constants
long, every admissible system has already settled by its end (measured remainder beyond `W`: cascade2 **0.02%**,
multi-strong **0.07%**, the burned cascade **0.13%**), and the three-way distinction would be **vacuous**.

## The method — bound the eventual distance; never model the tail

On the **difference** trace `delta = z_A - lambda*z_B` (the only thing the verdict depends on), over three
sub-blocks of the tail region:

1. **Contract checks** (is this a bounded relaxation at all?)
   `d2 <= rho_max*d1 + LVL_K*sd` — the level decays at least as fast as `TAU_MAX`
   `rip3 <= rho_max*rip2 + RIP_K*sig` — the ripple damps at least as fast (this is what carries an underdamped tail)
   Either failing -> **OUT OF CONTRACT**, `d_lo = 0`, `d_hi = inf`, abstain. **No bound is invented.**
2. **Worst-case envelope** (assume the slowest decay the contract permits — the rate is never fitted)
   `R = (d2 + BOUND_K*sd) * rho_max/(1-rho_max)` · `B = R + max(0, rip3 - RIP_NOISE_K*sig)`
3. **Bracket the extended distance.** `d_ext = sqrt((W*d_obs^2 + K*rho^2)/(W+K))` is monotone in `rho`, so
   bracketing `rho in [max(0,|delta_inf|-B), |delta_inf|+B]` brackets `d_ext`. Aggregate with the preserved **max**.
4. **Read the verdict off the bracket.** `D_hi <= r_cont` -> INDISTINGUISHABLE · `D_lo >= r_sep` -> DIFFERENT ·
   otherwise the bracket **straddles a boundary** -> `INDETERMINATE_IN_FLIGHT`.

**A single unbounded block is not outvoted by well-behaved ones.** The representation assumes containment; if one
probe's tail is not a bounded relaxation, that assumption has failed *for this system*, and a bound computed on
the blocks that happen to look convergent is a bound on a contract the system does not honour.

## Constants — all calibrated on NOISE-ONLY blocks. No label was consulted.

288 blocks from systems that **cannot respond**:

| statistic on pure noise | mean | q99.9 | max | frozen |
|---|---|---|---|---|
| level check `(d2-rho*d1)/sd_eff` | +0.31 | 3.44 | **3.49** | `LVL_K = 5.0` |
| ripple check `(rip3-rho*rip2)/sig` | +0.61 | 2.17 | **2.23** | `RIP_K = 3.0` |
| **remaining envelope `B`** | 3.76 | 7.39 | **7.40** | `TAIL_NOISE = 9.0` |

`BOUND_K = 2.0` is the **upper-confidence multiplier on the decrement** and is deliberately **not** the same
number as the check bars. A *check* needs a high bar (it must not fire across thousands of blocks by accident); a
*bound* needs an ordinary one (a 6-sigma bound on a decrement whose noise is 0.6 inflates the remainder estimate to
~15 units **on pure noise** and drowns the thing it is bounding). Conflating them is not conservatism; it is noise.

---

# TWO LIMITS THAT ARE NOT BUGS, AND WHICH KILL THIS VERSION

## 1. THE RESOLUTION FLOOR — measured, and fatal

`TAIL_NOISE = 9.0` is not merely a threshold. **It is the smallest remainder this bound can see.** Below it, a
real slow tail and a genuinely settled one are the same observation.

**The T4 near-boundary pair — built so that a real ~10% of its difference energy lies BEYOND the window, confirmed
by the privileged path — produces a measured remaining envelope of 8.25.** That is *inside* the floor. The bound
cannot see it, calls the tail `DECIDABLE_SETTLED`, and returns a **confident DIFFERENT** on a pair whose answer is
still partly outside the window.

**This is the same class of error as version 00's, in the opposite direction, and it is the case that
distinguishes a principled tail guard from a threshold-raising hack.** Failing it means the method is not
demonstrated.

**The floor is set by the length of the tail region (76 samples) against the noise on a sub-block mean.** The fix
is more tail leverage — a longer observation window — which is a **battery change** and therefore a **new, broader
instrument**. It is not made here.

## 2. THE CONTRACT CHECK'S POWER — measured, and declared

The out-of-contract test compares a per-sub-block decay factor against `rho_max = exp(-L/TAU_MAX) = 0.732`. A
system at `tau = 130` — well outside the contract — decays at **0.825**. The two differ by 0.09 per sub-block while
the noise on the decrement that carries them is comparable.

> **The check reliably detects `tau` greater than roughly `2.5 x TAU_MAX`. In the band `(TAU_MAX, ~2.5*TAU_MAX)` a
> system may be silently accepted as in-contract — and the bound, which ASSUMES `tau <= TAU_MAX`, is then TOO
> TIGHT.**

That is a **soundness** limit, not a tuning choice. It is stated here rather than discovered later by someone else.
Even at `tau = 300` the check fails to fire in the **limited** arm (W-D-20), because its power scales with the tail
level and the limited repertoire does not drive the system hard enough.

**UNVERIFIED SCOPE:** systems with relaxation between `TAU_MAX` and `~2.5 x TAU_MAX`. The instrument's bound is not
sound there and it cannot tell that it is not.
