# CAUSAL_CONFIRMATION_INDEPENDENT_VIEW — LCI-CAUSAL-CONFIRMATION-01

*Nouvel agent indépendant. Ce document est produit AVANT toute donnée prospective (aucun seed 52xxx ouvert). Il critique la conclusion héritée (VERDICT_01 / audit 53fd2b6) sans la supposer correcte, s'appuie sur une reproduction exacte du pipeline committé et sur un sondage empirique DEV (seeds 50001–50005), et fige ma position avant la confirmation.*

Provenance : branche `exp/local-causal-individuation-00`, tip audité `53fd2b6`. main `f3921a4`, V4 `23b53ae`, release : **intacts, rien ouvert**. Plateforme de calcul : Python 3.11.15, numpy 2.2.6, scipy 1.15.3, matplotlib 3.10.9 (le moteur est une PDE réaction-diffusion chaotique → reproductibilité *bit-identique sur plateforme fixe*, pas inter-plateforme ; vérifiée ci-dessous).

## 0. Ce que j'ai vérifié moi-même (pas hérité)

- **Reproduction exacte** du pipeline `exp1_reaudit.py` sur les bruts committés : own-order R²=**0.654** [0.517,0.856], own-dose **0.450** [0.380,0.752], null intra-monde p=2×10⁻⁴/7×10⁻³, jackknife 0.556–0.689, voisin **−0.306**, baselines taille/position/taille+pos **−0.17/−0.17/−0.22**, DD_mem **9018** (|diag|=0.180=11.4× base, |off|=1.8×10⁻⁵), DD_comportemental(Δuptake) **1629** avec |diag| absolu **2.66×10⁻⁴**. Tous les chiffres porteurs régénèrent **à l'identique** ⇒ le ré-audit est reproductible sur ma plateforme.
- **Déterminisme** : deux exécutions indépendantes du seed 50001 → features, matrices d'influence et histoires **byte-identiques** (max|Δ|=0). Coût ≈6 s/seed.
- **Sonde empirique du confond** (seeds DEV 50001–50005, 15 gouttelettes), résultats chiffrés utilisés partout ci-dessous.

## 1. Le stockage local au repos est-il réellement établi ?

**OUI — je concours.** L'individuation de **stockage/lecture** depuis le champ mémoire est réelle et robuste : lecture de l'histoire propre ≫ voisine, ≫ baselines triviales, bat le null **intra-monde** (le bon test, qui neutralise les décalages au niveau du monde), stable au jackknife inter-mondes, matrice d'influence diagonale en **valeur absolue** (pas seulement en ratio : |diag|≈0.18≈11× la mémoire de base). C1 et C4 passent. Ce point de l'audit hérité n'est **pas** sur-vendu ; je le certifie de nouveau.

## 2. Définition opérationnelle minimale de « causalement individualisé »

Une gouttelette est **causalement, comportementalement** individualisée si, **corps et environnement tenus communs entre branches contrefactuelles**, les huit conditions tiennent **simultanément** :
(i) sa réponse comportementale propre est prédite par son **histoire propre** ; (ii) **pas** par l'histoire d'une voisine ; (iii) **effacer sa mémoire** détruit l'effet ; (iv) effacer une **voisine** ne le détruit pas ; (v) **désactiver le canal de lecture** (λ→0) le détruit ; (vi) le **sham** ne le détruit pas ; (vii) taille, masse, position et **environnement résiduel** ne l'expliquent pas ; (viii) l'effet **absolu** dépasse le bruit et **se reproduit entre mondes**.
Point central : l'état stocké doit **changer un comportement ultérieur via le canal de lecture**, au-delà de tout résidu environnemental — démontré par **intervention (do-effacement)**, pas par décodage seul. Le décodage d'une histoire depuis un état n'est pas de la causalité ; c'est de la corrélation stockée.

## 3. L'uptake est-il un bon comportement, ou seulement la variable couplée par construction ?

**Couplée par construction, et de plus confondue.** L'uptake obéit à `g ∝ N·ρ·(1+β·σ)·(1+λ₊·m₊)` : à N fixé, l'uptake instantané est une fonction **monotone** de m₊ — le lire, c'est lire la mémoire à une transformation algébrique près. Pire, empiriquement l'uptake **en place** est dominé par le **résidu de nutriment**, pas par la mémoire :

| quantité (readout, settle=120) | valeur |
|---|---|
| résidu ΔN (région) vs contrefactuel sans-drive | **0.534 = 53 % de N0** (20–96 %) |
| mémoire stockée m₊ | 0.197 |
| modulation fractionnelle uptake par mémoire ≈ λ₊·\|m₊\| | **≈ 4.9 %** |
| modulation fractionnelle uptake par résidu ≈ \|ΔN\|/N0 | **≈ 53 %** → **résidu ≈ 11× la mémoire** |
| corr(dose, résidu ΔN) | +0.86 |
| corr(résidu ΔN, Δuptake en place) | **+0.95** |

