#!/bin/bash
# GTS Universal Model PASS Gate
#
# Reusable, manifest-driven verification gate for every GTS AI/model stage
# (AI-1, AI-2, AI-3, AI-4, and future stages). This script is never edited
# per stage — a new stage is onboarded solely by adding a manifest file at
# 00_safety/stage_manifests/<STAGE>.conf.
#
# A stage is PASS only when:
#   - every prerequisite stage (REQUIRES=) still has a MODEL_PASS.lock AND
#     its own unit/integration/compile/scope checks re-verify clean, and
#   - the current stage's own unit/integration/compile/scope checks pass.
# Any failure anywhere in that chain = FAIL, no lock is written/kept, and
# the script exits non-zero. PASS is never hard-coded.
#
# Usage: 00_safety/MODEL_GATE.sh <STAGE>     e.g. 00_safety/MODEL_GATE.sh AI-1

set -uo pipefail

ROOT="/opt/gts-1"
SAFETY="$ROOT/00_safety"
MANIFEST_DIR="$SAFETY/stage_manifests"

if [ $# -ne 1 ]; then
  echo "Usage: $0 <STAGE>   e.g. $0 AI-1" >&2
  exit 2
fi

STAGE="$1"
STAGE_ID="$(echo "$STAGE" | tr -cd 'A-Za-z0-9')"
LOG="$SAFETY/${STAGE_ID}_model_gate.log"
LOCK="$SAFETY/${STAGE_ID}_MODEL_PASS.lock"
MANIFEST="$MANIFEST_DIR/${STAGE}.conf"

rm -f "$LOCK"
exec > >(tee "$LOG") 2>&1

echo "=== GTS UNIVERSAL MODEL PASS GATE ==="
date -Is
echo "ROOT=$ROOT"
echo "STAGE=$STAGE"
echo "MANIFEST=$MANIFEST"
echo

GATE_FAIL=0

run_pytest_set() {
  # $1 = label; remaining args = test dirs (relative to ROOT)
  local label="$1"; shift
  local d ec
  if [ "$#" -eq 0 ]; then
    echo "$label: (no test dirs declared)"
    return 0
  fi
  for d in "$@"; do
    echo "--- $label: $d ---"
    python3 -m pytest "$ROOT/$d" -v
    ec=$?
    echo "${label}_EXIT($d)=$ec"
    if [ "$ec" -ne 0 ]; then
      return 1
    fi
  done
  return 0
}

run_compile_check() {
  local label="$1"; shift
  local rc=0 f
  if [ "$#" -eq 0 ]; then
    echo "$label: (no compile dirs declared)"
    return 0
  fi
  for d in "$@"; do
    [ -d "$ROOT/$d" ] || continue
    while IFS= read -r -d '' f; do
      python3 -m py_compile "$f"
      if [ $? -ne 0 ]; then
        echo "${label}_COMPILE_FAIL: $f"
        rc=1
      fi
    done < <(find "$ROOT/$d" -name "*.py" -type f -print0 2>/dev/null)
  done
  echo "${label}_COMPILE_EXIT=$rc"
  return $rc
}

run_scope_check() {
  # $1=label $2=forbidden stage tokens (space-sep) $3=forbidden filenames (space-sep), remaining = dirs
  local label="$1"; shift
  local stage_tokens="$1"; shift
  local filename_tokens="$1"; shift
  local rc=0 pattern hit d

  if [ -n "$stage_tokens" ]; then
    pattern="($(echo "$stage_tokens" | sed 's/ \+/|/g'))"
    hit=""
    for d in "$@"; do
      [ -d "$ROOT/$d" ] || continue
      f=$(find "$ROOT/$d" \( -type d -o -type f \) | grep -iE "$pattern" || true)
      [ -n "$f" ] && hit="${hit}
${f}"
    done
    if [ -n "$hit" ]; then
      echo "${label}_FORBIDDEN_STAGE_MATCH:${hit}"
      rc=1
    else
      echo "${label}_FORBIDDEN_STAGE_MATCH: none"
    fi
  fi

  if [ -n "$filename_tokens" ]; then
    pattern="($(echo "$filename_tokens" | sed 's/ \+/|/g'))"
    hit=""
    for d in "$@"; do
      [ -d "$ROOT/$d" ] || continue
      f=$(find "$ROOT/$d" -type f | grep -iE "$pattern" || true)
      [ -n "$f" ] && hit="${hit}
${f}"
    done
    if [ -n "$hit" ]; then
      echo "${label}_FORBIDDEN_FILENAME_MATCH:${hit}"
      rc=1
    else
      echo "${label}_FORBIDDEN_FILENAME_MATCH: none"
    fi
  fi

  echo "${label}_SCOPE_EXIT=$rc"
  return $rc
}

verify_stage() {
  # Loads a manifest and runs unit+integration+compile+scope checks for it.
  # $1 = label prefix for log lines, $2 = manifest path
  local label="$1" manifest="$2"
  local REQUIRES="" UNIT_TEST_DIRS="" INTEGRATION_TEST_DIRS="" COMPILE_DIRS=""
  local FORBIDDEN_STAGE_TOKENS="" FORBIDDEN_FILENAMES=""
  # shellcheck disable=SC1090
  source "$manifest"

  local rc=0
  run_pytest_set "${label}_UNIT" $UNIT_TEST_DIRS || rc=1
  run_pytest_set "${label}_INTEGRATION" $INTEGRATION_TEST_DIRS || rc=1
  run_compile_check "${label}_COMPILE" $COMPILE_DIRS || rc=1
  run_scope_check "${label}_SCOPE" "$FORBIDDEN_STAGE_TOKENS" "$FORBIDDEN_FILENAMES" $COMPILE_DIRS || rc=1
  return $rc
}

if [ ! -f "$MANIFEST" ]; then
  echo "FAIL: no verification manifest for stage '$STAGE' ($MANIFEST)"
  echo
  echo "=== RESULT ==="
  echo "NOT VERIFIED: stage manifest missing. Gate does not invent stage architecture."
  exit 1
fi

REQUIRES=""
# shellcheck disable=SC1090
source "$MANIFEST"
STAGE_REQUIRES="$REQUIRES"

echo "=== ACCUMULATED STACK CHECK (requires: ${STAGE_REQUIRES:-<none, root stage>}) ==="
for PRIOR in $STAGE_REQUIRES; do
  PRIOR_ID="$(echo "$PRIOR" | tr -cd 'A-Za-z0-9')"
  PRIOR_LOCK="$SAFETY/${PRIOR_ID}_MODEL_PASS.lock"
  PRIOR_MANIFEST="$MANIFEST_DIR/${PRIOR}.conf"

  echo "--- prerequisite: $PRIOR ---"
  if [ ! -f "$PRIOR_LOCK" ]; then
    echo "FAIL: prerequisite stage $PRIOR has no PASS lock ($PRIOR_LOCK)"
    GATE_FAIL=1
    continue
  fi
  if [ ! -f "$PRIOR_MANIFEST" ]; then
    echo "FAIL: prerequisite stage $PRIOR has no manifest, cannot re-verify"
    GATE_FAIL=1
    continue
  fi
  echo "PASS lock present: $PRIOR_LOCK"
  echo "Re-verifying accumulated tests for $PRIOR ..."
  if verify_stage "PRIOR_${PRIOR_ID}" "$PRIOR_MANIFEST"; then
    echo "PASS: prerequisite stage $PRIOR accumulated checks re-verified"
  else
    echo "FAIL: prerequisite stage $PRIOR accumulated checks failed on re-verification"
    GATE_FAIL=1
  fi
done
echo

echo "=== CURRENT STAGE CHECK ($STAGE) ==="
if verify_stage "CUR_${STAGE_ID}" "$MANIFEST"; then
  echo "PASS: current stage $STAGE checks passed"
else
  echo "FAIL: current stage $STAGE checks failed"
  GATE_FAIL=1
fi
echo

echo "=== REPOSITORY STATUS (informational only, does not gate PASS/FAIL) ==="
git -C "$ROOT" status --short
echo

echo "=== RESULT ==="
if [ "$GATE_FAIL" -eq 0 ]; then
  echo "VERIFIED: $STAGE accumulated verification PASSED."
  {
    echo "stage=$STAGE"
    echo "timestamp=$(date -Is)"
    echo "commit=$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || echo unknown)"
    echo "result=PASS"
  } > "$LOCK"
  exit 0
else
  echo "NOT VERIFIED: $STAGE failed one or more accumulated/current checks."
  rm -f "$LOCK"
  exit 1
fi
