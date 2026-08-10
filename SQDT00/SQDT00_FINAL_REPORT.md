# SQDT00 — SERIALIZED_QUOTIENT_DOSE_TRANSFER_00 — Rapport final

**DISPOSITION =**
`OFFLINE_QUOTIENT_BASIS_SERIALIZED_AND_TRANSFERABLE__DOSE_2X_STATICALLY_INADMISSIBLE__NO_FRESH_PANEL__ZERO_STARTS`

## Champs orthogonaux obligatoires

| champ | valeur |
|---|---|
| PARENT | `96c7d295e72106cd949d810fa92807c2514e7449` (dev/fresh-weighted-l2-carrier-factorial-00) |
| MAIN_DE_TOMMY | `f3921a4d…` — jamais déplacé, extrait, fusionné ni modifié |
| Q1_OFFLINE | **COMPLET** — redérivation exacte + base sérialisée + licences P2 et E2 accordées |
| Q2_PANEL | NON_LICENCIÉ (arrêt S5) |
| Q3_CELL | NON_ÉVALUABLE (aucune ligne fraîche) |
| Q4_DOSE | STATIQUEMENT_INADMISSIBLE |
| Q5_QUOTIENT | NON_ÉVALUABLE (aucune ligne fraîche) |
| Q6_TRANSFER | MACHINERIE_PRÊTE (aucune ligne fraîche à projeter) |
| R0 (exact) | reproduit **bit-à-bit** le rationnel parent de 1077 chiffres |
| I1 = λ₁ | encadrement certifié [3.63817765e-06, +5e-23] |
| I2 = λ₂ | encadrement certifié [3.62108242e-07, +5e-23] |
| ENERGY_MULTIPLIER_REQUIRED | **3.076** (intervalle certifié) |
| AMPLITUDE_MULTIPLIER_REQUIRED | **1.754** (intervalle certifié), **strictement < 2** |
| P2_TRANSFER_LICENSE | **ACCORDÉE** |
| E2_AXIS_TRANSFER_LICENSE | **ACCORDÉE** |
| GÉOMÉTRIE / ALLOCATION | NOT_TESTED_IN_THIS_DESIGN |
| UNITÉ_INDÉPENDANTE | le bloc d'ascendance ; n=8 **conçu, non construit** |
| DÉMARRAGES_MOTEUR | **0 / 64** (panel 0/16, sham 0/16, actif 0/32, autre 0/0) |
| TOMMY_ACTION_REQUIRED | false | 
| TOMMY_GIT_ACTION_REQUIRED | false |
| PUSH / DRAFT_PR / WORKFLOW | false / false / false |
| DÉVIATIONS | D0 (texte du handoff perdu à la compaction), D1 (clone complet remplacé), D2 (empreinte de bundle parent périmée, héritée) |
| NAMESPACE_62000_62009 | RÉSERVÉ_ET_NON_LU — jamais généré ni ouvert |

## Seize explications

1. **Provenance résolue depuis la branche, pas depuis la prose.** Les 13 commits de la chaîne
   (WSCCRP00 → … → FWL2CF00 commit 6) ont été lus par `git rev-parse` ; 12/12 flèches sont des
   parents directs uniques, sans aucune fusion.

2. **Contenu vérifié deux fois, dans deux conteneurs, avec deux git.** `SHA256SUMS` : 198/198 sur
   l'appareil (extraction depuis la base d'objets) **et** 198/198 dans le conteneur cloud ; le
   sous-arbre `FWL2CF00` `159577ee…` est recalculé identiquement par git 2.34.1 et 2.43.0. Un id
   d'arbre git est un hachage de contenu pur : cet accord certifie récursivement chaque blob.

3. **Gel maître avant tout chargement numérique.** `SQDT00_MASTER_FREEZE.md` a été écrit, haché et
   committé (commit 1) **avant** d'ouvrir le moindre npz, série de lecteur ou vecteur de score.

4. **Certificat de suffisance à support restreint.** La série du lecteur reconstruite depuis les
   octets bruts de `rho` sur le support d'union reproduit la série committée **caractère par
   caractère** (48/48). Le champ hors-support n'est donc jamais lu.

5. **R0 exact = parent, bit-à-bit.** La forme quadratique binaire exacte sur les 2¹⁵ jauges donne
   un `R0` égal au rationnel committé de 1077 chiffres. Aucun écart.

6. **Encadrements certifiés, pas seulement des flottants.** `R1, R2, I1, I2` sont encadrés par des
   intervalles rationnels exacts (inertie de Sylvester par mineurs principaux de Bareiss + borne de
   Weyl), largeur ≈ 5·10⁻²³. Les flottants parents tombent dans ces intervalles à leur propre
   borne de stabilité arrière près.

7. **Jauge argmin exacte et partagée.** `eps*` est l'argmin exact de `R0` et atteint aussi `R1` et
   `R2` (même argmin pour k=0,1,2), condition BASIS_S1–S2.

8. **Objet de découverte sérialisé comme de vrais tableaux.** `FWL2_RELATIVE_QUOTIENT_BASIS_V1`
   (`.npz` + `.json`) porte `mu, e1, e2, P1, P2`, les scores par ligne, la canonicalisation de
   signe et les signes de jauge. Ce n'est **pas** un résumé scalaire.

