# Harness derivation — faculty-action — round 179

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I tell you to do something, carry it out across my Mac and browser and tell me only what you independently verified—not what a tool merely reported."
- **useful because:** This is the core trust boundary for an action-taking assistant: a calendar edit, message draft, or browser change is not claimed complete until fresh state proves it. A mismatch halts before retries can duplicate or damage the action.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-action
- **model tier:** Use realtime only to capture/confirm the short voice intent; use the cheaper planner for decomposition, deterministic Mac/browser executors for steps, and faculty-perception for read-only postcondition checks.
- **latency:** Under 2 seconds for a simple action; up to 10 seconds for a multi-step browser workflow. Verification adds one fresh read per mutating step.
- **cost:** Usually one planner turn plus cheap verification reads; roughly $0.01–$0.08 depending on workflow, dominated by vision/browser steps rather than verification hashes.
- **security:** Secrets and page contents remain on Mac/browser. Per-step evidence is redacted and sensitivity-labeled. A failed or unknown verification must produce an honest stopped state, never an automatic mutating retry; irreversible actions still require the existing physical transaction approval latch.
- **missing:** Wire verify_operation_step into the commit path with operation_id and step_id correlation; Persist a tamper-evident receipt containing executor result, verifier provenance, and unknown/verified status; Add a policy rule for which action classes require physical approval

### "If an action partly succeeds, stop and show me exactly what changed and what did not, then offer a safe repair or undo plan instead of guessing."
- **useful because:** Today a multi-step action can leave a confusing partial state: one browser field changed, a file moved, or a draft created while a later step failed. A truthful action agent should turn that into a recoverable checkpoint, not silently continue or claim failure/success wholesale.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-action
- **model tier:** Cheap deterministic executor and verifier first; use a slower background model only to synthesize a human-readable repair plan. Realtime speaks the short status and asks before any compensating mutation.
- **latency:** Immediate partial-state receipt within 3 seconds; repair-plan generation within 15 seconds. No compensation runs automatically for irreversible or ambiguous states.
- **cost:** Low for file/app state; $0.02–$0.10 when browser screenshots or model-generated repair plans are needed.
- **security:** Evidence is scoped to the operation and expires. Never include secrets or full page contents in the pendant. Compensation must be separately approved when it can send, delete, purchase, or publish.
- **missing:** A per-step checkpoint/compensation schema in the job ledger; A read-only diff renderer for app/file/browser postconditions; A user-facing repair choice protocol over the pendant

### "Use my pendant over its USB connection to the Mac right now, even when it has no LTE registration, with the same voice, action, and confirmation flow and no special setup from me."
- **useful because:** The hardware is physically present on USB but absent from the relay's LTE device table. A Mac-tethered mode makes the wearable useful today in the owner's home and provides a deterministic development/fallback path instead of treating an unregistered radio as a dead product.
- **path:** pendant → mac-planner → mac-terminal → relay-realtime → faculty-action → faculty-perception
- **model tier:** Relay remains the policy and conversation authority; a small Mac USB transport daemon handles framed serial packets and reconnects; use the existing realtime voice tier only for conversation and cheaper background workers for queue reconciliation and telemetry.
- **latency:** Button-to-ack under 150 ms locally; voice/audio can follow the existing 24 kHz path. Reconnect after cable loss within 2 seconds, with explicit offline/connected indication.
- **cost:** Negligible API cost while tethered beyond normal voice turns; one lightweight local process and serial framing. No cloud audio copy unless the existing relay path is used.
- **security:** Pair the USB device by hardware identity and rotating challenge, not by a tty path alone. Do not expose serial control to arbitrary local processes. Preserve the existing physical confirmation latch; USB transport must carry intents and receipts, never bypass approval. Cable removal must fail closed.
- **missing:** A Mac serial transport service for /dev/cu.usbmodem00096003658* and the ESP32 bridge /dev/cu.usbserial-0287A9CA; Pendant pairing/identity handshake and reconnect state machine; A relay routing mode that treats the tether as the active device while LTE is absent; End-to-end USB audio/voice framing test and user-visible tether status

### "Treat a multi-app request as one transaction: prepare every change, show me one concise impact summary, commit only when all required preconditions hold, and automatically roll back every reversible part if a later step cannot be completed."
- **useful because:** The owner should be able to say “move this project, update its calendar event, and notify the team” without ending up in a half-finished state spread across Finder, Calendar, and Messages. Today the action surfaces execute individual steps and can verify them, but they do not provide a cross-surface all-or-nothing boundary.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-judgement → faculty-perception → faculty-action
- **model tier:** Use a cheap planner to construct a dependency graph and deterministic preflight; use realtime only for the spoken request and final confirmation; use faculty-action for execution and faculty-perception for independent postconditions. A slower model may synthesize the impact summary but must not be the commit authority.
- **latency:** Impact summary within 5 seconds; commit within 15 seconds for ordinary Mac/browser operations. If rollback or verification exceeds the deadline, freeze and report partial/unknown rather than continuing.
- **cost:** Approximately $0.02–$0.15 per bundle, dominated by browser/app inspection and any visual ambiguity; preflight and hashes should be cheap.
- **security:** The transaction manifest must contain references and redacted summaries, not message bodies or credentials. Sending, deleting, publishing, or purchasing remains gated by the existing physical approval latch. Rollback is never allowed to erase unrelated owner changes made concurrently.
- **missing:** A cross-surface transaction coordinator with dependency graph, prepare/commit/abort phases, and leases; Per-action compensators that are explicit about reversible, irreversible, and non-compensable effects; Conflict detection using fresh pre-state hashes immediately before commit; A user-visible impact summary and partial-state receipt over the pendant

