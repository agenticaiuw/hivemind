# Harness derivation — faculty-perception — round 55

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac input reachability** — As of 2026-08-07T11:58:17Z, /observe reports Accessibility trusted=false, Screen Recording=false, inputReachability.status=failed, eventsPost=false, and uiActionsWillReachTheScreen=false. It explicitly says synthesized events are rejected because Accessibility is granted to a different binary than the running com.aipendant.agent process.
  - evidence: GET /observe returned HTTP 200 with accessibility and inputReachability fields.
- **mac relay status** — As of 2026-08-07T11:58:17Z, Mac bridge is online and relay reachable; relay reports pendantPipelineTelemetry, pendantSpeech, persistentAgentState, and durableAudio true.
  - evidence: GET /ops/status returned HTTP 200; relay.payload and macBridgeOnline fields.
- **browser reachability** — As of 2026-08-07T11:58:17Z, home-chrome browser extension is offline with 5 pending commands; three durable browser sessions remain listed by /observe.
  - evidence: GET /browser/status and GET /observe returned HTTP 200.

## Capabilities it proposed

### "“Before I ask you to do anything, tell me what you can genuinely see and control right now—and warn me if any device is pretending to be online.”"
- **useful because:** The current system can report raw health, but the owner cannot distinguish a reachable relay from an unusable Mac UI or a stale browser queue. A concise spoken truth report prevents false confidence: it would say, for example, relay and pendant telemetry reachable, Mac UI actions untrusted because TCC failed, browser offline with five queued commands, and when each observation was last confirmed. This is specifically a cross-node perception function, not an action planner.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → faculty-perception
- **model tier:** Cheaper background/text model to aggregate typed status; realtime only speaks the already-computed report when asked. No vision or expensive inference.
- **latency:** Under 1 second when all local endpoints respond; stale components should be reported with age rather than blocking. Refresh only on request or before a risky action.
- **cost:** Near-zero model cost for a typed aggregation; roughly 1–2k input tokens and <300 output tokens only when natural-language rendering is needed. Dominant cost is endpoint polling, not inference.
- **security:** Do not expose bearer tokens, private URLs, account data, or raw process lists. Return capability classes and freshness, not secrets. Never infer control from a queued command or an optimistic receipt; require /observe inputReachability and permission readiness. Mark stale/unknown rather than guessing.
- **missing:** A unified typed perception snapshot with per-surface last-confirmed timestamps, freshness TTLs, and confidence/contradiction fields; A relay/pendant endpoint or tool that exposes this snapshot to the spoken agent; Browser heartbeat recovery or explicit queue-age semantics so offline pending commands cannot look active

### "“When you are looking at my screen, listening, or about to act through my logged-in browser, show me that state on the pendant—and let me cancel it with one press.”"
- **useful because:** The owner gets a physical, glanceable privacy and agency signal that does not depend on the Mac window, browser tab, or spoken response. A distinct LED/haptic pattern can mean listening, screen capture, browser session access, pending external action, or cancelled; a long-press can revoke capture/action authority even if the Mac UI is stuck or the voice link is delayed. This is a new physical trust boundary, not another activity log or confirmation dialog.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** No model for state signalling or cancellation. The realtime model may interpret the owner's spoken follow-up, but the pendant state machine and relay should be deterministic.
- **latency:** LED/haptic state change within 150 ms of a capability transition; cancellation must be locally acknowledged immediately and propagated within 1 second. If disconnected, the pendant must remain in a clearly marked offline/safe state.
- **cost:** Negligible API cost. Hardware change is modest: one RGB status LED or a small multi-pattern RGB indicator plus a stronger vibration/gesture path if the present I/O cannot distinguish states; roughly $2–8 in a new revision and under 10 mW while indicating.
- **security:** The pendant must default to non-capture/non-action on boot and link loss; cancellation must be enforced by relay, Mac agent, browser bridge, and pending-job queues, not merely displayed. Do not expose page titles or secrets through LED patterns. Every transition needs an immutable timestamped event so a compromised/stale node cannot claim it was cancelled when it was not.
- **missing:** A capability lease protocol: short-lived signed leases for microphone, screen observation, browser-session access, and external action, each revocable by the pendant; Firmware state machine and local cancel interrupt that survives a dropped relay link; Relay fan-out of lease revocation to Mac, vision loop, browser extension, and durable jobs, with acknowledgement quorum and explicit unresolved state; A hardware status indicator/feedback path with enough distinct patterns to separate listening, observing, acting, and revoked


## Changes it proposed to its own stack

