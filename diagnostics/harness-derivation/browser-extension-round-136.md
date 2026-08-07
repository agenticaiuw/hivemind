# Harness derivation — browser-extension — round 136

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What am I looking at? Read me the important parts of this private page, explain any jargon, and let me ask follow-up questions without leaving Safari.”"
- **useful because:** This is the browser's unique value in a wearable: the owner can be walking or hands-busy, while Safari supplies authenticated page text and the pendant supplies the conversational interface. It should preserve headings, links, warnings, and quoted evidence, skip navigation/ads, and answer follow-ups against the same page snapshot rather than repeatedly re-reading the whole site.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** Realtime for the short spoken explanation and follow-ups; a cheaper background extraction pass can identify semantic sections and citations before the first answer.
- **latency:** First spoken summary within 5 seconds; follow-up answers within 2 seconds while the page snapshot remains live.
- **cost:** About $0.01–$0.05 per page session, dominated by one extraction/context pass and realtime follow-ups; page text stays in the authenticated bridge-to-relay path.
- **security:** Private page text and screenshots must never enter public web search or durable logs by default. Show URL/title and source snippets in the response, expire the snapshot after the session, and redact obvious secrets/payment fields.
- **missing:** A live browser command enqueue implementation (the currently granted enqueue schemas are still stubs); A page-snapshot session with semantic section extraction, citation offsets, and follow-up turn affinity; A relay voice intent that binds questions to the active Safari tab and expires cleanly

### "“Turn this private booking or event page into a reminder: extract the exact date, time zone, location, confirmation number, and cancellation deadline, check my calendar for conflicts, then create the reminder with a link back to the page.”"
- **useful because:** Booking sites hide critical details in authenticated pages and often change them. The owner should not retype a flight, appointment, reservation, or filing deadline while wearing the pendant. This combines browser-only facts with Mac calendar/reminders and catches time-zone conflicts before they become missed appointments.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background/cheap model for structured extraction and conflict comparison; realtime only to summarize ambiguity and ask the owner to resolve a missing or conflicting field.
- **latency:** Extract in under 8 seconds, then create the reversible reminder in under 3 seconds after the owner says yes.
- **cost:** Roughly $0.01–$0.04 per booking, mostly extraction; Mac calendar/reminder actions add no model cost.
- **security:** Confirmation numbers and itinerary details are sensitive. Keep them local or encrypted, pass only the extracted fields needed for conflict checking, and do not retain page screenshots. Creating a reminder is reversible; never book, cancel, or modify the reservation.
- **missing:** Schema for normalized event/appointment facts with explicit source URL and time-zone confidence; A browser-to-Mac handoff that carries extracted fields and source citation rather than raw page HTML; A spoken disambiguation turn for date/time-zone conflicts

### "“Before I type anything into this page, check whether it is really the site I intended: inspect the URL, redirect chain, page identity, and suspicious payment or login cues, then tell me what is safe to do and what is not.”"
- **useful because:** Phishing protection is a browser-only superpower that becomes practical through a pendant: the owner can ask while a link is open, before credentials or card data leave the device. It should distinguish a genuine warning from a hard block, explain the evidence in plain language, and optionally offer to navigate to the known-good domain without touching the form.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** Cheap background classifier for URL/domain and page markers; realtime model only for the owner's spoken question and concise explanation. Never send page contents to public search unless explicitly requested.
- **latency:** Risk verdict in 2–4 seconds from URL plus a bounded DOM/screenshot sample; safe-domain navigation in under 3 seconds.
- **cost:** About $0.002–$0.02 per check, dominated by screenshot/DOM extraction; domain reputation can use a cached local list.
- **security:** The detector itself must not upload credentials, typed fields, cookies, or full private pages. Treat the result as advice, not a guarantee; show concrete reasons (lookalike domain, unexpected redirect, mixed-origin form, newly seen host). Navigation is reversible, but do not clear sessions or submit anything automatically.
- **missing:** A local, privacy-preserving URL/redirect and form-origin inspection result from the Safari extension; A maintained reputation/lookalike-domain feed or on-device ruleset; A typed browser security-verdict event that the pendant can speak and the Mac can optionally display

