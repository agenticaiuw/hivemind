# Harness derivation — relay-realtime — round 146

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Check my browser tabs for anything important and read me the highlights.”"
- **useful because:** It’s a quick situational brief you can request while walking. The system can summarize current work context without the owner opening a laptop.
- **path:** pendant → relay → browser → mac-bridge → relay
- **model tier:** Use the browser harness for page access; summarization can run on a cheaper model. Realtime only speaks the summary.
- **latency:** A few seconds for collection; summary should stream back as it’s ready.
- **cost:** Dominated by browser page reads and summarization tokens.
- **security:** Only access already-open tabs or explicitly approved sessions. Cite sources and avoid leaking private content beyond the summary.
- **missing:** Either functioning server-side browser actions or robust browser session access via the Mac.; Consistent tab/session affinity and typed results (a previously noted defect).

### "“Tell me what’s going on with my devices right now.”"
- **useful because:** When something feels off, a single voice check can report what’s online, what’s asleep, and whether the bridge and browser are reachable.
- **path:** pendant → relay → mac-bridge → browser → relay
- **model tier:** Realtime is fine; it’s mostly status reads and a spoken response.
- **latency:** Under a second if status is cached; a few seconds if probing is needed.
- **cost:** Very low; mostly lightweight status calls.
- **security:** Status only; no content. Don’t expose sensitive identifiers.
- **missing:** A stable device status endpoint that’s confirmed live (previous attempts at /v1/devices/status were absent).; Presence/sequence state to avoid confusing stale last-seen with current availability.

### "“When I say ‘make this safe,’ use the pendant as my physical presence signal: immediately mute Mac microphones, pause recording/streaming apps, hide or lock authenticated browser tabs, and tell me what was changed; when I return and press the button, restore only the state you recorded.”"
- **useful because:** A worn, always-available control is the one surface that can react when the owner notices a privacy risk, even away from the Mac. It turns the pendant into a practical emergency privacy switch rather than another voice remote.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → browser → dashboard
- **model tier:** Realtime relay handles the short intent and confirmation speech; deterministic Mac/browser executors perform the state snapshot and reversible changes. No expensive model is needed for the actual safety action.
- **latency:** Start muting and tab isolation within 2 seconds of the utterance; spoken acknowledgement within 4 seconds. Restoration can take up to 10 seconds.
- **cost:** Usually one short realtime turn (about $0.01–$0.05 depending on audio duration); execution is dominated by Mac/browser round trips, not inference.
- **security:** The pendant credential becomes a physical privacy token, so replay protection, device sequence numbers, and an append-only before/after receipt are required. Never expose tab contents in the spoken acknowledgement or logs. Restore must be limited to the exact recorded resources and tolerate apps having been changed manually.
- **missing:** A relay-to-Mac emergency command with priority over queued work; Mac adapters for microphone/recording state snapshots and reversible pause/lock operations; Browser extension support for bulk authenticated-tab isolation and exact restoration; Pendant presence/sequence and button-event authentication; A durable encrypted restoration receipt and an owner-visible recovery screen

### "“While I was away, tell me exactly what changed on my Mac and in my open browser sessions, grouped by project, with links and a one-sentence reason for each change.”"
- **useful because:** The owner can leave the computer unattended without losing situational awareness. This is not merely job status: it reconstructs a trustworthy, project-grouped change narrative from Mac action receipts, browser mutations, and the relay's voice history, then lets the owner ask follow-up questions hands-free.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** A cheap background summarizer builds the diff after each receipt; realtime is used only to answer the owner's spoken query and read a compact result.
- **latency:** Precompute incrementally after each action; spoken answer in under 3 seconds, with deeper drill-down under 8 seconds.
- **cost:** One small background summarization per changed batch, roughly $0.01–$0.08/day for normal use; realtime query cost roughly $0.01–$0.03.
- **security:** The report must distinguish observed facts from model inference, preserve source links and timestamps, redact secrets and page contents from audio, and never claim a change without a receipt or browser inspection. Retain only hashes and short summaries by default.
- **missing:** A durable cross-surface event ledger joining Mac receipts, browser request IDs, pendant sessions, and project labels; A browser mutation observer that records typed outcomes rather than only current inspections; Incremental background summarization (currently there is no scheduler or worker); Relay query endpoint that streams cited, bounded results to the pendant; A project-label resolver and dashboard timeline with source drill-down

