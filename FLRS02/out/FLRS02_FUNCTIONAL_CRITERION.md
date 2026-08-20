# FLRS02 §3–§4 — CRITERE FONCTIONNEL, GELE AVANT TOUT RESULTAT

`FROZEN_BEFORE_OUTCOME_ACCESS = True`

## 1. Deux niveaux, distingues

**`SOURCE_FUNCTION_ONSET`** — the step at which a spatial centre first sustains a local X source, i.e. the centre carries at least one Y and a non-empty accepted-birth candidate pool. C'est un evenement, pas une relaxation.

**`PROFILE_MATURATION`** — the step at which the centre's local X cloud has relaxed to the chosen fraction f of the level it would sustain.

Loi : `N_X(t) = N_inf (1 - (1-muX)^t)  =>  T(f) = ln(1-f)/ln(1-muX)`

## 2. Pourquoi le e-folding est le bon mode — demonstration, pas assertion

Operateur par pas : `n -> (1-muX) * Hop(n); Hop is the engine's four ordered sub-shifts, separable per axis`.

| Quantite | Valeur |
|---|---|
| Nombre de modes | 1296 |
| Mode le plus lent | indice [0, 0] |
| **Le mode le plus lent est le mode de population** | **True** |
| Taux du mode k=0 | 0.0040080213975388 |
| `-ln(1-muX)` | 0.0040080213975388 |
| **Identiques** | **True** |
| Deuxieme mode le plus lent | e-folding 209.7349571585 |
| Rapport d'ecart spectral | 1.1895950460 |

every spatial mode decays strictly faster than the uniform population mode, so the long-time relaxation of ANY positive local X functional is governed by muX. The population e-folding is therefore the correct primary relaxation mode for the functional observable.

L'ecart spectral est faible (1.1896) : la formation du profil et la croissance de la population se font a des echelles comparables. Le e-folding n'est donc ni une surestimation ni une sous-estimation grossiere.

## 3. Critere primaire et bande de sensibilite obligatoire

| Critere | fraction `f` | `T(f)` en pas |
|---|---|---|
| `T_50` | 0.50 | 172.9399900374 |
| **`T_primary`** | **0.6321205588** | **249.4996659983** |
| `T_80` | 0.80 | 401.5542215973 |
| `T_90` | 0.90 | 574.4942116347 |

## 4. Criteres retires

- **`H_HOLD = 16`** — RETIRE. Il ne livrait que **6.211538 %** de la reponse. C'etait la mediane d'une distribution observee, jamais une exigence derivee.
- **`101 naissances X`** — RETIRE. the pre_removal_level of one OBTC02 arm, not a derived threshold.

`REHABILITATION_RULE` : neither may be reinstated because it yields a favourable historical outcome.

## 5. L'evenement de lignee

Identite du fondateur : **irrelevant — no genealogy is constructed or required**.

Un monde compte comme succes fonctionnel a deux centres si et seulement si :

- 1. at least one dynamic Y birth occurs
- 2. the lineage does not go extinct before functional maturation
- 3. exactly two spatial centres form under the frozen centre classifier
- 4. both centres remain spatially distinct for at least T(f) consecutive steps
- 5. both centres exhibit the required local X response
- 6. no third centre appears BEFORE the functional maturation event
- 7. X/source integrity remains acceptable until that event

Unite : one world; steps and episodes are NEVER independent replicates.

