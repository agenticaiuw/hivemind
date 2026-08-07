# Harness derivation — mac-planner — round 137

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If my private browser connection breaks, tell me immediately, pause and preserve any queued work, then reconnect and resume only the safe steps without duplicating anything; give me a concise recovery report."
- **useful because:** Today the bridge reports contradictory online states and has 11 stale commands, including one processing for 19 attempts. Browser tasks silently time out or can be retried into duplicates. A cross-surface circuit breaker would protect authenticated work, let the pendant report the outage, and recover automatically when Chrome/Safari returns.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → unified
- **model tier:** Use deterministic relay/Mac state machines for heartbeats, lease expiry, idempotency, queue quarantine, and replay; use the realtime model only to explain the incident to the wearer and classify ambiguous recovery, never to decide whether a mutation is safe.
- **latency:** Heartbeat detection within 15 seconds; pendant alert under 2 seconds after relay receives the fault; reconnect probe within 30 seconds; replay only after three healthy heartbeats. Recovery report under 5 seconds after replay completes.
- **cost:** Near-zero model cost for normal operation; roughly $0.001–$0.01 only when the realtime model summarizes a failure or asks the owner to resolve an ambiguous step. Dominant cost is durable queue/state storage and heartbeat traffic.
- **security:** Authenticated URLs and extracted page data must stay local to the Mac/extension and be referenced by opaque job IDs in relay telemetry. Never replay submit/send/purchase/delete steps automatically; quarantine them with before-state evidence and require the existing owner-controlled review path. Expire leases and wipe quarantined payloads according to retention settings.
- **missing:** A browser queue circuit breaker that distinguishes stale/offline/processing leases from healthy commands; An idempotency-aware replay ledger shared by relay and Mac/browser bridge; A pendant-visible outage/recovery event and concise receipt format; A health handshake that verifies the actual tab/session, not only extension lastSeenAt

### "When I say “pause this and pick it up when I’m free,” freeze the work across my pendant, Mac, and private browser exactly where it is, save a private resume capsule, and restart it at the next suitable calendar window with a one-sentence reminder of what was waiting."
- **useful because:** Today an interruption strands multi-step work: the browser may lose its tab, the Mac may leave half-written artifacts, and the pendant has no reliable way to resume the same intent later. This would let the owner defer difficult work without re-explaining it or risking duplicate actions, while respecting meetings and focus time.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Use deterministic state capture, calendar-window selection, leases, and idempotency for the mechanics; use a cheaper background model to compress the resume capsule and rank suitable windows. Reserve realtime only for the spoken pause/resume exchange.
- **latency:** A pause acknowledgement within 2 seconds, capsule persistence within 5 seconds, and resume scheduling immediately after calendar synchronization. On resume, restore state before speaking; the spoken reminder should take under 10 seconds.
- **cost:** Usually under $0.01 per pause/resume, dominated by one small background summarization call; calendar reads, local snapshots, and durable capsule storage are the main non-model costs.
- **security:** Resume capsules may contain authenticated URLs, drafts, and local filenames. Keep raw contents on the Mac/browser session, store only encrypted references and hashes on the relay, apply owner-configured retention, and never auto-submit/send/purchase after resumption. If a page or file changed, stop and report the conflict instead of guessing.
- **missing:** A first-class resumable-work capsule spanning relay jobs, Mac receipts, and browser tab/session state; Atomic pause semantics that stop new mutations while allowing the current reversible step to finish; Calendar-aware resume scheduler with quiet hours and conflict detection; Conflict UI/voice flow showing what changed since pause and offering resume, revise, or discard


## Changes it proposed to its own stack

### `integration` — Add a durable cross-surface task capsule and lease protocol. Every relay-issued goal gets a capsule containing ordered step IDs, surface ownership (pendant/relay/Mac/browser), idempotency key, precondition snapshot hash, lease expiry, and receipt links. The Mac and browser bridge atomically claim one step, heartbeat it, and return a typed result; on disconnect the relay marks the lease abandoned, freezes dependent steps, and hands the capsule to the next available surface for reconciliation instead of replaying the whole plan.
- **owner gets:** A request such as “find the invoice in Safari, save it on my Mac, and tell me on the pendant” would survive a browser crash or dropped voice link without losing place or repeating a download, email draft, or other side effect. The owner gets one truthful status and one recovery report instead of conflicting “done” and timeout messages.
- effort: Medium-high: shared D1/local JSON schema, atomic claim/lease transitions, adapters in browser bridge and Mac executor, and receipt correlation tests across reconnects.  ·  risk: A bad precondition hash could pause harmless work or, worse, allow a duplicate if a client loses its receipt. Recover with conservative lease expiry, append-only receipts, duplicate-result reconciliation, and manual resume for any unknown mutation. Do not infer completion from lastSeenAt alone.
- cost: Negligible inference cost; small D1/local storage and heartbeat traffic increase. No new paid model calls in the normal path.  ·  latency: Adds one local ledger write and claim check per step (tens of milliseconds); reconnect recovery waits for bounded health confirmation rather than immediately retrying.
- security: Capsules should carry opaque identifiers and redacted hashes by default; sensitive page text remains on the owning Mac/browser session. Cross-surface messages need authenticated pairing and scope-limited session IDs.
- depends on: Browser bridge heartbeat/result endpoints must expose a stable command lease and actual tab/session identity; Mac receipts need a shared idempotency key and step ID rather than only per-action receipt IDs; Relay durable job records need a capsule pointer and explicit abandoned/reconciled states

