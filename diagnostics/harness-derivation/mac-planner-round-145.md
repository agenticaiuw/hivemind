# Harness derivation — mac-planner — round 145

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Save this for later” (or “make a task from what I’m looking at”)."
- **useful because:** The owner can turn a fleeting thought and the currently open private webpage into a durable, sourced work item without touching the Mac. The pendant supplies intent and confirmation; the browser supplies authenticated context; the Mac creates an editable artifact/reminder; the relay keeps the result available even if the browser disconnects.
- **path:** pendant → relay → browser → mac-bridge → dashboard
- **model tier:** Use realtime only to capture the short voice command and read back confirmation. Use a cheaper background model to extract the page’s title/key passage, classify task/date, and generate the Markdown; no model is needed for deterministic routing, hashing, or file creation.
- **latency:** Acknowledge on the pendant within 500 ms, extract and write within 5 seconds when the browser is online, and enqueue the capsule for later completion if it is offline. Never silently submit a form or send mail.
- **cost:** About $0.005–$0.03 per invocation depending on page length; realtime audio and page summarization dominate. Deterministic relay, browser extraction, and Mac file/reminder operations are negligible.
- **security:** Authenticated page text leaves the browser only to the owner’s relay/Mac path; redact secrets and exclude password/payment fields. Store URL, timestamp, tab/session id, and a content hash for provenance. Creating a local note/reminder is allowed by owner policy; sending mail, deleting files, or external submission remains an explicit confirmation boundary.
- **missing:** A single correlation-id capsule schema shared by relay, browser bridge, and Mac jobs; An active-tab extraction command that returns cited snippets and a stable page fingerprint (without screenshot permission); Offline durable queue/retry and deduplication keyed by page fingerprint plus spoken intent; A Mac-side artifact template writer that links the source and resulting reminder/job receipt

### "“Show me the privacy receipt for what you just did.”"
- **useful because:** Today the owner may get a job receipt, but cannot see one trustworthy, cross-device account of what the pendant heard, what authenticated browser data was read, what left the Mac, which model processed it, and what files or reminders changed. This capability gives a concise spoken answer plus a durable, inspectable receipt, so the owner can use the hive without surrendering invisible control.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic code for the event ledger, redaction, hashes, timestamps, model names, and file/action diffs. Use a cheap background model only to turn the structured ledger into a short plain-language explanation; realtime is only for the owner's follow-up question.
- **latency:** The pendant should answer from the already-built ledger in under 1 second for a completed task. Generating the human summary can take up to 3 seconds and must not delay the underlying action.
- **cost:** Under $0.01 per receipt in normal use; storage and hashing dominate operational cost, with an optional small background summarization call.
- **security:** Receipts themselves can reveal private URLs, snippets, and secrets. Keep raw content on the originating device, persist only redacted summaries and salted content hashes by default, encrypt relay records, scope them to the paired owner, and support immediate local deletion. Never claim a model did not see data merely because the raw text was not persisted.
- **missing:** A tamper-evident, append-only cross-surface event ledger with per-event actor, data-class, destination, and retention fields; Automatic redaction/classification before relay persistence and a user-visible retention/deletion control; A read-only receipt projection that joins pendant audio, browser extraction, relay model calls, and Mac action receipts by one correlation id; A dashboard and pendant response format for “what was seen / sent / changed / retained”


## Changes it proposed to its own stack

