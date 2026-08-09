# Harness derivation — relay-realtime — round 210

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When you finish something on my behalf, let me say “undo that” and have you reverse the last reversible change, even if it touched both my Mac and a browser tab."
- **useful because:** A wearable assistant becomes safe to use at conversational speed when mistakes are recoverable without finding the right app or remembering what happened. The relay can identify the exact completed job, explain any irreversible portion, and dispatch compensating actions across surfaces.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime relay handles the short undo utterance and selects the latest job; a cheaper background planner derives a compensation plan from action receipts; Mac/browser agents execute and verify it.
- **latency:** Acknowledge in under 500 ms; begin reversal within 2 s; completion may take as long as the original job, with a short pendant result and durable inbox fallback.
- **cost:** About $0.01–$0.08 per undo depending on whether compensation needs planning; latency and cost are dominated by receipt interpretation and postcondition verification, not the spoken turn.
- **security:** The system must never claim an irreversible send, purchase, deletion, or external side effect was undone. Every action needs before/after evidence, a reversibility class, and an explicit partial-undo report. Receipt data may contain URLs and document names, so dashboard retention should be bounded.
- **missing:** A durable before-state/compensation record for each Mac and browser action; A compensation planner and verification loop; A single undo endpoint that can correlate the latest job across relay, Mac, and browser; A user-visible distinction between fully reversed, partially reversed, and irreversible

### "What was the thing I saw about [topic]? Search my open and recently used browser pages and my Mac files, then tell me the answer with where each piece came from."
- **useful because:** Today web search can find public information, but the owner's useful context is often behind their own browser sessions or in local files. This would make the pendant a truthful memory of the owner's working world rather than a generic search box, while preserving citations so an uncertain match is obvious.
- **path:** pendant → relay → browser-extension → mac-planner → mac-terminal → dashboard
- **model tier:** Realtime relay extracts the topic and gives a concise answer; browser and Mac retrieval run in parallel with a cheaper model for ranking and deduplication; realtime is used only to narrate the final evidence-backed result.
- **latency:** Speak an acknowledgement immediately; return a first answer in 3–8 seconds and continue with a later alert if local indexing or a locked browser tab takes longer.
- **cost:** Roughly $0.02–$0.12 per query, mostly retrieval/reranking and any Mac planner turn; a local text index would reduce both cost and latency after initial indexing.
- **security:** Never send private page or file contents to public web search. Retrieval must be scoped to explicitly requested personal sources, redact secrets from the spoken summary, retain source URLs/paths only as long as needed, and clearly say when a source could not be opened.
- **missing:** A Mac-side local full-text index with permission-aware file and browser-history connectors; A browser command to export searchable page text and timestamps from the owner's authenticated session; A relay retrieval/ranking endpoint that merges Mac and browser evidence with provenance; A compact spoken citation format and dashboard transcript showing exact excerpts

### "Put me back into my work context from yesterday."
- **useful because:** The owner should be able to leave the Mac, use another machine, or recover after a crash without manually reconstructing apps, browser tabs, documents, and the exact page positions that mattered. A worn-device request can restore a meaningful working state while the owner is away, then report what could not be recovered.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** A background Mac agent captures and normalizes context snapshots; realtime only resolves the spoken snapshot name and gives a result. The Mac planner restores apps/files and the browser extension restores authenticated tabs, with computer vision reserved for pages whose URL/state is insufficient.
- **latency:** Acknowledge immediately; restore the first useful state in 5–15 seconds and continue asynchronously for large sessions. Speak a compact list of restored and skipped items.
- **cost:** About $0.03–$0.20 per restore, dominated by planner/vision turns; snapshot storage and local indexing are the larger ongoing costs, not inference.
- **security:** Snapshots can expose private URLs, document names, and scroll context. Store them encrypted on the Mac, keep only explicit named snapshots plus bounded retention, never replay passwords or form contents, and make the spoken result omit secrets. A restore must not silently submit or send anything.
- **missing:** A Mac context snapshot service for app windows, file URLs, browser tabs, scroll/selection metadata, and timestamps; A named snapshot store and diff format shared by Mac and relay; Browser extension save/restore commands for authenticated tabs without serializing cookies; A restore planner with idempotent actions and per-item receipts; A pendant command/result path that can survive the owner walking away


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities: reversible cross-surface “undo that” with truthful partial-undo reporting; evidence-backed personal search across authenticated browser context and Mac files; and named work-context snapshot/restore across Mac and browser. The largest missing pieces are durable pre/post action evidence and compensation planning, permission-aware personal retrieval/indexing, and encrypted cross-surface context snapshots with idempotent restore.

**Biggest unknown:** Which of these the owner considers the first daily-use priority; implementation still needs new relay/Mac/browser primitives rather than another discovery pass.

