#!/usr/bin/env python3
"""
observe_droplet.py  --  scientific observer for the IsingV3 / emergent-dynamics-lab droplet.

Deterministic recomputation from the COMMITTED frozen architecture (C1c; commit 1f8f789, H2-CERT-01).
No physics is added or tuned here. This is an OBSERVATION / AUDIT instrument, not proof by animation.

The droplet's memory is an ENGINEERED cumulative causal memory (h1). It is NOT identity, life, a genome,
consciousness, or an individual essence.

NOTE: the substrate self-organises into MANY small droplets; the analyses track the single LARGEST
connected entity (~30-55 active cells). The viewer outlines that tracked entity in red.

Usage (Windows PowerShell, from the repo root):
    python scripts\observe_droplet.py --help
    python scripts\observe_droplet.py --preset turnover --live
    python scripts\observe_droplet.py --preset turnover --export --contact --output outputs\turnover.gif

Presets:  basic | turnover | h1-memory | erase-transplant | h2-killswitch
Live controls:  Space=pause/resume  Left/Right=step(paused)  R=restart  S=screenshot  Q/Escape=quit
"""
import argparse, json, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
import numpy as np

C1C = dict(eta_w=0.015, eta_d1=0.35, eta_d2=0.006, k_exp=1.0)   # frozen writing (WD-01 Phase C)
COMMIT = "1f8f789 (H2-CERT-01) / C1c frozen"
MANIFEST = os.path.join(REPO, "results", "h2cert", "h2cert_prospective_manifest.json")


def _engines():
    from edlab.experiments.sc_mcm import config as C, harness as H
    from edlab.experiments.sc_mcm.engine import MultiChannelMemoryEngine, MCParams
    from edlab.experiments.sc_hmc.harness import PulseChaseTracer
    def mk(tracer, lam_plus=0.25, lam_minus=0.15):
        return MultiChannelMemoryEngine(C.SPEC, MCParams(lam_plus=lam_plus, lam_minus=lam_minus, **C1C), tracer)
    return C, H, mk, PulseChaseTracer


def _default_history(seed_idx=0):
    try:
        m = json.load(open(MANIFEST))
        return m["prospective"]["seeds"][seed_idx % len(m["prospective"]["seeds"])], m["prospective"]["histories"][0]
    except Exception:
        return 38501, [0.008988376206604445, 0.00614248117572431]


def _apply_history(H, eng, body, a_e, a_l, T=60, settle=20):
    cur = H.erase_memory(body).copy()
    for a in (a_e, a_l):
        for _ in range(T):
            cur.N = cur.N + a
            cur = eng.step(cur)
    return H.advance(eng, cur, settle)


def _relabel(st):
    out = st.copy(); out.C = np.stack([out.rho.copy(), np.zeros_like(out.rho)]); return out


def _frame(H, st):
    e = H.largest(st)
    old = st.C[0]; new = st.C[1]
    oldfrac_field = np.where(st.rho > 1e-4, old / np.maximum(old + new, 1e-9), np.nan)
    m = st.mem()
    mask = np.zeros_like(st.rho, dtype=bool)
    if e is not None:
        mask[e.cells[:, 0], e.cells[:, 1]] = True
    interior = mask & np.roll(mask, 1, 0) & np.roll(mask, -1, 0) & np.roll(mask, 1, 1) & np.roll(mask, -1, 1)
    bnd = mask & ~interior
    fr = dict(rho=st.rho.copy(), oldfrac=oldfrac_field, m1=m[0].copy(), m2=m[1].copy(),
              mplus=(m[0] + m[1]).copy(), mminus=(m[0] - m[1]).copy(), N=st.N.copy(), c=st.c.copy(),
              boundary=bnd, step=int(st.step), size=(0 if e is None else int(e.size)))
    if e is not None:
        ys, xs = e.cells[:, 0], e.cells[:, 1]
        cm = np.asarray(e.cohort_mass); fr["M"] = float(cm[0] / (cm.sum() + 1e-9))
        fr["mplus_mean"] = float((m[0] + m[1])[ys, xs].mean())
        fr["mminus_std"] = float((m[0] - m[1])[ys, xs].std())
    else:
        fr["M"] = np.nan; fr["mplus_mean"] = np.nan; fr["mminus_std"] = np.nan
    return fr


def build_trajectory(preset, seed, max_steps, stride):
    C, H, mk, PC = _engines()
    seed0, hist = _default_history()
    if seed is None:
        seed = seed0
    a_e, a_l = hist
    print("[observe] warming seed %d (frozen C0 warmup, %d steps) ..." % (seed, C.WARMUP), flush=True)
    body = H.warmup(seed)
    if preset == "basic":
        st = H.erase_memory(body).copy()
        eng = mk(C.TRACER)
        label = "A/basic: substrate droplets (no imposed history); red outline = tracked largest entity"
    else:
        eng = mk(C.TRACER)
        st = _apply_history(H, eng, body, a_e, a_l)
        st = _relabel(st)
        eng = mk(PC())
        label = "B/turnover: frozen C1c, seed %d, committed history a_e=%.4f a_l=%.4f" % (seed, a_e, a_l)
    frames = [_frame(H, st)]
    for step in range(1, max_steps + 1):
        st = eng.step(st)
        if step % stride == 0:
            frames.append(_frame(H, st))
    print("[observe] captured %d frames (to step %d)." % (len(frames), max_steps), flush=True)
    return frames, label, seed


