# Harness derivation — mac-planner — round 181

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-live-state** — As of 2026-08-08T01:51Z, AI Pendant Agent has Accessibility and Screen Recording, synthesized input is verified, all listed automation permissions are granted, relay and browser bridge are online, and the physical Mac bridge is reachable. GET /ops/snapshot exposes no pendant privacy/disconnect event feed or in-flight cancellation/quarantine supervisor state.
  - evidence: GET /observe and GET /ops/snapshot both returned HTTP 200 with trusted:true, eventsPost:true, screenRecording granted, relay macBridgeOnline:true, browser online, pendingCommands:0, spool:0, affinity:[]; no privacy/disconnect or supervisor fields.

## Capabilities it proposed

### "When I say “handle what’s on this page,” use the page I’m looking at, do the safe parts on my Mac, and tell me exactly what happened—even if the Mac or pendant disconnects halfway through."
- **useful because:** This is the single most useful cross-node behavior: the pendant supplies a spoken intent, the browser supplies authenticated page context, the Mac performs concrete work, and the relay preserves a resumable receipt instead of losing the task at a disconnect. Today each surface can act, but none gives the owner one truthful end-to-end outcome.
- **path:** pendant → relay → browser → mac-planner
- **model tier:** Use realtime only to capture/clarify the short spoken intent; use a cheaper background planner to extract page facts and make an action plan; use the Mac executor/browser harness for actions; use realtime or TTS only for the final one-sentence result.
- **latency:** Acknowledge on the pendant within 1 s, inspect the active tab and produce a plan within 5 s, then execute in bounded steps. A disconnect should queue the job and resume within 30 s of both nodes returning.
- **cost:** Roughly $0.01–$0.08 per task depending on page length and whether a background model is needed; browser extraction and Mac execution dominate latency, not speech.
- **security:** Authenticated page contents leave the browser only as redacted structured facts; passwords, payment fields, and tokens never enter relay memory. Sending mail, deleting files, purchases, or external submissions require the owner's existing confirmation policy. Every step needs an idempotency key and a receipt; a stale tab or changed page must pause rather than guess.
- **missing:** Durable cross-node action journal with step-level idempotency and resume semantics; Browser read/extract result bound to a tab revision, not merely a URL; Supervisor cancellation/quarantine signal for an in-flight job when the pendant privacy latch or browser session disappears

### "Run a silent pendant health check tonight, correlate the USB serial audio/diagnostic counters with the Mac and relay logs, and leave me a short report plus a playable explanation only if something is wrong."
- **useful because:** The owner has already had multiple audio regressions where a bench test would have caught the defect. This combines the physically attached pendant and bridge, Mac-side collection, relay history, and the diagnostic fixture into preventive maintenance rather than waiting for a bad call.
- **path:** pendant → relay → mac-planner
- **model tier:** Use firmware deterministic diagnostics and a cheap background model to compare counters against acceptance thresholds; reserve realtime only if the owner asks follow-up questions. No microphone content is captured.
- **latency:** Arm over USB serial after the owner schedules it, run in under 2 minutes, and write the report within 10 seconds. It must abort immediately on a call or privacy latch.
- **cost:** Under $0.01 per run if thresholds are computed locally; storage and serial transfer dominate, not model inference.
- **security:** Synthetic fixtures and counters only—never ambient audio. The report may contain device identifiers and timestamps, so redact them from spoken output and retain raw logs locally unless the owner explicitly enables upload. A diagnostic must not interrupt an active conversation or change the audio profile permanently.
- **missing:** A live Mac USB-serial exchange capability for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A scheduled diagnostic runner that invokes audio_path_diagnostic_fixture and records an atomic receipt; Relay route to compare fixture telemetry with prior calls and classify regressions

### "If I press the pendant’s privacy latch, stop anything the browser or Mac is doing for me, quarantine any results, and let me resume later without losing the task."
- **useful because:** A local privacy latch currently protects microphone and playback, but a browser or Mac job could still be reading or mutating authenticated data. This makes privacy physical and end-to-end: one local action immediately cuts off every other surface, while durable state prevents a half-finished task from silently continuing or being lost.
- **path:** pendant → relay → browser → mac-planner
- **model tier:** No model is needed for the stop path: firmware emits a signed latch transition, relay supervisor cancels/quarantines jobs, and browser/Mac agents acknowledge. A cheap background model may summarize the quarantined receipt later; never invoke realtime during the latch.
- **latency:** Local mute/LED response is immediate; relay fan-out and acknowledgements within 1 second when connected. Offline, the pendant remains latched and queues the transition for reconciliation.
- **cost:** Negligible inference cost; the work is protocol and supervisor implementation. A later resume summary costs under $0.01.
- **security:** The stop event must be authenticated, monotonic, and replay-resistant. Quarantine means no page text, screenshots, audio, or action outputs are spoken or uploaded while latched. Cancellation must be best-effort but explicit: destructive actions already committed need a receipt, and resume must revalidate the page/tab revision rather than replay blindly.
- **missing:** Authenticated pendant privacy/disconnect event route into the relay supervisor; Cross-node cancellation and quarantine semantics for Mac and browser jobs, including an acknowledgement deadline; Resume capsule containing step state, touched resources, and tab/document revision

