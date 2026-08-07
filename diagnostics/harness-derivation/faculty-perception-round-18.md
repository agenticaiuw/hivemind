# Harness derivation — faculty-perception — round 18

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-input-reachability** — Mac agent observation currently reports Accessibility untrusted and screen recording missing; synthesized UI events are not accepted from com.aipendant.agent, so ui_click/type/press receipts cannot be trusted. Browser extension is offline with 2 pending commands.
  - evidence: GET /observe at 2026-08-07T09:43:05Z and GET /browser/status: accessibility.trusted=false, eventsPost=false, uiActionsWillReachTheScreen=false, browser.online=false, pendingCommands=2.
- **audio-path-rate-mismatch** — Live pipeline telemetry shows a recent pendant uplink captured at 15,625 Hz and transcribed from audio-native realtime, while rendered downlink is 24,000 Hz mono PCM; the physical audio spec confirms capture is 15,625 Hz and Opus uplink nominally 16 kHz.
  - evidence: GET /pipeline event meta for relayJobId job_165a9c9a-e5e3-4e29-b500-2fad63115ab9: inputTelemetry.sampleRate=15625, and TTS done meta sampleRate=24000; get_hardware_spec(audio) confirms mic 15,625 Hz capture.

## Capabilities it proposed

### "“When I ask what happened, show me the complete, trustworthy timeline of my request—even if the pendant went offline, the browser was disconnected, or the Mac reported success incorrectly.”"
- **useful because:** Today the owner cannot distinguish an action that truly reached the screen from one that merely entered a queue or produced an optimistic receipt. This would give them an evidence-backed answer across disconnections, retries, delayed playback, and contradictory device reports, without requiring them to reproduce the failure.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → unified → dashboard
- **model tier:** Use deterministic event correlation and observation first; use a cheaper background text model only to summarize contradictions. Reserve realtime for the owner's live question, not reconstruction.
- **latency:** Immediate status from cached evidence in under 1 second; await reconnecting devices asynchronously and update the timeline. A final cross-device reconstruction may take several seconds.
- **cost:** Usually negligible model cost: compact event records and read-only probes dominate. Occasional summarization is roughly a few cents or less, depending on retained evidence volume.
- **security:** Timelines can expose private URLs, window titles, voice metadata, and action contents. Store redacted structured events by default, hash page/audio payloads rather than retaining them, enforce sensitivity and expiration policies, and require confirmation before revealing secret-bearing evidence.
- **missing:** A globally unique request/attempt ID propagated from pendant through relay, Mac, browser, and playback; An append-only event schema with source timestamps, monotonic device time, freshness, and evidence confidence; Independent read-only observation adapters for Mac input reachability, browser delivery, relay acceptance, and pendant playback completion; A reconciliation service that preserves contradictory executor receipts instead of treating them as ground truth; A dashboard and spoken-response formatter for partial states such as queued, delivered, started, completed, failed, and unverifiable

### "“Tell me, at any moment, what this system can currently hear, see, read, and send—and which device is doing each part.”"
- **useful because:** The owner cannot today get a truthful privacy state spanning the wearable microphone, LTE relay, Mac permissions, foreground application, browser sessions, and queued commands. A spoken privacy pulse would make unexpected recording, screen access, browser reach, or delayed uploads visible before they become a surprise.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → unified → dashboard
- **model tier:** Deterministic state collection and policy evaluation; a small background model may turn the structured result into plain language. Realtime is needed only when the owner asks verbally.
- **latency:** Under 2 seconds for a current snapshot, with explicit “unknown/stale” labels when a device is unreachable. No network action should be taken merely to answer the question.
- **cost:** Near-zero model cost; periodic signed state heartbeats and compact dashboard records are the main costs. A short spoken summary adds only ordinary TTS cost.
- **security:** The privacy report itself is sensitive because it reveals account access, URLs, permissions, and network state. Redact page contents and secrets, distinguish capability from actual use, retain snapshots briefly, and never claim a sensor is inactive without a fresh device attestation.
- **missing:** Signed, freshness-bounded sensor and capture-state heartbeats from the pendant; Relay telemetry describing whether audio is live, buffered, retained, or awaiting upload; Mac adapters for actual microphone, camera, screen-recording, Accessibility, and network-use state rather than grant-cache state alone; Browser extension reports of active tab, session scope, pending commands, and whether content has left the Mac; A shared privacy-state vocabulary distinguishing permitted, active, queued, uploaded, retained, and unknown

