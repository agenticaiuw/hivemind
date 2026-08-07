# Harness derivation — faculty-perception — round 57

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-bridge-state-2026-08-07T12:03Z** — The Mac agent reports the home-chrome browser extension offline, with 5 pending browser commands; the browser has no online device or active tab connection at observation time.
  - evidence: GET /ops/status at 2026-08-07T12:03:09Z: agent.browserExtension.online=false, devices[0].online=false, pendingCommands=5; GET /browser/status independently reports online=false and pendingCommands=5.
- **relay-mac-bridge-health-2026-08-07T12:03Z** — The local Mac agent and Cloudflare relay are reachable, and the relay says macBridgeOnline=true, while the browser extension alone is offline; this is a partial-fleet outage rather than total connectivity loss.
  - evidence: GET /ops/status at 2026-08-07T12:03:09Z: relay.reachable=true, relay.payload.macBridgeOnline=true, browser.online=false; devices lists home-macbook-bridge online.
- **audio-rate-mismatch-observed-2026-08-07T12:00Z** — A completed realtime pendant run reported uploaded input telemetry as pcm-s16le, mono, 15,625 Hz, 937,500 bytes, while the same pipeline's rendered response was 24,000 Hz mono PCM. The system is therefore not end-to-end 24 kHz on this observed input path.
  - evidence: GET /pipeline at 2026-08-07T12:03Z, run job_165a9c9a-e5e3-4e29-b500-2fad63115ab9 event meta.inputTelemetry: sampleRate=15625, format=pcm-s16le, channels=1; separate completed run job_309f5663... TTS event meta: sampleRate=24000, channels=1.

## Capabilities it proposed

### "“If my browser is disconnected, tell me what is waiting, keep safe reads queued, and never let a stale browser action silently run when it reconnects.”"
- **useful because:** Today the Mac and relay can be healthy while the browser extension is offline with five pending commands. The owner needs an honest, wearable-visible distinction between completed, queued, expired, and replayable work—especially to prevent a delayed form submission or message from executing out of context.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Cheaper background classifier for command safety/expiry; realtime only for the owner's brief spoken status and confirmation; deterministic relay/bridge state machine for replay and deduplication.
- **latency:** Immediate queue status from cached state (<300 ms spoken start); reconnect reconciliation within one heartbeat (target <5 s); mutations remain paused until explicit confirmation.
- **cost:** Low API cost: mostly deterministic status and hashes; roughly $0.001–$0.01 per reconnect batch if an LLM is needed to classify ambiguous commands, dominated by page re-read tokens.
- **security:** Queued commands may contain private URLs or form data. Keep payloads local/relay-encrypted, redact them from voice and logs, expire commands by TTL and tab/session identity, and require confirmation for all writes, sends, purchases, or submissions. Never infer success from enqueue alone.
- **missing:** Durable command metadata with operation class (read/write), TTL, tab/session fingerprint, and replay policy; Reconnect-time reconciliation that invalidates stale mutations and deduplicates safe reads; Pendant notification/ack semantics for stranded browser work; A dashboard queue view with exact command status and reason

### "“When I come back after a connection drop, tell me exactly what I missed—not just what was generated: which reply or alert reached the pendant, how much was actually played, and which browser or Mac work never happened.”"
- **useful because:** Today the fleet can be partially alive: the relay and Mac bridge may be online while Chrome is disconnected, and a response can be rendered at 24 kHz even when capture arrived at another rate. The owner cannot reliably distinguish generated, delivered, heard, and executed. A compact spoken recovery report would prevent repeated requests, missed alerts, and false confidence about browser actions.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic event ledger and reconciliation first; use a cheaper background model only to summarize a batch of missed items. Reserve realtime for the owner's short 'what did I miss?' question.
- **latency:** Cached recovery summary should begin speaking in under 500 ms; full reconciliation can complete in under 10 seconds after reconnect. No network wait should block the pendant from reporting its last locally known state.
- **cost:** Usually under $0.005 per recovery report; the dominant cost is optional summarization of many event records, not telemetry.
- **security:** The ledger may reveal private speech, alert text, URLs, and action payloads. Store content hashes and minimal excerpts by default, encrypt detailed records, apply short retention, and require confirmation before retrying any action. Never claim 'heard' from a successful upload or 'done' from queue insertion.
- **missing:** A durable per-response delivery ledger linking relay job, PCM artifact, pendant download, playback start/stop/bytes consumed, and interruption reason; A browser-command outcome ledger that distinguishes queued, dispatched, page-applied, and verified result; Reconnect reconciliation and a pendant-readable compact summary format; Actual capture/playback sample-rate metadata at every boundary so quality warnings are truthful


## Changes it proposed to its own stack

