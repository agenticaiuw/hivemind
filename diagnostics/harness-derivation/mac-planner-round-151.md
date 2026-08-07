# Harness derivation — mac-planner — round 151

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If something urgent arrives while I’m focused, interrupt me once; otherwise collect it quietly and give me a single digest when I’m free.”"
- **useful because:** The pendant is the only surface that can reach the owner away from the keyboard, while the Mac and authenticated browser are the only places that can establish what is urgent. This turns noisy mail/browser changes into a context-aware interrupt policy rather than another polling brief.
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision → unified → pendant
- **model tier:** Use a cheap background classifier for incoming Calendar/Mail/browser-watch deltas and a realtime model only when the owner asks follow-up by voice. The relay owns the urgency queue; the Mac supplies foreground app/focus state and the browser supplies cited private-page deltas; pendant delivers one short spoken alert plus LED pattern.
- **latency:** Under 10 seconds from an observed delta to a queued decision; under 2 seconds for delivery once the owner is interruptible. Quiet items can wait for the next focus transition or scheduled digest.
- **cost:** Low when quiet (event hashing and a small classifier); roughly one short realtime turn only for an interrupt or follow-up. Dominant cost is private-page extraction and speech generation, not idle monitoring.
- **security:** Only explicitly enrolled mail/calendar sources and browser watches leave their surfaces. Do not transmit page bodies for low-confidence items; send title, sender, deadline, and a source hash first. Never send, delete, or click. A user-configurable 'never interrupt' category and audit trail are required.
- **missing:** A cross-surface urgency event schema with deduplication and expiry; A Mac focus/idle transition publisher that does not require Accessibility for its baseline; A relay-side quiet-hours and interruption budget store; A pendant notification queue/LED/audio command that works when USB-tethered and later over LTE

### "“Test the pendant and audio bridge end to end, tell me exactly where the path fails, and leave a reproducible report I can hand to the firmware agent.”"
- **useful because:** The chips are physically connected over USB today but are not LTE-registered, so this can provide value immediately instead of pretending the wearable is online. One spoken request would exercise serial discovery, firmware diagnostics, I2S/Opus timing, ESP32 Bluetooth output, and relay reachability, then produce actionable evidence rather than a vague 'device offline'.
- **path:** pendant → mac-planner → mac-terminal → relay-realtime → unified → faculty-perception → faculty-action
- **model tier:** Use deterministic scripts and a cheap diagnostic model for parsing UART counters and known-good thresholds; reserve realtime reasoning for explaining an ambiguous failure to the owner. No cloud model is needed for raw audio or serial logs unless the owner explicitly asks to upload them.
- **latency:** A wired smoke test in 30–90 seconds; a full loopback and artifact report in under 5 minutes. The owner should get a one-sentence result first, followed by a report path and failing stage.
- **cost:** Near-zero API cost; dominated by local serial capture, test-tone playback, and optional firmware build/flash time. A cloud call is only needed for novel log interpretation.
- **security:** UART logs can contain tokens or private speech metadata. Redact credentials and retain raw logs only in ~/AI-Pendant-Workspace/diagnostics unless explicitly uploaded. Flashing must identify the exact port and build before writing; do not erase user SD data.
- **missing:** A stable serial diagnostic protocol for nRF9160 and ESP32 with versioned commands; A local test fixture that injects a deterministic mic tone and verifies decoded speaker output without opening a microphone to the room; Port discovery/locking for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A report schema with stage, timestamps, counters, thresholds, and firmware/build hashes; An optional relay reachability test that distinguishes 'not LTE registered' from TLS/WebSocket failure

