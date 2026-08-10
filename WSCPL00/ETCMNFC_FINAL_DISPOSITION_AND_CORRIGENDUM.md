# DISPOSITION FINALE ET CORRIGENDUM — `ETCMNFC`

**Émis par** `WARPED_SCALE_CLOSURE_PILOT_00`. **Ajout en annexe : aucune sortie d'`ETCMNFC`
n'est réécrite, aucun point de mesure n'est substitué sous son identifiant, aucun objet
primaire ou tenu à l'écart n'est ouvert.**

**Commit parent résolu depuis les preuves locales, jamais deviné :**
`c5171b72f3ed2cdaba1968bdbd9ebf3776eab8d7` (`git rev-parse` sur
`refs/heads/confirm/exact-twin-canonical-mf0-native-flux-00`). Ascendance vérifiée :
`c5171b7 → d86d248 → de1524b → 3f8dae8 → ba92a16 → 586108f`.

## Étiquettes finales, séparées comme exigé

```
CANONICAL_MF0_OPERATOR                   = QUALIFIED_IN_DEVELOPMENT
NATIVE_COMPONENT_BATH_SUPPORT            = EMPTY
PER_COMPONENT_OUTER_BOUNDARY_ATTRIBUTION = NOT_IDENTIFIABLE
GLOBAL_BODY_BATH_FLUX                    = IDENTIFIABLE_AS_AN_OBJECT_BUT_NOT_TESTED_AS_A_RESPONSE
ONE_STEP_GLOBAL_REACHABILITY             = STRUCTURALLY_UNREACHABLE_AS_REPORTED__VERIFIED
ETCMNFC_PRIMARY_C                        = NOT_TESTED
ETCMNFC_PRIMARY_N                        = NOT_TESTED
ETCMNFC_PRIMARY_IDS                      = NOT_ALLOCATED
ETCMNFC_HELD_OUT                         = UNOPENED
ETCMNFC_DISPOSITION                      = NOT_TESTED
STOP_REASON                              = JOINT_ENDPOINT_STRUCTURALLY_MISSPECIFIED
```

**Les deux faits ne sont pas le même fait, et ne sont pas fondus dans une étiquette générique.**

1. *Support vide.* La somme sur les faces composante→bain est **mathématiquement calculable**
   (c'est une somme vide, donc zéro) mais **scientifiquement vide de sens** : 0 lien sur 172,
   dans les quatre blocs de développement. Un test exécuté ainsi aurait renvoyé `p = 1,0` par
   construction.
2. *Non-identifiabilité d'attribution.* Attribuer la frontière externe du **corps connexe unique**
   à A plutôt qu'à B est un problème distinct : le prédicat matériel natif `ρ > 1e-4` produit
   **une seule** région connexe contenant les deux composantes, si bien qu'aucune règle native ne
   partage sa frontière.

`ONE_STEP_GLOBAL_REACHABILITY` est **vérifié** et non simplement repris : à la fenêtre gelée d'un
pas, aucune des 344 faces de frontière ne diffère entre `ON_SWAP` et `ON_SHAM` ; la perturbation
atteint 2 cellules et s'arrête 13 cellules avant la première cellule non vivante.

## Adjudication des cas adversariaux, par domaine et non par rhétorique

| cas | adjudication |
|---|---|
| `NaN`, `±inf` | **hors du domaine physique admissible.** `domain_ok` exige `np.isfinite` : ils sont rejetés **avant** l'appariement, jamais « gérés » après. |
| identifiants immuables dupliqués | **entrée invalide.** `transpose()` lève désormais une exception sur une liste de paires non disjointe, au lieu de briser silencieusement le multi-ensemble, `Q` et l'involution. |
| appariement vide | **échec scientifique de dose nulle**, et non une involution identité réussie. `O2` et `O8` sont les seuls garde-fous de non-vacuité ; les deux exigent des paires et `ΔQ ≠ 0`. |
| zéros signés, subnormaux | **octets bruts conservés** : l'opérateur est une transposition d'octets, il ne réécrit aucune valeur. |
| succès sur les 4 points de contrôle DEV | **n'est pas un théorème universel** sur des tableaux arbitraires. De plus les quatre blocs partagent des ensembles A/B **identiques** : `n = 1` en géométrie. |

## Formulations proscrites

`no effect` · `c or N failed` · `z transplantation` · `material-parcel exchange` ·
`component-bath flux was zero as a biological result` · `OFF flux result` · `memory ownership` ·
`individuality` · `life`.

L'opération est une **redistribution/transposition d'octets bruts du porteur canonique `Mf[0]`**.
**Rien de porteur de cible n'a été testé.**

## Relectures indépendantes

Les deux rapports finaux sont joints (`ETCMNFC_NUMERICAL_ORACLE_REVIEW.md`,
`ETCMNFC_CAUSAL_STATISTICAL_REVIEW.md`). Aucun ne réfute la qualification de l'opérateur ni la
topologie du point de mesure : les deux les **confirment**, la seconde en les renforçant. La
poursuite automatique était donc autorisée.
