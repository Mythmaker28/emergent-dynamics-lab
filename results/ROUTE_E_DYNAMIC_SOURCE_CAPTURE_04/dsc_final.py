"""ROUTE_E_DYNAMIC_SOURCE_CAPTURE_DEV_04 -- analysis, gates, figure."""
from __future__ import annotations
import csv, json, math, statistics as st
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

ARMS = ["SHAM", "D1_LEGACY_Q005", "D1_REDESIGNED_Q005", "D2_REDESIGNED_Q005",
        "D2_REDESIGNED_Q020", "D2_REDESIGNED_Q050", "D2_REDESIGNED_Q100",
        "DIRECT_INTERFACE_Q100"]
LADDER = ["D2_REDESIGNED_Q005", "D2_REDESIGNED_Q020", "D2_REDESIGNED_Q050", "D2_REDESIGNED_Q100"]
DOSE = {"D2_REDESIGNED_Q005": 0.05, "D2_REDESIGNED_Q020": 0.20,
        "D2_REDESIGNED_Q050": 0.50, "D2_REDESIGNED_Q100": 1.00}
SIZES = (24, 32)
C = {"inj": "#2a78d6", "contact": "#eb6834", "capture": "#1baf7a",
     "inc16": "#eda100", "ret": "#e87ba4", "dir": "#4a3aa7"}
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#d8d7d2", "#fcfcfb"


def f(r, k):
    v = r.get(k)
    if v in (None, "", "None", "nan"):
        return None
    try:
        x = float(v)
        return None if math.isnan(x) else x
    except (TypeError, ValueError):
        return None


rows = list(csv.DictReader(open("dynamic_source_capture_rows.csv")))
for r in rows:
    r["L"] = int(r["L"]); r["seed"] = int(r["seed"])
valid = [r for r in rows if r.get("t256_status") == "T256_VALID_TRACK"]
sham = {(r["L"], r["seed"]): r for r in valid if r["arm"] == "SHAM"}


def med(g, k):
    v = [f(r, k) for r in g]
    v = [x for x in v if x is not None]
    return st.median(v) if v else None


def endpoint(r):
    """Frozen 20-condition primary endpoint, evaluated per trajectory."""
    M = f(r, "M256")
    if M is None or r.get("t256_status") != "T256_VALID_TRACK":
        return False, "T256_INVALID"
    if not (r.get("survival_2048") == "True" and r.get("coast_survival") == "True"):
        return False, "NO_COAST_SURVIVAL"
    if (f(r, "direct_operator_insertion") or 0.0) > 1e-12:
        return False, "DIRECT_OPERATOR_INSERTION"
    if (f(r, "capture_by_merger") or 0.0) > 1e-12:
        return False, "CAPTURE_BY_MERGER"
    # NB: `x or default` misreads an exact 0.0 as absent. Error terms are read explicitly.
    alg = f(r, "algebraic_ledger_error")
    num = f(r, "total_system_balance_error")
    tests = [
        ("source", (f(r, "realized_source_injection") or 0) >= 0.04 * M),
        ("sink", (f(r, "realized_sink_removal") or 0) >= 0.04 * M),
        ("capture", (f(r, "unique_capture_transport") or 0) >= 0.04 * M),
        ("inc16", (f(r, "incorporation_16") or 0) >= 0.04 * M),
        ("dur128", (f(r, "durable_incorporation_128") or 0) >= 0.03 * M),
        ("egress", (f(r, "unique_incumbent_egress_to_sink") or 0) >= 0.04 * M),
        ("ret_post", (f(r, "fresh_retention_postforce") or 0) >= 0.04),
        ("ret_2048", (f(r, "fresh_retention_2048") or 0) >= 0.02),
        ("coast_ratio", (f(r, "coast_retention_ratio") or 0) >= 0.50),
        ("smr_post", (f(r, "sink_matched_replacement_postforce") or 0) >= 0.04),
        ("smr_2048", (f(r, "sink_matched_replacement_2048") or 0) >= 0.02),
        ("ledger", alg is not None and alg <= 1e-12),
        ("numeric", num is not None and num <= 1e-12 * M),
    ]
    for tag in ("postforce", "2048"):
        mr = f(r, f"mass_ratio_{tag}")
        tests.append((f"mass_{tag}", mr is not None and 0.75 <= mr <= 1.25))
    s = sham.get((r["L"], r["seed"]))
    if s is not None:
        a, b = f(r, "mass_ratio_2048"), f(s, "mass_ratio_2048")
        tests.append(("vs_sham", a is not None and b is not None and abs(a - b) <= 0.15))
    fails = [t for t, ok in tests if not ok]
    return (not fails), ("OK" if not fails else "|".join(fails))


