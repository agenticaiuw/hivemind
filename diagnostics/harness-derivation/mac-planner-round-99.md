# Harness derivation — mac-planner — round 99

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I lost connection—resume the task I was doing and tell me exactly what is left.”"
- **useful because:** Today a disconnected browser job can sit behind six pending commands while the Mac job receipt merely says failed; the owner has no single, trustworthy answer about what actually happened, what was already changed, or what is safe to retry. This creates a cross-device recovery conversation: the pendant identifies the interrupted intent, the relay reconciles Mac receipts with browser command/result history, the Mac writes a local recovery capsule, and the browser resumes only idempotent steps after its heartbeat returns. The owner gets one concise spoken status and one concrete next step rather than duplicate submissions or guesswork.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background for receipt reconciliation and capsule generation; realtime only to answer the pendant follow-up and read the final short status
- **latency:** Under 2 seconds for an initial spoken 'paused/resumed/blocked' status; reconciliation under 10 seconds; browser reconnect may take as long as the extension heartbeat, with no 45-second blind navigate timeout
- **cost:** About $0.002–$0.01 per recovery (small background text pass; realtime cost only if the owner asks follow-up). Storage is a small local JSON/Markdown capsule plus D1 job metadata.
- **security:** Never infer that an unacknowledged browser mutation succeeded. Reconcile by request/idempotency key and typed receipt, quarantine ambiguous writes, and expose URL/tab, timestamps, and before/after evidence locally. Authenticated page content stays on the Mac/extension unless the owner’s existing relay privacy setting permits excerpts. Resume should be limited to the exact original plan and expire after a short lease; no new submission or destructive action is invented.
- **missing:** A cross-surface causal recovery record linking relay intent, Mac jobId/action receipts, browser commandId/result, and the originating pendant utterance; A reconciliation endpoint that distinguishes completed, failed, not-delivered, and ambiguous browser mutations and emits one safe next step; A local recovery-capsule writer plus a reconnect trigger on browser heartbeat; current browser is offline and six commands are pending; A fail-fast browser enqueue/resume path that does not wait 45 seconds when the extension is offline

### "“Switch me to work mode” (or “personal mode”) and keep every action, tab, file, and spoken briefing in the right context."
- **useful because:** The owner cannot safely use one assistant across work and personal life today: a pendant request can reach the Mac, relay memory, Mail/Calendar, and authenticated browser without a durable context boundary. A physical mode switch would make the hive respect the owner's current context—work requests use the work browser session and project, personal requests use the personal session and files—and refuse to silently mix evidence or carry private content into a work briefing.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic routing and redaction by default; background model only to classify an ambiguous request. Realtime is used only to acknowledge the mode change and explain a blocked cross-context action.
- **latency:** Mode acknowledgment under 300 ms; routing decision under 1 second. Switching must take effect before the next Mac or browser action, and any in-flight action must be paused or explicitly marked with its prior context.
- **cost:** Near-zero per switch; small local/relay metadata records. Occasional background classification costs under $0.005, with no page bodies sent to the model unless explicitly allowed.
- **security:** Context must be a hard data boundary, not a prompt hint. Store only an opaque context ID in relay telemetry; keep source content local where possible. Tag every job, browser tab/session, file operation, receipt, memory write, and audio item with context and reject mismatches. The pendant should provide a long-press physical override to emergency-neutral mode; switching must not delete or move data.
- **missing:** A persistent context/profile identity on the pendant with an offline-safe toggle and current-mode announcement; Relay and Mac job schemas that carry a non-forgeable context ID through planning, execution, receipts, memory, and audio; Browser session/container affinity and a way to label existing tabs as work or personal without scraping their contents; A context-aware memory projection and redaction layer that prevents cross-context retrieval and cross-context summaries; Dashboard views and recovery tooling that show the active context and flag any in-flight work from the previous context


## Changes it proposed to its own stack

### `browser-harness` — Implement a causal recovery ledger and fail-fast reconciler between the existing relay/Mac job and browser queues. On enqueue, assign one intentId and per-step idempotency key; persist edges intentId→jobId→actionId→commandId. On browser heartbeat/poll/result, reconcile each step into completed, failed-before-delivery, delivered-unknown, or completed-with-evidence. If status is offline, return immediately with a resumable checkpoint instead of waiting 45 seconds. On reconnect, replay only steps marked safe-to-retry, quarantine delivered-unknown writes, and emit a local recovery capsule through /capture containing the exact evidence and next action.
- **owner gets:** A dropped connection stops being a mystery: the pendant can say what definitely happened, what did not happen, and what needs review, without duplicate form submissions or a misleading failed receipt.
- effort: Medium: shared ledger schema, adapters in browserBridge/browserSessions and Mac job receipts, reconnect worker, tests for crash between delivery and result.  ·  risk: A ledger bug could incorrectly classify a mutation. Default ambiguous states to quarantine/no replay; preserve raw receipts and support manual retry. Existing jobs remain readable during migration.
- cost: Negligible D1/local JSON storage and one cheap background reconciliation pass; no additional realtime calls.  ·  latency: Offline browser actions fail in milliseconds rather than 45 seconds; reconnect adds one heartbeat cycle and bounded reconciliation.
- security: Improves auditability; store hashes/snippets and tab/session identifiers rather than full private page content in relay. Keep detailed evidence local unless explicitly shared.
- depends on: Browser extension reconnect/heartbeat must actually report online; currently /browser/status reports offline with 6 pending commands.; A durable runner/checkpoint implementation (chg-16bc5dee) should supply step boundaries, but this ledger remains useful if that runner is delayed.

