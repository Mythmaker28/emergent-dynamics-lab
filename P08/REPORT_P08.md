# `ROUTE_E_SAFE_ACTUATION_AND_FEEDBACK_CAUSAL_PROGRAM_08` — rapport

**2026-08-09** · parent `99df74531e5ada73bd02953cab6072c2f04e7485`
(branche `dev/route-e-exchange-throughput-causal-program-07`,
bundle `_bundles/route-e-exchange-throughput-07.bundle`,
SHA-256 `0f398c8c5da641ddfcac0f3a0e243ae803dad3cb886bfc3d7d250f3af1a5ffd1`, `git bundle verify` → *okay*)
· 4 protocoles scellés avant exécution · 10/10 fixtures · aucun artefact parent modifié.

> **Ce que P08 change.** `ρ` cesse d'être un paramètre ajusté : il est mesuré **seul**, par une
> sonde de saturation qui ne regarde aucune courbe de débit, et il **décroît d'un facteur 3 à 5**.
> `Φ(s) = min(q/s, ρ)` reste vraie **dans la fenêtre d'estimation seulement**. Et les deux
> corrections envisagées — allocation sûre, feedback local — **échouent toutes les deux**, l'une
> en scindant le composant 9/9, l'autre en n'apportant aucune information au-delà d'un
> calendrier rejoué depuis un autre bloc.

---

## 1. Audit adversarial de P07 — ce qui tient, ce qui ne tient pas

Zéro appel moteur. Tout est recalculé depuis les ledgers bruts de P07 par un chemin qui ne
réutilise pas le code d'analyse de P07.

| item | verdict |
|---|---|
| sceaux des 3 protocoles et de tout le code scellé | **PASS** |
| ascendance : `99df745` sur `8e619e6` sur `29923e8` sur `7e41828` | **PASS** |
| bundle incrémental, vérifié, SHA-256 enregistré | **PASS** |
| 28 fichiers scellés de `DEV_05` octet à octet | **PASS** |

### 1.1 Les « 8 prédictions » n'en étaient que 2

`Φ(s) = min(q/s, ρ)` a été confirmée sur 8 points tenus à l'écart. Mais un modèle rival trivial,
`CONSTANT_PLATEAU` (`Φ = ρ` partout), passe **6 de ces 8 points**. Seuls les deux points à
`s = 128` discriminent la loi d'un plateau plat.

```
n_points_scelles = 8
n_qui_discriminent_la_loi_d_un_plateau = 2
le plateau echoue exactement sur L24|s128 et L32|s128
```

La forme de la loi survit — le plateau est bien réfuté par les deux points qui le testent — mais
le test réel est une discrimination à **2 points**, pas à 8. P07 a surestimé sa propre force.

### 1.2 `ρ` n'est pas stationnaire, et la confirmation de P07 n'avait pas tenu la fenêtre à l'écart

Taux de livraison mesuré par fenêtre de 2048 pas, apparié bloc par bloc :

| | 272–2320 | 2320–4368 | 4368–5376 | rapport apparié F1/F2 |
|---|---|---|---|---|
| L=24 | 0,0284 | 0,0155 | 0,0094 | **1,72** [1,59 ; 2,34] |
| L=32 | 0,0397 | 0,0130 | 0,0143 | **3,03** [2,77 ; 3,13] |

P07 avait tenu à l'écart la **cadence** et les **graines**, mais avait estimé `ρ` sur
`t ∈ [272, 2320)` et l'avait testé **sur la même fenêtre**. La confirmation est donc valide
*dans* la fenêtre et muette au-delà.

### 1.3 Modèles rivaux : `CONSTANT_RATE` gagne 0 bloc sur 18

Chaque modèle ajusté sur la première moitié de la phase forcée, noté par RMSE sur la seconde,
bloc par bloc, aucun modèle ne voyant ses propres données de test :

