# Harness derivation — unified — round 97

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Save this for me.”"
- **useful because:** While the owner is away from the keyboard, a spoken request on the pendant should capture the thing they are looking at—not merely their words. The browser contributes the authenticated page title, URL, and a bounded cited excerpt; the Mac writes a durable note in ~/AI-Pendant-Workspace with the owner's spoken annotation; the relay queues it if either machine is offline; the pendant confirms exactly what was saved. This turns an ephemeral thought into a retrievable, sourced bookmark without requiring a screen interaction.
- **path:** pendant → relay → browser → mac-planner → dashboard
- **model tier:** Use deterministic routing for the exact intent and note creation; use the cheap background model only to normalize the spoken annotation and title. Escalate to planner only when the page has no usable semantic content or the owner asks for a summary.
- **latency:** Acknowledge on the pendant within 1 second with a queued/saved state; complete browser extraction and Mac note within 5 seconds when online. If offline, persist the intent and replay later with an explicit late-save receipt.
- **cost:** Usually zero model calls for metadata and a small background call for normalization (roughly 1–2k prompt tokens); storage and relay writes dominate negligible API cost.
- **security:** The browser may expose private page content, so extract only the active tab and a bounded excerpt, attach URL/time/source, and honor the owner's existing permission to read/click but never submit or mutate. Do not put secrets into spoken confirmation or the note unless the owner explicitly dictates them; queue contents need encryption and expiry.
- **missing:** A unified save-context command across pendant audio, browser active-tab inspection, and Mac workspace note creation; An offline intent spool with idempotency and replay receipts (pending skill request); A bounded authenticated browser extraction contract that returns citations and tab identity; A Mac workspace write primitive (pending mac_workspace_edit request)

### "“Ask me silently before you send it.”"
- **useful because:** For any irreversible Mac or authenticated-browser action, the owner would receive a short spoken description or dashboard card, then approve with a deliberate pendant hold and receive a private vibration confirming the exact action hash was accepted. They can cancel with a separate gesture; if the pendant is offline or the approval expires, nothing is sent. This gives the owner trustworthy control in public places without speaking a secret or hunting for the Mac.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic policy and action-hash matching do the gating. Use a cheap background model only to compress the action description; use realtime only if the owner asks follow-up questions while the approval is pending.
- **latency:** Show/announce the pending action within 2 seconds; local approval acknowledgement under 200 ms; execute within the existing job latency. Expire unanswered approvals after 60 seconds.
- **cost:** Near-zero additional API cost when action summaries already exist; at most 300–800 background-model tokens for a concise spoken summary. Hardware and integration dominate.
- **security:** Approval must be a cryptographic, single-use token bound to the exact action hash, target session/tab, owner session, and expiry. Never allow a generic button event, stale receipt, or relay retry to authorize a different action. Keep page contents out of the haptic protocol and require confirmation for mail, deletion, purchases, and submissions.
- **missing:** Production pendant haptic and multi-zone input hardware/firmware; A canonical cross-surface action hash and approval-token verifier; A pending-action presentation that works when the Mac has no Accessibility permission


## Changes it proposed to its own stack

### `integration` — Implement an end-to-end audio-path contract and self-test spanning nRF9160 firmware, ESP32 bridge, relay, and dashboard. On connection (and on explicit dashboard request), run a 2–3 second non-recording calibration: relay sends timestamped 24 kHz reference frames; the pendant/bridge measure sequence gaps, decode/encode CPU headroom, I2S underruns, resampler drift, Bluetooth queue depth, and LTE uplink/downlink contention; each hop returns a signed receipt with sample rate, frame duration, packet loss, concealment count, latency and clipping. Publish one pass/fail verdict plus the failing hop, and automatically select a safe profile (voice-only, reduced bitrate, or hold-to-retry) rather than silently delivering broken audio. Store only aggregate metrics, never the calibration waveform or spoken content.
- **owner gets:** The owner can trust that a new 24 kHz path actually works before wearing it, and gets a clear diagnosis when it does not. It prevents the current failure mode where duplex contention drops ~7.8 seconds of speech and where 24 kHz PCM is rendered but the physical chain is 31.25 kHz I2S then 44.1 kHz SBC.
- effort: Medium-high: firmware and ESP32 telemetry, relay receipt schema and orchestration, dashboard status view, plus hardware-in-loop and LTE fault tests.  ·  risk: A bad test could falsely declare failure or interrupt a live call; run only before a session or on explicit request, make it non-recording, and retain the last known-good profile for rollback. Clock and queue instrumentation must be bounded on the nRF9160's 211,608 B app RAM.
- cost: No per-call model cost; small relay storage for aggregate receipts. Engineering/test hardware time dominates.  ·  latency: Adds 2–3 seconds only when starting a session or explicitly testing; normal conversations are unchanged.
- security: Telemetry contains device/network performance only. Do not upload raw mic samples; authenticate receipts to prevent a spoofed healthy status.
- depends on: The pending 24 kHz audio architecture and end-to-end acceptance thresholds; A firmware/bridge telemetry packet and relay receipt schema; The already-requested audio fault-injection and preflight-receipt tools

