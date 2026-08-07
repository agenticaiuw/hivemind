# Harness derivation — faculty-perception — round 9

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac agent readiness** — Mac agent v0.5.0 is reachable and relay-connected, but reports ready=false because Accessibility is not trusted and Screen Recording permission is missing; requiredMissing is empty, optionalMissing empty. Computer-use loop is disabled and vision upload consent is false.
  - evidence: GET /ops/status returned 200: agent.ready=false; permissions.accessibility.trusted=false; permissions.screenRecording.granted=false; computerUse.loopEnabled=false; visionUploadConsented=false.
- **Browser bridge** — The only registered browser extension device is offline; it has no tab identity and there are 2 pending browser commands.
  - evidence: GET /browser/status returned online=false, device fanout-probe-cleanup online=false/tabId=null, pendingCommands=2.
- **Audio pipeline** — A recent completed relay job proves response rendering and relay upload at 24,000 Hz mono PCM (160.8 KiB, 3.43 s, no clipping), while its input telemetry was 15,625 Hz capture, 937,500 bytes PCM, and live LTE upload. The system is not yet end-to-end 24 kHz.
  - evidence: GET /pipeline returned job_165a9c9a... inputTelemetry.sampleRate=15625 and tts done meta sampleRate=24000, pcmBytes=164650, clippedSamples=0; relay_result accepted response.
- **Offline pendant behavior** — The pendant has successfully held and later surfaced offline events: 2 alerts and a moment bookmark were stored on microSD and delivered after connectivity returned; at least one cloud reply arrived late and was forwarded after reconnection.
  - evidence: GET /pipeline returned nrf9160 events alert_delivered detail 'Held alerts surfaced' meta storage=microSD/origin=pendant-offline-store; bookmark detail link_at_capture=down; cloud-relay reply text 'Confirmed: it arrived late and was forwarded after the connection came back.'
- **Pendant audio implementation** — Pendant audio is prototype: I2S capture is 15,625 Hz; Opus uplink is 16 kHz/16 kbps; playback decodes Opus at 24 kHz in 60 ms frames and resamples to 31,250 Hz I2S wire clock. Encode takes ~15 ms/call and simultaneous encode/decode consumes ~87% of one core.
  - evidence: get_hardware_spec(audio) reports source firmware/nrf9160/src/audio_opus.c and libopus 1.6.1 fixed-point measurements.
- **SD policy** — microSD is intended only as a failure buffer when a chunk upload cannot be uploaded, not as routine audio storage; exFAT is enabled.
  - evidence: get_hardware_spec(storage) owner policy and firmware config report.
- **Audio retention** — Relay retains audio in R2 for 30 days, but automated sweep is disabled and approximately 100 recordings are currently stored.
  - evidence: get_hardware_spec(stack) relay storage policy.

## Capabilities it proposed

### "“If I lose signal, keep my request and tell me when it was received, worked on, and finished.”"
- **useful because:** The pendant already stores bookmarks and alerts offline, and the relay can forward late replies, but the owner has no trustworthy end-to-end receipt. This would turn uncertain silence into a durable status: captured locally, uploaded, accepted, acted on, awaiting approval, or failed—with one concise spoken update when connectivity returns.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** gpt-5.6-luna for reconciliation and concise summaries; gpt-realtime-2.1 only for the live spoken acknowledgement; deterministic firmware/relay state transitions for receipts
- **latency:** Local capture acknowledgement under 300 ms; upload receipt on reconnection within one LTE transaction; Mac/browser execution in the background; spoken completion update on next connected session, not realtime unless already connected.
- **cost:** Usually <$0.01 per request when deterministic receipts and existing Mac jobs are used; model cost is dominated by one short reconciliation/summary, while audio upload and storage dominate bandwidth/storage.
- **security:** Requests and receipts may contain private speech and browser/account metadata. Encrypt queued payloads at rest on microSD and in relay storage, bind receipts to the paired pendant and Mac bridge, redact secrets from spoken/dashboard summaries, and require confirmation for sending mail, purchases, deletion, or other irreversible steps.
- **missing:** A shared durable receipt schema with monotonic event sequence and idempotency key across firmware, relay, Mac jobs, and browser commands; A reconnect reconciliation endpoint that can prove which offline events were accepted and which remain queued; Pendant-local status playback/UI for queued versus completed events; Dashboard and spoken-summary support for event timelines

