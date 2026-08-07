# Harness derivation — faculty-perception — round 54

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-observation** — At 2026-08-07T11:55:07Z /observe is read-only and reachable, but UI input is not trustworthy: accessibility.trusted=false, screenRecording=false, inputReachability.status=failed, and uiActionsWillReachTheScreen=false. The running binary is com.aipendant.agent at /Users/evanliu/Applications/AI Pendant Agent.app/Contents/Resources/node; macOS reports permission granted to a different binary.
  - evidence: GET /observe HTTP 200 response: accessibility trusted false; eventsPost false; inputReachability failed; consequence says ui_click/type_text/press_keys report success while doing nothing.
- **browser-observation** — At 2026-08-07T11:55:07Z Chrome browser extension home-chrome is offline with no active tab identity and 5 pending commands. The Mac bridge itself is online, so browser reachability—not Mac reachability—is the current blocker for browser-grounded perception.
  - evidence: GET /browser/status HTTP 200: online=false, tabId=null, tabUrl='', pendingCommands=5; GET /ops/status reports macBridgeOnline=true.
- **cross-surface-reality** — At 2026-08-07T11:55Z the relay/Mac pipeline contains a completed 24 kHz TTS response and pendant offline-store alert-delivery events, while browser execution jobs explicitly failed because the extension was offline. Browser session records are stale (last used 05:40–06:26Z) and cannot be treated as current page state.
  - evidence: GET /pipeline shows 24,000 Hz mono PCM response and nrf9160 held-alert events; GET /jobs shows browser_read_page and browser_navigate failures with reason extension offline; GET /browser/sessions shows stale lastUsedAt values.

## Capabilities it proposed

### "“Did that actually happen?” Give me a trustworthy answer by checking the pendant/relay receipt, Mac observation, and the exact browser tab or app state—otherwise say ‘unknown’ instead of guessing."
- **useful because:** Today action receipts can report success while macOS drops synthetic input, and browser commands can remain pending after the extension goes offline. A cross-surface witness lets the owner distinguish confirmed, contradicted, stale, and unknown outcomes before relying on them.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use deterministic perception and receipt reconciliation first; use the cheaper background/text tier to summarize evidence, reserving realtime only for the owner's live spoken question.
- **latency:** 2–5 seconds for a fresh Mac/browser check; immediate when a recent pendant/relay receipt is already available. If a surface is offline, return unknown within 500 ms rather than waiting indefinitely.
- **cost:** Usually <$0.01 per check when deterministic route reads suffice; occasional text summarization is the dominant cost. No vision upload unless the owner explicitly permits it.
- **security:** Private browser URLs and Mac UI evidence must stay on the local bridge; relay should receive only hashes, status, timestamps, and redacted snippets. Never claim confirmation from a queued command. Require owner confirmation before any corrective action.
- **missing:** A first-class stateWitnessId with checkedAt, expiry, source provenance, and confidence; Monotonic session/tab epochs so stale browser observations cannot be mistaken for current state; Explicit post-dispatch unknown classification and reconciliation endpoint; Working Accessibility and Screen Recording permissions for the exact running AI Pendant Agent binary; Online browser extension heartbeat and a way to drain or invalidate the 5 pending commands

### "“When I come back online, tell me exactly what happened while I was away—including what the pendant heard or held, what the Mac/browser changed, what was attempted, and where the timeline has gaps.”"
- **useful because:** The owner currently receives isolated late alerts, job receipts, and stale browser/session records, but cannot obtain one causal, time-ordered account of an offline interval. This would let them recover confidently from a dropped connection without confusing queued delivery, attempted work, and verified real-world changes.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → faculty-perception → faculty-judgement
- **model tier:** Use deterministic event-log joining and timestamp normalization first; use a cheap background text model only to compress the verified timeline into speech. Realtime is needed only if the owner asks live while reconnecting.
- **latency:** Generate incrementally during reconnection; deliver a first concise account within 2 seconds and expand to detail on request. No waiting for an unavailable surface: mark its interval as a gap.
- **cost:** Near-zero API cost for event joining; under $0.01 for optional natural-language compression. Storage and retention indexing dominate, not inference.
- **security:** The timeline may contain private browser URLs, audio metadata, and Mac activity. Keep raw events on the local Mac/pendant stores, send the relay only encrypted event IDs and redacted summaries, apply short retention, and require explicit opt-in before including microphone content or private-page text.
- **missing:** A durable cross-device event ledger with a shared clock model and source sequence numbers; A pendant reconnect handshake that exports held-event ranges with acknowledgements and detects missing ranges; Mac and browser adapters that emit state-change events (not merely action receipts), including tab/session epochs and offline intervals; A causal joiner that distinguishes queued, delivered, attempted, failed, and externally verified events; A user-facing timeline renderer and spoken drill-down controls

