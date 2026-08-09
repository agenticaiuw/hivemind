# Harness derivation — faculty-action — round 174

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I ask “what did you just do?”, give me a short, trustworthy replay of the last action: what was attempted, what actually changed, what was verified, and what remains unknown—without rerunning it."
- **useful because:** The owner can audit an action hands-free immediately after it happens, instead of relying on vague success language or opening the Mac. This is the single most useful action-safety capability: it makes automation understandable and recoverable.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for receipt summarization; realtime only to answer the spoken query
- **latency:** Under 2 seconds from voice query; no new Mac/browser action unless the owner explicitly asks.
- **cost:** <$0.01 per replay; dominated by a small receipt-summary model call, often zero if a deterministic template suffices.
- **security:** Receipts may mention private files, apps, or browser domains. Keep sensitive fields on the relay/Mac, send only the minimum spoken summary to the pendant, and require explicit confirmation before exposing secrets or message contents.
- **missing:** A durable replay cursor keyed by action/attempt and a redaction policy for spoken receipts; A canonical receipt schema joining executor output to independent verification provenance

### "If I hold the pendant’s cancel gesture, stop every queued or in-flight Mac and browser action, then tell me which ones were stopped, which may already have taken effect, and verify that no new step starts."
- **useful because:** A physical emergency stop is useful when an automation is visibly going wrong or the owner changes their mind. It works even when the Mac screen is inaccessible and gives a bounded, truthful result rather than pretending cancellation rewinds an external side effect.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime for the stop command and concise status; background for reconciliation of affected jobs.
- **latency:** Issue cancellation within 500 ms of the relay receiving the pendant event; reconcile and speak a status within 5 seconds.
- **cost:** <$0.01 per stop, mostly deterministic routing; background reconciliation may use one cheap model call.
- **security:** Cancellation itself must not require page contents or secrets. It cannot undo already-sent messages or purchases; report those as possibly effective. Authenticate the pendant event with the physical transaction nonce and retain an immutable stop receipt.
- **missing:** A fan-out cancellation primitive covering Mac and browser executors; Executor cancellation acknowledgements and a post-stop quiet-period verifier; Firmware mapping for the safe cancel gesture on sw1

### "Let me say “do this later” after an action is staged, and have the relay hold the action until its deadline, wake the Mac/browser only when needed, obtain fresh context, and ask for my physical approval again if the context or risk changed."
- **useful because:** The owner can delegate routine follow-up without leaving a Mac agent running or approving against stale prices, pages, or calendar state. Requiring fresh context and renewed approval prevents a harmless draft from silently becoming a different action hours later.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background/scheduled model for deadline handling and context comparison; realtime only for the final approval conversation.
- **latency:** Wake within 30 seconds of the deadline; speak the approval request within 2 seconds after fresh context is available.
- **cost:** <$0.03 per deferred action; dominated by fresh browser/Mac inspection and one small risk-diff summary.
- **security:** Persist only an action intent and hashes, never form secrets or page contents. Expire intents, bind them to the originating session, and require a new physical approval whenever any material input, destination, or risk tier changes.
- **missing:** Durable deferred-intent records with expiry and wake conditions; Fresh-context hash comparison across Mac and browser; Integration with the existing physical_transaction_approval_latch rather than a new approval mechanism

### "Before changing anything, let me ask “what would happen if you did this?” and receive a concrete preview of the resulting file, calendar, message, or browser changes—including conflicts and side effects—without mutating the Mac or browser."
- **useful because:** Today a plan is still an abstraction; the owner cannot inspect the exact proposed diff across private browser and Mac state from the pendant. A cross-surface shadow run would make consequential automation understandable before approval.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background model for shadow planning and diff explanation; realtime only to answer the short spoken preview.
- **latency:** Preview in under 10 seconds for ordinary tasks; never mutate while previewing.
- **cost:** $0.02–$0.10 per preview depending on browser/Mac inspection and diff generation.
- **security:** Private page contents and local files stay on their owning surfaces; return structured redacted diffs, not raw content. Any preview artifact expires and is bound to the exact proposed action hash.
- **missing:** A mutation-free shadow executor for AppleScript, file, and browser operations; A common cross-surface diff format with sensitivity labels; A verifier that proves the preview performed no writes

### "Fill a sensitive form for me without telling the model the secret: use the browser session or Mac keychain locally, show me only the non-secret fields and destination, then let me physically approve the exact submission."
- **useful because:** The owner could automate tedious logins, payment, and personal forms while keeping passwords, card numbers, and one-time codes out of model context and out of pendant audio.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime for destination/field confirmation; deterministic local executor for secret retrieval and insertion; background model only for non-secret field mapping.
- **latency:** Field preparation under 5 seconds; submission only after physical approval.
- **cost:** Usually under $0.02, dominated by non-secret page interpretation; secret retrieval is local.
- **security:** Secrets never cross the relay or model boundary. Use one-use capability tokens scoped to origin, field, and expiry; redact screenshots, logs, receipts, and spoken output. Refuse unexpected origins or extra fields.
- **missing:** A local secret-provider adapter with origin/field scoping; Browser and Mac executors that accept opaque secret handles rather than values; A verifier for field names/origin and a commit record proving the secret value was not exported