### `hardware` — Replace the prototype's ESP32 classic-A2DP bridge with a low-power LE Audio companion (nRF5340 Audio DK-class design or production equivalent) connected to the pendant over the existing I2S/SPI boundary. Keep LTE-M on the nRF9160, but move the audio contract to native 24 kHz mono LC3/LC3plus-capable transport and report Bluetooth queue/clock telemetry back over SPI. The production board should expose a hardware clock/PLL arrangement that avoids the current 15,625 -> 24,000 -> 31,250 -> 44,100 chain.
- **owner gets:** A wearable call would sound consistent and remain intelligible under duplex traffic, without the current SBC-only 44.1 kHz bridge, tight 44 kB buffer, and multiple resampling stages. It also removes a separate bridge box the owner must carry or keep charged.
- effort: High: industrial design, RF coexistence, antenna and power work, LE Audio interoperability testing, and a migration path from the current dev-kit bridge.  ·  risk: New RF and battery failure modes, headphone compatibility gaps, and schedule risk. Ship with the existing bridge as a fallback during validation; retain the same I2S framing and telemetry contract so firmware can roll back.
- cost: Prototype companion BOM roughly tens of USD and modest additional idle/transmit power; likely lower total system power than keeping a separate ESP32 bridge, but requires measurement.  ·  latency: Should reduce buffering and resampling latency by one or more frames; LTE half-duplex contention remains and still needs the governor.
- security: Pairing keys and audio remain local to the companion; require authenticated pairing and erase keys on factory reset. No new cloud data.
- depends on: The end-to-end audio contract/self-test and telemetry schema; A measured 24 kHz acceptance target; Production pendant constraints beyond the nRF9160 DK

### `hardware` — Design the production pendant with a small haptic actuator and a two-zone capacitive touch surface (or a second sealed tactile control), alongside the existing button and LED. Expose distinct local events for confirm, cancel, and private acknowledgement; relay them as signed, single-use approval tokens bound to the exact Mac/browser action summary and expiry. Keep all sensing and the immediate tactile feedback local, with the server receiving only the resulting token/event.
- **owner gets:** The owner can approve or reject a sensitive action—sending a message, submitting a form, or accepting a browser transaction—without speaking private content aloud or reaching for a phone. A short vibration also tells them that a queued job, alert, or delayed audio response actually arrived when they cannot look at a screen.
- effort: High for a production enclosure/PCB revision and firmware input model; moderate relay and Mac/browser integration once the event contract exists. Requires accessibility-free action gating so it remains useful under the current TCC restriction.  ·  risk: False touches or accidental approvals could be dangerous. Require deliberate press-and-hold/chord timing, announce the pending action audibly or on the dashboard before arming, use a short expiry, and provide a physical cancel gesture. Fall back to the current button and dashboard if the sensor fails.
- cost: Roughly a few dollars of BOM plus PCB/enclosure and battery-impact validation; negligible model/API cost.  ·  latency: Local acknowledgement under 100 ms; no additional model round trip. Action execution still waits for the existing relay/Mac/browser job path.
- security: Improves privacy by keeping approval input local, but the approval token becomes security-sensitive: bind it cryptographically to action hash, user/session, nonce, and expiry; reject replay and never treat a generic vibration as authorization.
- depends on: A canonical action summary/hash shared by relay, Mac, and browser harnesses; The existing receipt/undo records and irreversible-action checkpoint path; A production pendant design beyond the nRF9160 DK with a validated sealed input and haptic driver


## What it asked for

_Nothing._
## Its own summary

Round 97 discovery: the Mac bridge is online, but the browser device is offline and no new grants are exposed this run. The physical audio chain remains the critical gap: 15.625 kHz capture, 24 kHz decode, 31.25 kHz I2S, 44.1 kHz SBC A2DP, with measured LTE duplex loss. I recorded three forward-looking items: an end-to-end non-recording audio self-test/receipt contract, a production LE Audio companion to remove the SBC/resampling bottleneck, and “Save this for me” (pendant + active authenticated browser tab + Mac workspace note + relay replay).

**Biggest unknown:** I still need the authoritative 24 kHz acceptance thresholds, production pendant constraints, queued-action/offline replay policy, and the Mac workspace-write plus browser extraction primitives. The owner timezone is also inconsistent: remembered profile says America/Chicago while the machine context previously reported America/New_York. Until those are resolved, scheduled briefs and audio-path pass/fail claims cannot be fully trusted.

