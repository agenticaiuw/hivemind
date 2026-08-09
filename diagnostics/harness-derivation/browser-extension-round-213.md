# Harness derivation — browser-extension — round 213

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser live state** — Safari extension is online with 3 tabs; active tab is authenticated chatgpt.com titled 'Hercules Mulligan Spy Tactics'. Three browser sessions exist: default plus two probe sessions. No commands are pending and browser spool is empty.
  - evidence: GET /browser/status returned online=true, tabCount=3, tabId=3839872, tabUrl=https://chatgpt.com, pendingCommands=0; GET /browser/sessions returned default, probe-form2, probe-form.

## Capabilities it proposed

### "“Keep an authenticated personal operations queue for me: watch the sites I configure, detect genuinely new deadlines, account changes, or requests, and tell me on the pendant only when something needs action.”"
- **useful because:** This is the highest-value browser-only capability: it turns sessions nobody else can reach into a continuously maintained, deduplicated queue, while the pendant makes urgent changes visible even when the Mac is closed. It should store short claims and provenance, not page bodies, and ship empty until the owner supplies origins and speech/retention rules.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Background watcher and cheap extraction model for routine page diffs; realtime only for the final spoken alert or an owner asking follow-up questions.
- **latency:** Polling can be minutes to hours old depending on the owner's schedule; a requested refresh should return a result within 30–60 seconds, with pendant alert delivery as soon as the relay receives a high-priority claim.
- **cost:** Low recurring cost dominated by authenticated page loads and extraction on changed pages; unchanged-page checks should use hashes/ETags where possible. Realtime speech is only paid for alerts the owner actually receives.
- **security:** Ship with an empty per-origin configuration. Never invent sites or sensitivity categories. Persist only <=200-character claims with host/URL provenance and the existing 24-hour browser TTL; never HTML, screenshots, or page text. Alerts must obey the owner's later may_speak/must_not_speak rules, and a dashboard must expose and delete every finding.
- **missing:** A scheduled browser page-watch job that can run browser sessions through the extension; Diffing and claim extraction specialized for authenticated pages, with explicit origin/category configuration; Relay delivery from browser findings into the accepted offline_alert_inbox; Owner-configurable per-origin and per-category policy UI, initially empty

### "“When I’m looking at a web form, turn it into a reviewable draft packet: explain each field in plain language, fill only what I explicitly authorize from my Mac data, and hand me a spoken summary on the pendant before I submit.”"
- **useful because:** Authenticated forms are where browser access matters most and where silent automation is dangerous. This gives the owner a concrete, inspectable bridge from a logged-in page to local data, catches mismatched names/dates/amounts, and lets the pendant review the final payload while the browser remains stopped before submit.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant → dashboard
- **model tier:** Cheap browser extraction and field matching first; use the expensive realtime model only to answer the owner's spoken clarification or summarize a disputed field.
- **latency:** Field inventory in 5–10 seconds; draft generation in under 30 seconds; no submission until the owner explicitly says to proceed in a later action.
- **cost:** Usually one extraction and one local lookup per form, with small context because only labels, constraints, and proposed values cross nodes. Speech cost is proportional to the number of fields summarized.
- **security:** Treat every proposed value as untrusted until shown with its source and confidence. Do not persist page contents or secrets; redact passwords, one-time codes, and payment numbers by default. Keep a reversible draft with an exact before/after diff and URL provenance, and make the owner explicitly choose which fields may be filled. The browser action allow-set must exclude submit/send until a separate owner instruction.
- **missing:** A browser forms schema that returns labels, constraints, current values, and stable field references without raw HTML retention; A local-data selector that can return candidate values with provenance and redact secret classes; A spoken pendant review packet with field-level navigation and correction; A durable, undoable draft transaction across browser and Mac

### "“While I’m away from the Mac, answer questions about my logged-in web accounts from the current page, and give me the exact claim plus where it came from and when it was checked.”"
- **useful because:** The pendant can ask the browser for facts no public search can reach—an order status, a portal balance, a reservation detail—without reading an entire page aloud. Provenance and freshness make the answer auditable, and a short-lived claim avoids turning private page text into permanent memory.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Use a small extraction model to locate the requested claim and a cheap verifier to check date/units; realtime handles the owner's follow-up dialogue and concise speech only.
- **latency:** On-demand response within 20–45 seconds, including browser navigation/read and relay delivery; if the page requires login or a challenge, report that rather than looping.
- **cost:** One browser read plus compact claim extraction per question; very little context because only the question, relevant snippets, and provenance are sent. Repeated questions within the 24-hour freshness window can reuse the claim.
- **security:** Only run against origins the owner later configures; ship empty rather than guessing. Do not expose full page text, screenshots, cookies, or credentials to the relay or memory. Return a bounded claim, host/URL, checked timestamp, and confidence; mark stale or ambiguous results clearly. Never click purchase/send/submit controls for a read question.
- **missing:** A pendant-to-browser request path that carries a natural-language question and target origin/session; Claim extraction with evidence offsets that can be shown in the dashboard without retaining page text; Freshness-aware join of browser findings into relay speech, with a way to force refresh; A device-side or relay-side redaction layer for secrets before any spoken response

