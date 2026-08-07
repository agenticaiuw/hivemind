# Harness derivation — mac-terminal — round 137

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Test the whole pendant setup.”"
- **useful because:** With both boards physically attached today, the owner gets a one-command commissioning check instead of guessing whether a silent failure is the radio, serial link, I2S path, Bluetooth bridge, or relay. It can speak a plain result through the pendant and name the exact failing stage.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal
- **model tier:** background for the deterministic hardware test and report; realtime only if the owner asks follow-up questions by voice
- **latency:** 30 seconds for serial enumeration, loopback tones, and relay heartbeat; up to 2 minutes for a full audio round trip
- **cost:** Near-zero API cost for device tests; at most one small realtime/text request for a spoken explanation. Time is dominated by serial firmware diagnostics, not inference.
- **security:** Serial device identifiers and local diagnostic logs stay on the Mac unless the owner explicitly shares them. Never transmit microphone content during a test; use generated tones and a fixed phrase. Require confirmation before flashing firmware or changing Bluetooth pairing.
- **missing:** A Mac serial supervisor that identifies /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA by USB descriptors; A tiny pendant diagnostic protocol (button/LED, I2S loopback, modem state, firmware version) and matching ESP32 bridge test commands; A relay health-check endpoint that correlates one test run without treating USB attachment as LTE registration; A single typed diagnostic result schema with stage, evidence, and remediation

### "“Use my pendant over USB right now, even though it has no LTE.”"
- **useful because:** The owner can wear/use the real nRF9160 board today: button press and microphone audio travel over the Mac's USB serial link to the relay, and the spoken response returns through the ESP32 Bluetooth audio bridge. This turns the currently attached prototype into a usable local pendant rather than falsely reporting it offline.
- **path:** pendant → mac-terminal → relay-realtime → mac-planner
- **model tier:** realtime for the live turn; background only for reconnect diagnostics and transcript persistence
- **latency:** Under 500 ms from button/audio frame to relay acknowledgment; under 2 seconds to first spoken response. USB framing and buffering, not model time, are the main constraint.
- **cost:** One realtime voice turn per utterance; audio transport is negligible. Avoid duplicate transcription by making the Mac a byte transport, not a second speech recognizer.
- **security:** Pair the two known serial identities to the local agent and encrypt/authenticate the USB session before forwarding audio. Do not claim LTE registration. Keep raw audio ephemeral unless the owner asks for a transcript; disconnect must stop forwarding.
- **missing:** A USB serial transport daemon with framing, device identity, reconnect, and backpressure for both boards; A relay ingress mode accepting a Mac-tethered pendant identity and returning audio packets to the bridge; A bridge routing contract from returned PCM/I2S data to the ESP32 A2DP source; A truthful device state exposed to the pendant LED: USB-tethered, relay-connected, speaking, or disconnected

### "“What am I looking at, and what should I do next?”"
- **useful because:** With the pendant button as the low-friction trigger, the Mac identifies the active Safari tab, the browser extension extracts the authenticated page's relevant state, and the relay speaks a concise answer back through the pendant. The owner gets private-page help without dictating a URL, taking a screenshot, or handing credentials to the cloud.
- **path:** pendant → mac-terminal → browser-extension → relay-realtime → mac-planner
- **model tier:** realtime for the short spoken question and answer; background model for large-page extraction and citation compression
- **latency:** 1–3 seconds for tab identity and targeted extraction, then under 2 seconds to first audio. Do not upload screenshots by default.
- **cost:** One small realtime turn plus local/browser extraction; background summarization only when page text exceeds the realtime context budget.
- **security:** The extension must return only the active tab's selected/visible semantic content, URL, title, and source anchors; never all tabs or passwords. Keep extraction on the Mac when possible, redact secrets, and clearly say when the page is unavailable or stale. Any form mutation remains a separate explicit request.
- **missing:** A pendant USB/button event bridge to the local agent (usable while the prototype is not LTE-registered); An active-tab identity endpoint shared by mac-planner and browser-extension; A targeted browser extraction command with DOM locators/source spans rather than screenshot-only output; A compact spoken-answer envelope carrying citations and freshness back through the audio pipeline

### "“Review what I’m about to commit and tell me the one thing most likely to hurt me.”"
- **useful because:** The owner gets a genuinely cross-surface review: the Mac reads the staged diff and test state, Safari supplies the relevant private issue/PR context, and the pendant delivers one prioritized risk with file-and-line evidence while the owner is away from the screen. This is decision support, not another generic code summary.
- **path:** pendant → mac-terminal → browser-extension → relay-realtime → mac-planner
- **model tier:** background model for diff/test/context synthesis; realtime only to answer the owner's follow-up
- **latency:** 10–30 seconds, with progress spoken if tests are long-running
- **cost:** One moderate background inference over a compact diff and selected page extracts; local git/test work dominates time and no audio transcription is needed unless the owner asks a question.
- **security:** Keep repository contents and authenticated PR data on the Mac whenever possible; send only selected hunks and cited context to the model. Never post, approve, or mutate the PR. Explicitly identify uncommitted/untracked files and stale browser context.
- **missing:** A Mac working-tree snapshot primitive that returns staged diff, impacted tests, and exact commit identity without dumping the whole repository; A browser extraction primitive that binds an issue/PR tab to the current commit and returns only relevant discussion and review requirements; A cross-surface evidence object joining file/line, test output, and private-page citation; A spoken result format that guarantees one ranked risk plus a drill-down command

