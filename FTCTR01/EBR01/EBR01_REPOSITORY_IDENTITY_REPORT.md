# EBR01 — REPOSITORY IDENTITY REPORT

## A genuinely distinct Ising project exists — and it is still not the one

| | current Windows EDL repository | recovered distinct project |
|---|---|---|
| path | `C:\Users\tommy\Documents\ising v3` | `C:\Users\tommy\Documents\ising-life-lab` |
| remote | `github.com/Mythmaker28/emergent-dynamics-lab` | `github.com/Mythmaker28/ising-life-lab` |
| package | `edlab` | `isinglab` |
| commits | 397 | 121 |
| newest ref | 2026-08-11 | 2025-11-14 |
| shape | metrology / individuation / Route E | Ising + cellular-automata + Hopfield atlas toolkit (`src/{ai,ca,core,energy,hopfield,memory,search,viz}`) |

`same Git root = false` · `common commits = 0` · `common trees = 0` · `common remotes = 0` ·
`common engine files = 0`.

**Verdict: `RECOVERED_PROJECT_IS_DISTINCT_FROM_WINDOWS_EDL_REPOSITORY`.**

The FTCTR01 audit's caution — *"the current Windows repository must not be assumed to be the
historical Ising-Life executable repository"* — was well founded: a separate `ising-life-lab`
repository really does exist on this machine, and no earlier mission had looked at it.

But it is not the target either. A content search over its 357 source files returns **zero** hits for
`p_hop_Y`, `TAU_SEP`, `nSY`, `muX`, `kY`, `binomial`, `p_hop`, `TWO_CENTRES`, `ONE_CENTRE`,
`sub_shift` or `n_centres`, and **zero** matches against the 24 expected content hashes. Its newest
commit predates the qualified source-response programme by nine months.

## Where the target actually lived

`PAPER_SOURCE_BINDING.json`, recovered from the paper capsule, answers this directly. Every source
directory it binds is a container path:

```
ORR01   -> /home/claude/ORR01
OBTC02  -> /home/claude/OBTC02
OBFOR01 -> /home/claude/OBFOR01
OBTR01  -> /home/claude/OBTR01
PQEC01  -> /home/claude/PQEC01
FLCR01  -> /home/claude/edl/FLCR01
```

Its `REPO_HEAD` `06c592313df96601de8d2a89676d5a5cf79fc414` and its branch
`codex/lineage-route-closure-and-paper-synthesis-01` **do not exist** in `ising v3`
(`git cat-file` → *bad object*; no matching ref among 193).

So the qualified source-response programme ran entirely inside an **ephemeral cloud container**, and
its code was never committed to any repository on this device. The binding says as much about its
own siblings, in its own words: CLOC02 *"lost in the first container reset"*, RSLOC03 and RIRA01
*"lost in the SECOND container reset"*, with the note that externalised capsules *"are not mounted
back into this container."*

`ORR01/code/kinetics.py` and its eleven companions are in the same category as CLOC02. They were
simply never named as lost, because the paper only needed their hashes.

## Restoration

`isolated_restoration_directory = NOT_CREATED`. Nothing was recovered to restore; creating an empty
`ising-life-lab-recovered` tree would misrepresent the outcome. No history was merged, no repository
was overwritten, and `ising-life-lab` was opened read-only.
