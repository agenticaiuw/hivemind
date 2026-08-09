# Harness derivation — faculty-perception — round 156

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-permissions-and-surfaces** — Fresh GET /ops/snapshot at 2026-08-08T02:27Z reports Accessibility trusted, Screen Recording granted, requiredMissing/optionalMissing empty, permissions.ready=true; Safari browser bridge online with 9 tabs and zero pending commands; relay reachable, D1-backed, Mac bridge online. It does not establish a pendant: registry discovery still shows only home-macbook-bridge online and cloudflare-contract-test offline.
  - evidence: Authenticated GET /ops/snapshot response: permissions.ready=true, accessibility.trusted=true, screenRecording.granted=true, browser.online=true, pendingCommands=0, relay.reachable=true; discover devices lists no pendant.
- **mac-agent-device-route-boundary** — GET /v1/devices/status is not a route on the Mac agent (404 'No such route on this agent'); therefore Mac-side route discovery cannot verify relay pendant registry. The fresh Mac snapshot still reports relay reachable but only Mac bridge freshness, not pendant presence.
  - evidence: Authenticated probe_http GET /v1/devices/status returned HTTP 404 with hint GET /capabilities; GET /ops/snapshot separately reported relay reachable and macBridgeOnline.

## Capabilities it proposed

### "Before you act on my computer, tell me whether the evidence you are looking at is live, stale, or unverified—and show me the exact tab, Mac permission state, relay state, and pending-command state behind that judgment."
- **useful because:** The system can now see all of these surfaces, but currently they are separate facts and completion often gets mistaken for truth. This gives the owner a trustworthy go/no-go reality fence before consequential actions.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** cheap background/state-composition model; escalate to realtime only when the owner asks during a live voice turn
- **latency:** Under 500 ms from cached ops snapshot; at most 2 s when refreshing browser and relay state
- **cost:** Near-zero model cost for structured state; one small model call only to phrase conflicts
- **security:** Expose only tab URL/title and hashed session identifiers, never page bodies or cookies; require confirmation if a source is stale or permission state changes during an action.
- **missing:** A versioned freshness envelope on GET /ops/snapshot with observedAt per source; A single verdict schema distinguishing observed, inferred, and unknown; Relay-side correlation of the snapshot to the action attempt

### "When I ask you to act on a browser page, prove that the page you inspected is the same live tab you are about to change, and stop if it changed or the login/session became ambiguous."
- **useful because:** The browser is online and holds nine authenticated tabs, while relay reads have no durable ID or hash. This prevents acting on a cloud-rendered copy, stale tab, or login wall that only looks like the owner's page.
- **path:** browser-extension → mac-vision → mac-planner → relay → dashboard
- **model tier:** cheap deterministic comparison first; use realtime only to resolve a genuine visual or semantic mismatch
- **latency:** 1–2 s for inspect→hash→compare; hard stop immediately on mismatch
- **cost:** No model cost for URL/title/content-hash comparison; occasional vision call for layout ambiguity
- **security:** Never send authenticated page bodies to the relay; compute redacted local hashes and retain only capsule IDs, source URL, tab/window pseudonyms, and mismatch reason; confirmation required before mutation after any mismatch.
- **missing:** A relay read response ID and content hash; A live-tab snapshot hash emitted by the browser extension; A precondition token consumed by browser mutation routes

### "Walk me through commissioning the physically USB-connected pendant and audio bridge, prove each local hop, then register and test the relay path without pretending LTE or a pendant heartbeat exists."
- **useful because:** The chips are physically attached and testable now, but the relay has no registered pendant. This turns the current dead gap into a safe, observable first-use experience: serial discovery, audio loopback, websocket handshake, relay receipt, and explicit failure point.
- **path:** pendant → relay → mac-terminal → mac-planner → dashboard
- **model tier:** background deterministic diagnostics with a cheap model summarizing; realtime is unnecessary except for spoken guidance
- **latency:** 90 s for a full commissioning run; each hop reports within 5 s
- **cost:** Negligible model cost; local serial tests and one relay registration/heartbeat exchange dominate
- **security:** Never print or persist the relay API key; use a one-time pairing credential, redact serial logs, and require explicit confirmation before registering a device or sending microphone audio off-device.
- **missing:** A Mac serial-harness route for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A pendant-safe scoped credential instead of the firmware's admin-key websocket path; A commissioning report schema joining serial, bridge, websocket, and relay evidence

