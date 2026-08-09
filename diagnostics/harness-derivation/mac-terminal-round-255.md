# Harness derivation — mac-terminal — round 255

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "From the pendant, say “handle this” while I am looking at a Safari page, and have the system carry out the next useful step, then tell me exactly what changed."
- **useful because:** This is the single most useful hive capability: the pendant supplies intent and voice while the browser supplies the authenticated page, the Mac supplies execution, and the relay supplies continuity. It removes the need to narrate URLs, copy page text, or move to the keyboard, while keeping the result grounded in the page actually open.
- **path:** pendant → relay → browser → mac-bridge → dashboard
- **model tier:** Realtime only for the short spoken intent and disambiguation; a cheaper background planner performs page grounding and action planning, with the realtime tier returning the concise result.
- **latency:** Acknowledge locally in under 300 ms; browser snapshot and plan in 2–4 s; execute the first reversible action within 6 s. Ask a spoken clarification only when the page contains multiple plausible targets.
- **cost:** Typically one short realtime turn plus one background planning call; roughly $0.01–$0.05 per invocation depending on screenshot/page extraction. Browser and Mac execution dominate latency, not tokens.
- **security:** The browser session may contain private authenticated data, and the request can cause external side effects. Send only the relevant page snapshot/accessible text to the planner, never cookies; record the source URL, selected DOM target, action, and before/after result. Require explicit confirmation for sending, deleting, purchasing, or publishing; reversible navigation and drafts can proceed without it.
- **missing:** A single cross-surface intent contract that carries pendant turn_id through relay, browser command, and Mac job; Browser-side target grounding that returns a stable target identity and before/after evidence rather than only a click result; A result join that correlates browser command, Mac job, and spoken completion into the pendant status beacon

### "When I come back to my Mac, say “what changed while I was away?” and hear a short, trustworthy delta of only the files, browser sessions, reminders, and scheduled jobs that changed since I left, with anything requiring my attention called out."
- **useful because:** Today the system can inspect individual surfaces, but it cannot give the owner a time-bounded return-from-away answer. This turns the pendant into continuity across the day without requiring the owner to remember which app or task changed.
- **path:** pendant → mac-bridge → browser → relay → dashboard
- **model tier:** Use deterministic collectors and hashes first; a cheap background model clusters and ranks the deltas. Use realtime only to ask a clarification or speak the final short answer.
- **latency:** Capture a departure checkpoint in under 2 seconds and produce the return delta in under 5 seconds; if a source is unavailable, say so rather than silently treating it as unchanged.
- **cost:** Usually one low-cost summarization call over compact change records, under $0.01; storage and hashing are local. No screenshot or full-document upload is needed for ordinary checks.
- **security:** Browser titles and file names can be sensitive. Keep raw snapshots on the Mac, send only selected deltas, redact secrets and document contents by default, and let the owner ask for the evidence behind one item. Never infer that an unchanged inaccessible source is unchanged.
- **missing:** A durable departure/return checkpoint tied to pendant presence or an explicit spoken marker; Mac file, browser, reminder, and job change collectors that emit stable fingerprints plus source freshness; A cross-surface delta schema with unavailable, changed, unchanged, and suspected-partial states; A compact evidence drill-down the pendant can read aloud without exposing unrelated private content

### "Give me a research answer that keeps working after I close the lid: gather sources in my authenticated browser, save a cited brief locally, and tell me on the pendant when it is complete or genuinely blocked."
- **useful because:** Today a multi-step browser task is tied to an active Mac agent and the owner has no dependable promise that closing the lid, losing the bridge, or losing a tab will produce either a finished artifact or an honest blocked result. This makes research a deliverable instead of a fragile live session.
- **path:** pendant → relay → browser → mac-bridge → dashboard
- **model tier:** A cheap background worker performs collection, deduplication, and citation extraction; realtime is used only for the initial request and the final one-sentence notification.
- **latency:** Accept and persist the task in under 1 second; resume within 30 seconds of the Mac/browser returning; deliver when complete rather than holding a live conversation open. A stalled task must be marked blocked within a bounded deadline.
- **cost:** One background planning call plus per-source extraction, roughly $0.03–$0.20 depending on source count; browser and local storage dominate. No repeated realtime context should be paid for while the owner is away.
- **security:** Authenticated pages and resulting notes are private. Keep cookies in the browser, allowlist source hosts per task, store citations and small evidence capsules rather than whole pages, encrypt the pending task capsule at rest, and require confirmation before publishing or sending the brief.
- **missing:** A durable task capsule with resumable browser checkpoints, source list, deduplication state, and deadline; A worker that can reconnect to a browser session after Mac sleep/restart and distinguish expired authentication from ordinary navigation failure; Atomic local artifact writes with citation-to-source provenance and a final integrity receipt; Relay notification semantics that distinguish complete, partial, expired-session, and permanently blocked

