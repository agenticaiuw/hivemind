# Harness derivation — mac-planner — round 187

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac Accessibility and Screen Recording state** — Live GET /observe at 2026-08-08T02:11:42Z reports AI Pendant Agent trusted, synthesized events posting successfully, Screen Recording true, and UI actions will reach the screen. This supersedes the older denied/blocked observation.
  - evidence: mac_readonly_inspect(operation=running_apps) resolved to GET /observe and returned accessibility.trusted=true, eventsPost=true, screenRecording=true, consequence=null.

## Capabilities it proposed

### "When I press the pendant's bookmark button and say “save this,” turn that moment into a context-rich note: what I said, the time, the app/window I was in, the relevant browser tab, and the next calendar item, then put a dated Markdown file in ~/AI-Pendant-Workspace and open it in VS Code."
- **useful because:** A bookmark today can mark a moment, but it cannot preserve why the moment mattered. This joins the worn button, the Mac's live context, and the always-awake relay into a durable note without making the owner reconstruct the scene later. It is the single most useful missing loop: fleeting thought to actionable artifact.
- **path:** pendant → relay → mac-planner → browser → dashboard-ux
- **model tier:** Realtime tier only for the short utterance and intent boundary; a cheaper background model extracts a title and next action from the transcript. Deterministic Mac collectors supply time/app/tab/calendar facts without spending model tokens.
- **latency:** Acknowledge the button locally immediately; relay event within 2 seconds when connected; write the note within 10 seconds. If offline, retain the bookmark and complete the enrichment when the link returns.
- **cost:** Usually one short realtime turn plus a small background extraction (roughly $0.01–$0.05 depending on transcript length); Mac observations and file creation dominate latency, not tokens.
- **security:** The note can contain sensitive window titles, mail/calendar subjects, and spoken content. Redact account identifiers and message bodies by default, store only the active tab URL/title and calendar item metadata, and require the owner's existing destructive policy only if the workflow ever sends or shares the note. Offline bookmark audio remains subject to the already-enabled capture setting.
- **missing:** A relay event-to-note orchestrator that joins offline_moment_bookmark records with a later transcript; A typed Mac collector for window identity and selected browser tab (GET /observe currently gives foreground app and browser sessions, but not semantic document selection); A stable note naming/deduplication contract so reconnect retries cannot create duplicate files

### "Keep me in focus mode: while I am in a meeting or presenting, do not speak for ordinary mail or notifications; interrupt the pendant only for a meeting starting within 5 minutes, a mail classified urgent, or a relay failure, and give me a quiet catch-up afterward."
- **useful because:** The Mac knows calendar, mail, foreground activity and presentation apps; the pendant is the only surface that can reach the owner away from the keyboard. Combining them prevents the two worst failures—missing a real deadline and being interrupted during a presentation—without requiring the owner to manage a mode manually.
- **path:** mac-planner → relay → pendant → dashboard-ux
- **model tier:** Cheap background classifier for mail urgency and meeting state; deterministic rules for calendar proximity, foreground Zoom/Keynote, and relay failure. Realtime is used only to speak an alert that survives the policy filter.
- **latency:** Evaluate on Calendar/Mail change and at most every 30 seconds; alert delivery under 3 seconds. Catch-up is generated after focus mode exits and can tolerate 30–60 seconds.
- **cost:** Near-zero model cost for rule checks; one small background classification batch per mail refresh and one short speech generation per delivered alert. Network polling and audio delivery dominate.
- **security:** Mail subjects/snippets and meeting titles leave the Mac only as minimized urgency facts; default to redacted snippets. Never infer urgency from full mail bodies unless explicitly enabled. A focus-mode transition must be visible in the dashboard and locally clearable; do not make leaving privacy/focus depend on network availability.
- **missing:** A policy engine that consumes mac_read_sources and foreground-app observations and emits one normalized alert priority instead of separate notification queues; A relay route to push a priority/expiry/quiet-mode envelope into the already-shipped offline_alert_inbox; A reliable focus-exit signal from the Mac (presentation/meeting state is not currently exposed as a semantic observation)

### "Turn the browser tabs I have open into a five-minute spoken research brief, with source links in a Markdown file, and stage the audio on the pendant so I can listen later even if the Mac goes offline."
- **useful because:** The owner repeatedly asks to inspect pages and list tabs, but the result currently dies as a chat response. This makes open-tab research a durable, listen-later artifact: browser sessions provide the private context, the relay synthesizes it, and the pendant's store-and-forward delivery makes it useful away from the desk.
- **path:** browser → mac-planner → relay → pendant → dashboard-ux
- **model tier:** A cheaper background model fetches and summarizes the bounded set of already-open pages; use realtime only if the owner asks a follow-up while listening. Do not resend page bodies to the low-latency model after the brief is created.
- **latency:** Collect tabs in under 5 seconds, fetch/summarize in 1–3 minutes, then stage audio asynchronously. The owner gets an immediate receipt and can continue working.
- **cost:** One background synthesis plus one speech render; cost scales with selected page text, so cap at 10 tabs and strip navigation/duplicate boilerplate. Storage is a small Markdown file plus one audio object with the existing 30-day retention.
- **security:** Authenticated pages may contain private research or account data. Only operate on tabs the owner explicitly selects or the current browser session, redact tokens/forms, never follow links or submit actions, and show the exact source URLs in the receipt. Audio should be encrypted in transit and deleted under the existing retention policy.
- **missing:** A read-only browser tab/page collector that can return bounded main-content text from the authenticated Mac browser without using click automation; A relay job that joins browser inspection results to /research and /research/briefings/:id/speech, then posts the finished audio to the pendant inbox; A durable listen-later receipt that identifies which tabs were included and prevents duplicate synthesis on retries

