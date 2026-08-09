# Harness derivation — faculty-perception — round 179

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac and browser reachability** — At 2026-08-08T04:49Z the Mac agent is fully ready: Accessibility and Screen Recording both granted, all required permissions present, computer-use loop enabled with vision configured, relay reachable and D1-backed. Safari bridge is online with 2 tabs, active Google Maps tab, 0 pending commands and 0 spooled commands.
  - evidence: GET /ops/status HTTP 200 and GET /browser/status HTTP 200; response reports permissions.ready=true, accessibility.trusted=true, screenRecording.granted=true, browser online=true, tabCount=2, pendingCommands=0, spooled=0.
- **continuity snapshot grant resolution** — The granted read_continuity_snapshot tool is not actually resolvable in the live capability resolver: it scored below the route threshold and returned no implementation. The nearest live route is GET /ops/snapshot, so a single authenticated cross-surface continuity read remains unavailable as a tool.
  - evidence: read_continuity_snapshot call returned error 'could not be resolved', nearest capabilities GET /ops/snapshot score 0.447 and GET /pipeline score 0.443.

## Capabilities it proposed

### "“Is this page telling me the truth, and if so do the next thing?”"
- **useful because:** This is the first capability that joins the private browser, the acting Mac, the relay, and the wearable into one trustworthy loop: it can inspect the page the owner is actually signed into, distinguish observed text from model inference, and refuse to act when the evidence is stale or ambiguous.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Realtime only for the spoken request and final concise answer; Mac vision/browser extraction uses the cheaper background computer-use tier, with the judgement tier invoked only when the requested action has consequences.
- **latency:** 3–6 seconds for capture and extraction, then an explicit spoken confirmation before any irreversible action.
- **cost:** Roughly $0.03–$0.15 per invocation depending on screenshot/vision steps; browser and Mac execution dominate latency, not the final spoken response.
- **security:** Private page contents must remain on the Mac unless the owner explicitly allows relay processing. The extension classifies/redacts credentials, payment data, and messages; every claim carries URL, tab, capture time, and content hash. No action proceeds from an expired, revoked, or ungrounded capsule; joining or submitting requires confirmation.
- **missing:** A relay-to-Mac evidence handoff that returns a stable capsule ID and hash for relay-originated reads; A judgement gate that consumes capsule freshness/revocation and grounded claims before action; A compact spoken citation format for the pendant

### "“When I come back, tell me only what changed on the private pages I care about—and show me which changes are real.”"
- **useful because:** A useful return-from-absence briefing should not repeat stale notifications. It should compare authenticated Safari pages against content-addressed captures, suppress cosmetic churn, and let the owner ask the pendant about one change with an honest source and age.
- **path:** browser-extension → mac-planner → relay-realtime → relay → faculty-perception → faculty-judgement → pendant
- **model tier:** Background scheduled extraction and hashing; cheap text classification for change categories; realtime model only when the owner asks a follow-up by voice.
- **latency:** Heartbeat/capture under 1 second per watched page, digest generated in under 10 seconds after reconnect, spoken follow-up under 2 seconds.
- **cost:** Low when DOM extraction and local hashing are used; approximately $0.01–$0.05 per changed page for classification, with no model call for unchanged pages.
- **security:** Private page bodies remain on the Mac by default. Store only hashes, bounded redacted snippets, URL origin, tab pseudonym, and capture times. Never send credentials, payment fields, or message bodies to the relay. A stale browser lease must produce 'could not verify' rather than a false unchanged result.
- **missing:** A durable watch scheduler that can run against authenticated Safari tabs without requiring a voice turn; A relay-visible, signed change receipt joining the Mac capsule to the spoken digest; A real cross-surface snapshot implementation; the currently granted read_continuity_snapshot does not resolve in the live resolver

### "“I’m driving/walking—keep an eye on this route and warn me through the pendant if the plan changes.”"
- **useful because:** The browser knows the authenticated route and live map context, the Mac can observe changes without the owner touching a screen, the relay can schedule low-cost checks, and the pendant can deliver a short interruption only when a meaningful delay, reroute, or arrival condition occurs.
- **path:** browser-extension → mac-vision → mac-planner → relay → relay-realtime → faculty-perception → faculty-judgement → pendant
- **model tier:** Scheduled/background browser polling and deterministic route-delta logic; realtime is used only to phrase an alert or answer a spoken question.
- **latency:** Poll every 30–60 seconds while active; route-change alert within 10 seconds of a confirmed change; no alert for cosmetic map movement.
- **cost:** Usually near-zero for DOM/accessible-tree deltas; approximately $0.01–$0.04 per meaningful change when vision or language classification is needed.
- **security:** Location and destination are highly sensitive. Keep exact coordinates and signed-in map data on the Mac; send only a coarse event ('ETA +18 min', 'route changed') to the relay. Require a spoken start/stop and auto-expire after the trip; never click reroute, call, or message anyone without confirmation.
- **missing:** A route-watch primitive bound to a Safari tab/session with a clear owner-visible lease; A deterministic semantic diff for Maps ETA/route state rather than screenshot-only comparison; Pendant delivery when the nRF9160 is actually registered; today the registry has no pendant

