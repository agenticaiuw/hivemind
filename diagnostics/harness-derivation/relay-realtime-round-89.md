# Harness derivation — relay-realtime — round 89

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Save this for me” — while I am looking at something in my authenticated browser, capture the exact page/selection, my spoken reason, and enough context that I can ask about it later from the pendant."
- **useful because:** Today the pendant can hear a request and the browser can act, but there is no durable, cross-surface bookmark that preserves what the owner meant about a private page. This turns fleeting voice-plus-browser context into a retrievable personal reference without requiring the owner to stop and copy URLs or notes.
- **path:** pendant → relay → browser → mac-planner → dashboard
- **model tier:** Realtime for the short spoken intent and confirmation-free capture; a cheaper background model can normalize the rationale, title, and tags after capture. Retrieval should use the cheaper model unless the owner asks a conversational follow-up.
- **latency:** Acknowledge capture in under 1 second; browser metadata and selected text may arrive within 3 seconds. Later spoken lookup should respond in under 2 seconds for indexed bookmarks.
- **cost:** Small realtime utterance plus one metadata extraction per save; roughly cents or less per capture depending on page text size. Storage/indexing dominates recurring cost, not inference.
- **security:** Authenticated page URL, title, selection, and rationale leave the browser/owner device and enter relay storage; page bodies must not be copied by default. Encrypt at rest, redact tokens/password fields, retain only the selected text and explicit metadata, and make deletion available by voice. Saving is reversible and should not require confirmation, but the spoken acknowledgment must say what was captured.
- **missing:** A browser-extension endpoint that atomically returns the active tab's URL/title/selection and a stable browser-session reference; A relay durable bookmark store with per-owner encryption, retention/deletion, and full-text or embedding retrieval; A browser-to-relay correlation ID so a spoken 'this' resolves to the tab active at utterance time rather than a later tab; A pendant retrieval intent that can search these bookmarks and cite the original page/session without exposing private page contents unnecessarily

### "“I’m driving” — put every non-urgent Mac/browser task into a safe hold, suppress non-urgent spoken/tactile alerts, and let me ask only brief status questions until I say “I’m stopped.” Then resume the held work without losing its browser session or action receipt."
- **useful because:** The pendant is worn away from the Mac, so an owner can start a task before traveling and unexpectedly receive distracting output or have an unattended workflow continue while driving. A single spoken mode should coordinate the relay, Mac planner, and authenticated browser rather than relying on separate app settings.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only classifies the two short mode commands and urgent-vs-nonurgent status. A deterministic relay policy and downstream agents do the pausing; no expensive model should be called for routine suppression/resumption.
- **latency:** Enter driving mode and silence queued nonurgent output within 500 ms at the relay; downstream agents should checkpoint or pause within 2 seconds. Status answers should be a single short spoken sentence in under 1.5 seconds.
- **cost:** Near-zero incremental inference cost after intent classification. Durable checkpoint and event storage are the main implementation cost; replaying a held job later may incur the normal planner/browser inference cost.
- **security:** Pausing is safer than silently abandoning work, but resumption can cause deferred external mutations. Every held job needs a checkpoint, expiry, and a clear spoken summary; never replay a mutation that lost its receipt or changed browser context. The mode state is sensitive presence/safety metadata and should be encrypted and excluded from routine logs.
- **missing:** A relay-wide foreground mode with durable owner state and an urgent-only event filter; Pause/checkpoint/resume semantics in Mac planner jobs and browser-extension command queues, including session/context invalidation handling; A small, deterministic urgent-status summary endpoint usable while all other model work is suppressed; A resume report that lists held, expired, failed, and safely continued jobs


## Changes it proposed to its own stack

### `integration` — Add a cross-surface “handoff receipt” protocol: whenever the relay delegates a multi-step task to mac-planner (or a browser workflow), it stores a compact, stable receipt containing the goal, target, correlation id, and a human-sized spoken status template. mac-planner writes progress updates and final receipts back to the same record. relay_job_status reads it. This defines a single source of truth for “what happened,” without inventing per-tool status hacks.
- **owner gets:** The owner can ask “what happened to that?” and get a consistent answer, even if they spoke, walked away, and the Mac finished later. It feels reliable and reduces repeated explanations.
- effort: Medium: define a receipt schema, add write points in relay and mac-planner, and ensure idempotent updates.  ·  risk: Schema drift between relay and Mac could break status. Mitigate with versioned receipts and strict validation; fall back to generic status if fields are missing.
- cost: Low storage and compute; dominated by Mac-side work, not status plumbing.  ·  latency: Improves perceived latency: status is local to relay storage and avoids unnecessary downstream calls.
- security: Receipts may contain sensitive task text. Store only what’s needed, redact content, and avoid logging full utterances when a reference will do.
- depends on: Implementations in relay and mac-planner; durable job runner still absent, so receipts must not assume it exists.

### `hardware` — Add a coin-ERM or LRA vibration motor with a dedicated low-side driver and local duty-cycle limiter to the nRF9160 pendant, exposing three short tactile patterns (acknowledgment, ordinary completion, urgent exception) to relay-originated notifications. Keep the existing button/LED path as fallback and require the firmware to drop non-urgent patterns when battery voltage is low.
- **owner gets:** The owner can be away from the Mac and in a noisy or socially inappropriate setting yet still know that a long-running browser/Mac task finished or needs attention. They can distinguish a harmless completion from an urgent failure without taking out the phone or speaking aloud.
- effort: Moderate hardware spin plus firmware notification protocol, battery characterization, enclosure/comfort validation, and relay delivery acknowledgments. The Mac and browser agents need to classify their existing receipts/events into the three patterns; no new conversational model is required.  ·  risk: Added vibration and RF/power noise could reduce battery life or be uncomfortable. Limit pulse duration, rate-limit notifications, test brownout behavior, and preserve LED/audio fallback. If the relay is unreachable, no false tactile event should be emitted; queued events must expire rather than arrive stale.
- cost: Approximately $2–$6 in added components/assembly at prototype volume, plus PCB/enclosure revision. Roughly 10–60 mW while vibrating for short pulses; negligible idle draw if the driver is fully disabled. API cost is negligible; routing existing receipts/events dominates no inference spend.  ·  latency: Near-real-time notification becomes possible once an upstream receipt/event is emitted; target under 2 seconds end to end. Firmware pulse generation is immediate and does not add speech latency.
- security: A vibration can reveal that a task exists to someone holding or touching the pendant, so only coarse urgency should be encoded; never encode private content. Authenticate relay-originated notifications and include expiry/request IDs to prevent replay.
- depends on: A durable relay notification/event channel that can deliver Mac and browser job receipts to the pendant while the owner is not speaking; Typed notification severity and expiry fields on existing job/action receipts; Pendant firmware update and battery telemetry support


## What it asked for

_Nothing._
## Its own summary

Recorded three concrete gaps: a browser-context bookmark that preserves the owner's spoken rationale, a tactile notification channel for unattended Mac/browser outcomes, and a cross-surface driving mode that checkpoints and suppresses non-urgent work. The required changes are durable relay storage/correlation, browser context capture, a pendant hardware/firmware revision, and pause/resume semantics across Mac and browser jobs.

**Biggest unknown:** The backlog similarity checks flagged all three as adjacent to prior ideas, especially tactile alerts and owner-controlled modes. I could not inspect further this round as instructed, so the remaining uncertainty is whether an existing backlog item already covers one of these exact end-to-end contracts.

