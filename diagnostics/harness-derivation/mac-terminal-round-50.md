# Harness derivation — mac-terminal — round 50

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-control-readiness-round50** — At 2026-08-07T10:52:46Z the Mac bridge and local agent are online, but Accessibility is untrusted for com.aipendant.agent, Screen Recording is false, inputReachability failed, and observe explicitly says UI actions may report success while doing nothing. Browser bridge is offline with 3 pending commands. The newly granted mac_read_diagnostics schema exists but has no implementation.
  - evidence: GET /observe and GET /ops/status returned these fields; mac_read_diagnostics returned 'tool was granted a schema but has no implementation yet'.

## Capabilities it proposed

### "Why didn't that Mac task work, and make it work if you can?"
- **useful because:** Today a failed browser command can spend 45 seconds before reporting offline, and UI actions can return success while never reaching the screen. This cross-surface diagnostic gives the owner a truthful answer and an actionable recovery instead of another blind retry.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Cheaper background/text model for diagnosis and remediation planning; realtime only speaks the short result to the pendant. Use deterministic local checks before any model call.
- **latency:** Under 2 seconds for status diagnosis; up to 10 seconds for a safe recovery attempt such as opening the relevant host app. Never wait on an impossible browser/UI action.
- **cost:** Usually near-zero model cost when deterministic checks suffice; occasional small text-model call (<$0.01) to summarize a multi-step job history. Dominant cost is local execution, not tokens.
- **security:** Diagnostics can include paths, foreground app, and browser tab metadata; redact secrets and page contents unless explicitly requested. Recovery must be limited to owner-authorized existing actions, and report whether it was attempted or only recommended.
- **missing:** Implement the granted mac_read_diagnostics tool or expose equivalent local preflight data to mac-planner; A typed recovery action for enabling/restarting the browser bridge or opening the exact permission pane; Receipt state distinguishing not-delivered from failed-after-delivery; Relay/pendant response schema for concise remediation options

### "Take this multi-step task all the way through, but stop safely if any prerequisite is missing—for example, build the project on my Mac, verify the result in my authenticated browser session, then publish it and tell me exactly what happened."
- **useful because:** The owner cannot currently have one truthful, dependency-aware workflow spanning terminal work and an authenticated browser session. A shell job can finish while the browser is offline, or a UI step can claim success despite unreachable input, leaving the owner to reconstruct which parts actually happened. This would turn the hive's separate reach into one coherent task with explicit checkpoints.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use a cheaper background model to compile the request into a typed dependency graph and summarize receipts; reserve realtime for the owner's live conversation and interruption handling. Deterministic executors perform shell/browser steps.
- **latency:** Begin speaking within 1 second, then run asynchronously. Each checkpoint should report within 2 seconds of completion or a capability failure; allow the owner to interrupt from the pendant at any checkpoint.
- **cost:** Usually <$0.02 per workflow for planning and final summarization; dominant cost is local/browser execution and any uploaded verification artifacts, not model tokens.
- **security:** Authenticated browser pages, source code, and command output must remain on their owning surfaces unless the owner explicitly requests sharing. Publishing or sending externally needs a clearly described final checkpoint; redact secrets from logs; persist only hashes and typed outcomes by default. A failed prerequisite must produce 'not attempted' downstream steps, never simulated success.
- **missing:** A durable cross-surface workflow/DAG coordinator in the relay with checkpoint and dependency semantics; A common receipt protocol linking Mac shell results, browser observations, and publication outcomes by one workflow ID; Browser online/permission attestation plus a truthful not-delivered state for unreachable UI actions; A pendant interrupt/resume command and relay-side cancellation propagation to both Mac and browser executors; Artifact handoff rules for passing only owner-approved build outputs or verification evidence between surfaces

