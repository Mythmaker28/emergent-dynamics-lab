"""DEV_06 mechanistic adjudication + figure. Raw-only, no engine."""
from __future__ import annotations
import csv, json, math, statistics as st, collections
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

SRC = Path("../DR05")
SIZES = (24, 32)
LADDER = [("DIRECT_Q100_ANCHOR", 1), ("DIRECT_Q200_UNIFORM", 2),
          ("DIRECT_Q400_UNIFORM", 4), ("DIRECT_Q800_UNIFORM", 8)]
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#d8d7d2", "#fcfcfb"
C = {"I": "#8c8b86", "F": "#1baf7a", "A": "#eda100", "T": "#2a78d6", "S": "#eb6834",
     "B": "#4a3aa7", "R": "#b02020"}


def num(v):
    try:
        x = float(v)
        return None if math.isnan(x) else x
    except (TypeError, ValueError):
        return None


rows = []
for f in ("direct_replacement_rows_a.csv", "direct_replacement_rows_b.csv"):
    rows += list(csv.DictReader(open(SRC / f)))
ROW = {(int(r["size"]), r["block"], r["arm"]): r for r in rows}
SNAP = {(int(r["size"]), r["block"], r["arm"]): json.loads(r["snapshots"]) for r in rows}
FATE = list(csv.DictReader(open("dr05_event_cohort_fates.csv")))
PAIR = list(csv.DictReader(open("dr05_paired_flux_rows.csv")))
RATE = list(csv.DictReader(open("dr05_rate_effect_decomposition.csv")))
EV = list(csv.DictReader(open(SRC / "direct_replacement_event_ledger_b.csv")))
BLOCKS = {L: sorted({r["block"] for r in rows if int(r["size"]) == L}) for L in SIZES}


def med(g, k):
    v = [num(x[k]) for x in g]
    v = [y for y in v if y is not None]
    return st.median(v) if v else None


def cellF(L, a):
    return [r for r in FATE if int(r["size"]) == L and r["arm"] == a]


def cellP(L, a):
    return [r for r in PAIR if int(r["size"]) == L and r["arm"] == a and r["status"] == "OK"]


# ------------------------------------------------------------------ numbers
rej = {}
flux = {}
for L in SIZES:
    for a, d in LADDER + [("SINK_ONLY_Q800", 8), ("DIRECT_Q400_BURST", 4)]:
        g = [ROW[(L, b, a)] for b in BLOCKS[L] if (L, b, a) in ROW]
        rej[(L, a)] = med(g, "n_rejected") / med(g, "n_scheduled")
        gf = cellF(L, a)
        M = med(gf, "M256")
        flux[(L, a)] = {"gross_sink": med(gf, "GROSS_SINK_REMOVAL") / M,
                        "incumbent": med(gf, "INCUMBENT_REMOVED_BY_SINK") / M,
                        "washout": med(gf, "FRESH_WASHOUT_FRACTION"),
                        "inc_yield": med(gf, "INCUMBENT_SINK_YIELD"),
                        "n_exec": med(g, "n_events"), "n_sched": med(g, "n_scheduled")}

# depth survival normalised by each cohort's OWN t256 mass
depth = {}
for L in SIZES:
    for a in ("SHAM", "DIRECT_Q400_UNIFORM", "DIRECT_Q800_UNIFORM", "SINK_ONLY_Q800"):
        acc = {"core": [], "inter": [], "bnd": []}
        persist = tot = 0
        for b in BLOCKS[L]:
            s = SNAP.get((L, b, a))
            if s is None:
                continue
            ts = sorted(int(k) for k in s)
            s0, sT = s["256"], s[str(ts[-1])]
            alive = [s[str(t)] for t in ts if s[str(t)].get("track") is True]
            if alive:
                tot += 1
                if all(x["scaffold_cells"] > 0 for x in alive):
                    persist += 1
            if sT.get("track") is not True:
                continue
            for k in ("core", "inter", "bnd"):
                if s0[f"{k}_in_track"] > 0:
                    acc[k].append(sT[f"{k}_in_track"] / s0[f"{k}_in_track"])
        depth[(L, a)] = {k: (st.median(v) if v else None) for k, v in acc.items()}
        depth[(L, a)]["scaffold_persistent_blocks"] = f"{persist}/{tot}"

