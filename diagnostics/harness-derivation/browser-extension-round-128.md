# Harness derivation — browser-extension — round 128

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Safari browser access** — Safari extension is online with 3 tabs; authenticated Gmail tab 901464 is visible to browser_list_tabs, but browser_snapshot and browser_read_page both fail because the extension does not have access to the frame.
  - evidence: POST /execute browser_list_tabs succeeded at 2026-08-07T17:59:19Z; prior browser_snapshot/read_page results for tab 901464 returned the exact frame-access failure.

## Capabilities it proposed

### "“Read the page I’m looking at and answer my question about it.”"
- **useful because:** This is the fastest path from a private logged-in Safari page to a reliable spoken answer: the browser supplies the page evidence, the Mac can compare it with local notes/files, and the relay returns a concise answer with a source link instead of making the owner dictate or copy anything.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use the cheap extraction/classification model for DOM cleanup and citation selection; reserve realtime for the owner's question and final answer.
- **latency:** 3–6 seconds for a normal page; up to 12 seconds for a multi-tab question.
- **cost:** Roughly $0.002–$0.02 per question, dominated by sending extracted page text; avoid screenshots and send only relevant DOM regions.
- **security:** Only the active tab and explicitly requested related tabs are read. Authenticated content leaves Safari only as selected snippets; never send cookies, hidden inputs, or full page HTML. Warn when the answer includes financial, health, or account-security data.
- **missing:** A working Gmail/Safari content-script permission path: live snapshot/read currently fails with 'Extension does not have access to this frame' even though tabs are online.; A tab-scoped extraction contract that returns URL, title, selected text, and DOM evidence rather than an opaque failure.; A voice intent that carries the active tabId and a relevance query.

### "“Reconcile this charge or renewal across my logged-in accounts and local receipts, and tell me what I should do.”"
- **useful because:** The owner currently has to search several private sites and Downloads manually. Browser can inspect the authenticated merchant or bank page, Mac can match local receipts and calendar events, and the relay can explain one discrepancy. It can prepare—but never send—a dispute or cancellation draft.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant
- **model tier:** Use a background cheap model for OCR/field normalization and duplicate matching; use realtime only to clarify which transaction the owner means and speak the result.
- **latency:** 8–20 seconds for two to four sources; give a progress acknowledgement after 3 seconds.
- **cost:** About $0.01–$0.08 per reconciliation, dominated by private-page extraction and receipt OCR; cache normalized merchant/date/amount hashes, not raw documents.
- **security:** Financial data is highly sensitive: only inspect tabs the owner names or the active transaction, redact full account numbers and addresses, and keep raw receipts on the Mac. Require explicit confirmation before opening a dispute, cancelling, or contacting a merchant; drafts show exact text and destination.
- **missing:** A cross-source transaction schema with provenance and confidence per amount/date/merchant.; Mac-side receipt indexing that can return candidate local files without uploading them.; A browser field extractor that handles account pages and statement PDFs safely.; An approval-aware draft handoff to the existing browser action executor.

### "“Turn this long private webpage into an interactive audio briefing I can listen to on the pendant—pause, skip, and ask follow-up questions without losing my place.”"
- **useful because:** Reading dense insurance, benefits, documentation, or work pages on a phone is painful. Safari supplies authenticated content, the Mac makes a durable chaptered audio queue, the relay handles follow-up questions, and the pendant provides pause/skip/replay even when the owner's hands and eyes are busy.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → mac-vision
- **model tier:** Use a cheap background model to segment and summarize into chapters and a low-cost TTS path to render audio; realtime handles only interruptions and follow-up questions.
- **latency:** Start playback within 5 seconds with the first chapter; render later chapters in the background. Follow-up answers under 2 seconds if the relevant excerpt is cached.
- **cost:** $0.01–$0.10 per long page depending on TTS duration; cache chapter text/audio by page fingerprint and only regenerate changed chapters.
- **security:** Private page text and generated audio are sensitive. Keep the source and queue encrypted on the Mac/relay with short retention, omit passwords/forms/hidden text, and show the source URL and excerpt when answering. Never activate links or submit forms from audio commands without an explicit separate request.
- **missing:** A chaptered browser extraction result with stable source offsets and semantic headings.; A durable audio queue with playback position synchronized between pendant and Mac.; Pendant controls/events for pause, next chapter, replay excerpt, and 'ask about this'.; A page fingerprint-to-audio cache and invalidation policy.

### "“Before I commit to this online, check it against my calendar, email, and notes, and tell me what it would conflict with.”"
- **useful because:** The owner often encounters deadlines, appointments, renewal terms, or invitations inside authenticated websites before agreeing to them. The browser can read the proposed date/obligation, the Mac can inspect local calendar and notes, and the relay can explain conflicts through the pendant before the owner clicks submit or accepts.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant
- **model tier:** Use a background model to normalize dates, obligations, and entities; use realtime only for the owner's spoken question and a short conflict explanation.
- **latency:** 5 seconds for a single proposed date; up to 15 seconds when comparing several private sources.
- **cost:** Approximately $0.01–$0.06 per check, dominated by extracting relevant private snippets; send only the proposed terms and matching evidence, not whole inboxes or notes.
- **security:** Read only the active page plus narrowly relevant calendar/email/note entries. Redact unrelated message content and account identifiers. Never accept, submit, RSVP, or send a reply automatically; present the exact conflicting commitments and require a separate owner decision.
- **missing:** A browser semantic extractor for proposed obligations, dates, deadlines, and cancellation terms.; A local commitment index spanning calendar, mail, notes, and reminders with provenance and time zones.; A conflict model that distinguishes hard conflicts from soft preferences and explains uncertainty.; A browser handoff that pauses at the final acceptance control while preserving the filled state.

