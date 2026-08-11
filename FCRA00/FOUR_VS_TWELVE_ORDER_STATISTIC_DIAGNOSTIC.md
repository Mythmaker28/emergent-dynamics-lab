# FOUR_VS_TWELVE_ORDER_STATISTIC_DIAGNOSTIC

The frozen tube = max of **four** true-LOBO out-of-sample calibration scores; the fresh gate required **all twelve** future scores below it. Under the hypothetical that four calibration and twelve future scores are continuous and exchangeable, with K = #future above the max of four:

    P(K=k) = C(15-k,3)/C(16,4)
    P(K=0) = 1/4    E[K] = 12/5 = 2.4
    P(K=3) = 11/91 = 0.120879…    P(K>=3) = 11/28 = 0.392857…

Exact checks: {"P_K0==1/4": true, "P_K3==11/91": true, "P_Kge3==11/28": true, "E_K==12/5": true}.

`FROZEN_ALL_BLOCK_GATE = FAILED_AS_PREDECLARED`; `UNIFORM_FIXED_PANEL_CONTAINMENT = NOT_QUALIFIED`; `POPULATION_P2_NONTRANSFER = INCONCLUSIVE_FROM_THIS_GATE_ALONE`. Observing 3/12 exceedances is unremarkable under exchangeability (P(K>=3)=11/28). The tube is never replaced after seeing the twelve scores; this reference never retroactively passes T4. The calibration folds use three-block fold-specific fits while fresh scores use the full frozen object, and exchangeability across the two panels is not established -- so this is an interpretation diagnostic, not a p-value.