⇒ **le signal comportemental « en place » est à ~95 % du résidu de nutriment, pas de la mémoire.** Le DD(Δuptake)≈1629 hérité est très probablement un **artefact de nutriment résiduel** dose-corrélé, non une lecture de mémoire.

**Ce que je retiens comme readout comportemental** : une **conséquence intégrée en aval**, sous **stimulus commun**, corps+environnement standardisés — l'**uptake intégré sur un horizon fixe** *certifié uniquement via le contraste d'intervention* (intact − effacé), plus la **croissance résultante** (Δmasse/Δtaille) et la **production d'attractant / chimiotaxie** comme axes secondaires intégrés. Le contraste intact−effacé rend le résidu **commun-mode** (l'effacement mémoire ne touche pas N) : il s'annule dans la différence. C'est ce qui convertit l'uptake en readout causal valide, malgré son couplage direct.

## 4. Éliminer les résidus de N, c, masse, taille, position après l'histoire

Deux leviers combinés :
- **Contraste apparié** (intact vs erase-target) : l'effacement met Mf→0 dans la région cible **sans toucher ρ, U, V, N, c ni la position**. Donc masse/taille/position **et le champ N/c résiduel sont identiques** dans les deux branches → **communs-mode, s'annulent** dans la différence. C'est la protection principale.
- **Standardisation du stimulus** : le résidu ΔN reste dose-corrélé et **amplifie multiplicativement** l'effet (g∝N). Pour une **réponse-dose propre**, ramener N à l'ambiant. Courbe de washout mesurée (résidu ΔN, % de N0) : **+0→53 % ; +120→30 % ; +300→13 % ; +600→3.2 % ; +1000→0.13 %**. Je préinscris un **washout naturel jusqu'à résidu ΔN < 2 % de N0** (data-driven ⇒ ~800 pas) **puis** un stimulus **uniforme commun** identique à toutes les branches. Le résidu de c est traité par washout naturel (décroissance δ), **pas** par reset brutal (cf. Q5).
- **Corps commun (transplant)** comme contrôle convergent : élimine masse/taille/position/résidu **par construction**.

## 5. Un reset environnemental risque-t-il de modifier la gouttelette ?

**OUI, surtout pour c.** c entre dans l'advection chimiotactique (`χ ∝ 1/(1+(c/c_sat)²)`) et la cohésion : un **reset brutal de c** change les flux et peut **déplacer/déformer** la gouttelette — il perturberait ce qu'on mesure. Un reset de N est plus doux (N n'entre que dans l'uptake). **Décision : washout naturel** (laisser N et c relaxer par leur propre dynamique D_N/F et δ, physique gelée) plutôt que reset instantané ; si standardisation, **seulement N**, doucement. Le pilote DEV vérifie explicitement que washout/standardisation ne bouge pas ρ/position au-delà d'une tolérance, et qu'effacer la cible ne modifie pas directement les voisines.

## 6. Essai in-place, transplant standardisé, ou les deux ?

**Les deux — complémentaires, avec l'in-place comme PRIMAIRE.**
- **In-place apparié** (primaire) : corps réel, **mémoire spatiale réelle**, intervention do minimale et locale, résidu commun-mode annulé. Écologiquement pertinent. *Limite : le washout nécessaire (~800 pas) oublie la composante rapide m1.*
- **Transplant** (secondaire convergent) : corps+environnement **strictement communs**, **zéro résidu par construction, aucun washout** → peut sonder **dose ET ordre**. *Limite : utilise la mémoire moyenne (perte du spatial), artificiel.*
Accord des deux = preuve forte ; divergence = drapeau d'artefact.

## 7. Puissance des seeds 52001–52012 (~75 % d'éligibilité)

À 9/12≈75 % → **9 mondes, 27 gouttelettes**. Le stockage au repos est **grand** (own-order 0.654, null-95 intra-monde≈0.27) et déjà significatif à n=9 (p=2×10⁻⁴) — **répliquer K2a est bien alimenté**. Mais l'effet **comportemental** est **~10–20× plus petit** (transplant : Δuptake≈2 % de la base, Δc≈5 %). Le **contraste apparié** récupère de la puissance en annulant le bruit commun-mode, mais l'effet reste faible.
**Je ne tranche pas ici** : une **analyse de puissance au niveau monde** (phase dédiée), calibrée par l'effet apparié par-monde et sa variance estimés au **pilote DEV**, décidera. Règle préinscrite : si la SNR par-monde de l'effet apparié est marginale à n=9, je **fige une famille prospective plus grande** (p. ex. 52001–52024) **avant** d'ouvrir quoi que ce soit ; toute extension adaptative fondée sur la seule éligibilité est **scellée à l'avance**. Aucune extension après avoir vu les outcomes.

## 8. La préinscription réparée (53fd2b6) est-elle complète et non ambiguë ?

