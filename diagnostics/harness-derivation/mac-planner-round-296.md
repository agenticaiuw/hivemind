# Harness derivation — mac-planner — round 296

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-accessibility-live** — The live Mac now reports Accessibility and Screen Recording trusted for AI Pendant Agent, synthesized input verified, and iPhone Mirroring foreground/running. This supersedes the older denied-permission context for current execution planning.
  - evidence: mac_readonly_inspect operation=running_apps returned GET /observe HTTP 200 at 2026-08-09T04:00:37Z: accessibility.trusted=true, screenRecording=true, eventsPost=true, uiActionsWillReachTheScreen=true; iPhone Mirroring listed running.

## Capabilities it proposed

### "“I’m watching or reading something—when I press the pendant button, save exactly where I am and make it easy to resume later.”"
- **useful because:** A physical bookmark is faster and more reliable than switching apps. It should preserve the authenticated browser URL, media timestamp or page position, the Mac foreground app, and the pendant's timestamp as one durable cross-device marker; later the owner can say “resume my last bookmark” and return to the exact place.
- **path:** pendant → relay → browser → mac-bridge → dashboard
- **model tier:** Cheap background model to normalize the marker and title; realtime only for the spoken confirmation. No model is needed for capture or resume routing.
- **latency:** Capture acknowledgement under 300 ms locally; relay receipt under 2 s when online; resume action under 5 s.
- **cost:** <$0.01 per bookmark when title/page extraction is needed; dominated by one small background summarization call. Browser and Mac operations are otherwise local.
- **security:** The marker may contain a private authenticated URL and selected page context, so redact query tokens and page text by default and retain only origin/title/position unless the owner opts in. Resuming a tab is reversible; opening a private URL should be visibly logged and never shared to other surfaces.
- **missing:** A browser command that returns stable media timestamp/page-position metadata rather than only a URL/title; A durable cross-surface bookmark schema joining pendant event, browser session, and Mac foreground identity; A resume intent that can target the original browser session without creating duplicate tabs

### "“Continue the job I started, even if the Mac or browser session was interrupted—use whichever node is awake and tell me only when there is a real result.”"
- **useful because:** Long research, file-generation, and browser workflows currently strand the owner at a partial state. A relay-owned job can checkpoint browser evidence, staged files, and completed steps; the Mac can atomically commit artifacts when awake, while the pendant receives a short success/failure notice. Retries become continuation rather than duplicate work.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background/cheap model for checkpoint summarization and deduplication; realtime only to answer a spoken status question.
- **latency:** Checkpoint within 2 s of each meaningful step; restart detection within 1 minute; final receipt within 10 s after a node returns.
- **cost:** <$0.03 per multi-step job, dominated by summarizing browser evidence; storage and relay polling dominate latency, not inference.
- **security:** Checkpoint only hashes and redacted excerpts by default, never passwords or full authenticated pages. Atomic file commits must remain scoped to the workbench root. Retrying a browser mutation or external send requires an explicit idempotency key and a separate owner confirmation policy; reads and local drafts can continue unattended.
- **missing:** A public idempotent job/checkpoint contract that both browser and Mac workers can claim; Browser-side resumable checkpoints containing action result and session identity; A pendant notification payload that names the completed job without leaking private content

### "“Call back the last person I was talking to.”"
- **useful because:** The pendant is the fastest place to ask while walking, but it cannot reach the phone by itself. The relay can resolve the intended recent contact from the mirrored iPhone, and the Mac can place the call without the owner hunting through apps. This turns a natural spoken request into a concrete phone action across wearable, relay, Mac, and iPhone.
- **path:** pendant → relay → mac-bridge → iOS → dashboard
- **model tier:** Realtime model only for resolving the spoken reference; deterministic local/iPhone inspection should identify the most recent contact and present a confirmation card.
- **latency:** Resolve candidate in 2 s; show contact/number and require confirmation before dialing; call initiation under 5 s after confirmation.
- **cost:** <$0.01 per request; inference is a short reference-resolution turn. Mac/iPhone control and contact lookup are local.
- **security:** Never infer a phone number from cloud memory. Read the recent-call/contact UI from the owner's paired iPhone, display the candidate and last-four digits, and require explicit confirmation before placing a call. Do not speak the full number aloud by default. If iPhone Mirroring is locked or ambiguous, stop and ask.
- **missing:** A typed iOS Mirroring read operation for recent calls/contact identity; A confirmation-aware call action routed through the Mac agent; A private pendant receipt for dialing/ringing state and cancellation

### "“What was I doing around 3pm, and show me the exact document, tab, or call I was working on?”"
- **useful because:** Today the system can inspect the present, but it cannot reconstruct a trustworthy past across surfaces. A local activity rewind would join Mac app/document events, browser navigation, iPhone Mirroring state, calendar, and pendant bookmarks into a time-bounded timeline. The owner could recover lost context after an interruption without relying on memory or sending their entire history to the relay.
- **path:** pendant → relay → mac-bridge → browser → iOS → dashboard
- **model tier:** Cheap background indexing and deterministic time-window retrieval; use the realtime model only to turn the selected evidence into one short spoken explanation.
- **latency:** Record events locally within 1 s; answer a one-hour rewind query in under 5 s; opening the selected artifact under 3 s.
- **cost:** Near-zero for capture and indexing; <$0.01 per query for concise synthesis. Storage and local event filtering dominate, not model inference.
- **security:** This is highly sensitive behavioral history. Keep raw events on the Mac, use coarse app/document identities by default, hash or redact URLs and filenames, define automatic retention (for example 24 hours unless pinned), and never upload the timeline wholesale. Opening a recovered document or private tab must be separately visible and cancellable.
- **missing:** A Mac event journal for foreground app, document identity, and selected browser context with timestamps; An iPhone Mirroring event adapter for calls and active app identity; A privacy-preserving temporal query/index service joining those events with pendant bookmarks; A dashboard and pendant response format that cites evidence without exposing raw history


## Changes it proposed to its own stack

### `integration` — Add a deterministic iPhone-Mirroring read/act bridge with typed operations: recent_calls (redacted contact labels and timestamps), contact_candidate, prepare_call (returns a confirmation payload), place_call, and cancel. Route every operation through the existing Mac job ledger and emit a pendant-safe receipt. Do not depend on generic screen scraping or resolver guesses.
- **owner gets:** The owner can ask the pendant to call or text the right person without navigating a mirrored phone, while still seeing exactly who will be contacted before an external action occurs.
- effort: Medium: implement an iOS Mirroring adapter plus typed Mac action mapping, then test locked/ambiguous/no-permission states on the live Mac.  ·  risk: Wrong-recipient calls are the primary failure; mitigate with candidate display, last-four redaction, explicit confirmation, and a hard stop when confidence is low. Recovery is cancellation before dialing; after dialing, record the receipt but cannot undo the call.
- cost: Negligible API cost; roughly 1–2 engineering weeks and no hardware cost.  ·  latency: Local UI inspection under 2 s; confirmation adds human latency; call initiation under 5 s after confirmation.
- security: Phone metadata remains on Mac/iPhone and is redacted in relay logs. External call placement is explicitly confirmation-required, unlike local reminders/notes.
- depends on: A typed iOS Mirroring capability (currently absent from the live route inventory); Stable Mac job receipts joined to action IDs; Pendant notification delivery via the existing inbox


## What it asked for

_Nothing._
