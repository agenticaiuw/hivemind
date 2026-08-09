# Harness derivation — relay-realtime — round 172

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Summarize what I was doing and what’s next, using my recent voice commands and Mac activity."
- **useful because:** It helps the owner resume work quickly after interruptions, especially when switching between pendant voice and desktop work.
- **path:** relay → mac-bridge → browser
- **model tier:** Cheaper background tier can compile context; realtime reads the summary aloud on request.
- **latency:** A second or two for a cached summary; longer if it needs to compile from scratch.
- **cost:** Moderate: reading recent jobs/journal plus optional browser context, then summarization.
- **security:** Summaries can expose private content. Keep them local unless the owner explicitly asks to share; redact obvious secrets; let the owner interrupt or request a shorter version.
- **missing:** A durable, privacy-scoped context graph that spans relay voice history and Mac job history without resending everything each turn; Clear policy for what sources are included by default and what requires opt-in

### "Diagnose my audio path and connection right now and suggest the fastest fix."
- **useful because:** When voice feels flaky, the owner needs a quick, actionable check. This saves time and frustration and keeps confidence high.
- **path:** pendant → bridge → relay → mac-bridge
- **model tier:** Realtime can run the checklist and narrate; heavy analysis can be offloaded to cheaper tier if logs are large.
- **latency:** Under 5 seconds for a basic check; longer only if fetching logs or running a test.
- **cost:** Low: a few status reads and a short spoken response.
- **security:** Diagnostics may include device identifiers and network state; keep it minimal and avoid logging extra sensitive metadata.
- **missing:** A unified health endpoint or tool that can read pendant/bridge health from the relay without relying on LTE registration; Standardized diagnostic signals from pendant firmware and bridge, plus a readable log path

### "“When I say ‘submit this application’, use the authenticated browser session to fill the form from the details I dictate, read back every consequential field, and submit only after I give the exact spoken confirmation; if the browser or Mac disappears, resume from the last verified field later.”"
- **useful because:** The owner can complete bureaucratic web work while away from the desk without repeatedly finding the right tab, while retaining a precise spoken checkpoint before an irreversible submit. Today the pieces can drive a browser or Mac, but no single workflow carries dictated data, field-level verification, interruption, and resumable state across them.
- **path:** pendant → relay → browser → Mac → dashboard
- **model tier:** Realtime handles short dictation, disambiguation, and read-back; a cheaper background planner validates field types and maintains the resumable form state; browser automation performs the authenticated interaction.
- **latency:** Under 1 second for each spoken acknowledgement; 2–5 seconds per browser field batch; a reconnect should restore state within 10 seconds.
- **cost:** Approximately $0.03–$0.15 per application depending on dictation and verification length; browser session time and repeated model context dominate.
- **security:** Form contents and dictated personal data leave the pendant for relay processing and enter the authenticated browser session. Persist only encrypted field state, redact secrets from logs, and require exact spoken confirmation immediately before submit. Recovery must never blindly resubmit a possibly duplicated transaction.
- **missing:** A typed form-state protocol with field provenance and idempotency keys; Browser-side DOM labels/values returned in a stable schema rather than screenshots alone; Durable resumable jobs and a relay-to-pendant checkpoint delivery path; A confirmation phrase matcher bound to the specific form hash

### "“Keep an eye on the thing I just asked you to do, and tell me only when its outcome changes or it needs me”—for example, a delivery, refund, application, or support case—using the authenticated browser, not a one-time lookup."
- **useful because:** Today the owner must remember to ask again and the relay cannot reliably distinguish an unchanged page from a meaningful state transition. This would turn a one-shot voice request into a useful, quiet watch that reports only evidence-backed changes and lets the owner query the latest snapshot from the pendant.
- **path:** pendant → relay → browser-extension → browser → dashboard
- **model tier:** Cheap scheduled/background extraction compares normalized page facts; realtime is used only to explain a detected transition in one or two spoken sentences.
- **latency:** Initial setup under 5 seconds; checks may run on a configurable cadence; notification delivery within 30 seconds of a detected change when the browser/Mac is reachable.
- **cost:** Roughly $0.001–$0.02 per check with DOM extraction and a small comparison model; authenticated browser availability and polling frequency dominate.
- **security:** The watch can access private authenticated pages and could expose sensitive changes through a spoken alert. Encrypt snapshots, retain only selected fact fields, provide one-tap spoken pause/delete, and suppress values classified as secrets. Never treat cosmetic page changes as an event.
- **missing:** A real scheduler/ Durable Object alarm and durable watch records; Authenticated browser page-watch execution with session affinity and normalized selectors; Change classification, deduplication, expiry, and quiet-hours policy; Reliable push of alerts to the pendant inbox

