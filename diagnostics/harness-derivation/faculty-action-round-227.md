# Harness derivation — faculty-action — round 227

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Fill this form, but show me exactly what will be submitted first.""
- **useful because:** This would make the pendant the missing trust boundary for high-consequence browser work: the Mac and logged-in browser can do the work, but the owner gets a concise spoken summary and a deliberate physical approval before any private or irreversible field is submitted. The system independently checks the URL and field values afterward instead of trusting an executor receipt.
- **path:** relay-realtime → faculty-judgement → mac-planner → browser-extension → faculty-perception → faculty-action → home-macbook-bridge
- **model tier:** Use the realtime tier only to capture the request and speak the short preview; use the cheaper background planner for field mapping and risk classification. Browser execution is deterministic. faculty-perception performs the read-only postcondition check.
- **latency:** Preview in 2-4 seconds; physical approval can wait indefinitely up to an explicit expiry; submission and verification in under 5 seconds after approval.
- **cost:** Typically one short realtime turn plus one cheap planner call; roughly $0.01-$0.05 depending on form complexity. Browser and verification calls dominate latency, not tokens.
- **security:** Never send page secrets or full form contents to the pendant. Redact sensitive values in the spoken preview (for example, last four digits only). Require the existing physical transaction approval latch for send/purchase/delete classes. Bind approval to URL, field-name/value digest, expiry, and monotonic nonce; refuse if any changes. If verification cannot establish the postcondition, report unknown rather than success.
- **missing:** A stable browser command correlation ID passed through planning, execution, and verify_operation_step; A standard redacted form-preview schema shared by judgement and browser-extension; Owner confirmation of which risk classes may be approved proactively; default all submission-like actions to staged

### ""I missed the last answer—repeat it." Turn the pendant wheel one click to replay it, and turn again to skip back through recent answers."
- **useful because:** A dropped link is not the only failure: audio can arrive successfully and still be missed in a noisy room. A physical replay cursor lets the owner recover the last few answers without reopening a conversation or speaking over the system. The wheel is a new selection axis, so it does not overload sw0 recording or sw1 bookmarking.
- **path:** relay-realtime → pendant → mac-planner → home-macbook-bridge
- **model tier:** No model is needed for replay selection. The realtime tier only generates the original answer; a cheap background task may compact metadata and expire old artifacts.
- **latency:** Haptic acknowledgement immediately; replay begins within 500 ms when the artifact is local and within 2 seconds after relay fetch.
- **cost:** Near-zero for local replay; one object-store fetch and no inference for a cached answer. Storage and LTE transfer dominate when the artifact is not local.
- **security:** Store opaque artifact IDs, not transcript text, in the pendant cursor. Enforce owner-initiated replay, per-artifact expiry, checksum, and replay count. Do not replay sensitive content aloud unless the owner explicitly requests it; the relay should mark sensitivity and require a spoken confirmation for secret-class artifacts.
- **missing:** The owner-directed rotary encoder and a second product button, currently not on the bench pendant; A relay INBOX manifest extension for replayable answer artifacts: cursor, codec/rate, checksum, expiry, sensitivity, and replay count; A small pendant UX state machine for wheel-click, wheel-turn, and cancel

### ""Remember this moment and make the right follow-up later." Press the bookmark button while speaking; have the system create a concise note and, only when clearly requested, a reminder with a link back to the audio."
- **useful because:** The pendant is the only surface present at the moment worth remembering. This turns the existing bookmark into a useful cross-surface handoff: durable capture now, structured understanding later, and a reversible Mac artifact whose creation can be independently verified. It avoids forcing the owner to repeat context when they are away from the Mac.
- **path:** pendant → relay-realtime → faculty-judgement → mac-planner → faculty-action → faculty-perception → home-macbook-bridge
- **model tier:** Use realtime only for capture acknowledgement. A cheaper background model transcribes and extracts a title, note, and candidate next action. Deterministic Mac actions create the note/reminder; perception verifies the file or reminder state.
- **latency:** Capture acknowledgement under 300 ms locally; relay upload opportunistic; structured note within 30 seconds of connectivity; reminder creation staged when ambiguity or risk is present.
- **cost:** One inexpensive transcription/extraction call per bookmark, usually $0.01-$0.08 depending on duration. SD/LTE transfer and transcription dominate.
- **security:** Capture is local and encrypted at rest if possible; never execute a reminder or external message from inferred speech without explicit owner intent. Preserve the original audio as a failure-path object, not a default duplicate. Attach confidence and source ranges to extracted claims, and verify the resulting note/reminder independently.
- **missing:** A typed bookmark-to-note extraction contract with confidence and source offsets; A user policy value distinguishing automatic note creation from staged reminder creation; A relay-to-Mac idempotency key so reconnects cannot create duplicate notes