### "Save this authenticated webpage to my workspace as a durable research packet: download the original document through the browser session, verify its checksum, create a Markdown citation card with the title, author, URL, access date, and a short abstract, and tell me on the pendant when the packet is safely local."
- **useful because:** Today the browser can see a private page and the Mac can write files, but the owner must manually download, rename, cite, and verify every document. This would turn a spoken “save this” into a trustworthy local research artifact while preserving authenticated browser access and giving the owner a spoken completion receipt away from the desk.
- **path:** pendant → relay → browser → mac-planner → dashboard-ux
- **model tier:** Use realtime only to resolve the owner's short command and target tab. A cheaper background model extracts bibliographic fields and the abstract from the already-fetched document; checksum verification, staging, and citation formatting are deterministic.
- **latency:** Acknowledge intent in under 2 seconds; download and stage in under 30 seconds for ordinary documents; if a large file takes longer, send a pending receipt and notify only on atomic completion.
- **cost:** One small background extraction, usually under $0.03; network transfer and local hashing dominate. No model call is needed for unchanged retries.
- **security:** The browser session may contain private or licensed material. Operate only on the explicitly selected/current tab, never submit forms or follow unrelated links, and keep document bytes on the Mac. The relay should receive only job metadata, checksum, title, and a redacted abstract unless the owner explicitly asks for cloud backup. Do not claim success until the atomic write and hash check both pass.
- **missing:** A browser-bridge command that downloads the current authenticated response as bytes without exposing cookies or replaying credentials to the relay; A Mac-side MIME/type detector and streaming SHA-256 verifier integrated with atomic workspace staging; A relay receipt schema that binds source URL, access timestamp, checksum, and local path while making retries idempotent


## Changes it proposed to its own stack

### `mac-harness` — Add a narrowly scoped USB-serial pendant session to the Mac agent: enumerate /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA, send only the diagnostic-fixture and bookmark-sync command frames, stream sequence-numbered logs, and return an atomic receipt tied to a job id. It must refuse arbitrary serial bytes, survive reconnects, and expose a dry-run/status mode.
- **owner gets:** The pendant and ESP32 are physically on this Mac now, but the hive cannot prove whether a live audio failure is radio, codec, UART, or Bluetooth. The owner could plug in the hardware and ask for a health check that produces an actionable answer in minutes instead of reading UART logs manually.
- effort: Medium: a serial adapter in local-agent plus protocol framing, reconnect handling, and relay receipt storage; firmware already has the diagnostic fixture and store-and-forward behaviors to exercise.  ·  risk: Wrong-port selection could send commands to the wrong USB device; require VID/PID and handshake before any command. A hung serial read must be cancellable. Recover by closing/reopening the port and preserving the partial diagnostic receipt.
- cost: No API model cost for the transport; roughly 1–2 weeks engineering. No hardware cost because both boards are connected already.  ·  latency: Port discovery and handshake under 2 seconds; a full fixture is bounded by its test duration and can run asynchronously.
- security: Serial logs may contain spoken-audio counters or paths but never raw microphone content; redact payloads in relay receipts and keep raw logs local unless explicitly exported.
- depends on: A real mac_serial_exchange capability (the current request is still unresolved); audio_path_diagnostic_fixture; offline_audio_delivery_retry; A typed device identity handshake for the two USB boards


## What it asked for

_Nothing._
## Its own summary

Round 187 produced three owner-facing capabilities and one concrete Mac-harness change. The strongest is bookmark-to-context-note: a pendant press becomes a deduplicated Markdown artifact enriched with live Mac/browser/calendar context. I also proposed policy-driven focus mode (calendar/mail/foreground state filtered into the existing pendant inbox), open-tabs-to-listen-later research briefs, and a USB serial diagnostic session for the physically connected nRF9160 and ESP32. Live inspection also established that Accessibility, Screen Recording, and synthesized input are now actually working on AI Pendant Agent, superseding the older blocked finding.

**Biggest unknown:** I still need a resolved, narrowly typed mac_serial_exchange capability to test the live pendant/bridge over USB; the request remains unavailable this round. For the three workflows, the remaining product gaps are orchestration rather than hardware: semantic browser/page extraction, a normalized priority/focus policy, and idempotent relay jobs that join existing records without duplicate notes or audio. Browser inspection is also currently resolver-ambiguous between action:browser_inspect and POST /browser/inspect, so I need that branch disambiguated before relying on it.

