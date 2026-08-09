# Harness derivation — unified — round 200

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Stop everything you are currently doing, everywhere, and tell me exactly what was stopped and what could not be reached."
- **useful because:** Privacy latch stops capture and playback, but it does not stop an already queued Mac action, browser command, or relay job. A single deliberate physical stop would give the owner an actual emergency boundary instead of a local mute that leaves remote work running.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** deterministic control plane; no model call for cancellation or receipts
- **latency:** Pendant mute immediately; cancellation fan-out begins under 250 ms and returns a per-job outcome within 2 seconds. Unreachable surfaces are explicitly marked, never implied stopped.
- **cost:** Negligible API cost; one authenticated event, bounded fan-out, and a compact receipt.
- **security:** Must be a separate deliberate gesture from ordinary privacy latch and transaction approval; authenticate with a monotonic device counter, make cancellation idempotent, never delete audit history, and require explicit owner confirmation before clearing the stop state.
- **missing:** A pendant emergency-stop event and persistent stopped-until-cleared state; Relay cancellation fan-out for queued/processing jobs with leases and an idempotent stop receipt; Mac and browser handlers that cancel or quarantine in-flight work instead of merely hiding it; A cross-surface convergence receipt

### "I was offline. Give me one short, ordered list of what happened while I was disconnected, what still needs my decision, and what already finished."
- **useful because:** The system has separate relay jobs, browser results, Mac receipts, pending inbox items, and physical approvals. After a link outage the owner should not reconstruct the story from several status surfaces or risk repeating an action; this is a cross-surface handoff, not another alert queue.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background model for concise ordering and deduplication; deterministic receipt joins and safety labels
- **latency:** Generate on reconnect in under 5 seconds, cache it, and speak only a bounded first 3 items; the full list remains on the dashboard.
- **cost:** <$0.02 per reconnect digest; most work is deterministic joins, with a small summarization call for ambiguous labels.
- **security:** Do not include page contents or secrets in the pendant digest; distinguish completed, failed, awaiting physical approval, and unreachable; bind each item to an opaque job/receipt ID and never auto-resume unrepeatable actions.
- **missing:** A reconnect event and durable last-seen cursor per surface; A typed join over relay jobs, Mac receipts, browser results, pendant inbox, and approval records; A delivery/read receipt so the same digest is not repeated after a restart

### "Keep this conversation and everything derived from it on the Mac; do not send audio, transcript, or inferred facts to the relay until I turn that off."
- **useful because:** The privacy latch is an immediate stop, not a selectable residency policy. A local-only mode would let the owner use the system for sensitive work while retaining local Mac automation and an explicit, inspectable queue of what was withheld, instead of trusting an implicit transport choice.
- **path:** pendant → mac-planner → relay → browser-extension → dashboard
- **model tier:** deterministic routing and redaction policy; background model only for local transcript/fact extraction
- **latency:** Apply before capture starts or any derived record is emitted; status visible within 500 ms. Turning it off requires a physical confirmation and a clear pending-upload count.
- **cost:** No incremental API cost while local-only; local inference cost depends on the selected model. Enabling upload costs the normal audio/transcript pipeline only after confirmation.
- **security:** The policy must be enforced before relay serialization, not as a dashboard label. Browser page contents and secrets remain bound to their target. Local-only artifacts need expiry and a visible discard/export action; never silently backfill the withheld queue when the mode changes.
- **missing:** A signed residency policy state shared by pendant, Mac, and relay; Pre-upload enforcement hooks for audio, transcripts, context extraction, browser evidence, and queued jobs; A local-only status and withheld-artifact inventory with explicit release or deletion

