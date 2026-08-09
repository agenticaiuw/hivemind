# Harness derivation — faculty-action — round 260

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Finish the web purchase or form I started, but never submit it twice if the connection drops."
- **useful because:** The owner can recover from a flaky browser/network session without duplicate orders, duplicate messages, or guessing whether the first submission succeeded. The system can inspect the logged-in browser, compare a stable idempotency marker or confirmation state, and only ask for physical approval when a genuinely new submission is required.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background model plans and classifies the recovery; realtime model is used only if the owner is actively asking. Mac/browser actions perform the workflow, relay owns the operation ledger, and faculty-perception verifies the postcondition.
- **latency:** Under 2 seconds to report current state; 5-20 seconds for browser inspection and recovery. No repeated submission while state is unknown.
- **cost:** Roughly $0.01-$0.08 per recovery, dominated by browser inspection and one planning call; verification and ledger work are local.
- **security:** Never transmit form secrets or page contents to the pendant. Treat an ambiguous result as unknown, not failure. Require the existing physical transaction approval latch for any new irreversible submit; retain only hashes, URLs, and redacted confirmation evidence.
- **missing:** A first-class idempotency/ambiguity state in the operation ledger; Browser adapters for site-specific confirmation markers; A recovery planner that can compare pre-submit and post-submit state

### "When I approve something on the pendant, let me ask later what I approved and whether it really happened."
- **useful because:** A haptic approval is easy to forget, especially offline. The owner gets a trustworthy, privacy-preserving answer instead of a vague success tone: the intended action, time, risk class, current result (verified, unknown, cancelled), and the evidence source.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Cheap background summarization of the existing ledger; realtime only for the spoken query. No model is allowed to infer completion when a receipt or verifier is absent.
- **latency:** Immediate local answer for the last 16 decisions; under 3 seconds for older ledger lookup.
- **cost:** Near-zero for local indexed lookup; at most a few cents when a short natural-language summary is generated.
- **security:** The pendant receives opaque IDs and short redacted summaries, never message bodies, credentials, or page contents. Require owner presence for detailed disclosure and expire sensitive summaries. Distinguish approved from executed and verified from unknown.
- **missing:** A privacy-filtered decision-history query exposed to the pendant; Ledger schema linking approval nonce, executor receipt, verifier receipt, and human summary; A compact offline inbox response format

### "If I'm moving or driving, hold non-urgent actions and tell me only what truly needs my attention; let urgent safety actions through."
- **useful because:** The pendant becomes context-aware without relying on a distracting screen. Motion from the owned IMU can suppress routine prompts and prevent an accidental approval while walking, while the relay and Mac continue preparing work and deliver a concise digest when the owner is still.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Firmware classifies motion locally with deterministic thresholds; a cheap background model classifies action urgency. Realtime is used only for an active conversation.
- **latency:** Motion state under 100 ms locally; policy decision under 1 second; deferred digest at the next stillness window.
- **cost:** Negligible device compute and relay storage; occasional small classification call, under $0.01 per digest.
- **security:** Motion is sensitive behavioral data: export only coarse states (still, moving, high-motion), never raw IMU. Safety-critical alerts bypass suppression. Motion must inhibit approval, not silently approve or execute anything.
- **missing:** The pending motion_context_safety_gate firmware skill; An urgency policy table with owner-configurable defaults; Relay delivery semantics for deferred versus urgent notifications

### "Before you send or buy anything, let me inspect the important fields one at a time on the pendant and change or reject any field without exposing the full page or secret."
- **useful because:** The owner can safely approve a real transaction while away from a screen. A short spoken summary is not enough for amounts, recipients, dates, or destinations; tactile/rotary review makes the approval meaningful without putting credentials or page contents on the wearable.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background model extracts a typed, redacted set of consequential fields from the browser state. Realtime is used only for the owner's live questions. Deterministic firmware presents fields and records the selected values; it must not interpret secrets.
- **latency:** Field list in 1-2 seconds; each field change under 300 ms; submission only after explicit final approval.
- **cost:** A few cents per transaction, dominated by structured extraction and browser verification; field navigation is local.
- **security:** The pendant receives labels and masked values, never passwords, full message bodies, or payment numbers. The browser must re-check that the approved field digest still matches immediately before submission. Any changed digest invalidates approval.
- **missing:** Typed consequential-field extraction contract; Rotary encoder and second-button firmware integration; Pendant field-review UI with masked values; Browser-side patch-and-reverify support

### "Let me start a task on the pendant, continue it on the Mac or logged-in browser later, and have the system bring back exactly what was pending without making me repeat myself."
- **useful because:** The owner can begin while away from a screen and finish when the Mac is available. The handoff preserves intent, constraints, pending questions, and expiry rather than replaying a vague transcript or silently executing an old request.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Relay stores a compact typed task envelope; a background model resolves it into a Mac/browser plan when a surface returns. Realtime is unnecessary unless the owner resumes by voice.
- **latency:** Pendant acknowledgement under 1 second; resume state under 3 seconds after Mac/browser return; stale tasks must remain paused rather than auto-run.
- **cost:** Usually under $0.02 per handoff; storage and routing dominate, not inference.
- **security:** Persist only the minimum intent and opaque references; expire sensitive envelopes. Never carry browser credentials or page secrets through the relay. Revalidate all facts and approval requirements at resume time.
- **missing:** A cross-surface typed task envelope with versioning and expiry; Resume UI that exposes pending questions and stale assumptions; Relay-to-Mac wake/retry trigger with explicit non-execution semantics

### "When something I asked for becomes possible later, bring it back to me with the reason it was blocked and the one decision or action needed to continue."
- **useful because:** The owner should not have to remember failed attempts, reconnect a cable, reopen a browser tab, or ask repeatedly. This turns blocked work into a durable, truthful queue instead of silently dropping it or retrying unsafely.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic relay state machine tracks blockers and retries; a cheap background model writes a one-sentence explanation. Realtime is only for delivery during an active conversation.
- **latency:** Record a blocker immediately; retry on surface availability within seconds; notify once per meaningful state change, not on every poll.
- **cost:** Near-zero for state transitions; less than a cent for occasional summaries.
- **security:** Blocker summaries must not leak credentials or private page content. Retrying a blocked mutation requires renewed preconditions and, where applicable, fresh physical approval. Expiry and cancellation must be explicit.
- **missing:** A first-class blocked state with typed blocker reasons; Dependency-triggered retry rules across relay, Mac, and browser; Deduplicated owner notification history and cancellation controls


## Changes it proposed to its own stack

### `integration` — Add an explicit unknown/ambiguous terminal state and idempotency key to every multi-step operation. POST /execute receipts, browser results, the action ledger, and verify_operation_step must all carry the same operation_id, attempt_id, and idempotency_key; retries must first run read-only verification and may never replay a mutating step while the result is unknown.
- **owner gets:** A dropped connection will stop causing duplicate purchases, messages, or calendar changes. The owner gets an honest 'I don't know yet' state and safe recovery instead of either dangerous replay or silent abandonment.
- effort: Medium: ledger migration, executor guard, browser adapter contract, and verifier correlation tests.  ·  risk: Old jobs lack keys and must be treated as non-retryable until manually reviewed. A bad site marker can leave work paused; recovery is a visible approval-required review, never an automatic second submit.
- cost: Small storage and engineering cost; reduces expensive duplicate actions and model retries.  ·  latency: Adds one read-only verification round before retry, typically 0.5-3 seconds.
- security: Improves auditability; keys must be opaque and must not contain form data or secrets.
- depends on: verify_operation_step; Existing action ledger and approval handoff; Browser result correlation


## What it asked for

_Nothing._
