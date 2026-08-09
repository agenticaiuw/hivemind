# Harness derivation — mac-planner — round 209

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Mark this.” (I press the pendant button while the document or Safari page I’m looking at is important.) Later: “Show me the things I marked.”"
- **useful because:** This is the pendant’s uniquely valuable capture affordance: a physical mark made at the exact moment becomes tied to the Mac’s foreground document, URL, tab title, and (when available) selected text, rather than an orphaned timestamp. The owner can recover the precise context without interrupting work or speaking aloud.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Realtime only for the tiny event acknowledgement; a cheap background model can normalize titles and deduplicate marks. Retrieval should be deterministic, not model-generated.
- **latency:** A local USB event acknowledgement under 300 ms; context attachment under 2 s while the Mac is awake; retrieval under 1 s from the local ledger.
- **cost:** Usually <$0.01 per mark (often zero if deterministic); model cost only for title normalization or deduplication. Storage is a few KB per mark.
- **security:** A mark may contain a private URL, document path, or selected text. Store the raw context locally first, redact query strings/password-like fields, and upload only after the existing pendant event policy permits it. Retrieval must show provenance and never expose page content merely because it was marked.
- **missing:** A real USB-serial exchange capability for /dev/cu.usbmodem00096003658* (the pending mac_serial_exchange request is unavailable this round); A semantic selected-text/document-identity read on the Mac; current mac_readonly_inspect is granted but unresolved in the live resolver; A durable cross-surface mark ledger and a relay route to query it

### "“Run a complete pendant check.”"
- **useful because:** Before a walk or call, the owner gets one honest pass/fail answer covering the parts that routinely fail differently: USB serial reachability, modem/WebSocket registration, microphone packet continuity, 24 kHz playback decode, ESP32-to-Bluetooth output, and relay receipt. It should name the failing segment and produce a shareable diagnostic receipt instead of making the owner guess whether silence is the pendant, bridge, headphones, or cloud.
- **path:** pendant → mac-planner → relay-realtime
- **model tier:** Background/cheap model for summarizing the measured fixture output; no expensive realtime model is needed. Firmware counters and pass/fail thresholds remain deterministic.
- **latency:** 60–90 seconds for the full fixture, with an immediate failure if either USB device is absent. A short connectivity-only check should return in under 5 seconds.
- **cost:** Near-zero API cost; one diagnostic invocation and a small receipt. Engineering cost is in the Mac serial harness and firmware test trigger, not inference.
- **security:** The fixture must synthesize audio only and never persist microphone content. Serial logs can contain device identifiers and network errors, so redact tokens and URLs before relay upload. Running a modem registration test may transmit traffic; make that explicit in the result.
- **missing:** mac_serial_exchange to open both live USB serial devices and arm the existing audio_path_diagnostic_fixture; A bridge-side loopback/health command that reports I2S and A2DP state without playing user audio; A relay endpoint that accepts the fixture counters, applies numeric acceptance thresholds, and returns a signed diagnostic receipt

### "“Use my pendant over USB.” (The pendant is plugged into my Mac, even when it has no LTE registration.)"
- **useful because:** The hardware is physically usable today but the radio is not registered. A USB-tethered mode would let the owner wear the same button, microphone, speaker path, and 24 kHz audio stack at a desk or hotel without waiting for LTE. The Mac carries the framed audio/control stream to the relay, while the pendant remains the low-latency physical interface.
- **path:** pendant → mac-planner → relay-realtime
- **model tier:** Realtime for the voice turn; no additional model is needed. The Mac is a transport adapter, not a second conversational agent.
- **latency:** Button-to-session start under 1 s; conversational round-trip should stay below 700 ms on a normal Wi-Fi Mac. USB framing must be back-pressured so it cannot starve the ESP32 Bluetooth path.
- **cost:** No meaningful per-turn API increase beyond the existing voice call. Engineering cost is a framed serial transport, reconnect state machine, and Mac route; hardware is already connected.
- **security:** Only the explicitly selected pendant serial devices may be opened; do not expose arbitrary serial ports. Pair the device identity with the relay session, encrypt the Mac-to-relay leg, and show a distinct single-LED/desktop indicator that USB mode is active. Never silently fall back from LTE to a Mac transport if the owner did not select it.
- **missing:** mac_serial_exchange for framed duplex access to /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A relay transport mode that accepts USB-originated Opus/control frames and preserves call/session receipts; Firmware mode negotiation so the pendant disables its unregistered-LTE reconnect loop while USB is authoritative

