# Harness derivation — mac-terminal — round 238

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live browser bridge state** — Safari extension is online with 7 tabs, active tab domainagents.com, extension v1.2.0, no pending commands or spool, but lastSeenAt is ~5.5 seconds old and device nonce is empty.
  - evidence: GET /browser/status returned HTTP 200 at round 238

## Capabilities it proposed

### "Is my pendant's microphone, nRF9160 link, and ESP32 audio bridge healthy right now? If not, tell me exactly which leg failed and save a timestamped diagnostic I can hand to you."
- **useful because:** The hardware is physically present today but has no relay registration. This gives the owner a truthful bench verdict instead of guessing from a silent wearable, and turns intermittent USB/audio failures into evidence.
- **path:** pendant → mac-bridge → relay → dashboard
- **model tier:** Background/local parsing for UART and pipeline logs; realtime only to summarize the final verdict over audio if a voice session is active.
- **latency:** 10 seconds for a bounded dual-UART capture and correlation; immediate LED/status response while the capture runs.
- **cost:** Near-zero model cost when parsed locally; at most one short realtime response, dominated by the 5–10 second serial capture.
- **security:** USB logs can contain identifiers and raw diagnostic text. Keep artifacts on the Mac by default, redact tokens/IMEIs, and require explicit owner request before uploading a log to the relay.
- **missing:** A real serial reader implementation behind the currently unresolved USB diagnostic schema; A bounded parser for diagnostics/start_dual_capture.sh and diagnostics/dual_chip_autocapture.sh output; A correlation envelope tying UART timestamps to a pipeline/session ID; A relay-readable diagnostic artifact route

### "Did that action really happen? Show me the proof, not just 'completed'—check the Mac receipt, the browser's resulting state, and the pendant's last-known status, then tell me what is still unverified."
- **useful because:** A completed job currently means dispatch returned, which is not the same as the owner's intended effect. Cross-checking three physically different surfaces prevents confident false success when a browser tab changed, a Mac process failed, or the wearable lost the acknowledgement.
- **path:** pendant → mac-bridge → browser-extension → relay → dashboard
- **model tier:** Cheap background verifier for typed receipts and page fingerprints; realtime only for the owner's spoken question.
- **latency:** Under 3 seconds when receipts and browser state are cached; up to 15 seconds for a fresh browser snapshot.
- **cost:** Low: deterministic checks dominate; one small model call only when the evidence conflicts or needs a spoken explanation.
- **security:** Never send page contents merely to prove a local action. Return hashes, titles, URLs, and typed postconditions by default; require confirmation before exposing sensitive browser evidence.
- **missing:** A postcondition declaration attached to each action; A browser result endpoint that can answer a specific expected-state query, not only return a generic snapshot; A shared trace ID linking execute job, browser command, pipeline event, and pendant beacon; A verifier route that reports proven/contradicted/unverified rather than collapsing all outcomes to success

### "When I reconnect the pendant after working offline, reconcile everything I asked it to do: apply each still-valid request once, skip stale ones, and read me a short list of what was applied, skipped, or needs me."
- **useful because:** The pendant can be worn away from the Mac and already has crash-safe queued state, while the Mac and authenticated browser are only reachable later. A reconnect should be a useful handoff, not a pile of duplicate jobs or silent loss.
- **path:** pendant → mac-bridge → browser-extension → relay → dashboard
- **model tier:** Deterministic idempotency and expiry checks first; a cheap background model groups the resulting receipts into a spoken summary; realtime is only the final low-latency voice turn.
- **latency:** LED acknowledgement immediately; reconciliation within 30 seconds of a healthy bridge, with progress available without holding the voice request open.
- **cost:** Low model cost; most work is local queue/receipt reconciliation. Storage and browser polling dominate, not inference.
- **security:** Queued requests may contain private browser intent. Encrypt the pendant spool and relay handoff, bind each request to an owner/device generation, expire destructive or login-sensitive requests, and do not replay them merely because connectivity returned.
- **missing:** A reconnect reconciler consuming the pendant outbox and Mac/browser ledgers; Exactly-once keys shared across pendant, relay, Mac jobs, and browser commands; A stale-request policy based on age, tab/session generation, and expected page fingerprint; A compact spoken reconciliation receipt delivered through the existing status beacon/audio recovery path