### "“If my Mac or browser gets stuck while I’m away, recover it and tell me only if I need to intervene.”"
- **useful because:** This gives the owner resilience rather than another status dashboard: a watchdog recognizes a hung local agent, dead browser extension, stalled job, or disconnected audio path, performs bounded, reversible recovery, and uses the pendant only for a concise escalation when recovery cannot be trusted.
- **path:** relay-realtime → mac-terminal → browser-extension → mac-planner → pendant
- **model tier:** cheap background model or deterministic rules for health classification and recovery; realtime only for the escalation conversation
- **latency:** Detect within 30 seconds, attempt recovery within 2 minutes, and speak an escalation immediately after the final failed attempt
- **cost:** Mostly local probes and process supervision; occasional small background summaries. No per-heartbeat model calls.
- **security:** Recovery must be limited to restarting the agent/extension, cancelling stale jobs, reconnecting serial links, and reopening known sessions; never silently resubmit forms or repeat non-idempotent shell commands. Keep a durable incident record and state exactly what was restarted.
- **missing:** A supervisor process independent of the Mac agent that can observe and restart it; A liveness protocol with monotonic heartbeats and job leases across relay, Mac, browser, pendant, and bridge; Idempotency-aware recovery recipes and a durable incident state machine; A pendant escalation packet that works even when the normal voice session is down


## Changes it proposed to its own stack

### `mac-harness` — Add a failure-aware shell execution journal around the existing unrestricted runShell path. For every command, record cwd resolution, start/finish monotonic times, timeout versus exit status, signal, bounded stdout/stderr previews plus hashes, environment keys used (never values), and an explicit reversibility classification. On nonzero exit, automatically capture a read-only machine snapshot and generate a replayable remediation bundle; expose both the raw evidence and the proposed retry as one job receipt. Do not gate, rewrite, or reduce commands.
- **owner gets:** When the Mac says “it failed,” the owner can hear exactly why, where it ran, and what the agent tried next, rather than losing time to invisible cwd, timeout, or permission mistakes. A failed long task becomes recoverable instead of needing to start over.
- effort: Medium: executor wrapper, durable journal schema, bounded output storage, and retry/snapshot worker; integrate with existing job and receipt endpoints.  ·  risk: Secrets can leak through stdout, arguments, or environment-derived output; redact known token patterns and cap previews while retaining hashes. Automatic retries can duplicate side effects, so only retry commands explicitly marked idempotent by the planner; otherwise provide a remediation bundle without executing it. Recover by retaining the current runShell path as fallback.
- cost: No additional model call for successful commands; one cheap background classifier/summarizer only after failures. Small local disk growth per job, with retention limits.  ·  latency: Negligible wrapper overhead; failed commands add roughly 1–3 seconds for diagnostics and receipt generation.
- security: Improves auditability without adding approval gates or narrowing the owner's deliberate FULL_CONTROL_MODE. Store raw evidence locally; relay only redacted summaries unless explicitly requested.
- depends on: Existing /jobs, /jobs/:jobId/receipts, /journal/:jobId, and /ops/snapshot routes; A shared command metadata field identifying idempotence and intended timeout; A bounded local retention/expiry policy for shell output

### `new-surface` — Add a pendant-to-Mac physical presence channel that is deliberately separate from LTE and voice: when the paired pendant is pressed twice in a short interval, the Mac agent receives a signed local event and can attach it to the currently active job, browser tab, or terminal task. The event should support semantic intents such as acknowledge, pause, mark-important, and request-more-detail, with LED/audio feedback from the pendant and an append-only event record. It must survive relay outages and reconcile later without replaying the intent.
- **owner gets:** The owner can control or annotate work without reaching for the Mac or speaking in public—pause a running task, mark a result important, or ask for detail with a physical gesture. It makes the worn device useful as a quiet second channel, not merely a microphone button.
- effort: High: firmware gesture/state machine, authenticated USB/BLE local transport, Mac active-target resolver, job/browser event API, and reconciliation semantics.  ·  risk: Accidental gestures could alter a job; default gestures should be non-destructive annotations, while pause/cancel requires a distinct long press and visible LED confirmation. Lost or duplicated events must be deduplicated by device sequence number. Recovery is append-only replay with explicit target validity checks.
- cost: Negligible model cost; modest firmware and protocol work. A small event journal fits comfortably in flash/RAM if records are compact.  ·  latency: Local acknowledgement under 100 ms; relay reconciliation is asynchronous.
- security: Use device-paired signing keys and monotonic counters; do not treat USB presence alone as authorization. Keep event contents minimal and local until reconciliation.
- depends on: A real pendant input transport independent of LTE registration; A Mac active-target resolver for current job/tab/terminal task; Typed job/browser event ingestion and sequence-aware reconciliation; Firmware gesture and LED feedback support


## What it asked for

_Nothing._
## Its own summary

Round 137 produced four owner-facing proposals: (1) a one-command end-to-end pendant/ESP32/relay commissioning test, (2) USB-tethered live pendant conversation while LTE is unregistered, (3) failure-aware journaling and recovery evidence around unrestricted Mac shell execution without adding gates, and (4) button-triggered “what am I looking at?” help using the active authenticated Safari tab and spoken pendant response. The strongest immediate value is USB-tethered voice plus truthful state, because both boards are physically attached now. The proposal recorder flagged the first, second, and fourth as connective work over existing routes, and flagged shell journaling as close to existing instrumentation; the missing pieces—not the APIs—are the serial transport, device identity/framing, state machine, active-tab bridge, and failure envelope.

**Biggest unknown:** Whether a USB serial supervisor or tethered voice path has already been implemented outside the HTTP route table. I asked unified for a collision check. I still need those implementation pieces, not another route: serial access to /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA, a typed device/test protocol, and a truthful offline/USB state propagated to relay, pendant LED, and spoken receipts. I do not need another permission request this round; existing grants expose observability but the newly granted Mac tool schemas still report no implementation.

