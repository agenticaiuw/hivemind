# Harness derivation — mac-planner — round 180

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Do that on my computer, and tell me when it is actually finished.” From the pendant, execute a multi-step browser/Mac plan end to end, then speak a one-sentence result or the exact blocker; never claim success from merely queuing the job."
- **useful because:** This is the system's most useful missing behavior: voice intent becomes a verified real-world outcome. The relay plans, the browser extension supplies authenticated session state, the Mac executes, and receipts are checked before the pendant says done. It handles partial failure by reporting the completed steps and offering retry rather than silently losing the request.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use realtime only to understand the short spoken request and deliver the result; use the cheaper background planner for decomposition, verification, and retry polling.
- **latency:** Acknowledge in under 1 s; begin actions within 3 s; speak completion as soon as the receipt arrives, with a 30 s bounded wait then an honest pending status.
- **cost:** About $0.01–$0.05 per ordinary task, dominated by planner/verification model calls; receipt polling and Mac/browser operations are negligible.
- **security:** Browser sessions may contain authenticated private data. Send only the minimum page facts to the relay, redact secrets in receipts, and require the owner's existing confirmation policy for send/delete/purchase classes. An empty policy must stop the relevant action, even though FULL_CONTROL_MODE currently bypasses it.
- **missing:** A durable cross-surface completion state machine joining one request ID to Mac job receipts and browser command results; A relay-to-pendant result event carrying completed/blocked/needs-confirmation, not just queued audio; A retry operation that resumes only idempotent steps and does not duplicate already verified mutations

### "“Watch this page and tell me only what changed.” While I have an authenticated page open in Safari, create a watch from the pendant; later, alert me when meaningful text or status changes, with an old/new diff I can hear, and let me cancel it by voice."
- **useful because:** It turns the browser's private authenticated session into a background sensor without making the owner repeatedly revisit it. The pendant is the capture/alert surface, the browser extension can see pages the relay cannot, and the relay can compare snapshots and suppress cosmetic churn. This is specifically for any page the owner is looking at now, not a generic work-portal integration.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Use a cheap background change detector and hash/DOM diff first; invoke the expensive model only for semantic change classification and a short spoken summary. Realtime is used only when the owner asks for status or cancellation.
- **latency:** Creating a watch should confirm in under 2 s; poll every 5–15 minutes according to page cost; alert within one polling interval; spoken diff under 5 s after detection.
- **cost:** Roughly $0.002–$0.02 per watched page per day, dominated by semantic classification; most polls should be hash-only and cost-free.
- **security:** Snapshots can contain private authenticated data. Keep raw DOM on the Mac/browser bridge, transmit redacted changed regions or hashes, encrypt durable state, expire watches by default, and never alert secret fields. Creating a watch needs explicit owner policy because it creates ongoing observation.
- **missing:** A browser watch create/update/delete route with URL/session affinity, interval, expiry, and redaction policy; A durable snapshot comparator that distinguishes meaningful DOM/text changes from timestamps, ads, and layout noise; A relay alert event that targets the existing offline_alert_inbox and includes a compact diff reference; A clear owner-visible list of active watches and their last successful poll

### "“What was I doing when I marked that moment?” After I press the pendant bookmark button, reconstruct the surrounding work context later: the Mac's foreground app and project, the authenticated browser tab, nearby calendar event, and any note or file I explicitly saved, then speak a short answer or make a dated note."
- **useful because:** A bookmark currently records that something mattered but not why. This makes the physical button a reliable time anchor and lets the Mac/browser/relay recover context without recording ambient speech. It is useful after interruptions, field testing, and debugging: the owner can recover intent from a single press rather than trying to remember it.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic timestamp joins and cheap metadata extraction first; use a background summarizer only to turn the joined evidence into one sentence. Realtime is reserved for the owner's later question.
- **latency:** Capture acknowledgement is local and immediate; context collection can happen within 10 s of reconnection; a later spoken answer should arrive within 3 s.
- **cost:** Usually under $0.01 per bookmark; model cost is only for summarization, while Mac/browser/calendar metadata joins are local or relay-side.
- **security:** Do not capture ambient audio by default. Browser URLs, mail/calendar titles, and filenames may be sensitive: store a redacted metadata envelope, scope collection to a short ±10 minute window, encrypt it, and allow the owner to delete a bookmark and its evidence. Never include page bodies or secrets in spoken output unless explicitly requested.
- **missing:** A correlation service that joins the existing bookmark event ID to Mac observation, browser session state, calendar range, and optional explicit note/file events; A stable project/document identity signal from the Mac beyond foreground-app name; A user-facing retention and deletion operation for the evidence envelope; A relay event/result type that can ask the Mac and browser for context at a historical timestamp rather than only current state

### "“I have no LTE. Can I still ask you something?” When the pendant is USB-attached to the Mac but the relay is unreachable, let me hold the button and have a short local voice conversation through the Mac, then sync the transcript and any answer metadata when connectivity returns."
- **useful because:** The wearable should not become inert merely because it is indoors or in a dead zone. This is a genuinely different operating mode from store-and-forward voice memos: it provides bounded conversational answers while disconnected, using the physically present Mac as the bridge and keeping the pending exchange durable until the relay returns.
- **path:** pendant → mac-planner → relay-realtime → dashboard
- **model tier:** Use a small local Mac speech/model stack for the disconnected mode; use the realtime relay model only after reconnection for sync, correction, or tasks requiring cloud context.
- **latency:** Detect relay failure locally within 2 s, start a fallback response within 3 s, and cap offline conversations at 30 s or a small token budget so they do not monopolize the Mac.
- **cost:** Near-zero API cost while offline; local model inference costs Mac CPU/battery. Reconnection sync may cost a few cents for summarization or conflict resolution.
- **security:** Offline mode must declare that cloud context is unavailable and must not silently read browser sessions or secrets. Store encrypted short-lived transcript chunks locally, delete them after relay acknowledgement, and honor the pendant's local privacy latch.
- **missing:** A USB serial audio/control transport between pendant and Mac; A local speech-to-text and small response model on the Mac; A durable offline conversation envelope with sequence numbers and conflict handling; A relay reconciliation endpoint that accepts the envelope without duplicating turns

