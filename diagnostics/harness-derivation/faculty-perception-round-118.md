# Harness derivation — faculty-perception — round 118

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-device-observability** — GET /v1/devices/status is not implemented on the local agent (404). /ops/status currently reports mac bridge and Safari extension online, but accessibility=false and screenRecording=false; relay says pairingRequired=true and macBridgeOnline=true. /pipeline contains historical nrf9160 events, not proof of current registration.
  - evidence: Authenticated GET /v1/devices/status returned 404; GET /ops/status at 2026-08-07T17:54Z; GET /pipeline showed nrf9160 source event created 2026-08-07T07:22Z and relay result waiting for pendant.
- **mac-agent-perception-boundary** — The live Mac agent is not automation-ready for visual/UI perception: accessibility.trusted=false and screenRecording.granted=false, while AppleScript automation grants are present for System Events, Finder, Calendar, Mail, Notes, Messages, Safari, Chrome, Music and others. Browser extension is online with 3 Safari tabs, but its current tab is an example.com failure page.
  - evidence: Authenticated GET /ops/status at 2026-08-07T17:54Z returned permissions.accessibility.trusted=false, screenRecording.granted=false, browser online=true, tabCount=3, tabUrl=https://example.com, tabTitle='Failed to open page'.

## Capabilities it proposed

### "“Did you actually do that, or did it just look like it worked?”"
- **useful because:** The owner gets a single truthful chain—heard by pendant, accepted by relay, planned, executed on Mac/browser, and delivered back—rather than a stale 'completed' label. It explicitly calls out offline queues, approvals, and historical telemetry.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Cheap background/state reducer for the chain; realtime only for a spoken answer when asked.
- **latency:** Under 2 seconds when records exist; no model call for straightforward receipt joins.
- **cost:** <$0.001 per query; dominated by no model call, with occasional small summarizer call.
- **security:** Private action names and browser provenance stay in authenticated relay/Mac records; never expose page contents in the spoken summary without an explicit request. Require confirmation before treating an action as successful when its final device acknowledgement is absent.
- **missing:** Authoritative pendant registration plus delivery acknowledgements; A normalized cross-surface event schema linking relay job, Mac receipt, browser request, and pendant playback; A user-facing receipt query route

### "“When I’m about to leave, tell me the one thing I’ll regret forgetting—and let me confirm it hands-free.”"
- **useful because:** It combines the worn button/mic, always-awake relay, Mac calendar/reminders, and private browser tabs into a timely departure check instead of another periodic briefing. The pendant can ask one concise question, queue the answer while offline, and the Mac can prepare (but not send) the relevant item.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Cheap scheduled classifier/planner; realtime voice only for the short interactive confirmation.
- **latency:** Schedule evaluation under 5 seconds; spoken prompt starts within 1 second of a confirmed departure window.
- **cost:** <$0.01 per departure check; model cost is a small context classification, not audio generation unless prompted.
- **security:** Calendar, reminders, and logged-in tabs are sensitive. Select only whitelisted sources and transmit compact facts, not page bodies. Do not create/send messages or purchases; require explicit button/voice confirmation for any Mac action.
- **missing:** Departure-window signal (calendar/location or explicit 'I’m leaving' button event); A compact cross-surface context projection with freshness; Offline prompt/answer acknowledgement semantics on the pendant

### "“Give me a private, one-sentence debrief after every conversation I choose to capture, and turn only confirmed follow-ups into drafts.”"
- **useful because:** The pendant is the only surface that can capture a thought immediately after a conversation; the relay can retain it when the Mac is asleep, while Mac calendar/browser context grounds names and dates. The owner gets a reviewable debrief, not silent surveillance or automatic sending.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Background transcription and extraction on a cheaper model; realtime is reserved for the owner's short capture command and confirmation.
- **latency:** Acknowledge capture locally in under 300 ms; debrief within 60 seconds after relay/Mac connectivity returns.
- **cost:** <$0.03 per 2-minute capture; transcription and summarization dominate, with no cost when no capture is triggered.
- **security:** Recording is opt-in per button press and visibly marked; encrypt in transit/at rest, short retention, and provide immediate deletion. Never infer or contact third parties automatically; drafts require review and explicit approval.
- **missing:** A real connected pendant capture path and local recording indicator; Consent-aware capture metadata and retention/deletion controls; A grounded extraction-to-draft review queue with source snippets

### "“Tell me when my commitments disagree—calendar, reminders, and the logged-in page should not silently contradict each other.”"
- **useful because:** The owner gets an actionable warning when, for example, a calendar meeting moved but the private event page still shows the old time, or a reminder is due after an appointment was canceled. It reconciles sources instead of merely reporting each source separately.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → dashboard
- **model tier:** Cheap background normalization and contradiction classifier; realtime only to speak an urgent conflict.
- **latency:** Detect within 5 minutes of a source change; speak only high-confidence conflicts, otherwise place a cited card in the dashboard.
- **cost:** <$0.02 per monitored commitment per day; polling and extraction dominate, with small-model classification.
- **security:** Keep full private page contents on the Mac; send the relay only normalized dates, titles, and confidence. Never edit either source automatically. Require confirmation before proposing a calendar or reminder change.
- **missing:** Cross-source entity matching for calendar/reminder/browser records; Change notifications or bounded polling for private pages; A conflict notification channel with suppression and acknowledgement

