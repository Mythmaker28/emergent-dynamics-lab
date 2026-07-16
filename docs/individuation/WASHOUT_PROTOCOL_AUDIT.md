# WASHOUT_PROTOCOL_AUDIT — LCI-CAUSAL-MERGE-INCIDENT-01 (Phase 5)

*Audit du washout et du protocole gelé, croisant `CAUSAL_CONFIRMATION_INDEPENDENT_VIEW.md`,
`CAUSAL_CONFIRMATION_PROTOCOL_01.md`, `CAUSAL_CONFIRMATION_PRESEAL_01.json`, `causal_confirm.py`, `VERDICT_01`.
Mesures reproduites byte-identique (`washout_audit.py` → `work/washout_audit.json`). **Le PRESEAL n'est pas
modifié rétroactivement.***

## Résumé

| Point vérifié | Constat |
|---|---|
| 1. Independent View annonçait washout naturel jusqu'à résidu ΔN **<2 % de N0 (~800 pas)** | Confirmé dans le doc (§4 ; courbe committée 0→53 %, 120→30 %, 300→13 %, 600→3.2 %, 1000→0.13 %). |
| 2. PRESEAL utilise **WASHOUT_LONG=200** | Confirmé (`frozen_constants.WASHOUT_LONG=200`). |
| 3. Résidu N réel après **200** pas | **Mesuré : 19.4 % de N0** (moyenne 6 seeds ; reproduit la courbe de l'Independent View : 0→50.9 %, 120→28.1 %, 200→19.4 %, 300→12.4 %, 600→3.1 %, 800→0.9 %). |
| 4. Expression « suppression du résidu » | **Inexacte pour le washout de 200 pas** (19 %, pas <2 %). La suppression réelle vient du **reset N:=N0** (WASHOUT_B=40), pas du washout naturel. À corriger. |
| 5. Transplant annoncé comme contrôle secondaire, exécuté ? | **NON.** Le transplant n'existe que dans `probe_confound_dev.py` (sonde DEV Phase 0) ; **absent** du runner scellé `causal_confirm.py`. Contrôle secondaire convergent **non réalisé**. |
| 6. Écarts réflexion↔protocole gelé↔exécution | Documentés ci-dessous. |

## Détail

### 3–4. Le washout de 200 pas ne « supprime » pas le résidu

La courbe de résidu ΔN (monde avec drive − contrefactuel sans-drive, dans les régions cibles, en % de N0),
reproduite indépendamment sur la plateforme scellée :

```
  step :      0     40    120    200    300    400    600    800   1000
  %N0  :   50.9   41.5   28.1   19.4   12.4    7.9    3.1    0.9    0.0
```

À `WASHOUT_LONG=200`, le résidu vaut **19.4 % de N0** — presque **10×** le seuil <2 % que l'Independent View
avait préinscrit, atteint seulement vers **~800 pas**. Or `causal_confirm.py` (l.42) justifie le choix de 200 par
un commentaire : *« residual ΔN decays to <~1% N0 (DEV curve) »* — **faux d'un facteur ~20** ; la propre courbe de
l'Independent View (300→13 %) impliquait déjà ~19 % à 200 pas.

Conséquence sur l'interprétation : le gate **G3f « survie au washout »** n'est **pas** un test « résidu ≈ 0 ». Il
montre que l'effet apparié survit à **200 pas de décroissance naturelle partielle** (résidu ~19 % restant), ce
qui reste un contrôle utile, mais la formule du VERDICT_01 « survie au washout naturel … suppression du résidu de
nutriment » **conflates** deux mécanismes distincts :

- **branches standardisées** (A, sham, ablate, erase) : résidu retiré **par construction** via `N:=N0` (reset),
  washout court WASHOUT_B=40 ;
- **branches longues** (intact_long, erase_long) : **pas** de reset, 200 pas de washout naturel → **19 %**
  résidu restant.

La « suppression du résidu » est réelle **seulement** dans les branches à reset. À corriger dans tout énoncé
futur : dire « effet robuste au reset N **et** à 200 pas de washout naturel partiel (résidu ~19 %) », pas
« suppression du résidu ».

Nuance importante : cette correction **n'annule pas** l'argument anti-confusion. La **double-dissociation**
(effet quasi identique avec/sans reset, ratio 1.13) et l'**effondrement sous ablation** (0.000) restent des
arguments valides que le signal n'est pas un pur résidu de nutriment. Le washout de 200 pas est simplement
mal-nommé « suppression », et le résidu n'y est pas négligeable.

### 5. Transplant non exécuté

L'Independent View §6 posait le **transplant corps-commun** comme « contrôle secondaire convergent » (zéro résidu
par construction, sonde dose ET ordre). Le runner scellé n'implémente **aucune** branche transplant ; le mot
n'apparaît que dans la sonde DEV `probe_confound_dev.py`. Le contrôle convergent annoncé **manque** à la
confirmation. Ce n'est pas une faute de gel (le PRESEAL ne le listait pas dans les gates), mais un **écart entre
la réflexion Phase 0 et l'exécution** : un contrôle jugé important n'a pas été porté dans le pipeline gelé.

### 6. Écarts réflexion ↔ gel ↔ exécution

- **Washout** : réflexion « <2 % (~800 pas) » → gel « 200 pas » (justifié par un commentaire erroné « <1 % ») →
  exécution « 19 % résidu ». Écart non signalé dans le VERDICT.
- **Transplant** : réflexion « contrôle secondaire » → gel : absent → exécution : absent.
- **Fusion** : ni la réflexion Phase 0, ni le PRESEAL, ni le VERDICT ne mentionnent un **critère géométrique de
  non-fusion** pour l'amplitude/durée du probe, alors que la fusion était déjà présente dans **6/8 mondes DEV**
  de calibration (vérifié en Phase 2). L'amplitude « frozen PROBE » a été gelée sur des données DEV
  elles-mêmes fusionnées et non diagnostiquées.

## Recommandations (pour la préinscription corrigée, sans toucher au PRESEAL actuel)

1. Si washout naturel visé « sans résidu » : **~800 pas** (ou reset N explicite, en l'assumant comme tel).
2. Corriger la formule « suppression du résidu » → « reset N + washout partiel 200 pas (résidu ~19 %) ».
3. Ajouter le **critère géométrique de non-fusion** au choix du probe (Phase 6).
4. Exécuter effectivement le **transplant** secondaire, ou retirer l'annonce.

*PRESEAL inchangé. main/V4/release intacts. Rien poussé/publié.*
