# `WARPED_SCALE_CONTINUOUS_CAUSAL_RESPONSE_PILOT_00` — rapport final

**Branche** `dev/warped-scale-continuous-causal-response-pilot-00` · **parent vérifié**
`7cc1ffa0a782a34774a57094189ed19f6bd2b761` · **développement, définitivement**

## 0. Verdict

```
WSCCRP00_DISPOSITION = NO_EXACT_CONTINUOUS_CAUSAL_ORACLE
DETAIL               = MEMBERSHIP_JUMP_DOMINATED_ENDPOINT
```

Le point de mesure continu hérité franchit ses deux portes de signal — il y a une réponse
matérielle, et elle n'est pas de rang un — puis échoue au contrôle d'éligibilité de la Section 4 :
**≈ 99 % de son énergie de réponse provient de la réaffectation d'appartenance par le détecteur à
seuil, pas d'une réponse lisse du champ.**

Le pilote s'arrête avant Q4, avant Q5, et avant toute construction de représentation.

## 1. Ce qui a été établi

**Q2, signal matériel — PASS.** Les deux superfamilles TRAIN dépassent `ETA_b` dans les quatre
fondateurs d'entraînement, avec des marges de 3× à 10×. Le signal n'est pas porté par le bras
environnemental, qui est verrouillé et n'a pas été exécuté.

**Q3, rang — PASS.** `σ₂/σ₁ = 0,646`, bien au-dessus de la porte de 0,10 ; le mode dominant ne
porte que 59 % de l'énergie. La réponse continue n'est **pas** un gabarit unique mis à l'échelle.
C'est un résultat positif et non trivial : il réfute l'hypothèse `RANK_ONE_RESPONSE` que la forme
des trajectoires WSCPL00 rendait plausible.

**Q1 — `r = 0` exactement à `h = 0`** dans les 16 unités, comme le prédit la structure : les
opérateurs de porteur ne touchent que `Mf[0]`, que `a` ne lit pas.

## 2. Pourquoi l'arrêt, précisément

La décomposition imposée sépare, dans la réponse, ce qui vient d'un changement de **valeur de
champ** et ce qui vient d'un changement d'**appartenance** — le détecteur gelé redétecte à chaque
temps quelles cellules composent A et B, au seuil 0,30.

```
énergie attribuable à l'appartenance :  médiane 0,988   max 1,228   (seuil 0,50)
```

Le détail est plus instructif que le verdict. La réponse à masques figés **n'est pas petite** :
médiane 0,73 fois la réponse dynamique, et au-dessus du bruit dans 16 unités sur 16. Mais les
deux sont **presque orthogonales en forme** — corrélation médiane **−0,039**. Ce ne sont pas deux
mesures du même objet : ce sont deux objets différents.

Ce que le lecteur hérité mesure est donc, pour l'essentiel, **le seuil qui bascule des cellules
d'une composante à l'autre**. Appeler cela une géométrie causale multi-échelle serait précisément
l'erreur que la Section 4 interdit.

**Je n'ai pas basculé sur le lecteur à masques figés**, qui aurait donné un point de mesure
au-dessus du bruit partout. La Section 4 impose d'hériter la règle exécutable exactement, et les
artefacts parents la déterminent de façon unique. Changer de lecteur après avoir vu le résultat
aurait été un magasinage de point de mesure.

## 3. Ce qui n'a pas été fait

Aucune représentation construite : ni `NUISANCE_ONLY`, ni `FLAT_EUCLIDEAN`, ni `LOG_SCALE`, ni
`NONLINEAR_EUCLIDEAN`, ni `CURVED`, ni les deux contrôles. Aucune permutation d'étiquettes, aucune
statistique de courbure, aucun défaut de commutateur. Aucun descripteur sélectionné ni haché.
`LOCKED_DEV_EVALUATION` n'a jamais été créé : aucun fondateur alloué, aucun résultat ouvert.
Accès primaire et tenu à l'écart du projet : **faux**, tous les deux.

Plafond de preuve gelé **avant** exécution : les cinq familles de WSCPL00 se réduisent à **trois**
superfamilles, puisque le handoff tranche lui-même que réflexion intensive, réflexion extensive
et ablation totale sont des **cousines**. `FULL_PILOT_PASS_ELIGIBLE = false` dès le départ ; le
plafond était `SINGLE_SUPERFAMILY_TRANSFER`. Aucune quatrième famille n'a été inventée, ni avant
ni après. Le niveau de preuve disponible aurait été
`RESPONSE_INFORMED_HELD_OUT_FAMILY_TRANSFER`, jamais `STRICT_PROSPECTIVE_OUT_OF_FAMILY`, puisque
la superfamille environnementale a été affichée dans WSCPL00.

## 4. Registres

**20 démarrages moteur** sur 24 de qualification ; **0 sur 144** post-porte ; **0 nouveau bloc
fondateur** — les quatre fondateurs d'entraînement ont été rechargés depuis des points de
contrôle déjà commis. Zéro plantage, zéro reprise, zéro abandon, zéro rallonge. Ce budget de 168
est neuf et indépendant ; aucun crédit WSCPL00 inutilisé n'a été hérité.

**Écart de Phase 0, consigné.** Les deux relectures finales commises dans l'arbre WSCPL00 sont des
relectures d'**ETCMNFC**, pas de WSCPL00. Elles confirment ce qu'elles relisent ; la disposition
propre de WSCPL00 n'a **aucune** relecture indépendante. L'écart porte sur le périmètre d'un
document, pas sur un fait, donc `PHASE0_PARENT_EVIDENCE_CONTRADICTION` n'est pas déclenché — mais
il n'est écrit nulle part que WSCPL00 a été relu.

## 5. Ce que cet échec ne dit pas

Il ferme **uniquement** la formulation gelée : ce point de mesure, ce lecteur, ce point de
contrôle, cet horizon. Il ne prouve aucune absence d'influence causale — Q2 montre le contraire —
et ne réfute aucune représentation à échelle courbée. Il n'est affirmé ni qu'une fermeture
multi-échelle existe, ni qu'elle n'existe pas.

Jamais affirmé : prédiction de transition de branche, basculement de bassin, géométrie
universelle, loi de groupe de renormalisation, dimensions physiques courbées, gravité, pertinence
ou avantage quantique, clôture causale, appartenance, individualité, autonomie, organismalité,
reproduction, hérédité, vie, conscience. Aucun QUBO, aucun QPU.

`NEXT_HANDOFF_WARPED_SCALE_GEOMETRY_00.md` n'est **pas** émis : il est conditionné à un passage
complet du pilote.
