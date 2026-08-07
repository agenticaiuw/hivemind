# Harness derivation — mac-planner — round 89

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If my browser or Mac is offline, queue the task safely, tell me when it comes back, and never execute a stale browser action without letting me cancel or restate it from the pendant."
- **useful because:** The live system currently has an offline browser extension with five pending commands. A request made in voice can otherwise become surprising later work when Chrome reconnects. This gives the owner a durable, spoken, cross-device handoff: explicit expiry, reconnect notice, and a fresh intent check before any queued browser mutation.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use the relay's cheap background model for queue classification and expiry summaries; use realtime only for the short spoken reconnect/cancel interaction. The Mac and extension execute deterministically; no model is needed to replay an approved command.
- **latency:** Immediate local acknowledgement on the pendant (<1 s); reconnect status within one heartbeat; cancellation or restatement should take one short voice turn. Queue reconciliation can run asynchronously.
- **cost:** Usually near-zero model cost: deterministic queue metadata and one short TTS response. A reconnect summary may cost roughly $0.001–$0.01 depending on speech length; storage is a few KB per queued command.
- **security:** Persist only the typed intent, target session/tab, creation time, expiry, and non-sensitive preview—not page contents or credentials. Destructive actions remain held even under the owner's maximum-access policy until a fresh spoken restatement. If the owner says cancel, revoke the command atomically in relay, Mac queue, and extension; late acknowledgements must be ignored.
- **missing:** A cross-surface command lease with TTL and state machine (queued, stale, cancelled, revalidated, executed).; Browser heartbeat handling that atomically leases or revokes pending commands instead of replaying all five blindly.; Pendant event/audio protocol for reconnect alerts and one-turn cancel/restate, including offline local acknowledgement.; Dashboard view showing pending, stale, and cancelled commands with receipts.

### "When I double-press the pendant before I walk away, put my Mac and logged-in browser into privacy pause, stop any spoken output, and when I return let me unlock and resume only the work that was safely paused."
- **useful because:** The owner wears the pendant but may leave an unattended Mac with private Mail, Calendar, and authenticated tabs. A physical gesture is available even when the Mac is locked or the browser is offline. This coordinates the pendant, relay, Mac, and browser into one reliable away/return boundary instead of requiring several manual actions.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** No model for the lock/unlock state machine. Use realtime only to acknowledge the gesture and report blocked/resumed work; use a cheap background model later to summarize what was paused. All security transitions and allowlists must be deterministic.
- **latency:** Local pendant LED/beep acknowledgement in under 300 ms; relay and Mac privacy pause within 2 seconds when linked. If disconnected, pendant enters a local pending-lock state and applies the lock as soon as the link returns. Resume should require one explicit long press plus spoken confirmation.
- **cost:** Negligible inference cost for state transitions; occasional one-sentence TTS, typically <$0.001. Requires a small encrypted state record and perhaps a few hundred bytes of firmware RAM.
- **security:** Do not claim the Mac is private until the bridge reports success. Pause should stop TTS/audio, cancel screenshots, suspend browser command polling, and invoke a deterministic macOS lock-screen/idle action; it must not delete cookies or sign out unless separately configured. Store no page data on the pendant. A failed or offline Mac action is announced as 'Mac still exposed' and remains visible in the dashboard. Resume must reject stale browser commands and produce a receipt.
- **missing:** A first-class cross-surface privacy lease and acknowledgement protocol.; Pendant double-press/long-press gesture mapping with debounce and offline state persistence.; Mac bridge action for lock-screen plus suspension of browser polling and active computer-use jobs.; Browser extension pause/resume handshake that does not discard authenticated sessions.; Dashboard status showing each surface's privacy state and the exact last successful transition.


## Changes it proposed to its own stack

