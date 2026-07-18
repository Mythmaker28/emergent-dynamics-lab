# Set-Valued Causal Metrology under Drift and Reference Contamination
### When Precision Is Not Identification

**Abstract.** We study the measurement of a continuous causal-response magnitude `q` from passively observed
reference channels that are contaminated by a shared drift. We show that naive scalar similarity and
threshold-based null detection are unsafe, and we develop a noise-aware instrument that represents evidence
as an *identified set* rather than a point: it propagates simultaneous channel confidence intervals through
a small family of proved identifiability inequalities under explicit sign, clean-anchor and sparsity
contracts. On a preregistered, frozen synthetic hold-out of 10,000 cases (40% reference dropout or sparse
contamination), the set instrument never converts non-detection into an exact-zero claim (0/10,000) and
attains marginal coverage of 0.959–0.969. We then ask whether a certified *point* can be extracted under
operational contracts and show, both empirically and by a short impossibility argument, that it cannot: a
stable contamination bias produces a precise, stable, replication-consistent estimate whose limit is wrong,
and no internal diagnostic (repeated measurement, high SNR, leave-one-out stability, bootstrap, independent
implementation) can resolve it. Point certification is withdrawn. We neither demonstrate nor claim identity,
individuality, life, or material-turnover continuity in any substrate; the droplet substrate is presented as
a negative passive-observability example. The central result is that, under explicit observational contracts,
noisy continuous causal responses admit valid identified sets, while exact or point-like recovery remains
impossible along stable contamination directions without external calibration.

## 1. The measurement problem and why scalar similarity fails
A response of magnitude `q` is read out on `m` reference channels, each of the form `v_i = q(1 − α_iκ_i)`,
where `κ_i` is a per-reference contamination and `α_i` a coupling. Passive references that can see the
environment also see the drift that the intervention perturbs. A scalar similarity between a probed and an
unprobed trajectory conflates response with drift, and a mean over measurement blocks dilutes a real
separation with noise blocks (historically, a genuine separation of 21.8 collapsed to 8.6 under a block
mean; per-block RMS with a max aggregate preserves it — claim 1). Scalar similarity is therefore neither
sufficient nor safe.

## 2. Why continuous noisy responses require factorization
Because units rescale both response and noise while gain rescales only the response, the accessible,
unit-invariant, gain-sensitive object is the response standardized by its own noise. This factorizes each
channel into a known response profile `p(t)` times a scalar coefficient `c_i = q(1 − α_iκ_i)` plus noise. The
measurement question becomes: given noisy estimates of the `c_i`, what can be said about `q`?

## 3. Why independent shams fail
An independent sham reference does not share the drift and therefore cannot cancel it; under shared drift the
passive-observable design fails because contamination dominates (claim 2). Identification requires *redundant*
references that share the common noise channel, so that their disagreement locates contamination. This is why
the instrument consumes multiple contaminated references rather than one clean sham.

## 4. Reference-contamination geometry
Writing `β_i = α_iκ_i`, each channel magnitude is `|c_i| = |q||1 − β_i|`. Attenuation (`0 ≤ β_i < 1`) makes
`|c_i| ≤ |q|`; amplification (`β_i ≤ 0`) makes `|c_i| ≥ |q|`; a clean reference (`β_i = 0`) reads `|q|`
exactly. The observed magnitudes thus bracket `q` from one or both sides depending on which contract holds.

## 5. Identifiability and impossibility results
Under contracts C0–C6 we prove (appendix, T6-A..E): attenuation gives a valid lower bound `|q| ≥ max_i|c_i|`;
amplification a valid upper bound `|q| ≤ min_i|c_i|`; a clean anchor gives the bracket `[min|c|, max|c|]`,
pinned to an extreme under a sign contract; sparse contamination with `m − s ≥ 2` locates the clean majority.
Crucially, with neither a sign nor a clean-anchor contract, `q` is **non-identifiable**: for any `q'` there is
a contamination configuration producing identical observations (claim 4, Proposition 1). Identification is
conditional on external contracts.

## 6. Sign-aware set identification
These inequalities define an instrument that emits a *set* — an interval, a one-sided bound, a
zero-compatible set, a below-detection set, or a non-identifiable verdict — labelled by the contract in
force. A point is emitted only when a contract pins `q` to a single value at sufficient precision; otherwise
the honest output is a set. Sign information that only bounds contamination yields a bound, never a point.

