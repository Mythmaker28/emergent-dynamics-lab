"""OMLDCT02 — the digest primitives, with every rule written out in committed code.

OMLDCT01 recorded four digests. Two of them, METHODS_HASH and SEED_SET_HASH, turned out to be
impossible to recompute from the committed repository, because the scripts that produced them were
inline heredocs that were never committed: 21 and 72 candidate serialisations respectively failed to
reproduce them. A third, the durability record's FREEZE_HASH, held the master freeze FILE digest
under a key the master freeze used for a digest of its own CONTENT — one label over two quantities.

This module exists so that neither failure can recur. Every digest OMLDCT02 emits is produced by a
function in this file, and every rule that could vary between two honest implementations is fixed
here explicitly rather than left to a default.
"""
from __future__ import annotations
import json, hashlib, os

# --------------------------------------------------------------------------- the declared rules
CANONICAL_RULES = {
 "algorithm": "SHA-256, output as 64 lowercase hexadecimal characters",
 "json_encoding": "json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True)",
 "sort_keys": "true — object keys are ordered by Unicode code point, so insertion order cannot "
              "change a digest",
 "separators": "',' and ':' with NO surrounding space",
 "whitespace_rule": "the encoded JSON contains no whitespace outside string literals",
 "newline_rule": "NO trailing newline. The digest is taken over the encoded bytes exactly as "
                 "produced by json.dumps, with nothing appended",
 "text_encoding": "UTF-8. ensure_ascii=True means the encoded form is pure ASCII, so the UTF-8 "
                  "step cannot introduce a platform difference",
 "float_rule": "no float is ever hashed. Law parameters enter a digest by their IEEE-754 bit "
               "pattern as a lowercase 0x-prefixed hexadecimal string, never by their decimal "
               "repr, which is where two Python versions could disagree",
 "path_ordering": "byte-lexicographic ordering of the UTF-8 encoding of the repository-relative "
                  "POSIX path. Every path begins with '/' and uses '/' as separator on every "
                  "platform",
 "list_ordering": "lists are hashed in the order given and that order is stated by the caller. No "
                  "digest depends on a set iteration order",
 "excluded_self_referential_fields": "a document's own digest field is removed before the document "
                                     "is hashed, and so is GENERATED_UTC, so that regenerating an "
                                     "unchanged document reproduces its digest exactly",
}

FOUR_DISTINCT_LABELS = {
 "FREEZE_CONTENT_HASH": "canonical digest of the master freeze document with FREEZE_CONTENT_HASH "
                        "and GENERATED_UTC removed. Answers: is the frozen CONTENT this content?",
 "FREEZE_FILE_SHA256":  "sha256 of the master freeze FILE's bytes on disk. Answers: is this FILE "
                        "byte-identical? Stored OUTSIDE the freeze, in its sidecar and in the "
                        "external manifest, because a file cannot contain its own file digest.",
 "METHODS_HASH":        "canonical digest of the ordered [path, sha256] list of every method file.",
 "SEED_SET_HASH":       "canonical digest of the ordered [role, index, seed] list of every seed.",
}

