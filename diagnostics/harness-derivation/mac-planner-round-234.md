# Harness derivation — mac-planner — round 234

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-permissions-live** — As of 2026-08-08T22:56Z, AI Pendant Agent has Accessibility and Screen Recording granted; synthesized input posted successfully, secure input is false, and UI actions will reach the screen. Relay and browser bridge are online; Safari has four tabs.
  - evidence: GET /ops/status HTTP 200 and GET /observe HTTP 200, plus mac_readonly_inspect(operation=running_apps) response.

## Capabilities it proposed

### ""I marked that moment on the pendant. When I get back to my Mac, show me exactly what I was doing and let me resume it.""
- **useful because:** This is the single most useful cross-node behavior: a button press on the worn device becomes a durable, privacy-preserving return point. The relay correlates the pendant bookmark with the Mac's foreground app, active browser session, meeting state, and a short owner-written label; when the Mac is available it presents a compact timeline card and can restore the relevant app/tab/files. It is materially more useful than a bare timestamp because it bridges an interruption in the physical world to the exact digital state left behind.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime only for the spoken bookmark acknowledgement; background relay correlation and ranking use a cheaper model, and deterministic Mac/browser state capture uses no model.
- **latency:** Acknowledge the button in under 300 ms locally. Persist the event within 2 s when linked. Build the return card within 5 s of Mac reconnection; restoration itself is a user-invoked action.
- **cost:** About $0.001–$0.01 per bookmark depending on whether a model is used for the optional label; state capture, correlation, and rendering are negligible. No audio needs to leave the device unless the owner explicitly enabled the existing bookmark audio option.
- **security:** Capture only app/tab identifiers, URL/title, and explicit bookmark metadata by default; redact page text and meeting content. Authenticated URLs must be stored as origin plus opaque session reference, not copied into relay logs. Restoration may open a private tab or local file and should be explicitly invoked. The current Mac FULL_CONTROL_MODE has no live approval gate, so the routine must consult the owner's future policy configuration before restoring anything.
- **missing:** A Mac context snapshot route that captures a bookmark-scoped, redacted foreground/app/browser state and returns a stable context id; A relay event type that links offline_moment_bookmark to that context id and expires it; A dashboard/card and an idempotent restore plan that can reopen the exact browser session and app state

### ""Run the pendant's audio diagnostic over USB now, collect the raw measurements, and tell me in plain English whether the whole voice path passed.""
- **useful because:** The pendant and ESP32 bridge are physically connected to this Mac today, so this turns bench hardware into a self-explanatory acceptance test instead of requiring firmware expertise. It exercises both uplink and downlink, captures sequence gaps, encode/decode time, clipping, underruns, and the 24 kHz fixture result, then gives the owner a spoken pass/fail with the failing stage and a durable report.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Deterministic parsing and threshold checks first; use a cheap background model only to turn a failed metric set into a concise explanation. Realtime is unnecessary except if the owner is asking follow-up questions live.
- **latency:** Start within 2 s, finish a normal fixture in under 60 s, and stream progress only as compact status events. Never open the microphone for this test.
- **cost:** Well under $0.01 per run; the dominant cost is Mac-side serial capture and a small optional explanation. The fixture is synthetic and sends no owner speech.
- **security:** USB serial writes must be restricted to the two known bench devices and the diagnostic command set; never expose arbitrary serial writes as a general product feature. Store raw logs locally with a short retention period, send only metrics to the relay, and require a deliberate owner command because the test produces audible fixture tones.
- **missing:** A bounded Mac bench runner that identifies /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA, starts the accepted audio_path_diagnostic_fixture, and returns exit status plus timestamps; A parser/threshold schema shared with scripts/audio-quality-probe.mjs and a relay endpoint for diagnostic receipts; A dashboard report that preserves the raw-log path locally while showing only metrics and pass/fail remotely

### ""What did the pendant and Mac agent actually access or change today? Give me a human-readable privacy and actions report, with anything sensitive redacted.""
- **useful because:** The owner currently has scattered Mac job receipts, browser command records, relay events, and device telemetry but no trustworthy cross-surface answer. This report would reconcile what was requested, what was observed, what was opened, what was mutated, and what failed—distinguishing intent from completed action. It makes an always-connected agent auditable by the person wearing it, not just by developers.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic joins, hashes, timestamps, and action classifications for the facts. A cheap background model may summarize the resulting event table; realtime is not needed.
- **latency:** On-demand report in under 10 s for one day, under 30 s for a week. Pendant voice reply should give a three-line summary first and offer the full report on the dashboard.
- **cost:** Negligible for joins and redaction; roughly $0.005–$0.03 for an optional summary depending on event volume. Keep raw sensitive payloads on the Mac and relay only redacted event metadata.
- **security:** The report itself is sensitive and must be local-first, encrypted at rest, and scoped to the owner's authenticated request. URLs, email snippets, file names, and audio identifiers need field-level redaction. Never claim an action succeeded from a plan alone: include receipt/job status and an explicit unknown state. Exporting or sharing the report must be a separate deliberate action.
- **missing:** A normalized cross-surface event envelope with request id, surface, resource class, observed/attempted/completed state, and redaction class; A relay query that joins Mac receipts/journal, browser command results, pipeline events, and pendant bookmarks without copying raw content; A dashboard timeline with filters for read, opened, mutated, failed, and unknown, plus a local export

