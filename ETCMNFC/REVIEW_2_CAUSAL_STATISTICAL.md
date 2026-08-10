# Revue indépendante 2 — causale / statistique (adversariale)

Commanditée par ETCMNFC comme livrable obligatoire. Le relecteur a vérifié ses affirmations
contre le moteur réel, pas seulement contre le document de conception. Reproduite fidèlement.

## (A) Faiblesses de conception, par gravité

**1. Aucune porte d'existence du support avant le gel de l'appareil.** Le point de mesure est une
somme sur des liens dont l'extrémité matérielle est dans la composante `k`. Cet ensemble d'indices
est **vide** (0 lien sur 172, quatre graines de développement). Une somme vide vaut 0 dans les deux
bras, donc `R ≡ 0`, `D ≡ 0`, `S ≡ 0`, `θ ≡ 0`, et le test de randomisation renvoie **`p = 1,0` par
construction**. Exécuté tel quel, le programme aurait produit un « résultat nul » garanti, de pure
vacuité définitionnelle. Une vérification de cardinalité du support est une précondition d'une
ligne et devait précéder l'algorithme d'appariement, le protocole de scellement et la règle IU —
pas arriver à la porte F10 après tout cela.

**2. Le test de randomisation est inerte : il mesure la cohérence de signe, pas la significativité.**
Les deux rechargements étant bit-identiques, `R` change de signe avec `A_b`, donc `D` est
*invariant* à `A_b` : la randomisation réelle induit une masse ponctuelle, pas une distribution.
L'énumération des 2¹⁰ « à `R` fixé » est la construction de Fisher standard et reste *valide*, mais
sous l'hypothèse nulle nette `R = 0` exactement, donc toute valeur de référence vaut 0 et
**`p = 1,0`. La taille réelle du test est exactement 0, pas 0,05.** En pratique `p` prend deux
valeurs : 1 (aucune différence bit-exacte) ou ≤ 0,0215 (effet présent, ≥ 9/10 blocs concordants).
Caractéristiques mesurées : 10/10 → `p = 0,00195` ; 9/10 → 0,0215 (passe) ; 8/10 → 0,109 (échoue).
C'est un test des signes déguisé, `n = 10`.
Pire, **`p` est totalement aveugle à l'amplitude** : des effets par bloc s'étalant sur un facteur
30 donnent le même `p = 0,00195` que des effets s'étalant sur 1,06. Le `p` n'ajoute rien que la
bit-exactitude ne donne déjà plus fortement : un seul bloc avec une différence binaire non nulle
falsifie l'hypothèse nulle nette. Le seul aléa réel de l'entreprise est le choix des 10 graines
fondatrices, et le test ne s'y réfère jamais.

**3. `D` est antisymétrique par construction et jette une partie réelle de l'effet.** Comme `O8`
impose `s0[A] = −s0[B]`, `D = 0,5·s0_A·(R_A − R_B)` : un contraste A-moins-B intra-bloc. Tout mode
commun s'annule exactement. Or ce mode commun **n'est pas nul** : la permutation change `Σκ(z)`
(+0,094 pour 61000, −0,025 pour 61001 — pas même de signe constant), parce que les 21 paires ont
des `ρ` inégaux, donc l'échange d'octets extensifs produit des `z` intensifs nouveaux. La
conception ne peut jamais autoriser qu'une affirmation *différentielle*, jamais « l'échange a
changé le transfert de A ».

**4. `θ = S/10` est une moyenne de population finie sans population définie, et l'intervalle est un
intervalle de décalage constant.** L'inversion d'un test de signes suppose l'additivité unitaire.
Sous l'hétérogénéité réelle du modèle, l'intervalle se comporte presque exactement comme un
intervalle de Student : dans un cas d'étalement ×30 il renvoie [0,70 ; 2,23] alors que 6 des 10
blocs ont leur vraie valeur en dehors. L'appeler intervalle de confiance pour `θ`, ou « l'étendue
des effets », n'est pas défendable. Combiné à la règle `eta_X`, c'est activement dangereux :
l'intervalle peut être « entièrement au-delà de `eta_X` » alors qu'une majorité de blocs ont un
effet *inférieur* à `eta_X`.

**5. La règle co-primaire IU n'est pas une confirmation indépendante.** `c` et `N` sont multipliés
par le **même** tableau `kap`. Différences de flux mesurées au niveau des faces : `r ≈ −0,85`,
concordance de signe ≈ 6 %. Les deux points de mesure sont fortement **anti-corrélés** (`c` est
produit par la matière, `N` consommé, gradients opposés). La règle IU est correctement énoncée
comme test intersection-union sans correction de multiplicité nécessaire, et son taux d'erreur de
type I est ≤ α (ici 0), mais elle fonctionne comme un contrôle de multiplicité quasi vide, et le
résultat attendu est « les deux significatifs, de signes opposés » — ce que la formule « change le
transfert de `c` et de `N` » masquerait.

