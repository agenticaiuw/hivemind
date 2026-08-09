# Harness derivation — faculty-action — round 172

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac permissions and browser bridge** — GET /ops/status now reports AI Pendant Agent Accessibility and Screen Recording granted, requiredMissing empty, ready true; Safari browser bridge online with 9 tabs and zero pending commands. Relay reachable, but device registry still lacks pendant.
  - evidence: GET /ops/status HTTP 200 at round 172

## Capabilities it proposed

### ""Fill in the form, but keep my passwords and private page contents on my Mac, and tell me only whether it succeeded.""
- **useful because:** Lets the browser extension use authenticated sessions without exporting secrets to the relay, model, or pendant; the owner gets a completed task plus a trustworthy minimal result.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for planning; realtime only for the owner's spoken request
- **latency:** Under 10 seconds for ordinary forms; staged approval before submission when the action is high risk.
- **cost:** One planning call plus cheap local/browser execution; typically <$0.03, dominated by model planning rather than browser operations.
- **security:** Field values and page contents stay in the browser/Mac process. Relay receives only a redacted intent, field identifiers, hashes, and success/failure provenance. Submission requires the existing physical approval latch; never put credentials in pendant audio or relay logs.
- **missing:** Browser-side secret-field executor that accepts a typed intent and writes only locally; A browser result schema for redacted field attestations and submission receipts; Owner policy marking which domains/actions may be submitted without an extra approval

### ""Stop whatever the AI is doing right now.""
- **useful because:** A physical stop path is the safest high-value action: one button press on the worn device cancels queued Mac/browser work even when the owner cannot reach the keyboard or voice session.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** No model on the stop path; relay and Mac execute a deterministic cancel broadcast.
- **latency:** Visible pending/cancelled state within 250 ms when linked; queued cancellation token survives a link drop and is applied before the next action.
- **cost:** Negligible API cost; a small relay event and local cancellation check. Hardware uses existing button/LED and audio path.
- **security:** Only cancellation is allowed from this gesture, never approval. Every executor checks a monotonic cancel generation before each side effect; receipts distinguish cancelled-before-start, interrupted, and unknown. The relay must not claim reversal of an already-completed external action.
- **missing:** Pendant event transport while currently USB-attached and later LTE-attached; Mac executor cancellation hook between action steps; A relay cancel-generation record and dashboard indicator

### ""Only let a sensitive action run while my pendant is physically present, and show me exactly what happened afterward.""
- **useful because:** Turns the worn device into a local presence-and-receipt boundary: a stolen or unattended Mac session cannot silently carry out queued high-impact work, while the owner gets a short physical confirmation and an auditable result.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Cheap deterministic policy checks; use the realtime model only to summarize the final receipt in speech.
- **latency:** Presence check under 1 second; result receipt within 3 seconds after execution.
- **cost:** Near-zero inference cost for gating; one optional short summary call, typically <$0.01.
- **security:** USB serial presence is evidence of attachment to this Mac, not proof the pendant is being worn; treat it as a weaker mode than deliberate button confirmation. Store only device ID, nonce, timestamps, and action digest. Fail closed when presence or receipt verification is stale.
- **missing:** Authenticated pendant presence heartbeat and monotonic nonce protocol; Policy levels distinguishing USB-present, radio-present, and deliberate physical approval; A receipt renderer for one-LED/audio feedback and dashboard provenance

### ""I need to tell you something private. Keep it out of transcripts, model training, Mac logs, browser history, and pendant storage, then forget it when this task is done.""
- **useful because:** The owner can use the system for passwords, health details, legal matters, or personal crises without having to trust every ordinary persistence layer. Today there is no end-to-end, independently auditable ephemeral mode.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime only for the live exchange; no background summarizer or memory writer may receive the payload.
- **latency:** Mode activation under 1 second; deletion receipt within 5 seconds of task completion.
- **cost:** Slightly higher relay/storage cost for deletion receipts and key rotation; no extra model call beyond the conversation.
- **security:** Requires per-session encryption keys, memory/log suppression at every hop, browser history suppression where possible, and a deletion receipt that contains only hashes and timestamps. The system must say when a third-party service necessarily retained data; it cannot promise deletion outside its control.
- **missing:** Ephemeral-session protocol spanning pendant, relay, Mac, and browser; A hard persistence deny-list enforced below individual features; Cryptographic destruction and an auditable zero-content deletion receipt; Owner-visible indication that ephemeral mode is active

