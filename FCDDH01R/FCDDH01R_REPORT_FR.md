# FCDDH01R — rapport final (français)

`FRESH_CROSSED_DIFFERENTIAL_DISCOVERY_HOLDOUT_01R`
Branche `dev/fresh-crossed-differential-discovery-holdout-01r`, enfant append-only de
`93f13f45e6b6550a7ff709768b7b574161ed6a4f`. Base de clôture : `ffbda326…` (C7).

## En un paragraphe

L'analyse découverte a bien été calculée sur douze ascendances fraîches et croisées. Le motif
candidat est numériquement identifiable et très stable lorsqu'on retire une ascendance, mais **D4,
D5 et D8 échouent** : aucun axe n'est licencié et le hold-out n'a jamais été ouvert. Le calcul est
mécaniquement vérifié, mais la campagne est **non conforme au protocole**, car le contrat
exécuteur/DEX gelé a été réparé après 48 démarrages facturés.

```
DISCOVERY_ANALYSIS_COMPUTED__AXIS_NOT_LICENSED_D4_D5_D8__ZERO_HOLDOUT_STARTS__PROTOCOL_NONCONFORMANT_POSTSTART_EXECUTOR_REPAIR
```

## 1. Chaîne de commits

| rôle | commit | UTC |
|---|---|---|
| parent FCDDH00 | `93f13f45e6b6550a7ff709768b7b574161ed6a4f` | 05:06:33 |
| C1 réautorisation + gel maître | `e77ef550a04cbf90ba2f90e5083719913bc005a4` | 13:09:10 |
| C2 espace de noms, rôles, randomisation | `1936efde316672f3950d249427aec5cb6c6d44b4` | 13:09:13 |
| C3 exécuteur durable, DEX0–16, Q0A–Q0W | `7dd098ea779ddbc241414fb3d7cad8d0d42279b8` | 13:09:28 |
| C4 panel découverte scellé | `b52b1eae820c69be601eaee7d7fa0d4d827eb463` | 13:24:01 |
| C5 réparation exécuteur post-construction | `2b152a2ad4f6abf4dc2c932fabff61a368fe1eed` | 13:43:27 |
| C6 verrou de seuils | `fc1b41f87cadcc94407e5ca70d0fb43a7fcbc968` | 13:51:52 |
| C7 verrou brut opaque actif | `ffbda326703f93aa5a34c03e5f259e976771f793` | 14:00:20 |

Chaîne linéaire, sans fusion. L'ordre annoncé `b52b1eae → 2b152a2a → fc1b41f8 → ffbda326` est
**vérifié sur les objets exacts**. `main` = `f3921a4d…`, inchangé, jamais extrait
(`CLOSURE_COPY_MAIN_STATUS = EXACT_MATCH`). Environnement antérieur : `NOT_OBSERVED`.
`REMOTE_REPOSITORY_SCOPE = NONE`.

## 2. Comptabilité des démarrages

| phase | démarrages facturés | séquences d'avance brute |
|---|---|---|
| construction découverte | 48 | 48 |
| sham découverte | 96 | 96 |
| actif découverte | 96 | 96 |
| hold-out (les trois) | 0 | 0 |
| autre / diagnostic / smoke / préflight | 0 | 0 |
| **total FCDDH01R** | **240** | **240** |

Maximum enfant 672 → **432 démarrages inutilisés**, clos et non transférables.
FCDDH00 historique : **108** (48 construction + 59 lignes sham complètes + 1 ligne sham facturée
interrompue). **Cumul de lignée : 348** sur un maximum de 780. Les trois comptes restent séparés.

Sur la formule « 59/96 » : 59 lignes sham **achevées et publiées** ; une 60ᵉ **lancée et facturée**.
Les deux énoncés sont vrais de quantités différentes ; la clôture FCDDH00 enregistrait déjà 60
facturées pour 59 achevées. **Aucune correction append-only n'est requise.**

## 3. Les deux réparations, distinctes

