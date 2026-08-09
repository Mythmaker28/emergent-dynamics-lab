# `ROUTE_E_EXCHANGE_THROUGHPUT_CAUSAL_PROGRAM_07` — rapport

**2026-08-09** · parent `8e619e61e776f962d3d73c1ccfeaa0591a81baf3` (`FLUX_06`) ·
4 phases enchaînées, 4 protocoles scellés avant exécution · 14/14 fixtures ·
aucun artefact parent modifié.

> **Question directrice.** Qu'est-ce qui fixe le débit maximal d'échange de matière ?
> Réponse établie : **une saturation conjuguée**. L'opérateur remplit sa région d'injection
> jusqu'au plafond `MMAX` et vide sa région de retrait sous le seuil `THRESH`. Ce n'est pas
> le composant qui s'épuise : il garde **97 %** de sa matière retirable pendant tout le
> forçage. Relâcher un côté déplace la contrainte sur l'autre au lieu de lever le plafond.

---

## 0. Ce qui a été fait, et pourquoi dans cet ordre

| phase | mode | ce qu'elle décide |
|---|---|---|
| **07A** | observationnel scellé, 0 nouvelle intervention | où part la capacité, sans la perturber |
| **07B** | interventionnel scellé, 6 bras, une porte à la fois | quelle porte est causalement liante |
| **07C** | balayage de cadence, découverte | forme de la loi de débit |
| **07D** | **confirmatoire scellé**, graines neuves, 3ᵉ taille, 2ᵉ loi | 4 prédictions ponctuelles |

Le programme a été **restructuré** par rapport à la suggestion initiale, pour une raison
mécanique découverte avant la première exécution scientifique (§1). Le bras
`SUBTHRESHOLD_SINK` prévu a été **retiré comme manipulation nulle**, et remplacé par une
décomposition en portes réellement indépendantes.

---

## 1. Le fait structurel qui a réorganisé le programme

Le prédicat d'éligibilité du puits de `DEV_05` est

```
i ∈ MASQUE   ET   i ∈ PISTE   ET   m[i] ≥ THRESH
```

Or `detect_components` construit **tout** composant à partir de
`occupied = (m ≥ matter_threshold)` avec `matter_threshold = THRESH = 0,45`. Le troisième
conjoint est donc **impliqué par le second** : c'est du code mort.

> Fixture 1 : 5308 cellules suivies sur 18 états gelés, `min m = 0,450457 ≥ 0,45`,
> plus vérification littérale du prédicat dans la source du détecteur.

Conséquence directe : « le puits est affamé par le seuil 0,45 » n'est pas une hypothèse,
c'est une reformulation de la porte de piste. L'opérateur a donc été reparamétré par trois
portes **indépendantes** — `GATE_MASK` (figé / co-mobile / piste entière), `GATE_TRACK`,
`GATE_THRESH` — plus une famille d'étalement et une échelle de localité pour la source.

**Continuité opératoire exacte avec le parent.** La porte `PARENT` reproduit
`DEV_05.direct_event(mode=DIRECT)` **bit à bit** : 216 cas gelés (2 tailles × 3 graines ×
3 temps × 4 axes × 3 quanta), `max|Δm| = 0,0`, `max|Δ cohorte| = 0,0`. C'est plus strict que
l'équivalence `DSC_04 ↔ DEV_05` (1,3·10⁻¹⁵). Les résultats 07 se branchent donc sur la
physique scellée du parent sans réimplémentation.

---

## 2. 07A — reproduction exacte, puis deux corrections au parent

### 2.1 Reproduction

Mêmes graines, même calendrier, même opérateur : `realized_sink`, `realized_source`,
`M256`, `n_events` sont **identiques à 0,0 près** sur 18 blocs × 2 bras, et la continuité ITT
est la même (2/9 à L=24 Q800, 9/9 à L=32).

### 2.2 Correction A — le dénominateur des rejets de `DEV_05` était incomplet

`DEV_05` n'incrémentait aucun compteur pour un événement programmé tombant alors qu'aucune
piste n'existait. Avec le dénominateur complet :

| taux de rejet, L=24 Q800 | `DEV_05` publié | 07A complet |
|---|---|---|
| | 0,406 | **0,517** |

