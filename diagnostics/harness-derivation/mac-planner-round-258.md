# Harness derivation — mac-planner — round 258

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live device availability** — Safari has 3 tabs and is online; home MacBook bridge is online; the cloudflare-contract-test mobile surface is offline. The pendant is not listed as a registered live device, so cross-node proposals must currently use USB bench mode rather than LTE.
  - evidence: discover(devices) returned Safari on MacIntel online, home-macbook-bridge online, cloudflare-contract-test offline; no pendant device entry.

## Capabilities it proposed

### "Before I put it on, validate the pendant end to end and leave me a short spoken pass/fail report with the exact failing stage if anything is wrong."
- **useful because:** Turns today's physically connected but unregistered hardware into a dependable pre-flight check: radio/audio/codec failures are found before a real conversation, and the owner gets a useful answer rather than UART logs.
- **path:** pendant → mac-planner → relay-realtime → dashboard
- **model tier:** background for fixture analysis and report; realtime only if the owner asks follow-up by voice
- **latency:** 30-90 seconds for the fixture and report; no microphone content is collected
- **cost:** Usually <$0.01 in API work; dominated by one bounded diagnostic run and optional speech synthesis
- **security:** USB UART is used only in explicit bench mode; synthetic fixture data and counters leave the Mac, never microphone PCM. Report must redact serial paths and tokens.
- **missing:** A small authenticated UART command/receipt protocol that can arm audio_path_diagnostic_fixture and return a completion marker; A Mac bounded UART-read action with exit code, timeout, and captured-log hash; A relay reducer that maps fixture counters to the shipped acceptance thresholds and creates an audio report

### "When I say 'make this reproducible', collect the current pendant QoS evidence and the Mac/browser state relevant to the incident, then create one redacted handoff packet I can attach to a bug."
- **useful because:** A dropped or distorted conversation currently produces scattered clues. This makes a one-sentence spoken request yield a timestamped, reproducible incident packet spanning the worn device, relay, active browser session, and Mac without copying private audio.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background; use realtime only to acknowledge capture and report completion
- **latency:** Under 20 seconds for state capture; packet assembly can finish asynchronously
- **cost:** <$0.02 per packet; storage and browser/Mac inspection dominate, not model inference
- **security:** Default to counters, timestamps, app/tab titles and hashes, not audio, page bodies, cookies, clipboard, or secrets. Require explicit owner phrase before including a screenshot or body text. Keep the packet local until the owner shares it.
- **missing:** A single incident correlation ID shared by pendant QoS frames, relay pipeline events, Mac receipts, and browser command results; A redaction-aware collector for browser tabs and Mac observations with per-field inclusion; An export/share action that preserves the packet's hashes and provenance

### "After I press the bookmark button during a real conversation, give me a later 'resume card' that says what I was doing, what I meant to remember, and the next concrete step—without saving raw audio."
- **useful because:** The button already records a durable moment, but a timestamp alone still makes the owner reconstruct context manually. Joining the bookmark with the relay transcript, calendar window, active browser tab, and Mac workspace makes it useful as a true interruption recovery point.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background synthesis after the link returns; one short realtime acknowledgment on bookmark only
- **latency:** Bookmark acknowledgment immediate; resume card within 30 seconds after connectivity or the relevant app state becomes available
- **cost:** <$0.03 per card; transcription/context synthesis dominates, and no call is made when the bookmark has no associated speech
- **security:** Raw audio remains on the existing voice path and is not copied into the card. Browser/Mac context is limited to the active tab/app and owner-selected workspace; redact URLs query strings and secrets. Cards expire unless pinned.
- **missing:** A server-side joiner that correlates offline_moment_bookmark with the nearest transcript segment and Mac/browser observation by monotonic time; A semantic, redacted active-document summary (the existing browser-tabs/UI observations do not provide selected text or document identity); A durable card store with expiry and a pendant inbox item containing only the short summary

