# Harness derivation — relay-realtime — round 131

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "What happened to the thing I asked you to do earlier?"
- **useful because:** The owner gets a truthful, speaker-sized status update without needing to open a laptop or remember details. It reduces anxiety and repeated commands when they’re away from the Mac.
- **path:** relay → mac-bridge → mac-harness
- **model tier:** relay realtime for the spoken request; cheap backend status read for the answer; Mac only if the status requires a new action.
- **latency:** Under a second for common cases where status is already recorded; longer only if a new action is requested.
- **cost:** Very low; dominated by a small status lookup. No browser or web calls unless the user asks to continue or retry.
- **security:** Status text may reveal sensitive app names or document titles; keep logs minimal and avoid repeating full paths unless necessary. Never claim completion unless the status says done.
- **missing:** relay_job_status needs a working implementation behind the schema; A relay-visible job/receipt store durable across reconnects

### "“On the checkout page I have open, fill the form with my saved details, but never read my card number aloud or send it through the relay; stop before the final purchase.”"
- **useful because:** The owner can safely delegate tedious authenticated form filling while away from the Mac without exposing payment credentials to the realtime model or requiring them to dictate sensitive data through a wearable microphone. The pendant remains the conversational control surface, while the browser extension performs local, field-scoped filling and reports only non-sensitive completion facts.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Realtime relay parses the request and confirms field scope; a small structured extractor classifies fields. The browser extension performs local autofill using the browser/OS credential store; no LLM should see secret values. mac-planner is used only if the target page or form cannot be reached through the extension.
- **latency:** Acknowledge scope in under 1 second, identify the active tab and fill in 3–8 seconds, then speak a field-level receipt. Do not block on model generation while local autofill is running.
- **cost:** Usually under $0.005 per invocation: one short realtime turn plus extension calls. Engineering cost is in field classification, local credential integration, and robust receipts; no screenshot model is required for standard forms.
- **security:** Sensitive values must stay in the browser/OS credential boundary and never appear in relay logs, transcripts, screenshots, analytics, or spoken replies. The extension must use origin-bound credentials, allowlisted field classes, and redact values in receipts. The owner’s stated no-gate policy permits reversible filling, but final submission, purchase, or sending must be a separate explicit action. Recovery must clear partially filled sensitive fields and report exactly which non-sensitive fields changed.
- **missing:** A browser-extension primitive for origin-bound local autofill that accepts field intents but never returns values; A relay-to-extension schema with explicit sensitive/non-sensitive field classes and redacted typed receipts; A reliable active-tab identity and form-state snapshot, including a stale/offline result; Credential-store integration on the Mac/browser side with origin and frame protections; Dashboard audit records that prove which fields were filled without retaining their contents


## Changes it proposed to its own stack

### `relay` — Implement the granted relay_route_intent schema as the relay’s canonical routing and status handshake. When a user speaks, the relay emits a structured intent event to the router (intent label, utterance, optional context) and receives a job handle or immediate response. The same job handle is used by relay_job_status to report progress back to the user without inventing phrasing or protocol. Add a small intent taxonomy and a mapping table to existing downstream tools (get_mac_status, mac_run_actions, browser_run_actions, web_search, mac_delegate).
- **owner gets:** They can say natural things and reliably hear what happened, even if the Mac sleeps or the browser is offline. No more “I sent it somewhere” ambiguity — they get a solid status update they can trust.
- effort: Medium: schema already granted; needs router endpoint, job handle plumbing, and mapping to existing action tools. Coordination across relay and orchestrator.  ·  risk: Misrouting or duplicate execution if the mapping table is wrong. Mitigate with idempotency keys and receipts; keep a safe fallback to mac_delegate for ambiguous tasks.
- cost: Low per request; dominated by downstream tool calls. Relay parsing is cheap compared to Mac planning.  ·  latency: Improves perceived latency by giving immediate structured acknowledgement and a consistent status path; routing itself should be sub-100ms.
- security: Structured intents reduce accidental overreach. Still must treat utterances as sensitive; log minimally and avoid storing raw audio. Requires auth on the routing endpoint.
- depends on: Durable job handles and relay_job_status implementation (currently schema-only); Agreement on intent labels and mapping to existing tools


## What it asked for

_Nothing._
## Its own summary

Discovered current tools, granted items, and device status. Several new tools are present but two are schema-only and still unimplemented. Proposed implementing relay_route_intent as the canonical routing/status handshake and a user-facing status capability built from job receipts, so the owner can trust what happened without opening the Mac.

**Biggest unknown:** Whether the orchestrator has implemented a durable job/receipt store and the relay_job_status backend; the tool is granted as a schema, but it’s unclear if the underlying routes and persistence exist yet.