# ------------------------------------------------------------------ summary
summary = {"mission": "ROUTE_E_DYNAMIC_SOURCE_CAPTURE_DEV_04",
           "protocol_sha256": json.loads(Path("t256_branch_manifest.json").read_text())["protocol_sha256"],
           "logical_trajectories": len(rows), "by_size": {}, "ladder": {}, "gates": {}}
man = json.loads(Path("t256_branch_manifest.json").read_text())
summary["engine_invocations"] = man["engine_invocations"]
risk = {}
for b in man["blocks"]:
    risk.setdefault(b["L"], {}).setdefault(b["t256_status"], 0)
    risk[b["L"]][b["t256_status"]] += 1
summary["t256_risk_set"] = {str(k): v for k, v in risk.items()}

for L in SIZES:
    cell = {}
    for a in ARMS:
        g = [r for r in valid if r["arm"] == a and r["L"] == L]
        if not g:
            continue
        M = med(g, "M256") or 1.0
        eps = [endpoint(r) for r in g]
        cell[a] = {
            "n": len(g), "M256_median": M,
            "planned_dose": med(g, "planned_dose"),
            "realized_source_injection": med(g, "realized_source_injection"),
            "realized_sink_removal": med(g, "realized_sink_removal"),
            "delivery_ratio": (med(g, "realized_source_injection") or 0) / (med(g, "planned_dose") or 1)
                              if (med(g, "planned_dose") or 0) > 0 else None,
            "unique_contact": med(g, "unique_contact"),
            "unique_capture_transport": med(g, "unique_capture_transport"),
            "capture_engulfment": med(g, "capture_engulfment"),
            "capture_by_merger": med(g, "capture_by_merger"),
            "direct_operator_insertion": med(g, "direct_operator_insertion"),
            "incorporation_16": med(g, "incorporation_16"),
            "durable_incorporation_128": med(g, "durable_incorporation_128"),
            "unique_incumbent_egress_to_sink": med(g, "unique_incumbent_egress_to_sink"),
            "directional_transit": med(g, "directional_transit"),
            "fresh_current_fraction_postforce": med(g, "fresh_current_fraction_postforce"),
            "fresh_current_fraction_2048": med(g, "fresh_current_fraction_2048"),
            "fresh_retention_2048": med(g, "fresh_retention_2048"),
            "incumbent_current_fraction_2048": med(g, "incumbent_current_fraction_2048"),
            "incumbent_absolute_residual_2048": med(g, "incumbent_absolute_residual_2048"),
            "sink_matched_replacement_2048": med(g, "sink_matched_replacement_2048"),
            "mass_ratio_2048": med(g, "mass_ratio_2048"),
            "survival_1536": sum(1 for r in g if r.get("survival_1536") == "True"),
            "survival_2048": sum(1 for r in g if r.get("survival_2048") == "True"),
            "endpoint_met": sum(1 for ok, _ in eps if ok),
            "failure_reasons": sorted({why for ok, why in eps if not ok}),
            "max_algebraic_ledger_error": max((f(r, "algebraic_ledger_error") or 0) for r in g),
            "max_system_balance_error": max((f(r, "total_system_balance_error") or 0) for r in g),
        }
    summary["by_size"][str(L)] = cell

# dose response
for L in SIZES:
    lad = []
    for a in LADDER:
        c = summary["by_size"][str(L)].get(a)
        if not c:
            continue
        lad.append({"arm": a, "dose": DOSE[a],
                    "delivered_over_M256": (c["realized_source_injection"] or 0) / c["M256_median"],
                    "capture_over_M256": (c["unique_capture_transport"] or 0) / c["M256_median"],
                    "fresh_fraction_2048": c["fresh_current_fraction_2048"],
                    "capture_efficiency": ((c["unique_capture_transport"] or 0) /
                                           (c["realized_source_injection"] or 1)),
                    "survival_2048": c["survival_2048"], "n": c["n"]})
    summary["ladder"][str(L)] = lad

