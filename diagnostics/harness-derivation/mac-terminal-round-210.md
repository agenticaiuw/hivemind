# Harness derivation — mac-terminal — round 210

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Are my pendant and audio bridge healthy right now?”"
- **useful because:** This is the most useful thing the owner can do today with the hardware that is physically attached: one answer distinguishes missing USB enumeration, silent firmware, UART faults, audio framing failures, and a genuinely healthy pair instead of making the owner read two raw logs. It uses the worn device as the source of truth, the Mac as the instrument, and the relay as the durable report.
- **path:** pendant → mac-planner → relay-realtime → dashboard
- **model tier:** Background/cheap model for parsing bounded diagnostic frames; realtime only to speak the short result over the pendant.
- **latency:** Under 10 seconds for a one-shot check; 30 seconds maximum if the dual capture scripts need a fresh sample.
- **cost:** Negligible model cost for structured counters; roughly one short realtime response only when the owner asks by voice. Mac cost is two 115200-baud reads and a few KB of logs.
- **security:** USB diagnostics are local and read-only. Do not upload raw audio or arbitrary UART text; send only parsed counters, firmware versions, port identity, timestamps, and failure excerpts. Require no confirmation because it has no side effect.
- **missing:** A real host serial reader/parser (the granted mac_usb_serial_diagnostics schema remains unresolved); alternatively a typed wrapper around the existing diagnostics/dual_chip_autocapture.sh and diagnostics/start_dual_capture.sh.; A small common health-frame format emitted by both firmwares.; A relay event/report route that associates the sample with the pendant and bridge identities.

### "“Bring the useful information from the page I’m looking at into this project, with sources.”"
- **useful because:** The owner should not have to copy/paste from an authenticated Safari tab into a local project. The browser can read the session nobody else can reach, the Mac can create a durable project note, and the pendant can confirm what was saved. The result is a small cited evidence packet, not an opaque screenshot or a claim detached from its origin.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Cheap background model extracts and deduplicates page claims; realtime only handles the spoken request and final confirmation.
- **latency:** 5–15 seconds for a normal page; up to 45 seconds for a long authenticated page.
- **cost:** One low-cost extraction call plus one short spoken response. Local file creation and browser command dispatch dominate latency, not tokens.
- **security:** Keep page content on the Mac/relay boundary and transmit only selected claims, URLs, titles, and an evidence capsule. Never expose cookies or full HTML to the pendant. Show the destination project and source list in the completion receipt; writing a project file is a mutation but the owner explicitly asked for it.
- **missing:** A typed browser-to-local handoff contract that returns claims plus provenance rather than only a screenshot.; A Mac action that writes an evidence packet with stable source anchors and opens the resulting file in the active project.; A join key linking browser provenance records, the Mac job, and the spoken request.

### "“Start a bench session and tell me immediately if either chip resets, loses audio, or starts producing bad frames.”"
- **useful because:** A one-shot health answer misses the failure that happens five minutes later while the owner is wearing or testing the hardware. A bounded session would watch both serial devices and the audio pipeline, correlate reset counters and framing errors, and speak one actionable alert instead of forcing the owner to tail two terminals. The pendant supplies the physical alert and mark, the Mac samples the live USB pair, and the relay keeps the timeline.
- **path:** pendant → mac-planner → relay-realtime → dashboard
- **model tier:** No expensive model in the monitoring loop: deterministic parser and thresholds. Use a cheap background model only to summarize the session; realtime speaks only an alert or requested status.
- **latency:** First status within 2 seconds; alert within 1 second of a missed heartbeat or reset frame; sessions bounded to 30 minutes unless explicitly extended.
- **cost:** Near-zero token cost during monitoring. Mac cost is two bounded serial readers and a small ring buffer; one short summarization call at session end.
- **security:** USB logs stay local by default. Relay receives counters and fault events, not microphone payloads or unrestricted UART text. Expire raw logs after the session, retain hashes and a compact timeline. Starting/stopping monitoring is reversible and should be visible on the pendant.
- **missing:** A real typed serial-monitor capability; the current schema request is unresolved and the only available fallback is run_shell invoking existing capture scripts.; A common heartbeat/error frame from nRF9160 and ESP32, with sequence numbers and reset reason.; A streaming event channel from the Mac job to relay and pendant; current job receipts are post-hoc.; A bounded session store and dashboard timeline.

### "“I’m leaving—freeze whatever I’m doing here and give it back to me when I return.”"
- **useful because:** The owner should be able to walk away without losing the exact state of a half-finished task. The pendant provides intent, the Mac snapshots active app/window and open project state, the browser records authenticated tab/session identifiers without exporting secrets, and the relay holds a resumable handoff until the Mac is available again. On return, it restores the relevant workspace and speaks a short delta rather than making the owner reconstruct context.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Cheap background model creates the compact handoff summary; deterministic code captures and restores state. Realtime is used only if the owner asks for the spoken resume.
- **latency:** Freeze acknowledgement under 2 seconds; handoff persisted under 5 seconds; restore under 10 seconds.
- **cost:** One small summarization call per handoff. Storage is a few KB of metadata; no page HTML, screenshots, or audio need leave the Mac.
- **security:** Browser cookies and secrets remain in the browser. Persist opaque session/tab IDs, URLs, titles, project paths, and user-approved task notes only. Restoration must verify the same browser profile and active project before acting; stale sessions become a clear unavailable item, never a fabricated resume.
- **missing:** A cross-surface handoff object with capture, expiry, and restore phases.; Mac snapshot/restore actions for focused app, project, and window arrangement.; Browser tab/session checkpoint and revalidation without exposing credentials.; A relay-held handoff queue keyed to the pendant identity and a return/presence signal.

