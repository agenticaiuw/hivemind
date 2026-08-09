# Harness derivation — faculty-action — round 190

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Make this change, then tell me tomorrow if it stayed changed.”"
- **useful because:** The system would not stop at an executor receipt. It would act across the Mac/browser, independently verify the postcondition, and later detect drift or a failed follow-up—turning one-shot automation into a maintained outcome.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-action
- **model tier:** Realtime for the initial spoken request and concise confirmation; a cheaper background model for delayed checks and drift summaries.
- **latency:** Initial plan and confirmation under 3 seconds; execution under the normal Mac job budget; follow-up checks run asynchronously and only interrupt the owner for a material failure or drift.
- **cost:** About $0.01–$0.05 initial model cost plus pennies per scheduled check; Mac/browser execution and verification dominate latency, not tokens.
- **security:** Checks must use least-privilege locators and hash-only evidence by default. Never send page secrets or file contents to the pendant or relay. Delayed re-checks need an expiry and explicit cancellation; an automatically corrective action must remain staged unless the owner has separately authorized that class.
- **missing:** A watch schema that stores operation_id, step_id, postconditions, check_at/interval, expiry, and notification policy; A durable correlation between executor attempts and independent verifier calls; A drift notification path to the pendant that distinguishes warning, failed, and unknown

### "“What exactly changed when I asked you to do that?”"
- **useful because:** The owner gets a defensible, spoken audit trail rather than a vague “done”: intended operation, actual receipt, independent postcondition evidence, and any unknown or partial step are joined into one answer across relay, Mac, and browser.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-action
- **model tier:** A cheap background summarizer over structured receipts; realtime only when the owner asks or when a high-risk operation is unresolved.
- **latency:** Return a short first answer within 2 seconds from stored receipts; fetch fresh verification only when provenance is stale, then answer within 8 seconds.
- **cost:** Usually under $0.01 per query; the expensive part is fresh Mac/browser verification and evidence handling, not summarization.
- **security:** Default to summaries and hashes, with sensitive fields redacted. Require a fresh physical confirmation before exposing secret values or taking any corrective action. Preserve immutable receipt provenance and clearly say “unknown” when verification cannot run.
- **missing:** A read-only audit aggregator joining job, action-ledger, browser-command, and verifier IDs; Stable action_id/attempt_id fields carried from planning through execution and verification; A spoken/paged result schema with changed, unchanged, partial, and unknown states

### "“Prepare this task, but do not run it unless the required session is still valid and the deadline has not passed.”"
- **useful because:** This lets the owner safely delegate fragile, session-bound work (browser checkout, form submission, calendar change) while away. The relay stages intent, the Mac/browser executes only when preconditions hold, and the pendant reports expiry or a request for confirmation instead of silently acting on stale state.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-judgement → faculty-perception → faculty-action
- **model tier:** Realtime for staging and owner-facing status; background/local planner for precondition polling and execution scheduling.
- **latency:** Staging under 2 seconds; precondition polls are low priority; execution begins within 5 seconds of a valid window and reports immediately on expiry or ambiguity.
- **cost:** Roughly $0.01–$0.04 per staged task; polling is mostly local/relay I/O. Browser inspection and any required verification dominate.
- **security:** A staged task must contain only a redacted summary, digest, deadline, and allowed action class—not credentials or page contents. Expired or changed sessions fail closed. Irreversible operations still require the existing physical transaction latch; no retry may broaden scope.
- **missing:** A first-class precondition/deadline envelope for jobs; Session-validity and scope-digest checks for browser actions; A scheduler that can wake the Mac bridge and deliver expiry/ambiguity status to the pendant

### "“If this verified state ever drifts, repair it automatically—but only within the limits I set—and tell me if repair fails.”"
- **useful because:** Today a watch can observe a page, but the owner still has to notice drift and manually recover. This would close the loop: relay detects a changed invariant, Mac/browser performs only a bounded reversible repair, faculty-perception verifies the result, and the pendant reports repaired, refused, or unknown.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Cheap background model for drift classification and repair selection; realtime only for owner-directed escalation or a high-risk refusal.
- **latency:** Detection follows the configured watch interval. A repair attempt starts within 10 seconds of a qualifying change and reports a verified outcome within the normal Mac job deadline.
- **cost:** About $0.01–$0.05 per drift event; browser/Mac execution and verification dominate cost and latency.
- **security:** Repair policies are explicit allowlists with scope, maximum attempts, expiry, and reversibility requirements. Never auto-repair irreversible actions or transmit secrets to the relay/pendant. A changed page structure, ambiguous locator, or failed verification must fail closed.
- **missing:** A repair-policy envelope tied to a specific watch and invariant; A bounded compensation executor with a maximum-attempt and expiry guard; A verified repair outcome and escalation route to the pendant

