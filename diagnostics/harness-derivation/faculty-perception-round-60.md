# Harness derivation — faculty-perception — round 60

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-ui-input-reachability-2026-08-07** — At 2026-08-07T12:10:57Z, /observe reports AI Pendant Agent foreground host com.anthropic.claudefordesktop, accessibility trusted=false, screenRecording=false, inputReachability.status=failed, and explicitly warns ui_click/ui_menu/type_text/press_keys may report success while doing nothing. AppleScript automation grants are present for System Events, Finder, Reminders, Calendar, Mail, Notes, Messages, Safari, Chrome, Music, Preview, TextEdit, VS Code and terminals.
  - evidence: GET /observe HTTP 200 response observed this round.
- **browser-offline-queue-2026-08-07** — At 2026-08-07T12:10:57Z, browser extension home-chrome is offline with 0 tabs and 5 pending commands; the Mac bridge itself is online via relay.
  - evidence: GET /browser/status and GET /ops/status HTTP 200 responses observed this round.
- **audio-rate-asymmetry-2026-08-07** — A recent live pendant pipeline run contains input telemetry at 15,625 Hz PCM (audioBytes 937,500, duration 1,441 ms) while the generated response audio is 24,000 Hz mono s16le PCM (75,734 bytes, 1,578 ms). Thus 24 kHz output is established for that run, but 24 kHz end-to-end input is not established.
  - evidence: GET /pipeline HTTP 200 response for pipeline job_165a9c9a-e5e3-4e29-b500-2fad63115ab9 and GET /pipeline/job_165a9c9a-e5e3-4e29-b500-2fad63115ab9/audio/output returned RIFF PCM header.
- **planner-cost-observation-2026-08-07** — Routing telemetry currently reports 7 requests: 57% off planner, 28,971 planner tokens across 3 requests, baseline planner average 8,837 tokens/request and 2,527 ms; recent routine briefing was deterministic while morning battery routine used background tier.
  - evidence: GET /routing HTTP 200 response observed this round.

## Capabilities it proposed

### "“Is my pendant voice link healthy right now?” Give me one spoken answer that distinguishes microphone capture, upload, transcription, response rendering, download, and physical playback—and automatically switch to a lower-bandwidth mode if any stage is degraded."
- **useful because:** Today the system can prove a 24 kHz rendered response while a real upload arrived at 15,625 Hz, and it can report a Mac UI action as successful even when input never reached the screen. The owner has no single, honest, end-to-end voice-health answer and no graceful quality adaptation. This capability turns invisible degradation into an actionable spoken status instead of making the owner debug logs.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Deterministic telemetry aggregation and threshold rules for all measurements; use the cheaper background tier only to phrase an unusual multi-fault explanation. Never spend realtime inference on health arithmetic.
- **latency:** A normal query should answer in under 2 seconds from cached recent telemetry; on-demand active calibration may take 3–8 seconds. Quality fallback must happen locally or at the relay without waiting for a model.
- **cost:** Near-zero model cost in normal use. Active calibration adds a small synthetic audio exchange and telemetry storage; background phrasing is typically under 500 tokens.
- **security:** Calibration uses synthetic tones and metadata only, never retained microphone content. Spoken status must avoid private transcript/page data. Health records should have short retention and device/session identifiers should be minimized. Automatic fallback must not silently record or send more audio than the current session policy permits.
- **missing:** A single cross-surface voice-health schema with stage, timestamp, sample rate, frame count, byte count, loss/jitter, and acknowledgement state; Pendant firmware telemetry for capture start/stop, packet enqueue/upload, response download, decoder underruns, and speaker-played acknowledgement; Relay correlation IDs that join one utterance across LTE upload, transcription, Mac rendering, response download, and playback; A deterministic adaptive-quality policy (24 kHz preferred, explicitly labeled lower-rate fallback) and a spoken/dashboard status renderer; A synthetic end-to-end calibration command that can be initiated by voice or dashboard and has a bounded timeout


## Changes it proposed to its own stack