| RMSE hors échantillon (médiane) | L=24 | L=32 | blocs gagnés |
|---|---|---|---|
| `CONSTANT_RATE` | 20,91 | 46,63 | **0 / 18** |
| `FINITE_CAPACITY_RESERVOIR` | **5,47** | 4,89 | 9 |
| `POWER_LAW` (`D ∝ t^0,44` / `t^0,38`) | 8,84 | **4,14** | 8 |
| `PROGRESSIVE_SATURATION` | 18,01 | 12,41 | 1 |

```
PHI_STATUS = CONFIRMED_EFFECTIVE_WITHIN_THE_ESTIMATION_WINDOW
RHO_AS_A_CONSTANT = REFUTED_OUT_OF_WINDOW
```

Le réservoir fini donne `C ≈ 28` (L=24) / `49` (L=32), `τ = 128` pas, `r∞ ≈ 0,014–0,016` —
c'est-à-dire exactement le débit tardif mesuré en §1.2.

### 1.4 Portée de l'« absence d'épuisement » : locale, pas globale

Les 4036 rejets de P07, classés causalement :

| catégorie | n | fraction |
|---|---|---|
| épuisement matériel **global** | 0 | 0,000 |
| support autorisé **vide de matière** | 0 | 0,000 |
| support autorisé ne portant **que du sous-seuil** | **4036** | **1,000** |
| matière **sur-seuil** hors piste dans le support | 0 | 0,000 |

Médiane de **24,2 unités** de matière échouées sous le seuil dans le masque. La revendication
correcte n'est donc pas « le composant n'est pas épuisé » mais :

```
PRIMARY_LIMIT = LOCAL_SUBTHRESHOLD_INACCESSIBILITY_IN_A_FIXED_SUPPORT
```

Ce n'est ni topologique, ni global, ni une pénurie de matière.

### 1.5 Les trois blocs non bit-identiques sont qualifiés

Critère **préexistant** (instrumenté en 07A, avant que 07B ne tourne) :
`SHORTFALL_DEREGISTRATION > 0` à au moins un événement. Il prédit **exactement** les trois blocs
qui diffèrent (`L32_S990100`, `L32_S990102`, `L32_S990104`), un événement chacun, **sans aucun
faux positif**. La revendication survit sous la forme « relâcher la porte de piste n'a **aucun
effet mesurable** », pas « aucun effet ».

### 1.6 `LAW_29` : la magnitude d'échange était pré-létale

| `LAW_29`, bras `PARENT` | L=24 | L=32 |
|---|---|---|
| continuité ITT | **0/9** | **1/9** |
| SHAM continuité ITT | **9/9** | **9/9** |
| médiane du 1er échec | t = 3104 | t = 5064 |
| fraction du calendrier tombant **après** la perte de piste | **0,447** | 0,056 |
| incumbent retiré / `M256` | 0,425 | 0,438 |

```
EXCHANGE_MAGNITUDE_GENERALISES = REVOQUE
disposition correcte = TRANSIENT_PRE_FAILURE_FLUX_TRANSPORTS
```

### 1.7 Le critère primaire de P08, validé adversarialement **avant** d'être scellé

`UCR = min(incumbent retiré et jamais recompté, frais encore retenu à l'horizon) / M256`,
rétro-appliqué aux bras de P07 dont la dégénérescence est déjà connue :

| L=24 | UCR | délivré | part futile de la prise | ITT |
|---|---|---|---|---|
| `COMOVING` | 0,405 | 0,744 | 0,282 | 8/9 |
| `PARENT` / `UNTRACKED` | 0,387 | 0,620 | 0,190 | 9/9 |
| `MULTISITE` | 0,282 | 0,455 | 0,149 | 0/9 |
| `TRACKALL` | 0,251 | 3,865 | **0,909** | 8/9 |
| **`SRC_SINKSIDE`** | **0,104** | **4,000** | **0,957** | 9/9 |
| `SRC_DISPERSED` | 0,000 | 0,516 | 0,057 | 1/9 |

Les deux bras dégénérés tombent au bas du classement, et un bras dont le composant est mort à
l'horizon reçoit **0**. Le critère n'est pas gonflable par un cycle futile.

```
P07_AUDIT = CORRECTED
```

---

