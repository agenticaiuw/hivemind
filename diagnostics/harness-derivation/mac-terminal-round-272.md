# Harness derivation — mac-terminal — round 272

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Make the pendant's replies sound genuinely wideband, and if the link or bridge cannot sustain 24 kHz, tell me immediately and continue intelligibly instead of dropping the turn.”"
- **useful because:** The owner gets a perceptible audio improvement now, with an honest fallback rather than silent underruns. It exercises the real USB-connected nRF9160 and ESP32 today, while preserving the same behavior when LTE replaces USB.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Realtime only for turn/audio control; a cheap background worker runs codec telemetry aggregation and nightly bench reports.
- **latency:** Audio control decisions under 100 ms; no extra conversational turn latency. The 24 kHz decode path already spends ~25.4 ms per 60 ms packet, so budget is dominated by codec CPU and bridge buffering.
- **cost:** Negligible per turn beyond existing realtime audio; background reports are a few cents/day at most. Engineering cost is substantial: synchronized framing, capability negotiation, jitter-buffer tests, and a real bench soak.
- **security:** Audio remains on the existing relay path; telemetry must contain counters and codec modes, never PCM. Dashboard must redact turn text and expose only link quality, underruns, and negotiated rates.
- **missing:** An end-to-end negotiated audio profile shared by relay, nRF9160 firmware, and ESP32 bridge (24 kHz decode, wire-clock conversion, fallback profile).; A bounded cross-chip test harness that injects loss, delay, and clock drift over the live USB serial bench.; Relay metrics and a user-visible route that reports negotiated mode, underruns, and recovery events.

### "“While you are doing something on my Mac, let me say ‘stop’ into the pendant and have the exact running operation stop or honestly report that it could not be interrupted.”"
- **useful because:** Today a voice-initiated Mac job can outlive the owner's intent: cancellation is cooperative between steps and a running shell is not killed. This gives the wearable a real emergency brake and makes the result trustworthy across the pendant, relay, and Mac rather than pretending a queued cancel succeeded.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Realtime handles only the short stop-intent classification and acknowledgement; no expensive model is needed for the actual cancellation or receipt.
- **latency:** Acknowledge the stop in under 300 ms and deliver a definitive stopped/still-running result within 2 s when the child permits termination. The relay must preserve the request if the pendant link drops and avoid duplicate cancels.
- **cost:** Near-zero model cost per stop. Engineering cost is medium-high: propagate an abort signal into child processes, persist an intent ID, reconcile process state, and test USB/LTE loss and restart cases.
- **security:** The stop command itself should be low-risk and limited to the owner's active job/session; never infer a target from an old spoken reference. Persist only job ID, intent ID, timestamps, and outcome, not audio. If the target cannot be unambiguously identified, say so rather than stopping the wrong job.
- **missing:** A real process-level abort path from POST /jobs/:jobId/cancel into run_shell execFile/spawn with AbortSignal and captured termination status.; A pendant cancel-intent event that uses the existing outbox and truthful status beacon, with exactly-once deduplication.; A cross-surface job target resolver tying pendant turn IDs to local job IDs and ledger IDs.; A terminal receipt distinguishing exited, signal-killed, timed out, and cancel-requested-but-still-running.

### "“When the audio glitches, save a small synchronized trace from both chips and the relay, explain the likely cause, and give me a one-sentence report I can act on.”"
- **useful because:** A 24 kHz path is only useful if failures become diagnosable. Instead of asking the owner to reproduce and collect logs manually, the worn device's event timestamp, Mac's two live USB UARTs, ESP32 buffer counters, and relay pipeline telemetry become one bounded incident that can distinguish codec CPU starvation, Bluetooth starvation, packet loss, and clock drift.
- **path:** pendant → mac-bridge → relay → dashboard
- **model tier:** Cheap background model summarizes already-structured counters and short log windows; realtime is used only to announce that an incident was captured. No raw audio needs an LLM.
- **latency:** Capture starts within one audio frame of an underrun and completes within 5 s after recovery. Spoken explanation should be available within 30 s, asynchronously if needed.
- **cost:** Low storage and model cost: a 10–20 s ring of structured UART/relay events per incident, plus a small summary. Engineering cost is medium: clock alignment, bounded ring buffers, redaction, and incident correlation.
- **security:** Store counters and firmware versions by default, not PCM or transcript. UART may contain tokens or personally identifying text, so scrub line patterns before relay upload and keep raw traces local unless the owner explicitly asks to share them.
- **missing:** A synchronized incident ID and monotonic timestamp format emitted by pendant, ESP32, Mac harness, and relay.; A read-only Mac collector that can consume the already-connected nRF9160 and ESP32 UARTs without arbitrary long-running shell jobs.; A relay route to ingest bounded diagnostic frames and a report route that links them to the affected pipeline turn.; A dashboard/audio response that says what was observed versus what is only a hypothesis.

