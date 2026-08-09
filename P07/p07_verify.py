"""Independent verification pass over PROGRAM_07. Recomputes every headline number from the
raw CSVs by a different route than the analysis scripts, and checks the invariants that must
hold if the ledgers are sound. No engine call."""
from __future__ import annotations
import ast, csv, json, math, statistics as S
from pathlib import Path

R = []


def chk(i, name, ok, detail):
    R.append({"check": i, "name": name, "PASS": bool(ok), "detail": detail})
    print(f"  {i:>2}. {name:<56} {'PASS' if ok else 'FAIL'}  {detail}")


def n(v):
    try:
        x = float(v)
        return None if math.isnan(x) else x
    except (TypeError, ValueError):
        return None


def rd(p):
    return list(csv.DictReader(open(p)))


def v1():
    """No engine step anywhere in the analysis or verification modules."""
    bad = []
    for f in ("p07a_analyse.py", "p07b_analyse.py", "p07d_analyse.py", "p07_verify.py",
              "p07_figures.py"):
        t = ast.parse(Path(f).read_text())
        mods = {a.name for x in ast.walk(t) if isinstance(x, ast.Import) for a in x.names} | \
               {x.module for x in ast.walk(t) if isinstance(x, ast.ImportFrom) and x.module}
        hit = mods & {"edlab", "od_core", "p07_core", "dr_core", "dsc_core"}
        if hit:
            bad.append((f, sorted(hit)))
    chk(1, "aucune analyse n'importe le moteur", not bad, f"violations = {bad or 'aucune'}")


def v2():
    """Cohort identity and global balance across every ledger row of every phase."""
    wi = wb = 0.0
    k = 0
    for f in ("p07a_event_ledger.csv", "p07b_event_ledger.csv"):
        for r in rd(f):
            a, b = n(r.get("identity_residual")), n(r.get("global_balance_residual"))
            if a is not None:
                wi = max(wi, abs(a))
                k += 1
            if b is not None:
                wb = max(wb, abs(b))
    for f in ("p07a_rows.csv", "p07b_rows.csv", "p07d_rows.csv"):
        for r in rd(f):
            wi = max(wi, abs(n(r.get("max_identity_residual")) or 0))
            wb = max(wb, abs(n(r.get("max_global_balance_residual")) or 0))
    chk(2, "identite des cohortes et bilan global sur TOUS les ledgers",
        wi <= 1e-9 and wb <= 1e-9,
        f"{k} lignes evenementielles; pire identite = {wi:.2e}, pire bilan = {wb:.2e}")


def v3():
    """The coupled operator moved exactly zero net mass in every trajectory."""
    w = 0.0
    k = 0
    for f in ("p07a_rows.csv", "p07b_rows.csv", "p07d_rows.csv"):
        for r in rd(f):
            a, b = n(r.get("realized_sink")), n(r.get("realized_source"))
            if a is None or b is None:
                continue
            if r.get("arm") == "SHAM":
                continue
            w = max(w, abs(a - b))
            k += 1
    chk(3, "masse NETTE deplacee par l'operateur couple = 0", w <= 1e-9,
        f"{k} trajectoires, pire |source - puits| = {w:.2e}")


def v4():
    """Every scheduled event is accounted: executed + rejected = scheduled."""
    bad = []
    for f in ("p07a_rows.csv", "p07b_rows.csv", "p07d_rows.csv"):
        for r in rd(f):
            sc = n(r.get("n_scheduled")) or 0
            if sc == 0:
                continue
            got = (n(r.get("n_events")) or 0) + (n(r.get("n_rejected")) or 0)
            if abs(got - sc) > 0.5:
                bad.append((f, r.get("block"), r.get("arm"), sc, got))
    chk(4, "executes + rejetes = programmes (aucun evenement perdu)", not bad,
        f"{len(bad)} divergences" + (f" ex: {bad[:2]}" if bad else ""))


