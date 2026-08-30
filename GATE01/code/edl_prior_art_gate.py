"""GATE01 — la porte d'anteriorite. Ecrite apres le retrait de RPP98.

RPP98 a ete retiree parce que sa question avait deja ete posee et repondue, quatre jours plus
tot, dans ce depot, sur plus de mondes, a la meme loi. Le constat n'exigeait aucun raffinement
statistique : il fallait chercher avant de geler.

Ce fichier rend la recherche MECANIQUE et son resultat OPPOSABLE. Il ne juge rien tout seul :
il produit la liste des fichiers publies qui parlent deja des memes objets, et il REFUSE de
laisser passer un pre-enregistrement tant que chaque fichier signale n'a pas recu un verdict
ecrit de l'operateur.

Usage :
    python3 GATE01/code/edl_prior_art_gate.py scan  <MISSION> <terme> [<terme> ...]
        -> ecrit GATE01/out/<MISSION>_PRIOR_ART.json avec les fichiers signales, verdicts vides

    python3 GATE01/code/edl_prior_art_gate.py check <MISSION>
        -> sortie 0 si tout fichier signale porte un verdict parmi
           ANSWERS_THE_QUESTION | ADJACENT_BUT_DIFFERENT | IRRELEVANT, avec une raison ;
           sortie 1 sinon. Un seul ANSWERS_THE_QUESTION suffit a interdire le gel.

La porte ne remplace pas le jugement. Elle empeche de ne pas avoir regarde.

REGLE SUR LES TERMES, apprise en la construisant. Les termes doivent etre les NOMS DES
GRANDEURS, pas les mots du concept. Sur la question meme de RPP98 :

    termes vagues   n_components components transition centres separation trajectory
                    -> 203 fichiers signales. Un operateur devant 203 lignes ne lit rien.
    noms de grandeurs  n_components single_centre two_centre terminators
                       MERGED_TO_ONE_CENTRE descent run_length
                    -> 26 fichiers, et TLMR01/out/TLMR01_ANALYSIS.json en tete.

Une porte franchie avec des termes vagues est une porte contournee. Les termes sont ecrits dans
le fichier de sortie : ils font partie de ce qui est opposable.
"""
from __future__ import annotations
import os, sys, json, re, subprocess

REPO = os.environ.get("TBRT02_REPO", "/home/claude/edl")
OUT = os.path.join(REPO, "GATE01/out")
VERDICTS = ("ANSWERS_THE_QUESTION", "ADJACENT_BUT_DIFFERENT", "IRRELEVANT")
# Une porte qui passe sur un ensemble vide n'est pas une porte : deux termes obscurs qui ne
# co-occurrent nulle part donnaient zero fichier signale et sortie 0. Constat F6, adopte.
MIN_FLAGGED = 10
# Trois chaines REASON pour dix-huit fichiers, c'est du remplissage. Constat F6, adopte.
MIN_DISTINCT_REASONS = 5
# les repertoires de sortie publies : c'est la qu'un resultat anterieur se trouve
# review/ est inclus depuis le constat F6 : les retours de checker adverses y vivent, et c'est
# l'anteriorite la plus lourde du programme. .txt aussi, pour la meme raison.
PUBLISHED = re.compile(r"/(out|work|review)/[^/]+\.(json|md|jsonl|txt)$")
CODE = re.compile(r"/code/[^/]+\.py$")


def _walk(mission):
    skip = {".git", "__pycache__", "node_modules"}
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in skip]
        for f in files:
            p = os.path.join(root, f)
            rel = os.path.relpath(p, REPO)
            if rel.startswith(mission + "/") or rel.startswith("GATE01/code/"):
                continue          # ni soi-meme, ni le code de la porte. GATE01/out EST scanne :
                                  # la carte d'anteriorite du programme y vit, et une porte qui ne
                                  # peut pas voir l'inventaire de ce qui est etabli n'est pas une
                                  # porte. Constat F6 du checker de FIMRCC02, adopte.
            yield p, rel


