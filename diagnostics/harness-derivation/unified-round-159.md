# Harness derivation — unified — round 159

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What changed since I left?”"
- **useful because:** The owner gets one short, evidence-backed spoken delta across the Mac job queue, browser tabs, reminders, and pendant events instead of manually checking four surfaces. It is read-only and does not guess: each sentence carries a source and timestamp, and it says when a surface was offline.
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision → unified
- **model tier:** background for collecting and normalizing deltas; realtime only to speak the final one-sentence answer
- **latency:** under 5 seconds when all surfaces are online; return partial results within 2 seconds when one surface is stale
- **cost:** roughly $0.01-$0.04 per request; most cost is one background synthesis call, not reads
- **security:** Read-only, least-privilege bindings to the owner’s active browser sessions and Mac job/journal records; redact page contents, secrets, and unrelated tabs; require an explicit since timestamp or use the last owner acknowledgement, never an invented time.
- **missing:** a typed temporal-delta aggregator joining /jobs, /journal/:jobId, /browser/inspections, /capture, and pendant event receipts; a durable last-acknowledged cursor per owner; a compact spoken provenance format

### "“Keep this conversation local.”"
- **useful because:** When LTE is unavailable or the owner is handling sensitive material, the pendant can still converse through the physically attached Mac and browser without sending audio or transcript to the relay. The owner gets an explicit local-only receipt, and the mode ends automatically when the USB link disappears or the owner clears it.
- **path:** pendant → mac-planner → mac-terminal → browser-extension → relay-realtime
- **model tier:** realtime on the Mac for the live exchange; no cloud model call in local-only mode, with an optional owner-confirmed background handoff later
- **latency:** button-to-local-listening under 300 ms; mode transition under 1 second; explicit failure rather than silently falling back to LTE
- **cost:** near-zero API cost while local; one small receipt write per turn; optional later handoff costs the normal transcription/synthesis call
- **security:** The pendant’s USB fallback must cryptographically bind the session to the attached Mac; block relay upload, cloud transcription, browser exposure outside explicitly bound tabs, and persistent audio storage; show a distinctive privacy-latch-compatible LED state and provide a signed local-only receipt.
- **missing:** a local-only session policy enforced across pendant firmware, Mac bridge, and relay; a transport-level no-upload receipt and teardown check; a Mac-resident realtime speech model or local STT/TTS path; a browser binding that prevents accidental use of unrelated tabs

### "“Prepare that browser change, but don’t apply it until I approve it on the pendant.”"
- **useful because:** This is the missing safe bridge between the owner’s voice and an authenticated browser action: the system stages a redacted, tab-bound plan, the pendant displays a pending state, a deliberate physical approval releases exactly that plan, and the browser result is read back with a receipt. The owner never has to trust a spoken “I’ll wait for approval” that silently disappears.
- **path:** relay-realtime → browser-extension → mac-planner → pendant → mac-vision
- **model tier:** background/planner for preparing and validating the plan; realtime only for the spoken preview and result
- **latency:** preview in 3 seconds; physical approval-to-execution under 2 seconds; verification within 5 seconds
- **cost:** roughly $0.02-$0.08 per staged action, dominated by plan validation and optional browser inspection; no model call for the physical approval itself
- **security:** Bind the approval to a plan digest, exact tab/session target, expiry, world fingerprint, and one-use nonce; redact secrets and page contents from pendant audio; refuse on tab navigation, expiry, stale lease, or mismatched result; require the owner’s existing destructive-action confirmation policy for sends/deletes/purchases.
- **missing:** relay persistence and delivery for the existing approval handoff contract; a production caller that prepares plans instead of discarding blocked plans; a browser execution gate consuming the pendant nonce with an idempotency check; post-action browser evidence and a single spoken receipt; orchestrator ledger closure and relay job leases so staged work cannot be mistaken for interrupted work

### "“Use only my personal Gmail and this one browser tab for this answer, and forget that access afterward.”"
- **useful because:** The owner can make narrowly scoped, temporary data-access decisions instead of granting the whole agent access to every browser session and Mac source. The system can answer across surfaces while proving exactly which tab/app was read, automatically expiring the permission and deleting the derived working context afterward.
- **path:** relay-realtime → browser-extension → mac-planner → mac-vision → pendant
- **model tier:** realtime for the spoken consent and final answer; background for source filtering and deletion verification
- **latency:** under 2 seconds to confirm the scope; under 6 seconds for a bounded query; expiry and cleanup receipt within 2 seconds
- **cost:** about $0.01-$0.05 per scoped query, dominated by synthesis; policy checks and cleanup are deterministic
- **security:** Permissions must bind to exact tab/session or app/path, query purpose, fields allowed, expiry, and a per-request nonce. Do not expose page secrets to the pendant. Refuse if a result came from an unbound source, and return a deletion receipt after the scope expires.
- **missing:** a cross-surface capability-token policy engine; browser and Mac executors that attach provenance to every read; ephemeral context storage with cryptographic deletion/expiry receipts; a pendant-visible scope summary and cancel action