### "“Did that actually happen?” after I ask the hive to change something across my Mac and browser."
- **useful because:** Today a plan can return a job receipt without proving the world reached the intended state. This capability performs an independent postcondition check—file hash, app state, browser URL/form value, or calendar/mail result—and answers in plain language which step succeeded, which did not, and what remains. It prevents the owner from trusting a green transport receipt when a browser navigation or Mac mutation silently failed.
- **path:** relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Cheap background model to summarize structured observations; postcondition matching and hashes are deterministic. Realtime is only needed when the owner asks during a live conversation.
- **latency:** Read-only verification within 3 seconds for Mac/files and 5 seconds for a browser page; never block the original action on this later check unless explicitly requested.
- **cost:** Usually <$0.01, dominated by one optional summary call; observations and hashes are local/relay metadata.
- **security:** Verification must not dump private page bodies or email contents. Use field-level redaction and return only the minimum evidence (hash, URL origin, title, status). A failed check must not automatically retry a mutation, because retries can duplicate sends or purchases.
- **missing:** A first-class plan postcondition schema attached to /plan and /execute jobs; Browser read-back primitives for authenticated form state and a Mac read-back primitive for semantic app/document state; A receipt joiner that correlates relay job, Mac action, browser command, and final observation IDs


## Changes it proposed to its own stack

### `hardware` — Add a low-power NFC Type 4 tag reader (and a small local tag-ID cache) to the next pendant revision, with a signed tag-to-mode association handled by the relay. Tapping the pendant to an owner-installed tag at a desk, car, studio, or meeting room should emit a one-shot context transition; it must not continuously track location or read arbitrary nearby tags.
- **owner gets:** The owner gets intentional, reliable place/context changes without GPS, a phone, speech, or an ambiguous button gesture: “at the front door” can start a leave-home handoff, “at the desk” can enable USB voice mode, and “in the studio” can route audio correctly. It works when LTE is absent and gives the hive a physical context signal no Mac or browser can infer.
- effort: Medium hardware and firmware revision: NFC front end and antenna in the enclosure, signed tag provisioning, a small offline event queue, and relay rules for context transitions. Validate read range and coexistence with the nRF9160 antenna and ESP32 audio bridge.  ·  risk: Nearby malicious tags could spoof a context, so tags need cryptographic signatures or an owner-paired challenge rather than trusting a bare UID. A failed read must leave the current mode unchanged. Recover by deleting/re-pairing tags from the Mac or relay; no context transition should be irreversible.
- cost: Roughly $3–8 in reader, antenna, matching, and assembly at prototype quantities; tens of milliwatts only during a brief scan, with scan duty-cycled to avoid meaningful battery impact. No per-invocation API cost.  ·  latency: Local tag recognition should be under 250 ms; relay propagation is asynchronous and should not delay audio or button handling.
- security: Adds a physical intent signal but also a new proximity attack surface. Use cryptographic tag authentication, encrypted event transport, replay counters, and a local allowlist. Do not transmit tag-derived location unless the owner enabled that context rule.
- depends on: A next-board design beyond the current nRF9160 development pendant, which has only two buttons and one LED and no NFC hardware; Relay support for signed context-transition events and mode rules; Mac USB/desktop mode integration so a tag can select or exit USB voice transport without an ambiguous automatic fallback


## What it asked for

_Nothing._
## Its own summary

This round I recorded four owner-facing capabilities: exact pendant-to-current-Mac context marking, a complete pendant/bridge/relay diagnostic check, USB-tethered pendant voice mode for the currently unregistered LTE device, and independent postcondition verification for cross-node actions. The strongest immediate opportunity is USB voice mode: the hardware is physically attached now, but it needs a real serial framing path and relay transport mode. I also discovered that mac_workbench_transaction resolves as a read-only handoff route, while mac_readonly_inspect is still unresolved despite its typed schema.

**Biggest unknown:** The pending mac_serial_exchange capability is still unavailable. Without it I cannot test either live USB device, determine the actual serial framing already emitted by firmware, or prove whether USB voice mode and the diagnostic fixture can run today. I still need that tool (or an equivalent explicit serial read/write capability), plus a relay endpoint for USB-originated audio/control frames.