### "“Check whether my personal details are consistent across the accounts I’m logged into, and show me anything stale before I use it.”"
- **useful because:** Old addresses, phone numbers, names, and billing details cause failed deliveries, lost account recovery, and embarrassing form errors. Safari can inspect the owner-selected account pages, the Mac can compare the canonical profile in local contacts/notes, and the pendant can report a short discrepancy list without changing anything.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant
- **model tier:** Use a low-cost extraction and field-normalization model; realtime is only for clarifying which account or field the owner means and speaking the result.
- **latency:** 10–30 seconds for three to six selected accounts; stream findings as each account completes.
- **cost:** About $0.02–$0.10 per sweep, mostly private-page extraction. Cache field fingerprints and never retain full profile pages.
- **security:** Identity and recovery data is sensitive. Require explicit account selection, redact full phone numbers and addresses in spoken output, never inspect password/MFA fields, and make all edits a separate owner-approved action with before/after evidence.
- **missing:** A canonical owner-profile record with field-level sensitivity and preferred values.; A browser extractor that recognizes profile and billing fields without reading secrets.; Cross-account normalization for names, addresses, phone numbers, and time zones.; A discrepancy report that links each value to its exact account page and timestamp.

### "“Audit the security settings of the private sites I choose and tell me the three highest-risk fixes, without changing anything.”"
- **useful because:** The owner cannot easily tell whether recovery email, active sessions, forwarding rules, app access, or public profile visibility drifted on each site. The browser reaches settings behind existing logins, the Mac keeps a private evidence report, and the pendant gives only the prioritized risks rather than a noisy checklist.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a cheap background model for settings extraction and risk scoring against a versioned ruleset; use realtime only to explain a risk or answer a follow-up.
- **latency:** 20–60 seconds for three selected sites, with incremental results after each site.
- **cost:** Approximately $0.03–$0.15 per audit, depending on screenshots/PDF settings pages; prefer structured visible fields and retain only hashes plus cited snippets.
- **security:** The audit itself accesses security-sensitive pages. Limit to explicitly selected sites, never read passwords or one-time codes, do not alter settings, and avoid speaking recovery addresses or session identifiers aloud. Any remediation must be a separate, explicit action.
- **missing:** A site-agnostic security-settings vocabulary covering sessions, recovery, forwarding, OAuth/app access, visibility, and alerts.; A browser recipe library for common account settings pages and safe secret-field suppression.; A ruleset with severity, rationale, and remediation links that can be updated independently of the model.; A durable private report that records evidence without retaining full settings pages.


## Changes it proposed to its own stack

### `browser-harness` — Add a Safari-extension diagnostics and recovery path for frames that reject content-script execution: on a failed browser_read_page/browser_snapshot, return the tab's frame tree and permission state, retry the top document after activating the tab, and expose an explicit Safari host-permission repair action (open the extension's Website Access settings and verify the origin). Persist the failure reason and origin in the browser inspection record so the planner can stop retrying blindly.
- **owner gets:** Private pages such as the owner's Gmail become readable instead of silently failing with 'Extension does not have access to this frame'; the owner gets a clear one-time repair path rather than repeated useless browser attempts.
- effort: Medium: extension permission/active-tab handling, bridge typed error, and a small diagnostics UI or guided Mac action.  ·  risk: Activating a tab can change the visible Safari window; never navigate or submit. If permission repair is unavailable, fall back to showing the exact origin and instructions. Recover by retrying only after a fresh heartbeat and permission check.
- cost: No meaningful API cost; one small diagnostic payload per failure.  ·  latency: Adds under 1 second to failures; successful reads unchanged.
- security: Improves security observability without broadening access automatically; host permissions remain explicit and origin-scoped.
- depends on: Safari extension content-script permission configuration; browserBridge typed failure payloads; POST /execute browser action receipts

### `browser-harness` — When Safari content scripts cannot access a private frame, add an accessibility-tree extraction fallback through the extension's native tab API, returning visible roles, labels, values, and links with tabId/URL provenance. Exclude password fields and offscreen/hidden nodes, and mark results as accessibility-derived so planners do not confuse them with DOM text.
- **owner gets:** Gmail and other logged-in pages remain usable even when Safari's frame isolation blocks DOM injection; the owner can ask about visible inbox content instead of hearing a generic failure.
- effort: High: extension native messaging/API work plus typed bridge result and tests across Gmail, PDFs, and cross-origin frames.  ·  risk: Accessibility trees may omit details or expose more visible text than intended. Limit to the active tab and visible nodes, redact secrets, and return a confidence/coverage warning. Recovery is automatic DOM retry when permissions later become available.
- cost: Negligible API cost; modest extension CPU and result payload size.  ·  latency: Adds 1–3 seconds only on DOM-access failures.
- security: No cookie or network access; still requires explicit extension Website Access. Sensitive visible text is handled under the same browser-read policy and should have short retention.
- depends on: Safari extension native accessibility integration; browserBridge typed fallback results; browser inspection records


## What it asked for

_Nothing._
