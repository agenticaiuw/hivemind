# Harness derivation — browser-extension — round 227

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Use the private site I’m already logged into to gather the facts for this task, then prepare the answer in my Mac workspace and read me a three-sentence preview—do not submit or send it.”"
- **useful because:** The owner can combine information unavailable to public search with local files and notes in one spoken request. The browser supplies authenticated facts, the Mac supplies the draft destination, and the pendant gives a reviewable preview without forcing the owner back to a screen.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision
- **model tier:** Cheap planner and extraction model for navigation and field capture; use realtime only for the final spoken preview or ambiguity. Escalate to the local planner for multi-step page workflows.
- **latency:** 2–5 minutes for a multi-page gather-and-draft task; preview should begin within 5 seconds after the draft is ready.
- **cost:** About $0.05–$0.30 per task; authenticated page reads and vision fallback dominate, while local file edits are nearly free.
- **security:** Use browser action allowlists in read/extract mode, retain claim-level provenance only, and show the exact draft plus destination before any irreversible submit. Existing owner policy permits browser reading/clicking but requires confirmation before sending mail, deleting files, or buying.
- **missing:** A cross-surface job schema that links browser findings to a Mac draft; A structured extraction contract with field-level provenance and redaction; A pendant review card/voice protocol for approve, revise, or abandon

### "“When I’m looking at a page, let me say ‘save this decision’ or ‘remind me about this exact section,’ and later ask the pendant what the page said and where it came from.”"
- **useful because:** It captures the owner's intent at the moment it occurs, rather than saving an entire page or hoping a generic bookmark is meaningful. The browser provides the focused selection and URL, the relay turns it into a concise claim, and the pendant can replay the claim offline or answer provenance questions later.
- **path:** browser-extension → pendant → relay-realtime → mac-planner
- **model tier:** Small extraction/summarization model for the selected DOM region; realtime model only for follow-up voice questions. No model is needed for URL, title, and selection capture.
- **latency:** Capture confirmation under 2 seconds; later retrieval under 3 seconds when online, with the short alert available offline.
- **cost:** Under $0.02 per capture; extraction is the dominant cost and can be skipped when the selected text is already short.
- **security:** Capture only explicit user-selected/focused content, not the whole page. Store a bounded claim with URL, host, timestamp, and provenance under the existing browser TTL; redact configured categories and never persist screenshots or raw HTML. Do not speak claims classified as must-not-speak.
- **missing:** An extension command that returns the active selection/focused DOM region; A browser finding type for explicit user bookmarks with expiry/forget controls; A voice query that joins only matching browser facts

### "“Find the tab where I was working on that contract or receipt, tell me which one it is, and put it back in front on my Mac.”"
- **useful because:** Safari sessions accumulate important work that is otherwise invisible to the voice and Mac agents. Semantic tab triage would let the owner recover a private logged-in workflow by description, without manually opening nine tabs or exposing unrelated page contents. The browser identifies candidates, the relay asks one concise disambiguation if needed, and the Mac/extension foregrounds only the chosen tab.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Local lightweight tab-title/URL classifier first; cheap extraction only for candidate tabs; realtime model only to resolve ambiguity in the owner's short spoken description.
- **latency:** List and rank tabs in under 3 seconds; foreground the selected tab within 5 seconds. Never read every page body unless the owner explicitly asks.
- **cost:** Usually below $0.01 per request; cost is dominated by extracting candidate tab metadata, not generation.
- **security:** Keep candidate metadata in memory only unless the owner explicitly bookmarks it. Do not infer or announce sensitive page contents while ranking; speak title/host only until the owner selects a tab. Navigating/foregrounding is reversible, and no form action is performed.
- **missing:** A real browser_list_tabs result that includes stable tab IDs, titles, URLs, and active state; A semantic tab-ranking action and foreground/focus command in the extension bridge; A short-lived cross-surface context token so Mac actions target the chosen tab

