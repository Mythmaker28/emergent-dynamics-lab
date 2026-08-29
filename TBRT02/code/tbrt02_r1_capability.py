"""TBRT02 — can the frozen refutation condition fire AT ALL?

The frozen condition is: "if the CERTAIN set of the daughter's lineage ever absorbs a
descendant of the displaced mass, Model C is REFUTED."

Enumerated over the 41 admissible triples it fired zero times. A zero is only evidence if the
statistic COULD have been non-zero. This file tests that, adversarially, on synthetic worlds
that are not bound by the engine's physics at all: occupancy at each step is drawn at random,
cells may appear and vanish freely, and the two roots are placed at the minimum separation the
displacement guarantees. If the condition can fire under ANY sequence of rows, a random search
this unconstrained should find it.

The propagation uses `clea01_lineage_i1.sources` byte-unchanged — the same primitive the real
enumeration uses. Nothing here touches the frozen file.

THE CONTROL MATTERS MORE THAN THE TEST. A search that finds nothing proves nothing unless the
same search finds the analogous event under a rule that permits it. So the same random worlds
are also run with the daughter side relaxed from the ALL-sources rule (CERTAIN) to the
ANY-source rule (POSSIBLE). If the relaxed version fires and the frozen one never does, the
difference is the rule, not the search.
"""
from __future__ import annotations
import os, sys, json, random

REPO = os.environ.get("TBRT02_REPO", "/home/claude/edl")
sys.path.insert(0, os.path.join(REPO, "CLEA01/code"))
import clea01_lineage_i1 as MC

L, sources = MC.L, MC.sources
SEPARATION = 2          # tbrt02_displace.MIN_SEPARATION_FROM_THE_DAUGHTER


def cheb(a, b):
    dy = min((a[0] - b[0]) % L, (b[0] - a[0]) % L)
    dx = min((a[1] - b[1]) % L, (b[1] - a[1]) % L)
    return max(dy, dx)


def one_world(rng, steps, density, relaxed):
    """Return (fired, first_t). `relaxed` swaps the daughter's ALL-sources rule for ANY-source."""
    d_root = (rng.randrange(L), rng.randrange(L))
    while True:
        c_root = (rng.randrange(L), rng.randrange(L))
        if cheb(c_root, d_root) >= SEPARATION: break
    prev = {d_root: 1, c_root: 1}
    daughter = {d_root}
    desc = {c_root}
    for t in range(steps):
        n = max(1, int(density * L * L))
        cur = {}
        # bias the draw towards the neighbourhoods of both live sets, so the two fronts actually
        # meet; a uniform draw on a 36x36 torus would almost never bring them into contact.
        seeds = list(daughter | desc) or [d_root, c_root]
        for _ in range(n):
            sy, sx = seeds[rng.randrange(len(seeds))]
            cur[((sy + rng.randint(-1, 1)) % L, (sx + rng.randint(-1, 1)) % L)] = 1
        nd, nc = set(), set()
        for cell in cur:
            S = sources(cell, prev)
            if not S: continue
            if relaxed:
                if S & daughter: nd.add(cell)
            else:
                if daughter and S <= daughter: nd.add(cell)
            if S & desc: nc.add(cell)
        daughter, desc = nd, nc
        if daughter & desc:
            return True, t
        if not daughter and not desc:
            return False, None
        prev = cur
    return False, None


def main(n_worlds=4000, steps=60, density=0.02, seed=20260828):
    out = {}
    for relaxed in (False, True):
        rng = random.Random(seed)
        fired = 0; firsts = []
        for _ in range(n_worlds):
            f, t = one_world(rng, steps, density, relaxed)
            if f: fired += 1; firsts.append(t)
        key = "RELAXED_any_source_control" if relaxed else "FROZEN_all_sources_CERTAIN"
        out[key] = {"worlds": n_worlds, "fired": fired,
                    "median_first_step": (sorted(firsts)[len(firsts)//2] if firsts else None)}
    out["SEARCH_IS_CAPABLE"] = out["RELAXED_any_source_control"]["fired"] > 0
    out["FROZEN_RULE_EVER_FIRED"] = out["FROZEN_all_sources_CERTAIN"]["fired"] > 0
    out["PARAMS"] = {"n_worlds": n_worlds, "steps": steps, "density": density, "seed": seed,
                     "L": L, "SEPARATION": SEPARATION}
    return out


if __name__ == "__main__":
    print(json.dumps(main(), indent=1))
