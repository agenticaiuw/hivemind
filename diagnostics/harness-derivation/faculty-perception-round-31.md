# Harness derivation — faculty-perception — round 31

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent-readiness-2026-08-07T10:33Z** — Mac bridge is online and relay reachable, but local agent is not operationally ready: Accessibility trusted=false, Screen Recording granted=false, input reachability failed, and synthesized UI actions would report success while doing nothing. Automation grants are present. Computer-use loop disabled and vision upload consent false.
  - evidence: GET /ops/status at 2026-08-07T10:33Z: agent.ready=false; accessibility.trusted=false; screenRecording.granted=false; inputReachability.status=failed; consequence says ui_click/type_text/press_keys cannot be trusted; computerUse.loopEnabled=false.
- **browser-connectivity-2026-08-07T10:33Z** — Authenticated browser extension is offline, with 3 pending browser commands and 3 durable browser sessions still visible to the Mac observer; no active tab is attached to the extension device.
  - evidence: GET /ops/status and GET /observe at 2026-08-07T10:33Z: browser.online=false, home-chrome online=false, pendingCommands=3; observed sessions=3 with tabs default/time.is/UTC, probe-form2 Selenium web form, probe-form httpbin.
- **audio-pipeline-sample-rate-mismatch-2026-08-07** — The observed response TTS path successfully rendered 24 kHz mono PCM (164,650 bytes, 3.43 s), but a recent live input telemetry record reports 15,625 Hz PCM capture (937,500 bytes) for 1.441 s. This is evidence of asymmetric sample rates in the current pipeline, not evidence that the 24 kHz objective is met end-to-end.
  - evidence: GET /pipeline at 2026-08-07T10:33Z: relay job job_165a... inputTelemetry.sampleRate=15625; same run tts event meta.sampleRate=24000, channels=1, pcmBytes=164650.
- **authoritative-timezone-2026-08-07** — The Mac machine-context reports America/New_York as the host timezone.
  - evidence: GET /machine-context at 2026-08-07T10:33:12Z returned machine.timezone='America/New_York'.

## Capabilities it proposed

### "If you can't safely reach the screen or my browser, tell me before doing anything, explain exactly what's unavailable, and use a trustworthy fallback when one exists—never say it worked when it didn't."
- **useful because:** Right now the Mac reports UI actions as successful even though Accessibility is untrusted and input delivery fails; the browser is offline with queued commands. A live capability contract would prevent silent no-ops and preserve the owner's trust while still allowing safe AppleScript/terminal or spoken-only alternatives.
- **path:** pendant → relay → mac-planner → mac-vision → mac-terminal → browser-extension → dashboard
- **model tier:** Realtime only for the spoken explanation and immediate classification; deterministic readiness probes and fallback selection run on the Mac/relay with a cheaper background model for ambiguous cases.
- **latency:** Under 1 second for readiness checks; under 3 seconds for a spoken diagnosis. No action should begin until the required surface is verified reachable.
- **cost:** Near-zero API cost for local probes and typed status; occasional cheap-model call (<$0.01) only when choosing among fallbacks. Realtime cost is limited to the short owner-facing response.
- **security:** Readiness metadata, app names, and browser connectivity leave the Mac only as compact status facts. Screen content and authenticated page data stay local unless separately requested. Irreversible actions still require normal confirmation; a failed readiness check must block the action, not merely warn.
- **missing:** A shared typed readiness contract consumed by planner, executor, and relay; Precondition enforcement that converts accessibility/input/browser failures into a blocked result before dispatch; A fallback matrix mapping each action to verified AppleScript, terminal, browser, or spoken alternatives; Owner-facing receipt field distinguishing dispatched, observed-success, and blocked-before-dispatch

### "When I tap the pendant and say “remember this moment,” save it even without a connection, then later attach the right time, nearby Mac app/document, and browser tab context and let me ask “what was that moment?”"
- **useful because:** A wearable bookmark is valuable precisely when the owner is moving or offline, but today an offline bookmark is only a raw event. The owner cannot reliably recover what they were looking at or doing when they made it. This would turn a one-button interruption marker into searchable episodic memory without requiring them to stop and take notes.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Pendant firmware records a tiny local event; relay performs durable delivery and deduplication; Mac planner performs delayed context joining and uses a cheap background model only to summarize ambiguous context. Realtime is unnecessary except for the immediate spoken acknowledgement.
- **latency:** Offline acknowledgement under 150 ms. After reconnection, context enrichment within 30 seconds when the Mac is online; retrieval response under 2 seconds from the local index.
- **cost:** Near-zero API cost for event storage and deterministic joins; occasional <$0.01 cheap-model summarization per bookmark. Storage is compact metadata by default, not continuous audio or screenshots.
- **security:** The bookmark may link to sensitive app names, document paths, or authenticated URLs. Keep raw event and context on the Mac/relay encrypted, apply short TTLs to browser-derived details, require explicit opt-in per source, and show provenance plus a delete button. Never capture screen contents or microphone audio beyond the utterance used to create the bookmark unless separately authorized.
- **missing:** A pendant offline bookmark record containing monotonic time, wall-clock estimate, link state, and a stable event ID; Relay acknowledgement/deduplication and replay of bookmark events after reconnect; Mac-side temporal context joiner that snapshots foreground app, active document, browser session/tab, and project context near the event time; A provenance-aware episodic-memory index and owner-facing retrieval/deletion UI; A privacy policy for which app/browser context sources may be joined


## Changes it proposed to its own stack

### `integration` — Add an end-to-end audio format contract: negotiate and validate capture sample rate at session start, resample explicitly to the target (24 kHz where supported), and stamp every input/output artifact with source rate, target rate, conversion, duration, and loss indicators. Reject or visibly downgrade a run when the pendant sends 15,625 Hz instead of silently labeling only the TTS side as 24 kHz.
- **owner gets:** Voice conversations will sound more consistent and diagnostics will tell the owner whether the pendant's microphone path actually met the promised quality, instead of hiding an input/output mismatch.
- effort: Medium: relay schema and validation, Mac pipeline instrumentation, pendant firmware negotiation/reporting, and one integration test using the currently observed 15,625 Hz capture path.  ·  risk: A strict reject could interrupt a conversation on older firmware; recover by accepting the stream with explicit resampling and a spoken/dashboard quality warning. Preserve raw telemetry for debugging but not raw audio by default.
- cost: Negligible compute and storage overhead for metadata; resampling is local CPU work. No additional model API calls. Firmware work may require a release.  ·  latency: Typically under 20 ms local processing; negotiation adds one control round trip at session start, not per audio chunk.
- security: Only format metadata crosses the relay by default; audio retention remains governed by existing retention controls. Avoid including speech content in telemetry.
- depends on: A pendant-side capture-rate diagnostic/negotiation event; A shared pipeline event schema for input and output format provenance; The pending 24 kHz implementation status confirmation


## What it asked for

_Nothing._
## Its own summary

Established and recorded three live facts: Mac bridge/relay are online but Mac actions are not trustworthy because Accessibility and Screen Recording are missing and input reachability fails; browser extension is offline with 3 queued commands; and audio capture is currently 15,625 Hz while output TTS is 24 kHz, so quality is not end-to-end 24 kHz. Also confirmed host timezone America/New_York. Proposed a readiness-gated cross-surface capability that blocks false-success actions and a typed audio format contract with explicit resampling/provenance.

**Biggest unknown:** Whether the owner intends to grant Accessibility/Screen Recording to the actual AI Pendant Agent binary and reconnect the browser extension; and whether pendant firmware can negotiate/report a 24 kHz capture mode rather than only producing 15,625 Hz input.

