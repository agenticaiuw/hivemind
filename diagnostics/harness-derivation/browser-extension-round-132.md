# Harness derivation — browser-extension — round 132

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser live state** — Safari extension is online with three tabs: authenticated Gmail inbox (tab 901464), and two example.com failed-open tabs. POST /execute browser_list_tabs and browser_read_page work; Gmail visibly contains multiple recent buckymatch GitHub Actions failures and 8 drafts.
  - evidence: GET /browser/status 200 at 2026-08-07T18:12:44Z; POST /execute browser_list_tabs and browser_read_page both returned success.

## Capabilities it proposed

### "“What am I looking at? Give me the important parts, and let me ask follow-up questions by voice.”"
- **useful because:** The pendant becomes a hands-free lens over the exact authenticated Safari tab in front of the owner. It avoids reading URLs or describing screens aloud, and unlike generic web search it can answer from private pages while preserving quoted evidence and links.
- **path:** pendant → browser-extension → relay-realtime → mac-planner
- **model tier:** Realtime for the short spoken summary and follow-up Q&A; a cheaper background model can pre-extract page sections and citations when the tab changes.
- **latency:** Initial capture and concise answer within 5 seconds; follow-up answers under 2 seconds when grounded text is already cached.
- **cost:** About $0.01–$0.05 per interaction depending on page length; browser extraction and cached follow-ups dominate less than realtime tokens.
- **security:** The active tab's authenticated text leaves Safari and is sent to the relay/model. Redact passwords, payment fields, hidden inputs, and unrelated tabs; show source URL and quoted snippets so the owner can detect a wrong-tab answer. No page mutations.
- **missing:** A reliable active-tab capture action that returns the tab identity and a bounded, sanitized text capsule; A pendant voice intent that binds the utterance to the current browser tab; Cross-surface citation objects that survive relay-to-pendant rendering

### "“Find the production failures in my logged-in inbox, open the linked runs, explain the root cause, and leave me a review packet on my Mac—do not send or merge anything.”"
- **useful because:** A noisy authenticated inbox becomes an actionable engineering triage packet: the browser can follow private GitHub links, the Mac can gather local repository/diagnostic context, and the pendant can announce only the highest-severity failure. No single node can correlate all three sources.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant
- **model tier:** Background/cheap model for email and run clustering; use realtime only to answer a spoken interruption such as “is production still down?”
- **latency:** Deliver a first packet in 30–90 seconds; continue collecting linked run details asynchronously and notify the pendant when complete.
- **cost:** Roughly $0.03–$0.20 per triage packet; authenticated page extraction and local diagnostics dominate, not the final summary.
- **security:** GitHub/email content and local logs are sensitive and must be scoped to matching failure threads. Never click merge, rerun, comment, or send. Keep source URLs, timestamps, and exact failure excerpts in the packet; require explicit owner instruction for any mutation later.
- **missing:** A cross-surface correlation job that maps inbox messages to linked private run pages and local repository evidence; A durable Mac artifact format for review packets with source citations and unresolved hypotheses; A pendant notification containing severity and a deep link back to the packet

### "“Before I book or buy this, check the logged-in page against my calendar and local budget, call out hidden commitments or conflicts, and fill only the reversible fields.”"
- **useful because:** The browser sees the real authenticated price, cancellation terms, and form; the Mac sees the owner's calendar and budget files; the pendant gives a quick spoken go/no-go explanation. It prevents costly double-bookings and surprise renewals without taking the irreversible purchase step.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant
- **model tier:** Cheap background model extracts dates, amounts, recurring terms, and cancellation rules; realtime model is used only for the owner's final spoken questions.
- **latency:** Analyze a loaded checkout or booking page within 10 seconds, then fill reversible fields in under 20 seconds.
- **cost:** About $0.02–$0.10 per check; browser page extraction and local file/calendar lookup dominate.
- **security:** Payment details, booking identity, calendar, and budgets are highly sensitive. Never read or expose full card numbers; mask personal data in the model context. Do not press final purchase/submit/confirm. Preserve a before/after field diff and exact terms URL.
- **missing:** A semantic checkout parser that distinguishes reversible profile fields from final commit controls; A local-only budget/calendar adapter with a narrow, date-and-amount query interface; A cross-surface conflict report rendered both as a Mac review card and a short pendant response

