# Executed commands and outputs

Task checkout: C:/Users/tommy/Documents/ising-life-manuscript-v2-final-seal-01

Existing scientific Python: C:/Users/tommy/Documents/ising-v3-recovery/ising v3/.venv/Scripts/python.exe

The following commands were executed using that Python from the task checkout. PYTHONUTF8=1 was set. Each subprocess in reproduce.py fails closed. PDF builds use SOURCE_DATE_EPOCH=1788480000.

~~~text
python paper/organiser-bound-source-response-operator/code/capture_recovery.py
python paper/organiser-bound-source-response-operator/code/audit_final.py --pqec-raw .audit-work/pqec/ISING_LIFE_RAW_PQEC01/raw
python paper/organiser-bound-source-response-operator/code/reproduce.py --tectonic .tools/tectonic.exe
python -m pytest paper/organiser-bound-source-response-operator/code/test_audit.py -q --junitxml=paper/organiser-bound-source-response-operator/provenance/TEST_RESULTS.xml
~~~

The first command was executed only once to capture exact Git bytes; it now refuses to overwrite SOURCE_MANIFEST.json. The optional PQEC check was executed against the separately extracted original archive.

PDF QA uses the bundled Python with pypdf:

~~~text
python paper/organiser-bound-source-response-operator/code/pdf_qa.py
pdftoppm -r 80 -png paper/organiser-bound-source-response-operator/manuscript/MANUSCRIPT.pdf .audit-work/pdf-qa/main
pdftoppm -r 80 -png paper/organiser-bound-source-response-operator/supplement/SUPPLEMENT.pdf .audit-work/pdf-qa/supp
~~~

All twelve PDF pages and all four figures were visually inspected; final bindings are in VISUAL_QA.json. Overlapping figure annotations and a table interrupting a long status were corrected in source, followed by rebuilding. The initial supplement path overflow was resolved through URL/path wrapping. A remaining underfull paragraph warning is typographic and has no lost text. A Fontconfig startup warning did not prevent embedded-font PDFs from being generated and inspected.

The packaging/standalone command is:

~~~text
python paper/organiser-bound-source-response-operator/code/package_review.py --verify --tectonic .tools/tectonic.exe
python paper/organiser-bound-source-response-operator/code/readiness.py
python paper/organiser-bound-source-response-operator/code/package_review.py
~~~

The first extracts a candidate ZIP to an isolated directory, rebuilds it without Git, runs four tests and compares deterministic numerical, figure, table, claim and PDF hashes. The final ZIP incorporates the resulting verification and readiness records. Its separate SHA256SUMS and DELIVERY_MANIFEST.json are the shipping integrity records.

Git checks include no science-source diff from 06c592313df96601de8d2a89676d5a5cf79fc414, the explicit changed-file inventory, source hashes, and branch/PR readback. No full legacy engine suite is rerun because no physics, tracker or experiment code is changed.
