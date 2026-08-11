# FSQBT00 — FRESH_SERIALIZED_QUOTIENT_BASIS_TRANSFER_00 — Rapport final

**DISPOSITION =**
`FRESH_PANEL_COMPLETE__FROZEN_P2_NOT_TRANSFERRED_PERBLOCK_TUBE_BREACH__FROZEN_E2_NOT_TRANSFERRED__CARRIER_DIRECTION_REPLICATED_12_OF_12__FRESH_QUOTIENT_RELATIVE_AT_LEAST_TWO_SECOND_BELOW_ABSOLUTE`

## Champs orthogonaux (jamais fusionnés)

| champ | valeur |
|---|---|
| PARENT | SQDT00 `16717582…` → FWL2CF00 `96c7d295` |
| MAIN_DE_TOMMY | `f3921a4d…` — jamais déplacé/extrait/fusionné |
| UNITÉ_INDÉPENDANTE | le bloc d'ascendance ; **n = 12** |
| CELL_MATERIALITY_STATUS | **PASS_24_OF_24** (marges M2/TAU 3.16–10.20) |
| LOBO_P2_LICENSE (corrigée) | **ACCORDÉE** |
| LOBO_E2_LICENSE (corrigée) | **ACCORDÉE** |
| FROZEN_P2_TRANSFER_STATUS | **NOT_TRANSFERRED** (T4 par-bloc échoue) |
| FROZEN_E2_TRANSFER_STATUS | **NOT_TRANSFERRED** (sous plancher + gated par P2) |
| E2_CARRIER_ORIENTATION_STATUS | **REPLICATED_WITH_DIRECT_MATERIAL_CONTRAST** (direct 12/12, concordant 10/12) |
| PROJECTIVE_P2_SECOND_ORIGIN | NOT_EVALUABLE (gated par la non-transférabilité de P2) |
| FRESH_QUOTIENT_STATUS | **RELATIVE_AT_LEAST_TWO__SECOND_BELOW_ABSOLUTE_MATERIALITY** |
| GÉOMÉTRIE / ALLOCATION / DOSE | NOT_TESTED_IN_THIS_DESIGN |
| DÉMARRAGES | construction 12, sham 24, actif 24, diagnostic 1 → **total 61 / 72** |
| DÉVIATIONS | D0–D2 (héritées), D3 (1 démarrage diagnostic, seed 70000, aucun résultat lu), D4 (checkpoints plein-champ digestés) |
| OBJET V1 | jamais réajusté / redimensionné / recentré / tourné / re-versionné |

## Les onze points demandés

1. **3,14° de SQDT00 : vrai LOBO ou LODO ?** — **LODO**. Le code `for dleft in range(16): keep=[i
   for i if D_OF[i]!=dleft]` retire **un descendant (2 lignes)** par pli sur 16 plis ; l'unité
   indépendante est le bloc. L'audit correct (leave-one-**bloc**-out, 4 plis, 8 lignes chacun) est
   recalculé ici **sans modifier** l'objet V1.

2. **Licences corrigées + 4 plis vrais.** Sous l'unité correcte : alignement carré min du plan P2
   `0,9962` (>0,80), alignement projectif carré min de e2 `0,9962` (>0,64), contribution maximale
   d'un bloc à I2 `0,3529` (<0,50), argmin commun k=0,1,2 avec I2>0 et les deux portes relatives sur
   chaque pli. **P2_TRANSFER_LICENSE_CORRECTED = VRAI**, **E2_AXIS_TRANSFER_LICENSE_CORRECTED =
   VRAI**. TUBE_P2_LOBO = 1,217·10⁻⁷.

3. **Unités indépendantes : 12** (graines 65100–65111, un descendant chacune). Jamais 24/48/sites/temps.

4. **Démarrages.** construction 12/24, sham 24/24, actif 24/24, + 1 diagnostic (D3) = **61/72**.

5. **Matérialité cellulaire : 24/24** matérielles ; marges M2/TAU 3,16 à 10,20.

6. **Transfert P2 gelé.** L'**agrégat** transfère : énergie projetée 4,03·10⁻⁶ > E_TAU 1,11·10⁻⁶
   (T2), résidu agrégé hors-plan 8,52·10⁻⁸ < tube 1,22·10⁻⁷ (T3). Mais **T4 par-bloc échoue** :
   **3 des 12 blocs** dépassent le tube LOBO — 65101_NEAR_a1 (×1,22), 65104_NEAR_a0 (×1,14),
   65108_NEAR_a0 (×1,06). Par la règle « une bonne moyenne ne peut masquer une ascendance hors du
   tube », **P2 ne transfère pas**. T5 (LOFO) suit ; T6 invariant de jauge.

7. **e2 gelé.** Énergie incrémentale 4,59·10⁻⁷ < plancher E_TAU 1,11·10⁻⁶, et l'axe est verrouillé
   par l'échec par-bloc de P2 → **NOT_TRANSFERRED**. **Mais** le contraste porteur direct en unités
   natives est **matériel dans 12/12 blocs**, et concordant avec l'orientation e2 parente dans
   **10/12** : `REPLICATED_WITH_DIRECT_MATERIAL_CONTRAST`. L'effet porteur se reproduit ; l'axe gelé
   précis, non.