# tracker geometry
geo = {}
for L in SIZES:
    for a in ("SHAM", "DIRECT_Q400_UNIFORM", "DIRECT_Q800_UNIFORM"):
        d, ar = [], []
        for b in BLOCKS[L]:
            s = SNAP.get((L, b, a))
            if s is None:
                continue
            ts = sorted(int(k) for k in s)
            s0, sT = s["256"], s[str(ts[-1])]
            if sT.get("track") is not True:
                continue
            d.append(math.hypot(sT["cy"] - s0["cy"], sT["cx"] - s0["cx"]))
            ar.append(sT["area"] / s0["area"])
        geo[(L, a)] = {"centroid_displacement": (st.median(d) if d else None),
                       "area_ratio": (st.median(ar) if ar else None)}

# burst bite by position
bite = {}
for L in SIZES:
    for a in ("DIRECT_Q400_UNIFORM", "DIRECT_Q400_BURST"):
        pos = collections.defaultdict(list)
        for r in EV:
            if int(r["size"]) != L or r["arm"] != a or r["rejected"] == "True":
                continue
            pos[((int(r["event_id"]) - 1) % 40) + 1].append(num(r["realized_sink"]))
        bite[(L, a)] = {p: st.median(v) for p, v in sorted(pos.items())}

# rate effect signs
rate_signs = {}
for L in SIZES:
    g = [r for r in RATE if int(r["size"]) == L]
    d = {}
    for k in ("I_over_I0", "INCUMBENT_REMOVED_BY_SINK", "FRESH_WASHOUT_FRACTION",
              "FRESH_TERMINAL_RETENTION", "CORE_256_SURVIVAL", "T_over_M256"):
        v = [num(r[f"delta_uniform_minus_burst_{k}"]) for r in g]
        v = [x for x in v if x is not None]
        d[k] = {"min": min(v), "median": st.median(v), "max": max(v),
                "n_neg": sum(1 for x in v if x < 0), "n_pos": sum(1 for x in v if x > 0), "n": len(v)}
    rate_signs[str(L)] = d