## 2. `ρ` mesuré seul : une sonde de saturation

À un instant `t` d'une trajectoire forcée ordinaire, on **fork un clone**, on **sature en un coup**
la région d'injection (chaque cellule source de la piste portée à `MMAX`), puis on laisse le
substrat courir **sans aucun opérateur** et on mesure la vitesse à laquelle la place libre se
rouvre. La sonde ne regarde **aucune** courbe de débit.

| | t=272 | t=1296 | t=2320 | t=3344 |
|---|---|---|---|---|
| **L=24** sonde (pente initiale) | 0,0495 | 0,0150 | 0,0158 | 0,0192 |
| débit observé sur la fenêtre **suivante** | 0,0408 | 0,0142 | 0,0158 | 0,0154 |
| **L=32** sonde | 0,0640 | 0,0187 | 0,0136 | 0,0130 |
| débit observé sur la fenêtre **suivante** | 0,0607 | 0,0153 | 0,0128 | 0,0132 |

Stratifié par la variable *préexistante* « quelle borne est active » :

| | n | rapport sonde/observé | intervalle | dans un facteur 1,5 |
|---|---|---|---|---|
| fenêtres **bornées par la source** | 46 | **1,020** [0,986 ; 1,059] | 0,878 – 1,238 | **46 / 46** |
| fenêtres où le **puits** a pris la main | 26 | 1,134 | 1,036 – 4,897 | — |

Les **seuls** écarts sont les fenêtres où le puits est devenu la borne active : la sonde ne
mesure que le côté source, donc elle sur-prédit exactement là où un autre facteur étrangle. Les
trois blocs à rapport > 2 sont précisément les trois dont la fraction bornée par la source tombe
à **0,000** avec 78–84 % de rejets. C'est une conséquence falsifiable de ce que la sonde mesure,
et elle tient sans exception.

```
RHO_STATUS = INDEPENDENTLY_PREDICTED (régime borné par la source) + NONSTATIONARY
facteur de décroissance apparié t272 → t2320 : 3,11 (L=24) et 4,71 (L=32), 9/9, p = 0,0039
```

**Et la sonde produit une prédiction prospective sur 08B**, écrite avant que 08B ne soit lu : la
vitesse de réouverture est **maximale à réserve nulle** et décroît quand la réserve s'accumule
(pente tardive/précoce = 0,761 [0,752 ; 0,767], n = 90). Une règle qui **garde délibérément de la
réserve** opère donc là où le substrat rouvre plus lentement, et doit délivrer **moins**.

---

## 3. 08B — la règle de quantité, factorielle 2×2 exacte

`floor` = le puits ne laisse jamais une cellule drainée sous cette valeur.
`ceil` = la source ne remplit jamais une cellule au-dessus. **WHEN et WHERE sont identiques
dans les quatre bras.** `PARENT` = (0,00 ; 1,00) reproduit l'opérateur P07 **bit à bit** sur
216 cas gelés.

| bras | L | UCR | ITT | ombre 0,55 | délivré | part futile | inc. retiré | rejets | verdict |
|---|---|---|---|---|---|---|---|---|---|
| `PARENT` | 24 | **0,387** | **9/9** | 9/9 | 0,620 | 0,190 | 0,460 | 0,175 | — |
| `SINK_FLOOR` | 24 | 0,216 | **0/9** | 9/9 | 0,306 | 0,044 | 0,284 | 0,000 | `SAFE_ABSTENTION` |
| `SRC_CAP` | 24 | 0,236 | **9/9** | 9/9 | 0,314 | 0,017 | 0,284 | 0,000 | `NO_EFFECT` |
| `BOTH_SAFE` | 24 | 0,227 | **0/9** | 9/9 | 0,351 | 0,097 | 0,298 | 0,000 | `NO_EFFECT` |
| `PARENT` | 32 | **0,333** | **9/9** | 9/9 | 0,414 | 0,034 | 0,377 | 0,000 | — |
| `SINK_FLOOR` | 32 | 0,225 | **0/9** | 9/9 | 0,308 | 0,061 | 0,284 | 0,000 | `NO_EFFECT` |
| `SRC_CAP` | 32 | 0,180 | **9/9** | 9/9 | 0,228 | 0,001 | 0,215 | 0,000 | `NO_EFFECT` |
| `BOTH_SAFE` | 32 | 0,196 | **0/9** | 9/9 | 0,265 | 0,037 | 0,243 | 0,000 | `NO_EFFECT` |

