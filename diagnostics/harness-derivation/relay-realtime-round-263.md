# Harness derivation — relay-realtime — round 263

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If my Mac is connected over USB, use it to help right now."
- **useful because:** Today the pendant can be physically attached to the Mac. If LTE isn’t registered, the Mac link becomes the lifeline for real work and debugging.
- **path:** pendant → mac-bridge → relay
- **model tier:** realtime for command intent; mac-planner for actions
- **latency:** Acknowledge immediately, then hand off to the Mac agent.
- **cost:** Low. Mostly local Mac actions and logs.
- **security:** USB control is powerful; keep actions reversible by default and avoid interfering with active work.
- **missing:** A clear relay-to-Mac USB bridge control path that the relay can invoke when the pendant is connected

### "“Pick up where I left off.” Reconstruct the work I was doing across my Mac and browser, tell me the one-sentence state and the next useful action, then resume it when I say go."
- **useful because:** When the owner returns after hours away, they currently must remember which app, tab, draft, and pending agent job mattered. This would make the pendant a true continuity surface rather than a command microphone, while preserving uncertainty instead of pretending stale context is current.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Realtime relay for the short spoken state; cheaper background planner for reconstruction and action selection; mac-vision only when a visual state is required.
- **latency:** Initial spoken state in 3–5 seconds; deeper reconstruction may continue asynchronously, with a compact update when evidence arrives.
- **cost:** About $0.01–$0.05 per resume depending on whether visual inspection is needed; dominant costs are planner context and browser/Mac state reads.
- **security:** The response can expose sensitive app and tab names over the pendant. Surface only the minimum relevant state, retain provenance, and require explicit confirmation only for an irreversible next action; stale or conflicting evidence must be said aloud.
- **missing:** A durable cross-surface context snapshot that records active Mac windows, browser tabs, unfinished jobs, and the owner's last stated goal; A resume planner that ranks evidence by recency and confidence and produces a single next action; A live-turn hook that injects the snapshot into relay conversation context without resending the large legacy memory block

### "“Protect my attention while I’m away from the Mac.” Let the pendant establish an attention mode, classify incoming changes from my browser and Mac, and speak only the rare event that is both urgent and actionable; give me a compact digest when I return."
- **useful because:** The owner wears the device away from the desk, so forwarding every completion or alert makes the pendant unusable. This creates a deliberate boundary between ambient work and interruptions, using the physical wearable as the authoritative attention state rather than guessing from Mac activity.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Cheap background classifier and rules for ordinary changes; realtime model only for the spoken exception or the return digest.
- **latency:** Urgent event classification within 30 seconds of an observed change; spoken interruption under 2 seconds after the decision; return digest under 5 seconds.
- **cost:** Low ongoing cost if change feeds are diff-based; roughly $0.001–$0.01 per observed event, with model calls reserved for ambiguous or high-value changes.
- **security:** A wrong urgency decision either leaks a private detail aloud or hides something important. Store only event hashes and short redacted summaries by default, expose source/provenance in the dashboard, and provide a physical escape gesture to hear the suppressed queue.
- **missing:** A pendant attention-mode state with explicit entered/left timestamps and offline-safe behavior; A cross-surface change feed that can compare Mac and authenticated browser state without treating a failed check as no change; An urgency/actionability policy and suppression ledger that supports later replay without duplicating existing alert records

### "“Don’t just tell me the job finished—prove the outcome.” For any delegated Mac/browser task, compare the requested outcome with fresh observations, identify exactly what is still wrong, and either repair it or tell me the smallest next decision."
- **useful because:** A queued job can report completion while an email remains unsent, a file is in the wrong folder, or a browser action landed on the wrong account. Outcome verification turns autonomous computer use from optimistic action execution into something the owner can trust while away from the screen.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Cheap structured receipt matcher first; planner model for discrepancies and repair; realtime model only to explain the final verdict in one short sentence.
- **latency:** Fast receipt verdict in 2–4 seconds after completion; repair can run asynchronously with a spoken provisional result and a later verified result.
- **cost:** About $0.005–$0.03 per task, dominated by fresh browser/Mac observations rather than speech generation.
- **security:** Verification may read private destinations and should never claim success from an old receipt. Bind evidence to job ID, account/session, and observation timestamp; redact payloads in the dashboard and announce uncertainty when a surface is offline.
- **missing:** A typed outcome contract captured at plan time (observable predicates, acceptable evidence, and repair budget); A verifier that can collect fresh observations from both Mac and browser and distinguish failure-to-observe from false; A repair loop with bounded attempts, immutable evidence receipts, and a concise pendant-facing verdict