### ""Watch this process until it finishes, and only interrupt me if it stalls or needs me.""
- **useful because:** Today the owner must either keep checking the Mac or ask repeatedly what happened. This capability would let the relay hold a bounded watch: the Mac/browser agent observes a specific app, job, or page condition; faculty-perception distinguishes progress, success, and genuine stall; and the pendant gives one meaningful haptic/spoken interruption only when the owner's attention is required. It is a new cross-surface behavior, not just another action or status query.
- **path:** relay-realtime → faculty-judgement → mac-planner → browser-extension → faculty-perception → faculty-action → home-macbook-bridge
- **model tier:** Use a cheap background model to turn the owner's natural-language goal into a bounded monitor and polling plan. Use realtime only for the initial clarification and the final short interruption. Deterministic observers handle snapshots and deadlines.
- **latency:** Acknowledge in under 2 seconds; poll cadence depends on the process (5-60 seconds); alert within one polling interval of a verified stall or required input.
- **cost:** Low: mostly host/browser polling and compact state diffs; one planner call per watch. Model cost should be cents or less for a typical hour-long watch.
- **security:** The watch must be scoped to named apps, tabs, files, or jobs and expire automatically. Do not continuously capture arbitrary screen contents. Store hashes and minimal state transitions by default; require confirmation before the watcher performs any new action. A stale observer must produce unknown, never success or stall.
- **missing:** A first-class watch/monitor job with expiry, polling cadence, cancellation, and deduplication; Typed progress and stall predicates that faculty-perception can verify from fresh Mac/browser state; A pendant notification policy that coalesces repeated alerts and lets the owner cancel the watch physically; An owner policy for which monitored processes may be allowed to self-retry versus only request attention

### ""I left my Mac for a while—tell me only what changed in the work I was doing, and what needs my decision.""
- **useful because:** The owner gets a useful return-from-interruption briefing instead of a raw notification stream or a full screen dump. The Mac records scoped, privacy-minimal state transitions while the pendant is away; on return, the system groups them into completed, changed, blocked, and decision-needed items and speaks one short sentence.
- **path:** pendant → relay-realtime → home-macbook-bridge → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** A cheap background model summarizes compact state diffs; realtime is used only when the owner requests the briefing. Deterministic collectors and faculty-perception establish what actually changed.
- **latency:** Return briefing in 2-5 seconds from cached diffs; no continuous inference while unattended.
- **cost:** Low: bounded event metadata and one small summarization call. Avoid storing screenshots or full page text by default.
- **security:** Scope each absence window to explicitly selected apps, tabs, files, or jobs. Store hashes, titles, and status transitions rather than content. Sensitive changes are reported as 'a private item changed' until the owner asks on the Mac. Never infer completion from notification presence alone.
- **missing:** A scoped absence-window/session marker shared by pendant and Mac bridge; A privacy-preserving state-diff journal with retention and sensitivity labels; A return-briefing reducer that groups transitions and deduplicates repeated updates; A way for the owner to start/end an absence window without overloading the recording/bookmark buttons

### ""Give me a private proof of what happened, without repeating the secret or putting it in the cloud.""
- **useful because:** For sensitive Mac work, the owner needs more than 'done' but less than a transcript or screenshot sent to the relay. The Mac can create a local, redacted evidence capsule containing action identity, timestamps, hashes, and verified postconditions; the pendant speaks a short result and can later identify the capsule for audit without receiving secrets.
- **path:** faculty-action → faculty-perception → mac-planner → mac-terminal → home-macbook-bridge → relay-realtime → pendant
- **model tier:** No realtime reasoning is needed after the request. Deterministic local code creates the capsule; faculty-perception verifies postconditions; a cheap model may summarize non-sensitive labels only.
- **latency:** Generate and verify in under 3 seconds for ordinary file/app actions; return a local capsule ID immediately if a longer operation continues.
- **cost:** Near-zero inference cost; local hashing and bounded metadata storage dominate.
- **security:** Keep contents and secrets on the Mac; relay receives only an opaque ID, sensitivity class, hashes, and minimal human-readable summary. Evidence must be append-only, expire by policy, and distinguish verified, failed, and unknown. Do not let possession of a capsule ID authorize replay or execution.
- **missing:** A local evidence-capsule format with sensitivity-aware redaction; A durable linkage between action, attempt, verifier provenance, and capsule ID; A pendant query/acknowledgement protocol that carries only opaque IDs and short summaries; Owner-selected retention duration for private evidence