### "“Before you send or submit anything important, require proof that it is really me: my pendant, this Mac, and the currently signed-in browser session.”"
- **useful because:** Today any one authenticated surface can be mistaken for the owner's intent. A three-surface presence quorum would protect purchases, messages, account changes, and submissions while remaining fast for ordinary reversible work. The owner gets a clear spoken reason when one factor is missing instead of a silent refusal or an unsafe action.
- **path:** pendant → relay-realtime → relay → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Deterministic policy and cryptographic verification; use the realtime model only to explain the checkpoint in one sentence. No language model should decide whether the quorum is satisfied.
- **latency:** Under 500 ms when all three leases are fresh; otherwise pause and ask the owner, never wait indefinitely.
- **cost:** Negligible model cost; a few signed nonce exchanges and local checks per protected action.
- **security:** The pendant must sign a one-time challenge locally without exposing its long-lived key. The Mac and extension each attest their current process/session and bind the nonce to the exact target, tab, and action digest. Replay, tab switching, stale heartbeats, and relay compromise must fail closed. The owner must be able to designate low-risk actions that do not require quorum.
- **missing:** A hardware-backed pendant signing key and challenge-response firmware endpoint; Mac-agent and Safari-extension attestation bound to a target action digest, not merely liveness heartbeats; A relay policy evaluator and receipt that records which factors approved or denied an action; An owner-facing policy editor for action risk classes

### "“If I lose my phone, laptop, or browser session, keep my place and let me resume the exact task from the pendant without repeating myself.”"
- **useful because:** The owner should be able to walk away from a half-finished real-world task—an application, booking, research comparison, or form—and resume safely from whichever surface is still alive. Today jobs, browser tabs, and spoken context are separate, so a dropped session loses the task's exact state and safe next step.
- **path:** pendant → relay → relay-realtime → mac-planner → browser-extension → mac-vision → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Background state capture and deterministic reconciliation; realtime only interprets the owner's resume request and speaks the next checkpoint.
- **latency:** Resume status under 2 seconds; reconstruction up to 10 seconds for a complex browser task, with no automatic mutation until the owner confirms the recovered checkpoint.
- **cost:** Low: local state hashing is free; approximately $0.02–$0.10 only when vision is needed to reconstruct a changed page.
- **security:** Persist a redacted task graph, not raw passwords or form contents. Bind each checkpoint to tab/session identity, page hash, and expiry; if any differs, mark the step needs-review. Never replay a submit/click merely because it was pending before disconnection.
- **missing:** A cross-surface task checkpoint format joining browser state, Mac action ledger, relay job, and pendant conversation sequence; A durable encrypted checkpoint store with bounded retention and explicit owner deletion; A reconciliation engine that can classify a checkpoint as resumable, changed, or unsafe; Pendant-side selection of one of several resumable tasks

### "“Notice when I am overwhelmed, reduce interruptions across every surface, and bring me one prioritized spoken decision when I am ready.”"
- **useful because:** The owner's attention is the scarce resource. A wearable, browser, Mac, and relay together can detect an interruption storm—rapid tab switching, unfinished actions, repeated failed attempts, queued announcements, and speech-quality degradation—then suppress noncritical alerts and present one reversible next choice. No single surface can see the whole load today.
- **path:** pendant → relay-realtime → relay → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Deterministic event aggregation and owner-configured thresholds first; a cheaper background model clusters related interruptions; realtime speaks only the final two-sentence decision card.
- **latency:** Detect a burst within 15 seconds; quiet-mode changes within 2 seconds; digest on demand under 3 seconds.
- **cost:** Usually negligible; approximately $0.01–$0.05 per digest when clustering heterogeneous events is needed.
- **security:** Behavioral signals are sensitive. Store coarse counts and event categories, not raw screen recordings or transcripts. Quiet mode must never suppress emergency or explicitly high-priority alerts. The owner needs a physical-button override and a visible audit of what was deferred.
- **missing:** A cross-surface attention-state model with configurable thresholds and explicit uncertainty; A relay-level policy that can pause announcements and browser/mac proactive work without cancelling it; A pendant-local quiet-mode control that survives link loss; A resumable priority queue that explains every suppressed item


## Changes it proposed to its own stack

### `integration` — Make the granted read_continuity_snapshot capability resolve to a real authenticated GET /ops/snapshot adapter, returning a bounded, timestamped union of pendant/relay/Mac/browser/pipeline/permission facts and explicit unknowns. Keep the current route as the source of truth, but publish an exact tool name/schema in the capability manifest so the resolver cannot fall through at score 0.447.
- **owner gets:** When the owner asks “what happened while I was away?”, the system can answer once from a coherent snapshot instead of silently failing or stitching together stale endpoints. It can say 'unknown' where evidence is absent rather than inventing continuity.
- effort: Small integration change: route alias/schema registration, adapter mapping, and an end-to-end resolver test.  ·  risk: A malformed adapter could make a partial snapshot look complete. Include per-source freshness and availability, preserve unknown states, and fail closed if any requested source is not readable.
- cost: Negligible API cost; one bounded local HTTP read.  ·  latency: Typically under 300 ms on the Mac agent.
- security: No new authority; retain bearer authentication and redact page/audio contents from the snapshot.
- depends on: The existing GET /ops/snapshot route; The existing read_continuity_snapshot schema and include enum; A test fixture for absent pendant and offline relay-device cases


## What it asked for

_Nothing._
## Its own summary

Established fresh live truth: the exact AI Pendant Agent now has Accessibility and Screen Recording, all required permissions are ready, computer-use vision is enabled, relay is reachable with D1, and Safari is online with two tabs (active Google Maps), zero pending commands, and zero spool backlog. I recorded three new owner-facing capabilities: evidence-grounded private-page fact checking before action, verified change briefings for authenticated pages, and a privacy-bounded route-watch alert loop. The highest-value connective gap is not hardware now: the continuity snapshot grant is present in the prompt but fails live capability resolution, so 'what happened while I was away?' still cannot be answered through the promised one-call surface.

**Biggest unknown:** Whether a physical nRF9160 pendant is connected/registered remains unknown to this live Mac-agent surface; prior authoritative context says no pendant has registered. I still need a real resolver-backed continuity snapshot adapter and, for wearable delivery, actual pendant registration plus device-originated playback evidence.

