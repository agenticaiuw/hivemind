# Harness derivation — relay-realtime — round 269

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "What’s going on with my system right now?"
- **useful because:** A fast health snapshot reduces confusion when the Mac, browser, and wearable disagree. It’s a quick sanity check before deeper troubleshooting.
- **path:** relay → mac-bridge → browser → pendant
- **model tier:** Realtime to summarize; background tiers to gather details if needed.
- **latency:** Under a second for a summary; a deeper report can be deferred.
- **cost:** Low; mostly reads like status endpoints and job summaries.
- **security:** Status can reveal app names, URLs, or device presence; keep the default summary high level.
- **missing:** A unified relay-side status aggregator; today status is scattered across Mac endpoints and job logs.; A consistent presence signal for the pendant when LTE is unregistered (USB-attached is real today).

### "Summarize and prioritize the notifications and results you’ve queued for me."
- **useful because:** When the owner returns after a busy day, they need one coherent digest instead of a stream of unrelated pings.
- **path:** relay → browser → mac-bridge → pendant
- **model tier:** Background model for ranking and summarization; Realtime only for the spoken top items.
- **latency:** Digest generation can take seconds; spoken top summary should be brief.
- **cost:** Moderate; dominated by summarization tokens and reading multiple sources.
- **security:** Digesting across sources risks mixing contexts; keep sources labeled and avoid exposing sensitive content without confirmation.
- **missing:** A unified queue model across existing inbox/outbox mechanisms; today they’re implemented as separate subsystems.; A standard schema for priority, expiry, and source labeling across alerts, job results, and memos.

### "“I’m leaving my desk—make a work capsule for this, and let me resume it from the pendant later exactly where I left off.”"
- **useful because:** Today a spoken request can be handed to the Mac, but the handoff loses the page, window, selection, and unfinished reasoning that made the task understandable. A durable capsule would let the owner leave the Mac, continue by voice, and return to the same browser/Mac state rather than restarting or explaining everything.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime extracts a compact goal and asks one clarifying question at most; a cheaper background planner assembles the capsule and reconciles it when the Mac or browser reconnects.
- **latency:** Acknowledge in under 1 second; capsule creation under 10 seconds; reconnection and reconciliation can take 1–3 minutes.
- **cost:** About $0.01–$0.08 per handoff depending on whether a background planner must summarize screenshots/page state; storage and polling dominate, not realtime inference.
- **security:** Capsules may contain authenticated page text and private documents. Encrypt at rest, scope each artifact to its originating surface, expire stale page snapshots, and never read a page merely because it is in a capsule without the owner asking to resume.
- **missing:** A first-class capsule schema containing goal, transcript excerpt, browser tab/page snapshot, Mac window/app state, pending actions, and provenance; A reconnect reconciler that can detect stale UI and ask the owner instead of blindly replaying clicks; A pendant command to list/resume/abandon capsules

### "“Is that actually done? Check everywhere you can, show me the evidence, and fix it if it isn’t.”"
- **useful because:** The current system can report a queued job or inspect one surface, but it cannot establish truth when a task spans a browser portal, a local file, a Mac application, and a relay job. This gives the owner an evidence-backed answer and an optional repair, instead of a confident stale-memory reply.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only classifies the question and speaks a short verdict; background perception gathers independent evidence and a judgement/action tier resolves contradictions or proposes the smallest repair.
- **latency:** Speak “checking” immediately; first verdict in 5–15 seconds, with late evidence pushed to the pendant and dashboard.
- **cost:** Roughly $0.03–$0.20 per check; browser snapshots and Mac round trips dominate, with a cheap model sufficient for evidence normalization.
- **security:** Evidence can expose mail, documents, and authenticated portals. Keep raw evidence on its source surface, transmit hashes/excerpts by default, record provenance and timestamps, and require explicit confirmation before any repair that sends, deletes, buys, or publishes.
- **missing:** A cross-surface claim/evidence model with freshness, authority, and contradiction fields; A verifier that queries Mac and browser in parallel and distinguishes “not found” from “could not check”; A repair planner that links each proposed mutation to the contradictory evidence and emits a receipt

### "“Approve this one sensitive action with my pendant.”"
- **useful because:** A spoken approval can be overheard or replayed, and a Mac session can remain unlocked after the owner walks away. A deliberate physical press on the worn device would bind approval to the owner’s current challenge, while still allowing the owner’s stated maximum-access policy for ordinary reversible work.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime presents the exact pending action and challenge; firmware performs the physical confirmation; the relay verifies the signed response; the Mac/browser executes only the matching action hash.
- **latency:** Challenge to spoken confirmation under 2 seconds; physical approval to execution under 3 seconds.
- **cost:** Under $0.01 per approval in inference; engineering is dominated by firmware cryptography, replay protection, and Mac/browser adapters.
- **security:** This is an authorization primitive, not a generic confirmation dialog. Use device-bound keys, nonce and action-hash binding, short expiry, monotonic counters, cancellation on changed parameters, and an audit receipt. Never speak secrets in the challenge; require a fresh press for each high-impact action.
- **missing:** Secure key provisioning and signed challenge-response support in the nRF9160 firmware; Relay endpoint for nonce issuance, verification, expiry, and replay detection; Mac and browser executors that refuse an action whose hash differs from the approved one; A clear pendant interaction pattern using the existing single button/LED without delaying ordinary presses

### "“Use my pendant normally even when LTE is unavailable—fall back to the Mac’s USB serial link, then switch back to LTE without losing the conversation.”"
- **useful because:** The wearable is physically connected and testable today, but an unregistered pendant cannot be a live voice front door. A transparent tethered mode would make the product usable at home and in development now, while preserving the same button, speaker, relay session, and queued delivery semantics when the owner walks away.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Realtime stays on the relay; the Mac USB companion only transports framed audio/control and never becomes a second conversational model. A small local connectivity supervisor chooses USB or LTE and resumes the same session on link change.
- **latency:** USB press-to-first-audio should remain under 500 ms; link failover should be detected in under 2 seconds, with no more than one audio frame lost.
- **cost:** Negligible per-turn model cost beyond current realtime inference; implementation is primarily serial framing, reconnect state, and a Mac launch agent. No recurring cloud browser cost.
- **security:** USB must be authenticated to the paired Mac, not accepted from arbitrary serial devices. Bind a session to a device identity, protect audio/control framing against injection, and visibly indicate which transport is active without exposing transcripts to unrelated local users.
- **missing:** A Mac USB companion that terminates the nRF9160 serial protocol and forwards the existing audio pipeline; Relay session transport abstraction with resumable sequence numbers and duplicate-frame suppression; Firmware link arbitration and a clear tethered-versus-LTE status indication using the existing LED patterns


## What it asked for

_Nothing._
## Its own summary

Recorded four owner-facing proposals: resumable cross-surface work capsules, evidence-backed “is it done?” verification with optional repair, physical pendant-bound approval for sensitive actions, and USB/LTE-transparent live voice continuity. The strongest near-term value is tethered live voice: it makes the physically connected pendant usable today, while the strongest long-term safety/value is action approval bound to a real press on the worn device. Several proposals were flagged as close to backlog items, so they should be deduplicated rather than rephrased.

**Biggest unknown:** Which existing relay routes actually terminate the live USB serial/audio path and whether /approve is already a complete execution gate; the tool inventory is gone this round, so I cannot distinguish an unwired connector from a genuinely missing subsystem.

