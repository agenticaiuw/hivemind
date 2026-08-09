# Harness derivation — mac-planner — round 244

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-accessibility-status** — The live Mac observe endpoint reports AI Pendant Agent Accessibility trusted, synthesized events posting successfully, Screen Recording true, secure input false, and UI actions will reach the screen. Foreground app is Claude; Safari session inventory is online with four browser sessions reported.
  - evidence: mac_readonly_inspect operation=running_apps and foreground_app both invoked GET /observe at 2026-08-08T23:51:53Z; response accessibility.trusted=true, screenRecording=true, inputReachability.status=verified.

## Capabilities it proposed

### "“Don't interrupt me while I'm in a meeting, but make sure I hear anything genuinely urgent.”"
- **useful because:** The pendant's inbox already survives link loss, but it cannot know whether an alert should break through right now. The relay can combine Calendar's current event, the Mac's foreground/full-screen state, and alert urgency: defer normal alerts, deliver urgent ones immediately, then speak a concise catch-up when the meeting ends. This is a real closed loop across pendant, relay, and Mac rather than another inbox.
- **path:** relay-realtime → mac-planner → pendant
- **model tier:** background for calendar/context classification; realtime only for the short spoken alert and owner reply
- **latency:** Urgent alert decision under 2 seconds; meeting-end catch-up within 30 seconds of Calendar/Mac state changing.
- **cost:** ~$0.01–0.04 per alert batch; most work is local Calendar/foreground reads, with model tokens only for ranking and compression.
- **security:** Calendar titles and foreground-app names leave the Mac only as minimized structured metadata. Never transmit meeting body or window contents by default. Owner must explicitly configure which urgency classes may interrupt; otherwise queue everything.
- **missing:** A relay scheduler/event trigger that reevaluates queued alerts when Calendar transitions or foreground state changes; A small Mac read route for full-screen/Do-Not-Disturb and current meeting state (foreground app alone is insufficient); An urgency and expiry schema added to the existing offline_alert_inbox rather than a second queue

### "“Finish this task across my browser and Mac, and don't tell me it's done unless you can prove what changed.”"
- **useful because:** Today a plan can execute actions and a workbench can atomically write files, but the owner still has to trust a vague completion message. This capability returns a compact, inspectable proof: before/after browser URL and title, file hashes, app actions, and any failed step, then speaks the receipt through the pendant. Retries use one job ID so a dropped link cannot duplicate the work.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → unified
- **model tier:** background model for decomposition and receipt summarization; realtime only when the owner asks a follow-up
- **latency:** Preflight under 3 seconds; ordinary desktop task under 20 seconds; receipt delivered as soon as the final verification arrives.
- **cost:** ~$0.02–0.08 per task; dominated by planning/verification tokens, not local hashes or route calls.
- **security:** Receipts must redact page text, tokens, and file contents, exposing hashes, paths, titles, and action outcomes only. Mutations use the owner's runtime policy; no silent expansion from a failed step to a new destructive plan. Browser sessions remain on-device.
- **missing:** A single cross-surface receipt schema joining browser command IDs, Mac action results, and workbench receipts under one job ID; A read-only postcondition verifier for browser DOM/state and selected Mac app state; Pendant delivery of structured completion/failure receipts, not just generated audio

### "“Tell me exactly what information left my Mac, browser, pendant, and relay today—and let me revoke or erase any item.”"
- **useful because:** The owner currently has no user-facing answer to the most important trust question: what this hive actually transmitted. This would produce a per-event data-flow ledger with source surface, destination, fields, purpose, retention deadline, and redaction status, then let the owner revoke future delivery or erase eligible retained copies. It is different from execution receipts: it audits information movement, not whether an action succeeded.
- **path:** unified → relay-realtime → mac-planner → browser-extension → pendant
- **model tier:** background model for grouping and plain-language explanation; deterministic logging and redaction must happen without a model
- **latency:** Live event ledger within 5 seconds; daily digest under 30 seconds; revocation acknowledgement under 2 seconds when nodes are online.
- **cost:** ~$0.01–0.03 per daily digest; raw event recording is local/structured and cheap, with model use only for summarization.
- **security:** The ledger itself is sensitive and must be encrypted, locally redacted, and partitioned by surface. Erasure must delete payloads, derived summaries, and cached audio where technically possible, while retaining only a minimal tombstone. A disconnected pendant must show revocation as pending rather than falsely claiming completion.
- **missing:** A mandatory data-egress event envelope emitted by Mac, browser, relay, and pendant paths; A retention/erasure controller that reaches offline nodes and reports per-node completion; Owner-facing ledger and revocation routes with field-level redaction

