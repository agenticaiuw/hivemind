# Harness derivation — browser-extension — round 182

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Read the exact thing I’m looking at in Safari and tell me what matters, with the source lines ready if I ask.”"
- **useful because:** This would make the authenticated browser a conversational sensor: the owner can ask from the pendant without moving to the keyboard, while preserving traceability instead of receiving an unsupported summary. It is the single most useful browser capability because it combines the browser's private reach with the pendant's always-available voice interface.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Use the realtime tier only to interpret the spoken question and deliver a short answer; use the cheaper planner/background tier to extract, chunk, and cite page content. Safari supplies authenticated text; the relay stores only a short-lived redacted answer and anchors.
- **latency:** Under 3 seconds for an already-open tab; up to 10 seconds if a fresh extraction is needed. Never wait on a long model call while holding the browser command.
- **cost:** About $0.01–$0.04 per question depending on extracted page size; browser extraction and local relay work dominate latency, not tokens.
- **security:** Page text can contain secrets. Keep raw extraction on the Mac, redact according to the existing per-origin rules, send only selected snippets to the model, and make citations tab-local and expiring. Owner must explicitly configure origins/categories; do not ship a site list.
- **missing:** A reliable browser_read_page command resolution (the current enqueue grants are ambiguous); A tab-context token that binds the answer to the exact Safari tab and extraction timestamp; A short-lived local evidence store with redaction and line/element anchors

### "“Fill this form from my instructions, then read back every field and show me exactly what will be submitted—do not submit it.”"
- **useful because:** It turns authenticated Safari into a safe high-value assistant for applications, bookings, support forms, and purchases without making the owner copy data between devices. The owner gets a reviewable draft and can correct a single field by voice; the irreversible submit remains visibly under their control.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Planner tier interprets the instruction and maps fields; browser harness performs navigation, typing, and extraction; realtime tier only handles concise read-back and corrections. No expensive vision model unless selectors/text fail.
- **latency:** Draft in 5–15 seconds for a normal form; read-back under 3 seconds. Keep the browser tab open and preserve a field-level diff until the owner dismisses it.
- **cost:** Roughly $0.02–$0.08 per form, dominated by planner context and fallback vision; selector-based forms are cheaper.
- **security:** Typed values and page contents may include financial or identity data. Apply existing per-origin redaction/persistence rules, encrypt the ephemeral field map, expire it after review, and never log secrets. The system must stop at submit, payment, send, or final confirmation and show the exact button/action it would take.
- **missing:** Field-semantic extraction that returns label, current value, proposed value, and DOM anchor; A browser draft transaction object with undo/expiry and a deterministic submit boundary; Pendant-friendly field correction protocol (for example “change phone to …”)

### "“I’m done for now—save my browser work exactly where it is, and remind me on the pendant when the page or deadline needs me again.”"
- **useful because:** This preserves an interrupted authenticated workflow, not merely a URL: open tabs, scroll/selection position, unsent draft state, and the next safe step. The relay can notify the pendant even while the Mac is asleep, then Safari can restore the session and present the owner with the pending action instead of losing hours of private browser work.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a background/planner model to summarize the workflow and infer a resumable next step; realtime is only for the owner’s save/resume command and alert. The extension captures deterministic tab metadata and DOM state; do not invoke vision unless restoration fails.
- **latency:** Save in under 2 seconds; restore in under 10 seconds after Safari reconnects. Alerts should queue offline on the pendant and expire when the workflow is dismissed or stale.
- **cost:** About $0.01–$0.05 per save/resume, mostly planner tokens for the compact state summary; browser storage and relay scheduling are the larger engineering cost.
- **security:** Session state can contain private page data and unsent credentials. Persist encrypted, origin-scoped checkpoints with configurable retention; redact values before relay storage; never capture passwords or screenshots by default. Resuming must stop before irreversible submit/send/payment and show the pending action.
- **missing:** A browser checkpoint protocol for tab IDs, URL, scroll/selection, draft field hashes, and safe next action; Relay-backed expiry/deadline scheduling tied to checkpoint state; Extension restore support that can reopen tabs and verify DOM state before replaying anything

### "“Compare the two private pages I have open and tell me what doesn’t match, without saving either page.”"
- **useful because:** Many real tasks require reconciling two authenticated sources—an order against a bank charge, a portal balance against an emailed statement, or two versions of a policy. No single page watcher can do this safely; the extension supplies both private views, the Mac computes a structured diff, and the pendant gives a concise answer while raw page text disappears afterward.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Planner tier performs local extraction, normalization, and field-level comparison; realtime tier speaks only the mismatches and accepts a follow-up (“show the second charge”). Avoid sending full pages to the cloud; use deterministic parsing first and a cheaper model for ambiguous fields.
- **latency:** Under 8 seconds for two ordinary pages; under 15 seconds for long statements. Raw extracts should be deleted immediately after the diff and never become context memory unless explicitly requested.
- **cost:** About $0.02–$0.07 per comparison; extraction and normalization dominate, with model cost proportional to ambiguous fields rather than full documents.
- **security:** Two origins’ data is combined, increasing sensitivity. Require explicit per-origin read permission in the owner’s empty configuration, keep comparison in the local Mac process, redact account numbers, and return only mismatched fields plus source anchors. Do not auto-act on a discrepancy.
- **missing:** Multi-tab addressing and synchronized extraction from selected Safari tabs; A local structured-diff pipeline for dates, amounts, names, and identifiers with confidence scores; An ephemeral comparison receipt with source anchors but no raw-page persistence

