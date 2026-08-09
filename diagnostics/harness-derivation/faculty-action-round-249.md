# Harness derivation — faculty-action — round 249

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-browser-state-round-249** — Safari browser bridge is online with 2 tabs, currently foreground Safari, 0 pending commands, and lastSeenAt 2026-08-09T02:03:30.893Z; the device table still exposes only home-macbook-bridge and an offline mobile device, not a registered pendant.
  - evidence: GET /browser/status returned online=true, Safari on MacIntel, tabCount=2, pendingCommands=0; discover(devices) returned no pendant.

## Capabilities it proposed

### "“What are the four newest things on my Safari Reading List, and open the one I mean when I say ‘the second one’?”"
- **useful because:** The owner has asked this repeatedly and currently gets failures. It turns a spoken, index-based question into a verified answer using the real logged-in Safari session, then lets a follow-up deictic command select an item without exposing Reading List contents to the relay or asking the owner to type.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for list extraction and citation normalization; realtime only for the short spoken answer and resolving “the second one”
- **latency:** Answer in under 5 seconds; opening the selected item may take up to 8 seconds and must report if Safari state changed.
- **cost:** About $0.01–$0.04 per query; browser inspection and local AppleScript dominate, not model tokens.
- **security:** Reading List titles/URLs remain on the Mac/browser session; relay receives only a redacted item ID, title snippet, and user-approved URL target. Opening a URL is reversible; sending or purchasing is never implicit.
- **missing:** A Safari Reading List inspection adapter with stable item IDs and freshness hash; A short-lived spoken-result cursor so “the second one” cannot select from an old list; A browser postcondition receipt proving the selected item opened

### "“While I’m listening to the daily research brief, press the pendant’s bookmark button when I hear something important, and later give me the exact source and timestamp for each mark.”"
- **useful because:** It connects the only surface that knows the owner’s moment of attention (the worn button) to the audio artifact and the Mac/browser source. The owner gets durable, searchable evidence instead of an unlabelled voice memo or trying to remember which paragraph mattered.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background model aligns bookmarks to transcript/citations; realtime only acknowledges the physical mark with a terse cue
- **latency:** Haptic/audio acknowledgement under 250 ms locally; source alignment and note creation within 30 seconds after connectivity.
- **cost:** Roughly $0.03–$0.12 per brief, dominated by transcript alignment; storage is small JSON plus links, not duplicate audio.
- **security:** The pendant uploads only a monotonic bookmark event and artifact ID; the Mac resolves private source URLs locally. Creating a note is allowed by current owner policy; publishing or sending anything requires approval.
- **missing:** Audio artifact timeline metadata exposed to bookmark consumers; A joiner that correlates sw1 monotonic events with the audio_delivery_ack_queue artifact cursor; Citation/source locator extraction from research briefings; A dashboard view of bookmark-to-source evidence

### "“I’m about to leave my desk. Save the current browser page, my draft, and a spoken handoff so I can continue from the pendant later—without sending anything.”"
- **useful because:** This is a real cross-device handoff, not a Mac bookmark: the pendant supplies the deliberate leave/return signal, Safari contributes the authenticated page and draft state, and the relay preserves a compact resumable task. It prevents losing work when the owner walks away and makes the next spoken request unambiguous.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background model summarizes the handoff and extracts next actions; realtime only confirms capture and later reads the compact handoff
- **latency:** Capture acknowledgement under 1 second; handoff bundle complete within 5 seconds; resume answer under 3 seconds.
- **cost:** About $0.01–$0.05 per handoff; model summarization dominates, with bounded metadata storage.
- **security:** Draft text and URLs stay encrypted/local to the Mac where possible; relay stores a digest plus owner-selected sensitivity class. Never submit/send a draft. Returning to a stale page must be reported, not silently overwritten.
- **missing:** A cross-surface handoff object with expiry, sensitivity, and browser-session affinity; A local-only draft/page snapshot adapter for Safari and editor apps; A pendant gesture distinct from sw0 recording and sw1 moment bookmark (the planned second button or rotary encoder); Resume-time verification against fresh /observe and browser state

