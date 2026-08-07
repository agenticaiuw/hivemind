# Harness derivation — mac-planner — round 67

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-bridge readiness** — Mac agent is online but not ready: Accessibility trusted=false and Screen Recording=false; browser extension is offline with 3 pending commands. FULL_CONTROL_MODE is enabled, so actions can run without confirmation, but GUI/browser actions are currently blocked by missing readiness.
  - evidence: GET /ops/status at 2026-08-07T11:08Z; GET /browser/status

## Capabilities it proposed

### "If you can't complete something because my Mac or browser is unavailable, tell me immediately on the pendant what is blocked, keep the request safely queued, and continue automatically when that device comes back—without repeating work or making me restate it."
- **useful because:** Today a browser command waits ~45 seconds and fails with no cross-surface recovery; the owner should get a concise spoken explanation, a durable pending intent, and a completion notice instead of silently losing the task.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background planner for queueing/retry and reconciliation; realtime only for the short spoken blocker/completion notification.
- **latency:** Readiness check under 1 second; spoken blocker within 2 seconds; retry on heartbeat with exponential backoff and a configurable expiry (default 24 hours).
- **cost:** About $0.001–$0.01 per queued job, dominated by one background planning/reconciliation call; heartbeat checks and receipts are local/relay logic.
- **security:** Queue only the user's explicit intent and minimum action parameters, encrypted at rest; never persist page contents or credentials. No retry after expiry, target/session identity change, or a reported high-impact mutation without re-planning; announce the exact target before any irreversible step.
- **missing:** A shared readiness/preflight contract for Mac Accessibility, Screen Recording, and browser-extension heartbeat; A durable intent state machine spanning relay and Mac jobs (blocked, queued, resumed, completed, expired, canceled) with idempotency keys; Pendant notification events for blocker, retry, and completion; A dashboard view showing dependency, last heartbeat, next retry, expiry, and receipt links

### "When I’m about to leave my Mac or Wi‑Fi, let me say “pack me for the day,” and give me a private offline day pack on the pendant: my next commitments, essential addresses/links, files I chose, and a short spoken summary that I can query while disconnected; sync any notes I make back to the Mac when I return."
- **useful because:** The pendant is the one surface that remains with the owner when the Mac, browser sessions, and relay are unreachable. Today information gathered on the Mac disappears at the moment the owner leaves it, so the owner cannot reliably act during travel, commutes, or dead zones.
- **path:** mac-bridge → browser → relay → pendant → dashboard
- **model tier:** Use a cheaper background model on the Mac to assemble and compress the pack; use the realtime model only for the owner’s live offline spoken queries after the pack is installed and for a brief sync-conflict conversation on return.
- **latency:** Build and verify the pack in under 60 seconds, transfer before disconnect, answer offline queries under 500 ms from local indexed content, and sync return notes within 10 seconds of reconnection.
- **cost:** Roughly $0.01–$0.05 per pack, dominated by summarization and optional TTS; local indexing, transfer, and offline lookup are negligible.
- **security:** The pack may contain calendar, travel, addresses, and selected private files, so require explicit item selection or a named profile, encrypt it with a device-bound key, show contents and expiry before transfer, support immediate remote revocation when online, and never include passwords, page session tokens, or unselected browser contents. Notes created offline must be treated as drafts until the owner resolves conflicts.
- **missing:** A pendant-side encrypted content store and bounded offline search/index runtime; A Mac-to-pendant pack compiler that can read approved Calendar/Mail/files/browser evidence and produce citations plus audio; A resumable authenticated transfer protocol with versioning, expiry, and remote revocation; Offline pendant query handling and an append-only outbound notes queue with conflict resolution; A clear owner-facing pack preview, deletion control, and storage-budget telemetry


## Changes it proposed to its own stack

### `integration` — Add a cross-surface readiness broker and intent handoff protocol. Before dispatch, Mac and browser adapters publish a signed capability snapshot (heartbeat age, Accessibility/Screen Recording readiness, active tab/session, pending-command count). The relay converts a blocked execution into one durable intent with an idempotency key, blocker class, retryability, evidence pointer, expiry, and terminal event; a later heartbeat resumes only the remaining steps and sends blocker/resumed/completed events to the pendant.
- **owner gets:** A request will fail fast and explain itself instead of burning 45 seconds, then finish after the owner reopens the browser or grants access—without duplicate clicks or needing to remember what they asked.
- effort: Medium-high: shared schema and relay D1 state machine, Mac/browser adapters, event delivery, dashboard and tests for crash/reconnect races.  ·  risk: A stale or spoofed heartbeat could resume against the wrong tab or app; bind intents to device/session fingerprints, require revalidation at resume, expire old intents, and surface every terminal receipt. Recovery is cancel-and-replan from the last completed step.
- cost: Low ongoing storage and heartbeat cost; one background planner call only when resuming or reconciling an ambiguous step.  ·  latency: Adds <1s preflight; avoids 45s browser timeouts and enables asynchronous completion.
- security: Improves security by preventing blind retries, but readiness snapshots must omit URLs/page text unless explicitly needed; encrypt queued intents and redact dashboard payloads.
- depends on: Durable browser job runner and typed receipts; Pendant event/notification delivery; A shared context/identity binding for Mac and browser sessions


## What it asked for

_Nothing._
