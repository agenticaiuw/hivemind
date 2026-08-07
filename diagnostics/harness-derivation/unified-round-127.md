# Harness derivation — unified — round 127

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **transport and timezone truth** — The pendant and ESP32 are physically reachable over USB serial, but the nRF9160 is not LTE-registered; the measured LTE path is half-duplex and drops substantial uplink under simultaneous speech. Owner memory says America/Chicago while machine-context reports America/New_York, so any spoken schedule must resolve an authoritative timezone before acting.
  - evidence: get_hardware_spec(pendant, bridge, network); mac-terminal live finding

## Capabilities it proposed

### "“Keep my conversation alive when I leave Wi‑Fi: if the pendant is plugged into my Mac over USB, switch the live call to that local link, then move it back to LTE when available without losing the transcript or repeating my request.”"
- **useful because:** The pendant is physically testable over USB today but is not LTE-registered. This gives the owner one continuous wearable conversation instead of a dead device whenever cellular coverage or registration fails, while preserving exactly-once task execution across transport changes.
- **path:** pendant → mac-planner → relay-realtime → relay → faculty-perception → faculty-action
- **model tier:** Realtime for the active voice stream; a cheaper background model reconciles transcript segments and transport receipts after handoff.
- **latency:** Handoff under 2 seconds, with at most one replay-free audio gap; reconciliation can finish within 10 seconds.
- **cost:** Negligible inference increase during handoff; roughly 1–2 extra short realtime turns per transport change. Dominant cost is persistent audio/WebSocket bandwidth, not tokens.
- **security:** USB serial audio and control stay on the owner's Mac; relay must authenticate the pendant session and bind both transports to one nonce. Never duplicate an irreversible Mac/browser action when reconnecting; require the existing confirmation policy for destructive actions.
- **missing:** USB serial transport bridge from Mac to relay; session migration protocol with monotonic audio and action sequence numbers; pendant link-state telemetry and reconnect test harness

### "“When I say ‘save this’ while wearing the pendant, capture the exact audio, transcript, time, and what page or Mac window I was looking at; later let me ask ‘what was I pointing at?’ and hear the answer with the original evidence.”"
- **useful because:** A wearable is present at the moment of intent, while only the browser and Mac can know the private page or window context. Joining a short local audio marker to a cross-surface snapshot makes fleeting ideas and references recoverable instead of forcing the owner to remember which tab or app they meant.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Realtime performs the short capture and confirmation; background extraction and cross-surface indexing use a cheaper model.
- **latency:** A tactile/voice acknowledgement in under 700 ms; indexing and evidence attachment within 5 seconds.
- **cost:** One short realtime turn per marker; background indexing is a small summarization call. Storage and audio retention dominate, so default to a 30-second clip and transcript.
- **security:** Capture only after an explicit spoken/button trigger, show a pendant LED indication, and encrypt/private-scope browser URLs and snippets. Redact secrets and allow immediate deletion. Never silently record ambient audio.
- **missing:** moment marker event and short encrypted audio spool; Mac active-window and browser-tab snapshot endpoint; cross-surface evidence index and spoken retrieval query

### "“If I am in the middle of a browser or Mac task and the pendant disconnects, stop before any irreversible step, tell me exactly where you stopped, and resume only when I explicitly say ‘continue’.”"
- **useful because:** A disconnected wearable can mean loss of attention, privacy, or transport. This turns a silent failure into a safe, inspectable pause, protecting the owner from a queued send, purchase, deletion, or navigation occurring after they can no longer hear the confirmation.
- **path:** pendant → mac-planner → browser-extension → relay → faculty-judgement → faculty-action
- **model tier:** Deterministic rules handle disconnect detection and checkpointing; a cheap model summarizes the paused state. Realtime is used only to announce the stop when a path remains available.
- **latency:** Pause within 250 ms of confirmed link loss; receipt available within 2 seconds of reconnection.
- **cost:** No per-event model cost for the safety latch; one short summary call per paused job at most.
- **security:** Default-deny for irreversible actions after disconnect, with idempotent cancellation and durable receipts. Do not expose private page contents in reconnect notifications until the pendant is authenticated again.
- **missing:** device presence/heartbeat tied to each active job; action checkpoint gate before irreversible browser/Mac steps; durable pause/resume state and explicit spoken continuation token

### "“When I’m busy, let the pendant be my interruptibility switch: one gesture should put my Mac, browser, and relay into quiet mode, defer nonurgent work, and let only genuinely urgent events break through; another gesture restores normal operation.”"
- **useful because:** Today quieting notifications, stopping background browser work, and changing wearable behavior are separate operations. A physical switch gives the owner an immediate, reliable boundary without opening an app or speaking over an interruption.
- **path:** pendant → mac-planner → browser-extension → relay → faculty-judgement → faculty-action
- **model tier:** Deterministic local state and relay policy; a cheap model classifies urgency only when an event is ambiguous.
- **latency:** Local gesture feedback under 150 ms; Mac/browser policy convergence under 2 seconds.
- **cost:** Near-zero model cost for explicit mode changes; occasional small classification calls for incoming events.
- **security:** The mode must fail closed on disconnect and never suppress safety-critical alerts. Store only the mode and expiry, not ambient audio. Require an explicit gesture or spoken command to exit quiet mode.
- **missing:** A pendant gesture/state event protocol beyond the single button; Shared interruptibility state consumed by relay, Mac, and browser jobs; Urgency policy and expiry semantics