### "“When I walk away from my Mac, hand me the unfinished task on the pendant; let me continue by voice and return the result to the exact browser or editor context when I come back.”"
- **useful because:** Today the Mac, browser, and pendant are separate execution surfaces. The owner loses the thread when leaving the desk: browser sessions remain open, Mac jobs may finish without context, and the pendant cannot resume the exact task. This creates genuine continuity between the device always on the owner and the machine holding authenticated sessions.
- **path:** pendant → mac-bridge → browser → relay → dashboard
- **model tier:** Use a cheap background model to create a compact task handoff capsule; use realtime only for the owner's spoken continuation and immediate confirmations.
- **latency:** Detect a stable away/return transition within 10 seconds. Deliver a spoken handoff in under 3 seconds after the owner asks. Restoring the browser/editor context can take up to 5 seconds.
- **cost:** Low per-use model cost because the capsule contains structured state and a short summary, not full history. Engineering effort is high: presence sensing, task ownership, browser/editor restoration, and conflict handling across concurrent jobs.
- **security:** Never transfer authenticated page contents to the pendant by default. The capsule should contain task title, progress, next safe action, and opaque session references; sensitive page text requires an explicit spoken request. Returning to a page must verify the same browser session and avoid silently submitting or sending anything.
- **missing:** A presence signal that is reliable enough to distinguish away from merely not typing, using Mac proximity/Bluetooth or a pendant link state without recording location history.; A durable task capsule linking relay turn ID, Mac job, browser session, active project, and resumable next action.; Browser and editor restore actions that can reopen the exact context without executing the final mutation.; A conflict resolver for work that completed or changed while the owner was away, with a spoken diff before continuation.

### "“When something you did fails, make a self-contained reproduction bundle, explain the smallest next test, and leave it open in VS Code so I can fix it instead of hearing only ‘failed’.”"
- **useful because:** The current Mac agent collapses shell and multi-step failures into a short message, loses exit-code detail, and cannot reliably connect the failed job to its ledger. The owner should receive an actionable, local reproduction rather than debugging from an opaque receipt.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** A background model extracts the failure signature and proposes a minimal reproduction; realtime only speaks the short outcome to the pendant. The reproduction itself is deterministic code and captured metadata, not generated blindly by the expensive model.
- **latency:** Capture failure metadata immediately; create the bundle within 10 seconds for ordinary commands and within 60 seconds for multi-step UI/browser failures. Never delay the owner's next spoken turn waiting for the bundle.
- **cost:** Low-to-moderate background inference cost per failure. Disk use is bounded per bundle, with automatic expiry. Engineering effort is high because shell, browser, UI, and audio failures need different adapters.
- **security:** Bundles must redact tokens, cookies, environment variables, page contents, and private paths unless explicitly requested. Reproduction must default to dry-run or a fixture and must never replay a destructive mutation automatically.
- **missing:** A failure schema preserving exit code, signal, timeout, argv, cwd, selected environment names, and action-to-ledger/job identity.; Adapters that turn shell, browser, and UI receipts into minimal local reproductions with fixture data.; A redacting bundle writer and retention policy in ~/AI-Pendant-Workspace.; A Mac action that opens the bundle and the relevant source location in VS Code, plus a pendant result linking to it.

### "“While I’m focused, keep interruptions off my pendant; quietly collect them across my Mac, browser, and phone, then tell me only what became urgent and let me deal with the rest later.”"
- **useful because:** The owner currently gets scheduled briefs, but no cross-surface interruption policy. A wearable that is always present should protect attention rather than repeat every notification, while still preventing a genuinely urgent message or system failure from being missed.
- **path:** pendant → mac-bridge → browser → iOS → relay → dashboard
- **model tier:** A small background classifier ranks notifications and maintains the queue; realtime is reserved for urgent alerts and the owner's “what did I miss?” query.
- **latency:** Ingest within 15 seconds of a notification; urgent alerts reach the pendant within 2 seconds. A catch-up summary should answer within 3 seconds from the local queue.
- **cost:** Low background inference cost, dominated by notification volume. Storage is a bounded encrypted queue with automatic expiry; implementation effort is high because Mac, browser, and iPhone sources differ.
- **security:** Notification text is sensitive. Keep raw content local where possible, send only a short urgency rationale to the relay, and never read message bodies aloud in public without a private-mode request. Deleting or replying must remain separate explicit actions.
- **missing:** Notification ingestion from macOS, authenticated browser sessions, and iPhone Mirroring with source and urgency metadata.; A durable, encrypted attention queue keyed by notification IDs with deduplication and expiry.; A focus-state signal from the active Mac project/app plus owner-configurable exceptions for people, systems, and deadlines.; Pendant patterns for urgent versus queued states and a spoken catch-up command that does not require opening the Mac.


## Changes it proposed to its own stack

### `hardware` — Replace the HUZZAH32 audio bridge in the wearable design with a Bluetooth audio bridge that has a hardware 24/48 kHz-capable audio clock, sufficient SRAM for two jitter buffers, and an exposed control channel for underrun counters; retain the current ESP32 as the bench adapter while the new bridge is validated.
- **owner gets:** The owner hears stable wideband speech instead of a 15.625/24-to-31.25-to-44.1 kHz chain whose software resampling and tiny Bluetooth buffers can starve. It also makes clock drift and underruns observable rather than intermittent mysteries.
- effort: High: select a production module, redesign the bridge PCB/power/audio wiring, implement the control protocol, and run a week-long interoperability soak against the owner's headphones. The existing ESP32 bench path remains usable during migration.  ·  risk: A new Bluetooth stack may lose compatibility with the owner's headphones or add pairing friction. Recover by retaining the ESP32 fallback and negotiating the old SBC/44.1 profile when the new bridge fails capability checks.
- cost: Prototype module and PCB roughly $30–$100, plus a few hundred dollars of bench parts; power likely +50–150 mW depending on Bluetooth module. No per-API cost.  ·  latency: Potentially removes one resampling/buffering stage and can reduce jitter, but a larger buffer may add 20–60 ms. Require a negotiated low-latency profile and measure end-to-end mouth-to-ear latency.
- security: Bluetooth pairing keys and bridge diagnostics must remain local; do not upload headphone identifiers in routine telemetry. Firmware updates need signed images before a production bridge is wearable.
- depends on: The 24 kHz negotiated audio profile proposal; A bounded cross-chip audio incident trace; A production hardware audio-clock and Bluetooth-module selection


## What it asked for

_Nothing._
