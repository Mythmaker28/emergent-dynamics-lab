# ROUTE_E_SINGLE_DISC_SOURCE_SINK_DEV_00 — rapport

**2026-08-07** · 24 microétats t0 · 48 checkpoints t=256 · **144 trajectoires** · horizon 2048 ·
0 échec technique · 0 modification du moteur de production · 0 raffinement · 0 remplacement de graine.

---

## 1. Authentification et correction du parent

Artefacts Morph02 retrouvés et hachés (9 fichiers, `UNCOMMITTED_INCLUDED_IN_ARCHIVE`), totaux
**recalculés depuis `morph02_rows.csv` sans relancer la physique** :

```
ENGINE_TRAJECTORIES 144 · UNIQUE_T0_MICROSTATES 72 (72 hashes distincts) · T0_ADMISSIBLE 72
INITIAL_GATE_FAILS 0 · TECHNICAL_FAILURES 0
RANDOM_IID 2/48 · SINGLE_DISC 42/48 · COMPACT_ISLANDS 6/48 · TOTAL 50
```

**Le prompt a raison et mon rapport avait tort** : j'avais écrit « 36 cas sur 48 » pour
`SINGLE_DISC` là où 6+12+12+12 = **42/48**. Erreur de sommation en prose, pas dans les données.
Corrigée **en place** dans `MORPH02_REPORT.md` et `morph02_summary.json` ; le protocole gelé et
les lignes brutes sont inchangés, aucun corrigendum séparé.

**Origine du « 0,343–0,351 » résolue.** `SINGLE_DISC` et `COMPACT_ISLANDS` valent exactement
202/576 = 0,350694 et 358/1024 = 0,349609 **pour chaque graine**. `RANDOM_IID` est binomial et
varie de 0,302 à 0,382 (L=24) et 0,325 à 0,361 (L=32). La cardinalité était donc exacte entre
les deux morphologies construites et égale seulement **en espérance** pour le bras aléatoire.

**Portée corrigée.** Formulation canonique retenue :
`SINGLE_DISC_INITIALIZATION_STRONGLY_INCREASES_PERSISTENCE_RELATIVE_TO_EQUAL_EXPECTED_MASS_RANDOM_IID_IN_THIS_DEV`
— et **non** « la compacité seule cause la survie ». Le disque met toute sa masse dans **un**
composant quand le champ aléatoire la répartit sur 22–38, et le tracker ne suit que le plus grand :
nombre de composants et fraction suivie sont **confondus** avec la compacité.
**Appariement** : les deux bras de loi d'un microétat sont bit-identiques (hash + `array_equal`) ;
les trois morphologies ne sont **pas** `array_equal` et sont seulement équilibrées par graine.
**Réplication** `RANDOM_IID|L24|LAW_16` : 2/12 frais contre une barre de 3/12 →
`NOT_REPLICATED_AT_FROZEN_BAR` ; cumul descriptif 5/24 vs 0/24, **pooling confirmatoire interdit**.
**Rétention LAW_16** : les 18 paires sont exactement les co-survivants (6 à L=24, 12 à L=32) ⇒
*parmi les co-survivants appariés, LAW_16 est associée à une cohorte retenue plus grande ;
l'analyse est conditionnée à la survie conjointe*, ce n'est pas une preuve générale.

## 2. Porte de mesure matérielle — franchie

```
COHORT_SCOPE = GLOBAL_UNION   (pour un disque unique, l'union EST le track)
COHORT_SEMANTICS = MATERIAL_LINEAGE
TRACKER_DEPENDS_ON_INITIAL_COHORT = false
RIGID_TRANSLATION_PRESERVES_MATERIAL_IDENTITY = true
SAME_SITE_REPLACEMENT_IS_DETECTABLE = true
MATERIAL_LINEAGE = IDENTIFIABLE
```

