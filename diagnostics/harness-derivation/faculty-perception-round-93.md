# Harness derivation — faculty-perception — round 93

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-device-presence** — As of 2026-08-07T13:59Z, reachable devices are home-macbook-bridge online, home-chrome offline, and cloudflare-contract-test mobile offline; no pendant is registered.
  - evidence: GET /ops/status payload lists relay macBridgeOnline=true and device discovery lists only those three devices.
- **mac-input-reachability** — The running AI Pendant Agent cannot post synthesized UI events: Accessibility trusted=false, Screen Recording granted=false, inputReachability.status=failed, and uiActionsWillReachTheScreen=false. AppleScript automation grants are present and ops requiredMissing is empty, but permissions.ready=false.
  - evidence: GET /ops/status and GET /observe at 2026-08-07T13:59Z.
- **browser-live-state** — Browser bridge is offline with 9 pending commands and three durable sessions/tabs visible in observation; commands cannot currently be delivered to Chrome.
  - evidence: GET /browser/status and GET /observe.
- **pipeline-audio-history** — Pipeline contains historical relay/nRF9160 records despite no live pendant; one completed response rendered 24 kHz mono PCM (75,734 bytes, 1,578 ms) and relay accepted it, while another nRF9160 alert-delivery record is processing. These are records, not proof of current playback or device receipt.
  - evidence: GET /pipeline and device discovery at same observation window.

## Capabilities it proposed

### "“Did that actually reach me, or is it just queued somewhere?”"
- **useful because:** Today the system can report a relay-accepted PCM payload or a historical nRF9160 event as if delivery were real. A cross-surface delivery truth report would distinguish generated, uploaded, relay-accepted, pendant-received, playback-started, and playback-completed, call out stale/contradictory records, and never claim the owner heard something without a device acknowledgement.
- **path:** pendant → relay → mac-planner → dashboard → unified
- **model tier:** background for reconciliation and routine monitoring; realtime only to answer a live spoken query against the already-computed ledger
- **latency:** Live answer under 2 seconds from cached ledger; reconcile asynchronously within 30 seconds of each event or reconnect
- **cost:** Usually <$0.01 per reconciliation using a cheap model or no model (typed state reduction dominates); realtime query cost only when the owner asks conversationally
- **security:** Audio metadata and delivery receipts leave the Mac for relay correlation; retain hashes/byte counts rather than audio by default, expire receipts, and require confirmation before exposing transcript or audio content. Never infer hearing from relay acceptance.
- **missing:** Pendant firmware must emit authenticated receive/start/finish acknowledgements with monotonic sequence, device boot/session id, and local timestamp, including offline-store replay markers; Relay needs an append-only, idempotent delivery ledger and an explicit distinction between accepted, delivered-to-device, and acknowledged playback; Mac bridge needs to attach pipelineId/jobId to generated audio and upload responses, and surface stale records as historical; Dashboard needs a contradiction/staleness view and a plain-language status endpoint/tool

### "“Before you tell me what to do, show me exactly what you can currently observe and what you’re only inferring.”"
- **useful because:** The owner cannot today inspect the evidence behind the hive mind’s beliefs. This would produce a compact, spoken-or-dashboard perception card: live observations, stale observations, unavailable surfaces, inference boundaries, timestamps, and source links. It lets the owner catch a mistaken assumption before it turns into an action, without exposing hidden chain-of-thought.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard → unified
- **model tier:** No expensive model for collection or freshness checks; use a cheap background model only to verbalize the typed evidence card, and realtime only when the owner asks for it aloud.
- **latency:** Cached card available in under 500 ms; refresh reachable surfaces within 5 seconds; spoken rendering under 2 seconds after the question.
- **cost:** Near-zero for typed collection; typically <$0.01 for optional short verbalization. The main cost is bounded metadata storage, not inference.
- **security:** Evidence may contain private URLs, calendar titles, and app state. Redact secrets and sensitive content by policy, show source class and redacted excerpts by default, and require an explicit tap/press to reveal private page text. Never include hidden reasoning or credentials.
- **missing:** A shared evidence-card schema with observation/inference/unavailable types, source, observedAt, freshness, confidence, and causal links; Every surface must publish a signed, machine-readable observation snapshot rather than only prose or action receipts; A relay endpoint to request and merge snapshots from the Mac, browser, and pendant, with redaction performed before storage; A pendant/dashboard renderer that can show provenance on demand and distinguish 'not observed' from 'observed false'

