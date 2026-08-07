# Harness derivation — faculty-perception — round 130

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-action-trust** — At 2026-08-07T18:34Z, mac-agent /ops/status and /observe both report Accessibility trusted=false, Screen Recording granted=false, inputReachability.status=failed, and ui_actions_will_reach_the_screen=false. Browser extension is online with 3 tabs, but its active tab 901786 is https://example.com titled 'Failed to open page'.
  - evidence: GET /ops/status and GET /observe responses at 2026-08-07T18:34Z
- **telemetry-lineage** — The live Mac bridge is online and relay reachable, but /pipeline includes historical-looking nrf9160 and cloud-relay records marked processing despite no nRF device in the live device table; one audio-native record reports 15,625 Hz input while current TTS output is 24,000 Hz.
  - evidence: GET /ops/status, GET /pipeline, and discover(devices) at 2026-08-07T18:34Z

## Capabilities it proposed

### "“Before you brief me or act, tell me what is genuinely live right now, what is historical, and what is contradicted.”"
- **useful because:** The system currently exposes contradictory realities: the relay advertises pendant telemetry while no pendant is registered; pipeline records an nRF event and 15,625 Hz audio as processing history; /briefing says Calendar/Mail lack grants while /ops/status says they are granted. An evidence-first answer prevents the owner trusting stale or simulated device state, and is the single most useful perception capability.
- **path:** relay-realtime → mac-planner → browser-extension → unified → faculty-perception
- **model tier:** background for assembling the evidence table; realtime only to summarize it when the owner asks
- **latency:** Under 2 seconds from cached probes; refresh only the sources whose freshness window has expired
- **cost:** <$0.01 per request when rule-based; model cost only for a short natural-language summary
- **security:** Must not expose page contents or secrets merely to report health. Each claim needs source, observedAt, freshness deadline, and confidence; stale pipeline records must be explicitly labeled historical. Acting on a contradicted claim requires owner confirmation.
- **missing:** A cross-surface observation schema with freshness and provenance; A relay-visible live device registry query (the Mac agent has no /v1/devices route); A contradiction/quarantine evaluator

### "“Treat the nRF9160 and ESP32 that are plugged into my Mac as my pendant right now—capture a button/mic event over USB and return the reply through the bridge, even without LTE.”"
- **useful because:** A physically tethered pendant is testable today even though the relay registry has no nRF device. This gives the owner the actual wearable interaction loop now, rather than silently pretending recorded LTE telemetry is live, and provides a path to validate firmware before cellular registration.
- **path:** mac-terminal → mac-planner → relay-realtime → faculty-perception → faculty-action
- **model tier:** realtime for the spoken request/reply; cheap background worker for serial framing, buffering, and health checks
- **latency:** Button-to-ack under 300 ms over USB serial; spoken response under 3 seconds after capture
- **cost:** Negligible API cost for button acknowledgements; normal realtime cost only for speech requests. No cellular transfer cost while tethered.
- **security:** Serial access must be restricted to the two exact USB VID/PID or stable device paths and never execute arbitrary serial data as shell commands. Audio stays local until the owner explicitly submits it to relay; pairing state must not be inferred from USB presence. Require confirmation before sending captured audio off-device.
- **missing:** A Mac serial transport skill for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A local relay ingress mode that authenticates a tethered device without claiming LTE registration; Firmware framing/heartbeat and explicit source=tethered_usb telemetry; A local audio bridge route that can feed capture to /pipeline/audio

### "“When you say you clicked, typed, or sent something, prove the target state changed; otherwise tell me it did not happen and stop.”"
- **useful because:** The live agent explicitly reports that ui_click, ui_menu, type_text, and press_keys can return success while doing nothing because Accessibility is untrusted. A perception-backed completion receipt would prevent false claims—especially for Gmail, reminders, and browser workflows—by comparing a pre/post observation and refusing to call an unverified action complete.
- **path:** mac-vision → browser-extension → mac-planner → faculty-perception → faculty-action → relay-realtime
- **model tier:** rule-based state diff first; vision model only when semantic visual comparison is unavoidable; realtime only to explain failure to the owner
- **latency:** Under 1 second for browser DOM/tab diffs; up to 4 seconds for a screenshot/vision verification
- **cost:** Near-zero for structured browser and AppleScript observations; vision calls are occasional and <$0.02 each
- **security:** Do not capture or upload screenshots containing private mail/passwords unless the action explicitly requires it and the owner consented. Redact secrets in receipts. A receipt must distinguish observed state change, inferred change, and no verification; unverified completion cannot trigger follow-up actions.
- **missing:** A mandatory pre/post observation contract on every action; Structured postconditions for browser, AppleScript, and file actions; A safe screenshot-diff path once Screen Recording is granted; current permission is false; Action receipts that can block dependent actions when verification fails

