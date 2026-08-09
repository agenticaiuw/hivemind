# Harness derivation — mac-planner — round 260

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-accessibility-live** — AI Pendant Agent currently has Accessibility and Screen Recording, synthesized input is verified, Safari is foreground, and the pendant's two USB serial devices are physically expected but no serial route is exposed in the live inventory.
  - evidence: mac_readonly_inspect foreground_app/running_apps returned GET /observe HTTP 200 at 2026-08-09T00:42:48Z with accessibility.trusted=true, screenRecording=true, inputReachability.status=verified; system hardware/live note identifies /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA.

## Capabilities it proposed

### "Run a complete pendant audio health check while it is USB-connected, then tell me whether the microphone, modem path, codec, and speaker passed and leave the raw measurements plus a concise report in my workspace."
- **useful because:** The pendant is physically on this Mac now, and audio failures are hard to localize. One command should exercise both directions and produce evidence instead of another subjective listening test.
- **path:** pendant → mac-planner → relay → dashboard
- **model tier:** background model for interpreting bounded fixture metrics; no realtime model needed
- **latency:** Start within 5 seconds and finish in 1–3 minutes; report partial results if the cable or board disappears.
- **cost:** Under $0.02 for summarization; most time is the on-device fixture and serial capture. Storage is a few KB per run.
- **security:** The fixture must use synthetic audio only and never capture or persist microphone content. Shell execution must be a named, fixed diagnostic command, not arbitrary user text. Raw logs stay in ~/AI-Pendant-Workspace.
- **missing:** a named Mac bench command that arms audio_path_diagnostic_fixture over the two USB serial ports and validates its sequence numbers; a parser that emits a stable JSON result and marks cable loss versus codec failure; relay ingestion of the report and a small history view

### "If an overnight pendant test is interrupted, resume it from the last completed fixture and deliver one final report instead of rerunning completed tests or leaving half-written files."
- **useful because:** USB bench runs can be interrupted by a reboot, cable movement, or a sleeping Mac. Idempotent resume turns a fragile lab procedure into something the owner can trust unattended.
- **path:** pendant → mac-planner → relay → dashboard
- **model tier:** cheap background orchestration; use the expensive model only to explain an abnormal final result
- **latency:** Checkpoint after every fixture stage; resume automatically within 30 seconds of the Mac returning, with a final report when all stages finish.
- **cost:** Near-zero model cost for normal runs; a few cents only when abnormal logs need explanation. Disk usage is bounded by one staged result bundle per job.
- **security:** Use a per-run job ID and atomic staging. Never treat a partial serial log as a pass. Keep raw diagnostic data local and expose only counters and failure reasons upstream.
- **missing:** a Mac-side serial harness that can reopen the two known USB ports and continue by sequence number; a durable stage manifest shared with the relay; a watchdog that distinguishes cable loss from board reset

### "Show me whether my pendant's audio path is getting worse over time, with a simple trend across its last ten USB diagnostic runs and the first metric that changed."
- **useful because:** A single health check can pass while latency, drops, or decode CPU slowly regress. A trend tells the owner when to reflash, replace a cable, or stop trusting the device before a conversation fails.
- **path:** pendant → mac-planner → relay → dashboard
- **model tier:** cheap background aggregation for numeric trends; use the expensive model only to explain a genuinely novel anomaly
- **latency:** Under 5 seconds for the dashboard view and under 30 seconds after a new diagnostic completes.
- **cost:** Negligible for aggregation; at most $0.01 for an anomaly explanation. Raw run records are small JSON and retained locally.
- **security:** Synthetic fixture metrics only; do not upload microphone samples or full UART logs by default. Dashboard should show timestamps and counters, not serial identifiers or filesystem paths.
- **missing:** a stable schema and run identifier for audio_path_diagnostic_fixture results; a Mac collector that uploads only summarized counters after each USB run; a dashboard trend route with thresholds calibrated to the measured 24 kHz acceptance criteria