### "“I was disconnected—tell me everything important that happened while I was away, and let me resume any unfinished thread.”"
- **useful because:** Today the pendant can surface individual held alerts and late replies, but the owner cannot get a trustworthy, deduplicated account of the entire disconnected interval across pendant events, relay jobs, Mac work, and logged-in browser changes. This would produce one time-bounded digest with source and status, then reopen a selected unfinished task with its prior context instead of making the owner reconstruct it.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Use deterministic event correlation and timestamps first; use a cheaper background text model to cluster and summarize the interval; reserve gpt-realtime-2.1 for the short spoken answer when the owner asks live.
- **latency:** On reconnect, reconcile metadata in under 2 seconds and make the digest available within 30 seconds; spoken answer should begin in under 1 second if a cached digest exists. Browser change inspection may continue in the background.
- **cost:** About $0.01–$0.05 per interval depending on event volume; model tokens for clustering/summarization dominate, while metadata storage is minor. Avoid reprocessing audio by referencing existing transcripts and hashes.
- **security:** The digest could expose private mail, calendar, or account activity over the pendant speaker. Keep raw details on the Mac/dashboard, speak only categories and urgency by default, require explicit expansion for account content, encrypt interval metadata, enforce browser-session permissions, and never perform resumed irreversible actions without confirmation.
- **missing:** A durable cross-surface event log with capture and completion timestamps, source, sensitivity, and deduplication identity; A reconnect interval API that can query pendant offline records, relay jobs, Mac receipts, and browser watch/session deltas consistently; A resumable-thread object linking a selected event to its transcript, plan, pending approvals, and browser tab/session; A privacy-aware spoken digest policy and dashboard review view


## Changes it proposed to its own stack

### `integration` — Create a cross-node delivery ledger for every pendant-originated request. The firmware assigns a monotonic request ID and stores a compact intent hash plus capture time/link state on microSD; relay appends authenticated received/forwarded/response-available events with idempotency; Mac maps the request ID to its job and receipts; browser commands inherit it and return before/after evidence. On reconnect, run a reconciliation exchange that is safe to repeat, marks gaps explicitly, and emits one owner-facing receipt rather than silently replaying or duplicating actions.
- **owner gets:** When the link drops, the owner will know whether a request was merely heard, actually delivered, completed, or still waiting—and will not get duplicate browser actions or a late answer with no context.
- effort: Medium-high: protocol/schema work across firmware, Worker/D1, Mac agent, and browser extension; migration for existing pipeline events; dashboard timeline and pendant status text/audio.  ·  risk: Schema mismatch or replay bugs could duplicate actions; mitigate with idempotency keys, action-level irreversible checkpoints, bounded queue TTL, signed sequence numbers, and a reconciliation test matrix covering power loss, LTE half-duplex interruption, Mac offline, and browser reconnect. Recover by preserving the original event and requiring manual review for ambiguous terminal state.
- cost: Negligible model cost; small D1/microSD metadata overhead (roughly hundreds of bytes per request plus retention policy). Existing audio storage remains the dominant cost unless receipts point to audio by reference.  ·  latency: Adds under 100 ms local ledger work and one small metadata exchange on reconnect; no added latency to already-connected speech.
- security: Improves auditability but creates a cross-surface activity trail. Encrypt sensitive intent hashes/metadata where possible, pair-bound authenticate all ledger writes, minimize spoken detail, and apply TTL/deletion controls.
- depends on: A stable pendant request identifier persisted across reboot; Existing pipeline/job receipt APIs exposed to the relay and Mac bridge; Browser command idempotency and tab/session affinity; A policy defining which terminal states require owner confirmation

