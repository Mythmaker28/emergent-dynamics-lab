"""TBRT02 — build the payload that survives a container rollback, and say what it cannot carry.

WHY. The container reverts to an old snapshot every thirty to ninety minutes; twenty times on the
27th of August. It takes the git repository, the working files and /mnt/user-data/uploads, which is
inside the container. Documents in the claude.ai Project survive. This script builds a compressed,
base64-encoded payload the agent then writes there with project_write, and reads back with
project_read after a rollback.

WHAT IT PACKS, and why the list is derived rather than guessed. The first version of this payload
packed only the directories holding the seventeen files pinned by METHODS_HASH. Restoring from it
alone, after rollback nineteen, the frozen import chain died on BPRTC01_MASTER_FREEZE.json — a
constant read at import time by TLMR01's law module, which lives in no method directory. The list
below is therefore taken from the frozen files themselves, by scanning every {REPO}/... path they
mention, and it is checked by unpacking into an empty tree and importing the chain there.

WHAT IT CANNOT CARRY, measured and not assumed. tbrt02_guard.py reads git, and tbrt02_fork.one_seed
calls it on EVERY seed, so the campaign cannot run at scientific scale without the C2 commit in git
history. A bundle from 82f6c84 — the commit the base snapshot always holds — to the tip is
1,715,431 bytes, which base64 inflates to about 2,287,241, above the Project's 2,000,000-byte
knowledge cap. The git provenance therefore cannot live in the Project and must come from the
bundles on the Windows disk. Re-parenting the C2 commit onto the snapshot base would shrink it, and
is refused: it would sever TBRT02 from the parent tip its freeze records, damaging the record to
save bytes.

Nothing here selects on a result. The path list is given, never inferred from a measured value, and
no frozen file, threshold or seed is touched.
"""
import base64, hashlib, json, os, subprocess, tarfile

REPO = "/home/claude/edl"
OUT = "/home/claude/durability"
B64_BUDGET = int(2_000_000 * 0.95)
PATHS = ["TBRT02/code", "TBRT02/out", "TBRT02/work",
         "OMLDCT02/code", "ORR01/code", "OBTC02/code", "PQEC01/code", "TLMR01/code",
         "FMRCT01/code", "FDFLT01/code", "FDOT01/code", "FMRT01/code", "MRCI01/code",
         "BPRTC01/out/BPRTC01_MASTER_FREEZE.json",
         "MCTT01/out/MCTT01_PHYSICS_DIFF_FROM_B1.json",
         "MCTT01/out/MCTT01_SELECTED_LAW.json",
         "PQEC01/out/PQEC01_MASTER_FREEZE.json"]


# --- added after the twenty-third rollback, 2026-08-29 -------------------------------------
# RPP97 was written, committed, and lost: it lived only in git inside the container, because this
# list named TBRT02 and nothing else. A commit is not durability here — the TBRT02 freeze already
# said so and I still let a new mission fall outside the payload.
#
# The fix is NOT to pack the whole laboratory: everything older than the base bundle is already
# durable in it, and pulling it all in blows the Project's 2 MB budget. The fix is a list that
# FAILS LOUDLY. ACTIVE_MISSIONS below must be extended THE DAY a mission is created, and the
# packer refuses silence: any mission directory holding a file newer than the newest file it
# actually packed is reported in PATHS_UNPACKED_AND_RECENT, which the caller must not ignore.
ACTIVE_MISSIONS = ["TBRT02", "RPP97", "RPP98", "GATE01", "FIMRCC02", "OMLDCT03", "CLOSE01"]
for _m in ACTIVE_MISSIONS:
    for _sub in ("code", "out", "work"):
        _rel = f"{_m}/{_sub}"
        if os.path.isdir(os.path.join(REPO, _rel)) and _rel not in PATHS:
            PATHS.append(_rel)


def _newest_packed_mtime(packed):
    """Newest mtime among everything actually packed; PATHS holds both directories and files."""
    newest = 0.0
    for rel in packed:
        full = os.path.join(REPO, rel)
        if os.path.isfile(full):
            newest = max(newest, os.path.getmtime(full)); continue
        for root, _, files in os.walk(full):
            for f in files:
                try:
                    newest = max(newest, os.path.getmtime(os.path.join(root, f)))
                except OSError:
                    pass
    return newest


def _unpacked_but_recent(packed, newest_packed_mtime):
    """Mission directories carrying work newer than anything we packed. A non-empty list means
    the payload is behind the laboratory and ACTIVE_MISSIONS needs extending."""
    import glob as _glob
    out = []
    for d in sorted(_glob.glob(os.path.join(REPO, "*"))):
        b = os.path.basename(d)
        if not os.path.isdir(d) or b in ACTIVE_MISSIONS:
            continue
        if not (b[:1].isupper() and any(c.isdigit() for c in b)):
            continue
        if any(f"{b}/{s}" in packed for s in ("code", "out", "work")):
            continue
        for root, _, files in os.walk(d):
            for f in files:
                try:
                    if os.path.getmtime(os.path.join(root, f)) > newest_packed_mtime:
                        out.append(b)
                        break
                except OSError:
                    pass
            if b in out:
                break
    return sorted(set(out))


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    os.makedirs(OUT, exist_ok=True)
    present = [p for p in PATHS if os.path.exists(os.path.join(REPO, p))]
    absent = [p for p in PATHS if p not in present]
    tgz = f"{OUT}/EDL_STATE.tar.gz"
    subprocess.run(["tar", "--exclude=__pycache__", "-czf", tgz, "-C", REPO] + present, check=True)
    b64p = f"{OUT}/EDL_STATE.b64.txt"
    with open(b64p, "w") as fh:
        fh.write(base64.b64encode(open(tgz, "rb").read()).decode())
    work = f"{REPO}/TBRT02/work"
    lines = sum(len(open(f"{work}/{f}").readlines()) for f in os.listdir(work)
                if f.startswith("TBRT02_SEALED_LEDGER_"))
    m = {"tar_gz_bytes": os.path.getsize(tgz), "tar_gz_sha256": sha(tgz),
         "b64_bytes": os.path.getsize(b64p), "b64_budget": B64_BUDGET,
         "FITS": os.path.getsize(b64p) <= B64_BUDGET,
         "n_members": len(tarfile.open(tgz).getnames()),
         "paths_packed": present, "paths_absent": absent, "ledger_lines": lines,
         "ACTIVE_MISSIONS": ACTIVE_MISSIONS,
         "PATHS_UNPACKED_AND_RECENT": _unpacked_but_recent(present, _newest_packed_mtime(present)),
         "IF_THAT_LIST_IS_NOT_EMPTY": "a mission is doing work this payload does not carry. Extend "
             "ACTIVE_MISSIONS before the next rollback, not after it.",
         "GIT_PROVENANCE_IS_NOT_IN_HERE": "the guard runs on every seed and reads git; restore the "
             "branch from the Windows bundles, it does not fit in the Project",
         "SELECTS_NOTHING_ON_A_RESULT": True}
    json.dump(m, open(f"{OUT}/EDL_STATE.MANIFEST.json", "w"), indent=1)
    print(json.dumps(m, indent=1))
    return m


if __name__ == "__main__":
    main()
