"""EDL — recalcul INDEPENDANT du test gele d'OMLDCT03, et structure des terminaisons.

Bibliotheque standard seule. Aucune archive n'est ouverte ; l'unique entree est
OMLDCT03/out/OMLDCT03_FROZEN_TEST_RESULT.json, champ PER_PAIR.

  python3 edl_omldct03_independent.py [racine_du_depot]

CE QUE CE SCRIPT EST. Un DEUXIEME CHEMIN vers les memes nombres : rang signe
exact par programmation dynamique sur la loi nulle du W+, mediane, estimateur de
Hodges-Lehmann par moyennes de Walsh, intervalle par inversion du test. Il ne
partage aucune ligne de code avec omldct03_frozen_test.py. Un desaccord serait
un detecteur de bug.

CE QUE CE SCRIPT N'EST PAS. Une replication independante. Les donnees sont les
memes 41 paires. Reproduire une arithmetique n'est pas reproduire une experience.

Le bloc « structure des terminaisons » est DESCRIPTIF et POST HOC. Il ne
constitue aucun test et n'a aucun taux d'erreur. Il est imprime parce que le
mode de terminaison de l'intervalle d'identite n'est pas invariant sous
l'intervention, ce qui conditionne la lecture du test gele.
"""
from __future__ import annotations
import collections, json, math, os, statistics, sys

EXTINCTION = "NO_COMPONENT_AT_THE_NEXT_STEP"


def null_counts(n):
    """Nombre de sous-ensembles de {1..n} de somme s, pour s = 0..n(n+1)/2."""
    m = n * (n + 1) // 2
    dp = [0] * (m + 1)
    dp[0] = 1
    for r in range(1, n + 1):
        for s in range(m, r - 1, -1):
            dp[s] += dp[s - r]
    return dp, m


def signed_rank_exact(x):
    """Wilcoxon signe-range EXACT. Rangs moyens sur les egalites de |x| ;
    la loi exacte n'est valide qu'en l'absence d'egalite, ce que l'on signale."""
    nz = [v for v in x if v != 0.0]
    n = len(nz)
    order = sorted(range(n), key=lambda i: abs(nz[i]))
    absv = sorted(abs(v) for v in nz)
    ranks, i = [0.0] * n, 0
    while i < n:
        j = i
        while j + 1 < n and absv[j + 1] == absv[i]:
            j += 1
        r = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[k] = r
        i = j + 1
    ties = len(set(absv)) != n
    w_plus = sum(ranks[k] for k in range(n) if nz[order[k]] > 0)
    dp, m = null_counts(n)
    lo = min(w_plus, m - w_plus)
    p = min(2 * sum(dp[s] for s in range(int(math.floor(lo)) + 1)) / 2 ** n, 1.0)
    return w_plus, n, p, ties


def hodges_lehmann(x, alpha=0.05):
    w = sorted((x[i] + x[j]) / 2.0 for i in range(len(x)) for j in range(i, len(x)))
    dp, _m = null_counts(len(x))
    tot, c, k = 2 ** len(x), 0, 0
    while 2 * (c + dp[k]) / tot <= alpha:
        c += dp[k]
        k += 1
    return statistics.median(w), (w[k], w[len(w) - 1 - k]), k


def main():
    root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
    src = os.path.join(root, "OMLDCT03/out/OMLDCT03_FROZEN_TEST_RESULT.json")
    d = json.load(open(src))
    per, dec = d["PER_PAIR"], d["DECISION"]
    out = {"source": src, "n_pairs": len(per), "endpoints": {}}

    for key, label in (("log_duration_difference", "duration"),
                       ("log_exposure_difference", "exposure")):
        x = [p[key] for p in per]
        w, n, p, ties = signed_rank_exact(x)
        hl, ci, _k = hodges_lehmann(x)
        st = dec[label]
        out["endpoints"][label] = {
            "W_plus": {"recomputed": w, "published": st["W_plus"], "match": w == st["W_plus"]},
            "n_nonzero": {"recomputed": n, "published": st["n_nonzero"], "match": n == st["n_nonzero"]},
            "exact_two_sided_p": {"recomputed": p, "published": st["exact_two_sided_p"],
                                  "match": abs(p - st["exact_two_sided_p"]) < 1e-12},
            "median": {"recomputed": statistics.median(x), "published": st["median_difference"],
                       "match": abs(statistics.median(x) - st["median_difference"]) < 1e-12},
            "hodges_lehmann": {"recomputed": hl, "published": st["hodges_lehmann"],
                               "match": abs(hl - st["hodges_lehmann"]) < 1e-12},
            "hl_interval": {"recomputed": list(ci), "published": st["hl_interval"],
                            "match": all(abs(a - b) < 1e-9 for a, b in zip(ci, st["hl_interval"]))},
            "ties_in_abs_differences": ties,
            "n_positive": sum(1 for v in x if v > 0)}

    flat = [v for e in out["endpoints"].values() for v in e.values() if isinstance(v, dict)]
    out["ALL_TWELVE_STATISTICS_REPRODUCE"] = all(v["match"] for v in flat)
    out["THIS_IS_A_RECONSTRUCTION_NOT_AN_INDEPENDENT_REPLICATION"] = True

    # --- structure des terminaisons : DESCRIPTIF, POST HOC, AUCUN TEST GELE ---
    t = {"STATUS": "POST_HOC_DESCRIPTIVE__NOT_A_FROZEN_TEST__NO_ERROR_RATE_CLAIMED"}
    for arm in ("SELECTIVE", "SHAM"):
        t[f"{arm}_mix"] = dict(collections.Counter(p[f"{arm}_termination"] for p in per))
    t["cross_table"] = {f"{a}|{b}": c for (a, b), c in
                        collections.Counter((p["SELECTIVE_termination"],
                                             p["SHAM_termination"]) for p in per).items()}
    b = sum(1 for p in per if p["SELECTIVE_termination"] == EXTINCTION
            and p["SHAM_termination"] != EXTINCTION)
    c = sum(1 for p in per if p["SELECTIVE_termination"] != EXTINCTION
            and p["SHAM_termination"] == EXTINCTION)
    n = b + c
    t["extinction_of_the_identity"] = {
        "SELECTIVE": sum(1 for p in per if p["SELECTIVE_termination"] == EXTINCTION),
        "SHAM": sum(1 for p in per if p["SHAM_termination"] == EXTINCTION),
        "discordant_pairs": {"SELECTIVE_only": b, "SHAM_only": c},
        "mcnemar_exact_two_sided_p":
            min(2 * sum(math.comb(n, k) for k in range(min(b, c) + 1)) / 2 ** n, 1.0) if n else 1.0,
        "WARNING": ("les canaux de terminaison ne sont pas les memes dans les deux bras : "
                    "MERGE est arithmetiquement impossible quand la fille est le seul objet du "
                    "monde. Ce contraste n'est donc PAS un contraste d'exposition egale.")}
    out["termination_structure"] = t
    print(json.dumps(out, indent=1))
    sys.exit(0 if out["ALL_TWELVE_STATISTICS_REPRODUCE"] else 2)


if __name__ == "__main__":
    main()
