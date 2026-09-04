# Ising Life — source-response manuscript V2

Read manuscript/MANUSCRIPT.pdf, then supplement/SUPPLEMENT.pdf. The French delivery report is ASTRA_HANDOFF_FR.md. The current machine-derived review status is provenance/PAPER_SUBMISSION_READINESS.json, explained in provenance/PAPER_SUBMISSION_READINESS.md. READY_FOR_REVIEW means a traceable, internally audited manuscript ready for critical reading; it is not independent peer review or journal acceptance.

The central result is conditional point compatibility of the frozen OBFOR01 predictor. A historical-copy baseline also passes. SEAL01 corrections, uncertainty, outcome-conditioned historical selection and related negative dispositions are retained.

## Rebuild from existing data

Keep this directory under paper/organiser-bound-source-response-operator inside the extracted review archive. Its sibling programme directories contain the 482 pinned source inputs. The archive is portable and requires no Git installation for the numerical build.

From this directory, with the audited Python environment:

~~~text
python code/reproduce.py
python -m pytest code/test_audit.py -q
python code/reproduce.py --tectonic /absolute/path/to/tectonic
python code/pdf_qa.py
~~~

The first command verifies the immutable source manifest, reads existing NPZ records, reproduces summaries, 48 numerical bindings, four figures and the arm table, and lints 36 major claims. No engine or predictor simulation is invoked. The second runs four integrity/quantile tests. The third additionally builds both PDFs. The fourth requires pypdf and checks PDF text and TeX logs. Exact tools and paths used here are in provenance/ENVIRONMENT.json; Python versions are pinned in requirements.txt. Tectonic may fetch its TeX bundle on first use; this task warmed its cache. Numerical rebuilding is offline.

The source manifest is an input. Never regenerate it to resolve a failed hash. capture_recovery.py is the one-time provenance capture tool and refuses to run if that manifest exists. Legacy programme code retains its original container paths and is supplied as evidence, not as a portable simulation launcher. V2 entry points are only the scripts in this paper's code directory.

The four figure filenames are preserved for compatibility: fig1 is the information-flow schematic, fig2 the fresh comparisons, fig4 the ablation/replica comparison (Figure 3 in the text), and fig3 the historical inclusion sensitivity (Figure 4). All are generated; no manual image alteration is used.

## Provenance and scope

The source-response history is pinned at 06c592313df96601de8d2a89676d5a5cf79fc414. The original delivered manuscript is preserved at commit 0a872ac. No newer V2 was found; this package is its new editorial V2. Obsolete paper summaries and build debris are removed from the current package, with the list in provenance/SUPERSEDED_FILES.txt and the originals retained in that commit. They are not current scientific authority.

EVIDENCE_CLAIM_MATRIX.csv binds claims to files, paths, hashes, evidence levels and limitations. provenance/SOURCE_MANIFEST.json binds all selected inputs to Git objects; GIT_FREEZE_VERIFICATION.json records fourteen unchanged files and freeze-before-raw ancestry. REPRODUCIBILITY_AUDIT.md describes exactly what was recomputed and what was only documentary.

PQEC01's 128 NPZ archives (1,004,089,434 uncompressed bytes) were all hash/schema checked during this task. They are an external context package, not inputs to these four figures. Their per-file verification is included. To repeat it, extract the separately identified archive and run:

~~~text
python code/audit_final.py --pqec-raw /path/to/extracted/raw
~~~

Without this argument a rebuild does not reverify the external PQEC bytes. Original archive locations, sizes and SHA-256 hashes are recorded in provenance/RECOVERY_ARCHIVES.json.

The independent unit is one seeded engine arm. Intermediate lattice snapshots are unavailable; stored frame radii and final lattices are available. Thus only the final-frame quantile is independently recomputed from lattice occupancy. No new campaign, independent full-engine replication or external manuscript review is claimed. The governing historical run-budget mandate is absent: compliance is UNKNOWN, not a proven violation. No manuscript publication, journal submission, DOI, deposition or merge is authorized by this package.

Route E and the persistence papers are separate. MYQBD01, PQEC01, FLCR01 and EXP-SC-IOM-00 appear only with their qualified documentary scope. INDIVIDUATION FAIL remains a failure. Historical STOP__ARCHITECTURE_CHANGE_REQUIRED dispositions are not reversed. No successor campaign follows from this editorial closeout.
