# Harness derivation — mac-terminal — round 94

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac long-running command reliability gap** — Mac agent is fullControlMode=true with receipt-backed jobs, but ops status exposes no shell supervisor or process/event cursor. Relay is reachable and macBridgeOnline, while browser extension is offline with 7 pending commands. Existing failed browser jobs wait ~45s and are recorded as failed receipts; this demonstrates lifecycle visibility exists for completed requests but not detached shell processes.
  - evidence: GET /ops/status and GET /jobs at 2026-08-07T13:17Z

## Capabilities it proposed

### "From the pendant, “run that build/test and tell me only when it finishes or needs me,” even if I walk away or the Mac briefly loses its connection."
- **useful because:** Today a long Mac command is tied to one request and a live bridge; the owner cannot reliably leave, reconnect, or distinguish a still-running process from a lost one. This makes the wearable a dependable command console without weakening the owner's deliberate full-control policy.
- **path:** pendant → relay → mac-planner → mac-terminal → dashboard
- **model tier:** Use deterministic routing and the background tier for lifecycle updates and failure summarization; reserve realtime for the initial spoken request and final short notification. No planner call is needed for ordinary heartbeats.
- **latency:** Acknowledge on the pendant within 1–2 seconds, persist the job before dispatch, update state within 5 seconds of each heartbeat, and speak only on completion/failure. Reconnection should catch up from a cursor in under 3 seconds.
- **cost:** Usually one background summarization call on failure (roughly 2–4k input tokens); heartbeat and completion events are deterministic and incur no model call. Storage is bounded per job by retaining metadata plus a configurable stdout/stderr tail.
- **security:** The command remains unrestricted and unattended under FULL_CONTROL_MODE, as the owner requires. Persist cwd, command, exit status, touched paths, and a redacted output tail; never persist inherited secrets or full environment by default. A detached process can outlive the initiating conversation, so the dashboard and pendant must clearly identify owner-started jobs and provide cancel/status, not silently retry arbitrary commands.
- **missing:** A Mac detached-process supervisor that assigns a durable process/job id, emits heartbeats and bounded output cursors, and reports exit/signal/timeout/resource state; Relay durable job events with ordered sequence numbers, replay-from-cursor, and device notification preferences; A reconnecting Mac bridge protocol that reattaches to an existing process instead of launching a duplicate; Pendant event rendering for job started, waiting, completed, failed, and needs-attention states

### "“Did that actually happen?” — give me one trustworthy answer about a task that crossed my Mac, logged-in browser, and pendant, showing what changed, what did not, and the evidence for each step without running it again."
- **useful because:** Today each surface reports its own job or receipt, so a browser failure, a Mac-side file change, and a spoken relay acknowledgement can appear as unrelated events. The owner cannot obtain a single causal answer distinguishing completed work, partial work, and merely-requested work. This is a new cross-surface truth primitive, not another task runner or page watcher.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension → dashboard
- **model tier:** Use deterministic correlation and hashes first. Use the background tier only to explain a complicated partial outcome in plain language; use realtime only if the owner asks the question by voice. Do not spend planner-tier tokens reconstructing a straightforward event chain.
- **latency:** Return a deterministic status in under 2 seconds from stored records; retrieve missing evidence from the Mac or browser within 10 seconds. Speak a short verdict first, then offer the evidence trail on the dashboard.
- **cost:** No model call for ordinary correlation. A background explanation would be roughly 2–4k input tokens and one call. Storage is compact: event ids, timestamps, hashes, URLs, paths, and receipt references rather than full page or shell output.
- **security:** The evidence can contain private URLs, filenames, browser account names, and command output. Keep raw content on the originating device, expose only authenticated projections, redact secrets, and label stale or inferred evidence. Never convert missing evidence into a claim of success and never rerun an action merely to verify it.
- **missing:** A cross-surface task identity and causal-link protocol shared by Mac jobs, browser commands, relay requests, and pendant utterances; A verifier that compares before/after evidence (file hashes, browser field snapshots, receipt status, and relay delivery state) and classifies complete, partial, failed, unknown, or contradicted; A compact authenticated evidence-bundle endpoint with per-item provenance and freshness; Pendant and dashboard rendering for a verdict plus expandable evidence chain


## Changes it proposed to its own stack

### `mac-harness` — Add a shell-specific execution adapter beneath FULL_CONTROL_MODE (not a policy gate): launch every run in a tracked process group with a durable job manifest containing cwd, exact command, start time, pid/process-group id, timeout, and redacted environment keys. Append stdout/stderr to a bounded per-job log with monotonically increasing byte/sequence cursors; emit started/heartbeat/output/exit/signal/timeout events to the existing journal and relay. On bridge reconnect, reconcile the process group by manifest and replay events from the last cursor instead of dispatching the command again. Extend the existing action receipt with exit code, signal, elapsed time, last output cursor, and an explicit 'cannot resume' reason for commands that died.
- **owner gets:** The owner can leave a compile, export, sync, or test running and later hear the real result rather than a vague timeout or an accidental duplicate run. Failures become actionable (last output, exit signal, cwd, and whether the process is still alive), while unrestricted shell access remains intact.
- effort: Medium: a small local supervisor/event journal, relay replay endpoint, and adapters in executor.js plus dashboard/pendant consumers; tests for disconnect, process exit, timeout, and duplicate prevention.  ·  risk: A stale pid or reused process-group id could attach the wrong process; bind manifests to start time and verify command/cwd before reattachment. Log growth and secret leakage are risks; cap bytes, redact known secret patterns, and provide deletion. If reconciliation is uncertain, report 'unknown—no retry' rather than rerun.
- cost: No additional model cost for lifecycle events; modest local disk and relay D1 writes per event. One background-tier summarization call only when the owner requests a human explanation of a failure.  ·  latency: Launch remains near current latency. Heartbeats add negligible local work; reconnect status is available in seconds instead of waiting for an HTTP timeout.
- security: No new authority and no confirmation gate. It makes existing arbitrary commands more observable; command text and output tails are sensitive and must use the existing authenticated Mac/relay paths with retention limits.
- depends on: A durable relay event stream with replay-from-sequence semantics; A local process supervisor that survives the request handler and records manifests; Wire shell lifecycle events into existing /journal, /jobs, and receipt APIs; Pendant notification consumer for completion/failure


## What it asked for

_Nothing._