9. **Les huit portes de stabilité passent.** `BASIS_S0…S7` : octets committés seuls, argmin exact,
   argmin partagé, encadrements disjoints (λ₁>λ₂>λ₃), orthonormalité (résidu 5·10⁻¹⁶), angle
   principal *leave-one-descendant-out* max 3.14° (< 30°), identité de reconstruction, aller-retour
   disque bit-à-bit.

10. **Licences de transfert accordées.** `P2_TRANSFER_LICENSE` et, imbriquée,
    `E2_AXIS_TRANSFER_LICENSE` sont accordées : le 2-plan **et** l'axe individuel `e₂` transfèrent,
    car `λ₂` est certifié séparé de `λ₃`. C'est exactement ce que le parent ne pouvait pas faire :
    GIMB00 n'avait sérialisé que des scalaires, et **on ne projette pas sur un scalaire**.

11. **Invariance par duplication.** Dupliquer exactement les lignes laisse `R0`, `I2` et tous les
    ratios inchangés (preuve + numérique exact) ; c'est ce qui autorise à comparer un panel de 8
    descendants aux 32 lignes du parent.

12. **Multiplicateurs certifiés, jamais le 0.570 arrondi.**
    `ENERGY_MULTIPLIER_REQUIRED = E_TAU/lower(I2) = 3.076`,
    `AMPLITUDE_MULTIPLIER_REQUIRED = upper(A_TAU)/lower(√I2) = 1.754`, en intervalles certifiés.

13. **Distinction décisive S4 vs S5.** S4 (« une dose ×2 suffirait-elle ? ») **passe** : 1.754 < 2,
    donc une dose doublée, si elle existait et était linéaire, ferait passer le second mode au-dessus
    du plancher absolu. S5 (« une dose ×2 existe-t-elle ? ») **échoue**. On s'arrête sur l'existence,
    pas sur la suffisance.

14. **Les deux porteurs verrouillés sont des involutions.** `matched_transposition` :
    `op² = identité` bit-à-bit pour les 16 descendants ; `intensive_reflection` : involution à
    ~10⁻¹⁶ près (artefact du plancher `rho`=1e-12, pas une dose). Répéter une involution donne
    l'identité : « deux fois la dose » retombe sur **aucune intervention**. Aucun paramètre
    d'amplitude n'existe dans les signatures ; l'appariement est déjà de cardinalité maximale ; et
    le mélange d'amplitude γ=2 **viole le prédicat de domaine gelé** `|Mf[0]| ≤ rho` sur les états
    réels. Aucune dose ×2 légitime sans exécutable nouveau — donc interdite.

15. **Oracle non-vacué (17 groupes).** Chaque groupe Q0A–Q0Q énonce une identité positive qui tient
    **et** un contrôle négatif qui se déclenche (poids, lecteur, zéro structurel, énergie u/v, jauge
    par bloc, minimiseur R0, encadrement, séparation, projection, reconstruction, duplication,
    agrégation α=1/16, sens du multiplicateur, mise à l'échelle de dose, involution, domaine,
    liaison de provenance). La machinerie hors-ligne ne peut pas approuver silencieusement une
    fausse entrée.

16. **Arrêt propre, zéro démarrage, et ce qui avance.** L'arrêt S5 est déclenché **avant** tout
    panel : 0/64 démarrages moteur. Fabriquer une dose maintenant, en sachant que le 1× manquait
    d'un facteur ~1.75, serait précisément le *dose/operator shopping* interdit. Ce qui avance vers
    un futur programme autorisé : une base relative-quotient **transférable et certifiée**, prête à
    recevoir par projection (sans réajustement) des réponses fraîches — le chaînon que le parent
    n'avait pas.

---

GOOD_NEWS = La redérivation hors-ligne reproduit `R0` du parent bit-à-bit et encadre `R1,R2,I1,I2`
à ~5·10⁻²³ ; l'objet `FWL2_RELATIVE_QUOTIENT_BASIS_V1` est sérialisé en vrais tableaux, passe les
huit portes de stabilité, et obtient les licences P2 et E2 — le défaut « non projetable » du parent
(scalaire) est levé. Le multiplicateur d'amplitude requis, certifié 1.754, est strictement inférieur
à 2.

LESS_GOOD_NEWS = La prémisse « doubler la dose » est **statiquement inadmissible** : les deux
porteurs verrouillés sont des involutions sans magnitude de dose ; un ×2 exigerait un exécutable
nouveau (interdit) ou viole le domaine gelé. Aucun panel frais n'est construit, `Q3/Q5` restent
non-évaluables et `Q6` sans lignes à transférer ; 0/64 démarrages.

WHAT_IT_CHANGES = Le programme passe d'un second mode « relatif mais sous le plancher absolu » à un
**axe sérialisé, certifié et transférable** pour ce second mode, réutilisable tel quel ; et il
établit, par arithmétique certifiée, qu'un facteur d'amplitude < 2 suffirait — tout en démontrant
que ce facteur ne peut pas être réalisé avec les porteurs verrouillés actuels.

NEXT_SCIENTIFIC_ELIGIBILITY = Un futur programme autorisé par le propriétaire qui dispose d'un
**axe de dose légitime** (un exécutable porteur paramétré par une amplitude, déclaré et verrouillé
en amont, admissible dans le domaine) **ou** d'un panel actif frais peut projeter ses réponses
weighted-L2 sur `P2`/`e₂` sans réajustement, et tester directement si une amplitude ~1.75–2×
franchit le plancher absolu de matérialité. Aucune action de Tommy ni action git n'est requise.
