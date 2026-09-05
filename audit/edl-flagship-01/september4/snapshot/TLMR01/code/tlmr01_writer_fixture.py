"""§5 — the WRITER and the READ-BACK, qualified on a non-scientific fixture seed before world 1."""
import sys,os,json,time,shutil
sys.path.insert(0,"/home/claude/edl/TLMR01/code")
import tlmr01_run as RUN, tlmr01_offline as OFF
RAW=RUN.RAW; os.makedirs(RAW,exist_ok=True)
t0=time.time()
rec=RUN.run_one(("LAW_A_B1","FIXTURE",999,71501))
chk=RUN.read_back([rec])
p=os.path.join(RAW,rec["tag"]+".npz")
A=OFF.Archive(p)
eps=OFF.episodes(A)
out={"SECTION":"5 — writer and read-back qualification","NON_SCIENTIFIC":True,
 "fixture_seed":71501,"law":"LAW_A_B1","role":"FIXTURE",
 "runtime_s":round(time.time()-t0,1),
 "meta_fields_present":sorted(rec.keys()),
 "steps_executed":rec["steps_executed"],"integrity_ok":rec["integrity_ok"],
 "TERMINAL_LABEL":rec["TERMINAL_LABEL"],
 "NARROW_DTYPES_LOSSLESS":rec["NARROW_DTYPES_LOSSLESS"],
 "archive_bytes":rec["archive_bytes"],"technical_failure":rec["technical_failure"],
 "READ_BACK":chk[0],
 "OFFLINE_READER":{"T":A.T,"schema":A.schema["VERSION"],"n_episodes":len(eps),
   "M4_single_centre_steps":OFF.M4_exposure(A)["single_centre_steps"],
   "M1_strata":len(OFF.M1_fork_hazard(A)["exposure_by_n"])},
 "NO_PART_FILE_LEFT_BEHIND":not (os.path.exists(p+".part") or os.path.exists(p+".part.npz")),
 "ALL_PASS":bool(chk[0]["OK"] and rec["NARROW_DTYPES_LOSSLESS"] and not rec["technical_failure"]
                 and rec["steps_executed"]==11000)}
json.dump(out,open("/home/claude/edl/TLMR01/out/TLMR01_WRITER_QUALIFICATION.json","w"),indent=1)
print(json.dumps({k:v for k,v in out.items() if k!="meta_fields_present"},indent=1))
os.remove(p)
# the ledger and sealed files must not carry a fixture into the scientific record
for f in ("/home/claude/edl/TLMR01/out/TLMR01_RUN_LEDGER.jsonl","/home/claude/TLMR01/sealed.jsonl",
          "/home/claude/edl/TLMR01/out/TLMR01_READ_BACK.jsonl"):
    if os.path.exists(f): os.remove(f)
print("fixture archive and any fixture ledger lines removed")
