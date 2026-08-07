# Harness derivation — faculty-perception — round 84

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-device-registry** — At 2026-08-07T13:29Z, home-macbook-bridge is online; home-chrome is offline with 0 tabs and 9 pending browser commands; cloudflare-contract-test mobile is offline. No pendant is registered.
  - evidence: GET /ops/status and GET /browser/status returned device/browser tables; discover devices matched.
- **mac-input-reachability** — AI Pendant Agent is running, but Accessibility and Screen Recording are not granted; synthesized UI input is not accepted and ui_click/type_text/press_keys receipts cannot be trusted. AppleScript automation grants are present for listed apps.
  - evidence: GET /observe at 2026-08-07T13:29:03Z and GET /ops/status.
- **machine-timezone** — Mac machine timezone is America/New_York.
  - evidence: GET /machine-context returned timezone America/New_York.
- **routing-cost-observation** — The live Mac routing ledger has 7 recent requests: 57% were served off planner (deterministic/background), while the planner baseline is about 8,837 prompt-token-equivalents and 2.5s latency; one background request escalated to planner.
  - evidence: GET /routing at 2026-08-07T13:29Z returned totals, baseline, and recent request records.

## Capabilities it proposed

### "“When my pendant, Mac, or browser comes back online, tell me what happened while it was disconnected, reconcile any actions whose outcome is uncertain, and show me only the items that need my confirmation.”"
- **useful because:** Today the system can queue work and report receipts, but it cannot give one trustworthy answer when different nodes disappear at different times. This would turn offline periods into a safe, understandable handoff: the relay supplies durable events, the Mac supplies local job receipts and observations, and the browser supplies authenticated-page evidence when its extension reconnects. It explicitly distinguishes confirmed success, confirmed failure, and unknown outcome instead of treating a queued command as completed.
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision → faculty-perception → faculty-judgement → faculty-action
- **model tier:** background for periodic reconciliation and event classification; deterministic for connectivity/state joins; planner only when evidence conflicts or an action's outcome needs interpretation. Realtime is used only to read the concise resulting card aloud when the pendant is actually connected.
- **latency:** Under 2 seconds for deterministic connectivity and receipt joins after reconnect; under 15 seconds for a background reconciliation pass; no planner call unless conflicts remain. The owner should receive a compact spoken summary plus a review queue, not a long transcript.
- **cost:** Usually near-zero model cost for event joins and hashes; roughly one gpt-4.1-mini call (about 2–4k input tokens) only for conflicting evidence, with a planner escalation only for genuinely ambiguous cases. Dominant cost is retained event metadata and occasional browser/Mac re-observation, not realtime inference.
- **security:** Private browser URLs, page snippets, Mac receipts, and relay event IDs leave their originating node only as redacted evidence summaries. Keep secrets and page bodies local; encrypt event records; attach source, timestamp, node identity, and freshness to every claim. Never infer success from command enqueue alone. Any retry, resend, cancellation, or browser submission requires explicit confirmation and an idempotency key.
- **missing:** A shared append-only cross-node event envelope with monotonic per-node sequence numbers, wall-clock plus monotonic timestamps, and delivery acknowledgements; A reconciliation endpoint that can correlate relay jobs, Mac jobs/receipts, browser command IDs, and pendant connectivity epochs without declaring unknown outcomes successful; Browser extension reconnect replay and acknowledgement of the 9 currently pending commands before any automatic cleanup; A compact review-queue/card surface and a pendant reconnect notification path; there is no pendant currently registered, so this cannot be exercised end-to-end yet