Écart = 146 événements `NO_TRACK` sur un bloc, jamais comptés. Ce n'est pas une divergence
physique — c'est une sous-déclaration.

### 2.3 Correction B — la « médiane de 1 cellule éligible » de `FLUX_06` était un artefact

`FLUX_06` écrivait : *« Cet ensemble éligible est minuscule — médiane : 1 cellule par
événement »*, et en tirait `PRIMARY_MECHANISM = SIZE_NORMALIZED_FLUX_LIMIT` par épuisement du
puits. Vérification : `DEV_05` **n'a jamais enregistré la taille de l'ensemble éligible** ;
sa colonne `n_sink_sites` compte les cellules **effectivement mordues**. Et son ledger était
sous-échantillonné 1/8 sur les exécutions mais **complet** sur les rejets, ce qui tire la
médiane vers 0.

| Q400, L=24 | cellules mordues | cellules **éligibles** |
|---|---|---|
| `DEV_05` (ledger sous-échantillonné) | 1 | *non mesuré* |
| 07A (ledger complet, 2880 événements) | 1 | **11** (16 sur les seules exécutions) |

```
FLUX_06_PRIMARY_MECHANISM = REFUTED_AS_STATED
```

---

## 3. Le mécanisme réel : saturation conjuguée

### 3.1 Ce n'est pas le composant qui s'épuise

Médianes sur 9 blocs, L=24, comparaison appariée avec le SHAM aux **mêmes instants** :

| | SHAM | forcé Q400 | forcé Q800 | test des signes |
|---|---|---|---|---|
| `CAP_PARENT` (capacité éligible du puits) | 79,17 | 8,10 | **0,00** | 0/9 ↑, p = 0,0039 |
| `MASK_REGISTRATION` (`|masque ∩ C_t| / |masque|`) | **1,000** | 0,105 | **0,000** | 0/9 ↑, p = 0,0039 |
| `CAP_TRACKALL` (matière retirable dans **tout** le composant) | 163,59 | 159,51 | 160,99 | −2,9 sur 163,6 |

Le masque figé reste **intégralement enregistré** dans le SHAM et se déregistre **totalement**
sous forçage, tandis que le composant conserve **97,5 – 98,4 %** de sa matière retirable.
Et à **100 % des rejets** (`n = 4036`), `CAP_TRACKALL > 0` alors que `CAP_PARENT = 0`.

```
LIMITEUR ≠ ÉPUISEMENT DU COMPOSANT
LIMITEUR = PERTE D'ENREGISTREMENT ACTIONNEUR↔CIBLE, AUTO-INFLIGÉE
```

`SHORTFALL_DEREGISTRATION = 0,0` partout : aucune cellule du masque figé ne porte `m ≥ THRESH`
en dehors de la piste. Les cellules du masque ne se sont pas détachées **pleines**, elles ont
été **vidées sous le seuil**, ce qui les retire du composant *et* les rend inéligibles. Le
détecteur et l'actionneur partagent le même seuil : l'opérateur détruit sa propre éligibilité.

### 3.2 Mais avant cela, c'est la **source** qui borne

Le ledger complet identifie, événement par événement, quelle borne est active dans
`q = min(planifié, capacité_puits, capacité_source)` :

| Q400, événements **exécutés** | bornés par la dose | par la **source** | par le puits |
|---|---|---|---|
| L=24 | 117 (5,2 %) | **1968 (87,0 %)** | 176 (7,8 %) |
| L=32 | 98 (3,4 %) | **2782 (96,6 %)** | 0 |

La place libre en amont, `Σ(MMAX − m)` sur la moitié amont de `C256 ∩ C_t`, part de 23,2
(L=24) / 38,3 (L=32) et tombe sous 0,7 en **~13 événements** : l'injection sature la région
amont à `m = MMAX = 1,0`. À partir de là, `q_event = capacité_source` **exactement**, et le
débit n'est plus que le filet que la dynamique rouvre en amont entre deux événements.

**Trois régimes, dans l'ordre :**

