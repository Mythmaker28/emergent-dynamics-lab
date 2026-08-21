# RCD01 §5 — PROVENANCE MATERIELLE DU SECOND NUAGE X

## Le critere, derive avant tout comptage

La desintegration de X est appliquee comme `rng.binomial(n["X"], muX)` a chaque pas : chaque
molecule meurt independamment avec probabilite `muX = 0.004`. Une molecule vivante en `t0`
survit donc `D` pas avec probabilite exactement `(1 - muX)^D`, et le nombre de survivantes parmi
`N0` suit `Binomial(N0, (1 - muX)^D)`.

Avec `D = 249` pas entre la separation et la maturation gelee :

    survie par molecule = 0.3686169213

**Critere R1, sans seuil arbitraire :**

    R1 vaut ssi   Dm  >  Q_0.95( Binomial(N0, (1 - muX)^D) )

ou `Dm` est la masse X locale de la fille dans le rayon `CORE_R` a la maturation et `N0` le X
total du monde a la separation. Aucun pourcentage n'est choisi : on compare le nuage mesure de
la fille a la borne superieure certifiee sur **tout** le materiau pre-separation survivant dans
le monde entier — y compris celui que le parent detient encore, ce qui est physiquement
impossible a attribuer a la fille. La borne est donc volontairement genereuse.

## Resultats

| Quantite | Valeur |
|---|---|
| Mondes R0 (succes fonctionnel complet) | **53 / 192** |
| Mondes satisfaisant R1 sous la borne certifiee | **25 / 53** |
| Fraction certifiee « nouvelle » du nuage fille — mediane | 0.0000 |
| — maximum | 0.3918 |

Comme la borne credite la fille de chaque molecule ancienne survivante du monde entier,
**25 est une borne inferieure** sur le nombre de mondes dont le nuage fille est
materiellement neuf, pas une estimation.

## Provenance exacte : disponible, mais pas dans les archives

the engine carries a molecular Tracker (engine_obtc.Tracker) that records id, birth_step and birth cell for every X molecule and draws from its own generator. Its state was NOT written to the PQEC01/FDFLT01 archives, so exact per-molecule provenance is NOT recoverable from the raw data alone. It IS recoverable by deterministic replay of a seed, which RCD01 may not perform because NEW_WORLD_CONSTRUCTIONS = 0.

`CLASSIFICATION = CERTIFIED_LOWER_BOUND_ON_NEW_MATERIAL`

## Un resultat inattendu sur l'identite des centres

La fille est le centre **le plus faible** dans seulement **24 des 53** succes evalues.

the frozen FDFLT01 condition F5 compared the WEAKER centre to the STRONGER one, which is identity-free and symmetric. Persistent identity shows the daughter is the weaker centre in fewer than half the successes, so F5 frequently constrained the PARENT. That makes F5 stricter than a daughter-only criterion, not weaker, and the FDFLT01 result is unaffected.
