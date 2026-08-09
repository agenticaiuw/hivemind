# Harness derivation — faculty-action — round 195

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Finish this multi-step task even if the Mac or browser drops halfway, but never repeat a side effect.”"
- **useful because:** Today the mind can decide a workflow, execute pieces, and verify a step, but it cannot resume at a durable boundary. A browser reload or Mac-agent restart forces either a dangerous replay or manual reconstruction. This gives the owner reliable completion rather than a plausible 'done' message.
- **path:** faculty-judgement → relay-realtime → mac-planner → browser-extension → mac-vision → faculty-perception → faculty-action → pendant
- **model tier:** background for checkpoint planning and reconciliation; realtime only for the owner's interruption or clarification
- **latency:** Create a checkpoint before each side-effecting step (<2 s); resume in 5–15 s after reconnection; no action is replayed until its prior postcondition is re-verified.
- **cost:** Usually 1–3 cheap planner/perception calls per resumed step; the dominant cost is fresh browser/Mac state capture, not audio.
- **security:** Persist only opaque step IDs, idempotency keys, artifact hashes, and redacted postconditions; never checkpoint form secrets or page contents. A stale lease must become unknown and require the physical approval latch again. Recovery must prefer no-op/compensation over replay.
- **missing:** A durable checkpoint token binding operation ID, step ID, idempotency key, browser lease, artifact hashes, and pendant approval counter; Executor adapters that accept idempotency keys and report a stable side-effect receipt; Resume coordinator that re-verifies completed steps and chooses retry, compensate, or unknown

### "“At 9 AM, do this only if the details still match what I approved; otherwise ask me on the pendant instead of sending anything.”"
- **useful because:** A scheduled routine today can fire at a time when a price, recipient, browser page, or file has changed. This makes automation conditional rather than blindly time-based: the relay wakes the Mac, perception compares the live state to an approval digest, and the pendant is the only place that can authorize a changed sensitive action.
- **path:** relay-realtime → faculty-judgement → faculty-perception → faculty-action → mac-planner → browser-extension → mac-vision → pendant
- **model tier:** background/scheduled model for preflight and comparison; realtime only when the owner is asked to resolve drift
- **latency:** Preflight within 10 s of the schedule; if unchanged, execute after a short lease; if changed, deliver a compact haptic/voice prompt and wait up to the owner's configured window.
- **cost:** One cheap scheduled preflight plus one verification call; realtime cost occurs only on drift. Browser/Mac state capture dominates.
- **security:** Approval stores a digest of allowed facts (recipient ID, amount, target URL, file hash), never secrets or full page content. Approval expires at the scheduled execution and cannot authorize a materially changed digest. If the pendant is offline, hold or cancel—never silently execute a high-risk drifted action.
- **missing:** A routine schema for typed preconditions and an approval-digest/expiry; A scheduler-to-action lease that obtains fresh Mac/browser state at fire time; A pendant prompt/response verb that distinguishes unchanged-auto-run from changed-needs-approval

### "“Undo what you just did, everywhere you changed it, and tell me exactly what could not be undone.”"
- **useful because:** Existing per-job undo is not enough for a workflow that edits a local file, changes a browser record, and sends a side effect through different surfaces. The owner needs a truthful compensating transaction: restore reversible artifacts, cancel queued work, verify each restoration, and explicitly isolate irreversible steps instead of claiming a magical undo.
- **path:** faculty-action → faculty-perception → mac-planner → browser-extension → mac-vision → relay-realtime → pendant
- **model tier:** background model builds the compensation plan; realtime handles an urgent owner request and presents the final status
- **latency:** Plan in under 3 s; begin reversible compensation immediately after physical approval; report each step as restored, not-restored, or unknown within 15 s.
- **cost:** One planner call and one verifier call per changed surface; browser and filesystem evidence dominate. No extra model call for already receipt-backed no-ops.
- **security:** Undo must be scoped to the exact operation ID and receipt set, never inferred from 'last action' across users or sessions. It must not delete unrelated files or send reversal messages without a second approval. Keep encrypted, redacted before-state hashes and retention limits; unknown state must block replay.
- **missing:** A compensation graph in each executor receipt (inverse action, required before-state, reversibility class); Cross-surface undo coordinator with dependency ordering and cycle/partial-failure handling; A read-only final report that binds every compensation result to fresh verify_operation_step provenance

