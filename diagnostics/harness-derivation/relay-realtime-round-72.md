# Harness derivation — relay-realtime — round 72

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Research this for me across my open browser tabs and Mac files, but keep me in the loop: tell me what you’ve found as you go, and let me say ‘focus on pricing’, ‘skip that source’, or ‘stop’ while it is still running.”"
- **useful because:** Today a request is either a synchronous tool handoff or an opaque queued job. The owner cannot steer a multi-surface investigation from the pendant while away from the Mac, nor reliably know which browser/Mac evidence produced the answer. This would make the wearable a genuine conversational control surface for work distributed across authenticated browser sessions and the Mac.
- **path:** pendant → relay → browser-extension → browser → mac-planner → mac-terminal → dashboard
- **model tier:** Realtime handles only the short spoken updates, intent changes, and stop/steer commands. A cheaper background planner performs the research and merges evidence; mac-vision remains an optional fallback for pages that cannot be read structurally.
- **latency:** Acknowledge a steer/stop in under 500 ms and stop dispatching new work within 2 s. Deliver an initial progress brief within 5 s, then event-driven spoken updates rather than polling every turn. Full research may take minutes.
- **cost:** Roughly $0.01–$0.08 per investigation depending on the background model and number of browser/Mac reads; realtime cost is limited to perhaps 3–10 short utterances. Browser and Mac extraction, not speech, dominate.
- **security:** Authenticated page contents and local files leave their respective surfaces only to the relay/planner and are retained in an encrypted, expiring evidence bundle. The owner must be able to say “stop and delete this run”; mutations remain opt-in and are not implied by research. Progress updates must cite source surface/title and distinguish observed facts from inference.
- **missing:** A durable, cancellable fan-out job with a per-run event stream and sequence numbers; A relay voice-session command that targets an existing run (steer, skip source, pause, resume, stop, delete); Browser and Mac adapters that emit incremental typed evidence rather than only final results; A merge/ranking layer that can revise conclusions when the owner changes criteria; Pendant delivery of short progress alerts while the live voice turn is no longer open; Dashboard controls to inspect the evidence timeline and recover an interrupted run

### "“For the next hour, let this task use my logged-in browser and my project folder, then forget that access; tell me if it tries to reach anything else.”"
- **useful because:** The owner currently has to trust a whole always-on surface or manually arrange context. A spoken, expiring context lease would let the pendant delegate exactly the browser session and Mac workspace needed for one task, even while away, with automatic revocation and an auditable record. It is useful for sensitive work without imposing confirmation gates on ordinary reversible actions.
- **path:** pendant → relay → browser-extension → browser → mac-planner → mac-terminal → dashboard
- **model tier:** Realtime parses the short lease request and reports scope violations or expiry. A cheaper policy/coordination worker mints, propagates, and revokes leases; downstream models do the actual work.
- **latency:** Lease acknowledgment under 1 s; propagation to browser and Mac under 3 s; revocation should take effect within 5 s even if one surface is temporarily offline, with queued revocation on reconnect.
- **cost:** About $0.002–$0.02 per lease, dominated by short realtime interpretation and audit writes; no model call is needed for renewal or revocation.
- **security:** Never transmit raw cookies, passwords, or filesystem credentials through the relay. Use opaque capability tokens bound to task, surface, resource patterns, expiry, and owner/device identity. Log every attempted access and report denied scope succinctly on the pendant. Offline surfaces must fail closed after lease expiry; the owner can say “revoke that lease” at any time.
- **missing:** A capability-token issuer and verifier shared by relay, local Mac agent, and browser extension; Resource-pattern scopes for browser origins/tabs and Mac paths/apps, with explicit expiry and revocation epochs; A device-bound lease handshake so a replayed voice transcript cannot mint access; Browser and Mac adapters that attach lease metadata to every read/action and return scope-denial events; A compact pendant command vocabulary for listing, narrowing, and revoking active leases; Dashboard UI for the owner to inspect lease history and emergency-revoke all leases


## Changes it proposed to its own stack

### `model-routing` — Add a minimal, typed relay intent envelope and status reporting convention so the relay can route to mac-planner or browser work without inventing per-task phrasing. The envelope would include: intent label, normalized utterance, target surface, urgency, and a correlation/job id if continuing an existing job.
- **owner gets:** The owner gets consistent behavior and faster handoffs. Saying “open my project notes” or “check that order status” doesn’t depend on fragile prompt phrasing; it reliably reaches the right place and reports back in a predictable way.
- effort: Medium. Define intent schema, map to existing tool calls (mac_delegate, browser_run_actions, web_search), and add status callbacks using existing job receipts.  ·  risk: Misrouting could do the wrong thing. Mitigate with conservative defaults: read-only actions first; only reversible actions without approval; require explicit approval for irreversible changes.
- cost: Low. Mostly schema and mapping; small added metadata per request.  ·  latency: Improves. Less back-and-forth; quicker routing decisions.
- security: Neutral to positive. Typed intent makes logging and auditing clearer; ensure sensitive utterance content is handled per existing privacy rules.
- depends on: No scheduler required. Uses existing plan/execute and receipts. Durable continuation remains a separate missing capability.


## What it asked for

### `c14-g3ie` (context) — granted tools that appear in the 'granted' category but are not describable via describe(name)
- why: The granted list includes relay_route_intent and server_browser_actions, but describe(name) says they are not found. I need to know if these are separate tool names, aliases, or documentation gaps so I can call the correct tool and not invent a protocol.
- would change: If they are aliases for existing tools or already represented by functions in this harness, I will use the correct callable name. If they are not actually available, I will avoid calling them and propose the missing tool wiring instead.

## Its own summary

Recorded two proposals. The strongest genuinely missing capability is an expiring, spoken context lease: the owner can delegate a specific browser session and Mac workspace to one task, revoke it by voice, and have every downstream read/action carry the lease and produce an audit trail. I also recorded conversational steering of a distributed research run, though the orchestrator flagged that as close to existing job plumbing and it needs to be differentiated as incremental event streaming/cancellation rather than treated as wholly new.

**Biggest unknown:** Whether /state/:stateKey and the existing job/session routes already carry any scope, cancellation, or event-stream semantics; this round was explicitly not allowed further discovery.

