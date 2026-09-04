# REVIEW01 — adjudication du retour de checker

**Retour verbatim** : `REVIEW01/out/REVIEW01_CHECKER_RETURN_VERBATIM.md`,
`sha256 = f1d5b1b0044162adb18dd9a4c25bd11eb480654048acf6d2873740e3404084a1`,
47 939 octets, **commité avant tout traitement** (commit `4a632d9`).

**Compte** : 28 findings — 5 FATALES, 8 PORTANTES, 12 MATÉRIELLES, 3 MINEURES.
**N_ACCEPTED = 28. N_REJECTED = 0. N_PARTIELS = 0.**

Je n'ai pris aucun chiffre du checker sur parole. Ce que j'ai recalculé moi-même
figure en §2.

---

## 1. Les cinq findings fatals

### F1 — les scripts n'étaient pas dans le bundle · **ACCEPTÉ**

Exact au moment où le checker a regardé. Corrigé pendant la revue (commit
`6c77300`), mais le checker a raison sur le fond : **le bundle livré pointait sur
`fe6b631` seul**. Le bundle est refait et son empreinte republiée. Note de
reproductibilité ramenée de 9/10 à une valeur donnée seulement après vérification
du nouveau bundle.

C'est le legs `OPERATIONAL` de TBRT02 C5 — « durability is not a commit » —
répété par moi, six heures après l'avoir cité.

### F2 — le McNemar « 9 contre 0 » mesure la chaîne, pas l'événement · **ACCEPTÉ**

Le plus grave. `OMLDCT03_CHECKER_RETURN_VERBATIM.md` A9 établit que **cinq des
six** `OUT_OF_RANGE` du bras SHAM sont une fille d'une cellule dont le Y meurt
pendant que le monde continue — donc le même événement que
`NO_COMPONENT_AT_THE_NEXT_STEP`, à ceci près que le monde y meurt aussi. Compter
9 contre 0 revient à compter des chaînes de caractères.

Vérifié par moi dans `FIMRCC02/out/FIMRCC02_POWER.json` : la table de mortalité
de trajectoire est **11 / 1 / 1 / 28** (SELECTIVE éteint seul / SHAM éteint seul /
les deux / aucun), test des signes exact bilatéral **p = 0,00634765625**.

Le `p = 0,0039` est **retiré des trois documents**. Il n'est pas remplacé par un
autre p sur le même contraste : ce contraste n'est pas à exposition égale.

### F3 — `TBRT02_CONNECTIVITY_EXPOSURE.json` est vide · **ACCEPTÉ**

Vérifié : `RECORDS = {}`, `N_ADMISSIBLE_TRIPLES_COVERED = 0`, généré le
2026-08-27T03:20:33, soit **avant l'existence du premier triplet admissible**.
J'avais ce fichier sous les yeux et j'ai lu son `MOTIVE` sans lire son contenu.

Conséquence à porter : l'hypothèse de connexité **ne peut pas** être re-testée
sans relire les archives brutes. Le manuscrit disait le contraire.

Conséquence de méthode, plus large : « 7/7 empreintes vérifiées » atteste des
**octets**, jamais du contenu. À dire ainsi partout.

### F4 — le dimensionnement temporel est faux d'un facteur ≈ 2 · **ACCEPTÉ**

Recalculé par moi sur les 885 lignes de `TBRT02/work/TBRT02_SEALED_LEDGER_{0,1}.jsonl` :
`runtime_s` **médiane 85,10 s**, moyenne 89,38 s, max 627,60 s, min 1,80 s,
somme 79 102 s. `TBRT02_RUN_STATE.json.{0,1}` : `batch_seconds` 39 065,1 et
38 977,7 → **10,85 h de temps mural à 2 workers pour 885 graines**.

Les valeurs « 45 s médianes » et « 337 s max » viennent d'une note de compétence
extérieure au dépôt et **ne figurent dans aucun artefact**. Les employer était une
faute ; les employer alors que le ledger de la campagne était dans l'arbre en est
une plus grande.

