# Harness derivation — mac-planner — round 159

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Pin the page I’m looking at for later.” (Press the pendant button, or say it while the pendant is connected to my Mac.)"
- **useful because:** It turns an in-the-moment Safari page into a durable, searchable review item without copying URLs or losing the tab. The Mac supplies the authenticated active-tab identity, the pendant supplies an intentional physical gesture, and the relay keeps the queue available after Safari closes.
- **path:** pendant → mac-bridge → browser → relay-realtime → dashboard
- **model tier:** Background model for title/tag suggestion; realtime only for the brief acknowledgement.
- **latency:** Under 1 second for button acknowledgement and local queueing; enrichment can finish asynchronously within 10 seconds.
- **cost:** <$0.002 per pin when enrichment is requested; most pins need no model call. Storage and a small browser-bridge request dominate.
- **security:** Only capture the active tab's URL/title and optional selected text, never all tabs or page bodies by default. Authenticated URLs must be encrypted at rest and excluded from spoken output. No submission or navigation occurs.
- **missing:** A serial pendant-button event reader on the Mac bridge; A browser command to identify the active Safari tab and optional selection; A durable pin/review-item endpoint and deduplication by tab URL plus timestamp

### "“Stop everything now.” (Double-press the pendant to cancel queued Mac/browser jobs, pause relay-originated execution, and lock the Mac; tell me when it is safe.)"
- **useful because:** A worn physical stop is the one control that still works when a browser automation loop is surprising, the owner cannot find the window, or the network is lagging. It is an emergency brake, not a routine approval gate: it prevents further actions and leaves receipts for what already happened.
- **path:** pendant → mac-bridge → relay-realtime → browser → dashboard
- **model tier:** No model required for the stop path; a cheap background model may summarize cancelled jobs afterward.
- **latency:** Local serial event to Mac halt/lock in under 300 ms; relay cancellation fan-out within 2 seconds.
- **cost:** Near-zero model cost. Requires a small always-running serial watcher and relay lease/revocation writes; negligible storage.
- **security:** The stop gesture must be recognized locally with debounce and work without LTE. It should cancel only this system's jobs, not kill unrelated user applications. Relay must revoke execution leases and reject late commands; dashboard shows the exact cutoff sequence.
- **missing:** Pendant firmware double-press event and a fail-safe local LED acknowledgement; Mac bridge serial listener with an idempotent emergency-stop endpoint; Relay-wide execution lease revocation propagated to browser and Mac queues; A lock-screen action that works without Accessibility permission, or explicit owner setup for that fallback

### "“After you act on my Mac, tell me on the pendant exactly what changed, and let me ask ‘undo that’ within the next minute.”"
- **useful because:** Silent desktop automation is easy to miss or misunderstand. A short, spoken, timestamped receipt makes every browser/Mac action legible while the owner is away from the screen, and a bounded undo phrase turns a mistaken reversible action into a recoverable one without opening the dashboard.
- **path:** pendant → relay-realtime → mac-bridge → browser → dashboard
- **model tier:** Realtime model only for compressing the structured receipt into one sentence; no model for action execution or undo eligibility.
- **latency:** Receipt audio starts within 1 second of a completed action; undo command is dispatched within 2 seconds and reports success/failure.
- **cost:** <$0.003 per receipt including short TTS; structured receipts, eligibility, and undo are deterministic. Cost is dominated by speech synthesis.
- **security:** Speak app/action names but redact URLs, email bodies, tokens, and file contents by default. Undo must use the existing job receipt and only offer actions with a verified inverse; after the one-minute window, say unavailable rather than guessing. Store the spoken text briefly and delete it with the underlying receipt.
- **missing:** A relay subscription to Mac/browser job completion events; A structured receipt-to-speech renderer and pendant playback delivery over the currently USB-attached bridge; A time-bounded 'undo that' resolver that binds to the owner's most recent receipt, with ambiguity handling; A reliable local Mac-to-relay event channel when the pendant is tethered but LTE is unregistered

### "“Where did I leave off?”"
- **useful because:** The owner should receive one concise, time-ordered state of unfinished work: the foreground Mac app, open browser work, active jobs, recent receipts, today’s calendar commitments, and the last captured thought. Today those facts live in separate surfaces and require manual reconstruction; this would make the pendant a reliable re-entry point after an interruption.
- **path:** pendant → relay-realtime → mac-bridge → browser → dashboard
- **model tier:** A cheap background model assembles and ranks the state; realtime is used only to answer a live spoken request and render the short response.
- **latency:** Return a first spoken summary within 3 seconds, with deeper evidence available asynchronously.
- **cost:** <$0.01 per request; most input is structured metadata, with model cost dominated by summarization rather than retrieval.
- **security:** Do not read page bodies, mail bodies, or microphone data by default. Return source labels and timestamps, redact authenticated URLs and sensitive titles in speech, and let the owner request a specific source explicitly.
- **missing:** A single cross-surface state snapshot contract with freshness and confidence per item; Active-tab and foreground-app inspection implementations; A re-entry ranking policy that distinguishes unfinished work from merely open windows; Pendant delivery of a structured summary while the device is tethered or later reconnects

