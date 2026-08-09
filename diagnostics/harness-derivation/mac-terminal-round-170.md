# Harness derivation — mac-terminal — round 170

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Finish the thing I started on my Mac, even if the link drops: when I reconnect the pendant, continue the browser or shell workflow from its last safe checkpoint and tell me exactly what happened.”"
- **useful because:** Today a long Mac job can be left processing, cancellation is cooperative, and interrupted ledgers are never resumed automatically. This would turn the worn device into a true remote control for unfinished work rather than a second, stateless microphone. The relay queues the intent, the Mac persists step checkpoints, and the browser preserves authenticated session affinity; reconnecting the pendant yields a truthful resume or a precise stop reason.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background for checkpoint reconciliation and retry planning; realtime only for the short spoken status on reconnect
- **latency:** A reconnect status in under 2 seconds; resume begins within 5 seconds. Checkpoint reconciliation can take 10–30 seconds in the background.
- **cost:** Low: one short realtime response plus occasional background planner calls; dominant cost is only when a failed step needs replanning, not on every heartbeat.
- **security:** The Mac must retain opaque browser session/tab IDs and command receipts, never send cookies or shell environment to the relay. Resume only the exact idempotent checkpoint; require explicit owner confirmation for a step whose prior receipt is ambiguous. The pendant should say 'stopped, not verified' rather than invent success.
- **missing:** A durable step checkpoint protocol joining jobId, ledgerId, browser commandId, and pendant turn ID; Boot-time reconciliation that closes or marks open ledgers and offers resumable steps; Abortable run_shell execution and an idempotency-aware retry executor; A relay-to-pendant queued-resume message type with authenticated nonce and monotonic sequence

### "“From the pendant, carry out this authenticated browser action and prove the result: send the message, submit the form, or place the order, then read back the exact account/page confirmation and leave me a receipt I can inspect later.”"
- **useful because:** A voice agent that merely clicks is dangerous because a success-looking UI can hide a failed submission, wrong tab, or stale session. This makes the unique combination of pendant intent, browser-held credentials, Mac execution, and relay receipt into a dependable action: the owner gets a spoken result grounded in post-action evidence, not an optimistic model sentence.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** realtime for intent disambiguation and a one-sentence spoken result; deterministic browser actions and evidence extraction first, background model only when the page needs interpretation
- **latency:** Simple actions 3–8 seconds; evidence verification up to 15 seconds. Do not speak completion until a postcondition is observed or timeout is explicitly reported.
- **cost:** Low-to-moderate: deterministic browser calls dominate latency; use the expensive model only for ambiguous page semantics or conflicting evidence.
- **security:** Credentials and page contents remain in the browser bridge. Bind every action to tab/session ID, origin, and a nonce from the pendant; redact secrets from receipts. For irreversible purchases, deletion, or external messages, the pendant must get a concise confirmation before dispatch; completion still requires independent postcondition evidence.
- **missing:** A typed postcondition/evidence contract for browser actions (expected URL, DOM text, receipt number, or changed state); Cross-surface transaction ID carried from pendant audio turn through relay, Mac job, browser command, and durable receipt; A browser result verifier that rejects stale-tab or wrong-origin evidence; A dashboard receipt view with before/after evidence and spoken/visual distinction between dispatched and verified