**Avant le premier démarrage — autorisée.** DEX13 a exposé un vrai défaut d'exactly-once : les
wrappers concurrents se disputaient le fichier *temporaire* du `START_GATE`, pas seulement sa
publication exclusive. Le temporaire est désormais unique par prétendant ; huit wrappers simultanés
pour un `RUN_ID` donnent exactement un gagnant et exactement une facturation.

**Après le premier démarrage facturé — non autorisée.** Les vraies lignes à deux sorties ont exposé
le défaut d'état terminal de publication. Le remède est arrivé en C5, **après 48 démarrages
facturés**. Voir §6.

## 4. Panel et complétude

12 ascendances indépendantes (73000–73011), 4 descendants chacune = 48, croisement factoriel complet
intra-ascendance {NEAR, FAR} × {membre H3 0, 1} depuis **un précurseur octet-identique par quatuor**,
12 précurseurs distincts (multiplicité max 1), identité des masques 48/48, un seul blob NEAR et un
seul blob FAR globaux, 390 pas moteur uniformes par ligne de construction, 0 rejet. Vérification du
panel : **15/15 PASS**.

* 48 lignes de construction, 96 lignes sham, 96 lignes actives complètes, scellées, publiées, vérifiées
* jumeaux sham **48/48** bit-identiques sur **tout l'horizon** (hash terminal, hashs par temps, ensemble de touches ; 11 temps notés)
* 48 `TAU` positifs et finis, reproduits indépendamment ; plage `[7,055948e-04 ; 1,264019e-03]`
* **aucune ligne facturée incomplète** ; **aucun rejeu, remplacement ni recouvrement idempotent**
* le verrou de seuils `fc1b41f8…` (13:51:52Z) précède toute ligne active (première porte 13:52:06Z)
* le verrou brut opaque `ffbda326…` (14:00:20Z) précède le premier décodage de réponse cible (14:01:00Z)
* **zéro** octet, verrou, objet d'axe, ligne, score ou accès numérique hold-out
* aucun octet scientifique de la série 71000 n'est entré dans le panel

## 5. Audit publication génération 1 / génération 2

| | construction | sham | actif |
|---|---|---|---|
| lignes | 48 | 96 | 96 |
| enregistrements WAL | 624 | 1056 | 1056 |
| par ligne | 13 | 11 | 11 |
| `VERIFIED` | 144 | 96 | 96 |
| alertes de monotonie | 48 | 0 | 0 |
| génération du contrat | 1 | 2 | 2 |

La génération 1 émettait l'état terminal `VERIFIED` une fois **par sortie déclarée** ; les lignes de
construction en déclarent deux. Les deux sorties ont bien été scellées et publiées pour chaque
ligne, aucun recouvrement n'est intervenu entre elles, aucune ligne n'a été sautée ni dupliquée, et
les octets de masque répétés ont été correctement distingués des octets de précurseur distincts.

**Conclusion : une faiblesse latente de recouvrement, sans corruption brute observée** — ni
corruption de données prouvée, ni implémentation conforme anodine.

## 6. Conformité protocolaire

```
PROTOCOL_CONFORMITY_STATUS       = NONCONFORMANT
PRIMARY_DEVIATION                = POST_FIRST_BILLED_START_EXECUTOR_PUBLICATION_CONTRACT_CHANGE
VIOLATED_RULES                   = SECTION_4_SOURCE_FREEZE_AND_STRICT_STOPS_5_AND_OR_11
POST_STOP_SHAM_AND_ACTIVE_STARTS = 192
RETROACTIVE_REPAIR_STATUS        = NOT_POSSIBLE
```

Le §6 du gel maître fait de l'exécution durable une **porte scientifique** ; le §7 interdit en
arrêt 5 que DEX ou Q0A–Q0W soient « *réparés après le premier démarrage facturé* » et en arrêt 11
les « *changements post-premier-démarrage de la source gelée, de la configuration, des files, des
plannings ou des gabarits de commande* ». **Les deux sont déclenchés sur leur texte littéral.**
L'arrêt 5 n'a pas besoin de la réserve « DEX0–DEX16 restent PASS » : sa formulation porte sur la
*réparation*, pas sur l'échec.

