"""Mid-run durability: export the SMALL state off the container.

It ships the run ledger, the read-back log, the sealed per-world records and a manifest of every
archive written so far with its sha256 and byte count. The per-cell archives themselves, about
1.2 GB, travel at the raw commitment as split bundles.

Nothing here is read by the operator: it is packed and shipped. The sealed records contain
outcomes and are deliberately not printed.
"""
from __future__ import annotations
import os, json, hashlib, tarfile, datetime, sys
REPO="/home/claude/edl"; OUT=f"{REPO}/TLMR01/out"; RAW="/home/claude/TLMR01/raw"
def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()
def main():
    U=datetime.datetime.now(datetime.timezone.utc).isoformat()
    files=sorted(f for f in os.listdir(RAW) if f.endswith(".npz"))
    man={"MISSION":"TLMR01","SECTION":"14 — archive manifest, incremental","GENERATED_UTC":U,
     "N_ARCHIVES":len(files),
     "TOTAL_BYTES":sum(os.path.getsize(os.path.join(RAW,f)) for f in files),
     "ARCHIVES":[{"file":f,"bytes":os.path.getsize(os.path.join(RAW,f)),
                  "sha256":sha(os.path.join(RAW,f))} for f in files]}
    json.dump(man,open(f"{OUT}/TLMR01_ARCHIVE_MANIFEST.json","w"),indent=1)
    with open(f"{OUT}/TLMR01_ARCHIVE_SHA256SUMS","w") as fh:
        for a in man["ARCHIVES"]: fh.write("%s  %s\n"%(a["sha256"],a["file"]))
    tp="/tmp/TLMR01_STATE.tar.gz"
    with tarfile.open(tp,"w:gz") as t:
        for p,n in ((f"{OUT}/TLMR01_RUN_LEDGER.jsonl","TLMR01_RUN_LEDGER.jsonl"),
                    (f"{OUT}/TLMR01_READ_BACK.jsonl","TLMR01_READ_BACK.jsonl"),
                    ("/home/claude/TLMR01/sealed.jsonl","sealed.jsonl"),
                    (f"{OUT}/TLMR01_ARCHIVE_MANIFEST.json","TLMR01_ARCHIVE_MANIFEST.json"),
                    (f"{OUT}/TLMR01_ARCHIVE_SHA256SUMS","TLMR01_ARCHIVE_SHA256SUMS"),
                    (f"{OUT}/TLMR01_PRE_RUN_DURABILITY.json","TLMR01_PRE_RUN_DURABILITY.json"),
                    (f"{OUT}/TLMR01_CHECK_PROTOCOL.json","TLMR01_CHECK_PROTOCOL.json"),
                    (f"{OUT}/TLMR01_ANALYSIS_QUALIFICATION.json","TLMR01_ANALYSIS_QUALIFICATION.json"),
                    (f"{OUT}/TLMR01_POST_FREEZE_ADDENDUM.json","TLMR01_POST_FREEZE_ADDENDUM.json"),
                    (f"{REPO}/TLMR01/code/tlmr01_analysis_fixture.py","tlmr01_analysis_fixture.py"),
                    (f"{REPO}/TLMR01/code/tlmr01_export_state.py","tlmr01_export_state.py")):
            if os.path.exists(p): t.add(p,arcname=n)
    print(json.dumps({"archives":len(files),"archive_MB":round(man["TOTAL_BYTES"]/1e6,1),
                      "state_tar":tp,"state_bytes":os.path.getsize(tp),
                      "state_sha256":sha(tp)}))
if __name__=="__main__": main()