### `integration` — Add an end-to-end audio contract checker and negotiation loop. Every pendant upload and Mac-rendered response must carry measured sampleRate, frame count, codec, channel count, timestamps, and byte count. The relay rejects or explicitly labels uploads that are not 24,000 Hz when the session advertises superwideband; the Mac bridge resamples only through one named stage and records pre/post rates. A deterministic periodic calibration packet from the pendant (no user audio content) verifies capture→LTE→relay→Mac→TTS→relay→playback, with a single status object reporting where conversion or loss occurred.
- **owner gets:** The current evidence proves 24 kHz playback output but a live input arrived at 15,625 Hz, so the owner cannot honestly be told that the promised 24 kHz path is end to end. This would make voice quality predictable and expose regressions before they become a confusing conversation.
- effort: Medium: typed telemetry schema across pendant firmware, relay D1, Mac pipelineTrace/audio, plus deterministic calibration and dashboard display; no model training required.  ·  risk: Rejecting a mismatched upload could interrupt a conversation. Default to compatibility mode (accept and label/resample) with a visible degraded-quality state; only strict mode rejects. Calibration packets must be synthetic and never contain microphone content.
- cost: Negligible inference cost; a calibration packet every session or hourly is small LTE/D1 traffic. Engineering cost is schema migration and one resampler audit.  ·  latency: Adds <100 ms to session startup if calibration is asynchronous; no per-turn delay. Strict negotiation may delay first utterance until the contract is known.
- security: Telemetry contains no transcript, but timestamps/device identifiers are metadata; retain briefly and apply existing audio-retention deletion. Do not upload calibration microphone recordings.
- depends on: Pendant firmware must report actual capture sample rate rather than nominal rate; Relay must preserve and validate audio metadata across upload/download; Mac pipeline audio endpoints must expose input metadata, not only output WAV headers; Dashboard/pendant status needs a degraded-quality indicator

### `mac-harness` — Make the executor perception-aware without adding an approval gate: before dispatch, consult the latest /observe inputReachability result and classify each planned step by its execution channel. If synthesized UI input is failed, automatically reroute eligible intents (Calendar, Reminders, Mail drafts, Notes, Safari/Chrome navigation) through their already-granted AppleScript or browser-session APIs; for ineligible UI-only steps, return an explicit 'unverifiable channel' result and stop that step rather than emitting a false success receipt. Attach the observation timestamp and channel to every receipt.
- **owner gets:** The owner can ask the pendant to carry out routine work and get a truthful result even while the agent's UI input is broken. Today clicking or typing may say success while doing nothing; this change preserves useful automation through granted channels and clearly identifies the small remainder that genuinely needs the owner.
- effort: Medium: typed intent-to-channel capability map, pre-dispatch observation lookup, receipt fields, and tests for stale observations and browser-offline state. No Accessibility grant is required for the fallback channels.  ·  risk: An incorrect mapping could choose the wrong automation route or alter behavior. Keep mappings allowlisted, require semantic preconditions, use existing reversible-action policy, and fall back to a no-op with a clear receipt when confidence or freshness is insufficient. Do not retry failed UI clicks blindly.
- cost: No additional model calls for deterministic routing; one local observation read per job. Small implementation and regression-test cost.  ·  latency: Adds tens of milliseconds locally; AppleScript/browser fallback latency is comparable to current action execution. Offline browser remains explicitly pending rather than blocking the whole job.
- security: Uses only existing owner-granted automation and browser sessions. Receipt metadata gains observation timestamps but no page contents. Preserve existing confirmation rules for sends, deletes, purchases, and other destructive actions.
- depends on: A typed capability map for AppleScript/browser equivalents of common UI intents; Freshness/expiry semantics for /observe snapshots; Executor receipts that record execution channel and verification state; A non-destructive partial-job result format


## What it asked for

_Nothing._
## Its own summary

Established new live facts: Mac UI automation is not trustworthy (Accessibility and Screen Recording false; input probe failed), browser extension is offline with 5 queued commands, relay/Mac bridge are online, and a real pipeline run proves 24 kHz output but only 15,625 Hz input. Routing currently keeps 57% of requests off the expensive planner tier. Recorded all four findings and proposed a new end-to-end audio contract/calibration change with compatibility-mode fallback. The broader 'did that actually happen?' capability was correctly rejected as already present in the backlog.

**Biggest unknown:** Pendant-side capture and playback truth: actual hardware sample rate, resampling stages, packet loss/jitter, download acknowledgement, and whether audio was physically played. I still need the granted pendant diagnostics/continuity tools or an authoritative device telemetry route; without them I cannot claim 24 kHz end-to-end.

