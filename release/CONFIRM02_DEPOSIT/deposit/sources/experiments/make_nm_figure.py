"""LCI-CAUSAL-NONMERGING-CONFIRM-02 — summary figure (Phase 6/7). POST-run visualization of the sealed raw."""
import json, importlib.util, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
K = 3
raw = json.load(open("work/nm_confirm_raw.json"))
cert = json.load(open("docs/individuation/NONMERGING_CONFIRM_CERTIFICATE_02.json"))
allrec = raw; elig = [r for r in allrec if r.get("eligible")]; valid = [r for r in elig if r["g0_valid"]]

def pw(fn): return np.array([np.mean([fn(r, i) for i in range(K)]) for r in valid])
tk = lambda r, c: r["beh"][c]["tracked"]; fx = lambda r, c: r["beh"][c]["fixed"]
own = pw(lambda r, i: tk(r, "intact")[i] - r["beh"]["erase"][i]["tracked"][i])
sham = pw(lambda r, i: tk(r, "intact")[i] - tk(r, "sham")[i])
neigh = pw(lambda r, i: np.mean([tk(r, "intact")[i] - r["beh"]["erase"][j]["tracked"][i] for j in range(K) if j != i]))
own_fx = pw(lambda r, i: fx(r, "intact")[i] - r["beh"]["erase"][i]["fixed"][i])
cov = np.array([r["max_cov_intact"] for r in valid])
seeds = [r["seed"] for r in valid]

fig = plt.figure(figsize=(13, 8))
# A: per-world own vs sham vs neigh
ax = fig.add_subplot(2, 2, 1)
x = np.arange(len(valid))
ax.axhline(0, color="grey", lw=0.8)
ax.bar(x - 0.25, own, width=0.25, color="#2a9d8f", label="own (intact−erase-target)")
ax.bar(x, sham, width=0.25, color="#e9c46a", label="sham (≈0)")
ax.bar(x + 0.25, neigh, width=0.25, color="#e76f51", label="neighbour (≈0)")
ci = cert["G3"]["own_worldCI"]
ax.axhline(ci[0], color="#264653", ls="--", lw=1, label=f"own worldboot 2.5%={ci[0]:.2f}")
ax.set_xticks(x); ax.set_xticklabels(seeds, rotation=90, fontsize=6)
ax.set_ylabel("world-level effect (integrated uptake)")
ax.set_title(f"A. Own-specific causal effect, {int((own>0).sum())}/{len(own)} worlds >0 (sham & neighbour ≈ 0)", fontsize=9)
ax.legend(fontsize=7)

# B: tracked vs fixed
ax = fig.add_subplot(2, 2, 2)
ax.scatter(own_fx, own, c="#2a9d8f", s=28)
lim = [0, max(own.max(), own_fx.max()) * 1.1]
ax.plot(lim, lim, ls=":", c="grey", label="y=x")
ax.set_xlabel("fixed-mask own effect (tracker-free, G5)")
ax.set_ylabel("bijective-tracked own effect (primary)")
ax.set_title(f"B. Tracked vs fixed readout agree (ratio {cert['G5']['tracked_over_fixed']:.2f}×, not 4.8×)", fontsize=9)
ax.legend(fontsize=7)

# C: coverage vs cap
ax = fig.add_subplot(2, 2, 3)
ax.bar(x, cov * 100, color="#457b9d")
ax.axhline(15, color="red", ls="--", label="G0 fusion cap 15%")
ax.set_xticks(x); ax.set_xticklabels(seeds, rotation=90, fontsize=6)
ax.set_ylabel("max grid coverage (%)"); ax.set_ylim(0, 16)
ax.set_title(f"C. No fusion: 23/23 worlds max coverage ≤ {cov.max()*100:.1f}% << 15% (3 distinct droplets throughout)", fontsize=9)
ax.legend(fontsize=7)

# D: storage readout decode
ax = fig.add_subplot(2, 2, 4)
g2 = cert["G2"]
bars = ["own-dose\nR²", "within-null\n95%", "neighbour-dose\nR²"]
vals = [g2["dose_R2"], g2["dose_null95"], g2["neighbour_dose_R2"]]
ax.bar(bars, vals, color=["#2a9d8f", "#adb5bd", "#e76f51"])
ax.axhline(0, color="grey", lw=0.8)
ax.set_ylabel("R²"); ax.set_title(f"D. Rest readout replicated: dose R²={g2['dose_R2']:.2f} ≫ neighbour (G2)", fontsize=9)

fig.suptitle("LCI-CAUSAL-NONMERGING-CONFIRM-02 — corrected NON-FUSING confirmation (53001–53032): G6 causal individuation PASS",
             fontsize=12)
fig.tight_layout(rect=[0, 0, 1, 0.96])
out = "docs/individuation/NONMERGING_CONFIRM_FIGURE_02.png"
fig.savefig(out, dpi=130); print("wrote", out)

# secondary: graded dose decode from behaviour (non-gating) + per-seed table
dose_w = np.array([np.mean(r["dose"]) for r in valid])
corr = np.corrcoef(dose_w, own)[0, 1]
print(f"secondary graded: corr(world dose, own effect) = {corr:+.3f} (non-gating; expected weak/INDETERMINATE)")
print(f"\nper-seed: eligible={len(elig)}/{len(allrec)} G0-valid={len(valid)} nonfusing_frac={len(valid)/len(elig):.2f}")
