# Harness derivation — browser-extension — round 268

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Check the authenticated sites I have configured, find only items that genuinely need my attention, and give me one short spoken queue I can work through from the pendant.”"
- **useful because:** This is the single most useful browser capability: it turns otherwise stranded logged-in web state into an actionable, low-noise queue without requiring the owner to open every site. It spans authenticated Safari tabs, local reasoning, an always-awake relay, and the pendant's offline alert inbox. It ships with an empty origin configuration; the owner adds sites and per-origin extraction rules later.
- **path:** browser → mac-bridge → relay → pendant → dashboard
- **model tier:** Use a cheaper background model for per-origin page extraction and deduplication; use realtime only to answer the owner's spoken follow-up or read the final queue. The Mac planner should rank urgency and merge duplicate items, while the browser remains the only component that sees logged-in pages.
- **latency:** Initial sweep 20–45 seconds for 3–5 configured origins; spoken queue begins as soon as the first origin is complete. Follow-up questions under 2 seconds when the short-lived finding and provenance capsule are already available.
- **cost:** Roughly $0.02–$0.10 per sweep depending on page count and extraction tokens; browser calls and relay wakeups dominate latency, not model cost. Do not send full HTML to the model when targeted extraction succeeds.
- **security:** Never assume sites or categories: configuration starts empty and is explicit per origin. Persist only short claims with URL/evidence provenance under the existing 24-hour, 200-character browser-fact bounds; never store page text or screenshots. Speak only matched findings, and show the source host in the queue. Form actions are out of scope for the sweep.
- **missing:** A durable per-origin configuration UI/API for read/extract/redact/never-store and may-speak/must-not-speak rules, initially empty; A reliable browser action dispatcher (the currently granted wrappers remain ambiguous at runtime); A scheduler/job runner that can fan out configured origins and publish ranked results to offline_alert_inbox

### "“I’m looking at this page—tell me what the highlighted section means, compare it with the last page I asked about, and remember only the conclusion.”"
- **useful because:** It makes the owner's existing authenticated browser context conversational from the pendant: no copying URLs or exposing page contents to another service. The extension supplies the current tab and a bounded selection; the Mac planner compares it with a prior provenance-backed claim; the relay speaks a concise answer. It is useful for dense contracts, bills, dashboards, and documentation where a whole-page scrape is wasteful.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** A small background model extracts the selected DOM region and normalizes the prior claim; realtime handles the owner's immediate question and interruption. Escalate to the expensive model only on ambiguity or conflicting values.
- **latency:** Under 3 seconds from a pendant request when the tab is already connected; under 10 seconds if a prior page must be re-read. Never wait for a full-page capture if the selection can be bounded.
- **cost:** About $0.005–$0.03 per question; DOM extraction and a tiny comparison prompt dominate. No screenshot or full-page token bill unless the owner explicitly asks for visual interpretation.
- **security:** Selection-only by default, with a visible browser indicator while capture is active. Do not persist selected text; persist at most the resulting claim using existing browser-finding TTL/size/provenance rules, and only if the owner says “remember.” Redact secrets before relay speech. Never click or submit as part of answering.
- **missing:** A functioning action:browser_read_page/browser_snapshot dispatch with an explicit tab or selection handle (current wrappers are unresolved/ambiguous); An extension event exposing active-tab and DOM selection context, rather than relying on a guessed tab; A spoken “remember this conclusion” intent that writes a bounded claim, not page content

### "“Prepare this web form from the facts in my local files and calendar, then give me a spoken diff of every field before anything is sent.”"
- **useful because:** This joins the browser's authenticated session with information physically available only to the Mac, while keeping the owner in control of the final irreversible step. It eliminates transcription errors for applications, claims, travel, and account forms: the system explains each proposed value, flags conflicts or missing evidence, and leaves a resumable draft in the browser. The pendant is the review surface even when the owner is away from the Mac.
- **path:** browser → mac-bridge → relay → pendant → dashboard
- **model tier:** Use a background model to map local facts into field candidates and detect conflicts; use realtime only for the spoken field-by-field review and owner corrections. A deterministic field-diff renderer should produce the final payload without another expensive model call.
- **latency:** 30–90 seconds for a multi-section form, with incremental progress after each page. Each spoken correction should update the draft within 5 seconds. Stop at submission and return an exact payload plus any attachments that would be sent.
- **cost:** Approximately $0.03–$0.20 per form, driven by DOM extraction, local-file/calendar context, and occasional OCR; subsequent corrections are cheap. Browser interaction latency is the main user-visible cost.
- **security:** The browser action allow-set must permit navigation, field filling, and reading but explicitly exclude submit/send/purchase for the preparation phase. Show origin, destination, every changed field, and attachment names. Do not persist raw field values or page text; retain only an undoable fill receipt and short provenance claims. Owner can explicitly request submission as a separate action, with a fresh exact-payload preview.
- **missing:** Reliable browser fill/read actions with stable field identifiers across navigation; A Mac context adapter that returns only the selected local facts/calendar entries, with provenance and redaction; A durable draft session that survives Safari reloads and supports undo via existing browser/job receipts; A pendant protocol for paging through field diffs and recording corrections

