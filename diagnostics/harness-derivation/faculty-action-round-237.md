# Harness derivation — faculty-action — round 237

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Do the whole thing, but don't leave me half-done if one step fails.""
- **useful because:** The system can currently execute individual Mac/browser actions and record receipts, but a real request such as 'download the invoice, rename it, attach it to this draft, and create a reminder' can fail after step 2. This capability makes a multi-surface workflow a verified transaction: stage reversible work, execute in dependency order, independently verify each postcondition, and either continue, compensate safe partial work, or stop with an exact resumable checkpoint. It is the single most useful execution capability because it turns computer control from a sequence of hopeful clicks into a truthful, recoverable operation.
- **path:** unified → faculty-judgement → faculty-action → faculty-perception → mac-planner → mac-vision → browser-extension → relay-realtime → pendant
- **model tier:** Use the cheap background model for dependency extraction and compensation planning; use realtime only to clarify an ambiguous owner request; use faculty-perception's read-only verifier for every committed step. No model should infer success from an executor receipt alone.
- **latency:** Up to 1 s for local planning, then under 3 s per verified step; pause immediately on unknown verification. The owner can hear a short progress update and resume later without rerunning completed steps.
- **cost:** Usually 1 background planning call plus one small verification call per step; roughly 2–8x the API cost of a one-shot action, dominated by perception snapshots, but much cheaper than repeating a failed workflow or sending a duplicate message.
- **security:** Assign every step an idempotency key, precondition digest, postcondition, and compensation. Never auto-compensate destructive or externally visible actions; stage them for the existing physical approval latch. Persist only opaque handles and hashes in relay logs, not mail bodies or secrets. If verification is unknown, do not claim success or retry blindly.
- **missing:** A first-class workflow ledger that stores step dependencies, idempotency keys, compensation policy, and checkpoint state across relay restarts; An executor contract that returns a stable action/attempt identifier joinable to receipts; A coordinator that invokes verify_operation_step after each step and exposes resumable checkpoints to the pendant

### ""Fill in the password/verification code and finish the form, but never tell me or the pendant the secret.""
- **useful because:** The browser is the only surface that already holds authenticated sessions and can see secret fields, while the pendant is intentionally a poor place to expose credentials. This lets the owner ask for a sensitive form completion conversationally without secret text entering voice transcripts, relay logs, model context, Mac action arguments, or pendant memory. The browser fills only the named field, submits only after the existing physical approval latch, and returns a redacted, independently verified result.
- **path:** relay-realtime → unified → faculty-judgement → faculty-action → faculty-perception → browser-extension → mac-planner → pendant
- **model tier:** Use a small background model to classify the requested field and risk; never send the secret to a model. The browser extension performs the secret-bearing operation locally. Use faculty-perception only for redacted DOM state and a hash of the target field's postcondition.
- **latency:** 1–2 s to identify the active origin and target field; 2–5 s for the browser-local fill and verification. If origin, field, or session binding is ambiguous, stop rather than ask the model to guess.
- **cost:** One small intent call plus one redacted verification per form, roughly the cost of an ordinary browser action; secret handling is local and adds negligible API cost.
- **security:** The browser bridge must enforce origin/session binding, field-type allowlists, and no-readback: the secret is write-only and never returned in screenshots, DOM snippets, receipts, speech, or logs. OTPs and payment fields require deliberate pendant approval; destructive submits remain staged. Refuse cross-origin redirects, clipboard extraction, and any request for the model to repeat the secret. A compromised page must not be able to turn a fill command into a different action.
- **missing:** A browser-local secret broker action with an explicit write-only field handle and origin hash; A redacted browser verification response that proves the intended field changed without returning its value; A policy binding between secret-field risk, physical_transaction_approval_latch, and submit

### ""Show me exactly what will change, then let me approve that exact change from the pendant.""
- **useful because:** Before an action crosses Mac, browser, and external services, the owner needs a compact, trustworthy preview rather than a vague confirmation. This capability computes a dry-run diff (files, drafts, calendar changes, browser target and side effects), binds it to a canonical digest, speaks a short summary, and makes the pendant's approval valid only for that digest. If the page, target, or data changes before execution, approval expires instead of silently applying a different operation.
- **path:** faculty-judgement → faculty-perception → faculty-action → mac-planner → mac-vision → browser-extension → relay-realtime → pendant → unified
- **model tier:** Use a cheap model to summarize already-structured diffs; never let a model generate the approval digest. The planner produces typed mutations, perception captures pre-state, and action executes the exact signed plan after the physical latch returns approval.
- **latency:** Preview in 2–4 s for a normal request, with a one-sentence spoken summary and a short haptic pending pattern. Commit in under 3 s after approval; invalidate immediately on stale session, changed pre-state, or deadline.
- **cost:** One planning call and one pre-state/post-state verification per mutation group; about 2–4x a normal action, dominated by generating the diff. This is worthwhile for high-impact actions and can be skipped for owner-whitelisted reversible actions.
- **security:** The preview must redact secrets and minimize private content, using field labels, counts, and hashes where possible. Approval is a nonce over plan digest, target session, precondition digest, risk class, and expiry; no approval may be reused after any mutation or redirect. Require explicit owner policy for whether previews may include message bodies or file paths.
- **missing:** Typed dry-run contracts for Mac and browser actions that return intended mutations without applying them; Canonical serialization and digesting of a cross-surface plan, including target session and pre-state; Pendant rendering for a compact diff summary (haptic categories plus optional spoken summary) and a stale-plan refusal path

