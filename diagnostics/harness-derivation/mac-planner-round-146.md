# Harness derivation — mac-planner — round 146

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/relay readiness** — Mac local agent and relay are reachable; browser extension is online with 3 Safari tabs and no pending commands. Full-control mode is enabled, but Accessibility and Screen Recording are not granted, so UI/vision loops are unavailable. The two physical chips remain USB-attached but no USB pendant transport is exposed in the current stack.
  - evidence: GET /ops/status returned agent.ready=false due to accessibility trusted=false and screenRecording granted=false; relay reachable=true; browser online=true/tabCount=3; hardware spec says pendant LTE link is not currently registered and USB devices are physically connected.

## Capabilities it proposed

### "When I plug the pendant into my Mac, let me use it immediately as a private push-to-talk remote: speak through its microphone, hear the reply through its speaker, and have the Mac or my logged-in browser carry out the requested task without requiring LTE registration."
- **useful because:** The hardware is physically present and testable today, yet LTE registration currently makes the wearable appear unavailable. USB-tethered operation would make the pendant useful at a desk, on a flight, or anywhere cellular setup is unreliable, while combining a worn input/output surface with Mac and browser reach.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use realtime only for the live speech turn; route deterministic USB framing, audio buffering, and task dispatch through the relay/Mac bridge, and use a cheaper background model to summarize long task results.
- **latency:** Under 250 ms from button press to capture start, under 1 s to begin the spoken response on a healthy USB link; task completion can be asynchronous with a short audible acknowledgement.
- **cost:** About $0.01–$0.08 per spoken turn depending on realtime audio duration; USB transport and Mac execution are negligible. Long browser results dominate background-model cost.
- **security:** USB pairing must bind to this Mac and relay account, with an explicit LED/audio indication when capture is active. Audio and browser-derived content leave the Mac only for the requested turn; never silently capture while plugged in. Destructive Mac/browser actions retain the owner's existing maximum-access policy but should produce a spoken receipt.
- **missing:** A Mac USB-serial pendant transport that bridges button/audio packets to the relay pipeline; Pendant firmware USB fallback mode and reconnect state machine (the current app assumes LTE WebSocket); Relay session binding that treats the tethered pendant as an authenticated audio endpoint; A low-latency downlink audio writer from Mac bridge to the ESP32 speaker path

### "Is my pendant ready right now? Give me one honest spoken answer covering USB connection, microphone/speaker loopback, relay reachability, browser link, battery/radio state, and whether you can safely hear and act on me; if something is broken, tell me the one fix that matters first."
- **useful because:** Today the owner cannot distinguish a dead wearable, a missing permission, an unregistered radio, and a healthy relay. A single preflight spoken from the pendant prevents wasted conversations and makes the prototype usable without engineering knowledge.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic probes and threshold checks for nearly everything; use a cheap text model only to turn structured failures into a concise explanation. Reserve realtime for speaking the result if the audio path is healthy.
- **latency:** A complete local preflight in 3 seconds, with a degraded text/dashboard answer in under 5 seconds when audio is unavailable.
- **cost:** Near-zero model cost for deterministic checks; under $0.01 for a templated spoken response. Serial loopback and relay health checks dominate latency, not inference.
- **security:** Do not expose account identifiers, browser URLs, or auth details in the spoken answer. Treat microphone loopback as a test recording with immediate deletion. Only report permission state and coarse connectivity, not tokens or private page contents.
- **missing:** A typed serial health/loopback protocol shared by nRF9160 firmware and ESP32 bridge; A relay endpoint that accepts a signed device-preflight report and returns normalized checks; Mac bridge probes for the two live USB serial devices and an audio round-trip timeout; A dashboard/pendant LED error vocabulary mapping failures to one actionable fix