### "“Keep this completely on my Mac.”"
- **useful because:** For sensitive work, the owner should be able to ask for planning and execution without sending page contents, file contents, or personal data to the relay or model service. The Mac can perform deterministic actions locally while returning only a minimal outcome, making privacy a usable per-task choice rather than an all-or-nothing system setting.
- **path:** pendant → relay-realtime → mac-bridge → browser → dashboard
- **model tier:** Use the realtime model only to interpret the short request; local Mac rules and AppleScript perform the task. If semantic reasoning requires data, stop and explain exactly what would need to leave the device.
- **latency:** Immediate local execution for deterministic tasks; under 2 seconds for a privacy-mode capability check.
- **cost:** Near-zero model cost for supported tasks. Local AppleScript/browser operations dominate latency.
- **security:** The privacy contract must be enforceable, not merely a prompt instruction: block body/page/file payloads from relay logs, telemetry, receipts, and error traces. Show the owner which fields stayed local and provide a local audit record.
- **missing:** A task-level locality policy carried from relay intent to Mac execution; Payload inspection/redaction at the Mac bridge boundary; Local-only receipts that do not mirror sensitive action details to the relay; A browser adapter capable of acting on authenticated pages while returning only typed success/failure

### "“Only speak private results when I’m wearing the pendant; otherwise keep them queued silently.”"
- **useful because:** The system should distinguish a reachable speaker from a private listening context. When the pendant is disconnected, out of range, or its presence signal is stale, sensitive mail, calendar, browser, and file results remain encrypted and silent; when the owner returns, the pendant delivers a compact digest. This prevents a helpful answer from becoming an overheard disclosure.
- **path:** pendant → mac-bridge → relay-realtime → browser → dashboard
- **model tier:** No model is needed for the privacy decision. A background model can summarize the queued digest after presence is re-established.
- **latency:** Presence changes reflected in under 1 second locally; queued results released within 2 seconds of verified return.
- **cost:** Negligible model cost; small encrypted queue and serial heartbeat processing dominate implementation.
- **security:** Presence must be cryptographically tied to the owner’s pendant, not inferred from Wi-Fi or an arbitrary USB device. Sensitive payloads must be encrypted before leaving the Mac, never placed in ordinary logs, and expired automatically. A visible LED/state indicator should show queued-private mode.
- **missing:** Authenticated pendant presence/absence heartbeats over the live USB serial link and eventually LTE; A sensitivity label on every relay, browser, and Mac result; An encrypted hold-and-release queue with expiry and replay protection; A local audio policy that refuses private playback when presence is uncertain


## Changes it proposed to its own stack

### `integration` — Ship a local USB pendant gateway on the Mac that opens /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA, parses framed button/LED/audio messages, and bridges them to the Mac agent and relay with sequence numbers, reconnect, and offline buffering. Expose explicit status (connected, last frame, queue depth) and make the gateway start at login.
- **owner gets:** The pendant and audio bridge become usable today while LTE registration is absent: button actions reach Safari/Mac immediately, acknowledgements play locally, and queued events survive a cable or relay interruption instead of disappearing.
- effort: Medium: serial framing protocol, launch agent, reconnect tests, and relay/Mac event adapters.  ·  risk: Malformed frames or reconnect loops could flood the Mac agent; bound buffers, validate frame lengths, and watchdog the process. Recovery is automatic restart plus visible LED error code.
- cost: No model cost; roughly 1–3 W USB draw already supplied by the Mac. Small persistent event log (<10 MB).  ·  latency: 100–300 ms local event path; relay round trips remain network-bound.
- security: Treat serial input as untrusted and authenticate the bridge-to-relay channel. Do not log raw audio or authenticated URLs; log hashes and event types only.
- depends on: A documented framed serial protocol for the nRF9160 and ESP32; A local launchd service with access to the two live USB serial devices; A relay endpoint for reconnect/resume acknowledgements


## What it asked for

_Nothing._
## Its own summary

Recorded three new capabilities: interruption-aware cross-surface re-entry (“Where did I leave off?”), enforceable Mac-local privacy mode, and presence-gated private result delivery. Each identifies the missing cross-surface contracts rather than restating backlog items.

**Biggest unknown:** Whether the owner wants privacy defaults to be strict (queue all sensitive results when presence is uncertain) or permissive (speak redacted summaries).