### `integration` — Implement a cross-surface Capsule envelope and relay-backed outbox. Every pendant intent gets capsuleId, utterance, activeTab/session binding, source URL/title, extracted snippets, content fingerprint, requested local outputs, and a state machine (heard→extracted→written→acknowledged). Browser results and Mac job receipts append events under the same capsuleId; retries are idempotent, and a reconnecting pendant receives only the missing terminal event/audio. Add a compact Markdown artifact format in ~/AI-Pendant-Workspace with citations and a receipt link.
- **owner gets:** “Save this” becomes dependable instead of occasionally creating a browser result, a Mac file, and an audio reply that cannot be correlated. If Wi‑Fi or the browser drops, the owner gets one eventual, traceable result rather than having to repeat themselves or wonder whether a task was duplicated.
- effort: Medium: shared schema and D1/outbox migrations, browser bridge correlation plumbing, Mac job metadata propagation, and a small artifact writer; then failure-injection tests for duplicate delivery and reconnect.  ·  risk: A stale tab could be attached to the wrong utterance, or retries could create duplicate reminders/files. Require a fresh heartbeat and tabId match, use deterministic artifact paths and idempotency keys, and emit a partial-failure receipt naming exactly what happened. Recovery is replaying the capsule’s unapplied event, not repeating the whole action.
- cost: Small D1/storage and metadata overhead; one cheap background extraction call when page text is needed. Audio is generated only for the final confirmation, not every retry.  ·  latency: No added latency to the initial spoken acknowledgement; roughly 100–300 ms relay bookkeeping and under 1 s for local receipt stitching. Offline work waits for reconnect.
- security: Capsules must be tenant/pair scoped, expire page snippets by policy, redact sensitive fields before persistence, and keep full authenticated content off logs. Provenance metadata remains available for audit.
- depends on: Browser heartbeat freshness and tab/session affinity from the existing browser bridge; Mac job receipts and correlation fields from the existing job queue; A durable relay audio/object retention policy; Owner’s existing local workspace path ~/AI-Pendant-Workspace

### `hardware` — Add a small tri-color status LED (or low-power RGB indicator) and vibration motor to the pendant, driven by a signed privacy-state envelope from firmware: idle, microphone open, private material being exported to relay, Mac/browser action in progress, and receipt complete/error. Make the indication local and fail-safe: if the pendant cannot verify the state or loses the link, it shows an unknown/offline pattern rather than implying privacy.
- **owner gets:** The owner gets an immediate physical answer to “is this thing listening or sending my private page right now?” without opening a dashboard or interrupting a conversation. It makes the hive’s privacy receipt visible at the moment it matters, including when the Mac screen is locked or the browser is in another window.
- effort: Low-to-medium hardware revision and firmware work: LED/vibration driver, signed compact state packets, configurable brightness/patterns, and an accessibility-friendly silent mode; add relay/Mac events for state transitions and test link-loss behavior.  ·  risk: A bright LED can expose use in a meeting, and a stale state could falsely reassure the owner. Default to dim/short patterns, allow a physical long-press to pause outbound transfer, expire every state quickly, and use an unmistakable unknown pattern after timeout. No indication should contain page content.
- cost: Approximately $1–$4 in components and small battery impact (LED bursts and vibration only on transitions); negligible API cost for compact state events.  ·  latency: Local state changes should appear within one audio/frame interval (<100 ms); remote confirmation may lag, so firmware must distinguish local microphone state from relay acknowledgement.
- security: Improves privacy transparency but adds a side channel (someone nearby can infer activity). Store no content; authenticate state packets and permit owner-configured patterns or fully silent operation.
- depends on: The cross-surface privacy receipt/event schema proposed above; Pendant firmware support for one additional GPIO/I2C output and a signed state-event decoder; Relay, browser bridge, and Mac job runner emitting explicit privacy-state transitions


## What it asked for

_Nothing._
## Its own summary

Fresh Mac evidence: browser bridge is online on Safari (3 tabs, zero pending commands), relay is reachable, and audio currently captures at 15,625 Hz / uplinks 16 kHz while playback decodes 24 kHz. I recorded a new cross-surface Capsule outbox design: correlate pendant intent, authenticated-tab extraction, Mac artifact/reminder, and durable audio/job receipts with idempotent retry. I also submitted the concrete missing-between-the-nodes integration rather than re-proposing the already-known browser-watch/audio-profile ideas. The attempted 24-kHz hardware proposal was correctly rejected as already covered by the existing backlog.

**Biggest unknown:** Implementation readiness, not another permission: the granted read-only Mac inspection and action tools are still schema-only, so I cannot verify or execute the capsule workflow from this round. The remaining owner-level choice is whether to enable Accessibility/Screen Recording manually for vision workflows (currently both false); browser extraction and AppleScript-based workflows do not require it. For the audio goal, the unresolved engineering decision is which 24-kHz-capable microphone/clock hardware will replace the current 15.625-kHz capture path.

