# Harness derivation — relay-realtime — round 206

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Keep an eye on the thing I just asked you to do, and tell me when it’s done."
- **useful because:** This is the single most useful behavior: the owner can ask for work, walk away, and still get a clear completion signal without polling or staring at a screen.
- **path:** relay-realtime → mac-planner → mac-terminal → browser-extension → pendant
- **model tier:** realtime for the initial promise; cheaper background tier for monitoring and summarizing completion
- **latency:** Immediate acknowledgement in under a second; completion notification can arrive minutes to hours later.
- **cost:** Low per job after start; the expensive part is keeping context and summarizing results, which should run off the realtime tier.
- **security:** Job status and short summaries leave the device; avoid including sensitive content in spoken alerts, and require confirmation before speaking anything potentially private out loud.
- **missing:** A reliable completion-event path that resolves to real delivery targets; A relay-to-pendant alert delivery that uses the existing unified inbox rather than a new queue; A summary renderer that can produce a short spoken line from receipts

### "Summarize what you know about what I’m working on right now, and keep it short."
- **useful because:** The owner gets a quick, consistent snapshot of the active project or task without dumping noisy history, perfect for voice.
- **path:** relay-realtime → mac-planner → faculty-perception → faculty-judgement
- **model tier:** realtime for spoken summary; cheaper tier for gathering and structuring context
- **latency:** Under a second for a short summary; longer only if it must fetch fresh machine context.
- **cost:** Moderate; dominated by context retrieval and summarization, not by speech.
- **security:** Context may include sensitive data; summarize conservatively and avoid quoting private content unless the user asks.
- **missing:** Live prompt path must use the memory projection instead of legacy context blocks; Task-scoped context selection for voice surface

### "Use the Mac as a bridge right now and act on what I say, even if the pendant isn’t on LTE yet."
- **useful because:** The owner can test real workflows immediately: the pendant is physically connected to the Mac, so the system should be useful today, not after registration.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension
- **model tier:** realtime for intent capture; mac-planner for planning and execution
- **latency:** Fast: acknowledgement under a second; execution time depends on the task.
- **cost:** Low to moderate; planning and execution dominate cost, not the relay.
- **security:** Avoid interrupting active work; confirm before destructive actions.
- **missing:** Reliable USB-bridge operational status reporting to the relay; A clear fallback policy: Mac-online path preferred when LTE is not registered

### "When I say “panic stop,” stop every action this system has started, tell me exactly what was stopped, and leave a recoverable record of anything that could not be interrupted."
- **useful because:** A worn button and voice are the only controls the owner can reach when away from the Mac. Today an active Mac/browser job can outlive the conversation with no single owner-facing kill switch. This turns the pendant into a genuine emergency brake across relay, Mac, and browser rather than merely another status query.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime classifies the utterance and immediately issues cancellation; no model should deliberate before stopping. Background reconciliation verifies each downstream job and summarizes partial effects.
- **latency:** Begin cancellation acknowledgement in under 500 ms; reconcile all known jobs within 5 s.
- **cost:** Near-zero inference beyond the live turn; dominant cost is one short realtime turn and status polling for active jobs.
- **security:** A false trigger could cancel useful work, so require the explicit phrase or a deliberate long button hold, never ordinary speech. Cancellation is safer than continuing but may leave partial mutations; retain immutable receipts and expose an undo path where available. No audio needs to leave the pendant beyond the normal turn.
- **missing:** A relay-wide active-job registry keyed to the owner session; A cancellation fan-out from relay to Mac planner, computer-use loop, and browser command queue; A pendant emergency gesture and a spoken/LED confirmation state; A structured cancellation receipt that distinguishes cancelled, already-completed, and uninterruptible actions

### "What is happening right now? Give me one concise situation report that combines my pendant connection, active Mac/browser work, queued jobs, and the last verified result, and call out contradictions instead of guessing."
- **useful because:** Today the owner must ask separate status questions and cannot tell whether silence means completion, a dead Mac, a stale browser session, or a disconnected pendant. A cross-surface truth report is uniquely valuable from a worn front door: it turns a fragmented hive into one dependable answer with explicit uncertainty.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use deterministic aggregation for health, job, and receipt facts; use the realtime model only to compress the already-collected evidence into one spoken sentence. No background model is needed.
- **latency:** Parallel probes and a spoken answer in 2 seconds when surfaces respond; state exactly which surface timed out rather than waiting indefinitely.
- **cost:** One short realtime synthesis turn per request; probe and aggregation costs are negligible. The main cost is retaining compact, timestamped receipts rather than resending full transcripts.
- **security:** Do not read page contents or private Mac data merely for health. Scope browser evidence to URL/title/command state unless the owner explicitly asks for content. Include timestamps and freshness so a stale result cannot be presented as current.
- **missing:** A relay aggregator that concurrently reads device health, active jobs, Mac status, browser inspection, and execution receipts; A common freshness/contradiction schema across pendant, Mac, and browser reports; A compact spoken renderer that names uncertainty and source timestamps; A live pendant health route, since the known /v1/devices/status route must be made authoritative for this USB/LTE split

