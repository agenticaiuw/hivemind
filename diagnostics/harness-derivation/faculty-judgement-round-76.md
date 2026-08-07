# Harness derivation — faculty-judgement — round 76

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What am I waiting on?” Then, whenever an expected reply or task is late, give me one short spoken nudge and prepare (but never send) the follow-up."
- **useful because:** Today the system can inspect individual mail, calendar, browser pages, and Mac jobs, but cannot turn them into the life-level answer: which commitments are blocked by another person/system, how long they have been waiting, and what the least-effort next move is. The pendant can deliver only the few genuinely actionable nudges; the Mac/browser can gather private evidence; the relay can continue watching while the Mac sleeps.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-terminal → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use the cheaper background tier for periodic reconciliation and drafting; use realtime only to answer the spoken question or deliver a one-sentence urgent nudge. Use faculty-judgement for dependency classification and faculty-action for preparing reversible drafts.
- **latency:** Spoken query: under 5 seconds for cached graph plus citations; background scans can take minutes. Never interrupt during quiet hours or repeat a nudge until the owner acknowledges it.
- **cost:** Periodic scan is dominated by authenticated page/email extraction and small summarization, roughly 1–3 cents per scan depending on page count; realtime answer is a small low-latency turn. Store normalized hashes and evidence snippets to avoid re-sending full pages.
- **security:** Private mail and logged-in pages leave the browser/Mac only to the relay/model as needed; redact secrets and unrelated message bodies. Treat inferred waiting states as uncertain. Drafts are reversible; sending mail, submitting forms, or changing deadlines always requires explicit confirmation.
- **missing:** A durable dependency/obligation projection that links outbound messages, appointments, browser transactions, and Mac jobs to expected evidence and due windows; A scheduler with quiet-hours, deduplication, acknowledgement, and escalation rules for pendant nudges; A typed evidence state such as prepared, sent, acknowledged, awaiting, overdue, cancelled, or unknown

### "“Make a temporary handoff for Alex: give them only what they need to finish this, let them ask questions, and revoke it tomorrow.”"
- **useful because:** The owner can delegate work today only by forwarding a messy email, exposing an account, or manually assembling context. This would let the hive turn a spoken goal into a narrowly scoped, expiring collaboration packet: relevant facts and files, the current state, allowed questions/actions, and a clear audit trail—without granting Alex access to the owner’s logged-in browser or Mac.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-terminal → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheaper background model to assemble and redact the packet and answer routine questions; use realtime only for the owner’s spoken approval, scope edits, or urgent revocation. Never let a model expand scope implicitly.
- **latency:** Produce a reviewable packet in under two minutes for ordinary mail/files/browser evidence. Revocation must take effect within seconds at the relay; questions can be answered asynchronously.
- **cost:** A few cents per handoff, dominated by extracting private evidence and generating a concise packet. Storage is a small encrypted manifest plus selected artifacts; an expiring relay link avoids repeated context transfer.
- **security:** Default-deny sharing: no secrets, credentials, unrelated messages, or raw browser sessions. Every field needs a source and sensitivity label; the owner must approve recipients, exact contents, expiry, and permitted operations. Relay must enforce expiry and revocation server-side, log every view/download/question, and support immediate destruction. Any action affecting an external system remains a draft for owner approval.
- **missing:** An encrypted, expiring relay workspace with recipient authentication, revocation, per-artifact permissions, and immutable access receipts; A cross-surface redaction and least-privilege compiler that can turn browser/Mac evidence into a packet without copying session authority; A constrained question-and-answer endpoint that can answer only from the approved packet and clearly say when the answer is outside scope; Owner-facing approval and revocation controls on the pendant, including a physical stop path


## Changes it proposed to its own stack

