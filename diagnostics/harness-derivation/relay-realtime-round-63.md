# Harness derivation — relay-realtime — round 63

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’m away from my Mac. When it becomes available, inspect the authenticated browser tab I’m looking at, compare it with the relevant files on my Mac, and tell me only what changed; if something needs action, prepare it but don’t do it until I say ‘go.’ Keep the task alive if either device disconnects.”"
- **useful because:** Today the pendant can start a conversation, but it cannot maintain one coherent, resumable investigation across an unavailable Mac and an authenticated browser session. This would let the owner delegate a real-world task while walking away, receive a compact spoken delta when the machines are reachable, and approve prepared work without losing context or accidentally retrying after a disconnect.
- **path:** pendant → relay → browser-extension → mac-planner → mac-vision → dashboard
- **model tier:** Realtime only handles the initial utterance, clarification, and final spoken summary. A cheaper background model performs change extraction and comparison; mac-planner produces a typed dry-run plan; mac-vision is used only for visual pages the extension cannot expose.
- **latency:** Acknowledge the request on the pendant in under 1 second. Resume opportunistically when both surfaces heartbeat; deliver the first useful delta within 30 seconds of availability. Reconnects must resume from a checkpoint rather than replaying actions.
- **cost:** Roughly $0.01–$0.08 per investigation depending on page/file volume; the dominant cost is background comparison and any vision fallback, not the short realtime turns. Browser and Mac transfer should be hashes/excerpts by default, not entire documents.
- **security:** Authenticated page contents and selected Mac files leave their local surfaces for relay comparison, so the task needs explicit scope (tab, folders, retention and expiry) and encrypted, per-task storage. Prepared mutations remain a visible dry-run until the owner says ‘go’; disconnects, stale tabs, changed file hashes, and duplicate delivery must never cause execution. The pendant needs a short spoken task identifier and a one-button cancel.
- **missing:** A durable cross-surface task record with checkpoints, leases, expiry, and idempotency keys; A browser watcher API that can snapshot an already-authenticated tab and report meaningful changes without scraping unrelated tabs; A Mac file-selection/read adapter that returns content hashes plus bounded excerpts and a planner dry-run; Relay orchestration that waits for both heartbeats, merges typed evidence with citations, and resumes after disconnects; A pendant notification/acknowledgement path for completed deltas, cancellation, and stale or blocked tasks; Dashboard controls for task scope, retention, pending plan, and audit trail

### "“Why did you say that? Read me the exact evidence, where it came from, and what you inferred versus what you actually observed.”"
- **useful because:** A spoken answer assembled from a browser session and Mac files is hard to trust or correct when the owner is away from a screen. The owner should be able to audit an answer hands-free, distinguish observation from inference, and stop a downstream action if the evidence is stale or wrong.
- **path:** pendant → relay → browser-extension → mac-planner → mac-vision → dashboard
- **model tier:** Realtime handles the short spoken audit dialogue. A cheaper background model builds a structured evidence ledger; no vision call is made unless the cited browser evidence came only from pixels.
- **latency:** Start reading the provenance in under 1.5 seconds, then stream one evidence item at a time. Fetching a missing citation may take up to 10 seconds, with an explicit spoken status rather than silence.
- **cost:** About $0.005–$0.03 per audit; storage and retrieval dominate more than model tokens. Keep compact excerpts, hashes, timestamps, and source locators rather than raw page/file copies.
- **security:** Evidence may contain private browser and Mac data. Store only task-scoped excerpts encrypted with short retention, redact secrets before spoken playback, and require a spoken confirmation before revealing likely credentials, tokens, or sensitive personal data aloud. Every inference must carry an uncertainty label and source timestamp.
- **missing:** An immutable evidence ledger shared by relay, browser, and Mac with observation/inference distinction; Stable browser locators and Mac file offsets that remain auditable after a tab or file changes; A relay spoken-audit protocol supporting follow-up questions without re-running the original task; Automatic secret/PII redaction before pendant playback; A dashboard view showing the evidence chain and allowing the owner to mark a citation incorrect


## Changes it proposed to its own stack

### `hardware` — Add a low-power vibration actuator and a capacitive touch strip to the pendant, with firmware events exposed to relay task leases: distinct short patterns for acknowledged, waiting-for-device, prepared-for-approval, completed, stale, and cancelled; a deliberate press-and-hold on the strip cancels the current task. Keep the existing button as the wake/voice control and make haptics local so they work during a dropped LTE link.
- **owner gets:** The owner can understand whether an away-from-Mac request is progressing, blocked, or ready for approval without taking out a phone or hearing an announcement in a noisy room. A reliable local cancel gesture prevents a stale queued action from continuing when speech is inconvenient.
- effort: Moderate hardware revision, enclosure and waterproofing work, a small firmware event/state machine, and relay mapping for leases and acknowledgements. Add factory tests for false touches and haptic patterns.  ·  risk: Vibration consumes power and can be mistaken for an alert; touch can false-trigger from clothing or rain. Require a long deliberate gesture for cancellation, debounce locally, and fall back to the existing LED/button when the actuator fails. Firmware OTA rollback is required.
- cost: Approximately $1–$4 in components and assembly at prototype volume; roughly 5–20 mW only while vibrating, negligible idle draw. No meaningful per-request API cost.  ·  latency: Local acknowledgement/cancel feedback under 100 ms; no network round trip. Relay task state still depends on heartbeats, but the pendant can honestly signal offline/stale.
- security: A physical cancel path reduces risk from unattended queued work. Touch events must not be accepted as approval for high-impact actions; approval remains an explicit spoken command or existing policy.
- depends on: A durable relay task lease/checkpoint protocol; Firmware OTA and local event delivery; A relay-to-pendant notification channel that survives transient LTE loss


## What it asked for

_Nothing._
## Its own summary

Recorded three new items: a resumable cross-surface authenticated-browser/Mac comparison with dry-run approval, a spoken provenance/audit trail distinguishing observations from inferences, and a hardware revision adding haptic/touch state and local cancellation. Each names the missing relay, browser, Mac, firmware, and dashboard work rather than pretending today’s stack can provide it.

**Biggest unknown:** Whether the existing unlisted backlog already contains an equivalent durable cross-surface watch or evidence-ledger implementation; I was instructed not to discover further this round, so I treated these as new and specified their differentiators.

