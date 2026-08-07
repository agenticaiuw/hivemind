# Harness derivation — faculty-action — round 90

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **execution readiness** — Mac bridge and relay are reachable, but agent ready=false because Accessibility and Screen Recording are not granted; browser bridge is offline with 9 pending commands. AppleScript/automation grants are present. Existing jobs emit receipts and undo metadata, but browser failures can consume ~45 seconds before reporting timeout.
  - evidence: GET /ops/status 200; GET /browser/status 200; GET /jobs 200

## Capabilities it proposed

### "Start this job now, but make it safe if I disconnect: pause before any irreversible step, tell me exactly what completed, and resume only after reconciling the Mac/browser state when I return."
- **useful because:** Today a multi-surface task can be queued or acted on, but a dropped pendant link can leave uncertain partial work. This gives the owner one reliable contract for unattended execution: bounded progress, an explicit pause point, and no duplicate actions after reconnection.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use realtime only to capture the request and speak status; use a cheaper background planner/worker for the job, with the local Mac planner for execution and relay for durable orchestration.
- **latency:** Acknowledge and issue a signed fence within 1 second; status updates within 5 seconds of each step; reconnect reconciliation can take 10–30 seconds before resuming.
- **cost:** Low per job when the background tier handles planning; dominant costs are browser/Mac execution and any screenshots or page extraction, not the fence metadata.
- **security:** Departure packets may contain private URLs, account context, and action parameters, so encrypt at rest and minimize projections. Never transmit credentials. Require explicit owner confirmation for irreversible actions; a pendant pause or expired lease must stop workers before that boundary.
- **missing:** A durable execution-fence/lease service shared by relay, Mac worker, browser bridge, and pendant; Signed pause/resume control and an offline-visible pendant fence indicator; A typed reconciliation endpoint that compares preconditions/state hashes with receipts before replay; Dashboard rendering for packet timeline, checkpoint, pending approval, and undo handles

### "Prepare the real-world change on my Mac or in my logged-in browser, then send me a compact exact summary on the pendant so I can approve that specific change from wherever I am; apply it only if the approved summary still matches, otherwise stop."
- **useful because:** The owner can currently approve work through a dashboard or a live conversation, but cannot safely approve a prepared browser/Mac transaction while away from the computer. This gives them a portable, human-readable commitment check: approve the exact recipient, amount, text, or file change—not a vague job—and prevents stale approvals from being applied.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use the realtime tier only to explain the pending change and capture a short confirmation; use a cheaper background planner and local Mac/browser workers to prepare and validate the transaction.
- **latency:** Preparation may take seconds to minutes; pendant approval delivery should be under 2 seconds when connected. Applying an approved transaction should begin within 5 seconds, after a fresh state check.
- **cost:** Low metadata and speech cost per approval. The dominant cost is preparing private-page evidence or screenshots, which should happen once and be cached by transaction digest.
- **security:** The approval must be cryptographically bound to a normalized action digest, target account/session, expiry, and precondition snapshot. Do not read secrets aloud; redact sensitive fields while preserving enough detail to identify the change. Reject replay, changed amounts/recipients, expired approvals, and approvals from an unpaired pendant. Irreversible actions still require explicit confirmation.
- **missing:** A transaction-preparation record that freezes the exact normalized mutation and evidence capsule; A relay-signed approval token bound to that digest, owner identity, expiry, and target session; Pendant rendering/input for a short redacted summary plus approve/reject buttons, including disconnected retry semantics; Worker-side compare-and-swap validation immediately before the external mutation


## Changes it proposed to its own stack

### `integration` — Implement a cross-surface Execution Envelope and fence coordinator. Every delegated job gets a compact signed envelope: job/thread id, monotonic checkpoint, target surface, preconditions/state hashes, idempotency key, reversible/undo handle, expiry, approval boundary, and receipt schema. Relay persists it and owns lease expiry; Mac/browser workers must validate the lease before each step and emit typed receipts. A pendant button/event or disconnect policy writes a signed pause fence; workers stop at the next safe boundary. Resume first runs reconciliation against current Mac/browser state and receipts, then advances only uncompleted idempotency keys. Dashboard and spoken status render the same envelope rather than inventing per-surface status.
- **owner gets:** If the owner walks away or the link drops during a real task, it will stop safely and later continue without guessing or duplicating clicks, messages, or purchases. They can see one trustworthy timeline of what happened and what still needs approval.
- effort: Medium-high: shared schema, relay durable storage, worker middleware in Mac/browser bridges, pendant event plumbing, reconciliation tests, and dashboard/status rendering.  ·  risk: A false pause or stale state hash could leave work unfinished; recover by preserving receipts, exposing manual resume, and allowing a fresh plan after lease expiry. A protocol bug must fail closed before irreversible steps.
- cost: Negligible storage/CPU for envelopes and receipts; background reconciliation is cheap. Occasional screenshot/page extraction remains the dominant API cost.  ·  latency: Sub-millisecond local fence checks; typically 1–5 seconds added on resume for state reconciliation, longer only when browser inspection is required.
- security: Improves security by binding actions to a signed, expiring lease and explicit approval boundary. Encrypt envelopes/receipts, redact secrets and page contents, and prevent workers from accepting unsigned or cross-job replayed commands.
- depends on: Durable job runner and browser command queue must expose stable job ids and idempotency keys; Pendant must expose a pause/fence event and local indicator; currently no pendant is connected; A typed state-inspection/reconciliation operation for Mac and browser workers; Owner confirmation policy for irreversible actions

### `interaction` — Add a portable approval-token protocol for prepared external mutations. The planner creates a canonical redacted transaction digest plus evidence capsule and precondition snapshot; relay signs a short-lived token addressed to the paired pendant and target browser/Mac session. The pendant displays a bounded summary and offers approve/reject; approval can be queued offline but is accepted only once relay verifies pairing, expiry, nonce, and digest. Immediately before execution, the worker performs compare-and-swap against the snapshot and refuses any changed recipient, amount, destination, text, or account. Record the digest and approval in the receipt so the owner can prove exactly what they authorized.
- **owner gets:** They can approve a carefully prepared real-world change from the pendant without being at the Mac, while stale pages, changed prices, altered recipients, or replayed approvals cannot silently turn into a different action.
- effort: Medium: canonical mutation normalization, evidence capsule storage, signed token verification in relay and workers, pendant UI/input, and compare-and-swap adapters for browser and Mac actions.  ·  risk: Over-redaction could make a summary ambiguous; fail closed and ask for a fresh preparation. Clock skew or a lost connection could delay approval; use relay-issued monotonic expiry and retain the pending transaction. Never treat a spoken 'yes' without the matching digest as authorization.
- cost: Small relay storage/signature overhead; no additional model call for approval. Evidence capture and private-page extraction remain the main cost.  ·  latency: Usually adds under 2 seconds for token delivery and one state verification before execution; changed state intentionally causes a re-preparation delay.
- security: Reduces confused-deputy and replay risk by binding approval to exact content, session, nonce, and expiry. Requires encrypted evidence capsules, paired-device authentication, redaction, and audit retention controls.
- depends on: A normalized transaction/evidence representation across Mac and browser action types; Paired-pendant identity and reliable relay delivery; Worker compare-and-swap hooks before irreversible effects; Pendant-side approve/reject interaction and offline queue


## What it asked for

_Nothing._
