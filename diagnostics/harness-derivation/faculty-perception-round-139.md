# Harness derivation — faculty-perception — round 139

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live permissions and surfaces** — At 2026-08-08T01:28Z, the exact AI Pendant Agent identity reports Accessibility trusted, Screen Recording granted, requiredMissing empty, ready true; AppleScript automation grants are cached for System Events, Finder, Calendar, Mail, Notes, Messages, Safari, Chrome, Edge, Music, Preview, TextEdit, VS Code, Cursor, Terminal, Warp, iTerm, System Settings. Browser extension is online with Safari tab 1148327 on platform.openai.com (9 tabs, 0 pending commands). Relay is reachable and D1-backed with mac bridge online. No pendant is present in the live device table.
  - evidence: GET /ops/status and GET /browser/status returned HTTP 200 at 2026-08-08T01:28Z; discover:devices lists only home-macbook-bridge online and cloudflare-contract-test offline.

## Capabilities it proposed

### "Before you act, tell me whether you can actually verify the result—not just whether the command was accepted."
- **useful because:** The owner gets a plain-language trust verdict for consequential work: independently observed preconditions, action execution, and post-state agree; if they conflict, the system stops claiming success and names the missing witness. This is more useful than another job status because it fuses the worn capture quality, relay trace, Mac receipt, and browser observation into one reality judgment.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** background for assembling evidence; realtime only to explain a verdict during the voice turn
- **latency:** Under 2 seconds for existing receipts/status; up to 8 seconds when a fresh Screen Recording visual observation is needed
- **cost:** Usually <$0.01 using structured evidence; a fresh vision verification dominates and costs one computer-use model call
- **security:** Evidence must be scoped to the requested action and redact page secrets; visual screenshots stay on the Mac unless explicitly summarized. Require confirmation before using a low-confidence verdict to trigger irreversible work.
- **missing:** A common evidence-envelope schema and quorum/contradiction evaluator across pendant quality frames, relay events, Mac action receipts, and browser results; A Mac post-state observer that records a bounded visual hash/summary after /execute; A dashboard and voice formatter for verified / partial / contradicted / unobservable states

### "What changed on my computer after you did that? Show me only the relevant before-and-after difference."
- **useful because:** Today receipts can say an action ran, but the owner still has to inspect the screen. A bounded semantic diff across the browser, Finder, and the target app would let them catch a wrong account, wrong tab, or silent no-op immediately—especially now that this exact agent has Accessibility and Screen Recording permission.
- **path:** mac-planner → mac-vision → browser-extension → dashboard → relay-realtime
- **model tier:** mac-vision for screenshot-to-diff extraction; cheaper text model for naming the delta; realtime only for spoken summary
- **latency:** 2–5 seconds after an action, with a 10-second fallback for a fresh app observation
- **cost:** One vision call per requested diff; roughly $0.01–$0.05 depending on screenshot size; most of the time is local capture, not API
- **security:** Capture only the target window/tab and redact passwords, payment fields, and hidden tabs before any model call. Persist hashes and a short diff, not screenshots, by default. Ask before exposing sensitive changes aloud.
- **missing:** A target-aware before/after capture hook around mac_run_actions and browser commands; Semantic diff records linked to existing action receipts and browser provenance capsules; A redaction pass that operates before screenshot upload, plus owner-facing diff UI

### "My pendant is unavailable—continue the conversation on the Mac, and when it comes back, give me only what I missed without repeating anything."
- **useful because:** The system should degrade gracefully instead of pretending the wearable is reachable: the relay can keep the intent alive, the Mac can speak/display the result now, and a future pendant can receive a compact, deduplicated handoff. This turns the current no-pendant state into a useful mode rather than an outage.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background for handoff compaction and deduplication; realtime only for the immediate spoken fallback
- **latency:** Fallback on Mac within 2 seconds; reconnect handoff assembled within 5 seconds of a verified pendant heartbeat
- **cost:** <$0.01 per handoff using stored structured events; TTS/vision are the dominant optional costs
- **security:** Do not claim the pendant heard the item; mark every handoff as pending until a device-originated receipt exists. Encrypt queued summaries, expire them by owner policy, and require confirmation for actions resumed after a long disconnect.
- **missing:** A session-migration state machine keyed by conversation and action IDs, with explicit absent/unreachable/returned states; A Mac fallback speech/display route and a reconnect merge that consumes existing briefing fingerprints without treating them as heard; A real pendant heartbeat/identity path and device-originated handoff receipt; the current registry absence is structural and no pendant is live

