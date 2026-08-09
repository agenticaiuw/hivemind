# Harness derivation — mac-terminal — round 156

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""What's running on my Mac right now, what is stuck, and if I say stop that one, stop exactly that one?""
- **useful because:** Today the relay can report a job and the Mac can execute actions, but neither gives the owner a single truthful control surface across a live shell, browser action, and computer-use loop. This would make the pendant a dependable job control tower: enumerate active work, identify it by plain-language target and current app/tab, report whether cancellation is merely requested or the child actually exited, and let the owner select one job without guessing. It is the highest-value missing capability because an autonomous assistant that cannot clearly stop or account for work is not trustworthy in daily use.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** deterministic for job enumeration, process-state and cancellation receipts; background model only to turn action labels and browser tab metadata into a short spoken disambiguation; realtime only for the spoken interaction
- **latency:** First spoken list under 500 ms from cached relay state; fresh Mac reconciliation under 2 s; stop acknowledgement immediate, with a second completion event when the child process group has really exited.
- **cost:** Usually <$0.001 per interaction because status, matching, and receipts are deterministic; occasional background summarization is the dominant cost and should be skipped for one unambiguous job.
- **security:** The relay must expose job IDs and redacted labels, never shell command strings, environment, page text, or tokens. Cancellation is a mutation but owner policy explicitly permits trusted unattended control; still report requested/confirmed/stale honestly. Process-group termination must avoid killing unrelated descendants and retain an audit receipt.
- **missing:** A real active-job registry that survives Mac-agent restart and maps local job IDs to action-ledger IDs; A cancellation endpoint that kills the run_shell child process group rather than only setting a between-step AbortController; A relay event carrying requested, process-exited, and reconciliation states; A compact browser-tab/app provenance field on every job

### ""Let me talk to you through the pendant over the Mac's USB connection even when LTE has never registered.""
- **useful because:** The nRF9160 pendant and ESP32 audio bridge are physically attached to this Mac now, while the cellular device is offline. The owner should be able to test the complete wearable interaction today instead of waiting for relay registration: press the pendant, stream audio over the bridge's serial link, use the Mac as the transport, and hear the response back on the bridge. This is not merely a link-status light; it makes the hardware useful in its actual present state and gives the system a graceful local mode when cellular is unavailable.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → new-surface
- **model tier:** realtime for the turn itself; deterministic local serial framing and buffering; background tier for optional transcript persistence after the turn
- **latency:** Button-to-recording acknowledgement under 150 ms, bridge round-trip audio under 250 ms, and first response audio under 1.5 s on the Mac's network. If the network drops, stop cleanly and retain only the turn cursor, not stale audio.
- **cost:** No new model call beyond the existing realtime turn; transport CPU and serial bandwidth dominate. Optional transcript summarization should be background and <$0.01.
- **security:** The USB serial route must be explicitly identified as the local pendant, with per-session nonce and framing CRC; never expose raw audio or relay credentials to arbitrary serial clients. Local mode should announce that it is using the Mac network and should not silently claim LTE privacy. Persist only the turn ID/cursor unless the owner asks for a transcript.
- **missing:** A production serial adapter for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA that bridges pendant audio frames to the realtime session; A local-mode session route and audio acknowledgement protocol distinct from LTE device registration; A Mac audio output path that feeds bridge playback without opening the Mac microphone; A reconnect handoff that transfers a local turn to LTE or relay exactly once

### ""Run the test/build and tell me whether it actually passed; if it fails, give me the first useful error and leave me a report I can reopen.""
- **useful because:** A failed Mac shell currently collapses to a message string: exit status is discarded, output is trimmed for the human but not stored as a durable artifact, maxBuffer can kill noisy commands, and the owner cannot distinguish a test failure from a transport timeout. This capability turns the shell into an honest diagnostic instrument. It captures exit code, signal, duration, cwd, process-tree termination, bounded head/tail plus a content-addressed full log, then speaks only the actionable diagnosis while leaving a local report available to the dashboard or browser. It is especially useful when the owner is wearing the pendant and cannot inspect Terminal.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → dashboard → browser-extension
- **model tier:** deterministic supervisor first; background model extracts the minimal diagnosis from the stored log and test conventions; realtime only speaks the short verdict
- **latency:** Return pass/fail and duration as soon as the process exits; spoken diagnosis within 2 s after that. Log writing must be streaming and bounded so a noisy build cannot hit the current 10 MiB maxBuffer failure mode.
- **cost:** <$0.001 for deterministic capture; background diagnosis is typically <$0.01 and should run only on failure or when the owner asks for explanation. Disk cost is capped per report with automatic retention.
- **security:** Redact environment variables and secret-looking lines before relay or model upload; keep the full log on the Mac by default and send only a redacted excerpt/hash. The report must state whether the command was rewritten (overlay/research interception) so the receipt cannot misrepresent what ran. No execution gates are added.
- **missing:** A spawn-based shell supervisor using argv/process groups and streaming stdout/stderr to a capped local artifact instead of exec/maxBuffer; Exit code, signal, timeout, and rewrite provenance fields in the action receipt and job result; A GET report/artifact route with retention and redaction metadata; A background diagnostic prompt that receives only the redacted failure excerpt and project context

