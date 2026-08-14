# OBTC01_APPEND_ONLY_CORRECTIONS

Append-only. Aucun octet gelé d'une mission antérieure n'est modifié. Chaque entrée porte son
diagnostic, la direction de son effet, et ce qu'elle entraîne pour la disposition.

---

## D-1 — 2026-08-14 — provenance : les vingt-trois affirmations héritées sont re-vérifiées

L'artefact CSC01 fractionné a été réassemblé dans un espace neuf, sommes des trois morceaux
re-calculées, `sha256` de l'archive recomposée `bc0583e1…b29c6`, puis cloné **dans un espace de
noms réseau supprimé** (`unshare -rn` ; contrôle DNS et TCP négatifs à l'intérieur, positifs à
l'extérieur ; `GIT_NO_LAZY_FETCH=1`).

```
HEAD a84ae975e76233c88e8277bf018a06e1417d6838    arbre ef53f8d8840ed5787054feafeda32f4d1fdd3f0e
fichiers 1367   objets manquants 0   remotes promisor 0   git status --porcelain vide   fsck propre
données présentes : ORR01 20 npz + 13 sorties, CSC01 28 npz + 18 sorties
harnais rejoués : CSC01 étape A 12/12 ALL_PASS, audit adverse CSC01 18/18 PASS, ORR01 ALL_PASS
```

Vingt-trois affirmations chiffrées du rapport CSC01 ont été recalculées depuis cet état
reconstruit — HEAD, arbre, fichiers, commits, `METHODS_CORE_HASH`, `lambda`, `m*`, 0 sur 6, 6 sur
6, 0.074, 0.519, `p = 0.03125`, 0.941, 0.676, deux extinctions, le verdict de la question A, les
six rejeux bit-exacts, 20 démarrages, les intervalles de quantiles N3b, la corrélation
cœur–organisateur, la distance cœur–organisateur, et les 17 hachages de fichiers gelés.
**23 sur 23 vérifiées.**

```
PROVENANCE_STATUS = SELF_CONTAINED_SPLIT_DELIVERY_PASS
```

---

## D-2 — 2026-08-14 — le gate en flux ne recevait aucune trame spatiale

**Concerne** `protocol_obtc.py`, la fonction `run_arm`, sous
`METHODS_CORE_HASH = f81b1c7ab92d1634b816c2b2f68ccf4fe3aadee4d9495822bbc71a11b7734eb5`.

Le rappel `online.frame(fr)` était **absent** de la boucle par pas. Le gate en flux a donc
agrégé zéro trame spatiale, tandis que le gate en tableau les a toutes reçues.

**Détection.** La règle séquentielle gelée — *« online et post hoc divergent → STOP »* — s'est
déclenchée sur le **premier bras**, `P/seed8101`, et le plan s'est arrêté immédiatement. La
redondance a fonctionné exactement comme elle avait été conçue pour fonctionner.

**Direction de l'effet.** Sans trames, le gate en flux rapporte `core_exists_frac = 0`,
`frac_r80_org_ok = 0` et `frac_with_org = 0`. Il ne pouvait donc produire que des **échecs**, et
jamais un succès indu. Le défaut est conservateur dans le seul sens qui compte.

**Correction.** Le rappel manquant a été ajouté. Après correction, les deux implémentations
s'accordent champ par champ sur les trames enregistrées du bras déjà consommé.

---

## D-3 — 2026-08-14 — décalage d'un pas dans le découpage en tiers du gate en flux

**Concerne** `gate_obtc.py`, `OnlineGate.step`, même hash gelé.

L'indice de tiers était calculé sur `(t − burn)`, qui court de 1 à 9000, alors que
l'implémentation en tableau découpe un tableau indexé de 0 à 8999. Les frontières des trois tiers
différaient donc d'un pas, ce qui déplaçait les moyennes de tiers de l'ordre de `10⁻⁵` en valeur
relative.

**Direction de l'effet.** Négligeable en amplitude — mais c'est précisément le genre d'écart que
la redondance existe pour attraper, et il a été attrapé par le même arrêt. Corrigé en indexant à
partir de zéro.

---

## D-4 — 2026-08-14 — la statistique de retard codée n'était pas la bonne statistique

**Concerne** `metrics_obtc.py`, `lagged_correlation`.

La fonction corrélait les **incréments** des trajectoires déroulées du cœur et de l'organisateur.
Les incréments d'une marche aléatoire sont un bruit blanc : leur corrélation décalée n'a pas de
maximum informatif. Sur le bras consommé elle rapporte un pic à 50 pas avec `r = 0.375`, ce qui
ne veut rien dire.

**La statistique correcte**, dérivée de l'opérateur, est
`τ* = argmin_τ E|C_t − Y_{t−τ}|²`, dont la prédiction analytique est `τ* = E[S] = (1−µ)/µ = 249`
pas. Appliquée aux trames enregistrées du bras consommé, elle donne un minimum **large et plat** :
`5.70` à 100 pas, `5.20` à 150, `5.77` à 200, `7.00` à 250, contre `11.23` à `τ = 0` — cette
dernière valeur étant à comparer à la prédiction analytique `E|C−Y|² = 12.43`.

Le minimum est donc réel et au bon ordre de grandeur, mais **une seule graine ne le résout pas**.
La statistique corrigée est enregistrée ici comme la méthode à geler dans la mission successeur ;
elle n'est pas appliquée comme critère dans celle-ci.

---

## D-5 — 2026-08-14 — ce que ces défauts entraînent

Le mandat est explicite sur trois points : la règle séquentielle doit s'arrêter si les deux gates
divergent ; aucune reprise manuelle après arrêt n'est autorisée dans cette mission ; et une
correction du gate après le gel, ou un bug détecté après ouverture des résultats, entraîne
`AUDIT_INVALID`.

Les trois se sont produits. Un bras a été ouvert, un défaut a été détecté, et du code postérieur
au gel a été corrigé.

```
DISPOSITION = AUDIT_INVALID
runs poursuivis sous le gate corrigé = AUCUN
graines consommées et désormais brûlées = 8101
familles de graines à ne plus utiliser en confirmation = 8101-8106, 8201-8203, 8301-8303,
                                                          8401-8402, 8501-8503
```

Le contenu **analytique** de la mission n'est pas invalidé par cette disposition : la dérivation
de l'opérateur, ses prédictions sans paramètre, le certificat de satisfiabilité, l'audit des
métriques et les quatre nuls sont produits en mode statique ou génératif et ne consomment aucun
démarrage. Seule la **confirmation** est nulle.
