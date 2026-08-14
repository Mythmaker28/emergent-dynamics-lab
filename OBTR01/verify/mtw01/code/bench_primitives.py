"""Primitive-level microbenchmark. NOT an engine trajectory: no World is built, no advance()
is called, no state is evolved, no observable is read. It times numpy Generator primitives on
bare arrays so that the run horizon and lattice size can be sized ARITHMETICALLY."""
import time, numpy as np
rng = np.random.default_rng(0)

def t(f, n=30):
    f(); s=time.perf_counter()
    for _ in range(n): f()
    return (time.perf_counter()-s)/n*1e6      # microseconds

for L in (40, 48, 64, 80):
    N = L*L
    a = rng.integers(0, 6, size=(L, L)).astype(np.int64)
    g = rng.integers(0, 6, size=(L, L)).astype(np.int64)
    b = rng.integers(0, 6, size=(L, L)).astype(np.int64)
    s = rng.integers(0, 4, size=(L, L)).astype(np.int64)
    tb = t(lambda: rng.binomial(a, 0.25))
    th = t(lambda: rng.hypergeometric(g, b + 1, np.minimum(s, g + b + 1)))
    tr = t(lambda: np.roll(a, 1, axis=0))
    print(f"L={L:3d} N={N:5d}  binomial={tb:8.1f}us  hypergeom={th:8.1f}us  roll={tr:6.1f}us")
    # engine per-step operation counts, read from mincore.advance()
    full = 24*tb + 40*th + 60*tr          # with the 3-channel cohort ledger
    lean = 24*tb + 0*th + 20*tr           # cohort ledger disabled
    print(f"        per-step  FULL={full/1000:7.3f} ms   LEAN={lean/1000:7.3f} ms")
    for H in (12000, 20000, 40000):
        print(f"          H={H:6d}  16 arms: FULL={16*H*full/1e9:7.2f} s   LEAN={16*H*lean/1e9:7.2f} s")