### "“Walk me through this complicated private web form one question at a time, fill my answers into Safari, validate the completed fields, and stop before submission.”"
- **useful because:** The owner can complete unfamiliar insurance, government, school, or support forms hands-free without exposing the whole page or losing track of required fields. The pendant handles one-question-at-a-time interaction while Safari retains the authenticated session and the Mac keeps a reviewable field ledger.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Realtime for short field questions and corrections; a cheaper background model parses the form schema, detects required/conditional fields, and validates formats.
- **latency:** Ask the next field within 1 second after each answer; parse a typical form within 10 seconds; never submit automatically.
- **cost:** Approximately $0.03–$0.15 per form, dominated by conversational turns and conditional-form parsing.
- **security:** Form answers may include health, identity, or financial data. Keep sensitive values out of long-lived logs, mask them in receipts, bind every write to a specific field and tab, and show a final complete diff before any submit action.
- **missing:** A form-schema extractor that models required, conditional, repeated, and validation-constrained fields; A pendant conversational slot-filling intent with local redaction of sensitive answers; A browser field ledger that records field locator, value status, and validation result without storing raw secrets

### "“Collect the personal data exports that my logged-in services already offer, save them locally in a labeled archive, and tell me which exports are still pending—never publish or delete anything.”"
- **useful because:** The browser can reach export controls and status pages that the Mac alone cannot access. The relay can continue checking asynchronous export readiness, the Mac can download and organize the files, and the pendant can report completion without the owner repeatedly revisiting every account.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant
- **model tier:** Cheap background model for export-page navigation, status polling, file labeling, and manifest generation; realtime only for owner questions or a completion announcement.
- **latency:** Start an export workflow within 20 seconds; monitor asynchronously for days; announce each ready archive promptly.
- **cost:** Roughly $0.05–$0.40 per service, mostly browser interaction and later archive indexing; storage cost depends on export size.
- **security:** Exports may contain an entire personal history, credentials, or private messages. Download only to an encrypted local directory, never send archive contents to the model, use a manifest of filenames/hashes rather than raw data, and stop before destructive account actions. Require explicit confirmation before sharing or deleting an archive.
- **missing:** A browser workflow that recognizes and initiates non-destructive data-export requests across different sites; A durable relay watch keyed to export request IDs and authenticated tabs; An encrypted local archive manager that indexes metadata without ingesting export contents

### "“Translate this private webpage live into my preferred language, preserve the important names, dates, and amounts, and let me ask questions about the translated text without changing the page.”"
- **useful because:** The owner can understand authenticated medical, school, travel, legal, or work pages that are not available through public translation services. Safari supplies the private content, the relay provides low-latency translation, and the pendant makes it usable while away from the screen; structured values remain auditable against the original.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** Realtime model for short visible sections and spoken follow-ups; background model for long-page translation with terminology memory and a side-by-side Mac artifact.
- **latency:** Begin translating the visible section within 3 seconds; stream subsequent sections while the owner listens; answer a grounded follow-up within 2 seconds.
- **cost:** Approximately $0.02–$0.20 per page depending on language and length; translation tokens dominate.
- **security:** Private page text leaves Safari and may include health, financial, or employment information. Send only visible/requested sections, redact credentials and hidden fields, retain original-language citations, and never trigger page actions from translation commands.
- **missing:** A streaming page-section extractor with stable source anchors; A terminology-aware translation session bound to one authenticated tab; Pendant controls for language selection, pause, repeat, and original-versus-translation citation


## What it asked for

_Nothing._
