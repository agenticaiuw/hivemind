# Harness derivation — browser-extension — round 158

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Watch the authenticated page I nominate in Safari and, when its contents materially change, tell me on the pendant exactly what changed and why it matters; keep checking while my Mac is asleep and queue the alert until I press the button."
- **useful because:** This is the one place the browser node is uniquely valuable: it can see a logged-in dashboard or account page that public search and the relay cannot. A semantic diff plus a queued spoken alert turns a fragile open tab into a dependable personal sentinel without requiring the owner to keep checking it.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** background for scheduled page capture and cheap semantic diff; realtime only to answer a follow-up spoken question
- **latency:** Initial setup under 10 seconds; each poll under 3 seconds and alert generation under 15 seconds; no foreground interaction required.
- **cost:** About $0.01–$0.05 per changed page check depending on capture size; most unchanged polls should use hashes/local extraction and cost near zero.
- **security:** Page text is authenticated and sensitive. Store only a redacted change summary and hashes by default, never raw page text; per-origin read/redact/never-store rules must be explicit and initially empty. Never click or submit. Alert content must obey a separate may-speak/must-not-speak category configuration.
- **missing:** durable scheduled browser page-watch runner; semantic DOM diff with local redaction and per-origin policy; relay-to-pendant delivery using the accepted offline_alert_inbox skill; owner-configurable origin and spoken-category rules

### "After I say “reconcile my booking,” inspect the authenticated confirmation page currently open in Safari, compare its date, time, location, amount and cancellation terms with the matching calendar event on my Mac, and speak only the discrepancies; do not change either system."
- **useful because:** Today the browser can read a confirmation and the Mac can read a calendar, but neither can establish that the two records agree. Catching a wrong timezone, venue, duplicate booking, or changed price before the appointment is the highest-value use of authenticated browser access that requires both nodes.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** background extraction and deterministic field comparison first; realtime model only for ambiguous matching or the owner's spoken clarification
- **latency:** Under 20 seconds for one open confirmation and its candidate calendar events; ask one concise clarification if there are multiple candidates.
- **cost:** $0.02–$0.10 per reconciliation, dominated by one small model call only when deterministic matching fails; DOM extraction and calendar reads are local.
- **security:** Never persist confirmation page text or booking identifiers beyond a short-lived encrypted job record. Speak amounts and locations only after applying the owner's configurable may-speak policy. Read-only browser and calendar actions; no booking edits or cancellation clicks.
- **missing:** cross-surface entity matcher for browser confirmation fields and Mac calendar records; structured extractor adapters that return typed fields with provenance rather than raw page text; short-lived sensitive-data vault with automatic expiry; a pendant voice intent that identifies which open confirmation to reconcile

### "Find every deadline or renewal date on the authenticated page open in Safari, explain the source sentence, and create Mac reminders for the dates with the page title and URL in the note; if the date is ambiguous, ask me instead of guessing."
- **useful because:** A logged-in invoice, insurance, benefits, school, or subscription page often contains dates that public tools cannot see. Turning those dates into durable Mac reminders while preserving the exact source gives the owner a practical outcome from browser access rather than another summary they must manually transcribe.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** cheap background DOM extraction plus deterministic date normalization; realtime only for ambiguity resolution and spoken delivery
- **latency:** 10–20 seconds per page; reminders should be created in the same interaction, with a concise spoken confirmation.
- **cost:** $0.01–$0.05 per page; local extraction and date parsing dominate, with a small model fallback for messy prose.
- **security:** Do not retain page body after extracting the deadline sentence; redact account numbers and amounts from reminder notes unless the owner explicitly enables them. Browser action is read-only; reminder creation is reversible and must emit a receipt and support undo.
- **missing:** typed deadline/date extractor with sentence-level provenance; calendar/timezone disambiguation tied to Mac locale; secure handoff that strips unrelated page text before model processing; one command that chains browser extraction to create_reminder and returns an undo receipt

### "When I say “make me an evidence pack,” collect the relevant facts from the authenticated Safari tabs I name and the matching local files on my Mac, reconcile contradictions, and give me a short answer with a source trail I can reopen later—without saving the underlying page or document text."
- **useful because:** The owner currently has to manually copy sensitive facts from several logged-in sites and local documents into one place. This would make the browser's unique reach useful for research and life-admin decisions while returning verifiable sources instead of an opaque summary.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** background extraction and deterministic entity/field reconciliation; realtime only for the final spoken answer or ambiguity questions
- **latency:** Under 45 seconds for up to five sources; stream progress to the pendant if a source is slow.
- **cost:** Roughly $0.05–$0.25 per pack, dominated by extracting and reconciling multiple sources; unchanged pages can be reused by content hash without resending text.
- **security:** Underlying content must stay ephemeral and encrypted; persist only source URLs, timestamps, field-level hashes, and the owner's explicit saved citations. Per-origin and per-category speak/persist rules must be supplied by the owner, not assumed. Never submit forms or send messages.
- **missing:** multi-source browser extraction addressed to explicit tab IDs rather than the active tab; field-level provenance graph that links each claim to a source range; ephemeral encrypted cross-surface workspace with automatic expiry; owner-configurable per-origin read/redact/never-store and per-category may-speak rules

