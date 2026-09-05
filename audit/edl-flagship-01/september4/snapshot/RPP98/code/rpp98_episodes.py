"""RPP98 — le détecteur d'épisodes multi-composantes. AUCUNE archive n'est ouverte ici.

Ce fichier ne contient que la règle, telle que la section 2 du pré-enregistrement la fixe :

    UN ÉPISODE MULTI-COMPOSANTES est un intervalle MAXIMAL de pas CONSÉCUTIFS pendant lequel
    n_components >= 2.

Deux points sur lesquels une erreur ne se verrait pas dans le résultat final, et qui sont donc
écrits ici explicitement puis exercés par le test de capacité :

  * « consécutifs » se lit sur t, pas sur la position dans le tableau. Si un pas manque dans la
    série, l'épisode est COUPÉ. Le détecteur ne recolle jamais par-dessus un pas qu'il n'a pas vu.
  * n_components vaut ZÉRO quand Y est éteint (len(comps) sur une liste de cellules vide). Zéro
    n'est donc pas un « pas de donnée » : c'est une valeur qui interrompt un épisode comme 1.

Le seuil de persistance est repris du déclencheur gelé de FDFLT01 (NEED = 250 pas consécutifs).
Il n'est pas choisi ici.
"""
from __future__ import annotations

MULTI_MIN = 2          # n_components >= 2 définit l'appartenance à un épisode
PERSISTENT_MIN_DUREE = 250   # = NEED du déclencheur gelé, repris pour comparabilité


def episodes(t, nc):
    """t : pas strictement croissants. nc : n_components au même index.

    Retourne la liste des épisodes, dans l'ordre chronologique, chacun un dict
    {t_start, t_end, duree, n_max}. La liste est vide s'il n'y a aucun épisode.
    """
    t = [int(v) for v in t]
    nc = [int(v) for v in nc]
    if len(t) != len(nc):
        raise ValueError("t et nc de longueurs differentes")
    for i in range(1, len(t)):
        if t[i] <= t[i - 1]:
            raise ValueError(f"t non strictement croissant en {i}: {t[i-1]} -> {t[i]}")
    if any(v < 0 for v in nc):
        raise ValueError("n_components negatif")

    out, cur, prev_t = [], None, None
    for ti, ni in zip(t, nc):
        if ni >= MULTI_MIN:
            if cur is not None and prev_t is not None and ti == prev_t + 1:
                cur["t_end"] = ti
                if ni > cur["n_max"]:
                    cur["n_max"] = ni
            else:
                if cur is not None:
                    out.append(cur)
                cur = {"t_start": ti, "t_end": ti, "n_max": ni}
        else:
            if cur is not None:
                out.append(cur)
            cur = None
        prev_t = ti
    if cur is not None:
        out.append(cur)
    for e in out:
        e["duree"] = e["t_end"] - e["t_start"] + 1
    return out


def annotate(eps, t_m, mass_by_step=None):
    """Attache les attributs qui demandent un contexte extérieur à la série.

    masse_parent = k_ncells de la plus grande composante au pas t_start - 1. Vaut None — et non
    zéro — si ce pas n'existe pas (épisode commençant au premier pas, ou ligne absente).
    """
    for e in eps:
        e["persistant"] = bool(e["duree"] >= PERSISTENT_MIN_DUREE)
        e["chevauche_t_m"] = bool(e["t_start"] <= t_m <= e["t_end"])
        e["tardif"] = bool(e["t_start"] > t_m)      # strict : commencer EN t_m n'est pas tardif
        e["masse_parent"] = None if mass_by_step is None else mass_by_step.get(e["t_start"] - 1)
    return eps
