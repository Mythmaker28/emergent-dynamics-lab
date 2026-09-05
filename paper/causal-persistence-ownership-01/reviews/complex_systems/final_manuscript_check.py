"""Static resolved-text/source consistency checks; no engine imports or worlds."""
from pathlib import Path
import csv
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
PAPER = HERE.parents[1]


def main():
    files = {name: (PAPER / name).read_bytes() for name in (
        "MANUSCRIPT_RESOLVED.md", "SUPPLEMENT_RESOLVED.md", "CLAIM_EVIDENCE_MATRIX.csv")}
    texts = {name: data.decode("utf-8") for name, data in files.items()}
    main_text = texts["MANUSCRIPT_RESOLVED.md"]
    supp = texts["SUPPLEMENT_RESOLVED.md"]
    check = json.loads((HERE / "SOURCE_CHECK.json").read_text(encoding="utf-8"))
    rows = re.findall(r"^\| (scaffold|memory) \| (\w+) \| ([0-9.eE+\-]+) \|$", supp, re.M)
    parsed = {(group, key): float(value) for group, key, value in rows}
    expected = {(group, key): float(value)
                for group in ("scaffold", "memory")
                for key, value in check[group + "_parameters"].items()}
    assert parsed == expected, "Resolved parameter table differs from extracted source values"
    ref_keys = ("lisman1985", "gardner2000", "krakauer2020", "kolchinsky2018",
                "zwicker2017", "plantec2025", "hintze2026", "bengio2004")
    verified = {r["key"]: r for r in json.loads(
        (HERE / "VERIFIED_REFERENCES.json").read_text(encoding="utf-8"))["references"]}
    references = {}
    for name in ("MANUSCRIPT_RESOLVED.md", "SUPPLEMENT_RESOLVED.md"):
        text = texts[name]
        assert not re.search(r"\{\{\w+\}\}", text), "Unresolved substitution"
        references[name] = dict(re.findall(r"^\[(\d+)\] (.+)$", text, re.M))
        assert set(references[name]) == {str(n) for n in range(1, 9)}
        for number, key in enumerate(ref_keys, 1):
            record = verified[key]
            entry = references[name][str(number)]
            assert record["title"] in entry
            identifier = record["doi"] or record["url"]
            assert identifier in entry
        # Citation numbers in prose must resolve; numerical interval endpoints are not citations.
        prose = text.split("## References")[0]
        assert set(re.findall(r"\[(\d+)\]", prose)) <= set(references[name])
    assert references["MANUSCRIPT_RESOLVED.md"] == references["SUPPLEMENT_RESOLVED.md"]
    assert "contributed at most one quarter of its current mass" in main_text
    assert "set to zero outside the alive mask" in supp
    assert "Before the internal reaction and its Laplacian are evaluated" in supp
    assert "Post-history masks are the nearest detected components" in supp
    assert "Bijective tracking starts at marking" in supp
    matrix = list(csv.DictReader(texts["CLAIM_EVIDENCE_MATRIX.csv"].splitlines()))
    assert len(matrix) == 25 and len({r["claim_id"] for r in matrix}) == 25
    assert all(r["qualification"] and r["status"] and r["evidence"] for r in matrix)
    missing = [{"claim_id": row["claim_id"], "path": path}
               for row in matrix for path in row["evidence"].split(";")
               if not (PAPER / path).is_file()]
    assert not missing, "Claim matrix references missing evidence files"
    result = {
        "status": "PASS_STATIC_SOURCE_CONSTRUCT_BIBLIOGRAPHY_CHECK",
        "file_sha256": {name: hashlib.sha256(data).hexdigest() for name, data in files.items()},
        "source_revision": "06fd9524f5c7ffb329ee850a10bd9959f2f0bde5",
        "parameters_matched": len(parsed), "references_matched": len(ref_keys),
        "claim_matrix_rows": len(matrix), "missing_claim_evidence_paths": missing,
        "FR01_FR02_FR03": "CLOSED_IN_RESOLVED_TEXT",
        "scope": "Read-only source/construct/bibliographic text checks; PDF font/layout and statistical calibration reviewed separately. No new world or engine import.",
    }
    (HERE / "FINAL_SOURCE_CONSTRUCT_CHECK.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
