# Harness derivation — relay-realtime — round 221

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Tell me what’s going on right now: is my Mac online, is the browser connected, and what can you reach?”"
- **useful because:** The owner can quickly understand what’s reachable from the pendant without guessing why a request failed (Mac asleep, browser offline, relay-only).
- **path:** relay-realtime → mac-planner → browser-extension
- **model tier:** Realtime, because it’s a quick spoken status check.
- **latency:** Under a second when cached; a couple seconds if it needs live checks.
- **cost:** Low. Prefer cheap relay-side status reads; only query downstream when needed.
- **security:** Status metadata may reveal device names and activity. Keep it generic by default and avoid exposing sensitive session details.
- **missing:** A relay self-capabilities inventory route (the Mac has /capabilities; the relay does not); A unified health endpoint that summarizes relay + Mac + browser reachability for voice

### "“Start this task with me here, and keep the conversation alive if I walk away from my Mac; hand it from USB to LTE without making me repeat myself.”"
- **useful because:** The pendant is worn and the Mac is unattended. Today a live task is implicitly tied to whichever transport and surface happened to be available when it began; walking out of USB range can strand the conversation or force a restart. A true handoff would make the pendant the continuous front door rather than a Mac accessory.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Realtime for the handoff sentence and session identity; mac-planner/browser-extension continue the work asynchronously, with a cheaper background model for checkpoint reconciliation.
- **latency:** Under 300 ms to acknowledge a transport change; resume speaking within 2 s when LTE is usable. Most work continues in the background.
- **cost:** Roughly one short realtime turn at handoff, then normal delegated-task cost; dominant cost is the resumed planner/browser work, not the transport event.
- **security:** A session token must be bound to the paired pendant and rotated on handoff; never replay microphone audio. The relay must mark the exact last acknowledged action so a reconnect cannot duplicate a click, send, or purchase.
- **missing:** A transport-independent conversation/session record with monotonic audio and action sequence numbers; USB-serial and LTE-M adapters that can both attach to the same relay session; Idempotent action receipts and checkpoint replay across mac-planner and browser-extension; Firmware/relay handoff signaling and recovery tests while the owner physically walks away

### "“When you act on my Mac or in my browser, give me a spoken before-and-after that proves what changed, and let me ask ‘what exactly did you touch?’ without reopening the apps.”"
- **useful because:** A wearable user cannot inspect a screen or sift through logs. Existing completion/status mechanisms can say that a job finished, but they do not provide a compact, conversational evidence chain spanning Mac state and authenticated browser state. This would make remote actions trustworthy and debuggable from the pendant.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Cheaper background summarization builds a structured evidence bundle from receipts and observations; realtime only answers the owner’s follow-up and never invents a result absent in the bundle.
- **latency:** Immediate spoken acknowledgment; first evidence summary within 3 s of completion, with detailed follow-ups under 1 s from stored receipts.
- **cost:** One small background summarization per completed multi-surface job; storage and receipt extraction dominate, while follow-up speech is a short realtime turn.
- **security:** Evidence must redact secrets, cookies, page content outside the requested scope, and private app fields. Preserve immutable hashes/timestamps for the action and observation pair; expose uncertainty when a post-state could not be verified.
- **missing:** A normalized before/after observation schema shared by Mac and browser agents; Receipt storage that includes affected resource identifiers and verification observations, not only success/failure; Relay query endpoint keyed by job/session for spoken evidence follow-ups; Redaction policy and a pendant-friendly evidence renderer

### "“I’m leaving now—finish preparing this across my browser and Mac, but stop at the first irreversible step and tell me exactly what is waiting for me.”"
- **useful because:** The owner routinely leaves the Mac while wearing the pendant. Today delegation either executes a plan or reports a job; it cannot intentionally drive a mixed workflow to a named boundary, preserve all preparatory work, and surface a precise next action when the owner is away. This turns the wearable into a safe remote desk without requiring a blanket confirmation policy.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Background planner performs reversible preparation and a deterministic boundary evaluator; realtime is used only to announce the boundary and answer a short clarification. No expensive model is spent polling idle work.
- **latency:** Acknowledge and state the boundary in under 500 ms; preparation may take minutes and must survive disconnects, with an inbox alert when it reaches the boundary.
- **cost:** One delegated planning call plus ordinary Mac/browser action costs; boundary evaluation is deterministic. The dominant expense is page/app interaction, not realtime speech.
- **security:** The boundary must be explicit in the job plan (e.g. before send/purchase/delete), not inferred from vague model confidence. Store a dry-run artifact and exact pending action; do not transmit unrestricted page contents to the pendant or relay.
- **missing:** A first-class workflow checkpoint/boundary primitive in POST /plan and POST /execute; Durable checkpoint state and resume semantics across Mac/browser disconnects; A shared classification of reversible preparation versus irreversible commit (for observability, not a blanket permission gate); Completion/attention delivery that carries the pending action payload into the existing pendant inbox


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities: (1) seamless pendant USB↔LTE task/session handoff while walking away, (2) spoken evidence chains that answer exactly what Mac/browser state changed, and (3) leave-now preparation that runs to an explicit irreversible boundary and surfaces the precise pending step. The recorder flagged all three as near existing backlog themes, but accepted them; their useful distinction is the concrete cross-surface contracts: transport identity, before/after evidence, and durable checkpoint boundaries.

**Biggest unknown:** The exact live schemas for /ops/history, /approve, and /workbench/jobs/:jobId/handoff are still not inventoried by this agent, so I cannot tell which portions of evidence, checkpoint, and handoff already work end-to-end versus merely having routes. The missing work is likely in the contracts between those routes, not another standalone feature.

