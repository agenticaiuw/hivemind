# Harness derivation — faculty-action — round 110

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Do this and only tell me it's done once you have independently verified the result—for example, that the file contains the requested text, the reminder exists, or the browser change is visible after reload. If it failed or is only queued, tell me that instead."
- **useful because:** Today action receipts prove that an executor accepted and returned an action, not that the outside-world postcondition is true. This gives the owner an honest distinction between queued, executed, and verified—especially when a Mac sleeps, a browser session disappears, or an app silently rejects a write.
- **path:** faculty-judgement → faculty-action → mac-planner → mac-vision → browser-extension → relay-realtime → faculty-perception
- **model tier:** Use the realtime model only to turn the spoken request into a compact intent and to report the result. Use the cheaper background/local planner for execution; use faculty-perception or deterministic checks for postconditions, escalating to vision only when structured verification is unavailable.
- **latency:** 1–3 seconds for normal file/reminder/app checks; up to 15 seconds for browser reload and evidence capture. Speak 'queued' immediately if needed, then update only when verified or definitively failed.
- **cost:** Low: one local planner/action cycle plus a deterministic read-back. Vision/model cost only for GUI-only postconditions; relay storage is a few KB of evidence per step.
- **security:** Verification must not expose private page contents in the spoken reply or relay logs—store minimal hashes/snippets and redact secrets. Never infer success from an HTTP 200 or executor receipt. Irreversible external actions still require the existing owner confirmation gate; verification is not approval.
- **missing:** A typed postcondition schema attached to each intent (target, predicate, evidence source, freshness window).; A verifier that can read back files, Calendar/Reminders, app state, or the authenticated browser after mutation and persist evidence.; A state machine and relay event for queued -> running -> executed -> verified/failed, with timeout and retry policy.

### "Before you send or submit something important, show me the exact final payload on the pendant, let me approve that specific version with one button, then send it from the account that owns the session and bring back proof of what was submitted and where it went."
- **useful because:** Today the system can prepare work and can execute Mac/browser actions, but the final human approval, the exact bytes or fields approved, the authenticated identity used, and the resulting submission are not one indivisible handoff. This would make consequential actions safe to delegate without forcing the owner to sit at the Mac.
- **path:** faculty-judgement → faculty-perception → faculty-action → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Use the realtime tier only for the short spoken approval interaction and concise result. Use a cheaper planner for assembling the payload and deterministic local/browser code for identity, field, attachment, and submission evidence. Escalate to vision only when the page exposes no structured representation.
- **latency:** Payload preview within 3 seconds; one-button approval immediately; submission and proof within 10 seconds when the relevant session is online. If the session disappears, hold rather than silently retry.
- **cost:** Usually low: one planning call and local deterministic checks. A few KB for the redacted payload hash and submission receipt; model cost rises only for GUI-only fields.
- **security:** The approval must bind to a canonical payload hash, destination, authenticated account, and expiry—not to a vague spoken intent. Show secrets and private content only on the pendant/Mac owner surfaces, never in relay logs. Never auto-submit after a timeout; reject changed payloads, changed destination, changed account, stale pages, or missing attachment hashes.
- **missing:** A canonical payload renderer and hash that both pendant and executor can verify.; A pendant approval protocol binding one button press to one immutable payload, destination, account, and short expiry.; Authenticated-session identity and submission-proof capture for Mail, Messages, and browser forms.; A commit coordinator that refuses execution if any bound field changes between preview and submit, then reports accepted, rejected, or indeterminate.


## Changes it proposed to its own stack

### `integration` — Add a postcondition contract and independent verification stage to the existing plan/execute/job pipeline. faculty-judgement emits typed predicates (for example file_hash, reminder_present, app_value, browser_dom_text) with target surface and freshness deadline. faculty-action records intent and executor receipt, then dispatches a read-back through the appropriate Mac AppleScript/file API or authenticated browser tab. faculty-perception evaluates evidence against the predicate, writes a minimal evidence record, and emits queued/running/executed/verified/failed/expired events. Keep executor receipts and verification evidence separate so a successful dispatch can never be presented as proof of effect; expose both through /jobs/:jobId/receipts and relay_job_status.
- **owner gets:** The owner can trust 'done' again: a reminder that was actually created, a document that really contains the text, or a logged-in page that visibly changed—not merely a command that the Mac accepted. Failures become recoverable and understandable instead of silent false success.
- effort: Medium-high: typed predicate model, deterministic verifiers for common Mac/browser targets, event/state migration, timeout/retry tests, and dashboard/voice wording.  ·  risk: A stale or weak verifier could falsely certify; mitigate with freshness timestamps, source-specific checks, and an explicit 'executed but unverified' state. Browser reloads may trigger side effects, so verification should default to read-only and preserve tab affinity. Recovery is to retry verification without replaying the write.
- cost: Negligible API cost for deterministic checks; occasional local planner or vision call for GUI-only verification. A few KB of evidence per job, with redaction and retention limits.  ·  latency: Adds roughly 0.5–3 seconds for local read-back and potentially several seconds for browser reload; immediate spoken acknowledgement remains possible while verification runs.
- security: Improves safety by preventing receipt-only claims. Evidence must be minimized/redacted; private browser evidence stays on Mac or encrypted relay and is never sent to public Browser Run.
- depends on: An owner-approved postcondition vocabulary and confirmation policy; The still-missing durable browser job runner/result stream for long browser workflows; A verifier route/tool (the previously requested verify_operation_step/verify_action_proof capability is still unavailable)


## What it asked for

_Nothing._
