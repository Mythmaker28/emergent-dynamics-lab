# Dependency license audit

Runtime dependencies required by the reproduction (`python -m reproduction.primary`) and their licenses.
All are permissive (BSD / PSF-style) and compatible with distributing this work under Apache-2.0 (code) and
CC-BY-4.0 (data/text). Versions are pinned in `requirements-lock.txt`.

| package | version | license | SPDX / type | compatible with Apache-2.0 release |
|---|---|---|---|---|
| numpy | 2.2.6 | BSD 3-Clause ("NumPy Developers") | BSD-3-Clause (OSI) | Yes |
| scipy | 1.15.3 | BSD 3-Clause ("SciPy Developers") | BSD-3-Clause (OSI) | Yes (not imported by reproduction.primary; used elsewhere in repo) |
| matplotlib | 3.10.9 | Matplotlib License (PSF-based) | PSF-style / BSD-compatible (OSI) | Yes |

Notes:
- `reproduction.primary` imports only **numpy** and **matplotlib**; scipy is listed for the wider repository.
- Matplotlib bundles fonts/test-data under their own licenses (OFL-1.1, Bitstream, STIX, CC0, etc.); these are
  the library's own bundled assets, distributed by matplotlib, not redistributed independently by this project.
- No copyleft (GPL/LGPL/AGPL) runtime dependency is present. No dependency imposes a share-alike obligation on
  this project's code or data.
- Full environment snapshot (145 packages, the container's complete set) is in `release/pip_freeze_full.txt`
  for provenance; only the three above are required to reproduce.

## Action before public release
- Confirm the copyright holder line in `LICENSE-CODE` and the author block in `CITATION.cff`/`AUTHORS.md`.
- If the container's other packages are NOT shipped (they are not part of the release tree), no further action.