### "“Before I accept this appointment or commit to this purchase, check all the relevant private sources for conflicts and tell me the exact evidence and two safe alternatives—without changing anything.”"
- **useful because:** A single source cannot catch the real constraint: Calendar may show a free slot while Mail contains a travel deadline, or an authenticated reservation page may overlap a meeting. The pendant gives a fast voice trigger, Safari supplies private account state, Calendar/Mail provide local evidence, and the relay reconciles them into a decision without committing the owner.
- **path:** relay-realtime → pendant → mac-planner → browser-extension → faculty-perception → faculty-judgement → unified
- **model tier:** Run deterministic date/entity extraction locally for Calendar/Mail/browser pages, then use a background reasoning model to reconcile overlaps and rank alternatives. Use realtime only to answer the owner's spoken follow-up; do not send any page body to realtime by default.
- **latency:** Return a preliminary conflict result in 5 seconds for Calendar/Mail-only checks and under 20 seconds when an authenticated page must be read. Alternatives may take another 10 seconds, but the owner must receive an explicit 'no conflict found' or 'unable to verify' state.
- **cost:** Usually one inexpensive reconciliation call plus local extraction; browser reads dominate latency. Realtime cost is limited to follow-up conversation.
- **security:** Read-only by default. Scope each check to named sources and a time window; redact unrelated mail and account identifiers. Evidence must include source, timestamp, and a short quoted field. Never accept, buy, send, or submit. Keep the final evidence packet local unless the owner asks to sync it.
- **missing:** A cross-source constraint schema for time windows, locations, deadlines, quantities, and cancellation terms; A browser extraction contract that returns normalized fields with source citations rather than arbitrary page text; A local join/redaction stage between mac_read_sources/browser and relay reasoning; A spoken response format that distinguishes verified, inferred, and inaccessible constraints

### "“Run the failing test, inspect the relevant code and current documentation, explain the smallest safe fix, and leave a patch plus a test result for me to review—do not commit or push.”"
- **useful because:** Today the owner must manually move between the pendant, terminal, editor, browser documentation, and test output. This would make the wearable a real entry point to a bounded engineering loop: the Mac runs the repository test and prepares the patch, the browser reads the relevant authenticated or public docs, and the relay returns a concise spoken diagnosis while preserving reviewable artifacts.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → faculty-perception → faculty-judgement → faculty-action → unified
- **model tier:** Use a cheaper background coding model for test-log triage, repository search, and patch drafting; use realtime only for the owner's short voice interaction and clarification. A separate deterministic local runner executes tests and records exact commands, exit codes, and diffs.
- **latency:** Acknowledge immediately, produce an initial diagnosis in 30 seconds when the test is short, and allow several minutes for a full test suite. The owner should be able to leave and later receive a completion receipt with patch path, tests run, and unresolved uncertainty.
- **cost:** One background coding invocation plus local compute; browser documentation reads and long test execution dominate. No audio or code needs to leave the Mac unless explicitly requested.
- **security:** Default to the current repository and a read-only branch/worktree. Never commit, push, modify secrets, or contact external services. Redact tokens from logs and require explicit scope when authenticated documentation is involved. Preserve the original tree and provide a complete diff and rollback path.
- **missing:** A sandboxed repository worktree executor with allowlisted test commands and timeout/resource limits; A typed patch artifact containing diff, files changed, test commands, outputs, and model rationale; A browser-to-code citation bridge that records the exact documentation URL and quoted rule used; A durable voice job that survives the owner leaving the Mac and reports completion without replaying actions

### "“If my pendant or Mac is lost, revoke its access everywhere and erase only the AI Pendant data, then show me proof of what was revoked and what was preserved.”"
- **useful because:** There is no owner-facing recovery action for a lost wearable or compromised Mac. The relay can remain reachable while the Mac and pendant are not: it should invalidate device/session credentials, stop browser bridges, command a tethered or later-reconnected pendant to wipe its failure-buffer data, and produce a receipt so the owner knows personal files were not touched.
- **path:** relay-realtime → unified → dashboard → pendant → mac-planner → browser-extension → faculty-action
- **model tier:** Use deterministic revocation and deletion workflows; use a background model only to explain the receipt in plain language. Never use a generative model to decide which credentials or paths to delete.
- **latency:** Revoke relay credentials and browser sessions within seconds; Mac cleanup on next connection within one minute; pendant wipe on next USB/LTE contact. The owner gets a durable receipt even if the device never reconnects.
- **cost:** Negligible API cost; dominated by secure key rotation, session invalidation, and verified local deletion.
- **security:** This is destructive and must require an authenticated recovery factor distinct from the lost pendant, with explicit scope and a final confirmation. Wipe only a dedicated pendant data partition and ~/AI-Pendant-Workspace state, never arbitrary files. Preserve an immutable audit receipt without retaining secrets; handle an offline pendant by marking wipe-pending and refusing new sessions when it returns.
- **missing:** Per-device credentials and revocation lists enforced by relay, Mac bridge, and pendant; A dedicated encrypted pendant data partition or wipeable namespace separate from firmware and owner SD files; A Mac bridge kill-switch that closes browser sessions and removes local tokens without deleting unrelated browser data; A recovery workflow with a second factor and tamper-evident revocation receipt


## Changes it proposed to its own stack

