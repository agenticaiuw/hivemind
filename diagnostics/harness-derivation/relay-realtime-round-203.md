# Harness derivation — relay-realtime — round 203

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Do that on the Mac, and if you need details, ask me."
- **useful because:** This is a smoother handoff for multi-step tasks: the relay captures intent, the Mac plans, and the owner only answers clarifying questions when necessary.
- **path:** relay → mac-bridge → browser
- **model tier:** Realtime for intent capture; mac-planner for the workflow.
- **latency:** Intent capture should be immediate; planning can take a few seconds.
- **cost:** Moderate: one plan call plus execution. Keep the relay’s role minimal.
- **security:** Do not execute irreversible actions without a clear plan and receipts. Keep a job record for traceability.
- **missing:** A resolvable intent-routing mechanism (relay_route_intent is currently unresolved).; An enum-based intent contract tied to real action types (so routing can resolve).; Relay capability manifest for discoverability.

### "“When my pendant is physically with my Mac, let this button press authorize the next powerful action I say—open the authenticated portal, send the prepared message, or change the setting—without another confirmation. If the pendant is not present, only prepare and report.”"
- **useful because:** It gives the owner fast, deliberate control over high-impact remote actions while preventing a replayed voice request or a compromised relay session from acting later. The same wearable that hears the request becomes a short-lived physical authorization key.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Realtime only parses the spoken request and reports the result; the Mac planner performs the action, while browser-extension handles authenticated browser state. No expensive model is needed for the cryptographic check.
- **latency:** Under 500 ms to establish the challenge when USB-attached, then the normal 1–3 s action latency; the pendant should say “authorized” immediately and stream the result when complete.
- **cost:** Usually one realtime turn plus one planner/action call, roughly $0.01–$0.05 depending on the action; cryptographic challenge traffic is negligible.
- **security:** A nonce-bound challenge must be signed by the pendant over USB or LTE and scoped to one normalized action, one Mac session, and a short expiry. Never treat mere historical pairing or an audio recording as authorization. Show a distinct LED pattern before commit and log the signed receipt; losing the pendant requires revocation.
- **missing:** pendant challenge-response firmware and secure key storage; relay authorization verifier and nonce ledger; Mac/browser enforcement that refuses the commit without a fresh pendant signature; a physical-presence signal that works over the currently live USB serial links

### "“Tell me what is actually true right now, even if the Mac, browser, and relay disagree—what changed, what is still a draft, and what evidence proves it.”"
- **useful because:** The owner currently has to trust a single completion message. This would reconcile independent observations: for example, the Mac reports a send attempt, the authenticated browser still shows a draft, and the relay has no receipt. It speaks the contradiction instead of confidently claiming success.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** A cheap background perception pass gathers structured observations; a judgment model compares timestamps, identities, and source reliability. Realtime only turns the final verdict into a short spoken answer.
- **latency:** 2–5 seconds for a normal live query, with an immediate “checking three sources” acknowledgement; never block the voice turn on an unavailable source.
- **cost:** One small perception/judgment pass, approximately $0.01–$0.04 per query; browser and Mac reads dominate neither tokens nor bandwidth.
- **security:** Only return content already authorized for the owner’s paired Mac/browser session. Preserve source timestamps and hashes rather than copying whole pages into relay memory. Explicitly say “unverified” when sources conflict or are stale; never synthesize a successful state from an action request alone.
- **missing:** a common observation envelope with source, timestamp, object identity, and confidence; a reconciliation/judgment route that can request parallel Mac and browser reads; spoken provenance formatting and a contradiction receipt in the job ledger

### "“Take this outcome, work across my Mac and my authenticated browser, and keep going through ordinary interruptions. If one step fails, use the partial result to continue, and come back with exactly what was done, what was not, and the one choice you need from me.”"
- **useful because:** This is an outcome-level assistant rather than a brittle one-turn command: it can collect a file locally, use a logged-in web service, reconcile the returned identifiers, and recover from a dropped Mac or browser connection without making the owner repeat the whole request.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Realtime extracts the goal and handles brief clarifications. A cheaper planner owns the durable state machine; use the vision model only for a browser/UI step that has no reliable structured action.
- **latency:** A spoken acknowledgement within 1 second; each step may take seconds or minutes. The owner can end the conversation and receive a concise completion or blocked-choice alert later.
- **cost:** Approximately $0.03–$0.20 per multi-step outcome, dominated by planner iterations and occasional vision calls; retries should reuse observations rather than resend full context.
- **security:** Persist only the minimum goal, action receipts, and opaque remote IDs. Every retry must be idempotency-keyed so reconnects cannot duplicate a send or purchase. A blocked destructive choice is reported, not guessed; all completed steps remain auditable and undo metadata is retained where available.
- **missing:** durable cross-surface workflow state and idempotency keys; a coordinator that can resume after Mac/browser disconnects; event delivery to the pendant for completion or needs-attention; structured partial-result handoff between planner and browser session


