# Harness derivation — faculty-perception — round 28

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent-readiness** — At 2026-08-07 live probe, Mac local agent is version 0.5.0 with full-control and LLM planner enabled, but not ready: Accessibility trusted=false and Screen Recording granted=false. Computer-use loop is disabled; vision model configured but vision upload consent false.
  - evidence: GET /ops/status HTTP 200: permissions.accessibility.trusted=false; permissions.screenRecording.granted=false; computerUse.loopEnabled=false, visionModelConfigured=true, visionUploadConsented=false; ready=false.
- **browser-connectivity** — The authenticated home Chrome bridge is currently offline, with no active tab and 3 pending browser commands; last seen 2026-08-07T09:21:08.821Z. Mac bridge and relay are online.
  - evidence: GET /browser/status and GET /ops/status HTTP 200: browser.online=false, tabCount 0/null, pendingCommands=3; relay reachable and macBridgeOnline=true.
- **audio-pipeline-observation** — Observed end-to-end output path is producing 24 kHz mono s16le PCM: a recent response rendered 164,650 bytes, 3,430 ms, 24,000 Hz, no clipping. The corresponding live input telemetry was 15,625 Hz PCM-s16le, 1 channel, 1,441 ms, 937,500 bytes, uploaded as PCM.
  - evidence: GET /pipeline HTTP 200, job_165a9c9a... events: inputTelemetry.sampleRate=15625; tts meta sampleRate=24000, pcmBytes=164650, clippedSamples=0.
- **timezone-consistency** — Timezone sources conflict: owner memory says America/Chicago, while live Mac /machine-context reports America/New_York. Do not use the Mac timezone as authoritative for owner-facing scheduling until reconciled.
  - evidence: discover(owner) remembered.timezone=America/Chicago; GET /machine-context HTTP 200 machine.timezone=America/New_York.
- **pendant-audio-hardware-contract** — The current prototype hardware captures mic audio at 15,625 Hz, Opus-encodes uplink at 16 kHz/16 kbps, and decodes playback at 24 kHz before resampling to a 31,250 Hz I2S wire clock. Thus 24 kHz currently describes playback output, not microphone capture bandwidth.
  - evidence: get_hardware_spec(audio): I2S mic 15,625 Hz; Opus uplink 16 kHz/16 kbps; playback decode 24 kHz/60 ms frames, resampled to 31,250 Hz I2S.

## Capabilities it proposed

### "“Before you do anything, tell me what you can actually see and what is unavailable right now.”"
- **useful because:** The owner currently receives confident answers despite contradictory timezone data, an offline browser with queued commands, and a Mac agent that lacks Accessibility/Screen Recording. This gives a short, cited readiness report so they know whether an answer is observed, stale, or impossible before an action or private-page request proceeds.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic probes and a cheap background summarizer; reserve realtime only for the spoken one-sentence rendering. No expensive model is needed to decide online/offline, permission, freshness, or conflicts.
- **latency:** Probe relay/Mac/browser in parallel and return within 1–2 seconds; cache only for display, never as proof. Pendant should say a concise result and offer detail on the dashboard.
- **cost:** Near-zero model cost for probes; roughly a few hundred tokens only when summarizing a conflict. Dominant cost is occasional relay/Mac network round trips.
- **security:** Do not include page contents, email, secrets, or screenshots in the default report. Return capability metadata, timestamps, permission states, queued-job counts, and source labels; require confirmation before probing private browser contents or uploading pixels.
- **missing:** A typed cross-surface perception snapshot schema with source timestamps, TTLs, confidence, and conflict fields; A relay endpoint that fans out authenticated readiness probes and returns one signed/cited snapshot; A browser heartbeat/queue policy that marks pending commands expired rather than leaving them apparently runnable; A dashboard/pendant rendering mode for observed vs stale vs unavailable facts

### "“I was offline—tell me what happened while I was away, in order, and what still needs me.”"
- **useful because:** Today the pendant can hold alerts and bookmarks, the relay can forward late responses, and the Mac/browser can have queued work, but the owner cannot receive one trustworthy causal account of the gap. A continuity digest would distinguish events that occurred, events merely queued, and events that expired or failed—then leave only the genuinely actionable items.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic event correlation and a cheap background summarizer to build the timeline; use the realtime tier only if the owner asks for the digest by voice and wants it spoken immediately.
- **latency:** On reconnection, ingest and deduplicate events within 5 seconds; spoken headline under 2 seconds from cached digest, with dashboard expansion for evidence and full chronology.
- **cost:** Low model cost: event normalization and hashes are deterministic, with a few hundred summary tokens per reconnect. Storage and event reconciliation dominate; no screenshot or page-content upload by default.
- **security:** Private browser/mail contents must stay on the Mac/browser boundary unless explicitly requested. The relay should carry event IDs, timestamps, outcome classes, and redacted summaries. Never infer that a queued action happened; show source, freshness, and an explicit unknown state. Require confirmation before replaying any action.
- **missing:** A shared append-only continuity event envelope accepted by pendant firmware, relay, Mac jobs, and browser commands; A durable correlation/causal-ID scheme linking offline bookmarks, held alerts, relay responses, Mac jobs, and browser queue entries without duplicating events; A reconnect reconciliation service that classifies each event as completed, delivered-late, queued, expired, failed, or unknown; A dashboard and pendant interaction for reviewing evidence and dismissing or approving proposed follow-up actions


## Changes it proposed to its own stack

