# Harness derivation — mac-planner — round 153

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What am I looking at?”"
- **useful because:** The pendant answers about the exact browser tab or Mac document currently in front of the owner, with a short quoted evidence snippet and a useful next step. This is the highest-value everyday interaction: no copying URLs, screenshots, or explaining context while walking around.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision
- **model tier:** Realtime for the one-sentence spoken answer; a cheaper background model may summarize long page text only when requested.
- **latency:** Under 2 seconds for tab metadata/snippet; under 5 seconds for a document or cross-app answer.
- **cost:** Roughly one realtime turn plus 1–3 KB of extracted text; dominated by realtime inference, with no image tokens for ordinary DOM/UI text.
- **security:** Only the active tab/app and a bounded evidence window leave the Mac. Never include hidden tabs, passwords, or form values. Any mutation (typing, sending, closing) must remain a separately confirmed command.
- **missing:** A signed pendant request that asks the Mac for its current focus without opening the microphone; A typed context envelope joining active browser tab, foreground app, and provenance timestamps; A browser-extension endpoint for active-tab bounded extraction and a Mac route for active-document text

### "“If I walk away, keep the work safe and hand me back exactly where I left off when I return.”"
- **useful because:** The system snapshots the owner's active browser/app context and in-progress Mac job, pauses risky or distracting actions, then restores a concise resume card on the pendant and Mac after reconnection. It prevents lost state when the laptop sleeps, the USB pendant disconnects, or a long job finishes unattended.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Background model compiles a compact resume capsule; realtime only speaks the capsule when the owner asks or reconnects.
- **latency:** Capture under 1 second on disconnect; restore in under 3 seconds after reconnection. Long summarization can finish asynchronously.
- **cost:** Low: mostly structured metadata and a small text summary; occasional background inference, not realtime.
- **security:** Persist only active URLs, app/document identifiers, job IDs, and owner-selected snippets; redact page bodies and secrets. Never auto-submit queued browser or Mac actions after reconnect; display them as pending.
- **missing:** A device disconnect/reconnect event stream over the existing USB serial link; A durable resume-capsule store keyed to session and device epoch; A restore protocol that reattaches browser tab IDs and Mac job receipts without replaying actions

### "“Run a private soundcheck and tell me whether the pendant, bridge, and voice path are actually ready.”"
- **useful because:** With both boards physically attached today, the system can test the complete path instead of guessing from server health: serial framing, button/event delivery, 24 kHz decode and 31.25 kHz I2S playback, bridge output, and a short synthetic round trip. It returns one spoken verdict plus a dated diagnostic artifact, making the prototype trustworthy before the owner wears it.
- **path:** pendant → mac-planner → relay-realtime → dashboard
- **model tier:** No expensive model for the test; deterministic firmware/host checks and a cheap background classifier for logs. Realtime only announces the final verdict.
- **latency:** 30 seconds maximum for a full test; individual checks should stream progress within 2 seconds.
- **cost:** Near-zero inference cost; one small log and optional generated test tone. Engineering cost is the serial test harness and bridge fixture.
- **security:** Use synthetic tones and loopback fixtures, never open the microphone or upload raw audio. Store only pass/fail metrics and hashes in ~/AI-Pendant-Workspace. Require an explicit physical button press for any microphone-path test.
- **missing:** A host-side dual-serial fixture that controls /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; Firmware diagnostic commands for codec, UART framing, I2S clock, and button/LED loopback; A relay health correlation endpoint that distinguishes local USB readiness from LTE registration

### "“Why didn’t that happen?”"
- **useful because:** The owner gets a causal explanation of a failed or partially completed request across pendant, relay, browser session, and Mac execution—not a generic failed status. It identifies the first broken handoff, shows the evidence and exact recovery action, and can safely retry only the missing step. This is a capability the owner cannot have today because receipts and job status do not reconstruct an end-to-end causal timeline.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic event correlation and typed error rules first; use a cheaper background model only to phrase the explanation. Realtime is needed only for the short spoken diagnosis.
- **latency:** Under 3 seconds for an existing request; under 10 seconds if correlated browser/Mac evidence must be fetched.
- **cost:** Low API cost: mostly structured event joins and small snippets; model usage is limited to final phrasing.
- **security:** Expose only events belonging to the owner’s request/session, redact page content and secrets, and never retry a side effect automatically. A retry plan must enumerate already-completed steps and require the owner’s existing confirmation policy for sending, deleting, or purchasing.
- **missing:** A durable end-to-end correlation ID propagated from pendant event through relay plan, browser command, and Mac action; Structured failure taxonomy with first-fault and partial-completion fields; A read-only causal-trace route and a retry-from-checkpoint route that cannot replay completed side effects

