"""LRCPS01 section 1 - bind every surviving source and classify it. Zero scientific runs."""
from __future__ import annotations
import hashlib, json, os, subprocess

REPO = "/home/claude/edl"
PKG = f"{REPO}/paper/organiser-bound-source-response-operator"
PROV = f"{PKG}/provenance"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def git(*a):
    return subprocess.run(("git", "-C", REPO) + a, capture_output=True, text=True).stdout.strip()


# programme -> (directory, files that carry load-bearing numbers)
PROGRAMMES = {
    "ORR01": ("/home/claude/ORR01", ["out/_freeze.json", "out/_analysis.json",
                                     "out/_theorem.json", "code/protocol.py",
                                     "code/kinetics.py", "code/lawspec_v2.py"]),
    "OBTC02": ("/home/claude/OBTC02", ["code/obtc02_protocol.yaml", "code/engine_obtc.py",
                                       "code/metrics_obtc.py"]),
    "OBDI02": ("/home/claude/OBDI02", []),
    "OBTR01": ("/home/claude/OBTR01", ["out/OBTR01_FINAL_REPORT.md", "out/_kernels_operator.json",
                                       "out/_observables.json"]),
    "OBFOR01": ("/home/claude/OBFOR01", ["out/OBFOR01_FINAL_REPORT.md",
                                         "out/_observables_exact.json", "out/_residual.json",
                                         "out/_m6.json", "out/_mechanisms.json",
                                         "out/_validation.json", "out/_adjudication.json",
                                         "out/_freeze.json", "out/_provenance.json"]),
    "PMCR01": ("/home/claude/PMCR01", []),
    "MYQBD01": ("/home/claude/MYQBD01", []),
    "PQEC01": ("/home/claude/PQEC01", []),
    "FLCR01": (f"{REPO}/FLCR01", ["out/FLCR01_FINAL_REPORT.md",
                                  "out/FLCR01_FINAL_DISPOSITION.json",
                                  "out/FLCR01_LINEAGE_REGIONS.json"]),
}

LOST = {
    "CLOC02": "branch, commits, 288 raw archives, code and delivery all absent; lost in the "
              "first container reset",
    "RSLOC03": "branch, 6 commits, 284 raw archives, methods capsule and every output absent; "
               "lost in the SECOND container reset. Externally delivered capsules exist in the "
               "owner's conversation but are not mounted back into this container.",
    "RIRA01": "branch, 3 commits, the direct point atlas, the two independent calculators and "
              "the route decision all absent; lost in the same second reset.",
}


def classify(prog, d, files):
    if not os.path.isdir(d):
        return "LOST", {"reason": "directory absent"}
    present = {f: os.path.exists(os.path.join(d, f)) for f in files}
    raw = os.path.isdir(os.path.join(d, "raw"))
    nraw = len([x for x in os.listdir(os.path.join(d, "raw"))]) if raw else 0
    hashes = {f: sha(os.path.join(d, f)) for f, ok in present.items() if ok}
    st = "BYTE_VERIFIED"
    if raw and nraw:
        st = "RAW_RECOMPUTABLE"
    elif not files:
        st = "DOCUMENTARY_ONLY"
    return st, {"dir": d, "files_present": present, "raw_archives": nraw, "sha256": hashes}


def main():
    os.makedirs(PROV, exist_ok=True)
    out = {"SECTION": "LRCPS01 paper source binding",
           "STATUS": "PAPER_ONLY_NONSCIENTIFIC_BINDING",
           "NEW_SCIENTIFIC_RUNS": 0,
           "REPO_HEAD": git("rev-parse", "HEAD"),
           "REPO_BRANCH": git("rev-parse", "--abbrev-ref", "HEAD"),
           "SOURCES": {}, "LOST": {}}
    for p, (d, fs) in PROGRAMMES.items():
        st, info = classify(p, d, fs)
        info["STATUS"] = st
        out["SOURCES"][p] = info
    for p, why in LOST.items():
        out["LOST"][p] = {"STATUS": "LOST", "why": why,
                          "usable_for": "project history and motivation only",
                          "may_carry_a_figure_table_number_or_abstract_claim": False}

    # the existing manuscripts actually present in this repository
    ms = {}
    for rel in ("docs/paper/MANUSCRIPT.md", "docs/consolidation/SET_IDENTIFICATION_MANUSCRIPT.md",
                "docs/replication/THEOREM_MANUSCRIPT.md", "docs/paper/FINAL_CLAIM_TABLE.md",
                "docs/paper/PUBLICATION_READINESS.md"):
        p = os.path.join(REPO, rel)
        if os.path.exists(p):
            ms[rel] = {"sha256": sha(p), "bytes": os.path.getsize(p),
                       "first_line": open(p, encoding="utf-8").readline().strip()}
    out["EXISTING_MANUSCRIPTS_IN_REPOSITORY"] = ms
    out["NAMED_V1_V2_PERSISTENCE_PACKAGE"] = {
        "searched_for": "persistence without evidence of local ownership",
        "FOUND": False,
        "note": "the launcher names this as the existing V1/V2 package. It is not in this "
                "repository. Every manuscript present belongs to the set-valued causal metrology "
                "line, which is a different scientific question. The absence is recorded rather "
                "than assumed away, and the strategy decision is taken against what exists."}
    out["EXCLUDED_BY_RULE"] = [
        "lost CLOC02 raw results", "conversation summaries as numerical authority",
        "stale pre-repair JSON", "superseded dispositions",
        "hand-edited numbers that do not regenerate",
        "invalid RSLOC03 interpolation outputs as scientific results"]
    json.dump(out, open(f"{PROV}/PAPER_SOURCE_BINDING.json", "w"), indent=1)
    for p, i in out["SOURCES"].items():
        print("%-8s %-18s raw=%-4d files=%d" % (p, i["STATUS"], i.get("raw_archives", 0),
                                                sum(1 for v in i.get("files_present", {}).values() if v)))
    print("LOST:", ", ".join(out["LOST"]))
    print("existing manuscripts:", list(ms))


if __name__ == "__main__":
    main()
