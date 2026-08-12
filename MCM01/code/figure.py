import glob, json
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
CAP, L = 16, 36; CELLS = L*L

def blocks(a, F, muX, nb=20):
    n = len(a); B = n // nb; r = []
    for i in range(nb):
        s = a[i*B:(i+1)*B]
        c = lambda k: float(s[:, F.index(k)].mean())
        O = (s[:,F.index("N_X")]+s[:,F.index("N_Y")]+s[:,F.index("N_SX")]+s[:,F.index("N_SY")]
             +s[:,F.index("N_WX")]+s[:,F.index("N_WY")]).mean()
        r.append((float(s[len(s)//2, F.index("step")]), c("N_X"), c("accepted_births_X")/muX,
                  c("free_at_org"), CAP - O/CELLS, c("c_X_per_org")))
    return np.array(r)

fig = plt.figure(figsize=(13.5, 7.4))
gs = fig.add_gridspec(2, 3, width_ratios=[1.7, 1, 1], hspace=0.34, wspace=0.3)
sel = [("/home/claude/MCM01/raw/cal__p3_mu0.002_phi0.1_ell2.5__seed1001.npz", 0.002,
        "muX=0.002  phi=0.10  ell_X=2.5"),
       ("/home/claude/MCM01/raw/cal__p1_mu0.004_phi0.4_ell2.5__seed1001.npz", 0.004,
        "muX=0.004  phi=0.40  ell_X=2.5")]

for row, (path, muX, ttl) in enumerate(sel):
    z = np.load(path, allow_pickle=True); F = list(z["fields"]); a = z["series"]
    b = blocks(a, F, muX)
    ax = fig.add_subplot(gs[row, 0])
    ax.plot(b[:,0], b[:,1], "o-", ms=3.5, lw=1.5, color="#2b6cb0", label="N_X realised")
    ax.plot(b[:,0], b[:,2], "s--", ms=3.5, lw=1.5, color="#2f855a",
            label="sustainable N_X = births/muX")
    ax.set_xlabel("step"); ax.set_ylabel("body molecules"); ax.grid(alpha=.25)
    ax2 = ax.twinx()
    ax2.plot(b[:,0], b[:,3], "^-", ms=3.5, lw=1.4, color="#c53030",
             label="free capacity at the organiser cell")
    ax2.plot(b[:,0], b[:,4], "v:", ms=3.5, lw=1.2, color="#dd6b20",
             label="free capacity per cell, lattice mean")
    ax2.set_ylabel("free capacity", color="#c53030")
    ax.set_title("%s  —  block means, 20 blocks\nthe cloud forms, then follows its own falling "
                 "sustainable level down" % ttl, fontsize=10)
    if row == 0:
        h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
        ax.legend(h1+h2, l1+l2, fontsize=8, loc="upper right")

    zz = z
    occ = (zz["nX_final"]+zz["nY_final"]+zz["nSX_final"]+zz["nSY_final"]
           +zz["nWX_final"]+zz["nWY_final"])
    ax = fig.add_subplot(gs[row, 1])
    im = ax.imshow(zz["nX_final"], cmap="Blues", vmin=0,
                   vmax=max(1, int(zz["nX_final"].max())))
    ys, xs = np.nonzero(zz["nY_final"] > 0)
    ax.plot(xs, ys, "r+", ms=11, mew=2.2)
    ax.set_title("final body molecules, N_X=%d\norganiser marked in red"
                 % int(zz["nX_final"].sum()), fontsize=9)
    ax.set_xticks([]); ax.set_yticks([]); plt.colorbar(im, ax=ax, fraction=.046)
    ax = fig.add_subplot(gs[row, 2])
    im = ax.imshow(CAP - occ, cmap="Reds_r", vmin=0, vmax=3)
    ax.set_title("final free capacity per cell\nmean %.2f of CAP = %d"
                 % ((CAP-occ).mean(), CAP), fontsize=9)
    ax.set_xticks([]); ax.set_yticks([]); plt.colorbar(im, ax=ax, fraction=.046)

fig.suptitle("MCM01 — the feed rule ratchets the lattice to capacity from the first step; "
             "c_X at the organiser, the birth rate and the sustainable population fall with it",
             fontsize=12)
fig.savefig("/home/claude/MCM01/out/mcm01_ratchet.png", dpi=130, bbox_inches="tight")
print("figure written")
