# Harness derivation — faculty-action — round 32

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Do it, and tell me only when you can prove it happened.”"
- **useful because:** Today the mind can decide an action and a hand can queue it, but completion is often inferred from the executor's acknowledgement. This gives the owner a genuinely closed loop: the pendant captures the intent, judgement chooses Mac/browser, faculty-action performs it, faculty-perception re-reads the resulting state, and the always-on relay retries and speaks a short proof or a precise failure. It is especially useful for reminders, edits, and browser workflows where 'queued' is not the same as 'done'.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the realtime tier only for the spoken intent and final concise result; use a cheaper background worker for retries, polling, and evidence normalization. faculty-judgement plans the operation; faculty-action executes; faculty-perception verifies against a declared postcondition.
- **latency:** Immediate reversible actions should return an acknowledgement in 1–2 seconds, then a verified result within 10 seconds. Long browser or offline jobs may take minutes, with one spoken completion/failure notification and no repeated chatter.
- **cost:** Roughly $0.01–$0.05 per completed workflow depending on verification reads and model use; most retries and field comparison should be deterministic, with model calls only for ambiguous page changes.
- **security:** Evidence may contain private calendar, mail, or account data and must stay on the Mac/relay encrypted path, with redaction before dashboard display. Never claim verified success from an executor receipt alone. Destructive or externally-visible actions still require the owner's existing confirmation gate; verification must not accidentally submit a second action.
- **missing:** A typed postcondition contract attached to every planned action (target, expected state, verification surface, timeout, and acceptable evidence).; A relay durable verification/retry worker that survives the Mac or browser bridge disappearing and reports typed states: queued, executed, verified, contradicted, or unknown.; Mac/browser adapters that return stable before/after evidence and a re-read operation, plus a pendant notification path for completion receipts.; A dashboard timeline that shows the action, executor acknowledgement, verification evidence, and any fallback without exposing raw private page contents.

### "“Take care of this until it’s done, but don’t spend more than $20, don’t contact anyone, and ask me only if you hit a real boundary.”"
- **useful because:** The owner cannot currently delegate a bounded mission safely: they must either supervise every step or grant an overly broad instruction. This capability lets them specify a time, money, privacy, and side-effect envelope once. The relay keeps the mission alive, faculty-action uses the Mac and authenticated browser as appropriate, perception checks progress, and the pendant interrupts only when the declared envelope would be exceeded or the evidence is genuinely ambiguous.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use realtime only to capture the spoken envelope and handle an exception conversation. Use a cheaper background model or deterministic policy engine to schedule retries, compare spend/time/side-effect counters, and route routine steps. Use the judgement tier only when a choice falls outside the envelope.
- **latency:** Capture and acknowledge the envelope in under 2 seconds. Routine work proceeds asynchronously; boundary checks should react within 1–5 seconds of a new cost, permission, or external-side-effect signal. The owner should not be kept in a live session while the mission runs.
- **cost:** About $0.01–$0.10 per mission, dominated by occasional ambiguous decisions; deterministic accounting, retry scheduling, and routing should be nearly free. External transaction costs remain separately visible and never hidden in model cost.
- **security:** The envelope itself may contain sensitive budgets, account scope, or prohibitions. Store it encrypted with short-lived mission credentials and least-privilege surface bindings. Treat missing telemetry as a stop, not permission. Never infer that 'don’t contact anyone' permits sending drafts, and require explicit confirmation before crossing any irreversible or financial boundary.
- **missing:** A first-class mission/envelope schema covering deadline, monetary budget, domains/accounts, allowed side effects, data-egress policy, retry limit, and escalation rules.; A relay-owned mission controller with durable counters and leases across Mac/browser availability, not merely a one-shot job tracker.; Action adapters that emit normalized cost and side-effect events (including 'attempted but not sent') and enforce the envelope before dispatch.; Pendant interaction for a single exception approval/deny response, plus dashboard controls to pause, amend, or terminate a mission with an audit trail.


## Changes it proposed to its own stack

### `integration` — Add a cross-surface ActionProof protocol. At planning time, faculty-judgement emits an immutable action_id and a typed postcondition (surface, locator or query, expected normalized value/hash, deadline, and privacy class). faculty-action records pre-state, dispatches to Mac or browser with idempotency_key=action_id, and returns executor_result without labeling completion. faculty-perception performs a fresh read on the declared surface, compares it to the postcondition, and emits signed proof or contradiction. Relay owns a durable state machine with bounded retries and an offline pendant notification queue; dashboard renders the evidence chain and exposes retry/undo where supported.
- **owner gets:** The owner gets honest, low-noise completion: “calendar event moved to 3pm—verified” rather than “I tried.” If the browser closes, Mac sleeps, or a site silently rejects a form, the pendant reports “not verified” and keeps working instead of leaving the owner to discover the failure later.
- effort: Medium-high: shared schema and state machine, adapters for typed Mac/browser reads, relay persistence and retry scheduling, privacy-aware evidence storage, and pendant notification integration. Start with reminders and one browser form flow before generalizing.  ·  risk: A stale cache or weak locator could produce a false proof; require fresh reads, timestamps, surface affinity, and an explicit unknown state. Retries could duplicate side effects, so only retry operations carrying an idempotency key or a verified undo path. If verification is unavailable, preserve the executor receipt but say unknown. Recovery is a bounded retry or owner-directed recheck.
- cost: Small relay/database/storage cost; approximately $0.005–$0.03 per verification-heavy job, dominated by ambiguous page interpretation. Evidence retention should default to hashes/snippets and expire quickly.  ·  latency: Adds one fresh read, typically 0.5–3 seconds on Mac/browser; background retries do not block the initial acknowledgement. Complex pages may take up to the declared deadline.
- security: Action proofs can reveal private values. Encrypt evidence in transit and at rest, minimize to normalized fields/hashes, apply sensitivity TTLs, and require explicit confirmation before any retry that might be externally visible.
- depends on: A durable browser command queue with request IDs and tab/session affinity; Typed readiness/reconciliation for Mac and browser surfaces; A pendant completion-notification and offline queue path; A provenance-aware context/evidence projection rather than raw page dumps


## What it asked for

_Nothing._
## Its own summary

Recorded a new closed-loop ActionProof capability and integration change: execution acknowledgements are not completion; a fresh Mac/browser read must verify a typed postcondition, with durable relay retries and concise pendant proof/failure notifications. Live discovery confirms the Mac bridge is online, but Accessibility and Screen Recording are still ungranted, the browser bridge is offline with 3 pending commands, and computer-use loop is disabled.

**Biggest unknown:** Whether faculty-perception and faculty-judgement already expose stable postcondition/evidence contracts; peer questions are pending.

