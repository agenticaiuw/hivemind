# Harness derivation — mac-terminal — round 100

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent health 2026-08-07 round 100** — GET /observe reports Accessibility trusted=false and eventsPost=false: ui_click, ui_menu, type_text, press_keys can report success while doing nothing; inputReachability failed. Screen Recording is also false, computer-use loop disabled. Browser extension is offline with 9 pending commands. /journal reports 120 retained jobs, 146 actions, 18 failed, 0 undoable, and 112 unattributed routing tiers.
  - evidence: Authenticated GET /observe, GET /ops/status, GET /journal returned HTTP 200 at 2026-08-07T13:38Z.

## Capabilities it proposed

### "Make computer control work again, and tell me exactly what I need to fix."
- **useful because:** Today the agent can claim UI actions succeeded even though macOS rejects them because Accessibility is granted to a different binary; browser work can also stall while the bridge is offline. The owner should be able to ask the pendant to diagnose the control plane, give a precise human repair checklist, wait for the repair, and prove that control really works with a harmless test.
- **path:** pendant → relay → mac-planner → mac-vision → browser-harness → dashboard
- **model tier:** Use the realtime model only for the short spoken diagnosis and repair conversation; use a cheaper background model to correlate health signals, generate the checklist, and validate the post-repair probe.
- **latency:** Initial diagnosis under 2 seconds from cached local health; checklist generation under 5 seconds; validation immediately after the owner changes permissions or enables the bridge.
- **cost:** Low: one short realtime turn plus a small background diagnostic/summary call; local probes and validation dominate latency, not API cost.
- **security:** Permission state, app identities, browser availability, and window metadata should remain on the Mac unless the owner explicitly asks to share them. Never ask the owner to expose tokens or private page contents. The repair assistant must not silently grant permissions, alter TCC databases, or run arbitrary remediation; it should explain exact System Settings locations and verify afterward.
- **missing:** A capability-level control-plane diagnostic contract that maps /observe and /ops/status failures to human repair steps; A guided System Settings handoff with deep links where macOS permits them; A post-repair harmless reachability probe whose result is independently verified rather than trusting the action receipt; A browser-bridge recovery check that distinguishes offline, stale polling, blocked dialog, and wrong-tab conditions; A pendant/dashboard repair state that persists across the owner leaving and returning


## Changes it proposed to its own stack

### `mac-harness` — Add an execution-health preflight and fallback planner driven by the existing read-only /observe, /ops/status, /browser/status, and /routing data. Before dispatching UI or browser actions, attach a capability snapshot (accessibility/inputReachability, screen recording, browser online/lastSeen, pending-command age, relay reachability) to the job. If UI reachability is false, do not claim success: automatically route reads to shell/AppleScript where possible, route public-page reads to relay/browser-run, and return a precise unmet prerequisite for private browser work. If the bridge is offline or commands are stale, collapse/supersede duplicate pending requests by idempotency key rather than waiting 45 seconds per attempt. Keep FULL_CONTROL_MODE and all owner-approved actions unchanged; this is observability, routing, and recovery, not a gate.
- **owner gets:** The owner currently can hear a receipt saying a click or typing succeeded when macOS rejected the event, and browser requests can burn nearly a minute while the extension is offline. This makes the pendant tell the truth immediately, use an alternate path when one exists, and avoid repeated dead waits.
- effort: Medium: health snapshot schema, planner preflight, fallback mapping for common reads, stale-command coalescing, and tests for truthful receipts.  ·  risk: A transient permission or bridge outage could cause a fallback to a less rich result or a fast prerequisite message; preserve the original requested action and make fallback provenance explicit. Never silently substitute a mutation. Recovery is retry after health changes.
- cost: Negligible API cost; fewer wasted model turns and browser timeouts. Small local CPU/storage overhead for health snapshots.  ·  latency: Adds <100 ms local preflight; avoids current 45-second browser timeout loops and unnecessary planner retries.
- security: Read-only health metadata stays local and should redact URLs/titles from relay telemetry. No new authority or restriction is introduced.
- depends on: Existing GET /observe, GET /ops/status, GET /browser/status, GET /routing, and durable job receipts; A typed fallback registry for read-only intents

