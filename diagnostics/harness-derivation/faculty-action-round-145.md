# Harness derivation — faculty-action — round 145

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Take care of this whole task on my Mac, but don’t stop at ‘done’: ask me on the pendant only when a risky step needs approval, execute the bounded plan, independently check each result, recover or undo safe failures, and give me one truthful spoken summary.”"
- **useful because:** This is the system’s highest-value promise: judgement can delegate an objective, action can carry it across Mac and authenticated browser sessions, and perception can distinguish completed, partially completed, and unknown instead of trusting executor claims. The owner gets outcomes rather than a fragile sequence of confirmations.
- **path:** unified → faculty-judgement → relay-realtime → faculty-action → mac-planner → browser-extension → faculty-perception → relay-realtime
- **model tier:** Use the realtime tier only for the owner’s short interactive approval conversation; use a cheaper background planner for decomposition, Mac/browser execution, and postcondition checks, escalating to realtime only on ambiguity or a dangerous branch.
- **latency:** Acknowledge in under 1 s; first safe step within 5 s; each approval prompt within 2 s of reaching the gate. Long tasks may run in the background and report on completion.
- **cost:** Roughly $0.01–$0.08 per ordinary task depending on planner turns and browser evidence; realtime approval dialogue dominates expensive tokens, while receipts and verification are cheap reads.
- **security:** Sensitive page contents and secrets stay on the Mac/browser. The pendant receives only a redacted action summary, risk, deadline, and opaque approval nonce. Require the existing physical approval latch for irreversible actions; independently verify with fresh state, record provenance, and report unknown rather than claiming success. Recovery must be limited to explicitly reversible steps.
- **missing:** A durable objective/step graph linking planner step IDs to executor receipts and verify_operation_step records; A policy-driven recovery planner that can select only whitelisted undo actions; A redaction contract for approval prompts and spoken summaries; A commit record that atomically binds approval nonce, execution receipt, verification evidence, and final status

### "“Give me a morning handoff of everything that happened while I was away: which Mac/browser actions ran, what was actually verified, what is still pending or unknown, and let me resolve the important leftovers from the pendant.”"
- **useful because:** Current receipts, journal entries, browser inspections, and pipeline events are scattered across surfaces. A concise, evidence-backed handoff lets the owner recover from interrupted work without rereading logs, while the pendant provides a physical way to approve, cancel, or defer outstanding items.
- **path:** relay-realtime → unified → faculty-perception → faculty-action → mac-planner → browser-extension → pendant
- **model tier:** Generate the digest with a cheaper background model from structured receipts and fresh perception reads; use realtime only to answer follow-up questions or conduct a short approval/cancellation exchange.
- **latency:** Precompute after each job and deliver a spoken digest in under 2 s when requested; fresh verification of a selected item under 5 s.
- **cost:** About $0.005–$0.03 per digest, dominated by summarization; structured evidence collection is local and inexpensive.
- **security:** Default to metadata and redacted titles, never spoken secrets or page bodies. Re-check stale items before presenting them as current. Mark executor-only claims as unverified, preserve provenance links, and require the existing physical latch for any action taken from the handoff.
- **missing:** A normalized event schema across jobs, browser commands, pipeline events, and routine runs; A durable per-owner handoff cursor so items are not repeated or silently skipped; A pendant-sized status/choice protocol for selecting one of up to 16 pending items; Freshness rules that invoke faculty-perception before an item is labeled complete

### "“Resume the work that was interrupted yesterday from the last verified step, not from the beginning—and ask me only if the next step is risky or the old evidence is stale.”"
- **useful because:** Mac sleep, browser restarts, link drops, and partial actions currently force the owner to guess what happened or repeat work. A checkpointed workflow can safely continue from the last independently verified postcondition, avoid duplicate purchases/messages/edits, and surface exactly one decision when state is ambiguous.
- **path:** relay-realtime → faculty-perception → faculty-judgement → faculty-action → mac-planner → browser-extension → mac-terminal → pendant
- **model tier:** Use a cheap background model to reconstruct and continue the step graph; invoke realtime only for a concise owner decision when a checkpoint is ambiguous or the next step is high risk.
- **latency:** Return a checkpoint summary within 2 s; resume safe work within 5 s; never auto-resume an irreversible step without a fresh physical approval.
- **cost:** Approximately $0.01–$0.06 per resumed workflow, dominated by reconstruction and one or two fresh verification reads; no model cost while idle.
- **security:** Persist hashes and locators rather than secrets or page contents. Verify every claimed checkpoint against fresh Mac/browser state, expire evidence after a policy-defined interval, and treat duplicate or unknown results as stop conditions. Bind resume to the original owner/session and require physical approval for irreversible continuation.
- **missing:** A durable step/checkpoint graph that survives relay and Mac restarts; Idempotency keys and duplicate-effect detection for browser and Mac actions; Freshness/expiry metadata on verification evidence; A resume coordinator that can distinguish safe replay, safe skip, and mandatory human review