### "Let me give an action a temporary scope—only these files, apps, sites, and accounts—and have the agent refuse every step outside that boundary, even if the planner later interprets my request broadly."
- **useful because:** The owner gets a practical blast-radius limit for powerful automation. A mistaken planner, stale browser tab, or injected page instruction cannot turn a narrow request into unrelated edits or messages.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → mac-vision → browser-extension → faculty-judgement → faculty-action
- **model tier:** Parse the scope once with the ordinary planner, enforce it deterministically in the Mac/browser action broker, and use realtime only to explain a refusal or ask for an explicit scope extension.
- **latency:** No perceptible delay for allowed steps; an out-of-scope attempt must be blocked before execution and explained within 1 second.
- **cost:** Very low after scope compilation; a small planner cost when the owner creates or changes a scope.
- **security:** Scope tokens must be capability-scoped, expiring, and bound to the operation and account/site identifiers. Never infer permission from a page's text. Scope extension requires a fresh owner gesture for high-risk actions.
- **missing:** A canonical scope language covering paths, bundle IDs, browser origins/accounts, and action verbs; Pre-execution enforcement in every executor, including AppleScript and browser commands; A pendant-visible scope summary and expiration indicator


## Changes it proposed to its own stack

### `model-routing` — Make action completion a two-stage commit: deterministic state/hash verification after every mutation, then invoke vision or a language model only when the deterministic check is inconclusive or mismatched. Store executor receipt and verifier receipt separately and expose a three-valued result (verified, failed, unknown).
- **owner gets:** The owner gets faster, cheaper, and more honest results: routine reminders, files, and app state complete without an expensive model, while visual ambiguity is escalated instead of being silently accepted.
- effort: Medium: add verifier dispatch and receipt schema to the existing action ledger/job pipeline; define deterministic locators for common app/file/browser states; add tests for stale state and timeout.  ·  risk: A bad locator can report unknown more often; recover by surfacing the exact locator and offering a fresh inspection, never by retrying the mutation. Schema migration must preserve existing job receipts.
- cost: Usually reduces model calls; small storage increase for per-step hashes and provenance. Vision escalation remains the dominant cost.  ·  latency: Adds tens of milliseconds for deterministic checks; avoids multi-second vision calls on clear cases. Ambiguous cases are slower but safer.
- security: Improves least-privilege evidence: hash-only verification by default, snippets only when needed and sensitivity-filtered. No new secret access.
- depends on: Wire verify_operation_step into POST /execute commit flow; Add operation_id/step_id to actionLedger and job receipts; Define deterministic postcondition locators for app/file/browser actions

### `integration` — Add a capability-scoped action broker between planners and all Mac/browser executors. It mints an expiring operation token containing allowed resource selectors and verbs, rejects non-matching calls before they reach AppleScript, shell intents, or the browser extension, and emits a refusal receipt with the exact violated selector.
- **owner gets:** A narrow spoken request stays narrow in practice, protecting the owner's files, accounts, and conversations from planner mistakes and hostile instructions encountered in a webpage.
- effort: Medium-high: define selectors, retrofit every executor, test path normalization and browser-origin/account binding, and expose scope summaries in the conversation layer.  ·  risk: Overly strict selectors can block legitimate work; recover through an explicit, user-visible scope amendment rather than silent widening. Path aliases, redirects, and multi-account browsers need careful handling.
- cost: Small local CPU/storage overhead; negligible API cost.  ·  latency: A deterministic authorization check per action, typically milliseconds.
- security: Strongly positive: least privilege and fail-closed enforcement. Tokens must not contain secrets and should expire quickly.
- depends on: Canonical scope language; Executor-wide enforcement hook; Owner confirmation policy for scope amendments


## What it asked for

_Nothing._
## Its own summary

Recorded three capabilities and one implementation change. The strongest is verified cross-surface execution: execute Mac/browser steps, independently verify fresh postconditions, and report verified/failed/unknown rather than trusting executor receipts. Also recorded partial-success repair checkpoints and a Mac-tethered pendant mode, plus two-stage deterministic-first verification routing. Fresh snapshot: Mac agent is ready, Accessibility and Screen Recording are now granted, Safari bridge is online with 9 tabs and no pending commands, and relay is reachable. The pendant itself is still absent from the relay device table despite the stated USB connection, so the most valuable immediate work is the USB transport/pairing path.

**Biggest unknown:** Whether the connected nRF9160 and ESP32 serial devices can be opened by the Mac agent today, and what exact pendant firmware framing/pairing protocol they speak. I still need a real serial diagnostic/transport surface (read-only first), the pendant identity/handshake details, and the owner's policy table for which action classes may run proactively versus require approval.