### "“Private mode. Let my Mac receive what I say, but do not send the audio or transcript to the relay or model.”"
- **useful because:** The owner could use the pendant for passwords, sensitive drafts, health information, or confidential work without having to trust the cloud path with raw speech. The Mac would still be able to perform local dictation or automation.
- **path:** pendant → mac-bridge → relay → dashboard
- **model tier:** No model for the private payload; local Mac processing only. Realtime handles only an authenticated mode toggle and a terse acknowledgement.
- **latency:** Mode change acknowledgement under 300 ms; local Mac transcription under 2 seconds for a short utterance.
- **cost:** Near-zero model cost in private mode; implementation cost is a local encrypted transport and retention controls.
- **security:** The relay must receive only an opaque session state and packet counters, never PCM, transcript, or command contents. The Mac must visibly and audibly distinguish private mode, expire it automatically, and erase temporary buffers on exit. A physical gesture should be required to enter private mode.
- **missing:** End-to-end pendant-to-Mac encrypted audio path that bypasses relay storage and inference; Firmware-visible private-mode state with crash-safe timeout; Mac local transcription/command endpoint with explicit zero-retention semantics; Independent audit proving no private packets reached relay logs

### "“Emergency revoke.” Cancel every pending action, invalidate every approval, and erase unsent drafts and queued browser commands everywhere, then tell me what was actually revoked."
- **useful because:** Today cancellation is fragmented across jobs, browser commands, approval records, and device inboxes. A single physical or spoken emergency action would give the owner a dependable way to shut down an accidental or compromised workflow across the whole hive.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic policy and signed revocation fan-out; no model should decide what to revoke. Realtime only summarizes the bounded result.
- **latency:** Local pendant acknowledgement under 250 ms; relay fan-out within 2 seconds; final inventory within 10 seconds, with unknown targets explicitly listed.
- **cost:** Less than $0.01 per invocation; dominated by receipt persistence and device fan-out.
- **security:** Must not claim deletion when a disconnected surface did not acknowledge. Use a monotonic revocation epoch, signed receipts, and a durable tombstone. The owner must be able to distinguish cancelled, erased, unreachable, and already-completed actions.
- **missing:** A hive-wide revocation epoch shared by relay, Mac jobs, browser commands, and pendant inbox/outbox; Deletion receipts for drafts and queued payloads, not merely command cancellation; An offline pendant trigger and later reconciliation protocol; A dashboard inventory of acknowledged versus unreachable surfaces

### "“Tell me exactly what crossed the privacy boundary for this task: which device saw my words, which app saw the result, what was retained, and when it expires.”"
- **useful because:** The owner currently has to trust a complicated multi-surface system without a human-readable provenance report. A per-task privacy receipt would make the pendant, relay, Mac, and browser accountable as one system rather than four opaque logs.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic event aggregation and redaction; a cheap background model may turn the receipt into one short sentence, but cannot alter its facts.
- **latency:** A compact receipt available within 3 seconds of task completion; full audit export within 15 seconds.
- **cost:** About $0.01 per receipt for optional summarization; event hashes and retention metadata are inexpensive.
- **security:** Receipts must not reproduce secrets or page contents. Store hashes, sensitivity labels, processors, timestamps, retention deadlines, and deletion status. The owner must be able to request erasure of the receipt itself.
- **missing:** A common privacy-event schema across pendant, relay, Mac, and browser; Packet-to-task correlation that survives browser and relay handoffs; Retention/deletion receipts from each surface; An owner-readable privacy dashboard and pendant summary mode


## Changes it proposed to its own stack

### `integration` — Implement a privacy-preserving Safari Reading List adapter on the Mac: snapshot the newest N entries locally, assign short-lived opaque IDs and a content hash, expose only requested title/domain snippets to the planner, and return a postcondition receipt when an ID is opened.
- **owner gets:** It directly fixes the owner’s repeated failed request for the newest Safari Reading List items and makes follow-ups like “open the second one” reliable even when the browser has multiple tabs.
- effort: Medium: AppleScript/Safari integration, stable cursor storage, freshness checks, and receipt wiring through the existing browser command ledger.  ·  risk: Safari changes or a stale list could cause the wrong item to open; refuse on hash mismatch and ask again. Never expose full Reading List contents to the relay by default.
- cost: No hardware cost; tiny local storage and roughly $0.01/query for optional normalization.  ·  latency: Local extraction 1–3 s; opening 1–5 s depending on Safari.
- security: Keeps URLs and titles on the Mac unless explicitly requested; opaque IDs prevent relay-side browsing of the list.
- depends on: Safari automation permission (currently granted); A browser cursor API with expiry; Fresh browser postcondition verification


## What it asked for

_Nothing._