### `dashboard-ux` — Replace the single browser online boolean with a state panel showing transport health, extension heartbeat age, active tab/session identity, oldest pending command age, lease owner/attempt count, and a clear “safe to resume / quarantined / owner action needed” state. Detect and visibly flag contradictions such as /browser/status offline while /ops/status says online, rather than presenting online:true.
- **owner gets:** When browser work fails, the owner can immediately see whether Chrome/Safari is closed, the extension is not polling, a page is blocked, or a command is stuck. They can recover the right thing instead of repeatedly asking the pendant to retry and risking duplicate actions.
- effort: Small-medium: derive health states from existing endpoints, add stale/contradiction rules, and link each queued item to its receipt and cancel/quarantine action.  ·  risk: An overly sensitive indicator could create noise during normal tab transitions. Use hysteresis (three heartbeats and a 15-second grace period) and preserve raw timestamps for diagnosis.
- cost: No model cost; a few local/relay reads and negligible dashboard storage.  ·  latency: Status refresh every 5–15 seconds; no impact on action execution.
- security: Show URLs/titles only on the local Mac dashboard; relay-facing telemetry should redact them and expose opaque session IDs.
- depends on: GET /browser/status; GET /browser/poll; GET /ops/status; POST /browser/heartbeat; GET /browser/sessions; GET /jobs/:jobId/receipts

### `context` — Add an owner-visible ephemeral-context mode spanning pendant, relay, Mac, and browser. Before a task begins, the system creates a declared data boundary (which tabs, files, calendar range, and mail scope may be read); each surface emits signed provenance receipts; when the task ends or the owner says “forget this,” relay copies, browser extraction buffers, and Mac temporary artifacts are cryptographically shredded or expired, while retaining only a redacted outcome and an auditable deletion receipt.
- **owner gets:** The owner could safely ask for help with a sensitive logged-in page or document and know exactly what was consulted, what left the Mac, and what was erased afterward. Today privacy depends on scattered redaction and retention behavior that the wearer cannot inspect or control from the pendant.
- effort: High: define a cross-surface data-boundary manifest, add provenance/deletion receipts to browser and Mac jobs, implement relay-side encrypted ephemeral storage with expiry, and expose a simple pendant review/forget interaction.  ·  risk: Deletion cannot retract data already copied by an external website or a model provider, and a crash could leave a temporary local artifact. Mitigate by defaulting to local extraction, minimizing outbound payloads, encrypting per-task keys, short TTLs, crash-startup garbage collection, and clearly reporting deletion limits.
- cost: Small storage and key-management overhead; lower model cost when local extraction avoids sending full pages. No recurring inference cost outside the task.  ·  latency: A few hundred milliseconds to establish the manifest and finalize deletion; no meaningful impact to ordinary read-only tasks.
- security: Strongly improves least-privilege and auditability, but requires careful key isolation and authenticated pairing. Raw sensitive content must never be logged in receipts or relay telemetry.
- depends on: A typed cross-surface task identity shared by relay, Mac, and browser; Browser extraction and Mac read actions must return provenance without raw content in logs; Relay durable storage needs per-task TTL and deletion receipts; Pendant needs a local confirmation/review affordance for scope and forget


## What it asked for

_Nothing._
## Its own summary

Fresh live checks found a real browser failure mode: /browser/status reports offline with 11 pending commands, /browser/poll returns a command stuck processing after 19 attempts, while /ops/status incorrectly reports online and has no tab identity. I recorded three new proposals: a cross-surface task capsule/lease protocol, automatic browser outage quarantine and safe recovery, and a dashboard that exposes contradictory health, lease age, and retry state. I also notified browser-extension. Nothing was retried or deleted, avoiding duplicate authenticated work.

**Biggest unknown:** Implementation ownership and semantics of the browser command queue are still unclear: whether the extension can be restarted remotely, how to atomically cancel/quarantine the 11 pending commands, and whether command results already carry durable idempotency keys. Owner-side Accessibility and Screen Recording are still not granted, so UI-based recovery remains unavailable; the owner must enable those manually if vision/accessibility automation is required. The browser extension also needs to be opened/enabled and actively polling.