### `hardware` — Replace the prototype nRF9160 DK's single LED/button feedback with a product pendant that includes a small tri-color status LED or sunlight-readable e-ink privacy indicator, a vibration motor, and a secure-element-backed link-status counter. The pendant should show distinct hardware-confirmed states—mic/audio active, relay connected, Mac/browser command lease active, and privacy-paused—using tactile/visual patterns that remain meaningful when the phone or Mac display is unavailable. The secure element signs state transitions so the relay and Mac can distinguish a real pendant gesture from a replayed network event.
- **owner gets:** The owner can know immediately, without opening a screen or trusting a spoken claim, whether the wearable is listening, connected, or still able to trigger private Mac/browser work. This is especially valuable while walking away from an authenticated Mac: a physical indicator gives a trustworthy answer even when Chrome is offline or the relay is unreachable.
- effort: New pendant PCB/enclosure revision, secure-element provisioning, low-power LED/e-ink and haptic drivers, firmware state machine, and relay/Mac verification of signed monotonic counters. Requires a product hardware prototype and testing across LTE dropouts, reboot, and low battery.  ·  risk: Added parts increase enclosure complexity and power draw; an ambiguous indicator could create false confidence. Fail closed: unknown, stale, or unverifiable state must display an unmistakable warning pattern rather than 'private.' Recover with a hardware reset and re-pairing flow that preserves no page or audio content.
- cost: Roughly $3–$10 BOM increase for secure element, haptic motor, driver, and indicator (more for e-ink); approximately 1–8 mA while indicating/vibrating, with deep-sleep nearly unchanged. No per-invocation API cost.  ·  latency: Gesture acknowledgement can be local in under 300 ms; signed state propagation adds roughly one network round trip when connected. E-ink updates are slower but need only change on state transitions.
- security: Improves authenticity and observability of privacy state through hardware-rooted signatures and monotonic anti-replay counters. It does not itself prevent a compromised Mac from misbehaving, so the indicator must distinguish 'Mac acknowledged' from merely 'relay requested.'
- depends on: A defined cross-surface privacy-state protocol with explicit per-surface acknowledgements; Product pendant redesign beyond the current nRF9160 development kit; Firmware support for signed state events and low-power feedback; Relay and Mac bridge verification of the pendant's counter and state signature


## What it asked for

### `s14-vkh3` (skill) — offline_privacy_pause_gesture
- does: Detect a debounced double-press of the single pendant button, immediately mute local playback and mark the device PRIVACY_PENDING even without network; send a signed pause nonce when LTE reconnects. A long press while PRIVACY_PENDING requests resume, but only after the relay confirms all linked surfaces are safe to resume.
- must be on-device because: The owner may be walking away with no link and needs an immediate physical privacy signal. Only firmware can mute the pendant/bridge path and remember the intent through a dropped connection; the relay cannot observe a gesture that never reaches it.
- trigger: Double button press to pause; long press to request resume; server acknowledgement event to transition pending to confirmed.
- storage: One small record in nonvolatile settings: mode, nonce/counter, timestamp/boot epoch, and last acknowledgement (well under 256 B). Do not store audio or page data.
- RAM budget: About 1–2 kB for debounce/state machine, event queue, and signed message buffer; comfortably within the 211,608 B application RAM, though existing Opus/audio buffers remain the dominant budget.

## Its own summary

Discovered the live system is healthy on the Mac/relay side, but Chrome is offline with five pending browser commands; Accessibility and Screen Recording are still not granted, while AppleScript automation is available. I added a distinct physical privacy-pause capability: pendant double-press immediately mutes/marks pending offline, relay coordinates a privacy lease, Mac locks and suspends jobs, browser polling pauses, and resume requires an explicit fresh gesture/confirmation. I also queued the required offline_privacy_pause_gesture firmware skill, designed for the nRF9160's single button and ~1–2 kB RAM. I do not need another tool or permission this round.

**Biggest unknown:** Implementation semantics of the Mac lock action and browser-extension pause handshake: the system must report per-surface success before claiming the owner's workspace is private, especially while Chrome is offline.

