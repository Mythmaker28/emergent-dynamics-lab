# `WSCCRP00` — spécification du point de mesure continu, et son inéligibilité

## Le lecteur hérité, rendu exécutable et haché

Hérité **exactement** de `WSCPL00/wscpl_probe_responsive.py`
(sha256 `207fa600c6fb220bb846c8fdae2cfb096d054a4fd9528a14fc75d4468d66bbd3`), sans aucun choix :

| élément | valeur héritée |
|---|---|
| champ de masse sommé | `st.rho` sur les cellules renvoyées par `domc_core.read_sites` |
| appartenance | **redétection dynamique** à chaque temps scoré par le détecteur gelé (seuil 0,30, min 12 cellules) — **pas** des masques `t0` immuables |
| persistance d'identité | affectation à l'entité la plus proche du site gelé, à l'intérieur de `read_sites` |
| bord | réseau périodique 64×64 |
| temps d'intervention | point de contrôle fondateur, pas 390 |
| `h = 0` inclus ? | **non** |
| scission / fusion / disparition | unité indéfinie et étage `NOT_IDENTIFIABLE` ; aucune imputation |
| grille `H` | `{40, 80, …, 400}` pas natifs → temps physiques `4,0 … 40,0` |
| horizon terminal | **400**, vérifié contre le gel parent : conforme au rapport |

## Le point de mesure

```
D(x) = m_A(x) − m_B(x) ;  S(x) = m_A(x) + m_B(x) ;  a(x) = |D(x)| / S(x)
r[b,u,h] = a(F^h(INT_u(x_b))) − a(F^h(SHAM(x_b))) ,  h ∈ H
```

Quadrature trapézoïdale en **temps physique**, normalisée à `Σ w_h = 1`, indépendante de la
cadence de journalisation. `ETA_ORACLE = 1e-12` (le rejeu est bit-exact ; c'est un plancher).

Portée volontairement limitée, comme exigé :

```
WINNER_IDENTITY_IS_OUTSIDE_PRIMARY_ENDPOINT       = true
TOTAL_COMPONENT_MASS_IS_OUTSIDE_PRIMARY_ENDPOINT  = true
EQUAL_MAGNITUDE_BRANCH_REVERSAL_CAN_BE_INVISIBLE  = true
```

## Le contrôle d'éligibilité, et son échec

Le détecteur gelé **redétecte par seuil**. `r` est donc un point de mesure fonctionnel à valeurs
réelles, **pas** une application mathématiquement continue. La Section 4 impose de séparer la
contribution du **changement de valeur de champ** de celle du **changement d'appartenance**, et
d'arrêter si les sauts d'appartenance dominent — définis comme plus de 50 % de l'énergie de
réponse pondérée par la quadrature.

Décomposition exécutée : `r_dyn` avec le lecteur gelé, `r_fix` avec les masques `t0` figés.

```
fraction d'énergie attribuable à l'appartenance
   = Σ_h w_h (r_dyn − r_fix)² / Σ_h w_h r_dyn²

médiane = 0,988      maximum = 1,228      seuil d'inéligibilité = 0,50
```

**La porte se déclenche, et très largement.**

### Le détail qui compte

La réponse à masques figés n'est **pas** petite : `A_fix / A_dyn` vaut 0,42 à 1,22, médiane
**0,73**, et elle dépasse `ETA_b` dans **16 unités sur 16**. Il y a donc bien une réponse de
champ réelle.

Mais les deux lectures sont **essentiellement décorrélées en forme** : `corr(r_dyn, r_fix)` va de
−0,77 à +0,56, médiane **−0,039**. Elles sont presque orthogonales — c'est pourquoi l'énergie de
leur différence égale celle de la réponse dynamique elle-même, et la dépasse parfois.

Autrement dit : la réponse que le lecteur gelé mesure et la réponse de champ à support figé sont
**deux objets différents**, pas deux mesures du même. Environ 99 % de l'énergie de réponse du
lecteur gelé provient de la **réaffectation d'appartenance par le seuil 0,30**, pas d'une réponse
lisse du champ. L'appeler géométrie serait exactement l'erreur que la Section 4 interdit.

### Ce que je n'ai pas fait

Je n'ai **pas** basculé sur le lecteur à masques figés, qui aurait donné une réponse de champ
au-dessus du bruit dans 16 unités sur 16. La Section 4 est explicite : *« n'arbitrez pas entre
ces options ici : héritez exactement la règle exécutable de WSCPL00 »*. Les artefacts parents la
déterminent **de façon unique** (redétection dynamique). Changer de lecteur serait définir un
nouveau point de mesure après avoir vu le résultat.
