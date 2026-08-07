# Harness derivation — faculty-action — round 125

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Even with no LTE registration, let me use the pendant today: press the button, speak through the USB-connected pendant/ESP32, and hear the response, with the Mac relaying it to the same conversation.”"
- **useful because:** The owner can wear and use the actual hardware now instead of waiting for cellular registration; a dropped relay link can fall back to the Mac USB path and resume the same session.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal
- **model tier:** Realtime model only for the spoken turn; local Mac routing and serial framing use deterministic code, not an LLM.
- **latency:** Button-to-listening acknowledgement under 150 ms locally; first spoken response under 2 s on the Mac path.
- **cost:** No meaningful extra model cost beyond the existing voice turn; hardware is already present. Engineering cost is the serial transport, session handoff, and 24 kHz codec integration.
- **security:** USB serial is local to the owner’s Mac, but arbitrary serial injection must be rejected; bind the device identity and never expose raw microphone/audio frames to unrelated relay jobs. No action should execute merely because USB connected.
- **missing:** A Mac serial bridge for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; Firmware/ESP32 framing and 24 kHz end-to-end acceptance test; A relay session-resume token that distinguishes USB-local from LTE transport

### "“When a Mac or browser job fails, don’t just tell me it failed: inspect the receipt, logs, browser heartbeat, and current Mac state, repair transient problems, retry safely, and tell me exactly what was fixed or why you stopped.”"
- **useful because:** Long-running work becomes dependable: stale browser bridges, expired tabs, temporary network errors, and interrupted Mac jobs are recovered without making the owner re-explain the task.
- **path:** relay → mac-planner → browser-extension → mac-terminal → pendant
- **model tier:** Use a cheap background planner for diagnosis and deterministic retry policies; invoke realtime only to speak the final result or ask for a decision.
- **latency:** Detect within 10 seconds of a failed receipt; recover common transient failures within 60 seconds; never loop more than three attempts.
- **cost:** Usually one small background planning call per failure, with deterministic checks dominating; negligible cost for healthy jobs.
- **security:** Retries must be idempotency-keyed and limited to reversible steps. Any send, delete, purchase, or external mutation pauses for confirmation. Logs may contain private content and should remain on the Mac unless a redacted diagnostic is needed.
- **missing:** A failure-classification and bounded retry worker; Typed precondition checks for browser session/tab freshness and Mac availability; A durable repair receipt linking the original job, attempted repair, and final state

### "“Do the private parts on my Mac, but still coordinate everything for me: use my logged-in browser and local files without sending their contents to the relay, then give me a concise answer or execute the approved next step.”"
- **useful because:** The owner gets the reach of private browser sessions and local files without turning the relay into a copy of their secrets; this makes cross-surface action safe enough for everyday use.
- **path:** relay-realtime → mac-planner → browser-extension → mac-terminal → dashboard
- **model tier:** A local Mac planner performs extraction, redaction, and action planning; the relay realtime model receives only typed claims, hashes, and the minimum excerpt needed for the conversation.
- **latency:** Local private inspection under 3 seconds for routine pages; relay response under 2 seconds after the redacted result arrives.
- **cost:** Lower than sending full pages: small local planning call plus the existing spoken turn; token savings grow with large authenticated pages.
- **security:** Define a deny-by-default field policy for credentials, tokens, health/financial identifiers, and message bodies. Keep raw evidence local with short retention; dashboard must show what crossed the boundary. External mutations still require the owner’s existing confirmation policy.
- **missing:** A local redaction/typed-result protocol with sensitivity labels and provenance; Relay enforcement that rejects raw private payloads rather than trusting the planner; Dashboard evidence showing local-only fields versus fields shared with the relay

### "“Repeat the last thing I had you do, but adapt it to what is on screen now, and show me the exact differences before you run it.”"
- **useful because:** The owner can safely reuse successful workflows without reconstructing them from memory: the system replays the intent and structure, not stale clicks or private page contents, then presents a current-state diff.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** A cheaper background planner reconstructs the prior typed action graph; realtime is used only for the owner’s spoken request and concise approval summary.
- **latency:** Reconstruction in under 5 seconds; current-state inspection and diff in under 15 seconds; no execution until approval.
- **cost:** One small planning call plus local browser/Mac inspection; no cost when unused.
- **security:** Never replay credentials or hidden fields. Bind replay to the original account/session, re-resolve targets semantically, and stop on changed recipients, amounts, destructive effects, or missing evidence. Keep prior raw evidence local.
- **missing:** A semantic action-graph recorder distinct from low-level receipts; Current-versus-prior field diff renderer with provenance; A replay engine that re-plans against the live browser/Mac state and requires approval at mutation boundaries

