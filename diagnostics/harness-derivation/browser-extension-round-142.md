# Harness derivation — browser-extension — round 142

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Keep an eye on this authenticated page and tell me on the pendant only when something materially changes — a new task, deadline, charge, status, or message — with a link and the exact changed fields."
- **useful because:** This turns the browser's unique access to logged-in services into a quiet, actionable wearable feed. The relay schedules checks, Safari reads the private page, a cheap model computes a structured semantic diff, and the pendant can deliver it even after the Mac link drops; public pages never need to leave the cheaper web-search path.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Background/scheduled small model for extraction and semantic diff; realtime only when the owner asks follow-up by voice.
- **latency:** Initial setup 1–2 minutes; scheduled checks can take 5–15 seconds each and should be silent unless the diff crosses the owner's configured materiality threshold.
- **cost:** About $0.002–$0.02 per check depending on page length and model; dominant costs are authenticated page extraction and scheduled model calls, not relay traffic.
- **security:** Page contents and diffs are sensitive and must stay ephemeral by default. Ship an empty per-origin policy and require the owner to configure origins, may-speak categories, and never-store categories. Keep only a hash plus redacted changed fields unless explicitly allowed; links should be spoken as a short origin/title, with the full URL available on the Mac dashboard. Never submit or mutate forms.
- **missing:** A durable browser page-watch scheduler that can target a Safari tab or re-find it by origin/title after tab restarts; DOM-to-structured-field extraction and semantic diff with confidence and materiality scoring; Per-origin read/extract/redact/never-store policy UI, empty by default; A relay-to-offline_alert_inbox delivery adapter with deduplication and expiry

### "From the private page I have open, find every date or amount I need to act on and turn only the high-confidence ones into reminders on my Mac, telling me on the pendant what you added."
- **useful because:** Authenticated portals hide bills, renewals, appointments, and application deadlines from ordinary web search. Safari can read them, the model can extract dates with source snippets, Mac can create reversible reminders, and the pendant gives an immediate audit trail without requiring the owner to copy anything.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background extraction model for candidate detection; realtime voice model only for clarification when confidence is low or dates conflict.
- **latency:** 30–60 seconds for a page or small set of tabs; never block the owner on a full-page workflow. Create reminders only after a compact candidate list is shown or spoken.
- **cost:** $0.01–$0.05 per run; extraction and conflict checking dominate, while reminder creation and pendant speech are negligible.
- **security:** Do not persist raw page text or financial/health details. Store reminder title/date plus origin and a redacted evidence hash. Candidate categories and whether they may be spoken must come from explicit per-origin policy, shipped empty; stop before any portal submission. Reminder text should omit account numbers and secrets.
- **missing:** A browser action that returns date/amount candidates with exact source spans and confidence, scoped to selected tabs; Cross-tab deduplication and timezone/locale normalization for dates; A compact review/commit protocol that can create several reminders through the existing Mac action and report receipts; Per-origin and per-category speech/persistence policy configuration

### "While I'm away from the keyboard, guide me through the form in my open Safari tab: tell me the next required field, let me dictate its value to the pendant, fill it, and read back a complete draft before I submit."
- **useful because:** This is a genuinely wearable use of authenticated browser access: the owner can complete tedious forms hands-free while Safari holds the session, without exposing credentials to another service or losing place in a long form. The extension supplies labels, required/error state, and tab identity; the relay conducts the short voice loop; the Mac planner can source allowed local values; submission remains an explicit final action the owner can perform separately.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Realtime model for the short dictate/confirm loop; deterministic DOM parsing for field labels and validation; background model only for ambiguous labels or error explanations.
- **latency:** Under 1 second for field prompts and fills; 2–4 seconds for ambiguous-field explanation. A 20-field form should remain resumable if the link drops.
- **cost:** $0.03–$0.20 per completed form, dominated by realtime transcription and spoken confirmations; DOM metadata and local field values are cheap.
- **security:** Never transmit passwords, OTPs, payment card numbers, or hidden fields; default deny those input types. Keep dictated values in volatile memory and erase them after fill or cancellation. Show origin, form title, field label, and exact final payload on pendant/Mac; do not click submit, send, purchase, or sign. Owner must explicitly configure any additional sensitive categories, with policy shipped empty.
- **missing:** A browser semantic-form action returning ordered fields, required/error state, and stable field IDs rather than page text; A voice session state machine that survives dropped links and resumes at a field without replaying values; Sensitive-input detection and volatile-value handling in the extension bridge; A final draft renderer with field-by-field provenance and an explicit non-submit handoff

### "When a site I already use pauses on an MFA challenge, ask me on the pendant for the one-time code, put it into the exact Safari tab that requested it, and tell me whether the login succeeded."
- **useful because:** This removes the most frustrating break in authenticated browser work without making the assistant a password manager. Safari identifies the requesting origin and tab, the relay routes a short-lived prompt, the pendant captures the code privately, and the extension fills only the OTP field; the owner can keep walking instead of returning to the Mac.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** Realtime model only for the brief prompt and confirmation; deterministic extension logic should detect OTP fields, origin, expiry, and success/failure. No general model should interpret or retain the code.
- **latency:** Prompt within 2 seconds of the challenge; fill within 5 seconds of the owner's reply. Abort automatically on expiry, origin/tab change, navigation, or mismatch.
- **cost:** Under $0.01 per challenge; the dominant cost is short realtime speech, with negligible browser and relay work.
- **security:** Never log, persist, summarize, or send the code to an LLM. Bind the value to an origin, tab, challenge nonce, and short expiry; reject passwords, recovery codes, and payment fields. Speak only the site name/origin, not page contents. Require a clear owner-initiated session and erase the value immediately after fill or cancellation. The current maximum-access policy means this is an observability/privacy boundary, not an execution gate.
- **missing:** Extension-side OTP challenge detector and origin/tab/challenge nonce binding; An end-to-end volatile secret channel from pendant microphone input to the matching Safari tab, bypassing model transcripts and generic action logs; Success/failure detector for the challenge and a safe expiry/abort state machine; A pendant prompt that identifies the requesting origin without retaining the code