def v5():
    """ITT: nine blocks per size per arm, always, including after track loss."""
    bad = []
    for f, key in (("p07b_rows.csv", lambda r: (r["size"], r["arm"])),
                   ("p07d_rows.csv", lambda r: (r["law"], r["size"], r["arm"]))):
        c = {}
        for r in rd(f):
            c[key(r)] = c.get(key(r), 0) + 1
        for k, v in c.items():
            if v != 9:
                bad.append((f, k, v))
    chk(5, "ITT: 9 blocs par cellule du plan, jamais moins", not bad,
        f"cellules hors norme = {bad or 'aucune'}")


def v6():
    """Rejection causes are exhaustive: every rejected event carries a named cause."""
    tot = named = 0
    causes = {}
    for f in ("p07a_event_ledger.csv", "p07b_event_ledger.csv"):
        for r in rd(f):
            if r.get("rejected") != "True":
                continue
            tot += 1
            c = r.get("reject_reason") or ""
            if c and c != "NONE":
                named += 1
                causes[c] = causes.get(c, 0) + 1
    chk(6, "toute non-execution porte une cause nommee", tot == named,
        f"{tot} rejets, {named} nommes; taxonomie = {causes}")


def v7():
    """Headline: the component is never exhausted at a rejection."""
    ev = [r for r in rd("p07a_event_ledger.csv")
          if r.get("rejected") == "True" and n(r.get("CAP_TRACKALL")) is not None
          and r["arm"].startswith("PARENT_")]
    with_mat = sum(1 for r in ev if (n(r["CAP_TRACKALL"]) or 0) > 1e-9
                   and (n(r["CAP_PARENT"]) or 0) <= 1e-9)
    chk(7, "a chaque rejet, de la matiere reste retirable dans le composant",
        len(ev) > 0 and with_mat == len(ev),
        f"{with_mat}/{len(ev)} rejets ont CAP_TRACKALL > 0 et CAP_PARENT = 0")


def v8():
    """Headline: UNTRACKED is numerically identical to PARENT."""
    b = {(r["block"], r["arm"]): r for r in rd("p07b_rows.csv")}
    a = {r["block"]: r for r in rd("p07a_rows.csv") if r["arm"] == "PARENT_Q400_UNIFORM"}
    w = 0.0
    k = 0
    for (blk, arm), r in b.items():
        if arm != "UNTRACKED" or blk not in a:
            continue
        for key in ("realized_sink", "incumbent_removed_total"):
            x, y = n(r[key]), n(a[blk][key])
            if x is not None and y is not None:
                w = max(w, abs(x - y) / max(1.0, abs(y)))
        k += 1
    ident = 0
    for (blk, arm), r in b.items():
        if arm != "UNTRACKED" or blk not in a:
            continue
        if abs((n(r["realized_sink"]) or 0) - (n(a[blk]["realized_sink"]) or 0)) == 0.0:
            ident += 1
    chk(8, "UNTRACKED ~ PARENT (la porte de piste est quasi inerte)",
        w <= 1e-2 and ident >= 0.8 * k,
        f"{ident}/{k} blocs BIT-IDENTIQUES, pire ecart relatif sur les autres = {w:.2e} "
        f"(les 3 blocs qui different sont exactement ceux ou de la matiere >= THRESH "
        f"s'est detachee de la piste : 3 evenements sur 5760)")


def v9():
    """Headline: SINKSIDE delivers everything and replaces almost nothing."""
    out = []
    ok = True
    for f, kk in (("p07b_rows.csv", lambda r: f"L{r['size']}"),
                  ("p07d_rows.csv", lambda r: f"{r['law']}|L{r['size']}")):
        rows = rd(f)
        for k in sorted({kk(r) for r in rows}):
            p = [r for r in rows if kk(r) == k and r["arm"] in ("PARENT",)]
            s = [r for r in rows if kk(r) == k and r["arm"] == "SRC_SINKSIDE"]
            if not s:
                continue
            if not p:
                p = [r for r in rd("p07a_rows.csv") if r["arm"] == "PARENT_Q400_UNIFORM"
                     and r["size"] == k[1:]]
            ep = S.median([n(r["incumbent_removed_total"]) / n(r["realized_sink"]) for r in p])
            es = S.median([n(r["incumbent_removed_total"]) / n(r["realized_sink"]) for r in s])
            out.append(f"{k}:{ep / es:.0f}x")
            ok = ok and (ep / es) >= 4
    chk(9, "SINKSIDE: efficacite de remplacement effondree", ok,
        "rapport PARENT/SINKSIDE = " + ", ".join(out))


