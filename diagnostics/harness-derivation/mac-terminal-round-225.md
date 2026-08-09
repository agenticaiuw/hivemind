# Harness derivation — mac-terminal — round 225

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “take over this,” have the pendant hand my current work to you and later resume it on whichever device is available, without me explaining where I left off."
- **useful because:** This would make the hive feel like one assistant rather than separate tools: the worn button/voice establishes intent, the Mac captures the live app and terminal state, the browser contributes authenticated tab/session context, and the relay keeps a resumable handoff when the Mac sleeps or the pendant disconnects.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Realtime only for the brief spoken acknowledgement; a cheaper background model should normalize the captured UI/browser/terminal state into a task handoff and generate a resume checklist.
- **latency:** Acknowledge in under 1 second; capture in 3 seconds; resume package can finish asynchronously in 10–30 seconds.
- **cost:** About $0.01–$0.05 per handoff, dominated by background summarization; most capture is local structured metadata and should not invoke a model.
- **security:** Authenticated URLs, window titles, and terminal snippets can be sensitive. Keep raw content on the Mac/browser, send the relay only a redacted task package by default, and require explicit opt-in before including page text, clipboard, or terminal output.
- **missing:** A first-class handoff record with source device, captured state, redaction policy, expiry, and resume steps; A Mac capture action that atomically samples foreground app/window, active browser tab metadata, project/branch, and running local job IDs; A browser snapshot command that returns session-scoped metadata without copying page secrets; Relay delivery and conflict resolution when both Mac and pendant reconnect

### "Are both chips actually alive right now? If not, tell me which link or firmware stage failed and collect a diagnostic bundle I can hand to the developer."
- **useful because:** The pendant and ESP32 are physically on this Mac now, but the system currently cannot turn that fact into trustworthy health. A spoken/typed bench check would distinguish enumeration, boot log, framing, audio clocks, and relay registration instead of saying merely “online.”
- **path:** pendant → mac-planner → relay-realtime → dashboard
- **model tier:** Use deterministic parsers for port discovery, bounded UART frames, firmware banners, counters, and timestamps; use a cheap model only to turn parsed failures into a short explanation. Realtime is unnecessary except for the spoken result.
- **latency:** Return a first verdict in 5 seconds; continue a 30-second capture for intermittent framing/audio faults and attach it to the result.
- **cost:** Near-zero model cost for healthy runs; under $0.01 for a failure explanation. The cost is local disk retention and a small bounded capture.
- **security:** UART logs may contain tokens or personal audio metadata. Redact credential-like strings, cap retention to 24 hours, and never upload raw logs to the relay unless the owner explicitly asks.
- **missing:** A real bounded serial reader/parser for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA (the granted schema is unresolved because no serial capability exists); Known-good frame schemas and health thresholds for nRF9160 and ESP32; A diagnostic-bundle route that hashes and links local logs to a job receipt without exposing raw content; A Mac job action that can invoke diagnostics/dual_chip_autocapture.sh and terminate it reliably

### "Keep this task moving while I’m away, but wake me only when you need a decision; if the Mac sleeps or a command fails, resume from the last safe point instead of starting over."
- **useful because:** Today a long shell action cannot be interrupted, jobs do not retry, cancellation is cooperative, and a restart leaves processing records orphaned. This would let the owner delegate real work from the pendant without returning to a dead or duplicated task, while preserving the owner’s deliberate maximum-access policy.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** A cheap background worker should supervise checkpoints, classify transient versus terminal failures, and retry idempotent steps. Realtime is reserved for the one-sentence pendant notification when a human decision is genuinely required.
- **latency:** No extra latency on the first dispatch; detect a failed/disconnected worker within 10 seconds; recover automatically within one retry interval, typically under 30 seconds.
- **cost:** $0.001–$0.02 per supervised task, mostly relay polling and occasional failure summarization; no model call on successful retries.
- **security:** Retries must not duplicate irreversible actions such as sending mail, deleting files, or submitting forms. Persist an action fingerprint and pre/post state, redact command output before relay transmission, and make the pendant say “stalled/needs you,” never “done,” when confirmation is absent.
- **missing:** Wire executionContext’s existing exactly-once/idempotency engine into POST /execute rather than leaving it unused; Close the orchestrator ledger and populate planMeta.jobId so a job and its recovery record join; Boot-time reconciliation of processing jobs and a supervisor that resumes only ledger steps marked runnable; Abortable child processes and typed retry classification, including exit code/signal capture; A relay-to-pendant decision event that carries the blocked step and a concise choice