### "While I browse, let me press the pendant button and ask “what is selected?” or “what happens if I activate this?” Have Safari report the focused control and its surrounding context, then explain it aloud and optionally carry out only the exact reversible action I name."
- **useful because:** Authenticated sites often hide meaning behind unlabeled controls, dense tables, or custom widgets that generic page text misses. Focus-aware help would let the owner operate unfamiliar sites hands-free and with far less trial and error, using the browser session no other node can reach.
- **path:** pendant → browser-extension → relay-realtime → mac-planner
- **model tier:** realtime for low-latency focused-control explanation; cheap local DOM classification first, with the model receiving only the focused subtree and nearby labels
- **latency:** A spoken explanation within 2 seconds of the button press; a reversible named action within 5 seconds.
- **cost:** A few cents per question; local DOM extraction should avoid model calls for obvious controls.
- **security:** Focused text can contain private account data. Apply origin/category redaction before transmission; do not infer or speak secrets such as password fields or full payment numbers. Keep the owner’s maximum-access policy, but produce an action receipt and never silently broaden a requested click into a submit or send.
- **missing:** extension command to return active element, accessible role/name, and bounded surrounding DOM; pendant event carrying a short query plus current browser session/tab provenance; reversible-action planner that distinguishes a named control from nearby submit/send controls; low-latency result streaming from extension through relay to pendant

### "When I say “witness this page,” capture a privacy-redacted, tamper-evident record of exactly what the authenticated page showed at that moment, with the URL, time, and a short spoken summary, so I can later prove what I saw without keeping the whole page."
- **useful because:** For account balances, policy terms, order status, and deadlines, a later dispute may depend on what the owner actually saw. Today the browser can read a page but cannot give the owner a durable, independently verifiable witness record while minimizing retained sensitive content.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** background for redaction, hashing, and signed evidence packaging; realtime only for the immediate spoken summary
- **latency:** Under 8 seconds for a normal page; the pendant confirms the receipt ID immediately and can defer upload/indexing.
- **cost:** Under $0.05 per witness record; local hashing and redaction dominate, with optional small summarization cost.
- **security:** Raw page text and screenshots should be opt-in, encrypted, and expiry-controlled. Default record contains a redacted excerpt, content hash, URL, timestamp, tab provenance, and signature. The owner must choose retention and whether the record may be spoken or shared; never expose cookies or credentials.
- **missing:** signed browser evidence envelope bound to URL, tab, timestamp, and content hash; selective redaction that runs before persistence and supports owner review; durable encrypted evidence store with expiry and export/revocation; pendant command and receipt lookup for later “what did I witness?” questions


## Changes it proposed to its own stack

### `browser-harness` — Make the granted browser_enqueue_command resolve to the already-live POST /execute browser action path, preserving the exact browser_* enum names and returning typed results (including the actual tabId selected). Remove the five ambiguous/unimplemented wrappers so an agent can reliably list, navigate, read, and target a tab without hand-crafting HTTP.
- **owner gets:** The authenticated browser is online with nine Safari tabs, but the only browser tools exposed to the agent are unresolved stubs. Today the owner can have the system read the active X page only because I bypassed the tool and posted /execute directly; fixing this makes logged-in Gmail and other pages reliably usable in ordinary voice requests.
- effort: Small-to-medium: tool manifest mapping plus an integration test for list_tabs, navigate, browser_read_page, click, type, and browser_press_key; no extension rewrite.  ·  risk: A bad mapping could dispatch the wrong browser action or target the wrong tab. Recover by returning typed errors, requiring explicit tab/session IDs for non-active reads, and retaining existing command receipts and cancellation.
- cost: Negligible API cost; one small backend/tool registration change.  ·  latency: No meaningful change; retain the existing extension poll and 45-second result timeout.
- security: No new authority—the path already reaches authenticated Safari. Preserve origin/session provenance and redact page content in tool errors and logs.
- depends on: POST /execute; GET /browser/poll; POST /browser/result/:commandId; GET /browser/sessions


## What it asked for

_Nothing._
## Its own summary

This round produced three distinct browser-only cross-surface capabilities: authenticated semantic page-change alerts queued to the pendant, booking/confirmation reconciliation against Mac Calendar, and extracting authenticated deadlines into reversible Mac reminders with source provenance. I also proposed repairing the browser harness so its granted enqueue tool actually maps to the live /execute path. Safari is genuinely online now with nine tabs, including authenticated Gmail and X; direct POST /execute browser_list_tabs and browser_read_page succeed, though read currently follows the active tab even when a tabId is supplied.

**Biggest unknown:** I still need the owner to provide explicit per-origin rules (which first sites may be read, what may be spoken, and what may never be persisted). I also need a functioning resolved browser enqueue tool or a supported typed tab-targeting contract; today I can work around it with direct /execute, but ordinary agent invocation cannot.

