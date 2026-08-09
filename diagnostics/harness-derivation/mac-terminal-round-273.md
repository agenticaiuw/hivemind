# Harness derivation — mac-terminal — round 273

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Tell me, from the pendant, whether both chips on my Mac bench are alive right now. If I say 'start a bench capture', collect synchronized nRF9160 and ESP32 UART logs, detect boot/heartbeat/audio-frame markers, and speak the first concrete fault instead of dumping raw logs."
- **useful because:** The hardware is physically connected today, but the system cannot currently answer whether the wearable and audio bridge are alive without manual terminal work. This gives the owner a one-sentence bench truth and makes bring-up observable through the same voice surface they will use in the finished product, without pretending USB is a product transport.
- **path:** pendant → relay → mac-terminal → mac-planner
- **model tier:** Use deterministic shell parsing and a cheap background model for marker extraction; use gpt-realtime-2.1 only to speak the result. Escalate to gpt-5.6-luna when logs show an unknown crash or framing mismatch.
- **latency:** Health answer under 3 seconds from a button/voice request; capture starts under 1 second and reports first heartbeat within 5 seconds. Stream only summarized counters during capture, with full logs retained locally.
- **cost:** Near-zero for health and known markers; about $0.005-$0.02 for an anomalous-log summary. Dominant cost is a single background model call on failure.
- **security:** Read-only UART access and local log files only; no LTE registration assumption and no USB data forwarded as wearable telemetry. Cap log retention and redact payload bytes before any relay upload. Starting capture writes files, so the spoken command must clearly confirm that it began and give the local path.
- **missing:** A real bounded serial reader/health route; the current mac_usb_serial_diagnostics grant is unresolved; A stable framed diagnostic protocol with heartbeat, firmware version, audio counters, and CRC; A local action that starts/stops the existing dual_chip_autocapture.sh and parses both logs; A relay event schema for summarized bench health and a voice response path

### "When I say 'package what just went wrong', gather the failed Mac job, its local logs, the active project and window, and the current authenticated browser tab into one local incident bundle; give me a short spoken diagnosis and a stable bundle ID I can refer to later."
- **useful because:** Failures currently scatter across job output, activity logs, browser state, and the owner's memory. A single, timestamped incident bundle lets the owner resume a complex task from the pendant and lets another hive node investigate without asking them to reproduce the problem.
- **path:** pendant → relay → mac-terminal → mac-planner → browser
- **model tier:** Use deterministic collection and redaction first; gpt-5.6-luna summarizes only the collected metadata and selected log excerpts. gpt-realtime-2.1 speaks the diagnosis and bundle ID.
- **latency:** Acknowledge immediately, finish collection in under 8 seconds, and speak a first diagnosis within 12 seconds. If Safari is unavailable, complete the local bundle and explicitly mark browser context missing.
- **cost:** $0.005-$0.03 per incident, dominated by one short summarization call; storage is a few hundred KB locally and should not require cloud upload.
- **security:** Browser tabs may contain authenticated secrets. Store the bundle locally by default, redact cookies/tokens/form values, include URL/title and provenance rather than page bodies, and require an explicit separate request to share any excerpt remotely. The bundle must record collection time and missing sources so it never implies complete evidence.
- **missing:** A first-class incident-bundle route that atomically snapshots job, journal, activity log, and browser provenance; A browser snapshot metadata endpoint that excludes page content and credentials; A durable bundle index searchable by spoken bundle ID; A relay response event carrying partial-completion and redaction status

### "If the bench audio bridge or pendant firmware crashes during a test, recover it for me: stop the stale capture, restart the affected process or reset the USB device when possible, verify fresh heartbeats from both chips, and tell me whether the recording test can continue."
- **useful because:** A dead bridge currently turns a physical test into a manual terminal session and leaves the owner unsure whether old audio frames are still being consumed. Recovery that is tied to fresh counters—not merely a process exit—gets the owner back to a trustworthy test quickly and prevents stale audio from being mistaken for live operation.
- **path:** pendant → relay → mac-terminal → mac-planner
- **model tier:** Deterministic watchdog and shell recovery state machine for known scripts and USB reset operations; gpt-5.6-luna only chooses among documented recovery recipes when the fault signature is unknown. gpt-realtime-2.1 speaks state transitions.
- **latency:** Detect stall within 2 seconds, attempt one recovery within 10 seconds, and declare trustworthy only after two consecutive heartbeat intervals. Never claim recovery from process exit alone.
- **cost:** Usually no model cost; $0.005-$0.02 only for an unknown-log explanation. Local disk and USB operations dominate time, not API spend.
- **security:** Recovery can reset hardware and discard in-flight test data. Keep the last log path, preserve the pre-reset tail, mark the exact reset/restart operation, and never erase or overwrite captures automatically. Do not use this path as an LTE or production transport; label it bench-only.
- **missing:** A typed bench recovery action for stopping/restarting capture and selecting the named USB device; A device reset mechanism or documented safe reset command for each chip; Fresh-heartbeat verification tied to firmware counters rather than process liveness; A recovery receipt linking the old capture, reset, new capture, and final health verdict

