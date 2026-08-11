# FCDDH00 — RAPPORT FINAL (français)

```
DISPOSITION =
    DISCOVERY_SHAM_OR_ACTIVE_PANEL_INCOMPLETE__NO_AXIS__ZERO_HOLDOUT_STARTS
```

**Aucune des questions scientifiques du programme n'a reçu de réponse — et aucune n'a reçu de
fausse réponse.** L'appareil a été construit, gelé, audité et prouvé ; le panel de découverte
croisé à douze blocs a été construit et scellé exactement comme spécifié ; la phase des shams
jumeaux a ensuite été interrompue par une **panne de contrôle de processus côté exécuteur** qui a
coûté un démarrage moteur facturé, après quoi le panel ne pouvait plus être complété dans le
budget gelé. Le programme s'est arrêté de lui-même à l'arrêt prédéclaré au lieu de combler le trou.

---

## 1. Traçabilité Git

| | |
|---|---|
| tip parent (FCRA00) | `334b7c2ba6d97dadb403c7a1ea9700a1c61ad512` |
| sous-arbre FCRA00 | `b43e04983e6a3cbf31b6ccc84b5267fbe17b1ad2` |
| digest du bundle parent | `95ef451164d31bea9b16b94e6d86aadad40c696a308e007e9955b1e506ae2e3b` (conforme) |
| branche | `dev/fresh-crossed-differential-discovery-holdout-00` |
| chaîne vérifiée | `96c7d295 ≺ 16717582 ≺ b3f45ac7 ≺ 334b7c2b` (`merge-base`) |
| **main de Tommy** | `f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77` — **inchangé**, jamais extrait, jamais fusionné |
| arbre d'exécution | **1392 / 1392** chemins identiques octet pour octet à l'objet-arbre parent |

Le tip final, le SHA du sous-arbre et le digest du bundle final sont donnés hors bande à la fin.

## 2. Le croisement G1 a-t-il été prouvé depuis des octets de précurseur identiques ?

**Oui.** C'est l'acquis substantiel de cette exécution, et il survit à la clôture.

FSQBT00 portait **un** descendant par bloc, avec géométrie et allocation liées à `S mod 4` : les
deux facteurs étaient confondus avec l'ascendance. FCDDH00 les délie : **douze ascendances amont
indépendantes portant chacune le quatuor complet `{NEAR, FAR} × {membre H3 0, membre H3 1}`, les
quatre descendants issus d'un précurseur identique octet pour octet.**

Prouvé statiquement avant tout démarrage moteur, et vérifié numériquement dans chaque worker :
`seed_state` est un tirage pur (aucun pas moteur, aucun symbole de géométrie) ; la géométrie
n'entre qu'ensuite, comme argument explicite, via `set_geometry → _blob`, avant toute histoire ;
**48/48** descendants ont revérifié à l'exécution, avec zéro avance, que
`found(S) == PRECURSOR(S) × blob(g)` champ par champ. Les trois routes de construction (parité
historique, explicite historique, FCDDH00) exécutent la **même** séquence d'opérations et ne
diffèrent que par la garde `seed % 2 == 0` contre `a == 0`, qui est le même booléen sous
`a := 0 si S % 2 == 0 sinon 1`. Aucun nouveau LawSpec, aucun nouveau moteur, aucun nouvel
exécutable.

## 3. Comptes exacts

| | prévu | réalisé |
|---|---|---|
| ascendances de découverte | 12 | **12 scellées** (graines 71000–71011, 12 hachages de précurseur distincts) |
| descendants de découverte | 48 | **48 scellés**, un par cellule, **zéro candidat rejeté** |
| lignes sham de découverte | 96 | **59 acquises, 37 manquantes** |
| lignes actives de découverte | 96 | **0** |
| ascendances de hold-out | 16 | **0** |
| descendants / lignes de hold-out | 64 / 128 | **0 / 0** |

| phase | facturés | autorisés | inutilisés |
|---|---|---|---|
| construction découverte | **48** | 96 | 48 |
| shams découverte | **60** | 96 | 36 |
| actifs découverte | **0** | 96 | 96 |
| hold-out (3 phases) | **0** | 384 | 384 |
| autres / diagnostics | **0** | 0 | — |
| **total facturé** | **108** | 672 | 564 |

`TOTAL_RAW_ADVANCE_SEQUENCES = 108`. Aucune sonde de chronométrage, aucun test à blanc, aucune
continuation de diagnostic : `OTHER_STARTS = 0`.

## 4. Matérialité des lignes et contrastes de porteur

**Non évaluées.** Aucune ligne active n'a été lancée, aucun seuil TAU n'a été calculé, aucun
verrou de seuil n'existe. Il n'y a dans cet arbre **aucune quantité de réponse d'aucune sorte** :
ni `z`, ni `d`, ni `x`, ni axe, ni score, ni valeur p.

