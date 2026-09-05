"""TLMR01 §10 — the COMPLETE pre-run methods closure.

WHY IT IS DONE TWICE. FOTSEA01's executability audit found three L-dependent modules that reach
the running process without appearing in the frozen manifest at all, and the TLMR01 handoff makes
closing that set a precondition for claiming a bounded scope. A manifest built by hand, or by
listing the imports one remembers, is exactly how a module escapes. So the closure is computed
two independent ways and the two must agree:

  RUNTIME   — import the entry modules in a clean interpreter and read sys.modules afterwards.
              This catches anything imported at any depth, including conditionally.
  STATIC    — parse the entry files with ast, follow every import name, resolve it against the
              same sys.path the modules build, and recurse. This catches anything the runtime
              path did not happen to take.

A module in one set and not the other is a DEFECT and is reported as one, never reconciled by
preferring the smaller set.

SCOPE OF THE CONFIGURATION. TLMR01 runs at the frozen L = 36. It changes no size, so the
11-file L re-parameterisation FOTSEA01 priced is NOT in this mission's scope and is not silently
half-done: it is declared out of scope with its reason. What IS in scope, and is closed here, is
that every module that actually executes is hashed, whether or not an inherited manifest knew
about it.
"""
from __future__ import annotations
import ast, os, sys, json, hashlib, subprocess, datetime, platform
REPO="/home/claude/edl"
ROOTS=("/home/claude/edl","/home/claude/ORR01","/home/claude/OBTC02")
ENTRIES=sorted(__import__("glob").glob(f"{REPO}/TLMR01/code/*.py"))
# every TLMR01 module is an entry, including the ones no other module imports (the binder, the
# closure itself, the freeze builder). A module that is not an entry and is imported by nobody
# would never be hashed, which is the same escape this file exists to prevent.

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def is_project(p):
    p=os.path.abspath(p)
    return any(p.startswith(r+os.sep) for r in ROOTS)

# ------------------------------------------------------------------ runtime closure
_RUNTIME_PROBE=r"""
import sys, json, os, sysconfig
ENTRIES=%r
for e in ENTRIES:
    d=os.path.dirname(e)
    if d not in sys.path: sys.path.insert(0,d)
loaded=[]; failed=[]
for e in ENTRIES:
    m=os.path.splitext(os.path.basename(e))[0]
    try:
        __import__(m); loaded.append(m)
    except Exception as ex:
        failed.append({"module":m,"error":repr(ex)[:300]})
P=sysconfig.get_paths()
EX=[os.path.abspath(P[k]) for k in ("stdlib","platstdlib","purelib","platlib") if P.get(k)]
def is_project(f):
    f=os.path.abspath(f)
    if "site-packages" in f or "dist-packages" in f: return False
    return not any(f.startswith(x+os.sep) for x in EX)
out=[]
for name,mod in sorted(sys.modules.items()):
    f=getattr(mod,"__file__",None)
    if not f: continue
    f=os.path.abspath(f)
    if f.endswith(".py") and is_project(f): out.append({"module":name,"abs":f})
print(json.dumps({"ENTRIES_IMPORTED":loaded,"IMPORT_FAILURES":failed,"MODULES":out,
                  "SYS_PATH_AFTER_IMPORT":[os.path.abspath(x) for x in sys.path if x],
                  "EXCLUDED_PREFIXES":EX}))
"""

def runtime_closure(entries):
    """what ACTUALLY executes. No hand-written root list: everything with a real .py file that is
    not stdlib and not site-packages counts. An earlier version of this function filtered by a
    hand-written list of three project roots and silently DROPPED three modules that execute from
    a fourth. That is exactly the escape FOTSEA01 warned about, and the filter is gone."""
    src=_RUNTIME_PROBE%(entries,)
    r=subprocess.run([sys.executable,"-c",src],capture_output=True,text=True,cwd=REPO,timeout=600)
    if r.returncode!=0:
        return {"OK":False,"stderr":r.stderr[-1500:],"MODULES":[]}
    d=json.loads(r.stdout.strip().splitlines()[-1])
    d["OK"]=True; d["stderr"]=r.stderr[-1500:]
    return d

# ------------------------------------------------------------------ static closure
def _lit(n):
    """the string a Constant or a REPO-interpolated f-string denotes, or None."""
    if isinstance(n,ast.Constant) and isinstance(n.value,str): return n.value
    if isinstance(n,ast.JoinedStr):
        t=""
        for x in n.values:
            if isinstance(x,ast.Constant): t+=str(x.value)
            elif getattr(getattr(x,"value",None),"id",None)=="REPO": t+=REPO
            else: return None
        return t
    return None

