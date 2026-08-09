# Harness derivation — relay-realtime — round 279

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I say a command, turn it into a safe, typed action plan and show me what you’re going to do before doing it."
- **useful because:** It reduces surprises and makes the system feel trustworthy. The owner gets clarity without losing speed.
- **path:** relay → mac-bridge → mac
- **model tier:** realtime to draft the plan, then mac planner for execution
- **latency:** Draft under 1–2 seconds; execution follows after owner approval.
- **cost:** Moderate only when used; planning tokens dominate.
- **security:** Plan text may reference files or apps. Keep it minimal and avoid exposing secrets in spoken output. High-impact steps still need confirmation.
- **missing:** A real routed intent tool (relay_route_intent is unresolved).; A plan-preview step in the relay that can be spoken and confirmed.; Consistent typed action schema exposed by the relay surface.

### "Record a voice bookmark when I press the button, then later help me find it on my Mac by context, like time or what I was doing."
- **useful because:** This makes the pendant a capture tool, not just a talking remote. It turns fleeting thoughts into findable context.
- **path:** pendant → relay → mac
- **model tier:** realtime for capture, cheaper model for indexing/search later
- **latency:** Capture immediate; indexing and search can be async.
- **cost:** Low per capture; storage and indexing cost grows with usage.
- **security:** Bookmarks can contain sensitive content. Keep local by default and require explicit share/export.
- **missing:** A bookmark item type in the existing outbox queue rather than a new queue.; Indexing and search on the Mac side for bookmarks.; UI/voice flow to list and open matches.

### "Keep a rolling, privacy-safe context of what I’m working on across devices so you can help without me repeating myself."
- **useful because:** It lowers friction and makes the assistant feel present without being nosy. The owner benefits from continuity.
- **path:** relay → mac → browser → memory
- **model tier:** cheaper model to maintain context; realtime only uses a small projection
- **latency:** Projection retrieval under a second, updates async.
- **cost:** Saves tokens per turn by reducing context size; storage cost modest.
- **security:** Context must be scoped to surface and task; sensitive facts shouldn’t leak across surfaces.
- **missing:** Wire the existing projection into the live conversation context path.; Task-scoped hints from the relay to select the right projection slice.; Instrumentation to measure token savings in production.

### "“Finish this for me even if the Mac, browser, or iPhone drops out halfway; pick up from the last confirmed step and tell me only when it is done or genuinely blocked.”"
- **useful because:** Today a compound request can be planned or delegated, but a partial failure leaves the owner reconstructing state and repeating instructions. A durable cross-surface transaction would make the pendant a dependable remote operator rather than a one-shot voice command: it can resume on reconnection, avoid repeating completed mutations, and report the exact blocker.
- **path:** pendant → relay → mac-planner → browser-extension → ios → dashboard
- **model tier:** Use relay-realtime only to acknowledge and classify; use mac-planner/background workers for planning, checkpoint reconciliation, and retries, with mac-vision or browser-extension only for the affected step.
- **latency:** Immediate acknowledgement under 1 second; checkpoint updates opportunistically; final result within the time the underlying task requires, including after hours offline.
- **cost:** Low conversational cost (one short realtime turn); background cost is dominated by replanning only after a failed or stale checkpoint, not every retry.
- **security:** A replay-safe action ledger must distinguish confirmed mutations from proposed actions and attach idempotency keys; the owner’s existing maximum-access policy remains, while destructive ambiguity is surfaced as a blocker rather than silently replayed. Only task-relevant context should leave the relay.
- **missing:** Durable checkpointed transaction state with per-action idempotency and receipts; A worker/alarm that retries and reconciles jobs after the Mac reconnects; A unified handoff format spanning mac-planner, browser-extension, and ios-control; Pendant/inbox delivery of the final checkpoint outcome

### "“What am I looking at on my Mac right now, and if it is an error, tell me the next safe thing to try?”"
- **useful because:** The pendant is the only always-available voice front door, but today it cannot answer questions about the owner’s current screen without the owner manually describing it. A screenshot/vision handoff would turn vague spoken requests into grounded help: identify the visible error, read the relevant UI, and explain it aloud without forcing the owner to switch devices.
- **path:** pendant → relay → mac-vision → mac-planner → dashboard
- **model tier:** Use relay-realtime for the short spoken answer; use the cheaper computer-use/vision tier for screenshot inspection and mac-planner only when the owner asks for a reversible follow-up action.
- **latency:** Capture and first grounded answer in 3–8 seconds; a one-sentence answer first, with optional deeper explanation on request.
- **cost:** One vision invocation plus one short realtime response per question; cost is dominated by the screenshot model, and no vision call is made for ordinary voice turns.
- **security:** The screenshot may contain passwords, private messages, or financial data. Keep it in the Mac/relay job path, retain no image after the result unless explicitly requested, and expose the source window/app and capture timestamp in the spoken or dashboard receipt. Any click/type follow-up must be separately represented as an action.
- **missing:** A live screenshot/selected-window capture route exposed to the relay; Re-enable or provide the mac-vision computer-use loop with image input; A redaction/retention policy for screenshots and a grounded citation to the inspected window; A low-latency result handoff from the vision job to the active voice turn

### "“What changed in my work since yesterday, across my Mac and signed-in browser, and what is the one thing I should do next?”"
- **useful because:** The owner can ask about current state, but cannot get a trustworthy cross-surface delta: files, local project status, open work, and authenticated web changes are disconnected and there is no baseline. A spoken, evidence-linked delta would replace manual tab-by-tab checking and make the pendant useful during commutes or between work sessions.
- **path:** pendant → relay → mac-planner → browser-extension → ios → dashboard
- **model tier:** Use background mac-planner/browser jobs to collect structured observations and a cheaper summarizer to rank changes; use relay-realtime only to ask a clarification or speak the top one or two findings.
- **latency:** On-demand report in 10–30 seconds for a small scope; stream the first high-confidence change as soon as available and continue in the background for the rest.
- **cost:** One collection pass over explicitly selected Mac/browser scopes and one summarization call; recurring baselines should be stored as compact hashes/metadata, not re-send full pages or files to the realtime model.
- **security:** Authenticated pages and local work are sensitive. Store only hashes, titles, timestamps, and owner-approved excerpts by default; keep source URLs/apps and evidence receipts so every claim is auditable. Never infer that an unchanged hash means a page was successfully checked—report unavailable sources separately.
- **missing:** An owner-scoped baseline store for structured observations and content hashes; Collectors for selected local folders/apps and authenticated browser pages, with explicit checked/unavailable status; A cross-surface diff and evidence model that can cite each spoken finding; A compact spoken prioritizer that separates changed, unchanged, and not checked


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities: resumable cross-surface transactions, pendant-mediated grounded screen help, and an evidence-linked cross-device work-change digest. The recorder flagged that they are connective gaps around existing routes rather than wholly absent primitives; the proposals explicitly identify the missing seams (durable checkpoints, screenshot-to-voice handoff, and baseline/diff collectors) instead of pretending today’s routes already provide them.

**Biggest unknown:** Whether the existing /capture, /workbench handoff, and vision-related routes can already be wired into these flows without new relay endpoints; the live relay surface remains incompletely inventoryable.

