# Turnover 03G risk register

| risk | status | control / residual limitation |
|---|---|---|
| runner did not execute | CLOSED IN IMPLEMENTATION | One runner executes ordered seeds, raw publication, analyzer, and certificate. Future prospective execution remains unauthorized. |
| authorization replay in canonical directory | CLOSED | Atomic fresh creation; second fresh invocation refused; resume explicit with identical binding. |
| malicious copied repository replay | ACCEPTED THREAT-MODEL LIMIT | Cannot be prevented in open source. It yields a separate untrusted ledger/repository-instance record and is not the sealed execution. |
| incomplete ledger lifecycle | CLOSED | Explicit FSM, seed start/resume/completion, primary/reserve/family closure, analysis, certification. |
| ledger truncation | CLOSED FOR ORDINARY/TAMPER CHECKS | Atomic anchor detects truncation/stale tip. An actor controlling both repository and all artifacts is outside the prevention claim. |
| raw overwrite or tamper | CLOSED | Exclusive atomic publication, per-file SHA-256, ledger/raw-manifest validation. |
| missing seal-to-runtime binding | CLOSED IN IMPLEMENTATION | Every protected Git blob/SHA, manifest, environment, family, runner, and analyzer are checked before engine import. |
| missing canonical analyzer | CLOSED | Closed-ledger raw-to-verdict analyzer emits one machine certificate and human report. |
| decision tree documentation-only | CLOSED | Structured tree expressions are executed and exhaustively tested over gate combinations. |
| G-full did not nest L | CLOSED | Gf is exact `L || Gm`; frozen unit test checks exact L slice equality. |
| environment lock invalid | CLOSED | Fresh Windows venv installs complete transitive requirements lock. |
| authority conflict | CLOSED BY INDEX | Canonical 03G index marks 03C/03E paths superseded and forbids prospective use. Historical files remain present. |
| fine distributed encoding outside E/Gm resolution | OPEN SCIENTIFIC LIMITATION | Protocol explicitly limits Outcome F/locality conclusions to frozen detectable access scopes. |
| fewer than 18 valid worlds | CONTROLLED | Outcome E, no scientific negative conclusion. |
| DEV smoke scientific values | CONTROLLED | DEV/EXPLORATORY watermark; no claim and no gate change. |
| final seal / human approval | OPEN BY DESIGN | Must be created only after a fresh independent final re-audit. |
