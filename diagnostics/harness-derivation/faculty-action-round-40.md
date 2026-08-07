# Harness derivation — faculty-action — round 40

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **action-readiness** — Mac local agent is reachable and full-control mode is enabled, but execution is not ready for GUI/browser work: Accessibility and Screen Recording are both untrusted, browser bridge is offline with 3 pending commands, and computer-use loop is disabled. Relay and Mac bridge are reachable.
  - evidence: GET /ops/status at 2026-08-07T10:55Z: permissions.accessibility.trusted=false, screenRecording.granted=false, browserExtension.online=false/pendingCommands=3, computerUse.loopEnabled=false, relay.macBridgeOnline=true.

## Capabilities it proposed

### "When I approve a multi-step task that spans my Mac and logged-in websites, carry it out as one staged transaction: prepare everything, show me the exact combined effects, commit each step in dependency order, and if a later step fails, automatically undo every earlier reversible step and tell me precisely what could not be rolled back."
- **useful because:** Today an action can succeed on one surface and fail on another, leaving half-finished bookings, messages, files, or settings for the owner to repair manually. This gives them one understandable approval and a reliable all-or-nothing attempt across the devices that actually hold the needed access.
- **path:** faculty-judgement → faculty-perception → faculty-action → pendant → relay-realtime → mac-planner → mac-vision → browser-extension
- **model tier:** Use a cheaper background planner for dependency analysis, field normalization, and compensation planning; use realtime only to speak the combined preview, request approval, and report the final receipt. Deterministic executors and browser/Mac harnesses perform the actual steps.
- **latency:** Preparation may take 5–20 seconds depending on authenticated pages. After approval, commit each step with visible progress; target under 2 seconds between steps and fail closed on stale state, expired sessions, or missing proof.
- **cost:** Approximately $0.01–$0.08 per task depending on page count and whether vision is needed; dominant costs are authenticated page reads/screenshots and any vision/computer-use turns, not the small orchestration model.
- **security:** The relay must carry opaque job IDs and approval tokens, not page secrets. A single-use approval token must bind to the complete plan fingerprint, ordered steps, recipients, amounts, and target accounts. Never compensate an irreversible external action by inventing a second external action; mark it unrecoverable and stop. Require explicit confirmation for financial, legal, deletion, or message-send effects.
- **missing:** A cross-surface two-phase job coordinator with durable prepare/commit/abort states and dependency edges; A shared typed effect ledger so Mac and browser steps expose compatible before/after state and compensation handlers; Browser executor support for transactional checkpoints, idempotency, and compensation receipts; A relay-delivered pendant approval UI that speaks a compact combined diff and binds approval to the plan fingerprint; A recovery worker that resumes or aborts disconnected jobs without replaying committed step IDs; An owner-facing dashboard showing the aggregate transaction, partial failures, and per-step undoability


## Changes it proposed to its own stack

### `mac-harness` — Extend the implemented action-receipt system with a provenance-aware stale-plan precommit gate. For every irreversible or externally visible step, persist draft provenance (source URL/tab or file/app, extraction timestamp, normalized field/value hashes, and plan fingerprint). Immediately before execution, faculty-action asks faculty-perception to re-read only those sources; compare fingerprints and required fields. If any source is unavailable or changed, pause the job, mark the step stale, retain the draft and evidence, and send the owner a one-sentence delta plus an approve/rebuild choice. Only an explicit approval on the unchanged fingerprint may pass the gate; receipts record the checked sources, comparison result, and approval token. Keep reversible local actions executable without the gate, and make paused jobs resumable without replaying completed action IDs.
- **owner gets:** A prepared email, form, purchase, or settings change will not silently use yesterday's price, recipient, appointment time, or page state. The owner gets a concise explanation and can approve the exact unchanged transaction or have it rebuilt.
- effort: Medium: typed provenance schema and persistence, precommit hook in executor, perception refresh RPC, pause/resume job states, dashboard/pendant prompt, and tests for changed/unavailable sources and retry idempotency.  ·  risk: A flaky source could pause a legitimate action; fail closed and offer rebuild. Never send the original draft after a mismatch. Recovery is resume after explicit approval or discard the paused job; completed reversible steps remain undoable via existing receipts.
- cost: Small extra storage and one bounded perception/read request per gated step; use a cheaper text model for fingerprint comparison and reserve realtime only for the spoken alert.  ·  latency: Adds roughly one source-read round trip (typically 1–3 seconds) only immediately before irreversible/external actions; no impact on read-only or reversible steps.
- security: Provenance stores hashes and minimal snippets rather than full private page contents; source access remains in the existing authenticated browser/Mac boundary. Approval tokens are single-use and bound to job, step, and fingerprint.
- depends on: faculty-judgement emits durable draft provenance and requests the gate; faculty-perception supports targeted re-read with source identity and freshness; job state machine supports paused/stale/resume states; existing actionReceipts.js and undo.js remain the receipt/compensation layer


## What it asked for

_Nothing._
## Its own summary

Discovered current action readiness and proposed a new stale-plan precommit gate layered onto the implemented action receipts: targeted source reread, fingerprint comparison, fail-closed pause on drift/unavailability, explicit approval bound to the unchanged step, and idempotent resume. Reported the design to faculty-judgement and recorded live blockers: Accessibility and Screen Recording are not granted, browser bridge is offline with three pending commands, and computer-use loop is disabled although relay/Mac bridge are reachable.

**Biggest unknown:** Whether the orchestrator will implement the provenance/precommit state-machine hooks and enable the missing Mac/browser permissions; without those, I can receipt actions but cannot safely execute private GUI/browser transactions.