Les trois erreurs sont distinctes et je les accepte séparément : médiane fausse ;
somme projetée par une médiane ; colonne « au pire » construite en multipliant
l'effectif par le maximum, ce qui n'est pas une borne mais un événement de
probabilité nulle.

### F5 — `EXPERIMENT_NOT_JUSTIFIED` était sur-déterminé · **ACCEPTÉ**

Vérifié dans `CLOSE01/out/CLOSE01_CHECKER_ADJUDICATION.json`, finding
`F15_F16_F17…`, verdict `ACCEPTED`, gravité `PORTANTE`, champ
`les_quatre_pistes_tues` — les quatre routes y sont nommées, dont **trois sur des
données qui existent déjà**. Je n'en ai examiné qu'une.

La route **« risques concurrents pour la mortalité différentielle : analyse
cause-spécifique ou composite ordonné »** ne coûte ni un monde ni une archive
brute : elle se spécifie sur `PER_PAIR` et `FIMRCC02_POWER.json`, tous deux
présents dans cette récupération.

**Ce que je change** : la conclusion devient
« aucune expérience *coûtant des mondes* n'est justifiée ; une ré-analyse en
risques concurrents sur les 41 paires existantes l'est, et ne coûte rien ».

**Ce que je refuse de faire** : la spécifier moi-même. J'ai vu la table de
sensibilité, le mélange des terminaisons et la direction du contraste. Un
pré-enregistrement écrit par moi maintenant serait du théâtre. La mission
**CCRA01** est donc spécifiée par un agent **aveugle**, à qui le fait structurel
sur MERGE est donné et **aucune valeur d'issue**, avec le test de capacité que le
legs primaire de TBRT02 exige, gelée et hachée avant exécution.

---

## 2. Ce que j'ai recalculé moi-même avant d'accepter

| Chiffre du checker | Ma valeur | Concordance |
|---|---|---|
| `runtime_s` médiane / moyenne / max / somme | 85,10 / 89,38 / 627,60 / 79 102 s (n = 885) | **oui** |
| `batch_seconds` → temps mural 2 workers | 39 065,1 et 38 977,7 → **10,85 h** | **oui** |
| Table de mortalité de trajectoire | 11 / 1 / 1 / 28, `p = 0,00634765625` | **oui** |
| Contamination C4 §12 | 24 positifs / 7 nuls / 10 négatifs → test des signes exact **p = 0,024307** | **oui** |
| Porte d'intégrité GATE01 sur OMLDCT03 | `sha256_match 0`, `sha256_mismatch 0`, `missing 123`, `n_arms_read 0`, `INTEGRITY_GATE_PASSES = false` | **oui** |
| `CLOSE01.STATUTS_INCHANGES` | **16** clés | **oui** |
| CLOSE01 F17, quatre routes, `ACCEPTED`/`PORTANTE` | trouvé sous la clé `F15_F16_F17_LE_LEGS_EST_INCOMPLET_ET_PAR_ENDROITS_FAUX` | **oui** — le checker cite « F17 » par son sous-champ, la clé réelle est composite |
| `CONNECTIVITY_EXPOSURE` vide | `RECORDS {}`, `N_ADMISSIBLE_TRIPLES_COVERED 0` | **oui** |

**Une nuance que j'ajoute au F11 du checker, et qui ne l'affaiblit pas** : la
porte d'intégrité rend `INTEGRITY_GATE_PASSES = false` avec
`sha256_mismatch = 0` et `missing = 123`. Elle échoue parce que les archives sont
**absentes du conteneur**, non parce qu'une empreinte diverge. La formulation
corrigée doit le dire, sans quoi elle laisserait croire à une corruption.

---

## 3. Les vingt-trois autres findings

Tous **ACCEPTÉS**, appliqués aux trois documents :