### "Why do you believe that? Show me the exact chain from what I said, through the Mac and browser work you did, to the answer—without making me search through logs."
- **useful because:** The system has separate receipts, browser provenance, journals, memory findings, and pipeline events, but the owner cannot receive one human-readable, cross-surface proof trail. This would make delegated work trustworthy: every claim would say whether it came from the pendant conversation, a Mac command, an authenticated browser page, or an inference.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic joins and hashes first; use a cheap background model only to summarize the evidence chain. Realtime should read a two-sentence answer on the pendant, with the detailed chain available on the dashboard.
- **latency:** Answer provenance questions in under 3 seconds for recent work; older traces can load asynchronously.
- **cost:** Usually under $0.01, dominated by optional summarization; joins and hashes are local/server-side.
- **security:** Evidence may contain private URLs, terminal output, or page text. Default to source type, timestamp, and redacted excerpt; reveal raw evidence only after an explicit owner request. Preserve source hashes so redaction cannot silently change the claim.
- **missing:** A unified evidence graph linking voice turns, action receipts, browser provenance records, journals, and memory findings; Stable cross-surface correlation IDs propagated from pendant turn through relay job and Mac/browser actions; A claim-trace API that returns cited evidence without exposing unrelated neighboring records

### "Let me say “make this private” and have the whole hive immediately stop speaking sensitive content aloud, pause browser/page capture, and continue only with redacted summaries until I say “private mode off.”"
- **useful because:** The owner wears the interface in public, while the Mac and authenticated browser can hold much more sensitive context than should ever reach a speaker or relay. A single spoken privacy mode spanning pendant audio, relay output, Mac screen capture, and browser observation is a user-facing safety control that does not exist as one coherent state today.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic state propagation; no model is needed except normal task processing after redaction. The pendant should acknowledge locally and the relay should enforce the mode before generating speech.
- **latency:** Local acknowledgement under 300 ms; all surfaces converge within 2 seconds, with fail-closed behavior if the relay cannot confirm receipt.
- **cost:** Negligible per invocation; a small persistent state record and event fanout.
- **security:** Privacy mode must be local-first and survive link loss. The pendant must never claim it is active unless it has a cached local state; relay and Mac must attach the mode to every audio, browser, screenshot, and context operation. Owner must explicitly turn it off.
- **missing:** A signed privacy-state event replicated between pendant, relay, Mac, and browser extension; A hard output/redaction gate before TTS and before capture—not merely a planner instruction; A local pendant privacy indicator and offline state persistence; Browser and Mac capture paths that honor the state consistently


## Changes it proposed to its own stack

### `hardware` — Build the wearable product around a dedicated privacy/status control and a real haptic actuator: a tactile privacy slider or button with a mechanically obvious state, plus a low-power LRA vibration motor. Keep the existing active-edge conversation button unchanged, and expose the privacy control as a separate interrupt to the nRF9160.
- **owner gets:** The owner could silence and privatize the assistant instantly in a meeting or public place without waiting for speech recognition, and receive unmistakable confirmation even when the LED or audio is hard to perceive. This makes the hive safe to wear continuously rather than safe only when the owner remembers a voice command.
- effort: Product-board revision, enclosure redesign, one GPIO interrupt, haptic driver, battery characterization, and firmware state replication; roughly one hardware prototype cycle.  ·  risk: Added power draw and enclosure complexity; accidental slider movement is possible. Use a guarded/tactile control, debounce it, and make the pendant’s local state authoritative until the relay acknowledges it.
- cost: Approximately $3–$10 in prototype BOM depending on actuator and enclosure changes; haptic bursts add tens of milliwatts only while active, with negligible idle draw.  ·  latency: Local privacy indication under 100 ms; remote surfaces still require the event path and should fail closed if disconnected.
- security: Improves privacy by making the control local and physically observable. The system must not rely on a network acknowledgement to enter privacy mode, and must not expose the slider state through untrusted logs.
- depends on: A signed privacy-state event replicated across pendant, relay, Mac, and browser; Capture/TTS gates that enforce the local privacy state; A firmware power and GPIO budget review on the eventual product board


## What it asked for

_Nothing._
