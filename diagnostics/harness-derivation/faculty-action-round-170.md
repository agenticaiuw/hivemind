# Harness derivation — faculty-action — round 170

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Do it, but don't let it silently go wrong": have the system stage a consequential Mac/browser action, show me exactly what will happen on the pendant, require a deliberate physical approval, execute it, independently verify the postcondition, and tell me whether it succeeded, was rolled back, or is unknown."
- **useful because:** This is the core trustworthy action loop: judgement can decide and faculty-action can act, but the owner gets a physical veto and a truth check instead of an executor saying 'done'. It composes pendant, relay, Mac/browser, and perception in one owner-visible operation.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-judgement → faculty-perception → faculty-action
- **model tier:** Realtime only for the spoken summary and approval turn; background/cheap model for plan normalization and receipt summarization.
- **latency:** Stage in under 2 s; approval feedback under 300 ms over USB/local bridge (or next relay heartbeat); execute and verify within 10 s for ordinary actions, with explicit progress for longer jobs.
- **cost:** Roughly $0.01–$0.05 per operation depending on whether planning and verification require model calls; dominated by vision/browser verification, not the pendant or relay.
- **security:** The relay must carry only a redacted human-readable summary and digest, never form secrets or page contents. Approval is an opaque nonce bound to operation and expiry. No commit from executor receipts alone: faculty-perception must independently verify. Irreversible actions remain staged if verification fails.
- **missing:** An end-to-end coordinator that binds POST /plan to POST /execute, physical_transaction_approval_latch, and verify_operation_step; A durable operation envelope carrying actionId/attemptId, digest, expiry, approval state, verification provenance, and unknown/rollback outcome; USB-serial pendant approval transport while the pendant is attached to the Mac but not LTE-registered; A policy value from the owner defining which risk classes may be staged or auto-executed

### ""Keep working while I am away, and bring me back only what needs me": hand a multi-step Mac/browser job to the system, receive durable progress updates, pause safely at an approval boundary, and resume from the exact unfinished step when I press the pendant."
- **useful because:** Long jobs currently split across relay jobs, Mac execution, and browser sessions are hard to recover conversationally. A resumable run lets the owner leave, return hours later, and continue without repeating completed steps or guessing what happened.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → pendant → faculty-action → faculty-perception
- **model tier:** Cheap background model for checkpoint summaries and step classification; realtime model only when the owner asks for status or must approve a boundary.
- **latency:** Checkpoint every completed step within 1 s; status response under 2 s; resume within 5 s of a physical approval or reconnect.
- **cost:** About $0.005–$0.03 per resumed run; storage and event delivery dominate, with model use limited to summaries and ambiguity resolution.
- **security:** Persist only step metadata, digests, and redacted summaries; never persist browser secrets. Checkpoints must bind to browser session identity and current URL/app state. If state diverges, stop and request fresh perception rather than replaying clicks. Expire abandoned runs.
- **missing:** A checkpoint/resume state machine shared by relay, Mac agent, and browser bridge; Idempotency keys and per-step preconditions so a reconnect cannot duplicate sends, purchases, or edits; A pendant-visible queue of pending approvals and reconnect-safe acknowledgement; Independent verification receipts for each checkpoint, not just a final job receipt

### ""Keep these things consistent everywhere": when I change a real-world commitment, update every dependent surface—calendar, messages, files, and browser forms—as one coordinated operation, and stop with a precise list of what changed if any surface cannot be made consistent."
- **useful because:** Owners routinely make commitments that span applications. Today the Mac agent can act in individual surfaces, but cannot guarantee that a calendar change, notification, and related document either agree or are safely reconciled. This would prevent contradictory schedules and half-completed updates.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-judgement → faculty-perception → faculty-action
- **model tier:** Background model derives dependency graph and compensation plan; realtime model is used only for ambiguity or owner-facing confirmation.
- **latency:** Plan under 5 s; each mutation may take seconds; owner receives a progress event within 1 s of each committed or compensated step.
- **cost:** $0.02–$0.10 per coordinated operation, dominated by cross-app perception and compensation planning.
- **security:** Never send private contents to the relay or pendant. Each mutation needs a bounded scope, idempotency key, and an explicit compensation policy. If compensation is unsafe, stop before the next mutation and report a partial state rather than guessing.
- **missing:** A dependency-graph representation for related app/browser artifacts; Cross-surface idempotency and compensation primitives; A durable consistency receipt that records each surface's before/after digest; Owner-configurable rules for which compensations are allowed automatically

