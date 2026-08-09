# Harness derivation — mac-planner — round 221

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/browser readiness Round 221** — Mac bridge and browser extension are online; Accessibility and Screen Recording are granted; pending browser commands are 0; Safari has two tabs with DoorDash active. Relay is reachable, but the pendant remains absent from relay registry.
  - evidence: GET /ops/snapshot HTTP 200 at 2026-08-08T22:17Z and GET /browser/status HTTP 200

## Capabilities it proposed

### "“When I leave a calendar meeting, make me a private handoff: what I was looking at, the meeting’s agenda, and a short list of unfinished next steps—without sending anything.”"
- **useful because:** The hardest part of a meeting is reconstructing the exact work context afterward. This joins the wearable’s moment marker, Calendar/Mail facts, the authenticated browser tab, and the Mac’s active work into one resumable artifact while keeping it private and unsent.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background model for extraction and ranking; realtime only if the owner asks for the handoff verbally.
- **latency:** Capture in under 5 seconds at meeting end; generate the handoff within 30 seconds. If a source is unavailable, produce a partial artifact and say which source was missing.
- **cost:** About $0.01–$0.04 per handoff; source reads and local file creation dominate latency, not model tokens.
- **security:** Calendar and authenticated-page content leave the Mac only as minimized snippets. Never include passwords, form values, page HTML, or message bodies by default. Create a local Markdown/JSON artifact, do not send or modify external systems. Require the owner’s configured policy entry for reading browser content and writing the artifact.
- **missing:** A reliable pendant-to-Mac meeting-end marker association (the existing moment bookmark is the event, but not meeting identity).; A semantic active-document/selected-text read that returns bounded, redacted evidence rather than a generic screenshot.; A server-side handoff assembler that joins browser evidence, mac_read_sources output, and a workbench receipt idempotently.

### "“For the last thing you did for me, show me exactly which browser facts, Mac files, and actions you relied on—and what was only an inference.”"
- **useful because:** Cross-node automation is currently hard to trust after the fact: a browser result, Mac receipt, and spoken answer are separate streams. A provenance view lets the owner audit a result without replaying the task, especially when an authenticated page or an irreversible desktop action was involved.
- **path:** relay → mac-bridge → browser → dashboard → pendant
- **model tier:** Cheap background model to normalize and redact evidence; realtime model only summarizes the already-built provenance graph when asked.
- **latency:** Append provenance during execution with no more than 100 ms overhead per step; answer an audit query in under 3 seconds from stored receipts.
- **cost:** Less than $0.01 per task for local hashing/metadata; $0.01–$0.03 for an optional natural-language audit summary.
- **security:** Store hashes, timestamps, resource identifiers, and redacted excerpts by default—not raw page bodies, passwords, or microphone audio. Keep sensitive evidence local and expire it. The owner must configure which domains/apps may retain excerpts. Audit output must label observed facts versus model inferences and must not silently reconstruct missing evidence.
- **missing:** A shared execution_id propagated through relay plans, browser command/result records, Mac jobs, and spoken responses.; A receipt schema with input hashes, output hashes, action type, touched resource, reversibility, and redaction status; current receipts are not sufficiently joinable.; A read-only provenance endpoint and dashboard timeline with retention controls.

