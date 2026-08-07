# Harness derivation — faculty-action — round 129

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Only interrupt me when it is genuinely urgent; let me acknowledge it from the pendant.”"
- **useful because:** The relay can watch Mac/browser sources while the owner is away from the screen, but the pendant is the only surface that can deliver a compact interruption and receive a physical acknowledgment. It prevents both missed urgent changes and notification spam.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → dashboard
- **model tier:** background classifier on relay; realtime only for the owner's follow-up conversation
- **latency:** Urgent event to pendant under 10 seconds; routine events are batched. Acknowledgment should be recorded under 2 seconds.
- **cost:** Low: event filtering and one short notification per true urgent event; dominated by relay wakeups and occasional Mac/browser polling, not LLM calls.
- **security:** Private browser/calendar/mail facts must remain on the relay/Mac path and only a redacted category plus short summary should reach the pendant. Require explicit per-source opt-in and never expose account contents on the LED/audio channel without an owner request.
- **missing:** event subscriptions from Mac Calendar/Mail and authenticated browser watches; a relay-to-pendant push transport for the currently USB-attached device and later LTE; pendant acknowledge/quiet-mode protocol; urgency policy and deduplication state

### "“Pin what I’m looking at right now so I can ask about it later.”"
- **useful because:** A physical pendant gesture would capture the owner's fleeting context before a tab, selection, or app changes. The later question can be answered from a time-stamped capsule instead of guessing which page or text they meant. This is especially useful today because the pendant is USB-connected to the Mac even without relay registration.
- **path:** pendant → mac-vision → browser-extension → mac-planner → relay-realtime → dashboard
- **model tier:** cheap local extraction and hashing on the Mac; realtime model only when the owner later asks a question about the capsule
- **latency:** Create a capsule in under 1 second after the button gesture; later retrieval under 3 seconds.
- **cost:** Low: local metadata/selection capture and compact text hashing; model cost only for later semantic retrieval or explanation.
- **security:** Capsules may contain private page text. Store encrypted locally by default, retain only a short TTL, show a visible LED acknowledgment, and require an explicit command before syncing content to the relay. Do not silently capture microphone audio or passwords.
- **missing:** an accessibility-free active-selection bridge (AppleScript/browser extension fallback where available, with honest unknown-selection state); pendant USB gesture and capsule-status protocol; encrypted capsule schema with URL, foreground app, selected text, screenshot/hash, timestamp, and provenance; cross-surface retrieval endpoint

### "“Tell me what is waiting for my review, in order, and let me dismiss or reopen one from the pendant.”"
- **useful because:** Long-running Mac and browser work currently finishes into separate job, receipt, and briefing surfaces. A wearable review queue gives the owner one truthful list while away from the screen, with enough identity to resume the exact item rather than starting over.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** no model for aggregation; use a cheap background summarizer only to compress stale receipts, reserving realtime for spoken follow-up
- **latency:** Queue refresh under 3 seconds after reconnect; one spoken item under 2 seconds; dismiss/reopen acknowledgment under 1 second.
- **cost:** Very low: existing job/receipt records plus short summaries; occasional summarization is the only model cost.
- **security:** The pendant must receive titles and redacted status, never raw private page contents or account tokens. Reopening an item should deep-link to the authenticated Mac/browser session, and any irreversible continuation must remain behind the existing review/approval surface.
- **missing:** a cross-surface queue projection joining jobs, receipts, browser sessions, briefings, and capture capsules; pendant list navigation and dismiss/reopen commands over USB/LTE; stable deep links from a queue item to its Mac or browser session; TTL and privacy classification for displayed summaries

