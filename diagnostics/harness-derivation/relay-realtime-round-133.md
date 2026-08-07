# Harness derivation — relay-realtime — round 133

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Find the thing I’m referring to—whether it is in an authenticated browser tab or a file/app on my Mac—using my spoken description, open the best match on the right surface, and tell me exactly what you opened. If there are multiple plausible matches, ask one concise question through the pendant before acting."
- **useful because:** The owner can refer naturally to 'the invoice from Acme' or 'that design doc I was looking at' while away from the desk. Today browser sessions and Mac-local state are separate worlds; neither can resolve a spoken reference across both and return a trustworthy handoff. This makes the pendant a genuine remote front door to the owner’s whole working context.
- **path:** pendant → relay → browser → mac-planner → mac-vision
- **model tier:** Realtime relay handles speech normalization and the single clarification question; a cheaper background planner performs federated candidate extraction/ranking across browser tabs and Mac metadata, while mac-vision is used only when an exact UI target must be opened or verified.
- **latency:** Acknowledge in under 500 ms; return candidates or ask clarification within 3 s; open and speak a concise receipt within 10 s, with progress audio if either surface is slow.
- **cost:** One realtime turn for the utterance and response; roughly 1–3 cheap planner calls per request. Dominant cost is extracting/ranking snippets from local and authenticated browser context, not speech.
- **security:** Data from authenticated tabs and local files crosses the relay/model boundary, so minimize excerpts, retain only opaque candidate IDs and provenance, and never send whole pages by default. Opening a match is reversible and should not require confirmation, but the spoken receipt must name the source surface and exact title/path/URL.
- **missing:** A federated reference resolver that can query browser-session tab metadata/content and Mac-local indexed metadata under one request ID; A durable candidate record with source, confidence, and provenance so clarification and opening refer to the same snapshot; A result/clarification channel that can speak a follow-up to the pendant without requiring the owner to repeat the original request; Mac and browser adapters that expose safe open-by-candidate operations rather than free-form re-searching

### "Take the page or text I’m talking about in my authenticated browser and hand it to my Mac as a usable artifact—for example, open the page, copy the selected passage into the clipboard, or create a local note—then tell me through the pendant what was transferred and where."
- **useful because:** The owner often notices something on the phone-like conversational surface while away from the desk, but browser sessions and Mac applications cannot currently exchange a precise, attributable artifact. This turns a spoken request into a practical cross-device handoff instead of making the owner find and copy the material again.
- **path:** pendant → relay → browser-extension → browser → mac-planner → mac-terminal
- **model tier:** Realtime only parses the request and confirms the target; a cheaper planner extracts the requested artifact and chooses the destination. Mac-terminal or mac-planner performs the local write/open, with browser-extension supplying the authenticated selection.
- **latency:** Acknowledge immediately; extract and transfer within 5–12 s. For a large artifact, speak completion as soon as the local receipt arrives rather than waiting for indexing.
- **cost:** One realtime turn plus one cheap extraction/planning call; browser extraction and local file/clipboard operations dominate latency, with negligible API cost for small text.
- **security:** Authenticated page content and clipboard material are sensitive. Transfer only the explicitly requested selection or bounded excerpt, attach source URL/title and timestamp, use a per-request nonce, and return a receipt. Never silently overwrite an existing file or clipboard; create a uniquely named note by default and report its path.
- **missing:** A first-class artifact-transfer envelope (content, MIME type, source provenance, destination, nonce, expiry) shared by browser and Mac adapters; Browser-side selection/extraction and Mac-side clipboard/file receivers with receipts and idempotency; A relay route that correlates the pendant utterance, browser extraction, and Mac mutation without passing sensitive content through multiple model prompts; A small owner-visible transfer history so a spoken 'undo that handoff' can identify the last artifact

### "Read the important parts of the page or document I’m currently using, but automatically keep passwords, API keys, payment numbers, and other sensitive strings out of the pendant audio; tell me what was withheld and let me explicitly request one narrowly identified field if I need it."
- **useful because:** A worn, always-audible device makes authenticated browser and Mac content useful while away from the desk, but unrestricted read-aloud can leak secrets to anyone nearby. Today the system can inspect or summarize sources, yet it lacks a source-aware safety boundary between private content and spoken audio. This would make hands-free access practical in public without making the owner choose between no access and full disclosure.
- **path:** pendant → relay → browser-extension → browser → mac-planner → mac-vision
- **model tier:** Use a cheap local/relay redaction pass for deterministic secret patterns and a low-cost classifier for contextual sensitive data; use realtime only for the spoken request, concise summary, and explicit field-reveal exchange. mac-vision is fallback for content visible only in rendered UI.
- **latency:** Speak an acknowledgement under 500 ms; provide a redacted summary in 3–8 s. A narrowly scoped reveal should complete in under 3 s and expire immediately after playback.
- **cost:** One realtime turn and one inexpensive extraction/redaction call; OCR or rendered-page inspection is the main latency/cost driver. No large page should be sent to the realtime model.
- **security:** Redaction must happen before content enters audio synthesis or long-lived logs, with defense-in-depth pattern matching for credentials, cards, and tokens. Keep only hashes/provenance and withheld-field labels. Require an explicit spoken confirmation naming the exact field for any reveal, play it once at reduced volume, and never expose an entire secret-bearing block.
- **missing:** A content firewall between browser/Mac extraction and relay TTS that enforces deterministic plus contextual redaction; Typed sensitive-span annotations with provenance and stable labels such as 'payment card ending 42' rather than raw values; A narrow, expiring reveal protocol bound to the current source snapshot and pendant session; Audio/logging guarantees that raw redacted spans cannot enter transcript, receipts, analytics, or model context


## What it asked for

_Nothing._
## Its own summary

Recorded three new owner-facing capabilities: federated spoken reference resolution across authenticated browser tabs and Mac files/apps; precise browser-to-Mac artifact transfer with provenance and receipts; and privacy-preserving read-aloud with pre-audio secret redaction plus narrowly scoped expiring reveal. The necessary changes are connective infrastructure between browser extraction, Mac adapters, relay correlation, and pendant audio—not merely more single-surface actions.

**Biggest unknown:** The backlog similarity checks indicate the first two may overlap earlier proposals (especially cross-surface handoff), while the pre-TTS content firewall and expiring field reveal appear more distinct. No further discovery was performed per instruction.

