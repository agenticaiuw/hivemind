# Harness derivation — mac-planner — round 173

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-live-state-2026-08-08-round173** — Mac bridge is online; AI Pendant Agent has Accessibility and Screen Recording trusted, synthesized input verified, and foreground app is Claude. Browser sessions expose three tabs, including an authenticated OpenAI billing URL. USB-connected pendant is still not represented by any resolved serial tool.
  - evidence: discover:devices and mac_readonly_inspect foreground_app response at 2026-08-08T01:21:40Z

## Capabilities it proposed

### "When I press the bookmark button during a call, save exactly what I was working on as a dated handoff note: the active Mac app, current browser tab(s), call timestamp and audio health, then tell me on the pendant when it is safely filed."
- **useful because:** A physical press is faster and more reliable than remembering a phrase. It turns a fleeting thought into a durable, privacy-redacted handoff that combines evidence no single node can see: the pendant knows the moment, the relay knows the call, and the Mac/browser know what the owner was looking at.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** background for assembling and redacting the note; realtime only for the one-sentence acknowledgement
- **latency:** Acknowledge locally immediately; file the note within 5 seconds when Mac and browser are online, otherwise queue until they return.
- **cost:** About $0.005–$0.02 per invocation; most cost is optional summarization, not the deterministic context collection.
- **security:** Default to app name, tab titles/URLs, timestamps and QoS counters with page bodies and microphone audio excluded. The owner must explicitly enable body capture. The note is a local workspace artifact; browser credentials never leave the browser.
- **missing:** A relay event consumer that binds offline_moment_bookmark to the active call id; A Mac-side context collector that returns semantic foreground/document identity (current inspect only gives coarse observe data); A browser command to return the active tab title and URL with redaction policy; A small durable bookmark-to-note job and receipt

### "Run a pendant hardware check and leave me a plain-English report in my AI-Pendant-Workspace, including whether the microphone, Opus uplink, modem delivery, downlink decode and speaker path all passed."
- **useful because:** The owner currently has to interpret UART counters and guess which half of a voice call failed. A deliberate test produces a report that is useful before a real call, and it combines the pendant's synthetic fixture with relay telemetry and a Mac artifact.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** background/cheap model for report wording; no expensive realtime model is needed
- **latency:** Start on demand, show progress within 1 second, and write the report within 30 seconds. Never run implicitly during a live call.
- **cost:** Under $0.01 per run; the fixture and counters are local, and only the final report needs model text.
- **security:** The diagnostic fixture must remain synthetic and must never include microphone content. Write only inside ~/AI-Pendant-Workspace and include raw counters plus a timestamp so the prose is auditable. Starting the test should require an explicit button/command because it interrupts audio.
- **missing:** A USB-serial control/read path for this Mac (the physical pendant is connected but mac_serial_exchange is not available); Relay ingestion and correlation for audio_path_diagnostic_fixture results; A report writer that atomically stages raw JSON and Markdown together

### "When I say 'save this screen' or press the pendant bookmark button, create a short Markdown source card containing the current browser page, the Mac app in front, the exact time, and my optional spoken note, without changing focus or clicking anything."
- **useful because:** This is a zero-friction research and debugging capture: the pendant supplies an intentional, timestamped trigger, while the browser and Mac supply authenticated context. It prevents the common failure of trying to reconstruct which tab or window mattered later.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** background model only when an optional spoken note needs transcription/summarization; deterministic capture otherwise
- **latency:** Local acknowledgement immediately; source card appears in under 3 seconds online and is queued offline.
- **cost:** $0.00 for metadata-only cards; roughly $0.003–$0.01 if the optional note is summarized.
- **security:** Never capture page body, screenshots, passwords, or cookies by default. Store URL/title and app identity in the workspace with a visible sensitivity label. Any spoken note must pass the existing redaction layer before persistence.
- **missing:** A server intent that accepts a bookmark event plus optional note and requests read-only context from both Mac and browser; Semantic window/document identity beyond the current coarse /observe response; A local card writer with deduplication for repeated button events

### "While the pendant is plugged into my Mac over USB, use the Mac as a temporary relay link so I can test live calls, bookmarks, and alert delivery even when LTE-M is unregistered; automatically switch back to cellular when it becomes available."
- **useful because:** This turns hardware that is physically usable today into a real wearable instead of a disconnected dev board. It enables end-to-end testing and daily use in the current dead zone, with no phone hotspot or manual flashing.
- **path:** pendant → mac-planner → relay → dashboard
- **model tier:** No model for transport; realtime only for the normal call
- **latency:** USB frames should add under 100 ms one-way; cellular remains preferred whenever registered, with reconnect transition under 5 seconds.
- **cost:** Negligible per invocation; it is a local serial/WebSocket bridge. Model cost is only normal conversation traffic.
- **security:** Bind the bridge to localhost and the authenticated Mac agent, never expose the serial port to LAN. Show a clear LED/voice transport status. Do not duplicate audio or bookmarks after switching transports; sequence numbers and acknowledgements must make handover idempotent.
- **missing:** A Mac serial exchange capability for /dev/cu.usbmodem00096003658* and the ESP32 bridge port; Relay transport adapter accepting framed pendant packets from the Mac bridge; Pendant link-manager state for USB-online versus LTE-registered; A tested handover protocol with packet sequence and acknowledgement persistence