### "Give me a private end-of-day data-exposure report: which pendant audio events, browser pages, calendar/mail fields, and Mac files were used by the system, what left the Mac, what was redacted, and what was deleted or retained."
- **useful because:** Today the owner can use the hive but cannot inspect its complete data trail. A factual report would make an always-listening, browser-connected system auditable instead of trust-based.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** cheap background aggregation for the ledger; realtime is unnecessary
- **latency:** Generate in under 30 seconds after request; maintain append-only events during the day with no conversational delay.
- **cost:** A few cents per daily report at most; storage and event signing dominate, not model inference.
- **security:** The audit ledger itself is sensitive and must stay encrypted locally by default. Hash URLs and file paths unless the owner explicitly expands them. Never log raw microphone audio, passwords, or page bodies. Export requires explicit confirmation.
- **missing:** a shared provenance event schema emitted by pendant, relay, Mac, and browser; local append-only encrypted storage with retention and deletion receipts; a redaction-aware report generator and dashboard view; transport metadata proving whether an item stayed local or crossed the relay

### "Before carrying out a sensitive browser or Mac action I requested by voice, show me the exact page, account, and target that will be changed, bind my pendant button press to that snapshot, and refuse the action if the page changed before execution."
- **useful because:** A spoken approval is unsafe when a tab, account, or DOM target goes stale. This would make the physical pendant a meaningful final authorization for the exact operation rather than a general 'yes'.
- **path:** pendant → relay → browser-extension → mac-planner → dashboard
- **model tier:** realtime for the short confirmation exchange; deterministic code, not a model, validates the snapshot and token
- **latency:** Preview within 2 seconds, allow a 15-second button confirmation window, and execute immediately only if the snapshot hash still matches.
- **cost:** Under $0.01 per confirmation; browser snapshotting and signed-token storage dominate.
- **security:** Never transmit secrets or full page bodies. Bind a one-use nonce to account/session, URL origin, target identity, action hash, and expiry. Destructive actions remain denied unless the owner explicitly confirms on the pendant.
- **missing:** a relay-minted one-use action capability token understood by both browser and Mac; browser/DOM target hashing and a pre-execution revalidation hook; pendant firmware support for displaying/indicating a pending exact-action token and accepting a one-press confirmation; a durable receipt proving the approved snapshot equals the executed snapshot

### "When my Mac is asleep or disconnected, let the pendant queue a small set of explicitly authorized routines, then run each one exactly once when the Mac and relay return and tell me which completed, which expired, and which were skipped."
- **useful because:** The pendant is worn away from the Mac, but today's routines disappear across a disconnected period. Durable intent would let the owner capture a time-sensitive action in a dead zone without pretending the action already happened.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** cheap background job orchestration; no realtime model needed
- **latency:** Queue locally in under 1 second; dispatch within 10 seconds of reconnection; expire stale intents deterministically.
- **cost:** Negligible model cost; bounded queue and receipts are the main resource.
- **security:** Only named, pre-authorized routine IDs may queue offline; never queue arbitrary shell, purchases, mail sends, or destructive mutations. Encrypt the queue, include expiry and idempotency keys, and report failures rather than retrying forever.
- **missing:** a firmware queue type for authorized routine intents distinct from voice memos and alerts; relay-side idempotency and expiry semantics across reconnects; Mac routine execution that accepts a signed intent and emits a durable receipt; owner-configurable allowlist of routines permitted to run unattended


## What it asked for

_Nothing._
## Its own summary

Discovered the live Mac state and produced three non-duplicate capabilities: a complete USB pendant audio health check, resumable/idempotent overnight fixture runs, and a ten-run audio regression trend. The bookmark-context idea collided with an existing resume-bookmark capability and was not restated. Accessibility and Screen Recording are now live and input reachability is verified.

**Biggest unknown:** The live inventory still lacks a confirmed bidirectional USB-serial harness and I do not yet know the relay's exact ingestion route for audio_path_diagnostic_fixture results; /workbench/contexts and /workbench/jobs/:jobId/handoff need route-level confirmation.