1. **événements 1 – 13** : rien ne borne, la dose planifiée est délivrée entièrement ;
2. **événements ~13 – 250** : la **source** borne — le débit est le taux de réouverture ρ ;
3. **tard, L=24 seulement** : le **puits** borne, `CAP_PARENT → 0`, rejet pur.

---

## 4. 07B — six portes relâchées une à une, à dose et état `t256` appariés

Q400 uniforme, 18 blocs, ITT sur les 9 blocs de chaque taille. `SHAM` et `PARENT` sont
réutilisés de 07A (même hash de code, même état `t256`) : aucun appel moteur dépensé deux fois.

| bras | L | délivré | inc. retiré | **efficacité** | continuité ITT | borné par source |
|---|---|---|---|---|---|---|
| `PARENT` | 24 | 0,620 | 0,460 | **0,744** | **9/9** | 0,870 |
| `UNTRACKED` | 24 | 0,620 | 0,460 | 0,744 | **9/9** | 0,870 |
| `COMOVING` | 24 | 0,744 | 0,478 | 0,643 | 8/9 | 0,844 |
| `MULTISITE` | 24 | 0,455 | 0,366 | 0,804 | **0/9** | 0,497 |
| `SRC_DISPERSED` | 24 | 0,516 | 0,448 | 0,895 | 1/9 | 0,000 |
| `TRACKALL` | 24 | 3,865 | 0,298 | 0,075 | 8/9 | 0,277 |
| `SRC_SINKSIDE` | 24 | **4,000** | **0,114** | **0,029** | 9/9 | 0,000 |
| `PARENT` | 32 | 0,414 | 0,377 | **0,910** | **9/9** | 0,966 |
| `COMOVING` | 32 | 0,413 | 0,375 | 0,910 | **9/9** | 0,966 |
| `UNTRACKED` | 32 | 0,414 | 0,377 | 0,910 | **9/9** | 0,966 |
| `MULTISITE` | 32 | 0,455 | 0,349 | 0,768 | **0/9** | 0,701 |
| `SRC_DISPERSED` | 32 | 0,510 | 0,463 | 0,914 | 4/9 | 0,062 |
| `TRACKALL` | 32 | 3,835 | 0,261 | 0,067 | 8/9 | 0,268 |
| `SRC_SINKSIDE` | 32 | **4,000** | **0,100** | **0,025** | 9/9 | 0,003 |

*efficacité = incumbent retiré / masse délivrée ; toutes les masses en fractions de `M256`.*

**Lectures.**

- `UNTRACKED` est **bit-identique à `PARENT` sur 15 blocs sur 18** — les 9 blocs de L=24 et
  6 des 9 de L=32. Les 3 blocs qui diffèrent (écart ≤ 0,7 %, test des signes p = 1,0) sont
  exactement ceux où de la matière `≥ THRESH` s'est détachée de la piste : cela se produit
  dans **3 événements sur 5760** (0 à L=24, 3 à L=32). La porte de piste n'est donc pas
  strictement inerte, mais son relâchement est **sans effet mesurable**. C'est la confirmation
  interventionnelle de la médiane `SHORTFALL_DEREGISTRATION = 0` de 07A, et la mesure de la
  rareté de son exception.
- **Le contraste primaire pré-enregistré échoue.** La règle de décision scellée
  (`R = 1,0 ≥ 0,5`) désignait `COMOVING` : gain de 20 % à L=24 (8/9, p = 0,039) mais avec
  8/9 de continuité, et **strictement nul à L=32** (0/9, différence médiane ≈ 0). Un masque
  co-mobile ne lève pas le plafond, parce que le puits n'était pas la borne active.
- **Relâcher la source déplace la borne sur le puits.** `SRC_DISPERSED` annule la contrainte
  source (0,000 / 0,062) mais les rejets `NO_SINK_CAPACITY` explosent (2123 et 2205) et la
  continuité tombe à 1/9 et 4/9. Le débit ne monte pas.
- `MULTISITE` **détruit le composant 9/9 aux deux tailles** sans délivrer davantage : mordre
  proportionnellement partout pousse trop de cellules sous le seuil en même temps.

### 4.1 Mon propre critère d'évaluation principal était piégeable — et il a été piégé

