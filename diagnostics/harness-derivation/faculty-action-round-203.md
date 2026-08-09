# Harness derivation — faculty-action — round 203

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Send this email and keep watch for the reply; tell me on the pendant when they answer, and draft a follow-up but never send it without asking."
- **useful because:** Today sending, monitoring, notifying, and drafting are disconnected. This makes the wearable useful for asynchronous commitments rather than only one-shot commands, while preserving a hard send boundary.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-action
- **model tier:** background for inbox polling and thread summarization; realtime only for the initial command and interruption
- **latency:** Initial staging under 3 seconds; inbox checks every 2–5 minutes; pendant alert within 10 seconds of a detected reply.
- **cost:** Low: one short realtime turn, then roughly 1–2 cheap background checks per polling interval; browser/Mac reads dominate latency, not tokens.
- **security:** Must bind to an explicit recipient/thread, show the exact outbound message before physical approval, never expose unrelated inbox content to the pendant, and treat a changed thread or expired browser session as unknown rather than sending. Follow-up remains a draft until a new approval.
- **missing:** durable watch record keyed by message/thread with expiry and stop conditions; inbox/thread change detector across Mail and browser sessions; pendant event for reply-arrived with redacted subject/sender; policy field distinguishing draft creation from outbound send

### "When I say 'do it when I get home' or 'if the price drops, buy it', stage the action now, wait for the specified condition, then ask me on the pendant for one physical approval before committing."
- **useful because:** The system can currently stage or schedule work, but cannot safely combine a future condition, live browser/Mac observation, an expiry, and a deliberate wearable approval. This turns natural-language intent into a bounded, reversible waiting action instead of a dangerous blind automation.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-judgement → faculty-perception → faculty-action
- **model tier:** background/scheduled model evaluates conditions and polls; realtime only handles owner clarification and approval
- **latency:** Condition evaluation within 1 minute of a relevant event; approval prompt on pendant within 5 seconds; never commit after lease/condition expiry.
- **cost:** Low-to-moderate: cheap scheduled polling plus one realtime approval interaction; browser/API polling dominates.
- **security:** Condition must be typed and inspectable (time, location supplied by Mac, price, page state), with explicit expiry and max attempts. Never infer location from the pendant's zoneless clock. Purchases, messages, and destructive actions always require physical approval; condition data sent to relay should be minimized.
- **missing:** durable conditional-operation record and evaluator; event sources for price/page changes and Mac location/context; pending approval delivery with condition snapshot and expiry; exactly-once commit/reconciliation across a condition firing and bridge disconnect

### "Handle a website's verification challenge for me without showing the site or any credential to the relay: tell me what the page is asking, let me approve on the pendant, and finish only if the browser proves the same challenge was completed."
- **useful because:** Many real tasks stop at a CAPTCHA, passkey prompt, payment confirmation, or one-time challenge. The browser has the authenticated session and the Mac has the local UI, while the pendant can provide deliberate consent without becoming a secret-bearing terminal.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-action
- **model tier:** realtime for challenge explanation and approval; local Mac/browser execution handles the actual credential or native prompt
- **latency:** Challenge description within 2 seconds; approval-to-continue under 1 second; timeout after 2 minutes with no blind retry.
- **cost:** Low: one short realtime interaction; browser observation and native prompt handling dominate.
- **security:** Relay receives only an opaque challenge ID, origin, action summary, and redacted screenshot/text—not passwords, passkeys, OTPs, payment data, or page secrets. Approval must bind to origin, challenge hash, and expiry. Postcondition verification must independently confirm completion; an unverified native prompt is UNKNOWN.
- **missing:** browser challenge detector with origin and challenge hash; local-only handoff for passkey/OTP/native credential UI; pendant approval envelope bound to challenge digest; browser verifier for challenge completion and cancellation