def scan(mission, terms):
    hits = {}
    lowterms = [t.lower() for t in terms]
    for p, rel in _walk(mission):
        is_pub = bool(PUBLISHED.search("/" + rel))
        is_code = bool(CODE.search("/" + rel))
        if not (is_pub or is_code):
            continue
        try:
            if os.path.getsize(p) > 40_000_000:
                continue
            txt = open(p, "r", errors="ignore").read()
        except OSError:
            continue
        low = txt.lower()
        found = [t for t, lt in zip(terms, lowterms) if lt in low]
        if len(found) < 2:                     # un seul terme commun n'est pas de l'anteriorite
            continue
        gen = None
        m = re.search(r'"GENERATED_UTC"\s*:\s*"([^"]+)"', txt)
        if m:
            gen = m.group(1)
        lines = []
        for t in found[:6]:
            for ln in txt.splitlines():
                if t.lower() in ln.lower():
                    lines.append(ln.strip()[:300])
                    break
        hits[rel] = {"terms_found": found, "n_terms": len(found), "kind": "published" if is_pub else "code",
                     "GENERATED_UTC": gen, "sample_lines": lines,
                     "VERDICT": None, "REASON": None}
    ranked = dict(sorted(hits.items(), key=lambda kv: (-kv[1]["n_terms"], kv[0])))
    doc = {"MISSION": mission, "TERMS": terms,
           "GENERATED_UTC": subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%S+00:00"],
                                           capture_output=True, text=True).stdout.strip(),
           "N_FLAGGED": len(ranked),
           "RULE": ("un fichier est signale s'il mentionne au moins DEUX des termes. Chaque "
                    "fichier signale doit recevoir un VERDICT et une REASON avant le gel. Un "
                    "seul ANSWERS_THE_QUESTION interdit de geler la question telle quelle."),
           "VERDICTS_ADMIS": list(VERDICTS),
           "FLAGGED": ranked}
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"{mission}_PRIOR_ART.json")
    json.dump(doc, open(path, "w"), indent=1, ensure_ascii=False)
    return doc, path


def check(mission):
    path = os.path.join(OUT, f"{mission}_PRIOR_ART.json")
    if not os.path.exists(path):
        print(f"REFUS : {path} n'existe pas. La porte n'a pas ete franchie.")
        return 1
    doc = json.load(open(path))
    if doc.get("N_FLAGGED", 0) < MIN_FLAGGED:
        print(f"REFUS : seulement {doc.get('N_FLAGGED',0)} fichier(s) signale(s). Une porte qui ne "
              f"trouve presque rien n'a pas cherche : les termes sont trop rares ou trop prives. "
              f"Il en faut au moins {MIN_FLAGGED}. Relancez le scan avec les NOMS DES GRANDEURS "
              f"que la question manipule, pas ceux de la mission parente.")
        return 1
    reasons = {v.get("REASON") for v in doc["FLAGGED"].values() if v.get("REASON")}
    if doc["FLAGGED"] and len(reasons) < MIN_DISTINCT_REASONS:
        print(f"REFUS : {len(reasons)} justification(s) distincte(s) pour "
              f"{len(doc['FLAGGED'])} fichiers. Des verdicts recopies ne sont pas des verdicts. "
              f"Il en faut au moins {MIN_DISTINCT_REASONS}.")
        return 1
    unjudged = [k for k, v in doc["FLAGGED"].items()
                if v.get("VERDICT") not in VERDICTS or not v.get("REASON")]
    answers = [k for k, v in doc["FLAGGED"].items() if v.get("VERDICT") == "ANSWERS_THE_QUESTION"]
    if unjudged:
        print(f"REFUS : {len(unjudged)} fichier(s) signale(s) sans verdict :")
        for k in unjudged[:20]:
            print("   ", k)
        return 1
    if answers:
        print(f"REFUS : la question est deja repondue par {len(answers)} fichier(s) :")
        for k in answers:
            print("   ", k, "->", doc["FLAGGED"][k]["REASON"])
        return 1
    print(f"PASSE : {doc['N_FLAGGED']} fichier(s) signale(s), tous juges, aucun ne repond a la question.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "scan":
        d, p = scan(sys.argv[2], sys.argv[3:])
        print(f"{d['N_FLAGGED']} fichier(s) signale(s) -> {p}")
        for k, v in list(d["FLAGGED"].items())[:15]:
            print(f"  [{v['n_terms']}] {k}   {v['GENERATED_UTC'] or ''}")
    elif len(sys.argv) == 3 and sys.argv[1] == "check":
        sys.exit(check(sys.argv[2]))
    else:
        print(__doc__)
        sys.exit(2)