Diff exact C4→C5 : 827 fichiers de preuve DEX génération 2 ajoutés, 1 enregistrement de supersession
ajouté, 4 modules d'ingénierie/test modifiés, 1 rapport de préflight, 1 document de delta.
**Zéro chemin scientifique.** Aucune équation, aucun runner scientifique, aucune définition de
porteur, aucun lecteur, masque, horizon, poids, randomisation, planning de lignes, checkpoint, seuil
ni analyseur n'a changé. Le `run_id` ne dépend pas du hash du code exécuteur.

Deux jugements séparés : **prospectivement**, ce n'est pas une expérience préenregistrée propre — le
programme aurait dû s'arrêter après la construction ; **mécaniquement**, les dépendances, la
randomisation, les sorties brutes, les verrous et les analyseurs sont restés identiques, donc le
panel supporte un **calcul descriptif déterministe**.

## 7. Échelle de portes D0–D11

| porte | verdict | règle | observé |
|---|---|---|---|
| D0 | PASS | ancre structurelle | vrai par construction |
| D1 | PASS | matérialité de cellule sur chaque ligne | 96/96 |
| D2 | **PASS** | contraste porteur direct `‖z₂−z₁‖² > 4·TAU²` | **48/48** |
| D3 | PASS | `‖X̄_D‖` certifié > 0 | enclos strictement positif |
| D4 | **FAIL** | matérialité absolue face à `A_X̄` | échec strict certifié |
| D5 | **FAIL** | `Σ_b J[b; v_D[−b]] ≥ 10/12` | **0 sur 12** |
| D6 | PASS | `min_b alignement²(v_D, v_D[−b]) ≥ 0,80` | 0,9992776839495647 |
| D7 | PASS | levier projeté max < 0,50 | 0,1386169981190795 (73008) |
| D8 | **FAIL** | signe de suppression **et** marge matérielle | signe 12/12, marge 0/12 |
| D9 | PASS | invariance d'échange d'allocation + orbites co-optimales | 12/12, 0 co-optimal (plafond 12) |
| D10 | PASS | production contre référence indépendante | 96/96 M₂², 96/96 jauge, 48/48 TAU |
| D11 | PASS | audit de dépendances du trainer + racine pare-feu | imports interdits = [] |

`DISCOVERY_AXIS_SERIALIZATION_STATUS = NOT_LICENSED__FAILED_GATES=D4,D5,D8`
`HOLDOUT_STATUS = NOT_REACHED_BY_PREDECLARED_STOP`

## 8. Les chiffres

```
‖X̄_D‖              = 5,695567518165154e-04   (enclos certifié, largeur 2⁻²⁰⁰)
A_X̄[DISCOVERY]     = 2,924046708945949e-03   (enclos certifié)
rapport             = 0,194783739
plancher / signal   = 5,133899
rapport d'énergie   = 0,037940705
alignement² min     = 0,9992776839495647      (LOAO, 12 plis)
levier max          = 0,1386169981190795      (ascendance 73008)
compte D5           = 0 sur 12                (critère prédéclaré 10/12)
```

L'amplitude vaut environ **19,5 %** du plancher opérationnel hérité ; le plancher vaut environ
**5,13×** le signal ; l'énergie vaut environ **0,03794** de l'énergie du plancher. **L'effet n'est
pas décrit comme exactement nul.**

**D4 est un échec strict certifié, pas UNRESOLVED** : `sup(‖X̄_D‖) < inf(A_X̄)`, les intervalles
certifiés sont disjoints et serrés à un ulp près.

**Correction.** `alignement² min` ne doit pas être annoncé « ≥ 0,999278 » : la valeur exacte
`0,9992776839495647` lui est inférieure de 3,16e-07. L'énoncé certifié correct est **≥ 0,999277**.
Aucune porte n'en dépend (seuil D6 = 0,80).

