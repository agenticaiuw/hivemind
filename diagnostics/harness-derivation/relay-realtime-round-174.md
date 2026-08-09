# Harness derivation — relay-realtime — round 174

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Undo the last thing you did for me."
- **useful because:** The owner can safely experiment hands-free: if a multi-step Mac or browser job produces the wrong result, one spoken command reverses the specific reversible changes instead of forcing them to reconstruct what happened.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension
- **model tier:** Realtime relay identifies the immediately preceding job; a cheaper background planner generates and validates inverse actions from the job receipt; Mac/browser agents execute them.
- **latency:** Acknowledge in under 500 ms; produce the inverse plan in 2–5 s and speak exactly what will be undone before execution when the inverse is not provably safe.
- **cost:** About $0.01–$0.06 per undo, dominated by planner calls and receipt retrieval; trivial relay storage.
- **security:** Only actions with recorded, typed inverse operations may be auto-undone. Never claim success without post-state verification. File deletion, sent messages, purchases, and external side effects are non-undoable and must be reported plainly rather than simulated.
- **missing:** A durable inverse-action field for every /plan and /execute action; A rollback endpoint that runs inverse actions in reverse order; Post-rollback state verification and an explicit non-undoable classification

### "Why did you say that, and let me hear the evidence."
- **useful because:** When away from the Mac, the owner can distinguish a measured fact from an inference: the pendant reads a short spoken explanation tied to the exact browser page, Mac state, timestamp, and action receipt, rather than trusting an opaque answer.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Realtime relay handles the follow-up and summarizes; faculty-perception or a cheaper background model extracts a few quoted evidence spans and confidence; no expensive reasoning is needed unless sources conflict.
- **latency:** Answer the follow-up in 1–3 s when evidence is already captured; re-query a surface only when the evidence is stale.
- **cost:** Usually $0.005–$0.03 per follow-up, dominated by fetching and summarizing source snippets; no continuous capture.
- **security:** Speak only source text and metadata the owner is authorized to hear. Redact secrets and avoid reading an entire private page aloud. Preserve immutable source hashes/timestamps so a later explanation cannot silently change.
- **missing:** An evidence bundle attached to every spoken claim and job receipt; A relay endpoint that retrieves source snippets by claim ID; A pendant interaction for 'why' that does not discard the current conversation

### "Keep a live watch on this exact thing and tell me only when it materially changes, even if my Mac is asleep."
- **useful because:** The owner gets genuinely unattended monitoring of a chosen authenticated browser view or Mac artifact, with concise wearable alerts only for meaningful changes, rather than repeatedly asking or leaving a laptop awake.
- **path:** pendant → relay → browser-extension → mac-planner → dashboard
- **model tier:** A durable relay worker performs cheap hash/DOM/metadata comparisons; a slower model classifies significance only for changed snapshots; realtime is used only to deliver or explain an alert.
- **latency:** Detect within 1–5 minutes for browser watches and within 30 seconds when the Mac is online; speak a two-sentence alert immediately after classification.
- **cost:** Roughly $0.01–$0.10 per material change; polling and hashing dominate infrastructure, model spend occurs only on diffs.
- **security:** Authenticated page content must remain in the owner’s browser session or encrypted relay storage, with retention limits and per-watch revocation. Never alert on every cosmetic change; include the changed field and source timestamp so stale data is obvious.
- **missing:** A real relay scheduler/ Durable Object alarm and durable watch state; A browser-side snapshot/diff protocol that works while the Mac is offline or asleep; Semantic diff classification, deduplication, quiet hours, and delivery through the existing pendant inbox

### "Make this authenticated site available to you even when my Mac is asleep, but do not expose my session to anyone else."
- **useful because:** The owner can ask the pendant for a current answer from a private work or household portal without leaving a Mac awake; the browser session remains deliberately paired to this owner and can be revoked.
- **path:** pendant → relay → browser-extension → dashboard
- **model tier:** Relay handles low-latency requests; a slower browser worker fetches only the pinned origin and extracts the requested fields, with no general-purpose model access to the session.
- **latency:** First escrow setup under 30 seconds; ordinary reads under 5 seconds; stale-session or reauthentication failures spoken immediately.
- **cost:** $0.01–$0.10 per read, dominated by remote browser execution; encrypted session storage and refresh traffic are the infrastructure cost.
- **security:** Session cookies/tokens must be hardware- or owner-key encrypted, origin-bound, never placed in model context, and auto-expire. The owner must explicitly pin and revoke an origin. Mutations remain unavailable in escrow mode; reads are logged with origin and timestamp.
- **missing:** A Cloudflare/browser worker with encrypted session escrow and origin isolation; A browser-extension pairing flow to transfer a session without exposing cookies to the relay model; Per-origin revocation, expiry, reauthentication, and audit UI

### "Before you change anything, tell me exactly what will be different when you finish."
- **useful because:** For a command that touches several apps, the owner hears a concrete before/after diff—files, calendar entries, tabs, or settings—rather than a vague promise, while still keeping the maximum-access policy and not forcing a confirmation gate.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** A cheap planner computes a predicted state diff from the action plan; downstream agents collect the actual post-state; realtime relay speaks only the compact diff.
- **latency:** Predicted diff within 2 seconds for a short plan and actual diff within 5 seconds after execution.
- **cost:** $0.01–$0.05 per compound command, mostly post-state reads; no extra cost for simple actions.
- **security:** Diffs must omit secret values and distinguish prediction from observation. If verification cannot establish the post-state, say so rather than claiming the change happened.
- **missing:** A typed precondition/postcondition schema on /plan actions; Snapshot adapters for files, apps, browser tabs, and calendar state; A compact spoken-diff renderer and receipt linkage


## Changes it proposed to its own stack

### `interaction` — Add a spoken, session-scoped 'focus contract' that the owner can set at the beginning of a task: goal, forbidden apps/origins, maximum duration, and what counts as completion. Relay injects the contract into every downstream plan and rejects drift; the pendant can say 'contract status' at any time.
- **owner gets:** Long computer tasks stop wandering into unrelated work. The owner can give a short goal while walking away and later hear whether it is complete, blocked, or still within scope.
- effort: Medium-high: contract parser, durable session state, planner/execute enforcement, and a pendant status utterance.  ·  risk: An over-broad or stale contract could prevent a legitimate action; allow the owner to replace it by voice and expire it automatically. Recovery is to stop the job and return its receipt.
- cost: About $0.005–$0.03 per task for parsing and status; negligible storage.  ·  latency: Less than 300 ms to attach the contract; up to one extra planner-context read per downstream step.
- security: Improves least-context exposure by limiting origins/apps and provides an audit boundary, but contract contents must be encrypted with the job record.
- depends on: A durable per-session state record; Planner support for explicit scope constraints and drift events; A relay status path that can speak contract state


## What it asked for

_Nothing._
