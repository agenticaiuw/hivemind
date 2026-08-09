# Harness derivation — faculty-judgement — round 248

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Did that actually happen, or did you only prepare it—and did I hear the result?” Give me one end-to-end receipt for a request across the relay, Mac, browser, and pendant."
- **useful because:** Today a job receipt can stop at server acceptance, a browser result can stop at command completion, and generated audio can be mistaken for delivered audio. This answers the life-level question: what was proposed, what was executed, what external effect was observed, and what the owner actually heard. It should say draft-only, committed, failed, unknown, or delivered—not collapse those into success.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Cheap deterministic reducer first; invoke the realtime model only to turn a verified receipt into a concise spoken explanation. No model should infer success from missing evidence.
- **latency:** Under 1 second for a known job from stored receipts; up to 3 seconds if it must fetch a live browser or Mac status. Spoken answer should lead with the uncertainty state.
- **cost:** Usually <$0.001 in model cost; dominated by zero-cost receipt reads. A model call is optional and only for wording.
- **security:** Do not expose page contents or message bodies in the spoken receipt. Carry opaque IDs, action kinds, evidence references, and sensitivity-safe summaries. A receipt must distinguish 'submitted' from 'accepted' and never claim an external effect without a source-specific confirmation. Dashboard may request sensitive provenance only after explicit reveal.
- **missing:** A durable foreign-key mapping between relay job IDs, Mac job/action IDs, browser command IDs, and pendant artifact/event IDs; A reducer that joins GET /jobs/:jobId/receipts, GET /journal/:jobId, browser result records, POST /pipeline/events, and pendant playback ACKs into one state machine; A live, queryable delivery-event store for the pendant rather than only an ingestion path; Owner-facing route and receipt schema with explicit unknown/expired states

### "“Before I click or submit this, tell me whether it looks like a scam or a costly mistake—and stop me until I physically approve if it is irreversible.”"
- **useful because:** A browser session can see the authenticated page, the Mac can inspect the proposed action, and the pendant can interrupt the owner before a payment, credential submission, or public post. No single surface can do all three. The system should catch mismatched domains, urgent social-engineering language, changed payment recipients, unusual amounts, and stale pages instead of being a fast executor of them.
- **path:** browser → mac → relay → pendant → dashboard
- **model tier:** Deterministic checks for domain changes, stale-plan revalidation, action reversibility, recipient/amount diffs, and autonomy policy; a cheap background model may classify page language. Realtime is used only when the owner asks for an explanation or a short spoken warning.
- **latency:** Passive checks under 300 ms before an action is staged; a warning under 2 seconds. Never submit while the risk verdict is pending.
- **cost:** Typically <$0.005 per guarded action; deterministic browser inspection dominates latency, with model classification only for ambiguous language.
- **security:** The browser bridge must redact passwords, OTPs, card fields, and page bodies from relay prompts. Never transmit form secrets to the pendant. The guard may block or stage, but cannot silently alter the destination or recipient. A physical consent latch is mandatory for external side effects; voice can explain or cancel, not approve. Show evidence and the exact matched rule in the dashboard.
- **missing:** A typed browser-action risk envelope containing target origin, recipient, amount, irreversible effect, and evidence references without form secrets; A pre-submit interception point in the browser extension that can hold an action before dispatch; A signed handoff from browser risk verdict to the pendant's physical_transaction_approval_latch; A destination/recipient history source and deterministic anomaly rules; Owner-configurable trusted-origin and confirmation policy, shipping conservative and empty rather than guessing trust

