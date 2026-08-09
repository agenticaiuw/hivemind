# Harness derivation — mac-terminal — round 174

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Make the pendant audio sound right end to end, then tell me if it passed.""
- **useful because:** The owner explicitly wants the 24 kHz superwideband path shipped. This turns today's physically connected nRF9160 + ESP32 into a one-command acceptance test: capture known audio, exercise USB/relay/codec/playback, measure underruns, latency and packet loss, and speak one truthful pass/fail with the failing stage.
- **path:** pendant → relay-realtime → mac-planner → mac-vision
- **model tier:** background for the automated test and measurements; realtime only for the owner's short spoken verdict
- **latency:** 30–90 seconds for a full loop; under 2 seconds for the final spoken verdict once measurements exist
- **cost:** About $0.01–$0.05 per invocation if relay transcription/analysis is needed; most work is local serial capture and deterministic metrics
- **security:** The test emits synthetic audio and timing data, not microphone content. Require explicit spoken start because it drives playback and occupies the audio path; keep raw frames on the Mac unless the owner asks to upload them.
- **missing:** A Mac typed action that opens both USB serial devices and runs a bounded audio fixture without arbitrary shell parsing; A relay test endpoint that correlates pendant turn ID, codec mode and bridge acknowledgements into one report; A firmware test mode that accepts a deterministic tone/chirp and returns sequence, underrun and decode counters

### ""The pendant audio broke—file the bug report for me.""
- **useful because:** The pendant already has a captured owner idea to file its own bug reports from UART logs. This makes that real: the worn device marks the failing turn, the Mac collects bounded serial/bridge logs and environment facts, relay redacts secrets and groups the failure with recent job/audio receipts, then drafts a reproducible issue with an attached minimal trace.
- **path:** pendant → mac-planner → relay-realtime → mac-vision
- **model tier:** background model for clustering and writing the report; realtime only to acknowledge that a report was filed
- **latency:** 5 seconds to capture and persist the trace; under 20 seconds to produce a draft issue
- **cost:** <$0.03 per report; local log collection dominates neither tokens nor network
- **security:** UART can contain transcripts, bearer tokens or paths. Redact credentials and default to timing/counters plus a short owner-selected window; never upload the full ring without confirmation. Filing externally must remain a draft until owner confirms.
- **missing:** A firmware crash/failure marker that atomically stores turn ID, reason and a small UART cursor; A Mac serial collector for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA with byte/time bounds; A relay report route that accepts redacted trace bundles and returns a reproducibility summary

### ""While I'm wearing it, keep a live engineering notebook of what the pendant and Mac actually did, and let me ask what changed.""
- **useful because:** Today jobs, ledgers, pipeline events and serial reality are split. A cross-node session ledger would answer useful questions like "did that audio retry happen before the bridge stalled?" with a time-ordered causal timeline, rather than another opaque success/failure sentence. It is especially valuable while the hardware is USB-attached and rapidly changing.
- **path:** pendant → mac-planner → relay-realtime → unified
- **model tier:** background model compacts events into durable daily summaries; realtime model only answers a short timeline query
- **latency:** Events append locally in milliseconds; a spoken query should answer in 2–4 seconds
- **cost:** <$0.01 for ordinary queries; storage and event transport dominate
- **security:** Persist event metadata (IDs, counters, durations, app/project) by default, not audio or command secrets. Make raw trace retention a separate owner-controlled setting.
- **missing:** A shared event envelope with monotonic sequence plus wall-clock estimate across pendant, bridge, Mac job and relay; A Mac route that tails serial and job receipts into that envelope without losing events on restart; A relay query/index endpoint that joins pipeline IDs, job IDs and pendant turn IDs

### ""Take the change I just described from my pendant all the way to a reviewed pull request, and tell me only when it is ready to merge.""
- **useful because:** The owner can currently ask the Mac to run commands and the browser to inspect pages, but cannot hand off one intent across spoken capture, a working tree, authenticated code-host browser state, tests, review evidence, and a durable status. This would turn the pendant into a genuine software delivery control surface rather than a command launcher.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** background model for test/review orchestration and evidence synthesis; realtime only for short status replies
- **latency:** Minutes for tests and browser review; immediate acknowledgement and resumable progress after every stage
- **cost:** $0.05–$0.30 per delivery depending on model review and browser interaction; compute/test time dominates
- **security:** The browser session may expose private repositories and review comments. Keep source and credentials on the Mac/browser, send the relay only hashes, stage results, and the minimum spoken summary. Creating a branch is automatic; pushing or submitting the PR should require explicit confirmation.
- **missing:** A durable cross-surface delivery state machine joining pendant turn, Mac job, browser command, commit and review IDs; Browser actions for authenticated diff creation, test-status collection, and draft pull-request composition; Mac receipts that include repository revision, changed-file digest and test command result rather than only free-form output; Relay job status that can resume a delivery after Mac, browser, or LTE interruption

