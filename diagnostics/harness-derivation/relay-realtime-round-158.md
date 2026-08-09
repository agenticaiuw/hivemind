# Harness derivation — relay-realtime — round 158

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Remember this exactly; later, when I ask about that thought or phrase, find the original recording and tell me the surrounding context.”"
- **useful because:** The owner can capture fleeting ideas while away and reliably recover the exact source later, rather than getting only a lossy memo or an untraceable summary. This turns the pendant into durable personal memory with provenance.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Realtime for immediate capture acknowledgement and a short transcript; background model for transcription, embedding, deduplication, and retrieval summaries.
- **latency:** Acknowledge within 500 ms; indexing may take seconds; retrieval spoken response under 2 seconds when the Mac is online and under 5 seconds from relay storage.
- **cost:** About $0.01–$0.05 per minute of captured audio depending on transcription/embedding provider; storage and retrieval dominate at scale.
- **security:** Voice and transcript leave the pendant and become searchable personal data. Encrypt at rest and in transit, retain the original plus provenance, and never expose a memory to browser/Mac actions without an explicit retrieval request.
- **missing:** A relay-owned encrypted memory store with chunked audio, transcript, timestamps, embeddings, and provenance; A retrieval endpoint that can return exact source clips and confidence-ranked context; Mac-side import/export and deletion controls so the owner can inspect and erase memories

### "“What changed across my open work tabs and Mac project since I last checked, and what actually needs my attention?”"
- **useful because:** The owner gets a single, cited delta instead of manually reopening tabs, comparing documents, and reconstructing what happened while they were away. It combines the browser’s authenticated view with local project state and filters noise into actionable changes.
- **path:** pendant → relay → browser-extension → mac-planner → faculty-perception
- **model tier:** Background perception jobs snapshot and diff content with a cheaper model; realtime only compresses the resulting evidence into a spoken answer.
- **latency:** Snapshot/diff in 10–30 seconds; spoken summary in under 3 seconds after the owner asks. If a source is unavailable, say which one rather than silently using stale data.
- **cost:** Roughly $0.02–$0.15 per check, dominated by page/document extraction and model context; hashes and local diffs keep unchanged sources cheap.
- **security:** Authenticated page content and local project text cross the relay boundary. Store only hashes, excerpts, and citations by default; require explicit opt-in for full-content retention and isolate unrelated tabs/projects.
- **missing:** A durable per-source baseline with timestamps, hashes, and user-selected scope; A unified diff service for browser pages and Mac files/apps with citations; A prioritization policy that distinguishes actionable changes from routine churn

### "“Take over this task across my Mac and authenticated browser; keep going through ordinary obstacles, and only come back to me when you need a fact or a choice I cannot delegate.”"
- **useful because:** Today a task that crosses apps, browser sessions, and intermittent connectivity fragments into separate commands. This would let the owner delegate an outcome while the hive maintains a live, intelligible handoff and resumes after recoverable failures, even though the owner is away from the Mac.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-judgement → faculty-action
- **model tier:** mac-planner handles planning and ordinary recovery; mac-vision handles visual ambiguity when enabled; realtime speaks only concise checkpoints and asks targeted questions; a cheaper background worker supervises long jobs.
- **latency:** Immediate spoken acceptance under 1 second; progress events on meaningful state changes; recoverable failures retried within 30 seconds; owner questions time out safely without losing the job.
- **cost:** $0.05–$0.50 per delegated task, dominated by planner/vision turns and browser extraction; retries should be capped and cached.
- **security:** This can mutate external systems and use authenticated sessions. Preserve action receipts, exact evidence, resumable checkpoints, and an owner-visible audit trail; never claim completion without a verifiable result. Data leaves the Mac only as needed for planning.
- **missing:** A durable workflow runner with checkpoints, retry classification, and resumable cross-surface jobs; A real relay-to-Mac event channel that can push state and questions to the pendant; A unified action/evidence schema spanning Mac, browser, and relay, plus mac-vision re-enablement for visual blockers


## What it asked for

_Nothing._