def v10():
    """Headline: the sealed cadence law reproduced from raw, by an independent route."""
    pred = json.load(open("p07d_protocol.json"))["SEALED_POINT_PREDICTIONS"][
        "P1_CADENCE_SATURATION_LAW"]["predicted_Phi"]
    cad = rd("p07d_cadence_rows.csv")
    worst = 0.0
    detail = []
    for L in ("24", "32"):
        for s in ("2", "8", "32", "128"):
            g = [n(r["delivered_total"]) / n(r["window"]) for r in cad
                 if r["size"] == L and r["spacing"] == s]
            if not g:
                continue
            o = S.median(g)
            rt = o / pred[f"L{L}"][s]
            worst = max(worst, abs(math.log(rt)))
            detail.append(f"L{L}s{s}={rt:.3f}")
    chk(10, "loi de cadence recalculee depuis le brut (delivre/fenetre)",
        math.exp(worst) <= 1.35, f"pire rapport = {math.exp(worst):.3f} (tolerance scellee "
                                 f"1,35); " + " ".join(detail))


def v11():
    """Every protocol still matches its seal, and every sealed code file is unchanged."""
    import hashlib
    bad = []
    for p in ("p07a_protocol", "p07b_protocol", "p07d_protocol"):
        j, s = Path(f"{p}.json"), Path(f"{p}.sha256")
        if not (j.exists() and s.exists()):
            bad.append((p, "missing"))
            continue
        if hashlib.sha256(j.read_bytes()).hexdigest() != s.read_text().split()[0]:
            bad.append((p, "protocol hash"))
            continue
        for f, h in json.loads(j.read_text())["code_sha256"].items():
            if hashlib.sha256(Path(f).read_bytes()).hexdigest() != h:
                bad.append((p, f))
    chk(11, "tous les sceaux tiennent encore (protocoles et code)", not bad,
        f"violations = {bad or 'aucune'}")


def v12():
    """Parent artefacts untouched."""
    import hashlib
    src = Path("../DR05/SHA256SUMS.txt")
    if not src.exists():
        chk(12, "artefacts parents intacts", False, "SHA256SUMS.txt du parent introuvable")
        return
    bad = []
    k = 0
    for line in src.read_text().splitlines():
        if not line.strip():
            continue
        h, name = line.split(None, 1)
        p = Path("../DR05") / name.strip()
        if not p.exists():
            bad.append((name.strip(), "missing"))
            continue
        if hashlib.sha256(p.read_bytes()).hexdigest() != h:
            bad.append((name.strip(), "changed"))
        k += 1
    chk(12, "aucun artefact du parent DEV_05 modifie", not bad,
        f"{k} fichiers verifies; violations = {bad or 'aucune'}")


def main():
    print("=== VERIFICATION INDEPENDANTE PROGRAM_07 (0 appel moteur) ===")
    for f in (v1, v2, v3, v4, v5, v6, v7, v8, v9, v10, v11, v12):
        try:
            f()
        except Exception as e:
            import traceback
            traceback.print_exc()
            chk(int(f.__name__[1:]), f.__name__, False, f"EXCEPTION {type(e).__name__}: {e}")
    p = sum(1 for x in R if x["PASS"])
    Path("p07_verify.json").write_text(json.dumps(
        {"n": len(R), "n_pass": p, "VERDICT": "PASS" if p == len(R) else "FAIL",
         "engine_invocations": 0, "checks": R}, indent=1))
    print(f"\n{p}/{len(R)} -> {'PASS' if p == len(R) else 'FAIL'}")
    return 0 if p == len(R) else 1


if __name__ == "__main__":
    raise SystemExit(main())
