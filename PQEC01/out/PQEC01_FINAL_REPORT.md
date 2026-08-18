# PQEC01 — calibration prospective de l'environnement `Q` résolu en position
## Rapport final — 128 départs scientifiques gelés, exécutés et analysés

```
BRANCHE            codex/prospective-q-environment-calibration-01
PARENT_TIP         86291212955d4a4816efc1ebd671fbd234bf574c
C1 instrumentation 0c8ed487641a06904f2690b23ee991857088ca00
C2 GEL, SEUL       0bba579f46895248364f3c74cd3c0e798c26eb4a
C3 128 départs     7d97205818ae723683280053512a27f1872db375
FINAL_DISPOSITION  PROSPECTIVE_Q_ENVIRONMENT_OPERATOR_NOT_IDENTIFIED__ADDITIONAL_INSTRUMENTATION_REQUIRED
PORTES             10 / 13
```

## Les dix réponses

**1. Combien de départs scientifiques gelés, et combien réellement utilisés ?**
**40 (Phase A) + 88 (Phase B, 44 à B1 et 44 à B2) = 128**, exactement le nombre gelé et exactement
le plafond. Toutes les graines gelées ont tourné, une seule fois chacune, avec les partitions
découverte/validation du gel. **Aucune graine de réserve utilisée**, aucun monde écarté, remplacé
ou rejoué, **zéro invalidité technique**. Le pare-feu de résultats a tenu : pendant l'exécution
seuls le code de retour, l'existence du fichier, sa taille, son schéma, sa somme de contrôle et
les drapeaux d'invariants moteur ont été lus.