### "“Before I rely on it, run a harmless end-to-end check and tell me whether my pendant, relay, Mac, browser, and speaker can actually reach one another.”"
- **useful because:** Today there is no owner-visible way to separate a broken microphone, LTE link, relay queue, Mac permission, browser bridge, or playback path until a real request fails. A consented synthetic check would catch a split path before a meeting, urgent message, or hands-free task, without reading private pages or sending anything irreversible.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → unified → dashboard
- **model tier:** Deterministic diagnostic workflow with fixed test payloads; no expensive model call. Realtime only narrates the result if requested by voice.
- **latency:** 30–60 seconds for the complete test, with each stage reporting independently and a usable partial result if a device is offline.
- **cost:** A small LTE transfer and one short local audio loopback per test; effectively no model cost. Dashboard storage is a few kilobytes per run.
- **security:** Use generated tones and synthetic text, never the owner’s speech or page contents. Do not click, type, send, or alter browser state. Expire diagnostic artifacts quickly and mark every test payload unmistakably as synthetic.
- **missing:** A pendant diagnostic mode that emits and verifies a synthetic audio marker without recording private speech; Relay test-run endpoints with nonce, hop-by-hop acknowledgements, and no durable audio retention; Mac and browser no-op probes that verify reachability without UI mutation; Playback-start and playback-complete telemetry from the pendant; A compact owner-facing diagnostic report that distinguishes unavailable from failed


## Changes it proposed to its own stack

### `integration` — Add a cross-surface evidence reconciler and truth ledger. Every delegated action carries a correlation ID from pendant/relay through Mac and browser. After execution, a read-only observer gathers independent evidence (Mac /observe input reachability and foreground state, browser session/result state, relay job status, and pendant pipeline telemetry), compares it with the executor receipt, and records one of reached, verified, not-reached, or unknown with source timestamps and contradictions. Never rewrite the executor's receipt; expose the reconciliation separately to judgement and the owner.
- **owner gets:** The owner will stop hearing confident 'done' reports when Accessibility is actually broken, the browser is offline, or a response is merely queued on the pendant. They get a short, honest completion statement such as 'typed nowhere—Mac input was rejected' or 'rendered and accepted by relay, playback not yet observed,' with a path to retry.
- effort: Medium-high: correlation propagation in relay, Mac jobs, browser queue, and pendant event metadata; observer/reconciler service; dashboard and spoken receipt formatting; fixture tests for offline, duplicate, and contradictory evidence.  ·  risk: Observation can be stale or unavailable and may classify a genuinely completed action as unknown; preserve raw evidence, timestamps, and executor receipts, use bounded freshness windows, and allow later reconciliation when the browser or pendant reconnects. No action is blocked or altered by this layer.
- cost: Low per action: a few small JSON observations and D1/storage writes; no extra model call for routine reconciliation, with a cheap text model only when turning a contradiction into a human explanation.  ·  latency: Adds roughly 0.2–1.5 s for immediate Mac/browser checks; pendant and relay evidence can arrive asynchronously. Spoken response can say 'accepted, verification pending' rather than waiting for slow links.
- security: Evidence may include window titles, URLs, and action metadata; redact page contents and secrets, apply existing sensitivity/TTL rules, and require explicit owner consent before retaining screenshots or audio. Correlation IDs must be unguessable.
- depends on: A durable job/event correlation ID shared by pendant, relay, Mac, and browser; A typed observation schema with source, timestamp, freshness, and confidence; Browser heartbeat/result queue and pendant pipeline telemetry available to the observer; Existing receipt/undo records remain immutable and are linked, not replaced

### `hardware` — Add a small audio-front-end/clock-monitor path in the wearable revision: a shared crystal-derived sample clock for mic and speaker, a hardware loopback/reference tone switch, and monotonic sample-counter + packet-loss registers exposed over the existing UART/telemetry channel. Keep the nRF9160 for control, Opus, and LTE, but measure capture/playback clocks and link gaps at the source instead of inferring them from relay timestamps.
- **owner gets:** Calls will sound consistently natural instead of occasionally drifting, underrunning, or losing speech, and support can identify whether a bad call came from the microphone clock, modem contention, or speaker path without asking the owner to reproduce it.
- effort: High for the next wearable PCB/firmware revision: audio codec or clocked I2S front end, board layout, boot diagnostics, calibration procedure, and relay/dashboard visualization. Prototype can use an external codec or test board before committing to a product enclosure.  ·  risk: A new clock domain can introduce I2S synchronization bugs and RF/power noise; retain the current path as a fallback, gate loopback mode behind a diagnostic command, and fail closed to normal audio if counters are invalid.
- cost: Approximately $3–12 in additional codec/clock/test components at volume, plus modest PCB area; likely tens of milliwatts depending on codec. No per-call API cost; reduces expensive retranscription/debug sessions.  ·  latency: Negligible steady-state latency; hardware counters and loopback diagnostics are out-of-band. A calibration tone would be unavailable during ordinary calls.
- security: Counters and tones contain no speech; do not upload raw audio for diagnosis by default. If loopback captures samples, keep them local and require explicit consent for export.
- depends on: A defined 24 kHz end-to-end audio contract (capture, Opus, relay, playback); Firmware telemetry schema and durable pipeline event IDs; Electrical/audio validation on the current nRF9160 + ESP32 bridge before PCB freeze


## What it asked for

_Nothing._