### "Before you do this, show me the plausible consequences—including the one you think is most likely—and let me choose among them."
- **useful because:** The owner can make informed choices before an ambiguous computer or browser action changes files, accounts, messages, or purchases. This is a counterfactual impact preview, not a completion receipt: it explores likely post-states and exposes uncertainty before anything is committed.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** background planner for scenario generation; realtime only to present the small set of consequences and collect the choice
- **latency:** 3–8 seconds for a bounded preview; never block on an open-ended simulation
- **cost:** One structured planning call, typically under $0.03; visual/browser state extraction is the dominant cost when needed
- **security:** Simulation must be read-only and must not send messages, submit forms, or mutate files. Treat credentials and private page content as local-only inputs. Require explicit confirmation of the selected scenario before execution.
- **missing:** A read-only action simulator that can model AppleScript, filesystem, browser, and app side effects without invoking them; A typed consequence graph with affected objects, reversibility, confidence, and assumptions; A planner contract distinguishing observed state from hypothetical state so speculative outcomes cannot enter memory as facts

### "Why do you believe that? Show me the evidence chain, what may be stale or conflicting, and let me correct the source you should trust."
- **useful because:** The owner can challenge a conclusion instead of accepting an opaque answer. The system would connect a spoken claim to its originating browser region, Mac file or app state, relay event, and capture time, then distinguish observed evidence from inference and preserve the owner's correction for future judgement.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** background evidence linker and contradiction detector; realtime only for the owner's follow-up question
- **latency:** Under 3 seconds for an existing chain; up to 10 seconds to collect fresh corroboration
- **cost:** Usually under $0.02 using stored hashes and metadata; fresh vision or web reads dominate
- **security:** Never speak secret snippets aloud; show sensitive evidence only on the Mac after confirmation. Corrections need provenance and versioning so an untrusted assertion cannot overwrite an observed fact. Expire evidence bodies while retaining safe hashes and revocation tombstones.
- **missing:** A claim ledger joining model statements to evidence capsules, pipeline events, action receipts, and browser provenance; A freshness/conflict evaluator that can request a second independent observation; An owner correction workflow with scoped trust changes rather than global source promotion

### "Learn how often each app, browser tab, and device is wrong for me, and warn me when you are relying on a source that has a bad track record."
- **useful because:** The owner gets personalized reliability rather than a universal trust ranking. For example, a stale browser tab, a lagging calendar cache, or a Mac-side claim made while the wearable was absent can be down-weighted based on prior corrections, making future answers safer without requiring the owner to remember every failure.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background statistical learner; realtime only to state a concise warning when a reliability threshold is crossed
- **latency:** No added latency for normal turns; warnings computed from a local lookup under 100 ms
- **cost:** Negligible after initial implementation; occasional background model calls for clustering correction patterns, under $0.01 per correction batch
- **security:** Reliability scores must describe sources and contexts, not profile the owner. Keep raw corrections local, allow inspection/deletion, prevent one mistaken correction from globally disabling a source, and require confirmation before applying a severe penalty.
- **missing:** A versioned correction ledger keyed by source, context, and observation type; A calibration model that separates source unreliability from transient staleness and model error; A visible dashboard showing why a source was down-weighted and an owner control to reset it


## Changes it proposed to its own stack

### `model-routing` — Make live surface availability a hard input to routing: before any pendant-dependent response, read /ops/status and /browser/status; if no pendant is registered/healthy, route speech and action to the Mac/browser fallback, attach an explicit unobserved-pendant flag, and queue only a resumable handoff rather than attempting silent wearable delivery.
- **owner gets:** The owner gets an answer where they can actually receive it now and is never told that a nonexistent wearable heard something. When the pendant returns, the system can resume from a labeled checkpoint instead of replaying or losing the request.
- effort: Medium: router policy plus a small handoff record and tests for absent, stale, and reconnected devices.  ·  risk: A transient status race could choose the fallback just as the pendant reconnects; use a short grace period and make fallback idempotent. Recovery is to reconcile by request ID, not replay blindly.
- cost: Negligible API cost; one status read per turn, with cached status for a few seconds.  ·  latency: Adds roughly 50–150 ms locally; avoids long waits on an absent pendant.
- security: Improves truthfulness and reduces accidental speech to the wrong endpoint; status records must not expose device credentials.
- depends on: A durable request/handoff ID shared by relay and Mac; A device-originated heartbeat when firmware exists; current /v1/devices/status absence must remain an explicit state, not inferred offline; A defined fallback speech/display policy


## What it asked for

_Nothing._
## Its own summary

Recorded three distinct owner capabilities: counterfactual consequence previews before actions, inspectable claim-to-evidence chains with owner corrections, and personalized source reliability warnings learned from corrections. Each names the cross-surface changes required rather than pretending existing routes provide them.

**Biggest unknown:** Whether any of these collide with an unseen backlog entry; the recorder accepted all three, and no further discovery is available this round.