### "Whenever you tell me something important or take an action for me, let me ask “why?” and hear the exact source, timestamp, page or message it came from, what was inferred, and whether that source has since changed."
- **useful because:** Today the hive can read one surface and act on another, but the owner cannot audit the chain of evidence across them. A provenance answer would make spoken summaries and autonomous actions trustworthy instead of opaque—especially when browser pages, mail, calendar, and local files disagree.
- **path:** pendant → relay → browser → mac-planner
- **model tier:** Use deterministic source fingerprints, timestamps, and action receipts for the audit trail. Use a cheap text model only to explain the already-recorded chain in one spoken sentence; realtime is unnecessary except for the owner’s follow-up question.
- **latency:** Record provenance inline without delaying actions by more than 100 ms. Answer a “why?” question in under 3 seconds from the durable ledger, even if the original browser tab is closed.
- **cost:** Below $0.01 per explanation; storage and hashing dominate. No raw page or mail body needs to be resent when a source fingerprint is sufficient.
- **security:** The ledger must contain redacted source identifiers and hashes, not passwords, full private messages, or screenshots by default. Provenance must distinguish observed facts from model inferences and must mark stale or inaccessible sources instead of fabricating continuity.
- **missing:** A cross-surface provenance ledger with source hashes, observation timestamps, inference boundaries, and action links; Browser and Mac agents emitting stable redacted source references rather than only final text; A relay query that can retrieve and speak a provenance chain to the pendant

### "When my pendant is plugged into my Mac, let me use it as a full voice terminal even when LTE has not registered; automatically use USB for audio and control, then hand the same conversation back to LTE when cellular returns without dropping context."
- **useful because:** The hardware is physically attached today, but the pendant is effectively unusable as a wearable voice endpoint until relay registration succeeds. A tethered mode would make the device useful immediately at a desk and provide a deterministic fallback in dead zones, while preserving one conversation rather than creating duplicate sessions.
- **path:** pendant → mac-planner → relay
- **model tier:** Use deterministic transport/session management and the existing 24 kHz audio path. Use realtime only for the actual live conversation; no background model is needed for handoff. The relay must preserve the session identifier while changing transports.
- **latency:** USB audio/control setup within 2 seconds of attachment; conversational round-trip should stay under 500 ms locally. LTE takeover should occur at packet boundaries with at most one lost audio frame and no repeated response.
- **cost:** No per-turn inference increase; USB framing and relay session bookkeeping are the main engineering cost. Existing realtime inference remains the dominant API cost.
- **security:** Pair the USB serial devices to the owner’s Mac and authenticate every session; never accept arbitrary serial commands as relay instructions. On handoff, deduplicate packets using sequence numbers and clear any buffered microphone audio after session termination. The privacy latch must stop both USB and cellular paths.
- **missing:** Live authenticated USB-serial transport for the nRF9160 and ESP32 bridge; Pendant firmware transport abstraction supporting USB tether and LTE with one sequence space; Relay session migration and duplicate suppression across transport changes

### "If my calendar, mail, and an authenticated web page disagree about a time, person, or deadline, tell me there is a conflict, show the competing evidence, and ask one short question instead of silently choosing."
- **useful because:** Cross-node automation is dangerous when each surface is individually plausible but jointly inconsistent. The owner needs conflict detection, not another summary: a browser deadline, a calendar move, and an unread reschedule message should be reconciled before the Mac creates reminders or takes action.
- **path:** pendant → relay → browser → mac-planner
- **model tier:** Use deterministic entity/time normalization and source timestamps first; use a cheap background model to cluster references and phrase the single clarification. Use realtime only to ask and capture the owner’s answer.
- **latency:** Detect conflicts during brief preparation in under 2 seconds and ask one spoken question within 3 seconds. Never block unrelated work while waiting; retain the unresolved item for later.
- **cost:** Under $0.02 per conflict; normalization and source reads dominate, with model cost only for ambiguous language.
- **security:** Read only by default and redact unrelated mail/page content. Never infer that a newer source is authoritative without recording that rule. Any action depending on the unresolved fact must remain a draft until the owner answers.
- **missing:** Cross-surface entity and temporal conflict index; Source-authority and freshness policy configurable by the owner; A pendant clarification channel that stores the answer and binds it to the pending Mac/browser plan


## What it asked for

_Nothing._