### "“Turn the open project page into a ready-to-review decision packet: extract the relevant facts from my authenticated browser tabs, compare them with the project files on my Mac and my calendar, draft the reply and a proposed follow-up task, and read me only the conflicts or missing facts.”"
- **useful because:** Today each surface can inspect one silo, but the owner still has to manually reconcile web evidence, local files, calendar commitments, and communication. This produces a reviewable packet without sending or committing anything, so the owner can make a decision from the pendant while away from the desk.
- **path:** pendant → relay → browser-extension → browser → mac-planner → mac-terminal → dashboard
- **model tier:** Use a slower background planner for extraction, comparison, and draft generation; realtime only captures the request and speaks the concise conflicts summary. Deterministic adapters provide citations and calendar/file facts.
- **latency:** Acknowledge immediately; packet in 30–90 seconds for four tabs and a modest project folder, with progress updates if it exceeds 10 seconds.
- **cost:** Roughly $0.05–$0.30 per packet, dominated by document extraction and the planner context; subsequent spoken follow-ups are pennies.
- **security:** Authenticated page and local-file contents cross the relay, so encrypt in transit, minimize retained content, attach source citations, and make the packet private to the paired pendant. Drafting is reversible; sending, editing files, or creating calendar events must remain separate explicit actions.
- **missing:** A single job type that can fan out to browser and Mac reads and then join typed results; Bounded project-folder and calendar readers with citations; Conflict detection for dates, quantities, and contradictory facts; An artifact store for draft reply/task plus provenance and expiration; Pendant-accessible packet retrieval and a separate execute-draft action


## Changes it proposed to its own stack

### `integration` — Add presence-aware session handoff: relay tracks device availability and last successful step, then resumes on another surface (Mac, browser, relay) when one goes offline.
- **owner gets:** Tasks don’t die when the Mac sleeps or the pendant disconnects. The system continues from where it left off, or tells the owner what’s blocking.
- effort: High: needs shared state, idempotent steps, and resumable workflows.  ·  risk: State divergence between surfaces. Mitigate with receipts, job IDs, and explicit step checkpoints.
- cost: Moderate; includes state storage and additional coordination calls.  ·  latency: Adds small overhead to coordination; improves perceived reliability.
- security: Shared state must be access-controlled; store only what’s necessary.
- depends on: Durable job runner or equivalent resumable workflow support; Presence/sequence tracking across relay and Mac

### `hardware` — On the pendant, add a low-power ‘task heartbeat’ LED pattern and a single-button status query: short press asks relay for the current job status and speaks a brief update if the audio path is available.
- **owner gets:** The owner gets immediate reassurance without opening anything: heartbeat means ‘working’, solid means ‘waiting’, quick press gets a spoken status.
- effort: Medium: firmware skill, relay endpoint, and a tiny status protocol.  ·  risk: LED meanings could confuse; keep patterns minimal and documented. Audio path failures must fall back to LED only.
- cost: Low; minor firmware work and negligible power if implemented as brief periodic blink.  ·  latency: Instant visual feedback; status query depends on relay reachability.
- security: No sensitive content; status only.
- depends on: Device skill for button-to-status request; A relay endpoint to answer status from job records

### `hardware` — Add a tiny low-power vibration motor and driver to the pendant, with firmware patterns for acknowledgement, urgent result, failure, and incoming completion. Expose a relay command that can request a pattern with a correlation id, and queue at most one completion pattern while the link is down.
- **owner gets:** The owner can know that a spoken request completed or failed without staring at the pendant or keeping audio enabled. This makes unattended, pocketed, or noisy use dependable and gives the wearable a private notification channel instead of relying on the single LED.
- effort: Moderate hardware revision and enclosure change: motor, transistor/driver, flyback protection, firmware PWM pattern table, and relay delivery semantics. Prototype can be wired onto the currently USB-connected nRF9160 pendant before a board revision.  ·  risk: Added vibration and current spikes could reset the modem or shorten battery life; rate-limit patterns, budget peak current, and fall back to LED/audio. A stuck driver needs thermal/current protection. Recovery is firmware-safe default-off and a physical disconnect option.
- cost: Approximately $1–$3 in components and under 20 mA peak while vibrating; negligible API cost because patterns are tiny events.  ·  latency: Local acknowledgement under 100 ms when USB/LTE link is live; queued completion may be delayed until reconnect.
- security: Patterns must not encode sensitive content; only generic states and opaque correlation ids should cross the device link.
- depends on: A reliable pendant event/push transport over the present USB serial connection; Firmware event queue and modem/USB power-budget measurement; Relay correlation of long-running Mac/browser jobs to device notifications


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities and one hardware change: a physical pendant privacy lockdown/precise restoration flow; a cited, project-grouped “what changed while I was away?” narrative; a browser+Mac+calendar decision packet with drafts and conflict-only spoken review; and a vibration notification channel for silent completion/failure feedback. The main missing pieces are cross-surface event/provenance joining, priority relay delivery, browser mutation logging, durable packet/restore artifacts, and a verified pendant push/event transport. The recorder flagged the first, third, and hardware ideas as somewhat close to existing work, but accepted all four; I did not re-submit them.

**Biggest unknown:** Whether the relay already has an unobserved durable event ledger, pendant push endpoint, or background worker that could reduce the listed implementation gaps; this round explicitly prohibited further discovery.

