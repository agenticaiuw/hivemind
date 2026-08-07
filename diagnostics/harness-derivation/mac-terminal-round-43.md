# Harness derivation — mac-terminal — round 43

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac readiness 2026-08-07 round 43** — Live /ops/status reports fullControlMode=true and token configured, but agent ready=false because Accessibility trusted=false and Screen Recording granted=false; browser extension is offline with 3 pending commands. Relay and Mac bridge are reachable.
  - evidence: GET /ops/status HTTP 200 at 2026-08-07T10:21Z

## Capabilities it proposed

### "Why couldn't you do that, and what do I need to fix?"
- **useful because:** Today the system can attempt actions while silently lacking Accessibility/Screen Recording or while the browser is offline with queued commands. The owner should get a precise, evidence-backed diagnosis instead of a vague failure: which surface was selected, which prerequisite failed, whether anything ran, what is queued, and the shortest repair path. A pendant can announce the diagnosis, the relay can retain it, and the Mac dashboard can show the exact permission or reconnection step.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background for periodic readiness snapshots and cheap classification; realtime only when the owner asks verbally or needs the short spoken diagnosis
- **latency:** Under 1 second for cached readiness; up to 5 seconds for a live Mac/browser preflight
- **cost:** About $0.001 or less per periodic snapshot using a small model; interactive explanation is usually one realtime turn, dominated by voice-model duration rather than tool calls
- **security:** Expose only capability states and sanitized error metadata, never command arguments, page contents, or credentials. Permission repair must open the relevant System Settings pane but should not claim permission was granted until a fresh probe confirms it. Pending browser commands need request IDs and expiry so stale work is not replayed.
- **missing:** A shared readiness schema spanning Mac permissions, browser connectivity/queue health, relay reachability, and pendant link state; A preflight endpoint that runs before and after each delegated job and records the failed prerequisite without capturing secrets; A Mac dashboard/pendant presentation for remediation steps and stale-command cancellation; A typed mapping from prerequisite failures to safe System Settings or browser-extension reconnect actions

### "When I press the pendant and say 'save this for the project,' capture it even if my Mac or browser is unavailable, then put it in the right project when they come back—without losing it or creating duplicates."
- **useful because:** The owner should be able to use the pendant as a reliable anywhere capture device rather than remembering thoughts until the Mac is available. The system would preserve the original audio/transcript, infer the intended project from compact shared context, and later reconcile it with the Mac's project files, reminders, and relevant authenticated browser work. This is more useful than a simple voice memo because it completes the handoff across the wearable, always-awake relay, Mac filesystem, and browser context.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only for the short capture acknowledgement and clarification; a cheaper background model should transcribe, classify, deduplicate, and perform the eventual merge.
- **latency:** Immediate local/relay acknowledgement under 2 seconds; classification within 30 seconds; final Mac/browser merge within 2 minutes of a device reconnecting.
- **cost:** Roughly $0.003–$0.02 per capture depending on audio length; transcription and classification dominate, while durable storage and reconciliation are negligible.
- **security:** Audio and transcript leave the pendant for relay processing and may include confidential material. Encrypt queued captures, retain the raw audio briefly, and keep project/browser credentials on the Mac/browser. Never write into a project or authenticated page without recording the target, source excerpt, and before/after result. If classification confidence is low, place it in an inbox rather than guessing.
- **missing:** A pendant-side capture-and-ack protocol that survives link loss and assigns a durable capture ID; Encrypted relay storage with per-capture retention and exactly-once delivery semantics; A Mac project-ingestion adapter that can merge into files/notes/reminders with conflict detection and provenance; A browser-context resolver that can associate a capture with an authenticated tab without exporting page contents; Cross-surface deduplication and an owner-visible review inbox for ambiguous captures


## Changes it proposed to its own stack

### `browser-harness` — Add an offline-queue reconciliation state machine to browserBridge/browserSessions: every queued command gets createdAt, TTL, originating request, tab fingerprint, and intended effect class; while the extension is offline the queue is visibly 'held' rather than silently pending. On reconnect, revalidate the tab/session fingerprint, collapse idempotent duplicates, expire stale commands with a receipt, and publish a compact reconciliation event to the relay/pendant. Do not auto-replay a command whose target tab changed or whose TTL elapsed; preserve it for explicit re-planning.
- **owner gets:** The agent currently reports the browser offline with three pending commands, so the owner cannot tell whether reconnecting will safely continue old work or unexpectedly act on a changed page. This prevents surprise replay and turns abandoned browser work into a clear, recoverable answer.
- effort: Medium: queue schema migration, reconnect reconciliation, tab fingerprinting, receipts, and a small dashboard/pendant status surface; test extension restarts and Mac sleep/wake.  ·  risk: A legitimate long-running task could expire or be held. Recovery is to retain the original request and re-plan it against the current tab; never delete without a tombstone. Fingerprints must avoid storing page secrets.
- cost: Negligible API cost; local storage/D1 receipts are small. One cheap classification pass per reconnect batch, not per command.  ·  latency: Adds tens to hundreds of milliseconds on extension reconnect; avoids costly and confusing failed replays.
- security: Improves security by preventing stale authenticated actions against a different tab. Store only hashed tab identity/URL origin and redacted command metadata, not DOM or credentials.
- depends on: Shared readiness schema from the proposed preflight capability; Existing browser request IDs/idempotency and action receipts; Relay event delivery to the pendant/dashboard

### `integration` — Create a durable cross-device capture ledger with append-only capture IDs, encrypted payloads, delivery acknowledgements, semantic deduplication fingerprints, and merge outcomes. The relay accepts a pendant capture once, the Mac consumes it idempotently after reconnect, and every attempted project/file/reminder/browser association records source, confidence, target, and conflict status. Unresolved items remain in an inbox rather than being silently discarded or misfiled.
- **owner gets:** A thought spoken while away from the Mac would survive dead batteries, Wi-Fi gaps, sleep, and reconnects, and the owner could trust that it was either filed exactly once or visibly awaiting review.
- effort: Medium-to-large: protocol and schema design, encrypted relay persistence, pendant retry state, Mac ingestion adapters, conflict UI, and fault-injection tests for crashes between acknowledgement and write.  ·  risk: Duplicate delivery, incorrect project inference, or partial writes could create confusing records. Idempotency keys, immutable originals, atomic local writes where possible, and an explicit unresolved inbox provide recovery.
- cost: Small durable-storage cost; one background transcription/classification call per capture. Raw-audio retention can be capped to control cost.  ·  latency: Acknowledgement is immediate; final filing is asynchronous and may wait for Mac/browser availability.
- security: Captures may contain private speech and authenticated-work context. Encrypt in transit and at rest, minimize raw-audio retention, keep credentials local to Mac/browser, and expose provenance without exposing secrets.
- depends on: Pendant capture trigger and retry state; Relay durable encrypted storage; Mac project/file/reminder ingestion API; Browser context lookup with redacted evidence


## What it asked for

_Nothing._