`SRC_SINKSIDE` délivre **100,0 %** de la dose planifiée (2880/2880 événements bornés par la
dose), avec **9/9** de continuité. La règle scellée de 07B le classe donc `IMPROVEMENT`.
**Ce verdict est rapporté tel quel, sans réécriture.**

Et il est trompeur : ce bras injecte dans les cellules mêmes que le puits vient de vider.
C'est un **cycle futile**. Preuves, toutes pré-déclarées comme critères secondaires :
incumbent retiré 0,114 / 0,100 contre 0,460 / 0,377 pour le parent ; efficacité 0,029 / 0,025
contre 0,744 / 0,910 (**×26 à ×36 moins bien**) ; `F/T` terminal 0,108 / 0,095 contre
0,383 / 0,337 ; balayage absolu du traceur 0,28 contre 1,80 — le composant ne bouge presque
pas, parce que l'effet net local de l'opérateur est nul.

> **6,4× plus de « débit » produit 4× moins de remplacement matériel.**

Correction déclarée et appliquée **en confirmation seulement** :
`REPLACEMENT_EFFICIENCY = incumbent retiré / masse délivrée`, ininflatable par ré-injection au
même endroit, puisque le retrait est proportionnel aux cohortes locales et que la matière
réinjectée est `FRESH`.

---

## 5. Ce que `FLUX_06` déclarait non reconstructible l'est maintenant

`FLUX_06` : `PHYSICAL_BOUNDARY_CROSSING_STATUS = NOT_RECONSTRUCTIBLE_FROM_SAVED_RAW`, faute de
`mass_inside_frozen_C256`, `C256_to_Ct_overlap` et `boundary_site_turnover`. Ces trois
grandeurs sont maintenant instrumentées, et la décomposition de balayage

```
ΔT = MATERIAL_CHANGE_ON_RETAINED_SITES + MASK_ENTRY + MASK_EXIT
```

est vérifiée **pas à pas** : 47/47 trajectoires sans lacune, pire résidu **6,8·10⁻¹³**.
(Les 7 trajectoires L=24 Q800 ayant perdu la piste sont exclues de ce contrôle d'identité et
comptées, jamais supprimées.)

| en fractions de `M256`, à l'horizon | SHAM L24 | Q400 L24 | Q800 L24 | SHAM L32 | Q800 L32 |
|---|---|---|---|---|---|
| balayage **brut** cumulé du traceur | 0,054 | **1,80** | **1,84** | 0,045 | **2,16** |
| balayage **net** cumulé | +0,043 | −0,116 | −0,145 | +0,045 | −0,145 |
| masse dans `C256` **figé** | 0,910 | 0,730 | 0,683 | 0,934 | 0,713 |
| incumbent dans `C256` figé | 0,666 | 0,393 | 0,334 | 0,733 | 0,404 |
| `FRESH` dans `C256` figé | 0,000 | 0,253 | 0,235 | 0,000 | 0,244 |
| recouvrement Jaccard `C256`/`C_t` | 0,925 | 0,399 | 0,362 | 0,926 | 0,378 |
| renouvellement des sites de bord | 0,081 | 0,878 | 0,975 | 0,080 | 0,907 |

Les deux phénomènes existent et sont désormais **séparés** : le traceur balaie **~2 `M256` en
brut** pour un solde net de seulement −0,13 (le composant fait du tapis roulant), **et** dans
le repère fixe la région d'origine perd de l'incumbent (0,67 → 0,33) et gagne du `FRESH`
(0 → 0,25). Le remplacement matériel est réel ; le déplacement du traceur aussi ; aucun n'est
inféré de l'autre.

---

## 6. La loi de débit

Fenêtre fixe de 2048 pas, dose planifiée variée d'un facteur 64 par la cadence :

| Φ = masse délivrée par pas | s=1 | s=4 | s=16 | s=64 | max/min |
|---|---|---|---|---|---|
| `INTERFACE` L=24 | 0,0301 | 0,0297 | 0,0284 | 0,0248 | **1,21** |
| `INTERFACE` L=32 | 0,0407 | 0,0405 | 0,0397 | 0,0364 | **1,12** |
| `DISPERSED` L=24 | 0,0388 | 0,0394 | 0,0386 | 0,0304 | 1,30 |
| `DISPERSED` L=32 | 0,0694 | 0,0702 | 0,0688 | 0,0549 | 1,28 |
| fraction de la dose planifiée délivrée (L=24) | 0,014 | 0,056 | 0,216 | 0,756 | ×53 |

