# `WARPED_SCALE_CLOSURE_PILOT_00` — rapport final

**Branche** `dev/warped-scale-closure-pilot-00` · **parent** `c5171b72f3ed2cdaba1968bdbd9ebf3776eab8d7`
**Portée** clôture du parent + audit sans moteur + pilote de développement borné
**Tout ce qui suit est du développement, définitivement.**

---

## 0. Verdict

```
WSCPL00_DISPOSITION = NO_VALID_MACRO_BRANCH_ENDPOINT
```

Le pilote s'arrête à la porte de faisabilité du point de mesure, **avant** de construire la
moindre représentation. La raison n'est pas que la branche macro soit constante — elle prend bien
les deux valeurs selon les blocs — mais qu'elle est **totalement insensible à l'intervention** :

> Aucune des cinq familles d'intervention admissibles, **y compris l'ablation totale du porteur
> `Mf ← 0` partout**, ne déplace le label de branche, dans aucun bloc de formulation.

Un point de mesure sans variance de label sous intervention n'offre rien à prédire. Les cinq
représentations obligatoires — euclidienne plate, logarithmique, métrique courbe apprise, base
euclidienne non linéaire forte, contrôle permuté — auraient toutes obtenu **exactement le même
score parfait**, y compris le contrôle aléatoire. Construire cette comparaison aurait produit un
tableau de nombres sans contenu.

---

## 1. Ce qui a été mesuré

### 1.1 La branche existe et bifurque

Depuis les quatre points de contrôle de développement (pas 390, les deux composantes encore
quasi équilibrées, |Δmasse| ≈ 1), le système **s'engage tôt et irréversiblement** :

| | `t = 0` | `t = 40` | `t = 120` | `t = 400` |
|---|---|---|---|---|
| bloc 61000, `m_A − m_B` | −1,013 | +1,560 | +5,021 | **+5,102** |
| bloc 61001, `m_A − m_B` | +0,802 | −1,504 | −6,000 | **−5,776** |
| bloc 61002, `m_A − m_B` | −0,940 | +0,475 | +5,777 | **+5,371** |

Les tailles passent de 21/21 à 21/13 ou 13/24, puis se figent. À partir de `t ≈ 120` la
trajectoire est plate jusqu'à 400. C'est une véritable **brisure de symétrie**, et elle est
**entièrement déterminée par l'assignation d'histoire fondatrice** : parité paire → `HL` → A
l'emporte ; parité impaire → `LH` → B l'emporte. Trois blocs sur trois.

Le nombre de composantes reste 2 partout, le signe du basculeur interne `σ` ne change jamais, et
la dominance en taille ne bascule jamais. Seule la dominance en masse traverse zéro, **une seule
fois**, dans le transitoire initial.

### 1.2 La branche ne répond à aucune intervention

Cinq familles appliquées au point de contrôle, puis 400 pas :

| famille | bloc 61000, `m_A − m_B` à `H` | bloc 61001 | label déplacé ? |
|---|---|---|---|
| `SHAM` | **+5,102** | **−5,776** | référence |
| `F1` transposition appariée du porteur | +5,264 | −5,935 | **non** |
| `F2` réflexion intensive | +5,395 | −6,071 | **non** |
| `F3` réflexion extensive | +5,366 | −6,040 | **non** |
| `F4` **ablation totale du porteur** (`Mf ← 0`) | +5,239 | −5,914 | **non** |
| `F5` perturbation environnementale `+0,5·N₀` | +7,893 | −9,285 | **non** |

**Aucun** bras ne franchit la frontière de décision. Pire pour l'espoir d'un sauvetage : **chaque**
intervention **augmente** `|Δmasse|`, c'est-à-dire éloigne encore le système de la transition.
Pour retourner le label il faudrait passer de +5 à −ε ; rien dans l'ensemble admissible n'en
approche.

### 1.3 La nuance qui compte

