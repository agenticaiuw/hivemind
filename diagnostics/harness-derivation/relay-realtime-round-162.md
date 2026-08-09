# Harness derivation — relay-realtime — round 162

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "After this finishes, let me know how it went, even if I’m not still talking to you."
- **useful because:** This is the single most useful thing: long-running Mac tasks need feedback. Without it, the owner must remember to ask later, and the system feels unreliable.
- **path:** relay → mac-bridge → pendant
- **model tier:** Cheap background model for monitoring; realtime only to speak the alert when it’s delivered.
- **latency:** Monitoring can be seconds to minutes; delivery should be near-instant when the device is reachable.
- **cost:** Low per job; dominant cost is job polling or subscription and occasional audio delivery.
- **security:** Avoid leaking task details; keep spoken text short. Only send to a paired device. Respect storage rules: do not store audio routinely on the pendant.
- **missing:** A real relay event delivery mechanism (relay_event_push is currently an unresolved schema).; A subscription or polling bridge from relay to device/phone that can queue alerts when offline.; A durable notification queue tied to job completion if the device is offline (can reuse inbox concepts but must fit storage rules).

### "When I ask 'what am I looking at?', use the Mac's current screen (or the authenticated browser tab I have open), understand the image and relevant text, and answer me through the pendant; if I say 'change that to...', make the smallest corresponding edit and tell me exactly what changed."
- **useful because:** The pendant currently has ears but no eyes. This would make a spoken request useful for charts, error dialogs, dense web pages, and visual UI state without requiring the owner to describe what is in front of them. It combines the wearable's immediate intent, the Mac's screen reach, and the browser's authenticated session in a way no one node can provide alone.
- **path:** pendant → relay → mac-vision → browser-extension → mac-planner
- **model tier:** Realtime relay for the short spoken exchange; gpt-4.1-mini vision for screenshot/OCR grounding; mac-planner only for an edit that needs multiple actions. Do not send the screenshot to a general model when local vision can answer it.
- **latency:** Under 2 seconds for a read-only answer after the screenshot arrives; under 6 seconds for a narrowly scoped edit.
- **cost:** About $0.01-$0.08 per interaction depending on screenshot dimensions and vision tokens; the screenshot and OCR dominate cost, not relay speech.
- **security:** Screenshots can contain secrets and authenticated work data. Keep capture on the Mac, send only the selected-window or redacted crop, attach app/tab origin and timestamp to the answer, and never infer an edit target from stale imagery. Screen edits should be limited to the explicitly named object but need not add a confirmation gate under owner policy.
- **missing:** A live mac-vision screenshot/vision action exposed to the relay; A typed screenshot crop plus origin/timestamp result in the Mac action protocol; A relay intent branch distinguishing visual_read from visual_edit; Browser-extension support for returning the visible authenticated tab as an image, not just extracted text

### "Save this exact place for me. Later, when I say 'take me back to the thing I saved', restore the right Mac app, browser tab, scroll position, selected text, and any safe draft context, then tell me what was restored."
- **useful because:** People lose work state rather than files: the right tab, paragraph, terminal directory, and unsent draft disappear into dozens of windows. A voice-addressable checkpoint would let the owner leave the Mac, return later, and recover the precise context without manually hunting. The pendant supplies the natural bookmark command, the Mac captures application state, and the browser extension contributes authenticated tab state that the relay cannot see itself.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension
- **model tier:** Cheap background model to label and search checkpoints; realtime relay only handles capture/restore utterances and speaks a compact receipt. Deterministic adapters should restore state; no model should fabricate a URL, draft, or scroll offset.
- **latency:** Capture receipt under 1 second; restore common browser/app state under 4 seconds, with a spoken list of anything that could not be restored.
- **cost:** Usually under $0.01 per save/restore; storage and Mac state collection dominate, with model use limited to naming and retrieval.
- **security:** Checkpoint metadata may expose private URLs, document names, or draft text. Encrypt checkpoint payloads at rest, keep authenticated page content on the Mac/browser bridge, expire raw screenshots and drafts, and speak only the checkpoint title until the owner requests details. Restoration must never submit a form or send a message.
- **missing:** A Mac state-snapshot protocol for focused app, window identity, workspace, terminal cwd, and browser tab/scroll/selection; Browser extension APIs to capture and restore scroll/selection without copying page secrets to the Worker; A durable encrypted checkpoint store and semantic lookup route; A deterministic restore executor with explicit non-submitting action types

