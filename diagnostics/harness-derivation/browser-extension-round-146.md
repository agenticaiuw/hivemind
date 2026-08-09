# Harness derivation — browser-extension — round 146

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-live-state** — Safari extension is online and currently exposes 9 tabs, including authenticated Gmail and OpenAI billing pages; active tab is OpenAI billing overview. POST /execute with actions:[{type:'browser_list_tabs'}] works and returns typed receipts.
  - evidence: POST /execute 200 at 2026-08-08T01:15:25Z; browser_list_tabs result reports tabCount=9 and extensionId ai-pendant...

## Capabilities it proposed

### "Keep an eye on this logged-in web page and tell me on the pendant only if the specific thing I care about changes—for example, if the amount due, deadline, or approval state changes."
- **useful because:** The browser is the only node that can see authenticated pages, while the pendant is the only one that can reach the owner away from the Mac. A semantic, condition-based watch turns that combination into a useful early-warning system instead of requiring the owner to remember to reopen a portal. It should compare normalized fields rather than replaying private page text, and queue a short alert through the already accepted offline_alert_inbox when the Mac or relay is temporarily unavailable.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** background for polling and field-level diffing; realtime only to answer setup questions or speak an alert immediately
- **latency:** Initial setup under 5 seconds; scheduled checks can take 10–30 seconds per origin and tolerate stale results. Alert delivery should be under 2 seconds once a change is detected.
- **cost:** Usually under $0.01 per check when extraction is deterministic; an LLM semantic diff is the dominant cost and should run only after a field-level hash changes.
- **security:** The owner supplies the URL, selector/field description, and retention policy; configuration ships empty rather than assuming sites or sensitive categories. Store hashes and a redacted field summary, not page bodies. Never perform a click or submit as part of a watch. Speaking a payment, health, or employment value requires an explicit per-category may_speak setting.
- **missing:** A durable watch evaluator that schedules authenticated origin reads and keeps last-seen field hashes; A user-editable per-origin extraction/redaction configuration exposed in the dashboard; A browser-to-relay alert route carrying only the redacted diff and then into offline_alert_inbox

### "Check this logged-in booking, billing, or appointment page against my Mac calendar and tell me if it conflicts; if it does not, add a reminder with the page's exact date, time, location, and source link."
- **useful because:** This is a genuinely cross-surface task: only Safari can read the authenticated confirmation, while only the Mac has the owner's calendar/reminder machinery. It prevents the common failure where an assistant summarizes a reservation but never notices a collision or loses the follow-up. The owner gets a spoken conflict report first; creating the reminder is reversible and leaves a cited receipt.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** background/cheap model for structured date extraction and conflict comparison; realtime only for the spoken result and any clarification
- **latency:** One page read plus local calendar lookup in under 8 seconds; reminder creation immediately after the owner asks for it. No polling loop.
- **cost:** Typically $0.002–$0.02 per invocation; browser extraction and calendar I/O dominate latency, with model spend limited to ambiguous date/location parsing.
- **security:** Read only the specified authenticated page and calendar event windows needed for the date. Do not retain page text; retain only normalized appointment fields, source URL, and a short receipt. The owner supplies an empty per-origin rule before first use. Never alter an existing event; if timezone or date is ambiguous, report it instead of guessing. Creating the new reminder is reversible but should be shown in the spoken result.
- **missing:** A structured browser extraction contract that returns date/time/location/confidence and source URL rather than unbounded page text; A local calendar conflict query exposed to the planner (not just free-form calendar reading); A typed handoff that carries browser provenance into the Mac reminder receipt

### "Save this browser work as a named session, including the open tabs and where I was on each page, and later reopen the whole workspace on my Mac when I say its name to the pendant."
- **useful because:** The owner's authenticated Safari state is valuable and inaccessible to the other nodes, but today it is ephemeral: a crash, context switch, or closed window loses the exact working set. A privacy-preserving workspace lets the pendant act as the voice key, the relay remember a small manifest, and the Mac/browser restore the session without copying private page contents into the cloud. It is useful for research, bills, and unfinished forms while remaining clearly different from summarizing page text.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** No model for capture/restore; cheap background model only for voice-name normalization and resolving a vague tab label
- **latency:** Capture under 2 seconds for up to 20 tabs; restore under 10 seconds. A voice rename/lookup should respond in under 2 seconds.
- **cost:** Near-zero API cost; the expensive part is browser command round trips. Optional language normalization is less than $0.001 per request.
- **security:** Persist only origin, URL, title, tab order, window identity, and optional scroll coordinates; never persist DOM text, cookies, form values, or screenshots. Workspace names and manifests should be encrypted/local-first where possible, with an owner-configurable per-origin never-store rule. Restore must never submit forms or trigger clicks; report tabs that failed to reopen.
- **missing:** Browser commands for reading/writing scroll position and a stable tab/window workspace identifier; A small encrypted workspace-manifest store with explicit retention and delete controls; A pendant voice intent and relay route that resolves a workspace name to a Mac/browser restore job

