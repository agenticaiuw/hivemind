# Harness derivation — mac-planner — round 236

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-accessibility-live** — AI Pendant Agent has Accessibility and Screen Recording granted; synthesized input probe succeeds, secure input is false, and UI actions should reach the screen. Safari is foreground with three durable browser sessions.
  - evidence: mac_readonly_inspect operation running_apps/foreground_app resolved to GET /observe at 2026-08-08T23:03:43Z; response accessibility.trusted=true, screenRecording=true, eventsPost=true, browser.sessions=3, foregroundApp=Safari.

## Capabilities it proposed

### "When I press the pendant's bookmark button, save what I was actually doing on the Mac and browser at that instant so I can say later, "take me back to that moment.""
- **useful because:** A timestamp alone is not useful memory. This binds the physical moment to the foreground app, open browser session, relevant files, and the voice pipeline, then reconstructs the workspace later instead of making the owner hunt.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only for the button acknowledgement and later voice lookup; a cheaper background model extracts a short label and deduplicates workspace state.
- **latency:** LED acknowledgement immediately; capture under 2 seconds; spoken lookup under 3 seconds; reopening the saved workspace under 5 seconds.
- **cost:** About $0.005-$0.03 per bookmark, dominated by optional summarization; raw state capture is local and effectively free.
- **security:** URLs, document names, and selected snippets can be sensitive. Store encrypted, redact query strings and passwords, and require an owner-configured policy before reopening external URLs or sending anything.
- **missing:** A durable cross-surface bookmark schema joining pendant event IDs to Mac/browser snapshots; A read-only semantic document/window identity operation beyond the current generic observe snapshot; An explicit owner-selected retention and redaction policy

### "Is my pendant healthy? Run a complete audio and link check while it is plugged into my Mac, explain the failure in plain language, and tell me whether I should trust it for my next call."
- **useful because:** Today a failed call can come from capture, Opus, USB/serial, radio, relay, or playback and the owner cannot distinguish them. A deterministic fixture plus the relay's live pipeline turns that into a go/no-go answer before an important conversation.
- **path:** pendant → mac-planner → mac-terminal → relay → dashboard
- **model tier:** Use deterministic firmware counters and a cheap background model for diagnosis; reserve realtime only if the owner asks follow-up questions by voice.
- **latency:** Start immediately when USB presence is detected; fixture and report in 30-90 seconds; voice answer in under 3 seconds after completion.
- **cost:** Under $0.02 per run; almost all work is local counters and log parsing, not model inference.
- **security:** The fixture must be synthetic and never capture microphone content. USB logs may include timestamps and device identifiers; retain only aggregate counters and a short receipt.
- **missing:** A bounded, receipt-producing Mac USB serial runner that can arm the existing diagnostic fixture and read its complete report; A correlation service joining fixture sequence numbers with relay pipeline/audio counters; A user-facing health verdict with explicit numeric acceptance thresholds

### "Read the page I am looking at, give me the important parts over the pendant, and if I say 'do the first one,' carry out only that specific follow-up on the Mac or in the browser."
- **useful because:** The owner can get information while walking away from the screen and then act without dictating URLs, copying text, or losing the current authenticated browser session. The two-step selection prevents a vague summary from silently becoming a consequential action.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → browser → dashboard
- **model tier:** Realtime for the short spoken summary and confirmation dialogue; a cheaper model extracts candidate actions and a deterministic executor performs the selected one.
- **latency:** Page snapshot under 2 seconds, summary under 5 seconds, selected action under 5 seconds.
- **cost:** Roughly $0.01-$0.08 per page, dominated by model context size; execution and page extraction are local.
- **security:** Authenticated pages can contain secrets and third-party data. Send only the current DOM/text selection, redact tokens and hidden fields, never expose cookies, and require explicit confirmation for external sends, purchases, deletes, or account changes.
- **missing:** A browser command that returns a bounded, redacted semantic page snapshot plus stable action IDs; A planner/executor contract that binds the spoken ordinal to the exact page snapshot hash and refuses stale actions; A Mac/browser policy configuration that the owner can set per action class

