# Independent red-team journal — RUN-20260810-1441-IPRR00R

- Role: lead independent auditor and integrator
- Mission: `INDEPENDENT_PROJECT_RED_TEAM_AND_ROADMAP_01R`
- Start: 2026-08-10 14:41:02 +02:00
- Starting source metadata: local active ref `confirm/exact-twin-canonical-mf0-native-flux-00` at
  `c5171b72f3ed2cdaba1968bdbd9ebf3776eab8d7`; remote `main` at
  `f382dbf077699aa65c80328b6519035d1cda4a57`
- Audit base: `d86d24864e0f88c6483d11bcde601d1f13221a82`
- Audit branch: `audit/chatgpt-independent-red-team-roadmap-01r`
- Shared source worktree: preserved; global status/tree intentionally not enumerated under the bootstrap firewall
- Assigned scope: independent code/DEV/provenance/GitHub red team; no engine, trajectory, primary allocation,
  held-out or near-held-out content

## Actions before freeze

1. Read the mission in full and treated it as a new mandate; inherited no scientific verdict from IPRR00.
2. Read `AGENTS.md`, the research charter, project state, complete decision log, experiment index, run index, the
   latest tracked journal, and the last completed future-only lifecycle qualification and report.
3. Queried structured GitHub metadata before local materialization. The repository is public, default branch
   `main`; no remote ETPC/EEFCA/ETNBFC/ETCMNFC/audit refs or matching commit were found by exact structured search.
4. Queried local ref and ancestry metadata only. ETPC is ancestor of EEFCA; EEFCA is ancestor of ETNBFC. ETCMNFC
   content was not opened.
5. Created a fresh no-checkout audit repository and an external path/command sentinel before content discovery.
6. Froze `INDEPENDENT_AUDIT_FREEZE_01R.md` before reading current experiment content or DEV results.

## Pre-freeze access classification

- L0: experiment-family names in the mission, branch labels, commit hashes, repository metadata.
- L1: none.
- L2: none.
- L3: none.
- L4: none.

## External sentinel at freeze

- allowlist SHA-256: `FF704DCE4F3AB81D2916D9418BC6B19AA50759B8395CB9F0B93EE97AED06A5A7`
- command/path sentinel SHA-256: `044F9B86435C1DF8310717060C287BB0581A62901509F4E2BF5BE527620F2E12`
- positive path probe: `ETCMNFC/protocol.json` allowed.
- negative path probe: `ETCMNFC/heldout/results.json` denied.
- negative command probe: repository runner invocation denied.

## OBSERVED

- The durable history repeatedly distinguishes DEV qualification from prospective evidence and records several
  false PASS cases caused by self-referential nulls, wrong labels, non-independent oracles and untested scope.
- The durable experiment/run indexes are stale relative to the later decision log and branch history; they cannot
  be treated as the authoritative current ledger without reconciliation.
- The last completed future-only lifecycle contract is source/synthetic qualified but explicitly not a scientific
  identity result and not installed in a future runner.

## INFERRED

- The load-bearing audit is not whether scripts print PASS, but whether operator reductions, oracle independence,
  denominator construction and inference boundaries survive adversarial recomputation.
- Remote absence of the experiment refs makes local archival provenance and a bundle necessary unless an audit-only
  publication can be proven safe.

## HYPOTHESIS

At least some ETCMNFC numerical claims may be reproducible from DEV artefacts, while the strongest wording about
minimality, forcedness or scientific identity may require stricter evidence than those endpoint counts provide.

## WHAT WOULD FALSIFY THIS?

Exact independent reductions plus adversarially fireable oracles, complete raw-to-report reconciliation and a
minimal-alternative test could support the strong wording; any mismatch, circular gate, outcome-conditioned
denominator or absent falsifier would refute the dependent part.

## Failures and dead ends so far

- A local fetch into the empty audit repository timed out. No checkout occurred. The repository now uses a read-only
  object alternate pointing at the source object database; the audit branch/index was created without materializing
  a source tree.
- PowerShell execution policy blocked direct sentinel invocation. All sentinel calls now use an explicit
  `-ExecutionPolicy Bypass`; the negative probes then failed closed as intended.

## Pending

- Commit this freeze.
- Inspect only allowlisted experiment paths and workflows.
- Run independent offline operator/oracle/endpoint checks.
- Produce the six remaining required deliverables, hashes, archive and bundle.
- Finalize this journal, indexes/state only if the audit branch's durable state genuinely changes, commit, and
  publish only if workflow-safe.

## Post-freeze events — first audit pass

- Access classification changed at L1: the ETCMNFC commit message and then its allowlisted protocol disclosed the
  held-out allocation. No held-out content, content hash, size, result, timestamp or internal result manifest was
  opened. The dependent held-out audit is `NOT_AUDITABLE`; all code/DEV/provenance/GitHub work continues.
- The GitHub reviewer found a sentinel normalization bug before opening a workflow. Amendment 1 corrects exact
  leading-`./` handling and adds a traversal denial without changing the frozen allowlist. Corrected sentinel hash:
  `A0E618F6BA638BE1457BD420DF19FCC80A590D8000F6699AE3E2F3CC9C5052BF`.
- An independent offline Git-blob consistency script reproduced 60 stored offline PASS rows, 14 second-pass rows,
  19 verifier rows, the protocol seal, all 18 listed artefact hashes, the shared geometry and empty endpoint support.
  It also found that all four ratios labelled `component minimum / boundary median` in `probe_depth.json` disagree
  with direct division of the corresponding committed numerator and median in `probe_attribution.json`. This is now
  an open contradiction under investigation, not silently rounded away.