### "“While I’m in a logged-in support chat, read the other person’s latest message, draft the best reply from my local context, and let me correct it by voice before you type it.”"
- **useful because:** This gives the owner an assistant inside authenticated conversations without handing message-sending authority to an opaque automation. The browser extension sees the private chat, the Mac supplies relevant local facts, the relay handles low-latency spoken correction, and the pendant lets the owner operate while away from the keyboard. It is materially different from reading a page or filling a static form: the system maintains a live conversational turn and preserves who said what.
- **path:** browser → mac-bridge → relay → pendant → dashboard
- **model tier:** Use a background model for thread summarization, local-context retrieval, and a first draft. Use realtime only for the owner's correction loop. The browser should type only the approved draft; sending remains a separate explicit owner command.
- **latency:** Draft within 5 seconds of a new incoming message; spoken correction reflected in under 2 seconds; keep the draft alive while the chat changes and invalidate it if the other party replies first.
- **cost:** Approximately $0.02–$0.08 per turn, dominated by thread extraction and context retrieval. Realtime voice is used only during correction, avoiding an expensive call for every page poll.
- **security:** Start with an empty origin configuration and no invented chat sites. Never send automatically. Display the exact draft, source facts, and any uncertain claims; redact secrets and do not persist the conversation body. Persist only a short-lived draft hash/provenance record and an undoable typed-text receipt.
- **missing:** A mutation-aware browser session that can detect an incoming chat turn and type a draft into the correct composer; A context selector that limits local files/calendar facts to those the owner explicitly makes available for this conversation; A pendant protocol for approve, revise, and discard of a draft with turn/version IDs; Conflict handling when the remote participant sends a new message during voice correction

### "“Before I send this web transaction, compare the exact payload against my calendar, local records, and what this site showed earlier; tell me only about contradictions or surprising changes.”"
- **useful because:** The owner gets a last-second semantic audit that no browser-only automation or Mac-only agent can perform. It catches changed prices, dates, account numbers, quantities, and stale form values by joining the authenticated page with local evidence and a prior page snapshot. It is advisory rather than a new permission gate: the owner may proceed, but receives a compact explanation through the pendant before an irreversible action.
- **path:** browser → mac-bridge → relay → pendant → dashboard
- **model tier:** Use deterministic field/value comparison first; a background model explains only genuine discrepancies and ranks severity. Use realtime to read the short anomaly report and answer “why?”; do not send the full payload into every voice turn.
- **latency:** 2–5 seconds after the final form state is available; audit incrementally while fields change so the final check is nearly immediate. If evidence is unavailable, say so rather than claiming a clean audit.
- **cost:** About $0.005–$0.04 per audit, mostly deterministic and therefore inexpensive. Costs rise only for ambiguous labels or document interpretation.
- **security:** The audit must not mutate the page or block execution. Keep raw payloads on the Mac/browser boundary; send the relay only redacted anomalies and field labels. Persist an expiring receipt containing hashes, source URLs, and comparison time—not form contents. Treat browser values as untrusted until compared with an owner-selected local source.
- **missing:** A browser submit-interception/preflight hook that exposes the exact would-be request without changing or sending it; A stable field/value normalization layer that understands dates, currencies, quantities, and account identifiers; An owner-selectable evidence bundle from local files/calendar with provenance and redaction; A pendant-friendly anomaly summary and a way to request the exact field comparison

### "“When I finish booking something in a logged-in site, reconcile the confirmation with my calendar and phone, point out any collision or hidden time-zone change, and prepare the right calendar update.”"
- **useful because:** A booking is not complete when the website says “confirmed”: the owner needs the commitment reflected correctly across calendar and phone. This joins authenticated browser confirmation, local calendar state, iPhone display, relay reasoning, and pendant notification. It catches silent time-zone conversions, duplicate reservations, cancellation windows, and overlaps that each individual node cannot see alone.
- **path:** browser → mac-bridge → ios → relay → pendant → dashboard
- **model tier:** Use deterministic extraction and calendar arithmetic for dates, locations, time zones, and identifiers. Use a background model only to interpret irregular confirmation language. Realtime is reserved for the owner asking why a conflict was found; ordinary reconciliation should be silent or a short pendant alert.
- **latency:** Extract within 5 seconds of a confirmation page appearing and produce a conflict report within 3 seconds. Keep a short retry window for sites that render confirmation details asynchronously. Calendar mutation should be a separately visible prepared update.
- **cost:** Approximately $0.005–$0.03 per confirmation; most work is DOM extraction and timezone arithmetic. Model spend is limited to unusual page layouts.
- **security:** Never infer a booking from a button click alone: require a confirmation state and stable booking identifier. Do not persist page text, payment details, or full itinerary; store only bounded claims and provenance. Show the exact proposed calendar diff, origin, and timezone. Treat cancellation or modification as a distinct action and never perform it during reconciliation.
- **missing:** A browser completion detector that recognizes booking/confirmation state across configured origins; A normalized itinerary object with timezone, cancellation deadline, and booking identifier fields; A calendar/phone reconciliation service that can propose but not silently apply updates; Pendant alert payloads capable of distinguishing a conflict, a timezone warning, and a clean confirmation


## What it asked for

_Nothing._
