# `P09_DOSE_YOKED_GUARD_SIGN_CLOSURE` — rapport

> **Passe de stabilisation, 2026-08-09.** Les tests de survie de ce rapport étaient des Fisher exacts à échantillons indépendants ; le plan est **apparié par bloc fondateur**. Ils sont remplacés ici par le test exact de McNemar. La « équivalence de dose » est une **porte de comparabilité**, pas un test d'équivalence. Les énoncés de médiation exclusive sont retirés. Détail complet et TOST post hoc : `STABILIZATION_P09.md`.

**2026-08-09** · parent `070aef4b0fa310ae3e9c3aa9a893ebae889cac09`
(branche `dev/route-e-safe-actuation-and-feedback-08`,
bundle `_bundles/route-e-safe-actuation-08.bundle`,
SHA-256 `05b732520b3341454be270098ad5fcb31f78f344e6131559d685549da01954e4`)
· 1 protocole scellé, 1 séquence exogène scellée · 216 trajectoires, 252 appels moteur ·
aucun artefact parent modifié.

> **Verdict.** Le renversement de `SINK_FLOOR` entre `LAW_16` et `LAW_29` **n'est pas un
> renversement de l'allocation**. Le côté **nuisible** sous `LAW_16` est bien un effet
> d'allocation, à dose appariée et vérifiée. Le côté **sauvetage** sous `LAW_29` s'obtient
> **entièrement sans plancher**, par la seule réduction de quantité — et l'équivalence de dose y
> échoue de toute façon.

---

## 1. Un contraste apparié existait-il déjà dans `P08` ?

**Non.** Vérifié avant tout appel moteur, sur les artefacts `P08` seuls :

| `LAW_29` | masse délivrée / `M₂₅₆`, médiane | étendue par bloc | règle | survie ITT |
|---|---|---|---|---|
| `PARENT` | 0,480 · 0,503 | [0,426 ; 0,537] · [0,481 ; 0,561] | `floor=0` | 0/18 · 3/18 |
| `SINK_FLOOR` | **0,230 · 0,243** | [0,210 ; 0,263] · [0,231 ; 0,275] | `floor=0,5` | 18/18 · 18/18 |
| `SRC_CAP` | 0,450 · 0,467 | [0,416 ; 0,496] · [0,449 ; 0,520] | `ceil=0,9` | 0/9 · 1/9 |
| `ONLINE_NORMALIZED` | 0,342 · 0,471 | [0,306 ; 0,505] · [0,446 ; 0,522] | `floor=0` | 0/9 · 3/9 |

Le bras à allocation `PARENT` le plus proche délivre **1,49×** (L=24) et **1,92×** (L=32) la masse
du plancher, et **aucune étendue par bloc ne se recouvre**. De plus, chaque bras bas-dosé porte
une seconde différence (un plafond, ou un déclencheur). Un contraste asservi était donc
nécessaire. `P09` a été exécuté.

## 2. Construction de la séquence exogène

Source : le **ledger événementiel complet** de `08B SINK_FLOOR` — vérifié complet avant
scellement : **320 événements sur 320 par bloc, 18 blocs, aucun sous-échantillonnage**.
Appariement cyclique entre blocs **distincts** et cohortes **distinctes** : le bloc receveur
d'indice `k` (graines 890000+) rejoue le bloc donneur `(k+1) mod 9` de la même taille
(graines 990000+). Mise à l'échelle `requête_k = réalisé_donneur_k × (M₂₅₆ receveur / M₂₅₆ donneur)`.
Pour chaque événement, `WHEN`, `SOURCE_REQUESTED`, `SINK_REQUESTED`, `SOURCE_REALIZED`,
`SINK_REALIZED` sont conservés séparément.

Séquence scellée : `p09_sequences.json`,
SHA-256 `7f8e5e9f116aae96b13c99f8e3ca78685edc1fcebebfd9197b9c4ac32e086bd2`.
Elle est **conservative par construction** : c'est ce que le plancher lui-même a réalisé sous
`LAW_16`, et à état donné la capacité du puits sous la règle `PARENT` est toujours ≥ celle sous
la règle plancher. Total demandé : 0,266 à 0,359 `M₂₅₆` selon le donneur, soit **13× moins** que
la pleine dose (4,000 `M₂₅₆`).

`PARENT_Q_REPLAY` et `FLOOR_Q_REPLAY` reçoivent **exactement** la même séquence, aux mêmes
instants, sur le même support gelé. **Seule la règle d'allocation par site diffère.**
`PARENT_LOW_CONSTANT` reçoit le même **total** demandé, le même **nombre** d'événements non nuls,
répartis aussi régulièrement que possible.