### "“Make this briefing available when I’m offline, with the sources attached.”"
- **useful because:** The owner can receive a cited, playable briefing on the pendant even when LTE and the Mac are unavailable. It is a bounded knowledge capsule, not an always-on sync: sources are captured at preparation time, integrity-checked, expire, and are removed after acknowledgment.
- **path:** relay-realtime → mac-planner → browser-extension → pendant
- **model tier:** background for research, citation extraction, and compression; realtime only if the owner asks follow-up questions while connected
- **latency:** prepare asynchronously in under 60 seconds; offline playback starts in under 1 second after the owner presses the inbox button
- **cost:** about $0.03-$0.15 per briefing depending on research depth and TTS length; no cost during offline playback
- **security:** Only explicitly allowed URLs/tabs may be captured; redact account data and credentials; sign the capsule and its source manifest; enforce size, expiration, and acknowledgment deletion; never silently mirror the browser.
- **missing:** a signed relay-to-pendant knowledge-capsule format; bounded source snapshot and citation extraction across browser and web search; offline playback metadata and source-index navigation on the pendant; acknowledgment/deletion receipts for the capsule

### "“Forget everything you learned about this project, everywhere.”"
- **useful because:** The owner gets a real, auditable deletion operation instead of merely hiding a memory from one index. The system identifies derived copies across context graph, captures, pending jobs, browser inspection records, and relay caches, deletes what it controls, and names anything it could not reach.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision
- **model tier:** background for inventory and deletion verification; realtime only to explain scope and final receipt
- **latency:** show the deletion plan within 3 seconds; complete bounded local/relay cleanup within 30 seconds; provide a final convergence receipt
- **cost:** about $0.01-$0.05 per request; storage scans and hashes dominate, not model inference
- **security:** Require a deliberate physical confirmation for broad deletion; use exact entity/project bindings rather than semantic guesses; preserve only a minimal tombstone and audit receipt; never claim deletion from third-party systems it cannot control.
- **missing:** a cross-surface data-lineage index from source reads to derived memories and jobs; a dry-run deletion plan with exact targets and byte counts; idempotent deletion plus convergence verification across relay, Mac, browser, and pendant; a physical-confirmation path for broad or irreversible deletion


## Changes it proposed to its own stack

### `integration` — Wire the already-written prepare/approve and physical_transaction_approval_latch into one end-to-end browser gate: blocked plans must persist a redacted staged record in the relay, deliver only a nonce and summary to the pendant on the next conversation, consume exactly one physical approval, execute only against the original browser session/tab binding, and append a verified browser result plus receipt. Close successful orchestrator ledgers and add a lease/requeue sweep before enabling recovery.
- **owner gets:** A browser action that needs approval will actually wait safely and then happen when the owner presses the pendant, instead of being spoken about and discarded. If the Mac or browser dies, it will not duplicate the action or falsely claim completion.
- effort: Medium-high: relay schema/store and delivery, bridge integration, browser idempotency gate, and fault-injected end-to-end tests.  ·  risk: A stale or duplicated nonce could cause an unintended action; mitigate with one-use nonce, digest/world/session binding, expiry, and refusal on any mismatch. Recovery should default to no execution when evidence is incomplete.
- cost: Negligible runtime/API cost; engineering work across relay, Mac agent, browser extension, and firmware event handling.  ·  latency: Adds roughly 100–500 ms for receipt validation after approval; preparation remains asynchronous.
- security: Improves least privilege and auditability, but the relay must never store page secrets or form values. Physical approval is consent, not a substitute for action-specific authorization.
- depends on: relay implementation of shared/approvalHandoff.js APPROVAL_STORE_CONTRACT; next-conversation pendant delivery path and physical approval event; orchestrator closeLedger call; relay_jobs lease_until and requeue sweep; browser command idempotency and post-action evidence


## What it asked for

_Nothing._