### ""Show me where my wearable connection is unreliable, and tell me what to change so conversations stop dropping.""
- **useful because:** The system has a wearable, a USB bridge today, and an LTE path later, but no owner-facing explanation of transport failures over time. A coverage-and-reliability map would correlate pendant acknowledgements, bridge serial gaps, radio registration, audio underruns, and Mac network state into actionable advice such as moving the bridge, changing a USB cable, or preferring LTE in a location.
- **path:** pendant → relay-realtime → mac-planner → unified
- **model tier:** background model for daily aggregation and diagnosis; realtime only when the owner asks for the current recommendation
- **latency:** Milliseconds for counters; a daily report in under 10 seconds; immediate warning after a repeated failure pattern
- **cost:** <$0.02 per daily report; local aggregation and retention dominate, not inference
- **security:** Store coarse location/context labels only if available; default to timestamps, transport type, signal/ack metrics, and device identifiers. Never retain microphone content for this feature.
- **missing:** A durable transport telemetry record emitted by pendant and bridge with sequence numbers and reason codes; A Mac collector that samples USB presence, serial framing errors, network state, and audio deadlines; Relay aggregation keyed by device and transport session, with retention and owner-readable recommendations

### ""When I say 'do this later', hold the whole task until the right machine, browser session, network, and power state are available, then finish it without losing what I meant.""
- **useful because:** Today an interrupted spoken request becomes a job or an offline queue, but the owner cannot express execution conditions such as 'only while charging', 'when Safari is authenticated', or 'when the pendant is back on USB'. This capability makes deferred intent dependable across the wearable, sleeping relay, Mac, and browser instead of forcing the owner to restate it.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** background model evaluates conditions and plans resumptions; realtime model only captures the intent and reports state
- **latency:** Under 2 seconds to persist the intent; execution begins within one polling interval after all predicates become true
- **cost:** <$0.03 per deferred task; most invocations are deterministic predicate checks
- **security:** Conditions and task payloads may contain private URLs, files, or credentials. Encrypt the payload at rest, keep browser secrets inside the extension, expire stale intents, and require confirmation immediately before irreversible actions.
- **missing:** A durable conditional-intent schema with expiry, dependencies, and exactly-once completion semantics; Pendant storage for the owner’s original intent and a concise local queued state; Relay scheduler that wakes or polls for device/session predicates; Mac and browser heartbeats exposing charging, USB, authentication, project and network predicates


## Changes it proposed to its own stack

### `hardware` — Replace the prototype nRF9160 audio path with a product pendant that has a second high-performance application core or dedicated audio DSP, while retaining the LTE-M modem; give the audio side enough SRAM for simultaneous 24 kHz Opus encode/decode, jitter buffering and USB diagnostics without time-slicing the modem/control loop.
- **owner gets:** The owner gets natural full-bandwidth speech instead of a prototype that spends roughly 87% of one core on encode plus decode and can glitch when radio, storage or recovery work arrives. It makes the requested 24 kHz path reliable while preserving button responsiveness and truthful offline behavior.
- effort: High: select a modem-plus-audio architecture, port fixed-point Opus and bridge firmware, redesign the board and power tree, then run the proposed end-to-end acceptance fixture against real hardware.  ·  risk: New silicon and RF/audio board risks, codec timing regressions and longer bring-up. Keep the existing nRF9160 pendant as a USB reference device and require bit-for-bit transport tests plus automatic fallback to the current 16 kHz mode.
- cost: Prototype engineering is substantial; rough added BOM $15–$40 per unit depending on DSP/MCU and board changes. Audio DSP raises active draw perhaps 50–150 mW, but avoids pathological CPU contention and retransmission.  ·  latency: Lower and more predictable audio latency; enough headroom for a 20–60 ms jitter buffer and live diagnostics without stealing decode deadlines.
- security: No new cloud data by itself. A separate audio processor must have signed firmware and avoid retaining PCM beyond the active buffer.
- depends on: End-to-end 24 kHz audio acceptance capability; Firmware counters for underrun, decode deadline and transport acknowledgement; A measured power budget for the modem plus audio workload


## What it asked for

_Nothing._
