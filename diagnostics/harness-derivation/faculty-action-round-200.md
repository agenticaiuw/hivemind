# Harness derivation — faculty-action — round 200

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When you say “send this,” carry the operation through browser/Mac execution and tell me truthfully whether it committed; if the result is unknown, reconcile the live state and either safely finish, undo, or leave it explicitly pending for my approval."
- **useful because:** Today an executor receipt can say a click ran without proving the intended world state. This is the single most useful action capability: it turns ambiguous failures into safe, understandable outcomes rather than duplicate sends or false success.
- **path:** unified → faculty-judgement → faculty-action → faculty-perception → mac-planner → mac-vision → browser-extension → relay-realtime
- **model tier:** background for planning/reconciliation; realtime only for the owner's conversational explanation
- **latency:** 2–5 s for ordinary execution; up to 15 s for postcondition reconciliation; never silently retry a non-idempotent action
- **cost:** One cheap planner call plus one verifier call per uncertain step; roughly 1–3¢ excluding realtime explanation. Dominant cost is browser/Mac round trips, not tokens.
- **security:** Action envelope contains only opaque operation IDs and redacted summaries on the pendant; secrets stay in browser/Mac. Non-idempotent retries require the existing physical transaction approval latch. Unknown outcomes must default to pending, not retry.
- **missing:** A durable reconciliation state machine that joins executor receipts, verify_operation_step evidence, and actionLedger by operation/attempt IDs; Per-action idempotency/undo metadata exposed to faculty-action; A relay-visible pending/unknown queue with expiry and owner-facing explanation

### "If my Mac or browser drops offline halfway through a task, keep the task as a resumable checkpoint—not a vague failed job—and when it returns, show me exactly which step is next before continuing."
- **useful because:** A multi-step task currently spans local jobs, browser commands, and relay state, but the owner cannot reliably resume at the first uncommitted step without risking duplicate side effects. This makes interruptions recoverable while preserving the physical approval boundary.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → faculty-action → faculty-perception → unified
- **model tier:** background/cheap model for checkpoint bookkeeping and dependency ordering; realtime only to notify the owner
- **latency:** Checkpoint each step in under 100 ms; resume preflight under 2 s after heartbeat; wait for explicit confirmation when the next step is irreversible
- **cost:** Usually under 1¢ per resumed task; storage and browser heartbeats dominate, not model calls.
- **security:** Persist hashes and redacted selectors, never page secrets or message bodies. A checkpoint is not consent: resume only reversible steps automatically; irreversible next steps use the pendant latch and expire stale checkpoints.
- **missing:** A cross-surface checkpoint schema with step dependency, attempt number, precondition hash, and next-action risk; Atomic lease/claim so relay, Mac, and browser cannot resume the same checkpoint concurrently; A user-visible diff between last verified state and current state before resumption

### "Before you act on a sensitive browser or Mac task, give me a tiny, concrete preview on the pendant—what will change, where, and whether it can be undone—then let one deliberate gesture authorize exactly that operation and nothing broader."
- **useful because:** The owner should not have to trust an opaque “approve” prompt or receive page contents on a wearable. Binding a redacted impact preview to the exact operation digest makes physical approval meaningful and prevents a queued action from being swapped after approval.
- **path:** faculty-judgement → faculty-action → faculty-perception → relay-realtime → mac-planner → browser-extension → mac-vision
- **model tier:** Cheap background model generates the redacted natural-language preview; realtime only reads it aloud if requested
- **latency:** Preview in under 1 s for known action classes; approval envelope valid for 60 s and one execution attempt only
- **cost:** Sub-cent for templated previews; one verifier call after execution. Main cost is secure relay persistence and device delivery.
- **security:** Never send form values, page contents, tokens, or message bodies to the pendant. Include operation digest, target class, reversibility, expiry, and attempt nonce; refuse mismatches, replay, expiry, or broadened scope. Default to stage, never auto-approve unknown classes.
- **missing:** A canonical redacted impact-summary renderer shared by planner and action; A digest binding the preview to exact executor parameters and verifier postconditions; Pendant firmware support for rendering/acknowledging compact structured previews beyond outcome beacons

### "Only carry out this action if the exact thing I approved is still true at the instant you act; if the page, file, recipient, amount, or permissions have changed since I approved it, stop and ask me again."
- **useful because:** A preview and approval can become unsafe in the seconds before execution: a page can navigate, a file can be replaced, or a recipient can change. The owner needs approval to mean “this exact state transition,” not merely “something resembling this action.”
- **path:** faculty-perception → faculty-judgement → faculty-action → mac-planner → mac-vision → browser-extension → relay-realtime → unified
- **model tier:** Cheap deterministic state hashing and policy checks; use a slower model only to explain a mismatch to the owner
- **latency:** Precondition recheck within 250 ms of dispatch; abort immediately on mismatch; explanation within 2 s
- **cost:** Less than 1¢ for ordinary operations; dominated by fresh Mac/browser reads and hashing
- **security:** Hash only sensitive values and keep secrets off the pendant. Bind the approval to resource identity, relevant field names, allowed mutation, expiry, and one attempt. A mismatch must fail closed, never silently refresh the approval.
- **missing:** A cross-surface optimistic-concurrency protocol with signed precondition snapshots; Per-action declaration of which state fields are security-relevant and which changes invalidate approval; Executor enforcement that rejects an approval whose snapshot or scope no longer matches


## Changes it proposed to its own stack

### `interaction` — Add an owner-visible “approval provenance” view: after any pendant-approved operation, the Mac and relay retain a compact chain showing the redacted preview digest, physical approval event, executor attempt, independent state observation, and final disposition. The view must distinguish “approved,” “dispatched,” “verified,” “undone,” and “unknown,” and allow the owner to revoke future approvals issued by a compromised or lost pendant session.
- **owner gets:** When something consequential happens, the owner can answer “what exactly did I approve, what actually ran, and who established that it worked?” without exposing the underlying message, form, or file contents. It also gives a practical response to a lost pendant or stale approval session.
- effort: Medium: shared event schema and append-only relay record, plus a compact Mac/dashboard presentation; no new hardware required  ·  risk: Metadata could reveal sensitive timing or targets, so redact names and values by default and expire detailed provenance. If provenance storage is unavailable, execution status must remain unknown rather than be invented.
- cost: Low storage and negligible model cost; one short background summarization only when the owner opens the view  ·  latency: No added execution latency if events are appended asynchronously; verification remains a prerequisite for “verified” status
- security: Improves auditability but creates a sensitive metadata trail. Encrypt at rest, scope records to the owner, and support revocation of unconsumed approval tokens.
- depends on: Canonical operation/attempt IDs; A live independent postcondition verifier rather than receipt-only completion; The existing physical transaction approval latch; Relay persistence for append-only outcome events


## What it asked for

_Nothing._