Justification mécanique : `advance_passive_tracer` advecte la cohorte à travers les **flux bruts
réels du ledger moteur** (`matter_forward`/`matter_reverse` × `matter_scale`) avec la fraction
marquée locale `tracer/pre_matter`, **re-dérive** `expected_post = pre − dt·div(net)` et **refuse**
toute incohérence pré/post, impose `0 ≤ tracer ≤ matière` et **assert la conservation exacte**
(`fsum`). Ce n'est ni un chevauchement spatial ni un historique de site. Le détecteur et la règle
de composant suivi ne lisent jamais le traceur.

**Fixtures : 9/9 PASS.** Les fixtures 3 et 4 ont d'abord échoué (0,5044 et 0,2035) parce que **ma
spécification** était fausse — un disque de rayon 6 fait 113 cellules, donc 50 % n'est pas exact —
et non la mesure. Correction mécanique en bloc exact de 100 cellules, rejeu des seules fixtures,
**aucune physique avant que toutes passent**.

## 3. Opérateur source–puits

`STATE_MATCHED_OPEN_RESERVOIR_EXCHANGE`, en boucle ouverte, aveugle au résultat.
Puits = moitié aval du disque **initial** (coordonnées absolues, jamais recentrées), retenue si la
cellule est actuellement occupée **et** dans le track. Source = demi-plan amont hors disque,
retenue si actuellement vacante, avec capacité libre, et **sans aucun 4-voisin dans le track**.
Priorités, calendrier (272…1536, 80 événements) et quotas `q_e = ⌊eQ/80⌋ − ⌊(e−1)Q/80⌋` gelés avant
le run (sommes vérifiées : 404 et 1432). RNG d'intervention dédié, tiré identiquement dans tous les
bras y compris SHAM ; le RNG moteur n'est jamais touché (moteur déterministe).
**`EVENTWISE_BALANCE = PASS`, erreur maximale 0,0** sur les 144 trajectoires. Aucun rattrapage de
déficit. Le SHAM est déclaré honnêtement comme `SCHEDULE_AND_INSTRUMENTATION_SHAM`.

**Choix de bande source, déclaré sans détour.** J'ai observé **deux** pilotes avant de geler :
l'anneau étroit (`r+3`) délivre ~43–60 cellules sur 404 et **le disque survit** (résidu 0,72) ;
le demi-plan amont entier délivre 60–107 et **le disque meurt** vers la frame 368–464. J'ai gelé le
**demi-plan large**, sur un critère de **capacité et non de résultat** : l'anneau plafonne la
livraison à ~0,27·N₀, ce qui rend la porte gelée (≥ 0,80·N₀) arithmétiquement inatteignable et
rend le facteur dose dégénéré. Ce choix retient la configuration où le disque **meurt** — il joue
donc contre un résultat positif.

## 4. Résultats

Risk set : **144/144 `T256_VALID_TRACK`**, 12/12 valides dans chacune des quatre cellules
`(taille, loi)`.

| L | loi | interv | n | S1536 | S2048 | coast | résidu 2048 | fract. source | ingress | egress | cible | joint |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 24 | BASELINE | SHAM | 12 | 12 | 5 | 5 | 0,727 | 0,000 | 0 | 0 | 162 | 0 |
| 24 | BASELINE | FLOW_2N | 12 | 0 | 0 | 0 | 0,602 | 0,095 | 19,4 | 58 | 162 | 0 |
| 24 | BASELINE | FLOW_4N | 12 | 0 | 0 | 0 | 0,541 | 0,139 | 24,1 | 60 | 162 | 0 |
| 24 | LAW_16 | SHAM | 12 | 12 | **12** | 12 | 0,876 | 0,000 | 0 | 0 | 162 | 0 |
| 24 | LAW_16 | FLOW_2N | 12 | 1 | 1 | 1 | 0,822 | 0,040 | 0,0 | 92 | 162 | 0 |
| 24 | LAW_16 | FLOW_4N | 12 | 1 | 1 | 1 | 0,871 | 0,015 | 0,2 | 98 | 162 | 0 |
| 32 | BASELINE | SHAM | 12 | 12 | **12** | 12 | 0,786 | 0,000 | 0 | 0 | 286 | 0 |
| 32 | BASELINE | FLOW_2N | 12 | 0 | 0 | 0 | 0,621 | 0,113 | 32,3 | 98 | 286 | 0 |
| 32 | BASELINE | FLOW_4N | 12 | 0 | 0 | 0 | 0,626 | 0,114 | 30,7 | 107 | 286 | 0 |
| 32 | LAW_16 | SHAM | 12 | 12 | **12** | 12 | 0,907 | 0,000 | 0 | 0 | 286 | 0 |
| 32 | LAW_16 | FLOW_2N | 12 | 0 | 0 | 0 | — | — | 0,0 | 80 | 286 | 0 |
| 32 | LAW_16 | FLOW_4N | 12 | 1 | 1 | 1 | 0,836 | 0,050 | 0,7 | 89 | 286 | 0 |

