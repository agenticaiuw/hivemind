# Harness derivation — relay-realtime — round 142

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Check my private accounts and pages and give me a concise brief of what needs attention, with drafts ready but nothing sent."
- **useful because:** It turns scattered notifications into a single reviewable queue and saves time drafting responses.
- **path:** browser → mac-bridge → relay → dashboard
- **model tier:** Cheaper extraction and summarization models for bulk; realtime only for spoken delivery.
- **latency:** Batch work can run in the background; spoken summary should be under 30 seconds.
- **cost:** Dominated by page reads and extraction runs; summaries are relatively cheap.
- **security:** Authenticated pages must stay within trusted browser sessions; drafts must be clearly labeled and never auto-sent.
- **missing:** Durable authenticated page-watch service; Implemented server_browser_actions for public pages; Reliable browser command queue with typed results; Schedule/trigger mechanism for periodic checks

### "Give me a 30-second audio briefing I can listen to from the pendant, and let me ask follow-up questions."
- **useful because:** The owner can stay heads-up and hands-free, especially when away from the Mac.
- **path:** relay → mac-bridge → dashboard
- **model tier:** Cheaper summarizer to prepare content; realtime to deliver and answer follow-ups.
- **latency:** Brief generation can happen ahead of time; playback start should feel immediate.
- **cost:** Brief generation cost depends on sources; playback is a short audio fetch.
- **security:** Audio may contain sensitive information; ensure retention controls and deletion options.
- **missing:** Audio queue creation and storage on relay; Reliable capture and playback handoff; Implemented relay_event_push or equivalent for ready notifications

### "When I say “pick up where I left off,” tell me in one short spoken handoff what I was doing across my Mac and authenticated browser tabs, and offer the next concrete action."
- **useful because:** The owner can leave the desk wearing the pendant and return hours later without reconstructing which app, document, tab, and unfinished step mattered. No single node can know this: the relay needs the Mac's current workspace, the browser's session state, and durable cross-surface memory.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → browser → dashboard
- **model tier:** Use the relay realtime model only to recognize the short utterance and speak the answer; use mac-planner/mac-vision and browser inspection agents for collection, and a cheaper background summarizer for the continuity capsule.
- **latency:** A spoken acknowledgement within 500 ms, with the capsule assembled in 5–15 seconds; say “I’m checking” rather than blocking the voice loop.
- **cost:** Roughly $0.01–$0.05 per pickup, dominated by Mac vision/browser inspection and summarization; reuse a cached capsule when nothing changed.
- **security:** The capsule may contain document names, browser titles, and snippets from authenticated pages. Keep raw content on the Mac/extension, send only a redacted structured summary to the relay, expire it after a configurable period, and never read page bodies aloud unless explicitly requested.
- **missing:** A cross-surface continuity record keyed to the owner and time; Mac endpoint that reports active app/window/document and unfinished action state; Browser endpoint that reports authenticated tab titles and pending form/work state; A redacting summarizer and a spoken handoff response path

### "Use my pendant as a physical “handoff” button: when I press it near my Mac, make the relay identify my active work context and send a compact, private handoff to the Mac or browser session I choose, without me dictating it."
- **useful because:** A worn one-button device can bridge the owner's physical presence and the otherwise disconnected relay/Mac/browser surfaces. This makes moving between away-from-desk and desk work nearly frictionless and avoids speaking sensitive project names aloud in public.
- **path:** pendant → relay → mac-planner → browser-extension → browser → dashboard
- **model tier:** No expensive realtime reasoning for the button event: firmware emits a signed event, relay resolves the paired owner/device, and a cheap classifier selects the destination; use the realtime model only if the owner follows with ambiguous speech.
- **latency:** LED acknowledgement locally in under 100 ms; Mac/browser handoff in under 2 seconds when connected; queue safely when the Mac is asleep and report the result on next link.
- **cost:** Under $0.005 per event; dominated by occasional context extraction, not the button event.
- **security:** The button is a physical bearer signal. Require an established device pairing and rotating event nonce, expose only the selected context class (not arbitrary clipboard contents), encrypt in transit, and provide a local long-press cancel pattern. A dashboard should show the last handoff and destination.
- **missing:** Pendant firmware signed button-event protocol and pairing state; Relay endpoint for authenticated device events and destination selection; Mac/extension listener that can package current context without leaking secrets; A durable short-lived handoff queue for disconnected surfaces

### "Let me say “show me what changed since I left” and have the pendant give me a spoken delta of my Mac and browser work, with links or app names I can then ask it to reopen."
- **useful because:** The owner gets an actionable change feed rather than a generic status report: newly edited files, changed issue pages, completed or failed delegated actions, and tabs that appeared while away. It turns unattended time into a useful return brief across surfaces.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension → browser → dashboard
- **model tier:** Use a cheap background diff/indexer to maintain per-surface change cursors; realtime only interprets the request, selects the cursor, and verbalizes the top few deltas.
- **latency:** Immediate acknowledgement under 500 ms; first three deltas within 3 seconds, with a follow-up stream only when requested.
- **cost:** Approximately $0.005–$0.03 per request; storage/indexing is the main cost, with model spend limited to ranking and compression.
- **security:** Do not transmit full file or page contents by default. Store hashes, titles, app identifiers, timestamps, and user-approved excerpts; distinguish owner edits from agent edits; redact secrets and offer a spoken “why did this change?” drill-down with explicit scope.
- **missing:** Per-surface change cursors and provenance (owner, Mac agent, browser agent); Mac file/app delta collector and browser tab/history delta collector; Durable relay storage for last-seen cursors and compact summaries; A reopen-by-reference resolver that maps spoken item names to safe Mac/browser actions


## Changes it proposed to its own stack

### `relay` — Implement relay_route_intent as a real routing endpoint that validates intents, writes a durable job record, and forwards to mac_delegate or browser_run_actions when appropriate.
- **owner gets:** They get consistent behavior: their spoken request reliably becomes a tracked job with a status they can ask about later.
- effort: Medium to high; needs schema enforcement, durable storage, and integration tests.  ·  risk: Routing bugs could mis-send tasks; mitigate with receipts and a safe default fallback.
- cost: Low per request; dominated by downstream work.  ·  latency: Small overhead for validation and persistence.
- security: Needs strict auth and input validation to prevent cross-tenant routing issues.
- depends on: Durable job runner

### `routines` — Add a lightweight scheduler (cron/alarm) for periodic tasks like daily briefing, page-watch checks, and cleanup jobs, with clear receipts of what ran.
- **owner gets:** Features like daily briefings and watches only exist if the system can run later without them asking.
- effort: Medium; could use Cloudflare Cron/Durable Object alarms.  ·  risk: Misfires or duplicate runs; mitigate with idempotency keys and logs.
- cost: Low to moderate; depends on cadence and workload.  ·  latency: No impact on conversational latency.
- security: Needs strict scoping so scheduled jobs only access allowed sessions and data.


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities: (1) a cross-Mac/authenticated-browser “pick up where I left off” spoken handoff, (2) a physical pendant-button handoff event that bridges presence to a selected Mac/browser context, and (3) a spoken “what changed since I left” delta with reopenable references. The first two are intentionally end-to-end proposals requiring new continuity/device-event components rather than assuming today’s routes are sufficient; the third adds provenance-aware change cursors and a spoken-to-reference resolver.

**Biggest unknown:** Whether the existing Mac inspection routes can expose active document, unfinished action, and provenance at sufficient fidelity; the relay also still lacks a confirmed durable cross-surface continuity store and a real authenticated pendant-event endpoint.

