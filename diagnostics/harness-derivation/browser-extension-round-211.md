# Harness derivation — browser-extension — round 211

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-live-state** — Safari extension is online with 3 tabs; POST /execute successfully listed tabs and read the active Wikipedia page. Browser execution is usable now despite ambiguous wrapper tools.
  - evidence: POST /execute browser_list_tabs returned tabCount=3; POST /execute browser_read_page tabId=3835178 returned Hercules Mulligan page text.

## Capabilities it proposed

### "When I press the pendant button and ask “what am I looking at?”, read the visible authenticated Safari page (or my current selection), explain it in three sentences, and let me ask a follow-up about the same section."
- **useful because:** This is the browser tier’s unique superpower: it can see the page behind an existing login while the pendant is the only interface the owner has while away from the keyboard. A stable page anchor and short-lived provenance make follow-ups useful without storing page text.
- **path:** pendant → browser → relay → mac-planner
- **model tier:** Realtime for the spoken summary and one follow-up; background is unnecessary.
- **latency:** 2–5 seconds for capture/extraction and first spoken answer; under 2 seconds for a follow-up while the page anchor is warm.
- **cost:** About $0.01–$0.05 per interaction, dominated by realtime summarization; browser extraction and relay calls are negligible.
- **security:** The active tab may contain sensitive data. Send only the visible/selected text and origin to the model, never screenshots or full HTML; retain only the existing 24-hour, <=200-character browser claims with URL provenance. Ship with an empty per-origin policy and let the owner configure read/extract/redact/never-store and spoken categories. Never act on the page in this mode.
- **missing:** A resolved callable browser action wrapper for browser_read_page/browser_snapshot (POST /execute already works today but the discovered wrapper is ambiguous); Pendant query trigger and a page-section anchor that survives one or two follow-ups; A relay route to join the browser evidence capsule to the realtime turn

### "Compare the two authenticated pages I name—such as a booking and its airline policy—and tell me exactly where they disagree, with the source sentence and timestamp for each side; then draft (but do not send) the support message and open it in a reviewable browser form."
- **useful because:** Single-page summaries miss contradictions. The browser can access both logged-in sessions, while the relay can reason over a small, cited evidence set and the Mac can stage the resulting message. The owner gets an actionable discrepancy report rather than manually hunting through tabs.
- **path:** browser → relay → mac-planner → pendant
- **model tier:** Background/standard model for extraction and comparison; realtime only for the final spoken discrepancy and follow-up.
- **latency:** 10–20 seconds for two-page capture and comparison; draft staging may take another 3–5 seconds.
- **cost:** Roughly $0.03–$0.12 per comparison, dominated by two-page extraction and reasoning; no cost for local tab operations.
- **security:** Cross-origin data is combined, so default to selected/visible text and an explicit origin list that ships empty. Redact account numbers, addresses, and payment details before model submission. Store only short claims and evidence URLs under existing browser TTL; do not persist page bodies or the drafted message unless the owner saves it. Stop before any send/submit and show the exact draft.
- **missing:** A first-class multi-tab browser capture returning bounded, labeled excerpts and timestamps; Cross-origin redaction/configuration UI (empty by default); A Mac action that opens a draft in the right authenticated support form without submitting it

### "Keep a private watch on an authenticated page I explicitly add, compare each revision with my Mac calendar and reminders, and alert my pendant only when a change creates a real conflict—then give me a one-tap spoken choice to create, move, or dismiss the reminder."
- **useful because:** This turns a constantly changing logged-in page into useful action instead of noisy notifications: a changed appointment, delivery window, or reservation is compared with commitments already on the Mac. The always-awake relay detects changes, the browser supplies authenticated truth, and the pendant delivers the exception without requiring a screen.
- **path:** browser → relay → mac-planner → pendant
- **model tier:** Cheap background model for polling, diffing, and calendar conflict classification; realtime only when the pendant speaks the alert and handles the owner’s choice.
- **latency:** Polling cadence can be 5–15 minutes; after a change, 3–8 seconds to compare and alert. Reminder mutation should complete within 5 seconds after a spoken choice.
- **cost:** Approximately $0.01–$0.08 per changed page, mostly background extraction/classification; unchanged polls should be near-zero model cost via hashes and DOM fingerprints.
- **security:** Never enable monitoring implicitly. Store an explicit per-origin watch with selector/section, schedule, and retention mode; default to no page persistence beyond short claims, 24-hour TTL and 200-character cap. Do not speak values classified as payment, health, or credentials unless the owner’s configuration permits it. Alert payloads must omit page text and include only the minimal delta.
- **missing:** A durable authenticated page-watch scheduler with DOM/content fingerprints and backoff; A calendar/reminder conflict join that can cite both the browser revision and Mac event; Pendant alert payload support for a bounded choice set (create, move, dismiss), beyond the existing read-next alert inbox; An owner-facing empty per-origin watch configuration

