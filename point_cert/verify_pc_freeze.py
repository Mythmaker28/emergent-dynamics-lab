import json,hashlib,sys,os
m=json.load(open(os.path.join(os.path.dirname(__file__),"..","docs","point_cert","POINT_CERT_FREEZE_MANIFEST.json")))
bad=0
for f,h in m["frozen_files"].items():
    got=hashlib.sha256(open(os.path.join(os.path.dirname(__file__),"..",f),"rb").read()).hexdigest()
    ok=got==h; bad+=(not ok); print(("OK  " if ok else "FAIL")+f" {f} {got[:16]}")
nd=hashlib.sha256(open(os.path.join(os.path.dirname(__file__),"..","noise_aware","nasi.py"),"rb").read()).hexdigest()
ok=nd==m["nasi_dependency_hash"]; bad+=(not ok); print(("OK  " if ok else "FAIL")+f" nasi.py dependency {nd[:16]}")
print("PC FREEZE VERIFY:","PASS" if bad==0 else f"FAIL({bad})"); sys.exit(1 if bad else 0)