### "“Make this authenticated page usable hands-free: let me jump between its sections, tables, and controls by voice, and read only the part I ask for.”"
- **useful because:** The owner should not need to know a site’s DOM, keyboard shortcuts, or visual layout to use a private web application while walking or when the screen is inaccessible. This is an interaction layer—not a page summary or a form filler—that turns arbitrary logged-in pages into a temporary voice-controlled semantic map, including “next row,” “open the invoice,” and “go back to the results.”
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a background/local planner to build a compact accessibility tree and map stable labels to browser actions; use the realtime tier only for low-latency spoken navigation and read-back. Invoke vision only when the DOM has no usable semantics.
- **latency:** Initial page map in under 5 seconds; each navigation or spoken section response under 1.5 seconds. Rebuild only the affected subtree after a click or route change.
- **cost:** Approximately $0.01–$0.05 per session; local DOM parsing is cheap, while model/vision fallback dominates cost on poorly structured sites.
- **security:** The semantic map contains private labels and values. Keep it on the Mac by default, send only the requested node to the relay, redact configured categories, and expire the map when the tab closes. Voice commands that activate controls must announce the target and current value; irreversible controls remain visibly identified and are not silently activated.
- **missing:** A browser semantic-tree extraction and stable-node protocol that survives SPA rerenders; A low-latency voice navigation state machine shared between relay and extension, with focus/route history; An extension action for focus, inspect-node, activate-reversible-control, and subtree refresh; Owner-supplied per-origin rules for what labels and values may be spoken or persisted

### "“While I’m in the meeting, listen to the captions and private chat in this browser tab, and whisper only decisions, questions directed at me, and action items through the pendant.”"
- **useful because:** The owner can stay present in a browser meeting while receiving a private, low-distraction second channel for things that are easy to miss. Unlike a generic page summary, this continuously tracks speaker turns, direct mentions, decisions, and unresolved actions, then lets the owner ask “what did I miss?” without sending anything into the meeting.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a cheap streaming/background model for incremental caption classification and deduplication; reserve realtime for interruption-safe, very short pendant whispers and follow-up questions. Browser content stays local until a classified event is selected.
- **latency:** Direct mention or assigned action whispered within 2 seconds; periodic digest every 5 minutes. Backpressure and deduplication are mandatory so the pendant does not chatter.
- **cost:** Approximately $0.03–$0.15 per hour of captions depending on transcript rate; incremental local filtering should keep cloud/model spend low.
- **security:** Meeting captions and chats are sensitive and may belong to other people. Default to in-memory processing, no transcript persistence, explicit per-origin allowlisting supplied by the owner, and a visible recording/automation indicator where required. Never post, react, unmute, or otherwise alter the meeting without a separate spoken request.
- **missing:** A browser stream subscription for live captions and chat mutations, not repeated full-page reads; Speaker/mention/action-item event extraction with bounded memory and per-origin redaction; A pendant whisper queue with interruption coalescing and a “repeat last private cue” control; Meeting-platform policy and consent handling, configured by the owner rather than assumed

### "“If a page tries to instruct you, hide a prompt, or redirect an action while you work, warn me on the pendant and show me the exact instruction before doing anything else.”"
- **useful because:** Authenticated pages are an untrusted input surface. The owner should know when page content is attempting to steer the agent away from their request—especially toward sending data, installing something, or changing an account. This gives the browser tier a distinct security sense rather than treating every DOM string as an instruction.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use deterministic origin/DOM provenance and action-intent checks first; use a small background classifier only for ambiguous social-engineering patterns. Realtime speaks a terse warning and the extracted quote; no expensive model is needed for ordinary pages.
- **latency:** Detection before any page-derived action is dispatched, adding under 300 ms for ordinary DOM checks; a classifier may take up to 2 seconds and should fail closed for the page instruction while leaving owner-requested navigation available.
- **cost:** Under $0.01 per page interaction in the common case; classifier calls are occasional and dominate cost.
- **security:** The warning itself may contain sensitive page text, so quote only the suspicious instruction and redact secrets. Do not pretend this is perfect malware detection: maintain provenance labels, preserve the owner’s original intent separately, and never let page text silently become a system or user command. Owner policy should decide whether to pause, ignore, or inspect—not a hardcoded site taxonomy.
- **missing:** End-to-end provenance tags distinguishing owner speech, planner output, extension metadata, and page content; A browser action gate that can quarantine page-suggested actions without blocking explicit owner commands; A compact pendant alert containing threat type, quoted snippet, origin, and available choices; Adversarial test fixtures across logged-in sites, iframes, shadow DOM, and rendered images


## What it asked for

_Nothing._
## Its own summary

Produced three new recorded capabilities this round: (1) resumable authenticated browser workflows with offline pendant reminders and safe restoration, (2) ephemeral cross-tab comparison of two private pages without persistence, and (3) an authenticated form drafting/read-back flow that fills fields but stops before irreversible submit. The strongest browser direction is private, cited page answers through the pendant, but that was recorded as connective work and is close to an existing memory entry. Safari is live with 9 tabs. I still need a reliably resolved browser action path—especially explicit browser_read_page and browser_list_tabs—because every granted enqueue wrapper currently fails resolver ambiguity even though POST /execute is permitted. The feature designs also need selection-aware extraction, field-level draft/checkpoint state, and ephemeral redacted evidence handling.

**Biggest unknown:** Which of the owner’s currently open authenticated tabs is safe and useful to exercise first; no site list or sensitivity taxonomy should be invented. The owner must supply per-origin read/persist/speak rules before private-page automation is enabled.