### "Before I send an email or submit a form, silently check it against my calendar, recent messages, and the current browser context; interrupt me on the pendant only when you find a concrete contradiction, such as a wrong date, recipient, timezone, attachment, or commitment."
- **useful because:** The most expensive mistakes are not spelling errors: they are sending the right words to the wrong person, promising a time already occupied, using a stale attachment, or submitting a form in the wrong account. No single surface can see the draft, calendar, mail history, and authenticated browser state together.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** A small background model extracts entities and compares dates, recipients, and commitments; realtime is reserved for the short, urgent pendant warning. Deterministic checks handle attachment existence, account identity, timezone, and calendar overlap.
- **latency:** Pre-send analysis must complete in under 1 second for a draft already on screen; a warning reaches the pendant within 500 ms and never blocks ordinary typing. Deep contradiction analysis can finish within 3 seconds before a final submit action.
- **cost:** Approximately $0.005-$0.03 per send, mostly for extracting commitments from draft/history; local deterministic checks dominate the common path.
- **security:** Drafts, mail, calendar, and authenticated page content are highly sensitive. Keep raw text on the Mac where possible, send only redacted structured facts to the relay, never transmit passwords or cookies, and make the warning advisory unless the owner explicitly configures a hard stop.
- **missing:** A pre-send browser and Mail interception hook that exposes the exact draft/form payload plus a stable submit fingerprint before transmission; A bounded Mac read surface for the current draft, selected account, attachments, and recipient identity without UI scraping; A cross-surface contradiction record that explains which local facts caused the warning and expires after the draft changes; An owner-configurable policy for which contradiction classes may interrupt the pendant

### "What have I promised other people that I have not followed through on? Give me only commitments with evidence from my sent mail, calendar, and browser work, and let me say 'schedule it' to create the smallest sensible next step."
- **useful because:** Promises are scattered across communication and work surfaces, while reminders capture only what the owner remembers to enter. This finds latent obligations, distinguishes commitments from casual language, and turns a spoken decision into a concrete calendar or reminder item.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheap background model for periodic extraction and deduplication; realtime only summarizes the few highest-confidence overdue commitments when asked.
- **latency:** Nightly scan under 2 minutes; on-demand answer under 8 seconds; creating a reminder under 3 seconds.
- **cost:** $0.03-$0.20 per nightly scan depending on sent-mail and browser volume; most filtering and date arithmetic is local.
- **security:** This processes private communications and may infer obligations incorrectly. Keep source excerpts local, show evidence and confidence, retain provenance, never contact another person automatically, and require explicit confirmation before creating or changing commitments.
- **missing:** A provenance-preserving commitment ledger that links each extracted obligation to exact Mail, Calendar, or browser evidence; A bounded write operation that creates a reminder/calendar item with the evidence link and confidence; A deduplication and expiry policy for completed, cancelled, or superseded promises

### "Before I forward this document, check every factual claim that matters against my local files and the current source page, mark what is stale or unsupported, and produce a corrected copy without sending it."
- **useful because:** The owner currently has to remember which source is authoritative, compare versions manually, and notice when a browser page has changed since a document was written. This turns the Mac, authenticated browser, and pendant into a private fact-checking desk while keeping the final send under the owner's control.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** A cheaper background model extracts claims and compares local/current sources; realtime is only for a concise spoken verdict. A deterministic diff preserves exact quotations, hashes, and source timestamps.
- **latency:** Small documents under 10 seconds; larger documents under 60 seconds with progress alerts; no outbound send without a separate owner command.
- **cost:** $0.03-$0.25 per document, dominated by claim extraction and source context; local file and browser reads are otherwise cheap.
- **security:** Documents may contain confidential material and authenticated sources may contain private data. Keep full text local, send only claim/source hashes when possible, redact secrets, preserve source permissions, and never publish the corrected copy automatically.
- **missing:** A Mac operation that reads a selected document and writes a versioned corrected copy without relying on fragile cursor focus; A browser snapshot API that returns source text, canonical URL, retrieval time, and authentication boundary; A citation-aware diff format that distinguishes contradiction, unsupported claim, and merely stale wording; A policy preventing model-generated corrections from being treated as authoritative without source evidence


## What it asked for

_Nothing._
## Its own summary

Round 236 produced three owner-facing proposals: (1) a pendant bookmark that captures and later restores the exact Mac/browser workspace, (2) a USB-attached synthetic end-to-end pendant health verdict before a call, and (3) spoken page reading with an ordinal action bound to a page snapshot hash. Live observation also established that Accessibility and Screen Recording are now granted for AI Pendant Agent, input posting succeeds, Safari is foreground, and three browser sessions exist. I told faculty-action the novelty seams.

**Biggest unknown:** The browser inspection capability is currently resolver-ambiguous between action:browser_inspect and POST /browser/inspect, so I still need a deterministic semantic browser snapshot/action-ID surface. I also still need a bounded receipt-producing USB serial fixture runner, a cross-surface bookmark schema, and owner-configurable redaction/action policy. Accessibility is no longer a blocker, but selected-text/document identity remains unobserved.