### "“For any task, show me exactly what information crossed between my pendant, Mac, browser, and relay—what was retained, for how long, and what was never sent—and let me erase the task’s remote traces without breaking my local receipts.”"
- **useful because:** The owner cannot currently audit the privacy boundary of a multi-surface action. They should be able to distinguish audio that stayed local from audio or page text sent to the relay, see which snippets were included in model context, and delete remotely retained material while preserving a minimal local proof that the task happened. This is a user-facing privacy capability, not merely logs: it answers “what did you learn about me, where is it now, and can I remove it?” across the whole hive.
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision → faculty-perception → faculty-judgement → faculty-action → unified
- **model tier:** Deterministic event accounting and redaction manifests on every task; background model only to turn the manifest into a short plain-language explanation. No realtime model call except when the owner asks verbally through a connected pendant.
- **latency:** A manifest should be available within 1 second of task completion; a spoken explanation within 5 seconds. Erasure should return a verifiable receipt within 10 seconds, with local-only cleanup continuing asynchronously if necessary.
- **cost:** Near-zero inference cost for manifests, hashes, retention metadata, and deletion receipts. A small gpt-4.1-mini call (about 1–2k tokens) is optional for natural-language explanation. Storage overhead is a few hundred bytes per event plus hashes, not page or audio bodies.
- **security:** The audit itself is sensitive and must be access-controlled, encrypted, and careful not to duplicate the secret it describes. Store content hashes, classifications, destinations, model/provider, retention deadline, and user-visible excerpts only where consented. Erasure must be cryptographically scoped by task and refuse to claim deletion from third-party systems it cannot control; preserve tamper-evident local receipts without recoverable content.
- **missing:** A mandatory cross-node data-lineage envelope recording source surface, destination, field classification, model/provider, purpose, retention deadline, and content hash for every transfer; Relay APIs for task-scoped export, deletion, and deletion receipts across D1/R2/audio artifacts; Mac and browser middleware that emits lineage events before sending page text, screenshots, audio, or action results; A local privacy ledger and owner-facing redaction/erase UI, plus a pendant command when a pendant is eventually registered


## Changes it proposed to its own stack

### `integration` — Add a cross-node evidence-quorum verifier for every mutating job. Before a job is considered complete, require an authenticated relay delivery record plus a surface-specific postcondition: Mac jobs must provide a typed local receipt and read-back state; browser mutations must provide commandId/session/tab affinity and a post-action DOM or page-state fingerprint; future pendant-originated actions must provide a device sequence and relay acknowledgement. If the nodes disagree or a postcondition cannot be read, persist status=unknown with the exact missing evidence and never auto-retry. On reconnect, replay and close the quorum using idempotency keys.
- **owner gets:** The owner stops hearing confident “done” when only a command was queued or a disconnected browser may have submitted it. They get a truthful three-way result—confirmed, failed, or unknown—with a concrete next check, preventing duplicate purchases, messages, form submissions, and reminders.
- effort: Medium-high: define a versioned evidence envelope and idempotency contract in relay and Mac job storage; add browser postcondition capture; implement deterministic verifier and dashboard/review cards; migrate existing receipts conservatively as unknown when evidence is insufficient.  ·  risk: Some previously reported jobs will downgrade to unknown, which may surprise the owner; no action is undone automatically. A malformed or stale postcondition could falsely confirm, so enforce source signatures, freshness windows, and schema validation. Recover by retaining raw evidence and allowing a manual re-check.
- cost: Negligible per-job compute/storage for hashes and metadata; occasional extra read-back request per mutation. Conflict resolution may use a small background-model call, but the common path is deterministic.  ·  latency: Adds roughly 0.2–2 seconds for local/browser read-back; long-running jobs remain asynchronous. If a node is offline, completion waits for reconnect rather than guessing.
- security: Improves safety by minimizing page/body transfer and binding evidence to node, session, tab, job, and timestamp. Evidence metadata still reveals activity, so encrypt at rest and redact URLs/snippets according to sensitivity.
- depends on: A shared append-only event/evidence envelope across relay, Mac, and browser; Stable idempotency keys and typed postcondition readers for Mac and browser actions; A review surface that exposes unknown outcomes without silently retrying; Pendant registration and device sequence acknowledgements before pendant-originated evidence can be verified


## What it asked for

_Nothing._
## Its own summary

Fresh perception is now recorded: the Mac bridge is online, but no pendant is registered; Chrome/browser bridge is offline with 0 tabs and 9 pending commands. AI Pendant Agent is running with AppleScript automation available, yet Accessibility and Screen Recording remain absent, so GUI action receipts are explicitly untrustworthy. The machine timezone is America/New_York. I proposed an evidence-quorum verifier so mutating work is only called confirmed when relay delivery plus a surface-specific postcondition agree; otherwise it remains unknown and is not retried. I also proposed a reconnect reconciliation flow, though it is close to existing async/review work and should be treated as an extension rather than a wholly separate product.

**Biggest unknown:** The system still lacks an observed, shared cross-node event/evidence contract: I cannot establish whether relay jobs, Mac receipts, browser command IDs, and future pendant sequence numbers can be joined with durable acknowledgements and idempotency. End-to-end verification also awaits browser reconnection, owner-granted TCC permissions, and an actually registered pendant.

