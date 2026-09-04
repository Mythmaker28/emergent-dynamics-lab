"""Portable locations; no engine or network is imported by the paper pipeline."""
from pathlib import Path
import hashlib
import json

PKG = Path(__file__).resolve().parents[1]
ROOT = PKG.parents[1]
PROV = PKG / 'provenance'

def read(rel):
    return json.loads((ROOT / rel).read_text(encoding='utf-8-sig'))

def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()

def dump(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')

def require(condition, message):
    if not condition:
        raise AssertionError(message)
