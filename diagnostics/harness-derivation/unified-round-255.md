# Harness derivation — unified — round 255

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Finish the thing I just asked for, but only after I physically approve the exact final result.”"
- **useful because:** This would turn a spoken request into a bounded, auditable transaction across the relay, Mac, browser, and pendant: the owner can walk away while the system prepares a checkout/form/message, then approve the exact digest from the pendant rather than trusting a vague spoken promise. It is the highest-value path from conversation to consequential real-world action.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime extracts the intent and speaks a concise preview; a cheaper planner builds the staged transaction and browser steps; deterministic executors perform only after the physical nonce approval.
- **latency:** Preview in 2–4 s; browser preparation may take 10–60 s; approval-to-submit under 5 s; never submit before the pendant approval receipt is correlated.
- **cost:** ~$0.01–$0.05 per invocation depending on planner turns; browser execution and receipts dominate latency, not model tokens.
- **security:** The digest must bind target, fields, recipients, totals, and browser origin; secrets/page contents never go to the pendant. Expire and single-use the nonce, reject world/page changes, and show a refusal rather than guessing. Requires a separate execution credential from approval if possible.
- **missing:** Wire the existing prepare/approve handoff to relay persistence and a real delivery/readback path; Connect physical_transaction_approval_latch events to the staged transaction verifier; Add browser page/world revalidation immediately before submit; Create an owner-visible pending/approved/expired dashboard state

### "“What exactly did you rely on when you told me that—and let me remove the underlying remembered fact if I don’t want you keeping it?”"
- **useful because:** The system currently can extract facts and act on them, but the owner cannot inspect a comprehensible provenance chain. This capability would show the originating utterance/evidence, derived graph entities, downstream uses, and off-machine deletion status, then erase the fact and its copies without erasing the action audit trail.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background model summarizes provenance into owner-readable language; deterministic code computes graph closure, deletion scope, and receipts; realtime is used only for the spoken answer.
- **latency:** Spoken explanation under 3 s for cached facts; deletion receipt under 10 s locally and explicitly marked pending for replicated relay storage.
- **cost:** ~$0.003–$0.02 per query; graph traversal and receipt generation dominate, with summarization optional.
- **security:** Return only evidence bound to the requesting owner/session; redact unrelated audio and page content. Erase extracted fact, derived copies, and evidence capsule, but preserve action history. Replicated deletion must be reported as requested-and-pending, never falsely complete.
- **missing:** Typed provenance edges from extraction evidence to context-graph entities and downstream jobs; A read-only owner-facing fact inventory and per-fact delete endpoint; Relay tombstone/replication receipts for off-machine erasure; Pendant-safe short summaries that do not replay private source audio

### "“Hand this conversation to my Mac and browser exactly where we left off, and tell me what happened if either side failed.”"
- **useful because:** A wearer can start with voice and finish in a logged-in browser without repeating the task. The relay packages a redacted turn summary, intent, constraints, and pending decisions; the Mac opens or resumes the bound tab, and the pendant receives a compact handoff/result receipt. This is useful precisely because no single node has both the conversation and the authenticated browser session.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime creates the short handoff capsule; deterministic routing and browser/Mac actions execute it; background model can compress long history after completion.
- **latency:** Acknowledge handoff in <2 s; open/resume browser in <10 s; report success/failure with a durable receipt even across bridge restarts.
- **cost:** ~$0.005–$0.02 per handoff; browser navigation and polling dominate latency.
- **security:** Bind capsule to a specific tab/session and expiry; exclude secrets and unrelated transcript; require confirmation when handoff changes or submits data. If the bridge or browser is offline, retain a resumable job rather than replaying actions blindly.
- **missing:** A redacted, signed conversation-handoff capsule schema; Binding between relay job, Mac workbench context, and browser session/tab; Use the existing browser lease with an active supervisor and explicit stale-command recovery; A pendant-readable completion/failure event path

### "“Before you act, tell me if my calendar, email, browser, and remembered context disagree about the same person, date, amount, or commitment.”"
- **useful because:** The dangerous failure is not lack of information but confidently combining contradictory information. This capability would create a contradiction report before an action: which sources disagree, what each actually says, how fresh it is, and what single clarification would resolve it. It would prevent wrong-date bookings, duplicate payments, and messages sent to the wrong person.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic normalization and comparison first; a background model explains only the conflicts that survive normalization; realtime speaks the short warning and asks one focused question.
- **latency:** Under 5 seconds for cached sources; up to 20 seconds when browser and Mac evidence must be freshly read. No external action proceeds while a material contradiction is unresolved.
- **cost:** ~$0.005–$0.03; evidence collection dominates, with model use limited to explanation.
- **security:** Inspect only explicitly bound browser tabs/apps and redact unrelated messages. Treat freshness and source identity as evidence, not truth. Never silently choose the newest or most convenient source; require owner clarification for material conflicts.
- **missing:** A normalized claim representation with source, timestamp, confidence, and scope; Cross-surface comparison over bound browser/Mac evidence, context graph, and relay receipts; A compact contradiction event the pendant can present without exposing private source text; A policy defining which contradiction classes block action

