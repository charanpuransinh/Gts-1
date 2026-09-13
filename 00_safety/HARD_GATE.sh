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

echo "=== RESULT ==="
echo "NOT VERIFIED: AI-1 has not yet been uploaded/tested."
exit 1