Pendant que la fraction délivrée varie d'un facteur 53, le **débit** varie de 21 %.

```
LAWSPEC_EXCHANGE_THROUGHPUT_SATURATION
        Φ(s) = min( q/s , ρ )
```

`q` est le quantum choisi par l'expérimentateur ; **ρ est une propriété du substrat et de la
région d'injection**, pas de la dose. Bascule prédite à `s* = q/ρ` = 69,5 (L=24) et 91,7
(L=32) — et c'est exactement à `s = 64` que Φ décroche pour la première fois.

ρ dépend de la région d'injection de façon **sous-linéaire** : `DISPERSED` la multiplie par
1,30 (L=24) et 1,72 (L=32) alors qu'elle contient ~2× plus de cellules. ρ n'est pas non plus
parfaitement stationnaire : sur la fenêtre forcée de 5104 pas de 07A il décline d'environ un
facteur 2. Les deux réserves ont été déclarées **avant** la confirmation.

---

## 7. 07D — confirmation prospective : 3 prédictions sur 4 confirmées, 1 réfutée

Graines **950000+**, jamais utilisées dans aucune mission de ce projet. Troisième taille
**L=40**. Seconde loi **`LAW_29`**. Espacements **2, 8, 32, 128** tenus à l'écart de
l'estimation de ρ. 45 blocs, 135 trajectoires, 252 appels moteur, `t256` valide 45/45.

### P1 — loi de saturation : **CONFIRMÉE**

| | s=2 | s=8 | s=32 | s=128 |
|---|---|---|---|---|
| **L=24** prédit (scellé) | 0,02966 | 0,02966 | 0,02966 | **0,01610** |
| observé (graines neuves) | 0,03016 | 0,02920 | 0,02704 | **0,01616** |
| rapport | 1,017 | 0,984 | 0,912 | **1,004** |
| **L=32** prédit (scellé) | 0,04050 | 0,04050 | 0,04050 | **0,02903** |
| observé | 0,03961 | 0,03925 | 0,03776 | **0,02884** |
| rapport | 0,978 | 0,969 | 0,932 | **0,994** |

Tolérance scellée : facteur 1,35. Pire écart réel : **8,8 %**. Le décrochage dose-limité à
`s = 128`, prédit *quantitativement* à partir de `s* = q/ρ`, est retrouvé à **0,4 % et 0,6 %
près**, et l'ordre `Φ(128) < Φ(32)` tient aux deux tailles.

### P2 — effondrement d'efficacité du cycle futile : **CONFIRMÉE** (5 configurations sur 5)

| | `PARENT` eff. | `SINKSIDE` délivré | `SINKSIDE` eff. | rapport |
|---|---|---|---|---|
| `LAW_16` L=24 | 0,739 | 1,000 | 0,028 | **26,2** |
| `LAW_16` L=32 | 0,925 | 1,000 | 0,024 | **38,9** |
| `LAW_16` L=40 | 0,955 | 1,000 | 0,020 | **47,1** |
| `LAW_29` L=24 | 0,851 | 0,997 | 0,052 | **16,4** |
| `LAW_29` L=32 | 0,813 | 1,000 | 0,042 | **19,4** |

Seuil scellé : rapport ≥ 4. Observé : 16 à 47.

### P3 — échange borné : **CONFIRMÉE**, avec une réserve que la prédiction n'excluait pas

| incumbent retiré / `M256` | médiane | étendue | dans la bande scellée [0,25 ; 0,60] |
|---|---|---|---|
| `LAW_16` L=24 | 0,455 | 0,445 – 0,473 | oui |
| `LAW_16` L=32 | 0,373 | 0,345 – 0,416 | oui |
| `LAW_16` **L=40** | **0,313** | 0,298 – 0,325 | oui |
| `LAW_29` L=24 | 0,425 | 0,393 – 0,444 | oui |
| `LAW_29` L=32 | 0,438 | 0,414 – 0,452 | oui |