**6. `eta_X` est mal nommé.** F4/F5/F6 prouvent que la sonde est bit-exacte et n'introduit aucune
erreur. Il n'y a donc **pas d'erreur d'observateur à borner**. `eta_X` est un seuil de
*matérialité*. C'est légitime, mais il faut le nommer honnêtement, car c'est lui — et non le `p` —
qui fait tout le travail scientifique.

**7. La porte OFF est proche d'une tautologie.** `if self.par.gain == 0.0: return lap(X)`, et
`κ(z,0) = 1` identiquement. `Mf[0]` *ne peut pas* influencer les champs publics à `g = 0`. La
valeur réelle de la porte est étroite mais authentique : elle exclut une fuite d'implémentation
(aliasing, mutation en place). C'est un contrôle de correction logicielle, pas un contrôle
scientifique, et il ne porte aucun contenu inférentiel sur les bras ON.

**8. Le traitement est adaptatif à l'état.** `eligible_edges` lit `ρ` et `Mf[0]` pour construire le
booléen, donc le manifeste et la dose varient par bloc. Ce n'est pas circulaire, mais « la même
intervention à travers les blocs » est inexact.

**Sur `s0` : aucune circularité.** `s0` est calculé depuis la ligne de base `t0` et le manifeste
avant toute avance de branche ; il ne peut pas être contaminé par le résultat. Une réserve : la
condition `s0[A] = −s0[B]`, tous deux non nuls, est *automatiquement* satisfaite par la réciprocité
exacte `O8` — elle ne peut donc jamais exclure un bloc. Ce n'est pas le garde-fou qu'elle paraît.

## (B) Verdict sur l'arrêt

**`NOT_IDENTIFIABLE` est correct, et plus largement correct que ce que F10 établissait.** Le
programme n'est **pas** trop prudent. Les deux sauvetages candidats ont été testés :

**Un point de mesure « transfert total matière–bain » ne sauve rien.** À la fenêtre gelée d'un pas,
le relecteur a comparé `ON_SWAP` et `ON_SHAM` au gain natif, face par face, sur les 172 liens :
**0 des 344 faces de frontière ne diffère, pour les deux espèces, sur les deux graines.** La
perturbation atteint 2 cellules depuis les sites échangés et s'arrête **8 cellules avant** le
premier lien de frontière. L'estimand total est non vide mais son *contraste* est bit-exactement
nul : encore `p = 1,0`, pour une raison de localité de stencil. Un nul garanti qui ressemblerait à
un vrai résultat négatif. **Le refuser est correct.**

**Allonger la fenêtre ne sauve rien non plus — cela rend l'attribution structurellement
impossible.** L'écrivain contient une réduction de champ moyen **globale** :

```python
up_ref = float(uptake[alive].mean())
```

À `t = 1`, `uptake` est identique entre bras et seules 74 des 1663 cellules vivantes (4,5 %) ont un
`z` perturbé : purement local. À `t = 2`, `uptake` diffère en 162 cellules, `up_ref` diffère, et
**100 % des cellules vivantes** ont un `z` différent. Les 344 faces de frontière diffèrent dès
`t = 2`. L'influence des deux composantes transite par **le même scalaire global** : aucun lien de
frontière ne peut plus jamais être attribué à A ou à B. Il n'existe **aucune fenêtre** où le point
de mesure par composante soit identifiable dans cette configuration — support vide à `W = 1`,
confusion globale totale à `W ≥ 2`. (De plus `ρ` diverge dès `t = 2`, rendant l'ensemble de liens
défini par `alive` dépendant du traitement aux horizons longs : risque latent de sélection
post-traitement.)

**Une sur-correction à éviter :** arrêter l'affirmation causale est obligatoire, mais l'obstruction
est elle-même un résultat structurel réel et vérifié sur l'observabilité du modèle. Elle doit être
rapportée comme *le* résultat, pas étouffée. La classification précise est plus forte que
`NOT_IDENTIFIABLE` : *le point de mesure a un support vide à la fenêtre gelée, et aucune fenêtre
alternative ne restaure l'attribuabilité dans cette configuration.*

## (C) Formulations à proscrire

