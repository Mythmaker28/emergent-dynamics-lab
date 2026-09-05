import numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
CAP,L=16,36; CELLS=L*L
fig=plt.figure(figsize=(13.5,7.6)); gs=fig.add_gridspec(2,3,width_ratios=[1.7,1,1],
                                                        hspace=.33,wspace=.3)
def load(t):
    z=np.load("/home/claude/ORR01/raw/%s.npz"%t,allow_pickle=True)
    return z, list(z["fields"]), z["series"]
za,Fa,A=load("conf__ADDITIVE_CONTROL__seed5001")
zr,Fr,Rr=load("conf__REPAIRED__seed5001")
ax=fig.add_subplot(gs[0,0])
ax.plot(A[:,Fa.index("step")],A[:,Fa.index("O_total")]/CELLS,lw=1.6,color="#c53030",
        label="additive LawSpec")
ax.plot(Rr[:,Fr.index("step")],Rr[:,Fr.index("O_total")]/CELLS,lw=1.6,color="#2f855a",
        label="repaired LawSpec (balanced exchange)")
ax.axhline(CAP,color="k",ls="--",lw=1); ax.text(200,CAP-0.7,"CAP = 16: the lattice is full",fontsize=8)
ax.set_ylabel("occupancy per cell"); ax.set_xlabel("step"); ax.grid(alpha=.25)
ax.legend(fontsize=8,loc="center right")
ax.set_title("paired seed 5001 — the ratchet, and its removal\nadditive drift 1.6275, repaired "
             "drift 0.00000 (exactly constant)",fontsize=10)
ax=fig.add_subplot(gs[1,0])
ax.plot(A[:,Fa.index("step")],A[:,Fa.index("N_X")],lw=1.2,color="#c53030",label="additive")
ax.plot(Rr[:,Fr.index("step")],Rr[:,Fr.index("N_X")],lw=1.2,color="#2f855a",label="repaired")
ax.axhline(50,color="k",ls=":",lw=1); ax.text(200,54,"N_KEEP = 50",fontsize=8)
ax.set_xlabel("step"); ax.set_ylabel("N_X (body molecules)"); ax.grid(alpha=.25)
ax.legend(fontsize=8); ax.set_title("the body population over the same 10250 steps",fontsize=10)
for j,(t,ttl) in enumerate([("conf__ADDITIVE_CONTROL__seed5001","additive LawSpec"),
                            ("conf__REPAIRED__seed5001","repaired LawSpec")]):
    z,_,_=load(t)
    occ=z["nX_final"]+z["nY_final"]+z["nSX_final"]+z["nSY_final"]+z["nWX_final"]+z["nWY_final"]
    ax=fig.add_subplot(gs[j,1])
    im=ax.imshow(z["nX_final"],cmap="Blues",vmin=0,vmax=max(1,int(z["nX_final"].max())))
    ys,xs=np.nonzero(z["nY_final"]>0); ax.plot(xs,ys,"r+",ms=11,mew=2.2)
    ax.set_title("%s\nfinal body, N_X = %d"%(ttl,int(z["nX_final"].sum())),fontsize=9)
    ax.set_xticks([]);ax.set_yticks([]);plt.colorbar(im,ax=ax,fraction=.046)
    ax=fig.add_subplot(gs[j,2])
    im=ax.imshow(CAP-occ,cmap="Reds_r",vmin=0,vmax=12)
    ax.set_title("final free capacity\nmean %.2f of %d"%((CAP-occ).mean(),CAP),fontsize=9)
    ax.set_xticks([]);ax.set_yticks([]);plt.colorbar(im,ax=ax,fraction=.046)
fig.suptitle("ORR01 — the balanced exchange removes the occupancy ratchet exactly; the body "
             "survives but does not localise",fontsize=12)
fig.savefig("/home/claude/ORR01/out/orr01_repair.png",dpi=130,bbox_inches="tight")
print("figure written")
