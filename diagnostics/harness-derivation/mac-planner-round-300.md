# Harness derivation — mac-planner — round 300

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-accessibility-live** — AI Pendant Agent now has Accessibility and Screen Recording trusted; synthesized input is verified reaching the screen, secure input is false, and the foreground app is Safari in the live observation.
  - evidence: mac_readonly_inspect operation=running_apps and foreground_app both invoked GET /observe at 2026-08-09T04:14:38–39Z; response accessibility.trusted=true, screenRecording=true, eventsPost=true, inputReachability.status=verified.

## Capabilities it proposed

### "“I’m at the bench. Verify the pendant’s whole audio path and tell me, in one sentence, whether it passed.”"
- **useful because:** This turns today’s physically connected but LTE-unregistered pendant into a dependable test instrument: the Mac triggers the firmware fixture over USB, captures bounded UART output, the relay parses measured counters against the shipped acceptance thresholds, and the result is spoken back instead of leaving the owner to interpret logs. It catches regressions in the exact path the owner cares about before they become a bad wearable call.
- **path:** pendant → mac-planner → relay → pendant
- **model tier:** Background/cheap model for log parsing and threshold comparison; realtime only for the final spoken verdict.
- **latency:** 30–90 seconds for fixture execution and parsing; final verdict under 2 seconds after the last UART line.
- **cost:** Usually <$0.01 per run; dominated by one short parsing/model call, not audio generation.
- **security:** UART logs can contain diagnostic identifiers and timestamps but must never include microphone PCM. Restrict commands to the existing fixed diagnostic fixture, redact serial numbers, and write a signed receipt. No owner confirmation for a non-destructive test.
- **missing:** A Mac-side bounded serial-test adapter that can write the fixture trigger and read until the fixture completion marker (the existing arbitrary run_shell is not a durable typed interface).; A parser/threshold profile versioned with scripts/audio-quality-probe.mjs, including alias rejection, decode/encode time, mic_drops, tx_starved, and peak/clipping.; A relay result route that attaches the receipt to the pendant firmware version and makes the one-sentence result available in the inbox when the pendant reconnects.

### "“Mark the start of this work session.” Later: “Close that session and tell me what changed.”"
- **useful because:** A short press on the worn device becomes a durable boundary around real work, not an unsearchable timestamp. At start, the Mac records the foreground app, browser tab set, active project, and calendar context; at stop, it records the same snapshot and the relay produces a compact before/after account: files touched, tabs opened, decisions captured as voice bookmarks, and unfinished items. The owner gets an honest work log without remembering to keep a timer or narrate every transition.
- **path:** pendant → relay → mac-planner → browser → pendant
- **model tier:** Cheap background model for diffing and summarizing; no realtime model except optional spoken confirmation.
- **latency:** Start/stop acknowledgement under 1 second; final diff 10–30 seconds after stop.
- **cost:** <$0.02/session, dominated by summarizing changed metadata and any owner-supplied bookmarks; raw snapshots stay local.
- **security:** This is intentionally sensitive: app names, URLs, filenames, and calendar context must be redacted by policy before relay upload. Keep raw snapshots on the Mac, send hashes and selected excerpts by default, and expose a local delete/retention period. Never infer productivity or transmit background audio.
- **missing:** A session-boundary correlator joining the pendant bookmark event ID to Mac/browser observations with monotonic timestamps and clock-skew correction.; Typed, read-only Mac snapshots for active project, foreground document, and browser tab metadata; current inspect is not sufficient for document identity and selected text.; A local diff/retention store and a spoken summary route; context-graph relations alone do not preserve an auditable session artifact.

### "“What am I looking at?” while I press the pendant’s bookmark button."
- **useful because:** The pendant becomes a physical, hands-free query key for the screen: the Mac identifies the active Safari page and readable region, the relay answers a question about that exact context, and the response comes back as audio. The owner does not have to wake the assistant, copy a URL, or describe which of several windows matters. This is the highest-value cross-node loop: a worn button supplies intent, the Mac supplies private authenticated screen context, and the relay supplies reasoning and speech.
- **path:** pendant → mac-planner → browser → relay → pendant
- **model tier:** Realtime model for a short answer after context capture; use a cheaper extraction model first to reduce the context sent to realtime.
- **latency:** Context capture under 500 ms; spoken first token within 3 seconds; hard cap of 10 seconds for a page answer.
- **cost:** $0.01–$0.05 per query depending on page length and realtime audio duration; extraction and redaction dominate input tokens.
- **security:** Authenticated page text must remain on the Mac until a deliberate query. Send only the relevant DOM/selection, redact password fields, hidden inputs, tokens, and URLs with query secrets, and show a distinctive LED/listening state. Never capture microphone audio for this trigger. Owner policy should allow browser reads but require confirmation for any resulting click or mutation.
- **missing:** A reliable pendant-to-Mac event bridge while the pendant is USB-attached today and LTE-attached later, with deduplication of the bookmark event.; A typed browser semantic-read operation returning active tab, selection, visible readable text, and page title with field-level redaction; browser status alone only reports URL/title.; A context packaging route that binds the captured page to a single request and expires it after the answer, plus an audio reply path to the pendant inbox/playback queue.

