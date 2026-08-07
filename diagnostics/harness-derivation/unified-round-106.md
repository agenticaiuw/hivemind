# Harness derivation — unified — round 106

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-and-audio-readiness** — The live Mac bridge is online, but the browser extension is offline with 10 pending commands. The pendant prototype captures at 15,625 Hz, uploads Opus 16 kHz/16 kbps, decodes 24 kHz, and the ESP32 bridge is SBC-only 44.1 kHz stereo. The measured LTE-M path is half-duplex and has recently lost 388 uplink packets (~7.8 s) during overlapping speech.
  - evidence: GET /browser/status; get_hardware_spec pendant/audio/network/bridge; GET /pipeline

## Capabilities it proposed

### "“If I ask you from the pendant to handle something on a private website, keep the task safe across dropouts: tell me immediately what can and cannot be done, continue when the browser reconnects, and give me one final spoken receipt with exactly what changed—or confirm that nothing was submitted.”"
- **useful because:** Today the Mac bridge is online but the browser is offline with 10 pending commands. The owner can issue a request while mobile, walk away, and later receive either a trustworthy completion or an explicit non-action; private tabs, the always-awake relay, Mac, and pendant work as one system rather than silently losing or duplicating a task.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only for the short initial status and final spoken receipt; a cheaper background planner handles retries, evidence reconciliation, and summarization.
- **latency:** Initial acknowledgement under 2 seconds; reconnect recovery within one browser heartbeat; final receipt within 5 seconds after the browser reports a terminal state.
- **cost:** About $0.01–$0.05 per task depending on whether background reconciliation needs a model; relay storage and browser polling dominate, not realtime inference.
- **security:** Private URLs and extracted fields stay in the authenticated browser session and relay's encrypted job record. Never retry a send, purchase, delete, or submit without an idempotency key plus explicit owner approval; spoken receipts must avoid secrets.
- **missing:** A cross-surface task state machine with lease, expiry, and resumable checkpoints; Browser heartbeat/reconnect handling and a policy for the existing stale pending queue; One canonical action receipt consumable by relay, dashboard, and pendant audio; Owner-configurable quiet hours and a terminal-state notification route

### "“For the next 30 minutes, let you handle routine parts of this task across my pendant, Mac, and logged-in browser, but stop before anything consequential; tell me exactly what authority is active and revoke it when I press the button.”"
- **useful because:** Today permissions are fragmented by surface and action. The owner cannot safely grant a bounded burst of autonomy that follows one task from spoken pendant request to Mac and private browser work. A short-lived, visible delegation scope would make the hive useful while preventing forgotten standing authority.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime handles the spoken scope summary and revocation acknowledgement; a cheaper policy engine evaluates every action against the signed, expiring scope.
- **latency:** Scope confirmation and revocation under 1 second locally; authorization decision under 100 ms per action; no model call required for ordinary policy checks.
- **cost:** Negligible model cost after initial setup; mostly durable policy storage and signing. Occasional realtime acknowledgement costs under $0.01.
- **security:** Use a cryptographically signed, task-bound capability token containing allowed surfaces, action classes, expiry, and confirmation requirements. Never include passwords or raw page contents. Consequential actions—send, purchase, delete, publish, or permission changes—remain blocked regardless of the token. Button revocation must work offline and propagate on reconnect.
- **missing:** A shared capability-token format understood by relay, Mac, and browser; A pendant-local revocation latch and LED/audio indication of active scope; A policy enforcement point before every Mac and browser action; An append-only, owner-readable delegation audit trail; Key rotation and recovery when a surface is offline


## Changes it proposed to its own stack

### `hardware` — Replace the prototype HUZZAH32 A2DP/SBC bridge with a production Bluetooth LE Audio companion (LC3, mono 24 kHz) and give the pendant a purpose-built audio/modem SoC or companion link with separate audio scheduling. Keep the relay's 24 kHz PCM contract, but remove the mandatory 31,250→44,100 resample and SBC stereo buffering. Add a small hardware audio FIFO and modem/audio clock domains with underrun telemetry.
- **owner gets:** The owner gets intelligible, lower-latency 24 kHz speech without the current bridge's silent-failure mode: the nRF9160 is already spending roughly 87% of its core on encode/decode, and LTE-M contention recently lost about 7.8 seconds of uplink. A real wearable should continue speaking cleanly when the owner talks over a response, rather than clipping or going silent.
- effort: High: select and prototype a LE Audio-capable companion, redesign the PCB and power budget, implement LC3/I2S firmware, and run RF, coexistence, and end-to-end audio acceptance tests. The existing nRF9160 DK remains the compatibility fixture during migration.  ·  risk: New radio/audio firmware can introduce pairing regressions, clock drift, or higher idle power. Recover with a dual-mode prototype (retain current SBC bridge as fallback), explicit codec negotiation, watchdog-resettable audio FIFOs, and packet-loss/underrun receipts.
- cost: Roughly $8–$25 added prototype BOM for a capable companion, plus PCB/antenna work; likely 30–80 mA active draw depending on codec/radio. API cost unchanged; fewer retransmits may reduce relay bandwidth.  ·  latency: Potentially 20–60 ms lower local output latency and less jitter; LTE-M half-duplex contention remains, so this does not replace a link-aware governor.
- security: Adds a Bluetooth attack surface. Use LE Secure Connections, bonded-device allowlisting, encrypted audio, and eraseable pairing keys; never expose raw audio over an unauthenticated debug characteristic.
- depends on: 24 kHz end-to-end audio acceptance criteria; link-aware duplex audio governor; production pendant constraints beyond the current nRF9160 DK; audio-path preflight and fault-injection tests

### `hardware` — Add a secure element with monotonic counters and a tamper-evident button event path to the production pendant. The secure element should mint and revoke short-lived delegation tokens after a deliberate press, sign local revocations while offline, and retain only token hashes/counters—not spoken content or secrets. Relay, Mac, and browser verify the signature before accepting an action.
- **owner gets:** The owner gets a physical, trustworthy way to say “you may do this for a little while” and “stop now,” even when the browser or relay is temporarily unreachable. A compromised or stale software surface cannot silently keep acting under yesterday’s permission.
- effort: Medium-high hardware and firmware change: select an I2C/SPI secure element, add board space and power analysis, implement provisioning, signed token/revocation formats, and test offline/reconnect races across all surfaces.  ·  risk: Lost or replaced hardware could strand authorization, and provisioning mistakes could lock out the owner. Provide recovery through a deliberate Mac ceremony, dual-key rotation, a visible reset procedure, and fail-closed behavior for consequential actions.
- cost: Approximately $1–$4 BOM increase and a few milliamps only during signing; negligible API cost. Engineering and manufacturing provisioning are the dominant costs.  ·  latency: Local press acknowledgement under 200 ms; cryptographic verification adds milliseconds to each action, below user-visible latency.
- security: Improves authorization integrity and offline revocation, but introduces key lifecycle and supply-chain risk. Keys must be non-exportable, debug interfaces disabled in production, and token scopes minimized.
- depends on: A shared capability-token format across relay, Mac, and browser; Pendant-local revocation semantics; Owner recovery and key-rotation procedure


## What it asked for

_Nothing._