### "“When a logged-in page gives me a deadline or appointment, reconcile it against my calendar and reminders, propose the least disruptive plan on the pendant, and create the local reminder only after I choose.”"
- **useful because:** The owner currently has to mentally transfer dates from authenticated websites into their calendar and notice conflicts themselves. This makes the browser a source of commitments, the Mac the planner, and the pendant the low-friction decision surface. It is not merely page reading or form filling: it resolves a web commitment against the owner's real schedule.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Background extraction and calendar-conflict computation use a cheap model or deterministic date parser. Realtime is reserved for the brief spoken choice when multiple plans are plausible.
- **latency:** Extract and compare within 20 seconds of an explicit request; speak two or three options in under 10 seconds; create the selected reminder immediately after the owner's choice.
- **cost:** One compact page extraction plus calendar/reminder lookup per request. Most work is deterministic; model cost is limited to ambiguous date language and a short spoken decision.
- **security:** Read only the configured authenticated origin and never submit or modify the website. Preserve the source URL, exact date interpretation, timezone, and evidence capsule. Ask before creating or changing local reminders, and make every created reminder undoable. Do not retain the page body.
- **missing:** A web-commitment extraction schema for deadlines, time zones, locations, and cancellation rules; A planner that compares extracted commitments with calendar/reminder availability and produces alternatives; A pendant choice protocol that identifies alternatives by short labels and carries the selected option back to the Mac; A durable cross-surface correlation linking the reminder to the source URL and browser evidence

### "“Compare the identity and account details shown on this logged-in site with my local records, tell me exactly what disagrees, and prepare the smallest correction plan for me.”"
- **useful because:** Small discrepancies in names, addresses, renewal dates, or account identifiers cause failed deliveries and support loops. No single node can do this: the browser sees the authoritative session, the Mac has local records, and the pendant can surface only the discrepant fields without exposing an entire private profile.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant → dashboard
- **model tier:** Use deterministic field normalization and a cheap comparison model; realtime is only needed to explain an ambiguity or ask which source should win.
- **latency:** A comparison should complete in 30 seconds for one page and return a short discrepancy list; correction plans are staged, never silently applied.
- **cost:** One page read and one local-record projection, with field-level context rather than full documents. Cost is dominated by logged-in page extraction, not conversation.
- **security:** Default to field hashes and redacted values in storage. Never speak full identifiers, payment data, passwords, or one-time codes. Show source and freshness for each side, keep a reversible correction plan, and stop before changing either the website or local records until explicitly selected.
- **missing:** A cross-surface identity-field schema with normalization rules for names, addresses, dates, and account IDs; A secret-aware comparison and redaction layer that can explain mismatches without echoing sensitive values; A staged correction planner spanning browser and Mac records with provenance and undo; A compact pendant UI for selecting which source is authoritative per field

### "“After I finish something in a logged-in website, verify that it actually took effect across the confirmation page and any matching local receipt, then tell me on the pendant if it is confirmed, pending, or failed.”"
- **useful because:** Today the owner can perform an action in Safari and still be unsure whether it succeeded, especially after a timeout or confusing redirect. This capability closes the loop without taking over the action: the browser supplies the private confirmation, the Mac checks local mail/files or records, and the pendant gives a decisive status with evidence.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant → dashboard
- **model tier:** Use deterministic confirmation markers and receipt matching first; a cheap model handles varied page wording. Realtime is only for an ambiguous spoken follow-up.
- **latency:** Check the live page within 10 seconds, then perform one delayed local-receipt check within 60 seconds; speak immediately when confidence is sufficient and mark pending when asynchronous confirmation is expected.
- **cost:** One browser read and one narrow local search per verification. Most checks are rules-based; model usage is limited to extracting confirmation IDs and status language.
- **security:** Never claim success from a page that lacks a confirmation identifier or matching evidence. Do not click retry, resubmit, or cancel. Store only a short status claim, timestamp, source URL, and redacted transaction/reference suffix under existing short browser TTLs; expose the evidence trail and allow revocation.
- **missing:** A post-action verification job that can correlate the current browser state with local receipts without initiating the action; A confirmation vocabulary and confidence policy for success, pending, failure, and ambiguous states; Cross-surface correlation of browser reference IDs with Mac mail/files/reminders; Pendant delivery that includes a concise status and a way to request the evidence trail


## What it asked for

_Nothing._
