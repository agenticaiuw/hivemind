# Harness derivation — mac-planner — round 200

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac_live_state_2026-08-08_round200** — The AI Pendant Agent is online with Accessibility and Screen Recording trusted, synthesized input verified, Safari extension online with 9 tabs, relay reachable, and no pending browser commands. Foreground app is Claude; the browser's durable session list currently exposes x.com/home plus two probe tabs.
  - evidence: GET /ops/snapshot HTTP 200 at 2026-08-08T02:54:55Z and mac_readonly_inspect operation running_apps/foreground_app responses.

## Capabilities it proposed

### "When I press the pendant's bookmark button, create a complete, timestamped 'what was happening' case on my Mac: link the bookmark/audio, capture the active app and browser tab, attach the nearest calendar/mail context, and leave one searchable note with a short spoken confirmation."
- **useful because:** This turns the existing one-bit moment bookmark into a reliable memory of interruptions, bugs, meetings, and ideas. It works even when the LTE pendant is unregistered because the pendant is USB-attached to the Mac today, and it uses the worn button to mark the instant while the Mac contributes context no wearable can see.
- **path:** pendant → mac-planner → relay-realtime → mac-vision → browser-extension
- **model tier:** Use deterministic local capture and a cheap background model for naming/summarising; reserve realtime only for the spoken acknowledgement. No model is needed to collect timestamps, app identity, URL, or calendar/mail snippets.
- **latency:** Acknowledge the button in under 1 second; write the durable case bundle within 5 seconds; summarise asynchronously within 30 seconds.
- **cost:** Usually under $0.01 per case; local capture dominates latency, and only the optional summary spends model tokens.
- **security:** Calendar/mail snippets and the active URL can be sensitive. Redact message bodies by default, store the bundle in ~/AI-Pendant-Workspace, hash/link the original audio rather than duplicating it, and require the owner's existing policy entry before including mail or authenticated URLs.
- **missing:** USB-serial pendant event/audio bridge into the Mac agent (the hardware is connected, but no callable serial-exchange tool is available to me this round); A durable case-bundle schema and event consumer joining pendant bookmarks to /observe and browser state; An explicit owner policy entry for whether mail bodies and authenticated URLs may be captured

### "Keep my pendant usable whenever it is plugged into the Mac: automatically detect the USB serial connection, route voice/audio and inbox alerts over the Mac when LTE is unavailable, and hand back to LTE without losing or duplicating a conversation when I unplug it."
- **useful because:** The pendant is physically connected now but is not LTE-registered, so this is the fastest path to a genuinely usable wearable today. It gives the owner continuous voice and alert behavior at a desk, while preserving the same device queues and audio quality rather than exposing a simulator-only path.
- **path:** pendant → mac-planner → relay-realtime → relay
- **model tier:** No expensive model for transport or deduplication. Realtime is used only for the actual voice conversation; a cheap background worker can reconcile reconnect receipts and queue state.
- **latency:** USB link detection under 2 seconds, audio failover under 500 ms where buffered packets permit, and exactly-once queue reconciliation within 10 seconds of reconnect.
- **cost:** Negligible model cost; local serial framing and relay receipt logic dominate engineering, with normal realtime audio cost only while speaking.
- **security:** The Mac becomes a local transport for microphone and generated audio. Require the owner's local privacy latch to be honored before opening the serial stream, encrypt or authenticate the USB session, never log PCM, and use sequence numbers plus relay acknowledgements so reconnects cannot replay audio or alerts.
- **missing:** A callable USB-serial exchange/daemon (the pending mac_serial_exchange request is still unavailable to me); A tether session protocol carrying pendant_store records, QoS frames, and Opus packets with sequence/ack ranges; Relay-side exactly-once reconciliation keyed by device session and packet range; A visible tether-versus-LTE status surfaced through the existing single LED semantics

