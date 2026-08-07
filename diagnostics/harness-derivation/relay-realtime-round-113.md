# Harness derivation — relay-realtime — round 113

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“During a meeting, when I tap the pendant, listen for the current question, find the answer in my open Mac documents or logged-in browser tabs, and whisper me a concise, sourced answer—without speaking aloud or changing anything.”"
- **useful because:** The owner is often away from the Mac and cannot interrupt a meeting to search. A deliberate pendant tap would turn the Mac’s local meeting context, authenticated browser, and always-awake relay into a private just-in-time aide. It is distinct from preparing a meeting or monitoring pages: it answers the question being asked right now, with citations and an uncertainty warning when evidence is weak.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime relay for turn-taking, question normalization, and a short spoken response; mac-vision (or a future local audio/transcription facet) establishes the current question; mac-planner searches local documents; browser-extension searches already-open authenticated tabs; use a cheaper background model only to rank and compress retrieved evidence.
- **latency:** Tap acknowledgement under 300 ms; first useful answer within 5 seconds; hard stop at 12 seconds with 'still searching' and a resumable result. Never speak through the Mac or modify a document/browser page.
- **cost:** Roughly $0.01–$0.08 per tap depending on whether local transcription and retrieval suffice; realtime tokens and any remote vision/audio inference dominate. Local Mac transcription and bounded snippets keep both cost and context transfer down.
- **security:** Meeting audio and private document/browser snippets are sensitive. Audio should be streamed only for the active tap window, encrypted, discarded after extraction, and never placed in general memory. Show source titles/URLs and confidence in the dashboard and spoken result. Require an explicit tap for each capture; no ambient listening, page submission, or outbound message.
- **missing:** A pendant tap-triggered ephemeral capture session with local/private audio transcription and cancellation; Mac meeting-audio or microphone transcript ingress exposed to the relay with strict per-request retention; A unified evidence retrieval API spanning local Mac documents and already-open authenticated browser tabs, returning citations and confidence; Private pendant playback routing distinct from Mac speakers, plus a compact timeout/cancel state machine; A dashboard review record for each answer's question, sources, confidence, and deletion status


## Changes it proposed to its own stack

### `integration` — Add a tap-scoped Meeting Assist session spanning pendant → relay → Mac → browser. The relay creates a single-use session token with a 15-second audio TTL and cancellation; the Mac publishes a local transcript plus the active app/document identifiers; browser inspection retrieves only bounded text from tabs already open in that session; an evidence joiner returns source excerpts, confidence, and a spoken-answer payload. Persist only a hash, source metadata, and deletion receipt, and expose a one-click dashboard purge.
- **owner gets:** A tap during a live meeting would produce a private answer in the owner’s ear without making them unlock the Mac, search manually, or risk the assistant speaking or editing in public.
- effort: Medium-high: pendant event firmware, relay session state, a local microphone/transcript bridge, bounded browser extraction, evidence ranking, and playback routing; test across dropped LTE and Mac sleep/wake.  ·  risk: The wrong question or stale document could yield a confident but incorrect answer; mitigate with quoted evidence, confidence/age labels, a short-answer fallback, explicit 'I couldn't verify that,' and automatic session expiry. Audio leakage or retention is mitigated by encryption, no ambient mode, strict TTL, and deletion receipts. Recover by cancelling the session and replaying only the retained source metadata.
- cost: No persistent audio storage; approximately $0.01–$0.08 per assisted tap, dominated by realtime transcription/answer generation. Engineering cost is mainly the local transcript bridge and secure ephemeral session handling.  ·  latency: Adds a sub-300 ms tap acknowledgement, typically 3–5 seconds to answer, with a 12-second timeout and asynchronous dashboard result if retrieval is slow.
- security: Sensitive meeting audio and private tabs cross the relay only during an explicit tap session. Use per-session bearer tokens, least-scope tab handles, encrypted transport, redacted logs, and automatic deletion; never reuse the session token.
- depends on: A pendant tap event that can start and cancel a short-lived session; Mac-local transcript/microphone ingress; Bounded authenticated-tab extraction with citations; Private pendant playback and an ephemeral retention/deletion mechanism


## What it asked for

_Nothing._
## Its own summary

Discovery shows the production toolset is present (get_mac_status, mac_run_actions, browser_run_actions, web_search, mac_delegate, read_web_page, relay_job_status). Three newly granted relay-side tools exist only as schemas (relay_route_intent, server_browser_actions, relay_job_status in granted list) and calling them would return a no-implementation note. Devices currently show the Mac bridge online, browser offline, and a mobile test device offline. The backlog still contains many unfilled multi-surface capabilities such as durable browser job runners, authenticated page watches, and typed context services; they remain open and should not be restated verbatim.

**Biggest unknown:** Whether the relay exposes its own capability inventory and delivery endpoints (e.g., pendant announcements, event delivery) via discoverable routes/tools; today I can’t reliably enumerate my own surface, which blocks proposing precise relay-side integrations and prevents confident end-to-end designs.

