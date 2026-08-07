# Harness derivation — browser-extension — round 126

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“When I say ‘what changed in the browser?’, compare the pages I currently have open with their last seen state, tell me only meaningful changes through the pendant, and let me pin a change for follow-up.”"
- **useful because:** This turns an already-open authenticated Safari session into an on-demand situational report: the browser supplies private page state, the relay normalizes diffs, and the pendant makes the result available without returning to the desk. Unlike a scheduled page watch, it reports the owner's live working set and can preserve a specific evidence item for later.
- **path:** browser-extension → mac-planner → relay-realtime → relay-realtime
- **model tier:** background for DOM normalization and diff scoring; realtime only to answer the spoken request and read the short result
- **latency:** Under 8 seconds for up to 5 open tabs; extraction dominates, with a 30-second fallback for slow pages.
- **cost:** About $0.01–$0.05 per request depending on page text; browser extraction and hashing dominate, not model tokens.
- **security:** Private authenticated page text leaves Safari only to the local Mac agent and relay for summarization; never include full page bodies in pendant audio. Store only selected excerpts and URL/title, with a one-click/voice delete. Pinning must be explicit; no page mutation occurs.
- **missing:** A live-tab baseline store keyed by tab identity plus URL and semantic fingerprint; An on-demand browser action that captures all open tabs in one request and returns bounded excerpts; Pendant voice intent for ‘what changed in the browser’ and a compact pinned-evidence queue

### "“Find meeting requests in my logged-in Gmail, check them against my private calendar, and give me three reply options that fit my actual availability; place a tentative hold only after I choose one, but never send the email.”"
- **useful because:** Email and calendar are separate authenticated surfaces, and only the browser can read the owner's live Gmail session. The system would turn an inbox burden into an actionable choice: it can detect date/time requests, check conflicts and travel buffers, speak concise options through the pendant, and make the reversible calendar hold on the Mac while leaving the external commitment unsent.
- **path:** browser-extension → mac-planner → relay-realtime → mac-vision
- **model tier:** background model extracts candidate meeting requests and calendar facts; realtime model is used only for the owner's spoken selection and final concise explanation
- **latency:** 30–60 seconds for Gmail plus calendar extraction; under 3 seconds after the owner chooses an option to create a tentative hold.
- **cost:** Roughly $0.03–$0.12 per invocation; authenticated page extraction and conflict reasoning dominate.
- **security:** Email bodies, invitees, and calendar details are sensitive; process on the Mac where possible and send only bounded structured fields to the relay. Do not send or accept anything. Calendar hold needs an explicit spoken selection but is reversible and receipt-backed.
- **missing:** Semantic extraction of meeting proposals from Gmail DOM including timezone and attendee fields; A calendar availability adapter that includes travel/buffer rules; A cross-surface draft object linking source email, candidate slots, hold receipt, and unsent reply text

### "“Before any subscription renews, open its logged-in account page, verify the exact price and renewal date, tell me on the pendant, and if I say ‘later’ schedule a reminder with the cancellation link; never cancel for me.”"
- **useful because:** Renewal terms are often visible only behind an authenticated account, while reminders belong in the Mac and the alert must reach the worn device. This prevents surprise charges without taking an irreversible action: the system verifies the live billing state, preserves the exact evidence, and creates a user-chosen follow-up.
- **path:** browser-extension → mac-planner → relay-realtime → relay-realtime
- **model tier:** background model extracts billing facts and compares them with the previous snapshot; realtime handles the short spoken alert and reminder choice
- **latency:** Under 20 seconds for one account page; reminder creation is under 2 seconds after the spoken ‘later’.
- **cost:** Approximately $0.01–$0.06 per check; authenticated navigation and page extraction dominate.
- **security:** Billing and account identifiers are sensitive; redact payment details and retain only merchant, amount, date, URL, and a short evidence excerpt. Never click cancellation or purchase controls. Reminder title should avoid exposing sensitive service names on shared notifications.
- **missing:** A renewal-watch registry with user-specified lead time and quiet hours; Authenticated page extraction that identifies renewal amount/date and cancellation URL robustly across sites; A relay-to-Mac reminder action carrying the evidence capsule and source URL

