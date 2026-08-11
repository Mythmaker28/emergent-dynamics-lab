# FCRA00 — FSQBT00_CORRECTIVE_RESIDUAL_AUTOPSY_00 — Rapport final

**DISPOSITION =**
`FSQBT00_RECORD_CORRECTED__PROTOCOL_NONCONFORMANT__READER_LEVEL_PRIMARY_REPRODUCED__FULL_BYTES_RECOVERED_ON_CHILD__RESIDUAL_AUTOPSY_COMPLETE__NO_UNIQUE_DIRECTION__ZERO_STARTS`

Analyse correctrice et secondaire, **zéro démarrage moteur**. Objet immuable
`FWL2_RELATIVE_QUOTIENT_BASIS_V1` et tube jamais modifiés. `main` intacte.

## Les treize points demandés

1. **Provenance.** Tip parent FSQBT00 `b3f45ac7`, chaîne 7/7 parents directs uniques vers SQDT00
   `16717582` et FWL2CF00 `96c7d295` ; sous-arbre `ab11f2c0` ; bundle `0a7ce1e2` vérifié. Tip enfant
   FCRA00 : voir bundle de clôture. **`main` inchangée à `f3921a4d`**, jamais déplacée/extraite.

2. **Démarrages corrigés.** construction 12, sham 24, actif 24, **diagnostic 1** → **total 61**. Le
   chiffre 60 était le compte brut d'avancées de la phase scellée et excluait la sonde ; brut
   inclusif = 62. FCRA00 : 0 démarrage.

3. **La graine 70000 a-t-elle ouvert un résultat scientifique ? NON.** La sonde (transcript
   2026-08-11T01:02:33Z) a construit 70000 et l'a avancée 400 pas pour le chronométrage, ne lisant
   que `t0_masks` (admissibilité de construction) — aucun lecteur/delta/M2/score/quotient/seuil.
   `ONE_UNAUTHORIZED_START__NO_SCIENTIFIC_OUTCOME_OPENED_PROVEN`. Cela affaiblit la conformité mais ne
   contamine pas les 24 lignes actives scellées ; 70000 n'est jamais entrée dans le panel.

