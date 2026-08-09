# Harness derivation — mac-terminal — round 162

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Make the pendant sound wideband, and tell me if the link is degrading.""
- **useful because:** This is the owner's explicit highest-priority ask and the single most valuable daily improvement: natural speech plus an honest quality indicator instead of metallic audio and silent stalls. It only works as one system: the nRF9160 captures/plays, the ESP32 bridge resamples and transports USB audio, the Mac/relay negotiate a 24 kHz codec and stream telemetry, and the pendant's existing recovery beacon reports truth.
- **path:** pendant → relay-realtime → mac-planner → dashboard-ux
- **model tier:** Realtime only for turn audio; deterministic DSP/resampling and a cheap background monitor for MOS/jitter summaries.
- **latency:** <120 ms capture-to-relay and <150 ms relay-to-playback; quality telemetry every 500 ms without adding turn latency.
- **cost:** Negligible inference cost beyond current realtime turns; engineering cost is codec/clock and framing work. Optional background summarization is <$0.01/day.
- **security:** Audio leaves the Mac only over the existing authenticated relay; telemetry contains timing and device identifiers, not transcript. Persist only rolling quality counters; confirmation unnecessary for transport changes.
- **missing:** 24 kHz superwideband codec negotiated end-to-end; ESP32 USB serial audio framing and clock-drift correction; relay pipeline audio format declaration plus PLC/jitter buffer; Mac local-agent audio-device selection for the bridge; a dashboard waveform/latency and packet-loss view

### ""When the pendant or Mac breaks, file a useful bug report and tell me what failed.""
- **useful because:** Today a UART failure, relay timeout, or failed Mac shell job is split across logs and often loses the decisive context. A single spoken request should produce a timestamped, redacted incident bundle: device/link state, pipeline turn, Mac job receipt, exact exit status, and a short diagnosis, then save it as a draft for the owner.
- **path:** pendant → relay-realtime → mac-terminal → mac-planner → dashboard-ux
- **model tier:** Deterministic collection first; background model classifies the incident and drafts one short report. Realtime is only used if the owner asks for an immediate spoken explanation.
- **latency:** Capture bundle in <2 s; draft in <30 s; never block active audio on report generation.
- **cost:** <$0.01 per incident for background classification; storage is a few KB per report. Main cost is implementing a redacted cross-node schema.
- **security:** Redact bearer/API keys, environment variables, cookies, and raw audio before leaving the Mac. Save as a local draft, never send externally without confirmation. UART logs may contain sensitive commands.
- **missing:** cross-node incident ID and clock-skew normalization; shell receipt fields for exit code, pid, argv/env redaction and duration; firmware UART log export trigger and bounded ring buffer; relay endpoint to assemble device plus Mac evidence; draft report writer in ~/AI-Pendant-Workspace

### ""Resume the thing I was doing when I put the pendant down.""
- **useful because:** A worn-device handoff should restore the owner's actual work, not merely repeat a transcript: the Mac foreground app and project, the authenticated Safari tab/session, the last pending Mac job, and the pendant's turn/bookmark are joined into one resumable checkpoint. The pendant supplies the physical interruption point; browser sessions supply access the cloud cannot have; the Mac performs the safe reopen/focus actions.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard-ux
- **model tier:** Deterministic checkpoint capture and action replay; cheap planner only resolves ambiguity among multiple recent checkpoints.
- **latency:** Checkpoint <1 s after button event; spoken resume summary <3 s; reopening/focusing apps <5 s.
- **cost:** Near-zero model cost for one checkpoint; <$0.01 only when ambiguity requires planning. Storage is <10 KB per checkpoint with a 20-item retention cap.
- **security:** Store opaque browser session/tab IDs and metadata, never page contents or cookies in relay memory. Require confirmation only for replaying mutations; opening/focusing and reading are fine under owner policy.
- **missing:** Mac hook that captures foreground app, active project and pending job at the pendant timestamp; browser checkpoint endpoint joining tab/session affinity to the checkpoint; resume token persisted in pendant OUTBOX for USB/LTE delay; typed replay receipt that reports each reopen/focus outcome; clock synchronization between pendant, Mac and relay

