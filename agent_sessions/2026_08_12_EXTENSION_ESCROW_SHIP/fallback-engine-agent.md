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

## Stage 2 — full page engine (SHIPPED 1.7.6)

Extraction (no forked logic):
- `src/executor.js` (new, shared): getConfig/extensionId identity, agent HTTP
  client, heartbeat (nonce+ledger parameterized), pollOnce, result retry,
  executeCommand + all tab helpers + runInPage, bridgeStatus/relayStatus/
  badge writers (bridgeStatus now stamps `engine`), labels, delay.
- `src/console-engine.js` (new, shared): history chain, consolePost, journal,
  hive records, handleConsoleSubmit + brain loop + affinity plan execution,
  decidePlan/decideApproval, relayFetch/getRelayConfig, mesh drain trio
  (ctx = {ledger, macFresh}), createMeshSocket controller factory.
- `src/background.js` rewritten as conductor over both (~580 lines from
  2923); pair:run handler + escrow + lifetime + alarms + router unchanged;
  startPeers now claims the engine lease as BACKGROUND_HOLDER every
  evaluation/alarm.
- `src/page-engine.js`: backgroundAliveVerdict (ping + updatedAt timestamps),
  leaseDecision (background always wins; page-vs-page staleness 9s, page
  never steals a background lease younger than 75s = two missed alarms),
  createPageEngine (agent loop + relay loop + lease heartbeat + acquire/
  confirm/release + configChanged), handle() dispatching to the SAME
  console-engine handlers the worker's router calls.
- `src/popup.js`: boot check (ping, 2.5 s wait, verdict) → engine start;
  routeLocal flips all owner actions to in-document handlers when the ping
  goes unanswered; sendToBridge wrapper; engine banner; standalone console
  runs a 20 s watchdog so the popover→pinned-console handoff never strands
  the bridge; engine stopped on pagehide beside the listener removal.

Live-feedback items folded in (owner testing live; direct pairing succeeded
on 1.7.5 as browser-24bf5f):
1. Setup card is three-state now: full pair card only with NO credentials;
   compact "Starting the brain…" (code box collapsed, re-pair link) while
   paired-but-not-live; hidden when the brain chip's own verdict is live.
2. Post-connect collapse: successful pair → compact immediately → hidden as
   the engine's relay loop turns relayStatus connected; command box only.
3. Fresh identity adoption: relay loop runs in EVERY engine host (popover
   included); popup's storage listener calls pageEngine.configChanged() on
   credential-key changes → refusal latch lifted, old-identity socket
   closed, interruptible relay sleep woken → socket rebuilds from the same
   RELAY_STORAGE_KEYS the background reads. Identity parity by construction:
   extensionId only from executor getConfig (stored instanceId), relay
   deviceId only from getRelayConfig — asserted by source-shape tests.

Tests: 214 → 230 green (`node --test --test-concurrency=1
'browser-extension/test/*.test.js'`): +11 pure (verdict timestamps, lease
acquire/retain/steal/blocked, cadence asymmetry), +5 lifecycle shapes
(engine teardown on pagehide, background-wins claim, no-fork markers,
identity parity, compact card, configChanged plumbing). eslint clean.

Ship: 1.7.5 → 1.7.6 via scripts/ship-safari-extension.sh. Verified: both
background bundles evaluate clean under a stubbed extension API (node),
popup bundle syntax-checked and carries the engine symbols; installed appex
popup.js/background.js hash-match build/safari; pluginkit still exactly one
enabled row, same UUID (9E196DE3-5C6C-485E-9C5C-83B9B5E3C7D8 — identity
preserved); codesign valid; safari manifest background.scripts / chrome
service_worker fork intact at 1.7.6. Safari relaunch ceremony left to the
owner.