### "If I double-press the pendant, stop every AI action currently running on my Mac or in my browser, cancel queued work, and tell me through the pendant what stopped and what could not be stopped."
- **useful because:** A wearable is the one surface the owner can reach while an automation is unexpectedly typing, navigating, or speaking. A physical interrupt is faster and more reliable than finding the Mac window, and it makes maximum-access automation safe to leave running.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** No model for detection or cancellation. Use a deterministic pendant event fan-out; use a cheap model only to compress cancellation receipts into one spoken sentence after the stop. Realtime is unnecessary except for the final voice response.
- **latency:** Button-to-cancel fan-out under 300 ms on USB and under 1.5 s over LTE; spoken status within 3 seconds. Do not wait for a model before issuing cancellation.
- **cost:** Effectively zero inference cost for the stop path; less than $0.01 for an optional templated spoken receipt. The main cost is implementing cancellation propagation and reliable receipts.
- **security:** The gesture must be difficult to trigger accidentally (double press within a bounded window, optionally hold to confirm). It should stop new mutations immediately, mark in-flight operations interrupted, and never claim rollback where none exists. Store only short-lived cancellation receipts.
- **missing:** Pendant firmware double-press event with debounce and a reserved emergency event code; Relay fan-out cancellation keyed to owner/session across Mac jobs, browser commands, and queued routines; Mac executor cooperative cancellation for run_shell, AppleScript, and UI loops; Browser extension cancellation acknowledgement and a durable partial-action receipt; A pendant-safe fallback tone/LED pattern when the network is down

### "Use my pendant as a hardware presence key: when I physically press and hold it, authorize exactly one sensitive Mac or logged-in-browser action that is already prepared, without sending my secret or relying on a spoken confirmation."
- **useful because:** The owner gets a fast, unambiguous way to approve a high-impact action while away from the keyboard, and a stolen browser session or replayed voice command cannot approve it by itself. This is a genuinely wearable capability rather than another Mac shortcut.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** No model for authorization. Deterministic challenge issuance, device signature verification, action-hash matching, and one-shot consumption should happen in firmware/relay/Mac bridge; use a cheap model only to explain a failed approval.
- **latency:** Under 500 ms from the completed long-press to authorization on USB; under 2 seconds over LTE. The prepared action must already exist, so no inference is on the critical path.
- **cost:** Negligible API cost. Hardware-secure key support and implementation dominate; a small secure element would be roughly $1–$3 in volume and consume only a few mW during verification.
- **security:** The key must be device-bound and non-exportable, with nonce/challenge, expiry, action hash, session binding, replay protection, and a visible LED/audio confirmation. Never authorize an altered action or silently widen scope. Lost-device revocation must be available from the dashboard.
- **missing:** A secure-element or protected-key implementation on the pendant (the current prototype has no established attestation path); Relay challenge/verification and revocation records; Mac bridge/browser extension hooks that attach a canonical action hash to a prepared action and consume one approval; A firmware long-press gesture and confirmation/error feedback

### "Fill private fields in my logged-in browser using values that stay on my Mac: let the relay describe which fields are needed, have the Mac resolve the values from Keychain or an owner-approved local profile, and return only a redacted completion receipt—not the secrets."
- **useful because:** The owner can complete repetitive authenticated forms without exposing addresses, IDs, phone numbers, or payment details to the relay, model, logs, or browser page extraction. This combines browser reach with local-only personal data instead of merely drafting a form.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use a small deterministic field-mapping service for known labels and local profile lookup; use a background model only when labels are ambiguous. Never send raw secret values to a language model or relay.
- **latency:** Known fields filled in under 2 seconds; ambiguous fields should pause and ask a concise spoken question rather than guess.
- **cost:** Near-zero API cost for local mappings; occasional ambiguity resolution costs under $0.01. Keychain access and browser DOM interaction dominate engineering effort.
- **security:** Values remain in the Mac process and are write-only into the target tab. Require origin/tab binding, an owner-approved field allowlist, no raw-value logging, clipboard avoidance, and a redacted before/after receipt. Payment and irreversible submission remain explicitly separate from filling.
- **missing:** A Mac-local Keychain/profile broker with field-level allowlists and audit redaction; Browser extension protocol for write-only field injection and origin binding; Relay schema for semantic field requests that carries labels/types but never values; A local scrubber that prevents secrets entering action receipts, model context, or telemetry


