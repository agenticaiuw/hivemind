# Harness derivation — relay-realtime — round 252

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Give me a one-sentence status of the thing I just asked for."
- **useful because:** The owner doesn’t want a verbose readout while walking. A quick spoken snapshot reduces cognitive load and keeps the interaction lightweight.
- **path:** relay → mac-bridge → pendant
- **model tier:** Realtime model to condense status into a single sentence.
- **latency:** Under 1 second for a short summary when job status is available.
- **cost:** Very low; dominated by a single job status fetch and a short summarization.
- **security:** Summaries can expose task details. Use minimal phrasing by default and avoid reading sensitive content unless asked.
- **missing:** A standard status vocabulary and summary rules shared with the Mac agent; Optional receipts access to include what changed

### "“Handle this for me end to end. If you hit a decision only I can make, ask me on the pendant, remember my answer, and continue without making me repeat the task.”"
- **useful because:** Today a delegated Mac/browser job either guesses through ambiguity or stops as an opaque job. This would make the wearable a real remote operator: the owner can leave the Mac, answer one precise follow-up by voice, and have the same job resume with its evidence and constraints intact. It is the single most useful missing capability because it turns all existing downstream reach into a dependable conversation rather than one-shot commands.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime relay for intent extraction and short clarification questions; mac-planner for planning and execution; browser harness for authenticated browser steps; a cheaper background model for summarizing job state and deciding whether a question is genuinely blocking.
- **latency:** Immediate acknowledgement under 1 second; clarification prompt under 3 seconds after a blocker; resume within 5 seconds of the owner's answer. Long execution is asynchronous.
- **cost:** About $0.01–$0.05 per clarification turn plus the existing planner/browser calls; cost is dominated by planner context and any repeated browser vision, not the short relay utterances.
- **security:** The relay must persist the original goal, pending question, candidate choices, and owner answer with provenance, and never silently reinterpret an answer as authorization for a different goal. Browser pages and local files may leave the Mac for planning; redact secrets. Destructive actions retain the owner's existing maximum-access policy but should produce a plainly spoken action trace and an undo/stop affordance.
- **missing:** A resumable job state machine with a first-class needs_owner_input state and correlation to the originating voice session; A pendant/phone delivery path that can turn a blocker into a question and route the next spoken answer back to the exact job; Planner support for emitting typed questions and consuming answers rather than returning only a terminal plan; A durable, scoped continuation context that uses the memory projection without leaking unrelated facts

### "“Stop the thing you’re doing right now,” or “pause it and show me what has already changed.”"
- **useful because:** A remote agent that can act while the owner is away needs an immediate brake, not merely a post-hoc undo. The pendant should identify the active job from the current conversation, halt queued Mac/browser work, collect the partial mutation receipt, and speak what did and did not happen. This is materially different from a completion notification: it protects the owner during execution and makes partial failure understandable.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime relay handles the short stop/pause command; a deterministic job controller cancels or pauses dispatch; mac-planner and browser harness acknowledge cancellation and return receipts; a cheaper summarizer produces the spoken partial-state report.
- **latency:** Acknowledge the stop in under 500 ms and prevent any new action within 1 second. Final partial-state summary within 5 seconds, subject to a downstream acknowledgement.
- **cost:** A few cents at most; the dominant cost is fetching downstream receipts or a final browser snapshot, not model inference.
- **security:** Cancellation must be idempotent and job-scoped, never interpreted as deleting evidence. Already-applied mutations must be listed honestly, and cancellation failures must be surfaced rather than claimed complete. The dashboard should retain an immutable event timeline.
- **missing:** A live cancellation/pause primitive understood by the Mac planner and browser command queue; An active-job binding in the relay so a terse spoken stop cannot target the wrong task; Downstream acknowledgement and a partial-effects receipt schema; Pendant handling for a high-priority control utterance while another response is playing

