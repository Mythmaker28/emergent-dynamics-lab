# TBRT02 — notes d'analyse en cours (pré-C4). ÉCRIT AVANT TOUTE CONCLUSION.

Ce fichier est un journal de travail. Il n'est pas C4. Il enregistre ce qui a été LU dans le
code gelé et ce qui a été ÉTABLI, dans l'ordre, pour qu'aucune étape ne soit reconstruite de
mémoire plus tard.

## 1. Ce que le gel dit, verbatim

TBRT02_MASTER_FREEZE.json, THE_REFUTATION_CONDITION_FROZEN_BEFORE_ANY_WORLD :

> "if the CERTAIN set of the daughter's lineage ever absorbs a descendant of the displaced
> mass, Model C is REFUTED. One absorption suffices. No threshold, no magnitude judgement,
> checkable by enumeration."

## 2. Ce que le modèle C fait, lu dans CLEA01/code/clea01_lineage_i1.py

Propagation avant depuis une racine, à partir des lignes de cellules Y-occupées de l'archive :

- `sources(d, occ_prev)` = les cellules Y-occupées au pas t dans le voisinage de Moore-1
  torique de d (9 décalages, self inclus).
- `d in CERTAIN(t+1)` ssi `S(d,t)` est non vide ET `S(d,t) ⊆ CERTAIN(t)`  — règle TOUS-les-parents.
- `d in POSSIBLE(t+1)` ssi `S(d,t) ∩ POSSIBLE(t) ≠ ∅`                     — règle UN-parent.
- Une cellule sans source (naissance spontanée non adjacente) est comptée en
  `invariant_violations` et n'entre ni dans CERTAIN ni dans POSSIBLE.

## 3. Ce que l'archive contient (schéma TLMR01-ARCHIVE-1, lu dans le npz)

`c_t,c_y,c_x,c_nY,...` une ligne par cellule Y-occupée par pas ; `ybirth/ydeath/xbirth` ;
`meta.intervention` porte `parent_cells`, `daughter_cells`, **`competitor_cell`**,
**`competitor_mass`**, `rng_hash_before/after`. La masse déplacée est donc étiquetée par
construction, à une cellule connue, au pas t_m.
`removal_semantics` : les lignes du pas t_m sont enregistrées AVANT l'intervention ; l'état
post-intervention apparaît pour la première fois à t_m+1.

## 4. Ce que le moteur fait des sauts Y (PQEC01/code/pqec01_observer.py::_diffuse)

Quatre sous-décalages von Neumann par pas, chacun ±1 le long d'un axe, avec acceptation
bornée par la capacité libre de la destination. Le déplacement net d'un quantum sur un pas
est donc au plus 1 en y ET 1 en x, c'est-à-dire **au plus 1 en distance de Chebyshev** :
il ne peut pas sortir du voisinage de Moore-1 que `sources()` inspecte.

## 5. CE QUI N'EST **PAS** GELÉ — à déclarer sans détour

La condition de réfutation est gelée EN MOTS. Elle n'a **jamais été opérationnalisée en code**
avant la campagne : les trois fixtures de TBRT02_FIXTURES.json certifient la mécanique de
l'intervention (conservation de la masse, aucun aléa consommé, séparation ≥ 2, déterminisme,
refus si la capacité manque) et **rien** sur l'énumération de l'absorption. Aucun fichier de
TBRT02/code ne contient les mots absorb / refute / descendant appliqués à une procédure.

Conséquence méthodologique : le passage des mots à l'énumération se fait MAINTENANT, après le
brut. C'est un degré de liberté réel. Il est neutralisé de la seule façon honnête disponible :
**calculer toutes les lectures défendables et les rapporter toutes**, plutôt que d'en choisir
une une fois les chiffres connus.

## 6. Lectures candidates, écrites AVANT d'avoir calculé quoi que ce soit

- **R1 — intersection stricte.** ∃t : CERTAIN_fille(t) ∩ DESC_compétiteur(t) ≠ ∅, où
  DESC = fermeture UN-parent depuis `competitor_cell` à t_m.
- **R2 — contamination permissive.** ∃t : POSSIBLE_fille(t) ∩ DESC_compétiteur(t) ≠ ∅.
- **R3 — niveau masse.** un quantum Y descendant de la masse déplacée occupe une cellule de
  CERTAIN_fille. À vérifier : l'archive ne contient PAS de registre de sauts (`pq_yhop` n'y
  est pas), donc R3 pourrait être non calculable depuis les archives. À établir, pas à supposer.

## 7. Un résultat structurel obtenu par preuve, à confirmer empiriquement sur les 41

Sous R1 l'intersection est vide **par construction**, indépendamment des données :

- Base : à t_m, CERTAIN = cellules-filles occupées, DESC = {competitor_cell}. Le déplacement
  impose Chebyshev ≥ 2 (`MIN_SEPARATION_FROM_THE_DAUGHTER = 2`), donc disjoints.