### "“Make sure this email, purchase, or booking is performed from the account and identity I intended—not merely whichever browser session happens to be open.”"
- **useful because:** A logged-in browser can hold several identities, profiles, and stale sessions. This capability would establish an identity-and-destination attestation before any consequential action, show the account, organization, recipient, and origin actually detected, and require a deliberate pendant confirmation when they do not match the spoken intent.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic browser/session inspection and origin matching; planner model maps spoken intent to the expected identity; realtime handles the concise discrepancy question.
- **latency:** 2–5 seconds for an already-open tab; up to 15 seconds for a safe navigation to inspect identity. Block submission until attestation is fresh.
- **cost:** ~$0.003–$0.02; browser inspection and revalidation dominate.
- **security:** Never display or transmit passwords, tokens, or full private profile data. Bind attestation to origin, tab/session, account identifier hash, destination, and expiry. Any account switch requires explicit physical approval and a fresh page-world check.
- **missing:** A browser identity attestation primitive returning minimally sufficient account/origin claims; Session-to-owner intent binding and freshness rules; A wrong-account refusal path that cannot fall through to ordinary execution; Dashboard and pendant presentation of redacted identity claims

### "“I’m traveling—show me what time this means where I am, but do not silently move my Mac routines or reinterpret the pendant’s zoneless timestamps.”"
- **useful because:** The system already has a deliberate Mac-zone rule, but the owner still cannot safely reconcile travel-facing times with machine-resolved routines. This capability would label Mac time, destination/local time, and unknown pendant time separately, highlight DST/date-boundary changes, and require an explicit choice before changing any routine.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic timezone conversion and DST calculations; realtime explains the result; background model is unnecessary except for ambiguous natural-language destinations.
- **latency:** Under 1 second for known zones; under 10 seconds when browser travel details or calendar evidence must be read. No routine mutation without explicit confirmation.
- **cost:** Near-zero model cost for structured zones; ~$0.002–$0.01 if natural-language travel context needs parsing.
- **security:** Do not infer location from IP, browser locale, or device clock. Treat owner-provided destination as an explicit value with expiry. Keep pendant zoneless timestamps as unknown instants unless the owner supplies a mapping.
- **missing:** An explicit owner travel-zone record with start/end and source; A three-column time presentation contract: Mac zone, travel zone, pendant unknown; DST/date-boundary test cases and routine-change confirmation semantics; A read-only preview before PATCH /routines/:routineId


## Changes it proposed to its own stack

### `relay` — Add an expiring lease and requeue sweep to relay_jobs, then have the Mac bridge publish a final claim/heartbeat/receipt state tied to the existing workbench context. On restart, classify a job as safely retryable only when its workbench context is uncommitted and every step is replaySafety idempotent/additive; otherwise surface a pendant/dashboard decision instead of replaying.
- **owner gets:** A Mac sleep, browser disconnect, or bridge crash would stop being a silent 24-hour 'processing' limbo. The owner gets a truthful resumed, waiting-for-approval, or failed result and does not have to repeat a request or wonder whether it already sent the email/booked the appointment.
- effort: Medium: schema migration, lease sweeper, bridge heartbeat, and one startup reconciliation path; add fault-injection tests for crash before dispatch, during dispatch, and after receipt.  ·  risk: A bad replay decision could duplicate an external action. Default to blocked for unrepeatable/unknown steps, require a fresh physical approval after any uncertainty, and retain the original receipt. If the sweeper is unavailable, leave jobs queued rather than guessing.
- cost: Negligible storage and request overhead; one heartbeat per active job (roughly tens of bytes/seconds). No model cost.  ·  latency: Adds at most one heartbeat interval to failure detection; normal execution unchanged.
- security: Lease ownership and idempotency keys must be authenticated and scoped to a job; do not let a stale bridge reclaim another worker's lease.
- depends on: orchestrator must close ordinary ledgers so completed plans are not falsely considered interrupted; relay_jobs lease_until plus requeue sweep; wire existing workbenchTransaction commit records into job finalization; use replaySafety, not reversibility, as the resume gate


## What it asked for

_Nothing._
