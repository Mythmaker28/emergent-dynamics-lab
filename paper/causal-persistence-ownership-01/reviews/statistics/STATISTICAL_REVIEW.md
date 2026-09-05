# Independent statistical review — 03G evidence

Reviewer: statistical subagent of Astra, 2026-09-05. This is a distinct internal AI review, not external human peer review. No prescribed favorable conclusion was supplied. Review target at this stage: pinned primary data and frozen methods underlying candidate B; the new manuscript will be reviewed separately when available.

**Disposition: numerically reproducible, but major inferential qualifications are necessary.** No numerical fatal was found in the central 03G result. The evidence supports a conditional statement about an engineered state and its directly coupled uptake readout in 21 valid worlds. It does not establish absence of informational ownership, calibrated generalization uncertainty for the decoder, or biological individuality. The strongest defensible paper is a methods/measurement case study, not a broad negative theorem about ownership.

## Work actually performed

I inspected the frozen 03G protocol, execution manifest and decision tree, all 50 raw JSON records, the older manuscript, and the source functions governing initialization, assignment, validity and measurement at Git `06fd9524f5c7ffb329ee850a10bd9959f2f0bde5`. I then wrote a new matrix-form LOWO ridge implementation, without importing any project module or simulator. A separate historical implementation was read for comparison, not used to calculate the new results. Fifty raw SHA-256 values match the manifest. The manifest and pre-existing seal are provenance evidence, not proof of inferential validity.

Reproduce from the standalone article directory, with Python, NumPy and SciPy available:

```console
python reviews/statistics/recompute_sensitivity.py
```

The script first uses `data/results/LCI-TURNOVER-PROSPECTIVE-03G` and verifies every entry in the article's `INPUT_MANIFEST.json` (222 entries in the checked version), including the 50 records and raw manifest. If the article-local raw directory is absent, a source-repository audit fallback is available. An existing but corrupt/incomplete local input set fails instead of silently falling back. Output paths are relative, with `input_status.mode` recording the selected source. No Git executable or repository is needed for the standalone path.

Outputs: `STATISTICAL_SENSITIVITY.json` and the script in this directory. New analyses below are explicitly **post hoc, using the same existing observations**. They do not change frozen gates or authorize a new experimental outcome. No worlds were simulated and no project module was imported.

## Major findings and required claim changes

### ST-01 — Failure to establish ownership is not demonstrated lack of ownership

The frozen mean L advantages over E and B are positive, 0.2071677 and 0.1446099. Their frozen-style intervals include zero but also scientifically substantial positive values. No equivalence/noninferiority margin or adequate negative-test power is supplied. Consequently, phrases such as “causal persistence and ownership are empirically dissociable,” “without ownership,” or “the experiment answered ownership” assert more than these data establish. Preserve “Outcome B” as the historical deterministic label, then translate it into ordinary language as **causal uptake effects with exclusive target-local ownership unresolved under the specified decoder and controls**. The same objection applies to interpreting `DISTRIBUTED_ENV=false` as absence of distributed information.

This is fatal to an article whose central discovery is actual absence of ownership. It is repairable by narrowing the article's central claim. The older manuscript contains both correctly cautious sentences and stronger incompatible sentences; keeping a caveat near the end does not repair a stronger abstract or conclusion.

### ST-02 — Shared LOWO fits invalidate an unqualified independent-score interval interpretation

