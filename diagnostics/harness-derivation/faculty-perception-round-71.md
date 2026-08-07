# Harness derivation — faculty-perception — round 71

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-timezone** — Live Mac machine-context reports timezone America/New_York, while owner memory projection says authoritative owner timezone America/Chicago; timezone is currently unresolved and should not be silently chosen for schedules or spoken times.
  - evidence: GET /machine-context returned machine.timezone=America/New_York at 2026-08-07T12:42Z; discover:owner remembered.text explicitly says timezone: America/Chicago.
- **browser-queue** — Chrome browser bridge is offline while five browser commands remain pending; three durable browser sessions exist, including a UTC time page last used at 06:26 and two probe forms. Pending commands must not be blindly replayed on reconnect.
  - evidence: GET /browser/status returned online=false and pendingCommands=5; GET /browser/sessions returned sessions default, probe-form2, probe-form.
- **input-reachability** — Mac agent's observation surface is live but synthesized UI input is not trustworthy: Accessibility and Screen Recording are false, inputReachability.status=failed, and ui actions may report success while doing nothing. AppleScript automation grants are present.
  - evidence: GET /observe at 2026-08-07T12:42:28Z: accessibility.trusted=false, screenRecording=false, inputReachability.status=failed, uiActionsWillReachTheScreen=false; GET /ops/status reports automation grants and permissions.ready=false.
- **audio-pipeline** — The live pipeline has demonstrated successful 24 kHz mono PCM output (75,734 bytes, 1.578 s, unclipped), but a recent live pendant input telemetry record was 15,625 Hz PCM, so end-to-end input remains below the owner's 24 kHz objective.
  - evidence: GET /pipeline event meta: TTS format s16le sampleRate=24000 channels=1 pcmBytes=75734; separate nrf9160 event meta inputTelemetry.sampleRate=15625 format=pcm-s16le.

## Capabilities it proposed

### "When my browser reconnects, tell me which queued actions are still safe, discard stale probes, and ask before replaying anything ambiguous."
- **useful because:** The bridge is currently offline with five queued commands and three durable sessions. Blind replay could click or submit in a changed tab; the owner needs a truthful reconnect report and controlled recovery rather than silent execution.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background for queue classification and stale-session summaries; deterministic rules for expiry, idempotency, and confirmation; realtime only if the owner is speaking during reconnect
- **latency:** Under 2 seconds for deterministic status; up to 5 seconds for a background classification after heartbeat/reconnect
- **cost:** Usually zero model cost for command metadata and TTL checks; roughly 2k–4k input tokens only when an ambiguous queued action needs background classification
- **security:** Never replay submit/send/delete/purchase or unknown UI clicks automatically. Bind commands to session/tab identity and URL/title fingerprints; expire probe/test commands quickly; show the exact command and destination before confirmation. No page contents leave the Mac unless the owner requests classification.
- **missing:** Durable per-command intent, creation time, TTL, risk class, and tab fingerprint in the browser queue; Reconnect reconciliation that marks each pending command safe, stale, or confirmation-required instead of polling and executing blindly; A pendant-readable reconnect receipt with explicit confirmation tokens

### "Tell me the correct local time for where I am, and warn me when the devices disagree before using that time for a reminder or scheduled action."
- **useful because:** The owner's remembered timezone is America/Chicago, while the live Mac reports America/New_York and an open browser page is UTC. Today the system can silently choose one source, causing wrong spoken times and misplaced scheduled work. The owner should receive a confidence-labeled time answer and an explicit conflict prompt instead.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic time-zone and clock reconciliation; use the background tier only to explain a conflict in one short sentence. Realtime is unnecessary unless the owner is actively asking aloud.
- **latency:** Under 300 ms when sources are available; up to 2 seconds if a browser or Mac heartbeat is needed.
- **cost:** Normally zero model/API cost; a background explanation is roughly 200–500 input tokens and a few dozen output tokens.
- **security:** Use only timezone identifiers and clock metadata, not location inference from browsing. Never change the owner's timezone or reschedule existing routines without explicit confirmation. A timezone override should be stored as a preference with provenance and revocation.
- **missing:** A first-class temporal-authority record separating owner preference, machine configuration, browser observation, and relay time; A conflict state that blocks timezone-sensitive scheduling until confirmed, while still allowing a clearly labeled UTC answer; A small owner confirmation flow on the pendant/dashboard and audit evidence showing which source governed each scheduled action


## Changes it proposed to its own stack

### `firmware` — Add an end-to-end audio truth contract: the pendant must stamp the actual ADC sample rate and frame clock in every upload; the relay and Mac pipeline must reject or visibly label non-24-kHz input, and a local resampler (or negotiated capture mode) must produce 24-kHz PCM before speech processing. Persist a compact last-session audio-integrity record so perception can distinguish output-only 24 kHz from true bidirectional 24 kHz.
- **owner gets:** The system can currently report a successful 24-kHz speaker payload while a live pendant capture was actually 15,625 Hz. This prevents the owner from being falsely told that the promised superwideband path is complete and makes bad conversations diagnosable instead of mysterious.
- effort: Medium: firmware capture metadata and resampling/clock validation, relay schema validation, Mac pipeline labels, and one integration test with deliberately mismatched input.  ·  risk: A strict reject could interrupt a live conversation on marginal firmware. Recover by falling back to the existing supported rate with an explicit degraded-mode event and spoken/dashboard status; never silently relabel it 24 kHz.
- cost: Negligible model/API cost; modest firmware CPU and buffer use for resampling, plus a few hundred bytes of telemetry per session. No hardware cost if the current codec can capture the negotiated rate.  ·  latency: Likely 1–5 ms buffering for a streaming resampler; validation is sub-millisecond. A fallback path preserves current latency.
- security: Audio metadata and integrity records stay within pendant/relay/Mac telemetry; do not upload raw audio solely for validation. Avoid persisting speech content.
- depends on: An authoritative negotiated-rate field in the relay audio contract; A fixture or test recording that proves actual pendant input clock rather than trusting declared metadata; The pending 24-kHz superwideband implementation work


## What it asked for

_Nothing._
## Its own summary

Fresh live evidence recorded: owner timezone (America/Chicago) conflicts with Mac-reported America/New_York; browser bridge is offline with 5 queued commands and stale durable sessions; synthesized UI input remains untrusted despite successful-looking UI receipts; 24-kHz playback is proven but live pendant capture was 15,625 Hz. Sent these to faculty-judgement. Proposed a reconnect queue quarantine/reconciliation capability and an audio truth-contract firmware change so the system cannot claim bidirectional 24 kHz when only output meets it.

**Biggest unknown:** The still-unavailable authoritative pendant/firmware observability: actual ADC clock, negotiated codec/rate, resampler state, and whether the 15,625-Hz telemetry is a real capture rate or a reporting artifact. Also unresolved is which timezone should govern schedules until owner authority is explicitly reconciled.