### ""I’m screen-sharing now—make the whole hive safe to glance at, and restore everything when I’m done.""
- **useful because:** Today the browser, Mac agent, relay, and pendant each expose state independently. A billing tab, private job output, transcript, or action status can appear on the wrong surface while the owner is presenting. The owner needs one spoken/button-triggered presentation mode that coordinates all four bodies: hide or replace sensitive browser tabs, suppress private relay speech/transcripts, use a neutral pendant indicator, and restore the exact prior state afterward. This is an end-user privacy behavior, not another execution gate.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic state capture, masking, and restoration; realtime only handles the short command; no background model needed unless the owner asks why something was masked
- **latency:** Enter presentation mode in under 500 ms; restore in under 2 s; a crash must leave the Mac and browser in the last explicitly recorded state rather than guessing.
- **cost:** Near-zero model cost. Storage is a small encrypted pre-mode snapshot; browser and relay control calls dominate latency.
- **security:** The snapshot contains tab URLs/titles and active-app state, so it stays on the Mac and is encrypted. Masking must be explicit and reversible, never close or navigate tabs. The relay must not receive page text. If restoration is incomplete, the pendant must say so instead of claiming success.
- **missing:** A coordinated presentation-mode state machine spanning Mac, browser extension, relay, and pendant; Browser commands to replace sensitive tab content with a local neutral veil without destroying the authenticated session; Relay controls for transcript retention, speech verbosity, and notification suppression; A crash-safe snapshot/restore record with a visible incomplete-restore state

### ""Tell me if anything the hive did recently may have leaked a secret, and show me exactly where so I can clean it up.""
- **useful because:** The Mac shell currently inherits the entire process environment, browser receipts can contain authenticated page text, and job/log stores retain command output. There is no owner-facing answer to the most important operational question: whether a token, billing value, cookie-like string, or private page excerpt crossed from Mac to relay/model or remains in durable records. A local-first exposure report would inspect history, classify the path, redact future reads, and speak only a count and remediation steps on the pendant.
- **path:** mac-terminal → mac-planner → browser-extension → relay-realtime → dashboard → pendant
- **model tier:** deterministic local secret-pattern and provenance scan first; background model may explain remediation from redacted snippets; realtime only reports severity and asks whether to open the local report
- **latency:** Scan the recent window in under 3 s and show a severity summary immediately; full historical scan can run in background with progress events.
- **cost:** Usually no model cost; local hashing/pattern matching and a small encrypted index dominate. Background explanation is <$0.01 per finding batch.
- **security:** The scanner must never upload the suspected secret it found. Store only a salted fingerprint, location, exposure path, and redacted context. It must distinguish a false positive from a confirmed credential without attempting to log in or rotate anything automatically. Reports need owner-visible deletion and retention controls.
- **missing:** A local provenance graph linking shell env inheritance, receipt evidence, browser capsules, relay payloads, and model requests; A redaction layer applied before job results or browser evidence leave the Mac; A read-only exposure-scan route and durable finding format; A relay event for severity/counts that contains no secret material

### ""What exactly happened between my button press and that browser change? Give me the timeline, the evidence, and what was not observed.""
- **useful because:** Current records are split across pendant pipeline events, relay jobs, Mac jobs/journal, action receipts, and browser provenance. The owner cannot reconstruct causality after an unexpected result; timestamps exist but there is no cross-surface event graph, and absence is silently mistaken for success. An incident replay should correlate one turn ID across every surface, present a compact timeline, link to redacted evidence, and explicitly mark gaps such as a missing completion acknowledgement or a restarted worker.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → dashboard
- **model tier:** deterministic event correlation and evidence hashing; background model turns the resulting timeline into plain language; realtime only reads the short answer when requested
- **latency:** A recent incident report in under 2 s from local/relay indexes; older reports can stream incrementally. The first spoken sentence must include the confidence/gap status.
- **cost:** <$0.001 for correlation; background narrative generally <$0.01. No raw audio or page text needs to leave the Mac.
- **security:** Reports must use per-owner authorization and redact command arguments, environment, cookies, page text, and audio by default. Preserve hashes and metadata so evidence can be checked without exposing it. Never fill timeline gaps with model inference; label them unknown.
- **missing:** A shared correlation ID propagated from the physical button edge through relay, /execute, ledger, and browser command provenance; An append-only, clock-normalized event index across pendant, relay, Mac, and extension; Evidence links that can be opened locally with redaction and retention controls; A dashboard/pendant incident-report view that distinguishes observed, inferred, and unknown events


## What it asked for

_Nothing._
## Its own summary

I verified the live Mac is online with the browser extension online, full-control execution enabled, relay reachable, and the wearable hardware physically present even though the cellular device is offline. I produced three capabilities: a cross-surface job control tower, a USB-local conversational mode for the pendant, and an honest build/test supervisor with durable failure reports. The recorder noted that the routes I named already exist; the real work is the missing joins: active process identity and kill semantics, serial audio framing/session handoff, and streaming shell artifacts with exit-code/provenance capture.

**Biggest unknown:** The still-pending mac_usb_serial_diagnostics request is the main blocker: I cannot yet inspect or exercise the two live serial devices, verify baud/framing, or prove whether the bridge can carry audio today. I also still lack a live artifact/report route and a process-group-aware shell executor; those must be added rather than inferred from existing /execute, /jobs, and /journal.