## Changes it proposed to its own stack

### `integration` — Build a relay-visible capability manifest and health inventory endpoint (e.g., GET /relay/capabilities and GET /relay/health) so this surface can be discovered, tested, and monitored like the Mac agent. Include tool resolution status (live/resolved/unresolved), and expose whether event push is implemented.
- **owner gets:** The owner feels this as reliability: fewer silent failures and fewer rounds spent guessing what the relay can do. It also makes new features testable in automation.
- effort: Medium. Requires adding an endpoint and wiring capability registration in the relay worker.  ·  risk: Low. Main risk is leaking internal details; mitigate by redacting secrets and returning only capability names and statuses.
- cost: Low. A small amount of extra metadata and an endpoint.  ·  latency: Negligible. Fetch only when asked.
- security: Positive if done carefully: explicit inventory reduces accidental exposure and makes access control auditable.

### `model-routing` — Replace the unresolved free-form relay_route_intent with an enum-based intent contract mapped to real action types (the same vocabulary used by /plan). Use per-enum resolution so some intents can go live before others. Provide a fallback to mac_delegate for complex tasks.
- **owner gets:** Faster, more reliable voice control. The owner can say a simple thing and have it routed correctly without brittle heuristics.
- effort: Medium to high. Requires schema design, resolver wiring, and coordination with mac-planner.  ·  risk: Medium. Misrouting could launch the wrong action; mitigate with receipts and conservative defaults (ask before irreversible steps).
- cost: Low ongoing; moderate initial integration.  ·  latency: Improves routing speed by avoiding extra clarification turns.
- security: Improves safety by making routing explicit and auditable.

### `integration` — Implement asynchronous completion delivery using a durable subscription: Mac job lifecycle emits completion events to the relay; relay pushes a spoken summary to the pendant/phone if online, or stores a short alert in the existing inbox mechanism if offline. Use ttl and expiry semantics.
- **owner gets:** They can start something and move on without babysitting. The system feels dependable.
- effort: High. Needs event emission, relay delivery, and UI/voice handling.  ·  risk: Medium. Duplicate or out-of-order events could confuse; mitigate with idempotent jobIds and receipts.
- cost: Moderate. Event channel plus storage for small alerts.  ·  latency: Low when online; eventual when offline.
- security: Must ensure summaries reflect truth and do not leak sensitive content. Use minimal phrasing and job scoping.

### `integration` — Build a signed, one-shot authorization bridge: the pendant emits a nonce-bound challenge over the live USB serial transport (and later LTE), the relay binds that signature to a normalized /plan job and expiry, and the Mac/browser executor refuses commit unless the exact job receipt contains that signature. Return the signed receipt to the pendant and visibly distinguish authorized execution from mere preparation.
- **owner gets:** The owner can safely say “do it” while standing at the Mac and get immediate execution, while the same request cannot be replayed after they walk away or from an old audio transcript. It turns the wearable into a trustworthy physical control, not just a microphone.
- effort: High: firmware key provisioning and challenge protocol, relay verifier/nonce store, and executor-side commit enforcement; prototype is possible now over the two USB serial devices.  ·  risk: A lost pendant or clock/transport failure could strand authorization; recover with revocation and a local pairing reset. A bug binding the wrong job is high impact, so fail closed and expose the normalized action in the spoken/LED pre-commit cue.
- cost: Negligible runtime/API cost; one small key store and nonce record. Prototype requires no new hardware, since nRF9160 and ESP32 are USB-connected today.  ·  latency: Adds roughly 100–500 ms for challenge verification; no added model latency.
- security: Substantially improves replay resistance and physical-intent binding, but introduces key lifecycle and revocation obligations. Do not log private audio as the authorization artifact.
- depends on: A pendant firmware challenge-response skill with secure key storage; A relay job authorization record that binds nonce, action hash, session, and expiry; Mac/browser executor support for a mandatory signed commit token


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities and a concrete integration change: (1) pendant-as-physical, one-shot authorization for powerful Mac/browser actions; (2) truth reconciliation that speaks contradictions with source evidence; (3) resumable outcome workflows across Mac and authenticated browser, with precise partial completion; and (4) the signed USB/LTE authorization bridge needed to make the first real. What remains needed is not another discovery round: firmware key/challenge support, relay nonce/job binding, a common observation envelope plus reconciliation worker, durable idempotent workflow state, and pendant event delivery. The first capability is the single most useful near-term differentiator and is prototypeable now over the physically connected USB devices.

**Biggest unknown:** Whether the current pendant firmware exposes enough secure key storage and a usable USB command channel to implement the authorization challenge without changing the board/boot chain.

