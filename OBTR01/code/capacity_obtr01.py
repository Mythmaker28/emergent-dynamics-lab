"""OBTR01 §12 — the capacity-refusal audit, and an attempt at a CERTIFIED bound.

`_diffuse` accepts min(movers, dest_free) per CELL. That truncation is the one place where the
engine departs from the unblocked kernel, so it is the single quantity that decides whether the
operator of §8 is exact. The mandate asks for the refusal to be characterised by size, seed,
population, position, phase and species, and for a certified bound to be SOUGHT before falling
back on an empirical characterisation.

A certified bound is found, and it is stated with its scope rather than in general:

    a tagged molecule offers on average p_hop hops per step and lives (1-mu)/mu steps, and a
    fraction eps of offered hops is refused, so the expected number of refusals over its whole
    lifetime is  E[R] = p_hop * eps * (1-mu)/mu.  By Markov, P(R >= 1) <= E[R].

    Hence for ANY per-particle observable f of one molecule's trajectory with 0 <= f <= F,
        | E_true[f] - E_unblocked[f] |  <=  F * E[R].

This is exactly the class of observables §9 registered, which is why the bound is useful there
and why it is NOT claimed for joint observables of the whole cloud: for those the union bound
over N molecules exceeds one and says nothing.
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np
import yaml

WC = "/home/claude/OBTR01/verify/obdca01/wc"
OUT = "/home/claude/OBTR01/out"
sys.path.insert(0, f"{WC}/OBTC02/code")


def binom_pmf(n, p):
    k = np.arange(n + 1)
    from math import comb
    return np.array([comb(n, int(i)) * p ** int(i) * (1 - p) ** (n - int(i)) for i in k])


def expected_refused(n, free, q):
    """E[max(0, B - free)] with B ~ Binomial(n, q); exact, n <= CAP so the sum is tiny."""
    if n <= 0:
        return 0.0
    pmf = binom_pmf(n, q)
    k = np.arange(n + 1)
    return float((np.maximum(k - free, 0) * pmf).sum())


def spatial_profile(field, occ, oy, ox, q, CAP, L, max_r=14):
    """Exact expected refusal fraction for X hops, cell by cell, binned by toroidal distance to
    the ORGANISER. Uses the recorded final occupancy: nothing is simulated."""
    free = np.maximum(CAP - occ, 0)
    i = np.arange(L)
    dy = np.minimum(np.abs(i - oy), L - np.abs(i - oy))
    dx = np.minimum(np.abs(i - ox), L - np.abs(i - ox))
    dist = np.sqrt(dy[:, None] ** 2 + dx[None, :] ** 2)
    off, ref = np.zeros(max_r + 1), np.zeros(max_r + 1)
    ys, xs = np.nonzero(field)
    for y, x in zip(ys, xs):
        n = int(field[y, x])
        b = int(min(round(dist[y, x]), max_r))
        for sy, sx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            f = int(free[(y + sy) % L, (x + sx) % L])
            off[b] += n * q
            ref[b] += expected_refused(n, f, q)
    return off, ref


def main():
    spec = yaml.safe_load(open(f"{WC}/OBDI02/code/obdi02_protocol.yaml"))
    pt = spec["point"]
    q, mu, CAP, p_hop = pt["p_hop"] / 4.0, pt["muX"], pt["CAP"], pt["p_hop"]

    # ---------------------------------------------------------------- gather every arm
    arms = []
    a2 = json.load(open(f"{WC}/OBDI02/out/_arms.json"))
    for a in a2:
        arms.append({"mission": "OBDI02", "tag": a["tag"], "L": a["L"], "seed": a["seed"],
                     "condition": "P", "blocked": a["blocked_fraction"],
                     "N_X": a["N_X"].get("window_mean"), "source_off": None,
                     "organiser_removed_at": None,
                     "mean_free_at_organiser": a.get("mean_free_at_organiser")})
    a1 = json.load(open(f"{WC}/OBDI01/out/_arms.json"))
    for a in (a1 if isinstance(a1, list) else []):
        arms.append({"mission": "OBDI01", "tag": a.get("tag"), "L": a.get("L"),
                     "seed": a.get("seed"), "condition": a.get("condition", "P"),
                     "blocked": a["blocked_fraction"],
                     "N_X": (a.get("N_X") or {}).get("window_mean"),
                     "source_off": a.get("source_off"),
                     "organiser_removed_at": a.get("organiser_removed_at"),
                     "mean_free_at_organiser": a.get("mean_free_at_organiser")})
    r0 = json.load(open(f"{WC}/OBTC02/out/_results.json"))
    for a in r0["arms"]:
        arms.append({"mission": "OBTC02", "tag": a["tag"], "L": a["L"], "seed": a["seed"],
                     "condition": a.get("condition"), "blocked": a["blocked_fraction"],
                     "N_X": (a.get("N_X") or {}).get("window_mean"),
                     "source_off": a.get("source_off"),
                     "organiser_removed_at": a.get("organiser_removed_at"),
                     "hops_offered": a.get("hops_offered"),
                     "mean_free_at_organiser": a.get("mean_free_at_organiser")})

    def col(key, sel=lambda a: True):
        return np.array([a["blocked"][key] for a in arms
                         if sel(a) and a["blocked"].get(key) is not None], float)

    def stats(v):
        if len(v) == 0:
            return None
        return {"n": int(len(v)), "mean": float(v.mean()), "median": float(np.median(v)),
                "min": float(v.min()), "max": float(v.max()),
                "sd": float(v.std(ddof=1)) if len(v) > 1 else 0.0}

    by_species = {s: stats(col(s)) for s in ("X", "Y", "SX", "SY")}
    by_size = {int(L): stats(col("X", lambda a, L=L: a["L"] == L))
               for L in sorted({a["L"] for a in arms if a["L"]})}
    by_mission = {m: stats(col("X", lambda a, m=m: a["mission"] == m))
                  for m in ("OBTC02", "OBDI01", "OBDI02")}
    by_condition = {c: stats(col("X", lambda a, c=c: a["condition"] == c))
                    for c in sorted({str(a["condition"]) for a in arms})}

    # ---------------------------------------------------------------- population dependence
    pop = [(a["N_X"], a["blocked"]["X"]) for a in arms
           if a["N_X"] and a["N_X"] > 0 and a["blocked"]["X"] > 0]
    if len(pop) > 3:
        x = np.log([p[0] for p in pop])
        y = np.log([p[1] for p in pop])
        slope, intercept = np.polyfit(x, y, 1)
        rho = float(np.corrcoef(x, y)[0, 1])
    else:
        slope = intercept = rho = float("nan")
    population = {"n_arms": len(pop), "log_log_slope_of_eps_on_N_X": float(slope),
                  "correlation": rho,
                  "READING": ("a slope near +1 would say refusal is proportional to the "
                              "population, i.e. driven by crowding; a slope near 0 would say "
                              "it is a property of the lattice occupancy set by the chemostat "
                              "and not by the cloud.")}

    # ---------------------------------------------------------------- position dependence
    off_tot, ref_tot, used = None, None, 0
    for a in arms:
        p = f"{WC}/{a['mission']}/raw/{str(a['tag']).replace('/', '__')}.npz"
        if not os.path.exists(p):
            continue
        z = np.load(p, allow_pickle=True)
        f, fy = z["nX_final"], z["nY_final"]
        if int(fy.sum()) < 1 or int(f.sum()) < 20:
            continue
        L = int(f.shape[0])
        occ = sum(z[k] for k in ("nX_final", "nY_final", "nSX_final", "nSY_final",
                                 "nWX_final", "nWY_final"))
        oy, ox = [int(v[0]) for v in np.nonzero(fy)]
        o, r = spatial_profile(f, occ, oy, ox, q, CAP, L)
        off_tot = o if off_tot is None else off_tot + o
        ref_tot = r if ref_tot is None else ref_tot + r
        used += 1
    position = {"arms_used": used,
                "LIMITATION": ("only the FINAL field of each arm is stored, so this profile "
                               "rests on one frame per arm. The bins are therefore thin and "
                               "the shape is indicative, not a measured law. The certified "
                               "bound below does not depend on it."),
                "method": ("exact expected refusal E[max(0, Binomial(n, q) - free)] per cell "
                           "and direction, from the recorded final occupancy; nothing is "
                           "simulated"),
                "by_distance_to_the_organiser": [
                    {"r": int(i), "offered": float(off_tot[i]), "refused": float(ref_tot[i]),
                     "fraction": float(ref_tot[i] / off_tot[i]) if off_tot[i] > 0 else None}
                    for i in range(len(off_tot))] if off_tot is not None else []}

    # ---------------------------------------------------------------- phase dependence
    phase_arms = [a for a in arms if a["mission"] == "OBTC02"]
    phase = {"note": ("hops_blocked is accumulated over a whole run, so the phase dimension is "
                      "resolved BETWEEN arms rather than within one: the frozen OBTC02 "
                      "conditions differ precisely in whether the source is on throughout, "
                      "switched off part-way, or immobile."),
             "by_condition": {},
             "conditions_present": sorted({str(a["condition"]) for a in phase_arms})}
    for c in phase["conditions_present"]:
        v = np.array([a["blocked"]["X"] for a in phase_arms if str(a["condition"]) == c])
        phase["by_condition"][c] = stats(v)
    r_arms = [a for a in phase_arms if a.get("source_off")]
    phase["source_off_arms"] = len(r_arms)

    # ---------------------------------------------------------------- the certified bound
    eps_mean = float(col("X").mean())
    eps_max = float(col("X").max())
    hops_per_lifetime = p_hop * (1 - mu) / mu

    def bound(eps):
        ER = hops_per_lifetime * eps
        return {"eps": eps, "expected_refusals_per_molecule_lifetime": ER,
                "P_at_least_one_refusal_upper_bound": min(ER, 1.0),
                "fraction_of_molecules_certified_unblocked_lower_bound": max(1 - ER, 0.0),
                "additive_error_on_a_probability_observable": min(ER, 1.0),
                "additive_error_on_M2_upper_bound": min(ER, 1.0) * 2 * (36 / 2) ** 2}

    certified = {
        "ARGUMENT": ("a molecule offers Binomial(4, q) hops per step, so p_hop on average, and "
                     "lives (1-mu)/mu steps; a fraction eps of offered hops is refused, and by "
                     "exchangeability within a cell each offered hop is refused with "
                     "probability eps on average. E[R] = p_hop * eps * (1-mu)/mu, and Markov "
                     "gives P(R >= 1) <= E[R]. No distributional assumption is used."),
        "hops_offered_per_molecule_per_lifetime": hops_per_lifetime,
        "AT_THE_MEAN_MEASURED_EPS": bound(eps_mean),
        "AT_THE_WORST_ARM": bound(eps_max),
        "SCOPE": ("valid for PER-PARTICLE observables of a single molecule's trajectory, which "
                  "is exactly the class §9 registered. For a joint observable of all N "
                  "molecules the union bound gives N * E[R] > 1 and is vacuous, so no "
                  "certified statement is made there."),
        "WHY_IT_IS_NOT_A_PER_PARTICLE_THINNING": (
            "acceptance is min(movers, dest_free) per CELL, so when the cap bites it truncates "
            "a whole batch. The refused hops are not an independent thinning of individual "
            "molecules and cannot be absorbed into an effective q; that is why the kernel "
            "status is CONDITIONAL_EXACT and not EXACT."),
    }

    out = {
        "SECTION": "OBTR01 §12",
        "CONSUMES_NO_SCIENTIFIC_RUN": True,
        "ARMS_AUDITED": {"total": len(arms),
                         "by_mission": {m: sum(1 for a in arms if a["mission"] == m)
                                        for m in ("OBTC02", "OBDI01", "OBDI02")}},
        "BY_SPECIES": by_species, "BY_SIZE": by_size, "BY_MISSION": by_mission,
        "BY_CONDITION": by_condition,
        "BY_SEED": {"note": "the per-arm spread IS the seed dimension",
                    "X": by_species["X"],
                    "coefficient_of_variation": (by_species["X"]["sd"]
                                                 / by_species["X"]["mean"])},
        "BY_POPULATION": population, "BY_POSITION": position, "BY_PHASE": phase,
        "CERTIFIED_BOUND": certified,
        "FULL_OPERATOR_ERROR":
            "CERTIFIED_FOR_PER_PARTICLE_BOUNDED_OBSERVABLES__EMPIRICALLY_CHARACTERIZED_OTHERWISE",
        "UNBLOCKED_SOURCE_RESPONSE_OPERATOR": "CONDITIONAL_EXACT",
    }
    json.dump(out, open(f"{OUT}/_capacity.json", "w"), indent=1, default=str)

    print("arms audited %d  %s" % (len(arms), out["ARMS_AUDITED"]["by_mission"]))
    print()
    print("%-10s %5s %12s %12s %12s" % ("species", "n", "mean", "median", "max"))
    for s, v in by_species.items():
        print("%-10s %5d %12.3e %12.3e %12.3e" % (s, v["n"], v["mean"], v["median"], v["max"]))
    print()
    print("by size (X):     " + "   ".join("L=%d %.3e (n=%d)" % (k, v["mean"], v["n"])
                                           for k, v in by_size.items()))
    print("by mission (X):  " + "   ".join("%s %.3e (n=%d)" % (k, v["mean"], v["n"])
                                           for k, v in by_mission.items() if v))
    print("by condition(X): " + "   ".join("%s %.3e (n=%d)" % (k, v["mean"], v["n"])
                                           for k, v in by_condition.items() if v))
    print("seed dimension : coefficient of variation %.3f"
          % out["BY_SEED"]["coefficient_of_variation"])
    print("population     : log-log slope %+.3f (corr %+.3f, %d arms)"
          % (population["log_log_slope_of_eps_on_N_X"], population["correlation"],
             population["n_arms"]))
    print()
    print("position, exact expected refusal fraction by distance to the organiser (%d arms):"
          % position["arms_used"])
    for b in position["by_distance_to_the_organiser"]:
        if b["fraction"] is not None and b["offered"] > 0:
            print("   r=%-3d offered %12.1f   fraction %.3e" % (b["r"], b["offered"],
                                                                b["fraction"]))
    print()
    print("CERTIFIED BOUND")
    for tag in ("AT_THE_MEAN_MEASURED_EPS", "AT_THE_WORST_ARM"):
        b = certified[tag]
        print("  %-26s eps %.3e -> E[R] %.5f -> at least %.2f %% of molecules never refused; "
              "additive error on a probability observable <= %.4f"
              % (tag, b["eps"], b["expected_refusals_per_molecule_lifetime"],
                 100 * b["fraction_of_molecules_certified_unblocked_lower_bound"],
                 b["additive_error_on_a_probability_observable"]))
    print()
    print("FULL_OPERATOR_ERROR = %s" % out["FULL_OPERATOR_ERROR"])


if __name__ == "__main__":
    main()
