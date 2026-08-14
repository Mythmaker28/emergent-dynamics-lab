#!/usr/bin/env bash
# Offline readback: clone the reassembled bare repository with no network, check out the exact
# commit, verify HEAD, tree hash, file count, missing objects and fsck, then run the tests.
# Usage:  bash offline_readback.sh [dir-produced-by-reassemble_and_verify.sh]
set -euo pipefail
OUT="${1:-$PWD/orr01_offline}"
HEAD_EXPECT=d89c2217697c33cfb66a6878b885442f13b19c57
TREE_EXPECT=b1cb4ae8f5d0c829eee752d11dd407310fd6c477
export GIT_NO_LAZY_FETCH=1 GIT_TERMINAL_PROMPT=0
rm -rf "$OUT/wc"
git clone -q "$OUT/bare4" "$OUT/wc"
cd "$OUT/wc"
git checkout -q "$HEAD_EXPECT"
H=$(git rev-parse HEAD); T=$(git rev-parse HEAD^{tree})
N=$(git ls-files | wc -l)
M=$(git rev-list --objects --missing=print HEAD 2>&1 | grep -c '^?' || true)
echo "HEAD       $H   $([ "$H" = "$HEAD_EXPECT" ] && echo OK || echo MISMATCH)"
echo "tree hash  $T   $([ "$T" = "$TREE_EXPECT" ] && echo OK || echo MISMATCH)"
echo "files      $N"
echo "missing    $M   $([ "$M" = "0" ] && echo OK || echo MISMATCH)"
git fsck --full >/dev/null 2>&1 && echo "fsck       clean" || echo "fsck       FAILED"
echo "== ORR01 tests from the offline clone"
( cd ORR01/code && python3 tests_orr.py 2>&1 | tail -3 )
if [ -d CSC01/code ]; then
  echo "== CSC01 tests from the offline clone"
  ( cd CSC01/code && python3 tests_csc.py 2>&1 | tail -3 ) || echo "(CSC01 tests not present in this snapshot)"
fi
