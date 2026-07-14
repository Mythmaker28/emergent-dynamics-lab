# LARGE DISTRIBUTIONAL HOLD-OUT — PREREGISTRATION (committed BEFORE execution)
Generator: consolidation/holdout_gen.py (HOLDOUT_SEED=90210000, N=2000, 12 strata).
Instrument: consolidation/signsafe.py FROZEN at 09016d7 (hash-gated). NO threshold/theorem may change after this commit.
Strata: attenuate, amplify, mixed, common_mode, no_anchor_atten, no_anchor_amp, all_contaminated, sparse1,
majority, dropout, nonlinear_contam, clean. Varies m in {2,3,4,5,8}, mixed coupling SIGNS, ill-conditioning (12%),
SNR in {5,15,50}, response sign +/-, amplitude-dependent contamination, reference dropout.
TWO ARMS: ARM-ORACLE (sign/anchor contracts supplied from truth) and ARM-BLIND (no contracts).
PRIMARY SAFETY ENDPOINT: proportion of EMITTED identified sets that EXCLUDE the true |q|. Target 0; report exact
one-sided (Clopper-Pearson / rule-of-three) upper confidence bound. Secondary: point rate, interval width,
abstention, bound tightness, by stratum / m / conditioning. Cluster-aware bootstrap over strata.
STOP RULE: one invalid confident set -> stop, preserve, do not patch on this hold-out.