# --------------------------------------------------------------------------- the primitives
def canonical_bytes(obj) -> bytes:
    """The one encoding. Everything hashed in OMLDCT02 passes through here."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")

def canonical_digest(obj) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()

def file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""): h.update(chunk)
    return h.hexdigest()

SELF_REFERENTIAL = ("FREEZE_CONTENT_HASH", "FREEZE_FILE_SHA256", "METHODS_HASH", "SEED_SET_HASH",
                    "GENERATED_UTC")

def content_digest(doc: dict, extra_excluded=()) -> str:
    """Digest of a document's content. The document's own digest fields and its timestamp are
    removed first, so that regenerating an unchanged document reproduces the digest."""
    d = {k: v for k, v in doc.items()
         if k not in SELF_REFERENTIAL and k not in tuple(extra_excluded)}
    return canonical_digest(d)

def sort_paths(paths):
    """byte-lexicographic on the UTF-8 encoding, not on Python's default string comparison, so that
    a non-ASCII path could never order differently between two implementations."""
    return sorted(paths, key=lambda p: p.encode("utf-8"))

def methods_hash(modules) -> str:
    """modules: iterable of {'path': '/A/b.py', 'sha256': '...'}. Ordered by path, then hashed as a
    list of two-element lists."""
    ordered = sorted(modules, key=lambda m: m["path"].encode("utf-8"))
    return canonical_digest([[m["path"], m["sha256"]] for m in ordered])

def seed_set_hash(seeds) -> str:
    """seeds: iterable of {'role': 'BASE'|'RESERVE', 'index': int, 'seed': int} in the order they
    are frozen. Hashed as a list of three-element lists IN THAT ORDER — the accrual order is part
    of the frozen object and must be inside the digest."""
    return canonical_digest([[s["role"], int(s["index"]), int(s["seed"])] for s in seeds])

def float_bits(x: float) -> str:
    """the only permitted way for a float to enter a digest."""
    import struct
    return "0x" + struct.pack(">d", float(x)).hex()

# --------------------------------------------------------------------------- self-test
def self_test():
    """Deterministic, no repository access. Every property this module promises is checked here."""
    r = []
    def chk(name, ok, detail=""): r.append({"case": name, "PASS": bool(ok), "detail": detail})
    chk("no trailing newline", not canonical_bytes({"a": 1}).endswith(b"\n"),
        repr(canonical_bytes({"a": 1})))
    chk("no whitespace", b" " not in canonical_bytes({"a": 1, "b": [1, 2]}),
        repr(canonical_bytes({"a": 1, "b": [1, 2]})))
    chk("key order irrelevant", canonical_digest({"a": 1, "b": 2}) == canonical_digest({"b": 2, "a": 1}))
    chk("list order matters", canonical_digest([1, 2]) != canonical_digest([2, 1]))
    chk("ascii only", all(c < 128 for c in canonical_bytes({"k": "é"})),
        repr(canonical_bytes({"k": "é"})))
    d = {"x": 1, "GENERATED_UTC": "A", "FREEZE_CONTENT_HASH": "zz"}
    e = {"x": 1, "GENERATED_UTC": "B", "FREEZE_CONTENT_HASH": "yy"}
    chk("content digest ignores timestamp and self field", content_digest(d) == content_digest(e))
    chk("content digest still sees content", content_digest(d) != content_digest({"x": 2}))
    m1 = [{"path": "/b.py", "sha256": "11"}, {"path": "/a.py", "sha256": "22"}]
    m2 = [{"path": "/a.py", "sha256": "22"}, {"path": "/b.py", "sha256": "11"}]
    chk("methods hash is order-independent in input", methods_hash(m1) == methods_hash(m2))
    chk("methods hash sees a byte change",
        methods_hash(m1) != methods_hash([{"path": "/b.py", "sha256": "11"},
                                          {"path": "/a.py", "sha256": "23"}]))
    s1 = [{"role": "BASE", "index": 0, "seed": 7}, {"role": "BASE", "index": 1, "seed": 8}]
    s2 = [{"role": "BASE", "index": 1, "seed": 8}, {"role": "BASE", "index": 0, "seed": 7}]
    chk("seed set hash IS order-dependent — accrual order is frozen", seed_set_hash(s1) != seed_set_hash(s2))
    chk("float bits are exact", float_bits(0.001004754572603833) == "0x3f50763f01e8e5b2",
        float_bits(0.001004754572603833))
    chk("float bits distinguish neighbours", float_bits(1.0) != float_bits(1.0000000000000002))
    chk("path sort is byte-lexicographic",
        sort_paths(["/b", "/a", "/A"]) == ["/A", "/a", "/b"], str(sort_paths(["/b", "/a", "/A"])))
    return r, all(x["PASS"] for x in r)

if __name__ == "__main__":
    rows, ok = self_test()
    for x in rows: print(("PASS " if x["PASS"] else "FAIL ") + x["case"])
    print("HASH_PRIMITIVE_SELF_TEST =", "PASS" if ok else "FAIL")