### "“Read the message on my iPhone, draft a reply saying I’ll handle it tomorrow, and let me approve it on the pendant before sending.”"
- **useful because:** The owner could handle a phone message without picking up the phone: iPhone Mirroring supplies the private screen, the relay drafts the response, the Mac executes only the approved UI steps, and the pendant provides a deliberate physical send approval. This combines surfaces no single node can reach and preserves a clear boundary between drafting and sending.
- **path:** pendant → relay → mac-planner → ios-control → pendant
- **model tier:** Realtime for the short spoken interaction and draft; deterministic Mac/iPhone actions for navigation and send; no model should autonomously press Send.
- **latency:** Read and draft in 5 seconds; approval-to-send under 3 seconds.
- **cost:** $0.02–$0.08 per interaction, mostly speech/context and draft generation.
- **security:** Messages are highly private. Capture only the foreground iPhone conversation, redact notifications and unrelated apps, retain no screenshot after completion, and require a fresh physical approval bound to the exact draft hash and recipient. If the screen changes, invalidate approval.
- **missing:** A semantic iPhone Mirroring reader that identifies the conversation, latest incoming message, recipient, and composer without relying on fragile coordinates.; A pendant approval protocol carrying a one-time draft hash and explicit approve/cancel state; the existing physical button events are not currently bound to Mac action approvals.; A Mac action transaction that re-checks recipient and composer contents immediately before Send and emits a receipt.

### "“I’m going offline for the next hour. Keep my Mac work going, and tell me on the pendant if it gets stuck.”"
- **useful because:** The system would become a resilient personal operator rather than a one-shot command runner. The relay hands a bounded plan to the Mac, the Mac checkpoints each step and verifies outcomes, and the pendant receives a short stuck/complete prompt even if the owner is away from the desk. On return, the owner gets exactly what completed, what failed, and the next safe action.
- **path:** relay → mac-planner → pendant → browser
- **model tier:** Background model for plan decomposition and recovery suggestions; deterministic executor and receipt checker for each step; realtime only for an owner interruption.
- **latency:** No conversational latency requirement; checkpoint within 2 seconds of each desktop step and alert within 10 seconds of a blocked job.
- **cost:** <$0.05 per multi-step job, dominated by recovery reasoning; routine checkpoints should be model-free.
- **security:** A job must have an explicit scope, expiration, and resource manifest. Never silently broaden a failed plan, send messages, purchase, or delete data. Store redacted receipts locally and send only status plus the minimum needed for a pendant alert.
- **missing:** A durable Mac execution supervisor with idempotency keys, checkpoints, process liveness, and restart recovery; current plans and receipts do not guarantee that a retry will not repeat a side effect.; A typed stuck-state classifier distinguishing waiting for a page, authentication, owner approval, network failure, and completed mutation.; A relay-to-pendant job-alert channel that can address a specific job and let the owner choose retry, pause, or abandon from the device.

### "“When my phone rings, tell me who it is on the pendant and let me answer, silence, or send ‘I’ll call back’ without looking at the screen.”"
- **useful because:** The owner gets a genuinely hands-free call gate: iPhone Mirroring identifies the caller, the relay speaks a minimal alert through the pendant, and a deliberate button choice controls the phone. It prevents a ringing phone from forcing the owner to stop driving, cooking, or working, while keeping outbound text and answering behind an explicit physical choice.
- **path:** ios-control → mac-planner → relay → pendant
- **model tier:** Deterministic event and caller lookup; realtime speech only for the short alert. No generative model is needed to choose an action.
- **latency:** Caller alert within 2 seconds of ring detection; button action within 1 second; expire the choices after 20 seconds.
- **cost:** Near-zero model cost; occasional short audio delivery is the main cost.
- **security:** Caller identity is personal data and must be spoken only after an explicit local listening state. Do not expose full notification text. “Send I’ll call back” is an external communication and must require a fresh press, exact fixed template, and recipient revalidation. Cancel choices when the call ends or the foreground phone state changes.
- **missing:** A push/event source for iPhone Mirroring call-state changes; polling the screen is too slow and brittle.; A pendant finite-state control protocol with three unambiguous choices using the existing buttons/LED, plus expiry and duplicate suppression.; A Mac iOS action that verifies the caller and current call state immediately before answer, decline, or fixed-template reply, and returns an auditable receipt.


## What it asked for

_Nothing._
