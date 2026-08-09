# Harness derivation — browser-extension — round 231

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser live state** — Safari extension is online and POST /execute browser_list_tabs returned five live tabs, including YouTube, dashboard, and three DoorDash pages; active tab is a DoorDash restaurant page. This differs from the earlier no-tab state and means authenticated browser workflows are testable now.
  - evidence: POST /execute with {"actions":[{"type":"browser_list_tabs"}]} returned status 200, tabCount 5, extensionId ai-pendant...

## Capabilities it proposed

### "Watch a signed-in page I choose and interrupt me only when something important changes — a new bill, delivery state, appointment slot, or security event — with a one-sentence explanation on my pendant."
- **useful because:** This turns the browser's private logged-in reach into an always-on service: the owner does not need to remember to check volatile portals, while the pendant delivers the result even when the Mac link later drops. It is the highest-value thing this system could do because it combines unique browser access, relay scheduling, judgement, and the offline alert inbox rather than merely reading a page on demand.
- **path:** browser-extension → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheap background model for scheduled page extraction and change classification; use the realtime model only to phrase an interrupt or answer a follow-up. A deterministic diff plus short claim extraction should precede any model call.
- **latency:** Polling/checks can take 1–5 minutes and must not block conversation; a detected high-priority change should reach the relay in under 10 seconds and queue locally on the pendant.
- **cost:** Roughly $0.01–$0.05 per monitored page check depending on extraction and model use; browser polling and deterministic diffs dominate volume, not realtime inference.
- **security:** Ship with an empty per-origin rule set and require the owner to add origins and categories. Never retain page HTML, text, or screenshots: store only host-keyed claims with URL evidence, 24-hour TTL, and 200-character value caps. Do not read aloud categories the owner marks must-not-speak. The monitor must stop at login/2FA and never submit forms.
- **missing:** A durable scheduled browser-watch job that creates or reuses a browser session and invokes POST /execute browser_read_page on a cadence; Semantic change classification and deduplication across page snapshots, with severity/category controls; Relay-to-pendant delivery wiring for browser findings using the accepted offline_alert_inbox skill; An inspectable empty per-origin and per-category configuration UI

### "When I say “what am I looking at?”, have the pendant answer from the active Safari page, then let me say “remind me” or “compare that with my calendar” without copying or pasting anything."
- **useful because:** The owner can use private, authenticated web context while away from the keyboard: the browser supplies the page, the Mac planner turns it into a small set of claims, and the relay/pendant handles a spoken follow-up. The useful novelty is the handoff of a selected, ephemeral page context into calendar/reminder action, not a generic browser reader.
- **path:** browser-extension → mac-planner → relay-realtime → faculty-perception → faculty-action
- **model tier:** A fast extraction pass should identify headings, dates, prices, and status deterministically; use the realtime model only for the spoken answer and intent resolution. Use a cheaper model for calendar comparison and reminder wording.
- **latency:** First spoken answer within 5 seconds; follow-up reminder or comparison within 10 seconds. Keep page context ephemeral and discard it after the interaction unless the owner explicitly asks to save a finding.
- **cost:** About $0.01–$0.04 per interaction; browser extraction and a short response dominate, with no need to send a whole page to the model.
- **security:** Read-only by default and stop before any page submit. Only the active tab is read, with an owner-configurable origin policy shipped empty. Page text stays on the Mac during extraction; persisted output is limited to short, task-matched claims under existing browser retention rules. Reminder creation should expose the exact title/date before it is created.
- **missing:** A pendant-to-browser intent route that selects the active Safari tab and requests a bounded browser_read_page; A short-lived page-context handle shared between browser and Mac planner without placing page text in general conversation memory; Calendar/reminder comparison that accepts extracted dates and creates a reversible reminder; A spoken confirmation/result path over pipeline audio/events

### "Prepare a logged-in web form for me from a voice request — fill the non-sensitive fields, show me exactly what will be submitted, and let me approve or edit it from the pendant before anything is sent."
- **useful because:** Forms are where browser access saves the most tedious work, but the owner should retain the final decision. This makes the Mac/browser combination do the tedious navigation and field mapping while the pendant is the physical review surface; it can handle applications, support requests, and reservations without requiring the owner to return to the screen.
- **path:** browser-extension → mac-planner → relay-realtime → faculty-judgement → faculty-action
- **model tier:** Use a cheaper model or deterministic DOM extraction for field mapping and a background model to draft values from the owner's explicit request. Realtime is reserved for the final spoken diff and approval conversation.
- **latency:** Draft in under 15 seconds for ordinary forms; approval response should be immediate. Never auto-submit after a timeout or dropped connection.
- **cost:** About $0.03–$0.15 per form depending on field count and page complexity; browser actions and DOM snapshots dominate, while model cost is bounded by field summaries.
- **security:** Owner policy allows maximum access, so this is not a blocking permission gate; nevertheless show a precise pre-submit diff and require an explicit pendant approval as a product interaction. Mask secrets and payment fields in spoken output, never persist page bodies, and retain only a provenance record of filled fields. Abort on CAPTCHA, 2FA, payment, or changed page structure rather than guessing.
- **missing:** A browser form planner that emits field-level proposed values and a stable pre-submit diff; A pendant approval/edit protocol that can target individual fields and survive a dropped Mac link; A browser action transaction with draft, preview, and explicit submit phases plus undo where the site supports it; Redaction for secrets/payment fields in browser receipts and spoken summaries