**Trois résultats, tous négatifs pour l'hypothèse de départ.**

**(a) Le plancher de sécurité fait SCISSIONNER le composant, 9/9 aux deux tailles**, à t ≈ 976
(L=24) et 1280 (L=32). Ce n'est pas une dissolution — la piste est vivante à l'horizon 9/9 — et
ce n'est pas un artefact du détecteur : les lecteurs fantômes à 0,50 et 0,55 voient eux aussi un
composant, celui du fragment. Le mécanisme est lisible : en ne prenant que `m − 0,50` par
cellule, le puits **amincit une bande large** au lieu d'exciser proprement quelques cellules, et
une bande à 0,50 casse. **Empêcher l'auto-effacement détruit l'individuation.**

**(b) Le plafond de réserve délivre moins — exactement comme la sonde l'avait prédit.**
0,314 vs 0,620 (L=24) et 0,228 vs 0,414 (L=32), soit 0,51 et 0,55 de `PARENT`. La prédiction
était écrite avant la lecture de 08B.

**(c) Les gardes déplacent la borne active mais ne lèvent pas le plafond.** Sous `SINK_FLOOR`,
la fraction bornée par le **puits** passe de 0,078 à **0,917** (L=24). Le système reste borné,
seulement ailleurs.

La règle de sélection scellée retient donc `PARENT` : la règle la plus simple, et la meilleure.

```
SAFE_ALLOCATION = NO_EFFECT   (et activement nuisible dans la variante plancher)
```

---

## 4. 08C — le calendrier seul, avec contrôle asservi sur donneur

`AMOUNT` figé à `PARENT`, `WHERE` figé, **masse tentée identique par construction** (une
opportunité sautée met son quantum en réserve, plafonnée à 4 quanta, la dernière opportunité
vide la réserve).

| bras | L | UCR | ITT | tirs / 320 | attentes | délivré | part futile | test vs FIXE |
|---|---|---|---|---|---|---|---|---|
| `FIXE` | 24 | **0,387** | 9/9 | 264 | 0 | 0,620 | 0,190 | — |
| `EN LIGNE` | 24 | 0,305 | 9/9 | **18** | 302 | 0,387 | 0,035 | **0/9, p = 0,0039** |
| `DONNEUR ASSERVI` | 24 | 0,310 | 9/9 | 18 | 302 | 0,400 | 0,034 | 0/9, p = 0,0039 |
| `CAPTEUR RETARDÉ` | 24 | 0,312 | 9/9 | 23 | 297 | 0,394 | 0,037 | 0/9, p = 0,0039 |
| `FIXE` | 32 | **0,333** | 9/9 | 320 | 0 | 0,414 | 0,034 | — |
| `EN LIGNE` | 32 | 0,231 | 9/9 | **14** | 306 | 0,271 | 0,004 | **0/9, p = 0,0039** |
| `DONNEUR ASSERVI` | 32 | 0,234 | 9/9 | 14 | 306 | 0,272 | 0,003 | 0/9, p = 0,0039 |
| `CAPTEUR RETARDÉ` | 32 | 0,236 | 9/9 | 17 | 303 | 0,277 | 0,004 | 0/9, p = 0,0039 |

- **En ligne vs donneur asservi** : `p = 0,51` (L=24) et `p = 1,00` (L=32), différence médiane
  −0,0006 et −0,00002. Le calendrier produit en ligne, **rejoué en boucle ouverte sur un bloc
  différent**, reproduit le résultat. Les décisions en ligne ne portent **aucune information
  propre au bloc**.
- **Capteur retardé** : différence médiane 0,006 (L=24) et 0,003 (L=32). La fraîcheur du capteur
  vaut moins de 1 % de l'UCR.
