# Harness derivation — faculty-perception — round 90

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **device_presence** — The live device inventory has no pendant: only home-macbook-bridge is online; home-chrome and cloudflare-contract-test are offline. The advertised /v1/devices/status route does not exist on this Mac agent.
  - evidence: discover devices Round 90; GET /v1/devices/status returned 404; GET /ops/status relay payload macBridgeOnline=true.
- **mac_input_reachability** — The running AI Pendant Agent cannot currently synthesize UI input: Accessibility and Screen Recording are false, inputReachability is failed, and observe says UI action receipts cannot be trusted.
  - evidence: GET /observe at 2026-08-07T13:50:13.484Z and GET /ops/status.
- **browser_connectivity** — The browser extension is offline with 9 pending commands and no attached tab, so browser actions cannot presently be verified as executed.
  - evidence: GET /browser/status and GET /ops/status at Round 90.
- **audio_provenance** — Pipeline history contains a 24,000 Hz mono PCM TTS response, but a separate live LTE input telemetry record reports 15,625 Hz PCM input; these are different directions and should not be conflated as an end-to-end 24 kHz path.
  - evidence: GET /pipeline response: TTS event metadata sampleRate=24000; realtime plan inputTelemetry sampleRate=15625, format pcm-s16le.

## Capabilities it proposed

### "Before acting, tell me what is reachable right now and whether the last thing actually happened: distinguish live device state from stale history, queued commands, and merely accepted uploads, with a source and age for each."
- **useful because:** Today the system can report a relay-accepted response as if a pendant could receive it, or a browser/UI receipt as if the action reached the screen. This gives the owner an honest, spoken answer and lets judgement/action avoid acting on stale or unverifiable state. It is specifically cross-node: the relay knows delivery, the Mac knows local permissions, the browser knows attachment, and the pipeline/jobs know whether work is only queued or completed.
- **path:** relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action → mac-terminal
- **model tier:** Deterministic evidence reducer on relay/Mac; use the realtime model only to phrase the short spoken result, never to infer freshness or delivery.
- **latency:** Under 1 second for cached state; up to 3 seconds when refreshing Mac, browser, and relay observations in parallel.
- **cost:** Near-zero model cost for reduction; one short realtime response only when spoken. Dominant cost is three authenticated status reads and optional relay refresh.
- **security:** Expose only state, provenance, timestamps, and redacted job metadata; never include page contents or secrets. Treat 'accepted by relay' and 'UI action returned' as non-delivery until a device/browser acknowledgment exists. Require confirmation before using this evidence to send, delete, purchase, or submit.
- **missing:** A shared typed observation/evidence schema with observedAt, sourceNode, freshness TTL, state (live/queued/accepted/delivered/failed/unknown), and confidence; Relay delivery acknowledgment tied to a device receipt, not merely upload acceptance; A browser heartbeat/command result that explicitly identifies execution versus queueing; A judgement/action gate consuming the evidence reducer before claiming completion


## Changes it proposed to its own stack

### `integration` — Add a direction-aware audio contract verifier spanning Mac, relay, and future pendant: on every audio upload, persist declared and measured sample rate/channels/bit depth/byte count, compute duration from PCM, verify the relay payload matches the Mac-produced artifact, and mark input capture versus output playback separately. Reject or quarantine metadata that claims 24 kHz when measured PCM is not 24 kHz; when a pendant exists, close the loop with a playback-start/finish acknowledgment referencing the artifact hash.
- **owner gets:** The owner gets intelligible audio instead of a falsely reassuring '24 kHz path complete' label: capture quality, rendered response quality, and actual playback become separately trustworthy, and malformed audio is caught before it reaches their ear.
- effort: Medium: shared schema and validator in Mac pipeline/relay, plus a small firmware acknowledgment once a pendant is connected; add fixtures for 15,625 Hz input and 24,000 Hz output.  ·  risk: Old telemetry may fail strict validation, so run audit-only first and quarantine rather than delete. If the pendant is offline, report 'not played' rather than failing the whole job. Recover by retaining the original artifact and validator diagnostics.
- cost: Negligible API cost; a few hundred bytes of metadata per audio artifact and one hash computation. Firmware flash/RAM impact is small (roughly 4–8 KB code, <1 KB state) when hardware exists.  ·  latency: Under 10 ms for metadata/PCM validation; acknowledgment adds no response latency and only changes completion status.
- security: Hashes and technical metadata leave the Mac; audio bytes already traverse the relay. Do not retain waveform content beyond existing retention policy; bind acknowledgments to authenticated device IDs and artifact hashes.
- depends on: A shared audio artifact ID/hash propagated through POST /pipeline/audio and relay result; A future pendant registration and playback acknowledgment protocol (currently no pendant is online); Direction-specific fields in POST /pipeline/events and GET /pipeline/:pipelineId/audio/:direction

### `integration` — Create a signed, causally ordered event chain shared by relay, Mac bridge, browser extension, and pendant: every command, observation, handoff, upload, queue transition, and device receipt carries a device signature, monotonic counter, parent event ID, and capture time. On reconnect, the relay merges branches by causal order (not arrival time), marks conflicting or unverifiable branches, and exposes one immutable chain ID to jobs, audio artifacts, and action receipts. This is a protocol-level change, not another status page or browser watcher.
- **owner gets:** The owner can leave Wi‑Fi or the Mac, reconnect later, and still get a trustworthy answer about what happened in the right order—without a late browser result being mistaken for a fresh action or a relay upload being mistaken for playback. They can audit one chain rather than reconcile contradictory timestamps from four machines.
- effort: High: define event envelope and key provisioning, implement append-only relay storage and merge logic, add Mac/browser/pendant emitters, and migrate existing job/audio receipts. Begin with shadow emission and verification before making it authoritative.  ·  risk: Clock drift, lost counters, key rotation, or duplicate retransmission could create apparent forks. Never silently resolve a fork: preserve both branches, mark the chain uncertain, and fall back to the current conservative unknown state. Recover with idempotent event IDs and device re-pairing that records a new trust epoch.
- cost: Low ongoing API cost; roughly 200–500 bytes of metadata per event plus signature verification. Relay storage grows with event volume, so compact only after retaining signed checkpoints and an owner-visible audit export.  ·  latency: About 1–5 ms local signing and verification; reconnect reconciliation may add tens of milliseconds, not conversational latency. Offline operation is unaffected because events append locally and sync later.
- security: Improves tamper evidence but introduces device keys and key-rotation obligations. Private page contents and audio stay out of the envelope; use hashes and opaque references. A compromised device can still emit false events, so trust epochs and revocation must be visible and propagated before receipts are accepted.
- depends on: A common event envelope implemented across all four nodes; Per-device signing keys and authenticated pairing/revocation; Relay append-only event storage and a merge endpoint; Job, browser-command, pipeline-audio, and playback receipts carrying the chain ID


## What it asked for

_Nothing._
## Its own summary

Round 90 established fresh truth: no pendant is registered; Mac bridge and relay are reachable; browser extension is offline with 9 queued commands; Mac Accessibility/Screen Recording are false and UI inputReachability failed, making UI receipts untrustworthy. Pipeline history shows 24 kHz mono TTS output but a distinct LTE input record at 15,625 Hz, so end-to-end 24 kHz is not established. Recorded all four findings, notified judgement/action, and proposed a direction-aware audio contract verifier plus evidence-aware status reporting.

**Biggest unknown:** The authoritative relay-side device/delivery acknowledgment and future pendant playback receipt do not yet exist or have not been inventoried; without them, 'relay accepted' cannot be promoted to 'pendant played.'

