# Harness derivation — faculty-action — round 252

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""When I press the bookmark button, save what I was looking at—not just the time—and make it useful later.""
- **useful because:** A physical moment bookmark is currently only an event. The pendant is the only surface that knows exactly when the owner marked a moment, while the Mac/browser know the foreground app, URL, tab title, and available document context. Joining those into a privacy-bounded, searchable situated note turns an impulsive press into something the owner can actually retrieve and act on.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Cheap background model summarizes and labels the captured context; realtime is unnecessary unless the owner asks for the note immediately.
- **latency:** Haptic acknowledgement under 250 ms; enrichment within 5-15 seconds when Mac/browser are online, otherwise preserve the raw bookmark and enrich on reconnect.
- **cost:** Tiny for raw bookmarks; one small summarization call per enriched bookmark dominates, with no call for discarded/empty context.
- **security:** The pendant sends only bookmark ID/time and optional audio reference; Mac/browser evidence is minimized and encrypted. Never capture page text by default; require an explicit per-site or per-bookmark policy for snippets, redact passwords/tokens, and expose a delete operation.
- **missing:** A signed bookmark event envelope from firmware with monotonic ID and capture timestamp; A relay joiner that correlates the event to the nearest /observe and browser session snapshot without inventing the pendant timezone; A user-visible retention/deletion policy for enriched context

### ""Before we start talking, tell me if the pendant audio path is actually healthy, and degrade safely if it isn't.""
- **useful because:** The shipped 24 kHz path is excellent when healthy, but configuration labels cannot reveal a bad I2S clock, bridge dropout, packet starvation, or excessive loss. A quiet golden-fixture check across the Mac, ESP32 bridge, relay, and pendant can detect a real failure before the owner speaks, select a measured fallback, and report a concise haptic/audio status instead of making them debug silence.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Background/local diagnostics for preflight and periodic checks; realtime model is only told the compact health verdict, not raw waveforms.
- **latency:** 1-3 seconds for a preflight fixture; periodic checks run opportunistically and never open the microphone. Fallback selection must happen before the first spoken response.
- **cost:** Near-zero model cost; local DSP and packet counters dominate. Persist only compact measurements and a receipt, not audio.
- **security:** Use silence/sweep fixtures or an internally generated loopback, never the owner's microphone without explicit consent. Do not upload raw audio. A degraded mode must be announced and reversible; never silently lower quality for a long-lived session.
- **missing:** A real audio_path_probe implementation rather than its current low-confidence resolution to GET /observe; Bridge firmware telemetry for I2S rate, Opus frame timing, jitter, drops, and playback start; A relay policy that maps measured failures to 24 kHz/alternate-mode choices and emits the accepted tactile outcome beacon

### ""After you do it, show me exactly what was touched and what you deliberately did not read—without exposing the private contents.""
- **useful because:** A success/failure answer is not enough for sensitive work. The owner needs a compact, auditable boundary: which app, tab, file, and fields were touched; which were only checked; what was withheld; and whether any step was skipped. This makes the Mac/browser hands trustworthy without dumping secrets into the relay or pendant.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Cheap structured receipt generation from executor and verifier metadata; use realtime only to answer a follow-up question.
- **latency:** A compact receipt within 1 second after verification; detailed dashboard rendering can arrive asynchronously.
- **cost:** Negligible model cost; storage and cryptographic hashing dominate. No raw page or file content needs to leave the Mac.
- **security:** Default to hashes, type/locator, app origin, and byte counts—not values. Secret locators are redacted. The receipt itself is signed and append-only, with owner-controlled retention and deletion. Never claim 'not read' unless the executor can attest it did not fetch or transmit the field.
- **missing:** A typed per-step access ledger emitted by mac_run_actions/browser actions (read versus write versus merely focused); A signed receipt envelope linking operation ID, action ID, verifier provenance, and data-minimization attestations; A dashboard/pendant rendering that summarizes sensitive receipts without leaking their contents


## Changes it proposed to its own stack

### `hardware` — Add a discrete secure element with protected monotonic counters and signing keys to the pendant revision, and route the existing approval/outcome protocol through it. Pair it with a fuel-gauge IC on the battery rail so every signed event carries an honest power-health state and the device can refuse new high-risk transactions before brownout.
- **owner gets:** The owner gets confirmations that remain trustworthy even if pendant flash is reset or firmware storage is inspected, plus a pendant that says 'I cannot safely complete this' before dying mid-action instead of appearing to approve something and disappearing. Battery percentage and low-power behavior become dependable enough for an everyday jewellery device.
- effort: Medium hardware respin and firmware integration: I2C/SPI secure-element driver, key provisioning ceremony, monotonic-counter migration, fuel-gauge calibration, and relay verification changes. Existing approval-latch and outcome-beacon semantics remain the user-facing behavior.  ·  risk: Provisioning mistakes could permanently orphan a pendant; recovery requires a controlled factory re-enrollment path. Fuel-gauge calibration can initially be inaccurate across batteries. Roll out in shadow mode, compare gauge readings against measured voltage/current, and accept old unsigned events only during an explicit migration window.
- cost: Approximately $2–$6 added components and PCB/enclosure work per unit; secure-element and gauge consume negligible standby power compared with the radio and audio bridge. No per-invocation API cost.  ·  latency: Usually under 50 ms for signing and counter operations; low-battery checks are local and immediate. Initial secure-element enrollment adds a one-time setup step.
- security: Substantially improves resistance to replay, flash rollback, forged approval/outcome events, and counter reset. The private key never enters relay, Mac, browser, or model context. Battery telemetry should be treated as operational metadata, not a secret.
- depends on: The existing physical transaction approval latch and tactile outcome beacon must define the canonical envelope and migration rules; Relay and faculty-perception must verify secure-element signatures and monotonic counters; A safe owner-visible enrollment/replacement flow must exist before production use


## What it asked for

_Nothing._
