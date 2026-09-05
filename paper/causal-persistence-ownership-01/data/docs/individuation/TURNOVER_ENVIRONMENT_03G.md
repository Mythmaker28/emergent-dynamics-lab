# Turnover 03G authoritative environment

The authoritative future prospective platform is **Windows AMD64**, because this is the platform on which the lock
was freshly installed and the complete 03G suite and DEV smoke were executed.

| component | frozen value |
|---|---|
| Python | CPython 3.12.10 |
| implementation | CPython |
| OS | Windows |
| architecture | AMD64 |
| NumPy | 2.2.6 |
| SciPy | 1.15.3 |
| Matplotlib | 3.10.9 |

The tested host was Windows 11, version `10.0.26200`, build `26200`, 64-bit. Runtime enforcement intentionally uses
the stable execution identity (Python version/implementation, OS, architecture, and direct scientific package
versions) rather than the mutable absolute venv path.

`TURNOVER_ENVIRONMENT_LOCK_03G.txt` is valid pip requirements syntax and includes every transitive dependency
installed for the scientific runtime. The clean environment was created at
`C:\Users\tommy\Documents\ising-lci-turnover-03g-env`.

03G does not claim exact Linux reproduction. A future platform change requires a new manifest, seal, and audit.