## 3. Équivalence de dose réellement obtenue

Statistique scellée : rapport apparié par bloc de la masse **délivrée**,
`FLOOR_Q_REPLAY / PARENT_Q_REPLAY`. Marge scellée avant exécution : médiane dans
**[0,847 ; 1,180]**, IC 95 % bootstrap dans **[0,781 ; 1,280]** — soit 1,5 à 3 écarts-types
bloc-à-bloc de `P08` pour la bande interne.

| | rapport médian | IC 95 % | `PARENT_Q` délivré | `FLOOR_Q` délivré | verdict |
|---|---|---|---|---|---|
| `LAW_16` L=24 | **1,001** | [0,840 ; 1,006] | 0,295 | 0,274 | **PASS** |
| `LAW_16` L=32 | **0,906** | [0,847 ; 1,045] | 0,298 | 0,279 | **PASS** |
| `LAW_29` L=24 | 0,796 | [0,692 ; 0,883] | 0,306 | 0,231 | **ÉCHEC** |
| `LAW_29` L=32 | 0,767 | [0,705 ; 0,812] | 0,308 | 0,244 | **ÉCHEC** |

Sous `LAW_29`, même en lui demandant exactement la même chose, le plancher **ne peut pas
délivrer** ce que le parent délivre : il reste 20 à 23 % en dessous, IC entièrement sous la
bande. La règle scellée s'applique : **aucune revendication d'allocation isolée n'est faite sous
`LAW_29`.**

## 4. Résultats sous les deux lois et les deux tailles

Masse tentée en unités de `M₂₅₆` ; 9 blocs par cellule ; intention de traiter.

| cellule | bras | survie ITT | scissions | dissolutions | UCR | tentée | délivrée | inc. retiré | frais retenu |
|---|---|---|---|---|---|---|---|---|---|
| `LAW_16` L=24 | `SHAM` | 9/9 | 0 | 0 | 0,000 | 0,000 | 0,000 | 0,000 | 0,000 |
| | `PARENT_FULL` | **9/9** | 0 | 0 | **0,386** | 4,000 | 0,610 | 0,455 | 0,385 |
| | `PARENT_LOW_CONSTANT` | **9/9** | 0 | 0 | 0,244 | 0,306 | 0,292 | 0,259 | 0,244 |
| | `PARENT_Q_REPLAY` | **9/9** | 0 | 0 | 0,227 | 0,306 | 0,295 | 0,278 | 0,226 |
| | `FLOOR_Q_REPLAY` | **0/9** | **9** | 0 | 0,202 | 0,306 | 0,274 | 0,262 | 0,202 |
| | `FLOOR_FULL` | **0/9** | **9** | 0 | 0,217 | 4,000 | 0,302 | 0,281 | 0,217 |
| `LAW_16` L=32 | `PARENT_FULL` | **9/9** | 0 | 0 | **0,341** | 4,000 | 0,439 | 0,388 | 0,341 |
| | `PARENT_LOW_CONSTANT` | **9/9** | 0 | 0 | 0,267 | 0,308 | 0,308 | 0,281 | 0,267 |
| | `PARENT_Q_REPLAY` | **9/9** | 0 | 0 | 0,246 | 0,308 | 0,298 | 0,287 | 0,246 |
| | `FLOOR_Q_REPLAY` | **0/9** | **9** | 0 | 0,217 | 0,308 | 0,279 | 0,266 | 0,217 |
| | `FLOOR_FULL` | **0/9** | **9** | 0 | 0,224 | 4,000 | 0,305 | 0,279 | 0,224 |
| `LAW_29` L=24 | `SHAM` | 9/9 | 0 | 0 | 0,000 | 0,000 | 0,000 | 0,000 | 0,000 |
| | `PARENT_FULL` | **1/9** | 0 | **8** | **0,000** | 4,000 | 0,465 | 0,409 | 0,000 |
| | `PARENT_LOW_CONSTANT` | **9/9** | 0 | 0 | **0,128** | 0,306 | 0,208 | 0,183 | 0,128 |
| | `PARENT_Q_REPLAY` | 6/9 | 0 | 3 | **0,147** | 0,306 | 0,306 | 0,289 | 0,147 |
| | `FLOOR_Q_REPLAY` | **9/9** | 0 | 0 | 0,117 | 0,306 | 0,231 | 0,227 | 0,117 |
| | `FLOOR_FULL` | **9/9** | 0 | 0 | 0,117 | 4,000 | 0,231 | 0,227 | 0,117 |
| `LAW_29` L=32 | `PARENT_FULL` | **1/9** | 0 | **8** | **0,000** | 4,000 | 0,521 | 0,430 | 0,000 |
| | `PARENT_LOW_CONSTANT` | **9/9** | 0 | 0 | **0,175** | 0,308 | 0,238 | 0,219 | 0,175 |
| | `PARENT_Q_REPLAY` | **9/9** | 0 | 0 | **0,200** | 0,308 | 0,308 | 0,297 | 0,200 |
| | `FLOOR_Q_REPLAY` | **9/9** | 0 | 0 | 0,153 | 0,308 | 0,244 | 0,240 | 0,152 |
| | `FLOOR_FULL` | **9/9** | 0 | 0 | 0,157 | 4,000 | 0,252 | 0,247 | 0,156 |

