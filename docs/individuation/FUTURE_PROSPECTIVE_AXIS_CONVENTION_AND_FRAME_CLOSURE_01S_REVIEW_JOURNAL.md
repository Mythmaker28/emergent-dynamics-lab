# FUTURE-PROSPECTIVE-AXIS-CONVENTION-AND-FRAME-CLOSURE-01S — journal de review

Registre complet, conformément à la Partie I §13. Le JSON fait autorité pour les gates, les hashes et la
route ; ce journal porte les findings et les adjudications ; le rapport porte le raisonnement.

## 1. Packages et digests

| Checkpoint | Commit | `REPORT.md` sha256 | Octets |
|---|---|---|---|
| 1 — Partie I gelée | `b560909b9e88e8eb00a6d542ed731239e329573d` | `096cd174213e9dec4a7518ac8e46426e3a59435aabf200712eee383f3770e5c6` | 23 901 |
| 2 — mécanique + conception (round 1) | non committé séparément | `79e9a85fb13c79732421106f4a2d142cfe716a6c8e2a19141cb8d6628ac1da6c` | 54 712 |
| 3 — correction consolidée (re-review) | non committé séparément | `d44609cc9365857ca41f3e21c30b5e05f32df35d28f1279f40004bc11096db36` | 86 031 |
| 4 — scellé | *ce commit* | enregistré dans `DECISION.json` | 91 874 |

Les verdicts du round 1 ont été rendus contre le package de 54 712 octets et contre aucun autre ; ceux
de la re-review ciblée contre celui de 86 031 octets et contre aucun autre. La Partie I est un préfixe
byte-exact de 23 901 octets à chaque état, vérifié par les deux reviewers.

## 2. Procédure

Deux reviewers indépendants **en parallèle** après le checkpoint 2 ; **une seule** correction consolidée
(Partie III) ; **une seule** re-review ciblée finale (Partie IV). Pas de troisième boucle. Le vote ne
contrôle pas la disposition : la matrice gelée de la Partie I §5 et la priorité §11 décident.

- **Reviewer A** — symétrie ; `Q` versus forme ; estimands ; distribution prospective ; statistiques ;
  puissance ; pseudo-réplication.
- **Reviewer B** — implémentation ; détecteur/tracker ; intervention ; lifecycle ; provenance ; replay ;
  contournements ; firewall.

## 3. Round 1 — FAIL / FAIL

| Reviewer | Verdict | Findings |
|---|---|---|
| A | **FAIL** | A1–A14 : 1 `PACKAGE_BLOCKER`, 6 `ROUTE_G_GATE_FAIL`, 3 `ROUTE_E_GATE_FAIL`, 5 `MINOR_NON_BLOCKING` |
| B | **FAIL** | B1–B14 : 1 `PACKAGE_BLOCKER`, 4 `ROUTE_G_GATE_FAIL`, 1 `ROUTE_E_GATE_FAIL`, 8 `MINOR_NON_BLOCKING` |

**28 findings. Aucun jugé invalide.**

### 3.1 Findings porteurs et adjudication

| ID | Catégorie | Finding | Adjudication |
|---|---|---|---|
| **A1** | `PACKAGE_BLOCKER` | `sign(Q)` n'est pas stable à l'horizon de design : croisements aux pas 509, 774, 820 ; imparité inter-branches en échec à 247/1025 échantillons | **ACCEPTÉ** → R1, épinglé par `fact19`. Reproduit aux valeurs exactes |
| **B1** | `ROUTE_G_GATE_FAIL` | le tracker n'est pas équivariant sous transposition quand un composant enroule le tore ; contre-exemple 8×8 explicite ; 179/3 840 séquences asymétriques | **ACCEPTÉ** → R4, épinglé par `fact20` ; **contenu** par `fact21` (1 280 séquences sans enroulement, 0 asymétrie) |
| **A5** | `ROUTE_G_GATE_FAIL` + `ROUTE_E_GATE_FAIL` (C1) | aucune loi de probabilité sur les conditions initiales ; `dt`, `m_max`, `n_max` jamais déclarés | **ACCEPTÉ** → réparé par `fact22`/`fact23` : équivalence exacte (B1)∧(B2) ⇔ admissibilité (2 500 points, 0 discordance) et loi de CI produit d'uniformes (1 680 validations, 0 rejet) |
| **B2, B3** | `ROUTE_G_GATE_FAIL` (C3) | le pont n'exprime ni intervention fenêtrée ou dépendante de l'état, ni égalisation du champ de ressource | **ACCEPTÉ** → R5 ; capacité manquante **non bornée**, donc pas un `PRE_RUN_BLOCKER` ; C3 FAIL pour G |
| **B4** | `PACKAGE_BLOCKER` | PRB-5 incomplet : trois points d'entrée publics supplémentaires délivrent un accès d'analyse sans pont ni receipt | **ACCEPTÉ** → R6 ; PRB-5 complété |
| **A2** | `ROUTE_G_GATE_FAIL` (C4) | l'indépendance de `Q` vis-à-vis de la forme n'est pas établie : la démonstration opère là où `S ≡ 0` ; le falsificateur de H2 ne peut pas se déclencher sur sa propre strate | **ACCEPTÉ** → R2 |
| **A3, A4** | `ROUTE_G_GATE_FAIL` + `ROUTE_E_GATE_FAIL` (C4) | les falsificateurs d'orientation (G) et de dépendance aux CI (E) sont vides par construction du fait de l'appariement `(x, Tx)` | **ACCEPTÉ** → R3 ; E abandonne l'appariement et tire **deux CI indépendantes par loi** |
| **A6** | `ROUTE_G_GATE_FAIL` (C9) | caractéristiques opératoires non évaluées sous attrition ; garde-fou sous la bande où l'attrition seule fabrique un `NÉGATIF` à p = 0,92 | **ACCEPTÉ** → R7 ; garde-fou de E rattaché à la coupure POSITIVE |
| **A7** | `ROUTE_G_GATE_FAIL` (C5) | pseudo-réplication : H2, H4, H5, H6 dans la séquence confirmatoire sans unité, sans dépendance, sans taille, sans puissance | **ACCEPTÉ** → R8 |
| **B5, B6** | `ROUTE_G_GATE_FAIL` (C5, C7) + `ROUTE_E_GATE_FAIL` (C5) | la stratégie composite rend `π ≡ 0` pour G ; la règle paire→outcome de E n'est pas énoncée | **ACCEPTÉ** → R8 ; mapping des six événements sur les cinq états terminaux explicité |
| **A8, A9** | `ROUTE_G_GATE_FAIL` (C7) + `ROUTE_E_GATE_FAIL` (C2) | cinq seuils déterminant l'outcome sans valeur ; `cohort_residual_fraction` hérité silencieusement | **ACCEPTÉ** → R9 ; règle d'invariance préspécifiée sur `{0,01 ; 0,05 ; 0,20}` |
| **A10** | `MINOR_NON_BLOCKING` | la justification de `ε̂_b ∈ [0,1]` par `ArithmeticError` est fausse (200 pas réussis à `ε̂_b = 5`) | **ACCEPTÉ** → R10 ; reclassée restriction de portée déclarée |
| **A11, A12, A13, A14, B7–B14** | `MINOR_NON_BLOCKING` | `H`/`Δf` non dérivés et étiquetés « témoins » ; équivariance jamais testée aux tailles ni aux lois déclarées ; `n = 259` masqué à 0,0625 ; en-tête binaire contredit ; citation d'un « §11.3 » inexistant ; plancher `L` dimensionnellement incohérent ; M10 non reproductible à ±15 % et hors acquisition ; la paire n'est pas un réplicat ; exactitude revendiquée là où le test asserte une tolérance ; « boule ouverte » de 18 points ; M11 sur un seul composant | **TOUS ACCEPTÉS** → R11, R12 ; `fact24` répare A12 aux tailles `{16,24,32}` et aux lois de `A` |

