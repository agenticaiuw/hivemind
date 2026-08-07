# Harness derivation — relay-realtime — round 114

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Continue where I left off.” The pendant should tell me, in a few seconds, which task I last abandoned across my Mac and signed-in browser, what state it is actually in, and offer the single next useful action—without making me remember the app, tab, or wording I used."
- **useful because:** The owner is often away from the Mac and cannot reliably remember whether a draft was saved, which browser tab mattered, or what a delegated job was waiting on. This is a genuinely cross-body capability: the pendant supplies the request and spoken answer, the relay correlates history, the Mac establishes local UI state, and the browser supplies authenticated tab state. Today those surfaces expose isolated jobs/sessions/receipts, but no durable notion of an unfinished human task or a resumable checkpoint.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime relay for intent recognition and a short spoken summary; a cheaper background planner builds the checkpoint and candidate next action from receipts, Mac diagnostics, and browser inspections. Use the realtime tier again only when the owner asks to resume or disambiguate.
- **latency:** A spoken answer within 2–4 seconds when recent receipts exist; up to 10 seconds when the Mac and browser must be queried. Never silently execute the candidate action—speak the proposed next step and let the owner's normal explicit command trigger it.
- **cost:** About one realtime turn plus one small background synthesis call per resume request; roughly $0.01–$0.05 depending on transcript/state size. The dominant cost is compressing multi-surface state, so store normalized checkpoints and send only deltas.
- **security:** Authenticated browser content and local Mac state must stay scoped to this owner and session; redact secrets and page bodies from the spoken response and logs. A stale checkpoint could cause the wrong action, so show source timestamps and distinguish observed state from inference. Reading is automatic; mutations require the owner's explicit follow-up utterance.
- **missing:** A durable cross-surface task/checkpoint schema with task identity, last observed state, timestamps, source citations, and confidence; Mac and browser adapters that report resumable foreground drafts/tabs and unsaved-vs-saved state without taking control; A relay read endpoint that merges job receipts, Mac observations, and browser inspections by task identity; Checkpoint invalidation/versioning when a tab closes, a file changes, or an action receipt is undone; A compact spoken-summary formatter and an explicit resume-intent handoff to mac-planner/mac-vision

### "“What changed since I left?” When I press the pendant after walking away from my Mac, it should give me a concise, spoken diff of meaningful changes across my delegated jobs, Mac workspace, and authenticated browser—not a generic notification dump."
- **useful because:** The owner cannot watch the Mac or browser while wearing the pendant. A departure-scoped diff answers the practical question of whether anything needs attention, while avoiding repeated summaries of unchanged state. It depends on all nodes because only the pendant knows the human's return moment, the relay can retain the baseline, and Mac/browser can observe their separate changes.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Cheap background model computes and ranks the diff from structured snapshots; realtime relay only captures the request, reads the prepared result, and speaks it. Escalate to a slower planner only when changes conflict or need interpretation.
- **latency:** Under 2 seconds for an already-built diff; under 8 seconds for a fresh Mac/browser sweep. No automatic mutations.
- **cost:** A small background synthesis call per departure/return pair, usually under $0.02; storage is the main cost, limited to compact hashes, titles, statuses, and cited deltas rather than page bodies or screenshots.
- **security:** Do not retain authenticated page contents by default; keep origin, title, change type, and minimal redacted excerpts. Baselines must be bound to the owner's device/session and expire. Clearly label inferred significance and provide “show me the source” as a separate explicit request.
- **missing:** A pendant departure/return marker (button gesture or connection transition) with monotonic timestamps; Versioned cross-surface snapshots and a diff engine for jobs, Mac foreground/workspace state, and browser tabs; A meaningful-change classifier that suppresses cursor movement, ads, and routine browser noise; Retention and invalidation rules for snapshots when sessions expire or sensitive tabs are closed; A spoken result endpoint that streams ranked diffs to the relay