**Forte mais incomplète pour un test causal propre.** L'ADDENDUM_01 corrige bien : (a) sépare K2a (stockage/mémoire) de K2b (comportemental) ; (b) **pré-déclare les deux coordonnées** (fin de la bascule dose↔ordre post-hoc) ; (c) committe le régénérateur ; (d) rend les contrôles first-class ; (e) exige **l'effondrement sous ablation** pour le mot « causal » ; (f) gèle la table C-K1…C-K5 et la règle de décision.
**Lacunes que je dois combler dans le PRESEAL :**
1. K2b y est défini comme **Δuptake/Δmean_c en place vs contrefactuel sans-drive, SANS washout ni standardisation** → mes données montrent que c'est ~95 % de résidu N. Le garde-fou « l'ablation doit l'effondrer » empêche les **faux positifs** mais le design ne peut pas **attribuer positivement** un signal à la mémoire ; il **manque la double dissociation** (reset-sans-effacement vs effacement-sans-reset).
2. **Aucune durée de washout** spécifiée.
3. **Rôles des coordonnées non classés par persistance** : la physique impose dose (m2 lent) **primaire**, ordre (m1 rapide) **secondaire** (cf. §9).
4. **Taille d'effet comportementale / puissance non quantifiées.**
⇒ La réparation est **nécessaire** ; le PRESEAL étend l'ADDENDUM pour corriger 1–4. En l'état, l'ADDENDUM n'est **pas suffisant** pour trancher la causalité comportementale.

**Classification des coordonnées (figée, pré-observation, justifiée par la physique gelée).** Constantes d'oubli : m1 rapide `η_d1=0.35` (e-fold ≈ 28 pas), m2 lent `η_d2=0.006` (e-fold ≈ 1666 pas). Tout washout suffisant pour retirer le résidu (~800 pas) **oublie m1** → l'**ordre** (m₋=m1−m2, porté par m1) **ne survit pas** ; seule la **dose** (m₊, portée par m2 lent) persiste. Donc : **DOSE = primaire** (test in-place apparié) ; **ORDRE = secondaire**, explicitement justifié, testé **uniquement** par le transplant sans-washout (où m1 est préservé). Cohérent avec le résultat turnover profond (ordre négatif, p=0.92).

## 9. Meilleure explication alternative si l'effet comportemental disparaît

**L'« individuation comportementale » antérieure était de la contamination par nutriment résiduel** : les gouttelettes baignaient dans des poches de N résiduel **dose-corrélées** (corr 0.86), produisant des uptakes immédiats différents **sans implication de la mémoire** (corr(résidu, Δuptake)=0.95 ; résidu 11× la mémoire). La mémoire **est** stockée (le repos est réel) mais reste **causalement silencieuse** sur le comportement aux magnitudes atteintes (λ₊·m₊≈5 %, et encore moins pour la composante lente persistante) : **état stocké mais non exprimé** (Cas B/E).
Alternative secondaire : effet réel mais **sous le seuil de détectabilité au niveau monde à n=9** (sous-puissance), distinguable par l'analyse de puissance et l'IC préinscrits.

## 10. ACTIVE-RECONSTRUCTION serait-elle la bonne prochaine étape en cas d'échec causal ?

**NON.** Si la causalité comportementale échoue, construire une mémoire **plus persistante** (Exp 2) attaque le **mauvais problème** : la panne serait dans la **lecture** (l'état stocké n'atteint pas le comportement), pas dans la **persistance** du stockage. La bonne suite (Cas B) est d'**étudier l'architecture de readout** — pourquoi un état réellement stocké reste causalement muet (force de couplage λ₊, saturation `tanh`, oubli de la composante exprimable) — **avant** d'ajouter de la persistance. ACTIVE-RECONSTRUCTION n'est justifiée qu'en **Cas A authentique** (repos répliqué **ET** causalité comportementale passe **ET** turnover profond indéterminé/négatif). De toute façon **interdite dans cette mission**.

## Position figée avant confirmation (résumé)

1. **Stockage/lecture au repos : établi** (je re-certifie).
2. **Causalité comportementale : non démontrée**, et le design hérité (K2b en place) est **confondu par ~95 % de résidu N** — quantifié, pas supposé.
3. **Protocole retenu** : intervention appariée in-place (primaire, DOSE) + transplant corps-commun (secondaire, DOSE & ORDRE), double dissociation reset↔effacement, washout naturel jusqu'à résidu <2 % N0, ablation de lecture, sham, erase-neighbour. Readout = conséquence intégrée sous stimulus commun, certifiée par contraste d'intervention.
4. **Coordonnées** : dose primaire (m2 lent), ordre secondaire (m1 rapide, non-survivant au washout) — figé par la physique.
5. **Puissance** : décidée au niveau monde après pilote DEV ; famille agrandie et scellée d'avance si marginale.
6. **En cas d'échec causal : REPAIR/étudier le readout, PAS ACTIVE-RECONSTRUCTION.**

*Rien poussé, tagué, publié. main/V4/release intacts. Aucune revendication d'identité, de vie ou d'agence.*