### "“Use my logged-in browser to answer this, but prove that no passwords, payment details, or unrelated private tabs were sent off the Mac.”"
- **useful because:** The browser is the only node that can reach authenticated sessions, which is also the largest privacy boundary. A local evidence firewall would let the owner use those sessions while making the relay receive only a narrow, inspectable answer capsule instead of raw page state.
- **path:** browser → mac-bridge → relay → dashboard → pendant
- **model tier:** Deterministic local classifier/redactor first; a cheap background model may summarize only the already-redacted capsule. Realtime is unnecessary.
- **latency:** Classify and redact each browser result in under 150 ms; return a normal question answer within 5 seconds.
- **cost:** Near-zero API cost for local DOM/field classification; up to $0.01 per short redacted summary.
- **security:** Treat password inputs, payment fields, cookies, tokens, hidden inputs, unrelated tabs, and free-form personal text as deny-by-default. Keep raw DOM on the Mac and erase it after the result receipt expires. Show the owner a compact disclosure card (domain, fields/classes shared, hashes, timestamp) before or alongside the pendant answer. This is a privacy boundary, not a promise that browser automation itself is safe.
- **missing:** A browser-extension result interceptor that performs local field-level redaction before POST /browser/result/:commandId.; A capability manifest for browser evidence classes (title, URL, visible text, table rows, selected region) with per-domain policy.; A relay contract that rejects un attested/raw browser payloads and carries the disclosure receipt to the dashboard.

### "“Start this browser/Mac job, but make it automatically stop if my pendant disconnects or I press the stop button—and tell me exactly what was completed before it stopped.”"
- **useful because:** Today a queued desktop or authenticated-browser plan can outlive the conversation that created it. The owner needs a bounded execution lease, not an approval gate: loss of the wearable link or an explicit stop should halt future steps across every node and return a durable partial-completion report.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** No expensive model is needed for enforcement; use a deterministic relay lease coordinator. Use a cheap model only to turn the partial receipt into a spoken summary.
- **latency:** Propagate stop within 500 ms while connected; on a hard link loss, Mac and browser leases expire within 2 seconds. Produce a completion receipt within 5 seconds.
- **cost:** Negligible model cost; roughly $0.001 or less per lease for state and receipt operations. The dominant cost is implementation and reliable testing under disconnects.
- **security:** This is a cancellation boundary, not a permission system. The lease token must be unguessable, scoped to one job, single-use on revoke, and rejected by both Mac and browser workers after expiry. Cancellation must be idempotent and must never claim rollback where an external action already happened. Persist only action metadata and redacted results; never treat a lost connection as evidence that a transaction was undone.
- **missing:** A relay-issued lease token and heartbeat protocol shared by pendant, Mac job executor, and browser command queue.; Mac and browser executors must check lease validity before every action, not only at job start.; A partial receipt schema that distinguishes completed, in-flight/unknown, skipped, and cancelled steps, with the existing job and browser command IDs joined.

### "“I’m about to lose service. Make me an offline packet of the next trip’s itinerary, addresses, tickets, and emergency contacts, then let the pendant read it without the network.”"
- **useful because:** The relay and authenticated browser are strongest while connected, while the worn device is most useful after connectivity disappears. Today there is no coordinated ‘prepare then carry’ handoff: the owner cannot safely turn Calendar/Mail/browser facts into an expiring, wearable-readable packet before entering a dead zone.
- **path:** browser → mac-bridge → relay → pendant → dashboard
- **model tier:** Cheap background extraction and deterministic field selection; realtime only to answer a follow-up before disconnect. No cloud model should see raw ticket/payment credentials.
- **latency:** Build in under 20 seconds for a normal itinerary; transfer and verify before the owner leaves coverage. Pendant lookup should be local and immediate.
- **cost:** $0.01–$0.03 per packet for extraction; local encryption and transfer dominate reliability, not inference.
- **security:** Encrypt the packet end-to-end for the pendant, include only explicitly selected travel fields, omit payment/card numbers and login tokens, and auto-expire after the trip or a configured TTL. The dashboard should show exactly which sources and fields were copied. A failed transfer must leave the source untouched and expose a clear incomplete state.
- **missing:** A relay-to-pendant durable packet format distinct from ordinary alert text, with authenticated encryption and a size limit appropriate to the existing microSD store.; A browser export operation that returns bounded ticket/address fields rather than raw authenticated-page content.; A preflight/verification step that confirms the pendant has the complete packet before the Mac or relay considers it offline-ready.

