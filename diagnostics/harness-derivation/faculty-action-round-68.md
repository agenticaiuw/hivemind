# Harness derivation — faculty-action — round 68

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Carry out this decision everywhere it applies, and tell me exactly what changed.” For example: update the calendar event, send the approved browser reply, and save the final document on my Mac as one coordinated operation."
- **useful because:** Today judgement can decide a multi-surface outcome, but action tools are isolated 1–3-step calls. This gives the owner one dependable handoff: preflight all targets, execute only the approved changes, detect partial failure, and report a single truthful result instead of implying that a bundle succeeded when one surface did not.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → unified → faculty-judgement → faculty-action
- **model tier:** A cheap background execution planner compiles the already-decided intent into typed steps; relay-realtime is used only for a short spoken approval or exception prompt. No expensive reasoning call is needed per step.
- **latency:** Preflight and first reversible steps within 2–5 seconds when Mac/browser are online; long work continues as a durable job. A partial-failure or approval exception should be spoken within 1 second of detection, with the job resumable later.
- **cost:** Roughly one cheap planner invocation plus existing Mac/browser/relay calls; about $0.01–$0.05 per bundle depending on browser extraction and retries. The dominant cost is context and screenshots, so send typed step inputs and compact receipts rather than full transcripts.
- **security:** Never widen approval from one target to another. Bind an approval token to an intent hash, target account/session, exact fields, and expiry; re-check preconditions immediately before each irreversible step. Do not transmit private page contents to the relay unless required. Store redacted before/after evidence and provide undo only where a compensating action is safe. If a step is irreversible or a session changes, pause and ask again.
- **missing:** A first-class bundle/transaction route with typed preconditions, idempotency keys, dependency ordering, and compensation metadata; An approval token bound to the exact compiled bundle and a pendant-visible pending/committed state (the requested physical confirmation and action-lease skills would provide the local UX); Per-step verification and proof tools so success means observed postcondition, not merely queued executor work; A durable runner that can resume a bundle and distinguish skipped, applied, failed, and compensated steps

### "“If the app or website changes while you’re doing it, recover and finish the approved task without making me start over.”"
- **useful because:** Today an approved action can fail when a tab reloads, a form changes, a Mac app presents a different dialog, or a session expires; the owner must repeat the whole task or manually take over. The mind should preserve the approved goal, re-observe the changed world, and repair only the affected step—without silently broadening what it is allowed to do.
- **path:** pendant → relay-realtime → faculty-perception → faculty-judgement → faculty-action → browser-extension → mac-vision → mac-terminal → mac-planner
- **model tier:** Use a cheap local recovery model for classifying executor errors and proposing bounded repairs. Escalate to the expensive realtime model only when the repair changes the approved effect, encounters an unfamiliar security prompt, or needs a spoken decision.
- **latency:** Attempt recovery within 2–4 seconds after a recoverable mismatch; continue as a durable background job if the page/app is slow. Ask the owner promptly only for scope, identity, payment, or security changes.
- **cost:** Usually one small recovery inference and a fresh compact observation; roughly $0.005–$0.03 per recovery. Screenshots and repeated page context dominate cost, so retain structured locators and hashes rather than replaying full transcripts.
- **security:** A changed interface must not become permission to do a different thing. Keep an immutable approved effect envelope (account, recipient, amount, destination, content hash, and allowed mutations); require renewed approval if any envelope field changes. Treat MFA, CAPTCHA, payment, deletion, and external-send prompts as hard stops. Redact observations before relay logging.
- **missing:** An executor error taxonomy distinguishing stale locator, transient transport failure, session expiry, changed content, and scope change; A perception-to-action repair loop that can re-observe the affected app/tab and generate a bounded replacement step; An effect-envelope and approval-scope verifier shared by Mac and browser executors; Structured post-action verifiers that prove the intended state after repair, rather than trusting a click/type acknowledgement


## Changes it proposed to its own stack

### `relay` — Add a durable ActionBundle coordinator between faculty-judgement and the existing executors. It accepts an intent hash plus typed steps (surface, target/session, preconditions, irreversible flag, idempotency key, verifier, and optional compensator), persists a state machine (planned → approved → preflighted → applied/verified or compensated/blocked), dispatches existing Mac/browser actions, and emits one signed receipt containing each step's observed before/after evidence. Resume must never replay a verified idempotent step; any changed target/session invalidates approval.
- **owner gets:** The owner can ask for one outcome spanning their Mac and logged-in browser without manually supervising each handoff, while getting an honest answer when only half completed and a safe path to retry or undo the completed reversible parts.
- effort: Medium-high: coordinator schema and worker, adapters around existing job/browser result records, verifier hooks, approval-token binding, and dashboard/pendant status rendering. Start with reversible AppleScript and browser field edits, then add irreversible steps.  ·  risk: A coordinator could accidentally duplicate sends or apply a stale decision. Mitigate with intent/target hashes, idempotency keys, expiry, preflight checks, explicit commit gates, and treating unknown executor outcomes as blocked rather than retrying. Recover by resuming from the ledger or invoking compensators; retain raw executor receipts for audit.
- cost: Small D1/R2 storage and queue overhead; one cheap orchestration call per bundle and no extra model call per step. Evidence storage should be redacted and retention-limited.  ·  latency: Adds roughly 100–300 ms for ledger transitions; execution remains parallel where dependencies permit. Long operations become durable instead of tying up the voice turn.
- security: Improves least-privilege and auditability, but approval tokens and private before/after evidence become sensitive. Encrypt or redact evidence, bind tokens to session/account and exact field values, and prevent relay logs from receiving page contents.
- depends on: A durable job runner (the existing browser runner backlog item is still only half-shipped); Per-step postcondition verification and action-proof tools (already requested but not granted); Pendant-local approval/lease indicator for offline or dropped-link safety (already requested but not granted)


## What it asked for

_Nothing._
## Its own summary

Discovered the live action surface: short typed Mac/browser batches, mac_delegate, durable job/status/receipt routes, and browser command results. Proposed a new owner-facing cross-surface “carry it out everywhere” capability and recorded the missing ActionBundle coordinator: immutable intent/approval binding, preflight, idempotent dispatch, postcondition verification, compensation, resume, and one truthful receipt. This is specifically the missing connective layer between existing primitives, not another browser watcher or form filler. Told faculty-judgement about the gap.

**Biggest unknown:** Whether the owner’s approval policy permits a bundle to contain multiple irreversible effects under one confirmation, or requires a separate confirmation per target/account. Still missing in this round: durable runner completion, per-step verification/proof, pendant-local approval/lease UX, and the owner’s exact timezone/action priorities. Accessibility and Screen Recording remain owner-granted blockers; AppleScript/browser routes are the viable fallback.