### `relay` — Create a cross-surface failure-recovery ledger. When a Mac job fails, persist a normalized incident containing job/action IDs, surface, error signature, health snapshot, safe diagnostics, likely cause, retryability, and a concrete repair recipe. Let the relay/pedant query incidents by natural references ('that browser thing', 'why didn't it open') and let mac-planner resume from the failed step rather than replaying the entire plan. Automatically deduplicate repeated failures and mark incidents resolved when a later receipt verifies recovery; never auto-run a mutation merely because a repair recipe exists.
- **owner gets:** Today the owner gets a failure string and must remember what happened or ask the whole task again. The pendant could explain 'the click never reached the Mac because Accessibility is assigned to another binary' or 'the browser bridge has been offline since…', then resume only the missing step after the fix.
- effort: Medium: normalized incident schema in the durable job store/relay D1, error fingerprinting, health-snapshot attachment, natural-reference lookup, and resume-from-step integration.  ·  risk: Error details can contain private paths, URLs, or snippets; redact secrets and keep raw diagnostics on the Mac. A bad repair classification could waste a retry, so recipes should be advisory and idempotency-aware.
- cost: Low local/D1 storage and negligible model cost; fewer repeated planner calls and fewer duplicate actions.  ·  latency: Instant status answers from stored incidents; resume adds only the remaining-step latency.
- security: Cross-surface relay records must use existing pairing/auth and sensitivity labels. Do not send shell stdout or private page content unless explicitly requested.
- depends on: Existing durable /jobs and /journal records; Existing receipts and idempotency keys; GET /observe and /ops/status health data; Relay job-status surface and mac-planner resume support

### `mac-harness` — Ship the local agent as a single signed, stable macOS application identity whose Accessibility and Screen Recording grants are requested and consumed by the same executable that posts input events. At startup, compare the bundle ID, code-signing identity, executable path, and TCC probe result; surface a one-click repair path when they diverge. Keep the current unrestricted execution policy, but refuse to label UI work as successful when the runtime identity cannot reach the screen. Add an integration test that launches the packaged app, verifies the TCC identity, performs a zero-impact focus/read probe, and survives an app update without silently losing the grant.
- **owner gets:** The owner should not have to understand that Accessibility was granted to a different binary than the running agent. A packaging/runtime identity fix would make GUI control persist across launches and updates instead of silently doing nothing while receipts claim success.
- effort: Medium to high: signing and bundle packaging changes, TCC migration/repair UX, startup diagnostics, and a release test on a clean Mac and an upgraded installation.  ·  risk: Changing the signed identity can invalidate an existing grant once, requiring the owner to re-enable it; retain a clear migration prompt and preserve shell/browser capabilities while UI permission is repaired. Do not modify the TCC database programmatically.
- cost: No per-call API cost; modest release engineering and QA cost. No meaningful runtime power draw.  ·  latency: Negligible startup identity check; removes false-success retries and long GUI debugging loops.
- security: A stable signed identity improves the meaning of the owner's explicit macOS permissions. It does not add authority or reduce FULL_CONTROL_MODE; private diagnostics remain local.
- depends on: Existing /observe inputReachability and permissions reporting; Packaged AI Pendant Agent application identity; Existing action receipts and /ops status dashboard; A clean-install and upgrade test harness


## What it asked for

_Nothing._
## Its own summary

Round 100 discovery is complete. Live observability shows the Mac agent is reachable and FULL_CONTROL remains enabled, but Accessibility is not trusted for the actual AI Pendant Agent binary, so synthesized UI events are rejected while UI receipts may still say success; Screen Recording is also absent and computer-use is disabled. The browser extension is offline with 9 pending commands, and the journal shows 120 retained jobs, 146 actions, 18 failures, 0 undoable, and 112 actions without routing-tier attribution. I recorded this finding and proposed (1) a cross-surface failure-recovery ledger that lets the pendant explain and resume failed work, and (2) health-aware fallback/coalescing (the latter was noted as close to existing work).

**Biggest unknown:** I do not need another tool grant this round. What is still needed operationally is owner-side Accessibility permission for the running AI Pendant Agent binary and, for private browser tasks, Safari/browser-bridge polling to come online. Screen Recording is needed before mac-vision can truthfully operate. Once those are fixed, a fresh /observe and one harmless UI/browser probe should validate the path.

