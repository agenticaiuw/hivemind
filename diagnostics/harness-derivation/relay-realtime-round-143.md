# Harness derivation — relay-realtime — round 143

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If my Mac is asleep, tell me the status of the thing I asked you to do earlier."
- **useful because:** It turns the relay into a reliable voice status desk. The owner can ask from anywhere and get an accurate update without waking the Mac.
- **path:** relay → mac-bridge
- **model tier:** Realtime for the spoken response; no heavy planning.
- **latency:** Under a second if the relay has the job record; otherwise it should say it cannot find a record and suggest what to ask for next.
- **cost:** Very low. One relay job-status lookup dominates; no Mac round trip.
- **security:** Job summaries may include sensitive task names. Only read the owner’s own job records and speak the returned sentence verbatim to avoid accidental reinterpretation.
- **missing:** relay_job_status implementation (currently schema-only); a consistent job reference strategy for voice, including mapping vague references like "that" to a job record

### "Remember the last few things I asked and what you did, so I can say "do the same as before" or "check that"."
- **useful because:** It makes voice interaction feel natural and reduces repeated explanation. It also helps route vague references to the right job without guessing.
- **path:** relay → memory → mac-bridge
- **model tier:** Realtime for recognition and disambiguation; cheaper background tier for retention and indexing if needed.
- **latency:** Fast for recent references (under a second). For older history, a brief pause is acceptable while searching.
- **cost:** Low to moderate. Small context reads/writes dominate; avoid resending full history each turn.
- **security:** Conversation history can be sensitive. Store minimal summaries, keep retention short, and ensure only this owner’s data is accessible.
- **missing:** a relay-side conversational memory store with TTL and privacy controls; a job-reference index to map phrases like "that" to job IDs; policy around what gets stored and for how long

### "Listen for a wake phrase or button press, capture a short voice note when I’m away from my Mac, and sync it to my Mac as a reminder or draft when the link is available."
- **useful because:** This would be the single most useful everyday feature: the pendant becomes a trustworthy capture tool for thoughts and tasks in the moment, even offline.
- **path:** pendant → bridge → relay → mac-bridge
- **model tier:** Realtime for capture confirmation; slower tier on Mac for transcription, summarization, and reminder creation.
- **latency:** Capture must start instantly. Sync and transcription can happen later, but the owner should get a quick confirmation that the note is saved locally.
- **cost:** Low per note. Audio transfer and transcription dominate; keep recordings short and compressed.
- **security:** Voice can contain sensitive info. Encrypt at rest on-device, encrypt in transit, and avoid uploading until needed.
- **missing:** device skill: offline voice note buffer with local persistence and retry sync; bridge route to transfer buffered audio to relay/Mac; scheduler or reconnect-driven sync mechanism (since no scheduler exists today); mac-side pipeline to transcribe and create reminders/drafts

### "“When I press the pendant button, tell me whether I am actually near my Mac, and only then carry out the desktop task I just spoke; if I am away, queue it for when I return and tell me which mode you chose.”"
- **useful because:** The owner currently cannot make the worn pendant adapt safely to physical presence. This joins a real USB-connected pendant, Mac presence evidence, relay conversation, and downstream Mac/browser action into one behavior: immediate execution when home, durable intent handoff when away, with an audible explanation rather than a silent failure.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension
- **model tier:** Realtime relay for the short spoken decision; a cheaper background classifier on the Mac/relay for presence evidence and intent normalization; gpt-5.6-luna only when the queued task needs planning.
- **latency:** Button acknowledgement under 300 ms; presence verdict under 2 s; task execution may be asynchronous and must produce a later spoken or LED result.
- **cost:** About $0.001–$0.01 per interaction depending on whether planning is needed; dominant cost is the realtime turn, not presence checks.
- **security:** USB serial presence and microphone-derived proximity signals leave the device/relay only as coarse state, never raw audio. A false 'home' verdict could run a desktop mutation, so the system must be explicit about uncertainty and default to queueing rather than pretending the Mac is reachable.
- **missing:** A relay endpoint that receives pendant button/audio state and correlates it with the Mac's live heartbeat; A signed, short-lived proximity proof between /dev/cu.usbmodem00096003658* pendant and the Mac; A durable intent queue with reconnect delivery and spoken/LED completion notices; A presence-aware routing policy distinct from the existing action receipts

