# Harness derivation — unified — round 30

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-cross-surface-readiness** — Relay and Mac bridge are online and relay has speech, durable audio, persistent state, and pipeline telemetry. Mac agent is not ready for GUI/vision work because Accessibility and Screen Recording are both untrusted; browser extension is offline with 2 pending commands. This blocks reliable urgent authenticated-page monitoring and visual evidence, though deterministic non-GUI routes remain available.
  - evidence: GET /ops/status at 2026-08-07T10:00:13Z: macBridgeOnline=true; accessibility.trusted=false; screenRecording.granted=false; browser.online=false; pendingCommands=2; relay capabilities include pendantPipelineTelemetry, pendantSpeech, persistentAgentState, durableAudio.

## Capabilities it proposed

### "When something genuinely urgent happens in my logged-in accounts or on my Mac, interrupt me through the pendant with a 20-second explanation; otherwise hold it for my next quiet briefing."
- **useful because:** The owner gets timely alerts without being flooded by unchanged notifications. The relay can stay awake and rank events while the Mac/browser are unavailable, the browser can inspect private sessions, and the pendant can deliver a concise spoken interruption and let the owner say 'snooze', 'show me', or 'handle it'. No single node can both watch private sessions, remain awake, and reach the wearer.
- **path:** relay-realtime → browser-extension → mac-planner → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheap background model on the relay for event normalization/deduplication and urgency scoring; use the text model only to compose the short alert; reserve realtime for the owner's spoken follow-up. Browser/Mac extraction should be deterministic first, with a stronger model only for ambiguous severity.
- **latency:** Event ingestion and dedupe under 10 seconds; alert composition under 3 seconds after evidence is available; pendant playback should begin within 5 seconds for critical events. Quiet-hour batching may take minutes by design.
- **cost:** Typically <$0.01 per event batch; browser/Mac reads and deterministic hashing dominate volume, while model calls occur only for changed or ambiguous items. Realtime cost is limited to the owner's follow-up conversation.
- **security:** Private page excerpts and Mac metadata leave the Mac only when an event passes the configured urgency threshold. Store evidence capsules with TTL and redact secrets; never click, send, purchase, or submit from an alert. Require spoken confirmation before any follow-up action, and provide an immediate 'mute alerts' control on the pendant.
- **missing:** A durable event-normalization and urgency policy shared by relay, Mac, and browser (not just page watches); A push channel from relay to pendant with interruption state, quiet hours, snooze, and delivery receipts; Browser extension online presence and authenticated watch execution; A user-visible review queue showing evidence, urgency reason, expiry, and why an alert was or was not sent; Mac Accessibility/Screen Recording permissions if foreground-app or visual evidence is needed

### "When I walk away from something unfinished, leave me a private, resumable breadcrumb: what I was trying to do, which Mac app and browser tabs mattered, what I already changed, and the safest next step. When I return or ask 'where was I?', bring me back to that exact state without making me reconstruct it."
- **useful because:** Today the owner loses work context whenever they switch devices, close a tab, or leave a conversation. This would turn interruptions into recoverable handoffs rather than another reminder or transcript. It requires the pendant to mark the interruption, the Mac to capture application state, the browser to preserve authenticated tab identity, and the relay to retain and reconcile the checkpoint while the Mac is asleep or disconnected.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use deterministic capture for foreground app, URLs, tab/session IDs, open files, and action receipts. Use a cheap background model to summarize intent and identify the next reversible step; use the expensive realtime tier only when the owner asks for spoken recovery or clarification.
- **latency:** Capture should complete within 2 seconds of a button press or explicit 'save my place'. Resume context should be available within 5 seconds when the Mac/browser reconnect. No continuous vision or audio recording is required.
- **cost:** Usually below $0.01 per checkpoint; storage and structured metadata dominate. Summarization can be deferred until the owner requests recovery, reducing model spend.
- **security:** Authenticated URLs, filenames, and page snippets are sensitive. Store only structured state plus short encrypted evidence capsules with configurable TTL; never persist passwords, form secrets, or raw microphone audio. Require confirmation before reopening a private tab or repeating an action. Show the owner exactly what was captured and provide one-tap deletion.
- **missing:** A first-class cross-surface checkpoint schema linking pendant interaction, Mac foreground state, browser tab/session identity, and execution receipts; A reliable browser reattachment mechanism that can restore the same authenticated tabs after reconnect; Mac APIs for capturing and restoring safe application state without screen recording by default; A relay-resident encrypted checkpoint store with expiry, conflict handling, and explicit owner deletion; A pendant command and playback flow for 'save my place' and 'resume the last thread'


## Changes it proposed to its own stack

### `hardware` — Replace the prototype pendant enclosure with a production board that adds a low-power haptic actuator on an I2C GPIO expander or dedicated driver, plus a fuel-gauge IC on the currently free I2C bus. Expose distinct short/long vibration patterns and battery percentage/low-battery events to firmware; keep the existing single button and LED as fallback. The relay should be able to request an interruption pattern without opening audio until the owner presses the button or says a wake phrase.
- **owner gets:** The owner can notice an urgent alert in a pocket or noisy room without a disruptive always-on voice prompt, and can trust that the pendant will not die unexpectedly during a conversation.
- effort: New PCB/enclosure revision, driver support, power characterization, and relay protocol fields for haptic intent and battery telemetry; validate patterns against real clothing and walking conditions.  ·  risk: Added motor noise can leak into the microphone and increase power draw; isolate mechanically, suppress mic during vibration, rate-limit patterns, and fall back to LED/audio. A fuel-gauge calibration error could misreport charge; expose confidence and retain low-voltage hardware cutoff.
- cost: Roughly $2–$6 BOM increase for haptic driver/actuator and $1–$3 for a gauge, with brief 10–30 mA vibration pulses and negligible idle draw; no per-call API cost.  ·  latency: Haptic request can be rendered locally in tens of milliseconds once received; battery telemetry is periodic and does not affect audio latency.
- security: Battery and haptic state are non-sensitive. Do not include alert content in device telemetry; send only an opaque alert ID and pattern class.
- depends on: Production pendant constraints and enclosure design; Firmware event protocol for relay-to-pendant push; Battery/power validation and audio-link coexistence tests


## What it asked for

_Nothing._