### "Let me say “quiet until three, except urgent work or a safety issue,” and have the pendant, relay, Mac, and browser all honor that rule, then give me a concise digest of what was held back."
- **useful because:** The owner currently has no single interruption policy spanning spoken alerts, Mac jobs, browser watches, and scheduled routines. This would make the pendant useful during focus time instead of either interrupting constantly or hiding important events.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Compile the spoken rule deterministically into typed predicates; use a cheap background classifier only to rank ambiguous incoming events. Realtime is limited to setting the mode and speaking the digest.
- **latency:** Mode takes effect in under 500 ms and survives link loss; incoming events are classified in under 2 seconds. At expiry, read a digest in one short turn, with no flood of stale notifications.
- **cost:** Near-zero for rule evaluation; occasional low-cost classification, under $0.01 per event batch. The main cost is local durable state, not model tokens.
- **security:** Urgency classification can suppress something important. Always surface safety/system failures, show the active mode and expiry on the pendant, never let a browser site redefine urgency, and retain only event metadata in the digest unless the owner asks for details.
- **missing:** A shared interruption-policy record consumed by relay events, routines, browser watches, and Mac job completion; Typed urgency and expiry semantics with a safe non-suppressible class; A durable held-event queue with deduplication and digest grouping; Pendant feedback for active quiet mode and an offline expiry clock


## Changes it proposed to its own stack

### `integration` — Build a bench-to-wearable 24 kHz audio acceptance path that runs the connected nRF9160 and ESP32 together: timestamp UART health, inject a known 24 kHz spoken test vector through the bridge, capture the decoded output, measure end-to-end latency, packet loss, underruns, resampler drift, and CPU headroom, and publish a pass/fail receipt. Fail closed on stale or duplicated frames and automatically produce the smallest diagnostic slice (turn ID, sequence gap, codec timing, and both UART excerpts) for the owner.
- **owner gets:** The owner gets a trustworthy answer to “does the audio path actually work?” instead of a demo that sounds good once. It is the shortest route to shipping the requested superwideband path and catches the current danger: decode already consumes about 25.4 ms per 60 ms frame and encode/decode together use roughly 87% of one core.
- effort: Medium: a Mac bench runner and framing parser, a deterministic audio fixture, bridge loopback hooks, and one relay-side receipt schema. Run it nightly and before firmware changes.  ·  risk: A test vector or bridge loopback can pass while radio conditions fail; label bench results as bench-only and separately add loss/jitter scenarios. Never let the fixture feed the owner's microphone or speaker. Recover by retaining raw bounded UART excerpts and rerunning only the failed stage.
- cost: Negligible API cost; local CPU and disk for short WAV/PCM fixtures and bounded logs. No new wearable BOM cost for the bench version.  ·  latency: A 30–60 second acceptance run, with the first health verdict in under 5 seconds.
- security: All test audio is synthetic or checked in locally; no microphone capture, cloud upload, or owner speech leaves the Mac.
- depends on: An implemented bounded USB UART reader for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA (the granted schema is unresolved today); A stable diagnostic frame format from both firmware images; The existing POST /pipeline/audio path and cloud-relay/opusTranscode.js test hooks

