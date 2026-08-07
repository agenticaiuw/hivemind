# Harness derivation — browser-extension — round 140

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Watch the authenticated GitHub and Gmail tabs for new build failures or security notices; when a genuinely new urgent issue appears, tell me in one spoken sentence on the pendant, include the source link, and never alert twice for the same incident."
- **useful because:** The browser can see private inbox and GitHub sessions that public search cannot. A semantic, deduplicated interrupt turns failures into timely action without requiring the owner to remember to ask.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** background cheap model for polling, extraction, and deduplication; realtime only to phrase and deliver the interrupt
- **latency:** Poll every 5 minutes; alert within 30 seconds of a changed page. No owner interaction unless they ask for detail.
- **cost:** About $0.01–$0.05/day for compact page diffs and classification; browser polling and relay delivery dominate engineering, not tokens.
- **security:** Private Gmail/GitHub text leaves Safari to the local agent and relay. Store hashes and minimal excerpts, redact tokens and message bodies, and require explicit opt-in per origin. Never click, reply, or send.
- **missing:** origin watch registry with per-origin selectors and authenticated session health; semantic page-diff plus incident deduplication state; pendant push/audio interrupt route; quiet hours and escalation policy

### "While I am in a browser meeting, let me say 'mute', 'unmute', or 'leave' to the pendant and have the browser perform that exact meeting control, then speak back the verified state; if the meeting tab disappears, tell me instead of guessing."
- **useful because:** A worn button or voice command is faster and safer than finding a hidden browser tab during a meeting. It combines the pendant's always-available input, the Mac's local control, and the browser's authenticated meeting session.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** realtime for intent parsing and short confirmation; deterministic browser selectors/state checks for execution
- **latency:** Under 2 seconds for mute/unmute state confirmation; leave can complete in under 3 seconds. No long model loop.
- **cost:** <$0.01 per command; almost all cost is local browser action and state verification.
- **security:** Mute is reversible; leave is disruptive and should require a spoken confirmation. Restrict control to the active meeting tab and do not transmit participant names/audio. If verification fails, report unknown state rather than retrying blindly.
- **missing:** meeting-provider adapters for Zoom/Meet/Teams DOM and accessibility labels; active-tab classification and state verification after click; pendant-to-relay low-latency command path while USB/LTE transitions; explicit confirmation only for leave

### "From the pendant, say 'save this page' while I am reading any logged-in web page; capture the relevant selection or article, URL, title, and timestamp into my AI-Pendant-Workspace notes, and later let me ask for the saved excerpt by topic."
- **useful because:** The browser has access to private pages and the pendant is available when the owner's hands are busy. This creates a durable, provenance-rich memory instead of losing useful research in an open tab.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** cheap background model for cleanup, tagging, and deduplication; realtime only for the spoken acknowledgment
- **latency:** Capture acknowledgment within 3 seconds; indexing can finish asynchronously within a minute.
- **cost:** <$0.02 per saved page for extraction/tagging; storage and browser extraction dominate.
- **security:** Persist only the requested selection by default, not entire pages; retain origin, URL, and capture time for provenance. Require a local confirmation phrase before saving content from sensitive origins; encrypt notes at rest and redact passwords/forms.
- **missing:** browser selection extraction and a stable content capsule format; workspace note writer with origin/URL provenance and encrypted storage; pendant voice command binding and later semantic retrieval; per-origin retention and sensitive-site policy

