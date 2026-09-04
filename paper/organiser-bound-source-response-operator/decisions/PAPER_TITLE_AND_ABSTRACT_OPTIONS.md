# TITLE AND ABSTRACT OPTIONS (LRCPS01 §8)

Forbidden in any title: `reproduction`, `heredity`, `life`, `organism`, `self-replication`,
`daughter`, `evolution`. Each candidate below was checked mechanically against that list by
`code/paper_claim_lint.py`.

## Three candidate titles

**T1 — selected.**
> A prospectively frozen operator for the extent of a source-maintained field on a
> capacity-limited lattice

*What it promises:* a construction, a freeze, and a test of the extent of a field around a
source. Every word of that is delivered in sections 3 and 4. It names the medium, which is the
scope limit, and it claims nothing beyond one parameter point.
*Cost:* it says nothing about the second result.

**T2.**
> The residual was in the summary rule: a frozen source-response operator tested on 28 fresh arms

*What it promises:* the estimator diagnosis first. Vivid and accurate, and the number 28 is
honest about the size of the test.
*Why not selected:* it leads with the retrospective result. The prospective test is the stronger
claim and the one that could have failed publicly; a title that leads with the diagnosis invites
the reading that the paper is an explanation of a past disappointment rather than a prediction
that was met.

**T3.**
> Predicting the radial extent of a source-maintained field in a discrete medium, and diagnosing
> an estimator artefact

*What it promises:* both results, in order.
*Why not selected:* "predicting" without "frozen" understates exactly the property that makes
the result worth reporting, and the two-clause form dilutes both halves.

## Selected title

```
A prospectively frozen operator for the extent of a source-maintained field
on a capacity-limited lattice
```

`TITLE_FORBIDDEN_WORD_HITS = 0`

## Abstract (264 words, seven parts)

**1. What the quantity is and why it is not trivial.**
The extent of a field maintained by a localised source in a discrete, capacity-limited medium is
set jointly by transport, mortality and the source's own history, and a continuum reading of it
is not available at the scale studied here: it errs by 18.7 % and 19.3 % against the discrete
operator.

**2. The methodological gap.**
Such extents are ordinarily reported after the fact, so it is rarely possible to say whether a
model predicted them or accommodated them.

**3. What was done, in order.**
We therefore constructed a one-step conditional operator directly from frozen kinetics, derived
an equivalence margin of 2.9 % from named error terms, froze two absolute predictions and their
ratio, hashed the analysis code, and only then ran 28 fresh arms.

**4. The prospective result.**
The observed medians met the frozen predictions to −0.14 % and +0.24 %, and the mobility ratio
to +0.39 % with unity excluded; every interval lay wholly inside the margin, with no extinction
and no invalid arm.

**5. The retrospective result.**
We then asked why an earlier record had shown deficits of −1.8 % and −5.2 %. Over 116 historical
arms the cumulative radial profile follows the operator at every one of 15 radii, maximum
absolute z of 0.64, so the field was never in deficit; a surrogate with no lattice dynamics at
all already carries −1.2 to −1.3 %, and the remainder requires the source's own wandering, which
moves the construction from −0.66 % to −4.42 % and then to −5.69 % once the empirical birth flux
is added.

**6. What is not established.**
The operator is exact given the state but the marginal density equation does not close, and the
qualification holds at one parameter point.

**7. Scope, stated in full in the paper's scope statement.**
No claim about reproduction, heredity, autonomous cohesion or living systems is made, and none
is tested; the six status lines are reported unconditionally in section 8.

## Abstract as one paragraph, for submission

The extent of a field maintained by a localised source in a discrete, capacity-limited medium is
set jointly by transport, mortality and the source's own history, and a continuum reading of it
is not available at the scale studied here: it errs by 18.7 % and 19.3 % against the discrete
operator. Such extents are ordinarily reported after the fact, so it is rarely possible to say
whether a model predicted them or accommodated them. We therefore constructed a one-step
conditional operator directly from frozen kinetics, derived an equivalence margin of 2.9 % from
named error terms, froze two absolute predictions and their ratio, hashed the analysis code, and
only then ran 28 fresh arms. The observed medians met the frozen predictions to −0.14 % and
+0.24 %, and the mobility ratio to +0.39 % with unity excluded; every interval lay wholly inside
the margin, with no extinction and no invalid arm. We then asked why an earlier record had shown
deficits of −1.8 % and −5.2 %. Over 116 historical arms the cumulative radial profile follows the
operator at every one of 15 radii, maximum absolute z of 0.64, so the field was never in deficit;
a surrogate with no lattice dynamics at all already carries −1.2 to −1.3 %, and the remainder
requires the source's own wandering, which moves the construction from −0.66 % to −4.42 % and
then to −5.69 % once the empirical birth flux is added. The operator is exact given the state but
the marginal density equation does not close, and the qualification holds at one parameter point.

`ABSTRACT_WORDS = 264` (permitted range 200–275)