### `relay` — Add an explicit ingress-audio contract and telemetry validator: reject or visibly flag live PCM whose declared sample rate is 15,625 Hz when the session contract is 24 kHz; resample once at a named boundary (pendant or relay), preserve original and effective rates in every pipeline event, and add a continuity/checksum marker so the Mac TTS 24 kHz output is not mistaken for end-to-end 24 kHz.
- **owner gets:** The owner gets consistent voice quality and an honest answer about whether their speech was actually captured at the promised wideband rate. It prevents silent pitch/bandwidth artifacts and makes dropped or late audio diagnosable instead of merely saying a response arrived.
- effort: Moderate: define schema/version, add a streaming resampler or enforce the pendant capture setting, validate frames, and expose a dashboard warning plus one regression fixture for 15,625→24,000 Hz.  ·  risk: A bad resampler could add latency or artifacts; recover by feature-flagging enforcement, retaining original PCM for a short diagnostic window, and falling back to the current path with a prominent degraded-quality status. Never retry a frame twice.
- cost: Small CPU/bandwidth increase for one resampling stage; negligible model/API cost. Diagnostic retention should be short and automatically deleted.  ·  latency: Target under 20 ms buffering per frame; avoid a second full-stream transcode.
- security: Audio remains within the existing relay/Mac path; raw diagnostic retention must be opt-in, encrypted, and TTL-deleted. Telemetry should contain rates and hashes, not speech text.
- depends on: A versioned pipeline audio schema carrying declared/effective sample rate and source; A verified choice of resampling boundary and pendant capture configuration; A playback-lifecycle/continuity telemetry consumer that understands degraded input

### `hardware` — Replace the prototype 15,625-Hz I2S microphone/clock path with a microphone and clocking design that natively captures 24 kHz (or higher with controlled downsampling), and make the uplink codec contract 24 kHz end-to-end instead of 16 kHz. Keep 24 kHz/60 ms playback frames but remove the misleading rate conversion boundary.
- **owner gets:** Speech captured from the pendant would genuinely retain the detail promised by the 24 kHz mode, rather than producing 24 kHz playback from a 15,625-Hz microphone source. Voice commands should sound clearer and be more robust in noise.
- effort: High hardware/firmware effort: select a low-power digital mic and supported clock, revise nRF9160 audio driver and Opus settings, validate LTE-M bitrate/latency, and update ESP32 I2S timing. Prototype on a dev board before a PCB spin.  ·  risk: Higher power, bandwidth, or CPU load; clock incompatibility and thermal/battery regressions. Recover with a negotiated per-session profile (wideband versus current mode), telemetry of actual rates, and a hardware-revision capability bit.
- cost: Prototype BOM increase roughly $3–$12 for mic/clock/board changes, plus engineering and a PCB spin; uplink bitrate may increase materially. No additional model cost.  ·  latency: Potentially higher encode/upload latency and radio airtime; target under 100 ms added buffering and benchmark Opus complexity against the current ~15 ms encode / ~25 ms decode per 60 ms packet.
- security: No new data class; higher bitrate means more audio leaves the pendant per second. Keep negotiated profile and consent visible, and never silently enable wideband on metered links.
- depends on: A documented 24 kHz end-to-end audio contract and sample-rate telemetry; Power/radio budget measurements on the actual wearable design; A/B firmware profile and relay codec negotiation

### `integration` — Introduce a cross-surface continuity ledger with immutable event envelopes: eventId, causalId, origin surface, observedAt, receivedAt, action state, evidence pointer, sensitivity, expiry, and acknowledgement. Pendant writes compact offline events to its existing local store; relay assigns receipt sequence numbers; Mac and browser append outcomes. Reconnect performs idempotent reconciliation and emits a signed state transition rather than overwriting history.
- **owner gets:** They can ask what happened during a dead connection and get an accurate timeline instead of a blended guess— including whether a response was spoken, merely generated, a browser command remained pending, or an action never ran.
- effort: High integration effort across firmware protocol, relay D1 schema, Mac job records, and browser queue. Add migration tooling, an event inspector, and fault-injection tests for duplicate, reordered, and permanently missing events.  ·  risk: Ledger growth, clock skew, and accidental exposure of private event summaries. Bound storage with compact envelopes and TTL/pinning; use monotonic per-origin sequence plus server receipt time; encrypt sensitive payloads and retain hashes when content is unnecessary. If reconciliation fails, preserve the unknown state rather than guessing.
- cost: Small relay storage and bandwidth overhead; low deterministic compute cost. No additional realtime API cost except when the owner requests a spoken summary.  ·  latency: A few seconds of reconciliation after reconnect; normal live voice path remains unchanged.
- security: Creates a durable metadata trail, so access control, per-surface redaction, deletion, and owner-visible audit are mandatory. Never replicate private page text to the pendant by default.
- depends on: A versioned event schema and causal-ID policy; Durable job/browser records with explicit terminal and expired states; Pendant offline-store sequence numbers and reconnect acknowledgement semantics


## What it asked for

_Nothing._
## Its own summary

Established and recorded four fresh facts: Mac computer-use is disabled because Accessibility and Screen Recording are not granted; Chrome bridge is offline with 3 pending commands while relay/Mac bridge are online; owner timezone (America/Chicago) conflicts with live Mac timezone (America/New_York); and current prototype audio is 15,625-Hz mic → 16-kHz Opus uplink → 24-kHz playback, not true 24-kHz end-to-end capture. Sent these to mac-vision, mac-planner, and relay-realtime. Proposed a cross-surface evidence-gated readiness report and concrete audio telemetry/resampling plus hardware changes.

**Biggest unknown:** The authoritative owner timezone and the actual pendant/firmware live diagnostic state remain unresolved. To proceed, the system still needs explicit timezone authority, a typed cross-surface perception snapshot endpoint, and (for computer use) owner-granted Accessibility/Screen Recording plus browser reconnection/heartbeat semantics.

