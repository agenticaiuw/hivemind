# Harness derivation — unified — round 25

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live stack readiness and audio path** — Mac agent 0.5.0 and relay 1.1.0 are reachable; browser extension online with 2 pending commands, but Accessibility and Screen Recording are ungranted and agent reports ready=false. Pipeline is receiving 15,625 Hz nRF9160 uplink and producing 24 kHz PCM TTS (example 160.8 KiB/3.43 s), while several nRF9160-origin runs remain status=processing after alert/bookmark events.
  - evidence: GET /ops/status and GET /pipeline probes at 2026-08-07

## Capabilities it proposed

### "“Repeat the last thing you told me, and show me what happened behind it.”"
- **useful because:** A wearable conversation should be recoverable when speech is missed or a job arrives late. The pendant can identify the last interaction even offline; the relay can reconcile its audio and delivery state; the Mac can expose the exact action receipt and browser evidence without making the owner remember a job ID.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic for lookup, reconciliation, and replay selection; background gpt-4.1-mini only to compress a long receipt; realtime only for the new spoken request
- **latency:** Under 300 ms for last-interaction lookup and a one-sentence replay; under 2 s to assemble cross-surface evidence. No network round trip should be required just to replay the pendant's locally cached last reply.
- **cost:** Usually near $0: D1/R2 and local event joins. A long receipt costs one background gpt-4.1-mini call, roughly a few thousand input tokens; audio replay uses already-rendered PCM where retained.
- **security:** Receipts can contain private page titles, mail subjects, or sensitive commands. Keep a sensitivity label with every event, redact by default in spoken output, require explicit confirmation before opening a private browser artifact, and never replay secrets aloud unless the owner asks. Delete cached audio under the configured retention policy.
- **missing:** A stable interaction/attempt ID carried from pendant button press through relay, Mac pipeline, browser command, and final delivery; Terminal pipeline states with append-only delivery acknowledgements instead of runs stuck at processing; A small pendant-side last-reply index with bounded audio metadata and encrypted replay cache; A read-only receipt endpoint and dashboard timeline that joins relay, Mac, and browser evidence

### "“Privacy hold.” Then, with one more button press, “Resume.”"
- **useful because:** Today the owner cannot instantly establish a physical, cross-device privacy boundary. This would make the pendant a trustworthy emergency mute: it would stop microphone capture locally, tell the relay to reject or discard in-flight audio, pause Mac and browser automation, and hold non-urgent notifications until the owner explicitly resumes. The owner gets a clear spoken/LED confirmation when the boundary is active, even if LTE is unavailable.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic firmware and relay state machine; no LLM required. Realtime only handles the owner's spoken “Privacy hold” after local wake, never policy decisions.
- **latency:** Local microphone shutdown and button confirmation under 100 ms. Relay/Mac/browser revocation under 2 seconds when connected; the pendant must remain safely muted and enforce the hold offline until an explicit resume gesture.
- **cost:** Negligible API cost: state transitions and acknowledgements are deterministic. A small D1 event and dashboard update per transition; no audio upload during the hold.
- **security:** This is a security boundary, so fail closed: reboot, LTE loss, malformed commands, and relay failure preserve mute and automation suspension. Do not allow a server push to clear it. Encrypt the persisted state, authenticate resume commands, show the state in the dashboard, and require a physical gesture to resume. Define emergency-alert exceptions explicitly rather than silently bypassing privacy.
- **missing:** A firmware privacy-state machine that gates I2S capture, button semantics, playback, and queued uploads; A signed, monotonic privacy epoch propagated through relay, Mac pipeline, and browser extension so stale commands cannot execute; Relay and Mac/browser middleware that cancels in-flight work and rejects commands from an earlier epoch; A visible dashboard state and audit record for hold/resume transitions; A tested policy for whether safety-critical alerts are suppressed, locally indicated, or allowed through


## Changes it proposed to its own stack

### `integration` — Introduce a cross-surface interaction ledger and reconciler. Generate one opaque interaction_id at button-down, propagate it in every audio chunk, relay job, Mac pipeline event, browser command, TTS object, and pendant playback acknowledgement. A worker periodically folds append-only events into terminal states (delivered, held-offline, replayed, expired, failed) and marks stale processing runs as unknown rather than completed. Expose a read-only receipt API consumed by the pendant and dashboard.
- **owner gets:** The owner will stop hearing ambiguous answers such as “it arrived” while the system still says processing. Late offline alerts, browser actions, and spoken replies will be traceable as one thing, and “repeat that” can reliably find the right response.
- effort: Medium-high: schema/versioning across relay and Mac, firmware metadata plumbing, idempotent reconciliation tests, and dashboard/voice formatting.  ·  risk: Old events lack IDs and need a migration fallback; duplicate or out-of-order LTE events could produce false terminal states. Preserve raw events, make folding idempotent, and use unknown/needs-review rather than guessing. Roll back by disabling the reconciler while retaining the ledger.
- cost: Small D1 storage/index overhead and one cheap scheduled Worker pass; no model call for normal receipts. Additional R2 metadata only, not duplicate audio.  ·  latency: Adds no synchronous path latency; receipt reads should be sub-300 ms. Reconciliation freshness target 5–30 seconds.
- security: Opaque IDs avoid exposing secrets, but joined metadata is sensitive. Enforce owner auth, field-level redaction, short TTL for private page details, and separate audio/object authorization.
- depends on: A shared interaction_id envelope in relay and Mac pipeline schemas; Pendant firmware event metadata support and bounded local replay index; Idempotent delivery acknowledgements from pendant playback and offline spool; A scheduled relay reconciliation trigger


## What it asked for

### `s4-o8y7` (skill) — last_interaction_receipt_index
- does: On each button press, received alert, spoken reply start/finish, and offline-forward event, stores a compact opaque interaction ID, event kind, monotonic uptime, link state, delivery/playback state, and a short redacted label. On a local “repeat/status” trigger it returns the latest interaction ID and whether the reply was delivered, held, or failed; it never stores routine audio.
- must be on-device because: The owner may ask immediately after a dropped LTE link, and only the pendant knows which response was actually heard. The SD policy permits failure buffering but forbids routine audio storage, so this skill is intentionally metadata-only and must survive a disconnected link.
- trigger: Second button gesture (short double-press) or a server push requesting a receipt lookup; ordinary conversation button events also append automatically.
- storage: A rotating binary journal on microSD under the existing FATFS mount, capped at 64 KiB (for example 512 entries); no routine audio. If SD is unavailable, retain the latest 8 entries in RAM and report degraded persistence.
- RAM budget: ~2 KiB working buffers plus one 128-byte latest-entry cache; comfortably below the 211,608 B application RAM budget, but append/flush must not contend with Opus buffers or the modem.

## Its own summary

Round 25 found a live but not-ready stack: relay 1.1.0 and Mac agent 0.5.0 are reachable, browser is online, 24 kHz TTS is already produced, but Mac Accessibility/Screen Recording remain absent and pipeline runs can stay in processing after offline alert/bookmark events. I proposed a cross-surface interaction ledger/reconciler, a user-facing “repeat the last thing and show what happened” capability, and queued a metadata-only pendant receipt index that respects the rule that SD is only a failure buffer for audio.

**Biggest unknown:** The authoritative 24 kHz acceptance criteria, target audio architecture, and production pendant constraints are still unavailable; without them I cannot safely claim the end-to-end audio path is shippable. The previously requested OS permissions and implementation tools also still do not appear as grants.