Affirmation maximale défendable : *le point de mesure par composante préenregistré a un support
vide dans cette configuration ; le programme s'est arrêté avant d'allouer le moindre identifiant
primaire ; aucune affirmation n'est faite sur l'effet de la redistribution sur le transport ;
l'opérateur a passé 60/60 portes de qualification hors ligne.*

Sont exclus :

- **« aucun effet », « aucun changement détectable »** — rien n'a été mesuré.
- **« aucune conséquence publique »** — vrai seulement à `g = 0`, où c'est une tautologie. Au gain
  natif ON, la projection publique **diffère bel et bien** en un cycle (vérifié directement). Le
  qualificatif « à gain natif nul » ne doit jamais tomber.
- **« transplantation de `z` »** — faux : `z` n'est pas conservé par l'opérateur ; les 21 paires ont
  des `ρ` inégaux, donc les `z` d'après échange n'existaient nulle part avant.
- **« échange de parcelles matérielles »** — faux : `ρ` est intouché, rien de matériel ne bouge.
- **« globalement conservateur »** — vrai seulement pour le multi-ensemble et la somme exacte de
  `Mf[0]` ; faux pour `z` et pour `Σκ(z)`, mesuré comme changeant. À qualifier ou à retirer.
- **la porte OFF présentée comme un résultat de flux** — c'est un contrôle de fuite
  d'implémentation sur une tautologie.
- **`p = 2/1024` décrit comme « hautement significatif »** — c'est un décompte de concordance de
  signe, avec un test de taille réelle 0.
- **« 60/60 portes passées » placé près de la discussion du point de mesure** — l'opérateur a
  qualifié ; l'*expérience*, non.
- **tout vocabulaire de fonction, d'appartenance, d'individualité ou de vie** — A et B sont 42
  cellules définies par un seuil (2,5 %), à 13 cellules de profondeur dans **une seule** région
  matérielle connexe de 1662 cellules, séparées de 28 cellules, délimitées par un seuil de
  détecteur 3000× supérieur au prédicat matériel du noyau. Ce sont des taches denses, pas des
  entités.
- **« redistribution entre A et B »** — acceptable seulement comme comptabilité. Description
  exacte : *une permutation involutive préenregistrée de 21 paires de valeurs `float64` d'un
  tableau interne entre deux ensembles de sites définis par seuil, préservant le multi-ensemble
  global et la somme exacte de ce tableau.*

## (D) Options futures, par défendabilité

1. **Recibler le point de mesure sur l'interface propre de la composante** (contour `ρ > 0,30`) au
   lieu de la frontière matière–bain. **Aucune modification du modèle.** Vérifié faisable : le
   support perturbé à `t = 1` est non vide (98 faces), `up_ref` est encore identique à `t = 1` donc
   pas de confusion globale, A et B sont à 28 cellules, et **aucune face perturbée n'est à distance
   ≤ 2 des deux composantes** : attribution propre. Coût : cela répond à « échange à travers
   l'interface propre de la composante », pas « échange avec l'environnement ». Ce recadrage doit
   être énoncé explicitement et tout vocabulaire « matière–bain » abandonné. À préenregistrer.
2. **Reconfigurer la géométrie** pour que les composantes touchent le bain. Seule option qui
   préserve la question scientifique d'origine. Coûteuse : tout doit être regelé et requalifié.
   Danger critique : le choix de géométrie doit suivre une règle *structurelle* préenregistrée,
   jamais un effet observé, sinon c'est du magasinage de configuration.
3. **Remplacer `up_ref` par une référence locale**, comme variante de modèle déclarée. Supprime la
   confusion de champ moyen et rend les fenêtres longues attribuables, mais modifie l'écrivain
   « inchangé depuis sc_mcm gelé » et casse l'emboîtement avec le LawSpec parent. Défendable
   seulement étiqueté comme modèle distinct, jamais comme correctif.
4. **Fenêtre longue avec point de mesure total non attribué.** Non dégénéré dès `t = 2`, mais
   globalement confondu par `up_ref`, aucune affirmation par composante possible.
5. **Aligner le seuil du détecteur sur celui du noyau** — auto-destructeur : la région vivante est
   un blob unique contenant A et B, qui cessent d'être distinguables.

**Orthogonal :** remplacer le cadrage « randomisation » par ce que la conception soutient
réellement — publier les différences bit-exactes par bloc, la concordance de signe comme un
décompte `k` sur 10, l'*étendue* des effets par bloc plutôt qu'un intervalle de décalage inversé,
et renommer `eta_X` seuil de matérialité. Conserver le bit d'allocation scellé comme dispositif
d'**aveuglement** contre le biais d'analyste — sa fonction authentique — et cesser de le décrire
comme une randomisation.