Les interventions **ont** un effet macro mesurable — `+5,10` contre `+7,89` n'est pas rien. Le
système est donc **causalement réactif** ; c'est le **label binaire** qui ne l'est pas, parce
qu'il vit au fond d'un bassin profond. L'échec est dans le **point de mesure**, pas dans
l'absence d'influence causale. C'est une distinction utile pour la suite, et elle est mesurée,
pas supposée.

---

## 2. Pourquoi je n'ai pas cherché un autre point de mesure

Le handoff exclut l'entrée dans un attracteur, l'effacement mémoire, la transition rare et la
réponse externe comme points de mesure alternatifs de ce pilote. Au-delà de cette interdiction,
enchaîner les définitions de branche jusqu'à ce que l'une bouge serait précisément le magasinage
de point de mesure que cette chaîne a documenté et condamné à trois reprises (`ETPC`, `EEFCA`,
`ETCMNFC`). Une porte de faisabilité qui ferme est un résultat ; la contourner en changeant la
cible ne l'est pas.

---

## 3. Ce que le pilote n'a pas fait, et ne prétend pas

Aucune représentation n'a été construite. Aucune métrique courbe n'a été apprise, gelée ou
évaluée. Aucun défaut de commutateur n'a été calculé. Aucun `alpha`, aucune dimension latente,
aucune marge de calibration n'a été choisie — donc aucune n'a pu être choisie en regardant un
résultat. Le rôle `UNTOUCHED_PILOT_EVALUATION` n'a **jamais été alloué ni ouvert**.

Il n'est donc affirmé **ni** qu'une fermeture multi-échelle approximative existe, **ni** qu'elle
n'existe pas. `NO_VALID_MACRO_BRANCH_ENDPOINT` ferme **uniquement** la formulation gelée de ce
pilote — pas la question.

Jamais affirmé : dimensions physiques courbées, gravité alignant des échelles biologiques, loi de
groupe de renormalisation, dynamique macro universelle, avantage quantique, appartenance,
individualité, clôture causale, autonomie, métabolisme, organismalité, reproduction, hérédité,
vie, conscience. Aucun QUBO n'a été formulé, aucun QPU touché.

`NEXT_HANDOFF_WARPED_SCALE_GEOMETRY_00.md` **n'est pas émis** : il est conditionné à la réussite
du pilote. La carte bornée de coordonnées causales candidates l'est aussi, et n'est donc pas
émise non plus.

---

## 4. Registres

**Démarrages moteur : 15** — 3 pour la faisabilité du point de mesure, 12 pour la réactivité à
l'intervention. Plafond de qualification 24. **Pilote : 0 sur 160.** Aucun nouveau bloc fondateur
créé : les probes réutilisent les quatre points de contrôle de développement déjà exposés et
commis, comme la discipline de budget le préfère. Zéro plantage, zéro reprise, zéro abandon,
**zéro rallonge après avoir vu un résultat**.

**Rôles.** `FORMULATION_TRAIN` = 61000–61002. `MODEL_SELECTION_VALIDATION` et
`UNTOUCHED_PILOT_EVALUATION` : **non alloués**, jamais ouverts — les allouer pour les abandonner
aussitôt aurait brûlé des blocs indépendants pour rien. Accès primaire et tenu à l'écart :
**faux**, dans les deux cas.

---

## 5. Force du dossier, avant / après

| | avant | après |
|---|---|---|
| clôture d'`ETCMNFC` | en suspens | **close, append-only**, avec les étiquettes séparées |
| revendication `CHMR` | slogans hérités | **résolue depuis ses artefacts gelés**, avec `STRONG_PAPER_GATE = FAIL` remis à côté |
| oracle de redémarrage causal exact | supposé | **vérifié et documenté** |
| diversité des familles d'intervention | inconnue | **5 familles déjà implémentées**, inventoriées |
| point de mesure de branche macro | non testé | **testé et rejeté : non réactif à l'intervention** |
| fermeture multi-échelle | non testée | **toujours non testée** |

Solde : positif sur l'inventaire et la clôture, **nul sur la question scientifique du pilote**.
