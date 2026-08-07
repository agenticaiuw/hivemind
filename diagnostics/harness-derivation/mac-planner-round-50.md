# Harness derivation — mac-planner — round 50

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-mac-readiness** — Relay and Mac bridge are reachable, but Mac local agent reports ready=false because Accessibility and Screen Recording permissions are not granted. Browser extension home-chrome is offline with 3 pending commands. Full-control mode is enabled, but UI capture/vision cannot safely operate until permissions and browser reconnect are restored.
  - evidence: GET /ops/status returned macBridgeOnline=true, accessibility.trusted=false, screenRecording.granted=false, browser.online=false, pendingCommands=3; GET /browser/status independently returned the same browser state.

## Capabilities it proposed

### "“Park this exactly where it is; when I say resume later, put me back in the same work and tell me what changed.”"
- **useful because:** Today a spoken task can strand its state in a browser tab, a half-filled Mac document, and the relay’s conversation history. A resumable capsule would preserve the actual work frontier—not just a transcript—and safely detect stale or conflicting changes before continuing.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the cheaper background model to serialize and summarize checkpoints; use realtime only for the owner’s park/resume utterance and a short conflict explanation. Use a vision model only if accessibility/UI metadata is unavailable.
- **latency:** Park acknowledgement under 2 seconds (write capsule asynchronously); resume should report capsule age and conflicts within 5 seconds, then restore reversible UI state in under 15 seconds.
- **cost:** About $0.01–$0.08 per park/resume pair depending on document/browser extraction; storage and Mac bridge calls dominate, not realtime tokens.
- **security:** Capsules may contain private tab URLs, document snippets, and draft text. Encrypt at rest, keep sensitive values as hashes/redacted placeholders unless needed, bind capsule to the paired relay/Mac/browser identity, and never auto-submit or send on resume. Show a before/after diff and require the owner’s explicit spoken confirmation for any irreversible continuation.
- **missing:** A versioned task-capsule schema with provenance (app/file/tab, selection, draft fields, last action, timestamps, sensitivity, and hashes); Mac read-only capture of focused app/document and browser tab/session state (current accessibility permission is false and browser bridge is offline); Browser bridge reconnect and tab/session reattachment with idempotent request IDs; three commands are currently pending; A relay durable capsule store plus conflict detector that compares checkpoint hashes and current state; A restore planner that can reopen files/tabs and place the cursor/selection without submitting changes; Pendant protocol/UI for park, list, resume, and cancel commands with compact spoken summaries

### "“If you’re carrying out a long task on my Mac or in Safari, let me interrupt you from the pendant at any moment; stop cleanly, preserve exactly what was done, and tell me what remains.”"
- **useful because:** Today a long Mac/browser operation can outlive the owner’s intent: the pendant, relay, local agent, and browser queue have no unified, low-latency cancel-and-checkpoint contract. This gives the owner a real emergency brake without requiring approval gates, while preserving a useful partial result instead of leaving an opaque half-finished job.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime handles only the short interrupt/cancel utterance and concise status. A cheaper background model classifies the current checkpoint and summarizes completed versus remaining steps; deterministic code performs cancellation and receipt reconciliation.
- **latency:** Pendant-to-relay cancel acknowledgement under 500 ms; Mac/browser cancellation propagation under 2 seconds; partial-result summary under 10 seconds.
- **cost:** Usually under $0.01 per interruption; transport, receipt persistence, and state reconciliation dominate model cost.
- **security:** A false wake or accidental phrase could stop work, so require a distinct cancel phrase or the pendant’s second-press gesture and provide a brief audible/LED acknowledgement. Cancel must never undo completed external mutations automatically; expose receipts and offer separate undo where supported. Keep content summaries redacted by default and bind cancellation to the owner’s paired session.
- **missing:** A pendant interrupt event that can be sent while audio playback or an uplink is active, with a deterministic local acknowledgement; Relay-wide cancellation fan-out keyed by job/session ID, including queued browser commands and Mac actions; Cooperative cancellation checkpoints in the Mac executor and browser runner, with idempotent cancel semantics and a final partial receipt; A dashboard state model showing cancelled, completed, skipped, and unknown steps, plus supported undo links; A bounded reconciliation timeout for nodes that are offline, so the owner is told when cancellation could not yet reach a surface


## Changes it proposed to its own stack

