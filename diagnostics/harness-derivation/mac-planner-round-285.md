# Harness derivation — mac-planner — round 285

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-accessibility-status** — As of 2026-08-09 03:17Z, AI Pendant Agent has Accessibility and Screen Recording trusted, synthesized input verified, secure input inactive, and UI actions will reach screen. iPhone Mirroring is running; iOS pairing probe remains offline.
  - evidence: mac_readonly_inspect operation=running_apps/foreground_app invoked GET /observe HTTP 200

## Capabilities it proposed

### "“I got interrupted—package exactly what I was looking at, tell me the one next step, and leave everything ready to resume.”"
- **useful because:** The current system can separately observe Safari, read Calendar/Mail, and write files, but it does not turn an interruption into a durable, time-stamped handoff. A pendant bookmark while worn becomes a relay event; the Mac captures the foreground app/browser URL and relevant schedule/mail context, writes a redacted handoff note, and queues one spoken next action back to the pendant. This is the highest-value daily behavior: it converts a fleeting moment into continuity without requiring the owner to narrate context.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Use the realtime model only for the short spoken acknowledgement; use a cheaper background model for ranking/context compression and redaction. Mac/browser observations are deterministic and should not consume model tokens.
- **latency:** Acknowledge the bookmark locally immediately; Mac evidence bundle within 5 seconds; spoken next-step card within 10 seconds. If the Mac is asleep or browser unavailable, retain the relay event and deliver a degraded card later.
- **cost:** Low: one compact background summarization call per bookmark (typically <$0.01), with most work from local observation and file creation. Avoid resending full pages; send URL/title and bounded snippets.
- **security:** Capture only foreground app, active tab URL/title, and explicitly allowlisted Calendar/Mail snippets; redact secrets and page bodies by default. Never capture password fields or microphone audio. The resulting note is local; relay stores only a short event and hash. Owner policy must explicitly authorize which apps/sites are included.
- **missing:** bookmark-event consumer that joins pendant timestamps to a Mac observation window; bounded foreground-document/selected-text semantic read (URL/title alone is insufficient for editor work); a relay inbox payload type for a redacted interruption handoff; owner-configurable app/site capture policy

### "“Prepare this email/purchase/message everywhere I’m signed in, show me exactly what will happen, and let me approve it from the pendant without moving focus.”"
- **useful because:** Today a draft may be prepared in one surface, but consequential actions across Mail, an authenticated browser, and iPhone Mirroring have no single human-readable preview or one approval decision. This would gather the proposed mutations from Mac, browser, and iPhone, normalize recipients/items/amounts into one preview, send the preview to the pendant, and execute only the exact approved plan. The owner keeps the browser session and phone reach while getting one clear approval moment.
- **path:** pendant → relay → mac-planner → browser → ios-control → dashboard
- **model tier:** Use a cheap model for extracting a structured diff from each surface; use realtime only to read the concise preview and receive spoken approval. Execution itself is deterministic and must not be delegated to a model after approval.
- **latency:** Preview in 3–8 seconds for a single surface and under 15 seconds for three surfaces. Approval-to-action under 5 seconds, with a durable receipt even if one node drops.
- **cost:** Usually <$0.02 per invocation; browser/iPhone snapshots and deterministic diffing dominate latency, not tokens. No page-body upload unless needed to resolve a visible mutation.
- **security:** The approval must bind to an immutable plan hash, recipient/account/item identifiers, and expiry; an altered plan requires a new approval. Destructive actions (send, delete, buy) remain confirmation-required, matching the owner's policy. Redact message bodies and payment details in relay logs; keep full previews local. If iPhone Mirroring is not paired, do not silently fall back to a different account.
- **missing:** plan-hash-bound approval token spanning Mac, browser, and iPhone action executors; iPhone Mirroring semantic read/action receipts with stable element identity; pendant-side display/voice confirmation payload and an unambiguous approval event; cross-surface mutation diff schema and expiry/replay protection

### "“The voice glitched—diagnose it end to end, tell me whether it was the pendant, radio, relay, or Mac, and file a reproducible bug bundle without recording my conversation.”"
- **useful because:** A single audio symptom currently spans four opaque boundaries. The pendant already has a synthetic bidirectional diagnostic fixture and congestion guard, while the relay and Mac can observe pipeline/job state; this capability would correlate those measurements by one incident ID, classify the fault, and leave a reproducible bundle for engineering. It turns 'it sounded bad' into a concrete answer without retaining private speech.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Use deterministic thresholds first (packet loss, underruns, encode/decode duration, reconnects, Mac input/output state); use a cheap background model only to write the human explanation and bug summary. Realtime should speak only the result if the owner asks during a call.
- **latency:** Show a local 'diagnostic queued' acknowledgement immediately; collect a 10–20 second fixture after the call or on explicit request; produce classification in under 30 seconds and a durable receipt afterward.
- **cost:** Usually <$0.01 for a short explanation. The cost is bounded fixture radio time and a small log bundle, not long audio storage.
- **security:** The fixture must use synthetic frames only and explicitly exclude microphone PCM. Store counters, sequence numbers, firmware/build IDs, and hashes; redact URLs, message content, and account identifiers from Mac context. Filing externally must be a separate owner-approved action; local issue creation is enough by default.
- **missing:** incident coordinator joining device QoS frames, relay pipeline metrics, and Mac/bridge observations under one ID; a read-only UART/USB fixture collector that returns bounded logs and exit status (the pendant is physically attached today, but LTE registration is still offline); fault taxonomy and deterministic threshold versioning; bug-bundle receipt plus deduplication by firmware/build/profile and metric hash

