"""PMCR01 — the two long-form deliverables, written from the machine-readable evidence."""
from __future__ import annotations

import json
import math

OUT = "/home/claude/PMCR01/out"


def operator_md():
    op = json.load(open(f"{OUT}/_operator.json"))
    rg = json.load(open(f"{OUT}/PMCR01_REACHABILITY_REGIONS.json"))
    adm = op["ADMISSIBLE_STATES"]
    ker = op["EXACT_KERNEL_CONSTANTS"]
    ver = op["EXACT_ONE_STEP_OFFSPRING_LAW"]["SCHEDULER_VERIFICATION"]
    m = ["# PMCR01 — dérivation de l'opérateur discret exact de la lignée `Y`", "",
         "> Rien n'est ajusté et rien n'est simulé. La loi est **écrite depuis le chemin de",
         "> code**, puis **vérifiée contre les arguments que l'ordonnanceur passe réellement**",
         "> à `binomial`, capturés au point d'usage. `rng.binomial(n, p)` *est* la loi",
         "> binomiale : prouver les arguments prouve la loi, sans aucun échantillonnage.", "",
         "## 1. L'invariant d'occupation, fait porteur de catégorie A", "",
         "```",
         "_diffuse  accepte min(movers, dest_free)          -> ne peut pas dépasser CAP",
         "_react    convertit SY -> Y et SX -> X            -> occupation conservée",
         "_decay    convertit Y -> WY et X -> WX            -> occupation conservée",
         "_exchange retire exactement ce qu'il insère       -> occupation conservée",
         "```", "",
         "Donc, en **toute** cellule et à **tout** pas :",
         "`nX + nY + nSX + nSY + nWX + nWY ≤ CAP = 16`. C'est un fait de LawSpec, connu avant",
         "tout run, et c'est la seule chose que la catégorie A sait de l'environnement de `Y`.",
         "",
         "## 2. Ordre intra-pas, transcrit et non supposé", "",
         "```"]
    for c in json.load(open(f"{OUT}/_gate0_static.json"))["SCHEDULER_ORDER"]["order"]:
        m.append("   %-18s %s" % (c["call"], c["args"]))
    m += ["```", "",
          "`_decay` s'exécute **après** `_react` : un `Y` nouveau-né est exposé à la",
          "décroissance **dès son pas de naissance**. Ce n'est pas une hypothèse, c'est",
          "`kinetics.World._one_step`.", "",
          "## 3. La loi de descendance exacte, pour un `Y`", "",
          "Soit, à la cellule occupée par le `Y`, après les quatre passes de diffusion :", "",
          "```",
          "c = min(nSY, free)              le nombre de candidats dans _react",
          "p = min(1, kY · nX · nY)        la probabilité de naissance dans _react",
          "m = muY                         la probabilité de retrait dans _decay",
          "```", "",
          "La fonction génératrice de la descendance d'un `Y` en un pas est **exactement**",
          "", "```",
          "f(z) = (m + (1−m) z) · (1 − p (1−m) (1−z))^c",
          "```", "",
          "— le premier facteur pour le parent, le second pour les `c` tirages candidats",
          "indépendants, chacun donnant une naissance avec probabilité `p`, chaque nouveau-né",
          "survivant à son propre pas de décroissance avec probabilité `1−m`. D'où", "",
          "```",
          "R = E[descendance] = (1 − muY) · (1 + c p)",
          "Var                = m(1−m) + c p m(1−m) + (1−m)² c p (1−p)",
          "```", "",
          "### Vérification contre l'ordonnanceur", "",
          "| état cellulaire | kY | muY | `c` analytique / capturé | `p` analytique / capturé | `m` analytique / capturé | `R` |",
          "|---|---|---|---|---|---|---|"]
    for r in ver[:10]:
        cs = r["cell_state"]
        m.append("| nX=%d nSY=%d free=%d | %g | %g | %d / %s | %g / %g | %g / %g | %.6f |"
                 % (cs["nX"], cs["nSY"], cs["free"], r["kY"], r["muY"], r["analytic_c"],
                    r["scheduler_c"], r["analytic_p"], r["scheduler_p"], r["analytic_m"],
                    r["scheduler_m"], r["R"]))
    m += ["", "**Tous les arguments concordent : %s.**"
          % op["EXACT_ONE_STEP_OFFSPRING_LAW"]["ALL_ARGUMENTS_MATCH"], "",
          "## 4. Le plafond exact `Q_max`, par énumération exhaustive", "",
          "L'intensité de naissance par pas est `c · p = kY · Q` dans la branche linéaire, avec",
          "`Q = nX · min(nSY, free)`. En énumérant les **%d** états cellulaires admissibles à"
          % adm["n_admissible_cell_states"],
          "`nY = 1` sous l'invariant d'occupation :", "",
          "```",
          "Q_max = %d,  atteint en %s" % (adm["Q_max"], adm["argmax_state"]),
          "Q = 0 est admissible : %s  (%.1f %% des états admissibles)"
          % (adm["Q_EQUALS_ZERO_IS_ADMISSIBLE"],
             100 * adm["fraction_of_admissible_states_with_Q_zero"]),
          "infimum de Q sur l'ensemble admissible = %d"
          % adm["INFIMUM_OF_Q_OVER_THE_ADMISSIBLE_SET"],
          "```", "",
          "`Q_max = 28` est retrouvé indépendamment ici ; il coïncide avec le plafond nommé",
          "dans le handoff hérité, ce qui est une concordance et non une reprise.", "",
          "**Conséquence décisive.** La catégorie A connaît l'**ensemble** admissible. Une",
          "valeur strictement positive de `E[Q]` est une propriété de la **mesure** sur cet",
          "ensemble — c'est-à-dire du nuage réalisé. La borne **supérieure** `β ≤ 28 kY` est",
          "certifiable sans aucun run ; la borne **inférieure** ne l'est pas.", "",
          "## 5. Pourquoi un rapport de branchement scalaire n'est pas légitime ici", "",
          "`c` et `p` sont fonctions de l'état de la cellule **du `Y` lui-même**, et `nX` à",
          "cette cellule est produit **par ce `Y`** : `_react` ne crée du `X` que là où",
          "`nX·nY ≥ 1`. L'environnement de la lignée est **endogène**. Le plus petit état exact",
          "est donc `(n_Y par cellule occupée, et (nX, nSY, free) à chacune de ces cellules)`,",
          "et non un scalaire.", "",
          "```",
          "OPÉRATEUR CONDITIONNEL   : CONDITIONAL_EXACT",
          "FERMETURE MARGINALE      : NOT_CLOSED",
          "```", "",
          "C'est le même diagnostic que le parent a posé pour `X`, pour la même raison",
          "structurelle. Il n'est pas hérité : il est redérivé ici sur la branche `Y`.", "",
          "## 6. Saturation du canal `X` — le point qui décide de la notion de « minorité »",
          "",
          "`p_X = min(1, kX · nX · nY)` avec `kX = 1.0`. Donc **`p_X = 1` exactement** dès que",
          "`nX·nY ≥ 1`. Vérifié contre l'ordonnanceur :", "",
          "| nX | nY (même cellule) | `p_X` analytique | `p_X` capturé | concorde |",
          "|---|---|---|---|---|"]
    for r in op["X_HAZARD_SATURATION"]["ROWS"]:
        m.append("| %d | %d | %.3f | %s | %s |" % (r["nX"], r["nY_same_cell"],
                                                   r["analytic_p_X"], r["scheduler_p_X"],
                                                   r["MATCHES"]))
    m += ["", "**Un seul organisateur sature déjà la source `X` à pleine puissance.** Un",
          "deuxième `Y` dans la *même* cellule n'ajoute rien ; il n'ajoute quelque chose qu'en",
          "**se séparant**, et ce qu'il ajoute alors est une **deuxième cellule-source**.",
          "« Minorité en nombre » et « minorité en rôle causal » se dissocient donc",
          "complètement : le nombre de `Y` n'est pas une variable de minorité dans cette",
          "architecture.", "",
          "## 7. La couche d'observables est mono-organisateur par construction", "",
          "```",
          "\n".join(op["OBSERVABLE_LAYER"]["evidence"]),
          "```", "",
          op["OBSERVABLE_LAYER"]["READING"], "",
          "## 8. Constantes exactes du noyau", "",
          "```",
          "q = p_hop/4        = %.18f" % ker["q_per_direction"],
          "a = 2q(1−q)        = %.6f     (manifeste : a_X = 0.05)" % ker["per_axis_activity_a"],
          "D = q(1−q)         = %.6f     (manifeste : D_X = 0.025)" % ker["D_per_species"],
          "D_rel = 2D         = %.6f     (manifeste : D_relative = 0.05)"
          % ker["D_relative_two_Y"],
          "concordance avec le manifeste gelé : %s" % ker["MATCHES"],
          "```", "",
          "Le déplacement par axe est la **différence de deux Bernoulli(q)**, pas `p_hop/4` :",
          "c'est la loi exacte établie par OBTR01, réemployée ici sans réapprentissage.", "",
          "Temps de séparation de deux `Y`, `⟨r²⟩ = 4 D_rel t` :", "",
          "| distance (cellules) | pas |", "|---|---|"]
    for k, v in ker["separation_time_steps"].items():
        m.append("| %.3f | %.1f |" % (float(k), v))
    m += ["", "## 9. Ce que l'opérateur permet de conclure, et ce qu'il ne permet pas", "",
          "| affirmation | statut |", "|---|---|",
          "| la loi d'un pas est exacte conditionnellement à `(nX, nSY, free)` | **établie**, "
          "vérifiée argument par argument |",
          "| `β ≤ 28 kY` pour tout état admissible | **établie** par énumération |",
          "| `β ≥ ε > 0` pour un `ε` numérique | **non établissable** en catégorie A |",
          "| un rayon spectral scalaire suffit | **non** : l'environnement est endogène |",
          "| la densité marginale de la lignée se ferme | **non** |", ""]
    open(f"{OUT}/PMCR01_DISCRETE_Y_OPERATOR_DERIVATION.md", "w").write("\n".join(m) + "\n")
    return len(m)


if __name__ == "__main__":
    print("operator derivation lines:", operator_md())