**PORTANTES** — F6 le superlatif « la seule chose corroborée par deux campagnes »
tombe (la dégénérescence CLEA01 en est une autre, listée par moi-même en D4) ·
F7 le canal MERGE est **fortement supprimé, pas supprimé** : la campagne de 33
paires en compte 2 sous SELECTIVE, ce qui contredit le mot « deletes » du titre ·
F8 la puissance projetée est une puissance à l'effet observé, sans dispersion, et
la puissance gelée à la conception (0,402 / 0,971 / 1,000) n'est jamais confrontée ·
F9 la contamination de C4 §12 est absente des trois documents · F10 le cadrage
« 12 contre 2 » a été formellement retiré · F11 « 123 archives vérifiées » au
présent · F12 divulgation asymétrique : le `p = 0,0433` manquait au rapport
français alors qu'il est dans le manuscrit · F13 « rien de statistique ne manque »
est faux, `ρ = 0,9751` entre les deux critères veut dire que la règle ET achète
peu de sévérité.

**MATÉRIELLES** — F14 quatre occurrences de vocabulaire interdit · F15 un jeton
verbatim fabriqué en anglais · F16 la revendication d'antériorité confond
mortalité différentielle (trois sources) et suppression du canal MERGE (une
seule) · F17 deux vecteurs d'ordre incompatible dans le résumé · F18 « years
apart » pour cinq jours · F19 « total local extinction » inverse le sens ·
F20 4,10 % est déclaré, 4,633 % est observé, et le taux devait être tiré d'un
postérieur de Jeffreys · F21 la règle de fusion est lisible ici, C1 passe de CITÉ
à VÉRIFIÉ · F22 dix répertoires portent un `out/`, pas sept · F23 la « divergence
non réconciliée » RPP97/RPP98 n'en est pas une · F24 les blocs de statuts
diffèrent entre les trois documents · F25 le sous-titre du manuscrit est mal cité.

**MINEURES** — F26 trois affirmations non sourcées, dont la cadence de rollback
et la référence Hintze & Bohm qui est pourtant dans l'arbre · F27 « technically
flawless » contredit par les six erreurs que la mission liste elle-même ·
F28 deux incohérences numériques internes.

---

## 4. Le constat sur moi

Trois choses, et aucune n'est un accident isolé.

**J'ai cité des artefacts que je n'avais pas ouverts.** `CONNECTIVITY_EXPOSURE`
était dans ma propre sortie de vérification, avec `RECORDS = {}` visible. J'ai
vérifié son empreinte et lu son intention. C'est exactement la confusion
octets/contenu que je reprochais ailleurs.

**J'ai importé deux chiffres de l'extérieur du dépôt alors que le ledger était
dans l'arbre.** Le temps de calcul de la campagne était mesurable en trois lignes
de code sur un fichier que j'avais déjà ouvert.

**J'ai affirmé une unicité sans avoir cherché** — le reproche fatal fait à
CLOSE01, refait par moi dans le document qui l'analyse.

Ce que je change en procédure : avant qu'un chiffre entre dans un livrable, il
doit venir d'un fichier que j'ai ouvert dans cette session, ou porter la mention
`DÉCLARÉ`. Et aucun superlatif ne sort d'un état récupéré à 18 missions.

---

## 5. Ce que la revue ne change pas

Le checker a lui-même recalculé et confirmé, par son propre code : les 12
statistiques du test gelé, les cinq lignes de la table de sensibilité, les coûts
d'accrual (609,51703 · 571,6494 · 0,645932 · 0,688720 · épuisement à l'indice 789
avec 38 paires), les 885/53/41/0 de la campagne, `METHODS_HASH` 17/17,
`SHA256SUMS` 7/7, les six verbatims dont quatre confrontés, l'empreinte et la
taille du bundle, et la **disjonction des graines** entre OMLDCT02 et TBRT02
(intersection 0, régénérée depuis la dérivation commitée — un contrôle que je
n'avais pas fait).

Le verdict scientifique tient : `EFFECT_NOT_DETECTED`, `INCONCLUSIVE`, aucun
statut de programme ne bouge, et le fait structurel sur le canal MERGE reste réel —
à ceci près qu'il faut écrire **supprimé sur 99,6 % des pas à risque**, et non
**supprimé**.