### "“Put the whole hive in private mode now, and tell me when no pending capture or upload still contains private data.”"
- **useful because:** A wearable owner needs an immediate, physical privacy boundary that covers the Mac, authenticated browser, relay queues, and pendant—not merely muting one application. This gives a trustworthy way to stop context collection before entering a sensitive situation and receive a verifiable cleanup result.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Deterministic policy engine; no model needed except optional natural-language explanation.
- **latency:** Local Mac/browser capture stops within 500 ms; relay revocation and purge receipt within 5 seconds.
- **cost:** Low storage and queue-scan cost; no routine model spend.
- **security:** Private mode must fail closed on uncertain connectivity, revoke future uploads, quarantine already queued payloads, and show exactly what could not be deleted. It must not claim deletion from third-party browser/server history that it cannot control.
- **missing:** signed privacy-mode command from pendant; shared capture/upload gate across Mac, browser, and relay; queue inventory with deletion receipts and honest unknown states; visible pendant confirmation and recovery path

### "“Before you use a logged-in account, prove to me which account and identity you are about to act as.”"
- **useful because:** The owner may have multiple accounts or stale authenticated tabs. The system should not infer identity from whichever tab happens to be open; it should bind the planned action to an explicitly displayed account, domain, tab, and freshness proof across the browser and Mac.
- **path:** pendant → browser-extension → mac-planner → mac-vision → relay-realtime → dashboard
- **model tier:** Deterministic account/session binding and cryptographic challenge; use the model only to explain ambiguity.
- **latency:** Identity check under 2 seconds for an open session; stale or conflicting sessions pause before any mutation.
- **cost:** Negligible model cost; small metadata and challenge storage.
- **security:** Never transmit cookies or credentials. Bind only to extension-reported origin, account label, tab/session identifier, and a nonce; if the browser cannot prove identity, report unknown rather than guessing.
- **missing:** authenticated account identity reporting from the browser bridge; freshness and origin attestation for tabs; pendant-readable identity summary; a pre-action gate that consumes the attestation

### "“When I say I’m leaving, package exactly where I was across the Mac and browser so I can continue from the pendant or another device.”"
- **useful because:** Today a task can be split across an active app, private tabs, drafts, and queued jobs, but losing the Mac session loses the owner's place. A portable, privacy-scoped handoff would preserve the unfinished intent, evidence pointers, and safe next step without copying secrets or requiring the original screen.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Cheap background state summarization; realtime only when the owner asks to resume or resolve ambiguity.
- **latency:** Create handoff in under 3 seconds; resume summary under 2 seconds.
- **cost:** Low: compact encrypted metadata and provenance pointers; occasional summarization cost per handoff.
- **security:** Never replicate cookies, passwords, or full private page bodies by default. Encrypt the capsule, scope it to the owner's device/session, expire it, and make every included tab, draft, and queued action visible before transfer.
- **missing:** portable encrypted handoff format; browser/Mac task-state and draft extraction with secret redaction; relay storage and device-to-device retrieval; resume validator that checks tabs and data are still fresh


## Changes it proposed to its own stack

### `interaction` — Add a unified wearable event envelope shared by pendant USB today and relay/LTE later: event_id, source, severity, expiry, redacted payload, acknowledgment state, and provenance pointer. Mac/browser jobs, watch notifications, and action receipts publish into it; the pendant renders only the compact envelope and returns ack/snooze/dismiss events. Deduplicate by event_id across reconnects.
- **owner gets:** The owner gets one dependable way to hear about urgent changes and know whether the system actually delivered them, rather than separate silent queues on the Mac, browser, and relay.
- effort: Medium-high: protocol, USB serial transport, relay queue, reconnect semantics, and pendant firmware/UI; can be prototyped over the live USB-connected chips without flashing by using the Mac bridge.  ·  risk: A malformed or duplicated event could annoy the owner or hide an urgent one. Use bounded queues, expiry, replay tests, and a Mac dashboard fallback; never let notification delivery mutate the source account.
- cost: Small relay storage and bandwidth; negligible model cost because envelopes are produced by existing jobs/classifiers.  ·  latency: Adds one queue hop, typically tens to hundreds of milliseconds over USB and under a few seconds over LTE.
- security: Redaction and provenance indirection reduce sensitive data on the pendant, but event metadata still reveals activity; encrypt transport and make source subscriptions explicit.
- depends on: relay-to-pendant transport over USB, then LTE; pendant acknowledgment firmware; event producers for browser/Mac watches; durable deduplication/TTL storage


## What it asked for

_Nothing._