### "“When I leave, protect my browser; when I come back, restore it.” The pendant should mark an away boundary and have the relay instruct the browser extension to blur or lock configured sensitive tabs, then restore them only after the pendant returns and the owner explicitly says “unlock.”"
- **useful because:** The pendant is physically with the owner while the Mac may be unattended. Today a signed-in browser can remain exposed after the owner walks away, and link loss alone cannot distinguish an outage from departure. This turns the wearable into a privacy boundary spanning hardware, always-awake relay, and the session-holding browser.
- **path:** pendant → relay → browser-extension → dashboard → mac-planner
- **model tier:** No expensive model is needed for the boundary event or lock operation. Use realtime only for the owner's spoken unlock/status request; use deterministic extension code for tab handling and a cheap background verifier to report which tabs were protected.
- **latency:** Lock command should reach the extension within 2 seconds when online; on reconnect, apply it before reporting state. Unlock waits for an explicit spoken command and should confirm which tabs were restored.
- **cost:** Near-zero model cost for automatic lock; a few cents only for occasional spoken status interpretation. Storage is small: tab/session identifiers and protection policy, never page contents.
- **security:** Default to locking/blur, not closing or editing pages. Protect against replay with monotonically increasing signed boundary events and a short-lived unlock nonce. Never speak or log page contents. If the browser is offline, tell the owner it could not be protected rather than claiming success; expose an unmistakable “protection incomplete” LED/voice state.
- **missing:** Browser-extension command delivery with leases, deduplication, and explicit acknowledgement per tab; A policy store mapping sensitive origins/tabs to lock behavior, with safe defaults and local-only secrets; Signed pendant away/return events and relay-side replay protection; A browser-side lock implementation that preserves form state without capturing or transmitting it; An owner-visible protection status and recovery path when the browser or Mac is offline


## Changes it proposed to its own stack

### `firmware` — Add a local one-button boundary marker: a deliberate long-press records AWAY, a deliberate double-press records BACK, and the nRF9160 emits a compact signed event containing device sequence number, monotonic time, battery, and link state when connectivity returns. The firmware must provide haptic/LED acknowledgement, debounce accidental presses, and preserve a small ring buffer through link loss.
- **owner gets:** The owner gets trustworthy “what changed while I was away?” answers anchored to when they actually left and returned, even if LTE briefly drops. They do not need to say a special phrase or keep the pendant app open.
- effort: Medium: firmware gesture state machine, event signing/serialization, relay ingestion, and a dashboard diagnostic. Validate that the gesture is distinguishable from the existing single-button interaction.  ·  risk: Accidental boundaries could produce misleading diffs; recover by allowing the next explicit spoken request to choose a different time window and by showing the event timestamp. A full ring buffer could overwrite old markers, so retain the newest few and surface that limitation.
- cost: Negligible API cost; roughly 1–2 KB firmware/event code and a few dozen bytes per boundary event. No meaningful power increase beyond the LTE uplink already used.  ·  latency: Immediate local LED acknowledgement; uplink delivery is deferred during outage and normally adds one small event packet.
- security: Sign events with the device identity so a forged boundary cannot alter history; do not include audio or page contents in the marker.
- depends on: A relay endpoint and durable store for signed boundary events; Cross-surface snapshot/diff capability; A documented long-press/double-press interaction that does not conflict with current single-button behavior


## What it asked for

_Nothing._
## Its own summary

I discovered the current toolset and grants: core routing still relies on get_mac_status/mac_run_actions/browser_run_actions/web_search/mac_delegate. Newer relay-level tools (relay_route_intent, server_browser_actions) are present only as schemas with no implementation. Devices show the Mac bridge online; browser has a stale command in processing with repeated attempts. The Mac route table is rich, but I still cannot inventory relay routes directly from my own surface.

**Biggest unknown:** Whether the relay will get its own discoverable capabilities/routes and working implementations for intent routing and server-side browser actions, so I can safely route and report without inventing a protocol or depending on the Mac/browser being online.

