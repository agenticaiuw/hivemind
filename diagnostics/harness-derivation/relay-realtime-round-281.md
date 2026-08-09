# Harness derivation — relay-realtime — round 281

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Find the thing I was looking at yesterday about [topic], tell me which app or browser tab it is in, and open it if I want.”"
- **useful because:** The pendant is the only interface available while away from the desk, but today it cannot recover a half-remembered page or document across Safari, apps, and local files. A temporal, cross-surface recall would turn vague spoken memories into a concrete link or file instead of forcing the owner to search manually.
- **path:** pendant → relay → mac-planner → mac-vision → browser → dashboard
- **model tier:** Use relay-realtime only to normalize the short spoken query and speak the result; use a cheaper background/local retrieval model on the Mac to rank browser history, app-window/document events, and captured page titles. Use mac-vision only for ambiguous visual matches.
- **latency:** Return likely matches in 3–6 seconds for a same-day query; if indexing is needed, acknowledge immediately and deliver the ranked result asynchronously.
- **cost:** Roughly $0.01–$0.05 per retrieval, dominated by embedding/reranking and any screenshot understanding; most queries should be local and incur no model cost.
- **security:** This would index sensitive browser history, window titles, and file names. Keep the index on the Mac, send only ranked titles/URLs and the minimum excerpt to the relay, redact secrets and form values, and expire raw visual captures quickly. Opening a result should remain an explicit spoken request.
- **missing:** A Mac-side append-only activity journal for browser tabs, app documents, and timestamps; A local temporal/semantic retrieval route that can return provenance and confidence; A relay conversation primitive for presenting multiple candidates and receiving a follow-up selection; Retention and redaction policy for activity metadata

### "“What am I looking at on my Mac right now? Read me the important parts, and if I say ‘that one,’ use the item I mean.”"
- **useful because:** A worn voice interface cannot see the owner’s current visual context. This would make the pendant a genuinely useful remote front door: the owner could ask about a chart, error dialog, email list, or browser page without narrating its contents, then refer to an on-screen item naturally in the next turn.
- **path:** pendant → relay → mac-vision → mac-planner → browser
- **model tier:** Use a low-cost vision model on the Mac for screenshot OCR/layout grounding and a compact relay response for the spoken summary. Escalate to the expensive realtime model only when the owner’s reference is ambiguous.
- **latency:** Capture and summarize the current screen in under 4 seconds; resolve a deictic follow-up such as “that one” in under 2 seconds while the screenshot/session is still warm.
- **cost:** About $0.005–$0.03 per screen query, dominated by vision tokens; crop to the active window and locally OCR first to keep cost low.
- **security:** Screens may contain passwords, private mail, health or financial data. Processing should stay on the Mac by default; transmit only the selected crop/OCR and spoken summary, never retain full screenshots beyond the turn, and visibly/logically identify which window was inspected. Do not click or mutate anything unless the owner separately asks.
- **missing:** A live mac-vision screenshot/OCR query that is enabled rather than merely described; A stable per-turn visual reference map (items, labels, bounding boxes) that the relay can reuse for follow-up speech; A privacy-preserving crop/redaction stage before any image leaves the Mac; A relay route that can maintain visual grounding across two voice turns

### "“Remember that when I say ‘the client,’ I mean Acme, and when I say ‘send the deck,’ use the latest PDF in my project folder.”"
- **useful because:** The owner should not have to repeat project-specific names, aliases, and artifact-selection rules to a voice agent. A spoken, scoped vocabulary would make short pendant commands reliable across Mac files, authenticated browser work, and future iPhone actions while keeping the owner in control of what is remembered.
- **path:** pendant → relay → mac-planner → browser → ios → dashboard
- **model tier:** Use relay-realtime to detect an explicit remember/update request; store and resolve the rule with a cheap deterministic matcher or local model. Use the expensive model only when multiple files or entities genuinely conflict.
- **latency:** Acknowledge a new alias in under 1 second; apply it to the next request with no additional perceptible delay. Conflict resolution can be a short follow-up question.
- **cost:** Near-zero for storage and exact matching; roughly $0.001–$0.01 only for ambiguous entity/file resolution.
- **security:** Rules can accidentally cause messages or uploads to target the wrong person or artifact. Store provenance, scope, confidence, and expiry; show the resolved target in the spoken confirmation for high-impact operations, without imposing a blanket confirmation gate. Keep sensitive aliases local and allow “forget that rule.”
- **missing:** Live-turn injection of the existing scoped memory projection into conversationContext.js; A first-class alias/selection-rule schema with provenance and conflict handling rather than encoding everything as a generic fact; Resolution hooks in mac planning, browser actions, and iOS actions so the same alias means the same entity everywhere; A spoken forget/list vocabulary operation and dashboard audit view


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities: (1) temporal cross-surface recall of a half-remembered page/file, (2) live Mac visual grounding with follow-up references like “that one,” and (3) spoken, scoped aliases and artifact-selection rules shared across Mac/browser/iOS. The single most useful is live visual grounding: it gives the worn pendant access to context the owner can see but cannot conveniently describe. The key missing work is connective rather than another isolated tool: enable mac-vision screenshot/OCR and per-turn reference maps, add a Mac activity journal and retrieval API, inject the existing scoped memory projection into the live turn, and make downstream planners consume those resolved entities.

**Biggest unknown:** Whether the currently disabled computer-use/vision loop can expose a read-only screenshot and OCR/reference-map operation without enabling mutation; no more discovery is available this round.