### "Use my logged-in browser to complete this task without showing the page contents to the model; return only the minimum structured fields needed and a proof that the requested state changed."
- **useful because:** Today browser automation generally exposes page text, screenshots, or command results to the agent even when the task only needs a narrow fact. A typed data-minimization boundary would let the owner use authenticated sites while keeping unrelated private page content out of model context and out of relay logs.
- **path:** browser-extension → relay → mac-planner → dashboard → pendant
- **model tier:** deterministic browser policy and schema validation; model sees only the returned typed fields, using a cheaper planner only to map the owner's request to an approved schema
- **latency:** Schema negotiation under 1 second; one browser transaction within the site's normal response time; return a signed receipt within 2 seconds of completion.
- **cost:** Similar to one normal browser action, with lower model/context cost because page contents and screenshots are not transmitted. No additional inference for approved schemas.
- **security:** The owner must approve the domain, operation, and output schema, not merely a natural-language goal. The extension must enforce field-level redaction before relay transmission, reject undeclared fields, prevent secrets from matching generic selectors, and bind the receipt to target URL, schema hash, and resulting state fingerprint. Confirmation remains required for purchases, messages, deletion, and other irreversible writes.
- **missing:** A browser-side typed-operation contract with allowlisted domains, actions, and output schemas; A field-level redaction/enforcement point inside the extension before browser results reach the relay or model; A signed state-change receipt that proves the declared postcondition without retaining page contents; Owner-facing schema/domain grant and revocation controls

### "For the next hour, let you handle only these approved kinds of work, on these sites, under this time and spending limit; stop automatically when any limit is reached."
- **useful because:** Current approval is action-by-action and does not express bounded delegation. The owner cannot safely hand over a routine batch while retaining a hard ceiling on domains, mutations, money, time, and model-visible data.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** deterministic policy evaluation and counters; background model only for translating the owner's spoken limits into a reviewable policy
- **latency:** Create and physically confirm a delegation in under 5 seconds; every action checks limits before dispatch with negligible added latency.
- **cost:** <$0.01 per delegation; persistent counters and signature verification dominate, not model calls.
- **security:** Use an expiring signed capability token scoped to domains, action types, monetary/value ceilings, count, and data classes. Deny by default on ambiguity, make counters monotonic and durable, require physical_transaction_approval_latch to create or broaden a grant, and show a live remaining budget.
- **missing:** A cross-surface capability-token and budget evaluator; Pre-dispatch hooks in relay, Mac, and browser that atomically reserve budget before execution; Owner-facing live budget and revocation controls; Receipts that show each reservation, consumption, and automatic expiry

### "Before you act on my behalf, tell me which private data classes the action would touch, which machine will see them, and let me approve the least-privileged version instead."
- **useful because:** Today risk approval is mostly about reversibility and action type, while privacy exposure can differ radically between two equally reversible actions. The owner needs a concrete data-flow decision, not a generic confirmation that hides whether audio, page contents, contacts, or files will cross surfaces.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** deterministic taint/data-flow analysis; model only converts the result into a short spoken explanation
- **latency:** Produce a compact exposure report in under 1 second for a prepared plan; no action dispatch until the selected least-privilege variant is bound and confirmed.
- **cost:** Negligible incremental API cost; static classification and hashing dominate.
- **security:** Labels must be conservative and fail closed when classification is unknown. Never put raw values into the report or relay logs. Bind approval to the data-flow graph and plan digest, invalidate it if a target, field, or surface changes, and retain only redacted receipts.
- **missing:** Data-class labels and taint propagation across audio, transcript, files, browser fields, and relay records; A planner that can synthesize least-privilege variants instead of merely blocking; Approval binding to a data-flow digest in addition to the existing action/world digests; A dashboard/pendant rendering of exposure classes


## What it asked for

_Nothing._
## Its own summary

Round 200 produced three distinct recorded capabilities: (1) a physical emergency stop that fans out across pendant, relay, Mac, and browser with per-surface convergence receipts; (2) an offline reconnect handoff digest that orders completed, failed, approval-pending, and unreachable work without auto-resuming unsafe actions; and (3) an owner-selectable Mac-local residency mode that blocks serialization/upload before data leaves the device and exposes withheld artifacts. The extracted-fact inventory/erase proposal was correctly rejected as an existing backlog item rather than restated.

**Biggest unknown:** I still need the implementation contracts for the three new capabilities: a relay-wide cancellation event and job lease semantics, reconnect cursors and a typed cross-surface receipt join, and a pre-serialization residency enforcement point. I also need the owner to choose whether local-only mode discards withheld artifacts by default or retains them for explicit release; that is a privacy/product decision, not something to infer.

