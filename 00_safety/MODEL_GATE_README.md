# GTS Universal Model PASS Gate

Reusable verification gate for every GTS AI/model stage (AI-1, AI-2, AI-3,
AI-4, future stages). One script, `MODEL_GATE.sh`, is never edited per
stage — a stage is onboarded by adding a manifest.

## Usage

```
00_safety/MODEL_GATE.sh <STAGE>
# e.g.
00_safety/MODEL_GATE.sh AI-1
```

## Manifest format

Each stage declares its own `00_safety/stage_manifests/<STAGE>.conf`:

- `REQUIRES` — space-separated prerequisite stage names (empty for a root
  stage). Each prerequisite's `MODEL_PASS.lock` must exist AND its own
  unit/integration/compile/scope checks are re-run and must still pass.
- `UNIT_TEST_DIRS` — pytest paths for the stage's own unit tests.
- `INTEGRATION_TEST_DIRS` — pytest paths for the stage's own integration/
  wiring tests.
- `COMPILE_DIRS` — directories whose `*.py` files are compiled with
  `py_compile`, and scanned by the scope check.
- `FORBIDDEN_STAGE_TOKENS` — tokens (e.g. `ai-2 ai-3 ai-4`) that must not
  appear as a path/file under `COMPILE_DIRS`.
- `FORBIDDEN_FILENAMES` — filenames that must not exist under
  `COMPILE_DIRS` (e.g. out-of-scope Strategy/Signal/Risk/Execution/Broker
  implementation files).

## Result

- PASS only if every prerequisite stage re-verifies clean AND the current
  stage's own checks all pass. The exit code always comes from actual
  command results — never hard-coded.
- On PASS: writes `00_safety/<STAGEID>_MODEL_PASS.lock` (stage, timestamp,
  git commit, result) and exits 0.
- On FAIL: no lock is written (a stale one is removed), exits 1, and the
  full run is recorded in `00_safety/<STAGEID>_model_gate.log`.
- A missing manifest is a FAIL, never an invented pass — this is what
  blocks a stage (e.g. AI-2) from proceeding until its own manifest is
  deliberately authored against its real file registry.

## Relationship to HARD_GATE.sh

`HARD_GATE.sh` is the original AI-1-specific gate and is unmodified. It
still owns and writes `00_safety/AI1_PASS.lock` and
`00_safety/verification.log` exactly as before. `MODEL_GATE.sh` is a
separate, generic mechanism with its own evidence namespace
(`<STAGEID>_MODEL_PASS.lock`, `<STAGEID>_model_gate.log`) so neither tool's
evidence overwrites the other's.