### "“For the last thing I asked, show me exactly what left my devices, which model or service saw it, what was retained, and what never left.”"
- **useful because:** A wearable voice system crosses pendant, relay, Mac, and private browser sessions, yet the owner cannot presently audit the actual data boundary of one interaction. A per-interaction egress receipt would make the system trustworthy: audio, transcript, screenshots, URLs, and action results are separately accounted for rather than hidden behind a generic success message.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → unified → faculty-perception
- **model tier:** Generate the ledger deterministically from transport and storage hooks; use no model for classification. A cheap text model may explain the receipt, while realtime only reads it aloud on request.
- **latency:** Attach the receipt during each interaction and make it queryable immediately after completion; explanation under 1 second from stored records.
- **cost:** Negligible inference cost. Small local/relay metadata writes per event; optional encrypted retention-index storage is the main cost.
- **security:** The audit itself can reveal sensitive URLs and content. Encrypt it per owner, redact payloads by default, retain hashes and byte counts unless expanded by explicit confirmation, and never transmit the audit to a third party merely to explain it.
- **missing:** End-to-end egress instrumentation at pendant radio, relay upload, Mac planner, vision upload, browser bridge, TTS, and durable stores; A tamper-evident per-interaction data receipt linking each payload to destination, model, purpose, retention TTL, and deletion status; A deletion verifier that can prove when relay/audio objects and local temporary files are gone; Owner controls for redaction and retention before an interaction starts


## Changes it proposed to its own stack

### `integration` — Add a cross-surface State Witness ledger between perception, judgement, and action. Every observation/action receipt gets a stable witnessId, source (pendant/relay/Mac/browser), checkedAt, expiresAt, monotonic surface epoch, tabId/sessionId or app identity, and a typed status: confirmed, contradicted, stale, unavailable, or unknown-after-dispatch. The ledger must invalidate browser witnesses when the extension heartbeat/session epoch changes, and must refuse to upgrade an action receipt from ‘accepted/queued’ to ‘completed’ without a fresh observation matching the expected postcondition. Expose a read-only aggregate endpoint consumed by faculty-judgement and faculty-action.
- **owner gets:** The owner stops hearing false success when UI automation did nothing or a browser command is stranded offline. They get a concise, evidence-linked answer—or an honest unknown—and can safely retry only when the evidence supports it.
- effort: Medium: typed schema plus append-only local journal, adapters for /observe, /ops/status, /browser/status, /browser/result/:commandId, /jobs/:jobId/receipts, and /pipeline; integration tests for stale epochs, contradictory observations, offline dispatch, and restart recovery.  ·  risk: Incorrect postcondition matching could mark a real action unknown or cause needless retries. Default to unknown, retain raw evidence references, and provide a human-visible evidence trail; never auto-retry irreversible actions.
- cost: Negligible storage and CPU locally; text summarization only when presenting a witness. No additional API cost for deterministic reconciliation.  ·  latency: Sub-100 ms for existing evidence; 2–5 seconds when a fresh Mac/browser observation is required. Offline surfaces fail fast as unavailable.
- security: Keep screenshots, DOM, and private content local; relay receives opaque witness IDs and redacted status only. Enforce per-session access and TTL deletion.
- depends on: Repair TCC for the exact running com.aipendant.agent app and node executable; currently /observe reports trusted=false and inputReachability failed.; Bring home-chrome online and define invalidation/drain behavior for its 5 pending commands.; Define expected postcondition schemas for common Mac and browser action types.


## What it asked for

_Nothing._
## Its own summary

Fresh discovery completed. Mac observation, ops, browser status, sessions, pipeline, and jobs are reachable. The key truth is unchanged despite the claimed grants: /observe reports accessibility trusted=false, screenRecording=false, inputReachability=failed, and uiActionsWillReachTheScreen=false for the exact running com.aipendant.agent binary. home-chrome is offline with tabId null and 5 pending commands; its stored sessions are stale. Relay/Mac audio and pendant held-alert telemetry are working, but browser actions explicitly fail offline. I recorded these facts, informed faculty-action and faculty-judgement, and proposed a State Witness ledger that binds evidence to epochs/expiry and classifies post-dispatch outcomes as unknown unless a fresh postcondition is observed.

**Biggest unknown:** Whether the orchestrator can actually repair macOS TCC for the running AI Pendant Agent executable and bring the browser extension online. Until both are verified by fresh probes, GUI actions and private browser state are not observable or trustworthy.