### "After I finish something in Safari, save just the confirmation number, status, amount, and next deadline from the resulting page so I can ask the pendant for it later — never save the rest of the page."
- **useful because:** Confirmation pages are often lost when a tab closes, yet the owner later needs a reservation code, return window, claim number, or delivery status. Safari can identify the resulting receipt, the Mac can keep a tiny structured record, and the pendant can retrieve it hands-free without turning private page content into a transcript or document archive.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Deterministic receipt-schema extraction first; a small background model handles unfamiliar layouts and emits field-level confidence. Realtime is only for later retrieval.
- **latency:** Extract within 3 seconds of the owner marking the page as a receipt; retrieval should answer in under 1 second from the Mac's local store.
- **cost:** Usually below $0.01 per receipt; unfamiliar-layout extraction is the dominant model cost. Retrieval and pendant speech are negligible.
- **security:** Store only explicitly selected fields, origin, timestamp, and a redacted evidence hash in encrypted local storage; no full DOM, screenshots, credentials, or free-form page text. Expire records by category and let the owner delete them. Never infer or persist card/security codes. Spoken retrieval must require an owner phrase/button context and omit sensitive fields by default.
- **missing:** A receipt-page classifier and strict allowlisted field schema with confidence/provenance; An owner gesture or voice command that marks the current tab as worth recording, rather than silently harvesting pages; Encrypted local structured storage with per-record expiry and deletion receipts; Pendant retrieval intents that can distinguish confirmation records from ordinary reminders

### "Find a better slot for the appointment in my open portal that does not conflict with my Mac calendar, fill the portal's rescheduling form, and read me the exact new time before I confirm it."
- **useful because:** Only the browser can see authenticated availability and only the Mac can see the owner's local calendar. Combining them turns a tedious search across two private systems into a concrete draft while preserving control over the consequential reschedule. The pendant makes the result usable away from the desk; no site-wide credentials or calendar export is required.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background model ranks candidate slots after deterministic calendar overlap checks; realtime is used only to ask a concise preference question and report the draft.
- **latency:** Search and compare in 10–30 seconds for a week's availability; pause at the filled-but-unsubmitted form and remain resumable if Safari or the Mac link drops.
- **cost:** $0.01–$0.08 per search, dominated by parsing portal availability and preferences; calendar reads and form filling are cheap.
- **security:** Read only the minimum calendar busy intervals, not event titles or attendees, and keep portal page text ephemeral. Bind the draft to origin, appointment identity, and slot timestamp; invalidate it if availability changes. Do not click the final reschedule/confirm button or send notifications. Ship per-origin and per-category rules empty until the owner configures them.
- **missing:** A browser availability-table parser that yields normalized slots and appointment identity; A privacy-preserving calendar-busy query exposed to the planner without event metadata; Cross-system conflict ranking using owner-supplied preferences (earliest, morning, travel buffer, etc.); A resumable draft transaction that fills fields, detects stale availability, and stops before confirmation


## What it asked for

### `t15-hy3m` (tool) — browser_read_or_navigate
- why: Safari is online with 9 tabs, and authenticated page access is the only capability unique to this agent, but every currently granted enqueue wrapper is unresolved or ambiguous at call time. I need a read-only path to inspect the live tabs and ground useful work now.

```json
{
  "type": "object",
  "properties": {
    "operation": {
      "type": "string",
      "enum": [
        "browser_list_tabs",
        "browser_read_page",
        "browser_snapshot",
        "browser_navigate",
        "browser_wait_for"
      ]
    },
    "deviceId": {
      "type": "string"
    },
    "tabId": {
      "type": "string"
    },
    "url": {
      "type": "string"
    },
    "selector": {
      "type": "string"
    }
  },
  "required": [
    "operation"
  ]
}
```

## Its own summary

Produced three browser-specific capabilities: (1) scheduled semantic monitoring of authenticated Safari pages feeding actionable diffs to the pendant's offline alert inbox, (2) extraction of high-confidence dates/amounts from private pages into Mac reminders with redacted evidence, and (3) a hands-free, field-by-field form-filling mode that dictates into Safari but never submits. I also queued a narrow read-only browser tool using the system's exact action spellings because all existing enqueue wrappers remain ambiguous/unresolved. Safari is now live with 9 tabs, so this is no longer blocked on tab availability.

**Biggest unknown:** I still cannot inspect which 9 tabs are open or read their authenticated content: the granted enqueue wrappers do not resolve, and direct POST /execute dispatch returned fetch failed. The orchestrator needs to grant/resolve the narrow browser_list_tabs/browser_read_page tool (t15-hy3m), or repair the execute bridge. Product-wise, per-origin and per-category policies must remain explicit owner configuration and ship empty; I will not invent the owner's sites or sensitive categories.