### "“Did that actually happen? Check everywhere you can and tell me what proves it.”"
- **useful because:** Current job status says what the orchestrator recorded, not whether the outside world agrees. A browser command can time out after a submission, or a Mac app can change state without a receipt. This capability would reconcile independent evidence from the relay job log, Mac state, authenticated browser DOM, and (when available) a fresh screenshot, then answer with a confidence level and the exact supporting observation. It prevents the owner from duplicating work or trusting a false success while away from the computer.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** A cheap background reconciliation model ranks and summarizes evidence; mac-planner/mac-vision and browser harness gather observations; realtime is used only to frame the owner's question and speak the short conclusion.
- **latency:** Speak an initial 'checking' acknowledgement immediately; return a concise answer in 5–15 seconds depending on whether the Mac and browser are reachable. Never substitute stale evidence without saying its age.
- **cost:** Roughly $0.01–$0.08 per check; browser snapshots and computer-use calls dominate, with model cost secondary.
- **security:** Authenticated page contents and screenshots stay scoped to the requested task and are not injected into generic conversation memory. Evidence must retain source, timestamp, and freshness; contradictory observations produce 'uncertain', not a fabricated yes/no. High-impact corrective actions remain a separate, explicit request.
- **missing:** A cross-surface evidence schema linking a user's goal to receipts, DOM observations, app state, and screenshots; A reconciliation endpoint that can fan out to Mac and browser surfaces and distinguish unreachable from negative evidence; Freshness/conflict scoring and a spoken citation format suitable for one-button interaction; A way to preserve evidence artifacts for dashboard inspection without storing sensitive page content by default


## Changes it proposed to its own stack

### `integration` — Add a USB-local transport mode that lets the physically connected nRF9160 pendant and ESP32 bridge hand audio to a small localhost companion on the Mac, with the companion forwarding to the cloud relay when reachable and buffering a session transcript/response envelope when it is not. The pendant should advertise transport health and switch back to LTE without duplicating a turn, using a monotonic conversation/session id and acknowledgements.
- **owner gets:** The hardware is plugged into the owner's Mac today but is not LTE-registered, so a conversation can fail in the exact setup used for development and at a desk. The owner gets a pendant that works immediately over USB, then continues seamlessly when they walk away, rather than having to know which radio is alive or repeat a thought.
- effort: Medium-high: a signed localhost companion, serial framing and reconnect state machine, relay session deduplication, and firmware transport selection. Hardware audio paths already exist; the missing work is coordination and failover testing.  ·  risk: A reconnect could duplicate audio or replay an old response. Use session/turn ids, relay-side idempotency, bounded failure-only storage, and an explicit 'not delivered' state. Never silently claim LTE continuity when only USB succeeded.
- cost: Low recurring API impact; the same audio/model calls are used. Engineering cost is several weeks across firmware, Mac bridge, and relay; no new hardware required.  ·  latency: USB should cut round-trip latency versus LTE by roughly a network hop; failover adds a few seconds only when transport changes.
- security: The localhost companion needs authenticated pairing and origin restrictions; audio must not be exposed to arbitrary Mac processes. USB is a trusted physical link but still needs a per-device session key.
- depends on: A small Mac USB companion service with authenticated serial access; A relay protocol carrying idempotent session/turn identifiers and transport-health acknowledgements; Firmware support for selecting USB versus LTE while preserving the existing failure-only SD rule; A surfaced transport indicator compatible with the single existing LED and spoken status


## What it asked for

_Nothing._
## Its own summary

Recorded four owner-facing gaps: resumable delegated work with precise voice clarification; an immediate pendant stop/pause with honest partial effects; cross-surface evidence reconciliation for whether an action really happened; and a USB-local pendant/Mac transport that fails over cleanly to LTE. The first is the highest-value capability: it turns one-shot automation into a remote operator that can finish real tasks while the owner is away. Each proposal names the missing state, protocol, or integration rather than treating existing routes as a finished feature.

**Biggest unknown:** Whether the existing job/execute implementation already has an undocumented cancellation primitive and whether the Mac bridge can currently expose the live pendant serial stream to a localhost companion. Those two facts determine how much of the stop control and USB-local mode is new engineering versus wiring.

