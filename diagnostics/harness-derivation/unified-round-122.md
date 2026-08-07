# Harness derivation — unified — round 122

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Wait—stop talking. Do that instead, and when you’re done tell me where we left off.” (The pendant must interrupt speech immediately, redirect the active Mac/browser work, and later resume with a one-sentence checkpoint.)"
- **useful because:** A wearable assistant is only trustworthy if the owner can change their mind mid-sentence without waiting for playback to finish or losing a multi-step task. This makes interruption, redirection, and recovery one natural voice interaction across all surfaces.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime model only for barge-in intent and a short acknowledgement; background planner on the cheaper local Mac model for checkpointing and redirected work.
- **latency:** Mute/acknowledge within 250 ms of detected speech; redirect dispatch within 2 s; completion notification when the existing job receipt is available.
- **cost:** Low incremental API cost: one short realtime turn per interruption; checkpoint and planning use local Mac inference. Dominant cost is audio streaming, not reasoning.
- **security:** The spoken interruption and current task state cross the relay; browser credentials remain in the authenticated Mac bridge. Redirecting an irreversible action must still stop at the existing approval checkpoint.
- **missing:** firmware barge-in VAD and an immediate playback mute signal; a resumable task checkpoint schema that can be replaced by a spoken redirect; relay cancellation/redirect semantics that preserve the old receipt and link the new one

### "“Save this moment so I can find it later.” The system should bind what I just said to the active Safari page, selected text, visible screen evidence, and the resulting task or reminder, then let me retrieve it by natural language."
- **useful because:** People lose the connection between a thought and the page that caused it. A wearable trigger plus browser provenance creates a searchable memory with evidence instead of an ungrounded transcript or a bookmark that lacks intent.
- **path:** pendant → relay-realtime → mac-vision → browser-extension → mac-planner → dashboard
- **model tier:** Realtime for the short capture command; local Mac vision/browser extraction for page and selection evidence; cheap background model for normalization and later retrieval.
- **latency:** Acknowledge capture in under 500 ms; gather page/selection/screenshot evidence within 5 s; retrieval answer under 3 s when indexed.
- **cost:** Usually one short realtime turn plus local OCR/extraction. Storage is small JSON plus optional compressed screenshot; screenshot retention dominates storage, not API calls.
- **security:** Private page content and screenshots must stay on the Mac by default, with only hashes/structured snippets sent to relay. Mask passwords/payment fields and require explicit confirmation before syncing sensitive evidence.
- **missing:** a unified moment-record route joining audio transcript, active tab, selection, screenshot and action receipt; Mac active-window/selection capture that works without Accessibility where possible; natural-language retrieval over moment records with per-field sensitivity filtering

### "“My pendant is silent—fix it.” The system should test the entire worn-audio chain, identify whether the fault is USB, firmware, relay, Opus, I2S, ESP32, or headphones, repair safe software faults, and tell me exactly what I need to reconnect or approve."
- **useful because:** Today a silent wearable can fail at several opaque boundaries. One voice command should turn a frustrating hardware hunt into a bounded diagnosis, using the Mac as a serial instrument and the relay as the end-to-end observer.
- **path:** pendant → relay-realtime → mac-terminal → mac-planner → dashboard
- **model tier:** Cheap deterministic diagnostics first; local planner interprets logs and chooses safe retries; realtime model only explains the result conversationally.
- **latency:** First fault hypothesis in 10 s; safe retries within 30 s; never claim recovery until a loopback/test tone and receipt confirm it.
- **cost:** Near-zero model cost for scripted probes; occasional local planner call. USB serial tests and generated test audio dominate elapsed time.
- **security:** Firmware flashing, deleting recordings, or changing Bluetooth pairing require explicit confirmation. Diagnostics may contain transcripts and device identifiers; retain only a redacted receipt.
- **missing:** a Mac serial diagnostic tool for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; end-to-end synthetic audio correlation IDs across pendant, relay, and bridge; a safe repair matrix and human-readable fault receipt

### "“Lock everything down now.” The pendant should immediately mute its microphone and playback, pause queued Mac/browser work, revoke active browser sessions, disable new actions, and give me a short spoken confirmation; I can later say “restore” to re-enable only the devices and jobs I approve."
- **useful because:** A lost pendant, exposed screen, or mistaken command can otherwise leave several surfaces active at once. One physical/voice emergency command gives the owner a clear, reversible digital firebreak across the wearable, relay, Mac, and private browser.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic control plane only for lock, pause, revoke, and confirmation; no expensive model should be needed. Use the realtime model only if the owner asks for an explanation afterward.
- **latency:** Local mute and button acknowledgement under 150 ms; relay-wide lock under 2 s; all active jobs visibly marked locked within 5 s.
- **cost:** Near-zero API cost. Dominant work is implementing revocation and reliable propagation across the four surfaces.
- **security:** The lock command must be accepted from a physical button gesture even if the network is unavailable, and must not be bypassable by an already-running job. Restore requires explicit physical confirmation or a pre-authorized recovery phrase; preserve audit receipts without retaining microphone audio.
- **missing:** a durable fleet-wide emergency-lock state with monotonic generation numbers; firmware-local microphone/playback mute latch and a distinct unlock gesture; Mac and browser agents that check the lock generation before every action and revoke authenticated browser sessions; a recovery UI showing exactly what is paused, revoked, or still unreachable

