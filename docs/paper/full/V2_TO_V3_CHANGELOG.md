# V2 -> V3 change log

**Manuscript:** `ORGANIZATIONAL_MEMORY_FULL_MANUSCRIPT_V3.tex/.pdf` (23 pp).
**Supplement:** `SUPPLEMENT_V3.tex/.pdf` (5 pp).
**Mandate:** make the paper genuinely submittable by correcting statistical over-claims, the mechanistic
contradiction, provenance language, the bibliography, and the figures. No new simulations were run; every
number below comes from re-analysing already-committed raw data (`STATISTICAL_REAUDIT.md`).

## 1. h2 kill-switch: "falsified" -> "not established"
- **What changed.** Everywhere V2 said the kill-switch *confirmed a failure* / that h2 *does not survive*
  deep turnover, V3 states the longitudinal deep-turnover h2 estimate is a **point of 0.34 with a 95% CI of
  [-0.89, 0.87]**, which **spans the 0.50 certification threshold**; retention is therefore **not
  established** rather than demonstrated absent.
- **Why.** An effect can only be declared below threshold if a pre-specified test's CI *upper bound* is
  below 0.50. Here the upper bound is 0.87. At n = 12 the test is underpowered, not decisive.
- **Loci.** Abstract; Results (kill-switch paragraph); Discussion (bistable-comparison paragraph, which also
  no longer calls the underpowered kill-switch "adequately powered"); Limitations; gate/results tables.
- **Power paragraph.** The V2 logic error ("a pilot point below threshold implies no future sample can
  exceed it") is removed; the corrected text states a single sub-threshold pilot bounds neither a future
  larger sample nor the population value.

## 2. h1 causality: "established" -> necessity established / sufficiency-magnitude uncertain
- Recomputed grouped bootstrap CIs (donor-level, n_boot = 3000, ridge lambda = 1.0) for:
  - mean transplant h1 = **0.61, CI [-0.69, 0.87]**;
  - in-place response h1 = **0.50, CI [-1.39, 0.92]**;
  - memory-inert / erased (lambda_plus = lambda_minus = 0, or M_f = 0) = deterministic **-0.19** (necessity);
  - memory vs. size+mass = **0.93 vs. 0.64**, CIs overlap.
- **Wording.** V3 states memory is **necessary** (erasure/readout-ablation destroy the decode
  deterministically) but the **magnitude of transplanted sufficiency is uncertain** (wide CI crossing 0);
  the memory-over-body-size advantage is **suggestive, not established** (overlapping CIs).
- **New figure.** Figure 2 is now a **predicted-vs-observed** scatter at the 12-history level (active vs.
  memory-inert) plus the bootstrap R^2 distribution with its CI. Erasure (M_f = 0) and readout ablation are
  reported as **separate** controls.
- **Reported for each estimate:** n, resampling unit (history/seed group), n_boot = 3000, percentile-CI
  method, ridge lambda = 1.0, and the 10-D feature vector (see Supplement S1.9).

## 3. h2 mechanism: contradiction removed -> indeterminate
- V2 simultaneously claimed (a) diffusion/templating ablations are negligible and dispersion *grows*, and
  (b) linear smoothing structurally causes the loss. These cannot both hold.
- **V3** states the mechanism of h2 non-persistence is **not causally identified**: disabling the linear
  smoothing terms (individually or together) did not change the decode, and dispersion grows rather than
  shrinks, which is inconsistent with a "linear averaging erases the code" account. Growth-injected
  history-independent dispersion, high inter-family variance, and the absence of bistable protection are
  presented as **hypotheses, not results**.

## 4. Preregistration / provenance: honest sequential wording
- Removed any implication the whole ladder was preregistered at once. V3 says **"sequential experiments,
  each with a protocol prospectively committed (frozen) before its prospective family was generated, and
  executed once."**
- Added a **provenance table** (`tab:provenance`) with protocol / commit / freeze-date / execution-date /
  hash per family, and a sentence defining **"executed once"** (the sealed family was run a single time
  after the freeze; no seed was re-run to obtain a preferred number).
- AI-generated internal reviews are now called **"simulated internal reviews,"** never "referee reports."

## 5. Reproducibility
- Supplement **S1** now contains the **full model**: scaffold PDEs (rho, U, V, c, N), the memory law
  (Eq. mem: write / two-timescale forgetting / templating / diffusion), both readouts, the numerical scheme
  (forward Euler, dt = 0.1, periodic 5-point Laplacian, upwind volume-excluding flux), detection
  (threshold 0.30 rho_max, min 12 cells), tracking (every 5 steps, overlap theta = 0.1), decoder (ridge
  lambda = 1.0, grouped leave-history-out, bootstrap n = 3000), the **10-D feature vector**
  ([mean, std, P10, P50, P90] x {m1, m2}), and the frozen **C1c** parameters.
- **"No data were withheld"** replaced by the exact statement: *"every reported number derives from a file
  in commit <this> on branch paper/organizational-memory-boundaries-01; no analysed run was excluded from
  the reported statistics."*
- A public reproducible-archive checklist was prepared (`REPRODUCIBILITY_RELEASE_CHECKLIST.md`); **nothing
  is pushed or published** pending authorization.

## 6. Literature
- Added and discussed, by direct comparison, three recent history-dependent-droplet works, each DOI and
  citation-claim web-verified:
  - **Nakashima et al. 2021**, *Nat. Commun.* 12:3819, 10.1038/s41467-021-24111-x (active/chemically-fuelled
    coacervate droplets, turnover);
  - **Matsuo & Kurihara 2021**, *Nat. Commun.* 12:5487, 10.1038/s41467-021-25530-6 (self-reproducing /
    proliferating droplets);
  - **Higashi et al. 2025**, *Nat. Chem.* 17:54-65, 10.1038/s41557-024-01682-y (synthetic-cell
    differentiation).
- Novelty rewritten as an explicit contrast with these systems (transplantable, turnover-surviving
  *decodable* memory coordinate vs. reproduction/turnover without a decoded internal coordinate). Decorative
  citations removed.

## 7. Figures and editing
- **Figure 2** redone (predicted-vs-observed + CI + 12 history points).
- **Figure 3b** (longitudinal certification) promoted to the **primary quantitative result** and captioned
  as such.
- **Figure 7** (claim ladder) retitled a **"corrected summary of the historical record."**
- h2 rest-storage values **harmonised** and attributed to their experiment+family: Phase C prospective
  storage h2 = 0.94/0.96 (within/train-on-dev), SMC storage ~0.90, H2-CERT deep-turnover h2 = 0.34 (the
  kill-switch), so the earlier free-floating "0.80/0.90/0.94" no longer read as one quantity.
- Abstract rewritten; the broken tracker sentence fixed; all "failure confirmed" phrasings removed
  (residual count = 0); fonts uniform; **PDF metadata** set (title/author/subject/keywords); the exact AI
  authorship disclosure retained; no operation is attributed to a human that was not performed.

## 8. Compilation
- V3 compiles with `pdflatex + bibtex` x3: **23 pages, 0 undefined references, 39 works cited**, one benign
  overfull hbox (checked in QA). Supplement: **5 pages, 0 errors**.