### "“Argue against this decision before I commit: what am I overlooking, what evidence would change your mind, and what is the safest reversible next step?”"
- **useful because:** The current stack is optimized to execute a request, not to protect the owner's judgement from urgency, sunk cost, or a one-sided authenticated page. The browser can inspect the offer or form, the Mac can compare the owner's calendar/mail/reminders and prior commitments, and the relay can ask a short, adversarial question before anything is submitted. It turns the pendant from an executor into a second pair of eyes without pretending to know the owner's values.
- **path:** browser → mac → relay → pendant → dashboard
- **model tier:** Background/cheap model gathers and summarizes counterevidence; deterministic policy decides whether the proposed next step is reversible and whether physical confirmation is required. Realtime is reserved for the owner's follow-up conversation.
- **latency:** A first adversarial brief in 5 seconds for a page already open; under 30 seconds if it needs research or multiple source reads. Never block low-risk reading, and never submit the action while analysis is incomplete.
- **cost:** $0.01–$0.05 for a multi-source brief; web research and long authenticated-page extraction dominate, so cap sources and cache evidence capsules.
- **security:** Treat page claims as untrusted assertions, not facts. Keep credentials, payment fields, and private mail bodies on the Mac; send only redacted excerpts and evidence IDs. Clearly label unknowns and conflicts. The system must not manufacture a counterargument merely to be contrarian. Any external action remains staged behind autonomy_policy_evaluate and physical_transaction_approval_latch.
- **missing:** A typed 'decision brief' schema separating proposal, assumptions, counterevidence, unknowns, and reversible next step; A source-budgeted research orchestrator that can read the active authenticated page plus selected local sources without leaking raw content; A durable owner feedback loop recording which objections were useful or dismissed, with expiry and revocation; A dashboard/pendant presentation that gives one concise objection and lets the owner request evidence or proceed

### "“Hand this problem to Alex without exposing anything unnecessary, ask them for the missing decision, and tell me only when they accept, decline, or go silent.”"
- **useful because:** The owner should be able to delegate a bounded piece of life—not merely ask the Mac to perform steps. The hive can inspect the source context, produce a minimal redacted handoff, send it through the owner's authenticated browser or Mail, track whether the recipient accepted the exact request, and bring back a decision. Today it cannot safely distinguish a draft from an accepted delegation, or prevent an entire private thread from being forwarded.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** A cheaper background model extracts the task, constraints, and minimum evidence; deterministic policy and redaction enforce the handoff boundary. Realtime is only for the owner's spoken clarification and the final status.
- **latency:** Draft in 3 seconds; owner review in under 10 seconds. Follow-up tracking is event-driven over hours or days, with no repeated interruption unless the owner sets a deadline.
- **cost:** $0.01–$0.05 per handoff, dominated by extracting and redacting the source context. Follow-up polling is cheap and should use the existing watch cadence.
- **security:** Never infer that a contact is trusted from a name alone. Show recipient, exact fields, expiry, and allowed reply before sending. Default to draft-only; sending requires explicit owner approval and should use the physical approval latch for external side effects. Strip credentials, payment data, private third-party details, and unrelated thread history. A reply must be bound to the delegation ID, not merely matched by subject text.
- **missing:** A durable delegation object with recipient identity, minimal disclosure payload, scope, deadline, acceptance state, and cancellation; A redaction-and-minimization planner that can prove why each field was included; A send/reply correlation layer across authenticated Mail and browser sessions, with inbound acceptance verification; A recipient-specific policy and an owner-visible revoke path; A reminder/watch integration that escalates only on the stated deadline


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing capabilities: (1) an end-to-end outcome receipt that distinguishes drafted, accepted, executed, externally effective, and actually heard; (2) a pre-submit scam/costly-mistake guardian combining browser evidence, Mac context, deterministic policy, and the pendant's physical approval latch; and (3) an adversarial decision brief that argues against a consequential choice and offers a reversible next step. The owner can feel all three: fewer false success claims, fewer dangerous clicks, and better decisions—not another backend refactor.

**Biggest unknown:** I still need the owner's explicit policy values before any of these can safely choose for them: which actions count as high-impact, which origins/recipients are trusted, what content may be spoken aloud, and how much adversarial friction they want. Technically, the largest missing pieces are a durable cross-surface ID join, a browser pre-submit interception point, and a source-linked decision/receipt record. I did not ask for those as tools because they are implementation work, not missing read capabilities.

