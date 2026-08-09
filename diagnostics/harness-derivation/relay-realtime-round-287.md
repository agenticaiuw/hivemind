# Harness derivation — relay-realtime — round 287

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "While I’m away from my Mac, check my authenticated sessions and summarize what changed that I should care about."
- **useful because:** This becomes a daily superpower: the wearable can summarize changes across sessions the owner is already logged into, without manual checking.
- **path:** relay → browser → mac-bridge
- **model tier:** Cheaper model for periodic checks and diffing; realtime only for delivering a spoken summary.
- **latency:** Background checks can take their time; summaries should be short and quick to deliver.
- **cost:** Moderate. Dominated by browser automation time and page reads, not LLM tokens.
- **security:** Sensitive data in authenticated sessions. Keep summaries minimal, avoid copying content, and require confirmation for actions.
- **missing:** A server-side browser capability (server_browser_actions is unresolved) or a reliable always-on browser node.; A scheduling mechanism that works even when the Mac is offline, or a durable relay-side watcher using existing watch/routine primitives.

### "“I’m about to walk away—finish the task I have open, but tell me if the result differs from what I asked.”"
- **useful because:** Today the owner can hand work to the Mac, but cannot leave with confidence that the browser/UI actually reached the requested end state. This would make the pendant a trustworthy handoff point: the Mac acts, the browser proves the visible result, and the relay reports only a meaningful mismatch.
- **path:** pendant → relay → mac-planner → mac-vision → browser → dashboard
- **model tier:** Realtime relay for intent and a one-sentence response; mac-planner for the action plan; mac-vision for visual verification; browser harness for DOM/session evidence; background verification should use a cheaper model.
- **latency:** Acknowledge in under 1 second; action may take up to 60 seconds; speak completion or mismatch immediately when evidence arrives.
- **cost:** About $0.01–$0.08 per handoff depending on planner/vision retries; browser and Mac calls dominate latency, not relay speech.
- **security:** The request can mutate authenticated sites. The owner has explicitly allowed trusted agents to act without extra gates, but the system must retain the exact utterance, planned effect, and before/after evidence. Page contents and screenshots leave the Mac only to the relay/dashboard.
- **missing:** A first-class job contract containing intent, expected postcondition, and evidence requirements; Mac-vision execution/verification loop enabled in production; Browser result evidence attached to the same job rather than emitted as unrelated commands; A relay reducer that classifies verified, contradicted, and inconclusive outcomes

### "“When I tap the pendant, tell me the one thing on my Mac or in my open browser that deserves my attention right now.”"
- **useful because:** The pendant currently answers explicit requests, but it cannot perform a cross-surface attention scan while the owner is away. A single ranked answer would replace checking several apps and tabs with an actually wearable interruption filter.
- **path:** pendant → relay → mac-planner → mac-vision → browser → dashboard
- **model tier:** Cheap background perception gathers active-app/window and browser facts; a judgement model ranks urgency and novelty; realtime relay only handles the tap, cancellation, and spoken one-sentence result.
- **latency:** First spoken acknowledgment under 500 ms; ranked result within 8 seconds, with an asynchronous inbox alert if inspection takes longer.
- **cost:** Roughly $0.01–$0.04 per scan; most cost is browser/page inspection and summarization. Cache unchanged surfaces to avoid paying for repeated scans.
- **security:** This intentionally reads authenticated tabs and local app state. Scope must be explicit (active window plus opted-in tabs/apps), redact secrets before storage, and never treat page text as an instruction. Nothing should be sent or changed without a separate command.
- **missing:** A permissioned cross-surface snapshot endpoint for active Mac UI plus selected browser tabs; Stable content hashes and timestamps so unchanged items are not repeatedly ranked; A priority/novelty judgement prompt and an owner-tunable attention policy; A wearable push path for a result that completes after the tap

### "“Remember this page as evidence for the project, and next time I ask, quote the exact passage and tell me when it was captured.”"
- **useful because:** A browser page can be read today and facts can be stored, but the owner cannot reliably ask the pendant for provenance-grade recall: exact excerpt, URL, capture time, and whether the page has since changed. This turns fleeting browsing into trustworthy project memory rather than an unsupported summary.
- **path:** pendant → relay → browser → mac-planner → dashboard
- **model tier:** Background browser extraction and deduplication; realtime relay handles the spoken save/retrieve request; a cheaper retrieval model selects passages, while the relay reads a short answer and offers the citation on the dashboard.
- **latency:** Save acknowledgment under 2 seconds; retrieval under 5 seconds for indexed pages; if the page is unavailable, say so rather than hallucinating.
- **cost:** About $0.005–$0.03 per save/retrieval after hashing; extraction and re-checking dominate, with stable pages reused from storage.
- **security:** Store only the owner-selected page and a bounded excerpt, never credentials or whole authenticated pages by default. Preserve source URL, host, timestamp, content hash, and sensitivity; require explicit confirmation before sharing a stored excerpt externally.
- **missing:** A provenance record distinct from ordinary browser facts, including excerpt offsets/content hash and capture timestamp; An exact-quote retrieval route that can distinguish captured text from a fresh page read; Change detection and versioning for pages that later differ; Voice-accessible citation formatting and dashboard drill-down


## What it asked for

_Nothing._
