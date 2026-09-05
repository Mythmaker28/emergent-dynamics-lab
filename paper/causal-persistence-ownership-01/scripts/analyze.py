"""Portable same-data reconstruction, tables and figures. No engine imports.

The historical 03M algorithm is run unchanged with a byte-source adapter.
The additional least-squares and causal reconstruction is a separate check.
"""
from pathlib import Path
import csv
import hashlib
import importlib.util
import json
import sys
from collections import Counter
import numpy as np
from scipy.stats import t, binomtest
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "results"
FIG = ROOT / "figures"


def save(path, obj):
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")


def interval(values):
    x = np.asarray(values, dtype=float)
    m = float(x.mean())
    h = float(t.ppf(.975, len(x)-1) * x.std(ddof=1) / np.sqrt(len(x)))
    return {"mean": m, "lower": m-h, "upper": m+h}


def table(path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader(); w.writerows(rows)


def verify():
    manifest = json.loads((ROOT / "INPUT_MANIFEST.json").read_text())
    for row in manifest["files"]:
        p = ROOT / row["path"]
        assert p.resolve().is_relative_to(ROOT.resolve())
        content = p.read_bytes()
        assert len(content) == row["bytes"]
        assert hashlib.sha256(content).hexdigest() == row["sha256"], row["path"]
        if row.get("protected_in_raw_binding"):
            bound = content if row["raw_binding_match"] == "exact Git bytes" else content.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
            assert hashlib.sha256(bound).hexdigest() == row["raw_working_file_sha256"]
    return manifest


def main():
    OUT.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
    manifest = verify()
    p = DATA / "analysis/lci-turnover-raw-reproduction-03m/independent_crosscheck_03m.py"
    spec = importlib.util.spec_from_file_location("historical_raw_only_03m", p)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    mod.committed_bytes = lambda repo, relative: (DATA / relative).read_bytes()
    hist = mod.run(DATA)
    # Keep the historical output including wording solely as an audit comparison.
    save(OUT / "HISTORICAL_03M_REPLAY.json", hist)
    run = DATA / "results/LCI-TURNOVER-PROSPECTIVE-03G"
    raw_manifest = json.loads((run / "raw_manifest_03g.json").read_text())
    records = [json.loads((run / r["path"]).read_text()) for r in raw_manifest["entries"]]
    valid = [r for r in records if r["feasibility"]["valid"]]
    n = len(valid)
    world_rows = []
    effects = {k: [] for k in ["own", "own_minus_sham", "own_minus_neighbour", "fixed_within_branch", "plus_ablation_residual", "half_own_minus_residual", "full_ablation_residual"]}
    retention = []; cross = []
    for r in valid:
        sc = r["scientific"]; b = sc["causal_intervention_battery"]["deep"]
        intact = np.asarray(b["intact"]["tracked"])
        er = np.asarray([v["tracked"] for v in b["erase"]])
        own = intact-np.diag(er)
        other = intact-(er.sum(axis=0)-np.diag(er))/2
        residual = np.asarray(b["ablate_plus"]["tracked"])-np.diag([v["tracked"] for v in b["erase_ablate_plus"]])
        vals = {"own": own.mean(), "own_minus_sham": (np.asarray(b["sham"]["tracked"])-np.diag(er)).mean(),
                "own_minus_neighbour": (own-other).mean(),
                "fixed_within_branch": (np.asarray(b["intact"]["fixed"])-np.diag([v["fixed"] for v in b["erase"]])).mean(),
                "plus_ablation_residual": residual.mean(), "half_own_minus_residual": (.5*own-residual).mean(),
                "full_ablation_residual": (np.asarray(b["ablate_full"]["tracked"])-np.diag([v["tracked"] for v in b["erase_ablate_full"]])).mean()}
        for k, v in vals.items(): effects[k].append(float(v))
        retention.extend(sc["material_tracer"]["deep_M"])
        # Trajectories are sampled every ten steps, so these cross fractions are
        # retained sampled observations, not falsely asserted exact deep snapshots.
        for frame in sc["material_tracer"]["trajectory"]:
            for item in frame.get("per", []):
                if item and item.get("M"):
                    cross.extend(item["M"].get("cross", {}).values())
        world_rows.append({"seed": r["seed"], "deep_step": sc["snapshot_time"],
                           "intact_uptake": float(intact.mean()), "fractional_own_reduction": float((own/intact).mean()),
                           "M_min": min(sc["material_tracer"]["deep_M"]), "M_max": max(sc["material_tracer"]["deep_M"]), **vals})
    y = np.array([v for r in valid for v in r["scientific"]["histories"]["own_dose"]])
    worlds = np.repeat(np.arange(n), 3)
    loss = {}; predictions = {}; base = np.zeros(n)
    for scope in ["L", "N", "E", "Gm", "B", "P", "Gf"]:
        X = np.array([v for r in valid for v in r["scientific"]["scopes"]["values"][scope]])
        loss[scope] = np.zeros(n); predictions[scope] = np.zeros(3*n)
        for i in range(n):
            tr = worlds != i; te = ~tr
            mu = X[tr].mean(0); sd = X[tr].std(0); keep = sd > 1e-12
            A = (X[tr][:, keep]-mu[keep])/sd[keep]
            T = (X[te][:, keep]-mu[keep])/sd[keep]
            ym = y[tr].mean(); var = max(float(y[tr].var()), 1e-15)
            coef = np.linalg.lstsq(np.vstack([A, np.eye(sum(keep))]), np.r_[y[tr]-ym, np.zeros(sum(keep))], rcond=None)[0]
            pred = T@coef+ym; predictions[scope][te] = pred
            loss[scope][i] = np.mean((y[te]-pred)**2)/var
            base[i] = np.mean((y[te]-ym)**2)/var
    comparisons = {s: interval(loss[s]-loss["L"]) for s in ["N", "E", "Gm", "B"]}
    causal = {k: {**interval(v), "n_positive": int(np.sum(np.asarray(v)>0)), "n_nonzero": int(np.count_nonzero(v)),
                  "sign_test_p_one_sided": float(binomtest(int(np.sum(np.asarray(v)>0)), int(np.count_nonzero(v)), .5, alternative="greater").pvalue) if np.count_nonzero(v) else 1.0} for k, v in effects.items()}
    check = []
    for k, old in [("own", "own_t95"), ("own_minus_sham", "own_minus_sham_t95"), ("own_minus_neighbour", "own_minus_neighbour_t95"), ("fixed_within_branch", "own_fixed_t95"), ("plus_ablation_residual", "own_under_lambda_plus_only_ablation_t95")]:
        check.extend(abs(causal[k][s]-hist["causal"][old][s]) for s in ["mean", "lower", "upper"])
    for k in comparisons:
        check.extend(abs(comparisons[k][s]-hist["ownership"]["G_LOCAL_EXCLUSION"]["comparisons"][k]["t95"][s]) for s in ["mean", "lower", "upper"])
    assert max(check) < 1e-10
    eligibility = Counter("valid" if r["feasibility"]["valid"] else "ineligible" if not r["feasibility"]["eligible"] else "split" if "SPLIT" in (r["feasibility"]["reason"] or "") else "lost" if "LOST" in (r["feasibility"]["reason"] or "") else "other" for r in records)
    result = {"status": "SAME_DATA_RECONSTRUCTION_NO_NEW_WORLDS", "input_files_verified": len(manifest["files"]),
              "n_worlds": len(records), "n_valid": n, "n_targets": 3*n, "feasibility": dict(eligibility),
              "valid_seed_ids": [r["seed"] for r in valid], "M_min": min(retention), "M_max": max(retention),
              "sampled_cross_fraction_max": max(cross), "sampled_cross_values": len(cross),
              "deep_step_min": min(r["deep_step"] for r in world_rows), "deep_step_max": max(r["deep_step"] for r in world_rows),
              "causal": causal, "fold_descriptive_comparisons": comparisons, "own_skill": interval(base-loss["L"]),
              "intact_uptake_mean": float(np.mean([r["intact_uptake"] for r in world_rows])),
              "fractional_own_reduction_mean": float(np.mean([r["fractional_own_reduction"] for r in world_rows])),
              "fractional_own_reduction_world_min": min(r["fractional_own_reduction"] for r in world_rows),
              "fractional_own_reduction_world_max": max(r["fractional_own_reduction"] for r in world_rows),
              "permutation_p_diagnostic": hist["ownership"]["G_OWN_PERM"]["p_value"] if "p_value" in hist["ownership"]["G_OWN_PERM"] else hist["ownership"]["G_OWN_PERM"],
              "historical_gates": hist["gates"], "historical_outcome_code": hist["outcome"],
              "max_difference_vs_historical_03m": max(check), "science_worlds_run": 0,
              "engine_imports": [x for x in sys.modules if x=="edlab" or x.startswith("edlab.")]}
    assert result["engine_imports"] == []
    save(OUT / "SUMMARY.json", result)
    table(OUT / "WORLD_LEVEL_DATA.csv", world_rows)
    table(OUT / "COHORT_ACCOUNTING.csv", [{"seed": r["seed"], **r["feasibility"]} for r in records])
    table(OUT / "PREDICTIONS.csv", [{"seed": valid[i//3]["seed"], "target": i%3, "own_dose": y[i], **{s: predictions[s][i] for s in loss}} for i in range(3*n)])
    table(OUT / "FOLD_LOSSES.csv", [{"seed": valid[i]["seed"], "baseline": base[i], **{s: loss[s][i] for s in loss}} for i in range(n)])
    tokens = {"N_WORLD": str(len(records)), "N_VALID": str(n), "N_TARGET": str(3*n), "N_INVALID": str(len(records)-n),
              "N_INELIGIBLE": str(eligibility["ineligible"]), "N_SPLIT": str(eligibility["split"]), "N_LOST": str(eligibility["lost"]),
              "N_ELIGIBLE": str(len(records)-eligibility["ineligible"]),
              "N_TRACK_CENSORED": str(eligibility["split"]+eligibility["lost"]),
              "M_MIN": f"{min(retention):.4f}", "M_MAX": f"{max(retention):.4f}",
              "DEEP_MIN": str(result["deep_step_min"]), "DEEP_MAX": str(result["deep_step_max"]),
              "SKILL": f"{result['own_skill']['mean']:.4f}", "N_INPUT": str(len(manifest["files"])),
              "MAX_REPRO_DIFF": f"{max(check):.2e}", "INTACT_MEAN": f"{result['intact_uptake_mean']:.4f}",
              "OWN_RELATIVE_PERCENT": f"{100*result['fractional_own_reduction_mean']:.2f}",
              "OWN_RELATIVE_MIN": f"{100*result['fractional_own_reduction_world_min']:.2f}",
              "OWN_RELATIVE_MAX": f"{100*result['fractional_own_reduction_world_max']:.2f}"}
    for key, values in causal.items():
        tokens[key.upper()] = f"{values['mean']:.4f}"
        tokens[key.upper()+"_CI"] = f"[{values['lower']:.4f}, {values['upper']:.4f}]"
    for key, values in comparisons.items():
        tokens["ADV_"+key.upper()] = f"{values['mean']:.4f}"
        tokens["ADV_"+key.upper()+"_BAND"] = f"[{values['lower']:.4f}, {values['upper']:.4f}]"
    tokens["OWN_SIGN_P"] = f"{causal['own']['sign_test_p_one_sided']:.3g}"
    tokens["ATTENUATION_PERCENT"] = f"{100*(1-causal['plus_ablation_residual']['mean']/causal['own']['mean']):.1f}"
    save(OUT / "TEXT_VALUES.json", tokens)
    plot_figures(result, world_rows, retention, loss, base, y, predictions)
    print(json.dumps({"status": "PASS", "worlds": len(records), "valid": n, "input_files_verified": len(manifest["files"]), "max_diff": max(check), "new_worlds": 0}))


def finish(fig, name):
    fig.savefig(FIG / (name+".png"), dpi=220, bbox_inches="tight", facecolor="white", metadata={"Software": "EDL paper reconstruction"})
    fig.savefig(FIG / (name+".pdf"), bbox_inches="tight", metadata={"Creator": "EDL paper reconstruction", "CreationDate": None, "ModDate": None})
    plt.close(fig)


def plot_figures(result, rows, retention, loss, base, y, preds):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                         "axes.labelsize": 10, "axes.titlesize": 11, "pdf.fonttype": 42})
    blue = "#21618C"; orange = "#B66328"; gray = "#6D7780"
    fig, axs = plt.subplots(1, 2, figsize=(8.1, 3.1), gridspec_kw={"width_ratios": [1, 1.1]})
    vals = [result["feasibility"].get(x, 0) for x in ["ineligible", "split", "lost", "valid"]]
    axs[0].barh(["Not initially eligible", "Split before threshold", "Lost before threshold", "Valid worlds"], vals, color=[gray,gray,gray,blue])
    for i,v in enumerate(vals): axs[0].text(v+.4,i,str(v),va="center")
    axs[0].set_xlim(0,25); axs[0].set_xlabel("Worlds (all 50 accounted for)"); axs[0].invert_yaxis(); axs[0].set_title("a  World accounting", loc="left")
    for i,r in enumerate(rows):
        vals=[r["M_min"],r["M_max"]]
        axs[1].plot([r["deep_step"]]*2, vals, color=blue, lw=1.2, alpha=.6)
        axs[1].scatter([r["deep_step"]]*2,vals,s=13,color=blue,alpha=.75)
    axs[1].axhline(.25,color=orange,ls="--",lw=1)
    axs[1].set_xlabel("Steps after tracer marking"); axs[1].set_ylabel("Own marked material / current mass")
    axs[1].set_title("b  Within-world target ranges",loc="left"); axs[1].set_ylim(0,.27)
    fig.tight_layout(w_pad=2); finish(fig,"figure_1_population_turnover")
    keys=["own","own_minus_sham","own_minus_neighbour","fixed_within_branch","plus_ablation_residual","half_own_minus_residual"]
    labels=["Target erasure effect", "Target effect minus sham effect", "Target effect minus neighbour effect", "Masks held fixed within each branch", "Residual with uptake channel disabled", "Half target effect minus residual*"]
    fig,ax=plt.subplots(figsize=(8.1,3.65))
    jitter=np.linspace(-.13,.13,len(rows))
    for i,k in enumerate(keys):
        d=result["causal"][k]; c=orange if i>=4 else blue
        ax.scatter([r[k] for r in rows],i+jitter,s=14,color=c,alpha=.35)
        ax.errorbar(d["mean"],i,xerr=[[d["mean"]-d["lower"]],[d["upper"]-d["mean"]]],fmt="o",color=c,capsize=4,lw=1.8)
    ax.axvline(0,color=gray,lw=.8);ax.set_yticks(range(len(keys)),labels);ax.invert_yaxis()
    ax.set_xlabel("World-average integrated uptake contrast (simulation units)")
    ax.set_title("Points: 21 worlds; bars: world-level 95% t intervals.  *Post hoc.",loc="left",fontsize=10)
    fig.tight_layout();finish(fig,"figure_2_causal_contrasts")
    fig,ax=plt.subplots(figsize=(8.1,3.25))
    for i,s in enumerate(["N","E","Gm","B"]):
        d=result["fold_descriptive_comparisons"][s]
        ax.scatter(loss[s]-loss["L"],i+np.linspace(-.12,.12,len(rows)),s=16,alpha=.4,color=blue)
        ax.errorbar(d["mean"],i,xerr=[[d["mean"]-d["lower"]],[d["upper"]-d["mean"]]],fmt="o",color=blue,capsize=4,lw=1.8)
    ax.axvline(0,color=orange,ls="--",lw=1)
    ax.set_yticks(range(4),["N: nearest-target memory (11)","E: memory-masked radial summary (24)","Gm: memory-masked global summary (18)","B: body/field baseline (8)"]);ax.invert_yaxis()
    ax.set_xlabel("Comparator NMSE minus target-memory NMSE; positive favours L")
    ax.set_title("Frozen descriptive fold bands; coverage for generalization is not established",loc="left",fontsize=10)
    fig.tight_layout();finish(fig,"figure_3_access_comparisons")
    fig,axs=plt.subplots(1,3,figsize=(8.1,2.7),sharex=True,sharey=True)
    for ax,s in zip(axs,["L","E","B"]):
        ax.scatter(y,preds[s],s=20,c=np.repeat(np.arange(len(rows)),3),cmap="viridis",alpha=.85)
        lim=[min(y.min(),min(preds[z].min() for z in ['L','E','B']))-.001,max(y.max(),max(preds[z].max() for z in ['L','E','B']))+.001]
        ax.plot(lim,lim,color=gray,lw=.8);ax.set_xlim(lim);ax.set_ylim(lim);ax.set_title(s);ax.set_xlabel("History amplitude sum")
    axs[0].set_ylabel("Held-world prediction")
    fig.tight_layout();finish(fig,"figure_4_predictions")
    fig,ax=plt.subplots(figsize=(8.1,3.6));ax.set_xlim(0,1);ax.set_ylim(0,1);ax.axis("off")
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    boxes=[(.01,.66,.28,.27,"INITIALIZE + SELECT\n800 warm-up steps\nThree separated components"),
           (.36,.66,.28,.27,"WRITE HISTORY\nTwo nutrient phases (60 each)\nThen settle 120 steps"),
           (.71,.66,.28,.27,"MARK MATERIAL\nLabel each current target mask\nStart bijective tracking"),
           (.71,.20,.28,.27,"TURNOVER MONITOR\nWriting remains active\nFirst all-three M ≤ 0.25"),
           (.36,.03,.28,.21,"CAUSAL BRANCHES\nErase / sham / ablate\nReset N; settle 40; probe 40"),
           (.36,.34,.28,.21,"PREDICTIVE ACCESS\nExtract fixed scopes\nLeave one entire world out")]
    for x0,y0,w,h,label in boxes:
        ax.add_patch(FancyBboxPatch((x0,y0),w,h,boxstyle="round,pad=0.008",facecolor="#EDF3F7",edgecolor="#7094AD",lw=.8))
        ax.text(x0+w/2,y0+h/2,label,ha="center",va="center",fontsize=8.7,linespacing=1.5)
    for a,b in [((.30,.79),(.35,.79)),((.65,.79),(.70,.79)),((.85,.64),(.85,.49)),((.70,.34),(.65,.43)),((.70,.30),(.65,.14))]:
        ax.add_patch(FancyArrowPatch(a,b,arrowstyle="-|>",mutation_scale=11,color=blue,lw=1))
    ax.text(.015,.42,"Unmet geometry or tracking\nconditions remain in the\n50-world accounting.\n\nOnly jointly valid worlds\nenter the reported assays.",fontsize=9,va="top",color=gray,linespacing=1.6)
    fig.tight_layout();finish(fig,"figure_5_protocol")


if __name__ == "__main__":
    main()
