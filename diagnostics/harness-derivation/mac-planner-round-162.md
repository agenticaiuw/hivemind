# Harness derivation — mac-planner — round 162

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I tap the pendant twice, save a private, time-stamped thought with the Mac's current app and open browser context, acknowledge it on the pendant, and let me ask for the unsorted captures later—even if LTE is unavailable."
- **useful because:** A thought can be safely captured in the moment without opening a phone or losing what the owner was looking at. The USB-attached pendant is usable today despite the relay being offline, and the context makes each fragment recoverable rather than an orphaned note.
- **path:** pendant → mac-planner → mac-vision → relay-realtime
- **model tier:** Realtime only for the spoken acknowledgement; deterministic local code records and indexes the event, while a cheaper background model clusters or summarizes captures on request.
- **latency:** LED/serial acknowledgement under 150 ms; local capture under 1 s; semantic grouping can take seconds in the background.
- **cost:** Negligible per capture when local; roughly $0.001–$0.01 for optional background grouping depending on batch size. The dominant cost is model summarization, not serial or Mac inspection.
- **security:** Context may include private tab titles and the foreground app. Keep raw context on the Mac by default, redact secrets before relay upload, and require an explicit request to export or summarize remotely. Never transmit the known secret capture fields.
- **missing:** A Mac USB-serial pendant gateway that maps button/serial frames to authenticated /capture records; A small local capture store with ordering, deduplication, and replay/export; Firmware event frames and an acknowledgement command over /dev/cu.usbmodem00096003658*; A background capture-clustering routine distinct from the existing generic capture endpoint

### "Start a focus session from the pendant: mute distracting Mac notifications, route the bridge audio to my headphones, show the session end time, and when I tap again restore everything and turn the session's spoken action items into reminders."
- **useful because:** The owner can enter and leave deep work without touching the Mac, while the same physical gesture brackets the work period. It joins wearable intent, Mac state, audio hardware, and later reminder creation instead of treating focus mode as a desktop-only toggle.
- **path:** pendant → mac-planner → relay-realtime → dashboard
- **model tier:** Realtime handles only the short start/stop confirmation; local scripts and a deterministic state machine control Focus/audio, and a cheaper background model extracts action items from the session transcript.
- **latency:** Start/stop acknowledgement under 500 ms; notification and audio changes under 2 s; action-item extraction after the session may take 10–30 s.
- **cost:** Near-zero for state transitions; approximately $0.01–$0.05 per session for transcript/action-item extraction. Audio transport and Apple Shortcuts dominate engineering complexity, not API spend.
- **security:** A focus session changes notification and audio state and could hide urgent alerts. Persist the prior state, visibly signal active mode on the pendant LED, and restore state automatically on timeout or disconnect. Reminders must be drafts unless the owner has explicitly enabled auto-create.
- **missing:** A serial command channel and pendant firmware gesture beyond the current conversation press semantics; A crash-safe Mac Focus/audio state snapshot and restore service; Bridge control over /dev/cu.usbserial-0287A9CA, including headphone connection status; A session transcript boundary and action-item extraction hook

### "If my Mac or network drops while I am away, give me a spoken return capsule when the pendant reconnects: what I was doing, which Mac jobs finished or failed, what changed in my open tabs, and the next calendar item—with a one-tap option to resume the unfinished job."
- **useful because:** This is the system's most valuable cross-device behavior: the pendant is the owner's continuity anchor, while the Mac has the private state and the relay can survive the outage. The owner returns to a coherent next step instead of reconstructing it from scattered apps and logs.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Deterministic collectors build the capsule; use a cheap background model to compress it. Reserve realtime for speaking the final short capsule and accepting the resume tap.
- **latency:** Detect reconnect and assemble local state in under 3 s; speech starts within 5 s; resume is issued only after the owner taps, with job status confirmed within 2 s.
- **cost:** Usually under $0.01 per capsule for local collection plus short summarization; $0.01–$0.05 if browser-change reconciliation needs a model. The main cost is retaining bounded state, not inference.
- **security:** The capsule can expose work titles and private tab metadata through audio. Require the pendant's physical tap to unlock playback, redact secrets and page bodies, and retain only hashes/diffs with a configurable TTL. Resume must be idempotent and report the exact job receipt before acting.
- **missing:** A reconnect detector that treats USB serial attachment as a first-class device presence even without LTE registration; A compact durable resume capsule joining Mac jobs, foreground context, browser tab diffs, and calendar; An idempotent resume-token protocol from pendant to Mac with stale-job refusal; A speech queue that can deliver the capsule through the current pendant/ESP32 audio path