### "On the authenticated page I’m viewing, tell me what consequential things I can do—cancel, change, return, download, dispute, or renew—what each will cost or affect, and which prerequisites are missing. Then stage the safest path without taking the final irreversible step."
- **useful because:** Today the owner must understand a site’s scattered controls, policy links, and hidden prerequisites before deciding what to do. This would turn an unfamiliar logged-in portal into an explainable decision surface: the browser discovers the available operations, the model compares their consequences, the Mac stages the path, and the pendant gives the owner a concise choice.
- **path:** browser → relay → mac-planner → pendant
- **model tier:** Standard/background reasoning for extracting and ranking available operations; realtime only for the owner’s spoken question and the final choice.
- **latency:** 8–20 seconds for an authenticated page and linked policy sections; staging should take under 5 seconds after the owner chooses a path.
- **cost:** Approximately $0.04–$0.15 per investigation, dominated by bounded extraction from the page and relevant linked policies.
- **security:** This is decision support over sensitive authenticated content. Use an explicit, initially empty per-origin configuration and submit only bounded relevant excerpts. Redact account identifiers and payment details; retain operation summaries and source URLs only under the existing short browser TTL. Never claim an operation is reversible unless the page explicitly supports it, and stop before submitting cancellation, purchase, dispute, or renewal.
- **missing:** A browser semantic-action inventory that identifies controls, linked policy text, prerequisites, and irreversible effects across a page flow; A consequence model that distinguishes reversible staging from irreversible submission using evidence rather than hard-coded button names; A cross-page browser session plan that can follow only relevant policy links and return a cited operation graph; Pendant output for presenting a small ranked choice set and receiving a selected operation

### "Translate this authenticated foreign-language page into plain English while preserving the meaning of every date, amount, warning, and form field; let me answer in English and stage the correctly translated reply in the original form without submitting it."
- **useful because:** Translation tools usually flatten a page into prose and lose the semantics that matter most in a logged-in workflow—local dates, currencies, required fields, warnings, and legally meaningful wording. This would let the owner actually complete foreign-language portals through the browser while keeping the original values visible for verification.
- **path:** browser → relay → mac-planner → pendant
- **model tier:** Standard model for translation and field alignment; realtime only for short spoken clarification and confirmation of the staged values.
- **latency:** 5–12 seconds for a page section and form mapping; under 4 seconds for each follow-up field.
- **cost:** Approximately $0.03–$0.10 per page/form, mostly translation context; local browser operations are negligible.
- **security:** Authenticated forms can contain identity, health, financial, or legal information. Default to selected fields and visible sections, redact identifiers, preserve original text beside translations, and never persist the full page or translated form. Do not submit; show the exact original-language payload and its English back-translation first.
- **missing:** A field-preserving translation representation that keeps locale, currency, date, validation, and warning metadata; A browser form mapper that can place translated answers into the correct original-language controls and validate them locally; A side-by-side review artifact delivered to the pendant/Mac before any submit action

### "Before I fill this authenticated form, show me every piece of personal data it requests, which fields are optional or excessive for the stated purpose, and stage the least-disclosing valid answers from my local information—without sending anything."
- **useful because:** Forms routinely request more identity and profile data than their stated purpose requires. The browser can inspect the actual logged-in form and its policy, while the Mac can supply local values only as needed. The owner gets a practical privacy check at the moment of disclosure, not a generic warning after the fact.
- **path:** browser → mac-planner → relay → pendant
- **model tier:** Standard model for field-purpose and policy comparison; realtime only to summarize the requested disclosures and answer the owner’s questions.
- **latency:** 6–15 seconds for form plus relevant privacy text; staging under 5 seconds after the owner selects a disclosure level.
- **cost:** Approximately $0.03–$0.12 per form, dominated by policy extraction and field-purpose reasoning.
- **security:** This necessarily handles highly sensitive personal data. Keep source values on the Mac where possible, send field names and redacted metadata to the model, and expose the exact proposed values on the pendant/Mac before typing. Never infer consent, never submit, and retain only a short audit claim that identifies the origin and fields—not the values.
- **missing:** A form-data inventory that maps each control to purpose, requiredness, validation, and nearby policy language; A local-only minimization planner able to choose among multiple owner-approved values without uploading the value set; A reversible browser fill plan with a field-by-field disclosure receipt and clear undo


## What it asked for

_Nothing._