Le `SHAM` survit **9/9 dans les quatre cellules** et son UCR est structurellement nul
(incumbent retiré = 0, frais retenu = 0). Le turnover spontané attribuable au `SHAM` se lit sur
`I/I₀` terminal : 0,75–0,81 sous `LAW_16`, 0,47–0,58 sous `LAW_29`.

## 5. Les quatre contrastes primaires scellés

| cellule | contraste | survie | McNemar exact apparié | UCR : Δ médian [IC] , p |
|---|---|---|---|---|
| `LAW_16` L=24 | **allocation** `FLOOR_Q − PARENT_Q` | 9/9 → **0/9** (**9 scissions**) | **p < 0,0001** | −0,012 [−0,048 ; −0,010] p=0,004 |
| | profil temporel | 9/9 → 9/9 | p = 1,00 | −0,019 [−0,027 ; +0,008] p=0,18 |
| | réduction de dose | 9/9 → 9/9 | p = 1,00 | −0,135 [−0,171 ; −0,121] p=0,004 |
| | réplication `P08` | 9/9 → **0/9** | **p < 0,0001** | −0,169 [−0,176 ; −0,162] p=0,004 |
| `LAW_16` L=32 | **allocation** | 9/9 → **0/9** (**9 scissions**) | **p < 0,0001** | −0,038 [−0,050 ; −0,014] p=0,004 |
| | profil temporel | 9/9 → 9/9 | p = 1,00 | −0,022 [−0,024 ; −0,019] p=0,004 |
| | réduction de dose | 9/9 → 9/9 | p = 1,00 | −0,071 [−0,085 ; −0,053] p=0,004 |
| | réplication `P08` | 9/9 → **0/9** | **p < 0,0001** | −0,118 [−0,141 ; −0,111] p=0,004 |
| `LAW_29` L=24 | allocation *(dose non appariée)* | 6/9 → 9/9 | p = 0,21 | −0,022 [−0,039 ; +0,115] p=0,51 |
| | profil temporel | 9/9 → 6/9 | p = 0,21 | +0,015 [−0,134 ; +0,029] p=0,51 |
| | **réduction de dose** | **1/9 → 9/9** | **p = 0,0078 (McNemar exact apparié)** | **+0,128 [+0,124 ; +0,136] p=0,039** |
| | réplication `P08` | **1/9 → 9/9** | **p = 0,0078 (McNemar exact apparié)** | +0,117 [+0,113 ; +0,127] p=0,039 |
| `LAW_29` L=32 | allocation *(dose non appariée)* | 9/9 → 9/9 | p = 1,00 | **−0,052 [−0,076 ; −0,041] p=0,004** |
| | profil temporel | 9/9 → 9/9 | p = 1,00 | +0,028 [+0,019 ; +0,043] p=0,004 |
| | **réduction de dose** | **1/9 → 9/9** | **p = 0,0078 (McNemar exact apparié)** | **+0,175 [+0,172 ; +0,183] p=0,039** |
| | réplication `P08` | **1/9 → 9/9** | **p = 0,0078 (McNemar exact apparié)** | +0,157 [+0,151 ; +0,159] p=0,039 |

**Ce que cela dit, ligne par ligne.**

- **Le résultat `P08` se réplique exactement** dans les quatre cellules : le plancher scinde 9/9
  sous `LAW_16` et sauve 8/9 blocs de plus sous `LAW_29`.
- **Sous `LAW_16`, à dose appariée et vérifiée, l'allocation seule détruit le composant** : même
  séquence, mêmes instants, même support, **9/9 scissions contre 0/9**. C'est un effet
  d'allocation propre, `p < 0,0001` aux deux tailles.
- **Sous `LAW_29`, la réduction de quantité seule suffit.** `PARENT_LOW_CONSTANT` n'a **aucun
  plancher** — allocation `PARENT` pure — et passe de **1/9 à 9/9**, `p = 0,0078 (McNemar exact apparié)`, aux deux
  tailles, avec un UCR **supérieur** à celui du plancher (0,128 contre 0,117 ; 0,175 contre 0,157).