## 5. Interaction moyenne, plancher matériel, LOAO, alignement, levier, marges d'orbite

**Tous non atteints** (`NOT_REACHED_BY_PREDECLARED_STOP`). Aucun axe de découverte n'a été
sérialisé ; le hold-out n'a jamais été ouvert ; aucun état de hold-out n'a été généré.

## 6. Résidus P2 par descendant, moyennes/max/contenance par ascendance

**Non atteints** : ils portent par définition sur les 64 descendants du hold-out, qui n'existent
pas. Les deux champs hérités sont reportés **inchangés**, sans requalification :

```
FSQBT00_LEGACY_STRICT_MAX4_ALL_BLOCK_CONTAINMENT_STATUS = FAILED_AS_PREDECLARED
P2_POPULATION_TRANSFER_INTERPRETATION                   = INCONCLUSIVE_FROM_THIS_GATE_ALONE
```

## 7. Ce qui a arrêté le programme, en clair

Le pilote d'acquisition des shams a été lancé en tâche de fond **à l'intérieur d'un appel d'outil**
dont la limite est de 120 secondes. À l'expiration, l'environnement a tué tout le groupe de
processus, interrompant en vol la ligne `SHAM_1_71007_FAR_a1`. 59 des 96 lignes requises étaient
terminées et publiées.

Le registre d'écriture anticipée a fonctionné exactement comme prévu : l'enregistrement `INTENDED`
était écrit et fsynché, le marqueur `ACK` **présent**, le marqueur `ADVANCE` **présent et
fsynché**, aucun octet de sortie. Selon le contrat gelé, un marqueur `ADVANCE` présent signifie que
le démarrage est **facturé et ne peut jamais être rejoué**. Ce marqueur est écrit juste avant le
`execv` vers le worker parent committé, ce que le gel qualifie déjà de « délibérément
conservateur ». Cette prudence a été **honorée, et non réinterprétée après coup** : la
réinterpréter parce qu'elle me dessert maintenant serait exactement la lecture favorable
a posteriori que le protocole existe pour empêcher.

Le panel se ferme alors par **deux arguments indépendants, chacun suffisant** :

1. **Non-rejeu** — le descendant `71007_FAR_a1` a un jumeau manquant, et le §7.2 dit qu'un jumeau
   manquant arrête le programme avec zéro démarrage actif de découverte.
2. **Arithmétique, sans aucun jugement** — 60 démarrages sham facturés sur 96 autorisés laissent
   **36** ; il manque **37** lignes ; **37 > 36**. Le panel complet de shams jumeaux est
   **inatteignable dans le budget gelé**, quelle que soit la lecture de la règle de rejeu.

## 8. Ce que les preuves acquises établissent quand même

Les **29** descendants dont les deux jumeaux ont été acquis sont **identiques bit à bit sur tout
l'horizon** : mêmes hachages d'état à chaque temps scoré, mêmes hachages terminaux, mêmes digests
de sortie pleine, ensemble de touche vide à `t0`, checkpoint d'entrée inchangé, mêmes masques et
mêmes normalisateurs. **L'instrument de mesure s'est comporté exactement comme requis.** La perte
est une panne d'infrastructure de l'exécuteur, ni de la physique ni de l'instrument.

## 9. Déviations, octets manquants, points non résolus

Trois déviations, toutes déclarées dans `PROTOCOL_DEVIATIONS.md` :

* **D1** — lecture, avant le gel, d'une constante de seuil héritée (`TUBE_P2_LOBO`) et de trois
  diagnostics de base parents. Impact **nul** : toutes les portes et tous les seuils de FCDDH00
  sont fixés mot pour mot par l'autorisation, cette constante n'intervient que dans les résumés P2
  du hold-out qui n'a jamais été ouvert, et aucun résultat FCDDH00 n'existait au moment de la
  lecture.
* **D2** — la panne de contrôle de processus décrite au §7, facturée et non rejouée.
* **D3** — deux lignes ajoutées à `fh_close.py` pour que le champ `DISCOVERY_SHAM_STATUS`
  s'affiche depuis le manifeste brut quand aucun verrou de seuil n'existe. Correction de rendu de
  rapport, explicitement permise, sans effet sur un seul nombre.

Octets manquants : **une** ligne sham (`SHAM_1_71007_FAR_a1`). Tout le reste est préservé :
48/48 checkpoints et masques de descendants avec leurs octets complets, 59/59 lignes sham acquises
avec archives pleine résolution et compactes, hachages par temps scoré et hachages terminaux.
Aucun problème de jauge ou numérique non résolu : rien de numérique n'a été calculé.

## 10. Jugement scientifique, en français ordinaire

Il faut distinguer deux choses, et cette exécution n'en a établi ni l'une ni l'autre :