## 7. Noise-aware sets and the repair of false zeros
Real channels are noisy. We estimate each `c_i` by a studentized moving-block bootstrap with a
max-statistic simultaneity correction, drift regressors, and a heteroscedasticity-and-autocorrelation
correction, giving simultaneous confidence intervals. Substituting the interval endpoints into the monotone
T6 inequalities yields a set whose coverage is inherited from the channel intervals. The decisive
consequence is that non-detection is represented as a *zero-compatible* or *below-detection* set — never the
exact point `{0}`. Exact zero is reachable only through an independent structural null contract. On the
frozen hold-outs this eliminates the historical false-zero failure entirely (0/5,000 and 0/10,000; claim 5).

## 8. Prospective set validation
On a preregistered, hash-gated hold-out of 10,000 cases (40% dropout or sparse contamination; SNR
oversampled low), the selection-aware set attains marginal coverage 0.959 (conditional arm) and 0.969 (blind
arm), with cluster-aware intervals confirming ≥95% (claim 6). Coverage is *marginal*, not uniform: it falls
to ≈0.92 at high SNR and ≈0.80 on strongly contaminated high-SNR references — a conditional weakness we do
not hide and explain in §9. The blind arm returns non-identifiable on 39% of cases, the honest cost of using
only operational contracts.

## 9. Why point certification fails under stable bias
We built a point-certification layer that issues a point only under eight certificates — external-contract
provenance, dropout audit, set diameter, leave-one-reference-out and leave-one-fold stability,
selection-aware uncertainty, an SNR floor, and independent-implementation agreement — and whose certified
interval is always a subset of the set. It eliminates *catastrophic* point errors (0 of 127 on the hold-out)
and refuses the historical catastrophic dropout cases. But its coverage is only 0.795, materially below the
preregistered 95% target, and the shortfall is concentrated where contamination is strong and SNR is high
(7/23 covered). This is not an implementation defect. It is a structural impossibility (appendix,
Propositions 1–2; claim 8): two latent configurations with different `q` can produce identical observed
distributions, so a procedure using only internal information has the identical sampling distribution under
both. High SNR then makes the *wrong* estimate precise and stable; every internal certificate passes and the
limit is biased (numerically, variance → 10⁻⁶ while bias → −0.30 persists). Internal precision is orthogonal
to identifiability. We therefore **withdraw point identification**; it survives only as a diagnostic and as
evidence for the impossibility boundary. Resolving it requires an *external anchor* that constrains some
`β_i` (a certified clean reference, a known gain, a conservation law, an absolute standard) — none of which
exists operationally in the substrates studied without oracle access (appendix, external anchors).

## 10. Structural transfer to a second substrate
On FitzHugh–Nagumo, whose response profile is a non-exponential spike-and-recovery, the same instrument
produces no false zeros, covers the structural identified set (0.984), and widens honestly under
ill-conditioning. This is *structural* transfer of the identifiability classes and the no-false-zero
property; it is not a claim of substrate-independent quantitative point accuracy (claim 9).

## 11. Negative droplet transfer
In the frozen droplet substrate, passive references able to observe environmental nutrient drift are
contaminated in the same common-mode direction, because drift and response both propagate through the
nutrient field `N`. This realizes exactly the non-identifiable direction of §5: the observables lack the
information a point would require, and no computation — classical or quantum — recovers information absent
from the observables. It blocks the current causal-continuity pilot and would require a genuinely external
anchor or a new passive observable to proceed (claim 10). It does not disprove all conceivable future
substrates, and it makes no claim about identity, individuality, life, or material turnover.

## 12. Limitations and external-anchor requirements
The set coverage is marginal and empirical under a declared noise family and contract mixture, not a uniform
theorem; it degrades conditionally on the stable-contamination direction. Point identification is withdrawn.
Quantitative recovery is substrate-specific. Valid point identification would require an external anchor
pinning a contamination parameter; establishing such an anchor is an instrumentation problem, not an
algorithmic one. The reproduction container and CI are configured but not yet executed on a host with
Docker. The work has not undergone external human review.

**Central claim.** Under explicit observational contracts, noisy continuous causal responses can be
represented by valid identified sets, while exact or point-like recovery remains impossible along stable
contamination directions without external calibration.

*Appendices:* theorem statements and proofs (`STABLE_BIAS_IMPOSSIBILITY.md`, historical
`SET_IDENTIFICATION_MANUSCRIPT.md`), failure taxonomy (`FAILURE_TAXONOMY.md`), external-anchor requirements
(`EXTERNAL_ANCHORS.md`), set-valued statistical audit (`SET_STATISTICAL_AUDIT.md`), claim table
(`FINAL_CLAIM_TABLE.md`). *Reproduction:* `REPRODUCTION_LOG.md`.
