# Harness derivation — mac-planner — round 152

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-mac-and-wearable-path** — Mac bridge and Safari extension are online; the nRF9160 pendant and ESP32 audio bridge are physically USB-connected per current system context, but relay reports pairing required and /ops/status shows Accessibility and Screen Recording ungranted, so UI computer-use loops are not ready.
  - evidence: GET /ops/status returned macBridgeOnline=true, browser online with 3 Safari tabs, pairingRequired=true, accessibility.trusted=false, screenRecording.granted=false; get_hardware_spec(bridge/io) confirms prototype USB-connected boards and one-button/one-LED I/O.

## Capabilities it proposed

### "“Use my pendant right now, even without LTE.”"
- **useful because:** The hardware is physically on this Mac today but currently cannot participate in the system because the pendant is unregistered. This would make the wearable useful in the very environment where it is easiest to test: USB-tethered, offline, and still able to start/stop conversations and play responses, then reconcile state when LTE returns.
- **path:** pendant → mac-planner → relay-realtime → unified
- **model tier:** Realtime only for the live voice turn; a cheap background worker reconciles queued events and audio receipts after reconnect.
- **latency:** Button-to-session-start under 500 ms locally; speech can use the existing Mac/relay path with normal network latency. Reconnect reconciliation may take seconds.
- **cost:** Negligible API cost for button/event forwarding; speech remains the dominant cost. One local serial daemon and a small durable queue are the engineering cost.
- **security:** USB serial is a privileged local control path: bind only the two explicitly configured serial device identities, authenticate the local bridge, and never expose raw serial commands to the browser. Store only encrypted short-lived audio/event buffers; require explicit pairing before forwarding private speech.
- **missing:** A Mac USB serial bridge for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A framed, authenticated event/audio protocol that carries button state, PCM, playback acknowledgements, and reconnect sequence numbers; A relay local-ingress mode that accepts tethered sessions without claiming LTE registration; A durable deduplicating reconciliation queue for events and audio receipts

### "“Tell me where my private sources disagree before I make a decision.”"
- **useful because:** Calendar can say a meeting is confirmed while Mail says it moved, a logged-in order page can show a different deadline than an email, or a browser dashboard can lag behind a local document. Today the system summarizes sources, but does not explicitly surface contradictions. This prevents the owner acting on a plausible but stale single source.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Background model performs extraction and entity/date normalization; realtime model is used only to answer the owner's follow-up question or read the short conflict brief aloud.
- **latency:** On-demand scan in 10–20 seconds for up to 3 open tabs plus bounded Mail/Calendar reads; spoken answer under 2 seconds after the scan is cached.
- **cost:** One inexpensive extraction/comparison call per scan; realtime tokens only for the final conversational answer. Dominant cost is authenticated page extraction, not synthesis.
- **security:** Never send full private pages by default: extract only claims, dates, amounts, and source snippets with redaction. Keep source URLs/tab IDs and hashes locally for audit. No mutation or sending; browser access must be limited to already-open authenticated tabs.
- **missing:** A normalized claim schema with subject, predicate, value, time interval, source, and freshness; A contradiction detector that distinguishes true conflicts from different scopes or timestamps; A cited conflict inbox and pendant-friendly short rendering; A browser extraction route that can read several already-open authenticated tabs in one bounded request

### "“When you do something for me, prove that it actually happened.”"
- **useful because:** A successful click or typed command is not the same as the intended outcome: a file may be saved in the wrong folder, a browser form may reject a field, or a calendar event may be created with the wrong time zone. The system should execute, then independently inspect the resulting Mac/browser state and report evidence instead of claiming success from an action receipt alone.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-action
- **model tier:** Cheap deterministic postcondition checks first (file existence/hash, app state, URL/title/text, Calendar/Mail readback); use the realtime model only when evidence is ambiguous and the owner is asking live.
- **latency:** Add under 1 second for local file/app checks and 2–5 seconds for browser or Calendar readback. If verification cannot complete, say “executed but unverified” immediately and finish asynchronously.
- **cost:** Near-zero model cost for typed checks; occasional small model call to interpret browser evidence. Engineering cost is a postcondition contract attached to each action plan.
- **security:** Verification must be read-only and scoped to the action's target; do not dump unrelated page content or mailbox data. Preserve before/after hashes, URLs, and minimal snippets in the receipt. Never silently retry a potentially irreversible action because verification failed.
- **missing:** An action-plan postcondition schema (what observable state proves success, and timeout); Readback adapters for files, Calendar/Reminders, app state, and browser tab DOM; A receipt state machine separating executed, verified, failed, and unverified; A concise pendant rendering that cites the observed evidence