4. **Évidence.** `FSQBT00_ORIGINAL_TIP_DELIVERY_STATUS = INCOMPLETE_MISSING_FULL_CHECKPOINT_BYTES` ;
   `CHECKPOINT_BYTES_STATUS = RECOVERED_EXACT_BYTES_AND_COMMITTED` (12/12 vs digests committés) ;
   `MASK_EVIDENCE_STATUS = ORIGINAL_EXACT_BYTES_ALREADY_COMMITTED` ; `FCRA00_RECOVERY_STATUS =
   RECOVERED_EXACT_BYTES_AND_COMMITTED` ; `CURRENT_CHAIN_EVIDENCE_STATUS =
   COMPLETE_AFTER_APPEND_ONLY_CHILD_RECOVERY`. La suffisance support-restreinte est re-prouvée
   bit-à-bit contre les trajectoires plein-champ récupérées (reproductibilité bout-en-bout livrée sur
   l'enfant). Récupérer sur l'enfant ne rend pas le tip FSQBT00 historique auto-suffisant.

5. **Reproduction indépendante.** `PRIMARY_RECOMPUTATION_STATUS = PASS`. Lecteur production ==
   référence ; jauge résiduelle-optimale == jauge committée ; deux chemins de résidu concordants.
   **Matérialité cellulaire 24/24** (carrés exacts) ; **contraste porteur direct matériel 12/12**
   (exact). Tout reproduit.

6. **Magnitude vs direction.** `DIRECT_CARRIER_CONTRAST_MATERIAL = 12/12` (magnitude) ;
   `PARENT_E2_SIGN_CONCORDANCE = 10/12` (direction). « Direction répliquée 12/12 » est **retirée**.
   `P_VALUE_STATUS = NOT_LICENSED` ; références combinatoires 79/4096 (unilatéral), 79/2048 (bilatéral).

7. **P2 gelé (tous les 12).** Ratios résidu/tube (trichotomie certifiée) : 3 `CERTIFIED_EXCEED`
   (65101_NEAR_a1 ×1,222 ; 65104_NEAR_a0 ×1,137 ; 65108_NEAR_a0 ×1,058), 9 `PASS`, 0 non-résolu.
   Énergie projetée 3,62× E_TAU (T2✓), résidu agrégé 0,701× tube (T3✓), **T4 échoue** (par-bloc),
   T5 suit, T0/T1/T6 ✓. `FROZEN_P2_TRANSFER_AS_FROZEN = NOT_TRANSFERRED` (gate gelé, non reclassé).

8. **Quotient frais (exact).** R0 = 4,0924·10⁻⁶ ; I1 = 3,5746·10⁻⁶ ; I2 = 4,411·10⁻⁷ ; R1 =
   5,178·10⁻⁷ ; R2 = 7,669·10⁻⁸ ; I2/R0 = 0,108 ; R1/R0 = 0,127 ; I2/I1 = 0,123 ; argmin commun
   k=0,1,2 ; classe `RELATIVE_AT_LEAST_TWO__SECOND_BELOW_ABSOLUTE_MATERIALITY`. Nouvelle structure sur
   les **mêmes 24 lignes** — « indépendante » signifie indépendante du panel parent, pas du contraste.

9. **Ordre-statistique (interprétation, sans reclasser le gate).** Le tube = max de **4** plis de
   calibration ; le gate exigeait les **12** scores futurs en dessous. `P(K≥3) = 11/28 ≈ 0,393`. 3/12
   dépassements sont **banals** sous échangeabilité. `POPULATION_P2_NONTRANSFER =
   INCONCLUSIVE_FROM_THIS_GATE_ALONE`. Le prose FSQBT00 (« géométrie spécifique au panel parent ») est
   **rétréci** : gate strict échoué, non-transfert population **NON établi**.

10. **Anatomie exclusive du résidu hors-P2** (identités à 2,6·10⁻²³) : **INTERCEPT 2,8 %**,
    **COMMUN-CENTRÉ 30,9 %**, **DIFFÉRENTIEL 66,3 %**. Le décalage n'est **pas** une moyenne
    transportée (intercept minime) ; il est **dominé par la composante différentielle-porteur** — les
    deux porteurs quittent le plan parent **différemment**. Canal u(A+B) 50 % / v(A−B) 50 %.

11. **Diagnostics nuisance 2×2 (descriptifs, post-outcome, non causaux).** G(T) = 2,30·10⁻⁸, aire
    d'échangeabilité 70/400 = 0,175 ; comptage 2×2 (NEAR 3 / FAR 0) : `P_all3_in_NEAR = 1/11`,
    Fisher bilatéral 2/11. La géométrie/allocation ne sont **pas** randomisées au niveau de l'unité ;
    aucune causalité.

12. **Arbitrage de direction (une jauge légale g*).** `M0_NO_UNIQUE_DIRECTION_LICENSED` — **aucune
    direction sérialisée**. La direction différentielle NEAR−FAR est **cohérente en interne**
    (DX4 = 12/12 prédictions de plis, alignement min 0,995, levier max 0,144) mais échoue le garde de
    matérialité conservateur **DX2** (énergie-contraste 4,59·10⁻⁸ ≪ plancher 1,07·10⁻⁶) et la
    robustesse d'allocation **DX3**. La commune échoue aussi. Jauge unique (bloc-séparable).

13. **Jugement scientifique.** Le correctif tient : chaque résultat primaire FSQBT00 se reproduit
    indépendamment, la magnitude 12/12 est distincte de la direction 10/12, et l'échec strict du gate
    P2 **ne prouve pas** un non-transfert de population (seuil = max de 4 plis ; 3/12 attendu). L'autopsie
    localise le désaccord : il est **différentiel-porteur** (66 %), pas une moyenne transportée. Cette
    structure différentielle est remarquablement cohérente à l'intérieur des 12 blocs, mais reste
    **sous le plancher matériel conservateur et non robuste en allocation** — donc rien n'est gelé
    comme candidat de découverte. Les bytes plein-champ manquants ont été **récupérés** sur l'enfant.

---

GOOD_NEWS = Tout le primaire FSQBT00 se reproduit indépendamment (production == référence,
`PRIMARY_RECOMPUTATION_STATUS = PASS`) : matérialité 24/24, contraste direct **magnitude 12/12** ;
les **12 bytes de checkpoint plein-champ manquants sont récupérés et committés** (suffisance
bout-en-bout prouvée) ; l'anatomie exacte (identités à 2,6·10⁻²³) montre que le désaccord hors-P2 est
**66 % différentiel-porteur** et seulement **2,8 % intercept**, et cette direction différentielle est
cohérente en interne (DX4 12/12, alignement 0,995).

LESS_GOOD_NEWS = Le gate strict P2 échoue toujours exactement comme préenregistré (3/12
`CERTIFIED_EXCEED`, tous NEAR) et n'est pas reclassé ; l'e2 gelé reste `NOT_TRANSFERRED` ; la
conformité protocolaire FSQBT00 reste **NONCONFORMANT** (un démarrage diagnostic non autorisé, sans
résultat ouvert) et le tip original reste **incomplet** ; et aucune direction de découverte ne se
qualifie (`M0`) — le différentiel est sous le plancher matériel (DX2) et non robuste en allocation
(DX3).

WHAT_IT_CHANGES = Deux corrections de prose sont actées : **magnitude 12/12 ≠ direction 10/12** (« 12/12
répliquée » retirée), et **échec strict du gate ≠ non-transfert de population** (`P(K≥3)=11/28`). Et
l'autopsie transforme un « échec de transfert » diffus en un fait précis : le désaccord est
**différentiel-porteur**, interne-cohérent mais sous-matériel — une piste, pas une conclusion.

NEXT_SCIENTIFIC_ELIGIBILITY = Ni la commune ni la différentielle ne se qualifient : **ne pas ajuster
davantage de directions sur ces 12 blocs**. Un programme séparément autorisé doit ouvrir un **nouveau
partage découverte/hold-out** croisant NEAR/FAR × allocation **dans chaque nouvelle ascendance**, et
tester une direction différentielle **pré-gelée** comme interaction prospective (jamais un
réajustement de V1) — ou revisiter l'estimand de transfert (le gate strict max-de-4 vs un test de
population calibré). Les bytes plein-champ étant récupérés, une analyse hors-support reste possible
sous autorisation séparée, jamais inférée d'un hash. Ne pas chasser la dose ni inventer un troisième
porteur. Aucune action de Tommy ni action git requise.