### "“Before you act, notice when the Mac, browser, and my remembered preferences disagree; ask me one concise question on the pendant, then use my answer as the authoritative correction everywhere.”"
- **useful because:** Today the owner can receive a confident but wrong result when surfaces disagree (for example, timezone or browser frame access). A spoken contradiction-resolution loop would turn hidden cross-agent inconsistencies into a single answer the owner can correct, instead of forcing them to inspect logs or repeat themselves.
- **path:** pendant → relay-realtime → faculty-perception → faculty-judgement → mac-planner → browser-extension
- **model tier:** Cheap background perception compares typed evidence and detects contradictions; realtime is reserved for the one clarification question and confirmation; no expensive planning unless the corrected fact changes the task.
- **latency:** Detect during normal task completion; ask within 1 s of detecting a material contradiction; resume after one answer within 3 s.
- **cost:** Roughly $0.001–$0.005 per task when a contradiction exists; most tasks use only local comparison and cost nothing beyond the normal turn.
- **security:** The system must distinguish observed facts from owner assertions and retain provenance. Never silently overwrite a secret or account setting; store the correction as a scoped, versioned preference and announce what scope changed.
- **missing:** A typed evidence/provenance envelope shared by relay, Mac, browser, and faculty agents; A durable owner-correction store with scope and expiry (session, device, or global); A low-latency spoken clarification/answer exchange that can interrupt a pending downstream job; A contradiction severity policy so harmless differences do not annoy the owner

### "“Let me say a private command into the pendant while I am away from my Mac; strip accidental secrets locally, execute only the intended safe portion through the relay, and let me review exactly what was heard and removed later.”"
- **useful because:** The owner cannot currently use the wearable as a trustworthy private control surface: raw voice may traverse the cloud, and there is no owner-visible account of redaction. This would make the pendant practical in public or around coworkers while still allowing useful Mac/browser delegation.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** A tiny local firmware/bridge detector handles wake word, obvious credential patterns, and audio clipping; realtime handles intent extraction from the sanitized transcript; background storage builds the review record.
- **latency:** Local sanitization must add under 150 ms; spoken acknowledgement under 1.5 s; review record available immediately after the turn.
- **cost:** Approximately $0.002–$0.02 per command, dominated by realtime transcription/intent extraction; local filtering adds no API cost.
- **security:** Redaction must fail closed for detected passwords, one-time codes, payment numbers, and private names, while clearly marking uncertainty instead of claiming deletion. Raw audio should be discarded after local processing; the review log should contain hashes/labels and sanitized text, encrypted at rest.
- **missing:** Firmware or ESP32 bridge support for local VAD/pattern filtering before uplink; A relay ingestion route accepting sanitized audio/transcript plus redaction annotations; An encrypted, owner-queryable redaction ledger and dashboard view; Downstream agents must reject unsanitized payloads when this privacy mode is active

### "“Learn my voice once, then ignore commands spoken by other people near the pendant; if you are unsure, ask me to press the button and repeat instead of sending anything to my Mac.”"
- **useful because:** A worn microphone is exposed to coworkers, family, and media. Today any captured speech can become a trusted command. Voice identity plus a physical-button fallback gives the owner a practical boundary between conversation and control without requiring the Mac to be nearby.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Local DSP/embedding on the ESP32 or pendant for the first filter; realtime only handles accepted speech; a background model manages enrollment quality and drift.
- **latency:** Reject or accept locally within 250 ms of end-of-utterance; spoken uncertainty response within 1.5 s.
- **cost:** Near-zero API cost for rejected speech; approximately $0.001–$0.01 for accepted commands. Hardware-side inference dominates engineering cost, not token cost.
- **security:** Voice embeddings are biometric data and must be encrypted, revocable, and never sent with raw audio by default. Do not promise identity certainty; require the physical button for low-confidence or high-impact commands, while respecting the owner's no-gate policy for ordinary reversible actions.
- **missing:** Enrollment and revocation UX through the pendant and dashboard; On-device speaker-verification model within the available RAM/power budget; A signed confidence field consumed by relay routing and downstream agents; A policy for button-confirmed fallback that does not become a generic confirmation gate

