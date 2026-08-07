# Harness derivation — relay-realtime — round 38

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Keep working after I stop talking, then tell me what happened when it’s done."
- **useful because:** The owner can start a task on the go, walk away, and still get a clear outcome later without babysitting the Mac or browser.
- **path:** relay → mac-bridge → browser
- **model tier:** Realtime only acknowledges; planning and execution happen on the Mac/browser tier.
- **latency:** Fast spoken acknowledgment (under a second), then background progress that can complete minutes later.
- **cost:** Low per voice ask at the relay; most cost accrues on Mac/browser execution and any authenticated page reads.
- **security:** May touch authenticated accounts. Must log evidence and avoid claiming completion without receipts. No hidden submissions; approvals only when required by policy.
- **missing:** Durable background job runner (queue + storage); Reliable server-push or polling notification path to pendant; Typed receipts for browser operations comparable to mac receipts; A unified progress vocabulary across Mac and browser jobs

### "“What exactly happened after I asked you to do that?” Give me a trustworthy, spoken timeline across the pendant, relay, Mac, and authenticated browser—including what was attempted, what actually changed, source links or evidence, failures, and the precise way to undo each reversible change."
- **useful because:** Today receipts and logs may exist in separate surfaces, but the owner cannot obtain one coherent, evidence-backed account of a cross-device operation. This would make an autonomous system legible after the fact without requiring them to inspect a dashboard or remember which machine acted.
- **path:** pendant captures the natural-language audit request and reads back a concise answer → relay correlates the request/session and fans out read-only evidence queries → mac-planner and mac-terminal return typed action results, diffs, and local undo handles → browser-extension returns authenticated-tab actions, URLs, and before/after evidence without exposing page secrets → relay produces a chronological, confidence-labeled spoken summary and can hand an explicitly named undo operation back to the relevant node
- **model tier:** Use the realtime tier only to understand the short spoken audit question and narrate the result; use a cheaper background model to normalize receipts, correlate timestamps/request IDs, detect contradictions, and draft the timeline. No autonomous model should infer success from intent alone.
- **latency:** A first acknowledgement in under 500 ms; evidence aggregation within 3–8 seconds for recent work, with progressive spoken updates if Mac or browser is offline. Historical searches can be asynchronous and notify the pendant when complete.
- **cost:** Roughly one low-token realtime turn plus a cheap background summarization call; dominant cost is receipt retrieval and context size, not inference. Indexing compact typed receipts avoids resending full transcripts or page contents.
- **security:** This is read-only by default but may reveal sensitive URLs, file names, and authenticated-work context over LTE/audio. Return redacted evidence and explicit provenance, retain opaque receipt IDs rather than secrets, and require the owner to name a specific receipt/change before offering an undo; never replay credentials or page bodies into speech.
- **missing:** A durable, cross-surface receipt schema with request ID, actor, timestamps, pre/post state, evidence pointers, failure reason, and reversible undo handle; A relay-side correlation/index service that joins pendant utterances to Mac and browser request IDs and supports offline nodes; Mac and browser adapters that emit before/after evidence and stable undo operations rather than only free-form completion text; A spoken progressive-results protocol and redaction policy for sensitive authenticated-browser evidence; An owner-facing receipt retention/expiry policy and a resolver that can route a named undo to the original acting node

### "“Privacy panic—stop everything and tell me what is still exposed.” From the pendant, immediately halt pending automation, lock the Mac, suspend browser command queues and authenticated sessions, then report what was stopped, what could not be stopped, and which active sessions or artifacts remain."
- **useful because:** The owner is often away from the Mac and cannot reach a keyboard when a sensitive action goes wrong. Existing per-operation receipts do not provide a single, wearable-triggered containment action spanning the relay, unattended Mac, and session-holding browser.
- **path:** pendant uses a deliberate button gesture or spoken phrase and gives immediate LED/audio acknowledgement → relay enters a durable emergency-stop state, rejects new delegated work, and tracks acknowledgements from each node → mac-planner/mac-terminal lock the workstation, cancel queued jobs, and return process/job state without deleting user work → browser-extension revokes or pauses command queues and closes/revokes supported authenticated sessions, returning session identifiers and residual-risk evidence → relay speaks a short containment report and later delivers a detailed receipt when all nodes reconnect
- **model tier:** No expensive reasoning is needed for the stop path: deterministic relay and node handlers execute immediately. Use a cheap background model only to summarize residual exposure after containment; realtime narrates acknowledgement and exceptions.
- **latency:** Pendant acknowledgement under 300 ms; relay stop state under 1 second; reachable Mac/browser containment within 2–5 seconds. Offline nodes must receive and apply the stop before accepting any subsequent work.
- **cost:** Negligible per event aside from a small realtime narration and optional low-cost residual-risk summary. The main cost is engineering durable state and reliable reconnect handling.
- **security:** The trigger must resist accidental activation while remaining usable under stress (e.g. long press plus spoken phrase, or a distinct button sequence). Store no credentials on the pendant; transmit only a signed emergency-stop token. Revocation can disrupt work and sign out sessions, so report exactly what occurred and preserve undo/reconnect instructions where safe, but never delay containment for confirmation.
- **missing:** A signed, idempotent emergency-stop token and durable relay kill-switch state honored by every worker; Mac adapter for lock/cancel/status and browser adapter for queue suspension/session revocation; Pendant firmware support for a deliberate offline-capable trigger and acknowledgement pattern; A reconnect protocol guaranteeing a node applies the newest stop epoch before accepting work; A residual-exposure inventory and safe spoken redaction layer


## What it asked for

_Nothing._