- Le feedback **réduit bien la futilité** (0,190 → 0,035) — mais l'échange auquel il renonce
  coûte beaucoup plus que la futilité qu'il évite.

```
FEEDBACK_VALUE = OPEN_LOOP_SCHEDULE_EFFECT
```

Et l'explication est mécanique, dérivable avant l'expérience : sous `LAW_16`, la boucle ouverte
survit déjà **9/9** et prend déjà **100 %** de ce que le substrat rouvre à chaque opportunité
(87–97 % des événements sont bornés par la source, c'est-à-dire saturés). Il n'y a **rien à
récupérer** pour une politique temporelle : elle ne peut que renoncer.

---

## 5. Le pare-feu contre un contrôleur oracle

Trois axes séparés et vérifiés :

| | 08B | 08C | branche spatiale |
|---|---|---|---|
| `WHEN` | identique | **seul à varier** | identique |
| `AMOUNT` | **seul à varier** | figé au gagnant de 08B | figé |
| `WHERE` | identique | identique | *non ouverte* |

Tout ce que la politique lit passe par `sensor_readout`, auditée par AST (fixture 5) : champ de
matière, géométrie gelée, piste courante, sa propre réserve et ses propres décisions passées.
Jamais la provenance, le futur, l'issue terminale, la graine, l'appartenance à une cohorte, ni
la survie future du tracker.

**Lecteurs fantômes.** Seuils 0,40 / 0,45 / 0,50 / 0,55 / 0,60 plus la distribution de
`m − THRESH`, enregistrés à chaque point de contrôle. Le tracker officiel reste gelé à 0,45 et
reste le **seul** utilisé pour les critères. Aucun bras ne survit à 0,45 en échouant à 0,55 :

```
TRACKER_GAMING = EXCLUDED
```

**La branche spatiale n'a pas été ouverte.** Sa condition d'ouverture pré-déclarée exigeait un
plafond maintenu **malgré** une allocation sûre. 08B montre que l'allocation sûre ne maintient
pas le plafond : elle le **baisse**. La condition n'est pas remplie ; ouvrir la branche aurait
été la recherche d'un réglage favorable.

---

## 6. Confirmation prospective et transport vers `LAW_29`

Graines **930000+**, jamais utilisées. 45 blocs, 180 trajectoires, `t256` valide 45/45.

### 6.1 Les quatre prédictions scellées

| | verdict | détail |
|---|---|---|
| **C1** le plancher scinde le composant | **CONFIRMÉE** | `SINK_FLOOR` 9/9 et 9/9 scissions ; `PARENT` 0 et 0 (seuil scellé : ≥ 7 et ≤ 1) |
| **C2** le plafond de réserve baisse le flux | **CONFIRMÉE** | 0,538 et 0,535 de `PARENT` (bande scellée 0,35–0,75), 9/9 blocs strictement en dessous |
| **C3** aucune garde n'améliore le remplacement | **RÉFUTÉE COMME ÉNONCÉE** | direction correcte partout (Δ médian −0,160 et −0,138 à L=24, −0,120 et −0,156 à L=32) mais à L=24 le test des signes donne 2/7, **p = 0,18** |
| **C4** la sonde prédit ρ sous une seconde loi | **RÉFUTÉE COMME ÉNONCÉE** | `LAW_16` 18/18 et 17/18 dans un facteur 1,5 ; `LAW_29` **2/18** et 10/18 |

**C3** échoue parce que `PARENT` lui-même perd la piste dans **2 des 9 blocs** de la cohorte de
confirmation à L=24 (ITT 7/9, contre 9/9 en découverte). Dans ces deux blocs son UCR vaut 0 et
les gardes le battent. La direction tient largement ; le seuil pré-enregistré, non. Rapporté tel
quel, sans réécriture.

**C4** échoue pour la raison exacte identifiée en 08A : la sonde ne mesure que le côté source.
Sous `LAW_29` la piste meurt tôt — `PARENT` n'exécute que 65 (L=24) et 116 (L=32) événements sur
320, le reste tombant sans piste — donc le débit observé s'effondre et une sonde côté source
sur-prédit mécaniquement. Sous `LAW_16`, où la piste vit, la sonde tient à 18/18 et 17/18.

### 6.2 Les deux transports du feedback échouent tous les deux

| `LAW_29` | continuité ITT | UCR | tirs / 320 | espacement |
|---|---|---|---|---|
| `PARENT` | 0/9 · 3/9 | 0,000 | 65 · 116 | 16 |
| `ONLINE_STRICT` | 0/9 · 3/9 | 0,000 | 25 · 22 | 16 |
| `ONLINE_NORMALIZED` | 0/9 · 3/9 | 0,000 | 21 · 22 | 64 · 16 |

```
LAW29_TRANSPORT = GENERALIZATION_LIMIT_CONFIRMED
```

Conformément à la règle scellée, **aucun troisième réglage de sauvetage n'a été créé**.

### 6.3 Ce que la cohorte de confirmation a révélé sans que ce soit pré-enregistré

Dans la même cohorte, un effet **non prédit** est apparu : sous `LAW_29`, le plancher de
sécurité — celui qui fragmente 9/9 sous `LAW_16` — **maintient le composant vivant 9/9 aux deux
tailles**, avec 0 scission, 320/320 événements exécutés, et le **seul** UCR non nul de toute la
configuration. C'est une découverte **dans** une cohorte de confirmation ; elle n'est donc pas
rapportée comme confirmée. Elle a été testée prospectivement.

### 6.4 08E — le renversement de signe, confirmé sur une troisième cohorte neuve

Graines **910000+**, jamais utilisées. Trois prédictions ponctuelles scellées avant exécution.

| `LAW_29` | continuité ITT | scissions | pertes | UCR | délivré | tirs | ombre 0,55 |
|---|---|---|---|---|---|---|---|
| `SHAM` L=24 · L=32 | **9/9 · 9/9** | 0 · 0 | 0 · 0 | 0,000 | 0,000 | 0 | 9/9 · 9/9 |
| `PARENT` L=24 · L=32 | **0/9 · 0/9** | 0 · 0 | **9 · 9** | **0,000** | 0,501 · 0,507 | 71 · 114 | **0/9 · 0/9** |
| `SINK_FLOOR` L=24 · L=32 | **9/9 · 9/9** | **0 · 0** | 0 · 0 | **0,118 · 0,152** | 0,239 · 0,242 | **320 · 320** | **9/9 · 9/9** |

| prédiction scellée | verdict |
|---|---|
| **E1** plancher ≥ 7/9 de continuité, `PARENT` ≤ 4/9 | **CONFIRMÉE** (9/9 vs 0/9 aux deux tailles) |
| **E2** UCR du plancher > 0,05 et > `PARENT` (p < 0,05) | **CONFIRMÉE** |
| **E3** plancher ≤ 2/9 scissions sous `LAW_29` | **CONFIRMÉE** (0/9 et 0/9, contre **9/9** sous `LAW_16`) |

```
REGIME_DEPENDENT_REPAIR_CONFIRMED
```

Et ce n'est **pas** un sauvetage du détecteur : sous `SINK_FLOOR` le lecteur fantôme à **0,55**
voit un composant borné dans **9/9** blocs, alors que sous `PARENT` il n'en voit **aucun** (0/9).
Le composant est vivant à un seuil nettement au-dessus du plancher.

**Le mécanisme unifie les deux régimes.** Le signe d'une garde de sécurité est fixé par le mode
de défaillance du composant, pas par la garde :

| | `LAW_16` | `LAW_29` |
|---|---|---|
| composant | épais, robuste (SHAM `I/I₀` 0,75–0,85) | redistribue vite, fragile (SHAM `I/I₀` 0,47–0,58) |
| mode de défaillance sous forçage | **fragmentation** | **dissolution** |
| effet du plancher | amincit une large bande → **scinde 9/9** | évite l'excision complète → **sauve 9/9** |

---

## 7. Registre des revendications

| # | revendication | statut | preuve |
|---|---|---|---|
| 1 | sceaux, ascendance, bundle, artefacts parents intacts | **VÉRIFIÉ** | 3 sceaux, 28 fichiers `DEV_05`, bundle `0f398c8c…` *okay* |
| 2 | 6 des 8 « prédictions » de P07 étaient satisfaites par un plateau plat | **ÉTABLI** | seuls `s=128` discriminent |
| 3 | `ρ` n'est pas stationnaire | **ÉTABLI** | facteur apparié 1,72 [1,59 ; 2,34] et 3,03 [2,77 ; 3,13] |
| 4 | `CONSTANT_RATE` est réfuté hors fenêtre | **ÉTABLI** | 0 bloc gagné sur 18, RMSE ×4 à ×10 |
| 5 | `ρ` est mesurable indépendamment | **ÉTABLI** | 46/46 fenêtres bornées par la source dans 1,5 ; ratio 1,020 [0,986 ; 1,059] |
| 6 | `ρ` décroît, et la sonde le retrouve seule | **ÉTABLI** | ×3,11 et ×4,71, 9/9, p = 0,0039 |
| 7 | la limite est locale et sous-seuil, dans un support fixe | **ÉTABLI** | 4036/4036 rejets, 0 épuisement global |
| 8 | les 3 blocs non identiques sont expliqués par un critère préexistant | **QUALIFIÉ** | correspondance exacte, 0 faux positif |
| 9 | `EXCHANGE_MAGNITUDE_GENERALISES` était pré-létal | **RÉVOQUÉ** | 44,7 % du calendrier après la perte de piste |
| 10 | `UCR` n'est pas gonflable par un cycle futile | **VALIDÉ ADVERSARIALEMENT** | les 2 bras dégénérés classés derniers |
| 11 | le plancher scinde le composant sous `LAW_16` | **CONFIRMÉ** (C1) | 9/9 en découverte **et** en confirmation |
| 12 | le plafond de réserve baisse le flux, comme la sonde le prédit | **CONFIRMÉ** (C2) | 0,538 et 0,535 |
| 13 | aucune garde n'améliore le remplacement sous `LAW_16` | **DIRECTION ÉTABLIE, SEUIL RÉFUTÉ** (C3) | p = 0,18 à L=24 |
| 14 | le feedback local n'apporte aucune information | **ÉTABLI** | en ligne ≈ donneur asservi, p = 0,51 et 1,00 |
| 15 | le feedback ne se transporte pas vers `LAW_29` | **CONFIRMÉ** | strict et normalisé échouent tous deux |
| 16 | la sonde ne prédit rien quand le puits étrangle | **ÉTABLI** (réfutation de C4) | `LAW_29` 2/18 |
| 17 | le signe de la garde s'inverse avec le régime | **CONFIRMÉ** (E1–E3) | 9/9 vs 0/9, 3 prédictions scellées, 3ᵉ cohorte |
| 18 | ce n'est pas un sauvetage du détecteur | **ÉTABLI** | ombre 0,55 : 9/9 vs 0/9 |
| 19 | organisation / identité / individuation / vie | **NON TESTÉ** | aucun observable validé n'existe |

---
## 8. Ce que ces données ne permettent toujours pas

- Aucun observable d'organisation validé n'existe dans ce projet ; aucun n'a été inventé.
  `ORGANIZATION_PRESERVATION = NOT_TESTED`.
- L'unité indépendante reste le **bloc**. Les décisions internes d'une politique ne sont
  **jamais** des réplicats.
- `ρ` n'est mesuré que sur le côté **source** ; il ne prédit rien quand le puits étrangle.
- Un seul substrat, `p = 0,35`, une seule famille de conditions initiales, deux lois, deux à
  trois tailles.

```
ROUTE_E_VERDICT = NONE          AUTONOMOUS_RENEWAL = NOT_TESTED
IDENTITY = NOT_ESTABLISHED      INDIVIDUATION = NOT_ESTABLISHED
LIFE = NOT_ESTABLISHED          ORGANIZATION_PRESERVATION = NOT_TESTED
```
