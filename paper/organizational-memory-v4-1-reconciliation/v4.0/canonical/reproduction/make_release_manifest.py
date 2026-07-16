"""Build RELEASE_MANIFEST.json + PUBLIC_RELEASE_TREE.txt by hashing the exact release inventory.
No new computation. Run: python -m reproduction.make_release_manifest"""
from __future__ import annotations
import os, json, hashlib, glob, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMMIT = "897f81d63f4ae67694446f326fe483739262585b"  # V3 tip (parent of the release branch)

INCLUDE = [
    # release engineering
    "release/README_RELEASE.md", "release/LICENSE-CODE", "release/LICENSE-DATA-TEXT",
    "release/CITATION.cff", "release/AUTHORS.md", "release/ENVIRONMENT.md",
    "release/DEPENDENCY_LICENSE_AUDIT.md", "release/CLEANROOM_REPRODUCTION_REPORT.md",
    "release/PORTABLE_DATA_AUDIT.md", "requirements-lock.txt", "release/pip_freeze_full.txt",
    "release/AUTHORIZE_COMMANDS.md", "release/VERDICT.md",
    # reproduction package (source)
    "reproduction/__init__.py", "reproduction/__main__.py", "reproduction/primary.py",
    "reproduction/decode.py", "reproduction/export_portable.py", "reproduction/make_release_manifest.py",
    "reproduction/EXPECTED.json",
    # portable data
    "release/data/*",
    # manuscript package (V3)
    "docs/paper/full/ORGANIZATIONAL_MEMORY_FULL_MANUSCRIPT_V3.pdf",
    "docs/paper/full/ORGANIZATIONAL_MEMORY_FULL_MANUSCRIPT_V3.tex",
    "docs/paper/full/SUPPLEMENT_V3.pdf", "docs/paper/full/SUPPLEMENT_V3.tex",
    "docs/paper/full/references.bib", "docs/paper/full/V2_TO_V3_CHANGELOG.md",
    "docs/paper/full/CLAIM_LEDGER_V3.md", "docs/paper/full/STATISTICAL_REAUDIT.md",
    "docs/paper/full/REPRODUCIBILITY_RELEASE_CHECKLIST.md", "docs/paper/full/VERDICT_V3.md",
    # provenance: raw data + gate certificates + audit specs
    "results/observer/tca_holdout_raw.pkl",
    "results/wd01_phasec/phasec_causal_transplant_raw.pkl",
    "results/wd01_phasec/phasec_causal_inplace_raw.pkl",
    "results/h2cert/h2cert_sealed_raw.pkl",
    "results/*/*_gate_certificate.json",
    "docs/audit/TCA_01_TRACKER_SPEC.md", "docs/audit/TCA_01_HOLDOUT_CERTIFICATION.md",
]

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""): h.update(c)
    return h.hexdigest()

def main():
    files = []
    for pat in INCLUDE:
        for p in sorted(glob.glob(os.path.join(ROOT, pat))):
            if os.path.isfile(p): files.append(os.path.relpath(p, ROOT))
    files = sorted(set(files))
    entries = [{"path": f, "bytes": os.path.getsize(os.path.join(ROOT, f)), "sha256": sha(os.path.join(ROOT, f))} for f in files]
    total = sum(e["bytes"] for e in entries)
    manifest = dict(
        release="organizational-memory-v1", status="PREPARED — NOT PUBLISHED (no push/tag/DOI)",
        source_commit=COMMIT, python="3.10.12", deps={"numpy": "2.2.6", "scipy": "1.15.3", "matplotlib": "3.10.9"},
        primary_command="python -m reproduction.primary --check",
        n_files=len(entries), total_bytes=total, files=entries,
    )
    with open(os.path.join(ROOT, "release", "RELEASE_MANIFEST.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    with open(os.path.join(ROOT, "release", "PUBLIC_RELEASE_TREE.txt"), "w") as f:
        f.write("PUBLIC RELEASE TREE — organizational-memory-v1 (PREPARED, NOT PUBLISHED)\n")
        f.write("source commit: %s\n" % COMMIT)
        f.write("files: %d   total: %.1f KiB\n" % (len(entries), total / 1024))
        f.write("=" * 78 + "\n")
        for e in entries:
            f.write("%10d  %s  %s\n" % (e["bytes"], e["sha256"][:12], e["path"]))
    print("manifest: %d files, %.1f KiB" % (len(entries), total / 1024))
    for e in entries: print("  %s  %s" % (e["sha256"][:10], e["path"]))

if __name__ == "__main__":
    main()
