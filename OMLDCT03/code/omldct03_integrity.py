"""OMLDCT03 — la porte d'integrite, ETAPE SEPAREE, qui tourne AVANT toute mesure.

Ecrite en reponse au constat F5 du checker, accepte : mon code lisait le registre scelle pour
ADMISSIBLE et ne lisait jamais d[sha256]. C'etait deja le constat F15 de RPP98, accepte alors,
et je l'ai repete deux missions plus tard sur les memes archives.

OMLDCT02 en fait une etape a part — omldct02_c3_raw.raw_manifest() — qui produit un manifeste
AVANT que measure() tourne. Ce fichier est l'equivalent, et il est ecrit pour etre reutilisable
par n'importe quelle mission future qui lit les archives de TBRT02 : il ne connait rien
d'OMLDCT03 en propre.

Il ne corrige rien et ne repare rien. Il constate, et il ECHOUE BRUYAMMENT si un seul controle
tombe. Une mission qui lit des archives sans avoir passe cette porte n'a pas de provenance.
"""
from __future__ import annotations
import os, sys, json, glob, subprocess

REPO = os.environ.get("TBRT02_REPO", "/home/claude/edl")
sys.path.insert(0, os.path.join(REPO, "OMLDCT02/code"))
import numpy as np
import omldct02_hashes as H

RAW = "/home/claude/TBRT02_raw"


def ledger():
    return [json.loads(l)
            for p in sorted(glob.glob(f"{REPO}/TBRT02/work/TBRT02_SEALED_LEDGER_*.jsonl"))
            for l in open(p) if l.strip()]