### "During a call, warn me only when audio quality has materially degraded, and after the call tell me in one sentence whether it recovered or needs a repair—never dump counters on me."
- **useful because:** The owner experiences packet loss as missing words, not as tx_starved or underrun counters. This turns the existing QoS telemetry into an actionable, low-noise experience and separates transient radio trouble from a repeatable hardware fault.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** deterministic thresholding and a cheap background summarizer; realtime model only for an immediate spoken warning
- **latency:** Warning within 2 seconds of a sustained threshold breach; post-call verdict within 15 seconds
- **cost:** Pennies per call at most; most decisions are local thresholding, with one short summary when state changes
- **security:** Transmit compact counters and state transitions, not audio or transcript. Do not expose network identifiers in the owner's spoken warning. Persist only aggregate session statistics unless the owner explicitly requests a diagnostic packet.
- **missing:** A relay policy that converts duplex_audio_congestion_guard frames into hysteretic owner-facing states (healthy, degraded, recovered, investigate); A pendant notification path that can queue one concise warning without competing with staged reply playback; A post-call reducer that compares this call with the last few sessions and optionally hands a repeatable fault to the Mac bench diagnostic

### "Tell me when my calendar, email, and browser commitments conflict, explain the collision in one sentence, and suggest the smallest change that resolves it."
- **useful because:** The owner currently has to notice contradictions across separate systems himself—double-booked meetings, a promised deadline that conflicts with travel, or a browser task that cannot finish before an appointment. This would catch conflicts before they become social or practical failures.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background rules and a cheap planner; realtime only for the short spoken alert
- **latency:** Recompute after new mail/calendar events and at most every 15 minutes; alert within 30 seconds of a high-confidence collision
- **cost:** <$0.02 per scan; calendar/mail extraction and browser commitment classification dominate
- **security:** Keep analysis on the owner's relay/Mac where possible. Do not send mail or alter events automatically. Spoken alerts must omit private attendees and message bodies unless requested.
- **missing:** A commitment extractor that represents source, confidence, due time, location, and flexibility uniformly across Calendar, Mail, and browser pages; A conflict-ranking policy distinguishing a real obligation from an informational email or speculative browser task; A cross-surface proposal object that can offer rescheduling, reminder, or draft-only remedies without mutating anything

### "When I ask 'why do you think that?', answer with the evidence trail across my Mac, browser, and pendant, including what is certain, what is inferred, and what may be stale."
- **useful because:** A personal agent that acts across surfaces must be able to earn trust. Today a spoken answer can be useful but opaque; provenance lets the owner catch stale calendar data, mistaken browser interpretation, or an incorrect memory before acting on it.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background provenance assembly with realtime verbalization; use a cheaper model for source grouping and the expensive tier only for ambiguous synthesis
- **latency:** Under 5 seconds for a short answer; deeper evidence view may load asynchronously
- **cost:** <$0.02 for common questions; cost scales with the number of source records, not audio length
- **security:** Spoken output should summarize sensitive sources rather than quote them by default. Every source needs sensitivity labels and revocation/expiry handling. Never expose hidden credentials or full private message bodies merely because they support an inference.
- **missing:** A provenance graph linking claims to source spans, timestamps, surface, and freshness; A user-facing certainty/staleness format that works both as one spoken sentence and as a dashboard expansion; A redaction-aware evidence resolver for Mac and browser results

### "Send the page I am looking at to my pendant and Mac as a compact handoff, preserving the exact title, URL, selected passage, and my spoken note, so I can continue without searching for it again."
- **useful because:** The owner can currently look at a page in a browser or speak to the pendant, but the transition between those surfaces loses the working context. A deliberate handoff would make the wearable useful while walking and the Mac useful when returning to the desk, without transferring browser credentials.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic capture and routing; background summarization only when the owner asks for a compact version
- **latency:** Capture and pendant acknowledgment within 2 seconds; Mac restoration within 10 seconds
- **cost:** Near-zero model cost for raw handoff; <$0.01 when summarization is requested
- **security:** Transfer only the active URL, title, explicitly selected text, and spoken note. Strip query parameters by default, never copy cookies or session state, and expire unclaimed handoffs.
- **missing:** Browser extension support for selected-text capture and a stable page fingerprint; A pendant inbox payload type for a signed page handoff, distinct from an alert; A Mac restore action that opens the page and optionally writes the note into the owner's workspace without silently submitting forms


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities: proactive cross-source commitment conflict detection, evidence-backed 'why do you think that?' answers with certainty and freshness, and an explicit browser-to-pendant/Mac handoff preserving selected passage and spoken note without credentials. Each names the missing cross-node primitives rather than pretending today's wiring is sufficient.

**Biggest unknown:** Whether the backlog already contains a materially identical provenance or browser-handoff proposal; the recorder accepted all three without a collision, so they were not rejected as restatements.

