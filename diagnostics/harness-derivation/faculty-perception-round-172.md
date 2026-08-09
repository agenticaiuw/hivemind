# Harness derivation — faculty-perception — round 172

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac observation and permissions** — At 2026-08-08T03:20Z the Mac agent's /observe reports inputReachability=verified, Accessibility and Screen Recording granted for com.aipendant.agent, secure input inactive, and UI actions will reach the screen. /ops/snapshot reports relay reachable, Mac bridge online, Safari extension online with 9 tabs and zero pending commands; no pendant appears in this Mac-agent inventory.
  - evidence: GET /observe HTTP 200 and GET /ops/snapshot HTTP 200 at 2026-08-08T03:20Z

## Capabilities it proposed

### "Tell me whether the system is actually healthy right now, and show me any disagreement instead of collapsing it into 'online'."
- **useful because:** The live probe just demonstrated why this matters: the Mac bridge and Safari extension are online, permissions are verified, and the relay is reachable, while the pendant is absent. A single green status would hide that critical split. This gives the owner a reality report with freshness and confidence, not a misleading boolean.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background for periodic reconciliation; realtime only when answering the owner's question
- **latency:** Under 2 seconds for an on-demand report; 30–60 seconds for periodic checks
- **cost:** <$0.01 per on-demand report if rendered from structured probes; periodic checks can be model-free. Cost is dominated by no model call unless there is a novel discrepancy to explain.
- **security:** Only health metadata leaves the Mac; never include page content, audio, tokens, or foreground-window titles unless explicitly requested. A stale device must be labeled unknown, not offline. Requires confirmation before using the result to suppress or reroute an action.
- **missing:** A relay-side authenticated health endpoint that includes the real device registry alongside /health; A Mac-side collector that records probe timestamps and source authority rather than returning one flattened snapshot; A discrepancy schema with per-field freshness, authority, and reason codes; A pendant heartbeat once the pendant actually registers

### "Is the pendant physically alive and usable right now, even if it has no relay connection?"
- **useful because:** Today the owner can have two chips physically attached over USB while the relay truthfully reports no registered pendant. This capability would distinguish USB enumeration, firmware responsiveness, microphone/audio-bridge health, and cloud registration, so 'offline' does not erase a device that is testable on the desk.
- **path:** pendant → mac-terminal → mac-planner → relay → dashboard
- **model tier:** background/model-free probes for serial and relay facts; realtime only to summarize a failure in plain language
- **latency:** 3 seconds for a normal serial health check; 15 seconds for a bounded audio loopback test
- **cost:** Near-zero API cost; one local probe and optionally one relay GET. Hardware test consumes brief USB power and a small amount of audio, no model call.
- **security:** Serial commands must be read-only and allowlisted; never flash firmware, erase storage, or write the SD fallback path without explicit confirmation. Do not transmit raw microphone audio during diagnostics by default—send only counters and hashes. Present 'USB responsive, relay absent' as two independent facts.
- **missing:** A read-only USB serial health protocol on the nRF9160 and ESP32 bridge (build ID, boot ID, monotonic age, audio counters); A Mac route or tool that opens /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA with bounded timeouts; A relay registration/heartbeat that the nRF9160 firmware actually emits, rather than inferring pendant state from converse sockets; A dashboard card that displays USB, audio bridge, and relay states separately

### "Before you look at or act on my screen, tell me whether the current context is private or high-risk, and refuse to collect a screenshot when it is."
- **useful because:** The system now has verified screen access, which is powerful enough to leak a password manager, Messages, banking page, or private photo. A perception layer should identify sensitive foreground apps, secure-input state, browser login walls, and tab context before any vision or browser capture, while still allowing a spoken answer. This is a user-visible safety boundary, not a status refactor.
- **path:** mac-vision → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** model-free policy classifier for bundle IDs, secure-input, URL host, and browser metadata; realtime model only when the owner asks for an explanation
- **latency:** Under 150 ms before every capture/action; under 1 second to explain a block
- **cost:** <$0.001 per check; local structured checks dominate. No image or page text should be sent when blocked.
- **security:** Default-deny for Passwords, banking/financial domains, private messages, secure input, and unknown login walls. Do not infer sensitivity from screenshot pixels if structured metadata is available. Require explicit confirmation to override a block for one named target, with an audit receipt that records policy reason but not the secret content.
- **missing:** A sensitivity policy with owner-editable app bundle and host classifications; A mandatory preflight hook shared by mac-vision, browser actions, and relay-originated capture requests; A structured 'blocked_before_capture' event in the action ledger and browser provenance store; A way to distinguish a permitted public tab from a private tab in the same browser window without relying on an image