### "When an action depends on another person replying, let me say “watch this and tell me only when it matters”: monitor the relevant browser, Mail, or Messages state, suppress routine changes, and bring the pendant a concise alert with the exact reason and a safe next action."
- **useful because:** The owner cannot currently delegate a private, ongoing follow-up that spans browser and Mac sessions without polling or leaving an automation running blindly. This turns asynchronous waiting into a bounded personal assistant behavior.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Cheap background watcher and classifier; realtime only when a material event crosses the owner’s threshold.
- **latency:** Detect material changes within 1 minute; speak an alert within 2 seconds of classification.
- **cost:** $0.01–$0.05 per monitored day, dominated by polling and occasional classification; use hashes/diffs to avoid model calls.
- **security:** Watchers must be explicitly scoped to app, account, thread, and expiry. Keep message bodies local, send only minimal event summaries, and provide a physical cancel gesture and automatic expiration.
- **missing:** A durable cross-surface watch with event cursors and expiry; Incremental private diffs for Mail/Messages/browser state; A materiality policy editable by the owner without embedding it in model prompts


## Changes it proposed to its own stack

### `relay` — Add a canonical action-attempt receipt envelope: action_id, attempt_id, executor receipt, verifier receipt, risk tier, timestamps, redacted human summary, and an explicit outcome enum {verified, stopped, failed, unknown, possibly_effective}. Store it append-only and expose a deterministic spoken replay selector.
- **owner gets:** They will hear exactly what happened instead of a misleading “done,” and can ask for the same answer later without rerunning a side effect.
- effort: Medium: schema, receipt writers, redaction, and selectors across relay and Mac/browser adapters.  ·  risk: Older jobs lack verifier fields; migrate them as unknown rather than inventing success. Redaction bugs could leak private names, so default to app/domain-level summaries.
- cost: Negligible storage and request cost; avoids repeated model calls by using templates first.  ·  latency: Adds under 100 ms to normal completion; replay is typically sub-second.
- security: Improves auditability, but receipts need field-level sensitivity labels and strict bearer authorization.
- depends on: t21-8d1c verify_operation_step; truthful_action_status_beacon s15-cbhs; A durable replay cursor keyed by action and attempt

### `relay` — Implement a cancellation barrier: on a physical stop event, mark the session stopped, fan out cancellation to every queued/in-flight executor, reject new steps for a short quiet period, then ask Mac/browser perception for a read-only post-stop snapshot and emit one bounded receipt.
- **owner gets:** One deliberate gesture can halt a runaway automation even when the owner cannot reach the computer, while distinguishing halted work from effects that may already have escaped.
- effort: Medium-high: executor cancellation protocol, idempotent barrier state, quiet-period enforcement, and post-stop verification.  ·  risk: External actions already committed cannot be undone; network partitions can leave an executor uncertain. Surface unknown explicitly and keep retrying cancellation without duplicating side effects.
- cost: Low per event; one extra read-only verification round trip.  ·  latency: Cancellation dispatch under 500 ms target; final reconciliation within 5 s.
- security: Physical authenticated stop event becomes a high-priority control; prevent browser content or secrets from entering the pendant event.
- depends on: physical_transaction_approval_latch s10-j9l4; POST /jobs/:jobId/cancel; POST /jobs/:jobId/undo; Executor cancellation acknowledgements

### `routines` — Add deferred-intent records that contain an intent hash, expiry, wake condition, originating session, risk tier, and fresh-context hash. At wake, re-plan against current Mac/browser state and invalidate the old physical approval if any material field changes.
- **owner gets:** “Do this later” becomes safe delegation rather than a stale command executing against a changed page, price, recipient, or calendar.
- effort: Medium-high: durable scheduler, context hashing, material-change policy, and renewed approval handoff.  ·  risk: A too-sensitive hash causes needless prompts; a too-loose comparator permits stale execution. Default conservative and record why a change did or did not invalidate approval.
- cost: Small storage plus one background planning/inspection call per deferred intent.  ·  latency: Wake within 30 s of deadline, then approval prompt within 2 s after inspection.
- security: Persist hashes and intent metadata only; never persist browser secrets or form contents.
- depends on: POST /routines/:routineId/run; GET /watches; POST /plan; physical_transaction_approval_latch s10-j9l4; GET /browser/inspections


## What it asked for

_Nothing._
## Its own summary

Round 174 produced six recorded items: (1) spoken replay of the last action from executor plus independent verifier receipts, (2) a physical pendant emergency stop that cancels queued/in-flight Mac and browser work and reports possibly-effective effects, and (3) deferred “do this later” intents that wake against fresh context and require renewed physical approval if anything material changed. I also recorded implementation changes for canonical attempt receipts, a relay cancellation barrier, and expiry/context-hashed deferred intents. I told faculty-judgement about the three capabilities.

**Biggest unknown:** The remaining blockers are implementation seams, not another feature idea: a durable action/attempt receipt and replay cursor, executor cancellation acknowledgements plus a cross-surface barrier, and a scheduler/context-hash comparator for deferred intents. Full GUI/browser reach still depends on the owner’s denied TCC grants; no agent can grant those internally. I will not re-request the already-pending hardware revision/button-count or replay-cursor requests this round.

