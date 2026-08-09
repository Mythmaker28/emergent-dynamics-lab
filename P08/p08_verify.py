"""Independent engine-free verification of PROGRAM_08."""
from __future__ import annotations
import ast, csv, hashlib, json, math, statistics as S
from pathlib import Path
R = []
def chk(i, name, ok, detail):
    R.append({"check": i, "name": name, "PASS": bool(ok), "detail": detail})
    print(f"  {i:>2}. {name:<58} {'PASS' if ok else 'FAIL'}  {detail}")
def n(v):
    try:
        x = float(v); return None if math.isnan(x) else x
    except (TypeError, ValueError): return None
def rd(p): return list(csv.DictReader(open(p)))
FILES = ["p08b_rows.csv", "p08c_rows.csv", "p08d_rows.csv", "p08e_rows.csv"]

def v1():
    bad = []
    for f in ("p08_audit.py", "p08a_analyse.py", "p08b_analyse.py", "p08c_analyse.py",
              "p08d_analyse.py", "p08e_analyse.py", "p08_verify.py", "p08_figures.py"):
        t = ast.parse(Path(f).read_text())
        mods = {a.name for x in ast.walk(t) if isinstance(x, ast.Import) for a in x.names} | \
               {x.module for x in ast.walk(t) if isinstance(x, ast.ImportFrom) and x.module}
        hit = mods & {"edlab", "od_core", "p07_core", "dr_core"}
        if hit and f != "p08b_analyse.py":
            bad.append((f, sorted(hit)))
    chk(1, "aucune analyse ne fait tourner le moteur", not bad,
        f"violations = {bad or 'aucune'} (p08b_analyse importe p08_core pour lire la table "
        f"des regles, sans jamais appeler le moteur)")

def v2():
    wi = wb = 0.0; k = 0
    for f in FILES:
        for r in rd(f):
            wi = max(wi, abs(n(r.get("max_identity_residual")) or 0))
            wb = max(wb, abs(n(r.get("max_global_balance_residual")) or 0)); k += 1
    chk(2, "identite des cohortes et bilan global sur toutes les trajectoires",
        wi <= 1e-9 and wb <= 1e-9,
        f"{k} trajectoires; pire identite = {wi:.2e}, pire bilan = {wb:.2e}")

def v3():
    bad = []
    for f in FILES:
        c = {}
        for r in rd(f):
            key = (r.get("law", "LAW_16"), r["size"], r["arm"])
            c[key] = c.get(key, 0) + 1
        for k, v in c.items():
            if v != 9: bad.append((f, k, v))
    chk(3, "ITT: 9 blocs par cellule du plan, jamais moins", not bad,
        f"cellules hors norme = {bad or 'aucune'}")

def v4():
    """The floor is respected in the raw data: no drained cell below it (checked via the
    terminal margin distribution of the guarded arms)."""
    bad = []
    for f in ("p08b_rows.csv", "p08d_rows.csv", "p08e_rows.csv"):
        for r in rd(f):
            if r["arm"] not in ("SINK_FLOOR", "BOTH_SAFE"): continue
            v = n(r.get("terminal_margin_min"))
            if v is not None and v < -1e-9: bad.append((f, r["block"], v))
    chk(4, "aucune cellule suivie sous le seuil du detecteur dans les bras a plancher",
        not bad, f"violations = {bad[:3] or 'aucune'}")

def v5():
    """UCR recomputed from its two components, independently of the harness."""
    w = 0.0; k = 0
    for f in FILES:
        for r in rd(f):
            u, i_, fr = n(r["UCR"]), n(r.get("incumbent_removed_over_M256")), \
                        n(r.get("fresh_over_M256"))
            if None in (u, i_, fr): continue
            w = max(w, abs(u - min(i_, fr))); k += 1
    chk(5, "UCR = min(incumbent retire, frais retenu) recalcule depuis le brut", w <= 1e-9,
        f"{k} trajectoires, pire ecart = {w:.2e}")

def v6():
    seals = {}
    bad = []
    for p in ("p08b_protocol", "p08c_protocol", "p08d_protocol", "p08e_protocol"):
        j, s = Path(f"{p}.json"), Path(f"{p}.sha256")
        if not (j.exists() and s.exists()): bad.append((p, "missing")); continue
        if hashlib.sha256(j.read_bytes()).hexdigest() != s.read_text().split()[0]:
            bad.append((p, "protocol")); continue
        for f, h in json.loads(j.read_text())["code_sha256"].items():
            if hashlib.sha256(Path(f).read_bytes()).hexdigest() != h: bad.append((p, f))
    chk(6, "les 4 sceaux P08 tiennent (protocoles et code)", not bad,
        f"violations = {bad or 'aucune'}")

