# Harness derivation — mac-terminal — round 229

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **bench USB serial capability** — The granted mac_usb_serial_diagnostics schema still does not resolve against the live inventory; no serial/USB capability is published, so no bounded UART read was performed.
  - evidence: mac_usb_serial_diagnostics returned unresolved; best match action:get_mac_status score 0.226, inventory 223 routes/109 actions.

## Capabilities it proposed

### "Let me have a normal conversation through the pendant while I walk: keep speech natural at 24 kHz, and if the Mac/USB or LTE-M path changes, continue the same turn without me repeating myself."
- **useful because:** This is the single most useful missing experience: the owner gets one conversation rather than a fragile demo that drops whenever transport or codec conditions change. The pendant, audio bridge, Mac and relay must agree on turn identity, codec and replay position; no one node can provide that continuity alone.
- **path:** pendant → relay-realtime → mac-planner → mac-vision
- **model tier:** Realtime only for live turn orchestration and interruption handling; use a cheaper background model for codec diagnostics and post-call quality summaries.
- **latency:** First audio under 250 ms; transport failover decision under 500 ms; resumed audio within 1.5 s without replaying more than the unacknowledged frame window.
- **cost:** Additional realtime inference should be near zero when only transport/codec state changes; roughly $0.01–$0.05 per long conversation for quality summaries, dominated by audio transcription/summary rather than the continuity state machine.
- **security:** Audio and turn IDs transit the relay; persist only bounded replay cursors and quality counters, never raw audio after acknowledgement. Require explicit owner control before recording diagnostic audio to disk.
- **missing:** A negotiated 24 kHz superwideband codec/framing contract shared by nRF9160, ESP32 bridge and relay; End-to-end sequence/ack protocol that can resume a turn across USB and LTE-M without duplicate playback; A live bridge route that exposes codec, jitter, loss and replay-cursor telemetry to the relay; Bench validation harness that can inject USB disconnects and LTE-M loss; the current serial grant is unresolved

### "When you do something on my Mac and it fails, tell me exactly what failed and recover automatically when it is safe instead of making me repeat the request."
- **useful because:** Today a shell failure loses the exit code, process identity and reliable job/ledger join; cancellation may not stop a running child, and nothing retries. The owner experiences a vague failure and must reconstruct state. A bounded recovery assistant turns trusted maximum-access execution into dependable work without adding approval gates.
- **path:** mac-planner → relay-realtime → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheap deterministic classifier for exit status, timeout, signal and idempotency; invoke realtime only to explain the result or ask a genuinely ambiguous recovery question.
- **latency:** Failure classification under 100 ms after process exit; one automatic retry only when the action declares replay-safe; spoken result within 1 s. Never wait for a model to decide whether a process-group kill is needed.
- **cost:** Usually <$0.001 per attempt for local classification; occasional model explanation <$0.01. The dominant cost is any repeated external command or browser action, not the recovery logic.
- **security:** The owner explicitly wants unrestricted shell and no gates. Preserve that policy, but record redacted environment fingerprints, argv, cwd, exit code, signal and process-group outcome; never persist secret environment values or command output beyond existing caps. Automatic retry must be opt-in per action or mechanically limited to declared idempotent reads.
- **missing:** run_shell must use a process-spawn API that captures argv, pid, exit code, signal, timeout and process group, rather than exec with a shell string; A durable job-to-ledger correlation ID and boot reconciliation for processing jobs; A retry recipe field with explicit replay safety and a bounded attempt count; Cancellation must pass an abort signal to the child and kill its process group, not merely set a between-step flag; A concise spoken failure/recovery formatter shared by Mac and relay

### "Know when I am presenting or in a call on my Mac, keep the pendant quiet unless something is truly urgent, and give me the queued items when I am free."
- **useful because:** A wearable that speaks at the wrong moment is unusable. The Mac can see the active app/window and browser session, the relay can rank incoming work, and the pendant can provide the only always-with-me delivery channel; combining them creates interruption judgment no single surface can make.
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay-realtime → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use deterministic local presence signals and a cheap priority/rule engine for almost all events; reserve realtime for a brief spoken escalation when urgency is uncertain or the owner asks why something was suppressed.
- **latency:** Presence changes reflected within 2 s; urgent escalation under 500 ms; queued digest generated within 5 s of the owner becoming available.
- **cost:** Near-zero model cost for app/window and calendar-state rules; <$0.01 per ambiguous event for classification. Storage is a small bounded queue of event IDs and reasons, not audio or page contents.
- **security:** Active app, meeting title and browser host are sensitive. Keep raw titles on the Mac, send only a coarse state and event priority to relay, and never infer or announce meeting participants without an explicit setting. Suppression must be reversible and visible in a short spoken status.
- **missing:** A Mac presence sensor that combines frontmost app, active meeting/call state and browser tab host without screen capture by default; A shared urgency contract and suppression queue between browser jobs, scheduled briefings, relay events and pendant delivery; A pendant-local quiet/urgent state cache so a dropped link cannot cause stale announcements; A user-facing explanation endpoint: which item was suppressed, why, and when it will be delivered

