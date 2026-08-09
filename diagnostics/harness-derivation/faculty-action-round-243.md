# Harness derivation — faculty-action — round 243

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Remember this moment and turn it into a follow-up I can finish later.”"
- **useful because:** A bookmark is currently just a durable payload. This would join the pendant's moment bookmark and optional voice memo to a single relay case, have the Mac create a linked note with timestamp and source hash, and let the owner later ask for the unfinished follow-up without hunting through files or audio.
- **path:** pendant → relay → mac-planner → mac-terminal → dashboard
- **model tier:** Background model for transcription and entity extraction; realtime only for the spoken acknowledgement.
- **latency:** Acknowledge the bookmark locally in under 300 ms; create the linked note within 30 s when the Mac is online; reconciliation may run later.
- **cost:** About $0.01–$0.05 per memo depending on transcription length; storage and hashing dominate at scale.
- **security:** Audio and extracted text leave the pendant only when the existing failure-path upload permits it. Notes are private by default. Never send external messages or create destructive tasks without the existing approval policy and physical confirmation.
- **missing:** A typed cross-surface case/link record that binds bookmark ID, memo ID, note ID, and follow-up state; A Mac-side reconciliation worker that can prove the note contains the source hash and timestamp; Owner choice of default note destination

### "“Keep working on this across my Mac and browser, and tell me exactly where it stopped if anything changes.”"
- **useful because:** Long tasks today are a collection of actions and receipts, not a resumable user-visible process. This would make a durable cross-surface work session: relay queues intent, Mac and browser execute bounded steps, faculty-perception independently verifies each postcondition, and a changed tab/app/session pauses rather than guessing. The owner gets a truthful resume point instead of a vague failure.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Background model for planning and summarizing; realtime only for interruption or owner clarification.
- **latency:** Start within 2 s, each bounded step under 20 s, and emit a pause/status event within 1 s of detected state drift.
- **cost:** Roughly $0.02–$0.15 per multi-step session; verification calls and browser/Mac round trips dominate, not tokens.
- **security:** No secrets or page contents go to the pendant. Each step has an explicit risk class, expiry, and postcondition. External sends, purchases, deletion, or credential use remain staged for approval. State drift must fail closed and preserve the last verified step.
- **missing:** A durable work-session state machine with step cursor, lease expiry, and drift/pause reason; A route that can subscribe to or poll step state without conflating executor receipts with independent verification; A user-facing resume/cancel control on the pendant or dashboard

### "“When I miss an answer, let me replay just the last useful part from the pendant.”"
- **useful because:** The owner can miss a response even when delivery succeeded; link retry and audio delivery acknowledgements do not solve that. A physical replay control lets the owner request the previous response without speaking again, while the relay serves a bounded, expiring cursor and the pendant never invents or records new audio.
- **path:** pendant → relay-realtime → mac-bridge → dashboard
- **model tier:** No new model call for replay; reuse the stored response artifact and a cheap background policy check for expiry/privacy.
- **latency:** Start playback within 500 ms when the artifact is cached at the bridge, otherwise within 3 s after relay retrieval.
- **cost:** Near-zero incremental inference cost; bandwidth and short-lived encrypted audio storage dominate.
- **security:** Replay only the most recent owner-requested response, with a short expiry and artifact hash. Do not replay private content after a conversation boundary or to a different bound device. Require a deliberate rotary/button gesture, not a hot-path recording press.
- **missing:** The planned rotary encoder/second button input and a firmware gesture mapping; A relay API for bounded response-artifact replay by opaque cursor, with privacy boundary and expiry enforcement; A pendant-visible local status when the requested artifact has expired

### "“Before you submit this, let me correct one wrong field on the pendant without exposing the whole page or starting over.”"
- **useful because:** Today an action is either executed from the current browser/Mac state or abandoned when one field is wrong. This capability would extract only the minimum action fields (recipient, date, amount, account, destination), attach provenance to each field, detect disagreement between the planner and live browser state, and let the owner rotate/select a correction on the pendant. The Mac then re-renders the exact corrected field, re-verifies the complete form, and only afterward proceeds through the existing approval boundary.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Background model for field extraction and conflict explanation; realtime only for the owner's short correction dialogue.
- **latency:** Conflict summary within 2 s; correction confirmation within 1 s per field; full re-verification before any submission.
- **cost:** Approximately $0.02–$0.10 per action, dominated by browser/Mac verification and model extraction of ambiguous fields.
- **security:** The pendant receives structured field labels and masked values, never page HTML, credentials, or unrelated private content. Every correction is versioned against the original page/form hash. A changed recipient, amount, destination, or permission scope invalidates prior approval and requires a fresh deliberate confirmation. External submission remains staged until the physical transaction latch approves.
- **missing:** A field-level provenance and conflict envelope with masking rules and form-version hash; A narrow pendant interaction model for selecting and correcting one field using the planned rotary encoder and second button; A Mac/browser adapter that can update one approved field and independently verify the complete postcondition


## What it asked for

_Nothing._
