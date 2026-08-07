# Harness derivation — mac-planner — round 124

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-reconnect-risk** — The browser bridge is currently offline with 9 pending commands and no active tab/session identity; do not dispatch additional browser work until a heartbeat/reconnect reconciliation exists.
  - evidence: GET /browser/status returned online=false, home-chrome offline, tabId/windowId null, pendingCommands=9; browser-extension independently reported Safari absent and stale sessions.
- **mac-readiness** — Mac bridge and relay are reachable, but computer-use is disabled and TCC accessibility/screen recording are missing; AppleScript automation grants are present. The newly granted inspection/source tools remain schemas without implementations.
  - evidence: GET /ops/snapshot: macBridgeOnline=true, loopEnabled=false, accessibility.trusted=false, screenRecording.granted=false, automation grants cached; describe(mac_readonly_inspect) and describe(mac_read_sources) say schema only.

## Capabilities it proposed

### "When my browser reconnects after being offline, reconcile anything queued while it was away: discard stale or duplicate commands, resume only safe read-only work, and leave me a concise pendant/Mac review showing what was skipped, resumed, or needs me."
- **useful because:** The browser is currently offline with 9 pending commands and stale sessions. Blind replay can repeat navigation or mutations; permanent blockage loses useful work. This makes outages recoverable without silently acting in a logged-in account, and joins the pendant’s alert, relay’s durable state, and Mac’s receipts.
- **path:** browser-extension → relay-realtime → mac-planner → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** background for reconnect reconciliation and summaries; deterministic rules for TTL, idempotency, read-only classification, and duplicate suppression; realtime only to notify the wearer when a decision is needed.
- **latency:** On extension heartbeat/reconnect: under 2 seconds for queue classification, under 10 seconds for a review capsule; no polling while offline.
- **cost:** Usually near-zero model cost for deterministic queue handling; roughly 2k–4k input tokens and under 200 output tokens only when ambiguous commands require a background summary.
- **security:** Never replay mutations, form submissions, sends, or clicks solely because connectivity returned. Bind every item to extensionId/session/tab and an expiry; redact page contents in the relay summary; require explicit owner confirmation for anything not provably read-only. Persist only hashes, status, and receipts unless the owner asks for details.
- **missing:** A reconnect reconciliation worker that atomically leases pending commands and marks stale/duplicate/resume-needed; A typed command risk/idempotency declaration and per-command TTL; An extension reconnect handshake carrying session/tab incarnation, not just extensionId; A pendant/Mac review capsule route and receipt linkage

### "Don’t interrupt me while I’m presenting, on a call, or actively typing; quietly queue important results, then give me a short pendant summary when I become available, with urgent exceptions only."
- **useful because:** A voice-first assistant can be disruptive even when its work is correct. Combining pendant interaction state, Mac foreground/activity signals, Calendar meeting context, and relay durability can make delivery attentive rather than merely immediate. No single surface knows all of those signals.
- **path:** pendant → relay-realtime → mac-planner → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Deterministic policy for interruption windows, urgency, quiet hours, and queue coalescing; background model only to compress several completed receipts into a brief. Realtime reserved for the actual urgent notification or owner conversation.
- **latency:** Classify delivery in under 100 ms when a result arrives; reevaluate on each heartbeat or Mac state change; flush a normal digest within 30 seconds after availability.
- **cost:** Near-zero for policy and receipt grouping; under 1k background input tokens per digest, dominated by existing result generation rather than this feature.
- **security:** Activity state should be coarse (available/busy/in-call/presenting), not raw keystrokes or screen contents. Calendar titles and app names must be redacted by default. Urgent exceptions need an explicit configurable allowlist. Queue items should expire and be deletable from pendant/dashboard.
- **missing:** A shared attention-state contract with source, timestamp, confidence, and expiry; A Mac read-only activity signal that works without Accessibility where possible (foreground app, active audio/call/presentation heuristics); Relay-side durable delivery queue with urgency and coalescing semantics; Pendant acknowledgement/availability event and a small dashboard control for quiet mode

### "When I speak an instruction while the pendant has no connection, keep the useful intent locally, then finish it later when the relay and Mac are reachable—without saving the raw recording—and tell me exactly what was completed or still needs my decision."
- **useful because:** Today a dropped link turns a spoken request into lost work or an opaque failure. A portable, privacy-preserving intent capsule would let the owner rely on the pendant for capture, the relay for eventual coordination, and the Mac/browser for execution even across outages. This is distinct from ordinary queued jobs: it preserves the owner’s intent and required context, not merely an already-created server command.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Pendant firmware performs only bounded local capture and confirmation; relay uses a cheap background model to normalize an intent capsule after reconnection; planner/action models are invoked only when execution requires them. Realtime is used only if the owner reconnects and asks for immediate clarification.
- **latency:** Local capture acknowledgement under 300 ms offline. Sync and normalization within 10 seconds after reconnect; execution timing depends on the requested task. Never block the pendant on server availability.
- **cost:** No API cost while offline. On reconnection, typically 1k–3k background input tokens for normalization; execution cost is the same as the eventual task and should not be paid twice after retries.
- **security:** Do not retain raw audio. Store a small encrypted intent capsule with transcript confidence, timestamp, expiry, and a user-visible review state. Sensitive intents must remain local until connectivity returns. Never execute an irreversible action from an ambiguous capsule; ask through the pendant or leave a review item. Provide local delete/cancel before sync.
- **missing:** Pendant firmware skill for encrypted offline intent capsules, retry metadata, and a cancel gesture; Relay endpoint and durable store for idempotent capsule upload, normalization, and conflict resolution; A planner contract that distinguishes captured intent from authorized execution and exposes missing context; Mac/browser executors that accept a capsule correlation ID and return durable receipts; A pendant-visible completion/failure queue that survives multiple reconnects

### "Use my private Mac and logged-in browser data to answer questions or prepare work, but send the smallest possible redacted facts to the cloud and show me what left my devices afterward."
- **useful because:** The current system can reach private Calendar, Mail, files, and authenticated tabs, but lacks a cross-surface data-minimization boundary. This would let the owner use powerful cloud reasoning without treating raw mail, page contents, or account sessions as ordinary prompt context.
- **path:** mac-planner → browser-extension → relay-realtime → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Deterministic local extraction, field classification, redaction, and token budgeting first; a background model reasons over the minimized packet. Realtime is reserved for the final spoken answer, not raw private-source processing.
- **latency:** Local minimization under 1 second for ordinary source reads; background answer within 10 seconds. If a source cannot be safely minimized, return a local-only result or ask the owner rather than uploading it.
- **cost:** Adds negligible deterministic compute; usually reduces model input tokens by 50–90%. A typical request should use 1k–4k minimized tokens instead of full source bodies.
- **security:** Raw source contents and authentication material must remain on the Mac/browser. Every outgoing field needs provenance, sensitivity label, purpose, TTL, and redaction reason. The owner must be able to inspect, revoke, and delete the minimized packet. Never infer that a secret, full message body, or account identifier is safe merely because a task is convenient.
- **missing:** A local privacy broker shared by Mac and browser that extracts purpose-limited fields before relay upload; A typed minimized-context envelope with provenance, sensitivity, TTL, and deletion status; Relay enforcement that rejects raw source payloads and retains only approved envelopes; Dashboard/pedant disclosure of exactly which fields were shared and which stayed local; Planner prompts and tool contracts that can operate on redacted entities rather than requiring full page or message text


## What it asked for

_Nothing._
