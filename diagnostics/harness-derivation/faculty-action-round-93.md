# Harness derivation — faculty-action — round 93

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **current execution blockers** — Mac bridge and Chrome extension are online, but no pendant device is reachable; computer-use loop is disabled, Accessibility and Screen Recording are ungranted, browser has 9 pending commands with no active tab, and recent browser navigation jobs timed out. Receipts/undo exist, but executor still has no precondition gate or approval-resume path.
  - evidence: GET /ops/status, GET /browser/status, GET /jobs live responses in Round 93

## Capabilities it proposed

### "“Start this on my Mac, and if it needs my approval while I’m away, ask me on the pendant; when I confirm, continue and tell me exactly what happened.”"
- **useful because:** Today a job can be planned, blocked on the Mac dashboard, or leave receipts, but the owner cannot safely bridge a mid-job approval from the wearable. This gives one cross-surface transaction: the pendant starts it, the Mac/browser performs it, the relay holds durable state, and a spoken/button confirmation resumes only the exact pending step. The owner can walk away without losing the job or approving a different action than the one previewed.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use realtime only for the short spoken approval prompt and response; use the cheaper background/local planner for decomposition, evidence comparison, and final receipt narration.
- **latency:** Initial acknowledgement under 1 s; approval prompt as soon as a gate is reached (target under 2 s); resume within 3 s of confirmation; background work may run for minutes while the owner is away.
- **cost:** Roughly one realtime turn for the approval exchange plus local/background planner calls; <$0.03 typical excluding any browser/model work. Dominant cost is repeated evidence/context if the job is re-planned rather than resumed.
- **security:** The relay must send only a redacted preview and action hash, never page secrets. Confirmation is single-use, expires (for example 10 minutes), is bound to jobId/actionId/target tab and precondition hash, and cannot authorize a changed action. Require explicit spoken yes or pendant button gesture for irreversible writes/sends; record the confirmation and before/after evidence in the receipt. If the bridge disconnects, hold rather than execute.
- **missing:** Durable cross-surface approval envelopes with action-hash binding and expiry; A relay-to-pendant notification/confirmation transport and a resume endpoint on the Mac executor; A true precondition gate (the current receipt/undo implementation observes pre-state but explicitly does not refuse or pause); A unified job state machine that survives Mac/browser/relay disconnects and correlates the final receipt to the spoken prompt

### "“If this task gets stuck while I’m away, follow my fallback rules: save a draft, notify me, or cancel—whichever I specified—and never leave a half-finished change.”"
- **useful because:** The owner cannot currently express what should happen when a Mac or browser action loses its tab, hits a dialog, times out, or waits for approval. Jobs simply fail or remain pending. A bounded contingency policy would let work continue safely without pretending that a timeout is success: preserve a draft or checkpoint, notify through the relay/pendant, and choose an explicitly authorized safe exit when the owner is unreachable.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use a cheaper background/local model to classify the failure against the owner’s predeclared policy and prepare the checkpoint; use realtime only to announce an urgent exception or request an override.
- **latency:** Classify and checkpoint within 2 seconds of a failure; notify the pendant promptly; policy execution within 5 seconds. No model call is needed for deterministic timeout, cancel, or save-draft branches.
- **cost:** Usually <$0.01 per incident; most branches are deterministic. Cost is dominated by optional summarization of the saved checkpoint, not policy evaluation.
- **security:** Policies must be explicit, scoped by app/site/action type, and deny-by-default. Never auto-send, purchase, delete, or publish. Store only a redacted checkpoint and action metadata in the relay; keep private page contents on the Mac/browser. Every fallback must produce a receipt and be reversible where possible.
- **missing:** A declarative contingency-policy format with allowed fallback effects and expiry; Failure classification that distinguishes timeout, changed precondition, lost browser tab, permission block, and partial completion; Atomic checkpoint/fallback primitives spanning Mac files, browser drafts, relay notifications, and receipts; A policy simulator/preview so the owner can test what would happen before enabling it


