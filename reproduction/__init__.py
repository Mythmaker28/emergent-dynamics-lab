"""Deterministic reproduction package for the IsingV3 organizational-memory paper.

Reproduces, from committed raw data only (no new physics, no new simulation), the paper's PRIMARY
longitudinal certification:
  * track survival through deep turnover,
  * h1 deep-turnover decode + grouped bootstrap CI  (certification: lower bound > 0.50),
  * h2 longitudinal decode + CI                     (not-established check: CI spans/below 0.50),
  * the primary figure and the primary table.

Run:  python -m reproduction.primary
"""
__version__ = "1.0.0-rc"