### ""Teach you this once": let me perform or correct a multi-surface workflow, then save the demonstrated sequence as a private, parameterized playbook that I can invoke by voice later—with approval boundaries preserved and a preview of every step that can affect another person or account."
- **useful because:** The owner cannot currently turn a corrected one-off action into a reliable personal procedure. A playbook would make the hive mind improve from interaction rather than repeatedly rediscovering the same workflow, while keeping risky steps explicit instead of silently learning authority.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-judgement → faculty-action → faculty-perception
- **model tier:** Background model extracts and generalizes the workflow; realtime model handles the demonstration conversation and disambiguates parameters.
- **latency:** Capture corrections inline; later invocation should produce a preview in under 3 s and execute each step with normal surface latency.
- **cost:** $0.01–$0.08 per invocation; extraction costs occur once per newly taught playbook, with storage and verification dominating thereafter.
- **security:** Playbooks must store selectors, parameter schemas, risk classes, and redacted examples—not credentials, page contents, or private message bodies. Any changed UI or account context invalidates the affected step and requires re-perception. Owner can revoke a playbook and inspect its history.
- **missing:** A private playbook store with versioning and revocation; Demonstration-to-parameter extraction and selector generalization; A policy-preserving compiler from playbook steps to existing action risk/approval modules; Regression tests that replay steps against fresh perception without performing mutations


## Changes it proposed to its own stack

### `integration` — Add a USB-local action bridge mode: when the nRF9160 pendant and ESP32 audio bridge are connected to the Mac, the Mac agent exposes a narrowly scoped serial protocol for pending-operation summaries, approval/cancel gestures, progress beacons, and signed receipts. The relay treats this as the same physical_transaction_approval_latch envelope used by LTE, with a transport-neutral monotonic counter and replay protection. No firmware flashing, secrets, or raw audio is required.
- **owner gets:** The owner can use the pendant's physical safety control today, even though LTE registration is absent. Actions can be approved or cancelled by touch while the pendant is worn, and the system can speak completion or uncertainty through the already verified 24 kHz path instead of pretending the offline device is unreachable.
- effort: Medium: serial framing and reconnect handling in the Mac bridge, firmware-side parser/UI integration, relay transport adapter, and hardware-in-the-loop tests.  ·  risk: Malformed or replayed serial frames could approve an action; require MAC/nonce binding, monotonic counters, expiry, and fail-closed behavior. On disconnect, leave the operation staged/unknown—never infer approval or success. Recover by reconnecting and reconciling the durable envelope.
- cost: Negligible API cost; roughly 1–2 weeks engineering. No new hardware cost or meaningful power increase while USB-attached.  ·  latency: Approval and cancellation can be sub-300 ms locally; relay reconciliation adds network latency only for final commit/status.
- security: Improves the physical security boundary without exposing secrets to the pendant. USB is treated as an untrusted transport with authenticated envelopes, not as a trusted cable.
- depends on: physical_transaction_approval_latch (s10-j9l4); truthful_action_status_beacon (s15-cbhs); A transport-neutral operation envelope and replay protection; A documented serial framing contract for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; Owner approval policy for action risk classes

### `context` — Create a cross-surface commitment graph owned by the owner: represent a commitment (event, person, deadline, artifact, and communication obligations) as a private semantic object, then have judgement and action resolve all linked calendar, message, file, and browser records before proposing a mutation. Perception periodically detects drift and presents only the affected edges; action can repair them through explicit, per-edge approvals.
- **owner gets:** The owner could say “move the launch to Thursday” once and get a trustworthy answer about every affected commitment, rather than manually remembering which calendar entry, document, form, and person now disagree.
- effort: High: private graph schema, entity resolution across Mac/browser surfaces, drift detection, owner correction UI, and integration with action approval and verification.  ·  risk: Incorrect linking could cause unrelated records to be changed. Default to read-only suggestions, require per-edge confirmation for ambiguous links, retain reversible history, and allow one-command graph freeze/revoke.
- cost: Low steady API cost for local metadata; occasional model cost for entity resolution and drift explanation. No new hardware cost.  ·  latency: Initial graph construction is minutes in the background; an individual query should answer in a few seconds, with mutations remaining explicitly staged.
- security: Graph contains highly sensitive relationship and schedule metadata. Keep raw contents on the Mac, send only hashes/labels to relay, encrypt at rest, and make sharing/export impossible by default.
- depends on: Private local memory store and revocation controls; Cross-surface entity-resolution model; Independent perception of calendar, files, browser, and messages; The coordinated-operation capability and owner approval policy


## What it asked for

_Nothing._
