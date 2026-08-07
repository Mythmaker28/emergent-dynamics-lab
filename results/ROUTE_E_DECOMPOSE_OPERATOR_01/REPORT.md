# ROUTE_E_DECOMPOSE_EXCHANGE_OPERATOR_DEV_01 — rapport

**2026-08-07** · 18 blocs t0 frais · 144 trajectoires logiques · horizon 2048 ·
0 échec technique · 0 modification du moteur de production · 0 raffinement.

---

## 1. Parent corrigé en place, sans nouvelle physique

Recalcul direct depuis `forced_exchange_rows.csv` (commit `5e31527b`). Toutes les valeurs
annoncées par le mandat sont **confirmées exactement** :

| Point | Valeur |
|---|---|
| `FORCED_TRAJECTORIES` | 96 |
| `FORCED_SURVIVORS_H2048` | **3/96** — échecs 93/96 |
| `FLOW_2N` / `FLOW_4N` | 1/48 · 2/48 |
| `BASELINE` / `LAW_16` forcés | 0/48 · 3/48 |
| Portes entières | 162 · **287** (et non 286) |

`PARENT_DECISION` corrigée en **`NO_EFFECTIVE_EXCHANGE_DELIVERED`** :
`PERSISTENCE_WITHOUT_SUFFICIENT_REPLACEMENT` était mal appliquée, son sujet étant le bras
d'intervention, lequel **ne persiste pas**. Correction d'application de règle, aucun seuil touché.

Valeurs temporelles ré-étiquetées : les résidus des cellules à `SURVIVAL_1536 = 0` sont des
**`PRE_FAILURE_VALUE`** au snapshot 2048, pas des endpoints (L24 BASE FLOW_2N 2/12, FLOW_4N 1/12 ;
L32 BASE FLOW_2N 7/12, FLOW_4N 4/12). Après perte de track : `UNDEFINED_AFTER_TRACK_LOSS`.
L'apparente incohérence « fraction 0,040 avec ingress 0,0 » est une différence d'unité et de
statistique : la fraction est sans dimension au snapshot, l'ingress est en cellules-équivalent, et
**la médiane** vaut 0 parce que 11/12 trajectoires perdent le track avant tout ingress.

**Statut prospectif : `PILOT_INFORMED_RETROSPECTIVE_DEV`.** 9 trajectoires pilotes (8 abouties,
1 plantée), **153 trajectoires moteur au total**. Fait aggravant que je n'avais pas déclaré :
le run de 144 a été **lancé avant** l'écriture et le hachage de son protocole. Graine 940000
présente dans tous les pilotes **et** parmi les 24 blocs enregistrés. Interprétation maximale du
parent : `THE_TESTED_INTERVENTION_WAS_STRONGLY_DESTRUCTIVE BUT DID_NOT DELIVER THE PRE_REGISTERED
MATERIAL_EXCHANGE`.

## 2. Porte matérielle — `PER_TRACK` et unité de masse réelle

`MATERIAL_UNIT` = somme du champ continu `m` sur le composant suivi (**masse**, pas un compte de
sites). `M256` ∈ [162,94 ; 300,52]. Toutes les doses sont des fractions de `M256`, jamais de `N0`.
`GLOBAL_TRACER_FIELD = true`, `GLOBAL_UNION_IS_TRACK = false`, **`PER_TRACK_READOUT = PASS`** :
une cohorte expulsée mais encore présente ailleurs dans le monde ne compte plus.

**Fixtures 10/10 PASS**, dont les nouvelles : cohorte expulsée (`global > per_track`),
fragmentation, disparition/réapparition, provenance fraîche hors composant (`ingress = 0`),
provenance fraîche dans le composant (masse exacte 0,75), transit directionnel (0,10 exact),
baisse de résidu de fraction connue (0,10 exact), relabeling sans échange, et **bilan séparé
lattice / réservoir source / réservoir puits / système total**. La fixture 7 a été corrigée
mécaniquement **avant le preseal** : sa spécification testait l'opérateur au lieu de la mesure.

**Incident de preseal, déclaré.** Un premier lancement du harnais a démarré avant l'écriture du
protocole (le script du protocole est mort sur une erreur de syntaxe). Il a été tué après
8 trajectoires sur le bloc `(L=24, seed=950000)` ; **ses sorties n'ont jamais été lues** — le log
n'affichait qu'un compteur — et son fichier de lignes a été supprimé. Le run enregistré a été
**relancé de zéro après** le hash. `ENGINE_INVOCATIONS = 152` (144 enregistrées + 8 pré-seal).

## 3. Résultats — tout est toléré

Risk set : **144/144 `T256_VALID_TRACK`**, 9/9 par taille.
**Survie à 2048 : 144/144, dans les huit bras, aux deux tailles. Aucun échec, d'aucun type.**

