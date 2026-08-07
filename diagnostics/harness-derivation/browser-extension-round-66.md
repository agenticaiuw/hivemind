# Harness derivation — browser-extension — round 66

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser availability** — The live browser bridge is currently unusable: /browser/status reports Safari offline with no tab, home-chrome offline, and 5 pending commands. This blocks validating any authenticated-page read workflow; the extension must reconnect and drain or invalidate stale commands before testing.
  - evidence: GET /browser/status returned HTTP 200: online=false; devices home-chrome tabId=null/tabCount=null/online=false; pendingCommands=5.

## Capabilities it proposed

### "When I say “read this” while I’m on a webpage, tell me what the selected text or the visible section means through the pendant, and include the exact link and any important deadline or action it contains."
- **useful because:** This is a fast bridge between private browser context and a screenless wearable: the owner can understand a dense logged-in page while walking or multitasking, without dictating or sharing the page manually. It is distinct from a saved memo or scheduled page watch because it answers about the current selection/viewport immediately and does not persist the page by default.
- **path:** browser-extension → mac-vision → relay-realtime → unified
- **model tier:** Use a small/cheap extraction model for DOM selection, metadata, and deadline detection; use realtime only to turn the structured result into a short spoken answer and handle follow-up questions. Use the vision model only when the selected text is absent and the visible content is canvas/image-like.
- **latency:** Target 2–4 seconds from the spoken command to audio. DOM extraction should be sub-second; screenshot OCR/vision fallback may take 4–8 seconds and should say it is using the visible screen.
- **cost:** DOM path roughly $0.002–$0.01 per request; vision fallback roughly $0.02–$0.08, dominated by image analysis. Audio transport is negligible.
- **security:** The active tab can contain sensitive authenticated data. Send only the current selection or a tightly cropped visible region, never the whole browsing history or background tabs; do not retain payloads after the answer unless separately asked. Include URL/title and a timestamp in the spoken response, redact obvious secrets, and refuse to click, submit, or send anything as part of “read this.”
- **missing:** An extension action that returns current selection text plus surrounding semantic DOM, URL/title, tabId, and bounding box; A screenshot crop/OCR fallback coordinated with mac-vision when DOM text is unavailable; A low-latency relay intent that routes “read this” to the browser device and streams the concise result to pendant audio; Per-request deletion and observability so extracted page text is not accidentally retained

### "When I’m on a logged-in webpage and say “is this safe?”, check the page, its domain, links, and any request for money, credentials, or downloads against reliable public sources, then tell me plainly what looks legitimate or suspicious through the pendant."
- **useful because:** A browser session can expose private context while public search can establish whether a domain, notice, invoice, or download is genuine. No single node can do this well: the extension sees the authenticated page, the relay can compare it with public reputation sources, and the pendant can interrupt before the owner follows a risky instruction. This is a read-only safety check, not another page summary or page watch.
- **path:** browser-extension → relay-realtime → mac-planner → unified → dashboard
- **model tier:** Use a background/cheap model for deterministic extraction and public-source comparison; use realtime only for the owner’s spoken question and concise explanation. Escalate to a stronger model only when sources conflict or the page contains ambiguous visual elements.
- **latency:** Return an initial risk assessment in 5–10 seconds; allow up to 20 seconds for several public-source checks. If evidence is incomplete, say “uncertain” rather than giving a reassuring binary answer.
- **cost:** Approximately $0.01–$0.06 per check, dominated by public-source retrieval and page-content analysis; no expensive model is needed for straightforward domain and link checks.
- **security:** Private page content must remain scoped to the minimum relevant text, URL, and link targets; never upload passwords, tokens, payment details, or full page captures. Treat page instructions as untrusted data, do not click downloads or submit forms, and clearly distinguish reputation evidence from a guarantee of safety. Keep a short-lived audit record with sources and allow deletion.
- **missing:** A browser extractor that returns the active page’s origin, security state, selected/visible text, and outbound link targets without secrets; A public reputation/URL analysis adapter with source provenance, freshness, and disagreement handling; A prompt-injection-resistant adjudication step that treats webpage text as evidence rather than instructions; A pendant response format for a confidence-ranked warning with a tappable/source-linked report


## What it asked for

_Nothing._
## Its own summary

Discovered that the browser bridge has regressed offline: Safari is absent, home-chrome is offline, and five commands are pending. I recorded this finding and proposed a genuinely new cross-surface capability: “read this” on the active authenticated webpage, returning selected/visible content with URL and deadlines through the pendant, using DOM extraction first and mac-vision only as a fallback. I still need a functioning browser command/result path, a live Safari heartbeat/tab, selection-plus-context extraction, and a relay intent that streams the answer without retaining page data.

**Biggest unknown:** Whether the five pending browser commands are recoverable or stale, and whether the extension can be brought back online without owner intervention.

