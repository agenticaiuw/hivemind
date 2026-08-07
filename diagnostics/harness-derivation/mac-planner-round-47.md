# Harness derivation — mac-planner — round 47

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I tell you to do something later, queue it safely: when my Mac or logged-in browser comes back, re-check that the request is still relevant, do it if the preconditions hold, and tell me on the pendant exactly what happened. If it has gone stale or would send/delete/buy, stop and ask me."
- **useful because:** The pendant can capture intent while walking or offline, the relay can hold it, and the Mac/browser can finish it later. Today pending browser commands and offline-held pendant events have no unified, freshness-aware handoff; this would turn intermittent connectivity into a dependable assistant without silently executing stale or high-impact work.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** gpt-5.6-luna for decomposition and stale-intent adjudication; gpt-4.1-mini for local UI perception; gpt-realtime-2.1 only for the immediate spoken capture/receipt; background replay and checks use a cheaper scheduled model.
- **latency:** Capture acknowledgement under 1 s offline; replay starts within 30 s of Mac/browser reconnection; simple checks under 5 s; stale or high-impact cases wait for explicit pendant confirmation.
- **cost:** About $0.01–$0.08 per queued request depending on browser extraction and replanning; realtime audio and authenticated-page context dominate.
- **security:** Intent, page excerpts, and action receipts leave the Mac only when needed and should expire by default. Never persist secrets in the relay. Re-check tab/session identity and preconditions; sending mail, deleting, purchasing, or submitting forms must remain pending until spoken confirmation.
- **missing:** A durable intent record with expiry, idempotency key, precondition snapshot, and retry state spanning pendant offline store, relay D1, Mac jobs, and browser sessions; A reconnect trigger and lease protocol so only one node replays an intent; A typed stale/precondition result and spoken/dashboard receipt for attempted_unverified versus completed; Owner-configurable expiry and quiet hours

### "Hand this conversation from my pendant to my Mac without making me repeat myself. When I tap twice, preserve the last few spoken turns and the relevant browser/app context, open a private continuation on the Mac, and let me continue there; when I leave, let me hand it back to the pendant as a short spoken summary."
- **useful because:** Today the pendant, relay, browser, and Mac are separate interaction episodes. The owner must repeat context or expose it by copying and pasting. A deliberate handoff would make the hive feel like one assistant while keeping the owner in control of when private context moves between surfaces.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** gpt-realtime-2.1 for the immediate handoff acknowledgement and short spoken summary; a cheaper background model compacts the recent transcript and selects relevant context; gpt-5.6-luna handles Mac/browser continuation planning.
- **latency:** Acknowledge the handoff in under 1 second; create the Mac continuation within 3 seconds when online; return a spoken summary within 2 seconds when handing back.
- **cost:** Roughly $0.005–$0.03 per handoff; transcript compaction and optional page-context extraction dominate.
- **security:** Handoff must be an explicit button gesture, never inferred from proximity. Encrypt the capsule in transit, minimize it to selected turns and cited context, expire it after completion, redact secrets and unrelated tabs, and show the destination surface before transferring private browser content.
- **missing:** A first-class handoff capsule format containing transcript turns, selected context references, sensitivity labels, and expiry; Pendant double-tap event and confirmation feedback tied to handoff creation; Relay endpoint for encrypted capsule transfer and single-use consumption; Mac continuation UI that opens the correct app/browser tab without leaking the capsule into logs; A return-handoff mechanism that summarizes the Mac session for spoken playback


## Changes it proposed to its own stack

