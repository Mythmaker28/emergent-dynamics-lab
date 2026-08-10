# `WSFSCRP00` — registre du parent et de la portée

## Provenance, vérifiée localement

| élément | valeur |
|---|---|
| commit parent `WSCCRP00` | `e912a1004c5b9732d12a8fcc417002bfd1135622` |
| bundle parent | `f8cc3df772e55c83b9179f1281f0eb0ba30845c14aa02b2139899293f019e62b` |
| grand-parent `WSCPL00` | `7cc1ffa0a782a34774a57094189ed19f6bd2b761` |

## 0.1 `WSCCRP00` reste clos, en annexe

```
WSCCRP00_DISPOSITION = NO_EXACT_CONTINUOUS_CAUSAL_ORACLE
WSCCRP00_DETAIL      = MEMBERSHIP_JUMP_DOMINATED_ENDPOINT
Q1_STRUCTURAL_ZERO / Q2_MATERIAL_SIGNAL / Q3_RESPONSE_RANK = PASSED_ON_16_EXPOSED_UNITS
REPORTED_SIGMA2_OVER_SIGMA1 = 0.646
REPORTED_MEMBERSHIP_ENERGY_MEDIAN = 0.988 · MAX = 1.228
REPORTED_FIXED_SUPPORT_TO_DYNAMIC_MAGNITUDE_MEDIAN = 0.73
REPORTED_FIXED_SUPPORT_ABOVE_BOUND = 16_OF_16_UNITS
Q4_TRIVIAL_PREDICTOR_GATE / Q5_STATE_DEPENDENT_LEARNABILITY = NOT_RUN
REPRESENTATIONS_CONSTRUCTED = false
LOCKED_DEV_EVALUATION_CREATED = false · OPENED = false
```

**Statut de preuve, corrigé.** Les 16 unités sont **6 cellules groupées**, non 16 réplications :
4 fondateurs partageant **une seule** géométrie (`FAR`) × 4 instances appartenant à **deux**
superfamilles. Des noms de fichiers ou des graines différents ne créent pas des géométries
indépendantes. Le stop parent était correct sous sa règle gelée. `WSCCRP00` n'est ni repris, ni
renommé, ni réparé, ni écrasé — la réponse à support figé est un **nouvel estimand**, donc une
nouvelle identité de programme.

## 0.2 `WSCPL00` n'a pas de relecture indépendante

```
WSCPL00_INDEPENDENT_REVIEW = NOT_ESTABLISHED
WSCPL00_RESULTS = EXPOSED_DEV_PARENT_RESULTS
```

Cela ne rend pas `WSCPL00` faux ; cela interdit de le dire certifié indépendamment. Ce programme
ne réutilise aucun résultat `WSC` : chaque fait dont il a besoin est re-dérivé sur des fondateurs
frais.

## 0.3 Registre de correction `ETCMNFC`, préservé tel quel

```
ETCMNFC_PRIMARY_C_N = NOT_TESTED
NATIVE_COMPONENT_BATH_SUPPORT = EMPTY_PRE_STEP; NOT_AUDITABLE_AT_EXCHANGE
PER_COMPONENT_OUTER_BOUNDARY_ATTRIBUTION = NOT_IDENTIFIABLE
GLOBAL_BODY_BATH_FLUX = IDENTIFIABLE_AS_GLOBAL_LEDGER; NOT_A_PRIMARY_RESULT
ONE_STEP_GLOBAL_REACHABILITY = UNRESOLVED_IN_IPRR00R
ETCMNFC_STOP_REASON = JOINT_ENDPOINT_STRUCTURALLY_MISSPECIFIED
ETCMNFC_MF0_TRANSPOSITION = ONE_CONDITIONAL_SCIENTIFIC_OPERATOR
ETCMNFC_MATCHING = REPORTED_EXHAUSTIVE_CONCORDANCE_ON_19266_CASES
ETCMNFC_60_OF_60 = 60_ASSERTIONS_OVER_4_DEV_STATES_SHARING_ONE_GEOMETRY
ETCMNFC_60_OF_60_REPLICATION_CLAIM = INVALID
ETCMNFC_VERIFIER_INDEPENDENCE = NOT_ESTABLISHED
ETCMNFC_TARGET_CONTRAST = NOT_MEASURED
ETCMNFC_DEPTH_RATIO = CONTRADICTORY_11_6_TO_15_1_PERCENT__DO_NOT_USE
```

Les rapports `IPRR00R` ne sont **pas** présents localement. Ils sont donc préservés comme
`OWNER_REPORTED_FROM_FINAL_AUDIT`, ce qui **plafonne les revendications documentaires** sans
bloquer l'exécution : ce programme ne dépend scientifiquement d'aucun objet `ETCMNFC` audité.
Aucun transfert n'est demandé à Tommy.

## 0.4 Séparation stricte des dépendances — vérifiée

`wsfscrp_core.py` n'importe que `numpy`, `domc_core`, `ppai_core`, `ppai_engine` et la config
`sc_mcm`. Le lecteur, l'étiquetage en composantes connexes, le point de mesure, l'arithmétique
dyadique exacte, le hachage, la sauvegarde/relecture et le générateur de fondateurs sont
**réimplémentés ici**. Ne sont **pas** utilisés : `TappedEngine`, l'arithmétique de sonde, les
registres composante-bain ou bain global, les masques matière–bain, les ratios de profondeur, le
compte 60/60.

Un seul objet est réutilisé : l'**opérateur** de transposition d'octets de `Mf[0]`
(`etcmnfc_core.py`, sha256 `b9c878acd70ab6d9734eb70e9fadc71b2db70cc919f9132656ce0ddc20ec1d02`).
Sa qualification n'est **pas** héritée de son nom : le domaine post-état et l'ensemble touché ont
été revérifiés **unité par unité** — ensemble touché = `['Mf']` dans 12/12, `rho` intacte dans
12/12.