### "“If a private website logs me out or asks for a security check, tell me exactly what happened through the pendant, guide me to the right Safari tab, and wait while I complete the login—never handle or repeat my password or code.”"
- **useful because:** Authenticated browser work currently fails opaquely when a session expires or a challenge appears. The owner should be able to recover access from the wearable instead of discovering later that a task silently stopped.
- **path:** pendant → browser-extension → mac-planner → relay → faculty-perception → faculty-action
- **model tier:** Deterministic page-state detection and tab targeting; realtime voice for concise guidance; no model should see credentials or challenge values.
- **latency:** Detect and announce within 3 seconds; resume the waiting job within 5 seconds after a fresh authenticated heartbeat.
- **cost:** No model call for ordinary detection; one short realtime turn for guidance and one background reconciliation after recovery.
- **security:** Challenge pages are metadata-only to the model. Credentials remain in Safari’s protected UI. Bind recovery to the original tab/session and invalidate stale commands.
- **missing:** Typed auth-expired/challenge browser results; A secure human-in-the-loop wait state in the job runner; Pendant-to-browser resume handshake

### "“At the end of a task, tell me not just that it finished, but what changed in the real world: compare the before and after state in the browser or Mac, name anything that did not take effect, and let me ask follow-up questions from the pendant.”"
- **useful because:** A successful tool call is not proof that a calendar event, setting, file, or web form actually changed. Cross-surface verification would make the wearable trustworthy for consequential everyday work rather than merely optimistic.
- **path:** pendant → mac-planner → browser-extension → relay → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Deterministic rereads and hashes establish state changes; a cheaper model explains the diff; realtime only speaks the concise receipt.
- **latency:** Verification within 5 seconds for local/browser changes; longer jobs produce an immediate pending receipt and later spoken update.
- **cost:** One or two low-cost extraction/reconciliation calls per completed task; browser reads and screenshots dominate, not realtime inference.
- **security:** Retain minimal before/after evidence, redact secrets, and scope rereads to the affected resource. Never claim success when verification is unavailable; label it unknown.
- **missing:** Typed before/after state snapshots for Mac and browser actions; A cross-surface verification stage in the action pipeline; Receipts queryable by the pendant conversation


## Changes it proposed to its own stack

### `integration` — Add a user-facing “wearable link test” that drives a known audio phrase from the Mac through the USB-connected nRF9160 pendant and ESP32 bridge, records round-trip latency, packet loss, underruns, resampler drift, and headphone output, then speaks a plain-language pass/fail and stores a timestamped receipt attached to the current pipeline.
- **owner gets:** The owner can test the physical pendant today even though LTE registration is absent. Instead of guessing whether a bad conversation is model quality or hardware/link failure, they get a two-minute answer and a concrete repair target before relying on it outside.
- effort: Medium: Mac serial harness, a firmware diagnostic opcode, ESP32 counters, and a small report/receipt route.  ·  risk: A diagnostic tone could surprise the owner or play loudly; cap volume, require a button/voice start, and abort on disconnect. Recover by leaving no persistent audio and marking incomplete runs.
- cost: No model cost beyond optional one-sentence interpretation; modest local CPU and serial traffic.  ·  latency: A 30–60 second test before use; no impact on normal calls.
- security: Keep raw test audio local and upload only aggregate metrics unless the owner opts in.
- depends on: USB serial access to both live boards; stable pipeline audio counters; owner-approved 24 kHz acceptance thresholds

### `hardware` — Replace the prototype pendant’s single button/LED interaction with a production input-output module: a low-power haptic actuator, a capacitive or pressure-sensitive side strip, and an ambient-light/proximity sensor. Expose gesture, pocket/worn, and tactile acknowledgement events to firmware while retaining a physical emergency/confirm button.
- **owner gets:** The owner could change modes, approve or cancel actions, and receive private confirmations without speaking or looking at a screen—especially in meetings, outdoors, or when the pendant is under clothing.
- effort: High: enclosure and industrial design, low-power driver, debounce/gesture firmware, interrupt routing, and an interaction vocabulary tested with real wear conditions.  ·  risk: False gestures or hidden confirmations could cause confusion or unsafe actions. Require deliberate multi-step gestures for consequential actions, make haptic patterns distinguishable, and fall back to the physical button plus LED.
- cost: Roughly $3–8 in added components at production volume, with tens to hundreds of microwatts idle and brief milliwatt-level haptic pulses.  ·  latency: Local feedback can be sub-100 ms; no network latency added.
- security: Enables private local confirmation, reducing spoken leakage. Sensor data should remain local and expose only coarse state, not raw proximity traces.
- depends on: A production pendant design rather than the current nRF9160 DK; Firmware event schema shared with relay and Mac; Owner-tested gesture and haptic vocabulary


## What it asked for

_Nothing._