### "“Make this whole assistant recoverable if my Mac is lost, replaced, or corrupted.”"
- **useful because:** Today the owner's useful state is fragmented across Mac files, browser sessions, relay state, routines, receipts, and pendant configuration. A Mac failure could destroy continuity even though the owner still has the wearable. They should be able to create an encrypted recovery bundle, test that it is restorable, and rehydrate a replacement Mac without exposing browser secrets or raw audio.
- **path:** mac-planner → relay-realtime → browser-extension → pendant → unified
- **model tier:** A cheap background job performs inventory, encryption, integrity checks, and restore simulation; realtime is used only to guide the owner through an interactive recovery.
- **latency:** Incremental backup in the background; a first full bundle in under five minutes. Restore should produce a usable shell within ten minutes, with browser re-pairing explicitly separated.
- **cost:** Low recurring storage/cryptographic cost; dominant cost is local disk or owner-selected encrypted storage. No model call should be needed for ordinary backups.
- **security:** Never export passwords, cookies, raw microphone audio, or bearer tokens by default. Encrypt with an owner-held passphrase or hardware-backed key, split sensitive browser-session metadata from restorable preferences, and provide a manifest showing exactly what is included.
- **missing:** A versioned recovery-bundle format covering relay state, routines, receipts, context data, Mac preferences, and pendant firmware/configuration; A redaction and secret-exclusion inventory pass; Encrypted export/import and restore simulation; A browser re-pairing flow that restores named tab/watch definitions without copying session cookies

### "“When I say ‘take this with me,’ move whatever I’m listening to on the Mac onto the pendant and let me resume it later at the exact point.”"
- **useful because:** The owner should not lose a podcast, meeting recording, generated briefing, or spoken answer when leaving the Mac. Today Mac playback, relay audio, and the wearable are separate experiences with no semantic handoff or resume position.
- **path:** mac-planner → pendant → relay-realtime → unified
- **model tier:** Deterministic media metadata and byte-range handling do the work; use a cheap model only to classify the current media and create a short spoken bookmark. Realtime is unnecessary except for a live voice command.
- **latency:** Capture the current item and position in under one second; start playback on the pendant within three seconds. Upload/resampling can continue in the background.
- **cost:** Usually no model cost; storage and transfer dominate for long recordings. Generated speech costs only when creating a bookmark.
- **security:** Do not upload commercial or private media without an explicit per-item setting. Keep resume tokens and local file paths private, use encrypted transfer, and expire cached media after the owner-defined retention period.
- **missing:** A media handoff protocol carrying source identity, position, duration, codec, and resume token; Mac adapters for Music, Safari audio/video, QuickTime, and generated briefing playback; Pendant/bridge playback control and bookmark persistence; Relay storage that supports encrypted range delivery and deduplication

### "“Know which account I’m acting as, and never confuse my personal and work identities.”"
- **useful because:** The browser can hold multiple authenticated identities, while the Mac and relay currently reason mostly from URLs and tab state. A wrong-account action can leak information or create an irreversible mistake even when the page itself looks correct. The owner should see a human-readable identity label attached to each tab and action target, with mismatches reported before execution.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → faculty-perception → faculty-action
- **model tier:** Deterministic account fingerprints and domain/tenant metadata handle normal checks; a small model resolves ambiguous page identity text. Realtime is only needed to explain a detected mismatch conversationally.
- **latency:** Identity lookup under 300 ms for known tabs; under two seconds when a page must be inspected. Do not delay unrelated read-only browsing.
- **cost:** Near-zero model cost after fingerprints are learned; minimal local storage. The expensive part is initial per-service identity adapters.
- **security:** Store salted fingerprints and labels, not passwords, cookies, or full account identifiers. Never infer identity from a URL alone. For an unknown or conflicting identity, stop the targeted mutation and report the evidence without exposing unrelated account data.
- **missing:** A browser account-fingerprint adapter for common identity providers and arbitrary pages; Per-tab identity labels and tenant/session binding in the browser bridge; Action-target metadata that carries intended identity through planning and execution; A mismatch event and pendant-readable warning


## Changes it proposed to its own stack

### `integration` — Add a Mac-side tether coordinator that identifies the two live USB serial devices by USB VID/PID and stable serial, opens them at the firmware baud, translates pendant button/audio frames into the existing /pipeline/events and /pipeline/audio routes, and exposes a small reconnecting local session. It must support deterministic sequence numbers, bounded buffering, and a playback acknowledgement back to the ESP32 bridge.
- **owner gets:** They can wear and use the actual pendant on the Mac immediately—even while LTE registration is absent—and receive a reliable response rather than waiting for a hypothetical network deployment.
- effort: Medium: serial framing and device discovery, a local daemon or launch agent, relay/local-ingress handshake, and firmware test fixtures for both chips.  ·  risk: A bad frame parser could wedge audio or leave the serial port locked; recover by closing/reopening ports, dropping malformed frames, and keeping the existing network path untouched. Never flash firmware automatically.
- cost: No recurring API cost beyond normal speech. Small local daemon; no new hardware cost. RAM pressure is on the ESP32 bridge, so buffers must stay below the known 44 kB starvation threshold.  ·  latency: Button events should be sub-100 ms over USB; audio adds only serial framing and local forwarding latency. Reconnect replay is asynchronous.
- security: Treat USB device identity as a pairing boundary; authenticate frames and keep the local ingress bound to loopback. Do not make serial control reachable from Safari or the LAN.
- depends on: A documented framed serial protocol for nRF9160 and ESP32; A relay/local-ingress endpoint or Mac-local pipeline mode; Firmware build/test access for the physically connected boards


## What it asked for

_Nothing._
