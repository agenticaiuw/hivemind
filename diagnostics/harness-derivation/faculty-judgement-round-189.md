# Harness derivation — faculty-judgement — round 189

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Did that actually happen?" — give me one answer that distinguishes planned, accepted, executed, and actually delivered to the pendant, and show me what evidence supports it."
- **useful because:** Today a Mac receipt, relay acceptance, browser result, and pendant playback can each look like success while the owner hears nothing or an external action never committed. A single closed-loop answer prevents false reassurance and makes retries safe.
- **path:** relay → mac → browser → pendant
- **model tier:** background for receipt correlation; realtime only for the final spoken sentence
- **latency:** under 2 seconds from an existing job or artifact; up to 10 seconds if a live browser result must be fetched
- **cost:** Low: mostly deterministic joins and status reads; one short realtime turn only when the owner asks verbally.
- **security:** Never infer execution from queue acceptance. External side effects remain governed by autonomy_policy_evaluate and physical approval; expose only redacted provenance and require confirmation before retrying a non-idempotent step.
- **missing:** a durable relay-job-id to Mac/browser job foreign key instead of telemetry-only localJobId; a query that joins execution receipts to browser command results and record_pendant_delivery_event events; a durable terminal state machine for planned/accepted/executed/delivered/failed

### ""These two sources disagree — keep the conflict from steering anything, tell me exactly what differs, and ask me one small question to settle it.""
- **useful because:** A low-confidence calendar, timezone, permission, or browser fact should not silently drive reminders, spoken briefings, or external actions. This turns uncertainty into a visible, reversible decision instead of a confident mistake.
- **path:** relay → mac → browser → pendant
- **model tier:** background deterministic comparison first; realtime only to phrase the single owner question
- **latency:** under 3 seconds for known sources; no mutation until the owner resolves it
- **cost:** Low to moderate: structured comparisons are cheap; model cost is limited to wording the conflict and extracting the owner's answer.
- **security:** Keep both source values and provenance; do not expose sensitive snippets on the spoken surface. Quarantine means read-only and non-actionable, not deletion. An owner answer that changes a permission or external action still needs the normal approval gate.
- **missing:** a durable conflict/quarantine record linked to source IDs and affected actions; a write path from resolved owner answers into fleet memory and local facts with retraction of the losing claim; policy integration so autonomy_policy_evaluate rejects quarantined evidence

### ""When a website needs me, hand the browser to me without showing the page or asking me to copy a password; tell me when it is safe to continue.""
- **useful because:** The hive can reach an authenticated browser but cannot honestly cross a CAPTCHA, passkey, biometric, or 2FA boundary for the owner. Today it either stalls opaquely or tempts the agent to handle secrets. A deliberate local handoff preserves the session and resumes only after the owner completes the challenge.
- **path:** browser → mac → relay → pendant
- **model tier:** background deterministic browser-state detector; realtime only for the short pendant prompt and owner response
- **latency:** detect within one browser poll (under 30 seconds); resume within 2 seconds after the extension reports the owner-completed checkpoint
- **cost:** Low: polling and signed state transitions dominate; model is optional and used only to summarize the checkpoint without page content.
- **security:** Never send passwords, OTPs, page screenshots, or DOM snippets to the relay or pendant. The extension emits only origin, opaque checkpoint ID, and typed state (needs_owner/owner_finished/expired). Require physical_transaction_approval_latch for any subsequent external submit; expire and revoke the handoff if origin or tab identity changes.
- **missing:** a browser-extension checkpoint protocol that detects owner-required challenges without reading secret fields; a local handoff UI/indicator and an owner-finished signal that does not expose credentials; relay persistence for checkpoint leases, origin binding, expiry, and resume correlation

### ""You were wrong about that." Learn the correction, show me exactly which future decisions it will change, and let me undo the lesson later."
- **useful because:** The system currently stores many facts and policies but has no durable, owner-visible calibration loop. Repeated mistakes about urgency, source reliability, or action interpretation therefore recur, while a single correction could silently become an overgeneralized belief. The owner should be able to improve judgement without granting an opaque permanent preference.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** background model for clustering repeated corrections and proposing a narrowly scoped rule; realtime only to acknowledge the correction and ask for confirmation when scope is ambiguous
- **latency:** Immediate acknowledgement under 1 second; proposed rule within 5 seconds; no future behavior changes until explicitly accepted
- **cost:** Low to moderate: deterministic correction receipts and rule evaluation dominate; occasional background clustering uses a cheaper model. Dashboard review is local and incurs no model call.
- **security:** A correction must never rewrite source evidence or silently change permissions. Store the original decision, owner correction, scope, confidence, expiry, and affected surfaces. Sensitive correction text stays local by default; external actions still require the existing autonomy and physical-consent gates. Every learned rule needs one-click revocation and an explanation of matches.
- **missing:** a first-class correction record linking an owner utterance or button event to the mistaken judgement and its evidence; a scoped rule store with expiry, confidence, conflict handling, and explicit acceptance; a dry-run endpoint showing which past and future decisions would differ before activation; a local pendant interaction for rejecting or deferring a proposed lesson without speaking sensitive content

### ""Make sure the result is what I meant, not merely that the command ran; if the intended outcome is not true, undo what you safely can and tell me what remains.""
- **useful because:** Execution success is only a process fact. A script can exit zero while deleting the wrong files, a browser action can land on the wrong account, and a reminder can be created with the wrong time zone. The owner needs outcome verification and bounded recovery, not another success receipt.
- **path:** mac → browser → relay → pendant
- **model tier:** cheap deterministic invariant checks first; background model only to translate an ambiguous natural-language goal into reviewable invariants; realtime for the final exception report
- **latency:** Verify within 5 seconds after reversible actions; up to 30 seconds for browser or filesystem scans. Never block a clearly read-only action on the expensive model.
- **cost:** Low for typed postconditions and snapshots; moderate only when natural language requires invariant extraction. Rollback itself uses existing local execution and costs no model call.
- **security:** Verification must not read secrets merely to prove success. External side effects and destructive operations remain confirmation-gated. Rollback must be limited to an action’s declared reversible scope, use idempotency keys, and stop rather than guess when observed state is ambiguous. Preserve before/after evidence with sensitive fields redacted.
- **missing:** typed postconditions and pre-action snapshots attached to every plan step; a verifier that can inspect Mac files/state and browser state without broadening permissions; a transaction coordinator that invokes existing undo routes only when the declared invariant fails; owner-facing distinction between verified, unverifiable, contradicted, and partially recovered


## What it asked for

_Nothing._