### "After I complete something important in Safari, have the pendant independently verify the result against what I intended and tell me immediately if the site did something different — wrong amount, date, address, quantity, or status — then prepare the exact correction or dispute without sending it."
- **useful because:** Today browser automation can read or fill, but there is no independent postcondition check that protects the owner after a real web transaction. The browser sees the authoritative receipt/status, the Mac compares it with the owner's original intent, and the pendant catches a mismatch while it is still easy to fix. This is a genuinely different safety net from form preview or page watching.
- **path:** browser-extension → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use deterministic extraction and typed comparisons for amount/date/address/quantity/status; use a background model only to normalize messy labels and draft a correction. Realtime is reserved for the short wearable warning.
- **latency:** Run immediately after the owner returns to the receipt page; speak a mismatch within 8 seconds. If the page is unavailable, retry in the background and do not claim success.
- **cost:** About $0.01–$0.08 per verification; DOM extraction and field comparison dominate, with model use only for ambiguous labels.
- **security:** The intent record must be short-lived and scoped to one transaction. Never store receipt HTML or payment details; retain only a redacted mismatch claim and provenance. Treat the site's receipt as evidence, not authority to send a correction. Stop before dispute submission and show the exact proposed text.
- **missing:** A transaction-intent envelope linking an owner request to a later receipt without retaining the full request transcript; A typed receipt/postcondition extractor and comparator for common fields; A browser trigger that recognizes completion pages or an explicit owner 'verify that' command; A discrepancy receipt that can be delivered through the offline pendant inbox

### "Let me say “keep this private until I get home,” and have the pendant, Mac, relay, and Safari enforce a temporary privacy bubble: no page content spoken or persisted, no background browser jobs, and automatic release only when my pendant is physically back on my trusted Mac."
- **useful because:** The owner currently has no way to express a temporary, physical-context privacy mode across all surfaces. A wearable presence signal can be the one control that reaches the browser session, Mac planner, and always-awake relay together; this is useful for banking, health, gifts, and shared spaces without inventing a permanent site taxonomy.
- **path:** relay-realtime → browser-extension → mac-planner → mac-vision → faculty-action
- **model tier:** No expensive model is needed for enforcement. Use a signed device-presence state machine and deterministic suppression; use realtime only to acknowledge activation and release.
- **latency:** Privacy activation under 2 seconds; revocation on pendant disconnect under 5 seconds. While active, queued browser jobs must be canceled or quarantined, not merely hidden.
- **cost:** Negligible inference cost; engineering is in signed presence, queue cancellation, and redaction across existing browser and relay stores.
- **security:** This must be fail-closed for speech and persistence but must not delete evidence silently: quarantine with an expiry and show a local status indicator. Presence should be cryptographically bound to the pendant, not inferred from Wi-Fi. The owner explicitly controls activation; never silently release because a timeout elapsed.
- **missing:** A signed pendant-presence lease exposed to relay and Mac over the current USB-connected hardware path; A cross-surface privacy state propagated to browser sessions, planner queues, logs, memory projection, and audio; Cancellation/quarantine semantics for in-flight browser commands and already-produced page findings; A small pendant UI/LED indication for active, pending-release, and expired privacy states

### "When a web service changes its terms, price, deadline, or eligibility while I already have an open tab, have the Mac compare the old and new clauses, have the judgement layer explain only the practical consequence for me, and let me ask the pendant “what changed?” without reopening the site."
- **useful because:** A normal page watcher reports that text changed; this would turn a volatile authenticated page into a personal-impact explanation tied to the owner's existing commitments. It combines browser snapshots, short-lived provenance, owner context, and wearable follow-up instead of dumping legal text or requiring the owner to reread it.
- **path:** browser-extension → mac-planner → faculty-perception → faculty-judgement → relay-realtime
- **model tier:** Use deterministic text/DOM diff first, a cheap background model to extract clauses, and the realtime model only for the owner's follow-up question. Never resend whole page bodies on every turn; pass a compact clause-diff capsule.
- **latency:** Detect on the next scheduled/open-tab check; produce a consequence summary within 15 seconds of a meaningful change. Follow-up answer under 3 seconds from the stored capsule.
- **cost:** About $0.02–$0.10 per meaningful change; most checks should be hash/diff-only, with model calls limited to changed clauses.
- **security:** Do not assume which origins or categories matter: ship an empty owner-configured policy. Store only changed short claims, URL, and evidence under the existing browser TTL/cap; never retain full legal pages. Mark uncertainty and link back to the source instead of presenting legal advice as fact.
- **missing:** A clause-aware diff that survives DOM rearrangement and identifies effective dates, prices, obligations, and eligibility; A personal-impact join against the owner's calendar, reminders, and saved commitments without broad memory projection; A compact browser evidence capsule addressable by a later pendant question; A notification severity policy that distinguishes informational changes from action deadlines


## What it asked for

_Nothing._
## Its own summary

Safari is genuinely live now: POST /execute browser_list_tabs returned five tabs, including three DoorDash pages, so browser work is no longer hypothetical. I recorded three capabilities: (1) the highest-value cross-node feature, an authenticated page-change sentinel that classifies changes in the background and escalates only important ones through relay to the pendant's offline alert inbox; (2) an active-page voice handoff that answers “what am I looking at?” and turns a page date into a reminder or calendar comparison without copy/paste; and (3) a draft/preview/approve form workflow that fills logged-in forms but stops at an exact spoken submit diff. The first is intentionally more ambitious than today's wiring and combines browser, scheduler, judgement, relay, and wearable delivery.

**Biggest unknown:** The missing pieces are not browser reach anymore: a durable scheduled browser-watch runner with semantic diff/deduplication, a short-lived page-context handle for pendant follow-ups, and a field-level form transaction/approval protocol. I still need the owner to choose origins and speak/persistence categories; that configuration must ship empty rather than be guessed. The live tabs also reveal sensitive commerce context, so I should not inspect or act on them without a concrete owner request.

