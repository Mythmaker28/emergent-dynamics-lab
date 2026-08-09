# Corrigendum à `PROGRAM_08` — enregistré, non rétroactif

`P08` (`070aef4b0fa310ae3e9c3aa9a893ebae889cac09`) **n'est pas modifié**. Ses artefacts restent
scellés et vérifiés, et `MANUSCRIPT_V1.md` reste archivé tel quel comme récit d'avant-P09. Ce
fichier corrige les **dispositions** et publie les tableaux que `P08` avait résumés.

---

## 1. Dispositions corrigées

```
FEEDBACK_VALUE            = NOT_ESTABLISHED
TRACKER_GAMING            = NOT_DETECTED_AT_ARM_LEVEL
TRAJECTORY_EXCEPTION      = 1/378
SINK_FLOOR_LAW16          = HARMS
SRC_CAP_LAW16             = NO_IMPROVEMENT
PHI_STATUS                = RESTRICTED_TO_SOURCE_BOUND_WINDOWS
RHO_STATUS                = PROSPECTIVELY_MEASURED_CAPACITY_PROXY + NONSTATIONARY
FAILURE_MODE_CAUSATION    = NOT_IDENTIFIED
```

Ce qui change par rapport au texte de `P08`, et pourquoi :

- **`FEEDBACK_VALUE`** : `P08` avait retenu `OPEN_LOOP_SCHEDULE_EFFECT`. C'est une
  sur-interprétation : l'égalité entre l'en-ligne et le donneur asservi est une **non-différence**,
  pas une équivalence démontrée avec marge scellée. La disposition correcte est
  `NOT_ESTABLISHED`, la non-différence étant rapportée comme telle avec son intervalle.
- **`TRACKER_GAMING`** : `EXCLUDED` était trop fort. Le critère pré-enregistré est un critère de
  **bras** ; il n'est violé nulle part. Une trajectoire sur 378 reste vivante à 0,45 et morte à
  0,50 et 0,55. La disposition honnête est `NOT_DETECTED_AT_ARM_LEVEL`, avec l'exception déclarée.
- **`RHO_STATUS`** : `INDEPENDENTLY_PREDICTED` suggère une mesure de la grandeur elle-même. La
  sonde mesure une **capacité de réouverture côté source**, qui se trouve prédire le débit dans
  le régime où la source borne. `PROSPECTIVELY_MEASURED_CAPACITY_PROXY` est la formulation exacte.
- **`PHI_STATUS`** : la restriction n'est pas seulement temporelle (fenêtre d'estimation), elle
  est aussi **de régime** : `Φ` n'a de contenu que dans les fenêtres bornées par la source.
- **`FAILURE_MODE_CAUSATION`** : `P08` a écrit que « le signe de la garde est fixé par le mode de
  défaillance ». Deux lois ne l'établissent pas, et le mode de défaillance n'a jamais été
  manipulé. **Non identifié.** C'est précisément ce que `P09` teste, sur l'axe dose.

---

## 2. La factorielle 2×2 complète (08B, `LAW_16`, graines 990000+, 9 blocs par cellule)

