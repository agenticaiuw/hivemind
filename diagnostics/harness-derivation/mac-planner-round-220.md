# Harness derivation — mac-planner — round 220

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser bridge live state** — Safari browser bridge is online and fresh (tab 3032326, DoorDash, 2 tabs, pendingCommands 0), but it advertises capabilities:[]; Mac Accessibility and Screen Recording are both granted and relay/mac bridge are reachable.
  - evidence: GET /ops/snapshot and GET /browser/status at 2026-08-08T22:14:18Z

## Capabilities it proposed

### "“When I say ‘take care of this’ on the pendant, carry out the obvious next step on my Mac or in my open browser, then tell me exactly what happened.”"
- **useful because:** This would make the pendant an actual remote control for the whole personal system rather than a voice memo endpoint. The relay can interpret the request while the Mac supplies authenticated app/browser reach; the owner gets one concise result, including a durable handoff if the action cannot safely finish. It is the highest-value missing behavior because it turns any small intention into a completed desktop outcome from anywhere.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime for the short spoken intent and confirmation/result phrasing; a cheaper background model for expanding the intent into a bounded action plan and summarizing receipts.
- **latency:** Acknowledge on the pendant within 1 s, begin Mac/browser work within 2 s, and speak completion or a durable ‘still working’ status within 10 s. Long jobs continue through the relay rather than holding the call open.
- **cost:** About $0.01–$0.05 for a short realtime turn plus <$0.01 for plan/receipt summarization; Mac/browser execution dominates wall-clock time, not tokens.
- **security:** The planner must show the exact target and action receipt to the relay, redact page text and secrets by default, and honor the owner's existing destructive-action confirmation policy (especially send, delete, purchase). An empty policy entry must stop unattended high-impact actions rather than relying on FULL_CONTROL_MODE. No microphone remains open after the request.
- **missing:** A relay intent-handoff record that binds one pendant utterance to one Mac/browser job and survives a dropped link; A result contract carrying touched resources, receipts, and unknown-outcome state back to the pendant; A policy-aware planner that can select between mac_run_actions and browser commands without treating arbitrary browser page text as instructions

### "“What am I looking at, and does it matter for anything on my calendar or in my inbox?”"
- **useful because:** The owner can ask this while a browser page is open and receive a short, source-grounded answer instead of copying URLs or explaining context. The browser extension contributes the authenticated page title, URL, selected text and a bounded readable extract; Calendar/Mail contribute only matching nearby commitments; the relay speaks the answer and can leave a cited note. This is meaningfully different from generic browser automation: it is cross-surface context joining with explicit provenance.
- **path:** browser-extension → mac-planner → relay → pendant → dashboard
- **model tier:** A cheap text model handles extraction, matching and citation selection; realtime is used only to phrase the final short spoken answer if the owner is still in a live pendant turn.
- **latency:** Page context in under 1 s, joined Calendar/Mail answer in 3–6 s, with a timeout that answers from the page alone rather than blocking on every source.
- **cost:** Roughly $0.005–$0.02 per request depending on page extract size; the dominant cost is redacted page-context tokens, so cap and hash repeated content.
- **security:** Never send passwords, form values, payment details, cookies or hidden DOM to the relay. Only the active tab's visible, bounded extract and URL should leave the Mac; mail/calendar matching should use snippets and redact bodies. Cite each claim with its source and say when no match exists.
- **missing:** A browser-bridge inspect result that returns visible text/selection with field-level redaction (status currently says online but capabilities is an empty array); A relay join endpoint that accepts browser context plus mac_read_sources results and emits provenance; A one-shot citation note writer that can be invoked only after the owner asks to save it

### "“Run the pendant health check now and tell me whether its microphone, radio path, and 24 kHz speaker path are trustworthy.”"
- **useful because:** The pendant is physically attached to this Mac over USB today even though it is not LTE-registered, so this can work now at the bench. It would turn the existing diagnostic fixture into an owner-facing answer: a dated pass/fail report, the measured counters, and an audio artifact the owner can replay, rather than requiring firmware logs and engineering interpretation. It catches the exact class of regressions that previously produced distorted or silent agent audio.
- **path:** pendant → mac-planner → mac-terminal → relay → dashboard
- **model tier:** No realtime model is needed for measurement. A cheap background model converts the structured fixture counters into one short spoken sentence and a detailed dashboard report.
- **latency:** Start within 2 s of the request; complete a bounded 30–60 s fixture; speak pass/fail immediately when the receipt arrives.
- **cost:** Near-zero model cost (under $0.01 for summarization); the cost is one controlled USB test run and a small report/artifact on the Mac.
- **security:** The fixture must generate synthetic audio only and never read or persist microphone content. The report should include counters, firmware version and timestamps but no serial secrets. A failed or interrupted run must be clearly marked incomplete, never silently reported as pass.
- **missing:** A resolved, read-only Mac USB diagnostic action that can arm the already-accepted audio_path_diagnostic_fixture and collect bounded UART output from /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A structured fixture receipt schema with pass thresholds for alias rejection, codec CPU, mic drops, tx starvation and clipping; Relay ingestion that turns the receipt into a durable health record and optionally queues the result in the pendant inbox when LTE is unavailable

