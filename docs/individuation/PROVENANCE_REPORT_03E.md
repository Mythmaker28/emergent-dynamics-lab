# LCI-CAUSAL-TURNOVER-PRESEAL-REPAIR-03E — provenance report (blocker B6 / PROV-01)

## Import of the audited lineage (local transport, no network)

Per Tommy's Option 1, the audited commits were imported into the destination repo `C:\Users\tommy\Documents\ising v3`
by **local git transport** from `…\ising-lci-turnover-integration` and `…\ising-lci-turnover-audit-03d-clean`
(both granted to this session). Verified exactly:

```
integration codex/lci-causal-turnover-preseal-integration-03c = a5e0a552b3f34a8cf9912292cd74bce3c6aee2d3  ✓
audit       audit/lci-causal-turnover-final-preseal-03d       = 9038ff08f7487e10f3615c269ed2a3af7197e2cb  ✓
audit parent  9038ff08^                                        = a5e0a552…                                 ✓
object completeness walk of a5e0a552: 3259 objects, 0 missing  ✓
required ancestry 244bc32 -> ca7929b -> cd74eda -> a5e0a552     ✓
```

The 03D certificate, risk register, and authorization template were read directly from `9038ff08` before any repair.

## Protected-main provenance

The 03D audit worked from the **remote** (`github.com/Mythmaker28/emergent-dynamics-lab`), where `main` =
`6d0bed67339c1b422877b8bfaae6861669597a93` and the object `f3921a4` was not a fetchable remote ref — hence its FAIL.

In the **local** device repository and both local source clones, `main` **is** `f3921a4`:

```
git rev-parse main = f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77   (commit; author Tommy Lepesteur; 2026-07-15)
```

- **Archival ref created, main untouched:** `refs/heads/archive/main-f3921a4 -> f3921a4d2eb…`; `main` unchanged and
  byte-identical to it.
- **Relation to the experimental ancestry:** `main`/`f3921a4` is the paper/consolidation head (Set-Valued Causal
  Metrology); it is **not** an ancestor of CONFIRM-02 (`830c2d0`) nor of the turnover repair line (`a5e0a552`), which
  descend from V4. The turnover work never touches `main`.
- **Local vs remote divergence (`f3921a4` vs remote `6d0bed6`):** this is a repository-synchronization matter OUTSIDE
  the turnover seal's scope — the protected-main invariant relevant to the turnover experiment is "the turnover
  pipeline never modifies main", which is verified (main unchanged). The full-hash reconciliation of local `f3921a4`
  against advertised remote `6d0bed6` requires network access this sandbox does not have; it is flagged as a
  pre-push action for Tommy and does **not** gate the turnover science. No force-push or remote-main modification is
  performed or recommended by this mission.

## Push commands (MANUAL — not executed)

```powershell
cd "C:\Users\tommy\Documents\ising v3"
git push origin archive/main-f3921a4:archive/main-f3921a4
git push origin repair/lci-causal-turnover-preseal-03e:repair/lci-causal-turnover-preseal-03e
# Before any main reconciliation: compare local f3921a4 against remote 6d0bed6 with a fetch on a networked machine.
```

The earlier `provenance/turnover-preseal-03e-blocker` branch (`bbd313a`) is retained ONLY as an honest record of the
temporary clone-visibility incident (before the local import). It is **not** the repair parent.