La bande tient 5/5. Mais sous `LAW_16` la valeur **décroît monotonement** avec la taille
(0,455 → 0,373 → 0,313). La bande scellée était assez large pour l'absorber : je rapporte donc
`BOUNDED = CONFIRMED` et **`SIZE_INVARIANT = REFUTED`**. Trois tailles ne font pas une loi
d'échelle ; aucun exposant n'est revendiqué.

### P4 — la source est la borne active : **RÉFUTÉE COMME ÉNONCÉE**

| fraction d'événements exécutés bornés par la source | seuil scellé 0,70 |
|---|---|
| `LAW_16` L=24 · L=32 · L=40 | 0,877 · 0,966 · **0,969** ✓ |
| `LAW_29` L=24 · L=32 | **0,296** · **0,493** ✗ |

**L'identité de la borne active dépend de la loi.** Sous `LAW_29` la charge se répartit :
`PLANNED` 0,270 / 0,120, `SOURCE` 0,308 / 0,485, `SINK` 0,422 / 0,395, avec 1076 et 1509
rejets `NO_SINK_CAPACITY`. La prédiction est réfutée telle qu'énoncée et n'est **pas**
réécrite.

### 7.1 Le régime lui-même ne généralise pas — et c'est le résultat le plus dur

| `LAW_29`, continuité ITT | `SHAM` | `PARENT` | `SRC_SINKSIDE` |
|---|---|---|---|
| L=24 | **9/9** | **0/9** | 0/9 |
| L=32 | **9/9** | **1/9** | 2/9 |

Le `SHAM` est **intact 9/9 aux deux tailles** : le composant est stable sans opérateur. C'est
le **forçage** qui le dissout, à t = 2288–4640 (L=24) et 4640–5792 (L=32), toujours par
`TRACK_LOST_OR_DISSOLVED`. Sous `LAW_16` aux trois tailles, le même forçage laisse **9/9**.

Une lecture unifie les deux écarts. `LAW_29` redistribue intrinsèquement la matière plus vite :
son `SHAM` termine à `I/I₀` = 0,467 / 0,584 contre 0,751 / 0,809 / 0,848 pour `LAW_16`. Une
redistribution rapide **desature l'amont** — donc la source borne moins souvent, ce qui explique
P4 — **et rapproche le composant de sa frontière de dissolution** — ce qui explique 0/9. La
même propriété de substrat lève le limiteur de débit et supprime la marge de survie.

```
GENERALIZATION_BEYOND_LAW_16 = false   (inchangé, et maintenant expliqué)
EXCHANGE_MAGNITUDE_GENERALISES = true  (bande [0,25 ; 0,60], 5/5)
BINDING_CONSTRAINT_IDENTITY_GENERALISES = false
REGIME_SURVIVABILITY_GENERALISES = false
```

### 7.2 Débit absolu et taille (découverte, non confirmé)

| `LAW_16`, bras `PARENT` | L=24 | L=32 | L=40 |
|---|---|---|---|
| `M256` | 165,5 | 295,5 | 464,9 |
| aire de `C256` | 211 | 371 | 579 |
| ρ absolu (masse/pas sur 5104 pas) | 0,0202 | 0,0233 | 0,0297 |

L'aire est multipliée par 2,74, ρ seulement par 1,47 : ρ croît **beaucoup plus lentement que
l'aire**, de façon compatible avec un flux de **bord** de la région d'injection saturée. Trois
points ne suffisent pas à établir un exposant ; c'est signalé comme piste, pas comme résultat.

---

## 8. Registre des revendications

