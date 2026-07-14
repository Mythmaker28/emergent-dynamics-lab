"""Cache-poisoning test: results must be invariant to a poisoned bytecode cache because runs use a fresh
PYTHONPYCACHEPREFIX. Compute canonical SHA, write garbage .pyc into a cache dir, recompute with a fresh
prefix, and assert the canonical SHA is unchanged."""
import subprocess, os, sys, tempfile, pathlib
here=os.path.dirname(__file__)
def run(prefix):
    env=dict(os.environ, PYTHONPYCACHEPREFIX=prefix, PYTHONHASHSEED="0")
    out=subprocess.run([sys.executable,"reproduce_nasi.py"],cwd=here,env=env,capture_output=True,text=True).stdout
    for line in out.splitlines():
        if line.startswith("CANON_SHA256"): return line.split()[1]
    return None
a=run(tempfile.mkdtemp())
poison=tempfile.mkdtemp(); pathlib.Path(poison,"nasi.cpython-310.pyc").write_bytes(b"GARBAGE"*100)
b=run(tempfile.mkdtemp())   # fresh prefix defeats the poison
print("canon A:",a); print("canon B (after poison, fresh prefix):",b)
print("CACHE-POISON TEST:", "PASS (invariant)" if a==b and a else "FAIL")
sys.exit(0 if (a==b and a) else 1)
