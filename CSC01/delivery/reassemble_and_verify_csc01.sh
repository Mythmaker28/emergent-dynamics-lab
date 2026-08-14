#!/usr/bin/env bash
# Reassemble the CSC01 self-contained repository from its parts and verify it.
# Usage:  bash reassemble_and_verify_csc01.sh [target-dir]
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="${1:-$PWD/csc01_offline}"
mkdir -p "$OUT"
echo "== 1. checking the parts"
( cd "$HERE" && grep -v 'reassembled whole' CSC01_OFFLINE_REPO.SHA256SUMS | sha256sum -c - )
echo "== 2. reassembling"
cat "$HERE"/CSC01_OFFLINE_REPO.tar.gz.part* > "$OUT/CSC01_OFFLINE_REPO.tar.gz"
echo "== 3. checking the whole archive"
EXP=$(grep 'reassembled whole' "$HERE/CSC01_OFFLINE_REPO.SHA256SUMS" | cut -d' ' -f1)
GOT=$(sha256sum "$OUT/CSC01_OFFLINE_REPO.tar.gz" | cut -d' ' -f1)
[ "$EXP" = "$GOT" ] && echo "   OK  $GOT" || { echo "   MISMATCH expected $EXP got $GOT"; exit 1; }
echo "== 4. extracting"
tar xzf "$OUT/CSC01_OFFLINE_REPO.tar.gz" -C "$OUT"
echo "   bare repository at $OUT/bare5"
echo "reassembly verified. Now run:  bash offline_readback_csc01.sh \"$OUT\""