### "“Keep separate work and personal lanes automatically: when I say ‘send this to work’ or ‘personal,’ route the request, browser session, memory, and spoken reply to that lane, and warn me if content is about to cross lanes.”"
- **useful because:** The owner cannot currently make the hive reliably respect a work/personal boundary. A worn front door is the only place that can classify an utterance before it fans out, while the browser and Mac are the only places that know which account/session is active. The result is fewer wrong-account searches, messages, and disclosures.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime extracts an explicit lane token or asks a short clarification only when absent; cheaper background policy checks compare destination account/session and memory labels.
- **latency:** Lane classification under 500 ms; cross-lane warning before dispatch, adding at most 1 s; ordinary same-lane commands remain immediate.
- **cost:** Under $0.005 per command on average; policy checks are local and the realtime turn is the main cost.
- **security:** Lane labels are not a substitute for account identity. The system must show which browser profile/account and memory scope will receive data, avoid copying raw private content into logs, and fail closed on an ambiguous cross-lane transfer while allowing the owner to explicitly override.
- **missing:** First-class lane labels on sessions, jobs, memory, browser tabs, and receipts; Browser profile/account identity reported to the relay; A cross-lane detector and owner-visible warning channel; A compact spoken syntax for setting and clearing the active lane

### "“After you finish a delegated task, tell me not just that it succeeded but show me the smallest evidence bundle: what changed, which account or tab was used, and how I can undo it, all summarized aloud and available on the dashboard.”"
- **useful because:** The owner currently has to trust a terse spoken completion or inspect raw jobs. A cross-surface evidence bundle would make the hive auditable while away from the Mac: the relay speaks the result, Mac/browser contribute receipts and identity, and the dashboard preserves the proof and undo path.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** No expensive model for collection: typed receipts and screenshots/URLs are assembled deterministically; realtime compresses only the final spoken summary; a slower model can explain conflicts on demand.
- **latency:** Initial spoken result within 2 s of job completion; evidence bundle can finish asynchronously, with a later short notification.
- **cost:** About $0.001–$0.005 for the spoken compression; storage and screenshot retention dominate, not API calls.
- **security:** Evidence may contain email, financial, or private page content. Redact secrets, preserve provenance and timestamps, encrypt retained artifacts, and expose deletion. Undo must reference the exact receipt/job rather than replaying an inferred opposite action.
- **missing:** A common receipt schema spanning Mac actions and browser actions, including account/tab identity and before/after evidence; Automatic artifact redaction and retention controls; A relay push/notification path to the pendant (not merely polling); Dashboard UI that links evidence to existing undo records


## Changes it proposed to its own stack

### `hardware` — Add a hardware secure element to the pendant and ESP32 bridge, with device-unique keys and signed challenge-response over both USB serial links. Bind each voice event, button event, and relay push to a short-lived sequence number; have the relay and Mac reject replayed or forged events and expose the verified device identity in the spoken receipt.
- **owner gets:** The owner gets confidence that a command came from their worn device and not a stale serial packet, a cloned bridge, or a misrouted browser session. This matters especially when the pendant can operate the Mac while the owner is away from it.
- effort: Moderate PCB respin and firmware/relay protocol work; provision keys during assembly, implement rotation/revocation, and add a recovery flow for a replaced pendant.  ·  risk: Key loss could strand the device, and clock/sequence bugs could reject legitimate commands. Provide monotonic counters, a device-repair enrollment path, and a clearly audible degraded-security state rather than silently accepting unsigned traffic.
- cost: Roughly $0.50–$2 per device plus provisioning/PCB work; negligible per-request API cost and low power draw during signing.  ·  latency: Typically under 20 ms per event for signing/verification, below conversational latency.
- security: Private keys never leave hardware; raw audio remains unaffected. The relay must not treat a valid device signature as authorization for every high-impact action—identity and action policy remain separate, with no surprise confirmation gate for ordinary reversible actions.
- depends on: A versioned signed-event envelope shared by pendant, bridge, relay, and Mac; Firmware monotonic-counter persistence across reboot; Relay and Mac verification plus device revocation/status endpoints


## What it asked for

_Nothing._
## Its own summary

Recorded five new owner-facing proposals: presence-aware pendant routing (execute near the Mac, defer while away), contradiction resolution across Mac/browser/memory, local privacy filtering with a review ledger, speaker verification for commands, work/personal lane separation, evidence bundles after delegated work, and a hardware secure element for signed pendant/bridge events. The recorder rejected the separate haptic proposal because an equivalent already exists in the backlog, so I did not rephrase it.

**Biggest unknown:** Which existing relay-side event/push and pendant serial routes are already implemented behind the unlisted /v1 surface; that determines whether the new capabilities are mostly wiring or require new firmware and relay endpoints.