Each world is held out from its own predictor, which prevents direct within-world training/test leakage. However, the training sets of different folds share 19 of 20 worlds. The 21 fold losses are therefore functions of overlapping data. A Student interval over them, and a bootstrap resampling them without refitting, do not by themselves supply calibrated uncertainty for generalization performance. This issue is distinct from treating three targets in one world as independent: world grouping solves that latter problem, but does not remove fitted-model dependence. The general danger of treating cross-validation errors as independent is established in [Bengio and Grandvalet (2004)](https://www.jmlr.org/papers/v5/grandvalet04a.html).

Required change: call these **frozen decision intervals over fixed fold scores**, explain the coverage limitation at first use, and reserve unqualified world-level confidence language for the directly observed causal contrasts. Report the frozen gate as reproduced, not statistically certified. I have not proven that every frozen interval is too narrow; some may be conservative. The defect is the unsupported coverage assertion, not a known universal direction of bias.

Post hoc deletion with complete refitting confirms material fitting sensitivity. Removing one original world and refitting all remaining LOWO models makes E's frozen-style lower bound positive in 5 of 21 deletions, B's in 5, and Gm's negative/nonpositive in 3. All L advantages retain positive point estimates. Thus the result cannot be interpreted as evidence that E or B encode the history equivalently well, and Gm's apparent superiority separation is less robust than its original interval suggests.

The script also reports first-order delete-world jackknife standard errors. These are diagnostics with unvalidated small-sample coverage, **not a replacement set of calibrated confidence intervals**. In particular, Gm's jackknife SE is 0.6195, compared with an estimated L advantage 0.4895. Do not use the numerical jackknife bounds as a new significance filter.

### ST-03 — The conditional permutation arithmetic is correct; design-based exactness is not demonstrated

The new implementation reproduces mean skill 0.3954457381, null 95th percentile 0.1483314371 and zero of 1,000 permuted statistics at least as large as observed; the plus-one value is 1/1001 = 0.000999001. This is the Monte Carlo resolution, not a probability estimated with six meaningful decimal digits. Within-world shuffling preserves the three-label multiset in each world; training/test separation and scaling remain valid. Refitting predictions for each permutation is implemented algebraically by the fixed linear ridge prediction operator, not skipped.

The inferential interpretation still requires label exchangeability conditional on the data and selection. The code assigns dose to size-ordered targets, restarts `default_rng(seed)` for dose after using the same seed to generate initial fields, and analyzes worlds surviving later geometry/tracking selection. There is no independent random assignment stream or audit showing exchangeability after that selection. Shared seeding does **not prove** that the observed association is an artifact; I did not simulate a counterfactual family. It prevents claiming an exact randomized-design test purely from the reported shuffling calculation. Present this as evidence against the **specified conditional permutation null**, with the assumptions stated. General permutation-testing background is [Ojala and Garriga (2010)](https://www.jmlr.org/beta/papers/v11/ojala10a.html); the specific limitations here follow from source inspection, not from that article.

Source chain: `turnover_engine_03g._storage -> causal_confirm.seed_world -> sc_mcm.config -> sc_iom.config -> sc_hmc.config -> exp_sc_00.seed_state`. The last function initializes density/internal fields with `default_rng(seed)`; `_storage` separately initializes `default_rng(seed)` for the six phase amplitudes. Frozen initialization code is read only; it was not executed.

### ST-04 — The target population is the valid-world subpopulation

The raw denominator is exactly 50. Seventeen worlds have fewer than three geometrically eligible targets; 33 are eligible. Of those, eleven incur a recorded SPLIT and one a LOST event before the deep endpoint. Twenty-one reach deep turnover and are valid. In this realized dataset no additional world is excluded only for assay geometry once deep turnover is reached. This matters: the formal validity rule conditions on all intervention branches, but it would be incorrect to claim that a post-intervention exclusion was observed to cause the 21/50 selection here.

The scientific estimates apply to those 21 complete, uncensored worlds, not all 50 realizations or all droplets. The selection rule was frozen and did not choose seeds by effect magnitude; that is useful protection against discretionary selection, not proof that missing-world outcomes resemble retained-world outcomes. Feasibility is 42%; an exploratory exact binomial interval, under an exchangeable-world interpretation, is 28.19–56.79%. No missing outcome was imputed and no sensitivity treats invalid tracks as valid measurements.

### ST-05 — Causal readout is engineered; fixed masks are branch-specific

`nonmerging_confirm.measure` erases memory, resets nutrient, runs 40 settling steps, then defines tracking and fixed masks separately in each branch. Thus “fixed-mask” means fixed during that branch's probe. It does not mean identical masks or masses across the intact and erased branches. It offers a time-tracker-free convergent measurement, but cannot exclude all geometry-mediated differences. The integrated uptake law is directly coupled to the engineered memory field. An intervention contrast is still causal within this simulator, but the result is not an emergent distal behavior, active reconstruction or proof of an intrinsic individual.

### ST-06 — Scope comparisons are representation- and learner-dependent

The scopes have different dimensions: L/N 11, E 24, Gm 18 and B 8. Standardizing and fixing ridge lambda to 1 does not equalize their representational capacity or establish optimal readout from each. Superior L loss under these definitions is a statement about this finite learner and these selected summaries. It is not an information-theoretic proof of exclusive storage. Conversely, failing superiority does not prove redundancy. The conjunction of four superiority requirements is an intersection-union structure: a blanket multiple-comparison objection is not the central problem for claiming the whole conjunction. Claiming separately discovered advantages would require its own inferential framing.

I report all three post hoc ridge settings 0.1, 1 and 10 without selecting the best. Local skill remains positive (0.3553, 0.3954, 0.4154). E's frozen-style lower bound crosses zero at 0.1, but B's stays nonpositive at all three. This illustrates learner sensitivity without rescuing the frozen ownership gate.

## Positive results that survive this review

The causal mean own contrast is 0.16484499, world-level t interval [0.14432164, 0.18536834]. The effect is positive in all 21 valid worlds (range 0.10087365–0.25757848). Own-minus-neighbor, own-minus-sham and branch-fixed-mask differences are also positive in all 21. A two-sided sign test gives 2/2^21 = 9.5367e-7 for each of these sign patterns, as a post hoc check of directional consistency under an independent exchangeable-valid-world interpretation. It tests signs/median tendency, not the population mean, and adds no new independent observations.

The original channel-collapse rule compares a residual upper bound with half the estimated own mean while treating that comparator as fixed. A cleaner paired post hoc contrast is

`D_world = 0.5 * own_effect_world - residual_under_lambda_plus_ablation_world`.

Its mean is 0.06428125, world t interval [0.05742986, 0.07113264], and it is positive in 21/21 worlds. This explicitly carries both quantities' within-world variation and supports substantial attenuation even under a more direct inferential formulation. It does not demonstrate complete elimination: the residual mean is 0.01814125 [0.01321844, 0.02306405], positive in 20/21 worlds. Use “attenuated below the frozen 50% criterion,” not “abolished.” The historical gate remains unchanged.

Own-scope skill remains positive in every delete-one-world refit (mean range 0.35999–0.43515). This is useful influence evidence, although it cannot supply independent validation or restore conditional permutation exactness. The combined defensible positive statement is: **the retained engineered state predicts assigned graded nutrient history under the specified decoder/null and changes a directly coupled uptake readout after the measured material replacement, in the valid-world subset**.

## Final methodological decision before manuscript review

No further world simulation is needed to establish the existing numerical result. New worlds could only address a separately designed replication or improved inference/controls; they cannot retroactively repair the old design. For this paper, repair language and label uncertainty, preserve the frozen result, include the paired attenuation check and deletion sensitivity as post hoc supplementary analyses, and avoid making the unresolved ownership question a positive discovery of ownership absence.

Pending: review of the new manuscript and supplements against these requirements. This report by itself is not manuscript approval.
