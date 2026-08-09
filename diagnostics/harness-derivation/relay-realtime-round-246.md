# Harness derivation — relay-realtime — round 246

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Give me a quick, privacy-preserving summary of what changed since I last asked about that task."
- **useful because:** Owners don’t just need completion; they need a digest of meaningful changes. This reduces back-and-forth while keeping sensitive details minimal.
- **path:** relay → mac-bridge → pendant → dashboard
- **model tier:** Realtime for the spoken summary; cheaper background tier to diff state and receipts.
- **latency:** Under 2 seconds for the spoken summary once the data is available.
- **cost:** Low; dominated by fetching job state and receipts and computing a diff.
- **security:** Diffs can leak content. Only report state transitions, errors, and high-level artifacts unless the owner asks for details.
- **missing:** A stable job changefeed or diff endpoint rather than repeated polling; A small, standardized summary schema for job transitions

### "Before you do it, tell me the risky parts and what you’ll touch."
- **useful because:** This gives the owner confidence and a chance to course-correct without blocking reversible work. It’s especially valuable for multi-app actions that could have side effects.
- **path:** relay → mac-bridge → mac-planner
- **model tier:** Realtime to explain the plan; mac-planner to generate it.
- **latency:** 1–3 seconds to outline the risky steps for complex tasks.
- **cost:** Medium for complex plans; dominated by planning and summarization.
- **security:** The plan summary could reveal sensitive filenames or app content; redact specifics unless needed.
- **missing:** A typed risk summary emitted by the planner (read-only) that is separate from execution; Receipts that correlate each risky step to a result for later auditing

### "If my Mac is offline, still capture my request and run it when it comes back."
- **useful because:** The owner is often away from the Mac. Queuing intent at the relay lets the system feel reliable even when the machine is asleep.
- **path:** relay → mac-bridge → pendant → dashboard
- **model tier:** Realtime to accept and confirm the queued request; mac-planner when the Mac is online.
- **latency:** Under 1 second to confirm the queue; execution can happen later.
- **cost:** Low to medium; dominated by storing queued intent and later planning/execution.
- **security:** Queued work is powerful. Require explicit confirmation for high-impact tasks and keep queued content encrypted at rest.
- **missing:** A persistent job queue at the relay (Durable Object or KV); A reconnect handshake from the Mac to claim queued work; Idempotency keys to avoid double execution

### "When I say “keep an eye on this while I’m away,” have the system watch the exact page or document I was looking at, notice a meaningful change, and tell me what changed and what I should do—without making me restate the URL or context."
- **useful because:** This turns a fleeting pendant interaction into continuity across an unattended Mac, its logged-in browser, and the always-awake relay. The valuable part is not another alert: it preserves the originating view, compares versions, explains the delta, and reaches the owner only when the change is actionable.
- **path:** pendant → relay → browser → mac-planner → mac-vision → dashboard
- **model tier:** Use relay-realtime only to capture and acknowledge the request; use a cheaper background model for page/document diff and prioritization; use mac-vision/browser-extension for the authenticated view and the Mac planner only for an explicitly requested follow-up action.
- **latency:** Acknowledge in under 2 seconds. Checks may take seconds to minutes; delivery should be event-driven rather than requiring the owner to poll.
- **cost:** About $0.01–$0.08 per check depending on page size and screenshot comparison; the dominant cost is vision/context extraction, not the spoken turn.
- **security:** The watch may read authenticated pages and could expose snippets in relay logs or the pendant. Store only encrypted page fingerprints and the minimum changed excerpts, expire watches by default, and require explicit confirmation before any follow-up mutation such as sending or submitting.
- **missing:** A durable watch registration that can bind a source tab/document to a relay watch; A Mac/browser trigger that can re-open the same authenticated source after the owner leaves; A semantic diff worker with source citations and actionable-change ranking; An event delivery path that can target the existing pendant inbox without polling