### "“If I miss something while I’m away from my Mac, tell me what happened without recording the room.”"
- **useful because:** A wearable-local event journal would detect a small, owner-chosen vocabulary of events (doorbell, timer, smoke alarm, my name, or a meeting-room cue), preserve only event labels and confidence, and later correlate them with Mac/browser state. Today no node can answer what was perceptually present during a disconnected interval without retaining raw audio or inventing a story.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** A tiny on-device classifier for the fixed vocabulary; background relay correlation and a cheap model for summarization. Realtime is unnecessary unless the owner asks live.
- **latency:** Local event label within 300 ms; offline storage immediate; post-reconnect correlation under 10 seconds.
- **cost:** No per-event API cost when classified locally; occasional <$0.01 background summary. Firmware flash/RAM and battery are the dominant costs.
- **security:** Raw audio must never leave the pendant for this mode. Store only label, confidence, monotonic time, and a short rolling sequence number; make categories opt-in, visibly enabled, and easy to erase. High-risk labels such as smoke alarm should be surfaced as detected—not asserted fact—until corroborated.
- **missing:** A firmware keyword/event classifier and a privacy mode that guarantees raw PCM is discarded; A durable offline event journal with authenticated sequence numbers and replay de-duplication; Relay support for delayed event batches and explicit offline/online provenance; Mac/browser correlation adapters for calendar, active calls, timers, and authenticated notification state; Owner-facing controls for vocabulary, sensitivity, retention, and confidence thresholds


## Changes it proposed to its own stack

### `context` — Add a typed reality ledger/reconciler between pipeline, relay receipts, device registry, and observation. Each fact carries source, observedAt, freshness TTL, causal ids, and confidence; contradictory claims (for example relay accepted vs no pendant registered) are retained as a contradiction, not flattened. Expose a read-only /reality endpoint and inject only the compact relevant slice into judgement/action prompts.
- **owner gets:** The owner gets honest answers about what is happening now instead of confident reports based on stale audio history, offline browser state, or UI actions that did nothing.
- effort: Medium: schema plus event adapters in Mac agent/relay, a small reconciler, tests for stale and out-of-order events, and dashboard rendering.  ·  risk: Incorrect correlation could mark a real delivery as failed or vice versa; recover by retaining raw events, making the ledger advisory/read-only, and allowing explicit re-reconciliation when a device reconnects.
- cost: Negligible storage for metadata; no model cost for typed reconciliation. Optional cheap summarizer only for human-readable explanations.  ·  latency: Sub-second local reads; asynchronous updates on event ingestion. No added latency to action execution.
- security: Improves provenance. Store identifiers, hashes, sizes, and timestamps by default; avoid copying private audio/transcripts into the ledger.
- depends on: Pendant registration and authenticated playback acknowledgements; Relay idempotent receipt semantics; Mac pipeline events carrying stable job/pipeline identifiers


## What it asked for

_Nothing._
## Its own summary

Fresh observation completed. At 2026-08-07T13:59Z the Mac bridge is online, but no pendant is registered; Chrome bridge is offline with 9 queued commands. The Mac agent's Accessibility and Screen Recording are still false, and /observe explicitly says UI actions report success while doing nothing, so GUI receipts are untrustworthy. Pipeline data includes historical 24 kHz audio and nRF9160 events, but cannot establish current playback. I recorded these facts and proposed a cross-node delivery-truth/reality ledger that refuses to equate relay acceptance with the owner hearing audio.

**Biggest unknown:** Whether a physical pendant can currently receive or play anything remains unknowable until one registers and emits authenticated receive/playback acknowledgements. For GUI actions, the remaining prerequisite is the owner granting Accessibility and Screen Recording to the exact AI Pendant Agent binary; no further internal tool can grant that.