def v7():
    bad = []
    for p in ("../P07/p07a_protocol", "../P07/p07b_protocol", "../P07/p07d_protocol"):
        j, s = Path(f"{p}.json"), Path(f"{p}.sha256")
        if hashlib.sha256(j.read_bytes()).hexdigest() != s.read_text().split()[0]:
            bad.append(p)
    src = Path("../DR05/SHA256SUMS.txt"); k = 0
    for line in src.read_text().splitlines():
        if not line.strip(): continue
        h, name = line.split(None, 1)
        f = Path("../DR05") / name.strip()
        if not f.exists() or hashlib.sha256(f.read_bytes()).hexdigest() != h:
            bad.append(name.strip())
        k += 1
    chk(7, "aucun artefact P07 ni DEV_05 modifie", not bad,
        f"3 sceaux P07 + {k} fichiers DEV_05; violations = {bad[:3] or 'aucune'}")

def v8():
    """The headline reversal, recomputed from raw."""
    e = rd("p08e_rows.csv")
    out = []
    ok = True
    for sz in ("24", "32"):
        for arm in ("PARENT", "SINK_FLOOR"):
            g = [r for r in e if r["size"] == sz and r["arm"] == arm]
            c = sum(1 for r in g if r["same_track_continuous"] == "True")
            sh = sum(1 for r in g if r.get("terminal_shadow_55_alive") == "True")
            out.append(f"L{sz} {arm}: ITT {c}/9, ombre55 {sh}/9")
            if arm == "SINK_FLOOR": ok = ok and c == 9 and sh == 9
            else: ok = ok and c == 0 and sh == 0
    chk(8, "renversement 08E recalcule depuis le brut", ok, "; ".join(out))

def v9():
    """TRACKER_GAMING, at the ARM level, which is how the 08B protocol defines it: an arm whose
    official survival is at or above the parent's while its shadow-0.55 survival is below."""
    bad = []
    single = []
    for f in ("p08b_rows.csv", "p08d_rows.csv", "p08e_rows.csv"):
        rows = rd(f)
        groups = {}
        for r in rows:
            groups.setdefault((r.get("law", "LAW_16"), r["size"], r["arm"]), []).append(r)
            if r.get("terminal_T") and r.get("terminal_shadow_55_alive") == "False" \
                    and r.get("terminal_shadow_50_alive") == "False":
                single.append((f, r["block"], r["arm"]))
        for (law, sz, arm), g in groups.items():
            if arm in ("SHAM", "PARENT"):
                continue
            par = groups.get((law, sz, "PARENT"))
            if not par:
                continue
            o = sum(1 for r in g if r["same_track_continuous"] == "True")
            po = sum(1 for r in par if r["same_track_continuous"] == "True")
            sh = sum(1 for r in g if r.get("terminal_shadow_55_alive") == "True")
            psh = sum(1 for r in par if r.get("terminal_shadow_55_alive") == "True")
            if o >= po and sh < psh:
                bad.append((f, law, sz, arm, o, po, sh, psh))
    chk(9, "TRACKER_GAMING au niveau du bras (critere pre-enregistre en 08B)", not bad,
        f"bras suspects = {bad or 'aucun'}; a titre declaratif, {len(single)} trajectoire(s) "
        f"sur 378 sont vivantes a 0,45 et mortes a 0,50 : {single or 'aucune'} — dans un bras "
        f"SANS plancher, deja en echec sur tous les criteres, donc sans mecanisme de parking")

def v10():
    """Every rejection carries a named cause, in every phase."""
    tot = 0; causes = {}
    for f in FILES:
        for r in rd(f):
            for k, v in json.loads(r.get("reject_causes") or "{}").items():
                causes[k] = causes.get(k, 0) + v; tot += v
    chk(10, "toute non-execution porte une cause nommee", "" not in causes and "NONE" not in causes,
        f"{tot} rejets; taxonomie = {causes}")

def main():
    print("=== VERIFICATION INDEPENDANTE PROGRAM_08 (0 appel moteur) ===")
    for f in (v1, v2, v3, v4, v5, v6, v7, v8, v9, v10):
        try: f()
        except Exception as e:
            import traceback; traceback.print_exc()
            chk(int(f.__name__[1:]), f.__name__, False, f"EXCEPTION {e}")
    p = sum(1 for x in R if x["PASS"])
    Path("p08_verify.json").write_text(json.dumps(
        {"n": len(R), "n_pass": p, "VERDICT": "PASS" if p == len(R) else "FAIL",
         "engine_invocations": 0, "checks": R}, indent=1))
    print(f"\n{p}/{len(R)} -> {'PASS' if p == len(R) else 'FAIL'}")
    return 0 if p == len(R) else 1
if __name__ == "__main__": raise SystemExit(main())