### "When I say 'privacy now' or double-press the pendant, immediately stop capture and playback, mute or lock the Mac, hide authenticated browser tabs, and show me a spoken/LED acknowledgement; when I say 'resume', restore only the things that were actively paused."
- **useful because:** The owner wears the microphone in public and may need a reliable panic privacy action faster than finding a laptop or phone. It coordinates the pendant's physical control, the relay's live session, the Mac's audio/lock state, and the browser's authenticated surfaces; no single node can close all of those exposures.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension
- **model tier:** No expensive model for the trigger: firmware phrase/button event plus deterministic relay command. Realtime model only handles natural-language variants and the spoken acknowledgement.
- **latency:** Pendant mic shutdown and relay session stop under 150 ms; Mac/browser mitigation best effort under 1 second, with acknowledgement naming any unreachable surface.
- **cost:** Near-zero per use; this is control-plane traffic and deterministic actions.
- **security:** A false trigger is annoying, but a missed trigger is worse. Make the physical double-press unconditional, stop local capture before network notification, and fail closed for audio. Locking the Mac can interrupt unsaved work, so default to mute plus browser concealment and make lock a separately configured mode. Do not claim a surface is private until its agent reports success.
- **missing:** Firmware double-press gesture and a local hard mute path that survives a dropped relay link; An authenticated emergency-stop endpoint that invalidates active audio/session tokens; Mac action types for mute, stop playback, and optional lock with returned success; Browser extension command to conceal/blur authenticated tabs and later restore their visibility; A privacy-state fanout and truthful per-surface acknowledgement


## Changes it proposed to its own stack

### `integration` — Add a USB desk-mode transport that treats the physically connected nRF9160 pendant and ESP32 bridge as a local audio/control endpoint. When the pendant is plugged into /dev/cu.usbmodem00096003658* (and optionally the bridge on /dev/cu.usbserial-0287A9CA), the Mac relay agent should advertise a short-lived local session to the Worker, route microphone frames and Opus downlink over USB instead of waiting for LTE registration, and automatically tear the session down on unplug. Preserve the same conversation/session IDs and audio framing as the network path so this is a transport switch, not a second voice product.
- **owner gets:** The owner can use the real wearable today at a desk even though it is not LTE-registered. A button press on the pendant would work immediately, with lower latency and no radio dead zone, while the owner can unplug and keep using it over the normal path without starting over.
- effort: Medium-high: Mac serial daemon and reconnect logic, a framed bidirectional audio protocol, Worker session binding, and firmware USB endpoint work; hardware is already present for testing.  ·  risk: USB disconnects, partial frames, or two transports claiming one session could cut speech or duplicate playback. Use monotonic sequence numbers, explicit transport lease/heartbeat, and discard stale frames; on loss, fall back to a new network/offline-memo session rather than pretending continuity.
- cost: Negligible API cost in desk mode; roughly 1-2 engineer-weeks. No new hardware or routine SD writes.  ·  latency: Potentially removes LTE and relay radio delay (target under 100 ms device-to-Mac); setup should be invisible after cable insertion.
- security: A local USB serial peer gains live audio access. Bind only to the known USB VID/PID and a per-boot device nonce, require the Mac agent's existing authenticated local channel, and invalidate the lease on unplug.
- depends on: A Mac serial transport daemon for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A Worker session/transport lease endpoint; Firmware USB audio/control framing alongside the existing 24 kHz Opus path


## What it asked for

_Nothing._
## Its own summary

Recorded four non-refactor proposals. The strongest immediate one is USB desk mode: use the physically connected nRF9160 and ESP32 over serial as a local transport so the wearable works today despite no LTE registration. I also recorded screen-grounded pendant vision/editing, exact cross-app/browser work-state checkpoints, and a deterministic privacy-now emergency stop spanning pendant, relay, Mac, and authenticated browser state.

**Biggest unknown:** The relay still lacks an honest, inventoryable capability surface for the Mac's screenshot/vision, serial transport, emergency-stop fanout, and browser state adapters. Those need explicit routes and per-surface success receipts before the pendant can truthfully promise them.

