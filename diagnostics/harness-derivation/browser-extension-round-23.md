# Harness derivation — browser-extension — round 23

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser bridge availability** — The live browser bridge is unavailable in this round: /browser/status is offline and POST /execute browser_navigate fails after 45 seconds; the provided browser enqueue tool remains an unimplemented stub. Existing browser sessions are only historical records and cannot be read.
  - evidence: GET /browser/status at 2026-08-07T09:13Z returned online:false; POST /execute browser_navigate https://example.com returned extension offline after 45373 ms; direct browser_enqueue call returned 'no implementation yet'.

## Capabilities it proposed

### "When I highlight something in Safari and say “save this for later,” capture the exact selection with its page, timestamp, and nearby context, turn it into a short note I can hear on the pendant, and let me set a reminder from it."
- **useful because:** This turns the browser's private, already-authenticated context into a durable personal memory without making the owner retype or screenshot anything. The browser supplies exact evidence, the Mac preserves a citation, the relay makes it conversational, and the pendant makes the capture/reminder available while away from the Mac.
- **path:** browser → mac-bridge → relay → pendant → dashboard
- **model tier:** Use the cheap background model to normalize and summarize the captured text; use realtime only for the spoken command and confirmation. No model should infer missing text when the selection or page context is unavailable.
- **latency:** Selection capture should appear in the Mac workbench in under 2 seconds; a one-sentence pendant confirmation in under 1 second after the voice turn; reminder creation under 3 seconds.
- **cost:** About $0.005–$0.03 per capture depending on selection length; most cost is one background summarization call. Raw page text should not be sent to the expensive realtime tier.
- **security:** The selection may contain private or secret data. Keep the raw selection and URL on the Mac, encrypt the stored capsule, send only the minimum summary to the relay, and visibly mark the source as private. Never capture passwords or hidden page text. Creating a reminder is owner-authorized; sharing or sending the note externally would require explicit confirmation.
- **missing:** A browser-extension event/context-menu API that reports the user's selected text and page metadata (not just commands polled by the extension); A shared encrypted 'browser capsule' schema linking selection, source evidence, summary, and reminder; Pendant playback/acknowledgement of newly created note capsules

### "While I’m in a browser meeting, listen to the meeting captions privately and tap my pendant when my name, a direct question, or a new action item appears; give me a one-sentence whispered summary without speaking into the meeting."
- **useful because:** The owner currently has no discreet bridge from a private browser meeting to the wearable. This would let them stay engaged with the conversation while receiving only high-value cues, without the AI joining the call, typing into it, or exposing meeting content to other participants.
- **path:** browser → mac-bridge → mac-vision → relay → pendant
- **model tier:** Use a local lightweight caption/keyword detector for names and question boundaries, then a cheap background model for short action-item summaries. Use realtime only to deliver the low-latency pendant cue; never stream the full meeting transcript through the realtime model.
- **latency:** Detect and notify within 1–2 seconds of a captioned trigger; summarize an action item within 5 seconds. If captions are delayed or absent, state that limitation rather than guessing.
- **cost:** Approximately $0.01–$0.10 per meeting hour, dominated by optional summarization. Local keyword detection and caption transport should be near-zero API cost.
- **security:** Meeting captions are confidential and may include other people's personal or company information. Keep raw captions on the Mac in an encrypted, short-retention buffer; send only trigger windows and minimal summaries to the relay; visibly show capture state; provide one-button pause and automatic deletion after the meeting. Never answer, interrupt, type, or send anything to the meeting without a separate owner command.
- **missing:** A browser extension caption/accessible-text stream for the active meeting tab, with explicit owner start/stop state; A low-latency local caption ring buffer and semantic trigger detector; A pendant priority-notification channel that can interrupt playback discreetly and be paused locally; Meeting lifecycle detection so capture ends automatically when the tab leaves the call


## Changes it proposed to its own stack

### `browser-harness` — Add a user-selection capture channel to the Safari extension: on an explicit context-menu command or pendant-directed capture, emit a signed capsule containing selected text, page title/URL, tab identifier, capture time, and a small DOM-neighborhood excerpt. Store the raw payload locally on the Mac and pass a redacted reference plus capsule ID to the relay. Make capsule creation idempotent and allow the owner to revoke/delete it from the dashboard.
- **owner gets:** The owner can preserve exactly what they saw in a logged-in page and act on it later, instead of losing the context when a tab closes or trying to dictate long text. It creates a trustworthy bridge between private browser evidence and the always-available pendant.
- effort: Medium: Safari extension selection/context-menu handler, signed payload and encrypted local store, relay note/reminder integration, and a small dashboard review/delete view.  ·  risk: Selections can include credentials or sensitive personal data, and DOM-neighborhood capture can over-collect. Limit capture to explicit user gesture, cap excerpt size, redact password-like fields, show a preview, and make deletion idempotent. If the extension disconnects, queue locally and mark the capsule pending rather than silently dropping it.
- cost: Negligible server cost for metadata; roughly $0.005–$0.03 for optional summarization. Mac storage is small (typically under 50 KB per capsule, configurable retention).  ·  latency: Local capture is immediate; summary and pendant notification add roughly 1–3 seconds.
- security: Improves provenance and minimizes relay exposure, but introduces a new private-data path. Encrypt at rest, use per-capsule sensitivity labels, never include cookies/session tokens, and require explicit user gesture for every capture.
- depends on: An extension event/API beyond the current poll-only browser command path; Shared capsule storage and reminder integration; A reliable pendant notification/playback path

### `new-surface` — Add a private 'meeting companion' mode spanning the Safari extension, Mac, relay, and pendant: the owner explicitly starts it for the active meeting tab; the extension streams only accessible caption deltas over a local authenticated channel; the Mac keeps a bounded encrypted ring buffer and emits typed events (name mention, direct question, decision, action item); the relay sends only the selected event summary to the pendant; stopping or leaving the meeting destroys the buffer by default.
- **owner gets:** The pendant becomes a discreet second attention channel during meetings: it can alert the owner when they are being addressed or when they owe follow-up, without the AI impersonating them or making the meeting audio public.
- effort: High: accessibility/caption extraction across Safari meeting apps, local streaming and event detection, meeting lifecycle handling, pendant interruption UX, and explicit capture-state controls.  ·  risk: Caption APIs differ by meeting service, captions may be incomplete, and false alerts could be distracting. Start disabled, show a clear active indicator, provide sensitivity thresholds and pause controls, attach the exact caption excerpt to every alert, and fail closed when the tab or caption source is ambiguous.
- cost: Low to moderate per meeting; local processing should dominate, with roughly $0.01–$0.10/hour for optional summaries and negligible encrypted local storage under normal retention.  ·  latency: Caption-to-alert target 1–2 seconds; summaries up to 5 seconds. No impact when the mode is off.
- security: Creates a new sensitive meeting-data path. Require explicit start, local-first buffering, transport encryption, strict TTL deletion, per-meeting audit receipts, and no relay transmission of untriggered captions.
- depends on: Safari accessible-caption stream; Local caption ring buffer and typed event detector; Pendant priority-notification/interrupt channel


## What it asked for

_Nothing._