### "“Give me a private two-person handoff: record what I tell you, turn it into a concise action brief with links and open questions, and deliver it to the right authenticated channel; tell me when the recipient actually opened or replied.”"
- **useful because:** The pendant is excellent for capturing a thought while walking, but today it cannot carry that thought through composition, authenticated delivery, and verified follow-up without the owner returning to the Mac. This joins wearable capture, relay drafting, browser sessions, and Mac context into a genuinely mobile handoff rather than another voice memo.
- **path:** pendant → relay → Mac → browser-extension → browser → dashboard
- **model tier:** Realtime transcribes and asks only essential clarifying questions; a cheaper background model drafts and extracts action items; the browser/Mac agent performs delivery and reports provider evidence.
- **latency:** Capture acknowledgement immediately; draft in under 20 seconds; delivery in under 60 seconds; follow-up alerts only on actual open/reply events.
- **cost:** About $0.05–$0.30 per handoff depending on audio length and draft complexity; authenticated channel automation and event monitoring dominate.
- **security:** Private audio, contacts, and message content cross the relay and may be sent to a third party. Require recipient/channel disambiguation, show a spoken summary before send, encrypt transient artifacts, and never claim opened/replied without provider evidence.
- **missing:** Cross-provider compose/send adapters with recipient identity resolution; A durable handoff object linking audio, draft, sent message, and provider event IDs; Authenticated event/watch support for open and reply state; A policy for expiration, redaction, and spoken notification

### "“Keep this private: use my Mac and authenticated browser if needed, but do not send the audio or its contents to the cloud model; tell me immediately if the task cannot be completed under that boundary.”"
- **useful because:** The owner can use the wearable for sensitive work without choosing between convenience and confidentiality. Today the relay is the low-latency voice front door and has no enforceable per-utterance locality boundary; it cannot truthfully guarantee that a sensitive request stayed on the Mac/browser.
- **path:** pendant → relay → Mac → browser-extension → browser → dashboard
- **model tier:** A tiny realtime classifier handles the explicit privacy phrase; all transcription, planning, and extraction for that turn run on the local Mac agent. The relay only transports opaque encrypted audio and typed status, not plaintext content.
- **latency:** A privacy-mode acknowledgement under 500 ms; local transcription and action latency within 2–10 seconds depending on the task; fail closed immediately if the Mac/browser is unavailable.
- **cost:** Near-zero cloud model cost for private turns; local Mac CPU and encrypted transport dominate. A small per-session policy record costs negligible storage.
- **security:** The relay must not log raw audio, transcripts, prompts, URLs, or action arguments for private turns. Use an authenticated device-to-Mac key, explicit mode indicators on the pendant, fail-closed routing, and an auditable receipt proving which surfaces handled the request. Browser page content still leaves the browser to the local Mac process.
- **missing:** A device-bound end-to-end encrypted audio channel terminating at the Mac; A privacy-mode session bit carried through every relay, planner, browser, and receipt route; Local speech-to-text and local intent parsing on the Mac; Redacted telemetry and a verifiable fail-closed receipt


## Changes it proposed to its own stack

### `integration` — Wire job completion to the existing offline alert inbox path: when a job transitions to complete/failed/needs_attention, generate a short spoken summary server-side and enqueue it as an alert for delivery to the pendant when available.
- **owner gets:** The owner gets timely updates without polling, and it works even when the Mac is offline or the session ended.
- effort: Medium to high: requires monitoring job state, generating speech, and using the existing inbox mechanism instead of inventing a new queue.  ·  risk: Medium: risk of noisy or sensitive notifications. Mitigate with default minimal messages and opt-in verbosity.
- cost: Moderate: status monitoring plus TTS generation per completion.  ·  latency: Completion alerts can be delivered asynchronously; no impact to interactive latency.
- security: Ensure summaries avoid sensitive content; allow per-task notification preferences.
- depends on: A durable job monitor (scheduler or durable object alarms); A real implementation of relay_event_push or equivalent delivery mechanism

### `model-routing` — Introduce a tiered routing policy: realtime model for conversational control and quick confirmations; cheaper background model for planning, monitoring, summarization, and diagnostics. Include explicit handoff markers so context is not resent.
- **owner gets:** Lower cost and more responsive voice interaction, with complex work handled efficiently in the background.
- effort: Medium: requires orchestration changes and context packaging.  ·  risk: Medium: handoff bugs could drop tasks. Mitigate with receipts and job status checks.
- cost: Potentially significant savings by keeping the expensive tier out of background work.  ·  latency: Improves interactive latency; background work may take longer but is acceptable.
- security: Limit context shared across tiers; send only what’s needed, and avoid sensitive content unless required.


## What it asked for

_Nothing._
