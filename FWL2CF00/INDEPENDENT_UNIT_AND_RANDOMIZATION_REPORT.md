# INDEPENDENT_UNIT_AND_RANDOMIZATION_REPORT

    INDEPENDENT_ANCESTRY_BLOCKS = 4

The four upstream ancestry blocks (65000, 65001, 65002, 65003) are the only independent units. The
16 descendants, 32 active rows, 2 carrier arms, 2 channels, 10 scored times and every lattice site
are **repeated conditions**, not replications. Every support check and every leave-one-out analysis
in this programme operates on the four blocks.

With four independent blocks the smallest attainable two-sided sign-flip p-value is `2/16 = 0.125`
and one-sided is `1/16 = 0.0625`. Therefore

    P_LESS_THAN_0_05_POPULATION_CLAIM = IMPOSSIBLE_AND_NOT_REQUIRED

and no such number is computed or quoted anywhere. The primary evidence is prospective materiality
against thresholds sealed before any active outcome, four-block support, leave-one-block-out
stability, block-share control and alignment. Nothing here is bootstrapped or permuted over
descendants, arms, timepoints, sites or channels.