### "“If the relay or Wi‑Fi drops while I’m talking, keep the conversation going and reconcile it when the link returns—without answering twice.”"
- **useful because:** The current offline mechanisms preserve bookmarks and audio chunks, but they do not preserve conversational state. A dropped call loses turn order, pending intent, and whether a response was already generated. A partition-tolerant session would let the pendant and Mac buffer bounded turns, assign causal sequence IDs, optionally continue with a local low-cost model, and merge one canonical transcript/answer after reconnection.
- **path:** pendant → mac-planner → relay-realtime → unified
- **model tier:** local/cheap model for degraded-mode short replies; realtime model only for reconciliation and normal connected turns
- **latency:** Local degraded reply under 3 seconds; reconnection reconciliation under 10 seconds; no duplicate spoken response after merge.
- **cost:** ~$0.01–0.06 per interrupted session; bounded transcript reconciliation dominates, with local buffering otherwise free.
- **security:** Keep the partition buffer encrypted and bounded in RAM or the existing failure buffer, expire it after the session, and never upload duplicate raw microphone content. The canonical merge must expose uncertainty instead of silently rewriting what the owner said.
- **missing:** A causal turn/session protocol shared by pendant, Mac, and relay; A bounded local degraded-mode speech/intent path on the Mac or pendant; An idempotent response ledger that marks audio as spoken, queued, or superseded; A merge endpoint that accepts sequence ranges and returns one canonical continuation

### "“Find commitments I’ve made that conflict with each other, explain the collision, and prepare the smallest set of changes to fix it.”"
- **useful because:** A normal briefing lists events and unread mail separately; it does not connect “I promised delivery Friday” in Mail, a Calendar meeting occupying the same time, and a browser task or document deadline. This capability would surface only genuine cross-source contradictions, rank them by consequence, and prepare concrete reschedules or reply drafts for the owner instead of making silent changes.
- **path:** relay-realtime → mac_read_sources → mac-planner → browser-extension → pendant
- **model tier:** background model for extracting commitments and resolving ambiguity; realtime only to answer the owner's short follow-up
- **latency:** Overnight scan under 2 minutes; on-demand result under 15 seconds; spoken collision alert under 3 seconds after a newly observed high-confidence conflict.
- **cost:** ~$0.05–0.20 per daily scan depending on mail volume; deterministic date extraction and deduplication should precede model calls.
- **security:** Process Mail snippets locally where possible and redact people, topics, and quoted content from relay telemetry. Never send, reschedule, or cancel automatically. Every proposed change must cite its source messages/events and preserve the owner's original commitments.
- **missing:** A durable commitment data model linking Calendar events, Mail promises, browser tasks, and pendant bookmarks; A source-citation extractor that retains offsets/IDs without retaining unnecessary bodies; A planner that can generate reversible change sets and let the owner apply selected items through Mac/browser actions


## Changes it proposed to its own stack

### `integration` — Add a USB-bench health gate for the currently attached nRF9160 and ESP32: on device attach, before the first call of the day, or on explicit “check my pendant”, the Mac runs the existing bounded diagnostic fixture procedure, captures the serial log, parses encode/decode time, packet drops, underruns and fixture completion, and publishes a signed pass/fail snapshot to the relay. It must never become a normal product transport; this is a bench-test path only.
- **owner gets:** The owner learns before speaking whether today's actual pendant/audio chain is healthy, instead of discovering a dead microphone or distorted playback during a live conversation. A failure can be spoken and placed in the Mac log with the exact failing metric and suggested recovery.
- effort: Medium: launch/attach detection, a narrow allowlisted diagnostic command, parser, relay health endpoint, and a small dashboard/briefing card. Reuse the shipped audio_path_diagnostic_fixture; do not invent another firmware test.  ·  risk: USB reconnects and partial logs can yield false failures; require fixture completion and sequence continuity, mark unknown rather than pass, and retain the raw log locally for troubleshooting. Never auto-flash firmware or alter device state from this gate.
- cost: Negligible API cost; one short local model-free parse. No hardware cost or extra power beyond the existing USB bench connection.  ·  latency: About 5–20 seconds before a call, depending on the fixture; never run in the middle of an active call.
- security: Serial output may contain identifiers and diagnostics, so redact before relay publication. Keep raw logs on the Mac and publish metrics only.
- depends on: audio_path_diagnostic_fixture; t22-ib1b mac_usb_serial_diagnostics; POST /pipeline/events; GET /health; A bounded allowlisted run_shell procedure for the two known USB serial devices


## What it asked for

_Nothing._