### `hardware` — Replace the prototype 15,625 Hz microphone path with a production digital microphone/codec and clocking that supports 24 kHz (or 32 kHz) capture, then carry an explicit audio-profile envelope through pendant firmware, Opus encode, relay transcoding, Mac TTS, and ESP32 playback. Negotiate profile per link and fall back to the current narrow capture mode when CPU, radio, or battery is constrained.
- **owner gets:** The owner gets genuinely wider, clearer voice capture instead of 24 kHz playback fed by a 15.625 kHz microphone. Speech is easier to understand in noisy places and the system can honestly report which end-to-end profile was used.
- effort: New microphone/codec and PCB revision, firmware DMA/Opus profile work, relay format negotiation, Mac bridge tests, and acoustic/battery validation; substantial hardware + firmware effort.  ·  risk: Higher sample-rate CPU, radio bandwidth, heat, and battery draw; clock or resampler bugs can cause dropouts. Recover with negotiated 16 kHz capture fallback, profile telemetry, and A/B soak tests before rollout.
- cost: Prototype hardware roughly $8–$25 BOM increase plus PCB/enclosure work; power likely +20–60 mW during capture. API cost is negligible, though larger audio uploads increase bandwidth cost.  ·  latency: Potentially +5–20 ms encoding/upload time and larger packets; negotiated low-rate mode preserves today's latency.
- security: Raw audio remains transient and follows existing retention rules; profile metadata should exclude content and avoid adding new identifiers.
- depends on: An end-to-end audio-profile negotiation contract between pendant, relay, Mac bridge, and ESP32; Per-job audio quality/format receipt and automated sample-rate integrity tests; A battery and thermal budget for sustained 24 kHz capture

### `mac-harness` — Implement the granted mac_readonly_inspect operations instead of leaving them as schema-only stubs. Add a read-only broker for running apps, foreground app, accessibility/input reachability, UI snapshot, browser tabs, and approved directory listings; return typed timestamps, capability errors, and a stable observation ID without invoking the action executor or arbitrary shell.
- **owner gets:** Before the pendant says a Mac action worked, it can verify whether the right app, browser tab, and input permissions actually exist. The owner gets honest status and fewer false-success receipts, especially while the current agent reports Accessibility=false and the browser extension is offline.
- effort: Medium: wire the existing /observe and browser-session data into the tool adapter, implement directory listing through the local agent's read-only path, add schema tests and stale-observation handling.  ·  risk: A snapshot can become stale or expose more app/tab metadata than intended. Minimize by timestamps, redaction defaults, bounded results, and never treating an observation as proof of a later mutation.
- cost: Negligible API cost; modest local CPU and implementation work.  ·  latency: Usually under 200 ms from cached state; UI snapshots may take longer and should be opt-in.
- security: Read-only but privacy-sensitive: redact URLs, mail, and paths by default, enforce approved roots, and never return page bodies unless explicitly requested.
- depends on: A real implementation behind the granted mac_readonly_inspect tool; Stable observation IDs consumed by action receipts and deferred-intent precondition checks; Browser reconnect/status events from the extension

### `interaction` — Add a deliberate cross-device handoff protocol: a double-press on the pendant freezes a short, sensitivity-labeled conversation capsule; the pendant gives a distinct LED/audio acknowledgement, the relay transfers it once to the Mac, and the Mac opens a continuation view with cited app/browser context. A second deliberate gesture returns only a compact summary to the pendant.
- **owner gets:** The owner can move from walking to desk work—or back again—without repeating themselves, while an unmistakable physical gesture prevents accidental transfer of private conversations.
- effort: Medium-to-large protocol and UX work across pendant firmware, relay storage, Mac continuation UI, browser context capture, and dashboard history; requires end-to-end tests for offline and reconnect cases.  ·  risk: Accidental disclosure or duplicate handoffs. Recover with explicit gesture confirmation, single-use capsules, expiry, sensitivity redaction, visible destination, and a cancel gesture before transfer.
- cost: Negligible per-use API cost; modest firmware, relay, and Mac UI engineering cost. One LED and the existing button can provide the basic feedback.  ·  latency: Sub-second local acknowledgement; 1–3 seconds for online transfer and Mac continuation.
- security: Private context crosses devices only after a physical gesture, with encryption, short retention, per-capsule access control, and no raw transcript in ordinary logs.
- depends on: The handoff capsule and relay transfer endpoint; A pendant gesture/event contract with acknowledgement patterns; Mac/browser context capture and continuation UI; Sensitivity-aware transcript compaction


## What it asked for

_Nothing._