### "“If something I asked you to do fails, explain the failure in one sentence, save the exact recovery state, and let me resume it later from the pendant.”"
- **useful because:** Today a failed browser or Mac action can leave the owner with a vague error and no trustworthy answer about whether anything happened. This capability would package the last safe checkpoint, touched resources, URL/app state and receipt into a redacted recovery card; the pendant can announce it later, while the Mac resumes or discards it. It is especially valuable for purchases, forms and long-running desktop work where a retry can duplicate an action.
- **path:** relay → mac-planner → browser-extension → pendant → dashboard
- **model tier:** A cheap background model summarizes structured errors and selects a safe recovery sentence; realtime is only used if the owner asks for the card during a live call.
- **latency:** Failure card within 2 s of the failed receipt; resume inspection under 2 s; resumption itself follows the original action's latency.
- **cost:** <$0.01 per failure for summarization; storage is a small encrypted JSON card and optional screenshot, with screenshot retention off by default.
- **security:** Persist only redacted state, never credentials or page form values. Unknown-outcome actions must be marked UNKNOWN rather than FAILED and must not be retried automatically. Destructive resumes remain subject to the owner's policy; discard must be local and explicit.
- **missing:** A durable recovery-card schema linking a Mac job, browser command, resource digest and unknown-outcome flag; A relay-to-pendant inbox payload type for recovery cards with expiry and one-tap inspect/resume/discard semantics; A browser/Mac checkpoint provider that captures URL, app identity and safe continuation point without screen scraping sensitive fields

### "“Before you tell me that something is done, independently prove that the outside world changed—then say what you verified and what you could not.”"
- **useful because:** The owner should never have to guess whether a browser submission, file operation, reminder, or purchase actually happened after an automation response. This capability separates execution from verification: the Mac or browser performs a bounded postcondition check, the relay compares it with the intended change, and the pendant speaks a compact evidence-backed result. It is different from retry or failure recovery because it prevents a false success from being presented in the first place.
- **path:** relay → mac-planner → browser-extension → pendant → dashboard
- **model tier:** A cheap background model maps each action to a typed postcondition and summarizes evidence; realtime only delivers the short spoken result.
- **latency:** Verification begins immediately after execution and returns within 3–8 seconds for ordinary browser/Mac actions; if verification is unavailable, the owner hears UNKNOWN rather than success.
- **cost:** <$0.02 per invocation; most cost is one extra bounded browser or Mac read, not model inference.
- **security:** Verification must read only the specific resource needed to establish the postcondition and redact values. Never infer success from a local click or HTTP 200 alone. Purchases, messages, and deletions require explicit evidence fields and remain subject to the owner's confirmation policy.
- **missing:** A typed postcondition schema attached to every planned action; Read-after-write adapters for browser pages, Calendar/Mail, Finder and reminders; A result state that distinguishes VERIFIED, NOT_VERIFIED, and UNKNOWN and can be spoken by the pendant

### "“After every request, show me exactly what information left this Mac, what stayed local, and let me erase the transcript and artifacts as one operation.”"
- **useful because:** The owner currently has to trust several surfaces independently. A single spoken or dashboard receipt would make data movement legible: page text, calendar snippets, audio, screenshots, and action results should each have a destination, retention time, and deletion state. This is not merely a settings page; it gives the wearer a usable privacy answer after a real interaction and a single purge operation across relay, Mac jobs, browser results, and local artifacts.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** No realtime reasoning is needed for the ledger. A small background summarizer can produce the one-sentence spoken receipt; deterministic code owns the inventory and purge operation.
- **latency:** A compact receipt within 1 second after a request completes; purge acknowledgment within 3 seconds, with any unreachable node clearly marked pending rather than claiming deletion.
- **cost:** <$0.01 per receipt; storage is a small metadata ledger. Purge cost is dominated by enumerating retained artifacts, not inference.
- **security:** The ledger itself must avoid copying the sensitive payload it describes. It needs cryptographic object identifiers, destination and expiry metadata, and authenticated deletion acknowledgments. The owner’s secret captures and microphone buffers must never appear in spoken receipts or dashboard previews.
- **missing:** A cross-node egress manifest with object IDs, destination, retention deadline and deletion status; Relay and Mac APIs for authenticated, idempotent purge with a receipt from every node; Browser-extension reporting of exactly which visible fields were exported, rather than only command success

### "“If I ask you to do something while the network is down, keep the request as a command—not just a recording—and carry it out automatically when the relay and Mac return. Tell me if the request was executed, rejected, or still waiting.”"
- **useful because:** The wearable should remain useful in dead zones. Today an offline voice memo can survive, but it does not preserve the difference between ‘remember this’ and ‘do this later.’ A durable deferred-command envelope would let the owner speak once, continue walking, and receive a truthful completion or rejection when connectivity returns. It combines the pendant’s local durability, relay transcription and scheduling, and Mac/browser reach without pretending the device has LTE now.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** No expensive realtime model is needed while offline. When connectivity returns, a cheaper asynchronous model transcribes/classifies the queued utterance; realtime only speaks the eventual status if the owner is present.
- **latency:** Local acknowledgement under 300 ms; upload when a link returns; classify and plan within 10 s; execute only when the Mac/browser heartbeat is healthy.
- **cost:** <$0.03 per deferred command including transcription and planning; storage is a small encrypted envelope plus optional audio that is deleted after classification.
- **security:** The local envelope must be encrypted and clearly labeled COMMAND versus MEMO. Never execute a command whose transcription confidence or target is ambiguous; expire commands and report rejection. Purchases, messages, deletion, and other high-impact actions need the owner’s configured policy at execution time, not when recorded offline.
- **missing:** A firmware/relay envelope type that preserves command intent, capture time, expiry and idempotency without retaining audio indefinitely; Relay-side deferred-command queue with deduplication and explicit states WAITING, PLANNED, EXECUTED, REJECTED and EXPIRED; Mac/browser executor support for delayed commands with a fresh context check and result callback


## What it asked for

_Nothing._