### `context` — Add a perception contradiction ledger between the relay and faculty-judgement. On every observation, normalize each surface into capability claims (reachable, authenticated, action-safe, evidence-fresh), compare claims from /ops/status, /observe, /browser/status, /pipeline, and relay heartbeat, and persist only contradictions with source timestamps and expiry. For example, classify fullControlMode=true plus permissions.ready=false plus uiActionsWillReachTheScreen=false as 'planning available, UI execution unsafe' rather than allowing a generic online flag. Make the ledger append-only and expose a compact signed witness to judgement; automatically expire it when the next probe is older than its TTL.
- **owner gets:** The owner stops hearing confident but false confirmations when a component is technically online yet unable to act. After a permission repair, stale warnings naturally clear; if browser heartbeat dies, queued commands become visibly stuck instead of silently pending.
- effort: Medium: typed schema, probe scheduler, contradiction rules, expiry tests, and relay-to-judgement projection. No new model training.  ·  risk: A bad rule could over-quarantine a useful path or leave the owner with too many warnings. Recover with conservative defaults, source-linked explanations, manual re-probe, and automatic expiry; never turn a contradiction into an action refusal without judgement policy.
- cost: Negligible storage and polling cost; no model call required except optional natural-language rendering.  ·  latency: Adds tens of milliseconds to planning when a fresh snapshot exists; first probe may take up to about 1 second.
- security: Ledger must omit bearer tokens, private URLs, raw page data, and process details; sign only capability claims and timestamps. Contradiction history itself may reveal device state, so retain briefly.
- depends on: Exact TCC identity repair and restart are still needed before the Mac UI claim can become safe; browser heartbeat recovery is needed before browser reachability can become fresh; a shared typed snapshot schema between relay and Mac agent.

### `firmware` — Add a pendant-local safety lease state machine with four signed states—idle, listening, observing, acting—and a hard revoked/offline state. A long press or dedicated cancel gesture immediately cuts local microphone forwarding, emits a revocation sequence number, and prevents any queued command from being acknowledged as active until the relay and every downstream executor confirms the same sequence. Persist only the current state, sequence, and last transition (well under 4 KB); on reboot or link loss enter revoked/offline rather than replaying an old permission.
- **owner gets:** The owner can physically stop the system even when the Mac is frozen, the browser bridge is disconnected, or a cloud response is late. They can trust that 'cancelled' means no new audio, screen observation, or browser action will begin after the gesture—not merely that a UI label changed.
- effort: Medium firmware and protocol work, plus relay/Mac/browser acknowledgement handling and fault-injection tests for link loss, reboot, duplicate revocations, and stale receipts.  ·  risk: A false gesture or lost acknowledgement could leave work paused or ambiguous. Use a deliberate long press, local haptic confirmation, monotonic sequence numbers, idempotent revocation, and an explicit 'revoked but downstream unconfirmed' indication; never silently resume.
- cost: No per-call API cost; firmware storage under 4 KB and low-power state checking. If the current pendant lacks sufficient feedback, a board revision with RGB LED/stronger haptic is roughly $2–8 BOM increase and under 10 mW while signalling.  ·  latency: Local safety transition under 150 ms; downstream cancellation target under 1 second, with safe local enforcement not waiting on the network.
- security: This creates a stronger local authority boundary: relay and executors must reject leases older than the pendant's revocation sequence. Lease metadata must contain no page content, account identifiers, or audio.
- depends on: A shared signed capability-lease format across pendant, relay, Mac agent, and browser bridge; A relay fan-out and acknowledgement route for revocation; An explicit distinction between cancellation acknowledgement and action completion in job/browser receipts; Possibly a hardware indicator upgrade if existing LED/button combinations cannot communicate all states


## What it asked for

_Nothing._
## Its own summary

Fresh discovery completed. The exact grants have not taken effect in the running agent: /observe at 2026-08-07T11:58Z says Accessibility trusted=false, Screen Recording=false, inputReachability failed, eventsPost=false, and UI actions will do nothing; /ops/status says permissions.ready=false. Relay and Mac bridge are reachable with pendant telemetry/speech/state/audio capabilities, but home-chrome is offline with 5 pending commands. I recorded these facts, warned judgement/action/planner not to trust UI receipts, proposed an owner-facing reachability report, and proposed a contradiction ledger that classifies 'online' versus genuinely action-safe and expires stale claims. Still needed: repair TCC for the exact running com.aipendant.agent app and its node executable, restart/reprobe until inputReachability=ready and permissions.ready=true; restore browser-extension heartbeat and resolve or age out its 5 queued commands. Do not claim Mac UI control before those probes pass.

**Biggest unknown:** Whether the orchestrator's permission grant targeted a different app identity or whether macOS requires a full agent restart/login before TCC state changes; current live evidence still proves the exact process is not trusted.