### `hardware` — Replace the prototype nRF9160-DK audio path with a production two-processor audio design: retain the LTE-M modem, add a low-power audio MCU/DSP with native 24 kHz mono capture, 24 kHz playback, and hardware-assisted Opus/PCM buffering, connected over I2S/SPI; keep the ESP32 bridge for bench diagnostics only unless power measurements justify retaining it. Specify DMA ping-pong buffers, clock domains, and a modem/audio isolation protocol before PCB selection.
- **owner gets:** They get intelligible, stable superwideband speech in both directions instead of a 15.625 kHz microphone path that is resampled later and an application core already near saturation when encoding and decoding overlap. It also leaves modem stalls less likely to cause dropped audio.
- effort: High: audio latency/power measurements, schematic and PCB redesign, enclosure and battery validation, firmware transport protocol, RF coexistence, and a staged prototype against the existing DK.  ·  risk: More components, board area, firmware synchronization failures, and possible RF/audio EMI. Recover with a development interposer that can bypass the DSP, watchdog-isolated processors, PCM loopback tests, and an automatic fallback to narrowband/half-duplex mode. Do not claim 24 kHz until microphone, uplink, decode, I2S output, and measured acoustic response are all verified.
- cost: Rough prototype BOM increase ~$15–$40 (audio MCU/DSP, clock, power, PCB), with tens of mW additional active draw but potentially lower peak draw than pushing the nRF9160 app core (~87% combined codec load). Final cost depends on codec licensing and volume.  ·  latency: Can reduce codec scheduling jitter and keep 60 ms frame cadence deterministic; target <80 ms local capture/playback buffering, subject to LTE-M half-duplex airtime.
- security: Adds a processor and firmware image to secure/update; require signed firmware, isolated debug disable in production, no persistent raw audio outside the existing failure-buffer policy, and authenticated inter-processor messages.
- depends on: A measured end-to-end 24 kHz acceptance test and current nRF9160 RAM/CPU profile; Decision whether the ESP32 bridge remains in the product; Power/RF/EMI characterization under simultaneous LTE and audio load; A defined 24 kHz codec and microphone acoustic specification

### `context` — Introduce a causal, interval-based event fabric rather than isolated pipeline/job/browser histories. Every node emits append-only events carrying an owner-visible time interval, monotonic device sequence, causal parent, sensitivity class, and stable content hash; the relay reconciles clock uncertainty and duplicate delivery, while Mac and browser adapters translate local jobs and page deltas into the same graph. Materialize two views: 'what happened while disconnected' and 'resume this thread', with explicit unknown/gap markers when a source was unavailable.
- **owner gets:** After a dead zone, the owner can ask one question and receive a complete account with honest gaps, rather than hearing a few alerts while missing work completed on the Mac or changes in a logged-in page. They can continue the exact unfinished thread without repeating themselves.
- effort: High: event schema and causal correlation library, firmware and relay persistence, Mac/browser adapters, clock-skew handling, retention/sensitivity rules, dashboard timeline, and test fixtures for power loss and duplicate LTE delivery.  ·  risk: Incorrect correlation could merge unrelated requests or imply that an action completed when only a response was generated. Mitigate with conservative parent matching, immutable raw events, confidence labels, visible unknown states, and mandatory revalidation before resuming any external action. If the fabric fails, existing per-node histories remain authoritative.
- cost: Low incremental inference cost because correlation is deterministic; moderate D1/R2 metadata growth, bounded by interval retention and content hashes instead of duplicate audio/transcripts.  ·  latency: No impact on live audio when events are batched asynchronously; reconnect reconciliation adds a small metadata round trip and background summarization time.
- security: Creates a richer cross-device activity graph. Encrypt sensitive fields, store only hashes plus references where possible, enforce per-surface authorization, apply TTL by sensitivity, and keep spoken output redacted by default.
- depends on: Stable event identity and authenticated pairing on the pendant; Relay support for append-only metadata and clock/sequence reconciliation; Mac job receipts and browser page-delta adapters; Dashboard controls for viewing, deleting, and resuming an interval


## What it asked for

_Nothing._
## Its own summary

Established live facts: Mac agent v0.5.0 and relay are reachable, but Mac readiness is false because Accessibility and Screen Recording are missing; browser bridge is offline with two pending commands. The pipeline proves 24 kHz mono PCM output but 15,625 Hz capture/16 kHz uplink, so 24 kHz is not end-to-end. Pendant offline bookmarks/alerts are durably held on microSD and later surfaced, and late relay replies can arrive after reconnection. Recorded these facts and proposed a cross-node delivery ledger/reconciliation capability plus a production two-processor audio design to address the owner's real gaps.

**Biggest unknown:** The exact current firmware build and acceptance-test results for the 24 kHz path, plus whether the owner intends the ESP32 bridge in the production hardware. I still need those to distinguish a firmware-only fix from a board redesign; I did not re-ask the already-pending observability/status requests.