### "Keep watch on the task I left running and tell me only if it finishes, gets stuck, or needs me."
- **useful because:** Today the owner must poll jobs and manually notice that the browser has gone offline or a Mac capability has become unusable. A relay-resident watchdog would turn long-running, cross-surface work into a dependable background service: silence on success, a concise pendant alert only for completion, a stall, or an actionable intervention.
- **path:** relay → mac-planner → browser-extension → pendant → dashboard
- **model tier:** No realtime model for monitoring: use deterministic heartbeats, deadlines, and receipt transitions. Use a cheap background model only to compress an exception into a short owner-facing explanation; realtime speaks it if the pendant is connected.
- **latency:** Heartbeat checks every 15–30 seconds; detect a missed lease within 60 seconds and notify within 5 seconds of classification. No polling or model call when the workflow is healthy.
- **cost:** Near-zero model cost for healthy workflows; <$0.01 for an occasional exception summary. Dominant costs are relay durable storage and heartbeat traffic.
- **security:** The relay should store workflow IDs, capability states, and redacted outcome summaries—not command text, secrets, or authenticated page content. Notifications must identify whether a step completed, was not delivered, or is awaiting the owner; never infer success from a disconnected executor.
- **missing:** Relay durable leases and watchdog timers tied to workflow IDs; Mac and browser executors emitting signed heartbeat/step-state events; A pendant notification policy with quiet hours, deduplication, and physical dismiss/snooze; Dashboard controls to inspect, pause, resume, or abandon a watched workflow; Cross-surface state taxonomy distinguishing running, stalled, unreachable, not-delivered, failed, and completed


## Changes it proposed to its own stack

### `mac-harness` — Add a non-blocking preflight attestation and execution telemetry envelope to every Mac job: snapshot /observe and /ops/status immediately before dispatch; attach capability facts (inputReachability, accessibility, screenRecording, browser online), command/action ID, cwd, duration, exit code, bounded stdout/stderr digests, and post-state observation to the receipt. If a UI/browser capability is unreachable, mark the step 'not-delivered' before attempting it; retain FULL_CONTROL_MODE and do not add approval gates. Automatically classify failures as retryable (bridge/browser offline, transient timeout) versus configuration-required (permissions, missing app), and offer a one-click retry after state changes.
- **owner gets:** The owner stops hearing 'done' when nothing reached the screen, and gets an exact explanation and recovery path instead of spending repeated voice turns guessing whether the Mac or browser is at fault. Shell remains maximally capable, while every command becomes auditable and failures become recoverable.
- effort: Medium: shared pre/post wrapper in executor plus receipt schema and dashboard/voice formatting; no shell-policy change.  ·  risk: Preflight can become stale between snapshot and action, and bounded output may omit useful details. Label it as an attestation, capture post-state, and preserve raw local logs for explicit debugging. Never claim UI success solely from process exit.
- cost: Negligible API cost; local JSON/log storage grows roughly 2–10 KB per job after truncation.  ·  latency: ~100–300 ms for local preflight/postflight; no model latency.
- security: Improves auditability but command metadata may expose paths. Redact environment values and secrets; hash command text where full text is unnecessary. Does not narrow owner-authorized execution.
- depends on: /observe and /ops/status remain available to the local agent; Receipt schema supports capability evidence and a not-delivered status


## What it asked for

_Nothing._
## Its own summary

Round 50 discovery is complete. The Mac bridge is online, but Mac UI control is not actually reachable: Accessibility is false for the running agent binary, Screen Recording is false, and the input probe fails. Browser control is offline with 3 queued commands. I recorded this fresh evidence, informed mac-planner, and proposed a non-blocking pre/post capability attestation so FULL_CONTROL_MODE stays intact while false-success receipts disappear. I also proposed a cross-surface 'why did it fail / make it work' diagnostic and recovery capability.

**Biggest unknown:** The granted mac_read_diagnostics tool still has no implementation, so planner-side recovery cannot yet obtain bounded host diagnostics through that interface. Remaining implementation needs are: expose an equivalent preflight endpoint or implement that tool; add a not-delivered receipt state; and add typed recovery for restarting the browser bridge or opening the exact macOS permission pane. I do not need another permission grant this round.

