# Harness derivation — unified — round 244

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Give me a daily 'did the system actually work?' report: calls attempted, audio heard, actions completed, failures, and anything that needs my decision."
- **useful because:** A healthy relay or a successful Mac job is not proof that the owner heard audio or that a browser action reached its destination. This turns scattered receipts and delivery acknowledgements into one honest daily answer, without pretending queued work succeeded.
- **path:** relay → pendant → mac-bridge → dashboard → browser
- **model tier:** background model; deterministic aggregation first, model only summarizes anomalies
- **latency:** Generate in under 10 seconds on schedule; pendant delivery can wait for its next connected window.
- **cost:** Low: mostly reads and aggregation; one short background summary call per report.
- **security:** Default to counts and opaque IDs, not message contents, URLs, or audio. Keep the report local unless the owner explicitly asks for relay delivery. Clearly separate attempted, accepted, delivered, heard, failed, and unknown.
- **missing:** A common event schema joining action, pipeline, browser, and audio-delivery receipts; A scheduled report route and durable acknowledgement of which report the owner reviewed; A relay-side aggregation query across job and delivery records

### "That's wrong — correct this remembered fact, show me what evidence supported the old version, and make the correction apply everywhere without rewriting the action history."
- **useful because:** Deletion alone cannot repair a false fact that the system will immediately re-infer. A correction needs provenance, supersession, propagation to derived context, and an audit trail of the correction while preserving the original Mac job history.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** realtime to capture the correction; background model to find dependent summaries and propose affected records; deterministic commit
- **latency:** Acknowledge and show the old evidence in under 3 seconds; local correction immediately; replicated copies report pending until confirmed.
- **cost:** Low-to-moderate: one background dependency scan per correction; writes and relay replication dominate.
- **security:** Require explicit owner confirmation before changing a fact used in routines or actions. Preserve immutable provenance and correction timestamps, but redact sensitive evidence by default. Never silently overwrite an audit receipt or infer a correction from ambiguous speech.
- **missing:** Versioned fact records with supersedes/supersededBy and correction provenance; Dependency traversal from a fact to derived summaries and relay replicas; A conflict state when an old and new evidence source disagree; Owner-facing correction and propagation receipt

### "Prepare a review packet for this task — what you intend to do, which browser tab or Mac app it will touch, what could change, and what evidence would prove success — but do not execute anything."
- **useful because:** The owner currently gets either a vague plan or a blocked spoken promise. A portable, redacted packet lets them inspect intent and risk from the dashboard or pendant, hand it to another machine after a restart, and decide later without creating side effects.
- **path:** relay → mac-bridge → browser → dashboard → pendant
- **model tier:** background planner for packet construction; deterministic redaction, risk classification, and digesting
- **latency:** Packet in under 5 seconds for ordinary tasks; no action dispatch while preparing it.
- **cost:** Moderate only for ambiguous multi-step tasks; otherwise route reads and hashing dominate.
- **security:** Bind packet to a plan digest, target tab/app identity, world fingerprint, expiry, and explicit non-execution state. Redact secrets and form values. Mark evidence expectations as unverifiable rather than inventing them. A packet must be invalidated by target or world change.
- **missing:** A stable packet schema and GET endpoint usable by dashboard and pendant; A handoff token that lets another Mac agent resume review without replaying actions; Evidence expectations tied to each step and a deterministic redaction layer

### "For this task, prove exactly what data left my Mac, which service received it, what was redacted, and whether any browser page content or audio was retained."
- **useful because:** The owner can currently trust individual controls but cannot audit the actual data path across Mac, browser, relay, and pendant. A post-task leakage report makes privacy a verifiable property rather than a promise.
- **path:** mac-bridge → browser → relay → pendant → dashboard
- **model tier:** deterministic event and payload accounting; background model only summarizes anomalies
- **latency:** Under 5 seconds for a normal task; unavailable fields must be reported immediately as unknown rather than inferred.
- **cost:** Low runtime cost; requires bounded metadata receipts, not storing payloads.
- **security:** The audit itself must not duplicate secrets. Store hashes, classifications, destinations, byte counts, and retention outcomes—not raw page text, audio, or form values. Tamper-evident receipts should distinguish measured from declared behavior.
- **missing:** End-to-end data-flow receipts with source, destination, classification, redaction, and retention fields; A relay append-only privacy ledger keyed to task and browser session; A dashboard and pendant summary that can explain unknown or unverifiable segments

