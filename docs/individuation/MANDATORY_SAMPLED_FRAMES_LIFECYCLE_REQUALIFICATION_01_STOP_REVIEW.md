# MANDATORY-SAMPLED-FRAMES-LIFECYCLE-REQUALIFICATION-01 — stop review

**Terminal disposition: `HUMAN_REVIEW_ACCEPTED_STOP`**
**Accepted attempted-mission disposition: `STOP_LIFECYCLE_REQUALIFICATION`**

Issued by the project owner and human reviewer, 2026-08-02.

The attempted `MANDATORY_SAMPLED_FRAMES_LIFECYCLE_REQUALIFICATION_01` mission is **closed** and may not be
resumed by the agent context that attempted it.

---

## 1. Accepted parent

| field | value |
|---|---|
| accepted parent | `7539c32831d84771e2425c21b6966c2667155dfb` |
| implementation candidate | **none — no candidate exists** |
| repair / requalification branch | **none was created** |
| decision branch | `codex/mandatory-sampled-frames-lifecycle-requalification-01-stop-review` |

---

## 2. Breach classification

**`METADATA_ONLY_FIREWALL_BREACH`**

The breach consisted of:

- recursively enumerating entries below an **overly broad documentation directory**;
- enumerating **forbidden DEV shard-related filenames**;
- computing **hashes for forbidden shard-related files and manifests**.

Six forbidden entries were touched in total: four compressed DEV shard files, one shard index, and one
completion manifest. Their names and digests are deliberately **not reproduced here**, in this or any
successor record.

---

## 3. Bounded exposure

Recorded equally clearly, and with equal weight:

- **no compressed shard was decompressed**;
- **no shard contents were displayed**;
- **no per-world measurements or outcomes were read**;
- **no trajectory, candidate record or reconstructed checkpoint was opened**;
- **no prospective namespace was accessed**;
- **no repository content was written**;
- **no branch, commit or worktree was created** by the attempted mission;
- **no engine, runner, tracker or analysis was executed**.

This was a **real firewall violation**. The `STOP` remains **mandatory** even though the exposure was
limited to metadata. A tripwire that fires is reporting truth, and the fact that the person who tripped
it can explain why is not a reason to wave it through.

---

## 4. Why the STOP is accepted

The mission instructions prohibited opening, enumerating, grepping, hashing or inspecting scientific
shard material **and its names**. The attempted preflight performed prohibited **enumeration** and
**hashing**. Continuing after disclosure would have violated the frozen terminal rule.

The agent **correctly halted before implementation**, disclosed the breach unprompted and in full, and
wrote nothing.

---

## 5. Scientific consequence

This breach:

- **invalidates this attempted qualification session**;
- does **not** invalidate any prior scientific result;
- does **not** alter the frozen Stage-B disposition;
- does **not** reveal a new scientific outcome;
- does **not** contaminate an already generated prospective family;
- does **not** require deleting or revising existing branches;
- **requires a fresh agent context** for any successor requalification attempt.

---

## 6. Safety correction — the proposed filter was not sufficient

The post-hoc exclusion filter proposed in the stop report is **rejected as insufficient**. A recursive
listing followed by `grep -v` **still enumerates forbidden paths** before removing them from downstream
output. Enumeration is the prohibited act; filtering the output afterwards does not undo it.

The successor must use **only positive, exact-path allowlists.**

**Forbidden in the successor:**

- `git ls-tree -r` on any documentation directory;
- `find` on `docs/`;
- `rg --files` on broad trees;
- broad `git grep` over `docs/`, `edlab/` or `tests/`;
- hashing a dynamically generated directory listing;
- filtering forbidden entries only after enumeration;
- glob patterns capable of matching unknown directories.

---

## 7. Successor authorization

A fresh mission is authorized:

### `MANDATORY_SAMPLED_FRAMES_LIFECYCLE_REQUALIFICATION_01R`

It **must begin in a new Opus 5 context that did not perform this breach.**

The successor must use only:

- exact named Git object paths;
- exact named source files;
- exact named test files;
- positive pathspecs **frozen before inspection**.

**The current agent must not begin, preflight, scaffold or advise the successor mission beyond writing
this review record.**

### 7.1 Successor inspection principle

For each required artifact:

1. **predeclare the exact path**;
2. use `git cat-file -e <commit>:<exact-path>` for existence;
3. use `git show <commit>:<exact-path>` **only for that file**;
4. **hash only that exact byte stream**;
5. **stop if the named file is absent.**

**No directory listing is necessary.**

Call-site qualification must be explicitly scoped to the **permitted generic tracker and synthetic
stack**. It **must not claim knowledge of callers inside firewalled historical runners.**

---

## 8. Record scope

This decision record adds exactly one file and changes no existing file. No additional project artifact
was inspected in order to write it. It starts no requalification, creates no implementation candidate,
runs no engine, opens no scientific material, wires no runner, and allocates no seed.