| # | revendication | statut | preuve |
|---|---|---|---|
| 1 | la porte `m ≥ THRESH` du puits est du code mort sous la porte de piste | **ÉTABLI** | fixture 1 + source du détecteur |
| 2 | la porte `PARENT` reproduit `DEV_05` bit à bit | **ÉTABLI** | fixture 2, 216 cas, `max|Δ| = 0,0` |
| 3 | 07A reproduit `DEV_05` exactement sur toutes les quantités physiques | **ÉTABLI** | 18 blocs × 2 bras, écart relatif 0,0 |
| 4 | le taux de rejet publié par `DEV_05` (0,406) avait un dénominateur incomplet ; il vaut 0,517 | **CORRECTION ÉTABLIE** | 146 événements `NO_TRACK` non comptés |
| 5 | `FLUX_06` « médiane 1 cellule éligible » était un artefact de sous-échantillonnage ; la médiane est 11 | **CORRECTION ÉTABLIE** | ledger complet, 2880 événements |
| 6 | le composant n'est jamais épuisé (97,5–98,4 % de `CAP_TRACKALL` conservé) | **ÉTABLI** | 07A, apparié au `SHAM`, 9/9, p = 0,0039 |
| 7 | la perte de capacité est auto-infligée par l'actionneur, pas dynamique | **ÉTABLI** | `MASK_REGISTRATION` 1,000 (SHAM) vs 0,000 (forcé), 9/9 |
| 8 | sous `LAW_16`, la borne active est la place libre en amont | **ÉTABLI puis CONFIRMÉ** | 87–97 % des événements ; P4 ✓ à 3 tailles |
| 9 | ...mais l'identité de la borne dépend de la loi | **ÉTABLI (réfutation de P4)** | `LAW_29` : 0,296 / 0,493 |
| 10 | relâcher la porte de piste ne change rien de mesurable | **ÉTABLI** | `UNTRACKED` bit-identique sur 15/18 blocs ; l'exception concerne 3 événements sur 5760 |
| 11 | un masque co-mobile ne lève pas le plafond | **ÉTABLI (négatif)** | `COMOVING` nul à L=32, +20 % à L=24 avec 8/9 |
| 12 | délivrer plus n'est pas échanger plus | **ÉTABLI puis CONFIRMÉ** | `SINKSIDE` ×6,4 délivré, ×4 moins d'échange ; P2 ✓ 5/5 |
| 13 | `Φ(s) = min(q/s, ρ)` | **CONFIRMÉ PROSPECTIVEMENT** | 8/8 points, pire écart 8,8 % |
| 14 | l'échange réalisable est borné dans [0,25 ; 0,60] `M256` | **CONFIRMÉ** | 5/5 configurations |
| 15 | cet échange est invariant en taille | **RÉFUTÉ** | décroissance monotone 0,455 → 0,313 |
| 16 | le franchissement physique de frontière est séparable du balayage du traceur | **ÉTABLI** | identité pas à pas, résidu 6,8·10⁻¹³ |
| 17 | le régime survit au forçage sous une seconde loi | **RÉFUTÉ** | `LAW_29` : 0/9 et 1/9, `SHAM` 9/9 |
| 18 | ρ croît comme un flux de bord et non d'aire | **PISTE, NON ÉTABLI** | 3 tailles seulement |
| 19 | organisation / identité / individuation / vie | **NON TESTÉ** | aucun observable validé n'existe |

**Invariants numériques sur l'ensemble du programme** : pire résidu d'identité des cohortes
**7,8·10⁻¹⁶**, pire résidu de bilan global **5,7·10⁻¹⁴**, pire `|source − puits|` par événement
couplé **2,8·10⁻¹⁴**, identité de balayage **6,8·10⁻¹³**.

---
## 9. Ce que ces données ne permettent toujours pas

- Aucun observable d'**organisation** validé n'existe encore dans ce projet ; aucun n'a été
  inventé ici. `ORGANIZATION_PRESERVATION = NOT_TESTED`.
- Le « résidu incumbent connecté » n'est **pas** appelé échafaudage : aucune intervention
  fonctionnelle ne l'a testé.
- L'unité indépendante reste **le bloc** : 9 par taille et par loi. Les 2880 événements d'une
  trajectoire ne sont **jamais** n = 2880.
- ρ n'est mesuré que sur une fenêtre de 2048 pas et décline ensuite ; la loi n'est établie
  que sur `s ∈ [1, 128]`.

```
ROUTE_E_VERDICT = NONE          AUTONOMOUS_RENEWAL = NOT_TESTED
IDENTITY = NOT_ESTABLISHED      INDIVIDUATION = NOT_ESTABLISHED
LIFE = NOT_ESTABLISHED          ORGANIZATION_PRESERVATION = NOT_TESTED
```