### ""When I press the pendant button, run my 'leave work' routine on the Mac, even if another app is in front, and tell me on the pendant exactly what completed.""
- **useful because:** The pendant is the owner's only always-available intentional input, while the Mac is the only node that can change desktop state. This makes a physical press a reliable cross-device command surface: close distracting apps, save a work checkpoint, open the next workspace, or run a Shortcut without requiring the owner to find a window or speak. The pendant receives a concise success/failure result instead of leaving the owner wondering whether the Mac acted.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Deterministic command routing and Mac execution; use the realtime model only to resolve a spoken routine name when necessary. Background work and status summarization use a cheaper model.
- **latency:** Button acknowledgement under 300 ms; begin the Mac routine within 2 s; return step-level completion within 10 s for ordinary routines. Long routines should stream compact progress and remain retryable.
- **cost:** Usually below $0.01 per invocation. Most work is local Shortcut/UI execution; model cost occurs only for ambiguous natural-language routine selection.
- **security:** A physical button is an intentional trigger but must not silently authorize arbitrary destructive actions. Bind it to named owner-defined routines, include an idempotency key, and report partial completion. Do not transmit page contents or microphone data. The current missing approval/policy layer must explicitly classify each routine before unattended execution.
- **missing:** A relay event path from the pendant's offline_moment_bookmark/button event to a named Mac routine invocation; A persistent routine registry shared by pendant, relay, and Mac with idempotency and step receipts; A compact result-to-pendant delivery format for success, partial completion, and retry

### ""Turn the authenticated page I'm looking at into a private, source-linked work artifact: preserve the relevant text, citation, timestamp, and downloaded files, then open it in the app I use for notes.""
- **useful because:** The owner should be able to move knowledge from a browser session into durable local work without copy-pasting sensitive content through chat. The browser contributes authenticated context, the Mac contributes local files and destination apps, and the relay coordinates a provenance-preserving handoff. This is more than a page summary: every excerpt and file remains traceable to its source and capture time.
- **path:** browser → mac-bridge → relay → dashboard
- **model tier:** Use a cheap background model for extraction and section selection; deterministic code preserves URLs, hashes, timestamps, and downloaded-file identity. Realtime is unnecessary.
- **latency:** Capture and preview in under 5 s for a normal page; artifact generation under 20 s. Never submit forms or modify the authenticated site as part of this operation.
- **cost:** Approximately $0.01–$0.08 depending on page size and extraction; local hashing and file creation dominate latency, not API cost.
- **security:** Authenticated page content and local destination are sensitive. Keep the raw capture on the Mac, send only selected excerpts to the model, redact tokens and personal fields, and require a preview before publishing or sharing. Preserve the original URL as a protected reference rather than leaking it into broad logs.
- **missing:** A browser command that returns structured selected content plus source metadata without requiring arbitrary page scraping; A Mac-side artifact builder that writes an atomic Markdown/PDF bundle with content hashes and opens it in Notes, Obsidian, or Preview; A relay provenance object joining browser capture, model extraction, local files, and final open receipt


## Changes it proposed to its own stack

### `hardware` — Add a secure presence channel to the next pendant revision: BLE or UWB proximity to the paired Mac, backed by a secure element and a signed rotating presence token. The Mac agent should grant automation capability only while the pendant is physically nearby and immediately revoke queued high-impact actions when the token disappears. Keep LTE/audio independent so loss of proximity cannot disable emergency communication.
- **owner gets:** The owner gets a wearable, physical boundary around desktop automation. Walking away from the Mac stops pending sensitive actions; returning with the pendant restores the trusted control surface. This is a tangible privacy and safety property that software-only session state cannot prove.
- effort: High: new radio/antenna and secure-element design, pairing UX, Mac background helper, relay token verification, firmware power management, and adversarial testing for relay/replay attacks. Prototype with BLE first; production should evaluate UWB against the owner's environment.  ·  risk: False absence could revoke a long-running benign job, so jobs need checkpointing and a grace period. False presence from a nearby unattended pendant is possible; require a button press or local challenge for high-impact actions. Recovery is local re-pairing and explicit owner reset, never a silent fallback to unrestricted control.
- cost: Roughly $5–$20 incremental prototype BOM depending on UWB and secure-element choice; modest battery cost from periodic advertising/ranging. No per-invocation API cost.  ·  latency: Presence loss detected in roughly 1–3 seconds for BLE, potentially sub-second with tuned ranging; adds negligible latency to ordinary Mac actions after pairing.
- security: Strongly improves physical-boundary security, but introduces pairing keys, proximity spoofing, relay attacks, and a new sensitive signal about the owner's location. Tokens must rotate, stay local where possible, and never be logged as raw coordinates.
- depends on: A Mac policy router that consumes presence state without bypassing owner policy; A relay capability for signed device pairing and token rotation; A pendant board revision with BLE/UWB and secure storage; the current nRF9160 pendant has no suitable proximity radio


## What it asked for

_Nothing._