### `hardware` — Revise the wearable from the dev kit into a small carrier with a low-power fuel gauge (I2C), a vibration motor with a protected driver, and a second capacitive/tactile input; expose battery percentage, charging state, and haptic acknowledgements to firmware. Keep the existing full-duplex I2S pins and route the gauge/haptics onto the currently free I2C/GPIO resources.
- **owner gets:** The owner can currently miss the one LED and cannot know whether a failed conversation is radio, battery, or audio. A discreet vibration confirms button presses and incoming queued work without opening the microphone or looking at the device; a real battery estimate lets the system warn before an important call dies.
- effort: New carrier/enclosure spin, power characterization, Zephyr fuel-gauge and haptic drivers, and updated event protocol; moderate firmware plus one hardware revision. Prototype with an I2C gauge breakout and coin vibration motor first, then integrate.  ·  risk: Added motor noise and current spikes could corrupt mic capture or brown out LTE bursts; mitigate with a MOSFET, separate filtered rail, duty limits, and tests during simultaneous TX/audio. A second input increases accidental gestures; ship conservative debounce and allow disabling it. Recovery is to fall back to LED/audio and existing single-button behavior.
- cost: Roughly $3–8 BOM increase at volume for gauge, driver, motor, and input; vibration bursts around 10–80 mA, gauge under 100 µA, with negligible idle impact. API cost unchanged.  ·  latency: Immediate local haptic acknowledgement (<50 ms); battery telemetry can be sampled every 30–60 seconds and piggybacked on existing status messages.
- security: Battery and gesture state are low sensitivity. Do not expose raw gesture timing as an owner identifier; keep it local unless needed for diagnostics.
- depends on: A versioned pendant status message shared with relay and Mac; An I2C address/power budget allocation that preserves the single full-duplex I2S path; A local diagnostic test for haptic and fuel-gauge readings

### `hardware` — Add a secure element and a physically isolated wipeable data partition to the wearable carrier, with per-device keys generated on first boot and a bootloader-enforced revoked state. The pendant should accept signed revoke/wipe commands over USB or LTE, erase only buffered audio/metadata, and refuse to open a new session after its credential is revoked until re-provisioned.
- **owner gets:** If the pendant is lost, the owner can protect private conversations and account access remotely instead of hoping nobody connects it. Recovery becomes a clear, verifiable operation rather than replacing every credential by hand.
- effort: Carrier redesign, secure-element integration, signed-command protocol, bootloader state machine, partition layout, manufacturing/provisioning flow, and destructive-path testing; substantial firmware and hardware work.  ·  risk: A false revoke or interrupted wipe could strand the device; require an offline recovery key, monotonic command counters, and an unmistakable local confirmation on re-provisioning. Secure-element supply or firmware bugs could make units unrecoverable, so retain a factory recovery path that cannot read user data.
- cost: Approximately $1–3 BOM increase in volume plus manufacturing provisioning; negligible runtime draw except during cryptographic operations.  ·  latency: Normal session setup may add tens of milliseconds for key operations; revocation is effectively immediate when connected and queued safely when offline.
- security: Strongly improves device identity, credential isolation, and deletion guarantees. It changes the threat model from bearer-token possession to revocable per-device identity.
- depends on: Relay-enforced per-device credential registry; A signed command format shared by relay, Mac bridge, and pendant; Dedicated wipeable storage namespace separate from firmware and owner SD content; Owner recovery-factor and re-provisioning workflow


## What it asked for

_Nothing._
## Its own summary

Round 151 produced three distinct owner-facing directions: (1) a context-aware urgency interrupt queue spanning browser, Mac focus state, relay, and pendant (recorder marked it somewhat close to an existing quiet-notification idea, so it needs a clearly differentiated implementation); (2) an immediately testable USB-tethered pendant/ESP32 end-to-end diagnostic command that emits a reproducible firmware handoff report; and (3) a read-only cross-source conflict checker that reconciles Calendar, Mail, and authenticated pages before the owner accepts an appointment or purchase. I also proposed a physical carrier revision adding a fuel gauge, haptic motor, and second input, so the wearable can warn about battery and acknowledge events silently. I still need implementation of the serial test protocol/fixture, normalized cross-source constraint and evidence schemas, and a shared pendant status/event protocol. Accessibility remains owner-manual blocked; I did not re-request it.

**Biggest unknown:** Whether the current USB serial firmware exposes enough deterministic counters/test hooks to distinguish I2S, Opus, Bluetooth, and LTE failures without adding a firmware diagnostic mode.