### "“Find my pendant.”"
- **useful because:** The system reports the pendant’s last authenticated contact, whether it is currently USB-attached, and—when nearby—causes the bridge or pendant to emit a distinctive local cue. If it is away from the Mac, it gives the last relay timestamp and battery/radio state instead of pretending it is online. This turns a wearable into something the owner can recover, not a device that silently disappears.
- **path:** pendant → mac-planner → relay-realtime → dashboard
- **model tier:** Deterministic device-presence and last-seen logic; no model needed except optional concise spoken phrasing.
- **latency:** Local USB answer under 1 second; remote last-seen answer under 3 seconds.
- **cost:** Negligible API cost. A future BLE/UWB locator would dominate hardware cost, approximately $5–$20 in components and modest battery draw.
- **security:** Only the owner’s enrolled device may trigger the cue; do not expose location history beyond coarse last-seen data. A loud cue must be explicitly requested and rate-limited.
- **missing:** A stable device identity and presence heartbeat usable over both USB serial and LTE; A Mac serial watcher that can distinguish attach, detach, and stale links; A physical locate cue (buzzer, stronger LED, or BLE/UWB radio) and a relay last-seen endpoint

### "“During a meeting, alert me silently only if something truly urgent needs me.”"
- **useful because:** Calendar state on the Mac, authenticated Mail/browser signals, and the pendant’s physical output combine into a quiet interrupt channel: ordinary notifications wait, while a genuinely urgent item produces a distinct tactile/LED pattern and a one-line spoken or queued explanation when the owner is free. Today each surface can inspect its own state, but none can safely arbitrate urgency against the owner’s meeting context and deliver it through a wearable without audio disruption.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Cheap background classifier ranks incoming signals; realtime is reserved for an explicit follow-up question. Deterministic calendar quiet-hours and sender/site allowlists override the classifier.
- **latency:** Urgency decision within 30 seconds of a new signal; local cue within 2 seconds after decision.
- **cost:** Low ongoing inference cost with event-driven classification; hardware addition is roughly $1–$4 for a vibration motor and driver, with brief pulse power under 50 mW.
- **security:** Use only user-selected Mail/browser sources, redact message bodies from logs, and never infer urgency from sensitive content without local policy. The cue reveals only that attention is needed; details wait for an explicit request.
- **missing:** A durable cross-surface event stream for Mail/browser changes and Calendar meeting state; A user-editable urgency policy and quiet-hours evaluator; A pendant haptic output (or a documented LED code) with queued notification acknowledgements


## Changes it proposed to its own stack

### `integration` — Ship a one-command “Pendant Ready” workflow on the Mac that detects the two known USB serial devices, runs a deterministic event/audio loopback against the nRF9160 and ESP32, correlates the result with relay health, writes a human-readable report in ~/AI-Pendant-Workspace, and exposes the latest verdict to the voice agent. It must distinguish “USB prototype works” from “LTE device registered” rather than collapsing them into one online flag.
- **owner gets:** The owner can plug in the real pendant and bridge and know in under a minute whether the thing they are about to wear can hear, speak, and deliver events—without reading UART logs or mistaking a healthy Mac connection for cellular service.
- effort: Medium-high: serial protocol fixture, firmware diagnostic opcodes, bridge test tone/loopback, report schema, and a small Mac launch action.  ·  risk: A malformed diagnostic command could wedge a prototype board or leave audio streaming; use timeouts, reset-on-failure, and never touch production audio configuration. Recovery is unplug/replug plus the existing firmware reset path.
- cost: No per-run API cost; roughly 1–2 MB of local logs per week if retained, with negligible CPU. Hardware unchanged.  ·  latency: Adds a manual 20–30 second readiness check; no steady-state voice latency impact.
- security: Raw microphone data must remain local and synthetic test audio should be used. Device serial identifiers and health metrics stay local unless the owner explicitly asks to share them.
- depends on: Firmware diagnostic opcodes on both boards; A Mac serial harness with stable port discovery; A relay health response that reports cellular registration separately from local USB reachability


## What it asked for

_Nothing._
## Its own summary

Round 153 produced three new owner-facing capabilities and one integration change. The most useful is “What am I looking at?”: a pendant-triggered, bounded active-tab/foreground-document answer with provenance and no screen takeover. I also proposed disconnect-safe resume capsules and a real USB pendant+ESP32 end-to-end soundcheck, plus a concrete “Pendant Ready” Mac workflow that separates USB readiness from LTE registration. Still needed: the signed pendant-to-Mac focus request, active-tab/foreground extraction envelope, disconnect events and durable resume storage, dual-serial diagnostic fixture/opcodes, and relay health that reports cellular registration independently. I did not re-request denied TCC or already-pending tools.

**Biggest unknown:** Whether the existing browser bridge and Mac local-agent routes can expose active foreground context and stable serial access without new permissions; the live USB boards are physically present, but I cannot inspect or drive their serial ports from this Mac-planner surface yet.