- **Le plancher n'ajoute rien de détectable sous `LAW_29`** : +3/9 à L=24 (p = 0,21) et 0/9 à
  L=32 ; et à L=32 il **coûte** de l'UCR à séquence identique (−0,052, p = 0,004).
- Le profil temporel n'a d'effet significatif sur la survie nulle part (p = 0,21 et 1,00).

## 6. Adjudication scellée

```
DOSE_EQUIVALENCE_LAW_16 = PASS      DOSE_EQUIVALENCE_LAW_29 = FAIL
FLOOR_HARMFUL_UNDER_LAW_16 = true   FLOOR_BENEFICIAL_UNDER_LAW_29 = false
LOW_CONSTANT_RESCUES_LAW_29 = true

VERDICT = FLOOR_SPECIFIC_MECHANISM_NOT_IDENTIFIABLE
```

La règle scellée est explicite : équivalence de dose en échec → aucune revendication d'allocation
isolée. Et la preuve positive va dans l'autre sens : le sauvetage s'obtient **sans plancher**.

**Formulation maximale autorisée, et elle ne couvre plus le sauvetage :**

> L'effet de l'allocation au seuil est **nuisible** sous `LAW_16` à dose appariée. Sous `LAW_29`,
> le sauvetage attribué au plancher en `P08` est **expliqué par le throttling de dose** : une
> allocation `PARENT` pure délivrant la même faible masse sauve tout aussi bien, avec un meilleur
> remplacement.

`P08` avait écrit « une garde de sécurité dont le signe s'inverse avec le mode de défaillance ».
**Cette formulation est retirée.** Le plancher ne change pas de signe : il est nuisible sous
`LAW_16` et **inerte** sous `LAW_29` une fois la dose contrôlée. Ce qui change de régime, c'est
**la sensibilité à la dose** : sous `LAW_16` diviser la dose par 13 ne change rien à la survie
(9/9 → 9/9) ; sous `LAW_29` c'est tout le sauvetage (1/9 → 9/9).

## 7. Registre des revendications

| # | revendication | statut | preuve |
|---|---|---|---|
| 1 | aucun contraste apparié en dose n'existait dans `P08` | **ÉTABLI** | rapports 1,49× et 1,92×, aucun chevauchement |
| 2 | la séquence exogène est complète et vient d'un autre bloc et d'une autre cohorte | **VÉRIFIÉ** | 320/320 événements, appariement cyclique, sceau |
| 3 | équivalence de dose atteinte sous `LAW_16` | **ÉTABLI** | 1,001 et 0,906, IC dans la marge scellée |
| 4 | équivalence de dose **non** atteinte sous `LAW_29` | **ÉTABLI** | 0,796 et 0,767, IC entièrement sous la bande |
| 5 | le résultat `P08` se réplique | **CONFIRMÉ** | 9/9 scissions et +8/9 survie, 4 cellules |
| 6 | sous `LAW_16` la nocivité du plancher est un effet d'allocation | **ÉTABLI** | dose appariée, 9/9 vs 0/9, p < 0,0001 |
| 7 | sous `LAW_29`, une dose basse **sans garde suffit à reproduire** le sauvetage (suffisance seulement ; la médiation exclusive par la dose n'est pas établie) | **ÉTABLI** | `PARENT_LOW_CONSTANT` sans plancher : 1/9 → 9/9, p = 0,0078 (McNemar exact apparié) |
| 8 | sous `LAW_29` le plancher ajoute un effet propre | **NON IDENTIFIABLE** | équivalence en échec ; +3/9 p = 0,25 (McNemar exact apparié) ; UCR −0,052 à L=32 |
| 9 | « le signe de la garde s'inverse avec le mode de défaillance » | **RETIRÉ** | le sauvetage est dose-dépendant |
| 10 | le profil temporel explique le sauvetage | **RÉFUTÉ** | p = 0,21 et 1,00 sur la survie |
| 11 | `FAILURE_MODE_CAUSATION` | **NON IDENTIFIÉ** | le mode de défaillance n'a jamais été manipulé |
| 12 | organisation / identité / individuation / vie | **NON TESTÉ** | aucun observable validé n'existe |

## 8. Fermeture

Aucun troisième sauvetage, aucune nouvelle politique, aucune nouvelle `LawSpec`, aucune branche
organisationnelle, aucun allongement d'horizon. Le programme est clos.

```
ROUTE_E_VERDICT = NONE          AUTONOMOUS_RENEWAL = NOT_TESTED
IDENTITY = NOT_ESTABLISHED      INDIVIDUATION = NOT_ESTABLISHED
LIFE = NOT_ESTABLISHED          ORGANIZATION_PRESERVATION = NOT_TESTED
```
