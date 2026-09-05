"""EDL — verification de la recuperation. Bibliotheque standard seule.

Rejoue, sans rien reecrire, les trois controles qui font la difference entre
« des fichiers » et « l'etat scientifique » :

  1. l'integrite octet a octet de l'arbre recupere,
  2. METHODS_HASH par la FORMULE GELEE (le code du depot est appele, jamais
     reimplemente),
  3. les empreintes de contenu publiees et les retours de checker verbatim.

    python3 edl_verify_recovery.py [racine_du_depot]

Sortie : JSON sur stdout, code 0 si tout concorde, 2 sinon.

CE QU'IL NE FAIT PAS. Il ne reconstruit aucun fichier de methode, ne touche a
aucune valeur gelee, ne lance aucun monde et n'ecrit rien dans l'arbre.
"""
from __future__ import annotations
import hashlib, json, os, subprocess, sys

ARMING_METHODS_HASH = "21571fb4cb1df9ac2e9089924e9d6ee5d4d63c920a007e188bdc24e0d94d1f99"
ARMING_CLOSE01_VERBATIM = "1543a8c9fd28de771b27430669b2b8400c25e58ec47ad5c38ce5c4d87b42135e"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def check_tree(root, rep):
    ref = os.path.join(root, "RECOVERY", "RECOVERY_HASHES.json")
    if not os.path.isfile(ref):
        rep["tree"] = "RECOVERY_HASHES.json absent — controle impossible"
        return False
    pre = json.load(open(ref))["sha256_before"]
    missing = [n for n in pre if not os.path.isfile(os.path.join(root, n))]
    diff = [n for n in pre if n not in missing and sha(os.path.join(root, n)) != pre[n]]
    rep["tree"] = {"n_files_referenced": len(pre), "missing": missing or "none",
                   "sha_mismatch": diff or "none",
                   "TREE_BYTE_IDENTICAL": not missing and not diff}
    return not missing and not diff


def check_methods_hash(root, rep):
    """Appelle la formule gelee. tlmr01_world.py code en dur REPO=/home/claude/edl,
    donc l'arbre doit etre atteignable sous ce chemin ; un lien symbolique suffit
    et ne modifie aucun octet."""
    code = ("import sys, json; sys.path.insert(0,'TBRT02/code');"
            "import tbrt02_freeze as F;"
            "f={p: F.H.file_sha256(F.REPO+'/'+p) for p in F.METHODS};"
            "print(json.dumps({'h':F.H.canonical_digest(f),'n':len(f),'files':f}))")
    env = dict(os.environ, TBRT02_REPO=root, PYTHONDONTWRITEBYTECODE="1")
    try:
        out = subprocess.run([sys.executable, "-c", code], cwd=root, env=env,
                             capture_output=True, text=True, timeout=120)
        got = json.loads(out.stdout.strip().splitlines()[-1])
    except Exception as e:                                    # noqa: BLE001
        rep["methods_hash"] = {"ERROR": repr(e),
                               "hint": "l'arbre doit etre atteignable sous /home/claude/edl"}
        return False
    frz = json.load(open(os.path.join(root, "TBRT02/out/TBRT02_MASTER_FREEZE.json")))
    bad = [p for p in got["files"] if got["files"][p] != frz["METHODS_FILES"].get(p)]
    ok = (got["h"] == ARMING_METHODS_HASH == frz["METHODS_HASH"]) and not bad
    rep["methods_hash"] = {"recomputed": got["h"], "n_files": got["n"],
                           "matches_arming_note": got["h"] == ARMING_METHODS_HASH,
                           "matches_master_freeze": got["h"] == frz["METHODS_HASH"],
                           "per_file_mismatch": bad or "none", "OK": ok}
    return ok


def check_published(root, rep):
    p = os.path.join(root, "TBRT02/out/SHA256SUMS")
    rows = [l.split() for l in open(p).read().splitlines() if l.strip()]
    bad = [n for h, n in rows if sha(os.path.join(root, "TBRT02/out", n)) != h]
    rep["published_content_hashes"] = {"entries": len(rows), "mismatch": bad or "none",
                                       "OK": not bad}
    return not bad


def check_verbatims(root, rep):
    found, confronted, mismatch = {}, {}, []
    for d, _s, fs in os.walk(root):
        for f in fs:
            if f.endswith("CHECKER_RETURN_VERBATIM.md"):
                rel = os.path.relpath(os.path.join(d, f), root)
                found[rel] = sha(os.path.join(d, f))
    for d, _s, fs in os.walk(root):
        for f in fs:
            if f.endswith("CHECKER_ADJUDICATION.json"):
                try:
                    a = json.load(open(os.path.join(d, f)))
                except Exception:                              # noqa: BLE001
                    continue
                dec, ref = a.get("CHECKER_RETURN_SHA256"), a.get("CHECKER_RETURN_VERBATIM")
                if dec and ref:
                    confronted[ref] = dec
                    if found.get(ref) != dec:
                        mismatch.append(ref)
    close = next((h for n, h in found.items() if "CLOSE01" in n), None)
    ok = not mismatch and close == ARMING_CLOSE01_VERBATIM
    rep["checker_verbatims"] = {
        "present": len(found), "declared_hash_confronted": len(confronted),
        "hash_computed_only": sorted(set(found) - set(confronted)),
        "mismatch": mismatch or "none",
        "CLOSE01_matches_arming_note": close == ARMING_CLOSE01_VERBATIM, "OK": ok}
    return ok


def main():
    root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
    rep = {"root": root}
    ok = all([check_tree(root, rep), check_methods_hash(root, rep),
              check_published(root, rep), check_verbatims(root, rep)])
    rep["ALL_CHECKS_PASS"] = ok
    print(json.dumps(rep, indent=1))
    sys.exit(0 if ok else 2)


if __name__ == "__main__":
    main()