### "While I am in a meeting, keep the pendant silent except for emergencies; watch my Mac and authenticated browser for genuinely time-critical changes, then give me one compact, prioritized debrief when the meeting ends."
- **useful because:** Today the wearable, Mac jobs, and private browser session each know fragments of urgency but cannot coordinate attention. This would protect the owner's concentration while ensuring that a critical deadline, security event, or direct human escalation is not buried in ordinary notifications.
- **path:** pendant → mac-bridge → browser-extension → relay → dashboard
- **model tier:** Deterministic quiet-hours and severity gates first; a cheap background model clusters and ranks deferred events. Realtime is reserved for the single spoken debrief when the owner ends the meeting.
- **latency:** Emergency event classification within 2 seconds; non-emergency items are held. Debrief should begin within 3 seconds of the meeting-context transition and fit under 30 seconds unless the owner asks for detail.
- **cost:** Low: event filtering and deduplication are local/deterministic; one short background summarization per meeting. Realtime cost occurs only for the final spoken digest.
- **security:** Meeting status and browser contents are sensitive. Store only event summaries and minimal evidence pointers, redact page text by default, encrypt the deferred queue, and make emergency categories explicit and auditable so the system cannot silently suppress a safety-critical alert.
- **missing:** A meeting-context signal from the Mac (calendar/foreground meeting app plus explicit pendant override); A cross-surface urgency taxonomy with source-specific rules and deduplication keys; A relay-held deferred attention queue with expiry and escalation semantics; A pendant command for enter/leave-focus mode that works offline and reports the current mode truthfully


## Changes it proposed to its own stack

### `firmware` — Add a bench-only diagnostic synchronization frame emitted by both nRF9160 and ESP32 when a physical button event or audio pipeline transition occurs. The Mac capture supervisor sends a nonce, both chips echo it with monotonic tick, firmware version, queue depth, and audio counters, and the Mac writes one correlation record alongside the UART logs. This is not a product transport; it is a deterministic calibration protocol for the existing USB bench scripts.
- **owner gets:** When audio is missing, the owner can distinguish microphone capture failure, USB framing loss, bridge playback failure, and relay absence in one test instead of mailing two unrelated logs to an engineer.
- effort: Medium: one diagnostic command/frame on each chip, a small parser, and changes to the existing dual-chip capture scripts.  ·  risk: Diagnostic frames must never enter normal LTE/audio streams. Gate them behind the existing bench build/USB command and make unknown frames safely ignored. If one chip is flashed with an old image, the Mac should report 'uncorrelated' rather than infer health.
- cost: No recurring API cost; negligible flash/RAM and no extra hardware. Adds only a few bytes per explicit bench event.  ·  latency: Adds under 100 ms to an explicit self-test, no impact on ordinary button/audio paths.
- security: Nonce and firmware metadata stay on the Mac unless the owner exports the report; do not include cellular credentials or raw audio.
- depends on: An implemented bounded USB serial reader (the currently unresolved capability request); Existing diagnostics/start_dual_capture.sh or diagnostics/dual_chip_autocapture.sh; A stable diagnostic frame schema in both firmware trees

### `integration` — Create a 'claim ledger' that records the intended effect separately from dispatch: every cross-surface request carries an intent nonce, expected postcondition, evidence sources, and an expiry. On completion, the Mac receipt, Safari state/fingerprint, pipeline acknowledgement, and pendant cached beacon independently append evidence; the ledger computes proven, contradicted, or unverified and preserves conflicts for the owner.
- **owner gets:** The owner stops hearing a reassuring 'done' when only a command was sent. They get an honest answer such as 'Mac opened the file, Safari never submitted it, and the pendant has not received completion.'
- effort: High: schema and persistence across relay, Mac agent, browser extension, and firmware beacon, plus adapters for existing job/receipt routes.  ·  risk: Evidence can become stale or disagree after a page changes. Every claim needs capture time, source generation, and expiry; never turn absence of evidence into failure. Keep the old job status as a raw fact during rollout.
- cost: Small storage growth per action; low background model cost because most verdicts are deterministic. Realtime is used only for spoken conflict summaries.  ·  latency: No added dispatch latency if evidence collection is asynchronous; a proof query may wait for one browser snapshot.
- security: Evidence capsules must default to hashes and typed metadata, with page text and screenshots opt-in. Bind nonces to the owner/device and redact credentials before relay storage.
- depends on: A shared trace/intent nonce across POST /execute, browser commands, pipeline events, and the accepted truthful_action_status_beacon; Browser postcondition/fingerprint response support; Boot-time ledger closure and interrupted-job reconciliation before claims are marked final


## What it asked for

_Nothing._
## Its own summary

Round 238 produced three owner-facing capabilities and two implementation changes: live dual-chip bench diagnosis, cross-surface proof-of-effect claims, offline reconnect reconciliation, plus synchronized bench frames and a durable claim ledger. Live discovery also confirmed Safari is online with 7 tabs and no pending commands. The USB serial diagnostic schema still has no live implementation.

**Biggest unknown:** Whether the Mac can access the two physically connected serial ports through any existing run_shell path without waiting for a real bounded serial capability; the granted serial tool remains unresolved.

