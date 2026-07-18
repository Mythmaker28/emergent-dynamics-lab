# THREE FAILURE CLASSES AND WHICH LAYER ADDRESSES EACH (deliverable 2)

## The three classes
1. **Detection failure** — a nonzero response is treated as an exact zero because it does not clear a
   threshold. *Cause:* converting non-detection into a `{0}` claim. *Resolved by:* NASI set outputs, which
   represent weak evidence as a zero-COMPATIBLE set, never the point `{0}`. *Evidence:* 0/10000 false `{0}`.
2. **Instability failure** — a point is determined by a dropped-out reference, a noise-selected reference,
   or a single probe/segment. *Cause:* treating a data-driven selection as fixed. *Controlled by:*
   selection-aware sets (Q_wide) + certificates C2 (dropout), C4 (leave-one-reference-out), C5
   (leave-one-fold). *Evidence:* both catastrophic dropout cases refused; dropout strata 4/4 covered;
   0 catastrophic on 10000.
3. **Identifiability failure** — a STABLE observational bias indistinguishable from a genuinely different
   response along the contamination-collinear direction. *Cause:* structural non-identifiability
   (Proposition 1). *NOT resolvable* by any internal procedure (Proposition 2); requires an EXTERNAL anchor.
   *Evidence:* `contaminated_highSNR` 7/23; point certification withdrawn.

## Decision diagram
```
                 observed noisy channels y_i
                          |
              [NASI set layer: simultaneous CIs -> T6 propagation]
                          |
          Q is zero-compatible / below-detection?  --YES--> report SET (never {0})   [handles DETECTION]
                          | NO
              [selection-aware set Q_wide: hull(Q, leave-one-ref, folds, MC)]
                          |
        C2 dropout? C4/C5 stability? C8 SNR floor?  --FAIL--> report SET, refuse point [handles INSTABILITY]
                          | ALL PASS
             external anchor constrains some beta_i?  --NO--> report SET, refuse point [IDENTIFIABILITY WALL]
                          | YES (not available operationally here)
                 PRACTICALLY_POINT_IDENTIFIED_WITHIN_MARGIN
```
The set layer handles Detection; certificates handle Instability; only an external anchor crosses the
Identifiability wall. On `ctrans`/FHN/droplet no such operational anchor exists, so the operational output
is always a SET.
