# Harness derivation — relay-realtime — round 106

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If I ask you to do something on my computer, keep track of it and tell me how it’s going, even if my Mac goes to sleep.”"
- **useful because:** The owner can fire-and-forget tasks and still get clarity later. It reduces anxiety and repeated commands, and it works with the reality that the pendant is worn while the Mac is often unattended.
- **path:** pendant → relay → mac-bridge → mac-planner → dashboard
- **model tier:** Realtime only for the spoken status request; planning and execution run on the Mac planner. Status summarization can use a cheaper model if available since it’s not time-critical.
- **latency:** Status check should respond in under a second when the relay has a record. If the Mac must be consulted, it becomes best-effort and should say it’s waiting.
- **cost:** Cheap when using relay job records (single read). More expensive only when it requires Mac planner status or receipts.
- **security:** Job summaries may include app names, file paths, or browser session details. Keep summaries minimal and avoid leaking content unless the owner asked for it. Never claim completion unless a receipt indicates completion.
- **missing:** A durable relay job ledger that survives restarts and stores: job id, target, submission time, last known state, and a short spoken summary.; An implemented relay_job_status tool or equivalent route that reads the ledger and returns a spoken string.; A job status ingestion path where the Mac planner posts updates/receipts back to the relay.

### "“Take the thing I’m looking at in my browser right now, put the useful excerpt and link into a note on my Mac, and tell me when it’s done.”"
- **useful because:** The owner is often wearing the pendant away from the Mac while authenticated browser context is on another surface. This turns a spoken request into a provenance-preserving handoff from the currently focused browser tab to a durable Mac artifact, without requiring the owner to repeat a URL, copy text, or return to the desk. It is meaningfully cross-node: only the browser has the private page and selection, while only the Mac can create the owner-visible note and the relay can coordinate and report completion.
- **path:** pendant → relay → browser-extension → mac-planner → dashboard
- **model tier:** Realtime relay performs intent extraction and a short spoken acknowledgement; browser extraction and Mac note formatting use a cheaper background model or deterministic extraction. The relay should not summarize expensive content itself unless the owner explicitly asks.
- **latency:** Acknowledge immediately (<500 ms); capture the focused tab/selection within 3 s; create the note and speak completion within 8 s. If either surface is offline, persist a correlated pending handoff and report the exact missing surface rather than pretending success.
- **cost:** Roughly $0.002–$0.02 per invocation depending on whether summarization is requested; dominated by optional background summarization and not the short realtime turn. Deterministic title/URL/selection transfer is near-zero model cost.
- **security:** The browser may expose authenticated, sensitive content, so transfer only the focused tab and explicit selection when present, never all tabs by default. Keep source URL, capture timestamp, and originating session in the note for auditability; redact passwords, payment fields, and page secrets. Creating a local note is reversible and should not require confirmation under owner policy, but the spoken result must distinguish captured text from a generated summary.
- **missing:** A browser-extension command that returns focused-tab metadata plus user selection/reader text with a strict single-tab scope; A relay handoff record that stores source/session correlation and survives a dropped pendant or Mac link; A Mac planner action for creating a note artifact with source URL, capture time, excerpt, and optional summary; End-to-end receipt propagation so the pendant can say queued, completed, or failed with the actual reason; A dashboard view for pending handoffs and their source/target receipts

### "“What exactly did you change across my Mac and browser in the last few minutes, and show me the source for each claim?”"
- **useful because:** Today receipts and browser results are fragmented by surface, while the owner hears only a short realtime reply. A spoken, evidence-linked change ledger would let the owner audit what happened while away from the desk: distinguish observation from mutation, identify the originating tab/app, and recover the exact result or failure without asking each agent separately. This is not an approval gate; it is post-action accountability and debugging.
- **path:** pendant → relay → browser-extension → mac-planner → mac-vision → dashboard
- **model tier:** Use deterministic receipt joining and source IDs first; use a cheaper background model only to turn the joined ledger into a concise explanation. Realtime is limited to answering the spoken audit question and should not re-run actions.
- **latency:** Speak a first answer in under 1.5 s from cached receipts; fetch missing browser/Mac evidence within 5 s. If evidence is unavailable or expired, say so explicitly and provide the correlation ID rather than hallucinating a narrative.
- **cost:** Near-zero for joining typed receipts; approximately $0.001–$0.01 when natural-language compression is needed. Storage and dashboard indexing dominate infrastructure cost, not inference.
- **security:** Receipts may contain private URLs, document names, or snippets. Encrypt at rest, scope retrieval to the owner/session, and avoid replaying page contents aloud unless requested. Preserve immutable raw evidence separately from the redacted spoken summary. Never claim a mutation based solely on a plan receipt.
- **missing:** A common receipt schema spanning Mac actions, browser commands, relay replies, and source observations; A durable cross-surface correlation/ledger query, including causal links from intent to plan to execution to result; Typed evidence labels separating observed, planned, executed, and verified states; A spoken audit formatter that can cite an app/tab and timestamp without reading secrets by default; Dashboard filtering and retention controls for the ledger

### "“Compare the deployment/status page I’m signed into with the project state on my Mac. Tell me only what disagrees, with the evidence from both sides, and don’t change anything.”"
- **useful because:** The browser session can see private dashboards and the Mac can inspect local repositories, processes, and configuration, but neither surface alone can establish whether the two views agree. A read-only cross-surface consistency check catches stale deployments, wrong branches, and misleading dashboards while the owner is away from the desk. It is an answer neither node can produce independently.
- **path:** pendant → relay → browser-extension → mac-planner → mac-terminal → dashboard
- **model tier:** Use deterministic extraction for known fields (URLs, commit hashes, timestamps, environment names, service states). A cheaper background model normalizes and compares heterogeneous evidence; realtime only disambiguates the target and reads the short discrepancy report.
- **latency:** Acknowledge and identify the target in under 1 s; gather both sources in under 6 s; return a discrepancy-only spoken result in under 10 s. If one source cannot be reached, report an incomplete comparison and never infer agreement.
- **cost:** Approximately $0.003–$0.03 per check, dominated by optional normalization of page text and terminal output. Structured field comparison is effectively free; repeated checks should cache immutable evidence by URL/commit/time.
- **security:** The browser page and local repository may contain credentials or proprietary code. Request only the focused tab and allowlisted read-only project metadata/commands; pass hashes, statuses, and bounded excerpts rather than full source. Keep evidence scoped to the owner and include freshness timestamps. No mutation is performed.
- **missing:** A user-selectable comparison profile mapping a browser page to a Mac project/environment; Browser extraction of named fields from the focused authenticated page with citations; Mac-terminal read-only probes that return typed project identity, branch, commit, and service status; A normalization/comparison worker that reports disagreement, stale evidence, and missing fields separately; A single spoken response format with links/citations and a dashboard evidence view


## What it asked for

_Nothing._
## Its own summary

I re-discovered the available tools, surfaces, and routes, and confirmed the newly granted relay-side tools are schemas without implementations. I also identified a useful owner-facing capability: reliable job status tracking and spoken updates from the relay even when the Mac is asleep. The connective tissue is missing: a durable relay job ledger, implemented status reads, and a status ingestion path from the Mac.

**Biggest unknown:** Whether the relay already has any implemented internal routes for job tracking, announcements, or state that aren’t visible through the Mac route table. I can only probe for these if I know likely paths or get a manifest/context describing the relay’s own surface.

