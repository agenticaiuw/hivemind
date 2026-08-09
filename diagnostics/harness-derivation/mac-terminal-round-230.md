# Harness derivation — mac-terminal — round 230

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Keep me in one voice conversation while I move between the pendant, my Mac, and an authenticated browser tab—continue the same turn, carry out the browser action, and speak back the result without making me repeat myself."
- **useful because:** This is the system's single most valuable cross-node behavior: the pendant supplies presence and audio, the relay preserves the turn, the Mac can act, and the browser contributes sessions the other nodes cannot reach. Today those surfaces exist separately; this would make them feel like one assistant.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Realtime only for the short spoken turn and routing decision; use the cheaper background tier for page extraction and action verification.
- **latency:** Acknowledge on the pendant in under 300 ms, dispatch within 1 s, and speak a concise result within 5 s for a normal browser action.
- **cost:** Usually one realtime turn plus a small background extraction call; roughly $0.01–$0.05 per request, dominated by realtime audio tokens.
- **security:** Browser cookies and page content stay on the Mac/browser bridge; only the minimum extracted result crosses the relay. Sending, purchasing, deletion, or other irreversible browser actions still require the owner's existing confirmation policy.
- **missing:** A stable cross-surface turn_id and replay cursor spanning pipeline audio/events, Mac jobs, and browser command/result records; A relay coordinator that waits for browser completion and streams a concise result back to the pendant; Exactly-once handoff so reconnects do not repeat a click or lose the spoken response; End-to-end 24 kHz audio framing and resumption on the pendant path

### "Run a 30-second bench check of my connected nRF9160 pendant and ESP32 audio bridge, then tell me in one sentence whether the 24 kHz path is healthy and attach the exact fault (frame loss, clock drift, underrun, or wrong firmware) if it is not."
- **useful because:** The hardware is physically present now, and the owner's stated priority is shipping the 24 kHz superwideband path. This turns a pair of UART logs into a decision they can act on instead of requiring firmware expertise or guesswork.
- **path:** mac-terminal → mac-planner → relay-realtime
- **model tier:** Use deterministic host parsing and signal-quality calculations first; call a cheap background model only to summarize an anomalous trace. No realtime model is needed unless the owner asks by voice.
- **latency:** Start capture immediately and return a health verdict in 35 seconds; stream an early 'capturing' acknowledgement in under 1 second.
- **cost:** Near-zero model cost for normal runs; at most a few cents when anomalous logs need summarization. The dominant cost is 30 seconds of USB capture and local DSP.
- **security:** Read-only access to the two explicitly connected USB serial ports; logs remain on the Mac unless the owner asks to share them. Never flash or reset hardware as part of this check.
- **missing:** A bounded serial capture/parser service that uses diagnostics/dual_chip_autocapture.sh or the two fixed USB paths and emits framed samples rather than opaque text; A common timestamp/counter schema from both firmwares so loss and drift can be computed; Local metrics for packet loss, jitter, underrun, clock ppm, codec mode, and firmware build identity; A result route that stores the verdict and links the raw log without sending the whole log to the model

### "When you run something on my Mac, give me a trustworthy answer about what actually happened: the command's exit code, duration, files or apps it changed, and—if it failed—retry only the safe step or tell me exactly where to resume after a restart."
- **useful because:** The Mac already has maximum-access execution, but its current record loses exit codes, inherits an unrecorded environment, cannot interrupt a running shell, never retries, and leaves jobs stuck as processing after a crash. This capability makes unattended action dependable rather than merely powerful.
- **path:** mac-planner → mac-terminal → relay-realtime → pendant
- **model tier:** Deterministic receipt/recovery machinery does the work; use the inexpensive model only to explain a failure in the owner's requested one-sentence style. Realtime is only for a live spoken status.
- **latency:** No added delay for dispatch; receipt available immediately on completion, and crash reconciliation within 5 seconds of agent restart.
- **cost:** Negligible model cost for normal jobs; under a cent or two for an occasional failure explanation. Storage overhead is bounded per action and job.
- **security:** Do not persist secret environment values: record a redacted environment fingerprint and explicit allowlisted variable names only. Preserve the owner's deliberate unrestricted execution and no-confirmation policy; this is observability and recovery, not a gate.
- **missing:** Capture execFile-style argv/command identity, exit code, signal, pid, start/finish/duration, and redacted environment fingerprint; Wire AbortController to the child process so cancellation can terminate a running shell, not merely stop between steps; Idempotency keys and selective retry for actions whose receipts prove they did not complete; Boot-time reconciliation that closes or marks interrupted jobs and ledgers, joins planMeta.jobId to the ledger, and exposes a resumable next step; A durable owner-facing spoken status path from GET /jobs/:jobId and receipts to the pendant

