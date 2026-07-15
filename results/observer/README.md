# Droplet observer (scripts/observe_droplet.py)

Deterministic recomputation from the COMMITTED frozen architecture (C1c; commit 1f8f789, H2-CERT-01).
This is DETERMINISTIC RECOMPUTATION FROM COMMITTED CONFIGURATION (not a stored-frame replay: only summary
statistics were committed, so frames are recomputed from the sealed seed/history with frozen physics).

Default condition: sealed H2-CERT-01 seed 38501, committed history a_e=0.00899, a_l=0.00614, forward to M~0.21.

## Windows PowerShell
    cd "C:\Users\tommy\Documents\ising v3"
    .\.venv\Scripts\Activate.ps1
    pip install scipy
    python scripts\observe_droplet.py --preset turnover --live

## Export (no window needed)
    python scripts\observe_droplet.py --preset turnover --export --contact --output outputs\droplet_turnover.gif

## Presets
basic | turnover(default) | h1-memory | erase-transplant | h2-killswitch
Live controls: Space=pause  Left/Right=step(paused)  R=restart  S=screenshot  Q=quit
Startup ~5-10 s (2000-step warmup). turnover run ~15-25 s to build, then the window animates in a loop.

## Panels
body density (tracked entity outlined red) | old/new material | nutrient N | m1 | m2 | attractant c |
m+ (h1/uptake) | m- (order) | time series (M, mean m+, std m-).

## Outputs
results/observer/droplet_turnover.gif ; results/observer/droplet_turnover_contact.png
