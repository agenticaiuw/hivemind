# Harness derivation — relay-realtime — round 136

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I press the pendant and say “summarize what’s on my screen and tell me what matters,” do it even if my Mac is asleep."
- **useful because:** This would be the single most useful everyday feature: a hands-free, low-friction briefing that works while the owner is away, without requiring the Mac to be awake or the browser extension to be active.
- **path:** pendant → relay → browser
- **model tier:** Realtime for the initial voice interaction; a cheaper background model for page extraction and summarization.
- **latency:** Fast acknowledgement (under a second) that the request is accepted; summary can arrive after a short delay.
- **cost:** Low per request for intent handling; extraction cost depends on number of pages and DOM size.
- **security:** Only authenticated sessions should be readable. Never exfiltrate private content; summaries must cite sources and avoid storing full page text unless needed for debugging.
- **missing:** Implement server_browser_actions on the relay; Session/auth handoff for browser context independent of the Mac; A status callback path to deliver results back to the voice session

### "If I say “check on that thing you sent to my Mac,” tell me its status right away."
- **useful because:** It closes the loop in a way the owner can feel: no guessing whether a delegated task is queued, running, failed, or done.
- **path:** relay → mac-bridge
- **model tier:** Realtime, because the owner is waiting for a quick spoken answer.
- **latency:** Sub-second; should not require waking the Mac.
- **cost:** Minimal; reads relay job records.
- **security:** Status text must be spoken verbatim to avoid misreporting outcomes.
- **missing:** 

### "If my pendant audio stops reaching you, detect it and switch to a fallback path if available."
- **useful because:** Audio failure is catastrophic for a voice-first device. Rapid detection and graceful fallback prevents silent failure and saves time debugging in the field.
- **path:** pendant → bridge → relay
- **model tier:** Realtime for detection and user-facing messaging; no heavy model work required.
- **latency:** Seconds; it should be noticed quickly.
- **cost:** Low; small heartbeats and ack messages.
- **security:** Avoid leaking audio content in diagnostics; only transmit health metadata.
- **missing:** A reliable heartbeat/ack protocol between pendant, bridge, and relay; Implementation of relay_route_intent and a device registry with signed beacons; A fallback transport (e.g., server browser audio path) if it exists

### "When I say “handle this end to end,” have the pendant identify the active browser page or Mac document, extract the relevant task, complete it across authenticated browser and Mac apps, and tell me exactly what changed."
- **useful because:** Today the owner must manually bridge context between a worn voice interface, an authenticated browser tab, and Mac applications. This would make one spoken request operate on the thing already in front of them, even when the work crosses surfaces.
- **path:** pendant → relay → browser → mac-planner → mac-vision → dashboard
- **model tier:** Realtime relay for disambiguation and a short spoken response; background mac-planner for the multi-step plan; browser harness for authenticated page state; mac-vision only when DOM or typed actions cannot identify the target.
- **latency:** Acknowledge in under 500 ms, then complete in under 30 seconds for ordinary tasks; stream progress only when a step exceeds 5 seconds.
- **cost:** Roughly $0.03–$0.20 per invocation, dominated by planner calls and any vision frames; relay speech handling should remain a single low-latency turn.
- **security:** The browser session and local document contents leave their surfaces and are merged into one task context. The system must show the source page/document and an action receipt, and must never claim completion without a typed result from each surface. Owner policy permits execution without confirmation.
- **missing:** A cross-surface active-context resolver that can identify the owner's focused browser tab or Mac document; A durable workflow state joining browser request IDs, Mac job IDs, and pendant utterance IDs; A completion/result synthesizer that can cite every mutation and distinguish partial failure

### "Put me in a live “show me and do it with me” mode: I press the pendant button, narrate what I want while looking at my Mac, and you keep the current Mac screen and authenticated browser tab in a shared session, asking only spoken clarifying questions and performing each small step as I confirm it verbally."
- **useful because:** A wearable owner cannot comfortably describe every UI detail, while the current computer-use loop is disabled and ordinary delegation waits for a complete goal. This would make the pendant a practical remote control for unfamiliar interfaces without requiring the owner to touch the Mac.
- **path:** pendant → relay → mac-vision → mac-planner → browser → dashboard
- **model tier:** Realtime relay maintains turn-taking; a low-cost vision model samples only changed screen regions; mac-planner handles action selection; browser harness supplies DOM/session state when available.
- **latency:** Speech acknowledgement and next question under 700 ms; each inspected frame under 2 seconds; action result under 4 seconds.
- **cost:** About $0.05–$0.40 per five-minute session, dominated by sampled vision frames and planner turns; screen regions should be diffed to control cost.
- **security:** Live screen and authenticated tabs may contain secrets or third-party data. Keep frames transient, bind the session to the pendant button press, visibly label the active app/tab, and retain only action receipts rather than screenshots.
- **missing:** A bidirectional realtime session endpoint carrying pendant audio, Mac screen diffs, browser DOM snapshots, and spoken responses; A Mac screen-diff capture and push channel; current mac-vision is disabled; An interruption-safe turn protocol that pauses action selection while the owner is speaking and resumes from the latest state

### "Let me say “use my work context for this once” and have the relay create a temporary, auditable data lease spanning my authenticated browser tabs and selected Mac files: answer the question or complete the task, then automatically destroy the assembled context and tell me what sources were used."
- **useful because:** The owner wants maximum access, but a single voice request should not turn into permanent shared memory or accidental cross-task leakage. This gives powerful cross-device work while making the privacy boundary understandable and automatic.
- **path:** pendant → relay → browser → mac-planner → mac-terminal → dashboard
- **model tier:** Realtime relay handles the short lease announcement and final spoken receipt; a cheaper background planner performs extraction and task work; no model should retain raw source contents after lease expiry.
- **latency:** Lease creation and spoken acknowledgement under 1 second; ordinary extraction under 15 seconds; destruction receipt within 2 seconds of completion or cancellation.
- **cost:** Approximately $0.02–$0.15 per task, dominated by source extraction and planner context; storage should be ephemeral and low cost.
- **security:** This intentionally grants one task access to sensitive browser and filesystem data. Enforce source allowlists, per-task encryption keys, hard TTLs, redaction of credentials, and an immutable receipt containing source identifiers, not contents. Failure to destroy must be surfaced immediately.
- **missing:** A relay-side ephemeral context vault with cryptographic per-task keys and enforced TTL deletion; Browser and Mac connectors that return source identifiers plus bounded excerpts under a lease ID; A deletion attestation and dashboard view proving expiry, including cleanup after worker or Mac failure


## What it asked for

_Nothing._
## Its own summary

Recorded three new owner-facing capabilities: (1) one-utterance end-to-end handling of the active browser/Mac context with cited cross-surface receipts, (2) a live spoken show-me-and-do-it-with-me session using Mac screen diffs plus authenticated browser state, and (3) a temporary auditable data lease spanning selected browser tabs and Mac files with automatic destruction. The most useful is the first: it turns the wearable into a context-aware operator rather than a voice-only dispatcher.

**Biggest unknown:** Whether the named Mac source-inspection routes actually exist in the live Mac router; the recorder flagged them as not fully inventoried. The other required gaps are explicit: active-context resolution, durable cross-surface workflow correlation, realtime screen/audio session transport, and an enforceable ephemeral context vault with deletion attestation.

