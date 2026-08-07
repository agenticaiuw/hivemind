# Harness derivation — mac-terminal — round 33

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If a task I handed you on my Mac fails or the connection drops, diagnose it, resume from the last completed step when safe, and tell me exactly what recovered and what still needs me."
- **useful because:** Today an unattended shell command can run with maximum access, but a timeout, sleep, network blip, or partial multi-step result leaves the owner unsure whether rerunning would duplicate work. This makes long Mac work dependable without adding approval gates: the pendant/relay can report progress, while the Mac can inspect and recover locally.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use a cheap background model for heartbeat interpretation, failure classification, and retry planning; use realtime only for the owner's spoken status or an explicit follow-up question. Deterministic Mac-side code should own checkpoints and idempotency; the model should not invent completion.
- **latency:** Start/acknowledgement under 2 seconds; progress events every 10–30 seconds; recovery decision under 10 seconds after failure. Long commands continue detached from the voice session.
- **cost:** Roughly $0.005–$0.03 per long job for a few small background classifications; dominant cost is occasional model calls on failure, not heartbeats or receipts.
- **security:** The existing FULL_CONTROL_MODE and unrestricted environment remain unchanged; this adds observability and recovery, not blocking. Persist command metadata, exit code, bounded stdout/stderr tails, cwd, and checkpoint hashes, with secret-pattern redaction before relay/dashboard storage. Never auto-retry a command classified as non-idempotent or whose checkpoint is ambiguous; report it for owner review. Browser actions must retain tab/session affinity and before/after evidence.
- **missing:** A Mac-local supervisor that detaches shell processes, emits heartbeats, captures bounded/redacted output, and records checkpoint boundaries; A shared job state machine with attempt IDs, resumable checkpoints, and explicit states (running, link-lost, failed, recovered, needs-owner); Failure classifiers and command-specific recovery recipes (sleep/network unavailable, missing path, transient browser tab loss, nonzero exit); Relay push/status subscription to the pendant and a dashboard timeline that distinguishes completed steps from merely attempted steps

### "Do it on my Mac, then prove to me that the intended result actually exists—not just that the command finished—and tell me if anything differs from what I asked for."
- **useful because:** Today the system can report that an action or shell command ran, but completion is not the same as the desired real-world state: a file may be written to the wrong folder, an upload may be rejected after a click, or a setting may be changed by another process. The owner should receive an independent outcome check with concrete evidence and a clear mismatch report.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use deterministic validators first (file hashes/metadata, process and preference reads, browser DOM/state checks). Use a cheap background model to choose or synthesize a validator from the goal, and mac-vision only when visual confirmation is genuinely required. Realtime is reserved for the concise spoken result.
- **latency:** Immediate action acknowledgement under 2 seconds; verification within 5 seconds for local state and under 20 seconds for browser/server propagation. If propagation is asynchronous, keep a background watch and notify only on confirmed success or a bounded timeout.
- **cost:** Usually under $0.01 per invocation when typed validators suffice; $0.02–$0.08 when a model must construct a validator or vision is needed. Storage and network transfer of small evidence artifacts dominate only for screenshots or large file checks.
- **security:** Verification may inspect private files and authenticated browser pages. Keep raw evidence on the Mac where possible; relay only hashes, selected fields, redacted snippets, and a user-readable explanation. Never claim proof from an identical action receipt. For destructive or externally visible actions, verification reports state but does not silently repair; any repair must be separately planned and visible.
- **missing:** A goal-to-postcondition schema that records what success means independently of the action used; A typed validator registry spanning filesystem, app preferences/processes, browser DOM/network-visible state, and mac-vision screenshots; An evidence bundle format linking each postcondition to source, timestamp, validator, and before/after values; Relay and pendant UI for a concise proof/mismatch/timeout result, with dashboard drill-down to the evidence; A policy for eventually consistent sites that polls for confirmation without duplicating the original action


## Changes it proposed to its own stack

### `mac-harness` — Add a Mac-local execution supervisor around run_shell and browser actions. Each job gets a durable execution manifest with attemptId, parent job ID, command/action fingerprint, cwd, start/heartbeat/exit timestamps, bounded stdout/stderr tails, and explicit checkpoint markers. Run long work in a detached process group so voice-session loss does not kill it; on restart, reconcile live process groups and manifests. Classify failures into retryable, resumable-from-checkpoint, ambiguous-partial, and terminal. Emit signed progress events to relay and store redacted evidence; permit automatic retry only for an allowlisted idempotent step or a deterministic checkpoint recipe, never by shrinking FULL_CONTROL_MODE.
- **owner gets:** A Mac job will finish—or clearly explain why it cannot—rather than silently dying when the pendant disconnects or leaving the owner guessing whether a second attempt will duplicate changes. They get useful progress and a trustworthy completion boundary for long tasks.
- effort: Medium-high: local supervisor/manifest store, process-group lifecycle, checkpoint adapters for shell/browser steps, event transport, crash-reconciliation tests, and dashboard/pendant status rendering.  ·  risk: A process can outlive the original intent, and a mistaken idempotency classification can duplicate work. Recover by defaulting ambiguous jobs to needs-owner, recording every attempt, exposing a stop/kill action, and retaining raw local evidence while relaying only redacted tails. Existing receipts remain the final user-visible outcome.
- cost: Low ongoing compute/storage; a few KB of manifest and bounded logs per attempt. Occasional background-model failure classification costs cents per long job. No hardware cost.  ·  latency: Negligible for short actions; detached launch adds under 200 ms. Heartbeats are asynchronous. Recovery adds seconds only after failure.
- security: No new execution authority and no approval gate. It does introduce durable command metadata, so encrypt local manifests, redact likely secrets (tokens, cookies, API keys), and enforce retention/deletion controls. Signed event envelopes prevent stale relay updates from being mistaken for current completion.
- depends on: A durable relay job record and event stream with attempt IDs; Mac-local persistence outside the voice process (SQLite or append-only journal); An explicit checkpoint/idempotency contract for multi-step Mac and browser plans; Existing action receipts/undo integration so recovered jobs produce the same evidence


## What it asked for

_Nothing._
## Its own summary

Discovered the shipped Mac tools and granted surface. Proposed a new cross-node capability and Mac-harness change: detached, checkpointed execution supervision with heartbeats, redacted bounded output, attempt IDs, failure classification, and conservative recovery after link loss—without changing FULL_CONTROL_MODE or adding gates. This goes beyond existing generic receipts by making partial completion and safe resumption explicit. I also tested the newly granted mac_read_diagnostics path; it is schema-present but still returns “no implementation yet.”

**Biggest unknown:** The concrete local-agent job lifecycle and observability contract remain unavailable, and the granted diagnostics tool has no implementation. I still need an implemented read-only Mac diagnostics/observability path (or equivalent live /jobs, /logs, /journal access) to validate process-group survival, heartbeat behavior, and reconciliation after a dropped connection.

