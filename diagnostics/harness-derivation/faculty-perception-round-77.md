# Harness derivation — faculty-perception — round 77

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-device-presence** — At 2026-08-07T13:04Z, device registry has Mac bridge online, Chrome extension offline, mobile test device offline; no pendant device is registered.
  - evidence: discover:devices live result; GET /ops/status payload shows macBridgeOnline=true and browser online=false; prior granted observability says no nRF9160 has ever registered.
- **mac-input-reachability** — AI Pendant Agent is running but cannot post synthesized UI events: Accessibility trusted=false, Screen Recording=false, inputReachability.status=failed, so UI click/type receipts are not trustworthy.
  - evidence: GET /observe at 2026-08-07T13:04:19Z: accessibility.trusted=false, eventsPost=false, uiActionsWillReachTheScreen=false, inputReachability.status=failed.
- **browser-state** — Browser extension home-chrome is offline with 7 pending commands; three durable browser sessions exist, including UTC clock and two Selenium probe pages.
  - evidence: GET /browser/status and GET /observe at 2026-08-07T13:04Z.
- **pipeline-staleness** — Pipeline contains historical completed audio-native and routine runs, including 24 kHz PCM rendered and relay-accepted, but this does not establish a connected pendant or current playback.
  - evidence: GET /pipeline at 2026-08-07T13:04Z lists runs sourced from nrf9160/cloud-relay with historical timestamps and status processing/completed; live device registry has no pendant.
- **device-status-route** — The Mac agent does not expose GET /v1/devices/status; it returns 404. Live device presence is currently available through the devices capability/ops relay payload, not that route.
  - evidence: probe_http GET /v1/devices/status at 2026-08-07T13:04Z returned 404 No such route.

## Capabilities it proposed

### "“Is that really happening right now?” Give me a live, evidence-backed status across my devices, Mac, browser, and relay—separate current observations from stale history, call out contradictions, and say what you cannot verify."
- **useful because:** The current system can expose historical pipeline records that look live even when no pendant is connected, and can report UI action success despite Accessibility being absent. This gives the owner an honest answer before they rely on a claim or receipt.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background/cheap model for scheduled or explicit audits; realtime only to phrase the short spoken answer after the evidence bundle is assembled.
- **latency:** 2–5 seconds for an explicit query; under 30 seconds for a full cross-surface audit. Parallel read-only probes dominate latency.
- **cost:** Usually <$0.01 per audit with a small summarizer; most cost is model synthesis, not the GET probes.
- **security:** Reads device presence, browser connectivity, Mac permissions, and recent pipeline metadata; do not include page contents or secrets unless separately requested. Contradictions and stale records must be shown rather than silently resolved. Any remedial action requires separate confirmation.
- **missing:** A first-class cross-surface evidence bundle with per-fact observedAt, source, freshness TTL, and live-versus-historical classification; A contradiction/quarantine rule preventing historical pipeline telemetry from being presented as current device state; An owner-facing audit endpoint or spoken intent that invokes read-only probes in parallel

### "“Show me exactly where that went wrong.” After a misunderstood request, failed action, or disputed receipt, assemble a private incident packet linking the pendant audio/transcript, relay delivery, Mac plan, browser command/result, permission state, and final receipt—then explain the first point of divergence and what evidence is missing."
- **useful because:** Today the owner can receive a confident answer or receipt without being able to reconstruct whether the words were heard correctly, delivered late, planned incorrectly, blocked by a disconnected browser, or falsely reported by an inaccessible Mac UI. A single causal timeline would make failures diagnosable instead of mysterious, especially when the owner is away from the Mac.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic correlation and a cheap background model to build the timeline; reserve realtime only for a short spoken summary when the owner asks from the pendant.
- **latency:** Under 10 seconds for a recent incident; up to 60 seconds when audio transcription or browser evidence must be fetched. The owner should receive an immediate acknowledgement while the packet is assembled.
- **cost:** Typically <$0.03 per incident, dominated by optional audio transcription and final synthesis; correlation itself is negligible.
- **security:** Incident packets may contain private speech, logged-in URLs, page excerpts, and action parameters. Encrypt at rest, default to a short retention window, redact secrets and tokens, require explicit owner request, and never transmit page contents to the pendant unless requested. Do not infer success from an unverified UI receipt.
- **missing:** A durable correlation ID propagated unchanged from pendant capture through relay job, local plan, browser commands, and receipts; An append-only event envelope with monotonic sequence, source clock, observedAt, deliveryAt, and verification status; A redaction and owner-visible export format for incident packets; A causal classifier that distinguishes transcription error, delivery delay, planner error, unavailable surface, permission failure, and unverified outcome


## Changes it proposed to its own stack

### `integration` — Add a server-side evidence joiner that stamps every pipeline event with observedAt, source device/session, relay receipt time, and a live-presence check. Mark historical events as historical when their source device is not currently registered; expose a read-only /evidence/current snapshot consumed by all faculty agents. Never let a completed audio or alert event imply current pendant connectivity by itself.
- **owner gets:** When the owner asks whether something happened now, the answer will not confuse an old successful run with a live wearable. They get a clear “current / last seen / historical / unverifiable” distinction.
- effort: Medium: relay schema migration, one join/read endpoint, and prompt projection updates across perception and judgement.  ·  risk: Old records may be relabeled, and a clock or registration outage could produce “unverified” rather than a confident answer. Recover by retaining raw immutable event timestamps and allowing a manual historical view.
- cost: Negligible storage and probe cost; one small read per audit. No model cost unless summarized.  ·  latency: Tens to hundreds of milliseconds for the join; parallel reads keep explicit audits within a few seconds.
- security: Adds device/session metadata to internal records; keep it bearer-protected and omit page contents. No new action authority.
- depends on: A relay/device registry truth source or equivalent current registration snapshot; Cross-surface evidence bundle proposed this round; Consumers stop treating /pipeline history as live state

### `interaction` — Add an explicit truth-status channel across relay and future pendant firmware: every spoken response carries a compact provenance class (LIVE, CACHED, DELAYED, or UNVERIFIED) plus an expiry, and the pendant expresses it with a distinct short haptic/LED pattern before or alongside playback. The Mac dashboard shows the same status; cached audio cannot silently sound identical to a live answer.
- **owner gets:** The owner can tell at a glance or by touch whether they are hearing a current answer, an answer prepared earlier, or something whose delivery/state was never verified—without opening the dashboard or remembering technical caveats.
- effort: Medium: define a signed response envelope, propagate status through relay and Mac pipeline, add firmware playback-state cues, and add dashboard labels. Requires pendant hardware/firmware integration when a device exists.  ·  risk: Extra cues could annoy or confuse the owner, and clock skew could misclassify expiry. Make patterns short, user-configurable, and fall back to UNKNOWN rather than claiming LIVE when evidence is absent; retain the spoken content unchanged.
- cost: Negligible per-request API/storage cost. Firmware work is moderate; hardware cost is $0 if existing LED/haptic I/O is usable, otherwise roughly $2–5 for a haptic driver/indicator and under 20 mW while signaling.  ·  latency: Under 100 ms for metadata and cue; no material impact on speech generation.
- security: Response envelopes must be authenticated so a stale or forged result cannot claim LIVE. Do not expose sensitive content in the cue metadata.
- depends on: A relay response envelope with authenticated provenance and expiry; A registered pendant with usable LED/haptic output; The cross-surface live-presence evidence joiner proposed this round


## What it asked for

_Nothing._
