# CSC01 §4 — note append-only : deux résultats hérités distincts, à ne pas confondre

Append-only. Aucun octet gelé d'ORR01, de MCM01 ou de MTW01 n'est modifié. `ORR01_FINAL_REPORT.md`
et sa disposition `ADDITIVE_LAWSPEC_CLOSED_REPAIR_FAIL` restent tels quels.

ORR01 a délivré **une** disposition pour **deux** questions indépendantes. Cette note les sépare.

---

## 1. `INHERITED_OCCUPANCY_RATCHET_REPAIR`

**Question.** Le chémostat équilibré supprime-t-il le cliquet d'occupation du LawSpec additif ?

**Mesures, sur les six graines appariées, lues dans `_results.json` et `_results2.json`.**

| grandeur | contrôle additif (v1) | chémostat équilibré (v2) |
|---|---|---|
| occupation initiale `O` | 7 892–7 908 (38.1 % de la capacité) | 7 781 (37.5 %) |
| occupation finale `O` | **20 736 = 100.0 %** dans les 6 bras | **7 781 = 37.5 %** dans les 6 bras |
| dérive `|O_last − O_first| / O_first` | 1.622 – 1.627 | **0.00000** |
| `O` exactement constante | Non | **Oui**, `std(O) == 0` sur 10 250 pas |
| capacité libre moyenne à l'organisateur (sur 16) | 0.14 – 0.20 | **8.96 – 9.17** |
| `N_X` moyen sur la fenêtre | 0.0 – 16.5 | **63.3 – 123.6** |
| unités échangées par bras | 0 (ajout net) | 3.10 – 3.15 × 10⁶, chacune déplaçant une unité |

**Contrôles pré-déclarés.** `SHAM_REINSERT` conserve l'occupation exactement mais ne renouvelle
rien : `N_X` moyen 0.1 et 16.1. `NO_EXCHANGE_AT_ALL` (φ = 0) : 0.1 et 16.1. Le maintien de la
population n'est donc pas attribuable à la seule conservation de l'occupation ; il est
attribuable au **renouvellement matériel** que l'échange apporte.

**Conclusion, dans le périmètre exact de ces mesures.**

```
INHERITED_OCCUPANCY_RATCHET_REPAIR = QUALIFIED
```

Le chémostat annule la dérive d'occupation **exactement** (conservation cellule par cellule et
pas par pas, sans tolérance), conserve 62.5 % de la capacité du réseau libre en régime établi,
empêche le remplissage qui survient systématiquement sous le LawSpec additif, et permet le
renouvellement de `X` à un niveau supérieur d'un ordre de grandeur. Il n'introduit **aucun
paramètre nouveau** : il réutilise φ comme taux et `S0` comme point de consigne.

**Ce que cela ne dit pas.** Cela ne dit rien sur la persistance à horizon infini — la disparition
de `X` reste certaine en temps fini sur un réseau fini, sous ce LawSpec comme sous tous ses
correctifs (ORR01 C-3). Toute affirmation de maintien est et reste une affirmation sur un
**niveau quasi-stationnaire et une durée de persistance sur une fenêtre déclarée**.

---

## 2. `INHERITED_SPATIAL_LOCALIZATION`

**Question, tout autre.** La population `X` maintenue par ce chémostat est-elle un objet spatial ?

C'est la question sur laquelle ORR01 a conclu, en une phrase de son rapport, que *« rien dans le
modèle ne localise le nuage »*. Cette phrase n'était appuyée par **aucune mesure spatiale
indépendante** : ORR01 n'avait conservé que 3 des 102 relevés de composantes par bras, et la
seule statistique spatiale entrée dans sa décision était le critère
`main_component_carries_the_mass` de son propre gate, plus un indicateur `wraps`.

L'étape A de CSC01 mesure cette question directement, sur le brut, et son verdict est enregistré
séparément (`_stage_a.json`, `CSC01_APPEND_ONLY_CORRECTIONS.md`). Il ne coïncide pas avec la
phrase d'ORR01.

```
INHERITED_SPATIAL_LOCALIZATION = TRAITÉE SÉPARÉMENT PAR CSC01 ÉTAPE A
```

---

## 3. La règle que cette note pose

Un bras qui **annule la dérive d'occupation, conserve de la capacité libre, empêche le
remplissage et permet le renouvellement de `X`** ne doit pas être appelé « une réparation
échouée ». Il a réussi ce qu'on lui demandait. Ce qu'il n'a pas fourni est une **propriété
différente**, qui ne lui était pas demandée et que le LawSpec ne contient pas.

La disposition globale d'ORR01, `ADDITIVE_LAWSPEC_CLOSED_REPAIR_FAIL`, reste exacte au sens de son
propre critère de succès gelé (5 bras sur 6 `MAINTENANCE_ACHIEVED`, non atteint). Elle n'est pas
révisée. Ce qui est corrigé ici est **l'attribution de la cause** : l'échec n'est pas dû à
l'absence de réparation du cliquet, et — comme l'étape A le montre — il n'est pas non plus dû à
une population délocalisée.

```
frozen bytes edited = NONE
ORR01 disposition revised = NO
cause attribution corrected = YES
```