### `integration` — Add a 'waiting-state projector' between perception and judgement. It consumes immutable journal/job/browser/research events and emits compact records keyed by correlation ID: obligation owner, expected evidence, createdAt, last positive evidence, dueAt or inferred response window, state (prepared/sent/acknowledged/awaiting/overdue/cancelled/unknown), confidence, and a redacted citation. It must require positive evidence before calling something sent, expire stale 'processing' records to unknown, merge duplicates across Mac and browser, and expose a read-only projection for the pendant nudge scheduler.
- **owner gets:** The owner gets an honest answer to 'what am I waiting on?' instead of a confident but false success report, and receives fewer, better-timed nudges with the exact evidence behind each one.
- effort: Medium-high: event schema and projector, correlation/merge rules, due-window inference, projection endpoint, tests with offline browser and stuck pipeline fixtures, then pendant delivery policy.  ·  risk: A mistaken inferred due date could create anxiety or a bad follow-up. Mitigate by labeling inference versus explicit deadline, requiring acknowledgement before escalation, and retaining source citations. If projection fails, fall back to raw job and journal status rather than inventing state.
- cost: Low recurring model cost if extraction/classification is batched and hashes are reused; storage is small JSON records plus short citation hashes. One initial migration of existing journal/jobs is the main cost.  ·  latency: No impact on ordinary voice turns when read from cache; updates arrive asynchronously after scans or events. A fresh query may wait for one bounded reconciliation pass.
- security: Projection should contain only minimal redacted evidence and sensitivity labels; raw mail/page text remains in its source surface. Correlation IDs must not be guessable and cross-account joins must be denied by default.
- depends on: The existing immutable job/journal/browser event identifiers and receipts; A durable context projection with TTL and provenance (the open memory work); A quiet-hours and acknowledgement policy for wearable notifications

### `relay` — Build an encrypted, expiring delegation workspace: a server-side manifest references approved redacted artifacts rather than copying sessions; each artifact and operation has a deny-by-default scope, recipient-bound capability token, expiry, and revocation version. Add a constrained Q&A endpoint whose retrieval is limited to the manifest, plus append-only view/download/question receipts and immediate purge on revoke.
- **owner gets:** The owner can safely ask another person to finish real work without forwarding an entire inbox, exposing credentials, or losing track of what was shared. They get the human benefit of delegation with the control of a temporary permission slip.
- effort: High: encrypted artifact broker, recipient authentication, redaction/scope compiler, constrained retrieval, revocation propagation, receipt UI, and pendant approval/revoke flows.  ·  risk: Over-sharing or a stale artifact could disclose private information; a compromised recipient could screenshot it. Mitigate with explicit field-level review, short expiry, watermarking, download limits where practical, immutable receipts, and a prominent physical revoke action. If authentication fails, do not create the workspace.
- cost: Moderate implementation and storage cost; per handoff uses small model calls for redaction and indexing, with relay storage and authentication dominating. No need to retain raw audio or browser sessions.  ·  latency: Initial packet preparation is asynchronous (seconds to minutes); permission checks and revoke are low-latency relay operations. Q&A may take a few seconds and must time out rather than broaden retrieval.
- security: This introduces a new controlled data-sharing boundary, so it must use separate encryption keys and tokens from the owner’s sessions, minimize logs, redact secrets before persistence, and make expiry/revocation authoritative at the relay.
- depends on: A durable correlation ID and provenance record for every selected artifact; A redaction/classification service that can prove why each field was included; Pendant-local approval and universal stop/revoke behavior; Recipient authentication and an owner-visible delegation audit surface


## What it asked for

_Nothing._
## Its own summary

Discovered the current owner evidence and 123-route surface, then proposed a new owner-facing capability: “What am I waiting on?” with concise, evidence-backed nudges and unsent follow-up drafts. I also proposed the missing integration: a correlation-keyed waiting-state projector that distinguishes prepared/sent/acknowledged/awaiting/overdue/unknown and refuses to treat UI success as truth. This is deliberately downstream of faculty-action’s execution contract, not a duplicate: execution governs permission to act; the projector governs what remains outstanding afterward.

**Biggest unknown:** The durable event/journal correlation and notification primitives are still not visible to me, so I cannot tell whether the projector is a small wiring task or needs new persistence. I also still lack the owner’s exact interruption/quiet-hours policy; I did not re-request either because those requests are already pending.