### "“When a site I use changes its terms, privacy policy, or subscription conditions, read the old and new versions from my logged-in browser, explain only what materially affects me, and prepare the exact opt-out or settings steps without submitting anything.”"
- **useful because:** Legal and privacy changes are often buried in authenticated account notices and are not meaningful as a raw diff. The browser can reach the owner’s private notices and account settings, while the relay can compare versions and the pendant can deliver a short practical explanation. This gives the owner a decision-ready consequence summary rather than another unread notification.
- **path:** browser-extension → mac-planner → relay-realtime → relay-realtime
- **model tier:** Background model performs document alignment, clause classification, and impact ranking; realtime is used only when the owner asks follow-up questions or wants the short spoken summary.
- **latency:** Up to 2 minutes for a policy pair and linked settings pages; under 5 seconds for a spoken explanation after analysis is cached.
- **cost:** Approximately $0.05–$0.30 per policy comparison, dominated by long-document extraction and alignment; follow-up answers are much cheaper from the stored structured diff.
- **security:** Policy pages may include account identifiers and sensitive usage terms. Keep raw documents encrypted on the Mac, send the relay only clause excerpts and structured changes, redact identifiers, and expire source copies after 30 days. Preparing settings changes is read-only until the owner separately chooses to execute them.
- **missing:** A policy-document capture and version store that preserves source URL, retrieval time, and exact text hash; Clause-level semantic alignment with materiality categories such as price, data sharing, retention, arbitration, and cancellation; A linked settings-discovery step that maps an impacted clause to reversible, unsent account actions


## Changes it proposed to its own stack

### `browser-harness` — Add a user-visible browser task checkpoint that snapshots the active tab set, extracted field values, scroll/step position, and pending reversible actions after every successful browser command. On Safari reconnect, offer ‘resume the browser task’ from the pendant or Mac, revalidate URL and key page anchors before continuing, and mark any changed field/page as needing re-inspection instead of blindly replaying clicks.
- **owner gets:** A laptop sleep, Safari restart, or brief extension disconnect would no longer erase a half-completed private web task. The owner can resume a form review, research pass, or draft exactly where they stopped and see what changed while they were away.
- effort: Medium-high: checkpoint schema and encrypted local persistence, anchor revalidation, reconnect UX, and integration with existing receipts/jobs.  ·  risk: DOMs can change and stale fields could be dangerous; recovery must stop on anchor mismatch and present the last safe state. If checkpoints corrupt, fall back to the untouched tab and receipt log. No irreversible action should be replayed automatically.
- cost: Negligible API cost; local encrypted storage and bounded page snippets add tens of KB per active task.  ·  latency: ~100–300 ms after each browser action for local checkpointing; reconnect adds 2–5 seconds for anchor validation.
- security: Checkpoints may contain sensitive page text and form values. Encrypt at rest on the Mac, redact passwords/payment fields, expire after 24 hours by default, and never send the checkpoint wholesale to the relay.
- depends on: A stable browser command/result identity and tab affinity (chg-14accc01’s existing pieces); Receipt linkage for reversible actions (chg-5fc73ce3); A reconnect event from the Safari extension instead of relying only on polling

### `browser-harness` — Make authenticated Safari extraction resilient to protected/isolated frames: when browser_read_page or snapshot receives ‘extension does not have access to this frame’, automatically retry through an extension-injected content script on the top frame, then use accessibility-tree or visible-text extraction as a fallback, returning a typed ‘partial/unavailable’ result with the frame URL instead of a generic failure.
- **owner gets:** The owner's live Gmail tab is visible and logged in right now, but the current browser tier cannot read it: a real read returned ‘Extension does not have access to this frame’. Fixing this unlocks the one capability no other node has—private web information—rather than merely improving logs.
- effort: Medium: Safari extension content-script permissions/manifest update, frame-aware extraction, and typed fallback results; test against Gmail and other authenticated SPAs.  ·  risk: A broader content script could expose more page data than intended or break complex sites. Limit injection to an explicit command, top-level visible frame, and bounded maxChars; if extraction fails, preserve read-only behavior and do not attempt clicks/types.
- cost: No meaningful model cost; small extension CPU/memory overhead only during an extraction.  ·  latency: Adds roughly 0.5–2 seconds for retry/fallback on protected frames; successful ordinary reads remain unchanged.
- security: Sensitive page text stays in the extension→local agent path, with redaction and maxChars limits. Never inject into password/payment fields and never persist raw frame contents by default.
- depends on: Safari extension update with explicit content-script/frame access; Typed browser result schema distinguishing complete, partial, and inaccessible frames; Existing POST /execute browser command path


## What it asked for

_Nothing._