### "“Stop what you’re doing and undo the last safe step.” While a Mac or browser job is running, let me interrupt it from the pendant, learn exactly which step is in flight, cancel before the next mutation, and roll back only the actions with recorded inverse operations."
- **useful because:** Today the owner can start delegated work while away, but cannot reliably seize control when the situation changes. A spoken stop-and-recover primitive is more valuable than another completion notification: it makes autonomy reversible in the moment, without requiring the owner to find the right Mac window.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Realtime relay for intent recognition and a one-sentence acknowledgement; deterministic job controller for cancellation and inverse actions; planner tier only when recovery requires choosing among multiple safe compensations.
- **latency:** Acknowledge within 1 second and stop before the next action where possible; recovery status within 5 seconds, with longer repair reported asynchronously.
- **cost:** Usually under $0.005 per interruption; cost is dominated by a fresh job-state read, not inference.
- **security:** A mistaken stop could abandon important work, while a mistaken undo could destroy unrelated state. Bind the command to the currently spoken job, expose the exact step being cancelled, make inverse operations idempotent, and never claim rollback if the target surface was offline.
- **missing:** A cancellation transition in the job state machine with an atomic before-next-action check; Per-action inverse metadata and durable action receipts, including partial-rollback status; A pendant utterance resolver that can identify “that” from the active job without requiring a new free-form protocol

### "“Find the latest trustworthy version of the thing I mean.” Search my local files, open browser sessions, and recent agent work together, resolve duplicates and stale drafts, then read me the best match with its source and confidence or ask one disambiguating question."
- **useful because:** The owner is often away from the Mac and remembers an object, not its app. Today each surface can be searched separately and a result can be acted on, but nothing can establish that a file, authenticated page, and prior job refer to the same artifact. This would eliminate the costly failure of sending or editing an obsolete copy.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Cheap lexical/index search and metadata joins first; planner model for entity resolution and conflict explanation; realtime model only for the spoken answer.
- **latency:** Return a first candidate in 3 seconds; continue deeper search for up to 15 seconds and speak a correction if a stronger source appears.
- **cost:** Roughly $0.005–$0.03 per query; indexing is the main storage/CPU cost, while model usage is limited to ambiguous duplicate resolution.
- **security:** Search can cross boundaries between private files and authenticated sites. Enforce surface/account scope, never quote content from a lower-confidence candidate as fact, show provenance and timestamps, and expire indexed browser content according to its source TTL.
- **missing:** A unified, permission-scoped artifact index spanning local files, browser pages, and job receipts; Stable entity/fingerprint extraction for drafts, URLs, filenames, and timestamps with duplicate and stale-version scoring; A relay retrieval endpoint that streams candidate provenance and can ask one targeted clarification without dumping private search results


## Changes it proposed to its own stack

### `relay` — Implement a real notification pipeline for job completion: a watcher that checks job state, emits a completion event, and writes a short alert into the device’s existing inbox mechanism for delivery when the link is available.
- **owner gets:** They can ask for something and trust they’ll hear about the result later, without keeping the session open.
- effort: Medium. Requires wiring to job status, an event emitter, and integration with the existing inbox delivery shape.  ·  risk: Duplicate or lost alerts. Mitigate with idempotent event IDs and receipts.
- cost: Low runtime cost; periodic checks. Development cost moderate.  ·  latency: No impact on live speech; completion arrives asynchronously.
- security: Carries task summaries; must redact sensitive content and respect confirmation rules.
- depends on: relay_event_push implementation or equivalent delivery mechanism; job_completion_watch behavior guaranteed beyond a single GET


## What it asked for

_Nothing._
## Its own summary

Recorded five capabilities. The strongest is “Pick up where I left off”: a spoken, evidence-ranked reconstruction of interrupted work across Mac, browser, and pending jobs, followed by safe resumption. It needs a durable cross-surface context snapshot and live-turn injection. Also recorded an attention firewall, independent outcome verification, pendant stop/undo control, and cross-surface artifact search. The proposals deliberately identify missing connective layers rather than pretending the existing routes already provide the owner-facing behavior.

**Biggest unknown:** Several proposals are close to existing backlog ideas, especially interruption/undo and attention filtering; the recorder accepted them but flagged similarity. The genuinely distinct gap is trustworthy interrupted-work reconstruction with ranked, timestamped evidence.