8. **Quotient frais (propre ajustement affine, espace séparé).** R0=4,09·10⁻⁶, I1=3,57·10⁻⁶,
   I2=4,41·10⁻⁷, R1=5,18·10⁻⁷, R2=7,67·10⁻⁸ ; I2/R0=0,108, R1/R0=0,127, I2 **sous** le plancher
   absolu → `RELATIVE_AT_LEAST_TWO__SECOND_BELOW_ABSOLUTE_MATERIALITY`. Les données fraîches
   reproduisent **indépendamment** la structure qualitative du parent.

9. **Séparation stricte structure fraîche / transfert d'objet.** Le quotient frais positif est une
   **structure nouvelle**, pas un transfert de l'objet parent ; il ne sauve pas le transfert échoué.
   L'énergie e2 gelée est mesurée autour de `mu_parent` ; I2_fresh utilise une moyenne affine
   fraîche — deux champs orthogonaux, jamais abrégés en une « seconde matérialité » ambiguë.

10. **Déviations, vérification, tip, main.** D0–D2 héritées ; D3 (un démarrage diagnostic seed 70000,
    aucun résultat lu, seed consommée) ; D4 (checkpoints plein-champ 7,7 Mo gardés dans l'atelier,
    digestés ; preuves de score support-restreintes committées avec preuve de suffisance).
    SHA256SUMS vérifié depuis l'arbre committé et un ré-extrait ; id de sous-arbre reproduit par
    git 2.34.1 et 2.43.0 ; bundle vérifié. **main inchangée à f3921a4d.** Aucun push/PR/workflow.

11. **Jugement scientifique.** Le phénomène se reproduit ; l'objet gelé précis, non. Les deux
    porteurs historiques produisent des réponses matérielles sur les 12 blocs frais (24/24), et le
    contraste porteur reproduit sa direction dans 12/12 blocs — l'effet physique est robuste et
    prospectivement répliqué. La **géométrie fittée** de l'objet réponse-informé (le plan P2 précis,
    l'axe e2) ne transfère pas au tube par-bloc : 3 blocs frais (tous NEAR) portent une composante
    hors-plan supérieure au pire bloc parent. C'est exactement ce qu'un test hors-échantillon strict
    doit révéler — un objet ajusté sur 4 blocs parents est, aux marges, spécifique à ce panel. Le
    fait descriptif que les 3 blocs fautifs soient NEAR est **générateur d'hypothèses seulement**
    (géométrie NON_TESTÉE). Le quotient frais retrouvant, en aveugle, la même structure
    relative-au-moins-deux que le parent est un résultat positif indépendant — sur la structure, pas
    sur l'objet.

---

GOOD_NEWS = Les deux porteurs historiques restent matériels sur douze blocs d'ascendance **frais**
(24/24, marges 3,16–10,20) ; l'objet V1, d'abord **requalifié par le vrai leave-one-bloc-out**
(licences P2 et e2 accordées, alignements ≥0,996, aucun bloc >0,353 de I2), voit son **plan P2
transférer en agrégat** (énergie projetée 3,6× E_TAU, résidu agrégé 0,70× tube) ; le **contraste
porteur direct est matériel dans 12/12 blocs** et concordant à 10/12 ; et le quotient frais
retrouve **indépendamment** la structure relative-au-moins-deux du parent.

LESS_GOOD_NEWS = Le transfert **strict sans réajustement échoue** : 3 des 12 blocs frais (tous NEAR)
dépassent le tube LOBO par-bloc (×1,06–1,22), donc `FROZEN_P2_TRANSFER = NOT_TRANSFERRED` ; l'axe
e2 gelé est sous le plancher absolu (4,59·10⁻⁷ < 1,11·10⁻⁶) et verrouillé par cet échec ; le
quotient frais est relatif mais son second incrément reste sous la matérialité absolue.

WHAT_IT_CHANGES = On distingue proprement, pour la première fois hors échantillon, **l'effet
porteur** (robuste, répliqué en direction sur 12/12) de la **géométrie fittée précise** (plan P2 /
axe e2, spécifique au panel parent aux marges) : l'objet réponse-informé ne se transporte pas tel
quel, alors que la structure qu'il encode réapparaît. La correction d'unité (LODO→LOBO) est actée
sans toucher l'objet immuable.

NEXT_SCIENTIFIC_ELIGIBILITY = P2 ayant échoué, **ne pas** chasser l'amplitude ni inventer un
troisième porteur : diagnostiquer d'abord la non-transférabilité. Un programme séparément autorisé
peut (a) caractériser la composante hors-plan des blocs NEAR frais comme une question descriptive
prospective, à jauge légale gelée ; et (b) puisque le quotient frais est relatif-au-moins-deux
tandis que P2 gelé échoue, traiter cette structure comme **nouvelle**, exigeant un nouveau partage
découverte/hold-out — jamais un réajustement de V1. Aucune action de Tommy ni action git requise.