### "Let me dictate an idea on the pendant and say “make this real”; have the system turn it into a durable, editable artifact on my Mac with the original audio, transcript, decisions, and source links attached, then let me ask later “why did we write this?” and get the reasoning back."
- **useful because:** A spoken thought currently disappears into a turn or becomes an untraceable file. This would make the pendant a low-friction capture device while the Mac supplies editing and the relay supplies durable provenance, so ideas remain understandable rather than merely remembered.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension → dashboard
- **model tier:** Realtime performs only capture acknowledgement and a short clarification; a background model extracts claims, open questions, and an artifact type; mac-planner/mac-terminal writes the artifact and browser-extension attaches citations when present.
- **latency:** Acknowledge immediately; create a first draft within 30 seconds and refine asynchronously. Retrieval should answer in one spoken turn when the owner asks later.
- **cost:** Roughly $0.02–$0.15 per captured idea, dominated by transcription plus structured extraction; retrieval is cheap if provenance is indexed.
- **security:** Voice recordings and work source links are sensitive. Encrypt the audio, keep it only until the owner-selected retention period, preserve immutable hashes for provenance, and never silently publish or send the resulting artifact.
- **missing:** A first-class artifact/provenance record linking voice, transcript, edits, and citations; A Mac-side writer that can create or update the chosen project file without destroying concurrent edits; A retrieval route that searches provenance and explains decisions rather than returning only memory facts; A user-selectable retention policy for raw audio versus derived text

### "When I am away from my Mac, let me hand off a multi-step task with a hard boundary—“prepare everything, but stop before the irreversible step”—and later resume it from the pendant with a spoken summary of exactly what is ready, what is blocked, and what remains."
- **useful because:** This gives the owner the benefit of unattended work without pretending that a queued job is finished. The relay can keep the conversation short, the Mac and browser can do the tedious preparation, and the owner can safely resume from a precise checkpoint instead of repeating the task.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime handles intent capture and checkpoint summaries; mac-planner and browser-extension execute preparation; a cheaper background worker validates the checkpoint and assembles a compact spoken delta.
- **latency:** Queue in under 2 seconds; preparation may run for minutes. The checkpoint summary should be available immediately after completion and pushed to the pendant when online.
- **cost:** $0.03–$0.20 per multi-step task, dominated by planner iterations and browser screenshots; status checks and summaries are low cost.
- **security:** Checkpoint state can contain drafts, recipients, and authenticated page data. Encrypt artifacts, bind each checkpoint to the initiating session and expiry, make resume idempotent, and require an explicit physical or spoken resume only for the final irreversible operation.
- **missing:** A durable typed checkpoint/receipt format with resumable action IDs and rollback metadata; A worker that can continue Mac/browser jobs after the voice session ends; A reconciliation step that detects stale pages or changed files before resuming; A pendant-facing checkpoint summary and resume command integrated with the existing inbox/event delivery

### "Ask several parts of my digital life one question at once—“is this meeting still worth attending, and what preparation is missing?”—then have the pendant give me one answer that clearly separates calendar facts, authenticated-browser facts, and Mac project state, instead of making me run separate commands."
- **useful because:** The owner thinks in decisions, not surfaces. Today each node has a different reach and the low-latency relay generally hands the turn to one downstream action. A parallel evidence pass with provenance-aware synthesis would make the hive feel like one assistant while keeping each source's authority visible.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime captures the question and speaks only the final concise synthesis; parallel source reads use inexpensive workers or the relevant specialist agents, followed by a background judge that resolves conflicts and marks unknowns.
- **latency:** Start all reads within 1 second and return a short answer within 10 seconds when sources are online; if one source is slow, speak a partial answer with an explicit missing-source label and push the completed synthesis later.
- **cost:** About $0.03–$0.20 per question, mainly from parallel browser screenshots and synthesis context; source reads should be cached and deduplicated within the request.
- **security:** The answer combines calendar, local files, and authenticated web data, increasing blast radius. Keep source-specific access tokens at their owning surface, pass only extracted evidence to synthesis, attach source and timestamp labels, and never allow a synthesis request to mutate anything.
- **missing:** A fan-out/fan-in orchestration primitive for read-only evidence requests; A common evidence envelope with source, timestamp, confidence, and stale/error state; Conflict-aware synthesis that refuses to invent agreement when sources disagree; A relay response mode that can speak a partial result and later deliver a completed one


## What it asked for

_Nothing._
