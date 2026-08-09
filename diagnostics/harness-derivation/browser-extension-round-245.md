# Harness derivation — browser-extension — round 245

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Pull the due date and amount from this logged-in page and put a reminder on my Mac, with a link back to the exact page.”"
- **useful because:** It closes the loop between a private browser page and an action the owner can actually use. Today the browser can read but cannot safely hand a grounded fact into Mac reminders as one coherent job. The owner gets a reminder created from evidence rather than manually transcribing a bill, renewal, appointment, or application deadline.
- **path:** browser → mac-planner → relay → pendant
- **model tier:** Background model extracts a small typed fact set (amount, date, title, URL, confidence); realtime only confirms the spoken request and reports completion. Use a cheaper deterministic date/amount parser before invoking a model.
- **latency:** Read and extraction in 5–10 seconds; reminder creation in another 1–3 seconds. Stop if date or amount is ambiguous and speak the competing candidates.
- **cost:** About $0.005–$0.04 per invocation; browser extraction and Mac action are the dominant work, not generation.
- **security:** Only pass extracted fields and provenance, not the page body. The reminder text must not include secrets or account numbers. Keep the source URL and claim evidence capsule under the existing short-lived browser-finding rules; reminder creation is reversible and must produce a job receipt/undo handle.
- **missing:** A typed browser-finding-to-Mac-action handoff carrying claim, confidence, URL, and evidence capsule; A date/amount ambiguity response that returns choices to the pendant instead of guessing; A reminder receipt that embeds provenance and can undo both the reminder and the browser finding

### "“Fill this logged-in web form from the details in my Mac, then read me every field and leave it ready for me to submit.”"
- **useful because:** Form entry is where browser access saves real time, yet the dangerous part is silent transcription into a private site. This capability combines Safari's session with local facts, performs the reversible fill, and gives the owner a precise spoken audit while deliberately stopping before submit. It is useful for applications, checkout drafts, insurance forms, and scheduling pages.
- **path:** browser → mac-planner → pendant → relay
- **model tier:** Use a cheaper extraction/field-matching model for labels and values; realtime only narrates the compact field diff. Use the expensive tier only for conflicting candidate values or unfamiliar form structure.
- **latency:** Inspect and map fields in 5–12 seconds; fill in under 5 seconds; spoken audit starts immediately after the browser result. Never wait on a model while a high-impact submit action is queued.
- **cost:** Roughly $0.01–$0.06 per form, dominated by page snapshots and field mapping; no model call is needed for deterministic local fields.
- **security:** Values come from local Mac sources and may include sensitive identity data. Keep them in memory for the job, redact them from ordinary logs, and store only field names, hashes, origin, and undo metadata. The browser action allow-set should be fill-only; submit, send, purchase, and upload must be impossible in this mode. Provide a complete before/after field diff on the pendant and Mac.
- **missing:** A browser fill transaction with an explicit fill-only action set and rollback of all modified fields; A local-source selector that lets the owner choose which Mac facts may populate each field without inventing site-specific rules; A compact spoken field-diff renderer and a browser job receipt containing an undo token

### "“Use the reservation page I’m viewing to prepare me for leaving: put the appointment on my calendar, check the travel time on my iPhone, and tell me when I need to go.”"
- **useful because:** This joins three otherwise disconnected realities: the authenticated reservation contains the authoritative time and address, the Mac can create the local event, and iPhone control can estimate the real departure time. The pendant then gives one concise reminder instead of making the owner transcribe a booking and separately plan travel.
- **path:** browser → mac-planner → ios → relay → pendant
- **model tier:** Background model extracts the reservation fields and resolves timezone/address; deterministic calendar and travel calculations do the rest. Realtime is only for the spoken confirmation or an ambiguity question.
- **latency:** Extract in 5–10 seconds, create the calendar event in 1–3 seconds, and obtain a travel estimate in under 15 seconds. If location permission or route data is unavailable, create the event but explicitly omit the departure estimate.
- **cost:** About $0.01–$0.08 per invocation; browser extraction and route lookup dominate. Repeated reminders reuse the event metadata rather than re-reading the page.
- **security:** Reservation codes, addresses, and travel history are sensitive: pass only the event fields to the Mac/iPhone tiers, redact confirmation numbers from spoken output, and store source provenance under the browser 24-hour TTL. Require the owner to name the destination tab or explicitly invoke the page context; never scrape all open tabs. Calendar creation should return an undoable receipt.
- **missing:** A browser-to-calendar typed reservation schema with timezone and confidence; An iOS travel-time action exposed through the Mac iPhone-Mirroring facet; A single job coordinator that waits for browser, calendar, and route results and handles partial completion cleanly