### "When I come back, tell me what the system can honestly certify did *not* happen while I was away, and where that certificate stops."
- **useful because:** A digest lists surviving events; it cannot distinguish 'nothing happened' from 'the source was blind, expired, disconnected, or overwritten.' The owner needs bounded negative knowledge: for each surface, a signed interval of observed connectivity, sequence watermarks, retention holes, and explicit unknown gaps, so silence is never presented as absence.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background/model-free interval and sequence reconciliation; use the slower model only to phrase an explanation of gaps
- **latency:** Under 3 seconds after return; periodic watermark collection can run cheaply in the background
- **cost:** Near-zero model cost; storage is a bounded interval ledger (roughly tens of KB per day).
- **security:** The certificate must contain metadata and hashes, not page text or audio. It must be tamper-evident and say 'not observed' rather than 'did not happen.' Never let a missing heartbeat be converted into an owner-facing claim of safety.
- **missing:** A monotonic, append-only observation watermark from each surface; A shared clock-offset and retention-hole record, including relay restarts and Mac spool eviction; A signed absence-certificate format with explicit unknown intervals; A dashboard/voice response that refuses absolute negative claims when coverage is incomplete

### "Tell me when the system's understanding of my intent is unsafe because the surfaces disagree about what I was referring to."
- **useful because:** The wearable hears an utterance, the Mac has a foreground app, and Safari has a current tab—but those may point to different objects. Instead of silently choosing one, the system should expose an ambiguity map: candidate referents, supporting observations, contradictory observations, and the minimum clarification needed. This prevents a confident action on the wrong surface.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension
- **model tier:** realtime for low-latency candidate extraction; background model for cross-turn entity resolution and contradiction clustering
- **latency:** 250 ms to flag ambiguity during a live turn; under 2 seconds for a full candidate map
- **cost:** Low: structured metadata first; model spend only when more than one candidate survives. Audio and page content stay local unless needed.
- **security:** Never expose private tab titles or screen contents merely to explain ambiguity. Candidate identifiers should be pseudonymous until confirmation. Any action with unresolved disagreement must pause and ask, not pick the highest score silently.
- **missing:** A shared reference-identity format linking speech spans, visible UI targets, browser tab/session IDs, and relay turn IDs; Perception hooks that emit candidate observations before judgement/action receives them; A contradiction scorer that preserves multiple hypotheses instead of collapsing to one; A confirmation UI/voice grammar for 'the X in Safari' versus 'the X on screen'


## Changes it proposed to its own stack

### `hardware` — Add a dedicated, owner-visible trust indicator on the worn unit (a small RGB status LED or low-power e-ink badge) driven locally by firmware, with distinct states for microphone armed, audio transmitting, relay-confirmed, offline-buffering, and uncertainty. The indicator must be fail-safe: loss of firmware heartbeat or link yields an unmistakable unknown/offline state rather than retaining the last green state.
- **owner gets:** The owner can know at a glance whether the pendant is listening, sending, or merely pretending to be connected, without opening a phone or trusting a dashboard. This is especially valuable during relay outages and privacy-sensitive conversations.
- effort: Moderate hardware revision plus firmware state machine and a small cross-surface status vocabulary; validate visibility in daylight and at night, and ensure no continuous LED drain when worn.  ·  risk: A bright indicator could reveal private activity or annoy the owner; provide a physical disable gesture and low-brightness mode. Firmware bugs could show stale green, so include a watchdog-controlled unknown state and a hardware timeout. Recovery is to disable the indicator and retain audio behavior.
- cost: Roughly $2–8 in components/PCB area for an RGB LED and driver, negligible compute cost, typically under 1–5 mA while lit; e-ink costs more but near-zero steady-state power.  ·  latency: Local state changes should appear within one audio frame or heartbeat (<100 ms for local mic state; seconds for relay state).
- security: Improves privacy signaling but can itself disclose that the owner is speaking; allow physical disable and never encode message content or contact identity in the indicator.
- depends on: A defined cross-surface trust-state vocabulary shared by firmware, relay, Mac, and dashboard; The accepted offline-reality-beacon behavior as the source of local monotonic/link facts; A relay/device acknowledgement path that distinguishes socket write from actual device receipt; A hardware revision or external wearable indicator module; current USB-attached boards cannot provide this as a reliable owner-facing cue


## What it asked for

_Nothing._
## Its own summary

Discovered live state at 2026-08-08T03:20Z: Mac agent /observe is verified and actionable (Accessibility + Screen Recording granted; secure input off; foreground app Photos); /ops/snapshot says relay reachable, Mac bridge online, Safari extension online with 9 tabs and zero pending commands. The Mac agent does not expose /v1/devices/status (404), so pendant registration cannot be inferred from this surface. Proposed three owner-facing capabilities: disagreement-aware cross-surface health truth, USB-vs-relay pendant liveness diagnostics, and privacy/sensitivity preflight before any screen/browser capture. These are grounded in live routes but require missing glue, not new model features.

**Biggest unknown:** The continuity snapshot grant still does not resolve to a live implementation (resolver chose neither /ops/snapshot nor /pipeline), and there is no read-only USB serial health route for the physically connected nRF9160/ESP32. I still need a working cross-surface snapshot resolver and a bounded serial probe to establish device reality rather than infer it.