### "“Make this private webpage usable for me: turn its dense tables, charts, and tiny controls into a spoken, navigable outline; tell me the values and trends, and let me jump Safari to the exact row or control I name.”"
- **useful because:** Authenticated dashboards and portals are often visually dense or inaccessible from a pendant. This gives the owner a hands-free semantic map rather than a generic page summary: chart trends become numbers and caveats, tables become row/column navigation, and every spoken claim can jump back to its source in Safari.
- **path:** browser-extension → relay-realtime → pendant → mac-vision
- **model tier:** Background model for DOM/accessibility-tree and chart/table normalization; realtime model for navigation commands and short spoken answers. Use vision only when the data exists solely in pixels.
- **latency:** Outline within 6 seconds; each row/control jump within 2 seconds.
- **cost:** $0.01–$0.08 per complex page, with vision calls dominating only for canvas-rendered charts; ordinary DOM tables are cheap.
- **security:** Keep raw authenticated DOM and screenshots transient; redact inputs and unrelated regions; do not click controls that mutate state. Chart extraction must state uncertainty and cite the source region.
- **missing:** A browser extraction result type for accessibility trees, tables, chart series, and stable DOM locators; A tab-scoped 'jump to source' browser action that scrolls/highlights without clicking; A voice navigation state machine for next row, previous column, and explain trend

### "“Audit my logged-in accounts for stale or contradictory personal details—address, phone, emergency contact, subscription status, and notification settings—and give me one sourced correction list without changing anything.”"
- **useful because:** People accumulate dangerous inconsistencies across insurers, banks, healthcare portals, employers, travel accounts, and subscriptions. No single browser tab can detect that the same fact is stale elsewhere. Safari can inspect the owner’s private sessions, the relay can reconcile identities and dates, the Mac can produce an editable correction worksheet, and the pendant can report only the discrepancies worth fixing.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** Background model for cross-account field normalization and contradiction detection; realtime only for explaining a discrepancy or answering the owner’s follow-up. Do not use the expensive tier for the full audit.
- **latency:** A 5–10 account audit can run in the background within several minutes; the owner gets a concise discrepancy summary as each account is completed.
- **cost:** Approximately $0.05–$0.30 per audit, dominated by authenticated page extraction and normalization; substantially cheaper than repeatedly asking the realtime model.
- **security:** This is unusually sensitive cross-account correlation. Keep raw values on the Mac, send the relay only typed discrepancy records and masked values, isolate each browser session, and retain an audit trail showing source URL, timestamp, and confidence. Never edit fields automatically; correction is a separate owner-directed task.
- **missing:** A cross-account fact schema with field-level sensitivity, provenance, freshness, and conflict semantics; A browser session orchestrator that can inspect a named set of authenticated services while preserving per-site isolation; A local encrypted correction worksheet and a spoken discrepancy-review flow

### "“When a logged-in service asks me to accept updated terms or a privacy policy, compare it with the last version I accepted, explain only the material changes that affect me, and prepare a list of settings I may want to change.”"
- **useful because:** Terms changes are consequential but nearly impossible to review on a phone or while distracted. The browser is the only node that can see the private, account-specific prompt; the Mac can retain prior versions and compute a diff; the pendant can explain the practical impact before the owner accepts.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Cheap background model for document normalization and clause diffing; realtime model for the owner’s questions about a specific changed clause.
- **latency:** A first material-change summary within 10 seconds of opening the policy; clause explanations within 3 seconds.
- **cost:** $0.02–$0.10 per policy comparison, primarily document extraction and one structured diff; unchanged boilerplate should be cached.
- **security:** Policy documents may contain account identifiers and should remain encrypted on the Mac. Preserve both versions with URL and timestamp, but do not retain unrelated page content. This informs the owner and must never click Accept or change settings.
- **missing:** Versioned, encrypted policy storage keyed to a site/account without storing credentials; A document normalizer that handles HTML, PDF, and expandable policy sections; A materiality rubric that distinguishes legal boilerplate from changes to sharing, fees, cancellation, or arbitration

### "“Collect the data-export and account-download options from my logged-in services, tell me what each export contains and how long it takes, and prepare a private export checklist I can run service by service.”"
- **useful because:** Personal data is scattered across services and export controls are deliberately buried. The browser can reach the owner’s authenticated settings pages; the Mac can organize a local inventory and deadlines; the pendant can make the process navigable without exposing raw archives to the model. This gives the owner practical control of their data without automatically requesting or downloading sensitive archives.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background model for locating and classifying export controls and documenting scope/retention; realtime only for answering “what will this export include?”
- **latency:** Inventory one service in under 15 seconds; build a multi-service checklist asynchronously and notify the owner when ready.
- **cost:** $0.02–$0.15 per service, dominated by authenticated navigation and document extraction; local checklist generation is negligible.
- **security:** Never download archives or transmit their contents by default. Store only export metadata, scope, estimated completion time, and source URL locally. Treat any click that requests an export as an owner-directed action and show the exact request first.
- **missing:** A per-service export metadata schema and local encrypted checklist store; Browser navigation that can traverse account settings while preserving the original tab and session; A Mac-side scheduler for export completion dates and a way to mark each request complete


## What it asked for

_Nothing._