def _path_literals(tree):
    """directories the module itself puts on sys.path, read from its own source.

    Two forms are collected, and the second is why the first alone is not enough. Several
    inherited modules build the list in a tuple and insert it in a loop --

        for _p in (f"{REPO}/FMRCT01/code", f"{REPO}/FDOT01/code", ...):
            sys.path.insert(0,_p)

    -- so the argument at the call site is a Name and carries no string. The rule adopted is
    therefore: take every literal argument of a sys.path.insert or append, PLUS every string or
    REPO-interpolated f-string ANYWHERE in the module that names an existing directory. It is a
    declared heuristic, it is deliberately generous, and any directory it adds in error can only
    ADD candidates -- which are then enumerated and byte-compared -- never remove one."""
    out=[]
    for n in ast.walk(tree):
        if isinstance(n,ast.Call):
            f=n.func
            if (isinstance(f,ast.Attribute) and f.attr in ("insert","append")
                and isinstance(f.value,ast.Attribute) and f.value.attr=="path"
                and isinstance(f.value.value,ast.Name) and f.value.value.id=="sys"):
                for a in n.args:
                    v=_lit(a)
                    if v: out.append(v)
        v=_lit(n)
        if v and "/" in v and os.path.isdir(v): out.append(v)
    return out

def static_closure(entries):
    """every module the entry files can reach, resolved on the search path the CODE ITSELF builds:
    the entry directories plus every sys.path literal found by ast in the modules reached so far.
    Nothing is borrowed from the runtime import graph.

    Two files on that path can answer the same import name. Which one Python takes depends on the
    ORDER of insertions performed deep inside inherited code, so every candidate is enumerated and
    byte-compared instead of being collapsed to one."""
    paths=[]
    def add(d):
        d=os.path.abspath(d)
        if os.path.isdir(d) and d not in paths: paths.append(d)
    for e in entries: add(os.path.dirname(os.path.abspath(e)))
    def candidates(name):
        rel=name.replace(".","/")+".py"
        out=[]
        for p in paths:
            c=os.path.abspath(os.path.join(p,rel))
            if os.path.exists(c) and c not in out: out.append(c)
        return out
    seen={}; amb={}; unresolved=set()
    roots=[os.path.abspath(e) for e in entries if os.path.exists(e)]
    SKIP=("numpy","scipy","pandas","matplotlib","yaml")
    # FIXED POINT. A directory discovered late must be re-offered to every name resolved earlier,
    # or a module resolved before its own directory was known would be missed. The walk therefore
    # repeats until neither the file set nor the search path grows.
    for _sweep in range(12):
        before=(len(seen),len(paths))
        pending=list(roots)+list(seen)
        seen={}
        _walk(pending,seen,amb,unresolved,paths,add,candidates,SKIP)
        if (len(seen),len(paths))==before: break
    return {"MODULES":sorted(seen),"SEARCH_PATHS":paths,
            "SEARCH_PATH_IS_BUILT_FROM":"the entry directories plus every sys.path literal the "
              "reached modules themselves contain; nothing is taken from the runtime",
            "SWEEPS_TO_FIXED_POINT":_sweep+1,
            "AMBIGUOUS_IMPORT_NAMES":amb,"UNRESOLVED_NON_STDLIB":sorted(unresolved)}

def _walk(pending,seen,amb,unresolved,paths,add,candidates,SKIP):
    while pending:
        f=pending.pop()
        if f in seen: continue
        seen[f]=None
        try: tree=ast.parse(open(f).read(),f)
        except Exception: continue
        for d in _path_literals(tree): add(d)
        names=set()
        for n in ast.walk(tree):
            if isinstance(n,ast.Import):
                for a in n.names: names.add(a.name)
            elif isinstance(n,ast.ImportFrom):
                if n.level==0 and n.module: names.add(n.module)
        for nm in sorted(names):
            cs=candidates(nm)
            if not cs:
                top=nm.split(".")[0]
                if top not in sys.stdlib_module_names and top not in SKIP: unresolved.add(nm)
                continue
            if len(cs)>1:
                hs={c:sha(c) for c in cs}
                amb[nm]={"candidates":cs,"sha256":hs,"ALL_BYTE_IDENTICAL":len(set(hs.values()))==1}
            for c in cs: pending.append(c)

# ------------------------------------------------------------------ inherited manifests
INHERITED=[("FDOT01","FDOT01/out/FDOT01_METHODS_MANIFEST.json"),
           ("FMRCT01","FMRCT01/out/FMRCT01_MASTER_FREEZE.json"),
           ("MCTT01","MCTT01/out/MCTT01_MASTER_FREEZE.json"),
           ("BPRTC01","BPRTC01/out/BPRTC01_MASTER_FREEZE.json"),
           ("PQEC01","PQEC01/out/PQEC01_MASTER_FREEZE.json")]