### "Compare the private page I am looking at with my last saved view and tell me exactly what changed, with the old and new snippets and a link; do not summarize unchanged boilerplate."
- **useful because:** This is a browser-exclusive operation on authenticated pages and is useful for dashboards, application status, and long forms where ordinary page reading overwhelms the owner. It answers a precise question on demand rather than polling everything.
- **path:** browser-extension → mac-planner → relay-realtime
- **model tier:** cheap background diffing for DOM normalization and snippet selection; realtime only for the final one-sentence spoken answer
- **latency:** Under 5 seconds for pages under 100 KB; return a partial diff if extraction times out.
- **cost:** <$0.01 per comparison; page extraction and local snapshot storage dominate.
- **security:** Snapshots can contain private data. Encrypt them locally, retain only the selected origin and normalized text, cap retention, and never send a full page to the relay when snippets suffice.
- **missing:** per-origin snapshot store with owner-controlled retention; DOM normalization that ignores ads, timestamps, and randomized IDs; evidence-linked diff response with old/new snippets; explicit handling for pages that block extension script access

### "When I say “what am I looking at?”, read the visible browser region under my pointer or the selected screen rectangle, identify the controls and values there, and answer through the pendant with coordinates and a link to the current tab."
- **useful because:** The owner can ask about a dense private dashboard, error dialog, or form without describing it verbally. Browser DOM extraction misses canvas-based and visual-only interfaces; this combines Safari access with Mac vision and the pendant’s hands-free conversation.
- **path:** pendant → relay-realtime → mac-vision → browser-extension
- **model tier:** realtime vision model only for the cropped region; deterministic local capture and OCR first to keep context and cost small
- **latency:** Answer within 3 seconds for a crop; fall back to a spoken “I cannot identify that region” rather than guessing.
- **cost:** Roughly $0.01–$0.08 per query depending on crop resolution; local screenshot/OCR is the dominant latency, with model cost proportional to the crop.
- **security:** The crop may contain private credentials or customer data. Capture only the requested rectangle, never retain it by default, redact password fields, and do not transmit the entire tab or screen.
- **missing:** pointer/rectangle capture command in the Safari extension; local crop-and-redact service shared with mac-vision; coordinate-to-DOM-element mapping for actionable links; pendant query binding and short spoken response path

### "Say “bring me back to where I left off” and have the browser reopen the exact private document, scroll position, selected text, and related tab group from my last session, even after Safari restarted."
- **useful because:** The owner loses substantial time reconstructing research and work state. A durable browser workspace would preserve authenticated context without making the owner bookmark every intermediate page.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** cheap deterministic state capture and restore; realtime only to resolve an ambiguous spoken workspace name
- **latency:** Restore within 5 seconds for up to 10 tabs; report each tab that could not be restored.
- **cost:** Under $0.01 per restore; encrypted local state storage and extension restore operations dominate.
- **security:** Session URLs, selections, and titles reveal private activity. Encrypt state locally, retain only owner-selected workspaces, expire credentials and signed URLs, and never copy page contents unless explicitly requested.
- **missing:** durable tab-group/workspace store with scroll and selection metadata; extension support for tab-group creation and scroll restoration; authenticated-session health check before restore; conflict handling when a URL or document has changed

### "When a private web service presents a security warning, suspicious login prompt, changed permissions page, or unexpected payment request, tell me exactly what changed and who is asking, preserve a local evidence snapshot, and give me a safe path back without clicking the dangerous control."
- **useful because:** The browser is the only node holding the owner’s authenticated sessions, making it the right place to detect account takeover signals and deceptive prompts before the owner acts. It provides practical protection without silently blocking normal work.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** cheap local rules and page classification first; realtime model only for ambiguous warning language and concise explanation
- **latency:** Classify within 2 seconds of page load or navigation; speak an alert within 5 seconds when high confidence.
- **cost:** <$0.02 per inspected page with local text rules; ambiguous screenshots cause occasional vision-model spend.
- **security:** Inspection itself touches sensitive pages. Keep evidence encrypted on the Mac, minimize transmitted text, do not click or submit anything automatically, and allow the owner to delete evidence. False positives must offer an inspect-only explanation rather than blocking.
- **missing:** navigation/page-load event stream from the extension; known-good origin and page-integrity baselines; local evidence snapshot plus redaction engine; safe-back navigation and verified alert delivery to the pendant


## What it asked for

_Nothing._