### "After I ask the system to change something on my Mac, give me a one-sentence spoken receipt on the pendant naming what changed and where; if the job is undoable, let my next button press undo that exact job."
- **useful because:** The owner should not have to look at the Mac to know whether a command finished. A spoken receipt closes the loop across server planning, Mac execution and wearable interaction, while retaining a precise undo target instead of guessing what 'undo' means.
- **path:** relay → mac-planner → pendant → dashboard
- **model tier:** Realtime for a short receipt only; use templated text where possible and a cheaper model for unusual multi-step summaries
- **latency:** Speak completion or failure within 2 seconds of the Mac receipt. The undo action must be dispatched within 1 second of the button event.
- **cost:** Usually under $0.002 per receipt with templates; normal generated audio dominates when not templated.
- **security:** Do not speak file contents, email bodies, or secrets; speak resource names and operation status only. Undo must be scoped to the latest acknowledged job and expire after a short TTL. Destructive operations still follow the owner's explicit confirmation preference.
- **missing:** A relay subscription that turns Mac job receipts into pendant downlink messages; A firmware button state for 'undo latest receipt' that does not conflict with recording/bookmark semantics; A typed undo eligibility field in receipts (current receipts cover only some actions); TTS/audio queue priority so a receipt cannot interrupt an in-progress agent reply

### "If a live call fails or audio quality drops, automatically run the synthetic pendant fixture over the USB-connected Mac, correlate its counters with the failed call, and leave one actionable diagnosis instead of asking me to reproduce it."
- **useful because:** The system can distinguish modem loss, uplink starvation, decode CPU overload, and speaker-path failure without recording the owner. It converts a frustrating intermittent failure into a report an engineer—or the next automated repair—can act on.
- **path:** pendant → mac-planner → relay → dashboard
- **model tier:** Cheap background classifier over counters; realtime model is not needed
- **latency:** Detect degradation during the call; run the fixture only after hangup or explicit consent, and publish a diagnosis within 45 seconds.
- **cost:** Under $0.01 per incident; synthetic counters are tiny and classification is the only model work.
- **security:** Synthetic audio only, no microphone persistence. Include raw evidence and confidence, and never silently reset firmware or alter audio profiles based on a low-confidence diagnosis.
- **missing:** Reliable USB serial trigger/read for the pendant fixture; A call-end hook linking /pipeline telemetry to a fixture run; A diagnostic classifier with known thresholds from the acceptance target; An incident artifact writer with deduplication and retention controls

### "Before carrying out a voice command on my Mac, tell me if the thing I named does not match the actual browser tab, app window, file, or selected text that would be changed, and let me correct the target from the pendant before anything runs."
- **useful because:** This catches the most dangerous class of silent computer-use error: the plan is reasonable but aimed at the wrong authenticated tab or document. It joins spoken intent, live Mac context, and browser session identity; none of those nodes can establish the mismatch alone.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Realtime only for ambiguous referent resolution; deterministic matching handles exact app, URL, file, and selection matches.
- **latency:** Resolve and report a mismatch within 1 second before execution; never delay an unambiguous low-risk action.
- **cost:** Usually below $0.005 per command; model cost occurs only for ambiguous references.
- **security:** Do not transmit page bodies or secrets by default. Redact account identifiers and selected text unless the owner explicitly asks to use them. A mismatch report must not itself execute or focus a tab.
- **missing:** Semantic Mac window/document/selection inspection beyond coarse /observe; A browser response containing stable tab identity and origin at plan time; A referent-matching stage in the relay-to-Mac handoff; A pendant interaction for correcting or accepting the proposed target

### "Give me a daily 'what changed while I was away' report that compares the last acknowledged state of my projects, browser work, calendar, and pendant bookmarks, then speaks only genuinely new changes and lets me open the cited source on the Mac."
- **useful because:** Today the system can collect several surfaces, but it cannot establish a durable acknowledged baseline and distinguish new information from repeatedly seen information. This would replace noisy briefings with a compact, evidence-linked delta across the whole hive.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Background model for cross-source deduplication and ranking; realtime only to answer follow-up questions.
- **latency:** Generate overnight or on demand in under 60 seconds; speak a three-sentence summary immediately and leave full citations on the Mac.
- **cost:** Roughly $0.01–$0.05 per daily run depending on source volume; storage and context selection dominate, not audio.
- **security:** Persist hashes and source metadata rather than full private content where possible. Mail and authenticated pages require redaction and per-source retention settings. Opening a cited source must preserve browser session affinity and never send credentials to the relay.
- **missing:** A durable per-source acknowledged watermark/summary store; Cross-surface change detection for Calendar/Mail/browser/projects/pendant events; Citation objects that can reopen the exact authenticated browser tab or Mac artifact; Owner-configurable retention and redaction policy


## Changes it proposed to its own stack

### `integration` — Build an end-to-end intent provenance record: every spoken request gets a stable intent id carried through relay planning, browser commands, Mac jobs, pendant acknowledgements, and final receipts; expose a compact timeline and evidence links on the dashboard and allow the owner to ask the pendant what happened to that intent.
- **owner gets:** When something goes wrong or appears not to happen, the owner can ask one question and get the exact plan, target, action, result, and failure point instead of repeating the command or searching logs.
- effort: High: protocol fields across relay, browser bridge, Mac jobs, audio events, and dashboard; moderate storage and UI work.  ·  risk: Identifiers could accidentally expose sensitive URLs or file names; redact evidence at presentation time and retain raw details only under local policy. Missing links must be reported as unknown, never inferred.
- cost: Negligible per request for IDs and metadata; modest storage growth. No additional model call for ordinary timelines.  ·  latency: No meaningful live-path cost; timeline assembly is asynchronous. A spoken status lookup should complete within 2 seconds.
- security: Improves auditability but creates a sensitive activity graph. Encrypt or locally retain detailed evidence, apply TTLs, and avoid including page bodies, mail contents, or audio by default.
- depends on: A shared intent-id field in /plan, /execute, browser commands, and pipeline events; A relay joiner for Mac receipts and pendant acknowledgements; A redacted timeline endpoint and dashboard view; Owner-selected retention policy


## What it asked for

_Nothing._
