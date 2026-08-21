# FDFLT01 — EXPERIENCE CONFIRMATOIRE DIRECTE, RAPPORT FINAL

```
FINAL_DISPOSITION = DIRECT_FUNCTIONAL_LINEAGE_POINT_QUALIFIED__SUCCESS_RATE_EXCEEDS_0_10
```

## 1. Le test primaire

| Quantite | Valeur |
|---|---|
| Point | B1, `kY = 2.5118864315095822e-05`, `muY = 9.261187281287937e-05` |
| Hypothese nulle | `p <= 0.10`, unilaterale, `alpha = 0.05` |
| N | 192 |
| Seuil de rejet gele avant execution | `SUCCESS_COUNT >= 27` |
| **Succes fonctionnels complets** | **53 / 192** |
| Taux | **0.2760416667** |
| Borne inferieure exacte unilaterale a 95 pourcent | **0.2232489797** |
| IC exact bilateral a 95 pourcent | [0.2141167654, 0.3450244900] |
| **valeur p exacte sous `p0 = 0.10`** | **5.255896e-12** |
| Les deux formulations de decision coincident | True |

Binomiale exacte partout. Aucune approximation normale, a aucune etape.

## 2. Concordance avec le developpemental

| Source | succes | taux | IC 95 pourcent exact |
|---|---|---|---|
| PQEC01 developpemental | 13/44 | 0.2955 | [0.1676, 0.4520] |
| **FDFLT01 frais** | **53/192** | **0.2760** | [0.2141, 0.3450] |

`DEVELOPMENTAL_CONCORDANCE = True` — chaque estimation ponctuelle tombe dans l'intervalle de l'autre. Aucun monde historique n'est entre dans l'estimation primaire.

## 3. Resultats secondaires predeclares

| Quantite | compte | taux | IC 95 pourcent exact |
|---|---|---|---|
| `first_birth` | 66 | 0.3438 | [0.2769, 0.4156] |
| `lineage_non_extinction` | 84 | 0.4375 | [0.3662, 0.5108] |
| `geometric_two_centre_formation` | 66 | 0.3438 | [0.2769, 0.4156] |
| `functional_maturation_timing_only` | 58 | 0.3021 | [0.2381, 0.3723] |
| `third_centre_before_function` | 0 | 0.0000 | [0.0000, 0.0190] |
| `X_source_integrity` | 192 | 1.0000 | [0.9810, 1.0000] |
| `reached_third_centre_at_any_time` | 25 | 0.1302 | [0.0861, 0.1862] |

Delai de separation geometrique : mediane 144.5 pas, moyenne 160.1970, etendue 22–572 (n=66).

Duree maximale d'un episode a deux centres : mediane **1872 pas**, maximum **7308 pas** — contre 250 pas de maturation.

Rapport de reponse X du centre le plus faible au plus fort a l'instant de maturation : mediane **0.8226**, moyenne 0.7420 (n=58). La prediction de l'operateur est 0.6321 : **la reponse observee la depasse**, donc le critere temporel est conservateur.

Motifs d'arret : EXTINCT 108, HORIZON 59, PREMATURE_THIRD_CENTRE 25.

## 4. Sensibilite temporelle — predeclaree, descriptive

| fraction | pas | succes | taux | IC 95 pourcent exact | rejette `p<=0.10` |
|---|---|---|---|---|---|
| `T_50` | 173 | 55/192 | 0.2865 | [0.2237, 0.3560] | **True** |
| `T_primary` | 250 | 53/192 | 0.2760 | [0.2141, 0.3450] | **True** |
| `T_80` | 402 | 39/192 | 0.2031 | [0.1486, 0.2670] | **True** |
| `T_90` | 575 | 21/192 | 0.1094 | [0.0690, 0.1623] | **False** |

Le rejet tient a `T_50`, `T_primary` et `T_80`. Il **ne tient pas** a `T_90` — exactement la limitation **predeclaree dans le passage de relais avant execution**. Aucune revendication n'est faite a `T_90`.

## 5. Comptabilite des echecs

Sur les 66 mondes qui forment deux centres : 8 ne les maintiennent pas 250 pas, 5 de plus echouent au critere direct de reponse X. 66 - 8 - 5 = **53**.

