"""THE DEVELOPMENT / PROSPECTIVE SPLIT, and the CONSTRUCTION-DECLARED CHALLENGE MATRIX.

WRITTEN AND COMMITTED BEFORE THE INSTRUMENT EXISTS. That is the point of it. A split declared afterwards is a
split declared by someone who already knows the answer.

STRUCTURAL PROTECTION, NOT CONVENTION:
  * disjoint SEED NAMESPACES               dev 1xx_xxx | prospective 9xx_xxx
  * disjoint PARAMETER GRIDS               no prospective system is parameter-identical to any dev system
  * a topology that exists ONLY prospectively   `feedback_sat` -- feedback around a saturating element
  * unseen NOISE REGIMES                   dev sigma = 1.0e-5 | prospective sigma in {1.2e-5, 1.6e-5}
  * the prospective experiment REFUSES TO RUN unless the freeze manifest's file hashes match on disk.

DECLARED FAMILY REUSE, AND THE CLAIM IT COSTS. The prospective set reuses the COMPONENT LIBRARY -- leaky sites,
transport delays, saturating readouts, a bistable memory, feedback, tapped delay lines, an uncontrollable mode. It
does not reuse a single parameter vector, and it adds one topology development never saw. This reuse is DECLARED
HERE, BEFORE EXECUTION, and the claim is bounded accordingly: what may be qualified is a fingerprint for
CONTINUOUS RESPONSES OF SYSTEMS DRAWN FROM THIS COMPONENT LIBRARY. It is not a claim about continuous systems in
general, and it is not a claim about droplets.

THE MEASUREMENT-NOISE CONTRACT, AND A THEOREM THAT FORCES IT.

    If the readout may be rescaled by an unknown a>0, the ONLY scale the instrument can calibrate against is the
    channel's own noise floor. Therefore: a system whose noise floor is halved is, to this instrument, EXACTLY as
    indistinguishable from a system whose gain is doubled. That is not an implementation defect. It is a THEOREM
    about the declared nuisance group -- absolute gain is not identifiable when both the output scale AND the
    noise scale are free.

So the noise SCALE is NOT a nuisance. It is part of the DECLARED MEASUREMENT CONTRACT: a comparison is admissible
only if the two systems are declared to sit on a COMMON NOISE CHANNEL. `common_channel=False` cases exist in both
splits and the admission layer must REFUSE them. Must-fail control L8 disables that refusal and shows the false
difference walk in. The droplet mapping will have to establish this contract PHYSICALLY -- which is precisely why
'field noise' already sits on the unresolved list in the domain-admission contract.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import systems as S

INDIST = "INDISTINGUISHABLE_UNDER_REPERTOIRE"
DIFFERENT = "DIFFERENT"
INDETERMINATE = "INDETERMINATE"

CONTINUITY = "CONTINUITY"
DIFFERENCE = "DIFFERENCE"
FALSE_SAMENESS = "FALSE_SAMENESS"
FALSE_DIFFERENCE = "FALSE_DIFFERENCE"
ABSTAIN = "ABSTAIN"

DEV_SEED_BASE = 100_000
PROSP_SEED_BASE = 900_000

DEV_SIGMA = S.SIG0                       # 1.0e-5
PROSP_SIGMA_A = 1.2e-5                   # 1.2x dev -- UNSEEN
PROSP_SIGMA_B = 1.6e-5                   # 1.6x dev -- UNSEEN


@dataclass
class Case:
    cid: str
    left: str
    right: str
    category: str
    expect: dict                          # {"limited": verdict, "rich": verdict}
    why: str
    common_channel: bool = True           # the DECLARED measurement contract
    left_seed: int = 0                    # offset within the split's seed namespace
    right_seed: int = 1
    tags: tuple = field(default_factory=tuple)


# =================================================================== DEVELOPMENT SPLIT
def dev_systems() -> dict:
    """dev grid:  tau in {0,4,8} | T in {5,8,16} | gain in {1.0,2.0} | k_out in {0,1.2} | fb k = 0.5 | sigma 1.0e-5
    """
    base = S.leak("D_leak", tau=0, T=8.0, gain=1.0, sigma=DEV_SIGMA)
    fb = S.feedback("D_fb", k=0.5, T2=6.0, T3=10.0, gain=1.0, sigma=DEV_SIGMA)
    mem_p = S.memory("D_mem_p", mem0=+1.0, T=8.0, Tm=5.0, gain=1.0, k_out=1.2, sigma=DEV_SIGMA)
    sysmap = {
        "D_leak": base,
        # --- continuity partners
        "D_leak_dead": S.dead_site("D_leak_dead", base, x0_5=0.7),
        "D_leak_units": S.with_units("D_leak_units", base, a=1000.0, b=0.5),
        "D_leak_fine": S.with_refined_solver("D_leak_fine", base),
        "D_leak_shift": S.with_time_shift("D_leak_shift", base, k=1),
        "D_leak_reloc": S.relocate("D_leak_reloc", base, src=2, dst=3),
        # --- difference partners
        "D_leak_gain2": S.leak("D_leak_gain2", tau=0, T=8.0, gain=2.0, sigma=DEV_SIGMA),
        "D_leak_sign": S.leak("D_leak_sign", tau=0, T=8.0, gain=1.0, sign=-1, sigma=DEV_SIGMA),
        "D_leak_tau8": S.leak("D_leak_tau8", tau=8, T=8.0, gain=1.0, sigma=DEV_SIGMA),
        "D_leak_T16": S.leak("D_leak_T16", tau=0, T=16.0, gain=1.0, sigma=DEV_SIGMA),
        "D_cascade": S.cascade("D_cascade", tau=0, T2=5.0, T3=10.0, gain=1.0, sigma=DEV_SIGMA),
        "D_sat": S.satsys("D_sat", tau=0, T=8.0, gain=1.0, k_out=1.2, sigma=DEV_SIGMA),
        "D_fb": fb,
        "D_fir": S.fir("D_fir", taps=((0, 1.0), (4, -0.5), (8, 0.25)), T=2.0, gain=1.0, sigma=DEV_SIGMA),
        "D_mem_p": mem_p,
        "D_mem_m": S.memory("D_mem_m", mem0=-1.0, T=8.0, Tm=5.0, gain=1.0, k_out=1.2, sigma=DEV_SIGMA),
        "D_supply": S.supply_cause("D_supply", base, w_s=0.9, site=3, T=7.0, gain=0.8),
        # --- the false-sameness construction
        "D_hidden": S.hidden_mode("D_hidden", base, c_h=1.2, T=9.0),
        # --- abstention cases
        "D_silent_dead": S.silent_dead("D_silent_dead", sigma=DEV_SIGMA),
        "D_silent_sat": S.silent_saturated("D_silent_sat", sigma=DEV_SIGMA),
        "D_noisy": S.too_noisy("D_noisy", sigma_mult=250.0),
        "D_slow": S.too_slow("D_slow", T=110.0, sigma=DEV_SIGMA),
        "D_drifty": S.too_drifty("D_drifty", drift_frac=8.0, sigma=DEV_SIGMA),
        # --- INTERVENTION ACCESS: the battery is identical; some probes simply cannot be applied
        "D_lowcov": S.access_restricted("D_lowcov", S.supply_cause("D_lowcov_src", base, w_s=0.9, site=3,
                                                           T=7.0, gain=0.8), blocked=(S.DRIVE,)),
        # --- the measurement-contract violation (a DIFFERENT NOISE FLOOR, same system)
        "D_leak_loud": S.leak("D_leak_loud", tau=0, T=8.0, gain=1.0, sigma=DEV_SIGMA * 4.0),
    }
    return sysmap


DEV_CASES = [
    # ---------------- CONTINUITY / FALSE DIFFERENCE: these must NOT be called different
    Case("C-DEV-01", "D_leak", "D_leak", FALSE_DIFFERENCE, {"limited": INDIST, "rich": INDIST},
         "the SAME system measured twice. Independent noise and drift realizations. Exact float inequality calls "
         "this DIFFERENT, which is why exact float inequality is not a causal metric.", tags=("noise_reseed",)),
    Case("C-DEV-02", "D_leak", "D_leak_dead", CONTINUITY, {"limited": INDIST, "rich": INDIST},
         "an EXTRA internal degree of freedom, coupled to nothing and read by nothing. Different insides; no "
         "admissible probe in EITHER arm can know it.", tags=("microimplementation",)),
    Case("C-DEV-03", "D_leak", "D_leak_units", FALSE_DIFFERENCE, {"limited": INDIST, "rich": INDIST},
         "u -> 1000*u + 0.5. A CHANGE OF UNITS IS NOT A CAUSAL DIFFERENCE.", tags=("units",)),
    Case("C-DEV-04", "D_leak", "D_leak_fine", FALSE_DIFFERENCE, {"limited": INDIST, "rich": INDIST},
         "the same ODE integrated at half the step. Solver discretization is not behaviour.", tags=("solver",)),
    Case("C-DEV-05", "D_leak", "D_leak_shift", CONTINUITY, {"limited": INDIST, "rich": INDIST},
         "a GLOBAL shift of the carrier's time origin -- the declared cyclic phase nuisance.", tags=("phase",)),
    Case("C-DEV-06", "D_leak", "D_leak_reloc", CONTINUITY, {"limited": INDIST, "rich": DIFFERENT},
         "the same transfer function built on a different internal ADDRESS. Limited access cannot tell. Rich "
         "access can, and SHOULD: equivalence is relative to a repertoire.", tags=("microimplementation", "arm")),
    Case("C-DEV-07", "D_mem_p", "D_mem_p", FALSE_DIFFERENCE, {"limited": INDIST, "rich": INDIST},
         "the memory system measured twice, INCLUDING the probes that flip its well. A stochastic re-measurement "
         "of a system with hidden state must still be continuous with itself.", tags=("noise_reseed", "memory")),
    Case("C-DEV-08", "D_sat", "D_sat", FALSE_DIFFERENCE, {"limited": INDIST, "rich": INDIST},
         "the saturating system measured twice.", tags=("noise_reseed",)),

    # ---------------- DIFFERENCE: these must separate
    Case("C-DEV-09", "D_leak", "D_leak_gain2", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "GAIN x2. Gain is declared part of the accessible function; it is not removed. Separable only because "
         "the response is standardized by the NOISE floor and not by its own amplitude -- see L7.",
         tags=("gain",)),
    Case("C-DEV-10", "D_leak", "D_leak_sign", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "SIGN INVERSION. The continuous deviation is a SIGNED real, so unlike the Boolean XOR-deviation it is "
         "not blind to this.", tags=("sign",)),
    Case("C-DEV-11", "D_leak", "D_leak_tau8", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "a transport delay of 8 samples. ACCESSIBLE LATENCY, and the representation is aligned to the EXOGENOUS "
         "probe onset -- which we know, because we applied it -- so latency stays in the response.",
         tags=("latency",)),
    Case("C-DEV-12", "D_leak", "D_leak_T16", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "a different time constant: the same steady state reached on a different trajectory.", tags=("shape",)),
    Case("C-DEV-13", "D_leak", "D_cascade", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "a different LATENCY STRUCTURE -- second order, not first -- rather than a shifted first order.",
         tags=("latency_structure",)),
    Case("C-DEV-14", "D_leak", "D_sat", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "SATURATION. The FIRST DERIVATIVE at the operating point is matched analytically, so the two part "
         "company only at second order -- i.e. only when probed HARD. The amplitude-ladder diagnostic "
         "measures how much of the separation the large-amplitude probes carry.", tags=("saturation",)),
    Case("C-DEV-15", "D_fb", "D_fir", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "GENUINE FEEDBACK versus a DELAYED STATIC tapped delay line.", tags=("feedback",)),
    Case("C-DEV-16", "D_mem_p", "D_mem_m", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "GENUINE HIDDEN STATE: the same equations, the bistable well on the other side. It is visible because it "
         "moves the operating point of the output saturation and so changes the INCREMENTAL CAUSAL GAIN. A hidden "
         "state that only added a constant would be absorbed by the readout offset b and would be, correctly, "
         "unidentifiable.", tags=("hidden_state",)),
    Case("C-DEV-17", "D_leak", "D_supply", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "an INDEPENDENTLY CONTROLLABLE ADDITIONAL CAUSE: a second path, from the supply line. Under DRIVE-ONLY "
         "probing the two are EXACTLY identical -- the supply path contributes a constant through a linear "
         "readout and the deviation response is bit-for-bit the same. Only the SUPPLY probes separate them. "
         "This is control L4's exact, constructed collapse.", tags=("cause", "L4")),

    # ---------------- FALSE SAMENESS: different under privileged access, indistinguishable under the limited one
    Case("C-DEV-18", "D_leak", "D_hidden", FALSE_SAMENESS, {"limited": INDIST, "rich": DIFFERENT},
         "an internal mode UNREACHABLE from the external fields that nonetheless feeds the readout. Under limited "
         "access it sits at exactly zero forever and the two systems are BIT-FOR-BIT identical. Clamp its address "
         "-- rich access only -- and they are not. Report EQUIVALENCE_CLASS_ONLY. Never SAME.",
         tags=("collision",)),

    # ---------------- ABSTENTION
    Case("C-DEV-19", "D_silent_dead", "D_leak", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "zero output gain: it answers nothing. Silence is not a fingerprint.", tags=("silent",)),
    Case("C-DEV-20", "D_silent_sat", "D_leak", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "driven so deep into saturation that its incremental gain is nil.", tags=("silent",)),
    Case("C-DEV-21", "D_silent_dead", "D_silent_sat", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "TWO SILENT SYSTEMS ARE NOT THE SAME SYSTEM. Two all-zero fingerprints match perfectly and mean nothing.",
         tags=("silent", "vacuity")),
    Case("C-DEV-22", "D_noisy", "D_leak", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "the response is below its own noise floor. UNREADABLE, not indistinguishable. "
         "BENCHMARK DEFECT, CAUGHT AND CORRECTED ON DEVELOPMENT: the first version used sigma_mult=60, giving a "
         "true SNR of 1.97 -- which is not 'below the noise floor', it is marginally ABOVE it. The instrument "
         "duly detected it and returned DIFFERENT, and the case 'failed'. The failing thing was my system, not "
         "the instrument. Raising the instrument's detection threshold until this case abstained would have been "
         "fitting a threshold to a label, so the SYSTEM was fixed instead (sigma_mult=250, true SNR 0.47) and the "
         "defect is recorded here rather than buried.", tags=("noise",)),
    Case("C-DEV-23", "D_slow", "D_leak", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "the response has NOT FINISHED when the window ends. An in-flight response is not a permanent mark, and "
         "the instrument must refuse rather than guess which it is.", tags=("in_flight", "window")),
    Case("C-DEV-24", "D_drifty", "D_leak", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "a baseline that wanders further than the response references it. Nonstationary; outside the contract.",
         tags=("drift",)),

    # ---------------- THE MEASUREMENT CONTRACT
    Case("C-DEV-26", "D_lowcov", "D_leak", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "THE DRIVE LINE CANNOT BE REACHED on this system. Six of the eight battery probes do not happen. They are "
         "recorded as MISSING, coverage falls to 0.25, and the instrument REFUSES -- even though this system DOES "
         "answer the two supply probes it admits. That is the point: it could have produced a confident number "
         "from a quarter of the battery. Do not silently replace a probe; do not score an absent response as a zero.",
         tags=("coverage", "access")),

    Case("C-DEV-25", "D_leak", "D_leak_loud", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "THE SAME SYSTEM ON A NOISIER CHANNEL. Declared common_channel=False. Absolute gain is not identifiable "
         "when both the readout scale and the noise scale are free, so the admission layer must REFUSE rather "
         "than emit a confident DIFFERENT. Control L8 removes the refusal and the false difference walks in.",
         common_channel=False, tags=("contract", "L8")),
]


# =================================================================== PROSPECTIVE SPLIT  (RESERVED -- DO NOT RUN)
def prospective_systems() -> dict:
    """PROSPECTIVE GRID -- DISJOINT FROM DEVELOPMENT ON EVERY AXIS.

        tau      dev {0,4,8}        -> prospective {2,6,11,14}
        T        dev {5,8,16}       -> prospective {7,13,21}
        gain     dev {1.0,2.0}      -> prospective {1.5,3.0}
        k_out    dev {0,1.2}        -> prospective {0,1.7}
        fb k     dev {0.5}          -> prospective {0.8}
        sigma    dev {1.0e-5}       -> prospective {1.2e-5, 1.6e-5}
        t_shift  dev {0,3}          -> prospective {9}
        units    dev {(1000,0.5)}   -> prospective {(250,-0.02)}
        topology dev {leak,cascade,sat,fb,fir,memory,hidden,supply}
                                    -> ALL OF THOSE PLUS `feedback_sat`, WHICH DEVELOPMENT NEVER SAW

    NO PROSPECTIVE SYSTEM IS PARAMETER-IDENTICAL TO ANY DEVELOPMENT SYSTEM.
    """
    sa, sb = PROSP_SIGMA_A, PROSP_SIGMA_B
    base = S.leak("P_leak", tau=6, T=13.0, gain=1.5, sigma=sa)
    base_b = S.leak("P_leak_b", tau=6, T=13.0, gain=1.5, sigma=sb)      # the ELEVATED-noise channel
    fb = S.feedback("P_fb", k=0.8, T2=7.0, T3=13.0, gain=1.5, tau=2, sigma=sa)
    mem_p = S.memory("P_mem_p", mem0=+1.0, w_drive=0.60, T=13.0, Tm=7.0, gain=1.5, c_mem=1.1,
                     k_out=1.7, tau=2, sigma=sa)
    return {
        "P_leak": base,
        "P_leak_b": base_b,
        # --- continuity partners
        "P_leak_dead": S.dead_site("P_leak_dead", base, x0_5=-0.4),
        "P_leak_units": S.with_units("P_leak_units", base, a=250.0, b=-0.02),
        "P_leak_fine": S.with_refined_solver("P_leak_fine", base),
        "P_leak_shift": S.with_time_shift("P_leak_shift", base, k=3),
        "P_leak_reloc": S.relocate("P_leak_reloc", base, src=2, dst=4),
        # --- difference partners
        "P_leak_gain3": S.leak("P_leak_gain3", tau=6, T=13.0, gain=3.0, sigma=sa),
        "P_leak_sign": S.leak("P_leak_sign", tau=6, T=13.0, gain=1.5, sign=-1, sigma=sa),
        "P_leak_tau14": S.leak("P_leak_tau14", tau=14, T=13.0, gain=1.5, sigma=sa),
        "P_leak_T21": S.leak("P_leak_T21", tau=6, T=21.0, gain=1.5, sigma=sa),
        "P_cascade": S.cascade("P_cascade", tau=2, T2=7.0, T3=21.0, gain=1.5, sigma=sa),
        "P_sat": S.satsys("P_sat", tau=6, T=13.0, gain=1.5, k_out=1.7, sigma=sa),
        "P_fb": fb,
        "P_fir": S.fir("P_fir", taps=((2, 1.0), (8, -0.6), (14, 0.3)), T=2.5, gain=1.5, sigma=sa),
        "P_fbsat": S.feedback_sat("P_fbsat", k=0.6, T2=9.0, T3=14.0, gain=1.5, tau=3, k_sat=1.4, sigma=sa),
        "P_mem_p": mem_p,
        "P_mem_m": S.memory("P_mem_m", mem0=-1.0, w_drive=0.60, T=13.0, Tm=7.0, gain=1.5, c_mem=1.1,
                            k_out=1.7, tau=2, sigma=sa),
        "P_supply": S.supply_cause("P_supply", base, w_s=1.1, site=3, T=13.0, gain=1.0),
        # --- false sameness
        "P_hidden": S.hidden_mode("P_hidden", base, c_h=0.9, T=15.0),
        # --- elevated-noise continuity partner (SAME channel as P_leak_b)
        "P_leak_b_dead": S.dead_site("P_leak_b_dead", base_b, x0_5=0.55),
        "P_leak_b_gain3": S.leak("P_leak_b_gain3", tau=6, T=13.0, gain=3.0, sigma=sb),
        # --- abstention
        "P_silent_dead": S.silent_dead("P_silent_dead", tau=6, T=13.0, gain=1.5, sigma=sa),
        "P_silent_sat": S.silent_saturated("P_silent_sat", sigma=sa),
        "P_noisy": S.too_noisy("P_noisy", sigma_mult=350.0, tau=6, T=13.0, gain=1.5),
        "P_slow": S.too_slow("P_slow", T=140.0, tau=6, gain=1.5, sigma=sa),
        "P_drifty": S.too_drifty("P_drifty", drift_frac=10.0, tau=6, T=13.0, gain=1.5, sigma=sa),
        "P_lowcov": S.access_restricted("P_lowcov", S.supply_cause("P_lowcov_src", base, w_s=1.1, site=3,
                                                           T=13.0, gain=1.0), blocked=(S.DRIVE,)),
        # --- contract violation
        "P_leak_loud": S.leak("P_leak_loud", tau=6, T=13.0, gain=1.5, sigma=sa * 4.0),
    }


PROSPECTIVE_CASES = [
    Case("C-P-01", "P_leak", "P_leak", FALSE_DIFFERENCE, {"limited": INDIST, "rich": INDIST},
         "same system, independent measurement", tags=("noise_reseed",)),
    Case("C-P-02", "P_leak", "P_leak_dead", CONTINUITY, {"limited": INDIST, "rich": INDIST},
         "extra internal degree of freedom, invisible in both arms", tags=("microimplementation",)),
    Case("C-P-03", "P_leak", "P_leak_units", FALSE_DIFFERENCE, {"limited": INDIST, "rich": INDIST},
         "u -> 250*u - 0.02", tags=("units",)),
    Case("C-P-04", "P_leak", "P_leak_fine", FALSE_DIFFERENCE, {"limited": INDIST, "rich": INDIST},
         "solver refinement", tags=("solver",)),
    Case("C-P-05", "P_leak", "P_leak_shift", CONTINUITY, {"limited": INDIST, "rich": INDIST},
         "carrier time-origin shift of 9 samples", tags=("phase",)),
    Case("C-P-06", "P_leak", "P_leak_reloc", CONTINUITY, {"limited": INDIST, "rich": DIFFERENT},
         "same transfer function on a different internal address (2 -> 4)", tags=("microimplementation", "arm")),
    Case("C-P-07", "P_mem_p", "P_mem_p", FALSE_DIFFERENCE, {"limited": INDIST, "rich": INDIST},
         "memory system re-measured", tags=("noise_reseed", "memory")),
    Case("C-P-08", "P_leak_b", "P_leak_b_dead", CONTINUITY, {"limited": INDIST, "rich": INDIST},
         "CONTINUITY AT AN ELEVATED, UNSEEN NOISE LEVEL (1.6x dev). The continuity radius is calibrated on the "
         "NULL, in noise-standardized units, and is therefore sigma-invariant BY CONSTRUCTION. This case is where "
         "that construction is cashed or exposed.", tags=("noise_regime",)),

    Case("C-P-09", "P_leak", "P_leak_gain3", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "gain x2 (1.5 -> 3.0)", tags=("gain",)),
    Case("C-P-10", "P_leak", "P_leak_sign", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "sign inversion", tags=("sign",)),
    Case("C-P-11", "P_leak", "P_leak_tau14", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "transport delay 6 -> 14", tags=("latency",)),
    Case("C-P-12", "P_leak", "P_leak_T21", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "time constant 13 -> 21", tags=("shape",)),
    Case("C-P-13", "P_leak", "P_cascade", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "different latency structure", tags=("latency_structure",)),
    Case("C-P-14", "P_leak", "P_sat", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "saturation, matched small-signal gain", tags=("saturation",)),
    Case("C-P-15", "P_fb", "P_fir", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "feedback vs delayed static", tags=("feedback",)),
    Case("C-P-16", "P_mem_p", "P_mem_m", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "HIDDEN STATE, prospective", tags=("hidden_state",)),
    Case("C-P-17", "P_leak", "P_supply", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "independently controllable additional cause", tags=("cause",)),
    Case("C-P-18", "P_fb", "P_fbsat", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "THE UNSEEN TOPOLOGY: feedback around a SATURATING element vs plain feedback.",
         tags=("unseen_topology",)),
    Case("C-P-19", "P_leak_b", "P_leak_b_gain3", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "a gain difference at the ELEVATED noise level: separation must survive a 1.6x noisier channel.",
         tags=("gain", "noise_regime")),

    Case("C-P-20", "P_leak", "P_hidden", FALSE_SAMENESS, {"limited": INDIST, "rich": DIFFERENT},
         "uncontrollable internal mode: EQUIVALENCE_CLASS_ONLY under limited access", tags=("collision",)),

    Case("C-P-21", "P_silent_dead", "P_leak", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "zero gain", tags=("silent",)),
    Case("C-P-22", "P_silent_dead", "P_silent_sat", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "two silent systems", tags=("silent", "vacuity")),
    Case("C-P-23", "P_noisy", "P_leak", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "below its own noise floor", tags=("noise",)),
    Case("C-P-24", "P_slow", "P_leak", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "response still in flight at the end of the window", tags=("in_flight", "window")),
    Case("C-P-25", "P_drifty", "P_leak", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "nonstationary baseline", tags=("drift",)),
    Case("C-P-26", "P_leak", "P_leak_loud", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "measurement-contract violation: a different noise floor", common_channel=False, tags=("contract",)),
    Case("C-P-27", "P_lowcov", "P_leak", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "the drive line is unreachable: coverage 0.25, below the frozen floor", tags=("coverage", "access")),
]
