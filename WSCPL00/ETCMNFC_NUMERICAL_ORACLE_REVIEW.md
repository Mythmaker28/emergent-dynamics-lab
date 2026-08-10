# Revue indépendante 1 — numérique / oracles (adversariale)

Commanditée par ETCMNFC comme livrable obligatoire. Le relecteur a redérivé chaque affirmation
avec son propre code dans un répertoire séparé, sans réexécuter les scripts du programme.
Reproduite ici fidèlement, y compris les constats qui condamnent le programme.

## Verdicts

| revendication | verdict |
|---|---|
| **C1** opérateur = involution octet exacte, conservatrice, réciproque | **CONFIRMÉ** |
| **C2** poids égaux suffisants, `ρ` égal non requis | **CONFIRMÉ** (quasi tautologique, preuve initiale faible) |
| **C3** appariement déterministe et aveugle aux valeurs | **CONFIRMÉ tel que littéralement écrit, TROMPEUR en portée** |
| **C4** sonde ON passive et exacte | **ORACLE VIDE** — les faits tiennent, les portes ne prouvaient rien |
| **C5** fenêtre = un pas natif | **CONFIRMÉ**, oracle faible |
| **C6** exclusion structurelle à gain nul | **CONFIRMÉ, plus fort que revendiqué** |
| **C7** l'arrêt : point de mesure non identifiable | **CONFIRMÉ, plus robuste que revendiqué** |

## Détail des constats retenus

**C1.** Reproduit sur les 4 blocs avec un comparateur d'état qui énumère `vars(st)` au lieu de
faire confiance au tuple `FIELDS` : les deux coïncident exactement, `full_state_sha` n'omet
aucun champ. Involution bit-exacte sur les 9 champs ; `Mf[1]` inchangé ; `ΔQ_A = −ΔQ_B ≠ 0` en
rationnels exacts (bloc 61000 : `129712396604471847/9007199254740992`).
*Réserves :* `transpose()` n'était pas auto-protégée contre une liste de paires non disjointe ;
`O11` est impliquée par `O10` ; `O4/O5/O6/O10/O11` passeraient à vide sur un appariement vide,
seules `O2` et `O8` sont des garde-fous de non-vacuité (les deux se déclenchent, 21 paires).

**C2.** Les 21 paires diffèrent en `ρ` à chaque bloc (min |Δρ| ≈ 6,8e-2). Mais la preuve
initiale de `w ≡ 1` reposait sur une recherche de sous-chaîne (`"dx" not in srcsc`) limitée à un
seul fichier — or `dx` existe dans `scaffold/observables.py`, et un poids nommé autrement serait
passé.
*Signal d'alerte de cadrage :* `Q` **n'est pas un invariant dynamique**. Un pas natif fait passer
`Q` de `+0,184192` à `+0,152807`. « Opérateur conservateur » signifie « préserve `Q` à `t0` »,
rien de plus.

**C3.** Déterminisme reproduit sous `PYTHONHASHSEED` 0/1/12345 et sous **200 réétiquetages
aléatoires indépendants** des deux côtés : 0 divergence. Minimalité lexicographique vérifiée
contre une implémentation indépendante.
*Mais :* contre-exemple explicite — sur le bloc 61000, en modifiant **uniquement** `Mf[0]` en un
site de A (`−0,283427 → +0,371149`, domaine toujours valide, `ρ`/ids/appartenance/géométrie
intacts), les paires choisies changent (`[1935,1967],[1936,1968] → [1935,1968],[1936,1967]`) à
cardinalité identique 21. **L'appariement EST fonction de la valeur du porteur** ; seule
`frozen_matching()` isolée en est aveugle.

**C4 — le point de rupture.** Trois sous-portes ne pouvaient pas échouer :
- `F5` comparait `recon` et `direct`, la **même expression évaluée deux fois sur la même entrée**.
  Exécutée sur du bruit aléatoire sans rapport avec le moteur : **PASSE**.
- `F6` calculait `exact_sum(f) − exact_sum(roll(f,1,ax))`, identiquement nul pour **tout** tableau
  fini, `roll` étant une permutation. Exécutée sur du bruit : **PASSE**. Aucune information
  physique.
- `F2` comparait `(out.rho>eps)` à `(tapped.rho>eps)` où `tapped is out`. Ne pouvait pas échouer.

Le relecteur a exécuté les tests substantifs manquants : la divergence reconstruite est **bit
identique** à la valeur réellement retournée par `_face_transport`, et
`c + dt*(D_c*tap_out + s*rho − delta*c)` reproduit le `c` du moteur **bit pour bit**, sur les deux
graines. *Les faits tiennent — par son test, pas par le nôtre.*