### "Let me start a long Mac task by voice from the pendant—such as preparing a research folder or cleaning Downloads—and then ask 'how far along is it?', 'stop', or 'undo that' from the pendant without returning to the Mac."
- **useful because:** A wearable command is otherwise a fire-and-forget request. This makes long-running desktop work trustworthy: the owner can leave the desk, get a concise progress receipt, cancel before the next irreversible step, or reverse the last supported mutation from the same device that started it.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension
- **model tier:** Use deterministic job state, receipts, cancellation, and undo routes; use a small text model only to resolve pronouns such as 'that task'. Realtime is needed only to speak the short status or cancellation result.
- **latency:** Start acknowledgement under 1 second, status under 2 seconds from cached receipts, cancellation request under 2 seconds, and completion notification as soon as the Mac receipt arrives.
- **cost:** Usually under $0.005 per status/cancel turn; the Mac job and any original research/action dominate cost, not the follow-up.
- **security:** A spoken 'undo' must target an immutable job id, never the last arbitrary desktop action. Keep destructive confirmation policy explicit for send/delete/buy, redact file contents from spoken receipts, and emit an audit receipt for every start, cancel, and undo.
- **missing:** Pendant-side rendering of structured job receipts and a compact command correlation id; Relay intent resolution that binds 'that' to the most recent active job for this owner; A Mac job state stream with step-level progress, not only terminal receipts; A policy-aware cancellation boundary for browser submissions and other irreversible actions

### "Before a high-impact browser or Mac action happens, read me one short exact preview on the pendant and let me authorize that specific preview with the pendant's physical button; reject stale previews, changed pages, and approvals intended for another action."
- **useful because:** The owner gets a trustworthy hands-free confirmation mechanism that is harder to trigger accidentally than saying 'yes' while the browser or foreground app may have changed. It binds wearable presence, the relay's intent, the Mac executor, and the browser session into one auditable action authorization.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision
- **model tier:** Use deterministic hashes, expiry, action identity, and button-event matching. Realtime only speaks the short preview; no model is needed to decide whether the physical authorization matches.
- **latency:** Preview within 2 seconds, button authorization accepted within 1 second, and stale or mismatched previews rejected immediately.
- **cost:** Negligible model cost; the dominant work is a signed authorization protocol and reliable button-event delivery.
- **security:** A stolen or unattended pendant could authorize actions, so require the local privacy latch state to permit approvals, expire previews after 30 seconds, bind approval to an action hash plus browser tab/session, and never authorize a changed plan. The owner must explicitly enable each action class, especially send, delete, and purchase.
- **missing:** A cryptographically bound preview and authorization protocol across relay, Mac, and browser; A USB/LTE-independent pendant button-event delivery path with replay protection; Mac/browser enforcement that checks the authorization immediately before execution, not when the plan is created; Owner-configurable action classes and expiry policy

### "If a Mac or browser task fails, tell me on the pendant exactly what failed, preserve the affected state, and offer one safe recovery choice—retry, open the failure, or undo—without silently retrying a possibly duplicated action."
- **useful because:** Today a failed desktop job can leave the owner unsure whether anything happened. A failure capsule would make automation recoverable from the wearable, preserve evidence for debugging, and prevent duplicate submissions or purchases caused by blind retries.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision
- **model tier:** Use deterministic receipts, idempotency keys, and action journals; use a cheap model only to compress a technical failure into one spoken sentence. Realtime is only for delivery of that sentence.
- **latency:** Failure notice within 3 seconds, recovery choices within 5 seconds, and no automatic retry of high-impact actions.
- **cost:** Under $0.01 for an occasional summarization; storage of compact receipts and the recovery journal dominates.
- **security:** Failure capsules may contain URLs, filenames, or document snippets. Redact by default, retain only bounded metadata, bind recovery to the original job and action hash, and require explicit confirmation for any recovery that could send, delete, buy, or submit twice.
- **missing:** A durable failure capsule with pre-state, post-state, and idempotency metadata; Mac/browser adapters that can classify whether an interrupted action is safe to retry; Pendant rendering for a small set of recovery choices; Relay routing for recovery commands after the original Mac session has ended


## What it asked for

_Nothing._
