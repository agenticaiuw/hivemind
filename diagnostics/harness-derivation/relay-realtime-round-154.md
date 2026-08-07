# Harness derivation — relay-realtime — round 154

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If you can’t reach my Mac, still check a public page and read me the important parts."
- **useful because:** The owner gets help even when the Mac is offline, and the relay can use a cheaper non-interactive browse path for public information.
- **path:** relay → browser
- **model tier:** non-realtime for browsing and extraction; realtime only for speaking results
- **latency:** A few seconds for fetch and extraction; speech should start as soon as a summary is ready.
- **cost:** Low per request; dominated by page load and extraction, not realtime tokens.
- **security:** Only public pages; avoid authenticated sessions and never submit forms. Log URLs and extraction results carefully to avoid collecting sensitive content by accident.
- **missing:** server_browser_actions implementation; policy for safe actions in the sandbox; observability for what was fetched/extracted

### "Tell me what happened to the thing I asked you to do."
- **useful because:** This is a daily-driver feature: the owner gets a clear status update without waking the Mac or repeating themselves.
- **path:** relay → mac-bridge
- **model tier:** realtime only; it’s a short status readout sized for speech
- **latency:** Sub-second to a couple of seconds; no Mac round trip required.
- **cost:** Very low; dominated by a small status payload and speech tokens.
- **security:** Status may include filenames or snippets; keep responses minimal and avoid expanding details beyond what the status tool returns.
- **missing:** relay_job_status implementation; consistent job labeling and references across relay and Mac

### "Help me handle this across my open tabs, but stop before submitting anything and show me exactly what will change."
- **useful because:** This becomes the system’s most useful “do work with me” mode: gather context across devices, prepare a reversible plan, and let the owner approve.
- **path:** relay → mac-planner → browser
- **model tier:** planner model for multi-step work; realtime only for confirmation and narration
- **latency:** Seconds to plan, longer to gather data; owner gets incremental updates.
- **cost:** Medium; dominated by planning and browsing actions, not relay speech.
- **security:** Authenticated data is sensitive. Must preserve tab/session affinity, record provenance, and require explicit approval before irreversible steps.
- **missing:** durable browser job runner; reliable command queue with typed results; approval UI for review; relay intent routing implementation

### "“Where are my keys / wallet / charger?” — use the wearable and my Mac to find the physical object and tell me where it is."
- **useful because:** This would solve a uniquely everyday problem no cloud-only assistant can solve: the pendant supplies the request and proximity context while the Mac’s camera/vision searches the owner’s actual rooms. It should return a confidence-ranked location and ask for another scan when uncertain.
- **path:** pendant → relay → mac-vision → mac-planner
- **model tier:** Realtime relay handles the short spoken request; a cheaper background vision model on the Mac indexes recent camera frames and a slower planner fuses sightings. Do not spend the low-latency model on image search.
- **latency:** First spoken acknowledgement under 500 ms; first candidate location within 10 seconds; additional room scans can take up to 30 seconds.
- **cost:** Roughly $0.01–$0.08 per search, dominated by vision-frame analysis; local camera inference can reduce API cost to near zero.
- **security:** Room imagery and object locations leave the Mac only if explicitly uploaded for analysis. Camera activation must be visibly indicated and automatically expire; never silently record continuously. Spoken results can reveal location to bystanders.
- **missing:** Mac camera capture and room-scan API; short-lived local visual memory keyed by object and timestamp; pendant-to-relay event delivery and spoken result push; object enrollment/disambiguation UI

### "“Handle this customer-service problem for me” — let the system inspect the authenticated browser session, conduct the support chat or call, and bring me back only when a judgment or identity decision is genuinely required."
- **useful because:** The owner currently has to stay at the keyboard for the tedious middle of refunds, cancellations, delivery disputes, and appointment changes. This makes the hive a real proxy: the pendant starts the job, the browser uses sessions the relay cannot possess, and the Mac completes non-browser steps.
- **path:** pendant → relay → browser-extension → browser → mac-planner → mac-vision
- **model tier:** Use a background planner for the multi-step workflow and a small realtime model only for clarifying the owner’s spoken constraints. Use browser vision/extraction for page state; resume from a durable checkpoint after every external response.
- **latency:** Acknowledge immediately, then work asynchronously for minutes. If a live support chat needs owner input, interrupt within 2 seconds with the exact question and current offer.
- **cost:** $0.05–$0.40 per case, dominated by browser-page interpretation and long support transcripts; most navigation should use deterministic browser actions.
- **security:** Authenticated page contents and personal data must stay in the browser/session boundary. Never invent consent, accept legal terms, expose payment credentials, or finalize irreversible cancellation/refund choices without an explicit spoken decision. Retain a complete transcript and receipt.
- **missing:** durable multi-step browser workflow runner with checkpoint/resume; browser chat/call interaction adapter; a narrow spoken approval/clarification interrupt channel; cross-surface action receipts with page citations

### "“Keep me safe when I’m overloaded” — notice a rapidly escalating conversation or distress in nearby audio, quietly tell me what is happening through the pendant, and offer one-tap exit actions such as calling a trusted contact or navigating home."
- **useful because:** A worn device is present when the Mac is not. Combining local audio cues, the owner’s spoken response, relay reasoning, and Mac/browser execution could provide a practical safety net rather than another productivity assistant. It should assist, not diagnose or autonomously contact anyone on ambiguous evidence.
- **path:** pendant → audio bridge → relay → mac-planner → browser
- **model tier:** Run an always-on low-power local acoustic classifier for trigger features; send only an explicit distress segment or feature summary to the relay. Realtime model interprets the owner’s whispered response; background models prepare route/contact options.
- **latency:** Local trigger under 300 ms; discreet haptic/audio prompt under 1 second; outbound call/navigation preparation under 5 seconds after the owner’s confirmation.
- **cost:** <$0.01 for ordinary monitoring if classification is local; $0.02–$0.10 when an event is escalated, dominated by transcription and reasoning.
- **security:** This is extremely sensitive ambient audio. Default to feature-only local processing, no recording, a physical LED indication, and a hard local disable gesture. Do not infer criminality or mental state, and require confirmation before contacting others except for a separately configured emergency mode.
- **missing:** on-device acoustic escalation classifier; private haptic/earpiece feedback path; explicit emergency contacts and confirmation policy; location source and navigation/calling integration; event push that survives a dropped Mac link


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities: wearable-assisted physical object finding using Mac vision, an authenticated customer-service proxy that resumes across browser/Mac and interrupts only for real judgments, and a local-first overload/safety assistant with discreet pendant feedback. The strongest near-term value is the customer-service proxy; the most unique capability is physical-world finding.

**Biggest unknown:** Whether the owner has an acceptable camera/privacy setup for room scanning and whether a trusted-contact/emergency policy can be configured for the safety capability. The recorded proposals explicitly list the missing pieces rather than assuming today’s wiring provides them.