### `model-routing` — Add a deterministic recovery classifier before any LLM call. It consumes typed Mac/browser receipts and maps them to four states (done, not-started, failed, ambiguous) using idempotency keys, delivery timestamps, and before/after evidence; only ambiguous multi-step cases go to a background model, while the pendant receives a fixed short status template from the realtime tier.
- **owner gets:** The owner gets an immediate, accurate answer after a disconnect and does not pay for an expensive model to interpret a simple receipt. More importantly, the system will not confidently hallucinate that a private browser action succeeded.
- effort: Small to medium: define receipt state machine, add tests for timeout/crash/reconnect orderings, and route only unresolved cases to background reconciliation.  ·  risk: A too-conservative classifier may say 'needs review' more often. That is preferable to duplicate or falsely reported actions; raw evidence and a retry path remain available.
- cost: Usually near-zero model cost; background model only for genuinely ambiguous cases, reducing realtime tokens and repeated context transmission.  ·  latency: Immediate (<200 ms) local classification; model-backed cases remain asynchronous.
- security: Reduces private page data sent to models because typed metadata is sufficient for most recovery decisions.
- depends on: Causal intentId/jobId/actionId/commandId links from the browser-harness recovery ledger.; Stable typed receipt fields from /jobs/:jobId/receipts and /browser/result/:commandId.

### `context` — Introduce a signed Context Capsule carried end-to-end with every request and artifact. The capsule contains an opaque profile ID, issuance/expiry, allowed surfaces, and a key version; the relay signs it, Mac and browser adapters verify it, and receipts/captures/briefings/memory writes inherit it automatically. Add a context firewall that rejects a job when its source capsule, active Mac project, browser session, or destination artifact disagree, while allowing an explicit owner-triggered reclassification that records both old and new context.
- **owner gets:** “Work mode” becomes an enforceable privacy guarantee instead of a label in the prompt: a personal browser tab cannot accidentally feed a work briefing, and a work file cannot silently become part of personal memory.
- effort: Medium to high: shared capsule schema and signing, propagation through relay/Mac/browser APIs, context-aware memory projection, migration for existing untagged jobs, and dashboard diagnostics.  ·  risk: Existing jobs and third-party tabs may be untagged and get paused. Treat unknown as quarantined, provide a local labeling flow, and preserve all existing receipts; never auto-classify sensitive content.
- cost: Tiny metadata overhead per request and receipt; no meaningful model cost. Key rotation and local capsule storage add minor implementation complexity.  ·  latency: Milliseconds for signature verification and mismatch checks; no additional model round trip for normal actions.
- security: Strongly reduces accidental cross-context disclosure, but requires secure key storage and careful handling of mode-switch events. The relay should retain only opaque IDs and audit hashes, not content.
- depends on: A durable owner-controlled work/personal mode source on the pendant or client.; Shared propagation hooks in relay, Mac job runner, browser sessions, context graph, and briefing/capture writers.; A migration policy for existing untagged sessions and artifacts.


## What it asked for

_Nothing._
## Its own summary

Discovered the live Round 99 state: relay and Mac bridge are healthy, but the browser extension is offline with 6 pending commands; the last browser navigation waited 45 seconds and failed. Accessibility and Screen Recording remain unavailable, while AppleScript automation is granted. I recorded a new cross-surface recovery design: a causal ledger linking pendant intent → Mac job/action receipt → browser command/result, deterministic receipt classification, fail-fast offline handling, quarantine of delivered-unknown writes, and a local recovery capsule. I also proposed routing simple reconciliation without an expensive realtime model and notified browser-extension about the required hooks. The granted mac_readonly_inspect tool is still schema-only in practice, despite being granted.

**Biggest unknown:** Whether the browser bridge can provide reliable delivery acknowledgements and idempotency across reconnects; without that, ambiguous private-page mutations must remain quarantined. Separately, live UI/browser inspection cannot be verified until mac_readonly_inspect is implemented, and visual inspection still depends on owner-controlled TCC permissions.