### "Only carry out this sensitive request while I am physically holding my pendant: have it prove my presence, then let the Mac and authenticated browser act, and tell me if the proof expires before completion."
- **useful because:** A spoken voice session alone is not a reliable presence signal when the owner is away from the Mac. This would make the pendant a physical authorization token that spans relay, Mac, and browser without imposing confirmation on ordinary reversible work. It is especially useful for an owner who wants maximum access but still wants a deliberate boundary for rare, consequential operations.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime identifies the requested presence-bound operation; cryptographic verification, expiry, and enforcement are deterministic. The model only explains the resulting receipt.
- **latency:** Challenge/response under 300 ms over the live USB path and under 2 s over LTE; leases should expire automatically after 60 s or completion.
- **cost:** Negligible inference cost; engineering cost is key provisioning, challenge verification, and enforcement adapters. No recurring API cost beyond a normal voice turn.
- **security:** Private keys must never leave the pendant. Bind each lease to a nonce, operation digest, target surface, and expiry to prevent replay or confused-deputy use. A lost pendant needs revocation through the relay. This is opt-in per utterance and must not silently gate normal actions.
- **missing:** A pendant secure-element or protected key slot and firmware challenge-response command; Relay-side operation-digest leases and revocation; Mac and browser adapters that refuse lease-bound actions when the lease is absent or expired; A visible/haptic/LED acknowledgement that the physical proof succeeded


## Changes it proposed to its own stack

### `relay` — Add a relay-local capability inventory endpoint and tool manifest, and expose a small health/status view for the USB-connected pendant and ESP32 bridge. The relay should be able to discover its own routes and what it can call, instead of relying on indirect evidence.
- **owner gets:** Fewer misroutes and fewer ‘I don’t know if that exists’ failures means smoother voice interactions and fewer dead ends.
- effort: Medium: implement a /capabilities-like route for the relay surface, plus a status probe for bridge and pendant connection state.  ·  risk: Low. Main risk is exposing sensitive operational details; mitigate by redacting secrets and requiring auth.
- cost: Small; a couple of new endpoints and lightweight probes.  ·  latency: Minimal per request.
- security: Must be bearer-protected; avoid logging tokens or private state.

### `firmware` — Implement a transport-independent conversation session on the pendant: start over USB serial when attached to the Mac, negotiate a session token and sequence window with the relay, then seamlessly resume the same audio/session over LTE-M when USB disappears. The relay must deduplicate replayed Opus/audio frames and preserve the staged spoken reply across the handoff.
- **owner gets:** The owner can begin speaking at the desk and walk away without losing the turn, or test the real pendant today over USB and later use the identical experience untethered. A dropped cable or radio transition would become a brief pause instead of a lost conversation.
- effort: High: firmware transport state machine, relay session persistence, USB bridge integration, LTE registration/reconnect testing, and hardware soak tests.  ·  risk: Duplicate or reordered audio could produce repeated words or corrupt a turn. Use monotonically numbered frames, bounded replay windows, explicit half-open session states, and discard stale transport epochs. Recover by ending the turn with a truthful reconnect notice if handoff exceeds the window.
- cost: No per-turn model cost. Moderate firmware/relay engineering; existing USB hardware and nRF9160 modem are reused. LTE data usage is unchanged except for bounded retransmission.  ·  latency: A successful handoff adds roughly 100–500 ms; normal USB/LTE turns are unchanged.
- security: Bind both transports to the same authenticated session token; never accept a USB-originated token from an unpaired host or reuse it after expiry. Keep audio encrypted in transit.
- depends on: A relay session record that survives transport changes; A USB serial bridge endpoint that exposes the same framing and authentication as LTE; nRF9160 LTE registration and reconnect behavior being tested end to end; Replay-safe audio/frame acknowledgements


## What it asked for

_Nothing._
## Its own summary

Recorded four new proposals: (1) a cross-surface panic-stop that fans cancellation through relay, Mac, and browser and reports partial effects; (2) a truthful “what is happening right now?” report aggregating pendant, jobs, Mac, browser, and receipts; (3) an opt-in pendant physical-presence lease for sensitive operations; and (4) USB-to-LTE conversation handoff so the owner can walk away without losing a live turn. The most useful is the panic-stop: it gives the worn front door an immediate, system-wide safety control that does not exist today. The highest-leverage enabling work is the transport-independent session, because the hardware is physically testable over USB now while LTE is not yet registered.

**Biggest unknown:** Whether the relay already has an authoritative active-job registry and cancellation fan-out, and whether the pendant USB bridge can expose the same authenticated framing as LTE. Those determine whether panic-stop and handoff are mostly integration or require new protocols.

