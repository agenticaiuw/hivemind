# Harness derivation — mac-planner — round 104

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Start this multi-step task and keep it safe if the browser, Mac, or connection drops—resume where you left off and tell me exactly what completed, what did not, and what needs me.”"
- **useful because:** Today a task can leave partial Mac mutations, stale browser commands, and a relay job with no single truth. A cross-surface transaction would make long tasks trustworthy: the relay coordinates checkpoints, the Mac records durable receipts, the browser contributes tab-scoped evidence, and the pendant gives a compact status/resume control even after disconnection.
- **path:** relay-realtime → mac-planner → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use the cheaper background model for checkpoint reconciliation and retry planning; reserve realtime for the owner's spoken request and a short exception/resume conversation.
- **latency:** Acknowledge in under 2 seconds; checkpoint updates within 5 seconds of each action; retries can run in the background. Never block the owner waiting for a whole workflow.
- **cost:** Roughly 1–3 background model calls per failed or resumed task; normal successful steps use typed receipts and no model call. Dominant cost is only reconciliation of ambiguous outcomes.
- **security:** The coordinator must never replay a non-idempotent browser submit or Mac mutation merely because a receipt is missing. Persist a step idempotency key, precondition/evidence hash, and outcome (completed/unknown/skipped); quarantine unknown steps for review. Private URLs, snippets, and action receipts leave the Mac only when needed for the relay's task record; redact by default. Pendant resume/status should reveal only task labels, not page contents. Existing maximum-access policy means this is observability and safe replay—not a new approval gate.
- **missing:** A durable cross-surface saga/job schema with step IDs, idempotency keys, preconditions, evidence hashes, and explicit unknown outcomes; A relay coordinator that leases work to Mac/browser and reconciles receipts after reconnect; A pendant status/resume command and offline-safe cancellation marker; Browser stale-command quarantine and a Mac-to-relay receipt acknowledgement protocol

### "“Prepare this for me, but make the approval expire if anything important changes—tell me exactly what changed instead of letting stale work go through.”"
- **useful because:** The owner can get drafts and prepared actions, but today a prepared artifact can become stale while it sits in a browser tab, Mac job queue, or relay overnight. This capability turns preparation into time-bounded escrow: the relay records the relevant facts, the browser and Mac re-check them immediately before the final action, and the pendant reports a concise change alert. A stale approval cannot silently authorize a different price, recipient, appointment, or document.
- **path:** relay-realtime → browser-extension → mac-planner → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a low-cost background model to identify which fields are approval-critical and compare before/after evidence; use realtime only to tell the owner what changed and ask whether to regenerate the preparation.
- **latency:** Preparation can be asynchronous. The final freshness check should complete within 3–5 seconds; if it fails, stop and notify rather than retrying blindly.
- **cost:** Usually no model call for typed field comparisons; approximately one inexpensive background call only when page structure or semantics changed. Storage is a small snapshot of redacted critical fields and hashes per escrow.
- **security:** Never retain full private pages or message bodies when hashes and selected fields suffice. Scope each escrow to a specific account, tab/session, file, recipient, and expiry. A changed critical field invalidates the escrow; a harmless volatile field should not. Final mutation remains impossible from an expired token, even if an old browser command or Mac job is replayed.
- **missing:** A cross-surface escrow record with expiry, critical-field allowlist, source identity, and approval nonce; Browser and Mac preflight endpoints that return typed before/after evidence against the escrow; Relay enforcement that rejects expired or invalidated non-idempotent actions; Pendant notification/control for approve, regenerate, or abandon


## Changes it proposed to its own stack