| `floor` | `ceil` | bras | L | UCR | IC 95 % | survie ITT | scissions | délivré | inc. retiré | frais retenu | part futile |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0,00 | 1,00 | `PARENT` | 24 | **0,3868** | [0,369 ; 0,393] | **9/9** | 0 | 0,620 | 0,460 | 0,387 | 0,190 |
| 0,00 | 1,00 | `PARENT` | 32 | **0,3330** | [0,320 ; 0,342] | **9/9** | 0 | 0,414 | 0,377 | 0,333 | 0,034 |
| 0,00 | 0,90 | `SRC_CAP` | 24 | 0,2355 | [0,224 ; 0,267] | 9/9 | 0 | 0,314 | 0,284 | 0,236 | 0,017 |
| 0,00 | 0,90 | `SRC_CAP` | 32 | 0,1796 | [0,171 ; 0,186] | 9/9 | 0 | 0,228 | 0,215 | 0,180 | 0,001 |
| 0,50 | 1,00 | `SINK_FLOOR` | 24 | 0,2157 | [0,197 ; 0,227] | **0/9** | **9** | 0,306 | 0,284 | 0,216 | 0,044 |
| 0,50 | 1,00 | `SINK_FLOOR` | 32 | 0,2250 | [0,217 ; 0,245] | **0/9** | **9** | 0,308 | 0,284 | 0,225 | 0,061 |
| 0,50 | 0,90 | `BOTH_SAFE` | 24 | 0,2267 | [0,196 ; 0,244] | **0/9** | **9** | 0,351 | 0,298 | 0,227 | 0,097 |
| 0,50 | 0,90 | `BOTH_SAFE` | 32 | 0,1958 | [0,176 ; 0,217] | **0/9** | **9** | 0,265 | 0,243 | 0,196 | 0,037 |

`SINK_FLOOR_LAW16 = HARMS` (9/9 scissions, UCR en baisse) · `SRC_CAP_LAW16 = NO_IMPROVEMENT`
(survie inchangée, UCR en baisse, flux à 0,51–0,55 du parent).

---

## 3. Identité de chaque cohorte

| base de graines | phase | lois | tailles | blocs |
|---|---|---|---|---|
| **990000+** | P07 découverte, puis P08 08A / 08B / 08C | `LAW_16` | 24, 32 | 9 par taille |
| **950000+** | P07 confirmation 07D | `LAW_16` (24, 32, 40) + `LAW_29` (24, 32) | — | 9 par configuration |
| **930000+** | P08 confirmation 08D | `LAW_16` + `LAW_29` | 24, 32 | 9 par configuration |
| **910000+** | P08 confirmation 08E | `LAW_29` | 24, 32 | 9 par configuration |
| **890000+** | **P09** | `LAW_16` + `LAW_29` | 24, 32 | 9 par configuration |

Aucune graine n'est réutilisée entre une découverte et sa confirmation.

---

## 4. `3/9` contre `0/9` — l'explication

Il s'agit du **même bras** (`PARENT`, `LAW_29`, L=32) dans **deux cohortes indépendantes** :
08D sur les graines 930000+ donne **3/9**, 08E sur les graines 910000+ donne **0/9**.

- Fisher exact bilatéral : **p = 0,206**. La différence n'est pas significative.
- Les temps de premier échec se recouvrent : 08D `[4240, 4288, 4928, 5728, 5808, 5936]`,
  08E `[4080, 4384, 4640, 5216, 5984, 6032, 6240, 6768, 6768]`.
- Dans les deux cohortes, l'échec est une **dissolution** et les trois survivants de 08D sont des
  blocs dont l'échec serait tombé après l'horizon.

Ce n'est donc pas une contradiction : c'est la variation d'échantillonnage attendue d'un bras dont
la probabilité de survie est faible mais non nulle, estimée sur 9 blocs.

---

## 5. SHAM et composantes séparées de l'UCR

Le SHAM ne reçoit **aucun** opérateur : son incumbent retiré est exactement 0, son frais retenu
exactement 0, donc son UCR est **structurellement** 0. Le turnover attribuable au SHAM se lit sur
`I/I₀` terminal, et c'est lui qui distingue les deux lois.

| cohorte | loi | L | survie ITT | `I/I₀` terminal (turnover spontané) | inc. retiré | frais | UCR |
|---|---|---|---|---|---|---|---|
| 08B 990000+ | `LAW_16` | 24 | 9/9 | **0,749** | 0,000 | 0,000 | 0,000 |
| 08B 990000+ | `LAW_16` | 32 | 9/9 | **0,811** | 0,000 | 0,000 | 0,000 |
| 08D 930000+ | `LAW_16` | 24 · 32 | 9/9 · 9/9 | 0,750 · 0,809 | 0,000 | 0,000 | 0,000 |
| 08D 930000+ | `LAW_29` | 24 · 32 | 9/9 · 9/9 | **0,473 · 0,579** | 0,000 | 0,000 | 0,000 |
| 08E 910000+ | `LAW_29` | 24 · 32 | 9/9 · 9/9 | **0,478 · 0,585** | 0,000 | 0,000 | 0,000 |

