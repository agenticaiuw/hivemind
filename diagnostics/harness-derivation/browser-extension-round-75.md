# Harness derivation — browser-extension — round 75

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser availability Round 75** — Live GET /browser/status now reports online:false; only home-chrome is listed, with no tab and 5 pending commands. The previously registered Safari device is not currently present/online, so authenticated page work cannot run until Safari extension heartbeats again.
  - evidence: GET /browser/status returned {online:false, devices:[home-chrome tabId:null tabCount:null online:false], pendingCommands:5}.

## Capabilities it proposed

### "“Brief the page I’m looking at.”"
- **useful because:** This makes the browser’s unique access to authenticated pages useful in the moment: the owner gets a short, source-grounded answer in their ear, while a durable cited brief remains on the Mac for later review. It works across Safari, relay, Mac workspace, and pendant rather than being just another Mac summarizer.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard-ux
- **model tier:** Use the cheaper background model for extraction, citation normalization, and 24 kHz speech preparation; reserve realtime only for the owner’s spoken request and playback control.
- **latency:** Return page title plus a 1–2 sentence spoken brief in 8–15 seconds; begin playback as soon as the first audio segment is ready, while the full cited artifact finishes in the background.
- **cost:** Roughly one background summarization invocation plus Opus/TTS processing; dominated by page text tokens and audio generation, not browser control. Cache the extracted page hash so replay or retries cost no model call.
- **security:** Only the already-open Safari tab and selected extracted regions leave the Mac; retain URL, timestamp, and source snippets in the local artifact, not raw page dumps. Apply the owner’s existing rule to stop before any click, send, purchase, or submit. Encrypt any queued audio/artifact and expire it after a short TTL; if upload fails, use the pendant SD only as a bounded failure buffer and delete after confirmed delivery.
- **missing:** A current-tab browser action that returns structured title, URL, selected text, and stable source anchors in one result; A one-shot browser-to-audio job coordinator that links extraction, summary, artifact, and playback IDs; A 24 kHz audio queue with resume/skip and delivery acknowledgement across relay and pendant; A local redaction/retention policy for authenticated page artifacts

### "“Save this exact passage I’m looking at, and remind me why I saved it.”"
- **useful because:** Today the owner can read a private page or make a generic note, but cannot create a durable, source-accurate memory of the exact paragraph in front of them while away from the keyboard. This would bind the authenticated Safari tab, quoted passage, page location, timestamp, and the owner’s spoken reason into one retrievable item; later the pendant can replay the reason and the Mac can reopen the passage at its original context.
- **path:** browser-extension → relay-realtime → pendant → mac-planner → dashboard-ux
- **model tier:** Realtime handles the short spoken reason and immediate acknowledgement; a cheaper background model normalizes the quote, extracts a compact title, and indexes it. No expensive model is needed for replay or exact retrieval.
- **latency:** Capture and acknowledge in under 3 seconds; persist the source packet immediately, then finish indexing within 10 seconds. Reopening the source should be on demand, not part of capture.
- **cost:** Small background extraction/indexing call per capture, dominated by quoted page text; near-zero cost for later lookup and audio replay. Storage is a small local record plus an optional short audio clip.
- **security:** Only the already-open authenticated tab’s selected/visible passage is copied; cookies and page credentials never leave Safari. Store sensitivity and an expiry with the record, encrypt local content, and require explicit confirmation before sharing it or sending it anywhere. If the source page later changes or disappears, retain the original quote and clearly mark the reopen link stale.
- **missing:** A browser extension event/action that captures the current selection or reading viewport with tabId, URL, DOM locator, and a short source hash; A pendant-side bookmark trigger that can carry the owner’s spoken annotation or a timestamped voice clip offline; A provenance-aware local memory record and retrieval API that can reopen or report stale source context; A small browser-to-pendant acknowledgement/replay path for saved annotations


## Changes it proposed to its own stack