### ""Do this task, but make it physically impossible for you to touch anything outside these files, websites, and apps.""
- **useful because:** Today an action plan can be semantically narrow while an executor or browser session still has broad authority. The owner should be able to declare a hard scope—specific file roots, URL origins, app identities, and allowed mutation types—and have Mac, browser, relay, and pendant enforcement reject anything outside it. This is stronger than asking the model to be careful: a mistaken plan or prompt injection becomes a blocked operation.
- **path:** faculty-judgement → faculty-action → mac-planner → mac-vision → browser-extension → relay-realtime → pendant → unified
- **model tier:** Use a small model only to translate the owner's scope into typed resources. Enforcement is deterministic in the relay and local executors; no model decides whether a path or origin is in scope.
- **latency:** Scope compilation under 500 ms; each action adds under 50 ms for policy checking. A violation should stop the operation before the attempted mutation and produce an immediate pendant outcome beacon.
- **cost:** Negligible per-action model cost after the initial scope compilation; policy checks are local. The engineering cost is implementing enforcement in every executor, especially browser navigation and shell actions.
- **security:** Use canonical paths, resolved symlinks, normalized URLs, origin and frame restrictions, app bundle identifiers, and deny-by-default network access. Scope tokens must be signed, short-lived, and bound to operation ID and physical approval digest. Never treat a natural-language phrase such as 'my project' as an enforceable scope without resolving it to concrete handles.
- **missing:** A shared signed capability-token format understood by relay, Mac executor, and browser bridge; Path/origin/app allowlist enforcement inside mac_run_actions and browser actions, before dispatch; A scope-violation receipt and pendant-safe explanation that reveals no private path or URL content

### ""When this exact kind of message arrives, prepare the work for me automatically, but never send or publish anything.""
- **useful because:** The owner should be able to turn recurring incoming work into a safe, useful draft without handing over authority to communicate externally. For example, an invoice email can be classified, its attachment saved to an allowed folder, a calendar proposal prepared, and a reply draft created—while the system leaves sending, deletion, purchases, and publication untouched. The pendant can alert the owner with a compact summary and a single explicit next step.
- **path:** relay-realtime → unified → faculty-judgement → faculty-action → faculty-perception → mac-planner → browser-extension → pendant
- **model tier:** Use a background model for message classification and draft generation; use deterministic typed rules for trigger matching and prohibited side effects. Realtime is needed only when the owner asks what was prepared. Never use the low-latency model for every incoming message.
- **latency:** Process each matching event within 30 seconds when the Mac/browser is online; queue it when offline and alert on reconnection. The owner gets one concise haptic/spoken alert, not a conversation for every event.
- **cost:** One small background inference per matched event plus local file/browser work; typically cents or less per event. Cost is controlled with deterministic prefilters before invoking a model.
- **security:** Triggers must bind to sender/domain, message class, and attachment type, not just keywords. Treat all message and attachment content as hostile instructions. Drafts are private and never sent automatically; any external side effect uses the existing physical approval policy. Keep a deduplicated event ID so reconnects cannot create duplicate drafts or files.
- **missing:** A durable event subscription source for Mail/browser changes with stable event IDs; A declarative trigger and side-effect allowlist language that can be reviewed by the owner; A background worker that invokes the Mac/browser surfaces and records draft-only receipts while the relay is asleep

### ""Keep this automation on a leash: no more than this many messages, file changes, or dollars per day, and stop before the limit.""
- **useful because:** Recurring automation can be logically correct yet still go wrong at scale—a loop can create hundreds of drafts, rename a directory tree, or incur repeated purchases/API charges. The owner should be able to set hard, visible budgets by action class, destination, time window, and workflow. The relay reserves budget before dispatch, the Mac/browser executors decrement it atomically, and the pendant warns as the limit approaches. This gives the owner a safety control they cannot get from a per-action confirmation alone.
- **path:** unified → faculty-judgement → faculty-action → relay-realtime → mac-planner → browser-extension → pendant → faculty-perception
- **model tier:** No model should decide budget compliance. A small background model may translate a spoken policy into a proposed typed rule, but deterministic relay enforcement owns reservation, accounting, and refusal.
- **latency:** Budget reservation under 100 ms before each dispatch; warnings can be batched. A limit breach must stop synchronously before the action, not after a receipt arrives.
- **cost:** Near-zero inference cost after policy creation; a compact append-only counter store and reconciliation receipts are the main engineering cost.
- **security:** Budgets must be keyed by owner, operation, destination, and currency/resource type; use monotonic counters and idempotency keys so retries cannot double-spend. Unrecognized costs or uncertain receipts reserve conservatively and quarantine the workflow. Never allow a model, webpage, or Mac process to raise its own budget. Changes to high-risk budgets require the existing physical approval latch.
- **missing:** A relay-side atomic quota/reservation service with durable counters and expiry windows; Typed cost attribution in Mac/browser receipts (message sent, bytes changed, purchase amount, external API spend); Pendant UI/haptic states for reserved, near-limit, exhausted, and reconciliation-unknown


## What it asked for

_Nothing._
## Its own summary

Recorded three new, non-identical capabilities: (1) verified multi-surface transactions with checkpoints and safe compensation—the highest-value execution capability; (2) a browser-local, write-only secret broker for completing sensitive forms without exposing secrets to the model, relay, or pendant; and (3) digest-bound dry-run previews so physical approval applies only to the exact planned change. Live discovery confirms verify_operation_step is granted only as an unresolved schema, so it cannot yet independently verify anything.

**Biggest unknown:** The actual implementation route for fresh Mac/browser postcondition verification is still missing. The nearest observed candidates are GET /workbench/contexts/:contextId, POST /browser/provenance/:recordId/check, and GET /journal; these need inventory and a live test before action commits can honestly be closed. I also still need typed dry-run contracts, a workflow ledger with idempotency/compensation, and a browser-local write-only secret-field primitive.