### `browser-harness` — Add a reconnect reconciliation gate between the existing browser command queue and result/heartbeat routes. Persist for every pending command: read-vs-mutate class, creation/expiry time, originating tab URL/title hash, session id, and an idempotency key. When heartbeat returns after offline time, automatically replay only non-sensitive idempotent reads whose tab/session fingerprint still matches; mark writes, sends, and stale commands as held with an explicit reason. Emit typed queue-state events to /pipeline/events and surface the count/reasons in dashboard and pendant status. Enqueue must never be reported as completion.
- **owner gets:** A disconnected Chrome currently leaves five commands pending while the rest of the system is healthy. This prevents a delayed browser action from silently running later against a different page, while still letting harmless research recover without making the owner repeat it.
- effort: Medium: queue schema migration, deterministic classifier with an ambiguous=hold default, heartbeat reconciliation, idempotency ledger, and dashboard/pendant status plumbing; add crash/reconnect tests.  ·  risk: Misclassification could replay a mutation or unnecessarily hold a read. Default ambiguous commands to hold, require confirmation for any mutation, bind to tab/session fingerprints, and retain undo/cancel records. If reconciliation crashes, commands remain pending and can be retried idempotently.
- cost: Negligible storage and relay request overhead; occasional cheaper-model classification for ambiguous commands, ideally under $0.01 per reconnect batch.  ·  latency: Safe reads add at most one heartbeat round trip; mutations intentionally wait for owner confirmation. Queue status is available from local cached state.
- security: Reduces accidental delayed writes. Metadata still contains sensitive URLs and possibly payload references; encrypt at rest, redact payloads in logs/voice, and TTL-delete expired entries.
- depends on: Existing browser command IDs and result receipts; A durable idempotency ledger (the existing queue work needs this exposed to reconciliation); Pendant/dashboard status event consumer

### `integration` — Add an explicit audio-contract validator at relay↔Mac↔pendant boundaries. Every input and output artifact must carry sample rate, channel count, encoding, byte count, duration, and resampling history; reject or visibly label unexpected rates instead of silently accepting them. Emit a single run-level 'end-to-end audio contract' result (for example input 15.625 kHz → resampled 24 kHz output) into pipeline events and diagnostics.
- **owner gets:** The owner should know whether the pendant is actually receiving the intended audio quality. Today an observed realtime input was 15.625 kHz while output was 24 kHz; without an explicit contract, degraded capture can look like a successful 24 kHz session.
- effort: Small-to-medium: schema/event additions, validator at upload/download, one resampling policy, and regression fixtures for legacy 15.625 kHz input.  ·  risk: Strict rejection could interrupt calls from legacy firmware. Start in warn-and-label mode, preserve playback compatibility, then enforce only after fleet telemetry confirms upgraded senders.
- cost: Negligible compute/storage; resampling may add a few milliseconds and modest CPU on the Mac/relay.  ·  latency: <20 ms typical metadata/validation overhead; resampling latency depends on audio chunk size.
- security: No new data exposure; telemetry should contain format metadata only, not audio content.
- depends on: Authoritative pendant audio telemetry and continuity semantics; A single agreed 24 kHz input/output contract; Pipeline event schema accepting input and resampling metadata

### `context` — Create a cross-surface outcome ledger with four non-interchangeable proofs—generated, delivered-to-pendant, playback-consumed, and world-state-verified—and bind each proof to one correlation ID spanning relay pipeline events, audio artifacts, pendant acknowledgements, Mac jobs, and browser command results. The ledger should expose a compact 'missed since last contact' projection, while retaining detailed evidence only behind the dashboard. Unknown or missing proofs must remain unknown rather than being upgraded to success.
- **owner gets:** After a drop or partial outage, the owner gets an honest answer about what they actually heard and what actually changed, instead of a plausible but wrong success message. This is especially important when browser commands are stranded and audio ingress/egress formats differ.
- effort: Medium-high: define event/proof schema, add correlation propagation across relay and Mac bridge, implement pendant playback acknowledgements and browser verified-result ingestion, then build reconnect projection and retention rules.  ·  risk: Firmware loss or clock skew may leave gaps; represent gaps explicitly, use monotonic sequence numbers plus server timestamps, and make the system conservative. A ledger bug must never trigger automatic retries of writes; retries require a separate policy and confirmation.
- cost: Small persistent metadata overhead; detailed audio need not be stored, only hashes, byte ranges, timestamps, and failure codes. Optional summaries use a low-cost model.  ·  latency: Negligible on the live audio path if acknowledgements are asynchronous; reconnect summaries add a few hundred milliseconds from local cache and seconds only for remote reconciliation.
- security: Correlation IDs and hashes reduce content leakage, but URLs/action metadata remain sensitive. Encrypt records, redact spoken summaries, enforce per-owner access, and expire detailed evidence quickly.
- depends on: Pendant firmware playback-consumption acknowledgement; Relay durable event retention with correlation IDs; Mac/browser adapters that emit verified completion rather than enqueue success; A defined timezone/clock policy for human-readable missed-event ordering


## What it asked for

_Nothing._
## Its own summary

Established two fresh live truths and recorded them: (1) the browser extension is offline with exactly five pending commands while relay/Mac bridge remain online, proving a partial-fleet outage; (2) observed realtime input was 15,625 Hz while response output was 24 kHz, so the path is not end-to-end 24 kHz. Proposed a degraded-browser reconciliation gate that safely replays only fresh idempotent reads and holds stale/mutating work, and proposed explicit audio-contract validation/telemetry. No additional tool or permission request is needed this round; Accessibility/Screen Recording remains an owner-side constraint already documented.

**Biggest unknown:** The contents and operation classes of the five pending browser commands, and whether the current pendant firmware intentionally captures at 15,625 Hz or is being resampled before upload. Determining either requires authenticated queue inspection/pendant diagnostics not available to this agent.