### "If the browser session, Mac permissions, or relay identity changes while you are working, stop immediately, tell me through the pendant, and show me exactly which trust boundary changed before anything is sent or clicked."
- **useful because:** Today a command can outlive the state in which it was authorized: a tab can navigate, a login can switch, or permissions can change while a job is pending. The owner needs interruption at the moment the evidence becomes unsafe, not an explanation afterward.
- **path:** pendant → browser-extension → mac-planner → relay → dashboard
- **model tier:** Deterministic monitors and cryptographic comparisons first; use the realtime model only to explain the specific boundary change in plain speech.
- **latency:** Detect within 250 ms of a browser heartbeat or Mac permission change; cancel queued mutations before dispatch.
- **cost:** Negligible model cost; continuous browser heartbeats and local hashes dominate, with one short explanation call only on violation.
- **security:** Keep page content local; transmit only domain, tab/session pseudonyms, state version, and violation class. A cancellation must be fail-closed and require fresh owner confirmation to resume.
- **missing:** Monotonic state-version tokens shared by browser extension, Mac agent, and relay; A cancellation primitive that invalidates queued browser and Mac commands; A pendant delivery path for urgent trust-boundary warnings

### "Keep a private, local-only record of what the pendant heard me authorize, what the Mac actually changed, and what the browser visibly showed afterward—then let me ask months later whether a specific action really happened."
- **useful because:** The owner currently has logs and receipts scattered by subsystem, with count/byte eviction and no durable owner-facing causal record. A compact local witness would answer disputes like “did I send that?” without uploading private content or confusing Mac completion with real-world outcome.
- **path:** pendant → mac-planner → browser-extension → relay → dashboard
- **model tier:** Local deterministic event joining and hashing; a cheaper text model summarizes a requested witness, with realtime reserved for live follow-up.
- **latency:** Record each event synchronously under 100 ms; answer historical queries within 2 s when retained.
- **cost:** Near-zero model cost for recording; small summarization call only when queried. Local encrypted storage is the main resource cost.
- **security:** Store redacted claims, hashes, timestamps, and device/session pseudonyms—not raw speech, page bodies, or credentials. Require explicit confirmation before exporting a witness off-device.
- **missing:** An encrypted append-only witness store with retention chosen by the owner rather than incidental count caps; A shared event envelope linking voice authorization, action attempt, browser observation, and relay/device outcome; A query route that returns an uncertainty-qualified causal chain

### "When the system is unsure, make the pendant communicate that uncertainty physically—using a distinct vibration or light pattern—before I rely on the answer, even if audio is masked by noise or I am not looking at a screen."
- **useful because:** Spoken confidence is easy to miss in a noisy environment and the dashboard is unavailable while the owner is moving. Perception can already identify stale, inferred, and contradictory evidence; the owner needs that distinction at the body, where it can affect a decision before an unsafe action.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic confidence classification from cross-surface evidence; no expensive model call for the physical signal, with realtime speech explaining only on request.
- **latency:** Emit the confidence pattern within 150 ms of classification; never delay ordinary speech more than one audio frame.
- **cost:** Negligible API cost; requires a small haptic/LED actuator and firmware power budget.
- **security:** Patterns must not reveal private content to bystanders; use only neutral states (confirmed, uncertain, blocked). Do not let confidence signaling override a required owner confirmation.
- **missing:** A haptic or LED output on the pendant, if the current nRF9160 enclosure lacks one; A compact confidence-state protocol shared by perception, relay, and firmware; A user calibration flow so the owner can distinguish patterns reliably


## Changes it proposed to its own stack

### `hardware` — Add a low-power, wearer-only haptic actuator to the pendant (coin ERM or LRA with a dedicated driver), plus a firmware state machine for three non-content patterns: confirmed, uncertain, and blocked. Perception supplies only the state and urgency; no speech or private data crosses the haptic interface.
- **owner gets:** The owner can tell a trustworthy answer from an uncertain one while walking, in noise, or with the phone away, and can stop before relying on a risky answer.
- effort: Moderate hardware revision and enclosure work; firmware driver/state machine; cross-surface confidence mapping and a short user calibration routine.  ·  risk: Added power draw, accidental vibration, and pattern confusion. Recover by disabling patterns remotely, reverting to silent mode, and requiring explicit confirmation for blocked states.
- cost: Roughly $2–$8 in actuator/driver/BOM cost and brief vibration bursts consuming tens of milliwatts; negligible API cost.  ·  latency: Under 150 ms from confidence classification to tactile output; should not delay audio.
- security: Improves privacy because uncertainty is conveyed without speaking sensitive details aloud; patterns must remain content-neutral.
- depends on: A shared confirmed/uncertain/blocked confidence protocol across perception, relay, Mac, and firmware; A firmware output driver and calibration flow; A device-side health/telemetry bit confirming the actuator is functioning


## What it asked for

_Nothing._