# aggregate gate on the primary arm
PRIM = "D2_REDESIGNED_Q100"
agg = {}
for L in SIZES:
    c = summary["by_size"][str(L)].get(PRIM, {})
    v = risk.get(L, {}).get("T256_VALID_TRACK", 0)
    M = c.get("M256_median", 1.0)
    g = [r for r in valid if r["arm"] == PRIM and r["L"] == L]
    agg[str(L)] = {
        "T256_VALID": f"{v}/9",
        "delivered_source_gate": sum(1 for r in g if (f(r, "realized_source_injection") or 0) >= 0.04 * (f(r, "M256") or 1)),
        "delivered_sink_gate": sum(1 for r in g if (f(r, "realized_sink_removal") or 0) >= 0.04 * (f(r, "M256") or 1)),
        "endpoint": c.get("endpoint_met", 0),
        "sham_failures": summary["by_size"][str(L)]["SHAM"]["n"] - summary["by_size"][str(L)]["SHAM"]["survival_2048"],
    }
summary["gates"] = agg
ok_all = all(int(agg[str(L)]["T256_VALID"].split("/")[0]) >= 7 and agg[str(L)]["endpoint"] >= 7
             for L in SIZES)

# ------------------------------------------------------------- disposition
def disposition():
    p24 = summary["by_size"]["24"].get(PRIM, {})
    p32 = summary["by_size"]["32"].get(PRIM, {})
    if any(int(agg[str(L)]["T256_VALID"].split("/")[0]) < 7 for L in SIZES):
        return "PREPHASE_YIELD_INSUFFICIENT"
    if ok_all:
        return "DYNAMICS_MEDIATED_CAPTURE_DEV"
    def rel(c, k):
        return (c.get(k) or 0.0) / (c.get("M256_median") or 1.0)
    dl = min(rel(p24, "realized_source_injection"), rel(p32, "realized_source_injection"))
    ct = min(rel(p24, "unique_contact"), rel(p32, "unique_contact"))
    cp = min(rel(p24, "unique_capture_transport"), rel(p32, "unique_capture_transport"))
    d128 = min(rel(p24, "durable_incorporation_128"), rel(p32, "durable_incorporation_128"))
    eg = min(rel(p24, "unique_incumbent_egress_to_sink"), rel(p32, "unique_incumbent_egress_to_sink"))
    if dl < 0.04:
        return "SOURCE_DELIVERY_LIMITED"
    if ct < 0.04:
        return "HALO_TRANSPORT_LIMITED"
    if cp < 0.04:
        return "BOUNDARY_ASSIMILATION_LIMITED"
    if d128 < 0.03:
        return "CAPTURE_TRANSIENT_ONLY"
    if eg < 0.04:
        return "COUPLING_LIMITED"
    return "CAPTURE_TRANSIENT_ONLY"


summary["DECISION"] = disposition()
summary["mechanism_flags"] = {
    "LEGACY_FILTER_DELIVERY_LIMITED": all(
        (summary["by_size"][str(L)]["D1_LEGACY_Q005"]["realized_source_injection"] or 0)
        < 0.5 * (summary["by_size"][str(L)]["D1_LEGACY_Q005"]["planned_dose"] or 1) for L in SIZES),
    "REDESIGNED_FILTER_DELIVERY_RESCUED": all(
        (summary["by_size"][str(L)]["D1_REDESIGNED_Q005"]["realized_source_injection"] or 0)
        > 5 * ((summary["by_size"][str(L)]["D1_LEGACY_Q005"]["realized_source_injection"] or 0) + 1e-9)
        for L in SIZES),
    "DIRECT_INTERFACE_EXCHANGE_TOLERATED": all(
        summary["by_size"][str(L)]["DIRECT_INTERFACE_Q100"]["survival_2048"] >= 7 for L in SIZES),
    "ACCRETION_ONLY": all(
        (summary["by_size"][str(L)][PRIM]["incumbent_absolute_residual_2048"] or 0) > 0.9 for L in SIZES),
    "CAPTURE_BY_MERGER": any(
        (summary["by_size"][str(L)][PRIM]["capture_by_merger"] or 0) > 1e-9 for L in SIZES),
    "DYNAMICS_MEDIATED_CAPTURE_FOUND": ok_all,
}
Path("dynamic_source_capture_summary.json").write_text(json.dumps(summary, indent=1))
print("DECISION =", summary["DECISION"])
for L in SIZES:
    print(f"  L={L} risk={summary['t256_risk_set'][str(L)]} gates={agg[str(L)]}")

