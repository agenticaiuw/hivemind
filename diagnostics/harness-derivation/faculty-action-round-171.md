# Harness derivation — faculty-action — round 171

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If I tell you ‘handle this meeting,’ turn my pendant voice note into a calendar follow-up package: identify the meeting on my Mac, draft the follow-up email in the browser or Mail, attach the note and action items, and leave it staged until I physically approve it.”"
- **useful because:** This is the highest-value everyday handoff: the worn device captures intent while the Mac and browser supply calendar/session context. It eliminates reconstructing a meeting from memory without allowing an accidental send.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → faculty-perception → faculty-action
- **model tier:** Realtime only for the short voice capture and clarification; a cheaper background model extracts action items and drafts. faculty-judgement selects the matching meeting; faculty-perception verifies calendar identity, draft recipients, attachments, and final state; faculty-action executes only after the existing physical transaction approval latch.
- **latency:** Acknowledge capture in under 2 seconds; draft within 30 seconds. Matching and verification may take up to 2 minutes, with a spoken progress update.
- **cost:** Roughly $0.01–$0.05 per meeting, dominated by transcription and extraction; Mac/browser actions are local.
- **security:** Meeting notes and recipient identities leave the pendant for relay processing unless kept local. Never send automatically. Read-only calendar lookup and a redacted spoken summary precede approval; approval envelope contains only a digest and action summary, not message contents or secrets.
- **missing:** A durable cross-surface meeting correlation record linking pendant capture, calendar event, draft, and attachment hashes; An explicit attachment handoff from pendant outbox to Mail/browser draft; A policy decision for whether drafts may be created proactively

### "“Keep trying this action until it is actually true—or tell me exactly what is blocking it.”"
- **useful because:** Today an executor can report completion while the real browser or Mac state is unchanged. A bounded recovery loop would make the system dependable: execute, independently verify, classify unknown versus contradicted, retry safely, then route to another surface or ask the owner with a concrete explanation.
- **path:** relay-realtime → mac-planner → browser-extension → faculty-action → faculty-perception → pendant
- **model tier:** Cheap background orchestration handles retries and idempotency; realtime is used only when the owner must answer a clarification or approve a risky retry.
- **latency:** First attempt immediately; up to three bounded retries or 90 seconds total. The pendant gets a short status cue after each state transition.
- **cost:** Usually under $0.01 per action; costs rise only when a retry requires model replanning or browser inspection.
- **security:** Retries must be idempotency-keyed and limited by risk class. Never retry sends, purchases, deletions, or authentication changes without a fresh physical approval. Verification uses hash-only evidence by default and redacts private page contents.
- **missing:** A recovery-controller route that consumes executor receipts and verifier outcomes; Idempotency and retry budgets attached to each operation step; A durable alternate-surface policy (Mac app versus browser)

### "“Make sure I don’t silently miss a commitment.” When I mention a promise or deadline on the pendant, continuously reconcile it against my Mac calendar, email, and browser activity; if it is at risk, tell me on the pendant, prepare the smallest repair (a reschedule request, progress update, or draft reply), and let me approve that repair physically."
- **useful because:** The owner gets protection against forgotten promises rather than another passive reminder. The pendant hears the commitment, the always-awake relay watches for drift, and the Mac/browser can assemble a repair using the real account context. No single node can provide this end to end.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-judgement → faculty-perception → faculty-action
- **model tier:** Use a cheap background model for commitment extraction, deadline-risk scoring, and periodic reconciliation; reserve realtime for the brief warning and any owner clarification.
- **latency:** Capture acknowledgement under 2 seconds. Reconciliation can run hourly and on relevant email/calendar/browser events; urgent risk warnings should reach the pendant within 30 seconds.
- **cost:** Approximately $0.01–$0.08 per commitment per day, dominated by email/calendar summarization; local Mac and browser reads add no model cost.
- **security:** Commitments may contain sensitive work or relationship information. Keep raw messages on the Mac where possible, send only extracted facts and hashes to the relay, and never contact anyone or alter a calendar entry without physical approval. Expired or ambiguous deadlines must produce uncertainty, not an invented date.
- **missing:** A commitment ledger with source citations, confidence, due-time semantics, and lifecycle states; Cross-surface event subscriptions for relevant calendar, Mail, and browser changes; A risk model that distinguishes owner timezone from travel/location timezone; A repair planner that produces reversible drafts and a concise physical-approval summary