### "“Tell me whether the pendant is truly usable right now—not merely connected—and, if it isn’t, run a safe loopback test and explain the failing part.”"
- **useful because:** The owner gets an immediate, trustworthy answer about button capture, microphone input, speaker playback, serial transport, and relay reachability instead of guessing from a USB icon or LED.
- **path:** pendant → ESP32 audio bridge → mac-terminal → relay-realtime → dashboard
- **model tier:** Deterministic hardware probes and signal checks do the work; use realtime only to explain the result in one short spoken response.
- **latency:** Basic status under 2 seconds; full loopback under 10 seconds; never transmit captured test audio beyond the local Mac unless explicitly requested.
- **cost:** No model cost for healthy checks; negligible local CPU and a few seconds of generated test tone.
- **security:** Use synthetic tones and discard them immediately. Do not open the owner’s microphone or record environmental audio. Device identity must be allowlisted and tests must not flash or alter firmware.
- **missing:** A read-only serial/I2S diagnostic protocol; A deterministic audio loopback and button/LED test runner; Typed health evidence that distinguishes attached, authenticated, audio-ready, and relay-reachable

### "“Put this page, quote, or result from my private browser onto my phone as a secure handoff, and let me pick it up later on the pendant without making me copy or expose the whole page.”"
- **useful because:** The owner can move a useful fragment between the browser they are using and the device they are wearing without email, clipboard leakage, or losing the source context; the handoff remains useful even when the browser tab is later closed.
- **path:** browser-extension → mac-planner → relay-realtime → iOS → pendant → dashboard
- **model tier:** Local Mac extraction and redaction are deterministic/cheap; background model normalizes the selected fragment and title; realtime only speaks confirmation or retrieval.
- **latency:** Create a handoff in under 3 seconds; retrieve it from the pendant in under 2 seconds when cached.
- **cost:** Tiny background-model call per handoff, dominated by local extraction; no call for plain URL-only transfers.
- **security:** Handoffs inherit source sensitivity and expire by default. Do not send whole authenticated pages; require explicit selection or a narrowly scoped excerpt, encrypt in transit and at rest, and show the destination/device and expiry before creation.
- **missing:** A cross-device handoff object with encrypted payload, expiry, source URL, and sensitivity label; Browser command to select/clip a bounded excerpt with provenance; iOS/pendant retrieval and deletion protocol


## Changes it proposed to its own stack

### `integration` — Add a local USB device supervisor that opens the nRF9160 and ESP32 serial ports by stable USB identity, performs a signed hello/capability negotiation, bridges framed 24 kHz audio and button/LED events into the existing /pipeline session, and exposes transport state (attached, authenticated, audio-ready, last frame, fault) to the relay. It must fail closed on unknown serial devices and never auto-flash firmware.
- **owner gets:** The pendant becomes usable on the desk and while worn today, despite absent LTE registration, with an honest indicator when audio is not actually flowing.
- effort: Medium-high: Mac daemon, serial framing, reconnect tests, pipeline adapter, and a small dashboard status view.  ·  risk: A malformed stream could wedge audio or send the wrong device’s data; use device VID/PID/serial allowlisting, bounded buffers, watchdog reconnect, and a kill switch. Recovery is unplug/replug without changing firmware.
- cost: No API cost; one low-CPU Mac process and existing USB power. Some implementation/testing time.  ·  latency: Adds roughly 10–30 ms serial buffering if frames are kept bounded.
- security: Local-only transport, authenticated device handshake, no raw serial logs in relay telemetry.
- depends on: Firmware/bridge framing specification; A local serial transport implementation with test fixtures; Pipeline session resume keyed by device identity

### `relay` — Create a typed action-repair contract between relay jobs and the Mac agent: each failed step returns a stable failure class, observed preconditions, safe recovery candidates, idempotency key, and a hard mutation boundary; the relay may auto-select only explicitly reversible repairs and otherwise asks the owner.
- **owner gets:** The system can recover from ordinary interruptions instead of abandoning work, while making it obvious when a retry could have side effects.
- effort: Medium: schema, local-agent adapters, bounded worker, receipts, and tests for stale tabs, offline Mac, and duplicate delivery.  ·  risk: Incorrect classification could repeat an external action; default unknown to stop, require idempotency, and preserve before/after receipts. Undo/cancel remains available.
- cost: Small background-model cost only on failures; healthy jobs unchanged.  ·  latency: No healthy-path impact; failed jobs gain a few seconds of diagnosis.
- security: Failure reports should redact page contents and secrets; mutation boundary is enforced server-side, not by model instruction.
- depends on: Typed action result schema; Durable worker/lease; Existing receipt and cancel routes


## What it asked for

_Nothing._
## Its own summary

Round 125 produced five recorded proposals. The most useful is a USB-worn mode: a Mac serial supervisor authenticates the physically connected nRF9160/ESP32 pair, bridges button/audio/events into the existing pipeline, and preserves session continuity even though LTE is unregistered. I also recorded bounded self-healing for failed Mac/browser jobs with typed failure classes and mutation boundaries, a local-private execution boundary that returns only redacted typed facts, plus the concrete USB supervisor and relay action-repair contract changes. I told faculty-judgement the three main gaps.

**Biggest unknown:** The exact firmware/ESP32 serial framing and 24 kHz acceptance criteria remain unavailable, and there is no verified serial supervisor or session-resume path yet. I still need those specifications (and an owner-controlled build/test invocation) before this can be run safely; I do not need or want permission to flash hardware.

