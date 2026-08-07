# Harness derivation — faculty-action — round 136

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **24 kHz delivery is server/Mac-complete but pendant playback is unverified** — Live pipeline telemetry shows macOS say produced 75,734 bytes of 24 kHz mono PCM, uploaded successfully to relay, and marked waiting for the nRF9160; live device table still lists only Mac bridge and offline mobile, so end-to-end physical playback has not been demonstrated.
  - evidence: GET /pipeline returned tts done format s16le sampleRate 24000 and relay_result done; GET /ops/status reported no online pendant device.

## Capabilities it proposed

### "When I hold the pendant button, capture a short voice note through the pendant/ESP32 bridge, transcribe it on the Mac, and put the result in ~/AI-Pendant-Workspace as a dated note with suggested reminder/task; tell me what was saved and never create an external commitment without my approval."
- **useful because:** This is the fastest genuinely hands-free way to turn an idea encountered away from the keyboard into a durable, searchable artifact. The physical hold is an intentional capture trigger, while the Mac supplies transcription and the relay survives disconnects.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → dashboard
- **model tier:** Realtime only for the button-start/stop acknowledgement; a cheaper background model performs transcription cleanup and task extraction.
- **latency:** Start acknowledgement under 300 ms; save and speak a provisional transcript within 5 s of release; background refinement can take 30 s.
- **cost:** About $0.01–$0.05 per 30-second note, dominated by speech transcription; local transcription can reduce recurring API cost.
- **security:** Audio and transcript leave the device only to the authorized relay/Mac path. Store locally by default, encrypt at rest, expose a delete action, and require confirmation before sending, scheduling, or editing external services.
- **missing:** A pendant button-event/audio capture protocol that works over the current USB serial attachment; An audio ingestion/transcription route accepting bounded clips; A workspace note/task writer that returns a durable receipt; A physical-action confirmation policy for suggested reminders

### "Before any queued action can send, delete, buy, or publish, let me approve it by holding the pendant button for two seconds; show a compact preview on the Mac, give a short spoken description through the pendant, expire the approval after 60 seconds, and leave an undoable receipt."
- **useful because:** It makes consequential automation safe while keeping the owner’s hands on the pendant instead of hunting for a Mac dialog. The same intent can be decided by judgement and physically authorized even when the voice link is intermittent.
- **path:** faculty-judgement → relay-realtime → pendant → mac-planner → browser-extension → dashboard
- **model tier:** Realtime for the spoken preview and acknowledgement; deterministic policy code enforces the lease, expiry, target binding, and one-shot use.
- **latency:** Preview under 1 s; button approval recognized under 500 ms; execution starts within 2 s; expired leases must never execute.
- **cost:** Negligible model cost per approval; one short realtime turn if spoken preview is generated.
- **security:** Bind the lease to exact action hash, account/session, and target; require a fresh button hold, reject replayed events, audibly state irreversible effects, log proof and receipt, and default-deny on disconnect or ambiguity.
- **missing:** A signed pendant button event with monotonic counter and local LED/vibration state; A relay action-lease/approval endpoint and deterministic gate before Mac/browser execution; A Mac/browser preview renderer and receipt/undo integration; A no-link local cancellation latch

### "When I unplug the pendant, pause every not-yet-started external action and keep working only on reversible local drafts; when I plug it back in, tell me exactly what was paused, what expired, and offer one-button resume or cancel for each item."
- **useful because:** A cable or radio drop should be a visible safety boundary, not a silent race in which a queued browser or Mac action finishes without the owner. Reconnection gives a concise recovery queue instead of forcing the owner to reconstruct state.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** No expensive model is required: a durable state machine handles suspend/expiry/resume; realtime is used only to announce the recovery summary when the pendant reconnects.
- **latency:** Detect USB/link loss within 2 s; freeze new external side effects immediately; recovery summary within 3 s of reconnect.
- **cost:** Negligible inference cost; small durable job-state and event-log storage.
- **security:** Fail closed for send/delete/purchase/publish; use idempotency keys so reconnect cannot duplicate work; distinguish completed from merely acknowledged; retain a tamper-evident event trail and require explicit resume for any irreversible item.
- **missing:** Reliable USB serial connect/disconnect events from the pendant bridge; A relay-wide job state transition hook that can suspend queued work atomically; Browser and Mac executors honoring suspend tokens and reporting in-flight outcomes; A pendant reconnect summary/choice protocol

