"""Verify manuscript DOIs against Crossref and emit BibTeX plus an audit ledger."""

from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
PAPER = SCRIPT.parents[1]
USER_AGENT = "PersistenceWithoutOwnership05/1.0 (scientific manuscript verification)"

REFERENCES = {
    "turing1952": "10.1098/rstb.1952.0012",
    "fitzhugh1961": "10.1016/S0006-3495(61)86902-6",
    "nagumo1962": "10.1109/JRPROC.1962.288235",
    "gierer1972": "10.1007/BF00289234",
    "wolpert1969": "10.1016/S0022-5193(69)80016-0",
    "cross1993": "10.1103/RevModPhys.65.851",
    "zwicker2017": "10.1038/nphys3984",
    "brangwynne2009": "10.1126/science.1172046",
    "nakashima2021": "10.1038/s41467-021-24111-x",
    "matsuo2021": "10.1038/s41467-021-25530-6",
    "donau2020": "10.1038/s41467-020-18815-9",
    "hanczyc2003": "10.1126/science.1089904",
    "gardner2000": "10.1038/35002131",
    "elowitz2000": "10.1038/35002125",
    "xiong2003": "10.1038/nature02089",
    "hopfield1982": "10.1073/pnas.79.8.2554",
    "hermann1977": "10.1109/TAC.1977.1101601",
    "efron1979": "10.1214/aos/1176344552",
    "pearl1995": "10.1093/biomet/82.4.669",
    "rubin1974": "10.1037/h0037350",
    "nosek2018": "10.1073/pnas.1708274114",
    "kaufman2012": "10.1145/2382577.2382579",
    "jaqaman2008": "10.1038/nmeth.1237",
    "rosenfeld1966": "10.1145/321356.321357",
    "varela1974": "10.1016/0303-2647(74)90031-8",
    "bedau2000": "10.1162/106454600300103683",
    "maturana1980": "10.1007/978-94-009-8947-4",
    "godfreysmith2009": "10.1093/acprof:osobl/9780199552047.001.0001",
    "banani2017": "10.1038/nrm.2017.7",
    "hyman2014": "10.1146/annurev-cellbio-100913-013325",
}


def fetch(doi: str) -> dict[str, Any]:
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)["message"]


def clean(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value)
    return value.replace("{", "").replace("}", "").replace("&", r"\&").strip()


def year(message: dict[str, Any]) -> int:
    block = message.get("published-print") or message.get("published-online") or message.get("issued")
    return int(block["date-parts"][0][0])


def authors(message: dict[str, Any]) -> str:
    values = []
    for author in message.get("author", []):
        family = clean(author.get("family", ""))
        given = clean(author.get("given", ""))
        values.append(f"{family}, {given}" if given else family)
    return " and ".join(value for value in values if value) or "Unknown"


def bib_entry(key: str, message: dict[str, Any]) -> str:
    item_type = message.get("type", "journal-article")
    entry_type = "book" if item_type in {"book", "monograph", "edited-book"} else "article"
    fields = {
        "author": authors(message),
        "title": clean((message.get("title") or [""])[0]),
        "year": str(year(message)),
        "doi": message["DOI"],
        "url": f"https://doi.org/{message['DOI']}",
    }
    if entry_type == "book":
        fields["publisher"] = clean(message.get("publisher", ""))
        fields["isbn"] = ", ".join(message.get("ISBN", []))
    else:
        fields["journal"] = clean((message.get("container-title") or [""])[0])
        fields["volume"] = clean(str(message.get("volume", "")))
        fields["number"] = clean(str(message.get("issue", "")))
        fields["pages"] = clean(str(message.get("page", message.get("article-number", ""))))
    lines = [f"@{entry_type}{{{key},"]
    for field, value in fields.items():
        if value:
            lines.append(f"  {field} = {{{value}}},")
    lines.append("}\n")
    return "\n".join(lines)


def main() -> int:
    verified = []
    entries = []
    for key, requested_doi in REFERENCES.items():
        message = fetch(requested_doi)
        resolved = message["DOI"]
        if resolved.lower() != requested_doi.lower():
            raise AssertionError((key, requested_doi, resolved))
        title = clean((message.get("title") or [""])[0])
        if not title:
            raise AssertionError(f"missing title for {requested_doi}")
        verified.append(
            {
                "citation_key": key,
                "requested_doi": requested_doi,
                "resolved_doi": resolved,
                "title": title,
                "year": year(message),
                "publisher": message.get("publisher"),
                "container_title": (message.get("container-title") or [None])[0],
                "crossref_url": f"https://api.crossref.org/works/{urllib.parse.quote(requested_doi, safe='')}",
                "status": "VERIFIED",
            }
        )
        entries.append(bib_entry(key, message))
    (PAPER / "references.bib").write_text("\n".join(entries), encoding="utf-8", newline="\n")
    (PAPER / "REFERENCE_VERIFICATION_05.json").write_text(
        json.dumps(
            {
                "schema": "PERSISTENCE-WITHOUT-OWNERSHIP-REFERENCE-VERIFICATION-05-v1",
                "registry": "Crossref REST API",
                "verified_count": len(verified),
                "failed_count": 0,
                "references": verified,
            },
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({"verified": len(verified), "failed": 0}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