* « **les deux porteurs réagissent différemment à NEAR qu'à FAR** » — non testé ;
* « **cette différence est assez grande pour être matériellement significative et survit aux deux
  allocations neutres** » — non testé.

Ce que cette exécution a réellement produit, c'est **l'appareil** : un plan croisé à l'intérieur de
chaque ascendance, prouvé constructible sans toucher au moteur, et un panel de douze ascendances
fraîches réellement construit avec ce plan. C'est exactement le défaut de conception que FCRA00
avait laissé ouvert — la confusion entre facteur et ascendance — et il est maintenant réglé et
committé. Ce qui manque, c'est la moitié d'une phase de mesure de routine, perdue pour une raison
qui n'a rien de scientifique.

Il serait facile, et faux, de relancer la ligne perdue et de continuer comme si de rien n'était.
Le protocole l'interdit, et il a raison de l'interdire : c'est précisément la discipline qui rend
crédibles les résultats de cette chaîne. Le programme s'arrête donc proprement, avec 564
démarrages autorisés non dépensés.

---

```
GOOD_NEWS = Le croisement G1 à l'intérieur de l'ascendance est PROUVÉ et EXÉCUTÉ : douze
  ascendances fraîches (71000-71011), chacune portant les quatre cellules NEAR/FAR x H3 issues
  d'un précurseur identique octet pour octet, 48/48 descendants vérifiant found(S) = PRECURSOR(S)
  x blob(g) champ par champ, zéro candidat rejeté, 48 démarrages sur 96. La provenance est exacte
  (1392/1392 chemins identiques, main intact à f3921a4d), l'oracle de pré-exécution passe 23
  groupes non vacués, et les 29 paires de shams acquises sont identiques bit à bit sur tout
  l'horizon : l'instrument est sain. Le défaut de conception de FSQBT00 (facteur confondu avec
  l'ascendance) est corrigé et committé.

LESS_GOOD_NEWS = La phase des shams jumeaux a été tuée en vol par une limite de temps d'appel
  d'outil côté exécuteur, qui a supprimé tout le groupe de processus. La ligne
  SHAM_1_71007_FAR_a1 porte un marqueur ADVANCE fsynché : elle est donc FACTURÉE et ne peut jamais
  être rejouée. Il manque 37 lignes et il ne reste que 36 démarrages autorisés — le panel est
  inatteignable, arithmétiquement, indépendamment de toute règle de rejeu. Zéro démarrage actif,
  zéro hold-out, aucun axe, aucun chiffre scientifique. La cause n'est ni la physique ni le
  protocole : c'est moi qui ai lancé une acquisition longue dans un appel d'outil borné.

WHAT_IT_CHANGES = Rien sur le plan scientifique : aucune affirmation de FCRA00 n'est confirmée,
  infirmée ni nuancée, et les deux champs P2 hérités restent inchangés (ancienne porte stricte
  ÉCHOUÉE ; transfert de population INCONCLUSIF depuis cette porte seule). Sur le plan
  méthodologique, cela change deux choses réelles : (1) la route G1 croisée intra-ascendance
  n'est plus une hypothèse de conception, elle est prouvée, gelée et exécutée, donc le prochain
  programme part d'un plan strictement meilleur que celui de FSQBT00 ; (2) l'appareil complet —
  arithmétique certifiée par intervalles rationnels, jauge séparable par descendant, énumérateur
  exact 2^16, pare-feu de dépendances, oracle à 23 groupes non vacués, registre d'écriture
  anticipée qui a effectivement détecté et facturé sa propre perte — est écrit, audité et
  committé, et pourra être réutilisé tel quel.

NEXT_SCIENTIFIC_ELIGIBILITY = Aucun rattrapage sous l'autorisation actuelle : je ne rejoue pas la
  ligne perdue, je n'ajoute pas de blocs, je ne calcule aucun seuil sur un panel incomplet et je
  n'ouvre pas le hold-out. L'espace de noms 71000-71055 et 108 démarrages sont consommés
  définitivement. Ce qui est éligible, si et seulement si tu le réautorises explicitement, c'est
  la MÊME expérience, sans la moindre modification scientifique — mêmes estimands, mêmes portes
  D0-D11 et H0-H9, mêmes budgets, même plafond de revendication — sur un espace de noms frais
  (N >= 72000), avec un unique correctif d'ingénierie côté exécuteur déjà spécifié : lancer
  l'acquisition dans sa propre session (setsid) pour qu'aucune limite d'appel d'outil n'atteigne
  le groupe de processus, et rendre le pilote reprenable ligne par ligne AVANT que le premier
  démarrage ne soit facturé. Tant que cette réautorisation n'est pas donnée, l'hypothèse
  « direction différentielle de porteur NEAR-moins-FAR hors P2 parental » reste exactement où
  FCRA00 l'avait laissée : cohérente en interne sur le panel historique, mais jamais testée de
  façon prospective.
```