## Changes it proposed to its own stack

### `firmware` — Add a small, versioned pendant control-event protocol independent of audio: button press/double-press/long-press, USB-vs-LTE transport state, and a 4-state LED/buzzer status vocabulary. Events must be emitted locally over USB immediately and queued with sequence numbers for relay delivery when the link returns.
- **owner gets:** The owner gets dependable physical controls and understandable feedback even when speech, LTE, or the Mac is broken: they can start/stop capture, invoke the emergency stop, and know whether the system heard them.
- effort: Moderate firmware and Mac-bridge work: reserve event IDs, debounce in Zephyr, persist a tiny sequence counter, implement USB framing and relay translation, then add integration tests for disconnect/reconnect.  ·  risk: Incorrect debounce could cause accidental stops or missed presses; recover with a long-press reset and host-side duplicate suppression. A firmware update bug could strand the button, so retain the existing audio/button path as a compatibility mode.
- cost: No per-call API cost. Fits comfortably in RAM/flash if implemented as a compact event struct and ring buffer (well below 4 KB RAM); no additional hardware cost or meaningful power draw.  ·  latency: Local LED/button response becomes sub-50 ms; relay delivery remains link-dependent. Sequence numbers add negligible framing overhead.
- security: Control events must be authenticated to the paired relay session; an unpaired USB host may read only coarse device state and must not issue remote actions.
- depends on: USB serial transport for the currently connected nRF9160 and ESP32; A relay-side owner/session cancellation fan-out; A documented mapping from control events to /pipeline/events and job/browser cancellation

### `integration` — Create a local-only 'sensitive value lane' between Mac Keychain/profile storage and the browser extension: the relay sends a typed field request and origin-bound nonce, the Mac resolves an allowlisted value, injects it directly into the bound tab, and emits only a salted field-type receipt. Make the lane impossible for generic model/tool calls to read back.
- **owner gets:** The owner can finally automate the tedious parts of private forms without making the AI service a copy of their identity and secrets. A compromised or overbroad transcript sees that an address was filled, not the address itself.
- effort: High integration effort across Keychain access, browser content-script isolation, nonce/action binding, redacted receipts, and recovery tests for tab navigation or stale requests.  ·  risk: A field-classification bug could put the wrong value in a form. Recover with strict origin/label allowlists, a dry-run preview showing field names only, automatic clearing on tab change, and no submit capability in this lane.
- cost: No recurring model cost for known fields; modest local engineering/storage cost. Keychain lookup and injection add tens to hundreds of milliseconds.  ·  latency: Known-field completion should add less than 300 ms per field batch; ambiguous labels fall back to a user question.
- security: Strongly improves confidentiality, but creates a high-value local integration. Require macOS Keychain ACL, per-origin consent, nonce expiry, memory zeroization, and redacted telemetry.
- depends on: Browser extension field inspection/injection API; Mac Keychain/profile broker; Relay typed field-request schema; Strict separation between fill and submit actions


## What it asked for

_Nothing._
## Its own summary

Round 146 produced four non-duplicate items: (1) USB-tethered push-to-talk pendant operation using the physically connected nRF9160/ESP32, (2) a one-command spoken pendant readiness preflight, (3) a physical double-press emergency stop fan-out across Mac jobs/browser commands/relay work, and (4) a compact firmware control-event protocol with LED/buzzer state vocabulary and sequence numbers. Live status confirms relay and browser are online, but Mac readiness is false because Accessibility and Screen Recording remain unavailable; the chips are USB-connected yet no USB transport exists in the stack.

**Biggest unknown:** Whether the owner wants to manually grant Accessibility/Screen Recording to AI Pendant Agent. I did not re-request the blocked TCC permission. The major implementation gap is USB serial framing and transport/session binding between the connected pendant/ESP32 and the existing pipeline.