**C5.** Indépendamment : 1 `step`, exactement 2 appels `_face_transport` (c, N), 3 `lap()` bruts
(internes), 1 `_face_flux` (voie matérielle distincte). Tout `np.clip` du pas agit sur `g`, `u`,
`v`, `mk` — jamais sur `c`, `N` ni sur l'incrément de transport. Vérifié aussi que
`clip(mk,−1,1)` **ne mord pas** dans la fenêtre (max |z| = 0,630 sham / 0,770 swap) : le
traitement n'est pas silencieusement tronqué.

**C6 — plus fort que revendiqué.** Le relecteur a remplacé l'échange par 6 perturbations sur les
4 blocs : appariement, `z` aléatoire, inversion de signe, saturation `z ≡ +1`, `Mf[0] ≡ 0`, et
**injection de NaN**. À gain nul, les 7 tableaux publics **plus `Mf[1]`** sont bit-identiques
après un pas dans tous les cas, tandis que `Mf[0]` diffère réellement. Qu'un NaN dans `Mf[0]`
n'atteigne aucun champ public est décisif : l'exclusion est **structurelle**, pas numérique.

**C7 — l'arrêt, plus robuste que revendiqué.** Étiquetage BFS périodique 4-connexe indépendant :
`alive = ρ > 1e-4` donne exactement **1** région connexe sur les 4 blocs, A et B portant la même
étiquette. **172** faces matière–bain, **0** avec une extrémité matérielle dans A ∪ B, **0**
cellule de composante ayant un voisin mort. Profondeur : 14 cellules en distance de réseau
4-connexe (13,0 en euclidien dans notre sonde — même fait, convention différente).
*Réserve importante :* les quatre blocs « indépendants » ont des **ensembles de cellules A et B
identiques** (mêmes 21+21 cellules, même pas 390). Le résultat topologique est **n = 1 en
géométrie**.

## Route non explorée, vérifiée et fermée

Le noyau possède quatre échanges matière↔réservoir **par cellule** : `+F(N₀−N)` et `−g` pour `N`,
`+s·ρ` et `−δ·c` pour `c`. Ils ne demandent ni nouveau prédicat ni partition inventée.
Le relecteur les a recalculés exactement : **les quatre sont bit-identiques entre les bras à
l'intérieur de la fenêtre**, car ils ne dépendent que de `ρ, U, V, c, N` en `t0`, qu'aucun échange
ne touche. De plus ils sont unilatéraux (pas de partenaire débit/crédit) et `g` est écrêté.
Enfin, la portée causale du traitement dans la fenêtre est de **82 cellules**, à distance
minimale **13** de la première cellule non vivante : le traitement **ne peut physiquement pas
atteindre la frontière** dans la fenêtre gelée.

> « Aucune route ne rend le point de mesure matière–bain par composante identifiable dans la
> fenêtre gelée sans nouveau prédicat, nouvelle partition ou fenêtre plus longue. **L'ARRÊT
> TIENT.** »

## Défauts signalés, par gravité

1. `F5` tautologique. 2. `F6` tautologique. 3. `F2` compare un objet à lui-même.
4. L'audit `O1` était une liste noire de noms, pas un audit de valeur.
5. Portée de `C3` : le manifeste dépend des valeurs.
6. `w ≡ 1` prouvé par recherche de sous-chaîne sur un seul fichier.
7. `transpose()` sans garde de disjonction. 8. `F0/F3` par recherche brute, sans retrait des
docstrings. 9. Docstring « caractère pour caractère » inexacte. 10. Les fixtures adversariales
ne touchaient jamais l'opérateur (`mk()` mort, jamais appelée). 11. Code mort.
12. `O11` impliquée par `O10`. 13. Le hash de manifeste n'était pas auto-vérifiant.
14. `n = 1` en topologie présenté comme 4 blocs. 15. `exact_sum` lève sur NaN/inf.

## Suites données par le programme

| défaut | traitement |
|---|---|
| 1, 2, 3 (oracles vides) | **portes remplacées** dans `etcmnfc_phaseC2.py`, chacune avec un **contrôle négatif** ; les anciennes sont conservées et déclarées superseded |
| 4 | remplacé par un test de type (`dtype == bool`) et un test d'invariance à matrice fixée |
| 5 | **publié** comme correction de portée `O1_SCOPE_CORRECTION`, contre-exemple inclus |
| 6 | remplacé par un test par conséquence (poids non uniformes → conservation brisée) |
| 7 | garde de disjonction ajoutée, lève une exception |
| 9 | docstring corrigée |
| 14 | déclaré dans le rapport |
| 8, 10, 11, 12, 13, 15 | consignés, non corrigés — sans effet sur une conclusion, le programme s'arrêtant ici |