### "“Show me exactly what this browser or Mac task would do, without changing anything; let me approve the real run only after I see the resulting diff.”"
- **useful because:** The owner can safely explore consequential work such as editing a form, moving files, or changing a calendar. An isolated browser session or temporary workspace performs a dry run, computes a redacted before/after diff, and returns a truthful preview before any live mutation.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-action
- **model tier:** Local Mac planner and browser harness for deterministic replay; a cheap model summarizes the structured diff; realtime is used only to answer the owner and collect final approval.
- **latency:** Preview in under 10 seconds for a normal form/file task, with explicit progress for longer workflows. No live mutation is permitted while previewing.
- **cost:** Roughly $0.02–$0.10 per preview depending on browser replay length; temporary workspace and browser execution dominate.
- **security:** The sandbox must not inherit write credentials, submit buttons, real mail delivery, or payment capability. Diffs are redacted and hash-linked to the exact plan. If isolation cannot be proven, return “preview unavailable” rather than running live.
- **missing:** A disposable Mac/browser sandbox with credential and network-write isolation; A structured diff format for files, app state, and browser fields; A commit gate binding the approved diff digest to the live execution attempt

### "“When I am back at my desk, hand this unfinished task to the Mac and continue from the exact safe checkpoint—do not repeat anything already done.”"
- **useful because:** A dropped link or sleeping Mac currently leaves the owner reconstructing where a multi-step task stopped. This would let the relay hold a resumable, redacted checkpoint, have the Mac reacquire the browser/app session, verify the last committed postcondition, and resume only the next uncommitted step.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-action
- **model tier:** Background/local planner for checkpoint selection and replay; realtime only for owner-facing handoff and exceptions.
- **latency:** Checkpoint acknowledgement under 2 seconds; resume within 15 seconds after the Mac returns, with an immediate “cannot prove checkpoint” response when verification is stale.
- **cost:** Usually under $0.03 per resume; storage and fresh verification are the main costs.
- **security:** Checkpoints contain opaque IDs, digests, and redacted summaries—not page secrets or file contents. Resume must be idempotent, verify the last step independently, expire after a bounded interval, and require the existing physical latch for irreversible next steps.
- **missing:** An atomic checkpoint record per step with committed/uncommitted state and digest; Idempotent resume semantics in Mac/browser executors; A relay-to-Mac wake/reconnect handoff and explicit stale-checkpoint refusal


## Changes it proposed to its own stack

### `integration` — Make every planned step carry an opaque operation_id and per-attempt attempt_id from POST /plan through POST /execute, job receipts, browser commands, and verify_operation_step. The verifier must return the same IDs plus evidence timestamp and provenance; the commit layer must refuse to mark a step complete when IDs, locator, or attempt do not match.
- **owner gets:** When a task changes the wrong tab, partially runs, or is retried after a link drop, the owner hears the truth about this attempt—not a receipt from a different run—and can safely decide what to do next.
- effort: Medium: shared envelope and persistence migration, adapters in Mac/browser executors, and verifier response validation; no new hardware.  ·  risk: Old jobs may lack IDs and become explicitly unknown rather than falsely complete. Roll out read-only correlation first, retain legacy receipt lookup, then enforce refusal for new jobs; provide a migration mapping for queued work.
- cost: Negligible storage and token overhead (roughly 100–250 bytes per step); no meaningful API cost.  ·  latency: Under 10 ms local correlation overhead; fresh verification remains the dominant delay.
- security: Improves provenance and prevents cross-operation receipt confusion. IDs must be opaque and non-secret; evidence remains hash-only by default.
- depends on: verify_operation_step; POST /plan; POST /execute; GET /jobs/:jobId/receipts; GET /journal/:jobId


## What it asked for

_Nothing._
## Its own summary

Round 190 produced three new owner-facing capabilities and one implementation change. (1) “Make it, then tell me tomorrow if it stayed changed”: delayed postcondition watches and drift alerts across relay, Mac/browser, and pendant. (2) “What exactly changed?”: an auditable spoken reconstruction joining plan, executor receipt, browser state, and independent verification. (3) Deadline/session-gated staged execution: prepare now, run only if the session, scope digest, and deadline still hold. I also recorded the concrete integration change that carries opaque operation_id/attempt_id from /plan through /execute and verify_operation_step, refusing mismatched receipts. I confirmed GET /watches is real and currently stores generic disabled page watches, not operation-linked watches.

**Biggest unknown:** I still need the owner’s policy data: which action classes may execute proactively, which always require the physical latch, acceptable expiry windows, and whether delayed drift should notify immediately or only during allowed hours. Technically, the pendant is still not relay-registered, Accessibility/Screen Recording remain owner-blocked, and no operation-specific watch schema or end-to-end correlation exists yet.