### "“Before you use a private browser session or send anything through my Mac, tell me exactly what information is crossing between the pendant, relay, Mac, and browser—and let me approve just that scope.”"
- **useful because:** The owner can use the hive mind without an all-or-nothing privacy decision. A spoken approval such as “share the order number, not the address” becomes a machine-enforced data boundary across nodes.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic policy engine for classification and redaction; small model only for mapping natural-language scope to fields.
- **latency:** Under 500 ms for known fields; under 3 seconds for an ambiguous scope request.
- **cost:** <$0.005 per approval; mostly deterministic filtering.
- **security:** The policy engine must run before logging, upload, or browser action; default deny on unknown fields; approvals expire per task and are auditable. Audio approvals should require a nonce or button confirmation for consequential actions.
- **missing:** Typed sensitivity labels on Mac/browser/pendant payload fields; A preflight data-flow preview and scoped approval token; Redaction enforcement at every relay and browser boundary

### "“If I lose connectivity halfway through a task, resume from the exact safe point when any node comes back—without repeating or silently skipping a step.”"
- **useful because:** The owner can start a multi-surface task from the pendant, walk away from Wi-Fi/LTE, and return to a trustworthy continuation: already-completed steps are not repeated, irreversible steps are held for approval, and the pendant gives a concise recovery summary.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Cheap durable workflow state machine and deterministic retry logic; use the expensive realtime model only for a spoken explanation or ambiguity.
- **latency:** Local offline acknowledgement under 300 ms; resume within 10 seconds of a node heartbeat; explanation under 2 seconds when requested.
- **cost:** <$0.01 per resumed task; storage and retries dominate, not model inference.
- **security:** Persist only task state and redacted parameters; encrypt queued work; expire authorization while offline; never retry sends, purchases, or deletes without a fresh confirmation.
- **missing:** A durable cross-node workflow state machine with idempotent step keys; Heartbeat/reconnect events from pendant, relay, Mac, and browser; A safe-point definition and approval renewal protocol


## Changes it proposed to its own stack

### `firmware` — Implement a capture transaction protocol on the nRF9160: button press creates a local sequence number, starts a visible/audio-marked capture, writes chunks plus a manifest to microSD, and emits uploaded/accepted/processed/deleted acknowledgements with retry-safe sequence IDs when LTE returns.
- **owner gets:** A pressed button means a capture truly exists and can be recovered later—even when the pendant is offline—rather than producing an untraceable promise.
- effort: High: firmware state machine, SD power-fail recovery, relay idempotency, and end-to-end tests over USB/J-Link.  ·  risk: SD wear, battery drain, and privacy exposure; recover with bounded chunk size, retention limits, encryption, and a long-press cancel/delete path.
- cost: No API model cost; modest flash/SD writes and LTE upload power draw.  ·  latency: Local acknowledgement under 300 ms; cloud processing deferred until connectivity.
- security: Opt-in recording indicator, encrypted-at-rest chunks, and no upload without explicit capture state.
- depends on: Live pendant registration; Relay delivery acknowledgements; Owner-approved retention policy

### `relay` — Create a departure-window coordinator that consumes calendar/reminder facts and an explicit pendant 'leaving' event, computes one high-confidence missing-item prompt, and delivers exactly-once prompt/answer transactions. It should never infer location from stale history and should expire unanswered prompts.
- **owner gets:** The pendant asks one useful question at the moment it matters, without becoming a noisy notification stream or repeating an already answered prompt.
- effort: Medium: event consumer, compact context selector, dedupe/expiry state, and Mac/browser adapters for preparing reversible drafts.  ·  risk: Wrong timing or sensitive prompt; recover with explicit trigger first, confidence threshold, quiet hours, and dashboard snooze/delete.
- cost: Low background inference cost, typically <$0.01 per departure event.  ·  latency: Prompt delivery target under 1 second after explicit event; scheduled checks can be slower.
- security: Only send minimal fact labels to the pendant; keep source details on Mac/relay and require confirmation before any action.
- depends on: Authoritative timezone and calendar freshness; Pendant event acknowledgements; Cross-surface context projection


## What it asked for

_Nothing._
## Its own summary

Established fresh live facts: /v1/devices/status is absent on this agent; /ops/status shows the Mac bridge and Safari extension online, relay reachable, but Accessibility and Screen Recording are still false. The browser currently reports 3 Safari tabs with the active tab at a failed example.com page. /pipeline includes nrf9160 and 24-kHz playback records, but those are historical events and cannot establish current pendant presence. I recorded these boundaries. Proposed three new owner capabilities: end-to-end truthful request status, a departure-time single-item check, and opt-in capture-to-debrief with review-only drafts. The first integration change (a cross-surface evidence ledger) collided with an existing ledger proposal and was correctly not restated. Two non-colliding changes were recorded: offline-safe pendant capture transactions and exactly-once departure prompts.

**Biggest unknown:** The authoritative current pendant registry and delivery acknowledgements remain unavailable: the local agent has no /v1/devices/status route, and historical pipeline events conflict with any claim of present registration. I still need a live USB/firmware identity plus relay registration/heartbeat/playback acknowledgements before recording the pendant as connected or validating offline capture end to end. For visual Mac perception, the owner still must grant Accessibility and Screen Recording to com.aipendant.agent; AppleScript/browser paths remain usable without them.