| L | bras | egress | porte | ingress | transit | résidu | fraction source |
|---|---|---|---|---|---|---|---|
| 24 | 1 Sham | 0,00 | 6,64 | 0,00 | 0,00 | 0,866 | 0,000 |
| 24 | 2 Puits seul | 6,94 | 6,64 | 0,00 | 0,00 | 0,813 | 0,000 |
| 24 | 3 Source seule | 0,00 | 6,64 | 3,10 | 0,00 | 0,885 | 0,018 |
| 24 | **4 Couplé réf.** | **6,92** | 6,64 | **3,09** | 0,00 | 0,832 | 0,019 |
| 24 | 5 Dose haute | 22,75 | 19,93 | 4,73 | 0,00 | **0,703** | 0,033 |
| 24 | 6 Impulsions | 6,75 | 6,64 | 3,62 | 0,00 | 0,825 | 0,021 |
| 24 | 7 Puits contigu | 7,96 | 6,64 | 3,09 | 0,00 | 0,825 | 0,019 |
| 24 | 8 Source loin | 6,92 | 6,64 | **0,55** | 0,01 | 0,813 | 0,004 |
| 32 | 1 Sham | 0,00 | 11,94 | 0,00 | 0,00 | 0,903 | 0,000 |
| 32 | **4 Couplé réf.** | **12,92** | 11,94 | **5,01** | 0,00 | 0,861 | 0,017 |
| 32 | 5 Dose haute | 41,42 | 35,81 | 8,48 | 0,00 | **0,732** | 0,030 |
| 32 | 6 Impulsions | 12,77 | 11,94 | 6,77 | 0,00 | 0,859 | 0,022 |
| 32 | 7 Puits contigu | 14,30 | 11,94 | 5,01 | 0,00 | 0,855 | 0,017 |
| 32 | 8 Source loin | 12,92 | 11,94 | **1,32** | 0,00 | 0,846 | 0,005 |

`TOLERATED_DIRECTIONAL_MICROFLOW_H2048` : **0/144**. Bilan système total exact
(**1,1 × 10⁻¹³**). Le bilan *lattice seul* des bras couplés est violé (max 0,746) parce que la
région source **sature** : l'opérateur retire tout son quota mais ne peut pas tout replacer. Cette
imbalance est elle-même la preuve directe de la limitation de capture, pas un défaut d'opérateur.

**Contrastes appariés — zéro perte supplémentaire partout** : ablation 0, addition de source 0,
dose 0, impulsions 0, puits contigu 0, source lointaine 0, aux deux tailles.

## 4. Décision

`OPERATOR_OR_LINEAGE_INVALID` non (fixtures 10/10, bilan exact) ; `PREPHASE_YIELD_INSUFFICIENT`
non (9/9) ; puis :

```
DECISION = SOURCE_CAPTURE_LIMITED
```

Le bras 4 atteint sa **porte d'egress 9/9 aux deux tailles** et manque sa **porte d'ingress 9/9
aux deux tailles** — très au-delà du critère de 5/9. Le retrait fonctionne parfaitement ; c'est la
**capture** de la provenance fraîche qui plafonne (3,09 sur 6,64 requis à L=24 ; 5,01 sur 11,94 à
L=32), et avec elle la fraction source (0,019 contre 0,04 requis).

**Drapeaux mécanistiques** : `ABLATION_DOMINATED_FAILURE` false · `SOURCE_ADDITION_DOMINATED_FAILURE`
false · `PER_EVENT_SHOCK_DOMINATED` false · `CONTIGUOUS_SINK_INJURY` false ·
**`SOURCE_CAPTURE_LIMITED` true** · `SOURCE_DISTANCE_EFFECT` false *par sa définition gelée*
(elle exige ≥3 échecs supplémentaires, il y en a 0) — mais l'effet sur la capture est grand et
répliqué : **0,55 contre 3,09** à L=24 et **1,32 contre 5,01** à L=32, soit 3,8 à 5,6× moins, à
**coût de survie nul**.

Deux effets dose-dépendants, monotones et répliqués aux deux tailles : le résidu initial descend
de 0,866 → 0,832 → **0,703** (L=24) et 0,903 → 0,861 → **0,732** (L=32) ; la fraction source monte
de 0 → 0,019 → 0,033 et 0 → 0,017 → 0,030. Les impulsions capturent **plus** que le lissé à dose
cumulée identique (3,62 vs 3,09 ; 6,77 vs 5,01) sans aucun coût de survie.

## 5. Portée

`FORCING_IS_EXTERNAL = true`. Rien ici n'établit `80_PERCENT_REPLACEMENT`, `AUTONOMOUS_TURNOVER`,
`SELF_MAINTENANCE`, `INDIVIDUATION`, `IDENTITY` ni `LIFE`. Résultat DEV, limité à `LAW_16`,
sélectionnée post hoc comme châssis stable ; aucune généralisation à d'autres lois. Les horizons
et les doses sont imbriqués : ni réplications indépendantes, ni dénominateurs à pooler.