## 9. Anatomie D5 et D8

Les deux échouent sur la **matérialité de réponse**, pas sur le **signe**.

* Les 48 scores d'appariement sur l'axe complet sont strictement positifs : **0 inversion de signe**.
* Les 48 marges matérielles `p − A_PAIR` sont négatives : **48/48 en échec**.
* D5 : les 12 scores signés de l'ascendance omise sont positifs sur leur propre axe de pli ; toutes
  les marges du pire couple sont négatives ; `Σ_b J = 0`.
* D8 clause 1 (moyenne de suppression signée > 0) : **12/12 PASS**, borne inférieure min `5,538464e-04`.
* D8 clause 2 (marge matérielle moyenne du pire couple > 0) : **0/12**, marges dans
  `[−2,654179e-03 ; −2,611160e-03]`.
* Orbites de jauge co-optimales : **0** (plafond 12). Invariance d'échange d'allocation : 12/12.
  Accord production/référence : `rel 1e-9 / abs 1e-30`.
* Aucun intervalle non résolu.

**L'échec de D5 seul n'établit pas une fragilité d'allocation** : ici les signes ne s'inversent pas,
seules les marges matérielles échouent. L'orbite est stable et sous-matérielle.

**D4, D5 et D8 ne sont pas trois résultats négatifs indépendants** : ils réutilisent les mêmes bornes
héritées propagées par TAU et sont trois vues d'un seul fait — l'amplitude d'interaction est sous son
plancher opérationnel hérité.

Le critère prédéclaré `10/12` de D5 est un **garde-fou de stabilité interne**, pas une p-value ni un
résultat de population.

## 10. Pourquoi la stabilité LOAO n'est pas une réplication

Les douze plis partagent **onze ascendances sur douze** avec l'ajustement complet et entre eux. Un
`alignement² ≈ 0,99928` dit que l'estimateur ne bascule pas quand on retire une ascendance : c'est
de la **stabilité interne d'estimateur**, ni une réplication indépendante, ni un résultat de
hold-out. Un levier maximal de `0,1386` dit qu'aucune ascendance ne domine l'estimation projetée ;
il n'établit aucune matérialité.

## 11. Formulation la plus forte soutenue

> Sur 48 descendants nichés dans douze ascendances indépendantes, le contraste porteur direct
> satisfait mécaniquement sa porte de matérialité héritée, tandis que sa modulation NEAR-contre-FAR
> produit un motif de découverte numériquement identifiable et intérieurement stable, mais
> sous-matériel. Comme le contrat exécuteur a changé après des démarrages facturés, il s'agit d'un
> résultat descriptif déterministe, non d'une confirmation prospective propre. Il ne franchit pas les
> portes héritées de matérialité et de pire couple ; aucun axe scientifique n'est licencié et aucune
> validation hold-out indépendante n'a eu lieu.

Non soutenu : que l'axe se soit répliqué ; qu'une direction de population soit prouvée ; qu'il
s'agisse d'un négatif préenregistré propre ; qu'aucune interaction physique n'existe ; qu'une
seconde dimension matérielle ait été trouvée. Aucune revendication de population, de transfert
causal, d'individualité, de vie, de mémoire ou d'agentivité n'en découle.

## 12. Axe et hold-out

Aucun objet d'axe officiel n'a été créé. Tout vecteur diagnostique figurant dans un rapport de porte
(`v_D`, `v_fold`) est un **calcul de découverte non licencié** et n'est pas exposé via le chargeur
ni le chemin canonique d'axe. Zéro démarrage hold-out est le résultat **correct** de l'arrêt
prédéclaré : l'axe n'a jamais été licencié, il n'y avait donc rien à valider, et ouvrir le hold-out
aurait brûlé des ascendances irremplaçables contre une direction non licenciée.

## 13. Champs de protocole reportés

