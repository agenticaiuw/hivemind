# Harness derivation — faculty-action — round 192

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Undo the last thing you did for me.” If it is safely reversible, restore the prior state; if the state changed since then, show me exactly what prevents a safe undo instead of guessing."
- **useful because:** An action that succeeded can still be wrong. A bounded undo window turns the executor from one-way automation into a trustworthy hand: it uses the recorded inverse only when fresh perception proves the target has not changed, and otherwise stops safely.
- **path:** faculty-judgement → faculty-action → faculty-perception → relay-realtime → mac-planner → browser-extension
- **model tier:** Background/standard model plans the inverse; realtime model is used only if the owner is conversing live. Verification and execution are deterministic routes, not an expensive model call.
- **latency:** For a recent Mac action, 2–5 seconds for precondition verification and undo; if state has drifted, under 2 seconds to report blocked. No silent retries.
- **cost:** Usually <$0.02 in model/API cost; most cost is one perception/verifier round trip and the inverse action itself.
- **security:** Undo records must contain opaque object IDs and redacted state hashes, not page contents or secrets. Require the existing physical transaction approval latch for destructive or externally visible inverses. Never undo an operation whose precondition hash no longer matches; report unknown rather than overwrite another person’s change.
- **missing:** An inverse/precondition schema in action receipts (operation ID, reversible steps, before-state hash, expiry, and safe inverse description); A verifier-backed undo endpoint that refuses on state drift and emits a signed result for the pendant

### "“Make this change across all the apps, but if any step only partly succeeds, repair what you can and tell me what remains.”"
- **useful because:** Cross-app work currently risks stopping with a half-finished world: a calendar edit may succeed while a browser form or message fails. A verified saga would execute steps one at a time, verify each postcondition, run only predeclared compensations for reversible steps, and leave an explicit unresolved remainder instead of blindly retrying.
- **path:** faculty-judgement → faculty-action → faculty-perception → mac-planner → browser-extension → relay-realtime
- **model tier:** Standard/background model compiles the saga and compensation plan; realtime is only for the owner’s live clarification. Mac/browser executors and the read-only verifier do the actual work.
- **latency:** One verification after each step, typically 5–15 seconds for a three-step workflow. On failure, compensation begins immediately but never exceeds the declared retry/rollback budget.
- **cost:** <$0.05 for a normal three-to-five-step workflow; dominant cost is Mac/browser round trips, not model tokens.
- **security:** Before execution, show a concise step/compensation summary and require the existing physical approval latch when any step sends, deletes, purchases, or changes permissions. Compensation must be allowlisted and independently verified. If verification is stale or unavailable, pause as unknown rather than claiming completion.
- **missing:** A saga/compensation operation schema and durable step state in the job ledger; Executor support for idempotency keys and compensation actions; A single owner-facing receipt that distinguishes completed, compensated, and unresolved steps

### "“Apply my requested change, but preserve anything I or someone else changed since you planned it.” When the live state conflicts with the plan, show me a three-way diff and let me approve a merged result rather than overwriting or simply giving up."
- **useful because:** Today an action executor can verify that state changed, but safe verification alone cannot reconcile concurrent edits. A three-way merge capability would let the owner automate collaborative calendars, documents, task lists, and browser forms without clobbering fresh human changes. It is materially different from retry, rollback, or undo: it computes a merge from the original observation, intended mutation, and current observation.
- **path:** faculty-judgement → faculty-perception → faculty-action → mac-planner → browser-extension → relay-realtime
- **model tier:** Use a standard/background model to derive a structured patch and conflict explanation; use the realtime tier only to discuss conflicts live. Deterministic diff/merge and postcondition verification should run without a model.
- **latency:** 2–8 seconds for one structured object; 10–30 seconds for a document or multi-field browser workflow. Never apply an ambiguous merge automatically.
- **cost:** Typically $0.02–$0.10 per conflict depending on document size; dominant cost is fresh Mac/browser observation and model context for the conflicting fields.
- **security:** Send only field-level redacted values or hashes for sensitive data; never route passwords, tokens, or private page contents through the pendant. Require the existing physical approval latch before applying a merge that sends, deletes, changes permissions, or edits another person’s shared data. Record the base/current/intended hashes and the exact fields changed for audit.
- **missing:** A structured observation/patch format with stable locators and field-level sensitivity labels across Mac and browser surfaces; A merge planner that returns unchanged, owner-intended, concurrent, and conflict fields with explicit confidence; An apply-merged-patch executor with idempotency and independent postcondition verification

