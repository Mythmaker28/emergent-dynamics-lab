# MERGE_INCIDENT_ERRATUM — LCI-CAUSAL-CONFIRMATION-01

*Erratum explicite, produit par un agent d'audit indépendant (mission LCI-CAUSAL-MERGE-INCIDENT-01) sur la
branche isolée `audit/lci-causal-merge-incident-01` (base `b415503`). Il **n'altère pas l'historique** : les
commits `c371346` (RESULTS), `8b2e12d` (PRESEAL), `53fd2b6` (audit), `b415503` restent intacts, de même que
main `f3921a4`, V4, release. Rien poussé/tagué/publié. Cet erratum corrige l'interprétation, pas les données.*

## Objet

Le VERDICT_01 de LCI-CAUSAL-CONFIRMATION-01 annonçait, pour la famille 52001–52024 (13 mondes éligibles, 39
gouttelettes) : expression causale comportementale **ÉTABLIE** (G3 PASS), effet propre **+2.03** [1.63,2.48],
**13/13 mondes & 39/39 gouttelettes >0**, tracking **robuste 13/13**, indépendance-tracker **PASS**, et bascule
ACTIVE-RECONSTRUCTION **justifiée** (recommandation : répliquer d'abord).

Une relecture directe du raw, reproduite et étendue indépendamment ici, établit que **le readout comportemental
est corrompu par une fusion physique des gouttelettes suivie d'une collision d'affectation du tracker** dans
**11/13 mondes**. Corrections ci-dessous.

## Corrections (chiffrées, reproductibles)

1. **Fusion physique (nouveau fait).** Le stimulus comportemental — `st.N += 0.50` uniforme pendant 15 pas, soit
   **+7.5 = 7.5× l'ambiant N0** déversé sur toute la grille 64² — provoque une croissance ×19 médiane (max ×43)
   et une **percolation** : composantes finales couvrant jusqu'à **52 %** de la grille. Dans 11/13 mondes, ≥2
   cibles finissent dans **une seule** composante connexe. Preuve : **19 paires** de tracks à (taille, masse,
   mean_c) finales **byte-identiques** (branche intacte) ; mondes « les 3 cibles fusionnées » = 52005, 52010,
   52012, 52017 ; mondes propres = 52008, 52018. Reproduit par replay event-by-event (premier merge t=62–109,
   **phase horizon**, après le stimulus) et par le tracker bijectif (censures aux mêmes pas).

2. **Tracker non-bijectif (spec ≠ implémentation).** `TRACKER_SPEC.md` prescrit une affectation **un-à-un** ;
   `causal_confirm.py::measure_branch` implémente un `max(overlap)` **indépendant par track**, sans exclusion
   croisée (cadence 1, non 5). Conséquence : après fusion, 2–3 tracks lisent **la même** composante — ni censure,
   ni détection de merge.

3. **« 39/39 gouttelettes » → INVALIDÉ tel quel.** Composantes finales **uniques réelles = 24** (pas 39).
   Survivants individuels sous tracker bijectif (censure explicite du merge) = **17/39** ; **11/13 mondes ≤1
   survivant**. Le « 39/39 >0 » reflète un readout couplé positif partout (y compris tracker-free), pas 39
   entités distinctes.

4. **« Tracking robuste 13/13 » → INVALIDÉ.** Le tracking échoue dans 11/13 mondes ; la « survie » des tracks est
   un double-verrouillage sur un blob partagé, non une persistance individuelle.

5. **Magnitude +2.03 → tracker-gonflée ×4.8.** Le readout **masque-fixe** (sans tracker, C-K5) donne **+0.53**
   [0.36,0.73], soit **×0.21** du tracké. Le certificat rapportait ce chiffre mais le déclarait « PASS » sans
   signaler que seul le **signe** est indépendant du tracker, pas la **magnitude**. Le chiffre porteur à retenir
   est la valeur masque-fixe, pas +2.03.

6. **Localité (voisin 10.4 %) → contaminée en fusion.** Voisin propre **≈+0.0006** dans les mondes non fusionnés
   mais **+0.247** dans les fusionnés (effacer un voisin qui partage le blob affecte la même région). Le 10.4 %
   poolé dilue cette contamination.

7. **Washout (voir WASHOUT_PROTOCOL_AUDIT).** Le résidu ΔN réel après `WASHOUT_LONG=200` est **19.4 % de N0**
   (mesuré, reproduit la courbe de l'Independent View), non « <~1 % » comme l'affirme le commentaire du runner,
   ni le « <2 % » (~800 pas) préinscrit. La « suppression du résidu » est obtenue par le **reset N:=N0**
   (WASHOUT_B=40), pas par le washout de 200 pas. Le **transplant** annoncé (Independent View §6) comme contrôle
   secondaire **n'a pas été exécuté** dans le runner scellé.

## Ce qui reste valide (inchangé)

- **Stockage local au repos** (C-K1, DD_mem 5951) et **lecture de l'histoire au repos** (C-K2a, own-dose R²=0.75
  ≫ voisin) : **inchangés** — mesurés au repos, sans tracker comportemental ni fusion.
- Une **empreinte causale mémoire→feeding locale** (tracker-free ~+0.5, effondrement ablation 0.000,
  double-dissociation 1.13, DEV non-fusionnant +0.44 8/8) : **non invalidée**, mais **qualifiée** et **non
  re-confirmée** ici (diagnostic post hoc, pas un nouveau claim positif).

## Statut résultant

- **G3** : à ré-énoncer sur le readout masque-fixe et **re-confirmer sans fusion**.
- **G6 (individuation causale)** : **SUSPENDU**.
- **ACTIVE-RECONSTRUCTION** : **BLOQUÉE** jusqu'à une confirmation prospective **non-fusionnante** (réalisable —
  Phase 6 : 9 probes DEV géométriquement valides).
- **Aucun monde retiré silencieusement, aucun seuil modifié, aucun « tracker repair » présenté comme validant
  l'ancien résultat.**

*Fusion des gouttelettes ≠ git merge : rien n'est mergé/poussé/publié. main/V4/release intacts.*
