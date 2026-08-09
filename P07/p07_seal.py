"""Seal a protocol: inject code SHA-256s, then write the protocol's own SHA-256."""
import hashlib, json, sys
from pathlib import Path

proto = sys.argv[1]
files = sys.argv[2:]
d = json.loads(Path(proto).read_text())
d.pop("code_sha256_placeholder", None)
d["code_sha256"] = {f: hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in files}
txt = json.dumps(d, indent=1, sort_keys=True)
Path(proto).write_text(txt)
h = hashlib.sha256(Path(proto).read_bytes()).hexdigest()
Path(proto.replace(".json", ".sha256")).write_text(h + "  " + proto + "\n")
print(f"SEALED {proto}\n  sha256 = {h}")
for f, v in d["code_sha256"].items():
    print(f"  {f:<22} {v}")