### "“Cancel every pending action I have authorized, from whichever device is reachable, and prove that none of them can still run.”"
- **useful because:** The owner should have a panic-level revocation that is stronger than cancelling one known job. Today an approval can be distributed across relay, Mac, browser, and an offline pendant queue; cancelling one record can leave a stale command or lease elsewhere. A global revocation epoch would let the owner stop the whole action surface with one deliberate gesture or voice request and receive proof from each node.
- **path:** pendant → relay-realtime → faculty-action → faculty-perception → mac-planner → browser-extension → mac-vision
- **model tier:** Realtime for the urgent request; background reconciliation to sweep every queue and lease
- **latency:** Broadcast revocation immediately (<1 s when connected); each node must acknowledge or be marked unreachable within 10 s; no pending action may execute against an older epoch after reconnect.
- **cost:** One lightweight signed broadcast plus bounded acknowledgements; reconciliation costs a few cheap state reads, not a large model call.
- **security:** Use a monotonic, signed owner revocation epoch; do not transmit page contents or secrets. Revocation must be fail-closed for sensitive actions, survive relay restart and pendant offline storage, and distinguish 'cancelled everywhere' from 'node unreachable'. Re-authorizing requires a fresh approval, never reuse of an old nonce.
- **missing:** A system-wide revocation epoch and durable key management shared by relay, Mac, browser bridge, and pendant; Mandatory epoch checks in every executor, queued command, browser lease, and scheduled routine; An independently verified revocation receipt aggregating acknowledgements and unreachable-node status

### "“Finish the task, but when a password, payment code, or private answer is needed, let me enter it directly without the AI ever seeing it, then continue.”"
- **useful because:** The browser can hold a logged-in session, but a blocked workflow currently forces either exposing a secret to the model or abandoning the task. A secure input detour lets the owner type into the real browser field while the action mind sees only a redacted completion signal, then resumes the same operation without receiving the secret.
- **path:** faculty-judgement → faculty-action → browser-extension → mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** Realtime only for the short handoff prompt; background model continues the workflow after a typed, non-secret completion receipt
- **latency:** Focus the field and notify the owner within 2 s; resume within 3 s of browser confirmation; never poll or OCR the secret field.
- **cost:** A few browser bridge events and one postcondition verification; negligible model cost once the detour is implemented.
- **security:** The bridge must enforce an allowlist of sensitive-field types, suppress keystrokes, clipboard contents, screenshots, accessibility values, logs, receipts, and model context, and return only field identity plus success/failure. The owner must see the actual origin and field before typing. Timeout and navigation changes cancel the operation and require fresh approval.
- **missing:** Browser-side secret-field isolation that accepts owner input without emitting value events; A sealed continuation token binding the same operation to the redacted completion event; Postcondition verification that proves the field accepted input without revealing its contents

### "“If I walk away from the pendant before a sensitive action finishes, freeze it; only continue when I am back and deliberately confirm.”"
- **useful because:** A one-time approval is unsafe for a long-running browser or Mac workflow: the owner can approve, put the pendant down, and leave an unattended session with a pending side effect. The pendant's IMU and the ESP32 bridge can provide a separate presence/liveness boundary, while the relay revokes leases during absence and requires a fresh gesture on return.
- **path:** pendant → ESP32 audio bridge → relay-realtime → faculty-action → faculty-perception → mac-planner → browser-extension → mac-vision
- **model tier:** Firmware and relay state machine; no expensive model call is needed except to explain an interruption
- **latency:** Detect removal/absence within 1–2 s; invalidate sensitive leases immediately; re-establish presence and request confirmation within 3 s of return.
- **cost:** Low runtime/model cost; implementation is firmware integration and bridge presence signaling, with occasional verification reads.
- **security:** Presence is not identity and must never silently approve; it only pauses/revokes. IMU data stays local as coarse state, not raw motion traces. Treat link loss, sensor fault, and ambiguous movement as absent. A new physical approval is mandatory after every absence.
- **missing:** Firmware IMU wear/settled-state classifier using the owned LSM6DSOX (enable i2c2); Authenticated short-range presence channel between pendant/ESP32 bridge and relay; USB is bench-only; Executor lease hooks that fail closed on presence loss and a fresh-confirmation path on return


## What it asked for

_Nothing._
## Its own summary

Round 195 produced three new action capabilities: (1) durable cross-surface checkpoint/resume that binds browser leases, Mac artifacts, idempotency keys, and pendant approval without replaying side effects; (2) scheduled actions that re-check a typed approval digest at fire time and ask on the pendant if live state drifted; and (3) truthful multi-surface compensation undo with dependency ordering and independently verified restoration. I also told mac-planner to expose stable idempotency keys and inverse-action metadata in receipts. The system still needs a durable checkpoint/resume coordinator, executor-level idempotency and compensation metadata, typed routine preconditions with approval expiry, and a pendant prompt for changed scheduled actions. Existing per-job undo and verification primitives are useful building blocks but do not close those gaps.

**Biggest unknown:** Whether every concrete executor (Mac actions, browser commands, and future pendant/relay actions) can expose stable idempotency keys and inverse metadata; without that, cross-surface resume and undo cannot honestly guarantee no duplicate side effects.

