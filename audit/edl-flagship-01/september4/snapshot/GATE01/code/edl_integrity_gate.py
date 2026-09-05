"""GATE01 — la porte d'integrite, generique.

OMLDCT03/code/omldct03_integrity.py a ete ecrit en reponse au constat F5 de son checker, qui
etait deja le F15 de RPP98 : lire un registre scelle pour ADMISSIBLE et ne jamais lire d[sha256].
Ce fichier-la reste tel quel — son manifeste porte un hachage de contenu publie, et on ne touche
pas aux entrees d'un artefact publie. Celui-ci est sa generalisation, et la difference tient en
une ligne : le chemin du registre et le repertoire d'archives sont des PARAMETRES.

Le docstring de l'original disait « ecrit pour etre reutilisable ». Il ne l'etait pas : deux
chemins y sont codes en dur. Une mission suivante aurait du l'editer pour s'en servir, donc ne
s'en serait pas servie. C'est la forme la plus commune d'un outil « reutilisable ».

    python3 GATE01/code/edl_integrity_gate.py <MISSION> \
        --ledger 'TBRT02/work/TBRT02_SEALED_LEDGER_*.jsonl' \
        --archives /home/claude/TBRT02_raw

DEUX PROPRIETES QUE CETTE PORTE DOIT AVOIR, et qui sont verifiees plus bas :

  1. elle ECHOUE quand elle ne peut pas verifier. Un repertoire d'archives vide ne donne pas un
     passage par defaut : il donne un refus. Une porte qui passe faute de donnees n'est pas une
     porte — c'est le defaut que la version reparee de la porte d'anteriorite avait deja corrige.
  2. elle ne CORRIGE rien. Elle constate, elle compte, et elle nomme ce qui manque.
"""
from __future__ import annotations
import os, sys, json, glob, argparse, subprocess

REPO = os.environ.get("TBRT02_REPO", "/home/claude/edl")
sys.path.insert(0, os.path.join(REPO, "OMLDCT02/code"))
import numpy as np
import omldct02_hashes as H

# les champs de fidelite exiges, tels que le registre de TBRT02 les ecrit
FORK_FIELDS = ("PHYSICAL_STATE_IDENTICAL", "RNG_STATE_IDENTICAL")
# ALL_THREE_ARMS_DIVERGED vit a la racine de la ligne, pas dans FORK — la porte gelee
# le verifiait et ma premiere generalisation l'avait PERDU en silence. Le controle croise
# contre le manifeste gele l'a rattrape ; c'est exactement a cela qu'il sert.
ROW_FIELDS = ("ALL_THREE_ARMS_DIVERGED",)
IV_FIELDS = (("SELECTIVE", "parent_emptied"), ("SELECTIVE", "daughter_untouched"),
             ("SELECTIVE", "occupancy_conserved"), ("SELECTIVE", "rng_unchanged"),
             ("SHAM", "removed_nothing"), ("SHAM", "phys_unchanged"))


def read_ledger(pattern):
    paths = sorted(glob.glob(os.path.join(REPO, pattern)))
    if not paths:
        raise SystemExit(f"REFUS : aucun registre ne correspond a {pattern}")
    return [json.loads(l) for p in paths for l in open(p) if l.strip()], paths