### `mac-harness` — Add an automatic command-repair loop for failed Mac jobs without reducing FULL_CONTROL_MODE: when a run_shell action fails, preserve the original command, exit status/signal, cwd, elapsed time, and bounded stderr, then let a cheaper repair planner choose one of three explicit recoveries—retry unchanged once, retry after correcting a discovered cwd/path, or stop and explain the blocker. Give the repaired attempt a new step ID linked to the original, and have the pendant report “retrying” versus “blocked” rather than a generic failure.
- **owner gets:** A spoken request should not die because the agent started in the wrong directory, hit a transient bridge disconnect, or used a stale path. The owner gets useful completion or a precise reason, while still retaining maximum unrestricted shell power and no confirmation gate.
- effort: Medium: capture real process termination details, add process-group-aware bounded retry, expose a repair-plan endpoint, and link attempts in the job/ledger records. Start with path/cwd and transient local-agent failures; do not auto-retry arbitrary destructive commands.  ·  risk: Blind retries can duplicate side effects. The repair planner must classify whether the command is observational, idempotent, or already partially applied; for uncertain mutations it should stop with a suggested command, not repeat it. A killed process group must be verified before retrying.
- cost: One small background planning call only on failure; usually under $0.01. Local storage increases by bounded per-attempt diagnostics, not full environment dumps.  ·  latency: Successful commands are unchanged. Failed commands gain about 1–3 seconds for diagnosis and at most one bounded retry; cancellation must terminate the actual child process group rather than merely setting the cooperative job flag.
- security: Do not record the inherited environment or secrets. Redact token-shaped values from stderr and persist only command metadata, exit code/signal, cwd, and bounded output. Keep the owner's deliberate unrestricted execution policy unchanged.
- depends on: POST /execute; GET /jobs/:jobId; GET /jobs/:jobId/receipts; GET /journal/:jobId; The existing action ledger and durable pendant-jobs.json store; A real process-group cancellation path in computerControl.js

### `hardware` — Replace the prototype's 15,625 Hz I2S capture clock with a product audio front end that can capture 24 kHz speech bandwidth (at least 48 kHz I2S sampling, with a clock tree and DMA budget sized for simultaneous Opus encode and 24 kHz playback). Keep the current nRF9160/ESP32 boards as the bench compatibility mode, but make the negotiated audio profile explicit so the relay never labels 15.625 kHz capture as superwideband.
- **owner gets:** The requested 24 kHz superwideband path will be honest in both directions. Today playback decodes at 24 kHz but the microphone captures at 15,625 Hz, so the owner can hear a wide reply while sending permanently bandwidth-limited speech. A real front end removes that asymmetry rather than hiding it with resampling.
- effort: High: select and lay out a production mic/clock path, validate DMA and power, retune fixed-point Opus complexity, and add profile negotiation across pendant, relay, and bridge. Prototype first with an external 48 kHz I2S source on the bench.  ·  risk: Higher sample rate increases CPU, RAM bandwidth, radio payload pressure, and battery drain; the current prototype may miss real-time deadlines. Recover by retaining a negotiated narrowband mode and measuring encode timing before enabling the profile by default.
- cost: Prototype external clock/mic: roughly $10–$30. Product BOM increase likely $2–$8 plus PCB revision; power draw may rise by tens of mW depending on the mic and clock.  ·  latency: No intentional conversational latency increase if frames remain 60 ms, but encode budget must be proven under 24 kHz capture plus current ~25.4 ms decode load.
- security: No new data exposure. Audio remains the owner's voice path; profile negotiation and test recordings must not be uploaded without consent.
- depends on: The existing audio_opus.c and cloud-relay/opusTranscode.js profile negotiation; The bench acceptance path proposed above; A product pendant SoC/audio-clock design instead of treating the current Nordic development kit as final hardware


## What it asked for

_Nothing._
## Its own summary

This round produced four non-duplicate proposals: a cross-surface pendant→browser→Mac task handoff with evidence, a real bench acceptance test for the connected audio chips, failure-aware Mac command repair, and a product audio-clock change needed for honest 24 kHz capture. The immediate highest-value path is the audio acceptance test plus explicit profile negotiation; current hardware plays 24 kHz but captures at only 15,625 Hz.

**Biggest unknown:** I still cannot inspect the two physically connected serial devices: mac_usb_serial_diagnostics is granted but unresolved against the live inventory, and the requested run_bench_health_check remains pending/denied. I need an implemented bounded UART reader (or a working shell-based bench runner) and the firmware diagnostic-frame format to validate the 24 kHz path today.

