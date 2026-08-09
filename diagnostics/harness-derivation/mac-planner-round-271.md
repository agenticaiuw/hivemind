# Harness derivation — mac-planner — round 271

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-accessibility-and-screen-recording** — The live Mac observe endpoint reports AI Pendant Agent Accessibility trusted, synthesized events posting successfully, Screen Recording true, secure input false, and ui actions will reach the screen. This supersedes the older denied snapshot for this host.
  - evidence: mac_readonly_inspect operation=running_apps resolved to GET /observe at 2026-08-09T01:39:18Z; body accessibility.trusted=true, eventsPost=true, screenRecording=true.

## Capabilities it proposed

### "“Watch this USPS tracking page until the package is delivered; tell me only when the status changes to out-for-delivery or delivered, and leave a short spoken alert on the pendant.”"
- **useful because:** The Mac already has a live USPS tracking tab, but today the owner must remember to revisit it. This turns a transient browser page into a useful, quiet physical alert: no constant notifications, only the two states that change what the owner should do.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** background/scheduled model for polling and state comparison; realtime tier only to render the final alert if the owner asks for details
- **latency:** poll every 30–60 minutes while active; alert within one polling interval; stop automatically after delivered or 72 hours of no change
- **cost:** about $0.002–$0.01 per day if the page exposes structured status; model cost is avoidable with deterministic status extraction and only one short generation on change
- **security:** The tracking number and status are sensitive logistics metadata. Keep it local to the browser session and relay job, redact the full number from logs, and require explicit opt-in per tracking page. Never click delivery-management or account actions.
- **missing:** A browser page-watch job that can re-open a saved public URL/session, extract a named status field, diff it, and terminate on a predicate; A relay scheduler that can push a compact alert into the already-shipped pendant inbox with expiry and deduplication

### "“Run the pendant audio diagnostic on the USB-connected bench, compare it with the acceptance limits, write a dated report, and tell me whether the device is safe to use for a call.”"
- **useful because:** The pendant and ESP32 bridge are physically connected right now, and the diagnostic fixture is already accepted. This would turn raw UART counters into a decision the owner can trust before wearing it: it catches codec regressions, packet loss, clipping, and underruns without recording private speech.
- **path:** mac-planner → mac-terminal → relay-realtime → pendant
- **model tier:** background model for interpreting the bounded diagnostic output; deterministic checks decide pass/fail, with realtime only for the final spoken result
- **latency:** under 90 seconds for fixture execution and report; abort on missing serial output or a stalled device and preserve the partial log
- **cost:** under $0.02 per run; almost all latency is the on-device fixture and serial capture, not inference
- **security:** The fixture must use synthetic audio only and never enable the microphone capture path. Store the log under ~/AI-Pendant-Workspace with counters and firmware hash, redact serial identifiers from any cloud summary, and do not flash or reset firmware automatically.
- **missing:** A bounded mac-terminal procedure that can invoke the existing serial diagnostic trigger and read only its framed output from /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A report validator encoding the measured thresholds (alias rejection ≥60 dB, codec under one core, mic drops about 1%, tx_starved near zero, zero preamble samples); A durable relay-to-pendant result handoff for a pass/fail alert

### "“I just hit the pendant button because something went wrong. Package the last minute of device diagnostics, the active browser URL, and a timestamp into a private bug report draft, then read me the short diagnosis.”"
- **useful because:** The owner explicitly wants a pendant that files its own bug reports. A button press is the only reliable signal available on this hardware; pairing it with the Mac's current browser context and bounded UART diagnostics makes the report useful instead of just an unlabeled timestamp. It works even when the LTE device is not registered because the pendant is USB-connected to the Mac today.
- **path:** pendant → mac-planner → mac-terminal → browser-extension → relay-realtime
- **model tier:** background model for correlating the bounded log and writing a concise diagnosis; deterministic collection and redaction first, realtime only for the spoken acknowledgement
- **latency:** acknowledge the button locally immediately; produce a draft within 30 seconds; if serial collection fails, save a partial packet and say exactly which source was unavailable
- **cost:** about $0.01–$0.05 per incident, dominated by log summarization; collection and markdown generation are local
- **security:** Treat the active URL and diagnostic data as private. Capture only the URL/title, not page body or keystrokes; exclude cookies, query parameters matching secrets, and microphone PCM. Write a draft under ~/AI-Pendant-Workspace and never file externally or send mail without a separate owner action.
- **missing:** A bridge event correlator joining offline_moment_bookmark timestamps to the Mac agent's observation and serial-diagnostic windows; A bounded serial-log collector for the two currently connected USB devices, with framing and timeout handling; A redaction rule for URLs and a local issue-draft schema

### "“Turn what I’m researching in the browser into a reproducible evidence packet: preserve the exact source URLs and access times, capture the relevant quoted passages, save a local Markdown report with citations, and give me a short spoken conclusion on the pendant.”"
- **useful because:** A normal summary loses the trail back to evidence. This would let the owner return days later—or hand the work to another node—and verify exactly which pages supported each claim, while keeping the packet local and avoiding publication or account actions.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** background model for passage selection, claim-to-source alignment, and concise synthesis; deterministic URL/time capture and local file creation should happen without the expensive realtime tier
- **latency:** under 45 seconds for up to six already-open pages; save partial results immediately if a page fails or changes
- **cost:** approximately $0.03–$0.12 per packet, dominated by quoted-page text sent for alignment; metadata capture and Markdown generation are local
- **security:** Page text, URLs, and authenticated content can be sensitive. Default to local storage under ~/AI-Pendant-Workspace, redact cookies/query tokens and account identifiers, retain only selected passages rather than full pages, and never share or upload the packet without an explicit later action.
- **missing:** A browser snapshot primitive that returns stable URL, title, access time, selected passage, and a content hash for each tab; A citation/evidence packet schema with claim-to-passage links and source freshness metadata; A pendant playback handoff that can speak the conclusion while leaving the full report on the Mac

### "“When a browser task pauses for an approval or one-time code on my iPhone, tell me exactly what is waiting, guide me through the approval on the mirrored phone, and resume the same browser task without reading my unrelated notifications.”"
- **useful because:** Authenticated workflows often fail at the boundary between the browser and the real phone. This would close that boundary while constraining phone access to the visible approval screen, so the owner does not have to rediscover the browser state or expose unrelated private messages.
- **path:** browser-extension → mac-planner → ios-control → relay-realtime → pendant
- **model tier:** realtime tier for the brief spoken interaction and screen-target identification; background tier for retry bookkeeping and task continuation
- **latency:** detect a blocked step within 5 seconds, guide the owner in under 30 seconds, and resume the original browser plan immediately after approval
- **cost:** roughly $0.01–$0.05 per interruption; vision/UI inspection dominates, with little text generation
- **security:** Never copy OTPs into relay logs or expose unrelated phone content. Scope inspection to the active approval app/window, keep the owner in control of the actual approval, and expire the continuation token after one use. Purchases, messages, and destructive operations still require the owner's existing policy.
- **missing:** A semantic iPhone Mirroring surface that can identify only the active approval prompt and accept bounded UI actions; A browser-plan continuation token that freezes the pending step and resumes it exactly once; Cross-surface redaction preventing OTPs and notification text from entering ordinary model context


## What it asked for

_Nothing._