### "“What changed in my project since I last marked it?” Have the pendant bookmark a baseline, then later compare the workspace and active editor state, explain the meaningful code/config changes in one spoken sentence, and optionally open a review note without submitting or sending anything."
- **useful because:** It gives the physical bookmark a software-engineering meaning: the owner can leave a debugging session and return to an intelligible delta. The Mac has the files and editor, the pendant supplies a low-friction baseline, and the relay turns raw diffs into a concise explanation. It avoids ambient recording and does not require a commit or a clean working tree.
- **path:** pendant → mac-planner → relay-realtime → dashboard
- **model tier:** Use local hashing and git diff/statistics for collection; use a cheaper background model for summarization and realtime only for the spoken answer or follow-up question.
- **latency:** Baseline acknowledgement under 1 s; ordinary diff under 5 s; spoken explanation under 4 s; large repositories should produce a bounded summary and a workspace note asynchronously.
- **cost:** Usually under $0.02 per comparison, dominated by summarizing changed hunks; file hashing and diff collection are local.
- **security:** Code can be proprietary. Keep full diffs on the Mac, send only selected hunks or redacted summaries, exclude secret-like files by default, and make the owner explicitly choose a repository and retention period. Never alter or submit changes without a separate command.
- **missing:** A time-indexed workspace snapshot manifest tied to the existing pendant bookmark ID; A read-only repository/diff collector that works without requiring a commit; A redaction and hunk-selection layer before code leaves the Mac; A review-note receipt linking the spoken summary to the exact snapshot pair

### "“Why did the last pendant call sound bad?” After a call or diagnostic run, give me a causal explanation rather than raw counters: identify whether the problem was radio loss, encoder/decoder load, underrun, clock drift, or the Mac/browser path, cite the measured evidence, and recommend one next test."
- **useful because:** The owner currently gets telemetry and can get a bug report, but not an explanation they can act on. This capability combines the pendant's QoS and diagnostic frames, relay pipeline timing, Mac bridge state, and browser transport health into a ranked fault hypothesis. It prevents wasting time changing codec settings when the real fault is USB, radio, or scheduling.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic thresholds and known signatures for first-pass classification; use a cheaper background model to write the explanation. Reserve realtime for the owner's follow-up question.
- **latency:** Produce a provisional explanation within 10 s of call end; refine it when delayed counters arrive, without waiting more than 60 s.
- **cost:** Under $0.02 per call in normal cases; most work is rule-based aggregation, with model cost only for explanation and next-test wording.
- **security:** Telemetry must exclude microphone payload and transcripts. Keep raw sequence data short-lived, expose the evidence window and confidence, and avoid claiming a single cause when measurements are ambiguous.
- **missing:** A shared call-run identifier propagated through pendant QoS frames, relay pipeline records, Mac jobs, and browser heartbeats; A normalized telemetry schema with timestamps, packet loss, underruns, CPU duration, USB serial counters, and browser delivery state; A causal-rule library validated against the existing 24 kHz acceptance fixtures; A spoken and dashboard result type that includes evidence references, confidence, and one recommended diagnostic action


## Changes it proposed to its own stack

### `integration` — Add a USB-serial pendant evidence bridge on the Mac: continuously parse only explicitly tagged diagnostic lines from /dev/cu.usbmodem00096003658* (and the ESP32 bridge on /dev/cu.usbserial-0287A9CA), rotate a bounded redacted log, correlate fixture counters with relay pipeline IDs, and expose a one-command “file this failure” action that writes a Markdown bug report into ~/AI-Pendant-Workspace and opens it in VS Code. It must be opt-in per diagnostic session, never open the microphone, and never persist raw audio.
- **owner gets:** When the wearable misbehaves, the owner gets a usable bug report instead of a UART dump and can hand it to the system or developer immediately. This is runnable today because both boards are physically USB-connected, even though LTE registration is not available.
- effort: Medium: a serial reader/parser, bounded rotation, pipeline correlation, report template, and VS Code handoff; then one hardware-in-the-loop test for each board.  ·  risk: Wrong-port selection or malformed serial data could create noise; constrain to exact VID/PID/port patterns, require diagnostic mode, cap disk use, and allow deleting reports. Recovery is simply disabling the bridge and deleting generated Markdown files.
- cost: No API cost for parsing; negligible Mac CPU and under 10 MB rotating storage. No new hardware cost.  ·  latency: Counters and failure reports appear within seconds of a diagnostic run; no impact on live audio because the bridge is read-only serial metadata.
- security: UART may contain identifiers or transcript fragments if firmware logs them; redact payload fields, allow a per-session raw-log toggle, and default to counters/sequence IDs only.
- depends on: A real mac_serial_exchange capability or an equivalent allowlisted serial-read route on the Mac; audio_path_diagnostic_fixture emitting stable tagged diagnostic records; A report receipt route linking the generated file to the relay pipeline/job ID


## What it asked for

_Nothing._
