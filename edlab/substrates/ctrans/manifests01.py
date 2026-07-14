"""THE v01 SPLIT and CHALLENGE MATRIX — EXP-GT-CONTINUOUS-FINGERPRINT-01.

COMMITTED BEFORE THE v01 INSTRUMENT EXISTS. Version 00's prospective hold-out is BURNED; nothing here reuses it as
a decisive case. `P_cascade` -- the pair that killed v00 -- appears ONLY as a DEVELOPMENT REGRESSION system
(`R_cascade_burned`, control T1) and never in the prospective set.

STRUCTURAL PROTECTION
  * seed namespaces      v01 dev 2xx_xxx | v01 prospective 8xx_xxx   (disjoint from v00's 1xx/9xx AND each other)
  * noise regimes        dev sigma 1.0e-5 | prospective {1.3e-5, 1.7e-5}  -- both UNSEEN in v00 and in v01 dev
  * topology reserved to prospective ONLY:  THIRD-ORDER cascade (`cascade_n` with three sites)
  * disjoint parameter grids on order, damping, time constants, delay, gain, hidden state, drift, amplitude, solver

THE DECLARED TAIL CONTRACT -- the load-bearing addition, and the thing v01 lives or dies by.

    TAU_MAX = 80    the slowest ACCESSIBLE relaxation time constant the instrument is qualified for
    D_MAX   = 60    the longest ACCESSIBLE transport delay; NO causal component may arrive later than
                    (probe end + D_MAX), which is why settling may not even be ASSESSED before then

TAU_MAX = 80 AGAINST A WINDOW OF 160 IS NOT AN ACCIDENT, AND MY FIRST CHOICE OF 40 WAS A MISTAKE WORTH RECORDING.
With TAU_MAX = 40 the window is FOUR time constants long, so every admissible system has already settled by the
end of it: measured remainder beyond the window, as a fraction of total transient energy -- V_cascade2 0.02%,
V_multi_strong 0.07%, the burned R_cascade 0.13%. Under that contract the tail bound is ALWAYS negligible, every
case is DECIDABLE_SETTLED, DECIDABLE_SLOW_TAIL never occurs, and the three-way distinction this experiment exists
to test would have been VACUOUS -- passing loudly while testing nothing. A benchmark cannot exercise a boundary it
has defined out of existence.

These are DECLARED, exactly as the noise scale is declared, and for the same reason: they are properties of the
DOMAIN, not quantities the instrument may infer from the system it is currently judging. A system outside them is
OUT OF CONTRACT and is refused -- which is an honest abstention, not a failure.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import systems as S
from . import tails as T

INDIST = "INDISTINGUISHABLE_UNDER_REPERTOIRE"
DIFFERENT = "DIFFERENT"
INDETERMINATE = "INDETERMINATE"

CONTINUITY, DIFFERENCE, FALSE_SAMENESS, FALSE_DIFFERENCE, ABSTAIN = (
    "CONTINUITY", "DIFFERENCE", "FALSE_SAMENESS", "FALSE_DIFFERENCE", "ABSTAIN")

DEV_SEED_BASE = 200_000
PROSP_SEED_BASE = 800_000

DEV_SIGMA = S.SIG0          # 1.0e-5
PROSP_SIGMA_A = 1.3e-5      # UNSEEN in v00 and in v01 development
PROSP_SIGMA_B = 1.7e-5      # UNSEEN

# ---- THE DECLARED TAIL CONTRACT (see module docstring)
TAU_MAX = 80.0
D_MAX = 60


@dataclass
class Case:
    cid: str
    left: str
    right: str
    category: str
    expect: dict
    why: str
    common_channel: bool = True
    tags: tuple = field(default_factory=tuple)


# =================================================================== DEVELOPMENT
def dev_systems() -> dict:
    sg = DEV_SIGMA
    base = T.first_order("V_leak", tau=0, T=8.0, gain=1.0, sigma=sg)
    ms = T.multiscale("V_multi_strong", T_fast=4.0, w_fast=1.0, T_slow=45.0, w_slow=1.40, gain=1.0, sigma=sg)
    return {
        # ---- first-order reference and its continuity partners (the PRESERVED v00 core)
        "V_leak": base,
        "V_leak_dead": S.dead_site("V_leak_dead", base, x0_5=0.6),
        "V_leak_units": S.with_units("V_leak_units", base, a=800.0, b=0.3),
        "V_leak_fine": S.with_refined_solver("V_leak_fine", base),
        "V_leak_shift": S.with_time_shift("V_leak_shift", base, k=1),
        "V_leak_reloc": S.relocate("V_leak_reloc", base, src=2, dst=3),
        # ---- preserved difference core: gain, sign, extra cause, hidden state, false sameness
        "V_leak_gain2": T.first_order("V_leak_gain2", T=8.0, gain=2.0, sigma=sg),
        "V_leak_sign": T.first_order("V_leak_sign", T=8.0, gain=1.0, sign=-1, sigma=sg),
        "V_supply": S.supply_cause("V_supply", base, w_s=0.9, site=3, T=7.0, gain=0.8),
        "V_mem_p": S.memory("V_mem_p", mem0=+1.0, T=8.0, Tm=5.0, gain=1.0, k_out=1.2, sigma=sg),
        "V_mem_m": S.memory("V_mem_m", mem0=-1.0, T=8.0, Tm=5.0, gain=1.0, k_out=1.2, sigma=sg),
        "V_hidden": S.hidden_mode("V_hidden", base, c_h=1.2, T=9.0),

        # ================= THE TAIL FAMILIES -- what v01 exists for =================
        # second-order cascade: a slow tail whose remainder is NEGLIGIBLE for the verdict
        "V_cascade2": T.cascade_n("V_cascade2", Ts=(6.0, 18.0), tau=0, gain=1.0, sigma=sg),
        # underdamped: RINGS forever-ish. "still moving" is YES at nearly every sample; the remainder is tiny.
        "V_underdamped": T.underdamped("V_underdamped", k=6.0, T2=6.0, T3=10.0, gain=1.0, sigma=sg),
        # delayed onset
        "V_delayed": T.first_order("V_delayed", tau=45, T=8.0, gain=1.0, sigma=sg),
        # THE TRAP: flat plateau, then a second component at delay 55 (inside D_MAX = 60)
        "V_delayed2": T.delayed_second("V_delayed2", d2=55, T1=5.0, T2=6.0, w2=0.9, gain=1.0, sigma=sg),
        "V_delayed2_w": T.delayed_second("V_delayed2_w", d2=55, T1=5.0, T2=6.0, w2=0.45, gain=1.0, sigma=sg),
        # WEAK long tail -- slow, and harmless to the verdict
        "V_multi_weak": T.multiscale("V_multi_weak", T_slow=60.0, w_slow=0.10, gain=1.0, sigma=sg),
        "V_multi_weak_g2": T.multiscale("V_multi_weak_g2", T_slow=60.0, w_slow=0.10, gain=2.0, sigma=sg),
        # STRONG long tail
        "V_multi_strong": ms,
        "V_multi_strong_g2": T.multiscale("V_multi_strong_g2", T_fast=4.0, T_slow=45.0, w_slow=1.40, gain=2.0, sigma=sg),
        # the difference lives ALMOST ENTIRELY IN THE TAIL: only the slow time constant differs
        "V_multi_tailonly": T.multiscale("V_multi_tailonly", T_fast=4.0, T_slow=79.0, w_slow=1.40, gain=1.0, sigma=sg),
        # ---- OUT OF THE DECLARED CONTRACT
        "V_slow_oos": T.out_of_contract_slow("V_slow_oos", T=300.0, gain=1.0, sigma=sg),   # tau > TAU_MAX
        "V_nonsettle": T.nonsettling("V_nonsettle", k=0.15, T=8.0, gain=1.0, sigma=sg),   # never settles
        # ---- BURNED-CASE REGRESSION (T1). P_cascade's EXACT parameters. DEVELOPMENT ONLY.
        "R_cascade_burned": T.cascade_n("R_cascade_burned", Ts=(7.0, 21.0), tau=2, gain=1.5, sigma=1.2e-5),
        "R_leak_burned": T.first_order("R_leak_burned", tau=6, T=13.0, gain=1.5, sigma=1.2e-5),

        # ---- preserved abstention core
        "V_silent_dead": S.silent_dead("V_silent_dead", sigma=sg),
        "V_silent_sat": S.silent_saturated("V_silent_sat", sigma=sg),
        "V_noisy": S.too_noisy("V_noisy", sigma_mult=250.0),
        "V_drifty": S.too_drifty("V_drifty", drift_frac=8.0, sigma=sg),
        "V_lowcov": S.access_restricted("V_lowcov", S.supply_cause("V_lowcov_src", base, w_s=0.9, site=3,
                                                                   T=7.0, gain=0.8), blocked=(S.DRIVE,)),
        "V_leak_loud": T.first_order("V_leak_loud", T=8.0, gain=1.0, sigma=sg * 4.0),
    }


DEV_CASES = [
    # ---------- PRESERVED CORE: continuity / false difference
    Case("W-D-01", "V_leak", "V_leak", FALSE_DIFFERENCE, {"limited": INDIST, "rich": INDIST},
         "the same system, measured twice", tags=("noise_reseed",)),
    Case("W-D-02", "V_leak", "V_leak_dead", CONTINUITY, {"limited": INDIST, "rich": INDIST},
         "an extra internal degree of freedom, invisible in both arms", tags=("microimplementation",)),
    Case("W-D-03", "V_leak", "V_leak_units", FALSE_DIFFERENCE, {"limited": INDIST, "rich": INDIST},
         "u -> 800u + 0.3. A change of units is not a causal difference.", tags=("units",)),
    Case("W-D-04", "V_leak", "V_leak_fine", FALSE_DIFFERENCE, {"limited": INDIST, "rich": INDIST},
         "solver refinement", tags=("solver",)),
    Case("W-D-05", "V_leak", "V_leak_shift", CONTINUITY, {"limited": INDIST, "rich": INDIST},
         "carrier time-origin shift", tags=("phase",)),
    Case("W-D-06", "V_leak", "V_leak_reloc", CONTINUITY, {"limited": INDIST, "rich": DIFFERENT},
         "same transfer function on a different internal address", tags=("microimplementation", "arm")),
    # ---------- PRESERVED CORE: difference
    Case("W-D-07", "V_leak", "V_leak_gain2", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "gain x2 -- must survive the noise-standardization that kills units", tags=("gain",)),
    Case("W-D-08", "V_leak", "V_leak_sign", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "sign inversion", tags=("sign",)),
    Case("W-D-09", "V_leak", "V_supply", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "an independently controllable additional cause", tags=("cause",)),
    Case("W-D-10", "V_mem_p", "V_mem_m", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "genuine hidden state", tags=("hidden_state",)),
    Case("W-D-11", "V_leak", "V_hidden", FALSE_SAMENESS, {"limited": INDIST, "rich": DIFFERENT},
         "an uncontrollable internal mode: EQUIVALENCE_CLASS_ONLY under limited access", tags=("collision",)),

    # ================= TAIL CASES -- the reason version 01 exists =================
    Case("W-D-12", "V_leak", "V_cascade2", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "SECOND-ORDER CASCADE. Its tail is still moving at the window's end. Version 00 abstained on exactly this "
         "shape. The remainder is bounded and cannot cross the decision boundary: DECIDABLE_SLOW_TAIL.",
         tags=("slow_tail", "T3")),
    Case("W-D-13", "V_leak", "V_underdamped", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "UNDERDAMPED RINGING. 'Is the signal still moving?' answers YES at nearly every sample and is therefore "
         "the wrong question. The remaining ENERGY is what matters, and it is negligible.", tags=("slow_tail",)),
    Case("W-D-14", "V_multi_weak", "V_multi_weak_g2", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "a WEAK long tail, and a gain difference that dwarfs it. Slow, and harmless to the verdict.",
         tags=("slow_tail", "T3")),
    Case("W-D-15", "V_multi_strong", "V_multi_strong_g2", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "a STRONG long tail, and a gain difference that still dwarfs it. Bounded, therefore decidable.",
         tags=("slow_tail", "T3")),
    Case("W-D-16", "V_multi_strong", "V_multi_tailonly", ABSTAIN, {"limited": INDETERMINATE,
                                                                   "rich": INDETERMINATE},
         "THE DIFFERENCE LIVES ALMOST ENTIRELY IN THE TAIL: only the SLOW time constant differs (45 vs 79), so the "
         "observed window barely separates them while the unseen remainder carries the answer. The bound must "
         "STRADDLE the decision boundary and the instrument must abstain. This is T4, and it is the case a "
         "threshold-raising 'fix' to version 00 would have got wrong.", tags=("near_boundary", "T4")),
    Case("W-D-17", "V_delayed2", "V_delayed2_w", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "THE TRAP (T5). Both have a flat plateau and then a SECOND component at delay 55, inside D_MAX=60. They "
         "differ ONLY in that second component. A guard that stops when the derivative goes quiet stops in the "
         "plateau and never hears it.", tags=("delay_horizon", "T5")),
    Case("W-D-18", "V_leak", "V_delayed", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "delayed onset (transport delay 45)", tags=("latency",)),

    # ---------- T1: THE BURNED CASE, as a DEVELOPMENT REGRESSION ONLY
    Case("W-D-19", "R_leak_burned", "R_cascade_burned", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "T1 -- THE PAIR THAT KILLED VERSION 00, with its exact parameters, as a DEVELOPMENT REGRESSION. v00 "
         "measured 64.15 against a radius of 23.36 and then abstained, because its tail moved by 5.3% against a "
         "frozen 5% threshold. v01 may classify it ONLY if its uncertainty bound PROVES the verdict cannot change. "
         "Passing it by hard-coded exception is forbidden.", tags=("burned_regression", "T1")),

    # ---------- OUT OF CONTRACT / abstention
    Case("W-D-20", "V_slow_oos", "V_leak", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "relaxation slower than the DECLARED TAU_MAX=40. Out of contract; refused BY CONTRACT, not by accident. "
         "T2 -- a genuinely unresolved response.", tags=("out_of_contract", "T2")),
    Case("W-D-21", "V_nonsettle", "V_leak", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "a response that NEVER settles (undamped oscillator). There is no bound to be had. T2.",
         tags=("nonsettling", "T2")),
    Case("W-D-22", "V_silent_dead", "V_leak", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "zero output gain: silence is not a fingerprint", tags=("silent",)),
    Case("W-D-23", "V_silent_dead", "V_silent_sat", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "two silent systems are not the same system", tags=("silent", "vacuity")),
    Case("W-D-24", "V_noisy", "V_leak", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "below its own noise floor: unreadable, not indistinguishable. T6.", tags=("noise", "T6")),
    Case("W-D-25", "V_drifty", "V_leak", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "nonstationary baseline. Drift must not be read as unresolved causal response. T6.",
         tags=("drift", "T6")),
    Case("W-D-26", "V_lowcov", "V_leak", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "the drive line is unreachable: coverage below the floor", tags=("coverage",)),
    Case("W-D-27", "V_leak", "V_leak_loud", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "measurement-contract violation: a 4x noisier channel", common_channel=False, tags=("contract",)),
]


# =================================================================== PROSPECTIVE (RESERVED — NOT RUN)
def prospective_systems() -> dict:
    """PROSPECTIVE GRID -- disjoint from v01 development on every axis, and NOT reusing v00's burned hold-out.

        order        dev {1st, 2nd}          -> prospective ADDS **THIRD-ORDER CASCADE** (never seen)
        damping      dev k=6.0               -> prospective k=11.0
        T            dev {4,5,6,8,10,18,45,60,79} -> prospective {5,9,15,24,50,66,77}
        out-of-contract tau  dev 300 | prospective 280  -- BOTH >= 3.5 * TAU_MAX. See the declared
        resolution limit in cfingerprint01: the contract CHECK cannot separate tau=130 from TAU_MAX=80,
        so an out-of-contract system placed at 130 would be asking the check to do something it
        provably cannot. The benchmark tests what the instrument can do, and the unverifiable band
        (TAU_MAX, ~2.5*TAU_MAX) is reported as UNVERIFIED SCOPE rather than quietly assumed away.
        delay        dev {0,45,55}           -> prospective {12,38,52}
        gain         dev {1.0, 2.0}          -> prospective {1.6, 2.8}
        w_slow       dev {0.10, 1.40}        -> prospective {0.28, 1.30}
        slow tau     dev {45, 60, 79}        -> prospective {50, 66, 77}   (all <= TAU_MAX = 80)
        sigma        dev {1.0e-5}            -> prospective {1.3e-5, 1.7e-5}   UNSEEN
        solver       dev {4}                 -> prospective ALSO {8} (refinement case)
        P_cascade    **NOT PRESENT.** Burned. Development regression only.
    """
    sa, sb = PROSP_SIGMA_A, PROSP_SIGMA_B
    base = T.first_order("Q_leak", tau=12, T=9.0, gain=1.6, sigma=sa)
    return {
        "Q_leak": base,
        "Q_leak_dead": S.dead_site("Q_leak_dead", base, x0_5=-0.35),
        "Q_leak_units": S.with_units("Q_leak_units", base, a=180.0, b=-0.05),
        "Q_leak_fine": S.with_refined_solver("Q_leak_fine", base),
        "Q_leak_shift": S.with_time_shift("Q_leak_shift", base, k=2),
        "Q_leak_reloc": S.relocate("Q_leak_reloc", base, src=2, dst=4),
        "Q_leak_gain28": T.first_order("Q_leak_gain28", tau=12, T=9.0, gain=2.8, sigma=sa),
        "Q_leak_sign": T.first_order("Q_leak_sign", tau=12, T=9.0, gain=1.6, sign=-1, sigma=sa),
        "Q_supply": S.supply_cause("Q_supply", base, w_s=1.1, site=3, T=15.0, gain=1.0),
        "Q_mem_p": S.memory("Q_mem_p", mem0=+1.0, w_drive=0.60, T=9.0, Tm=6.0, gain=1.6, c_mem=1.1,
                            k_out=1.5, tau=0, sigma=sa),
        "Q_mem_m": S.memory("Q_mem_m", mem0=-1.0, w_drive=0.60, T=9.0, Tm=6.0, gain=1.6, c_mem=1.1,
                            k_out=1.5, tau=0, sigma=sa),
        "Q_hidden": S.hidden_mode("Q_hidden", base, c_h=0.9, T=15.0),

        # ---- TAIL FAMILIES, unseen combinations
        # THE RESERVED TOPOLOGY: a THIRD-ORDER cascade. Development never saw one.
        "Q_cascade3": T.cascade_n("Q_cascade3", Ts=(5.0, 15.0, 24.0), tau=0, gain=1.6, sigma=sa),
        "Q_cascade2": T.cascade_n("Q_cascade2", Ts=(9.0, 24.0), tau=0, gain=1.6, sigma=sa),
        "Q_underdamped": T.underdamped("Q_underdamped", k=11.0, T2=9.0, T3=15.0, gain=1.6, sigma=sa),
        "Q_delayed": T.first_order("Q_delayed", tau=38, T=9.0, gain=1.6, sigma=sa),
        "Q_delayed2": T.delayed_second("Q_delayed2", d2=52, T1=5.0, T2=9.0, w2=0.85, gain=1.6, sigma=sa),
        "Q_delayed2_w": T.delayed_second("Q_delayed2_w", d2=52, T1=5.0, T2=9.0, w2=0.40, gain=1.6, sigma=sa),
        "Q_multi_weak": T.multiscale("Q_multi_weak", T_fast=5.0, T_slow=66.0, w_slow=0.28, gain=1.6, sigma=sa),
        "Q_multi_weak_g": T.multiscale("Q_multi_weak_g", T_fast=5.0, T_slow=66.0, w_slow=0.28, gain=2.8,
                                       sigma=sa),
        "Q_multi_strong": T.multiscale("Q_multi_strong", T_fast=5.0, T_slow=50.0, w_slow=1.30, gain=1.6,
                                       sigma=sb),
        "Q_multi_strong_g": T.multiscale("Q_multi_strong_g", T_fast=5.0, T_slow=50.0, w_slow=1.30, gain=2.8,
                                         sigma=sb),
        # the difference lives almost entirely in the TAIL (slow T only): must abstain
        "Q_multi_tailonly": T.multiscale("Q_multi_tailonly", T_fast=5.0, T_slow=77.0, w_slow=1.30, gain=1.6,
                                         sigma=sb),
        # ---- out of contract
        "Q_slow_oos": T.out_of_contract_slow("Q_slow_oos", T=280.0, gain=1.6, sigma=sa),
        "Q_nonsettle": T.nonsettling("Q_nonsettle", k=0.22, T=9.0, gain=1.6, sigma=sa),
        # ---- abstention core
        "Q_silent_dead": S.silent_dead("Q_silent_dead", tau=12, T=9.0, gain=1.6, sigma=sa),
        "Q_silent_sat": S.silent_saturated("Q_silent_sat", sigma=sa),
        "Q_noisy": S.too_noisy("Q_noisy", sigma_mult=300.0, tau=12, T=9.0, gain=1.6),
        "Q_drifty": S.too_drifty("Q_drifty", drift_frac=9.0, tau=12, T=9.0, gain=1.6, sigma=sa),
        "Q_lowcov": S.access_restricted("Q_lowcov", S.supply_cause("Q_lowcov_src", base, w_s=1.1, site=3,
                                                                   T=15.0, gain=1.0), blocked=(S.DRIVE,)),
        "Q_leak_loud": T.first_order("Q_leak_loud", tau=12, T=9.0, gain=1.6, sigma=sa * 4.0),
    }


PROSPECTIVE_CASES = [
    Case("W-P-01", "Q_leak", "Q_leak", FALSE_DIFFERENCE, {"limited": INDIST, "rich": INDIST},
         "same system, re-measured", tags=("noise_reseed",)),
    Case("W-P-02", "Q_leak", "Q_leak_dead", CONTINUITY, {"limited": INDIST, "rich": INDIST},
         "extra invisible internal DOF", tags=("microimplementation",)),
    Case("W-P-03", "Q_leak", "Q_leak_units", FALSE_DIFFERENCE, {"limited": INDIST, "rich": INDIST},
         "u -> 180u - 0.05", tags=("units",)),
    Case("W-P-04", "Q_leak", "Q_leak_fine", FALSE_DIFFERENCE, {"limited": INDIST, "rich": INDIST},
         "solver refinement", tags=("solver",)),
    Case("W-P-05", "Q_leak", "Q_leak_shift", CONTINUITY, {"limited": INDIST, "rich": INDIST},
         "carrier shift", tags=("phase",)),
    Case("W-P-06", "Q_leak", "Q_leak_reloc", CONTINUITY, {"limited": INDIST, "rich": DIFFERENT},
         "relocated machinery", tags=("microimplementation", "arm")),
    Case("W-P-07", "Q_leak", "Q_leak_gain28", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "gain 1.6 -> 2.8", tags=("gain",)),
    Case("W-P-08", "Q_leak", "Q_leak_sign", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "sign inversion", tags=("sign",)),
    Case("W-P-09", "Q_leak", "Q_supply", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "independently controllable additional cause", tags=("cause",)),
    Case("W-P-10", "Q_mem_p", "Q_mem_m", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "hidden state, prospective", tags=("hidden_state",)),
    Case("W-P-11", "Q_leak", "Q_hidden", FALSE_SAMENESS, {"limited": INDIST, "rich": DIFFERENT},
         "uncontrollable mode: EQUIVALENCE_CLASS_ONLY under limited access", tags=("collision",)),

    # ---- TAIL: the decisive prospective cases. NOT P_cascade.
    Case("W-P-12", "Q_leak", "Q_cascade3", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "THE RESERVED TOPOLOGY: a THIRD-ORDER cascade, an order development never saw. Its tail is slower still. "
         "The bound must prove the verdict cannot change: DECIDABLE_SLOW_TAIL.",
         tags=("slow_tail", "unseen_topology")),
    Case("W-P-13", "Q_leak", "Q_cascade2", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "second-order cascade at unseen time constants -- the shape that killed v00", tags=("slow_tail",)),
    Case("W-P-14", "Q_leak", "Q_underdamped", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "underdamped ringing at unseen damping", tags=("slow_tail",)),
    Case("W-P-15", "Q_multi_weak", "Q_multi_weak_g", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "weak long tail + a gain difference that dwarfs it", tags=("slow_tail",)),
    Case("W-P-16", "Q_multi_strong", "Q_multi_strong_g", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "STRONG long tail at the ELEVATED unseen noise level, with a gain difference that still dwarfs it",
         tags=("slow_tail", "noise_regime")),
    Case("W-P-17", "Q_multi_strong", "Q_multi_tailonly", ABSTAIN, {"limited": INDETERMINATE,
                                                                   "rich": INDETERMINATE},
         "the difference lives almost entirely in the UNSEEN TAIL (slow T 34 vs 41). The bound must straddle the "
         "boundary and the instrument must abstain.", tags=("near_boundary",)),
    Case("W-P-18", "Q_delayed2", "Q_delayed2_w", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "the delay-horizon trap at an unseen delay (52) and unseen weights", tags=("delay_horizon",)),
    Case("W-P-19", "Q_leak", "Q_delayed", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "delayed onset, unseen delay", tags=("latency",)),

    # ---- out of contract / abstention
    Case("W-P-20", "Q_slow_oos", "Q_leak", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "relaxation slower than the declared TAU_MAX", tags=("out_of_contract",)),
    Case("W-P-21", "Q_nonsettle", "Q_leak", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "never settles", tags=("nonsettling",)),
    Case("W-P-22", "Q_silent_dead", "Q_leak", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "zero gain", tags=("silent",)),
    Case("W-P-23", "Q_silent_dead", "Q_silent_sat", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "two silent systems", tags=("silent", "vacuity")),
    Case("W-P-24", "Q_noisy", "Q_leak", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "below its own noise floor", tags=("noise",)),
    Case("W-P-25", "Q_drifty", "Q_leak", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "nonstationary baseline", tags=("drift",)),
    Case("W-P-26", "Q_lowcov", "Q_leak", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "drive line unreachable", tags=("coverage",)),
    Case("W-P-27", "Q_leak", "Q_leak_loud", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "measurement-contract violation", common_channel=False, tags=("contract",)),
]