### "“Build me a support-case packet from this private order page and the relevant emails/files on my Mac, then draft the exact message and leave it unsent.”"
- **useful because:** When something goes wrong with a purchase, reservation, or account, the evidence is split between an authenticated webpage and local mail/files. Today no single node can assemble a grounded chronology, identify the missing proof, and prepare a useful support request. The owner gets a complete, reviewable packet instead of hunting through tabs and attachments.
- **path:** browser → mac-planner → relay → pendant
- **model tier:** Use a background model to extract a structured chronology and deduplicate evidence; use realtime only to answer the owner's questions and read the short draft aloud. Use the expensive tier only for contradictory dates or policy language.
- **latency:** Collect and index the selected page plus named local sources in 15–30 seconds; produce a draft in under 45 seconds. Never send, upload, or submit anything automatically.
- **cost:** Approximately $0.05–$0.30 per packet, dominated by document extraction and attachment OCR; later edits should reuse the local evidence index.
- **security:** This may contain names, addresses, order IDs, and correspondence. The owner must explicitly select the browser tab and local folder/mail thread; do not search the whole mailbox or all tabs. Store a manifest of source hashes, URLs, and filenames rather than copied page bodies; redact payment credentials and unrelated recipients. The generated message must clearly show recipients, attachments, and claims before any future send action.
- **missing:** A cross-surface evidence collector that accepts an explicit Safari tab plus explicit Mac files/mail threads; A provenance-preserving chronology and contradiction detector that can cite each claim back to its source; A draft-message and attachment staging object with reversible cleanup, separate from any send/upload action; A pendant-friendly review protocol that summarizes the packet and lets the owner request a specific citation or correction

### "“Audit the privacy and security settings in this logged-in account, explain what changed since last time, and prepare recommendations without changing anything.”"
- **useful because:** Account settings are private, fragmented, and often impossible to evaluate from public documentation. The browser can inspect the real effective settings, while the Mac can compare a prior claim set and the pendant can explain the few consequential changes. This gives the owner an actionable security review without granting the system permission to alter protections.
- **path:** browser → mac-planner → relay → pendant
- **model tier:** Use a background model for structured setting extraction and diffing; realtime handles only the spoken summary and owner questions. Use the expensive model for ambiguous policy wording or conflicting controls.
- **latency:** Scan a named settings area in 10–20 seconds and report material changes in under 30 seconds. Do not crawl beyond the explicitly selected account area.
- **cost:** About $0.03–$0.15 per audit, driven by several page reads and policy-text comparison; incremental audits are cheap if only changed claims are retained.
- **security:** Security settings themselves are sensitive. Persist only normalized setting names, values, host, timestamp, and provenance—not screenshots, tokens, recovery codes, or page bodies. Never click save, enable, disable, revoke, or rotate. The owner must explicitly invoke the audit on the current account and receive a clear scope statement.
- **missing:** A typed security-setting schema with impact labels and effective-vs-inherited state; A host-scoped historical diff store for short normalized claims, with expiration and deletion; A browser read-only scope that can traverse settings navigation but cannot mutate controls; A spoken prioritization rubric that distinguishes urgent exposure from harmless presentation changes

### "“For this private account, tell me what data it holds, what I would lose by closing it, and prepare an export or closure request without submitting it.”"
- **useful because:** Public help pages cannot reveal the account's actual stored profile, subscriptions, credits, active sessions, or deletion consequences. The browser extension can inspect the authenticated account while the Mac organizes a private checklist and the pendant gives a plain-language decision brief. It helps the owner leave services deliberately instead of discovering irreversible losses afterward.
- **path:** browser → mac-planner → relay → pendant
- **model tier:** Background model extracts account-specific assets, dependencies, and export options; deterministic checklists handle counts and dates. Realtime is reserved for the owner's decision questions, not the full page scrape.
- **latency:** Produce an inventory in 20–40 seconds across the explicitly selected account pages. Preparing a draft export/deletion request may take another 5 seconds, but no destructive control is ever activated.
- **cost:** Roughly $0.05–$0.25 per account, depending on the number of settings and export pages; retain only compact claims so follow-up questions are inexpensive.
- **security:** Never download or persist the account's full data export by default. Do not expose recovery codes, payment details, private messages, or session tokens in speech. Require explicit owner selection of the account and a visible list of planned fields/actions. Export, close, revoke, and submit controls must remain outside the read-and-prepare action set.
- **missing:** An account-asset inventory schema covering subscriptions, credits, stored content, integrations, sessions, and deletion dependencies; A browser workflow that discovers export/closure prerequisites without activating them; A local decision brief with citations and a reversible draft request object; A retention/deletion control allowing the owner to purge the extracted account inventory immediately


## Changes it proposed to its own stack

### `browser-harness` — Add a live, privacy-minimal browser context channel: Safari heartbeat reports the owner-selected tab's title, origin, tab ID, and whether text is selected, plus an explicit “owner invoked context” event from the pendant. It must report metadata only until that invocation, then issue one scoped browser_read_page/snapshot job and expire the context after the answer.
- **owner gets:** The owner can say “this” while looking at a private page and get help without naming a URL, copying text, or accidentally having the system inspect unrelated tabs. It makes the pendant feel present in the browser rather than forcing a separate navigation command.
- effort: Medium: extension heartbeat/context payload, relay correlation to the pendant utterance, and a one-shot scoped read job with expiry.  ·  risk: A stale active-tab ID could read the wrong page; show the origin/title in the spoken or Mac confirmation and reject a context older than a few seconds. If the extension disconnects, fall back to asking the owner to name the page.
- cost: Negligible API cost for metadata; one normal browser read per explicit invocation. No new hardware cost.  ·  latency: Removes a navigation/list-tabs round trip; answer should be 1–3 seconds faster.
- security: Improves privacy by making content reads explicit and one-shot, but tab title/origin metadata still leaves the device. Never persist metadata beyond the short session and honor the existing empty per-origin configuration.
- depends on: A functioning extension heartbeat payload beyond tabCount/tabUrl; POST /pipeline/events carrying the pendant invocation ID; POST /execute browser_read_page/browser_snapshot scoped to the reported tab ID; Existing browser provenance and short-lived browser-memory policy


## What it asked for

_Nothing._