### "“Privacy mode.”"
- **useful because:** A physical, immediate command should make the whole hive stop exposing the owner's work: the Mac locks or blanks sensitive windows, Safari pauses page watches and browser commands, active voice capture stops, and the relay marks all pending outputs as held. When the owner explicitly resumes, the system reports what was held and what expired. Today these controls are fragmented across surfaces and a user cannot reliably know that one short command covered all of them.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Deterministic policy fan-out; no model is needed to enter or leave privacy mode. Realtime speaks only the terse local acknowledgement.
- **latency:** Local acknowledgement under 300 ms; Mac/browser enforcement under 2 seconds; relay state replicated within 3 seconds.
- **cost:** No model cost. A small durable state record and a handful of existing Mac/browser actions dominate implementation.
- **security:** The trigger must be a deliberate physical second-button press or a local hardware event, not an ambiguous voice command. Fail closed for outward speech and browser automation when the relay cannot confirm the mode. Never delete work; pause and expire pending actions according to policy.
- **missing:** A shared privacy-mode state machine understood by pendant, relay, Mac agent, and browser extension.; An interrupt route that cancels or pauses browser polls, page watches, speech output, and queued remote work rather than only marking a job cancelled.; A Mac lock/blank and browser redaction contract with truthful acknowledgements from every surface.; A resume report listing held, expired, and completed work.

### "“Run this while I sleep, but stop if it becomes unsafe, expensive, or different from what I asked.”"
- **useful because:** The owner cannot currently delegate a long Mac/browser task with a meaningful safety envelope: a job can run unattended, but there is no shared budget, deadline, drift detector, or trustworthy stop across the Mac, browser, relay, and pendant. This capability would let the owner delegate overnight research, cleanup, or preparation while guaranteeing that a changed page, unexpected app, excessive runtime, or network loss turns into a held result rather than silent escalation.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Cheap background model plans and summarizes; deterministic monitors enforce deadline, step count, destination scope, and network/app drift. Realtime is only for an exception alert.
- **latency:** Start acknowledgement under 2 seconds; invariant checks before every side effect; exception alert within 5 seconds; final report on completion or deadline.
- **cost:** One planning call plus optional low-cost summaries. The dominant cost is Mac/browser runtime, not tokens; relay stores a compact event log rather than transcripts.
- **security:** The owner defines the envelope in the request: deadline, allowed apps/sites, maximum steps, and whether mutations are allowed. No new approval gate is implied; this is bounded execution with automatic pause on violation. Keep credentials in the browser and redact page contents from relay logs. The pendant must say held/expired, never completed, if the relay loses contact.
- **missing:** A durable execution-envelope schema shared by POST /execute, browser commands, routines, and relay jobs.; A pre-step invariant evaluator that can observe current app, URL, page identity, network, elapsed time, and mutation count.; A real process-kill/abort path for run_shell and computer-use actions, not merely a cooperative between-step cancellation.; A cross-surface watchdog and final receipt that distinguishes completed, held, expired, and abandoned.


## Changes it proposed to its own stack

### `firmware` — Add a compact, versioned diagnostic frame emitted only on the existing USB bench UART: device ID, monotonic sequence, boot count, reset reason, audio frame counters, CRC/framing error counters, queue depth, and firmware git/build ID. Emit a heartbeat at 1 Hz and an immediate frame on reset or transport fault; never include microphone samples or secrets.
- **owner gets:** The owner can ask whether the physically connected pendant and bridge are healthy and get an answer grounded in counters, not a guess from a silent terminal. It also makes later audio continuity failures explainable instead of mysterious.
- effort: Moderate firmware work on both chips plus a small host parser and golden-frame tests.  ·  risk: UART bandwidth or timing bugs could disturb the bench path. Keep it compile-time bench-only, rate-limit frames, and fall back to the current raw logs if parsing fails.
- cost: No API cost; a few hundred bytes of flash/RAM and negligible USB bandwidth/power impact.  ·  latency: Adds at most one heartbeat interval to detection; immediate fault frames reduce alert latency.
- security: Low if the frame is bench-only and excludes payloads, credentials, and memory contents.
- depends on: A real typed serial reader or bounded run_shell wrapper on the Mac; A shared frame schema and parser; A relay event endpoint for compact health/fault events


## What it asked for

_Nothing._
## Its own summary

I discovered that both chips are represented only as expected hardware facts; the live Mac device inventory still shows Safari and the Mac bridge, not usable serial endpoints. I attempted the granted mac_usb_serial_diagnostics call and it remains genuinely unresolved because no serial capability exists in the live inventory. This round produced: (1) an owner-facing one-shot dual-chip health check, (2) a browser-authenticated page-to-project evidence handoff with provenance, (3) a continuous bench session that alerts on resets/audio faults, plus a firmware change adding compact USB-only diagnostic heartbeats and fault frames. I also notified relay-realtime that the bench session needs a compact event contract.

**Biggest unknown:** There is still no callable bounded serial reader or streaming Mac-to-relay event path. The existing dual-chip capture scripts are the fallback, but without a typed reader/parser I cannot establish live UART health or alert latency from this agent.