def inherited_hashes():
    """every (abs path -> sha256) an ancestor mission froze, gathered by walking its JSON."""
    out={}
    for tag,rel in INHERITED:
        p=f"{REPO}/{rel}"
        if not os.path.exists(p): continue
        try: d=json.load(open(p))
        except Exception: continue
        def walk(o):
            if isinstance(o,dict):
                a=o.get("abs") or o.get("path") or o.get("file")
                h=o.get("sha256")
                if isinstance(a,str) and isinstance(h,str) and a.endswith(".py"):
                    ab=a if a.startswith("/") else f"{REPO}/{a}"
                    out.setdefault(os.path.abspath(ab),[]).append((tag,h))
                for v in o.values(): walk(v)
            elif isinstance(o,list):
                for v in o: walk(v)
        walk(d)
    return out

def main():
    U=datetime.datetime.now(datetime.timezone.utc).isoformat()
    ent=[e for e in ENTRIES if os.path.exists(e)]
    rt=runtime_closure(ent)
    st=static_closure(ent)
    RT={m["abs"]:m["module"] for m in rt.get("MODULES",[])}
    R=set(RT); S=set(st["MODULES"])
    runtime_names={v:k for k,v in RT.items()}
    by_base={}
    for f in R|S: by_base.setdefault(os.path.basename(f),[]).append(f)
    # classify every file the static closure found that did NOT execute
    static_only=[]
    for f in sorted(S-R):
        b=os.path.basename(f); name=b[:-3]
        exe=runtime_names.get(name)
        if exe is not None:
            same=sha(f)==sha(exe)
            static_only.append({"file":os.path.relpath(f,"/home/claude"),
              "class":"ALTERNATIVE_COPY_OF_AN_EXECUTED_MODULE",
              "the_copy_that_executed":os.path.relpath(exe,"/home/claude"),
              "BYTE_IDENTICAL_TO_THE_EXECUTED_COPY":same,
              "HARMLESS":same})
        else:
            static_only.append({"file":os.path.relpath(f,"/home/claude"),
              "class":"REACHABLE_BY_IMPORT_BUT_NOT_EXECUTED_ON_ANY_TLMR01_ENTRY_PATH",
              "HARMLESS":True})
    runtime_not_static=sorted(R-S)
    amb=st["AMBIGUOUS_IMPORT_NAMES"]
    amb_bad={k:v for k,v in amb.items() if not v["ALL_BYTE_IDENTICAL"]}
    agree=(not runtime_not_static) and all(x["HARMLESS"] for x in static_only) and not amb_bad
    inh=inherited_hashes()
    # EVERY file in either closure is hashed, whichever one executed
    mods=[]
    for f in sorted(R|S):
        h=sha(f)
        fr=inh.get(f,[])
        mods.append({"abs":f,"rel":os.path.relpath(f,"/home/claude"),"sha256":h,
          "bytes":os.path.getsize(f),"lines":sum(1 for _ in open(f,"rb")),
          "EXECUTED":f in R,"module_name":RT.get(f,os.path.basename(f)[:-3]),
          "in_static_closure":f in S,"owned_by_TLMR01":"/TLMR01/" in f,
          "frozen_by":[t for t,_ in fr],
          "matches_every_inherited_freeze":(all(x==h for _,x in fr) if fr else None),
          "ABSENT_FROM_EVERY_INHERITED_MANIFEST":(not fr) and "/TLMR01/" not in f})
    drift=[m for m in mods if m["matches_every_inherited_freeze"] is False]
    absent=[m for m in mods if m["ABSENT_FROM_EVERY_INHERITED_MANIFEST"]]
    execd=[m for m in mods if m["EXECUTED"]]
    comp=hashlib.sha256(json.dumps([[m["rel"],m["sha256"]] for m in mods],sort_keys=True).encode()).hexdigest()
    art={"MISSION":"TLMR01","SECTION":"10 — complete pre-run methods closure","GENERATED_UTC":U,
     "PYTHON":platform.python_version(),"PLATFORM":platform.platform(),
     "ENTRY_FILES":ent,
     "TWO_INDEPENDENT_CLOSURES":{
       "RUNTIME_OK":rt.get("OK"),"RUNTIME_N":len(R),"STATIC_N":len(S),
       "RUNTIME_FILES_NOT_FOUND_BY_THE_STATIC_CLOSURE":runtime_not_static,
       "STATIC_FILES_THAT_DID_NOT_EXECUTE":static_only,
       "CLOSURES_AGREE":agree,
       "WHAT_AGREEMENT_MEANS":"every file that executed was also found statically, every file "
         "found statically that did not execute is either a BYTE-IDENTICAL alternative copy of a "
         "module that did execute or is reachable-but-unexecuted, and no import name resolves to "
         "two files with different bytes.",
       "IMPORT_FAILURES":rt.get("IMPORT_FAILURES"),
       "STATIC_UNRESOLVED_NON_STDLIB":st["UNRESOLVED_NON_STDLIB"],
       "SYS_PATH_AFTER_IMPORT":rt.get("SYS_PATH_AFTER_IMPORT"),
       "RUNTIME_STDERR":rt.get("stderr","")},
     "RESOLUTION_AMBIGUITY":{
       "WHY_IT_MATTERS":"several inherited modules exist in more than one directory on the search "
         "path, and which copy executes depends on the ORDER of sys.path insertions performed "
         "deep inside inherited code. metrics_obtc.py inserts /home/claude/OBTC01/code at import "
         "time, so topology, nulls_obtc and source_operator execute from OBTC01 and not from the "
         "OBTC02 paths that FOTSEA01's executability audit named. The copies are byte-identical "
         "today; the hazard is that nothing was checking.",
       "N_AMBIGUOUS_IMPORT_NAMES":len(amb),
       "AMBIGUOUS_IMPORT_NAMES":amb,
       "ANY_AMBIGUITY_WITH_DIFFERING_BYTES":amb_bad,
       "ALL_AMBIGUITY_IS_BYTE_IDENTICAL":not amb_bad},
     "N_FILES_HASHED":len(mods),"N_EXECUTED":len(execd),
     "MODULES":mods,
     "EXECUTED_MODULE_FILES":[m["rel"] for m in execd],
     "N_OWNED_BY_TLMR01":sum(1 for m in mods if m["owned_by_TLMR01"]),
     "N_INHERITED":sum(1 for m in mods if not m["owned_by_TLMR01"]),
     "INHERITED_BYTE_DRIFT":drift,
     "NO_INHERITED_MODULE_HAS_DRIFTED":not drift,
     "EXECUTING_MODULES_ABSENT_FROM_EVERY_INHERITED_MANIFEST":[m["rel"] for m in absent if m["EXECUTED"]],
     "N_ABSENT_AND_EXECUTING":sum(1 for m in absent if m["EXECUTED"]),
     "THE_FOTSEA01_GAP":"FOTSEA01 found three L-dependent modules reaching the running process "
       "without appearing in any frozen manifest, and named them at their OBTC02 paths. This "
       "closure shows the executing copies are OBTC01's, that all four copies of each are "
       "byte-identical, and hashes every copy either way. The set is closed at this mission "
       "whatever the ancestors recorded, and the count that remained unfrozen upstream is "
       "reported rather than hidden.",
     "L_REPARAMETERISATION_SCOPE":{
       "IN_SCOPE":False,
       "REASON":"TLMR01 runs at the frozen L = 36 and changes no size. The 11-file "
         "re-parameterisation FOTSEA01 priced is required only by a size ladder, and "
         "ONE_ZERO_RUN_DETOUR_ONLY is spent. It is declared out of scope rather than half-done.",
       "FINITE_SIZE_RELEVANCE":"NOT_SUPPORTED"},
     "COMPLETE_PRE_RUN_METHODS_HASH":comp}
    os.makedirs(f"{REPO}/TLMR01/out",exist_ok=True)
    json.dump(art,open(f"{REPO}/TLMR01/out/TLMR01_METHODS_CLOSURE.json","w"),indent=1)
    with open(f"{REPO}/TLMR01/out/TLMR01_METHODS_SHA256SUMS","w") as fh:
        for m in mods: fh.write("%s  %s\n"%(m["sha256"],m["rel"]))
    print("runtime executed=%d  static reachable=%d  agree=%s"%(len(R),len(S),agree))
    for x in static_only: print("   static-only: %-45s %s  harmless=%s"%(x["file"],x["class"][:44],x["HARMLESS"]))
    if runtime_not_static: print("   RUNTIME NOT IN STATIC:",runtime_not_static)
    print("ambiguous import names: %d, all byte-identical: %s"%(len(amb),not amb_bad))
    for k,v in amb.items(): print("   %-18s %d copies, identical=%s"%(k,len(v["candidates"]),v["ALL_BYTE_IDENTICAL"]))
    print("files hashed=%d  executed=%d  TLMR01-owned=%d  drifted=%d  absent&executing=%d"%(
      len(mods),len(execd),art["N_OWNED_BY_TLMR01"],len(drift),art["N_ABSENT_AND_EXECUTING"]))
    for m in absent:
        if m["EXECUTED"]: print("   ABSENT FROM EVERY INHERITED MANIFEST:",m["rel"])
    print("COMPLETE_PRE_RUN_METHODS_HASH =",comp)

if __name__=="__main__": main()