**`JOINT_EXCHANGE_PERSISTENCE_H2048` = 0 / 144.** Aucune trajectoire n'atteint 0,80·N₀ en ingress
**et** egress : **0/96**.

Deux faits qui comptent plus que la décision :

- **L'échange partiel délivré suffit déjà à tuer le disque.** Apparié contre son propre SHAM, sous
  `LAW_16 × FLOW_2N`, la survie est perdue dans **11/12 paires à L=24 et 12/12 à L=32**, et gagnée
  dans **0** paire. Or l'egress n'a atteint que **28–53 %** de la cible.
- **Le forçage marche dans la bonne direction.** Le résidu tombe de 0,73–0,91 (sham) à **0,54–0,63**
  (BASELINE forcé) et la fraction de provenance source monte de 0 à **0,10–0,14**. Le mécanisme
  n'est pas en cause ; le débit accessible l'est.

## 5. Décision

Règles gelées appliquées dans l'ordre : R1 `b = 0` par taille → échec ; R2 et R3 `joint = 0` →
échec ; R4 aucune cellule ne satisfait la barre → échec ; R5 `joint@1536 = 0` aussi → échec ;
R6 **applicable** : les composants persistent (SHAM 41/48 jusqu'à 2048) alors que résidu, fraction
source et ingress/egress n'atteignent aucune de leurs portes.

```
DECISION = PERSISTENCE_WITHOUT_SUFFICIENT_REPLACEMENT
```

`REPLACEMENT_DESTROYS_PERSISTENCE` **n'est pas** retenue bien que le forçage détruise le disque
dans 46/48 trajectoires, parce que sa précondition — un échange **suffisant** effectivement
délivré — est fausse.

## 6. Interprétation obligatoire et portée

```
FORCING_IS_EXTERNAL = true              REPLACEMENT_IS_OPERATIONALLY_IMPOSED = true
AUTONOMOUS_REPLACEMENT = false          SPONTANEOUS_SELF_MAINTENANCE = not established
INDIVIDUATION = not established
DIRECTIONAL_THROUGH_FLOW = NOT_VERIFIED
```

L'ingress dans le track et l'egress depuis le track ont été mesurés, mais **aucun compteur de
résidence-puis-sortie par unité** n'a été instrumenté : je ne revendique donc que
`FORCED_SOURCE_SINK_REPLACEMENT`, jamais `THROUGH_FLOW`.

Cet échec **ne démontre aucune incompatibilité universelle**. Il montre qu'aucun régime conjoint
n'a été trouvé avec `SINGLE_DISC`, `p ≈ 0,35`, `BASELINE` ou `LAW_16`, `FLOW_2N` ou `FLOW_4N`,
`H = 2048`, et **cette géométrie de réservoir**. Les horizons et les deux doses sont imbriqués :
ni réplications indépendantes, ni dénominateurs à pooler. `UNIQUE_T0_BLOCKS = 24`,
`LAW_SPECIFIC_T256_CHECKPOINTS = 48`, `PAIRED_LOGICAL_TRAJECTORIES = 144`.