## Changes it proposed to its own stack

### `integration` — Implement a resumable cross-surface approval envelope and job state machine between the existing planner/executor, browser queue, pipeline, and receipts. When an action reaches a declared gate, persist {jobId, actionId, target surface/tab, redacted preview, precondition hash, effect class, expiry, nonce}; emit a pipeline event and pendant prompt. Accept exactly one authenticated confirmation carrying the nonce, re-check the precondition, then resume the same actionId (never re-plan or replay completed IDs). On mismatch/expiry/disconnect, transition to held and require a fresh preview. Append the prompt, confirmation, re-check, and final receipt to the existing job and pipeline records.
- **owner gets:** The owner can leave the Mac and still safely finish a real browser or desktop task from the pendant, without a stale dashboard approval silently authorizing changed content. Jobs become recoverable rather than abandoned when a bridge or browser session drops.
- effort: Medium-high: shared state schema and migration, relay event/confirmation route, Mac executor gate/resume handling, browser command correlation, pendant UI/firmware event support, and end-to-end disconnect/replay tests.  ·  risk: A bug could resume the wrong action or duplicate a send. Mitigate with single-use nonces, action hashes, idempotent action IDs, expiry, precondition re-check, explicit irreversible confirmation, and default hold on uncertainty. Recovery is cancel/undo where available; otherwise preserve the held envelope and receipt for review.
- cost: Small durable relay storage and a few pipeline events per gated action; one short realtime prompt. No continuous model cost while held.  ·  latency: Adds approximately 100–500 ms for persistence and precondition re-check; resume target under 3 s after pendant confirmation.
- security: Improves security by constraining approval to an exact redacted action and tab/session, but introduces a sensitive confirmation channel. Use bearer-authenticated device identity, nonce replay protection, encrypted transport, and avoid storing page contents in the envelope.
- depends on: A real precondition gate in the executor (the current actionReceipts implementation records receipts but explicitly does not gate); Pendant online event/confirmation transport; otherwise dashboard-only fallback; Durable relay job runner and browser command correlation; Owner-defined confirmation policy for irreversible effects

### `integration` — Add a deterministic contingency-policy engine that runs after every failed, timed-out, or partially completed Mac/browser step. Policies are compiled into an allowlisted decision table before execution (for example: browser timeout → capture current URL/title and save local draft; permission failure → notify and hold; changed precondition → discard draft and request review; network loss → retry once then cancel). The engine must atomically checkpoint safe artifacts, emit a typed pipeline event, and attach the selected rule plus evidence to the existing receipt. It must never infer permission for a new side effect from a natural-language failure summary.
- **owner gets:** Tasks stop failing ambiguously while the owner is away. Their chosen safe fallback happens predictably, unfinished work is preserved as a draft or cleanly canceled, and the owner can understand exactly why the system stopped or changed course.
- effort: Medium: policy schema and validator, failure taxonomy, checkpoint adapters for local files/browser drafts/relay alerts, receipt and dashboard rendering, plus fault-injection tests for duplicate delivery and partial completion.  ·  risk: An overly broad rule could create or retain sensitive drafts, or misclassify a partial action. Mitigate with deny-by-default scopes, per-site/app limits, expiration, dry-run simulation, immutable rule IDs in receipts, and a hold state whenever classification is uncertain. Recovery is cancel or existing undo.
- cost: Negligible storage and compute for deterministic rules; occasional background summarization only when the owner asks for a human-readable explanation.  ·  latency: Adds roughly 50–300 ms for policy lookup and checkpointing; network/browser recovery may take longer but is bounded by the selected rule.
- security: Reduces unsafe retries and silent partial changes. Checkpoints must be encrypted or local-only by default, with redaction before relay notification; policies cannot authorize sends, purchases, deletion, or publication.
- depends on: A durable job/event store shared by Mac, browser, and relay; Typed failure and partial-completion evidence from executors; Atomic local/browser checkpoint adapters; Dashboard and pendant notification delivery


## What it asked for

_Nothing._