### "“Stop the Mac task that is running right now.” (spoken to the pendant, with “the task” resolved from the latest spoken request or currently active job)"
- **useful because:** The pendant is the one surface available while walking away from the Mac, but today cancellation only sends a cooperative signal and cannot interrupt a running shell child. A real remote stop would prevent runaway commands, browser loops, or an accidentally expensive workflow from continuing, then report whether it was actually terminated.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** realtime for resolving the current job and speaking the result; deterministic relay routing and host process control, with no planner call unless the reference is ambiguous
- **latency:** A stop request should reach the Mac in under 1 second and produce a truthful terminated/not-terminated response within 3 seconds. Long-running process cleanup may be bounded at 10 seconds.
- **cost:** Very low: a short realtime utterance and deterministic control calls; no background LLM needed for an unambiguous current-job stop.
- **security:** Bind cancellation to the authenticated pendant session and a concrete job/process identity, never 'kill all'. The Mac must distinguish graceful cancellation from SIGTERM/SIGKILL and record the escalation. If the host is offline, the relay queues a stop intent with expiry and the pendant says it has not yet stopped anything; on reconnect, stale intents must not kill a new job.
- **missing:** A live-job registry that exposes jobId, action, child PID/process group, and owner-facing label to the relay; Abortable run_shell using a process group and signal escalation rather than exec without signal; A typed remote-cancel route carrying jobId, nonce, expiry, and expected session ID; Pendant voice-to-intent routing for cancel plus a completion receipt that truthful_action_status_beacon can display

### "“What am I looking at right now, and is it safe to trust?” — asked while away from the Mac, with the answer grounded in the active window, browser origin, visible page, and the last action receipt."
- **useful because:** The owner can currently get a screenshot or browser text, but not a compact, cross-checked answer about whether the visible UI is the expected authenticated page or a stale/error/phishing-looking state. This would use the pendant as an always-available question surface, the Mac for foreground/window facts, the browser extension for origin and DOM evidence, and the relay for a short spoken explanation.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** realtime for the final spoken answer; deterministic collection first, with a small background classifier for page-state comparison and only escalate to the expensive model when evidence conflicts
- **latency:** Collect evidence in 1–3 seconds and speak within 5 seconds; if the screenshot and DOM disagree, say that explicitly rather than delaying indefinitely.
- **cost:** Low for ordinary checks; browser and host probes dominate. Expensive model calls occur only on conflicting or novel UI states.
- **security:** Never transmit cookies, passwords, or full page contents by default. Bind evidence to active window, tab ID, origin, and capture timestamp; redact sensitive fields in the dashboard receipt. The answer must distinguish observed facts from model interpretation.
- **missing:** A single evidence capsule joining active-window capture, browser tab metadata, DOM text, origin, and recent action receipt; A Mac-vision route that can return a bounded redacted view while preserving provenance; A relay intent that requests a read-only trust check rather than an action; A compact pendant speech/result format for confidence and conflicting evidence

### "“Only interrupt me when this is genuinely urgent.” Then let the system arbitrate browser-watch changes, Mac job failures, and scheduled results against whether I am recording, speaking, presenting, or idle, and deliver the least disruptive alert that still meets the deadline."
- **useful because:** The owner currently has independent jobs, watches, routines, and pendant alerts, but no hive-wide interruption decision. A relay that knows the wearable's conversation state, the Mac's foreground activity, browser urgency, and job deadlines can stop routine completions from talking over the owner while still surfacing a failed payment, expiring form, or blocked task in time.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Background/deterministic scoring for every event; realtime only when an urgent alert must be phrased for speech. Do not spend the expensive tier on ordinary event arbitration.
- **latency:** Classify events under 250 ms; urgent escalation under 2 seconds; defer nonurgent events until the next natural conversational boundary or idle window.
- **cost:** Very low: event scoring and scheduling dominate, with occasional short realtime speech generation.
- **security:** Urgency rules and quiet hours remain local and inspectable. Browser page text should be minimized and redacted before relay scoring. Never suppress a deadline-critical event solely because the owner is busy; expose the reason and age of every deferred alert.
- **missing:** A shared event envelope with source, deadline, urgency evidence, sensitivity, and deduplication key; A pendant conversation/recording-state feed available to the relay in real time; A Mac foreground/presentation/idle signal and browser-watch change severity classifier; One durable alert queue with coalescing, quiet-window delivery, expiry, and truthful LED/audio state