### "When I say “remember that chart” or “follow up on this,” save the exact thing I am looking at—not just a timestamp—so later I can ask about it and you can reopen the same page, section, and evidence."
- **useful because:** Today a spoken reference to “this” loses its referent as soon as the browser changes. A wearable hears the intent, Safari knows the authenticated page and scroll/selection state, the browser extension can capture a stable locator and evidence capsule, and the relay can retain a short-lived provenance record. Together they create a durable, queryable reference without storing an indiscriminate browsing history.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → faculty-perception → faculty-judgement
- **model tier:** Use realtime only to resolve the spoken deictic reference and ask one clarification when multiple visible candidates exist; use a cheaper background model to summarize the captured evidence and generate stable page locators.
- **latency:** Capture the referent within 1 second of the utterance; confirmation in under 2 seconds; reopening and presenting the evidence within 3 seconds later.
- **cost:** <$0.01 per saved reference when structured DOM/URL data is sufficient; occasional screenshot or vision interpretation dominates cost. Keep evidence capsules bounded and expire them by default.
- **security:** Authenticated URLs, page titles, selections, and screenshots may contain sensitive information. Store the minimum locator and claim evidence, encrypt relay storage, preserve host-scoped access controls, and require explicit confirmation before exporting or sharing a captured reference. The pendant should retain only a reference ID and status.
- **missing:** A browser command that atomically captures active tab URL, title, frame/section locator, selection or visible-region metadata, and a bounded evidence capsule; A relay record type for spoken referents with provenance, expiry, host, locator, and replayable reopen instructions; A resolver that can reopen the authenticated browser session and verify the locator still points to the same content before answering; A pendant utterance protocol that carries the active turn's referent ID through interruption and reconnect

### "Only let the assistant take actions as me when my pendant is physically present; if it is gone, keep ordinary read-only help available but refuse voice approvals and authenticated browser actions until it returns."
- **useful because:** A stolen or unattended Mac session should not be enough to authorize a consequential action. Today the Mac agent has a bearer token and broad control, while the pendant is not a hardware-rooted presence factor. A challenge signed by the worn device would make physical possession part of the owner's identity without turning every harmless query into an approval ceremony.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** No realtime inference is needed for cryptographic verification; use deterministic policy for presence and action classes. Realtime only explains why an action was deferred or asks the owner to bring the pendant near the Mac.
- **latency:** Presence challenge under 150 ms over USB/BLE and under 1 s over LTE-assisted relay; authorization decision before dispatch, with read-only responses unaffected.
- **cost:** Negligible inference cost. Engineering cost is key provisioning, replay protection, and recovery UX; hardware cost is near zero if an existing secure element or chip unique ID can be used, otherwise roughly $0.50–$2 for a secure element revision.
- **security:** Private keys must never leave the pendant. Use rotating nonces, monotonic counters, revocation, and a recovery flow that does not silently downgrade to bearer-token authorization. Do not expose presence location or raw proximity telemetry to the relay. The owner must be able to revoke a lost pendant from another trusted session.
- **missing:** A hardware-backed pendant identity and challenge-signing protocol; Mac bridge presence verification with short-lived leases and replay protection; Browser-extension and action-router hooks that classify which actions require physical presence; A lost-device revocation and re-pairing workflow, plus a safe read-only degraded mode


## Changes it proposed to its own stack

### `hardware` — Add a physically latching privacy switch that cuts the microphone power/data path and signals a privacy state to the nRF9160; expose the same state to the Mac bridge so browser capture, screen recording, and relay audio are refused while engaged. Add a clearly visible two-state indicator independent of software.
- **owner gets:** The owner can guarantee “nothing is listening or looking” during sensitive moments even if the relay, Mac agent, or firmware is misbehaving. That is stronger than a spoken command or software mute and makes an always-worn assistant trustworthy in homes, meetings, and confidential work.
- effort: Moderate hardware revision: switch, input protection/debounce, microphone power gating, firmware state propagation, Mac bridge enforcement, and end-to-end tests for insertion/removal and reboot. Must define the fail-safe default and preserve the existing recording button's active-edge behavior.  ·  risk: A faulty switch or debounce could prevent conversations or falsely report privacy. Recover with a hardware bypass jumper during development, watchdog validation, and a boot self-test that refuses to claim privacy unless the physical state is readable. The software must fail closed when the state is unknown.
- cost: Approximately $0.20–$1.50 BOM increase plus PCB revision; negligible steady-state power change, with a small reduction when the microphone rail is physically cut.  ·  latency: Immediate local mute; Mac/relay state propagation under 500 ms when connected. Privacy must not depend on network acknowledgement.
- security: Strongly improves confidentiality by creating a hardware-enforced boundary. The Mac and relay should receive only coarse privacy state, never raw microphone data, and must not override the switch.
- depends on: A device-to-Mac privacy-state frame in the USB bench protocol and LTE control protocol; Mac bridge enforcement before audio capture, browser capture, and screen-recording actions; A durable, truthful privacy indicator that distinguishes physically muted from merely disconnected


## What it asked for

_Nothing._
