# Harness derivation — relay-realtime — round 88

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Stop what you’re doing on my Mac right now,” or “finish only the first part, then wait for me.”"
- **useful because:** A long Mac/browser task should remain under the owner’s live control even after the original spoken turn ends. Today the relay can hand off work, but the owner cannot reliably interrupt or safely narrow an in-flight multi-step job from the pendant; this would prevent an unwanted later step without requiring the owner to reach the Mac.
- **path:** relay-realtime → mac-planner → browser-extension → dashboard-ux
- **model tier:** Realtime handles the short interruption command and intent matching; the existing slower Mac planner/computer-use tier performs the task. No expensive model call is needed for status-only updates.
- **latency:** The pendant should acknowledge stop/pause in under 1 second, and the downstream agent should reach a cancellation checkpoint within 2 seconds. The owner should hear whether cancellation was accepted, already completed, or could not be stopped.
- **cost:** About $0.001–$0.01 per interruption, dominated by one short realtime turn; status polling and cancellation receipts should be local/relay operations with negligible model cost.
- **security:** The relay must bind the interruption to the owner’s active job/session and reject stale or ambiguous job references rather than stopping unrelated work. Cancellation must be cooperative and idempotent, with a durable receipt identifying the last completed action; already-completed external effects cannot be undone silently. The command and resulting receipt should be retained in the normal private operation history.
- **missing:** A durable, authenticated cancel/pause/resume command on the relay-to-Mac job protocol; Planner checkpoints before every externally visible action, with a cancellation state and last-safe-boundary receipt; Browser-extension support for cancelling queued commands and reporting whether a browser action has already committed; A pendant-facing active-job summary so “that thing” resolves to the currently spoken or most recently handed-off job

### "When my Mac agent gets stuck, ask me one short question through the pendant—“Which Alex?” or “Which folder?”—then continue the same task when I answer."
- **useful because:** Today a delegated task tends either to guess, fail, or wait invisibly when a detail is ambiguous. The owner should be able to resolve a narrow question from wherever they are, without repeating the whole request or sitting at the Mac. This is different from status reporting: it is a resumable clarification exchange tied to the exact blocked step.
- **path:** mac-planner → relay-realtime → relay → browser-extension → dashboard-ux
- **model tier:** The Mac planner detects an action-level ambiguity and emits a structured clarification candidate; realtime delivers the one-sentence question and normalizes the owner’s answer. The planner then resumes, while a cheaper background component can expire unanswered questions.
- **latency:** Question delivery under 2 seconds after the planner reaches the blocked step; resume within 3 seconds of the owner’s answer. Only one active question per job, with a clear spoken timeout/expiry response.
- **cost:** Approximately $0.002–$0.02 per clarification, mostly one short realtime exchange; no additional inference is needed for transport, job binding, or timeout.
- **security:** The question must identify the app/task without leaking sensitive page contents, and the answer must be bound to a single authenticated job plus a short-lived nonce. Never treat unrelated speech as an answer. Record the question, answer, and resumed action in the job receipt; expire unanswered questions rather than guessing.
- **missing:** A bidirectional clarification message type from Mac planner to relay and back, with job ID, nonce, expiry, and typed choices/free text; A pendant UX for speaking or selecting a response while preserving the active conversation; Planner pause/resume checkpoints that retain task state without replaying already-committed actions; Browser-extension propagation of a clarification when the ambiguity is in an authenticated tab


## Changes it proposed to its own stack

### `relay` — Implement a real relay-side capability inventory endpoint and publish it (e.g., GET /v1/relay/capabilities) plus a lightweight health/introspection route for pendant delivery endpoints (e.g., /v1/pendant/*). Include route names, auth requirements, and a minimal schema so the relay agent can stop guessing what exists on its own surface.
- **owner gets:** The pendant experience becomes more reliable: the relay can correctly route, acknowledge, and debug voice actions without accidentally relying on invisible endpoints. That means fewer dropped requests and clearer voice feedback.
- effort: Medium. Define schema, wire to Worker router, expose only safe metadata, add tests, and keep it in sync with deployed routes via a build step.  ·  risk: Exposing internals could leak implementation details. Mitigate by returning only route names and purpose-level metadata, not secrets or full configs. If the endpoint fails, relay should continue to operate with conservative defaults.
- cost: Small runtime cost per introspection call; negligible infra cost. Biggest cost is engineering time.  ·  latency: No impact on normal voice flow; used sparingly for debugging and routing confidence.
- security: Positive if done carefully: reduces misrouting. Ensure output is sanitized and requires appropriate auth. Avoid reflecting user data or secrets.

### `integration` — Build a durable, cross-surface job lifecycle service: a single job record that can be created by the relay, executed by mac-planner/browser, and observed by the relay later. It should support state transitions (queued/running/blocked/succeeded/failed), progress notes, artifact pointers, and user-facing receipts. Provide a relay-safe read API for status and a subscription/push mechanism for completion events to the pendant.
- **owner gets:** They can ask for something, leave, and later hear exactly what happened. The system can also recover gracefully from offline Mac/browser periods and resume work when connectivity returns.
- effort: High. Requires storage, routes, coordination with mac-planner/browser harness, and a completion notification path to the pendant.  ·  risk: Race conditions, duplicate execution, and confusing user messaging. Mitigate with idempotency keys, receipts, and clear state transitions. Provide undo where possible.
- cost: Medium ongoing cost for storage and occasional polling; higher engineering cost upfront.  ·  latency: Adds minimal overhead at start; improves end-to-end reliability for long tasks.
- security: Sensitive artifacts must be access-controlled and redacted for voice summaries. Store minimal data and encrypt where appropriate.
- depends on: A durable store for jobs and receipts; A relay-visible status API; Notification delivery path to pendant


## What it asked for

_Nothing._
## Its own summary

Recorded a new cross-node capability: a resumable clarification loop, where the Mac/browser planner asks one bounded question through the pendant and resumes the exact job after the owner answers. The required missing work is a bidirectional, nonce-bound clarification protocol, planner checkpoints, and browser propagation. I also submitted an interruption capability, though the system flagged it as close to existing job/undo behavior; the genuinely new gap is live clarification, not another status or cancel surface.

**Biggest unknown:** Whether the existing relay/agent transport already supports a reverse Mac-to-pendant event stream that is undocumented; if it does, only the typed clarification state machine and planner checkpoints remain.