### "Let me start a long, multi-step task from the pendant, walk away from my Mac, and come back to a spoken checkpoint: pause exactly before any irreversible step, show me what will happen, let me approve or revise it by voice, then finish and prove the final state."
- **useful because:** Today the nodes can each execute pieces, but the owner cannot safely carry an evolving task across distance and time. This would make the pendant a real remote control for authenticated Mac/browser work rather than a voice front end that must stay attached to one live interaction.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-terminal
- **model tier:** Use a cheaper background model for decomposition, checkpoint summaries, and final-state comparison. Use realtime only for the owner's short voice approval or revision.
- **latency:** Immediate spoken acknowledgement under 500 ms; checkpoint summary under 5 seconds after the preceding step; resume within 2 seconds of approval.
- **cost:** Typically one planning call and one compact verification call, roughly $0.01–$0.05 per task; storage and browser execution dominate neither cost nor latency.
- **security:** The browser session and page contents remain on the Mac. The relay sends only task state and a redacted checkpoint. Irreversible actions are never inferred as approved from an old approval, silence, reconnect, or a changed page; approval is bound to the exact proposed step and page state.
- **missing:** A durable task graph with explicit reversible and irreversible checkpoints rather than a flat action list; A pause/resume protocol spanning relay disconnects, Mac job restarts, and browser command queues; A compact checkpoint artifact containing the proposed action, relevant page/app state hash, and available alternatives; Voice approval/revision binding to one checkpoint token with expiry and exactly-once consumption; Post-action semantic verification that reports what changed, not merely that a process returned success

### "Update the pendant and audio bridge from my Mac, but only declare success after both devices reboot, report their build IDs and health counters, and automatically roll back the device that fails its first real audio check."
- **useful because:** Firmware updates are currently an engineering operation with a dangerous gap between 'flash completed' and 'the wearable still works.' This would let the owner keep the system current without being stranded by a bad image, and it uses the Mac's physical USB reach while preserving a truthful result on the pendant.
- **path:** mac-terminal → mac-planner → pendant → relay-realtime
- **model tier:** Deterministic flashing, boot verification, and rollback; use a cheap model only to summarize the resulting diagnostics. No realtime generation is needed except a short spoken status.
- **latency:** Preflight under 5 seconds, flash/reboot in under 2 minutes, and a pass/fail verdict after a bounded 30-second audio self-test.
- **cost:** Near-zero model cost; local USB transfer and device reboot dominate. Requires engineering work for signed images and rollback storage.
- **security:** Only explicitly selected, signed firmware artifacts may be installed. Keep the existing maximum-access Mac policy, but make the device refuse unsigned or mismatched-board images. Never erase the known-good slot until post-boot validation passes.
- **missing:** A/B or otherwise recoverable firmware slots on both chips with boot-attempt counters and automatic fallback; A signed manifest tying image, board revision, codec protocol version, and minimum companion versions together; A typed USB flasher/health protocol instead of opaque shell output; A post-boot self-test covering button, LED, audio loopback, frame counters, and transport heartbeat; A durable update record linked to the Mac job and spoken result

### "After you change something on my Mac or in a browser, let me ask 'show me' and hear a short before-and-after proof: the exact object changed, the old and new value, the source page or file, and whether anything else changed unexpectedly."
- **useful because:** A success message is not evidence. This gives the owner a fast, human-auditable answer for settings, files, and browser forms without replaying the whole task or exposing a large page dump. It is especially valuable when the work happened while the owner was away from the Mac.
- **path:** mac-planner → mac-terminal → browser-extension → relay-realtime → pendant
- **model tier:** Collect structured before/after facts deterministically; use a cheap summarizer for the one-sentence spoken explanation. Realtime is only needed to answer the follow-up voice question.
- **latency:** Proof available within 3 seconds for a local action and 5 seconds for a browser action; spoken answer under one sentence by default.
- **cost:** Usually negligible model cost; a small verification call only when structured diffs are unavailable.
- **security:** Redact secrets and unrelated page fields. Keep source URLs and hashes, not whole sensitive documents. For destructive operations, retain the evidence long enough for undo/audit but honor the existing confirmation policy.
- **missing:** Pre-state capture appropriate to each action type, including file hashes, app settings, and browser field values; Post-state capture and semantic diffing rather than relying on process exit status; A single proof record joining Mac receipt, browser provenance, source URL/file, and action/job IDs; A compact spoken-proof endpoint that can resolve 'that change' from the owner's current session; Detection and reporting of collateral changes outside the requested target


## Changes it proposed to its own stack

### `firmware` — Complete the 24 kHz superwideband audio path as a negotiated, measurable transport: advertise codec/rate/frame-size in the first handshake, attach monotonic sequence and capture/playback timestamps to every frame, maintain a bounded jitter buffer, and downgrade or resume at 16 kHz without losing the turn when the link cannot sustain 24 kHz. Export the same counters over the existing UART diagnostics.
- **owner gets:** Calls will sound clear when the link is good and fail gracefully when it is not, instead of producing silence, robotic audio, or a falsely completed turn. The owner can hear and trust the improvement immediately on the connected bench hardware.
- effort: Medium-high: firmware framing/codec work on nRF9160 and ESP32, relay negotiation, and end-to-end tests with induced loss and clock drift.  ·  risk: A framing mismatch could break current audio. Keep a protocol version and retain the existing mode as a fallback; reject unknown codecs and preserve the last acknowledged turn cursor.
- cost: No meaningful per-call API increase; modest RAM for a jitter buffer and counters. No new hardware cost.  ·  latency: Adds one negotiation round and bounded buffering (target 20–60 ms); adaptive downgrade prevents much larger stalls.
- security: Audio remains in the existing authenticated transport; diagnostics must exclude raw audio and redact any identifiers beyond firmware/build IDs.
- depends on: audio_link_truth_and_recovery is already accepted; A shared frame schema between nRF9160, ESP32 bridge, relay, and Mac pipeline; The missing host-side serial capture/parser for validating UART counters


## What it asked for

_Nothing._