### "When I ask 'is it really done?', verify the result across every surface involved instead of trusting a green job status: confirm the Mac process exited successfully, the expected file or state exists, the browser session reflects the change when relevant, and the pendant receives a matching completion. Tell me what was verified and what remains unproven."
- **useful because:** Today a completed job can mean only that a command returned, while the real-world result may be missing, stale, or invisible to the browser and pendant. The owner should be able to distinguish 'the agent stopped working' from 'the requested outcome is true' without manually checking several devices.
- **path:** pendant → relay → mac-terminal → mac-planner → browser
- **model tier:** Use deterministic postcondition checks and route-specific validators first; use gpt-5.6-luna only to choose or explain validators for an unfamiliar task. Use gpt-realtime-2.1 for the concise spoken verdict.
- **latency:** For local jobs, produce a verdict within 3 seconds after completion. Browser verification may take up to 10 seconds, with an immediate partial verdict while it runs. Never claim success when a required surface is unavailable.
- **cost:** Usually below $0.01 because checks are deterministic; an unfamiliar-task explanation may add $0.01-$0.03. The dominant cost is browser/Mac round trips, not inference.
- **security:** Verification must read only the minimum required state and must not submit forms or mutate browser sessions. Store claim, validator, timestamp, and evidence digest locally; do not copy authenticated page contents to the relay. Explicitly report unavailable or stale evidence rather than inferring success.
- **missing:** A postcondition/verification plan attached to each action intent rather than only an action list; Typed validators for process exit, filesystem state, browser DOM/state, and pendant acknowledgment; A cross-surface evidence record that joins job ID, browser command ID, artifact digest, and pendant turn ID; A spoken verdict schema distinguishing verified, partially verified, contradicted, and unknown

### "If the Mac, browser, and pendant disagree about what happened, interrupt me with the contradiction instead of choosing a convenient answer: say which sources disagree, freeze any follow-up automation, and let me ask 'show me the evidence' or 'continue with the safest interpretation.'"
- **useful because:** A stale browser tab, a lost relay acknowledgment, and a successful local command can currently produce three incompatible stories with no unified contradiction state. The owner needs uncertainty surfaced before a duplicate message, purchase, deletion, or other irreversible follow-up occurs.
- **path:** pendant → relay → mac-planner → mac-terminal → browser
- **model tier:** Deterministic source comparison and freshness rules first; gpt-5.6-luna explains an unfamiliar contradiction and proposes non-mutating investigations. gpt-realtime-2.1 delivers the interruption and accepts the owner's next spoken choice.
- **latency:** Detect contradictions within 2 seconds of receiving the last source update. Speak a concise warning immediately, then gather evidence asynchronously in under 10 seconds. Do not silently resume automation while contradiction remains unresolved.
- **cost:** Near-zero for freshness, IDs, hashes, and acknowledgment comparisons; $0.01-$0.03 only when a model must interpret semantic disagreement. Local evidence storage is small.
- **security:** The interruption must reveal only redacted source summaries, not authenticated browser contents or secrets. 'Safest interpretation' must mean a non-mutating inspection, never an automatic destructive choice. Preserve the contradictory records and timestamps for later audit.
- **missing:** A shared contradiction record keyed by intent and turn ID; Freshness and identity metadata on browser results, Mac receipts, relay events, and pendant acknowledgments; A non-mutating evidence drill-down route usable from the pendant; A unified automation stop/resume state that survives relay or Mac restarts

### "After any multi-step request, tell me what you deliberately did not do: skipped actions, unavailable devices, unverified assumptions, and side effects that may still be pending. Let me ask 'what remains?' and get a concrete continuation list rather than a generic success message."
- **useful because:** The current system reports executed actions more readily than omitted or unverified ones. That makes partial completion look complete, especially when the browser, Mac, relay, or pendant drops out mid-task. An explicit negative-result report is what lets the owner safely continue without repeating work or assuming a side effect happened.
- **path:** pendant → relay → mac-planner → mac-terminal → browser
- **model tier:** Build the omission set deterministically from the requested plan, action ledger, cancellations, unavailable surfaces, and postcondition results. Use gpt-5.6-luna only to turn it into a prioritized continuation list; gpt-realtime-2.1 speaks the short summary.
- **latency:** Speak a first 'done / not done' split within 3 seconds of the last action. Generate the detailed remainder list within 8 seconds. Never hide an unknown behind a completion phrase.
- **cost:** Usually under $0.01 because the core is ledger comparison; $0.01-$0.03 for prioritizing ambiguous continuation steps. No additional browser data is needed beyond existing result metadata.
- **security:** The report must distinguish not attempted, attempted-but-unverified, failed, and completed. It must not expose sensitive browser values merely to explain an omission. Continuation suggestions must be non-mutating until the owner explicitly requests them, and must retain original intent IDs to prevent duplicate submissions.
- **missing:** A plan-to-execution ledger that records intended steps before dispatch and joins them to actual receipts; A standardized omission taxonomy and durable remainder list; Cross-surface freshness and postcondition metadata; A pendant-readable continuation API keyed by intent ID


## What it asked for

_Nothing._