- Récurrence : soit CERTAIN(t) ∩ DESC(t) = ∅. Si d ∈ CERTAIN(t+1) ∩ DESC(t+1), alors
  S(d,t) ⊆ CERTAIN(t) et S(d,t) ∩ DESC(t) ≠ ∅, donc il existe c ∈ CERTAIN(t) ∩ DESC(t) — vide.
  Contradiction.

Si cela se confirme, R1 ne peut **jamais** se déclencher : ce n'est pas un test empirique mais
un contrôle de cohérence de l'implémentation avec sa propre définition. La « falsifiabilité »
revendiquée dans tbrt02_displace.py (« Model C becomes falsifiable instead of merely
self-consistent ») ne serait alors pas acquise par R1. Le contenu empirique se déplacerait vers
R2 et vers la durée de survie de CERTAIN.

**Rien de tout cela n'est conclu ici.** Les trois lectures sont à calculer sur les 41 triplets
et les trois bras, et le résultat sera écrit dans C4, puis soumis à UN checker adverse dont le
retour sera écrit verbatim AVANT d'agir dessus.

## 8. Statuts inchangés

H3_STATUS = NOT_TESTED ; REPRODUCTION_STATUS = NOT_TESTED ; HEREDITY_STATUS = NOT_TESTED ;
AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED ; X_LAWSPEC_BASELINE = UNCHANGED ;
ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED ;
COMPANION_PAPER_V1_1_STATUS = UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED ;
OMLDCT02_STATUS = INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS__UNCHANGED ;
CLEA01_STATUS = CLOSED__LINEAGE_ROUTE_PAUSED__NOT_REOPENED.

---

## 9. Un second défaut de MON énumération, trouvé et corrigé avant usage (04:47 UTC)

Premier passage sur les 41 : trois triplets — **85, 240, 347** — donnaient
`DESC_seed_cell_present_in_that_row = False` et `DESC_duration = 0`. Vérification cellule par
cellule dans les archives :

| idx | t_m | cellule compétitrice | masse | présente à t_m+1 | voisin de Moore-1 occupé à t_m+1 | ligne ydeath à t_m+1 |
|-----|-----|----------------------|-------|------------------|----------------------------------|----------------------|
| 85  | 685 | (31, 35)             | 1     | non              | (30, 35) : 1                     | aucune               |
| 240 | 445 | (28, 5)              | 1     | non              | (28, 4) : 1                      | aucune               |
| 347 | 1108| (5, 10)              | 1     | non              | (5, 11) : 1                      | aucune               |

Aucune mort enregistrée et un voisin immédiat occupé : **le quantum déplacé a SAUTÉ au premier
pas**. Mon amorçage `DESC(t_m+1) = {cellule compétitrice} ∩ occ(t_m+1)` le perdait alors qu'il
existait toujours. Ce n'est pas un fait sur le monde, c'est un défaut de mon instrument.

**Cause racine, plus générale.** La ligne enregistrée à t_m est l'état AVANT l'intervention.
Amorcer une lignée sur cette ligne est faux pour tout ce que l'intervention change :
- la masse déplacée n'y figure pas (elle apparaît à t_m+1) ;
- le Y du parent y figure ENCORE, alors qu'il a été retiré — donc, dans les bras SELECTIVE et
  DISPLACED, la cellule parente compte comme « source » à la transition t_m → t_m+1 et
  disqualifie de CERTAIN toute cellule fille qui la touche.

Le second point affecte le modèle C GELÉ lui-même, tel qu'il est écrit dans
`clea01_lineage_i1.py` : ce n'est pas une erreur de CLEA01 (où la ligne enregistrée était le bon
état de départ), c'en est une de son application ici.

**Correction, à calculer dans les deux variantes plutôt qu'à trancher après coup :**
- **Variante A** — `prev(t_m)` = la ligne enregistrée, telle quelle. C'est ce que fait le code
  gelé, littéralement.
- **Variante B** — `prev(t_m)` = la ligne enregistrée reconstruite à l'état POST-intervention :
  Y du parent retiré de `parent_cells`, et pour DISPLACED `competitor_mass` placée à
  `competitor_cell`. La reconstruction est entièrement déterminée par `meta.intervention`
  (`parent_cells`, `competitor_cell`, `competitor_mass`), sans aucun paramètre libre, et sa
  validité est contrôlable : la masse Y totale doit être conservée pour DISPLACED et diminuée
  d'exactement le Y parental pour SELECTIVE.

Les deux variantes seront rapportées côte à côte dans C4. Aucune ne sera choisie sur son
résultat.

## 10. Premier passage (variante A, amorçage compétiteur défectueux) — enregistré pour mémoire, NON conclusif

R1 : 0 déclenchement sur 41. R2 : 17 sur 41, premier contact médian 1 252 pas après t_m.
Durée de CERTAIN, médiane par bras : SHAM 1 791, SELECTIVE 10 093, DISPLACED 2 896.
Dans SELECTIVE, POSSIBLE = CERTAIN exactement sur les 41 triplets — c'est le mode d'échec sur
lequel CLEA01 s'était fermé, reproduit ici.
Ces chiffres sont conservés comme trace, pas comme résultat : le passage corrigé les remplace.
