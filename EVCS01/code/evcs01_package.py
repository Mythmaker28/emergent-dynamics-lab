"""EVCS01 §8 — the Windows durability package, built by committed code.

Written generically over (MISSION, BASE) so the next mission does not need a fourth copy of this
file. The full bundle is not produced and the reason is measured, not asserted: the repository pack
is ~571 MiB and the device bridge caps a committed file at 20 MB, so a full bundle would exist only
inside a container that gets discarded.
"""
from __future__ import annotations
import datetime as dt, json, os, subprocess, sys

REPO = os.environ.get("EVCS01_REPO", "/home/claude/edl")
MISSION = os.environ.get("PKG_MISSION", "EVCS01")
BASE = os.environ.get("PKG_BASE", "b9f4804c575123492038774a4b756bc60dde67f5")  # CLEA01 C5 terminal
OUT = os.environ.get("PKG_OUT", f"/home/claude/{MISSION.lower()}_pkg")
sys.path.insert(0, f"{REPO}/OMLDCT02/code")
import omldct02_hashes as H


def git(*a):
    return subprocess.run(("git", "-C", REPO) + a, capture_output=True, text=True,
                          check=True).stdout.strip()


def main():
    os.makedirs(OUT, exist_ok=True)
    br = git("rev-parse", "--abbrev-ref", "HEAD")
    tip = git("rev-parse", "HEAD")
    commits = git("rev-list", "--reverse", f"{BASE}..{tip}").split()
    inc = f"{OUT}/{MISSION}_FINAL_INCREMENT.bundle"
    cap = f"{OUT}/{MISSION}_FINAL_EVIDENCE_CAPSULE.tar"
    for p in (inc, cap):
        if os.path.exists(p):
            os.remove(p)
    git("bundle", "create", inc, f"{BASE}..{tip}", br)
    git("archive", "--format=tar", "-o", cap, "HEAD", MISSION)
    git("bundle", "verify", inc)

    for rel, name in ((f"{MISSION}/out/{MISSION}_FINAL_REPORT.md", f"{MISSION}_FINAL_REPORT.md"),
                      (f"{MISSION}/out/{MISSION}_FINAL_DISPOSITION.json",
                       f"{MISSION}_FINAL_DISPOSITION.json"),
                      (f"{MISSION}/review/{MISSION}_CHECKER_RAW.txt",
                       f"{MISSION}_CHECKER_RAW.txt")):
        with open(f"{OUT}/{name}", "wb") as w:
            w.write(open(f"{REPO}/{rel}", "rb").read())

    pkg = [f"{MISSION}_FINAL_INCREMENT.bundle", f"{MISSION}_FINAL_EVIDENCE_CAPSULE.tar",
           f"{MISSION}_FINAL_REPORT.md", f"{MISSION}_FINAL_DISPOSITION.json",
           f"{MISSION}_CHECKER_RAW.txt"]
    sums = {f: H.file_sha256(f"{OUT}/{f}") for f in pkg}
    disp = json.load(open(f"{REPO}/{MISSION}/out/{MISSION}_FINAL_DISPOSITION.json"))

    man = {
        "MISSION": MISSION, "SECTION": "final external manifest",
        "GENERATED_UTC": dt.datetime.now(dt.timezone.utc).isoformat(),
        "FINAL_DISPOSITION": disp["FINAL_DISPOSITION"],
        "LAUNCHER_WAS_SELF_ISSUED": True,
        "BRANCH": br, "TIP": tip,
        "COMMITS": {f"C{i+1}": c for i, c in enumerate(commits)},
        "INTENTIONAL_COMMITS": len(commits), "MAX_INTENTIONAL_COMMITS": 3,
        "C3_WAS_AMENDED_ONCE_IN_PLACE_TO_INCLUDE_THIS_FILE": True,
        "BUNDLE_PREREQ": f"{BASE} (the CLEA01 C5 terminal tip)",
        "BUNDLE_PREREQ_IS_ALREADY_DURABLE_ON_WINDOWS_AS": "CLEA01/CLEA01_FINAL_INCREMENT.bundle",
        "NO_FULL_BUNDLE_AND_WHY": "the repository pack is ~571 MiB; the device bridge caps a "
            "committed file at 20 MB and a 124 MiB stage failed twice on wall-clock. A full bundle "
            "would live only in a container that is discarded. The increment plus the eight-bundle "
            "chain already on Windows restores the tip byte-for-byte.",
        "RESTORE_CHAIN_HEAD": "CLEA01/CLEA01_FINAL_INCREMENT.bundle, whose own chain is documented "
                              "in CLEA01_DURABILITY_RECORD.json",
        "A_TRAP_IN_THIS_ARCHIVE": "three of the upstream bundles declare their ref as HEAD, not as "
            "a branch. A restore driven by 'refs/heads/*:refs/heads/*' silently fetches nothing "
            "from them and fails four hops later pointing at the wrong bundle. Map each bundle's "
            "declared ref explicitly.",
        "PACKAGE": sums,
        "CHECKERS_DISPATCHED": 1,
        "LOAD_BEARING_DEFECT_COUNT": disp["LOAD_BEARING_DEFECT_COUNT"],
        "N_FINDINGS_ADJUDICATED": disp["N_FINDINGS_ADJUDICATED"],
        "N_CORRECTIONS_MADE": disp["N_CORRECTIONS_MADE"],
        "GATE0_PASS": disp["GATE0_PASS"],
        "SHAM_COMPOSITION": disp["SHAM_COMPOSITION"],
        "SELECTIVE_COMPOSITION_IS_UNINFORMATIVE_BY_CONSTRUCTION": True,
        "NEW_SCIENTIFIC_WORLDS_USED": 0,
        "CLEA01_STATUS": disp["CLEA01_STATUS"],
        "OMLDCT02_STATUS": disp["OMLDCT02_STATUS"],
        "OMLDCT02_PAIRED_STATISTICS": disp["OMLDCT02_PAIRED_STATISTICS"],
        "H3_STATUS": "NOT_TESTED", "REPRODUCTION_STATUS": "NOT_TESTED",
        "HEREDITY_STATUS": "NOT_TESTED", "AUTONOMOUS_COHESION_STATUS": "NOT_ESTABLISHED",
        "X_LAWSPEC_BASELINE": "UNCHANGED", "ARCHITECTURE_CHANGE_NECESSITY": "NOT_ESTABLISHED",
        "COMPANION_PAPER_V1_1_STATUS": "UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED",
    }
    man["MANIFEST_CONTENT_HASH"] = H.content_digest(man, extra_excluded=("MANIFEST_CONTENT_HASH",))
    mp = f"{OUT}/{MISSION}_FINAL_EXTERNAL_MANIFEST.json"
    json.dump(man, open(mp, "w"), indent=1)
    sums[f"{MISSION}_FINAL_EXTERNAL_MANIFEST.json"] = H.file_sha256(mp)
    with open(f"{OUT}/{MISSION}_FINAL_SHA256SUMS", "w", newline="\n") as w:
        for f in pkg + [f"{MISSION}_FINAL_EXTERNAL_MANIFEST.json"]:
            w.write(f"{sums[f]}  {f}\n")
    for f in sorted(os.listdir(OUT)):
        print(f"{os.path.getsize(OUT + '/' + f):>9}  {f}")
    print("TIP =", tip, " commits:", len(commits))


if __name__ == "__main__":
    main()