### "“Show me exactly what would happen if I did that, but don’t change anything.” The system should run a cross-surface dry run—browser form effects, Mac file/calendar/mail effects, and downstream job changes—then present a before/after diff without touching the real accounts or filesystem."
- **useful because:** The owner can safely explore consequential workflows instead of choosing between blind trust and manually checking every surface. It is especially valuable when one request crosses a logged-in browser and local Mac state.
- **path:** relay-realtime → mac-planner → browser-extension → dashboard → pendant
- **model tier:** Local Mac planner and deterministic adapters perform the simulation; a cheap model summarizes the diff. Realtime is used only to acknowledge and read back a concise result.
- **latency:** Preview acknowledgement under 1 s; simple previews under 10 s; complex multi-surface previews may take 30 s but must show progress.
- **cost:** Low-to-moderate local compute; API cost is one summary call. Storage cost is temporary isolated browser profiles and filesystem snapshots.
- **security:** Simulation must use isolated browser sessions, shadow files, and non-sending mail/calendar APIs. If an adapter cannot guarantee dry-run semantics, mark that operation “not simulated” rather than execute it. Never upload private page contents merely to generate the diff.
- **missing:** transactional dry-run adapters for AppleScript, filesystem, browser forms, and job scheduling; isolated browser/session and temporary Mac workspace snapshots; a typed cross-surface before/after diff format with unsimulated-operation warnings


## Changes it proposed to its own stack

### `integration` — Add a USB-serial companion transport that makes the physically connected nRF9160 and ESP32 a first-class local pendant path when LTE is unregistered: framed, authenticated audio/events over /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA, with the same correlation IDs and receipts as relay traffic. The relay chooses LTE or Mac-USB per session, never both, and the pendant LED reports which path is active.
- **owner gets:** The owner can wear and test the real pendant today instead of waiting for cellular registration; conversations, playback, and button events continue over the Mac while preserving the same behavior they will get away from home.
- effort: Medium: Mac serial daemon, Zephyr framing/transport adapter, ESP32 bridge routing, relay session-path selection, and an end-to-end test harness.  ·  risk: USB disconnects or partial frames could wedge audio; use sequence numbers, bounded buffers, watchdog reset, and automatic fallback to LTE. Never silently route microphone audio over USB without the session LED state and dashboard indicator.
- cost: Negligible API cost; roughly 1–2 weeks engineering. No hardware cost; Mac CPU/USB power is minor.  ·  latency: Potentially lower latency than LTE (USB transport), with one extra framing hop; reconnect should be under 2 s.
- security: USB is a local trust boundary, not inherently private: authenticate the companion handshake, reject unknown serial identities, and encrypt audio/control frames if the Mac daemon is not the signed app.
- depends on: Mac serial diagnostic/access tool for both live device paths; stable audio packet framing and correlation IDs shared with /pipeline/audio; relay session transport selection and duplicate suppression

### `hardware` — Add a low-power haptic actuator and a second tactile control to the production pendant, with a local event vocabulary: short pulse for listening, double pulse for approval needed, long pulse for completion/error, and a hold gesture for the emergency lock. Keep the existing LED/button compatibility for the prototype and expose the same events to relay receipts.
- **owner gets:** The owner can understand and control the assistant discreetly in public, in darkness, or when headphones are disconnected—without looking at a screen or speaking sensitive commands aloud. The emergency gesture also works when the network is down.
- effort: Production enclosure/PCB revision, GPIO or I2C driver, firmware event mapping, and accessibility testing; prototype validation can use an external haptic breakout on the currently free I2C/GPIO resources.  ·  risk: False holds or vibration fatigue could annoy the owner; require deliberate timing, configurable patterns, and a physical override. Added openings and wiring need water/impact testing.
- cost: Approximately $2–6 BOM increase plus PCB/enclosure revision; haptic draw is tens of milliamps only during brief pulses, with negligible daily energy impact.  ·  latency: Local feedback is immediate (<50 ms) and removes reliance on network round trips for confirmation.
- security: A physical lock gesture reduces remote misuse, but unlock must require a distinct long hold plus spoken or dashboard confirmation; never expose raw gesture events as authority without replay protection.
- depends on: firmware-local mute/lock latch; event correlation and receipt protocol shared with relay; production pendant design replacing the current provisional nRF9160 DK enclosure


## What it asked for

_Nothing._