### "“Find a time with them next week.” The system should negotiate a meeting through the relevant browser or Mail session: infer the right person and context, offer only slots that fit my calendar and quiet hours, track the thread until a reply arrives, and prepare the calendar event. I approve each outbound message from the pendant."
- **useful because:** This removes the tedious back-and-forth while preserving the owner’s control over communication. The browser’s authenticated session, the Mac calendar, the relay’s persistence, and the pendant’s physical approval are all required.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-judgement → faculty-perception → faculty-action
- **model tier:** Cheap background model handles thread extraction, slot computation, and polling. Realtime is used only for the initial request, exceptions, and approval prompts.
- **latency:** Produce candidate slots in 10 seconds; draft each reply within 20 seconds of a received response; poll for up to two weeks without keeping a realtime model active.
- **cost:** About $0.02–$0.10 per negotiation, dominated by thread parsing and occasional replanning; browser and calendar operations are local.
- **security:** Outbound messages and calendar details are consequential. Show recipient, proposed times, and a short draft digest on the pendant; require a fresh physical approval for every send. Do not expose mailbox contents or session tokens to the pendant or relay.
- **missing:** A negotiation state machine with reply correlation, expiry, and loop limits; Availability computation that understands the authoritative Mac timezone and explicit unknown travel timezone; A browser/Mail send gate integrated with physical approval and independent post-send verification; A cancellation path that stops polling and invalidates outstanding drafts


## Changes it proposed to its own stack

### `integration` — Add a cross-surface ‘handoff capsule’ protocol. Every pendant capture, relay plan, Mac/browser action, approval decision, and independent verification is bound into a compact chain containing operationId, actionId, attemptId, stepKey, idempotencyKey, source eventId, precondition hash, postcondition hash, freshness window, and evidence receipt. The relay exposes a human-readable timeline and a machine-verifiable terminal state, while the pendant receives only status, digest, and the next safe gesture—not private content.
- **owner gets:** The owner can ask “did you really do it?” and get a truthful answer tied to what changed, even after a link drop or Mac restart. It also lets the system resume a half-finished task instead of repeating or silently losing it.
- effort: Medium-high: schema shared by relay, Mac agent, browser bridge, perception, and pendant firmware; migration adapters for existing jobs and receipts.  ·  risk: Schema bugs could mark an action complete incorrectly. Fail closed on missing or stale evidence, preserve unknown as unknown, and keep old receipts readable during migration.
- cost: Negligible storage and bandwidth (hundreds of bytes per step); small relay/database implementation cost; no model cost unless a human summary is requested.  ·  latency: Adds one verification round trip, typically 0.5–3 seconds; no impact on simple read-only actions if verification is local.
- security: Improves auditability and prevents replay through monotonic attempt/idempotency fields. Evidence must default to hashes and avoid carrying secrets or page text to the pendant.
- depends on: verify_operation_step; faculty-perception’s verification envelope fields; GET /jobs/:jobId/receipts; POST /pipeline/events; physical_transaction_approval_latch (s10-j9l4)

### `new-surface` — Create a ‘local-only disclosure broker’ between faculty-judgement and Mac/browser execution. The planner sends the Mac a typed operation with selectors, predicates, and a redacted summary; the Mac resolves private values inside the authenticated app, performs only the approved operation, and returns hashes plus minimal proof. The pendant can approve a digest without ever receiving message bodies, credentials, page text, or attachments.
- **owner gets:** The owner can use powerful browser and Mac automation without turning the relay or pendant into a copy of every private account. It makes sensitive actions practical while preserving a clear boundary around secrets.
- effort: High: typed operation vocabulary, Mac-side value resolution, browser bridge enforcement, audit logging, and adapters for existing action routes.  ·  risk: A selector or predicate bug could target the wrong record. Require preview verification, exact-match constraints for destructive actions, fail closed on ambiguity, and retain the existing approval latch as a separate consent boundary.
- cost: Small per-action payloads and hash storage; moderate engineering cost; no recurring model cost beyond planning.  ·  latency: Adds local resolution and one verification exchange, typically 1–5 seconds.
- security: Substantially reduces sensitive data leaving the Mac. Requires strict anti-exfiltration checks, capability-scoped selectors, replay protection, and no raw secrets in logs or receipts.
- depends on: POST /plan; POST /execute; POST /browser/inspect; POST /browser/result/:commandId; verify_operation_step; physical_transaction_approval_latch (s10-j9l4)


## What it asked for

_Nothing._
