# Harness derivation — unified — round 192

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Finish checking out this order, but do not place it until I approve the exact store, items, total, address, and delivery time with one button press on the pendant.""
- **useful because:** It turns the browser's private authenticated session into a safe real-world hand: the Mac/browser can prepare the transaction, the relay can preserve the exact digest across a link drop, and the worn device supplies consent without sending page contents or secrets to the model.
- **path:** browser-extension → mac-planner → relay-realtime → dashboard-ux → pendant
- **model tier:** planner/background for cart interpretation; deterministic browser executor and digest verifier; realtime only for the spoken summary
- **latency:** Prepare in 5-10 s; spoken approval summary in under 2 s after preparation; submit within 3 s of a valid physical approval.
- **cost:** $0.02-$0.08 per preparation depending on planner calls; browser execution and digest verification dominate latency, not tokens.
- **security:** Never speak or persist card numbers/passwords. Bind approval to tab origin, cart/total/address digest, expiry, and current page world fingerprint; refuse if any changes. Require physical_transaction_approval_latch and make cancel equivalent to no submission.
- **missing:** production relay persistence and delivery for the staged approval handoff; browser-side final-review digest covering all merchant-visible fields; submit-only-after-verified-pendant-nonce executor path

### ""Read the important, non-sensitive numbers and labels on the page I'm looking at, and tell me what changed since the last time I asked—without reading passwords, messages, or unrelated tabs.""
- **useful because:** With Screen Recording and Accessibility now live for the AI Pendant Agent, the owner can use the pendant as a privacy-bounded visual query instead of handing over an entire screen or asking for a brittle full computer-use task. Change tracking makes repeated checks useful for checkout totals, travel status, and dashboards.
- **path:** pendant → mac-vision → browser-extension → relay-realtime
- **model tier:** realtime vision for the small requested region; deterministic redaction and diffing before model upload
- **latency:** Initial answer 2-4 s; subsequent same-tab change check under 1.5 s.
- **cost:** $0.01-$0.05 per visual query; screenshot upload and vision tokens dominate.
- **security:** Require explicit tab binding and a field allowlist; locally redact password inputs, payment fields, message bodies, and other tabs before upload. Store only hashes and selected labels, never screenshots by default; ask before reading a newly bound origin.
- **missing:** field-level screenshot redactor; tab-scoped visual snapshot/hash store; spoken command to bind and release a tab

### ""When the browser or Mac disappears while you are working, tell me exactly what was completed, what was not attempted, and let me resume only the safe parts from the pendant or dashboard.""
- **useful because:** A dropped Mac job currently leaves the owner guessing whether a browser action happened. This is an owner-facing recovery contract, not blind retry: it joins durable receipts, browser leases, and the pendant's physical approval state, then offers only idempotent or additive steps while blocking unrepeatable actions.
- **path:** relay-realtime → mac-planner → browser-extension → dashboard-ux → pendant
- **model tier:** deterministic ledger/receipt classification first; background model only to explain the state in plain language
- **latency:** Recovery status in under 2 s after reconnect; safe resume starts within 5 s of explicit owner request.
- **cost:** <$0.01 per recovery; mostly D1/local ledger reads, with an occasional low-cost explanation call.
- **security:** Never infer completion from a timeout. Require receipt or browser evidence, expire stale relay jobs, bind resume to plan digest and world fingerprint, and require the existing physical approval latch for any off-machine or irreversible remainder.
- **missing:** closeLedger integration for normal orchestrator runs; relay job lease expiry/requeue; single cross-surface recovery route joining local ledger, browser lease, relay receipt, and pendant approval; owner-facing resume controls

### ""Move this live conversation from the pendant to my Mac or phone without making me repeat myself, and move it back when I leave the desk.""
- **useful because:** Today the pendant, relay, Mac dashboard, and iOS surface are separate conversation endpoints. Losing LTE, putting the pendant down, or reaching for a larger screen forces a cold restart and loses the active turn, pending answer, and audio position. A negotiated handoff would make the system feel like one assistant with several bodies rather than several unrelated sessions.
- **path:** pendant → relay-realtime → mac-planner → dashboard-ux → iOS
- **model tier:** deterministic session coordinator for turn/audio ownership and sequence reconciliation; realtime model continues the conversation without summarization unless a gap must be repaired
- **latency:** Handoff offer within 500 ms; target surface audible/visible within 2 s; no duplicate response or more than one lost audio frame at the boundary.
- **cost:** Negligible relay cost for handoff metadata; at most one short realtime context repair call per failed boundary, under $0.02 typically.
- **security:** Authenticate each surface and bind ownership to the active session nonce. Only one endpoint may emit audio at a time. Require explicit owner confirmation for moving to a new surface, never expose pending private audio on an unlocked dashboard, and expire abandoned handoff offers.
- **missing:** cross-surface session ownership and handoff protocol; turn/audio sequence checkpoints shared by pendant, relay, Mac, and iOS; dashboard and pendant handoff affordances; duplicate-suppression and gap-repair logic


## Changes it proposed to its own stack

### `firmware` — Add a bridge-side audio continuity supervisor on the ESP32 that timestamps I2S input/output progress, detects A2DP disconnect, stalled SBC callbacks, and buffer starvation, then performs a bounded Bluetooth reconnect and emits one compact fault record. It must never grow the audio buffer or write audio to SD; after a deadline it hands a structured degraded/failed state to the existing audio delivery acknowledgement queue.
- **owner gets:** If headphones silently disconnect, the owner should hear a clear failure indication or recover automatically instead of continuing a conversation they cannot hear. The pendant/relay can then stop speaking or offer a safe alternate response rather than pretending delivery succeeded.
- effort: Medium: ESP32 watchdog/state machine, reconnect testing, and relay/dashboard rendering of the fault record.  ·  risk: A reconnect at the wrong time could cut a valid sentence or loop against Bluetooth firmware. Bound attempts, preserve sequence numbers, and fall back to an explicit error state; validate with the existing audio fixture and fault injection.
- cost: No API cost. Tens of KB of ESP32 RAM/code and negligible additional power except during reconnect; no routine SD writes.  ·  latency: Detect a stalled bridge in 200-500 ms; reconnect may take 1-5 s and should be announced as degraded rather than hidden.
- security: No new content leaves the device; records only opaque stream IDs, counters, and link state.
- depends on: audio_delivery_ack_queue (s9-vtxc); audio_path_diagnostic_fixture (s16-dbfs); duplex_audio_congestion_guard (s15-rzms)


## What it asked for

_Nothing._