### "“Do not interrupt me for duplicates: merge new alerts from Mail, Calendar, browser sessions, Mac apps, and iPhone into one urgency-ranked stream, and let me hear only the next genuinely actionable item on the pendant.”"
- **useful because:** The existing pendant inbox can hold alerts, but it cannot know that a calendar change, an email, a browser notification, and an iPhone notification describe the same event. The owner currently pays the attention cost repeatedly or misses the important item. A cross-node deduplicator would cluster by entity and time, preserve source links, escalate only when state changes, and synchronize read/snooze state across every surface.
- **path:** pendant → relay → mac-planner → browser → ios-control → dashboard
- **model tier:** Use deterministic entity/time/thread matching first; use a cheap background model only for ambiguous clustering and urgency extraction. Realtime is needed only to speak the selected alert.
- **latency:** Ingest within 30 seconds of a source change; update the pendant queue in under 5 seconds after classification. Never block a source app while clustering.
- **cost:** Low, roughly <$0.01 per burst of alerts; most work is local event normalization and hash-based clustering. Send snippets, not full mail or page bodies, to the model.
- **security:** Source connectors must expose only notifications and bounded snippets, never passwords or arbitrary page content. Keep source IDs and account scopes local; relay receives redacted cluster records. Snoozing an alert must not delete the underlying mail/calendar event. Owner policy must define quiet hours and urgency overrides.
- **missing:** event connectors for Mac notifications, browser notification state, and iPhone Mirroring notifications; stable cross-source entity/thread identifiers and a deduplication store; urgency and escalation policy editable by the owner; inbox payload fields for cluster membership, source links, expiry, and snooze state

### "“When I join a call or share my screen, automatically protect private windows and tabs, keep the work context I need visible, and restore my workspace exactly when the call ends.”"
- **useful because:** A meeting can expose mail, passwords, medical or financial tabs, and private notes even when the owner did not intend to share them. This capability would combine Calendar/Zoom state, Mac screen observation, browser session metadata, and a pendant privacy latch: it would stage a safe workspace before sharing, keep a reversible manifest of what moved or hid, and restore only after the call. It protects the owner without making them manually close twenty windows.
- **path:** pendant → relay → mac-planner → browser → ios-control → dashboard
- **model tier:** Use deterministic app/window classification and a local allow/deny policy; use a cheap model only to label ambiguous windows. No realtime model is needed except an optional short pendant warning.
- **latency:** Detect a meeting/share transition within 2 seconds; stage the safe workspace within 5 seconds. Restoration should be atomic or leave a clear recovery manifest.
- **cost:** Near-zero model cost in normal operation; the main cost is local UI observation and reversible window/tab operations.
- **security:** This must fail closed for unknown windows and never transmit screenshots or page bodies to the relay by default. Account/site policies belong to the owner and must be editable. Restoration must not reopen a tab that has since become sensitive or logged out. The privacy latch must remain local and usable if the network is down.
- **missing:** reliable meeting/share lifecycle events from Zoom and macOS; semantic window classification with app/document identity, beyond a foreground-app snapshot; reversible workspace manifests covering browser tabs, windows, and iPhone Mirroring; owner-managed sensitivity policy and a local fail-closed privacy controller

### "“If my pendant, phone, or Mac drops out while I am talking, keep the conversation alive on whichever surface is still reachable, then reunite the transcript and pending actions without repeating anything.”"
- **useful because:** The owner currently experiences each node as a separate failure domain: a radio drop can strand audio, an iPhone pairing loss removes controls, and a Mac restart can leave a plan half-done. A session migration protocol would elect the surviving surface, downgrade gracefully to text or Mac audio, checkpoint conversation state and unexecuted actions, and resume on reconnection with explicit sequence numbers. It is the difference between a hive and several unrelated assistants.
- **path:** pendant → relay → mac-planner → browser → ios-control → dashboard
- **model tier:** Use deterministic session/sequence handling and a cheaper background model to compress old context after migration. Use realtime only for the active voice leg; never regenerate already acknowledged actions from model memory.
- **latency:** Fail over in under 3 seconds for transport loss; resume state within 10 seconds after a surface returns. A reconnect must be idempotent even after repeated crashes.
- **cost:** Low-to-moderate: one compact state checkpoint per turn and occasional background compression, generally <$0.02 for a long session. Bandwidth and durable state dominate.
- **security:** Bind checkpoints to the owner/session and encrypt pending actions at rest. Do not copy microphone audio or authenticated browser cookies between surfaces. A migrated session must preserve destructive-action confirmation state only if the exact plan hash and expiry still match; otherwise require reapproval.
- **missing:** surface capability leases and a deterministic session-election protocol; cross-surface transcript/action checkpoints with sequence numbers and idempotency keys; Mac audio/text fallback and iPhone Mirroring reconnect detection; relay-side migration receipts and a way to tell the pendant which state was durably committed


## What it asked for

_Nothing._
## Its own summary

Produced three non-overlapping cross-node capabilities: (1) interruption-to-handoff packaging from pendant bookmark + Mac/browser context + spoken next step, (2) immutable cross-surface preview and pendant approval for Mail/browser/iPhone consequential actions, and (3) synthetic end-to-end audio incident diagnosis and reproducible bug bundles. Fresh Mac observation also established that Accessibility and Screen Recording are now trusted and synthesized input reaches the screen; iPhone Mirroring is running but its pairing probe and the pendant remain offline.

**Biggest unknown:** The critical missing seams are not basic Mac control: they are a cross-surface event/plan coordinator, semantic document context beyond URL/title, plan-hash-bound approval receipts, and a bounded UART fixture collector with exit-status receipts. iPhone Mirroring pairing is still unresolved, and the pendant needs an explicit, safe approval-event design rather than overloading its existing buttons.