```
FCDDH01R_NO_LOOK_RETRY_LICENSE = PASS      (0 regard sur la réponse cible, 0 test confirmatoire,
                                            0 alpha dépensé dans FCDDH00 ; 341 chemins parents énumérés)
FCDDH01R_RANDOMIZATION_LICENSE = NOT_REBUILT_AT_CLOSURE__NO_CONSUMER
ESPACE_DE_NOMS                 = N = 73000 ; découverte 73000–73023 (12 utilisées),
                                 hold-out 73024–73055 (0 utilisée). 72000 rejeté.
IDENTITÉ_PARENT                = 1392 / 1392 chemins octet-identiques, 0 écart
VALEURS_PARENT_ANNONCÉES       = toutes vérifiées SAUF le SHA-256 d'autorisation FCDDH00
```

## 14. Preuves DEX existantes (aucun nouveau test)

Campagne génération 2 : **20/20 PASS**, `REAL_ENGINE_CONSTRUCTOR_COUNT = 0`,
`REAL_ENGINE_ADVANCE_COUNT = 0`, 0 démarrage facturé, worker factice sans moteur. DEX17, DEX18,
DEX19 PASS. `Q0A–Q0W` **23/23 PASS**, non vacuous, 0 démarrage moteur, les 11 contrôles négatifs se
déclenchent. DEX0 : le gabarit de lancement a conservé PID, identité de démarrage et heartbeat à
travers une expiration délibérée à la même frontière de 120 secondes qui avait tué FCDDH00.

Ces preuves montrent que la réparation génération 2 **fonctionne**. Elles ne peuvent ni satisfaire
rétroactivement la porte d'ingénierie d'avant démarrage, ni restaurer la conformité.

## 15. Artefacts manquants ou inéligibles

* `FCDDH01R_RANDOMIZATION_LICENSE` — `NOT_REBUILT_AT_CLOSURE__NO_CONSUMER`
* objet d'axe officiel — `NOT_GENERATED_BY_PREDECLARED_STOP`
* tout livrable hold-out — `NOT_GENERATED_BY_PREDECLARED_STOP`
* décomposition par couple sur axe de pli — `PERSISTED_AS_SUMMARY_ONLY`
* `HANDOFF_FCDDH01R_FINAL_RECORD_REVIEW.md` — absent de l'espace de travail ; empreinte annoncée non
  vérifiable et non revendiquée comme vérifiée

Inventaire complet : `FCDDH01R_PROTOCOL_DEVIATIONS.md` (D-1 … D-11).

## 16. Éligibilité future (descriptif — ne lance rien)

L'interaction `NEAR−FAR × porteur`, à support fixe et moyennée sur l'allocation, échoue à sa porte de
matérialité héritée. Cela **n'annule pas** le contraste porteur direct qui passe séparément (D2,
48/48). Ajouter des blocs ne répare pas automatiquement un critère d'effet minimal moyenné. Aucun
relancement immédiat, changement de dose, troisième porteur, axe alternatif ni changement de seuil
n'en découle.

Deux choses pourraient devenir éligibles sous une **tâche future distincte** : une anatomie
zéro-simulation de la règle `A_X` existante, et/ou un audit exploratoire plein champ verrouillé
séparément avant analyse. Un audit de `A_X` devrait d'abord le classer comme critère d'effet
minimal, enveloppe d'incertitude, borne opérationnelle mixte, ou non résolu — des jumeaux sham
exacts ne réduisent pas un critère d'effet minimal à zéro, et une propagation d'erreur conjointe plus
fine serait purement méthodologique. Un audit plein champ futur exigerait un estimand physique
primaire gelé, des temps et poids fixes, un seuil aveugle à l'actif, et un contrôle de multiplicité
si plusieurs critères étaient inévitables. **Aucun audit futur ne peut reclasser FCDDH01R**, et toute
revendication positive exigerait une validation prospective fraîche. Un estimand de population P2
calibré au niveau ascendance reste une question scientifique orthogonale, hors de ce dossier.