### "“Handle these purchases or paid actions, but never exceed the total budget I gave you across the browser and Mac.” Show the running commitment, reserve before submitting, and stop every other action when the cap would be crossed."
- **useful because:** A per-action approval is not a cumulative safety boundary. The owner needs one budget that follows a workflow across browser sessions, Mac apps, retries, and delayed jobs, so a partial failure or duplicate submission cannot quietly exceed what they intended.
- **path:** faculty-judgement → faculty-action → faculty-perception → relay-realtime → browser-extension → mac-planner
- **model tier:** Standard model classifies and explains costs; deterministic relay accounting performs reservations and releases. Realtime is only for live clarification.
- **latency:** Under 1 second for a reservation check; 2–5 seconds for fresh price/total verification before submission.
- **cost:** <$0.02 per guarded action; most cost is the existing browser/Mac verification round trip.
- **security:** Persist only merchant/action identifiers, amount, currency, and hashes—not card data or checkout secrets. Require the existing physical approval latch for each externally committing submission unless the owner explicitly establishes a narrower policy. Reservations expire and are released on unknown outcomes; never assume a failed receipt means no charge.
- **missing:** Relay-level durable budget accounts and atomic reserve/commit/release primitives; Receipt fields for monetary commitment and duplicate-submission identity; Fresh browser/Mac total extraction with currency normalization

### "“If the same request is already running somewhere, join it instead of doing it twice, and tell me which attempt is authoritative.” Deduplicate overlapping actions across the relay, Mac, and browser even when the first link drops or the owner repeats the request."
- **useful because:** The owner should not have to remember whether a dropped voice exchange submitted an email, changed a record, or started a purchase. A durable semantic action identity lets every surface converge on one operation, attach late receipts to it, and prevent duplicate external side effects without pretending an unknown outcome is failure.
- **path:** relay-realtime → faculty-judgement → faculty-action → mac-planner → browser-extension → faculty-perception
- **model tier:** Standard model derives a canonical intent fingerprint from the owner’s request; deterministic relay and executors enforce idempotency. Realtime only handles the owner-facing status conversation.
- **latency:** Under 500 ms to detect an existing in-flight operation; normal execution latency thereafter. Unknown external outcomes remain pending until independently checked.
- **cost:** <$0.01 per request beyond existing calls; storage and lookup dominate, not model inference.
- **security:** Fingerprints must exclude secrets and sensitive free text, using typed normalized fields and keyed hashes. Scope identities to the owner, account, target, and expiry so unrelated actions cannot collide. Never merge two requests merely because their wording is similar; require a strong typed match and expose the chosen operation ID.
- **missing:** A canonical intent fingerprint and idempotency-key contract shared by relay, Mac, and browser executors; An operation registry that supports attach/resume/unknown states across link drops; A commit rule that independently verifies whether an external side effect occurred before allowing a retry


## Changes it proposed to its own stack

### `integration` — Extend verify_operation_step and the action ledger with an attemptId and evidence-chain fields: the executor receipt's operationId/stepId/attemptId must be passed to the verifier; the verifier returns observedAt, locator, postcondition hash, and source surface; the commit path accepts success only when the attempt matches and evidence is fresher than the action start. On mismatch, classify the step as unknown and block retries until a new plan is produced.
- **owner gets:** The system will stop saying “done” because an old browser snapshot or a receipt from a previous retry happened to look successful. When something goes wrong, the owner can see which exact attempt was verified and why the system stopped instead of making a second unintended change.
- effort: Moderate: extend the operation/receipt schema, thread correlation through Mac/browser executors, and enforce freshness in the commit service; no new hardware required.  ·  risk: Older jobs lack attempt IDs; migrate them as legacy and refuse automatic commit, offering a read-only status. A clock mismatch could reject good evidence, so use server monotonic timestamps plus source observedAt and surface the reason for rejection.
- cost: Negligible storage and model cost; saves repeated model calls caused by false success and unsafe retries.  ·  latency: Adds one verifier round trip (roughly 0.5–2 seconds) before commit; no impact on actions that are only prepared or read-only.
- security: Improves replay resistance and prevents receipt/evidence confusion. Evidence remains sensitivity-labeled and should default to hash_only; never put secrets into the correlation envelope.
- depends on: verify_operation_step; GET /jobs/:jobId/receipts; POST /execute; faculty-perception exposing fresh observedAt/source provenance


## What it asked for

_Nothing._
## Its own summary

Recorded three new action-layer proposals: (1) a verified, state-drift-safe “undo the last action” capability; (2) a cross-surface saga that verifies every step and compensates only declared reversible steps after partial failure; and (3) attempt-correlated, freshness-checked evidence linking executor receipts to faculty-perception verification, preventing stale or replayed evidence from closing an operation. I still need the operation schema to carry inverse/precondition hashes, durable saga compensation state, and executor/verifier attempt correlation. I also asked faculty-perception to identify any collision or remaining postcondition gap.

**Biggest unknown:** Whether the live ledger already has a reversible-step or compensation representation hidden behind an undocumented route; without that inventory, implementation planning may duplicate existing receipt semantics.