### ""While I was away, give me one honest sentence about everything you changed, opened, or failed to do across my Mac, browser, and pendant.""
- **useful because:** Today action history is fragmented across Mac jobs, browser commands, relay work, and device state. The owner cannot reliably know what happened while they were away without manually inspecting several logs. A signed cross-surface change digest would make the system accountable in the one form the owner actually uses: a short spoken sentence, with drill-down only on request.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard-ux
- **model tier:** Deterministic event folding and deduplication first; a cheap background model compresses the final ordered events into one sentence. Realtime only speaks the already-built digest.
- **latency:** Continuously fold events with no user-visible delay; answer in under 1 second from cached state and under 3 seconds if a fresh Mac/browser poll is needed.
- **cost:** Near-zero inference for the common deterministic path; <$0.005 for an occasional background compression. Retain compact event hashes and summaries, not full transcripts or page contents.
- **security:** The digest must respect source sensitivity: do not quote private page text, email bodies, shell secrets, or audio. Store only redacted labels, effect class, outcome, timestamp, and source. Browser session identifiers remain local to the Mac; relay receives opaque event IDs. No confirmation is needed to read the digest.
- **missing:** a shared append-only event envelope emitted by relay jobs, Mac action receipts, browser commands, and pendant transport state; cross-node monotonic ordering with clock-skew correction and exactly-once event IDs; a redaction layer that classifies sensitive labels/output before aggregation; a durable per-owner unread cursor so the pendant can distinguish already-reported from new changes; a compact spoken-digest endpoint and on-demand drill-down mapping to source job/receipt IDs


## Changes it proposed to its own stack

### `mac-harness` — Make shell execution produce a truthful immutable execution envelope before and after dispatch: preserve the submitted action and any rewrite, record argv-equivalent tokenization (or explicitly mark shell-string), cwd, allowlisted env names with secret values hashed/redacted, pid, start/finish/duration, numeric exit code/signal, timeout classification, stdout/stderr byte counts plus capped excerpts, and join the envelope to the job and action-ledger IDs. Wire AbortController.signal into the child process, close the ledger on every terminal path, and reconcile processing jobs at boot as interrupted.
- **owner gets:** When the owner asks what happened, the pendant can answer precisely whether the command ran, timed out, was rewritten, or died, and can recover an interrupted multi-step task instead of confidently reporting a stale 'running' job. This makes maximum-access shell materially more dependable without adding gates.
- effort: Medium: replace exec with spawn/execFile-compatible capture while retaining arbitrary shell strings, extend receipts and ledger joins, add boot reconciliation and signal wiring, then test rewrite and crash paths.  ·  risk: Changing process invocation can alter quoting and shell behavior; preserve an explicit shell-string mode and regression-test existing commands. Killing a process tree may leave grandchildren; use process groups and mark uncertain cleanup. Reconciliation must never replay a side effect automatically.
- cost: No model cost; a few KB per job and modest CPU for capture/redaction.  ·  latency: Negligible for short commands; spawn and receipt writes add tens of milliseconds.
- security: Improves auditability while keeping owner-requested unrestricted execution. Never persist secret env values or shell output beyond existing caps.
- depends on: existing action receipts and action ledger; jobTracker durable records; a verified process-group cancellation implementation


## What it asked for

_Nothing._
## Its own summary

This round produced three end-user capabilities and one Mac harness change. The strongest is the end-to-end 24 kHz superwideband path with live degradation truth, spanning the physically connected nRF9160 pendant, ESP32 bridge, Mac agent and relay. I also proposed cross-node incident reports that turn UART/link/Mac failures into redacted drafts, and a pendant-triggered resume checkpoint joining Mac project state, Safari session affinity, pending jobs and the existing moment marker. Finally, shell execution now has a concrete observability/recovery change: preserve rewrites, exit/signal/PID/timing, redacted environment metadata, job-ledger joins, real cancellation, ledger closure and boot reconciliation without adding gates.

**Biggest unknown:** The remaining blocker is physical/audio-path truth: I still need a live USB-serial diagnostic implementation that can identify the nRF9160 and ESP32 ports, framing/clock status and actual 24 kHz capability. The granted diagnostics resolver cannot perform audio_devices, and the previously requested mac_usb_serial_diagnostics is still queued. Until that exists, codec and bridge claims are design requirements rather than measured facts.