PANELS = [("rho", "body density (red = tracked entity)", "viridis", 0, None),
          ("oldfrac", "old/new material (1=old,0=new)", "coolwarm", 0, 1),
          ("N", "nutrient N", "YlGn", None, None),
          ("m1", "memory m1 (fast)", "RdBu_r", -1, 1),
          ("m2", "memory m2 (slow)", "RdBu_r", -1, 1),
          ("c", "attractant c", "YlOrBr", None, None),
          ("mplus", "m+ = m1+m2  (h1 / uptake)", "RdBu_r", -2, 2),
          ("mminus", "m- = m1-m2  (order channel)", "PuOr", -1, 1)]


def _bnd_rgba(b):
    rgba = np.zeros(b.shape + (4,)); rgba[..., 0] = 1.0; rgba[..., 3] = b.astype(float); return rgba


def make_figure(frames, label, seed, preset):
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(13, 9))
    gs = fig.add_gridspec(3, 3)
    f0 = frames[0]
    scales = {}
    for key, title, cmap, vmin, vmax in PANELS:
        if vmin is None: vmin = float(np.nanmin([np.nanmin(fr[key]) for fr in frames]))
        if vmax is None: vmax = float(np.nanmax([np.nanmax(fr[key]) for fr in frames]))
        scales[key] = (vmin, vmax)
    axes = [fig.add_subplot(gs[i // 3, i % 3]) for i in range(8)]
    tsax = fig.add_subplot(gs[2, 2])
    ims = []
    for ax, (key, title, cmap, _, _) in zip(axes, PANELS):
        vmin, vmax = scales[key]
        im = ax.imshow(f0[key], cmap=cmap, vmin=vmin, vmax=vmax, interpolation="nearest")
        ax.set_title(title, fontsize=8); ax.set_xticks([]); ax.set_yticks([])
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.02)
        ims.append(im)
    bnd_im = axes[0].imshow(_bnd_rgba(f0["boundary"]), interpolation="nearest")
    Ms = [fr["M"] for fr in frames]; mp = [fr["mplus_mean"] for fr in frames]; ms = [fr["mminus_std"] for fr in frames]
    xs = list(range(len(frames)))
    tsax.plot(xs, Ms, "k-", label="M (old frac)")
    tsax.plot(xs, mp, "b-", label="mean m+ (h1)")
    tsax.plot(xs, np.array(ms) * 20, "r-", label="std m- x20 (h2 disp.)")
    vline = tsax.axvline(0, color="gray", lw=1)
    tsax.set_title("time series", fontsize=8); tsax.legend(fontsize=6, loc="upper right")
    tsax.set_ylim(-0.1, 1.1); tsax.set_xlabel("frame", fontsize=7)
    sup = fig.suptitle("", fontsize=11, fontweight="bold")
    def draw(i):
        fr = frames[i]
        for im, (key, *_r) in zip(ims, PANELS):
            im.set_data(fr[key])
        bnd_im.set_data(_bnd_rgba(fr["boundary"]))
        vline.set_xdata([i, i])
        sup.set_text("%s  |  seed %d  |  step %d  |  M=%.2f  |  tracked size=%d  |  %s\n%s   "
                     "[engineered cumulative causal memory -- not identity/life/genome]"
                     % (preset, seed, fr["step"], fr["M"], fr["size"], COMMIT, label))
        return ims + [bnd_im, vline, sup]
    draw(0)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    return fig, draw


def run_live(frames, label, seed, preset):
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation
    fig, draw = make_figure(frames, label, seed, preset)
    state = {"i": 0, "paused": False}
    def upd(_):
        if not state["paused"]:
            state["i"] = (state["i"] + 1) % len(frames)
        return draw(state["i"])
    FuncAnimation(fig, upd, interval=120, blit=False, cache_frame_data=False)
    def onkey(ev):
        k = ev.key
        if k == " ":
            state["paused"] = not state["paused"]
        elif k == "right" and state["paused"]:
            state["i"] = min(len(frames) - 1, state["i"] + 1); draw(state["i"]); fig.canvas.draw_idle()
        elif k == "left" and state["paused"]:
            state["i"] = max(0, state["i"] - 1); draw(state["i"]); fig.canvas.draw_idle()
        elif k == "r":
            state["i"] = 0
        elif k == "s":
            fn = "observe_screenshot_step%d.png" % frames[state["i"]]["step"]; fig.savefig(fn, dpi=120); print("[observe] saved", fn)
        elif k in ("q", "escape"):
            plt.close(fig)
    fig.canvas.mpl_connect("key_press_event", onkey)
    print("[observe] live: Space=pause  Left/Right=step(paused)  R=restart  S=screenshot  Q=quit")
    plt.show()


def run_export(frames, label, seed, preset, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation, PillowWriter, FFMpegWriter
    fig, draw = make_figure(frames, label, seed, preset)
    anim = FuncAnimation(fig, draw, frames=len(frames), interval=120, blit=False)
    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    if output.lower().endswith(".mp4"):
        try:
            anim.save(output, writer=FFMpegWriter(fps=8))
        except Exception as e:
            output = output[:-4] + ".gif"; print("[observe] ffmpeg unavailable (%s); writing GIF" % e)
            anim.save(output, writer=PillowWriter(fps=8))
    else:
        anim.save(output, writer=PillowWriter(fps=8))
    plt.close(fig)
    print("[observe] exported movie -> %s" % output)
    return output


def contact_sheet(frames, seed, preset, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    targets = [1.00, 0.75, 0.50, 0.25, 0.21]
    picks = []
    for t in targets:
        i = int(np.nanargmin([abs((fr["M"] if not np.isnan(fr["M"]) else 9) - t) for fr in frames]))
        picks.append((t, i))
    rows = [("rho", "body", "viridis", 0, None), ("oldfrac", "old/new", "coolwarm", 0, 1), ("mplus", "m+ (h1)", "RdBu_r", -2, 2)]
    fig, axes = plt.subplots(3, len(picks), figsize=(3 * len(picks), 8.5))
    for r, (key, rlab, cmap, vmin, vmax) in enumerate(rows):
        vm = vmin if vmin is not None else float(np.nanmin([np.nanmin(frames[i][key]) for _, i in picks]))
        vM = vmax if vmax is not None else float(np.nanmax([np.nanmax(frames[i][key]) for _, i in picks]))
        for cix, (t, i) in enumerate(picks):
            ax = axes[r, cix]; ax.imshow(frames[i][key], cmap=cmap, vmin=vm, vmax=vM, interpolation="nearest")
            if r == 0:
                ax.imshow(_bnd_rgba(frames[i]["boundary"]), interpolation="nearest")
            ax.set_xticks([]); ax.set_yticks([])
            if r == 0: ax.set_title("M~%.2f\nstep %d" % (frames[i]["M"], frames[i]["step"]), fontsize=9)
            if cix == 0: ax.set_ylabel(rlab, fontsize=10)
    fig.suptitle("Turnover contact sheet -- frozen C1c, seed %d  |  %s\n"
                 "h1 (m+) persists as material turns over (old->new); tracked entity outlined; engineered causal memory, not identity"
                 % (seed, COMMIT), fontsize=11, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    fig.savefig(output, dpi=110); plt.close(fig)
    print("[observe] contact sheet -> %s" % output)
    return output


def main():
    ap = argparse.ArgumentParser(description="Observe the IsingV3 droplet (frozen C1c; deterministic recomputation from committed config).")
    ap.add_argument("--preset", default="turnover",
                    choices=["basic", "turnover", "h1-memory", "erase-transplant", "h2-killswitch"],
                    help="which committed condition to observe (default: turnover)")
    ap.add_argument("--seed", type=int, default=None, help="body seed (default: committed sealed seed 38501)")
    ap.add_argument("--steps", type=int, default=650, help="forward turnover steps (default 650 -> M~0.21)")
    ap.add_argument("--stride", type=int, default=10, help="capture every Nth step (default 10)")
    ap.add_argument("--live", action="store_true", help="open an interactive window")
    ap.add_argument("--export", action="store_true", help="render a movie file")
    ap.add_argument("--contact", action="store_true", help="also render a turnover contact sheet")
    ap.add_argument("--output", default=os.path.join("outputs", "droplet_turnover.gif"), help="movie path (.gif or .mp4)")
    args = ap.parse_args()

    pr = "basic" if args.preset == "basic" else "turnover"
    if args.preset in ("h1-memory", "erase-transplant", "h2-killswitch"):
        print("[observe] note: preset '%s' uses the committed turnover trajectory; the full statistical result "
              "for that preset is in the docs/paper figures (single-trajectory video cannot show a population statistic)."
              % args.preset)
    frames, label, seed = build_trajectory(pr, args.seed, args.steps, args.stride)
    if args.export or (not args.live):
        out = run_export(frames, label, seed, args.preset, args.output)
        if args.contact:
            contact_sheet(frames, seed, args.preset, os.path.splitext(out)[0] + "_contact.png")
    if args.live:
        run_live(frames, label, seed, args.preset)


if __name__ == "__main__":
    main()