### "Turn whatever I am doing across Safari and Mac apps into a resumable handoff: save the relevant tabs, selected text, drafts, local files, pending jobs, and the exact next step, then let me say “resume my handoff” from the pendant later and restore the work without reopening unrelated private context."
- **useful because:** The owner can leave a task midstream—at a meeting, while commuting, or after a crash—and return to the exact point rather than reconstructing it from tabs and memory. This is a user-visible continuity capability, not merely a memory refactor.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-terminal → dashboard
- **model tier:** A cheaper background model compiles and summarizes the handoff; realtime only handles the short capture and resume exchange.
- **latency:** Capture acknowledgement under 1 s; handoff artifact within 5 s; resume preview within 2 s and restoration within 10 s.
- **cost:** Usually under $0.02 per handoff, dominated by summarization; local metadata extraction can avoid most API calls.
- **security:** Never snapshot passwords, payment fields, hidden tabs, or full page contents by default. Encrypt the handoff locally, attach per-item sensitivity and expiry, require confirmation before reopening a private tab, and provide permanent deletion.
- **missing:** A cross-surface handoff schema with tab/file/job locators and expiry; Browser extraction of selected text and draft state without submitting forms; Mac restoration that can reopen only the approved items; Pendant commands to list, preview, resume, and delete handoffs

### "When I say “keep this local,” route the rest of this task entirely through my Mac and browser sessions, show me what information would otherwise leave the machine, and refuse relay/model calls that are not necessary until I explicitly switch back to normal mode."
- **useful because:** The owner can use private logged-in pages, drafts, and sensitive work without having to guess which parts of the hive are receiving data. It turns privacy from a policy document into a control they can invoke while wearing the pendant.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-terminal → dashboard
- **model tier:** A deterministic routing/policy layer makes the data-boundary decision; use a local Mac model for summarization where available and realtime only for the spoken mode switch.
- **latency:** Mode switch acknowledged within 500 ms; policy decision before every tool call; local-only responses within 5 s for ordinary tasks.
- **cost:** Potentially lower API cost because private tasks avoid cloud inference; small local policy and audit overhead.
- **security:** The relay may need to receive only an opaque command envelope, never page contents or audio after local mode begins. Display the active boundary prominently, block cloud fallback, redact telemetry, expire the mode after inactivity, and log blocked egress attempts locally.
- **missing:** A signed local-only mode token propagated to relay, Mac, and browser; A planner/router that can run without cloud model fallback; Per-tool data-egress declarations and enforcement; A pendant LED/voice indicator and dashboard control for boundary state

### "If a browser or Mac transaction may have partially completed, tell me whether it actually took effect: reconcile the local action log, browser confirmation state, and the external page or receipt, then give me one of succeeded, failed, unknown, or needs-human-check with the evidence and a safe next action."
- **useful because:** Network drops and ambiguous web responses currently leave the owner unsure whether an order, form, upload, or message happened. This prevents duplicate submissions and replaces guesswork with an evidence-backed recovery decision.
- **path:** pendant → relay → mac-planner → browser-extension → mac-terminal → dashboard
- **model tier:** Deterministic reconciliation and page-state checks first; use a cheaper model only to explain conflicting evidence. Realtime is only for the concise spoken result.
- **latency:** Initial status within 2 s; authenticated-page reconciliation within 15 s; never retry an irreversible operation automatically.
- **cost:** Low per incident; one browser inspection and mostly local log reads, with model cost only for ambiguous explanations.
- **security:** Read-only reconciliation must be separate from execution. Bind evidence to request ID, tab/session, URL, timestamp, and action hash; redact secrets; treat contradictory evidence as unknown; require confirmation before any compensating action.
- **missing:** A transaction state machine with an explicit unknown state; Browser probes for post-submit confirmation, receipts, and server-side status; Cross-surface correlation of Mac job receipts with browser request IDs; A spoken/dashboard recovery card that prevents accidental retry


## Changes it proposed to its own stack

### `firmware` — Add a tiny authenticated pendant event journal shared by button and USB/radio transport: each press/release/connect/disconnect event receives a monotonic counter, device boot epoch, and CRC/MAC; persist only the last 32 counters in a wear-leveled 2 KB ring, expose them over the existing serial protocol, and drive the LED as a local pending-approval/expired indicator. The relay rejects duplicates, gaps requiring re-pair, stale epochs, and events received after a lease expiry.
- **owner gets:** The owner can approve or cancel a consequential action with a physical hold and trust that a flaky cable, reconnect, or replay cannot accidentally execute it. It also makes unplug/replug recovery understandable instead of silent.
- effort: Medium: firmware event journal and serial framing, relay verifier, and a Mac harness test with forced disconnect/reconnect; do not flash until the owner approves and supplies the controlled build/secrets process.  ·  risk: A corrupted journal could strand approvals or falsely force re-pair; recover by a deliberate local re-pair gesture and retain a visible LED error state. Incorrect clock use must not matter because expiry is relay-monotonic, not wall-clock based.
- cost: Negligible API cost; roughly 2 KB flash/RAM buffers and under 1 mA intermittent LED/CPU overhead. No new hardware.  ·  latency: Under 50 ms event framing; no effect on 24 kHz audio payload if journal writes are deferred from the audio ISR.
- security: Improves anti-replay and action authorization; keys must remain outside logs and secrets.conf must never be printed.
- depends on: A relay action-lease endpoint and deterministic executor gate; A documented button event framing contract over the currently connected USB serial; Owner-controlled firmware build and flashing procedure; Physical-action confirmation policy


## What it asked for

_Nothing._