# ---------------------------------------------------------- adjudication
adj = {
    "mission": "ROUTE_E_DIRECT_EXCHANGE_FLUX_DECOMPOSITION_06",
    "scientific_engine_invocations": 0,
    "PAIR_IDENTITY": json.loads(Path("_pair_identity.json").read_text())["PAIR_IDENTITY"],
    "MATCHED_SHAM_HORIZONS": "PASS",
    "RISK_SET_HANDLING": "PASS",
    "mechanisms": {
        "SIZE_NORMALIZED_FLUX_LIMIT": {
            "verdict": "SUPPORTED_PRIMARY",
            "evidence": {
                "event_rejection_rate_by_dose": {f"L{L}": {a: round(rej[(L, a)], 3)
                                                           for a, _ in LADDER} for L in SIZES},
                "event_rejection_sink_only": {f"L{L}": round(rej[(L, "SINK_ONLY_Q800")], 3)
                                              for L in SIZES},
                "gross_sink_over_M256_by_dose": {f"L{L}": {a: round(flux[(L, a)]["gross_sink"], 4)
                                                          for a, _ in LADDER} for L in SIZES},
                "dose_x8_buys": {f"L{L}": round(flux[(L, "DIRECT_Q800_UNIFORM")]["gross_sink"]
                                                / flux[(L, "DIRECT_Q100_ANCHOR")]["gross_sink"], 2)
                                 for L in SIZES},
                "median_eligible_sink_sites_per_event": 1},
            "statement": "The ladder saturates because scheduled events are increasingly REJECTED "
                         "for zero eligible sink capacity: 0% at Q100 and Q200, 40.6% at Q800 "
                         "(L=24) and 13.9% (L=32), and 94.8% / 94.5% when the source is uncoupled. "
                         "x8 dose buys only x2.34 (L=24) and x2.97 (L=32) gross removal."},
        "FRESH_SELF_WASHOUT_DOMINATED": {
            "verdict": "SUPPORTED_SECONDARY",
            "evidence": {"washout_fraction_by_dose": {f"L{L}": {a: (round(flux[(L, a)]["washout"], 4)
                                                                   if flux[(L, a)]["washout"] is not None else None)
                                                                for a, _ in LADDER} for L in SIZES},
                         "incumbent_share_of_bite": {f"L{L}": {a: round(flux[(L, a)]["inc_yield"], 4)
                                                               for a, _ in LADDER} for L in SIZES}},
            "statement": "Real and rising, but second order: from Q100 to Q800 the flux limit "
                         "costs a factor 2.7-3.4 while the falling incumbent share of the bite "
                         "costs a further 1.35-1.47."},
        "EXCHANGEABLE_BOUNDARY_SHELL": {
            "verdict": "REJECTED",
            "evidence": {"depth_survival_normalised_by_own_t256_mass": {
                f"L{L}": {a: {k: (round(v, 3) if isinstance(v, float) else v)
                              for k, v in depth[(L, a)].items()}
                          for a in ("SHAM", "DIRECT_Q400_UNIFORM", "DIRECT_Q800_UNIFORM")}
                for L in SIZES}},
            "statement": "Normalised by each cohort's OWN t256 mass, CORE/BOUNDARY survival is "
                         "1.02-1.44x, and the ratio is LARGEST in the SHAM. Forcing FLATTENS the "
                         "depth gradient instead of sparing the core. The apparent 4-6x core "
                         "protection in DEV_05 was an artefact of normalising by I0 while CORE "
                         "holds 63% of I0 and BOUNDARY only 17%."},
        "CORE_ACCESS_LIMITED": {"verdict": "REJECTED", "statement": "same evidence as above: the "
                                "core is reached about as efficiently as the shell."},
        "AMBIENT_COMPETITION_ASSOCIATED": {
            "verdict": "SUPPORTED_ASSOCIATIVE_ONLY",
            "evidence": {"AMBIENT_DELTA_median": {f"L{L}": {a: round(med(cellP(L, a), "AMBIENT_DELTA"), 4)
                                                            for a, _ in LADDER if cellP(L, a)}
                                                  for L in SIZES}},
            "statement": "AMBIENT_DELTA is NEGATIVE in every direct arm (-0.004 to -0.028 of M256): "
                         "the treated track carries LESS ambient than its matched sham. A negative "
                         "delta does not by itself prove the source causally displaces ambient."},
        "AMBIENT_REPLENISHMENT_ASSOCIATED": {"verdict": "NOT_SUPPORTED",
                                             "statement": "the sign is the opposite of the one this "
                                                          "mechanism requires."},
        "TRACKER_BOUNDARY_SWEEP_DOMINATED": {
            "verdict": "NOT_IDENTIFIABLE_FROM_SAVED_RAW",
            "evidence": {"centroid_displacement_t256_to_terminal": {
                f"L{L}": {a: round(geo[(L, a)]["centroid_displacement"], 2)
                          for a in ("SHAM", "DIRECT_Q400_UNIFORM", "DIRECT_Q800_UNIFORM")}
                for L in SIZES},
                "missing_frozen_frame_fields": ["mass_inside_frozen_C256", "C256_to_Ct_overlap",
                                                "boundary_site_turnover"]},
            "statement": "Under forcing the tracked component TRANSLATES 4.5-6.3 cells while the "
                         "sham moves 0.08. Ambient appearing inside the track therefore cannot be "
                         "separated from the track sweeping over stationary ambient. The frozen-"
                         "frame fields that would settle it were never saved."},
        "CONNECTIVITY_BREAKAGE_LIMIT": {
            "verdict": "SUPPORTED_AT_L24_Q800_ONLY",
            "statement": "7/9 track losses between t=7696 and t=10880, at compositions "
                         "(I/I0 0.36-0.42, F/T 0.37-0.43) indistinguishable from the 2 survivors: "
                         "breakage is a connectivity event, not a compositional threshold."},
        "PERSISTENT_INCUMBENT_SCAFFOLD": {
            "verdict": "SUPPORTED_TIME_FOLLOWED",
            "evidence": {f"L{L}": {a: depth[(L, a)]["scaffold_persistent_blocks"]
                                   for a in ("SHAM", "DIRECT_Q400_UNIFORM", "DIRECT_Q800_UNIFORM",
                                             "SINK_ONLY_Q800")} for L in SIZES},
            "statement": "A non-empty connected incumbent scaffold exists at EVERY sampled step in "
                         "9/9 blocks of every arm, including SINK_ONLY_Q800. This is the "
                         "time-followed qualification, not merely a terminal snapshot."},
    },
    "RATE_EFFECT": {
        "verdict": "RATE_EFFECT_RELAXATION_COMPATIBLE",
        "rejected_label": "RATE_EFFECT_SELF_WASHOUT_MEDIATED",
        "why_rejected": "washout moves OPPOSITE to the outcome: uniform has MORE washout (9/9 "
                        "both sizes) yet BETTER turnover, so washout cannot mediate the effect.",
        "event_level_mediator": {
            "burst_bite_by_position": {f"L{L}": {str(p): round(v, 4)
                                                 for p, v in bite[(L, 'DIRECT_Q400_BURST')].items()}
                                       for L in SIZES},
            "uniform_bite_by_position": {f"L{L}": {str(p): round(v, 4)
                                                   for p, v in bite[(L, 'DIRECT_Q400_UNIFORM')].items()}
                                         for L in SIZES},
            "statement": "Inside a burst the realized sink bite collapses from 2.06 (L=24) / 3.72 "
                         "(L=32) at position 1 to ~0.08 at positions 9-33, a 26-48x fall across "
                         "4-step gaps, while the uniform arm is flat at 0.287 / 0.231 across the "
                         "same positions with 16-step gaps. The schedule acts through sink-capacity "
                         "relaxation, and this link IS measured at event level."},
        "paired_signs": rate_signs},
    "SOURCE_FEEDS_SINK": {
        "verdict": "SUPPORTED",
        "evidence": {f"L{L}": {"coupled_gross_sink": round(flux[(L, "DIRECT_Q800_UNIFORM")]["gross_sink"], 4),
                               "sink_only_gross_sink": round(flux[(L, "SINK_ONLY_Q800")]["gross_sink"], 4),
                               "ratio": round(flux[(L, "DIRECT_Q800_UNIFORM")]["gross_sink"]
                                              / flux[(L, "SINK_ONLY_Q800")]["gross_sink"], 2)}
                     for L in SIZES},
        "statement": "At the identical Q800 schedule the coupled arm removes 1.63-1.65x MORE mass "
                     "than sink-only, and is rejected 14-41% of the time instead of 95%. Upstream "
                     "injection keeps downstream cells above threshold: the source feeds the sink."},
    "AMBIENT_ASSISTANCE": "NOT_ESTABLISHED",
    "PHYSICAL_BOUNDARY_CROSSING_STATUS": "NOT_RECONSTRUCTIBLE_FROM_SAVED_RAW",
    "FRESH_EVENT_SURVIVAL_CURVES": "NOT_RECONSTRUCTIBLE_FROM_SAVED_RAW "
                                   "(per-event FRESH cohorts were aggregated by design in DEV_05)",
    "PRIMARY_MECHANISM": "SIZE_NORMALIZED_FLUX_LIMIT",
    "SECONDARY_MECHANISMS": ["FRESH_SELF_WASHOUT_DOMINATED", "AMBIENT_COMPETITION_ASSOCIATED",
                             "CONNECTIVITY_BREAKAGE_LIMIT", "PERSISTENT_INCUMBENT_SCAFFOLD",
                             "TRACKER_BOUNDARY_SWEEP_DOMINATED (not identifiable)"],
    "DECISION": "SIZE_NORMALIZED_FLUX_LIMIT",
    "NEXT_SCIENTIFIC_ACTION": "MAP_RATE_AND_GEOMETRY_FRONTIER",
}
Path("dr05_mechanism_adjudication.json").write_text(json.dumps(adj, indent=1))
print("DECISION =", adj["DECISION"], "| NEXT =", adj["NEXT_SCIENTIFIC_ACTION"])