### ""Before you send or publish anything, stop if it contains private information I said must never leave this device—even if I forgot to ask for approval.""
- **useful because:** Prevents accidental disclosure across email, messaging, browser forms, social posts, and uploads. Approval alone is not enough when the owner does not notice a secret or sensitive detail embedded in a draft.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** A cheap local deterministic classifier handles known labels; a slower model is used only for ambiguous text and never receives protected raw values when local classification suffices.
- **latency:** Under 500 ms for known patterns; under 3 seconds for an ambiguous draft, with sending held during analysis.
- **cost:** Usually near-zero inference cost using local rules; occasional classification call under $0.01.
- **security:** The policy engine must classify before network submission, not after. Protected values and classifier explanations stay local. False positives must offer redact/review, never silently rewrite. The owner can define classes such as passwords, medical details, financial identifiers, or home address.
- **missing:** Local outbound data-loss-prevention hook covering browser, Mail, Messages, and file uploads; A user-editable sensitivity policy with durable versioning; Redaction preview and an explicit override path tied to the existing approval mechanism; Provenance proving the inspected bytes equal the submitted bytes

### ""If the Mac is asleep, the browser is closed, or the relay is unreachable, remember exactly what I asked and resume only when the same conditions are safe again—without making me repeat myself.""
- **useful because:** The owner gets durable intent continuity across real interruptions instead of a lost conversation or an action that runs under changed circumstances. This is not merely an offline audio spool: it preserves an unexecuted intent, its safety prerequisites, and its expiry.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Cheap background model may normalize the intent after connectivity returns; deterministic code owns expiry, prerequisite checks, and replay. Realtime is not needed.
- **latency:** Capture locally within 200 ms; resume decision within 10 seconds of all required surfaces becoming healthy.
- **cost:** Small durable metadata cost; one inexpensive normalization call per recovered intent, typically <$0.01.
- **security:** Never replay against a changed recipient, account, URL, or price without revalidation. Store a compact intent digest and safety constraints, not secrets or page contents. Expired intents must be discarded with a receipt rather than executed late.
- **missing:** A typed durable intent record distinct from audio outbox items; Prerequisite snapshots for app, account, URL, and browser state; Safe replay planner with expiry and change detection; A user-facing recovery queue showing pending, blocked, expired, and resumed intents


## Changes it proposed to its own stack

### `relay` — Add a capability-scoped USB pendant session: the Mac bridge opens the live serial link, performs mutual challenge-response, and exposes a short-lived device session to relay actions. It must distinguish link presence from owner approval, rotate nonces, and emit disconnect/reconnect receipts without claiming LTE availability.
- **owner gets:** The pendant that is physically connected to the Mac today becomes usable immediately as a trusted control surface, while the system stays honest that it is not yet LTE-registered.
- effort: Medium: serial framing, device identity provisioning, reconnect state machine, and relay session binding.  ·  risk: A stale or cloned device could be mistaken for the pendant; fail closed on nonce mismatch and require explicit re-pairing. USB disconnect during an action must produce unknown status, not success.
- cost: Negligible API cost; no hardware cost. Small persistent session metadata only.  ·  latency: Sub-second challenge and event delivery over USB.
- security: Improves possession binding but does not replace physical approval; secrets remain out of logs and device payloads.
- depends on: Pendant serial protocol and identity key provisioning; Relay device-session route; A deterministic Mac serial transport implementation

### `mac-harness` — Make every multi-step executor checkpoint a cancellable, verifiable action boundary: before each side effect, read the current cancel generation; after it, persist the exact step receipt and expose a narrow postcondition for faculty-perception to verify.
- **owner gets:** When the owner says stop, disconnects the pendant, or asks what happened, the system can say which step ran, which did not, and which outcome is unknown instead of guessing.
- effort: Medium-high across executor, job ledger, and verifier integration.  ·  risk: Cancellation between an external side effect and its receipt can still leave unknown outcomes; surface that explicitly and offer undo only where the target supports it.
- cost: Low storage and negligible inference cost; verification may add one local read per step.  ·  latency: Tens to hundreds of milliseconds per checkpoint, depending on browser state.
- security: Reduces silent partial execution and makes action receipts auditable; do not persist page secrets in receipts.
- depends on: Granted verify_operation_step; Executor step IDs correlated to job receipts; Relay cancel generation record


## What it asked for

_Nothing._
