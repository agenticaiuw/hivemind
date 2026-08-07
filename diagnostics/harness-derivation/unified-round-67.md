# Harness derivation — unified — round 67

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live cross-surface readiness round 67** — Relay and Mac bridge are reachable, but the Mac agent is not ready: Accessibility and Screen Recording are ungranted, computer-use loop disabled, browser extension offline with 5 pending commands. AppleScript automation grants are present, so non-GUI Mac actions remain viable. A recent pipeline run rendered 24 kHz PCM successfully but stopped at an approval gate for a shell action.
  - evidence: GET /ops/status at 2026-08-07T12:11Z; GET /pipeline shows 24 kHz mono PCM TTS completed and waiting-for-approval; GET /jobs shows plan_ready with run_shell action.

## Capabilities it proposed

### "If a task gets interrupted or the connection drops, resume it later exactly where it stopped and tell me only what changed—without repeating any completed clicks, messages, or form fields."
- **useful because:** Today a wearable conversation, relay job, Mac automation, and logged-in browser can each lose context independently. A verified checkpoint lets the owner leave, reconnect, or switch surfaces and safely continue instead of restarting or guessing what happened.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use the cheap background model to reconcile checkpoints and produce a delta; reserve realtime only for the owner's spoken interruption and the final one-sentence handoff.
- **latency:** A reconnect acknowledgement under 2 seconds; checkpoint reconciliation 5–20 seconds in background. No need to hold the voice turn open while Mac/browser work resumes.
- **cost:** Roughly $0.01–$0.05 per resumed task, dominated by summarizing only the changed receipts and page evidence; storage and relay calls dominate less than model tokens.
- **security:** Checkpoints may contain private URLs, typed fields, and draft text. Encrypt payloads, retain only hashes plus minimal redacted summaries by default, bind each checkpoint to the owner/session, and require confirmation before any irreversible resumed action (send, purchase, delete).
- **missing:** A shared checkpoint schema spanning audio turn, relay job, Mac action receipt, and browser command/result; Idempotency keys that survive a reconnect and are enforced by both Mac and browser executors; A pendant-visible resume/paused indicator and a spoken 'continue' affordance; A durable reconciliation worker that can distinguish verified completion from merely dispatched work

### "Use the private page I have open and the relevant files on my Mac together, then answer me with what each source says and what they disagree about—without sending either source's contents through the relay or changing anything."
- **useful because:** The browser alone cannot see local project files, and the Mac agent should not receive browser cookies or broad page contents. The owner needs one trustworthy answer spanning both private surfaces while keeping each sensitive source on the device that can access it.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a low-cost background reconciliation model on redacted, structured extracts; use realtime only to clarify the owner's request and speak the final short result.
- **latency:** Collect parallel extracts in 5–15 seconds and speak a concise answer immediately after reconciliation. If one surface is offline, say exactly which source is missing instead of silently substituting.
- **cost:** About $0.01–$0.06 per request, dominated by reconciliation tokens; local extraction and relay metadata are inexpensive.
- **security:** The relay must never receive raw cookies, page bodies, or local files. Each surface performs local extraction and sends field-level claims, source hashes, sensitivity labels, and minimal snippets. Encrypt claims in transit and at rest; require confirmation before any mutation.
- **missing:** A device-local extraction protocol for Mac files and browser pages; A relay schema for redacted claims with provenance, sensitivity, hashes, and contradiction links; Scoped, one-task capability tokens instead of forwarding browser credentials; A reconciliation UI that lets the owner open the original source on its owning surface


## Changes it proposed to its own stack

### `integration` — Define and implement a cross-surface Task Checkpoint Envelope: immutable task step IDs, idempotency key, executor (pendant/relay/Mac/browser), precondition fingerprint, dispatch time, verified result, evidence pointer, and safe-resume policy. Have relay persist envelopes at every boundary and reconcile them after reconnect; expose a compact delta to the pendant and dashboard. Treat dispatched-without-receipt as unknown, never as success.
- **owner gets:** Interrupted work becomes trustworthy: the owner can walk away, lose LTE, or close the laptop and later hear exactly what completed, what is uncertain, and the single safe next step—without duplicate actions or a full re-explanation.
- effort: Medium-high: shared schema and migrations, executor adapters, reconciliation tests with dropped WebSocket/browser responses, and dashboard/pedant resume UX.  ·  risk: A false verified receipt could cause duplicate or destructive actions; fail closed on missing evidence, use idempotency at every executor, and keep undo for reversible steps. Recovery is manual review of the checkpoint with the original tab/session.
- cost: Low storage/compute; modest background model cost only when producing a human delta. No new pendant hardware required.  ·  latency: Adds a few milliseconds to local receipt writes and one relay round trip on resume; voice acknowledgement remains immediate while reconciliation runs asynchronously.
- security: Increases retention of task metadata. Encrypt envelopes, minimize page content, redact secrets, enforce session ownership, and expire evidence according to action sensitivity.
- depends on: Existing job receipts and undo routes; Browser request IDs/tab affinity and typed results; A durable browser job runner (currently only partly shipped); Pendant local resume indicator; Accessibility/Screen Recording remains unnecessary for the checkpoint layer

### `relay` — Add a capability-token and claim-envelope protocol for cross-surface private research. The browser and Mac each keep raw content local, derive typed claims with source URI/path, locator, timestamp, sensitivity, and content hash, and send only the claims to the relay. The relay joins claims by task ID, detects contradictions, and returns source-bound references that can be reopened only on the owning surface.
- **owner gets:** They can ask one question across their logged-in browser and local Mac without exposing private material to the cloud or forcing one agent to impersonate another. Answers remain auditable: every statement points back to the exact tab or file that produced it.
- effort: High: local extractors for browser DOM and files, token minting/expiry, claim signing, contradiction handling, and source-reopen UX across pendant and dashboard.  ·  risk: Over-redaction may make answers incomplete; under-redaction could leak sensitive text. Default to structured fields and hashes, reject unlabelled raw content, expire tokens quickly, and fall back to separate per-surface summaries when joining is unsafe.
- cost: Low relay storage and compute; modest model cost for claim reconciliation. No required hardware purchase.  ·  latency: Parallel local extraction adds roughly 1–5 seconds; contradiction reconciliation adds 1–3 seconds. The pendant can acknowledge immediately and speak when the joined result is ready.
- security: Substantially reduces cloud exposure, but introduces signed claim metadata and source-reference risks. Bind tokens to task, owner, surface, and expiry; audit every claim access.
- depends on: Browser extension reconnect and durable command delivery; A Mac file-extraction route that does not require Accessibility; Typed provenance and sensitivity fields in the shared context service; Owner-defined rules for which browser pages and Mac folders may participate


## What it asked for

_Nothing._