# ==================================================================== figure
fig, axes = plt.subplots(2, 3, figsize=(16.4, 8.8))
fig.patch.set_facecolor(SURF)
for i, L in enumerate(SIZES):
    a0, a1, a2 = axes[i]
    for ax in (a0, a1, a2):
        ax.set_facecolor(SURF); ax.grid(True, color=GRID, lw=0.8, axis="y", zorder=0)
        for sp in ("top", "right"): ax.spines[sp].set_visible(False)
        for sp in ("left", "bottom"): ax.spines[sp].set_color(GRID)
        ax.tick_params(colors=INK2, labelsize=9)
    xs = [d for _, d in LADDER]

    # col 1 : where the dose goes
    a0.plot(xs, xs, ":", color=INK2, lw=1.4, zorder=2, label="dose planifiée" if i == 0 else None)
    a0.plot(xs, [flux[(L, a)]["gross_sink"] for a, _ in LADDER], "o-", color=C["T"], lw=2.4, ms=7,
            zorder=4, label="retrait brut réalisé" if i == 0 else None)
    a0.plot(xs, [flux[(L, a)]["incumbent"] for a, _ in LADDER], "s-", color=C["I"], lw=2.4, ms=7,
            zorder=5, label="incumbent retiré" if i == 0 else None)
    a0.set_xscale("log", base=2); a0.set_yscale("log")
    a0.set_xticks(xs); a0.set_xticklabels([f"Q{d*100}" for d in xs], fontsize=9)
    a0.set_ylabel(f"L = {L}\n\nmasse / M₂₅₆", color=INK2, fontsize=10)
    ar = a0.twinx()
    ar.bar([x for x in xs], [rej[(L, a)] for a, _ in LADDER], width=[x * 0.5 for x in xs],
           color=C["R"], alpha=0.22, zorder=1)
    ar.set_ylim(0, 1.0); ar.set_ylabel("taux de rejet d'événement", color=C["R"], fontsize=9)
    ar.tick_params(colors=C["R"], labelsize=8)
    for sp in ("top",): ar.spines[sp].set_visible(False)
    a0.annotate(f"puits seul : {rej[(L,'SINK_ONLY_Q800')]*100:.0f} % rejetés",
                xy=(8, flux[(L, "SINK_ONLY_Q800")]["gross_sink"]), xytext=(1.15, 0.055),
                color=C["R"], fontsize=8.4, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C["R"], lw=1.2))
    a0.plot([8], [flux[(L, "SINK_ONLY_Q800")]["gross_sink"]], "D", color=C["R"], ms=8, zorder=6)

    # col 2 : paired decomposition, per block
    keys = [("INCUMBENT_EXCESS_EGRESS", C["I"], "excès d'égression I"),
            ("FRESH_PRESENT", C["F"], "F présent"),
            ("AMBIENT_DELTA", C["A"], "Δ ambiant"),
            ("TOTAL_MASS_DELTA", C["T"], "Δ masse totale")]
    for k, col, lab in keys:
        for b in BLOCKS[L]:
            ys = []
            for a, _ in LADDER:
                m = [r for r in PAIR if int(r["size"]) == L and r["arm"] == a
                     and r["block"] == b and r["status"] == "OK"]
                ys.append(num(m[0][k]) if m else float("nan"))
            a1.plot(xs, ys, "-", color=col, lw=0.7, alpha=0.30, zorder=2)
        a1.plot(xs, [med(cellP(L, a), k) if cellP(L, a) else float("nan") for a, _ in LADDER],
                "o-", color=col, lw=2.6, ms=7, zorder=4, label=lab if i == 0 else None)
    a1.axhline(0.0, color=INK2, lw=1.2, zorder=3)
    a1.set_xscale("log", base=2); a1.set_xticks(xs)
    a1.set_xticklabels([f"Q{d*100}" for d in xs], fontsize=9)
    a1.set_ylabel("fraction de M₂₅₆ (traité − sham apparié)", color=INK2, fontsize=9.5)
    if L == 24:
        a1.annotate("Q800 : 2 survivants sur 9", xy=(8, med(cellP(L, "DIRECT_Q800_UNIFORM"),
                                                            "FRESH_PRESENT")),
                    xytext=(2.4, 0.52), color=C["R"], fontsize=8.4, fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color=C["R"], lw=1.2))

    # col 3 : the event-level mediator
    pb = bite[(L, "DIRECT_Q400_BURST")]
    pu = bite[(L, "DIRECT_Q400_UNIFORM")]
    ps = sorted(pb)
    a2.plot(ps, [pb[p] for p in ps], "o-", color=C["B"], lw=2.4, ms=8, zorder=4,
            label="burst (écart 4 pas)" if i == 0 else None)
    a2.plot(ps, [pu[p] for p in ps], "s-", color=C["S"], lw=2.4, ms=8, zorder=4,
            label="uniforme (écart 16 pas)" if i == 0 else None)
    a2.set_yscale("log")
    a2.set_xticks(ps); a2.set_xticklabels([str(p) for p in ps], fontsize=9)
    a2.set_xlabel("position de l'événement dans la salve", color=INK2, fontsize=9.5)
    a2.set_ylabel("morsure réalisée du puits", color=INK2, fontsize=10)
    f = pb[ps[0]] / pb[ps[1]]
    a2.annotate(f"chute ×{f:.0f}\nentre les positions 1 et 9", xy=(ps[1], pb[ps[1]]),
                xytext=(ps[1] + 3, pb[ps[0]] * 0.55), color=C["R"], fontsize=8.6,
                fontweight="bold", arrowprops=dict(arrowstyle="->", color=C["R"], lw=1.2))

