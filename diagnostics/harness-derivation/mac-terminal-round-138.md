# Harness derivation — mac-terminal — round 138

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Press the pendant button to start a work session, do the task on my Mac and in Safari, then press it again to give me a reproducible timeline and a resume point if anything failed.”"
- **useful because:** A physical start/stop boundary turns an otherwise invisible automation run into something the owner can audit and resume. The pendant remains the trusted clock while the Mac sees frontmost apps, shell output, files and browser tabs; the relay can preserve the timeline even if the cable disappears. This is materially different from generic job history: it captures the owner's intent boundary and a resumable checkpoint.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → unified → dashboard-ux
- **model tier:** Use realtime only for the button interaction and concise status; use a cheaper background model to normalize the event timeline and derive a resume plan.
- **latency:** Button acknowledgement under 300 ms over USB; task actions as fast as today; timeline available within 5 s of stop.
- **cost:** About $0.01–$0.05 per completed session for normalization, dominated by transcript/context tokens; raw event capture is local and nearly free.
- **security:** The session may contain clipboard text, private URLs, shell output and filenames. Keep raw events on the Mac by default, upload only hashes/summaries, and require an explicit 'share timeline' action before relay or dashboard display.
- **missing:** Serial button start/stop event bridge from pendant to local-agent; A frontmost-app/clipboard/selection snapshot API with redaction; Checkpoint schema that can replay only unfinished steps without duplicating completed mutations; A dashboard timeline and resume control

### "“If I lose the USB connection while you’re working, keep the unfinished Mac task queued on the pendant and finish it automatically when I plug back in; tell me exactly what was completed and what was skipped.”"
- **useful because:** The pendant is physically real today even without LTE, and USB loss is a normal failure mode. This makes a long task dependable rather than silently stranded: completed steps remain acknowledged, unfinished steps resume once, and the owner gets a truthful result instead of guessing whether anything ran.
- **path:** pendant → mac-planner → relay-realtime → unified → dashboard-ux
- **model tier:** Use a cheap background state machine for checkpointing and reconnection; reserve realtime for the short reconnect/status exchange.
- **latency:** Detect disconnect within 2 s; show queued state on the pendant within 1 s; resume within 5 s of serial reattach.
- **cost:** Negligible API cost for state transitions; $0.01–$0.03 only if a model must re-plan failed steps.
- **security:** A queued command may outlive the owner's original context. Persist only the typed plan, step inputs and hashes—not arbitrary secrets or full shell output—and expire queues after 24 hours unless the owner renews them. Never replay a step marked completed.
- **missing:** Pendant-side durable queue in flash with sequence numbers; Serial reconnect handshake and duplicate-resistant acknowledgements; Mac executor checkpoints with idempotency keys and precondition checks; A relay record that distinguishes disconnected, queued, resumed and permanently failed

### "“When something breaks, press the pendant and say ‘make a bug report’: capture the current Mac app, screen, relevant logs and browser page, turn them into a concise reproducible report, and open a draft in my issue tracker without submitting it.”"
- **useful because:** This uses reach no single node has: the pendant supplies an intentional physical incident marker and timestamp, the Mac can inspect the active app and local logs, Safari can read the authenticated issue tracker, and the relay can correlate and summarize evidence. It turns the moment of failure—when context is otherwise lost—into a ready-to-review report.
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay-realtime → unified → dashboard-ux
- **model tier:** A cheaper background model should extract and redact logs; use realtime only to acknowledge capture and ask one missing-detail question.
- **latency:** Capture acknowledgement under 500 ms; local evidence bundle under 10 s; draft report under 30 s.
- **cost:** $0.02–$0.10 per incident, dominated by screenshot/log summarization; local capture and hashing are negligible.
- **security:** Logs and screenshots can contain credentials, tokens and private customer data. Redact known secret patterns locally, show an evidence manifest and exact draft before any browser mutation, and never submit automatically. Keep the raw bundle local with a short TTL.
- **missing:** Pendant incident-marker event with monotonic timestamp; Mac API for active app/window, bounded logs and screenshot plus secret redaction; Browser tab handoff into the authenticated issue tracker; Evidence bundle schema linking each fact to file/region/URL and a draft-only browser action

### "“Test the pendant and audio bridge”: build or flash the current firmware, run a scripted USB serial hardware check, press/observe the button and LED, exercise bridge audio loopback, and give me a pass/fail report with the failing component and logs."
- **useful because:** The hardware is connected to the Mac now, so this can provide a real answer instead of assuming LTE registration or trusting stale firmware. It combines Mac build/flash tools, both serial devices, pendant I/O, ESP32 audio, and relay reporting—something no server-only or Mac-only planner can truthfully do.
- **path:** pendant → mac-planner → mac-terminal → relay-realtime → unified → dashboard-ux
- **model tier:** Use a deterministic local test runner for flashing, serial protocol checks and waveform/LED assertions; use a cheaper model only to summarize failures. Realtime is needed only for the spoken result.
- **latency:** Discovery under 2 s; non-destructive smoke test under 30 s; full flash-and-test under 3 min.
- **cost:** Near-zero API cost; local CPU/serial work dominates. Optional summary is under $0.02.
- **security:** Flashing can erase configuration and a bad image can make the pendant unusable. Require an explicit test/flash mode distinction, preserve the prior firmware image and serial logs locally, and never claim LTE health when the device is USB-only and unregistered.
- **missing:** A stable serial protocol/test fixture for nRF9160 and ESP32 ports; Typed flash/build/test actions with port identity and firmware backup/rollback; Button/LED observation and audio loopback assertions; A hardware-test report route linked to job receipts

