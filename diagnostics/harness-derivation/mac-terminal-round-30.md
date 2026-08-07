# Harness derivation — mac-terminal — round 30

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac agent readiness and cross-surface health** — The live Mac agent is running v0.5.0 with fullControlMode and relay reachability, but reports ready=false because Accessibility and Screen Recording are not granted; browser extension home-chrome is offline with two pending commands. Relay says macBridgeOnline=true.
  - evidence: GET /ops/snapshot returned status.agent.permissions.accessibility.trusted=false, screenRecording.granted=false, requiredMissing=[], ready=false; browser.online=false and pendingCommands=2; relay.reachable=true and macBridgeOnline=true.

## Capabilities it proposed

### "“Run a health check on the Mac and pendant, fix anything safe, and tell me what still needs me.”"
- **useful because:** Today the owner cannot get one truthful answer about the whole system: the Mac agent reports relay reachability, browser offline with two queued commands, missing Accessibility/Screen Recording, and full-control readiness in one snapshot, while pendant audio and relay health live elsewhere. A spoken diagnostic should correlate those states, perform only reversible repairs (reconnect bridge, retry stale queue, refresh machine context, restart a failed job), and leave permission or destructive issues as explicit owner tasks.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** background for collection and deterministic correlation; realtime only to ask a follow-up or speak the short result
- **latency:** Under 5 seconds for deterministic status; up to 30 seconds for one repair-and-recheck cycle
- **cost:** Typically <$0.01 per invocation; most calls are deterministic, with a small background summary only when several failures need prioritizing
- **security:** The Mac snapshot contains local paths, app inventory, permission state, and job metadata; relay must return redacted typed health facts rather than raw logs. Repairs must be allowlisted as reversible and idempotent; never alter files, send mail, or change permissions without an owner request.
- **missing:** A relay endpoint that aggregates pendant telemetry, Mac /ops/snapshot, and bridge heartbeat into one signed health report; Typed repair operations with idempotency keys and before/after receipts (reconnect, retry, refresh, cancel stale browser command); A pendant button/voice intent and concise spoken rendering of severity plus owner-required steps; A clear readiness model: distinguish 'agent process up' from 'permissions ready' and 'browser online'

### "“Show me exactly how that request moved through the pendant, relay, Mac, and browser, and point to the first thing that went wrong.”"
- **useful because:** Today the owner gets isolated job results and logs, not a single causal explanation spanning the spoken request, model routing, relay delivery, Mac execution, browser state, and spoken response. When something silently fails or produces the wrong result, they cannot tell whether the fault was recognition, planning, transport, stale browser state, a Mac permission, or synthesis. A voice-triggered causal replay would make the hive debuggable by the person wearing it, without requiring them to inspect developer logs.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic event correlation first; use a cheaper background model only to turn the correlated timeline into a short explanation. Realtime is unnecessary except for the owner's spoken query.
- **latency:** Return a first fault location in 2 seconds from indexed events; generate a detailed replay in under 15 seconds.
- **cost:** Usually under $0.01, dominated by a small background summarization call; correlation and redaction are local/deterministic.
- **security:** A replay may contain private speech transcripts, authenticated URLs, page text, file paths, and action parameters. Store event payloads encrypted with short retention, expose hashes and redacted excerpts by default, and require an explicit owner request to reveal sensitive fields. Never replay credentials or full page contents into speech.
- **missing:** A shared causality envelope propagated from pendant utterance through relay, model calls, Mac jobs, browser commands, and TTS, with parent/child IDs and monotonic timestamps; An append-only, encrypted event index on the relay and Mac that records outcomes, retries, routing decisions, and permission failures without raw secrets; A cross-surface redaction and evidence API that can return the first divergent event plus bounded excerpts; A dashboard and concise pendant rendering for timeline, confidence, and 'show more' drill-down


## Changes it proposed to its own stack

### `firmware` — Add an end-to-end 24 kHz audio negotiation and validation protocol: the relay advertises codec/rate/frame parameters, the pendant acknowledges them, and every stream begins with a short loopback/test-vector exchange carrying sequence numbers, CRC, encode/decode timing, underrun counters, and resampler mode. Persist only the last health counters and negotiated profile; automatically fall back to the existing 16 kHz uplink/24 kHz downlink profile when the 24 kHz path misses its latency budget.
- **owner gets:** The owner gets genuinely consistent wideband playback instead of silently hearing a degraded or glitchy stream. When it fails, the pendant can say whether the cause was network loss, relay transcoding, decoder CPU saturation, or the Mac TTS path, rather than making the owner debug three machines.
- effort: Medium: shared protocol fields in relay and Mac bridge, a small fixed-point test vector in firmware, and telemetry/receipt display in the dashboard; validate on the current nRF9160 DK before selecting product silicon.  ·  risk: A negotiation bug could leave the pendant silent or produce incompatible frames. Keep the current profile as a versioned fallback, require a timeout before switching, and make the test-vector path run before user audio only.
- cost: Negligible API cost; roughly 2–4 KB flash and under 2 KB RAM for counters/test buffers on the pendant. Test packets add a few hundred bytes per session.  ·  latency: Adds approximately 100–250 ms once per session for validation; steady-state target remains 60 ms frames, with fallback if decode plus encode exceeds the observed ~87% single-core combined load.
- security: Telemetry should contain counters and negotiated formats only, not audio content. Authenticate the profile exchange with the existing paired relay/session identity.
- depends on: A relay telemetry schema and dashboard view for negotiated audio profiles; A Mac bridge receipt path that records TTS sample rate and resampling decisions; The owner's requested 24 kHz superwideband path being enabled in the production audio pipeline

### `relay` — Introduce a cross-surface causality ledger with a signed trace envelope. Every pendant utterance, relay decision, model call, Mac job, browser command/result, retry, and TTS segment receives a trace ID, parent span ID, sequence number, monotonic duration, wall-clock estimate, actor, sensitivity label, and outcome. Mac and pendant buffer events while disconnected and reconcile them on reconnect; the relay detects duplicate or missing spans rather than presenting an apparently complete but false timeline.
- **owner gets:** When the system acts incorrectly or appears to ignore them, the owner can get a trustworthy answer about where it diverged instead of hearing a generic failure. It also makes cross-device handoff and recovery intelligible: the owner can see whether the Mac never received the request, the browser acted on stale state, or the response was generated but never played.
- effort: High: a shared envelope library, durable append-only storage and reconciliation, instrumentation in relay/Mac/browser/pendant paths, redaction, and dashboard queries. Start with one trace through voice → relay → Mac job → TTS.  ·  risk: Tracing can leak more personal data and create a second failure path. Keep payloads separate from metadata, encrypt sensitive attachments, bound per-trace size, degrade to metadata-only when storage is unavailable, and make correlation IDs opaque. Clock skew could misorder events, so use per-device monotonic clocks and mark wall-clock ordering as estimated.
- cost: Small storage and bandwidth overhead per event; no meaningful model cost for correlation. A background summarizer is optional and only invoked when the owner asks for a human explanation.  ·  latency: Sub-millisecond local event creation and a few milliseconds per relay write when online; disconnected buffering avoids adding network latency to voice execution.
- security: Improves auditability but expands the sensitive metadata surface. Encrypt at rest and in transit, apply short retention, redact transcripts/URLs/paths by default, and enforce owner-scoped trace access.
- depends on: A common trace-envelope schema adopted by pendant firmware, Cloudflare relay, Mac bridge, and browser extension; Durable encrypted event storage and reconnect reconciliation; A redaction-aware trace query API and dashboard/pendant presentation


## What it asked for

_Nothing._