## Changes it proposed to its own stack

### `interaction` — Add a cross-surface freshness circuit breaker: before any staged browser action leaves preparation, faculty-action must require a recent browser session binding and URL digest; if the extension heartbeat or bound session is older than the action's freshness budget, automatically cancel the pending transaction and ask the owner to reopen/review rather than executing against a changed tab.
- **owner gets:** The owner will never get a frightening 'approved one thing, submitted another' result merely because Safari went stale or a tab navigated while they were deciding. It fails closed without requiring them to understand bridge state.
- effort: Medium: add freshness metadata to the approval envelope, have browser-extension expose the last-bound session and URL digest, and route stale cases through the existing cancellation/status beacon.  ·  risk: A legitimate action may be deferred when the Mac sleeps or the extension misses a heartbeat. Recovery is simple: refresh/rebind and present a new digest; never reuse the old approval.
- cost: Negligible API cost; one extra status read and digest comparison.  ·  latency: Adds under 200 ms when browser status is fresh; stale cases intentionally wait for owner review.
- security: Improves fail-closed behavior and prevents replay of approvals across tabs/sessions. Do not include form secrets in the digest payload sent to the pendant.
- depends on: A browser session identity and last-seen timestamp from the existing browser status surface; Correlation of approval nonce to URL/field digest; Existing physical transaction approval latch

### `hardware` — Build the next pendant revision around the owner's requested rotary encoder plus one additional tactile button, with the encoder on a protected side edge and a detent/button input routed to nRF GPIO/interrupts. Reserve the second button for deliberate confirm/cancel or replay, while leaving sw0 as record and sw1 as bookmark.
- **owner gets:** Everyday use gains selection and recovery without making the owner remember twenty meanings for a long press. They can replay a missed answer, choose among pending outcomes, or deliberately approve/cancel without slowing recording.
- effort: Medium-high: select a low-profile jewellery-suitable encoder, wire/debounce it, add a compact gesture state machine, and update enclosure/PCB or harness. Bench prototype can use the existing nRF9160-DK GPIOs before a gold enclosure revision.  ·  risk: Accidental wheel turns could trigger actions if treated as approval; wheel events must only navigate/select, and approval must require a distinct deliberate button gesture. Mechanical wear and switch bounce need filtering. Recovery is firmware update and physical bypass via existing buttons.
- cost: Roughly $3-$15 for an encoder/button prototype, plus enclosure/PCB cost; negligible additional power except interrupt wakeups.  ·  latency: Sub-50 ms input acknowledgement; no model latency for navigation.
- security: Adds a safer explicit selection axis and reduces overloaded gestures. Keep secrets and action payloads off-device; only opaque IDs and summaries belong in the pending queue.
- depends on: A new enclosure/PCB or verified bench wiring; Firmware gesture semantics that preserve sw0 record and sw1 bookmark; Relay support for replay cursor and approval item selection


## What it asked for

_Nothing._
## Its own summary

Recorded five non-infrastructure changes this round. The highest-value capability is approval-bound browser form execution: the Mac/browser does the work, the owner sees a redacted preview and physically approves, and faculty-perception independently verifies URL and field postconditions. I also recorded wheel-based replay of missed answers, bookmark-to-structured-follow-up capture, a stale-browser freshness circuit breaker, and a concrete rotary-encoder/second-button pendant revision. Discovery shows Safari and the home Mac bridge online, but no LTE-registered pendant device.

**Biggest unknown:** The remaining blocker is product input and contract definition, not model capability: the rotary encoder/second button are not yet on the bench, and browser execution still needs a stable session/action correlation plus a typed redacted-preview schema. The owner must also choose which inferred follow-ups may create reminders automatically; conservative default is stage them.