### "“Fill out and submit this form using my saved information, but let the AI see only the field names and whether each field passed validation—not my passwords, payment numbers, or private answers—and let me approve the final redacted summary on the pendant.”"
- **useful because:** Today the browser can hold authenticated sessions, but a general model still needs a safe contract for using sensitive values without exposing them in prompts, receipts, speech, or verification evidence. This would let the owner automate high-value forms and purchases while keeping secrets inside the Mac/browser boundary.
- **path:** browser-extension → mac-planner → faculty-action → faculty-perception → relay-realtime → pendant
- **model tier:** A cheaper background planner maps intent to field labels and validation rules. A local Mac/browser executor performs secret insertion. Realtime is used only for the short final approval conversation.
- **latency:** Field mapping in under 5 s; local filling under 2 s; approval prompt under 1 s after validation. Submission waits indefinitely for explicit approval when risk requires it.
- **cost:** About $0.01–$0.05 per form, dominated by intent-to-field mapping; secret handling and validation are local.
- **security:** Secrets never leave the browser/Mac boundary and never enter model context, relay logs, pendant audio, screenshots, or receipts. Verification returns field labels, validation status, and a cryptographic digest rather than values. Bind approval to the exact form origin, field schema, redacted summary, and expiry; refuse if the page changes.
- **missing:** A browser-side secret-slot API that accepts opaque field handles rather than values; A redacted form schema and validation receipt format; A Mac-local secret-provider integration with explicit origin and field allowlists; A final approval digest that can be spoken without leaking sensitive content

### "“When I ask why you took an action, show me the exact evidence and reasoning chain that led to it, what I approved, and what remains uncertain—without replaying private page contents.”"
- **useful because:** An owner cannot meaningfully audit an autonomous assistant from a success message alone. A provenance replay makes mistakes diagnosable: it connects the spoken request, plan, approval, executor receipt, fresh perception evidence, and final claim while redacting secrets and irrelevant content.
- **path:** relay-realtime → unified → faculty-judgement → faculty-action → faculty-perception → mac-planner → browser-extension → pendant
- **model tier:** Use a cheap background summarizer over structured receipts and hashes; use realtime only to answer the owner’s follow-up questions conversationally.
- **latency:** Initial explanation in under 3 s from stored evidence; a selected evidence item should load in under 2 s.
- **cost:** Approximately $0.005–$0.03 per replay; storage and local redaction dominate rather than inference.
- **security:** Default to hashes, selectors, timestamps, action summaries, and minimal snippets. Never expose passwords, tokens, full private pages, or unrelated browser content. Evidence must be immutable, content-addressed, and labeled executor-claimed versus independently verified; stale or missing evidence must be disclosed.
- **missing:** An immutable provenance bundle spanning relay, planner, executor, browser, pendant approval, and perception; A redaction/presentation policy for spoken and visual evidence; A user-facing provenance query language keyed by action or time; Retention and deletion controls for evidence bundles

### "“Put me in a temporary meeting mode with one tap: silence or defer Mac notifications, pause nonurgent autonomous work, keep only my chosen emergency channels, and restore everything exactly when I tap again.”"
- **useful because:** The pendant is the one surface the owner can reach without finding a window or phone. A reversible, time-bounded mode would coordinate the wearable, relay, Mac apps, and browser so interruptions stop consistently rather than being silenced in one place while jobs or alerts continue elsewhere.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → faculty-action → faculty-perception
- **model tier:** No expensive realtime reasoning is needed for entry/exit. Use a background policy executor to apply and restore the owner’s declared mode; use realtime only if a conflict needs explanation.
- **latency:** Enter or exit in under 2 s; emergency-channel changes propagate within 5 s. Automatically expire at the declared end time.
- **cost:** Negligible inference cost after configuration; occasional background reconciliation is under $0.01 per mode session.
- **security:** Default to defer rather than discard. Preserve notification provenance and original scheduled times. Never suppress safety-critical alerts without an explicit allowlist. Restoration must be idempotent and verified against the pre-mode snapshot; if an app changed independently, report the conflict instead of overwriting it.
- **missing:** A device-side mode toggle that works offline and queues the mode transition; A Mac notification and application-state snapshot/restore adapter; A relay policy that pauses only nonurgent jobs and prevents new autonomous work from bypassing the mode; Fresh postcondition checks for notification state, job state, and restoration


## What it asked for

_Nothing._
