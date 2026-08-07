# Harness derivation — faculty-judgement — round 61

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **current cross-surface reachability** — At 11:59Z relay and Mac bridge are online, but the running AI Pendant Agent still has Accessibility=false, Screen Recording=false, inputReachability=failed, and uiActionsWillReachTheScreen=false; browser extension is offline with 5 pending commands. AppleScript automation grants remain available. Pendant pipeline shows offline-held alerts and bookmarks, plus a 24 kHz PCM response path.
  - evidence: GET /observe, GET /ops/status, GET /browser/status, GET /pipeline at 2026-08-07T11:59:40Z

## Capabilities it proposed

### "“Before you act, tell me what you can actually reach right now, what is stale or offline, and whether the result will be verified. If a surface drops out, keep the request safe and tell me what remains.”"
- **useful because:** The owner currently gets plausible success even when UI input cannot reach the screen, while the browser bridge can be offline with queued commands. This turns raw diagnostics into a dependable decision: use a granted AppleScript route, queue work, ask for confirmation, or refuse to claim completion. It is especially valuable from the pendant, where the owner cannot inspect dashboards.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Cheap background/state model compiles the reachability snapshot and freshness/confidence; realtime is used only for the short spoken verdict and any owner clarification. No expensive reasoning is needed unless the requested action is ambiguous.
- **latency:** Under 1 second for cached status; under 3 seconds for a fresh probe. The owner hears one sentence plus an optional actionable fallback.
- **cost:** Near-zero model cost for typed status evaluation; occasional realtime token cost for the spoken explanation. Dominant cost is a fresh Mac/bridge probe, not inference.
- **security:** Expose capability classes and freshness, not bearer tokens, private URLs, or secret memory. Never imply an action succeeded from a local receipt when uiActionsWillReachTheScreen=false. Any fallback that sends, deletes, purchases, or changes external state still requires the owner's existing confirmation policy.
- **missing:** A unified typed reachability witness joining /observe, /ops/status, /browser/status, relay status, and recent /pipeline or /jobs receipts with one timestamp/confidence/expiry per claim; A pre-action gate that consumes that witness and routes around an unavailable surface; A concise pendant protocol for saying queued, blocked, attempted-but-unverified, and externally-verified as distinct outcomes

### "“If I made this an automatic rule, show me what you would have done over the last week, which cases would have needed my approval, and where the rule would have gone wrong—without actually changing anything.”"
- **useful because:** The owner is accumulating routines and delegated jobs, but cannot safely tell whether a new automation policy matches their real life. A replay against prior Mac jobs, browser observations, pendant interruptions, and receipts makes autonomy testable before it becomes surprising. It turns repeated one-off confirmations into evidence rather than silently learning permission.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Background model performs deterministic event filtering and a cheaper batch simulation; use realtime only to answer a follow-up question or read the short result aloud. High-cost reasoning is reserved for ambiguous counterfactuals.
- **latency:** A seven-day replay in 5–15 seconds on the Mac/relay; a spoken summary in under 2 seconds after results are ready. No action is taken during simulation.
- **cost:** Low batch-model cost; most work is local replay over logs and receipts. Dominant cost is browser page re-reads only when historical evidence is absent, and those reads should be labeled as estimates.
- **security:** Default to local redacted event features and never upload email/page contents unless the owner explicitly includes them. Simulations must be read-only, clearly marked hypothetical, and separate from executable jobs. Secret values and destructive actions are represented as categories, not payloads.
- **missing:** A deterministic counterfactual runner that replays historical events through a candidate policy and records hypothetical actions; A normalized event stream joining pendant bookmarks/alerts, Mac jobs, browser commands, receipts, and routine runs with retention and redaction; A dashboard and pendant report that distinguish observed historical evidence from inferred outcomes and let the owner approve a policy only after review