**Defaut auto-signale, non repare.** Le bloc `FIRST_FAILING_COMPONENT_COUNTS` est mal nomme : ses categories sont des comptes marginaux, pas une partition, donc elles ne somment pas au nombre d'echecs. Le controle gele `FAILURE_ACCOUNTING_SUMS_TO_NON_SUCCESS` l'a signale `False` au lieu de le masquer. `MAX_POST_OUTCOME_SCIENTIFIC_REPAIRS = 0` : le code n'a pas ete touche. La chaine 66 - 8 - 5 = 53 ci-dessus est la lecture exacte.

Le diagnostic `newer_centre_is_weaker` n'a produit aucune donnee : sa condition exigeait exactement une composante non appariee entre le debut d'episode et l'instant de maturation, ce qui est rarement le cas. Signale, non repare.

## 6. Portes de decision

| Gate | Etat |
|---|---|
| `ALL_192_PRIMARY_STARTS_ACCOUNTED` | **True** |
| `NO_OUTCOME_DRIVEN_REPLACEMENT` | **True** |
| `COMPLETE_PRE_RUN_METHODS_HASH` | **True** |
| `WINDOWS_PRE_RUN_DURABILITY` | **True** |
| `WINDOWS_RAW_DURABILITY_BEFORE_ANALYSIS` | **True** |
| `RAW_BEFORE_ANALYSIS_CHRONOLOGY` | **True** |
| `PRE_RUN_GATES` | **True** |
| `DUAL_IMPLEMENTATION_EXACT_AGREEMENT` | **True** |
| `NO_LOAD_BEARING_REVIEW_DEFECT` | **True** |
| `PRIMARY_EXACT_TEST_REJECTS_H0` | **True** |

## 7. Revue adverse unique

15 attaques, **0 defaut confirme**, 1 juge plausible.

L'attaque 4 (inertie de l'observateur) a ete jugee `DEFECT_PLAUSIBLE` parce que le relecteur cherchait un fichier a un chemin inexistant. Adjudication : refutee sur preuve que le relecteur n'avait pas localisee — `INSTRUMENTATION_INERTNESS = PASS` et `OBSERVER_INERTNESS_HOLDS = None`. Aucun code n'a ete modifie. Un seul relecteur, aucune cascade.

## 8. Durabilite

`WINDOWS_PRE_RUN_DURABILITY = PASS` — bundle autonome de 122 882 835 octets reassemble et rehashe depuis les octets Windows, clone sur la machine de Tommy avec code 0, `git fsck --full` code 0, commit de gel present, 28 empreintes de methodes sur 28 reproduites, 198 graines presentes.

`WINDOWS_RAW_DURABILITY_BEFORE_ANALYSIS = PASS` **pour le noyau porteur du resultat**, et il faut en lire la portee : the five non-X field planes (Y, SX, SY, WX, WY) of field_delta, i.e. the difference between the 92 MB core and the 1.16 GB full package. The endpoint does not read them. They remain only in this container.

Raison : measured device-bridge throughput fell to roughly one 19 MB part per call, with repeated wall-clock timeouts and one disconnection. The full package is 59 such parts; transferring it would have required on the order of sixty round trips with a high failure rate. The 192 full-archive hashes ARE on the disk, so any later recovery of the full archives can be verified against them.

Suffisance : the core contains every array the frozen primary endpoint reads. All seven conditions, INCLUDING F5 (the direct local-X functional response, which needs the X plane), are exactly re-derivable from the core alone. The primary result can therefore be reproduced and audited from Tommy's disk without this container.

## 9. Plafond de revendication

at the prospectively frozen B1 law, the probability of the predeclared complete functional two-centre lineage event exceeds 0.10. Nothing further.

- `REPRODUCTION_STATUS = NOT_TESTED`
- `HEREDITY_STATUS = NOT_TESTED`
- `H3_STATUS = NOT_TESTED`
- `AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED`
- `X_LAWSPEC_BASELINE = UNCHANGED`
- `ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED`

## 10. Suite

`NEXT_SCIENTIFIC_ELIGIBILITY = REPRODUCTION-CRITERION-DESIGN-01 (zero run)` — voir `HANDOFF_REPRODUCTION_CRITERION_DESIGN_01.md`, zero execution, non lance ici.