### "Use my rules for this site: let the browser act on my behalf, but never send page text, account identifiers, or audio to the relay; if a step needs them, stop and ask me."
- **useful because:** The owner needs a durable privacy boundary finer than all-or-nothing capture or approval. A logged-in browser can see sensitive pages while the relay and model should receive only the minimum structured facts needed to plan or verify an action.
- **path:** browser → mac-bridge → relay → dashboard → pendant
- **model tier:** deterministic policy enforcement at the boundary; planner model receives only policy-approved projections
- **latency:** Policy decision inline in under 100 ms; blocked requests explain the missing permission on the next spoken turn.
- **cost:** Low per action; policy matching and redaction are local, with occasional background policy conflict review.
- **security:** Default deny for unclassified content and fail closed on tab identity uncertainty. Policies must be scoped by site, tab, data class, and purpose; never allow a model-generated policy to broaden access without explicit owner confirmation.
- **missing:** A least-privilege browser-to-relay data firewall; Owner-editable site/data-class/purpose policy records; A structured projection API so browser actions can return only approved fields; Violation receipts without retaining the blocked content

### "Simulate this browser or Mac task first: show me the pages, files, messages, and side effects it would touch, then tell me what cannot be simulated safely. Do not change the real world."
- **useful because:** Plans and approvals describe intent, but they do not reveal hidden navigation, redirects, writes, or irreversible branches. A shadow run gives the owner a concrete preview before a logged-in action crosses the point of no return.
- **path:** browser → mac-bridge → relay → dashboard → pendant
- **model tier:** deterministic sandbox/interceptor for navigation and filesystem reads; planner model only explains the resulting trace
- **latency:** Simple browser tasks under 8 seconds; complex tasks may return a partial trace with explicit unsimulated steps.
- **cost:** Moderate infrastructure cost for isolated browser contexts and filesystem snapshots; no recurring model cost beyond explanation.
- **security:** Never simulate by performing the real external mutation and undoing it. Use isolated browser sessions, network allowlists, read-only filesystem snapshots, and synthetic credentials where possible. Mark external services that cannot provide dry-run semantics as blocked, not simulated.
- **missing:** An isolated browser session or request-interception harness; Read-only Mac execution/snapshot mode covering app and filesystem effects; A side-effect trace schema with simulated/unsimulated confidence; A hard boundary preventing a simulation from reaching real submission endpoints


## Changes it proposed to its own stack

### `integration` — Wire a read-only review-packet flow across planPreview, browser target inspection, workbench handoff, and the dashboard: persist a digest-bound packet with redacted intent, touched surfaces, riskTier/replaySafety, expected evidence, world fingerprint, expiry, and explicit non-executed state.
- **owner gets:** Before anything changes on the owner's Mac or logged-in browser, they can see exactly what will happen and later resume reviewing it without accidentally rerunning it.
- effort: Medium: packet schema, redaction, dashboard rendering, and tests for plan/world invalidation.  ·  risk: A stale or over-redacted packet could mislead; invalidate on world or target changes, and fail closed if evidence cannot be described. Recover by regenerating the packet.
- cost: Negligible runtime/API cost; one small durable record per pending review.  ·  latency: Adds under 1 second for deterministic plans; ambiguous plans still use the planner tier.
- security: Improves security by keeping secrets out of relay/pendant and binding review to a digest; requires careful target identity and redaction tests.
- depends on: A typed packet schema and owner-facing review surface; Existing planPreview/action ledger risk and replay classifications; Browser tab/session identity and workbench handoff route


## What it asked for

_Nothing._