### "When I walk away from my Mac, automatically hide or lock my sensitive logged-in Safari tabs, and restore them when I return wearing the pendant—without closing tabs or losing my place."
- **useful because:** The pendant is the one reliable signal that the owner is physically present; Safari is the one place holding authenticated sessions that must not be exposed to someone at the Mac. Today neither node can turn physical presence into browser privacy. A local presence state could blur/replace sensitive tabs or lock the Safari window on departure, then restore the exact session on return, protecting Gmail, billing, and other private accounts without forcing sign-in again.
- **path:** pendant → mac-planner → browser-extension → relay-realtime
- **model tier:** No language model for presence transitions or tab locking; use deterministic local rules. Realtime is only needed if the owner asks why a tab was hidden or wants an exception.
- **latency:** Departure detection and browser protection within 2 seconds; return restoration within 3 seconds. It must work with no relay connectivity while the pendant is USB-attached or locally paired.
- **cost:** Negligible API cost; implementation is local. Hardware uses existing pendant radio/USB and adds no recurring cloud spend.
- **security:** Presence tokens must be short-lived, signed, and never expose page content or cookies. Default to protecting only origins the owner explicitly marks sensitive; do not infer a sensitivity taxonomy. On uncertain connection loss, offer a configurable grace period rather than silently destroying state. Never close tabs or submit forms; lock/restore must be reversible and auditable.
- **missing:** A low-latency local presence signal from pendant firmware to the Mac agent, including connected, departed, and uncertain states; Safari extension commands for per-origin tab redaction/window lock and exact restoration without reading page content; An explicit owner-managed origin policy and local audit/override control

### "While I have a logged-in meeting or webinar open in Safari, capture the visible agenda or live captions, turn only explicit action items into a private checklist, and read me the next deadline through the pendant."
- **useful because:** The browser can see authenticated meeting captions and agendas that the relay cannot access, while the Mac can turn extracted commitments into reminders and the pendant can deliver the next deadline without making the owner return to the screen. This converts a transient web session into useful follow-through, rather than merely summarizing a page.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Cheap background extraction/classification for captions and action-item candidates; realtime only for a spoken query such as 'what is next?'
- **latency:** Incremental caption chunks processed within 10 seconds; action-item checklist available within 30 seconds of a segment ending. Spoken deadline lookup under 2 seconds.
- **cost:** Roughly $0.01–$0.05 per 30-minute meeting depending on caption volume; the model pass over captions dominates, so hash unchanged chunks and process incrementally.
- **security:** The owner explicitly starts and stops capture per tab. Captions and page text must remain local or be discarded after extracting candidate tasks; do not retain participant names or meeting content by default. Every extracted task carries the source timestamp and URL, and ambiguous language is presented as a candidate rather than silently becoming a reminder.
- **missing:** A browser capture stream for live caption/agenda regions with timestamps and incremental updates; An action-item extractor that distinguishes assignments and deadlines from general discussion; A local private task buffer and a pendant query route for the next deadline

### "Warn me on the pendant if a logged-in Safari page suddenly asks for credentials, payment details, or a security-code entry from an unexpected origin, and show me the exact domain and the page that triggered it."
- **useful because:** The browser extension sees the real origin, form controls, and current authenticated context; the pendant can interrupt before the owner types a secret. A local origin/form anomaly detector would catch a class of phishing, injected checkout pages, and expired-login traps that a generic webpage summary cannot reliably identify. It can be advisory only and never block the owner's maximum-control workflow.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Deterministic local checks for origin changes, credential/payment field appearance, and known session transitions; a cheap model may classify an ambiguous prompt locally, with realtime reserved for the short spoken warning.
- **latency:** Inspect each DOM/navigation transition in under 250 ms and deliver a warning within 2 seconds. It must continue locally if relay connectivity is absent, using the pendant's offline alert inbox.
- **cost:** Near-zero API cost for deterministic checks; optional classification costs under $0.001 per suspicious transition. Memory and CPU usage are the main costs.
- **security:** Never transmit entered values, cookies, passwords, or page bodies. Alerts should contain only domain, field category, and a short reason. The owner supplies any allowlisted origins; unknown does not mean malicious, so phrase it as a warning and provide an override. Keep a local, deletable alert receipt rather than a history of browsing.
- **missing:** A Safari content-script event stream for navigation and sensitive-field appearance; A local origin/session continuity and prompt-anomaly classifier; A signed low-latency browser-to-pendant alert path that works without the relay


## What it asked for

_Nothing._
## Its own summary

Safari is genuinely usable now: 9 live tabs, including authenticated Gmail and OpenAI billing, and POST /execute with browser_list_tabs returns receipts. I recorded three new owner-facing capabilities: condition-based semantic watches that alert the pendant, authenticated booking/billing-to-calendar conflict checking with cited reminders, and privacy-preserving named browser workspaces that can be resumed by voice. The strongest immediate value is turning a private authenticated page into a cross-device action (detect a date conflict, then create a sourced reminder), because no single node can do both halves. I still need implementation of structured browser field extraction, durable watch scheduling/diffing, calendar conflict querying, and encrypted URL-only workspace manifests; I do not need another browser enqueue wrapper because /execute is the working path.

**Biggest unknown:** The owner has not supplied the first per-origin rules: which authenticated origins may be read, what categories may be spoken, and what may never be persisted. These must remain explicit configuration rather than guessed defaults.