### `browser-harness` — Add an expiring, tab-bound browser capability lease to the Safari extension protocol. On each heartbeat, Safari issues a random lease ID for the currently attached tab/window; /execute actions must carry that lease and an idempotency key, and results echo the lease plus a DOM-generation counter. Lease rotation on navigation, tab close, or idle timeout makes stale queued clicks and late results harmless without introducing an approval gate. Persist only hashes and audit metadata (not cookies or page contents), and let the Mac planner renew the lease when the owner explicitly asks to continue on the same tab.
- **owner gets:** Long browser tasks stop acting on the wrong tab after Safari changes pages or the Mac reconnects. The owner can safely say “continue” across multiple agents while private login sessions stay inside Safari, and the action history can explain exactly which tab generation was read or changed.
- effort: Medium: extension heartbeat/protocol update, browserBridge lease validation, queue schema migration, and tests for navigation, reconnect, duplicate delivery, and two simultaneous tabs.  ·  risk: A lease mismatch could abort an otherwise harmless workflow; recover by refreshing the current tab lease and replaying only idempotent reads. Never replay clicks or typing automatically after a generation change. This is observability and stale-command protection, not a user confirmation gate.
- cost: Negligible API cost; a few dozen bytes per command/result and a small D1/local metadata record.  ·  latency: Under 100 ms for local validation; no extra model round trip. Reconnect may add one heartbeat interval before continuation.
- security: Improves containment: a stolen or delayed command cannot target a later tab state, and no authentication material leaves Safari. Lease IDs must be high-entropy, short-lived, and excluded from spoken logs.
- depends on: A working durable browser job runner or queue persistence (the current router exists but the durable runner is still open); Safari extension heartbeat support for tab/window identity and navigation generation; Typed result receipts already present in browserBridge/browserSessions

### `hardware` — Add a low-power haptic actuator and driver to the production pendant, with firmware primitives for distinct short patterns (new private-browser item, playback ready, action failed, and urgent interruption). Let the relay/browser path request a pattern, but queue and rate-limit it locally so a reconnect storm cannot buzz continuously; the single button should acknowledge or replay the most recent pattern.
- **owner gets:** The owner can receive a discreet alert about a meaningful authenticated-page result or completed brief while in a meeting, on transit, or where spoken audio would be inappropriate. It gives the browser and pendant a useful channel that survives muted audio and makes completion status perceptible without looking at the Mac.
- effort: Low-to-medium product hardware and firmware change: coin/LRA actuator, haptic driver, one GPIO or I2C line, enclosure isolation, pattern API, local queue, and battery characterization.  ·  risk: Vibration can be distracting or expose that a private event occurred. Provide a physical mute mode, quiet hours, intensity limits, and generic patterns that do not reveal content. If the driver fails, audio/LED remain available; firmware must fail open to normal button behavior.
- cost: Approximately $1–$4 BOM increase plus PCB/enclosure work; short pulses likely add only a few mWh per day, but standby leakage must be measured on the actual power budget.  ·  latency: Local acknowledgement under 50 ms after a relay push; no model latency. If offline, queued patterns play when connectivity returns only if still within their expiry window.
- security: Do not encode message contents in patterns. Browser-originated notifications should carry only an opaque event class and expiry, with sensitive detail remaining on the Mac/relay.
- depends on: A relay event-to-pendant notification route; Firmware support for a local notification queue and mute/quiet-hours state; Browser result receipts that classify completion or failure without exposing page contents


## What it asked for

_Nothing._
## Its own summary

I discovered a live regression: Safari is no longer reporting at all. GET /browser/status shows only the offline home-chrome stub, no tab, and 5 pending commands, so authenticated browser work is currently unavailable. I recorded and broadcast that finding. I proposed (1) a one-shot “Brief the page I’m looking at” cross-surface flow—Safari extraction to cited Mac artifact plus 24 kHz relay/pendant playback—and (2) expiring tab-bound capability leases with DOM-generation counters to prevent stale queued browser actions without adding approval gates. The remaining implementation gaps are a durable browser job runner, current-tab structured extraction, and browser-to-audio queue linkage.

**Biggest unknown:** Why the real Safari extension disappeared from /browser/status and whether its 5 queued commands are safe to discard, retry, or inspect once it reconnects.

