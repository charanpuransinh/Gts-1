#!/bin/bash
set -euo pipefail

ROOT="/opt/gts-1"
LOG="$ROOT/00_safety/verification.log"
LOCK="$ROOT/00_safety/AI1_PASS.lock"

rm -f "$LOCK"
exec > >(tee "$LOG") 2>&1

echo "=== GTS HARD VERIFICATION GATE ==="
date -Is
echo "ROOT=$ROOT"

test -d "$ROOT/uploads" || {
  echo "FAIL: uploads directory missing"
  exit 1
}

echo "=== UPLOAD INVENTORY ==="
find "$ROOT/uploads" -type f -print | sort

echo "=== SHA256 ==="
find "$ROOT/uploads" -type f -print0 | sort -z | xargs -0 -r sha256sum

echo "=== AI-1 ORIGINAL TESTS (01_market_data/tests) ==="
set +e
python3 -m pytest "$ROOT/01_market_data/tests" -v
UNIT_EXIT=$?
set -e
echo "UNIT_TEST_EXIT=$UNIT_EXIT"

echo "=== AI-1 INTEGRATION TESTS (28_tests) ==="
set +e
python3 -m pytest "$ROOT/28_tests" -v
INTEGRATION_EXIT=$?
set -e
echo "INTEGRATION_TEST_EXIT=$INTEGRATION_EXIT"

echo "=== RESULT ==="
if [ "$UNIT_EXIT" -eq 0 ] && [ "$INTEGRATION_EXIT" -eq 0 ]; then
  echo "VERIFIED: AI-1 original tests and integration tests passed."
  touch "$LOCK"
  exit 0
else
  echo "NOT VERIFIED: AI-1 tests failed (unit_exit=$UNIT_EXIT integration_exit=$INTEGRATION_EXIT)."
  exit 1
fi
