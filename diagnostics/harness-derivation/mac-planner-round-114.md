# Harness derivation — mac-planner — round 114

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **cross-node availability 2026-08-07 round 114** — Relay and Mac bridge are reachable, but browser extension home-chrome is offline with 9 pending commands. Mac agent reports fullControlMode=true, automation grants present, Accessibility and Screen Recording false, and ready=false; browser actions therefore fail or time out and pending work has no durable reconciliation outcome.
  - evidence: GET /browser/status returned online:false,pendingCommands:9; GET /ops/status returned relay reachable, macBridgeOnline:true, browser online:false, accessibility.trusted:false, screenRecording.granted:false; GET /jobs showed browser_navigate failures caused by offline/timeout.

## Capabilities it proposed

### "If I ask you to do something while my Mac or browser is offline, remember the intent, wait for the right device to reconnect, then carry it out safely and tell me exactly what happened — without losing it or doing it twice."
- **useful because:** Today the pendant can hear an intent while the browser is offline and the Mac may reconnect later, but there is no owner-visible, cross-node reconciliation contract. This would turn intermittent connectivity into a dependable assistant: one request ID, durable pending state, deduplication, conflict detection, and a short spoken result when the action is finally applied. It is specifically multi-node: pendant captures intent, relay persists and arbitrates, Mac/browser execute, and the pendant reports the receipt.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the realtime model only to normalize the spoken request and clarify ambiguity; use a cheap background model (or deterministic rules) to reconcile queued intents, device capabilities, and receipts after reconnect.
- **latency:** Capture acknowledgment under 1 second offline; reconnect reconciliation within 10 seconds of a device heartbeat; spoken completion within 3 seconds after receipt. No waiting loop on the pendant.
- **cost:** About $0.001–$0.01 per request, dominated by optional normalization/reconciliation; most retries, dedupe, and receipt matching should be deterministic. Small durable relay storage per intent and receipt.
- **security:** The relay must store only a minimized intent capsule, not page contents or secrets, with encryption, expiry, and device-scoped bearer authorization. Never replay destructive actions (send mail, delete, purchase) from an offline capsule without a fresh owner confirmation; reversible/read-only actions may replay according to owner policy. Surface conflicts such as changed URLs, stale files, or changed calendar state instead of guessing. Dashboard must expose cancel/expire and the full action/receipt chain.
- **missing:** Pendant firmware offline intent capsule queue with monotonic request IDs and retry-safe upload; Relay-side intent ledger/state machine with idempotency keys, expiry, capability matching, and conflict states; Mac bridge reconnect endpoint that claims intents atomically and returns typed receipts; Browser extension reconnect/heartbeat protocol that can resume pending commands and report tab/session validity; Pendant notification/audio path for queued, blocked, completed, and conflict outcomes; Dashboard view and cancel/approve controls for pending intents

### "When the assistant fails or feels slow, tell me the actual cause and fix whatever can be fixed automatically; if it needs me, give me one clear repair step."
- **useful because:** Today failures are scattered across pendant telemetry, relay jobs, Mac permissions, and browser heartbeats. The owner sees generic failure or timeout messages instead of knowing whether the problem is LTE, audio, relay reachability, a sleeping Mac, missing TCC permission, or a stalled browser extension. A cross-node health investigator would correlate the evidence, avoid blaming the wrong device, perform low-risk recovery, and leave a concise diagnosis and repair instruction.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic health rules and cheap background analysis for correlation and remediation selection; reserve realtime only for speaking the diagnosis and asking a clarifying question when multiple causes remain.
- **latency:** Detect degradation within 5 seconds of a failed job or heartbeat miss; attempt safe recovery within 15 seconds; deliver a one-sentence diagnosis within 3 seconds after classification.
- **cost:** Typically under $0.001 per incident because probes, thresholds, and remediation are deterministic; occasional small-model correlation costs under $0.01. Storage is a compact rolling health timeline, not raw audio or page data.
- **security:** Health data can reveal device presence, network state, and logged-in browser usage, so retain only summarized metrics with short TTLs. Automatic remediation must be limited to safe operations such as restarting the bridge, refreshing a heartbeat, retrying a read-only request, or creating a local repair note. Never alter permissions, send messages, delete data, or replay browser mutations without the owner's explicit direction.
- **missing:** A normalized cross-node health event schema with timestamps, device identity, causal links, and confidence; Relay correlation and incident state machine that groups symptoms into one incident instead of many alerts; Pendant-side compact status/error telemetry and a local 'diagnosing' cue that works offline; Mac bridge diagnostic/remediation primitives for bridge restart, permission explanation, network check, and job classification; Browser extension self-test endpoint covering polling, tab attachment, command latency, and stale queue state; Dashboard incident timeline with one recommended repair step and an owner-dismiss/ retry control


## Changes it proposed to its own stack

### `browser-harness` — Add a reconnect watchdog and stale-command quarantine for the browser bridge. On every heartbeat transition offline→online, atomically inspect pending commands, expire entries past TTL, mark attempts with a stable idempotency key, replay only commands whose tab/session preconditions still match, and emit one aggregate receipt for skipped/failed items. If the extension stays offline, surface a single actionable alert rather than allowing an unbounded queue (currently 9 pending commands).
- **owner gets:** The owner stops seeing repeated opaque browser failures and does not accidentally get old commands replayed against a different tab. When Safari/Chrome returns, useful work resumes once, stale work is clearly discarded, and the pendant can say exactly what was recovered.
- effort: Medium: bridge heartbeat state machine, durable command metadata and TTL migration, atomic claim/replay, aggregate receipt, and a small dashboard status panel; test crash/reconnect races.  ·  risk: A command may be incorrectly judged stale or its tab may have changed. Recover by defaulting to quarantine (not replay), showing the reason and original URL/title, and offering explicit retry. Existing pending commands need a one-time migration with conservative expiry.
- cost: Negligible model cost; small D1/local JSON metadata and a few heartbeat writes. No new external data beyond existing command payloads.  ·  latency: Heartbeat processing adds under 100 ms; reconnect replay begins within one poll interval and avoids 45-second timeout failures.
- security: Keep tab/session binding and bearer authorization; never replay irreversible browser actions automatically. Quarantine records should redact page content and expire.
- depends on: Browser command records need createdAt, TTL, tab/session preconditions, and idempotency key; Extension must reliably report heartbeat transitions and command results; Receipt/journal schema must support aggregate recovery outcomes


## What it asked for

_Nothing._
## Its own summary

Discovered current state: relay and Mac bridge are online, but home-chrome is offline with 9 pending browser commands; Mac Accessibility and Screen Recording are still false, while AppleScript automation is granted. Proposed a cross-node offline intent capsule/reconciliation capability and a concrete browser reconnect watchdog that quarantines stale commands, deduplicates replay, preserves tab affinity, and emits aggregate receipts. Recorded live evidence of the current failure mode.

**Biggest unknown:** Whether the owner wants browser recovery to auto-replay only read-only/reversible commands or to quarantine everything until explicit review; the pending 9 commands also need an owner-visible inspection before any cleanup.