axes[0][0].set_title("Où va la dose : le rejet d'événement", color=INK, fontsize=11.5,
                     fontweight="bold", pad=8)
axes[0][1].set_title("Décomposition appariée, bloc par bloc", color=INK, fontsize=11.5,
                     fontweight="bold", pad=8)
axes[0][2].set_title("Médiateur de la cadence, par événement", color=INK,
                     fontsize=11.5, fontweight="bold", pad=8)
axes[1][0].set_xlabel("dose (nombre d'événements ; quantum gelé)", color=INK2, fontsize=9.5)
axes[1][1].set_xlabel("dose (nombre d'événements ; quantum gelé)", color=INK2, fontsize=9.5)
fig.suptitle("Décomposition du flux d'échange direct — 0 appel moteur, tout depuis les ledgers DEV_05",
             color=INK, fontsize=14.5, fontweight="bold", y=0.985)
fig.text(0.5, 0.945, "DECISION = SIZE_NORMALIZED_FLUX_LIMIT · la dose sature parce que les "
         "événements sont REJETÉS faute de capacité éligible · n = 9 blocs indépendants par taille",
         ha="center", color=INK2, fontsize=9)
fig.tight_layout(rect=[0, 0.075, 1, 0.925])
for j, (ax, xa) in enumerate(zip((axes[0][0], axes[0][1], axes[0][2]), (0.035, 0.365, 0.715))):
    h, l = ax.get_legend_handles_labels()
    fig.legend(h, l, frameon=False, fontsize=7.8, labelcolor=INK2, ncol=2,
               loc="lower left", bbox_to_anchor=(xa, 0.002))
fig.savefig("direct_exchange_flux_decomposition.png", dpi=170, facecolor=SURF)
print("figure -> direct_exchange_flux_decomposition.png")