### "“Work on this until it is done, but stop at $X, 20 minutes, or any irreversible step, and bring me the best next decision.” The pendant should let me set that budget, while the Mac, browser, and relay execute and checkpoint the work without needing me to micromanage every click."
- **useful because:** Today the owner can ask for an action or a plan, but cannot give the hive a bounded objective with an explicit time/cost/risk budget and receive a decision-ready checkpoint. This is the difference between a remote command and a dependable personal operator: the relay remains awake, the Mac can act, the browser retains authenticated context, and the pendant is the escalation channel.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Background planner for multi-step execution and checkpoint summaries; realtime only for initial budget capture and escalation questions. Deterministic tiers should enforce elapsed-time, step-count, and spend budgets.
- **latency:** Acknowledge the budget in under 2 seconds; ordinary steps proceed asynchronously; escalate at the first boundary or within 5 seconds of a blocked decision.
- **cost:** Moderate and controllable: background planner calls only at checkpoints, with a hard token/request budget. Browser and Mac execution are the dominant wall-clock costs, not conversation.
- **security:** Budgets must be signed to the specific task and expire. No irreversible or external side effect may be silently inferred as allowed just because time remains. Persist every consumed budget unit and evidence; if the relay is offline, the Mac must fail closed at the last checkpoint and the pendant must report that it cannot supervise.
- **missing:** A first-class task lease containing owner intent, deadline, token/API budget, allowed effect classes, and escalation policy; Budget accounting across planner calls, browser commands, shell runtime, and network/API spend; Checkpoint summaries that cite receipts and expose the exact next decision; A pendant control/result protocol for pause, resume, amend-budget, and abandon


## Changes it proposed to its own stack

### `mac-harness` — Make every run_shell action execute through a tracked process group with a stable child PID, explicit start/finish/exit metadata, and a cancellation escalation: send SIGTERM to the group, wait a bounded interval, then SIGKILL descendants. Persist the group identity and a monotonic execution sequence in the receipt, and make the relay's cancel intent target that exact sequence.
- **owner gets:** When the owner says stop from the pendant, the command actually stops instead of continuing invisibly for up to two minutes. They can also trust the later answer: terminated, exited itself, or could not be reached — rather than a generic cooperative-cancel message.
- effort: Medium: replace exec with a spawn/execFile-style wrapper, create process-group bookkeeping, persist exit metadata, and add crash cleanup/reconciliation tests.  ·  risk: Some commands depend on shell semantics, so preserve an explicit shell mode and test pipes/redirection. Killing a process group can terminate legitimate descendants; target only the recorded group and expose the command label. On agent crash, reconcile orphan groups conservatively instead of killing by stale PID alone.
- cost: Negligible API cost; small CPU and disk overhead for process metadata.  ·  latency: Normal commands are effectively unchanged; cancellation becomes seconds instead of waiting for the command timeout.
- security: No new authority beyond the already deliberate unrestricted shell. Stable process-group identity improves auditability and prevents an ambiguous remote cancel from affecting another job.
- depends on: A relay-visible current-job identity and authenticated cancel intent; Boot-time handling for orphaned process groups; The accepted truthful_action_status_beacon state mapping


## What it asked for

_Nothing._
## Its own summary

Round 170 produced four non-duplicate outcomes: (1) resumable cross-node workflows that continue browser/shell checkpoints after reconnect, (2) authenticated browser actions that require postcondition evidence before claiming success, (3) a true pendant-triggered remote stop rather than today's cooperative cancel, and (4) a Mac process-group execution change that makes cancellation real and receipts truthful. The connective primitive all four need is one authenticated transaction identity spanning pendant turn, relay event, Mac job/ledger, browser command, and final receipt. Live discovery also confirms Safari has nine tabs and the bridge is online; the pendant is still not registered with the relay.

**Biggest unknown:** I still cannot inspect the physical USB serial streams or firmware framing because the requested mac_usb_serial_diagnostics capability remains unresolved/pending. I need the actual nRF9160↔Mac and ESP32↔Mac protocol constants (HELLO/auth nonce, turn IDs, CRC, ACK/replay cursor, backpressure) before specifying the tether/resume implementation honestly. I also need the live process/job registry to expose child PID/process-group identity; current /jobs and /journal show outcomes but not a killable running process.

