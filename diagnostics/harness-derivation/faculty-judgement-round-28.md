# Harness derivation — faculty-judgement — round 28

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Keep me from missing the things I implicitly promised: find deadlines and commitments across my logged-in mail, calendar, work pages, and local notes, tell me what matters next, and quietly prepare the reversible parts before the deadline.”"
- **useful because:** Today reminders only cover what the owner explicitly schedules. This would catch obligations buried in threads or forms, explain why each is believed due, account for calendar availability, and turn an approaching deadline into a ready-to-review action rather than a last-minute surprise. The pendant is the only surface that can give a brief cue while the owner is away from the Mac; the Mac/browser are the only surfaces that can gather private evidence and prepare work.
- **path:** relay-realtime → browser-extension → mac-planner → mac-vision → mac-terminal → relay-realtime
- **model tier:** Background model performs scheduled extraction, deduplication, and prioritization; realtime is used only when the owner asks a follow-up or must resolve an ambiguity. No expensive voice turn for routine polling.
- **latency:** Nightly or every 2–4 hours, with a sub-minute relay alert only for a high-confidence deadline inside the owner's configured horizon. Preparation can take minutes while the owner is away; spoken alert should be one short sentence.
- **cost:** Roughly $0.02–$0.15 per daily scan depending on number of private pages and local notes; browser extraction and context tokens dominate, not the short alert.
- **security:** Reads sensitive mail, calendar, authenticated pages, and local notes; keep source snippets on the Mac/relay with field-level sensitivity, send only a minimal alert to the pendant, and never submit, send, purchase, or delete without confirmation. Require per-source opt-in and show evidence plus confidence for every inferred commitment.
- **missing:** A durable obligation/commitment ledger with source evidence, due-date confidence, status, and deduplication (not just generic memory facts); Cross-surface impact scan that checks calendar capacity and existing commitments before proposing a plan; A resumable preparation job that can fill reversible browser forms or draft notes and stop at an approval boundary; Quiet-hours and escalation policy for pendant alerts

### "“When a new request would overload me or conflict with something I already committed to, tell me plainly, show me the tradeoff, and prepare a kind reply or rescheduling option I can approve.”"
- **useful because:** The owner can currently accumulate commitments across email, calendar, and browser work without a single agent protecting their time. This capability turns fragmented obligations into a boundary decision: preserve the important commitment, negotiate a realistic alternative, or explicitly accept the cost. It supports the owner's agency without silently declining or sending anything.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime
- **model tier:** Use a cheaper background model to compare the incoming request with confirmed commitments, calendar load, and stated priorities. Use realtime only to ask the owner a short clarification when tradeoffs are genuinely ambiguous. Draft generation can run asynchronously.
- **latency:** When a request is opened, produce an initial conflict explanation in under 30 seconds; draft alternatives may take up to two minutes. Pendant notification should be one concise sentence and never interrupt during quiet hours unless the conflict is urgent.
- **cost:** Approximately $0.03–$0.20 per evaluated request, dominated by authenticated page reads and calendar/context retrieval; most routine comparisons can use cached structured facts.
- **security:** This crosses private messages, calendar, and potentially work systems. Require source opt-in, keep the original request and proposed response on the Mac/relay, expose quoted evidence and affected commitments, and require explicit approval before sending, declining, or moving anything. Never infer a social obligation from sensitive content without showing the owner why.
- **missing:** A priority and boundary profile that distinguishes firm commitments, negotiable commitments, protected personal time, and acceptable tradeoffs; A cross-source conflict evaluator that compares requests with calendar load and existing commitments without duplicating or silently rewriting them; A review surface showing the tradeoff, evidence, and multiple response options before approval; A browser/Mac draft-and-approval transaction with a hard no-send boundary and an auditable receipt


## Changes it proposed to its own stack

### `integration` — Add an obligation-evidence graph and deadline radar across the relay, authenticated browser bridge, and Mac workspace. Normalize candidate obligations (actor, deliverable, due window, consequence, source URL/file/message, quoted evidence, confidence, last-verified timestamp, status), merge duplicates, re-check volatile sources before escalation, compare against calendar capacity, and emit either a quiet preparation job or a minimal pendant cue. Keep inferred items separate from owner-confirmed commitments and expire unsupported inferences.
- **owner gets:** The owner gets warned about real obligations they never thought to turn into reminders, with enough evidence to trust or correct the warning, and receives prepared next steps before the deadline instead of vague anxiety or a noisy stream of notifications.
- effort: Medium-high: schema and lifecycle, authenticated extraction adapters, deduplication and revalidation, calendar-capacity reasoning, relay scheduling, and review UI/audio receipts.  ·  risk: False inferences could create stress or bad drafts; mitigate with confidence thresholds, quoted evidence, expiry, quiet defaults, and no irreversible action. If a surface is offline, mark stale and do not claim completion; resume from an idempotent preparation job.
- cost: Low recurring model cost if extraction is incremental and only changed sources are summarized; storage is small text metadata plus bounded evidence snippets. Browser/private-page reads dominate.  ·  latency: No impact on live conversation; background scans are asynchronous. High-confidence urgent alerts add a short relay-to-pendant delivery delay.
- security: Introduces a sensitive cross-source index. Encrypt at rest, minimize copied content, retain source pointers and hashes where possible, enforce source-level opt-in, and redact secrets from pendant audio.
- depends on: Authenticated browser read/queue with tab affinity; Mac local-note and calendar read adapters; Durable jobs and receipts with resumable/idempotent steps; Owner-configurable quiet hours, urgency horizon, and confirmation policy


## What it asked for

_Nothing._