**2. L'instrumentation était-elle physiquement inerte ?** **Oui — `INSTRUMENTATION_INERTNESS =
PASS`.** Sept fixtures différentielles non scientifiques (`L = 5`, 8 pas, `kY` jusqu'à 0,90,
`muY` jusqu'à 0,20, 18 naissances `Y` réelles) concordent **bit à bit à chaque pas** avec un monde
nu sur les six champs, les **trois** états de générateur, les compteurs et le `state_hash`. Le seul
endroit où des lignes de physique sont dupliquées — la ré-implémentation verbatim des quatre
sous-décalages `Y` — est vérifié par un contrôle de source **séquentiel** doté de **trois contrôles
négatifs** (bloc de compteurs déplacé, mutation ajoutée, ligne supprimée) : les trois se
déclenchent. Le fichier observateur est **identique octet pour octet** à celui qui a produit les
128 archives ; des lignes mortes qu'il contient sont **signalées, pas supprimées**, précisément
pour ne pas casser cette provenance.

**3. L'environnement spatial complet de Phase A a-t-il été identifié ?** **Oui.** 40 mondes, champ
pré-réaction complet à **chaque** pas. Profil radial d'exposition culminant à **r = 1** (3,036)
plutôt qu'à la source (2,873) et décroissant à 0,08 en r = 12 ; noyau de transition d'exposition
aligné sur l'événement à 25 états avec `P(rester à Q = 0) = 0,8208`. Exposition moyenne au niveau
du monde **2,8730** (sd 0,7754, ETR 4,27 %). **La borne inférieure sans hypothèse au 10ᵉ centile
vaut 0,0** — aucun monde n'a de plancher d'exposition positif, exactement comme le parent
l'annonçait.

**4. Combien de naissances `Y` réelles en Phase B ?** **56**, dans **34 mondes sur 88** — contre
**zéro descendant** dans les 28 archives héritées, sur 308 000 pas. C'est la lacune centrale du
parent, comblée. Également : 40 morts `Y`, 80 437 sauts `Y`, `nY` maximal 3.

**5. Co-localisation et séparation ont-elles été observées ?** **Les deux.** **17 331** pas d'état
à deux `Y` co-localisés dans un seul centre et **92 649** pas d'état à deux centres **séparés**,
dans **34 mondes**, distance maximale entre centres 25,46 (le diamètre du tore). 14 mondes ont
atteint la frontière gelée du troisième centre prématuré. Le **délai médian mesuré** entre la
première naissance et l'apparition de deux centres vaut **111 pas**, contre `TAU_SEP = 125` gelé
analytiquement — une vérification indépendante à 11 % d'une constante qui n'avait jamais été que
dérivée.

**6. L'exposition locale du descendant a-t-elle été enregistrée ?** **Oui**, et vérifiée sur les
archives brutes : **112 223 lignes** portant une cellule `Y` occupée autre que la première, chacune
avec le `(nX, nSY, free, cand_Y, Q)` **de cette cellule-là**, à la phase alignée sur l'événement ;
44,7 % de ces lignes ont `Q > 0`, maximum 24–28. Les 34 événements de séparation ont été recalculés
indépendamment par liaison simple à `CORE_R = 5,0` : **34 sur 34 concordent exactement**.

**7. Quelle est l'ampleur de la rétroaction de `Y` ?** **Grande — et l'analyse groupée initiale la
masquait.** Conditionnellement à ce qu'une naissance ait eu lieu : `N_X` **+61,0 %** (`z = +5,65`)
en B1 et **+51,9 %** (`z = +5,88`) en B2, avec `nSY` **−0,98 %** (`z = −5,92`) et **−0,82 %**
(`z = −6,00`). Groupée avec les mondes sans naissance, cela devenait +11,9 % / +15,2 % à
`z ≈ 1,3–1,8`, « non significatif » — un **paradoxe de Simpson**. Le mécanisme est architectural :
`kX = 1,0`, donc `p_X = 1` dès que `nX·nY ≥ 1` ; un second `Y` sur une autre cellule **ajoute** une
source `X` saturée au lieu de concurrencer la première. `free` est numériquement dégénéré ; son
`z` est publié mais **récusé** comme preuve.

**8. La validation en aveugle passe-t-elle ?** **Partiellement.** B1 passe les trois tests
prédéclarés (première naissance `z = +0,88` ; fraction de pas à deux `Y` `z = +1,16` ; survie du
fondateur `z = −1,43`). B2 passe les tests 1 et 3 mais **échoue le test 2** (`z = −2,82` : 19,66 %
des pas en découverte contre 4,53 % en validation). **Rien n'a été ré-ajusté après ouverture de la
validation** — c'est ce que le gel interdit — et c'est cet échec qui nomme l'objet manquant.

**9. La région candidate `(kY, muY)` est-elle non vide ?** **Non — et pour une raison bien plus
forte que « la mesure n'a pas suffi ».** En éliminant `kY` et l'exposition entre les critères
gelés :

```
C1 & C3  =>  muY >= 1 - (GAMMA_SEP/MIN_EVENTS)^(1/tau) = 6,225e-3
C2       =>  muY <= 1 - (1-ALPHA_SURVIVAL)^(1/T_HORIZON) = 6,301e-5
```

**`kY` et l'exposition disparaissent.** Les deux bornes sont incompatibles d'un facteur **98,8**,
pour **tout** `kY` et **toute** exposition — la marge maximin reste à −0,151 décade sur quatre
ordres de grandeur d'exposition. Le fondateur doit survivre 11 000 pas (`muY` minuscule) pendant
qu'un nouveau-né doit mourir en ~111 pas (`muY` grand) : **le même paramètre, deux usages
opposés**. Le gel avait préenregistré que la région serait vide, mais **son explication était
fausse** : ce n'est pas un déficit que la mesure aurait pu combler, c'est de l'algèbre sur les
critères. Ce n'est **pas** `EXISTING_ARCHITECTURE_FEEDBACK_PRECLUDES_CONTROLLED_WINDOW` — ce n'est
pas un résultat de rétroaction du tout.

**10. Prochaine éligibilité unique :** `TWO-Y-OPERATOR-INSTRUMENTATION-REPAIR-01` — une réparation
**étroitement délimitée**, nommant trois objets précis (conditionnement du sous-opérateur à deux
`Y` ; substituts observables pour l'âge de lignée, puisqu'un parent est irrécupérable dans une
cellule multiplement occupée ; canal de production `X` conditionné sur la configuration `Y`), et
une **précondition bloquante** : découpler les deux rôles de `muY`, ou déclarer la fenêtre gelée
inatteignable par construction. **Pas une troisième calibration générique.**

## Relecture adversariale et réparation

Une relecture indépendante unique : **0 défaut porteur**, 20 substantiels, 4 cosmétiques, **2
attaques sur 12** mises en échec. Verdict `EVIDENCE_OR_PROVENANCE_INCOMPLETE` — la chaîne de
disposition survit à toutes les attaques dans les deux directions, mais la provenance est
incomplète. L'unique round de réparation autorisé a été appliqué ; l'opérateur a re-dérivé
lui-même chaque constat accepté.

**Deux corrections changent le sens du résultat :** l'algèbre de la région (question 9) et la
rétroaction stratifiée (question 7). La seconde fait basculer
`FEEDBACK_CONTROLLED_OR_EXPLICITLY_MODELLED` de `True` à `False`. La disposition terminale, elle,
est **inchangée**.

**Trois faiblesses de provenance sont déclarées, non lissées :**

1. `PQEC01_METHODS_HASH` a été calculé sur le code présent **au moment du gel** : il couvre la
   conception, **pas** l'exécuteur ni l'analyseur, écrits ensuite. Un hachage post-hoc de
   l'exécuteur est enregistré, en précisant qu'il ne prouve **rien** sur l'antériorité.
2. Un cycle d'analyse complet, incluant les sorties de validation, s'est terminé **avant** que deux
   défauts d'analyse ne soient corrigés. L'un des correctifs a fait passer le test 2 de B1 de
   `z = −14,32` (ÉCHEC) à `z = +1,16` (SUCCÈS). C'est la forme d'un sauvetage post-hoc, et le fait
   que le correctif restaure une règle que le gel énonce mot pour mot est une **défense, pas une
   preuve**. La porte et la disposition sont identiques avant et après, et **les deux jeux de
   chiffres sont publiés**.
3. `PQEC01_FINAL_DISPOSITION.json` a été annoté à la main avec des blocs que le code scellé
   n'écrivait pas ; ils sont désormais produits par `pqec01_repair.py`.

**Déclaré également :** le gel visait 0,81 % d'erreur-type relative en Phase A, calculée sur la
dispersion à 14 bras du parent. La dispersion réelle au niveau du monde est **4,76× plus grande**,
d'où 4,27 % atteints. `N_A` n'a **pas** été augmenté — ce serait un redimensionnement piloté par le
résultat. La cause est descriptive et n'entre dans aucune porte : **2 mondes frais sur 40** ont vu
leur nuage `X` s'effondrer (`N_X` moyen < 5), un mode d'échec que les bras développementaux
n'avaient pas échantillonné, et `Q = nX·min(nSY, free)` y vaut identiquement zéro.

```
H3_STATUS = NOT_TESTED   REPRODUCTION_STATUS = NOT_TESTED   HEREDITY_STATUS = NOT_TESTED
AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED   X_LAWSPEC_BASELINE = UNCHANGED
ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED
SCIENTIFIC_RUNS_USED = 128   TOMMY_ACTION_REQUIRED = NONE
```