### "“Only let this one authenticated-browser task run while I’m physically holding my pendant; show me the exact domain and action bound to that hold.”"
- **useful because:** A logged-in browser session can perform actions that the relay cannot safely infer from a voice request alone. A short-lived, hardware-originated presence proof would bind one plan to the owner’s physical pendant without exposing credentials or requiring the owner to operate the Mac.
- **path:** pendant → relay → browser → mac-bridge → dashboard
- **model tier:** Deterministic cryptographic verification and policy matching; no model call is required except an optional spoken explanation.
- **latency:** Issue the single-task capability in under 1 second after the button event; reject stale or replayed proofs immediately.
- **cost:** Negligible API/model cost; modest firmware and browser-extension engineering cost.
- **security:** The proof must be nonce-bound, single-use, short-lived, and scoped to an origin plus an action digest—not a general browser unlock. Never transmit credentials or raw button history. The dashboard must display the domain, action class, and expiry before execution. This is optional owner-configured policy, not a hidden confirmation gate, and it cannot prove the owner’s intent beyond physical possession.
- **missing:** A secure challenge-response primitive on the pendant with protected key storage; the current prototype has buttons but no product-grade secure element.; Relay/browser support for an action digest and one-use capability token checked before each external mutation.; A browser disclosure card and policy setting that defines which domains/actions may require physical presence.


## Changes it proposed to its own stack

### `hardware` — On the product pendant (not the current nRF9160 DK), add a normally-open physical microphone power/analog cutoff switch with a visible mechanical position, wired ahead of the I2S mic path and sampled by a GPIO. Keep the existing local_privacy_latch as the software state, but make the switch electrically authoritative: when open, mic bias/capture is impossible even if firmware or relay misbehaves. Report only switch state, never audio, to the relay.
- **owner gets:** The owner gets a privacy guarantee they can verify by touch and sight, including when the Mac, relay, or firmware is compromised or offline. The current board has one full-duplex I2S path, one button, and one LED but no mic-disable switch; a software latch alone cannot provide the same assurance.
- effort: High: product-board redesign, low-leakage analog switch or mic-bias disconnect, GPIO debounce, enclosure cutout, EMC/audio validation, and firmware integration. Prototype with an I2C/GPIO-controlled analog switch on the currently free I2C/SPI headers before PCB layout.  ·  risk: A poor switch can add mic noise, pop/clicks, leakage, or prevent capture after reboot. Default electrically muted on uncertain GPIO state; test switch continuity and mute/unmute pop on the full-duplex I2S path. Recovery is manual switch reset plus firmware state reconciliation.
- cost: Roughly $1–$4 BOM plus enclosure/PCB cost; negligible steady-state power, with a few µA leakage target. Prototype wiring may cost more than the final part.  ·  latency: No network latency. Add under 10 ms debounce before reporting state; audio remains muted until the physical state is valid.
- security: Strongly improves defense against unintended recording. The switch state is low-sensitivity telemetry; microphone content must remain unavailable while open. It does not replace the existing persistent local privacy latch.
- depends on: A product pendant revision rather than the current development kit; A defined microphone power/bias schematic and GPIO-safe default; Firmware amendment to local_privacy_latch to reconcile physical mute state


## What it asked for

_Nothing._
## Its own summary

Discovered live readiness: Mac bridge, Safari extension, Accessibility, Screen Recording, and relay are all online; there are zero pending browser commands. The pendant is still not registered with relay. I proposed three cross-node owner capabilities: post-meeting private handoff, auditable fact/action provenance, and a browser evidence firewall; plus a hardware change for an electrically authoritative microphone cutoff. The recorder flagged the latter as close to an earlier hardware idea, so I will not rephrase it next round.

**Biggest unknown:** The key missing contract is not Mac access: it is whether the relay/browser stack can carry a stable execution ID and redacted evidence capsule end-to-end. I still need an inventory of the actual workbench/context and browser-result schemas (including retention/redaction fields), and a verified pendant pairing/registry status before claiming any wearable-triggered handoff can run live.