# ==================================================================== figure
fig, axes = plt.subplots(2, 3, figsize=(15.6, 8.6))
fig.patch.set_facecolor(SURF)
for i, L in enumerate(SIZES):
    a0, a1, a2 = axes[i]
    for ax in (a0, a1, a2):
        ax.set_facecolor(SURF); ax.grid(True, color=GRID, lw=0.8, axis="y", zorder=0)
        for sp in ("top", "right"): ax.spines[sp].set_visible(False)
        for sp in ("left", "bottom"): ax.spines[sp].set_color(GRID)
        ax.tick_params(colors=INK2, labelsize=9)
    S = summary["by_size"][str(L)]
    M = S[PRIM]["M256_median"]

    # --- col 1: the chain, per arm, normalised by M256
    keys = [("realized_source_injection", "injection", C["inj"]),
            ("unique_contact", "contact", C["contact"]),
            ("unique_capture_transport", "capture (transport)", C["capture"]),
            ("incorporation_16", "incorporation 16", C["inc16"]),
            ("fresh_retention_2048", "rétention 2048", C["ret"])]
    show = ["D1_LEGACY_Q005", "D1_REDESIGNED_Q005", "D2_REDESIGNED_Q005",
            "D2_REDESIGNED_Q050", "D2_REDESIGNED_Q100", "DIRECT_INTERFACE_Q100"]
    w = 0.15
    for j, (k, lab, col) in enumerate(keys):
        vals = []
        for a in show:
            c = S.get(a, {})
            v = c.get(k)
            mm = c.get("M256_median") or 1.0
            vals.append(0.0 if v is None else (v / mm if k != "fresh_retention_2048" else v))
        a0.bar([x + (j - 2) * w for x in range(len(show))], vals, w * 0.9,
               color=col, zorder=3, label=lab if i == 0 else None)
    a0.set_yscale("symlog", linthresh=1e-3)
    a0.annotate("filtre P2 :\n0 livré,\n0 capturé", xy=(0, 3e-4), xytext=(0.02, 6e-3),
                color="#b02020", fontsize=8, fontweight="bold", ha="center",
                arrowprops=dict(arrowstyle="->", color="#b02020", lw=1.2))
    a0.set_xticks(range(len(show)))
    a0.set_xticklabels([s.replace("_REDESIGNED", "\nP2'").replace("_LEGACY", "\nP2")
                        .replace("DIRECT_INTERFACE_Q100", "DIRECT\nQ100") for s in show],
                       fontsize=7.4)
    a0.axhline(0.04, color=INK, lw=1.1, ls="--", zorder=4)
    a0.set_ylabel(f"L = {L}\n\nmasse / M₂₅₆", color=INK2, fontsize=10)

    # --- col 2: dose response
    lad = summary["ladder"][str(L)]
    xs = [d["dose"] for d in lad]
    a1.plot(xs, [d["delivered_over_M256"] for d in lad], "o-", color=C["inj"], lw=2.2,
            ms=7, zorder=3, label="livré" if i == 0 else None)
    a1.plot(xs, [d["capture_over_M256"] for d in lad], "s-", color=C["capture"], lw=2.2,
            ms=7, zorder=4, label="capturé (transport)" if i == 0 else None)
    a1.plot(xs, [d["fresh_fraction_2048"] or 0 for d in lad], "^-", color=C["ret"], lw=2.2,
            ms=7, zorder=5, label="fraction fraîche @2048" if i == 0 else None)
    a1.plot(xs, xs, ":", color=INK2, lw=1.4, zorder=2, label="livraison parfaite" if i == 0 else None)
    a1.axhline(0.80, color="#b02020", lw=1.4, zorder=2)
    a1.set_xscale("log"); a1.set_yscale("log")
    a1.set_xticks(xs); a1.set_xticklabels([f"{x:g}" for x in xs], fontsize=8.5)
    a1.set_ylabel("masse / M₂₅₆", color=INK2, fontsize=10)

    # --- col 3: composition at 2048
    comp_arms = ["SHAM", "D2_REDESIGNED_Q005", "D2_REDESIGNED_Q100", "DIRECT_INTERFACE_Q100"]
    inc = [(S.get(a, {}).get("incumbent_current_fraction_2048") or 0) for a in comp_arms]
    fre = [(S.get(a, {}).get("fresh_current_fraction_2048") or 0) for a in comp_arms]
    amb = [max(0.0, 1 - x - y) for x, y in zip(inc, fre)]
    xr = range(len(comp_arms))
    a2.bar(xr, inc, 0.62, color="#8c8b86", zorder=3, label="incumbent" if i == 0 else None)
    a2.bar(xr, amb, 0.62, bottom=inc, color="#c9c8c2", zorder=3, label="ambiant" if i == 0 else None)
    a2.bar(xr, fre, 0.62, bottom=[a + b for a, b in zip(inc, amb)], color=C["capture"],
           zorder=3, label="source fraîche" if i == 0 else None)
    for x, v in zip(xr, fre):
        a2.text(x, 1.02, f"{v*100:.1f}%", ha="center", color=INK, fontsize=8.5, fontweight="bold")
    a2.axhline(0.20, color="#b02020", lw=1.4, zorder=4)
    a2.set_ylim(0, 1.12)
    a2.set_xticks(list(xr))
    a2.set_xticklabels([a.replace("D2_REDESIGNED_", "P2' ").replace("DIRECT_INTERFACE_Q100", "DIRECT\nQ100")
                        for a in comp_arms], fontsize=7.6)
    a2.set_ylabel("composition de la piste", color=INK2, fontsize=10)