### "“If I long-press the pendant, immediately stop every Mac task this system started, close the private browser tabs it opened, and put the whole hive into a paused state; tell me what was actually stopped when I release.”"
- **useful because:** The owner needs a physical, offline-capable escape hatch when an automation behaves unexpectedly or a laptop is being handed to someone else. A server command cannot reach a disconnected USB pendant, and a Mac UI control cannot reliably stop relay-held work. This gives one unambiguous action spanning pendant, Mac executor, browser sessions and relay state, with truthful accounting rather than a false all-clear.
- **path:** pendant → mac-terminal → mac-planner → browser-extension → relay-realtime → unified
- **model tier:** Deterministic firmware and relay cancellation logic; no model needed for the stop path. A cheap background model may summarize what was interrupted afterward.
- **latency:** Pendant LED acknowledgement under 100 ms; local Mac cancellation under 2 s; relay pause propagation under 5 s.
- **cost:** Negligible per use; storage for a cancellation receipt is the only material cost.
- **security:** A false trigger can cancel useful work, so require a distinct long-press pattern and make cancellation idempotent. Do not erase data or kill unrelated user processes; scope it to jobs carrying this system's execution identity. Preserve a local receipt containing stopped, completed and unknown steps.
- **missing:** Firmware long-press event and local acknowledgment even without relay; A job cancellation protocol that reaches shell processes, browser actions and delegated planners; Execution identity and process-group ownership for every launched Mac task; Browser session close/pause endpoint and a durable hive-paused state; A post-cancel reconciliation receipt

### "“Find duplicate downloads and project files across my Mac and Safari, group them by content rather than filename, and leave a reviewable cleanup plan with safe quarantine actions—do not delete anything.”"
- **useful because:** Filename-based cleanup misses duplicates created by browser downloads, exports and renamed project copies. The Mac can hash local files, Safari can identify the originating tabs and download context, and the relay can produce a compact review queue that survives the browser or USB link going away. The owner gets reclaimed space without irreversible deletion or guessing which copy mattered.
- **path:** mac-terminal → mac-planner → browser-extension → relay-realtime → unified → dashboard-ux
- **model tier:** Use local deterministic hashing and metadata grouping; use a cheap background model only to label ambiguous clusters and explain likely canonical copies.
- **latency:** Start reporting within 2 s; incremental scan for 100 GB within 2 min; review plan available as clusters arrive.
- **cost:** No model cost for hashing; optional ambiguity labeling under $0.03 per scan. Local disk I/O dominates.
- **security:** File paths, document names and browser URLs are sensitive. Keep hashes and raw metadata on the Mac, redact paths in relay summaries, never upload file contents by default, and quarantine to a dated local folder with an undo manifest.
- **missing:** A bounded local file-index/hash action with resumable scans; Safari download provenance extraction tied to tab/session IDs; Cluster and canonical-copy scoring with a reviewable dashboard; Quarantine/restore operations with content hashes and collision checks

### "“While I’m away from the Mac, turn important Mac and browser events into a small tactile queue on the pendant: blink patterns identify the source, a button press marks one read, and when I reconnect, give me the exact underlying event—not just a generic notification.”"
- **useful because:** The pendant can be worn and physically connected today, while the Mac and browser are where events occur. This gives the owner an interruption-light channel for completion, failure, and urgent private-page changes without opening a microphone or relying on LTE. Acknowledgement and exact-event retrieval prevent notifications from becoming an unaccountable stream of badges.
- **path:** pendant → mac-terminal → mac-planner → browser-extension → relay-realtime → unified
- **model tier:** Deterministic event prioritization and queueing; a cheaper background model may collapse duplicates. No realtime model is needed for the notification path.
- **latency:** USB event-to-LED under 500 ms; reconnect synchronization under 3 s; exact event detail available on demand within 10 s.
- **cost:** Negligible API cost and tiny local storage; optional duplicate clustering costs under $0.01/day.
- **security:** Notification patterns can leak sensitive categories to bystanders. Use owner-configurable generic patterns, keep payloads off the LED, encrypt queued details, expire stale events, and require the Mac connection for full text.
- **missing:** A pendant flash/vibration pattern protocol and persistent acknowledged sequence numbers; Mac and browser event adapters with severity/source and privacy labels; Offline queue synchronization over serial with duplicate suppression; A detail-fetch route that resolves a tactile event to its cited job/page evidence


## What it asked for

_Nothing._
## Its own summary

Round 138 produced four owner-facing ideas, led by a physical pendant-bounded work session with resumable checkpoints, USB-disconnect queue/resume, incident-to-draft bug reports, and a real two-board flash/serial/audio hardware self-test. The shell observability proposal was correctly rejected as already covered by an existing execution envelope, so I did not rephrase it. The most concrete new near-term capability is the hardware self-test: both USB devices are live on this Mac even though LTE is not registered.

**Biggest unknown:** The exact serial protocols and safe flashing/rollback commands for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA are still unknown. I also still lack an implemented serial executor/test-fixture tool; the granted Mac diagnostic/action schemas are explicitly unimplemented, and my earlier requests for USB-link truth, disconnect caching, and device button skills remain queued.