### `integration` — Add a durable cross-surface task-capsule and lease protocol. The relay issues a capsuleId and monotonically increasing checkpoint; the Mac agent atomically records app/file/UI state and reversible action receipts; the browser bridge records tab/session IDs, URL, extraction hashes, and pending command IDs. On reconnect, each node exchanges a signed state vector, marks stale fields as conflicts rather than replaying them, and returns a restore plan plus a human-readable diff. Replays must be idempotent and expire after a configurable lease.
- **owner gets:** The owner can leave mid-task, close the lid, lose LTE, or switch from Mac to pendant without losing the exact place they were working or accidentally applying an old action to changed content.
- effort: Medium-high: shared schema and D1/R2 persistence, local-agent atomic journal integration, browser reconnect/queue reconciliation, restore adapters for common apps, and dashboard inspection UI.  ·  risk: Incorrect state capture could reopen the wrong document or misplace a draft. Recover by making restore dry-run first, showing a diff, retaining the original capsule, and allowing cancel/rollback of supported actions. Never replay irreversible actions automatically.
- cost: Small background-model and D1/R2 cost per checkpoint; roughly 1–5 KB metadata plus optional redacted snippets per capsule. No meaningful pendant runtime cost if protocol remains relay-side.  ·  latency: Park adds under 2 seconds asynchronously; reconnect reconciliation typically 1–5 seconds, restore 5–15 seconds depending on apps and browser availability.
- security: High-value private state crosses Mac/browser/relay. Encrypt capsule contents, minimize snippets, use per-capsule capabilities, expire leases, and audit every read/restore. Current browser is offline and Mac Accessibility/Screen Recording are not granted, so capture must degrade explicitly rather than guess.
- depends on: Durable browser job runner and command queue with request IDs/idempotency; Read-only Mac UI/context capture and app/file provenance; Relay durable job/state store and reconnect events; Owner-facing dashboard diff/restore controls

### `firmware` — Add an interruptible-execution control path to the pendant firmware: reserve a compact control frame on the existing WebSocket for cancel/pause/resume, queue it ahead of audio, and acknowledge it locally with a distinct LED pattern and a short tone through the existing full-duplex I2S path. The relay should prioritize this frame over speech and fan it out to the active Mac/browser job; the job runner must checkpoint before each side-effecting step and emit a terminal partial receipt.
- **owner gets:** The owner gets a dependable physical emergency brake for actions happening away from the screen, even when the voice stream is congested or the browser is temporarily slow. They can stop an unwanted action immediately and know exactly what did and did not happen.
- effort: High: firmware protocol and UX, relay priority/cancellation routing, cooperative cancellation in both Mac and browser runners, receipt schema, and failure-injection tests for LTE loss and node disconnects.  ·  risk: A cancel frame may be delayed or lost during modem failure, and stopping between a request and its external commit can leave ambiguous state. Mitigate with sequence numbers, local acknowledgement that distinguishes “received” from “applied,” idempotent cancellation, commit boundaries, and an explicit unknown-state result rather than claiming success.
- cost: Negligible API cost; modest firmware RAM/flash for a small control queue and relay/database fields. No additional hardware is required, though a production pendant should expose a stronger tactile/haptic acknowledgement than the prototype’s single LED.  ·  latency: Sub-500-ms local acknowledgement when connected; LTE worst-case remains bounded by modem scheduling and must be reported honestly.
- security: Control frames must be authenticated to the paired owner/session and reject stale sequence numbers. Do not let arbitrary dashboard clients cancel another session; audit who/what issued every interrupt.
- depends on: Relay job cancellation and receipt APIs; Mac executor cooperative checkpoints; Browser command queue with cancellation and idempotency; Pendant audio/control multiplexing on the existing WebSocket


## What it asked for

_Nothing._
## Its own summary

Discovered a concrete cross-node gap beyond simple background jobs: resumable task capsules with versioned checkpoints and leases. I proposed the owner capability “Park this exactly where it is; resume later,” and the integration change spanning pendant, relay, Mac, and browser. Live state: relay/Mac bridge reachable, but Accessibility and Screen Recording are ungranted; browser extension is offline with 3 pending commands. I recorded that finding.

**Biggest unknown:** Whether the owner wants private document/tab snippets encrypted into relay storage or only local hashes/provenance; that choice determines whether capsules can restore drafts richly or only reopen locations and report changes.