def run(mission, ledger_pattern, archive_dir):
    rows, ledger_paths = read_ledger(ledger_pattern)
    adm = sorted([r for r in rows if r.get("ADMISSIBLE")], key=lambda x: x["index"])
    n = len(adm)

    idx = [r["index"] for r in adm]; seeds = [r["seed"] for r in adm]
    uniq = {"n_rows_total": len(rows), "n_admissible": n,
            "indices_unique": len(set(idx)) == len(idx),
            "seeds_unique": len(set(seeds)) == len(seeds),
            "n_distinct_indices": len(set(idx)), "n_distinct_seeds": len(set(seeds))}

    sha_ok = sha_bad = sha_missing = 0
    mismatches, missing_names = [], []
    n_arms = meta_ok = horizon_ok = contig_ok = 0
    horizons = set()
    for r in adm:
        for arm, d in sorted(r["ARCHIVES"].items()):
            name = os.path.basename(d["path"])
            p = os.path.join(archive_dir, name)
            if not os.path.exists(p):
                sha_missing += 1; missing_names.append(name); continue
            if H.file_sha256(p) == d["sha256"]:
                sha_ok += 1
            else:
                sha_bad += 1; mismatches.append(name); continue
            z = np.load(p, allow_pickle=True)
            meta = json.loads(str(z["meta"][0])); s = z["s"].astype(np.int64); z.close()
            n_arms += 1
            meta_ok += int(bool(meta.get("integrity_ok")))
            horizons.add(int(meta.get("steps_executed", -1)))
            horizon_ok += int(int(meta.get("steps_executed", -1)) == len(s))
            t = s[:, 0].tolist()
            contig_ok += int(all(t[i] == t[i-1] + 1 for i in range(1, len(t))))

    fk = {k: 0 for k in FORK_FIELDS}
    fk.update({k: 0 for k in ROW_FIELDS})
    iv = {f"{a}_{k}": 0 for a, k in IV_FIELDS}
    for r in adm:
        Fk = r.get("FORK") or {}
        for k in FORK_FIELDS:
            fk[k] += int(bool(Fk.get(k)))
        for k in ROW_FIELDS:
            fk[k] += int(bool(r.get(k)))
        A = r.get("INTERVENTION_AUDIT") or {}
        for a, k in IV_FIELDS:
            iv[f"{a}_{k}"] += int(bool((A.get(a) or {}).get(k)))

    n_expected_arms = sum(len(r["ARCHIVES"]) for r in adm)
    doc = {
     "MODULE": "GATE01/code/edl_integrity_gate.py",
     "SECTION": "porte d'integrite generique — etape SEPAREE, a passer AVANT toute mesure",
     "MISSION_QUI_LA_PASSE": mission,
     "GENERATED_UTC": subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%S+00:00"],
                                     capture_output=True, text=True).stdout.strip(),
     "LEDGER_PATTERN": ledger_pattern,
     "LEDGER_FILES": [os.path.relpath(p, REPO) for p in ledger_paths],
     "ARCHIVE_DIR": archive_dir,
     "N_ADMISSIBLE_TRIPLES": n, "N_ARCHIVES_EXPECTED": n_expected_arms,
     "UNICITE": uniq,
     "OCTETS": {"sha256_match": sha_ok, "sha256_mismatch": sha_bad, "missing": sha_missing,
                "MISMATCHES": mismatches, "MISSING_NAMES": missing_names[:20],
                "n_missing_names_listed": min(20, len(missing_names))},
     "CONTENU": {"n_arms_read": n_arms, "meta_integrity_ok": meta_ok,
                 "steps_executed_equals_row_count": horizon_ok,
                 "step_index_contiguous": contig_ok, "distinct_horizons": sorted(horizons)},
     "FIDELITE_DU_FORK": fk, "FIDELITE_DE_L_INTERVENTION": iv,
    }
    doc["ALL_ARCHIVE_HASHES_MATCH"] = bool(sha_bad == 0 and sha_missing == 0
                                           and sha_ok == n_expected_arms and n_expected_arms > 0)
    doc["NO_DUPLICATE_SCIENTIFIC_SEED"] = bool(uniq["indices_unique"] and uniq["seeds_unique"])
    doc["ALL_CONTENT_CHECKS_PASS"] = bool(n_arms > 0 and meta_ok == n_arms
                                          and horizon_ok == n_arms and contig_ok == n_arms
                                          and len(horizons) == 1)
    doc["ALL_FIDELITY_CHECKS_PASS"] = bool(n > 0 and all(v == n for v in fk.values())
                                           and all(v == n for v in iv.values()))
    doc["INTEGRITY_GATE_PASSES"] = bool(doc["ALL_ARCHIVE_HASHES_MATCH"]
                                        and doc["NO_DUPLICATE_SCIENTIFIC_SEED"]
                                        and doc["ALL_CONTENT_CHECKS_PASS"]
                                        and doc["ALL_FIDELITY_CHECKS_PASS"])
    doc["POURQUOI_ELLE_REFUSE_SI_ELLE_NE_PEUT_PAS_VERIFIER"] = (
        "un repertoire d'archives vide donne sha256_match = 0 et missing > 0, donc "
        "ALL_ARCHIVE_HASHES_MATCH faux, donc refus. Une porte qui passerait faute de donnees "
        "certifierait le vide.")
    doc["ELLE_NE_CORRIGE_RIEN"] = True
    doc["GATE_CONTENT_HASH"] = H.content_digest(doc, extra_excluded=("GATE_CONTENT_HASH",))
    return doc


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mission")
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--archives", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    d = run(a.mission, a.ledger, a.archives)
    out = a.out or f"{REPO}/GATE01/out/{a.mission}_INTEGRITY.json"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(d, open(out, "w"), indent=1, ensure_ascii=False)
    print(f"triplets admissibles : {d['N_ADMISSIBLE_TRIPLES']}  archives attendues : {d['N_ARCHIVES_EXPECTED']}")
    print(f"octets   : {d['OCTETS']['sha256_match']} concordent, {d['OCTETS']['sha256_mismatch']} ecarts, {d['OCTETS']['missing']} manquantes")
    print(f"unicite  : {d['NO_DUPLICATE_SCIENTIFIC_SEED']}   contenu : {d['ALL_CONTENT_CHECKS_PASS']}   fidelite : {d['ALL_FIDELITY_CHECKS_PASS']}")
    print("PORTE    :", "PASSE" if d["INTEGRITY_GATE_PASSES"] else "REFUS")
    print("->", os.path.relpath(out, REPO))
    sys.exit(0 if d["INTEGRITY_GATE_PASSES"] else 1)