def run():
    rows = ledger()
    adm = sorted([r for r in rows if r.get("ADMISSIBLE")], key=lambda x: x["index"])

    # 1. unicite : le gel exige qu'une graine ne donne au plus qu'une paire
    idx = [r["index"] for r in adm]
    seeds = [r["seed"] for r in adm]
    uniq = {"n_rows_total": len(rows), "n_admissible": len(adm),
            "indices_unique": len(set(idx)) == len(idx),
            "seeds_unique": len(set(seeds)) == len(seeds),
            "n_distinct_indices": len(set(idx)), "n_distinct_seeds": len(set(seeds))}

    # 2. les octets : sha256 de chaque archive contre le sceau
    sha_ok = sha_bad = sha_missing = 0
    bad = []
    per = []
    for r in adm:
        row = {"index": r["index"], "seed": r["seed"], "t_m": r["t_m"], "ARMS": {}}
        for a, d in sorted(r["ARCHIVES"].items()):
            p = os.path.join(RAW, os.path.basename(d["path"]))
            if not os.path.exists(p):
                sha_missing += 1; row["ARMS"][a] = {"present": False}; continue
            got = H.file_sha256(p)
            match = (got == d["sha256"])
            sha_ok += int(match); sha_bad += int(not match)
            if not match:
                bad.append({"index": r["index"], "arm": a, "sealed": d["sha256"], "found": got})
            row["ARMS"][a] = {"present": True, "sha256_matches_the_seal": match,
                              "bytes": os.path.getsize(p)}
        per.append(row)

    # 3. le contenu : integrite declaree, horizon, contiguite des pas
    meta_ok = horizon_ok = contig_ok = 0; n_arms = 0
    horizons = set()
    for r in adm:
        for a, d in sorted(r["ARCHIVES"].items()):
            p = os.path.join(RAW, os.path.basename(d["path"]))
            if not os.path.exists(p):
                continue
            n_arms += 1
            z = np.load(p, allow_pickle=True)
            meta = json.loads(str(z["meta"][0])); s = z["s"].astype(np.int64); z.close()
            meta_ok += int(bool(meta.get("integrity_ok")))
            horizons.add(int(meta.get("steps_executed", -1)))
            horizon_ok += int(int(meta.get("steps_executed", -1)) == len(s))
            t = s[:, 0].tolist()
            contig_ok += int(all(t[i] == t[i - 1] + 1 for i in range(1, len(t))))

    # 4. la fidelite du fork et de l'intervention, telle que le registre la porte
    fk = {"PHYSICAL_STATE_IDENTICAL": 0, "RNG_STATE_IDENTICAL": 0, "ALL_THREE_ARMS_DIVERGED": 0}
    iv = {"SELECTIVE_parent_emptied": 0, "SELECTIVE_daughter_untouched": 0,
          "SELECTIVE_occupancy_conserved": 0, "SELECTIVE_rng_unchanged": 0,
          "SHAM_removed_nothing": 0, "SHAM_phys_unchanged": 0}
    for r in adm:
        f = r.get("FORK", {})
        for k in fk:
            fk[k] += int(bool(f.get(k) if k in f else r.get(k)))
        A = r.get("INTERVENTION_AUDIT", {})
        for arm, key in (("SELECTIVE", "parent_emptied"), ("SELECTIVE", "daughter_untouched"),
                         ("SELECTIVE", "occupancy_conserved"), ("SELECTIVE", "rng_unchanged"),
                         ("SHAM", "removed_nothing"), ("SHAM", "phys_unchanged")):
            iv[f"{arm}_{key}"] += int(bool((A.get(arm) or {}).get(key)))

    n = len(adm)
    doc = {
     "MODULE": "OMLDCT03/code/omldct03_integrity.py",
     "SECTION": ("porte d'integrite — etape SEPAREE, a passer AVANT toute mesure. Reponse au "
                 "constat F5 du checker d'OMLDCT03, qui etait deja le F15 de RPP98."),
     "GENERATED_UTC": subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%S+00:00"],
                                     capture_output=True, text=True).stdout.strip(),
     "SOURCE_OF_TRUTH": "TBRT02/work/TBRT02_SEALED_LEDGER_*.jsonl",
     "ARCHIVE_DIR": RAW,
     "UNICITE": uniq,
     "OCTETS": {"sha256_match": sha_ok, "sha256_mismatch": sha_bad, "missing": sha_missing,
                "MISMATCHES": bad, "expected": 3 * n},
     "CONTENU": {"n_arms_read": n_arms, "meta_integrity_ok": meta_ok,
                 "steps_executed_equals_row_count": horizon_ok,
                 "step_index_contiguous": contig_ok,
                 "distinct_horizons": sorted(horizons)},
     "FIDELITE_DU_FORK": fk, "FIDELITE_DE_L_INTERVENTION": iv, "N_ADMISSIBLE_TRIPLES": n,
     "PER_TRIPLE": per,
    }
    doc["ALL_ARCHIVE_HASHES_MATCH"] = bool(sha_bad == 0 and sha_missing == 0 and sha_ok == 3 * n)
    doc["NO_DUPLICATE_SCIENTIFIC_SEED"] = bool(uniq["indices_unique"] and uniq["seeds_unique"])
    doc["ALL_CONTENT_CHECKS_PASS"] = bool(meta_ok == n_arms and horizon_ok == n_arms
                                          and contig_ok == n_arms and len(horizons) == 1)
    doc["ALL_FIDELITY_CHECKS_PASS"] = bool(all(v == n for v in fk.values())
                                           and all(v == n for v in iv.values()))
    doc["INTEGRITY_GATE_PASSES"] = bool(doc["ALL_ARCHIVE_HASHES_MATCH"]
                                        and doc["NO_DUPLICATE_SCIENTIFIC_SEED"]
                                        and doc["ALL_CONTENT_CHECKS_PASS"]
                                        and doc["ALL_FIDELITY_CHECKS_PASS"])
    doc["CE_QUE_CETTE_PORTE_NE_FAIT_PAS"] = (
      "elle ne corrige rien, ne repare rien et ne relance rien. Elle constate. Un echec ici est un "
      "fait sur les donnees, pas un probleme a contourner.")
    doc["MANIFEST_CONTENT_HASH"] = H.content_digest(doc, extra_excluded=("MANIFEST_CONTENT_HASH",))
    return doc


if __name__ == "__main__":
    d = run()
    json.dump(d, open(f"{REPO}/OMLDCT03/out/OMLDCT03_RAW_MANIFEST.json", "w"),
              indent=1, ensure_ascii=False)
    for k in ("ALL_ARCHIVE_HASHES_MATCH", "NO_DUPLICATE_SCIENTIFIC_SEED",
              "ALL_CONTENT_CHECKS_PASS", "ALL_FIDELITY_CHECKS_PASS", "INTEGRITY_GATE_PASSES"):
        print(f"{k:32s} {d[k]}")
    print("octets :", d["OCTETS"]["sha256_match"], "concordent /", d["OCTETS"]["expected"],
          "| ecarts", d["OCTETS"]["sha256_mismatch"], "| manquants", d["OCTETS"]["missing"])
    print("contenu:", d["CONTENU"])
    sys.exit(0 if d["INTEGRITY_GATE_PASSES"] else 1)