axes[0][0].set_title("Chaîne causale par bras (échelle log)", color=INK, fontsize=11.5,
                     fontweight="bold", pad=8)
axes[0][1].set_title("Réponse à la dose, halo gd=2", color=INK, fontsize=11.5,
                     fontweight="bold", pad=8)
axes[0][2].set_title("Composition à t=2048", color=INK, fontsize=11.5, fontweight="bold", pad=8)
axes[1][1].set_xlabel("dose planifiée (× M₂₅₆)", color=INK2, fontsize=10)
axes[0][1].legend(fontsize=7.4, labelcolor=INK2, loc="lower right", frameon=True,
                  facecolor=SURF, edgecolor=GRID, framealpha=0.96)
for i, L in enumerate(SIZES):
    lad = summary["ladder"][str(L)]
    r_d = lad[-1]["delivered_over_M256"] / lad[0]["delivered_over_M256"]
    axes[i][1].annotate(f"dose ×20 → livraison ×{r_d:.1f}\nla source SATURE",
                        xy=(1.0, lad[-1]["delivered_over_M256"]), xytext=(0.09, 0.30),
                        color="#b02020", fontsize=8.6, fontweight="bold",
                        arrowprops=dict(arrowstyle="->", color="#b02020", lw=1.3))
fig.suptitle("Capture dynamique au halo — 18 blocs appariés × 8 bras, horizon 2048",
             color=INK, fontsize=15, fontweight="bold", y=0.985)
fig.text(0.5, 0.945,
         f"protocole scellé AVANT tout appel moteur · DECISION = {summary['DECISION']} · "
         "trait rouge = porte gelée de Route E (résidu ≤ 0,20 ⇔ fraction fraîche ≥ 0,80) · "
         "tiret noir = plancher de porte 0,04 × M₂₅₆",
         ha="center", color=INK2, fontsize=9)
fig.tight_layout(rect=[0, 0.055, 1, 0.925])
h0, l0 = axes[0][0].get_legend_handles_labels()
fig.legend(h0, l0, frameon=False, fontsize=8.6, labelcolor=INK2, ncol=5,
           loc="lower left", bbox_to_anchor=(0.05, 0.008))
h2, l2 = axes[0][2].get_legend_handles_labels()
fig.legend(h2, l2, frameon=False, fontsize=8.6, labelcolor=INK2, ncol=3,
           loc="lower right", bbox_to_anchor=(0.985, 0.008))
fig.savefig("dynamic_source_capture.png", dpi=170, facecolor=SURF)
print("figure -> dynamic_source_capture.png")