### `relay` — Add a lease-and-checkpoint coordinator between the existing relay jobs, Mac /plan+/execute, and browser command queue. Each workflow step gets a stable stepId and lease expiry; the Mac and browser must acknowledge the same stepId with a typed receipt or explicit unknown result. On reconnect, reconcile receipts before issuing any new command, quarantine the seven currently pending browser commands if their device epoch is stale, and expose a compact causal timeline to /jobs/:jobId/receipts. This is wiring and failure semantics between existing components, not another generic durable job runner.
- **owner gets:** A dropped Wi‑Fi link or sleeping browser would no longer make the owner wonder whether something happened twice. They get one truthful timeline and safe continuation from the last confirmed step, while stale browser commands cannot unexpectedly execute after reconnect.
- effort: Medium-high: shared schema, relay state transitions, Mac acknowledgement hook, browser device-epoch handling, migration/tests for existing jobs.  ·  risk: A too-short lease can mark a slow action unknown and pause work unnecessarily; a too-long lease delays recovery. Recover by explicit unknown state and manual resume. Existing FULL_CONTROL_MODE remains unchanged; this adds receipts and quarantine, not a confirmation gate.
- cost: Negligible API cost on successful steps; small D1 storage increase for step receipts and hashes. Background reconciliation may use an inexpensive model only for ambiguous failures.  ·  latency: One local receipt write per step; reconnect recovery adds a few seconds to reconcile before resuming.
- security: Store hashes and redacted metadata rather than page bodies by default. Do not replay unknown mutating steps without an owner-directed resume. Device epochs prevent old browser sessions from consuming new commands.
- depends on: Browser extension reconnect heartbeat/device epoch; Mac executor emitting durable step acknowledgements; Relay job schema that supports per-step state and idempotency keys

### `integration` — Introduce a single-use, expiring approval nonce bound to a redacted critical-field snapshot and source identities (browser tab/session or Mac file/app). Before any final browser or Mac mutation, the executor must re-read those fields and atomically consume the nonce; any mismatch, stale device epoch, or expiry changes the result to invalidated rather than executing. Relay receipts should record invalidated, regenerated, and consumed states so an old queued command cannot revive.
- **owner gets:** Prepared work stays trustworthy while the owner is away. They will never approve yesterday's form, an old price, or a changed recipient by accident, and they get a clear explanation when regeneration is needed.
- effort: Medium: shared escrow schema, atomic relay check, small Mac/browser preflight adapters, and migration tests for queued commands.  ·  risk: Overly broad critical-field selection could invalidate harmless changes and annoy the owner; recover by showing the changed fields and offering regenerate. A relay outage should fail closed for final mutations but preserve the draft locally for later.
- cost: Minimal storage and one extra typed preflight per final action; no additional realtime-model usage in the normal path.  ·  latency: Adds roughly one network round trip (target under 3 seconds) immediately before the final mutation.
- security: Improves replay resistance and limits authorization to the exact artifact and context the owner reviewed. Redacted snapshots reduce private-data exposure; nonce consumption must be atomic and never logged with secret contents.
- depends on: A shared escrow/approval record across relay, Mac, and browser; Typed critical-field extraction from each source; Final-action adapters that can reject an invalid nonce


## What it asked for

_Nothing._
## Its own summary

I found the Mac bridge and relay online, but the browser extension is still offline with 7 pending commands, and the Mac remains Accessibility=false, Screen Recording=false, and computer-use loop disabled. I proposed a new concrete relay change: a lease/checkpoint coordinator that connects existing /plan, /execute, job receipts, and browser commands with stable step IDs, device epochs, stale-command quarantine, and explicit unknown outcomes. This enables safe resume after disconnects without adding an approval gate. What is still needed to make it real is implementation of the cross-surface step schema/ack protocol, a browser reconnect heartbeat, and Mac receipt emission. From the owner, the only practical unblock is reconnecting the browser extension; Accessibility/Screen Recording remain optional manual macOS settings and are not required for the receipt-based path.

**Biggest unknown:** Whether the existing Mac executor and browser bridge can emit durable per-step acknowledgements without modifying their current job schemas; this determines whether the coordinator is a small wiring change or needs a migration.