### 3.2 Findings jugés invalides

**Aucun.**

## 4. Correction consolidée — une seule passe

Douze retraits `R1`–`R12` (rapport §III.2), six faits mécaniques ajoutés (`fact19`–`fact24`), Route G
**rejetée définitivement** sur six gates, Route E corrigée et sélectionnée. Le fichier de test passe de
21 à **27 tests** (38 924 → 72 939 octets) ; la suite complète passe de 667 à **673 tests**, tous
passants. **Aucun autre fichier n'a changé.**

Deux corrections vont **contre** la position initiale de l'auteur : R1/R2 détruisent le résultat que
l'auteur présentait comme décisif pour sa route préférée, et R3 supprime un dispositif d'enrôlement que
l'auteur avait gelé en Partie I.

**Route E n'a pas été réparée sous pression de review sur les points de fond** : l'abandon de
l'appariement, la déclaration des trois échelles et la loi des CI sont des **fermetures**, pas des
ajustements — chacune est prouvée mécaniquement, aucune n'est calée sur une sortie.

## 5. Re-review ciblée — PASS / PASS

| Reviewer | Verdict | Findings restants |
|---|---|---|
| A | **PASS** | A15–A19, tous `MINOR_NON_BLOCKING` |
| B | **PASS** | B15–B19, tous `MINOR_NON_BLOCKING` |

**Aucun `PACKAGE_BLOCKER`, aucun `ROUTE_E_GATE_FAIL` ne survit.** Les dix findings restants sont
déclarés comme limitations au rapport §IV.2 et ne sont pas corrigés : la mission n'autorise pas de
troisième boucle.

Les deux reviewers ont revérifié indépendamment la préfixation byte-exacte, les six nouveaux faits, la
suite complète et toute l'arithmétique de Route E, sans écart. Les deux confirment que le rejet de
Route G est honnête et surdéterminé, et que `backup_route = null` est correct.

## 6. Totaux

| Round | A | B | Verdicts |
|---|---|---|---|
| 1 | A1–A14 (1 blocker, 6 G-fail, 3 E-fail, 5 mineurs) | B1–B14 (1 blocker, 4 G-fail, 1 E-fail, 8 mineurs) | FAIL / FAIL |
| re-review | A15–A19 (5 mineurs) | B15–B19 (5 mineurs) | **PASS / PASS** |
| **total** | **19** | **19** | — |

**38 findings. Zéro jugé invalide. Douze retraits. Dix limitations déclarées.**

## 7. Registre de gouvernance

- La Partie I n'a jamais été modifiée ; préfixe byte-exact vérifié aux checkpoints 1, 2, 3 et 4, par
  l'auteur et par les deux reviewers.
- Aucune source acceptée, aucun test existant, aucun runner, aucun `__init__.py`, aucun document
  historique n'a été modifié : **un seul fichier ajouté**, dans l'allowlist de la Partie I §14.
- Aucun gate n'a été moyenné, pondéré ou échangé. La matrice décide ; les reviewers produisent des
  findings.
- **Une déviation de la Partie I est déclarée** (A19) : le §6.6 gelé impose l'enrôlement en paires
  `(x, Tx)` ; Route E corrigée l'abandonne, le but du §6.6 — une loi de CI invariante sous `T` — restant
  préservé par l'échangeabilité des entrées i.i.d.
- La décision préliminaire de l'auteur (`ROUTE_G_SELECTED`, E en backup) a été **renversée par la
  review**. C'est enregistré comme le résultat, sans adoucissement.
