# Harness derivation — relay-realtime — round 68

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Route this to the right place and keep me posted on progress."
- **useful because:** It lets the owner speak naturally on the pendant and have the system pick the right downstream agent, then report status later even if the Mac goes to sleep.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** Realtime only for intent capture and immediate clarification; mac-planner for multi-step work; cheaper backend models for status summarization.
- **latency:** Under a second to acknowledge and choose a route; progress updates can arrive later.
- **cost:** Low per intent; dominant cost is downstream planning/execution, not the relay decision.
- **security:** The relay should not invent actions; it should only forward intent and minimal context. Status should be read-only.
- **missing:** A consistent, discoverable tool registry that includes relay-only tools like intent routing and server-side browser automation.; Durable job tracking that works across relay and Mac even when devices sleep.

### "“Stop that,” or “Change the last request to …” while the Mac or browser is still working, and have the running job halt safely and resume with the corrected request without me repeating all the context."
- **useful because:** Today the pendant is a low-latency front door, but once it hands work to a planner or browser queue the owner has no reliable conversational interrupt or amendment path. This matters because the owner is usually away from the Mac: a mistaken click, stale goal, or newly remembered constraint can otherwise continue unattended. It is a genuinely cross-node capability: the pendant must recognize and correlate the interruption, the always-on relay must own the live job state, the Mac planner/computer-use loop or browser session must cooperatively cancel at safe checkpoints, and the relay must report the resulting receipt back over voice.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → browser → dashboard
- **model tier:** Realtime handles only the short interrupt/amendment recognition and spoken acknowledgment. A cheaper background model may normalize the replacement goal and summarize the cancellation receipt; downstream planners retain responsibility for action planning.
- **latency:** Acknowledge “stopping” within 300 ms; cancellation request reaches the active worker within 1 s. If an operation is non-interruptible, say so immediately and report its eventual receipt rather than claiming it stopped.
- **cost:** Approximately one realtime turn (about $0.01–$0.05 depending on audio duration), plus negligible relay storage/traffic. Background re-planning should use the cheaper planner tier; the dominant cost is speech inference, not the control messages.
- **security:** The relay must bind an interrupt to the owner’s authenticated active voice session and exact job id, never cancel an unrelated household job. Cancellation cannot undo an already-committed external side effect, so the spoken response must distinguish requested, halted, completed, and partially completed. Replacement goals should inherit only explicitly retained context, with a concise spoken recap of what will now be sent. Store short-lived transcripts and receipts with expiry.
- **missing:** A first-class job-control protocol shared by relay, mac-planner, mac-vision, and browser-extension: correlation ids, cancel/amend states, idempotency, safe checkpoints, and typed receipts.; Worker-side cancellation propagation for Mac actions and browser actions, including a cooperative stop endpoint and an explicit non-interruptible state.; Relay voice-session state that keeps the active job and its compact context across turns without resending the full transcript.; A pendant-facing spoken status/receipt event channel for completion, partial completion, and cancellation failure.; Dashboard visualization and test harness scenarios for interrupt races (cancel versus completion, duplicate stop, offline Mac, and amended intent).

### "“What did you do about the invoice I mentioned yesterday?” or “Open the page and file you used for that,” and get a concise, cited answer with the related Mac/browser artifacts and any available undo or follow-up action."
- **useful because:** Existing history and receipts can record individual operations, but the owner cannot presently recall a human conversation or task and have the relay connect it to evidence read in an authenticated browser, files opened on the Mac, actions taken, and the final outcome. A durable action lineage would make the hive understandable and recoverable rather than a stream of opaque jobs. It requires all surfaces: the pendant supplies the natural-language reference, relay resolves it cheaply against an indexed task graph, Mac and browser agents emit artifact and evidence edges, and the dashboard exposes the same lineage for inspection.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → browser → dashboard
- **model tier:** Use embeddings/structured indexes and a cheap background model for candidate retrieval and clustering. Realtime is needed only to turn the selected lineage into a short spoken answer or to route a requested follow-up; do not resend full historical context to the expensive tier.
- **latency:** Return the top matching task and a one-sentence status in under 1.5 s for indexed history. Loading cited artifacts may take up to 5 s and should be spoken as a separate progress event.
- **cost:** Low ongoing storage/index cost; roughly $0.001–$0.01 per recall using embeddings or a small model, with occasional background summarization. Realtime cost is limited to the brief spoken query and response.
- **security:** Lineage may contain sensitive mail, work-portal titles, URLs, and file paths. Encrypt it, enforce the owner/session identity, retain only compact metadata plus user-approved evidence excerpts, and never read a private artifact aloud without saying what source it is. Cross-origin links must preserve browser-session boundaries; deleting a source should tombstone its lineage edges.
- **missing:** A shared task-lineage schema with request ids, semantic labels, evidence citations, artifact identifiers, action receipts, outputs, and retention/tombstone semantics.; Mac and browser instrumentation that emits signed evidence/artifact edges rather than only free-form completion text.; A relay-side encrypted lineage index and natural-language resolver with compact context projection.; Read-only deep-link/open-artifact adapters for Mac and authenticated browser tabs, with failure states when a session or file is unavailable.; Dashboard views and automated tests for cross-surface joins, deletion, stale links, and ambiguous references.


## What it asked for

_Nothing._
## Its own summary

Discovered the currently shipped tools, granted items, devices, and surfaces. New tools appear in the granted list, but they are not consistently discoverable/describable via the same registry; relay_job_status is documented and available. Proposed a capability centered on spoken intent routing plus progress reporting across sleeping devices.

**Biggest unknown:** I still need a reliable way to discover and describe relay-only tools (like intent routing and server-side browser actions) through the standard discovery mechanism, plus durable cross-surface job tracking if progress updates are expected when devices sleep.

