# Harness derivation — unified — round 32

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Changes it proposed to its own stack

### `hardware` — Replace the prototype’s single-button/LED-only interaction with a production pendant interaction module: a recessed, physically latched microphone/speaker privacy switch, a small vibration motor, and a fuel-gauge IC on the battery rail. Expose switch transitions and battery telemetry to firmware, relay, Mac, and browser as signed device-state events; keep the existing button for conversation start/end. The physical switch must cut the local playback amplifier and microphone power path, not merely set a software flag, while firmware reports the state when connectivity returns.
- **owner gets:** The owner can silence and privacy-lock the device instantly in a meeting or sensitive situation, feel confirmation without looking at an LED, and know whether a scheduled or browser-driven task will outlive the pendant’s battery. Today the one button, one LED, missing gauge, and network-dependent audio path cannot provide that confidence.
- effort: New pendant revision and enclosure; select a low-leakage latching switch, haptic motor/driver, and fuel gauge; update power tree, PCB, DFU image, device-state protocol, relay state projection, Mac menubar status, and dashboard. Add hardware-in-loop tests for switch bounce, brownout, reconnect replay, and amplifier/mic isolation.  ·  risk: A physical cutoff can terminate a conversation mid-utterance and may make the owner think the agent is unavailable; provide distinct haptic patterns and a dashboard/banner state, and make reconnect state reconciliation idempotent. PCB/enclosure redesign and battery-path changes require safety/regulatory review. Recovery is a software bypass only for diagnostics, never for the user privacy switch.
- cost: Prototype BOM roughly $8–$20 incremental (switch $1–$3, haptics/driver $1–$3, gauge $1–$4, power/PCB/enclosure changes $5–$10); haptics add brief 10–30 mA pulses and the gauge draws tens of microamps, while the physical cutoff reduces idle drain. No meaningful API-token cost.  ·  latency: Local privacy mute is effectively immediate (< one audio frame); telemetry reaches the relay/Mac on the next available uplink and is replayed after reconnect. Battery queries become local/near-real-time instead of depending on a nonexistent gauge.
- security: Improves privacy because the cutoff is physical and locally enforceable. Device-state events must be authenticated and monotonic to prevent a stale or forged reconnect from falsely reporting unmuted; do not upload microphone data while the switch is latched.
- depends on: Production pendant hardware definition beyond the nRF9160 DK; Firmware device-state event schema and reconnect replay; Relay/Mac/dashboard rendering of signed privacy and battery state; Audio power-domain design and validation

### `integration` — Add a device-privacy lease spanning pendant, relay, Mac, and browser: the pendant’s physical privacy state becomes a signed, short-lived lease with monotonic sequence and explicit expiry/reconciliation. While latched, relay refuses audio ingest/playback and suppresses proactive spoken notifications; the Mac agent pauses screen capture/computer-use and clipboard export; the browser bridge pauses page extraction and queued mutations. The dashboard shows the lease and every paused job, then resumes only after a fresh physical unmute plus explicit per-job reconciliation. Record a local and server receipt for each transition without recording content.
- **owner gets:** One physical action would make the whole personal AI private, rather than muting only the speaker while a browser tab, screen capture, or queued Mac action continues. Today the owner cannot confidently walk into a meeting and know every surface has stopped observing or acting.
- effort: Define an authenticated device-state envelope and lease coordinator in the relay; add pause/resume hooks to the Mac planner/computer-use loop and browser bridge; add queue semantics, dashboard state, and reconnect/replay tests. Requires integration with the proposed physical switch and existing action/job records.  ·  risk: A lost or stale unmute could leave useful work paused, while an incorrect resume could violate privacy. Default-deny on uncertainty, show the reason and affected jobs, expire leases conservatively, and require fresh device-originated unmute; queued irreversible actions remain paused until separately revalidated.
- cost: Low recurring API cost (small state events and D1 records); engineering cost is moderate across relay, Mac, browser, and dashboard. No continuous polling: lease updates are event-driven.  ·  latency: Privacy stop is local and immediate; relay/Mac/browser pause propagation should target <500 ms online. Reconnect reconciliation may take one LTE round trip and must never unblock work optimistically.
- security: Strongly improves privacy by making the hardware state authoritative and fail-closed. Use device-bound keys, monotonic counters, replay protection, and do not expose secret content in receipts; treat the lease as a policy gate before any capture or action.
- depends on: Production pendant privacy switch, haptic feedback, and fuel gauge; Authenticated device-state protocol and key provisioning; Mac computer-use pause/resume hooks; Browser bridge pause/resume hooks; Relay job queue and action receipt integration


## What it asked for

### `s6-89q6` (skill) — local_output_mute_latch
- does: A long press (about 700 ms) immediately mutes pendant playback locally, regardless of modem or relay state; LED gives a short confirmation. A second long press resumes playback. It emits best-effort mute_state events when connected so the relay and Mac/browser agents know not to enqueue spoken output until resumed. On reboot it comes up unmuted.
- must be on-device because: The user needs silence within one audio frame even when LTE-M is congested, the WebSocket is wedged, or the relay is unreachable. Waiting for a server command cannot reliably stop already-buffered audio and is unsafe in a meeting or noisy environment.
- trigger: Long press of the existing sw0 button; firmware gesture recognition must coexist with the current short-press start/end conversation behavior.
- storage: One byte mute state plus CRC in a tiny settings record (or RAM only if persistence is rejected); no audio or transcript storage.
- RAM budget: ~2 kB code/data including debounce/gesture state and one control message; no buffers beyond the existing playback path, comfortably within 211,608 B application RAM.

## Its own summary

Discovered the live fleet: only the Mac bridge is online; the pendant remains a prototype nRF9160 with one button/LED, a single shared full-duplex I2S path, ~87% core audio load, and LTE-M half-duplex contention. The owner’s active goal is still end-to-end 24 kHz superwideband audio. I queued a genuinely new device-local skill, local_output_mute_latch: long-press immediately silences playback offline and synchronizes mute state when connected, without storing audio. I still need the pending 24 kHz acceptance criteria/target architecture, production pendant constraints, audio fault-injection/validation access, and workspace-edit permission/tooling to implement and verify the path; the orchestrator has not exposed any new grants this round.

**Biggest unknown:** Whether the product should preserve the current single-button short-press semantics exactly, and what long-press duration/LED pattern the owner will accept for the new emergency mute gesture.