### "“When a private website asks me to upload or download something, have the browser and my Mac assemble the right local files, show me exactly what will be uploaded, and let me approve the upload from the pendant.”"
- **useful because:** Uploading the wrong document is a common, high-cost failure that neither a browser-only agent nor a file-only Mac agent can reliably prevent. The browser knows the authenticated destination and required fields; the Mac can inspect and prepare local files; the pendant provides a remote, spoken approval surface with an exact manifest.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant
- **model tier:** Cheap local planner for filename/type matching and document metadata; vision only when the site exposes requirements visually; realtime model only to explain the proposed manifest and collect approval.
- **latency:** 30–90 seconds for a multi-file preflight; approval response under 3 seconds after the owner presses the button.
- **cost:** $0.03–$0.20 per preflight, dominated by OCR/vision for ambiguous documents; local hashing and metadata checks are negligible.
- **security:** The owner sees filenames, sizes, destinations, and extracted document types before upload. Never upload or submit until explicit pendant approval. Hashes and a short-lived receipt may persist; raw documents and page contents stay local. Destructive/send policy remains intact.
- **missing:** A browser action contract for upload-field discovery without submitting; A Mac-side file candidate matcher with content-type and redaction preview; A signed approval token binding the exact file hashes to the exact browser upload fields; A pendant spoken manifest/approval interaction

### "“Pause my private web task on the Mac and resume it later from the pendant, even if the browser was closed, with the exact page, fields, and next step restored.”"
- **useful because:** Long authenticated workflows—applications, claims, travel, onboarding—fail today when a tab closes or the owner leaves the desk. A resumable handoff would preserve the browser's session reach while letting the owner continue from the wearable, without storing a page dump or asking the owner to reconstruct context.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background state serializer and deterministic browser replay; use a cheap model only to re-identify changed DOM elements, and realtime only for a spoken recovery question.
- **latency:** Checkpoint under 2 seconds; resume within 10 seconds. If the page changed, report the first mismatch rather than guessing.
- **cost:** Under $0.05 per checkpoint/resume; model cost appears only when selectors or page structure drift.
- **security:** Store encrypted, bounded workflow state: origin, tab identity, non-secret field labels, redacted values, and selector fingerprints—not passwords, cookies, page HTML, or screenshots. Expire checkpoints quickly and let the owner delete them. Never replay a submit/send/purchase action without fresh approval.
- **missing:** A durable browser workflow checkpoint schema and encrypted store; Extension support for restoring a tab and reporting selector/field state; A replay engine that detects DOM drift and stops safely; Pendant controls for resume, inspect-next-step, and discard

### "“Compare the private offer, policy, or bill I’m viewing with the local document or earlier version I choose, and tell me the exact differences that matter before I agree to anything.”"
- **useful because:** The browser can access the current authenticated version while the Mac can access the owner's local records; neither surface alone can perform a trustworthy comparison. A field-level diff—price, dates, exclusions, renewal terms, names—would catch silent changes before the owner accepts them, and the pendant makes the result usable away from the screen.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant
- **model tier:** Deterministic text/table diff first, with a cheap extraction model for page and PDF structure; realtime model only to explain the ranked material differences.
- **latency:** Under 60 seconds for two ordinary documents; speak the top three differences within 5 seconds of completion.
- **cost:** $0.05–$0.25 per comparison, with OCR/vision for scanned PDFs as the main cost.
- **security:** Keep source documents local where possible and persist only a short-lived diff receipt with URLs/file paths and hashes. Redact account numbers and secrets from speech by default. This is analysis only: no acceptance, payment, or submission is performed.
- **missing:** A browser focused-region/document extraction result with stable provenance; A local document parser that emits normalized clauses and tables; A cross-surface comparison job and materiality ranker; A pendant result format supporting a concise diff plus ‘read next difference’


## What it asked for

_Nothing._
## Its own summary

Discovered the live owner context and granted browser surface, then recorded three distinct browser capabilities: (1) authenticated page-to-Mac drafting with pendant preview and no auto-submit, (2) explicit page-section decision capture with provenance and offline replay, and (3) semantic recovery/focus of a lost Safari tab. An attempted authenticated change watcher collided with an existing backlog item and was not restated. The strongest new direction is cross-surface authenticated research-to-draft: private Safari facts become a locally reviewable draft, while the pendant gives the owner a concise spoken preview and preserves the stop-before-send boundary.

**Biggest unknown:** I still need the extension-side primitives that are absent or unverified: stable tab metadata plus active-tab/focus control, explicit-selection extraction, and a cross-surface job/context token. I also still need the owner to supply origins and retention/speaking rules; those must remain an empty explicit configuration rather than invented defaults. The previously requested browser current-page/focus tools remain unavailable this round.

