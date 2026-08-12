# Fallback engine agent — worklog

Task: make the extension work when Safari refuses to run the background script.
Re-scoped mid-task by the orchestrator into two stages.

## Stage 1 — popup-direct pairing (SHIPPED 1.7.5)

- `src/page-engine.js` (new): `PAIR_REPLY_TIMEOUT_MS` (2.5 s),
  `pairFallbackVerdict` (pure: when may the popup pair on its own),
  `directOutcomeWritePlan` (pure: a direct failure never buries a fresher
  worker success under PAIR_OUTCOME_KEY), `runDirectPairing` (effectful:
  the worker's pair:run body run from the page — pairStoragePatch →
  storage.local, session sentinel before credentials, sync token removal,
  escrow via sendNativeMessage guarded, outcome record guarded by the plan).
- `src/popup.js`: Connect now races `pair:run` against the 2.5 s window;
  a real reply keeps the worker path; timeout/undefined/thrown send consults
  the verdict (fresh PAIR_OUTCOME_KEY = worker acted) and otherwise runs the
  exchange directly from the popup document. The dead-end "Still pairing…"
  narration is gone.
- Safety facts measured before coding: agent's /pair/browser code is the
  static PAIRING_CODE (timing-safe compare, NOT single-use), so a double
  exchange is benign — the only real race is failure-over-success on the
  outcome record, which the write plan guards.
- Tests: `test/page-engine.test.js` (17 new: verdict rules, write-plan rules,
  full fake-api runs of the direct exchange incl. sentinel ordering and
  session-never-escrowed). `test/popup-lifecycle.test.js` extended (popup
  escalation shapes; page-engine honours the worker's storage contract; no
  storage listeners in page-engine). Suite: 195 → 214, all green
  (`node --test --test-concurrency=1 'browser-extension/test/*.test.js'`).
- Ship: manifest 1.7.4 → 1.7.5, `scripts/ship-safari-extension.sh` completed
  1.7.4 → 1.7.5; pluginkit shows exactly 1 enabled row at ~/Applications;
  codesign valid; installed popup.js hash == build/safari/popup.js; installed
  manifest = background.scripts (Safari), chrome build keeps service_worker.
  Safari relaunch ceremony left to the owner per orchestrator instruction.

## Stage 2 — full page engine (pending)

Agent bridge loop (heartbeat/poll/execute/report), relay socket + drain,
storage lease single-flight, standalone-console host, popup UX note.
Planned extraction: executor out of background.js shared by both contexts;
lease pure rules in page-engine.js. Ship as 1.7.6.
