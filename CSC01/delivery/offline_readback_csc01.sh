#!/usr/bin/env bash
# Offline readback of the CSC01 artefact: clone with no network, verify HEAD, tree hash, file
# count, missing objects and fsck, then run the CSC01 and ORR01 integrity harnesses.
# Usage:  bash offline_readback_csc01.sh [dir-produced-by-reassemble_and_verify_csc01.sh]
set -euo pipefail
OUT="${1:-$PWD/csc01_offline}"
HEAD_EXPECT=bc9ce265cdb16f349946d552153d4a90a371a7b6
TREE_EXPECT=b5ef7f1a7c5e10c10e24ea6dbcbcb15cfea2527b
export GIT_NO_LAZY_FETCH=1 GIT_TERMINAL_PROMPT=0
rm -rf "$OUT/wc"
git clone -q "$OUT/bare5" "$OUT/wc"
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
echo "== CSC01 stage-A harness from the offline clone"
( cd CSC01/code && PYTHONPATH="$PWD:$PWD/../../ORR01/code" python3 tests_csc.py 2>&1 | tail -3 )
echo "== CSC01 adversarial audit from the offline clone"
( cd CSC01/code && PYTHONPATH="$PWD:$PWD/../../ORR01/code" python3 audit_csc.py 2>&1 | tail -3 )
echo "== ORR01 harness from the offline clone"
( cd ORR01/code && python3 tests_orr.py 2>&1 | tail -2 )
