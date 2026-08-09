# Harness derivation — relay-realtime — round 271

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Bookmark this moment and attach it to what I’m working on.”"
- **useful because:** The owner can capture a quick thought while away from the Mac and later find the exact file, tab, or project state it refers to, without rummaging through notes.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** Realtime for capture; mac-bridge/browser for context binding; cheaper tier for indexing/search later.
- **latency:** Under a second to confirm capture; binding may take a few seconds depending on Mac/browser state.
- **cost:** Low ongoing cost. The main cost is capturing context snapshots (browser tabs, open files) when binding, which should happen only when the owner asks.
- **security:** Context binding can expose sensitive URLs, document paths, or content. Store minimal references (IDs, titles, hashes) and require confirmation before including sensitive text.
- **missing:** A typed capture payload that can represent voice memo, bookmark, or text note as items in the existing outbox/inbox queue; Reliable context snapshot/restore for browser and workspace state; A unified index so voice search can find captures by project/task

### "“Move this conversation and unfinished task to my Mac when I sit down, without making me repeat anything.” The pendant should hand an active voice task to the Mac, where the owner can continue it with the exact spoken context, discovered artifacts, pending plan, and current uncertainty."
- **useful because:** The pendant is the only surface available while away and the Mac is the only surface with rich control. Today the owner must restart or remember what was said; a true task baton would make the system feel like one assistant rather than disconnected sessions.
- **path:** pendant → relay → mac-planner → mac-vision → browser → dashboard
- **model tier:** Realtime model handles the short handoff summary and spoken continuity; mac-planner performs the work; mac-vision/browser supply current UI state; a cheaper background model can compress the transcript and artifacts.
- **latency:** Handoff acknowledgement under 2 seconds; Mac rehydration under 10 seconds after the Mac is detected. The owner should hear one sentence immediately, not wait for the whole task.
- **cost:** About one realtime turn for the handoff plus a cheap summarization call, typically under $0.03; the dominant cost is rehydrating large browser/UI artifacts, which should be content-addressed rather than resent.
- **security:** The baton must be bound to the owner’s paired devices and expire. It must carry artifact references and action scope, not blindly replay credentials or stale UI actions. The owner should be able to revoke a baton from the pendant or dashboard; no new confirmation gate is required for reversible work.
- **missing:** A paired-device presence/discovery signal that can announce the Mac is available; A durable handoff record containing transcript, artifact references, plan, and uncertainty; Mac-side session rehydration that can resume a task rather than start a new planner run; A continuation UI on the Mac and a compact pendant acknowledgement

### "“Keep working until you hit a real ambiguity, then ask me exactly one useful question.” The assistant should run a multi-step Mac/browser task autonomously, pause only when observations create materially different next actions, speak the smallest discriminating question through the pendant, and resume with the answer."
- **useful because:** Long tasks fail today either by guessing through ambiguity or by dumping a whole plan on the owner. This would let the owner stay away from the Mac while still steering the few decisions that genuinely require human intent.
- **path:** pendant → relay → mac-planner → mac-vision → browser → dashboard
- **model tier:** mac-planner does ordinary planning and execution; mac-vision/browser provide observations; realtime is used only for the short ambiguity question and answer normalization; a cheaper judge model scores whether a question is actually decision-changing.
- **latency:** Continue automatically for ordinary steps. When blocked, surface a question within 3 seconds and resume within 5 seconds of the owner’s reply.
- **cost:** One inexpensive judge call per suspected ambiguity and one realtime exchange only when needed, roughly $0.01–$0.05 per task; savings come from not invoking realtime for routine progress.
- **security:** The system must show the evidence that caused the pause and record the selected branch. It must distinguish ambiguity from a high-impact action; this is an interaction mechanism, not an authorization gate. Stale observations must invalidate the pending question rather than silently applying the answer to a changed page.
- **missing:** A planner protocol for typed pause/resume checkpoints with competing branches and evidence; A relay-to-pendant question/answer exchange that survives the normal turn ending; A stale-observation/version check across Mac and browser actions; A compact owner-visible decision log

### "“At the end of the day, tell me what actually changed because of my assistant, what is still uncertain, and let me correct the record by voice.” The system should build an evidence-backed personal activity ledger from Mac action receipts, browser outcomes, relay conversations, and offline pendant notes, then speak a concise discrepancy-focused digest."
- **useful because:** The owner currently has scattered logs and no trustworthy answer to “what did it do?” or “what did I tell it that it failed to do?”. A ledger with provenance and corrections would make automation accountable and improve future decisions without pretending that an attempted action succeeded.
- **path:** pendant → relay → mac-planner → mac-vision → browser → dashboard
- **model tier:** A cheap background model clusters receipts and detects contradictions; realtime only conducts the short spoken review and applies explicit corrections; Mac/browser agents remain sources of evidence, not narrators of their own success.
- **latency:** Generate asynchronously in under a minute after the chosen cutoff; spoken review should begin in under 2 seconds when requested and fit in 30–60 seconds unless the owner asks for detail.
- **cost:** Usually one background summarization call, about $0.01–$0.05 per digest; storage/indexing and receipt normalization dominate engineering cost, not inference.
- **security:** Every claim needs provenance, timestamp, target surface, and confidence. Private browser content must be excluded unless explicitly included; corrections must be versioned rather than overwrite evidence. The digest should clearly separate completed, attempted, failed, and unknown.
- **missing:** A cross-surface append-only activity ledger joining voice turns to Mac/browser job IDs; Receipt normalization and contradiction detection; A user-correction endpoint that creates scoped memory facts with provenance; A routine trigger and durable spoken delivery using the existing inbox semantics


## What it asked for

_Nothing._