### "Before speaking or displaying anything sensitive, ask the Mac what context I am in—current meeting, foreground app, and active browser account—and have the pendant give me a discreet safe/unsafe signal; if unsafe, defer the answer into a private queue instead."
- **useful because:** Today the system can retrieve private information but cannot reliably know whether it is safe to reveal it at this exact moment. This prevents an embarrassing spoken disclosure in a meeting or in front of another person without requiring the owner to remember a manual privacy command.
- **path:** pendant → mac-planner → relay-realtime → browser-extension
- **model tier:** Use deterministic context and account classification first; use realtime only when the owner asks an ambiguous safety question. No model is needed for ordinary allow/defer decisions.
- **latency:** Safety verdict under 300 ms from local context; deferred response available within 2 s after the context becomes private.
- **cost:** Near-zero for local checks; occasional realtime clarification costs less than a cent. The expensive part is integrating reliable context signals, not inference.
- **security:** The safety service itself handles sensitive meeting and account metadata. Keep it local, expose only a boolean plus reason category to the relay, encrypt the deferred queue, and expire it automatically. A false-safe verdict is the primary hazard, so unknown context must default to defer.
- **missing:** A local context classifier combining Calendar attendees, foreground app, browser account/session identity, and an explicit private-mode state; A pendant haptic or LED vocabulary richer than the current recording/error indications; A relay contract for deferred answers that never sends their content until a private context is verified

### "While I am working, let the pendant interrupt me only for events that pass my personal urgency rules: detect incoming Mac notifications and calendar changes, collapse duplicates, and deliver a one-line alert with a physical tap to open the full item on the Mac."
- **useful because:** The owner should not have to choose between missing an urgent change and being constantly interrupted. The wearable is the right place for a tiny decision signal, while the Mac retains the private payload and the browser can open the exact source only when requested.
- **path:** pendant → mac-planner → relay-realtime → browser-extension → dashboard
- **model tier:** A local rules engine handles urgency, deduplication, quiet hours, and rate limits; a cheap background model can classify unfamiliar notifications. Realtime is only for the short alert interaction.
- **latency:** Classify within 2 s of a notification; alert under 500 ms after classification; opening the source under 3 s after the tap.
- **cost:** Near-zero for known notification rules; under $0.01/day for optional classification. Mac notification observation and reliable wearable delivery dominate implementation cost.
- **security:** Notification titles can reveal private content. Keep payloads on the Mac, send only a redacted category and short owner-approved label to the pendant, and require a second tap before any sensitive detail is spoken or opened.
- **missing:** A bounded read-only Mac notification feed with source app, timestamp, and stable event IDs; A persistent urgency/rate-limit rule engine with quiet hours and duplicate suppression; A serial notification channel and pendant interaction state separate from conversation recording; A safe deep-link registry from notification IDs to Mac/browser actions

### "When I say 'make this recurring', have the system observe the completed Mac/browser action for a week, infer the stable steps and exceptions, then propose a pendant-triggered routine with a plain-language preview and an easy way to disable it."
- **useful because:** Today routines must be authored up front, but the owner often discovers repetition only after doing a task several times. Learning from actual completed actions would turn one-off Mac and browser work into reliable personal automation without silently creating a powerful rule.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Use deterministic action receipts and event logs to detect repetition; use a cheaper background model to summarize the inferred routine. Realtime is unnecessary except for the owner's brief command and confirmation.
- **latency:** Record each action immediately; weekly inference can run asynchronously in under a minute; preview appears before any routine is enabled.
- **cost:** Usually under $0.05 per inferred routine, dominated by summarizing action traces. Storage and log retention are the larger operational costs.
- **security:** Action traces may contain URLs, file names, and typed text. Redact secrets at capture, retain only the minimum trace needed to reproduce steps, show every inferred mutation and exception in the preview, and never enable a routine without explicit approval. Disable must work from the pendant offline by storing a local kill switch.
- **missing:** A normalized cross-surface action-event schema linking Mac and browser receipts; A repetition/exception detector with trace redaction; A routine draft and approval UI plus a pendant-local disable flag; A scheduler/executor that can replay the routine idempotently and report receipts


## What it asked for

_Nothing._
## Its own summary

Recorded three new cross-device capabilities: (1) LTE-independent contextual pendant capture using the live USB serial link, (2) pendant-bracketed focus sessions that control Mac notifications/audio and produce reminder drafts, and (3) a reconnect-triggered spoken return capsule with safe job resumption. The third is the single most useful: it turns the pendant into continuity across Mac/network outages rather than another remote control. What remains needed is implementation of the USB serial gateway/firmware event protocol, crash-safe local state and reconnect detection, bridge audio control, and bounded capsule/resume storage. I did not re-request denied permissions or previously queued tools.

**Biggest unknown:** The live pendant and ESP32 serial protocols are not inventoried from this Mac agent's perspective: I do not yet know their current frame format, whether button events are emitted over USB today, or how audio/control commands are currently multiplexed. That determines which of the three can be prototyped immediately versus requiring firmware work.