### "“Protect my energy this week: look across my calendar, reminders, unfinished work, travel, and recent interruptions; show me where the load is likely to exceed what I can realistically do, then suggest specific swaps or deferrals for my approval.”"
- **useful because:** The owner does not need another chronological briefing—they need judgment about capacity. Today the system can read pieces of their schedule and act on individual items, but cannot form a privacy-preserving load estimate, explain which commitments collide, or propose a humane plan that accounts for recovery time and interruption cost. This would help prevent overcommitment before it becomes an emergency.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Use a cheap background model for extraction, clustering, and load estimation; use the expensive realtime tier only if the owner asks for a conversational tradeoff discussion. The default result is a short generated plan, not live reasoning.
- **latency:** Generate overnight or on demand in 10–30 seconds; deliver a 30-second spoken summary. Proposed calendar/reminder edits remain pending until approval.
- **cost:** Low batch inference cost; the dominant cost is authenticated reads of calendars, task systems, and private browser pages. Cache normalized facts with short TTLs and re-read only changed sources.
- **security:** Keep raw mail and page text on the Mac whenever possible; send the relay only redacted commitment entities, times, durations, and sensitivity labels. Never infer health or emotional diagnoses. Do not cancel, decline, reschedule, or message anyone without explicit approval. Let the owner exclude sources or categories.
- **missing:** A personal capacity model that learns estimated effort, transition time, recovery time, and interruption cost without diagnosing the owner; A cross-source commitment graph that identifies collisions and distinguishes hard obligations from negotiable intentions; A proposal engine that produces reversible swaps/deferrals with explicit tradeoffs and approval-ready calendar/reminder changes; A feedback loop recording whether the predicted load was useful, without silently converting feedback into permissions


## Changes it proposed to its own stack

### `hardware` — Add a low-power LRA haptic actuator with a dedicated haptic driver on the currently unused I2C bus, plus a second physical acknowledge/cancel button (keep the existing button for conversation). Define three unmistakable patterns: short pulse=queued/understood, double pulse=needs approval, long pulse=failed or unverified. The relay/Mac can request a pattern, but the pendant must render it locally and safely when disconnected.
- **owner gets:** The owner can receive and approve a request discreetly in a meeting, on a bike, or when speech playback would be socially disruptive. A tactile distinction between queued, approved-needed, and actually failed prevents the dangerous silent-success problem when the Mac UI or browser is unreachable.
- effort: Moderate industrial/firmware revision: actuator, driver, button, enclosure and waterproofing; add a tiny local event state machine and test patterns against the existing full-duplex I2S path (haptics do not compete for I2S).  ·  risk: False or repeated vibration could annoy or startle; cap amplitude, duration, and retries, and provide a long press to silence. If the driver is absent or battery is low, fall back to LED/audio. A second button increases accidental presses, so require deliberate press durations and log all local acknowledgements.
- cost: Roughly $2–8 in prototype components, under 10 mA only during a pulse and near-zero idle; negligible API cost. Product enclosure and certification dominate eventual cost.  ·  latency: Local acknowledgement under 50 ms; remote status still depends on LTE-M/relay latency. No impact on audio latency if driven off I2C/GPIO.
- security: Haptic patterns reveal only coarse state, not private content. Do not encode message identity or secrets in vibration patterns. A local acknowledge must be treated as an intent signal and still pass server-side destructive-action policy.
- depends on: A typed cross-surface state vocabulary distinguishing queued, approval-required, attempted, externally verified, and failed; Relay push of coarse status events with deduplication and expiry; Pendant firmware persistence for an unsent acknowledgement while offline

### `context` — Build a local-only capacity-and-recovery model that represents commitments as effort intervals with transition cost, hard/soft negotiability, expected interruption load, and recovery buffers. Fit estimates from the owner's explicit corrections and completion history; keep raw source text on the Mac, export only redacted intervals and confidence. Add a weekly counterfactual planner that proposes swaps but cannot mutate calendars or send messages.
- **owner gets:** Instead of discovering they overcommitted after the week has already collapsed, the owner gets an honest warning and concrete alternatives that account for setup time and recovery—not merely an empty calendar slot.
- effort: High: typed commitment schema, source adapters, estimation feedback, privacy boundary, and a review UI. Start in shadow mode and compare predictions with actual completion before showing recommendations.  ·  risk: The model could be wrong or paternalistic. Show evidence and uncertainty, let the owner override every estimate, never infer medical/mental state, and provide a one-tap disable and source exclusions. Recovery is deleting the derived model and returning to raw schedules.
- cost: Moderate background model cost during nightly fitting; no realtime cost by default. Local storage and computation dominate, with minimal relay traffic.  ·  latency: Nightly generation avoids voice latency; on-demand estimate should complete within 20 seconds.
- security: Sensitive commitments stay on-device; only redacted time/effort features cross surfaces. Derived capacity inferences require a separate privacy class and retention limit.
- depends on: A typed cross-source commitment graph; Owner corrections and completion feedback; A review surface for proposed swaps and explicit approval; Reliable calendar/reminder/mail/browser read adapters


## What it asked for

_Nothing._