Le SHAM survit **9/9 dans les huit cellules**. `LAW_29` perd spontanément 52 % de son incumbent
là où `LAW_16` en perd 25 % : la différence de régime est intrinsèque, mesurée sans opérateur, et
reproductible d'une cohorte à l'autre à 0,005 près.

---

## 6. La trajectoire signalée par le Check 9

`LAW_29_L24_S930001`, bras `ONLINE_NORMALIZED`, cohorte 08D. `floor = 0.0` — **aucun plancher**,
donc aucun mécanisme de « parking » possible. Survie ITT = `False`. À l'horizon un composant
existe à 0,45 (`T = 23,90`) mais aucun à 0,50 ni à 0,55 : un résidu mince, pas un objet préservé.
UCR = 0,031, délivré 0,329 `M₂₅₆`. Le bras est déjà en échec sur tous les critères.

C'est **1 trajectoire sur 378**. Le critère pré-enregistré de `TRACKER_GAMING` est un critère de
bras et n'est violé dans aucun bras ; l'exception est déclarée ici plutôt que supprimée.

---

## 7. 08C — fixe, en ligne, donneur asservi, capteur retardé, avec intervalles d'effet

| L | bras | UCR | IC 95 % | tirs / 320 | vs FIXE (Δ, IC, p) | vs EN LIGNE (Δ, IC, p) |
|---|---|---|---|---|---|---|
| 24 | `FIXE` | **0,3868** | [0,369 ; 0,393] | 264 | — | — |
| 24 | `EN LIGNE` | 0,3054 | [0,288 ; 0,346] | **18** | −0,0838 [−0,1000 ; −0,0229] p=0,0039 | — |
| 24 | `DONNEUR ASSERVI` | 0,3104 | [0,288 ; 0,332] | 18 | −0,0757 [−0,0995 ; −0,0552] p=0,0039 | **+0,0006 [−0,0199 ; +0,0103] p=0,508** |
| 24 | `CAPTEUR RETARDÉ` | 0,3119 | [0,291 ; 0,347] | 23 | −0,0776 [−0,0966 ; −0,0217] p=0,0039 | +0,0062 [+0,0012 ; +0,0076] p=0,039 |
| 32 | `FIXE` | **0,3330** | [0,320 ; 0,342] | 320 | — | — |
| 32 | `EN LIGNE` | 0,2309 | [0,220 ; 0,243] | **14** | −0,0985 [−0,1011 ; −0,0971] p=0,0039 | — |
| 32 | `DONNEUR ASSERVI` | 0,2337 | [0,224 ; 0,238] | 14 | −0,0963 [−0,1067 ; −0,0956] p=0,0039 | **+0,0000 [−0,0091 ; +0,0068] p=1,000** |
| 32 | `CAPTEUR RETARDÉ` | 0,2357 | [0,225 ; 0,243] | 17 | −0,0962 [−0,0977 ; −0,0937] p=0,0039 | +0,0034 [−0,0005 ; +0,0048] p=0,180 |

L'en-ligne est **strictement moins bon** que le fixe, aux deux tailles, 0/9. Sa différence avec le
donneur asservi est **non détectée**, avec un intervalle qui contient zéro — ce qui **n'est pas**
une preuve d'équivalence : aucune marge d'équivalence n'avait été scellée pour ce contraste.
D'où `FEEDBACK_VALUE = NOT_ESTABLISHED`.

Le capteur retardé bat l'en-ligne d'un montant **positif mais minuscule** (+0,006 et +0,003) :
rendre le capteur périmé n'abîme rien, ce qui est cohérent avec l'absence d'information en ligne.