### "At the end of the day, give me one private pendant digest of only the commitments that changed—new meetings, unanswered requests, deadlines, and actions you completed—with a way to ask for the evidence behind any one item."
- **useful because:** The owner should not have to reconstruct their day from browser tabs, Mail, Calendar, job receipts, and voice history. A compact, interruptible digest turns distributed activity into actionable awareness without streaming all private content to the relay.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-action
- **model tier:** background model builds the digest and clusters changes; realtime answers an evidence drill-down only when requested
- **latency:** Digest ready within 30 seconds of the configured quiet-time boundary; individual evidence answer within 3 seconds.
- **cost:** Low: incremental local extraction plus a small summarization call; source scanning dominates.
- **security:** Compute the digest on the Mac where possible; send only compact redacted cards to the relay. Each card needs source, timestamp, confidence, and sensitivity. Never infer a commitment from an unverified draft or browser text alone. Drill-down requires an explicit pendant gesture for private/secret items.
- **missing:** cross-source change journal for Mail, Calendar, browser, and action receipts; deduplication and commitment classification with provenance; quiet-time delivery policy and pendant digest protocol; evidence drill-down that returns a bounded, redacted source excerpt


## Changes it proposed to its own stack

### `integration` — Add a freshness-gated commit barrier to faculty-action: immediately before each irreversible Mac or browser step, read the relevant bridge/session state and require a still-valid operation lease. If the browser session, focused app, or verification evidence is older than the lease, stop with UNKNOWN and emit a compact pendant outcome instead of retrying blindly. Store the freshness snapshot alongside the action receipt and pass it to verify_operation_step.
- **owner gets:** A command will no longer quietly act on a stale tab, logged-out session, or changed focused app after the owner walks away. The owner gets a truthful 'not done—needs attention' signal rather than a plausible but wrong success.
- effort: Medium: action ledger schema, pre-commit checks in policyRouter/prepareApprove, and relay-to-pendant unknown outcome mapping.  ·  risk: A legitimate slow workflow may expire and require re-approval; recover by presenting the exact stale condition and allowing a fresh staged attempt. Never auto-extend a lease for irreversible steps.
- cost: Negligible token cost; one or two local status reads per commit.  ·  latency: Adds about 100–500 ms for local state reads; avoids expensive failed/repeated workflows.
- security: Improves safety by preventing stale-context commits; freshness metadata must redact URLs, message bodies, and secrets, retaining only hashes/session IDs.
- depends on: t21-8d1c verify_operation_step must be callable with concrete postcondition kinds; s10-j9l4 physical_transaction_approval_latch; GET /observe; GET /browser/status; GET /jobs/:jobId/receipts

### `context` — Create a cross-surface evidence capsule format for faculty-action and faculty-perception: every owner-visible claim about an action or commitment carries an opaque capsule ID, source surface, captured-at time, freshness deadline, content hash, sensitivity, and a typed locator. The Mac keeps the private payload; relay and pendant receive only the capsule metadata until the owner requests a drill-down.
- **owner gets:** The owner can ask 'why do you think that happened?' or 'what changed?' and get a traceable answer without having their messages, calendar, or browser contents copied into the relay by default.
- effort: Medium: shared capsule schema, local retention/indexing, redacted relay projection, and capsule-aware action receipts and briefings.  ·  risk: Stale or deleted source data may make a capsule unverifiable; report UNKNOWN with the original timestamp rather than fabricating evidence. Retention must be bounded and support revocation.
- cost: Small storage/index cost; lower recurring token cost because full context is fetched only for requested drill-downs.  ·  latency: No cost on normal haptic outcomes; drill-down adds a local lookup and optional model summarization.
- security: Reduces data exposure by separating proof metadata from private payloads. Hashes and locators must avoid leaking sensitive filenames, URLs, or message subjects.
- depends on: t21-8d1c verify_operation_step; GET /journal/:jobId; GET /jobs/:jobId/receipts; GET /briefing/latest; GET /observe; GET /browser/status


## What it asked for

_Nothing._