### "“Before you send, delete, book, or publish anything, rehearse the whole action across my Mac and browser and show me exactly what would change—without touching the real state.”"
- **useful because:** Today the system can plan or execute, but it cannot safely answer the owner’s most important uncertainty: what side effects a multi-surface action would cause. A dry-run that snapshots relevant tabs/files/calendar state, resolves references, and renders the predicted diff lets the owner make informed decisions before an irreversible external effect.
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision → faculty-perception → faculty-judgement
- **model tier:** background model for multi-step simulation and diff explanation; realtime only for the owner’s short request and spoken result
- **latency:** 3–8 seconds for browser/API-backed workflows; clearly label longer simulations rather than blocking conversation
- **cost:** <$0.05 per rehearsal dominated by planner context; zero vision cost when DOM/AppleScript state is sufficient
- **security:** Simulation must use isolated browser sessions or read-only API adapters and never submit forms, send mail, mutate files, or trigger downloads. Snapshots may contain private data, so retain only redacted diffs and discard source state after the rehearsal. The final real execution must remain a separate, explicit action.
- **missing:** Read-only shadow adapters for AppleScript apps, browser forms, filesystem operations, and relay jobs; A stable state snapshot/diff schema spanning Mac and browser sessions; Reference resolution that can identify the exact recipient/file/tab before simulation; A hard separation between simulation credentials and mutation credentials

### "“When I press the pendant’s bookmark button, save what I was doing at that exact moment so I can later ask ‘what was happening when I marked that?’”"
- **useful because:** A physical button is an unambiguous, low-friction perception marker that software alone cannot provide. Correlating its timestamp with the Mac’s foreground app, browser tab, active session, audio pipeline, and nearby calendar/mail metadata would let the owner recover context after interruptions without remembering to narrate it.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → faculty-perception → unified
- **model tier:** cheap background correlation and indexing; realtime only when the owner later asks for a spoken reconstruction
- **latency:** Acknowledge the button locally within 150 ms; ingest a redacted context bundle within 2 seconds; answer historical lookups within 3 seconds
- **cost:** Near-zero for local event metadata; <$0.01 for an occasional retrieval summary; storage grows roughly 5–20 KB per bookmark if screenshots are excluded
- **security:** Default to metadata, not microphone or screenshots. Sensitive tab titles, message subjects, and app names need per-source opt-in and local encryption. The physical marker must carry a monotonic device sequence plus timestamp so replayed USB/LTE events cannot fabricate history.
- **missing:** Firmware button-event sequence and timestamp protocol; A Mac observer that atomically captures foreground/browser/pipeline state on receipt; Encrypted, queryable cross-surface bookmark storage with retention controls; A causal correlation window that distinguishes state observed before versus after the press

### "“Run a harmless end-to-end test of the whole hive and tell me which exact link is broken—from pendant input through relay, Mac planning, browser access, and spoken output.”"
- **useful because:** The owner currently sees isolated health flags and historical pipeline records, not proof that a real request can traverse every surface. A synthetic, non-mutating transaction would expose failures such as an unregistered pendant, stale browser tab, missing TCC permission, broken relay handoff, or audio-format mismatch before the owner relies on the system. It turns invisible integration failure into one actionable diagnosis.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → faculty-perception → faculty-action
- **model tier:** cheap deterministic harness with a background model only to explain the resulting dependency graph; realtime is unnecessary except for an optional spoken report
- **latency:** 15 seconds for the complete test; individual link failures should be surfaced as soon as observed
- **cost:** Near-zero API cost; one short local synthetic request, with no external web or LLM call unless explicitly selected
- **security:** Use a reserved local test phrase, disposable browser page/session, loopback audio or muted playback, and never touch personal tabs, send network messages, or create calendar/mail records. Test artifacts must be clearly tagged synthetic and auto-expire.
- **missing:** A reserved synthetic transaction protocol and correlation ID across firmware, relay, Mac, and extension; A loopback pendant/USB test mode that verifies input and output without LTE or recording private audio; Non-mutating browser and planner test fixtures; A dependency-graph evaluator that distinguishes unavailable hardware from stale telemetry


## What it asked for

_Nothing._
## Its own summary

Round 130 established two actionable truths: the only live devices are the Mac bridge and Safari extension—no nRF pendant—and Mac UI automation is not trustworthy because Accessibility/Screen Recording are absent and input reachability failed. Browser state and pipeline state are also visibly misleading (failed active tab, stale processing jobs, contradictory briefing grants, 15,625 Hz historical input vs 24 kHz output). I recorded these findings, notified judgement/all agents, and proposed three owner-facing capabilities: a tethered-USB pendant loop, proof-of-state action receipts, and evidence/provenance-aware perception. What remains needed is not another probe: a serial transport/firmware framing path for the two USB chips, explicit telemetry lineage/freshness and contradiction handling, and owner-granted TCC permissions if visual/UI verification is required.

**Biggest unknown:** Whether the physically connected nRF9160 and ESP32 are actually present on the stated USB serial paths in this current Mac session; the HTTP surface cannot see them, and the requested serial diagnostic/transport capability is not yet available.

