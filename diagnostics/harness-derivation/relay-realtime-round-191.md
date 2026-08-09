# Harness derivation — relay-realtime — round 191

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If I start a task, summarize what you’re doing in one sentence, then ask if I want more detail.”"
- **useful because:** It keeps voice interactions calm and concise. The owner gets a quick mental model without being trapped in a long readout, and can opt into details when needed.
- **path:** relay-realtime → mac-planner → relay
- **model tier:** Realtime for the summary and follow-up question; mac-planner for the underlying plan and execution.
- **latency:** Under a second for the summary; details only if the owner asks.
- **cost:** Minimal incremental cost. Summary can be derived from the planned action list already produced.
- **security:** The summary must avoid leaking sensitive content from documents or emails. If the plan touches private data, keep it generic.
- **missing:** A stable, structured plan representation returned to the relay for summarization (or a relay-visible summary field).; A convention for details-on-demand that the mac-planner can fulfill without replaying sensitive content.

### "“When I’m away from my Mac, check my authenticated sites and tell me if anything urgent needs action.”"
- **useful because:** This would make the pendant genuinely proactive when the Mac is off, surfacing urgent changes without the owner opening a laptop.
- **path:** relay-realtime → browser → relay
- **model tier:** Background tier for periodic checks; realtime only to deliver a spoken alert.
- **latency:** Not interactive. Alerts can arrive within minutes of change, depending on polling interval.
- **cost:** Dominated by headless browser sessions and authentication maintenance.
- **security:** High risk: authenticated sessions and personal data. Needs strong isolation, secret handling, and explicit user consent per site.
- **missing:** A server-side browser capability (server_browser_actions is absent); A scheduler or push mechanism for periodic checks; Session storage/rotation for authenticated sites

### "When something I asked the system to do fails, tell me what actually went wrong, collect the relevant Mac and browser evidence, and offer a safe repair I can approve by voice—without making me repeat the original request."
- **useful because:** Today a failed job leaves the owner to reconstruct context and troubleshoot from a wearable. This would turn failures into recoverable conversations, especially while away from the Mac, while keeping the owner in control of consequential repairs.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime relay for the short failure explanation and clarification; background mac-planner for evidence collection and repair planning; mac-vision/browser harness only where planner evidence shows UI state is necessary.
- **latency:** Speak an initial failure explanation within 2 seconds of a terminal error; evidence and repair proposal may take 10–30 seconds and arrive asynchronously.
- **cost:** About $0.01–$0.08 per incident, dominated by planner/vision calls; relay speech remains a short low-token response.
- **security:** Evidence can include private screen text, authenticated pages, and command output; keep it in the existing authenticated session, redact secrets in the spoken summary, and require explicit voice confirmation before irreversible repair actions. A repair must carry the failed-job receipt and a bounded action diff.
- **missing:** A failure-classification and evidence-bundle worker that correlates job receipts, Mac state, and browser inspection; A repair-plan/approval protocol with an idempotency key and action diff; A reliable asynchronous pendant delivery path for the proposal and final outcome

### "Take the document or page I’m looking at, make a share-safe copy by finding and redacting secrets and personal data across the browser and my Mac, then tell me exactly what was removed before I send it."
- **useful because:** The owner can currently copy or send content, but cannot reliably notice credentials, tokens, private names, or local paths hidden in a mixed document. A wearable command could make safe sharing practical while away from the keyboard.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Background planner performs extraction and deterministic scanning; a cheaper model classifies ambiguous spans; realtime relay only handles the request, a concise removal summary, and confirmation.
- **latency:** Acknowledge in under 2 seconds; produce a preview in 15–45 seconds for a normal document, with a spoken completion and a review URL.
- **cost:** Roughly $0.02–$0.15 per document, dominated by OCR/vision and model review; local deterministic scanners should handle most text cheaply.
- **security:** Raw content must stay on the Mac/relay session and never be sent to a third-party sharing endpoint without confirmation. Never overwrite the source; create a new artifact, preserve an audit manifest, and require explicit confirmation before upload or send.
- **missing:** A local extraction/redaction engine covering text, PDFs, screenshots, and browser DOM; A span-level review artifact and spoken summary protocol; A final send/export action that accepts only the redacted artifact and records its receipt

### "Answer a question by checking the current state of my Mac and any authenticated browser page, and include where each fact came from and when it was observed—then warn me if the sources disagree or are stale."
- **useful because:** A spoken answer that sounds certain is dangerous when the Mac, browser session, or a cached job has changed. The owner needs a provenance-aware answer they can trust while walking around, not merely a plausible synthesis.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime relay asks one focused clarification if needed and speaks the result; faculty-perception/planner gather source snapshots; a small synthesis model produces the answer and conflict report rather than spending realtime tokens on research.
- **latency:** First source-health acknowledgement in under 2 seconds; normal answers in 5–20 seconds; stale/conflicting source warnings must be spoken before the conclusion.
- **cost:** About $0.01–$0.10 per query, mostly planner/browser inspection and synthesis; avoid vision unless DOM or screen-only evidence is required.
- **security:** Authenticated content remains scoped to the owner’s existing sessions. Spoken output should minimize sensitive quotations and identify sources generically when in public. Every claim needs a source ID, observed timestamp, and freshness policy; never silently merge contradictory values.
- **missing:** A unified observation envelope and freshness/conflict policy shared by Mac, browser, and relay; A provenance-aware synthesis endpoint that can cite claims in a compact spoken format; A pendant-friendly follow-up gesture or phrase to hear the underlying evidence without restarting collection


## Changes it proposed to its own stack

### `relay` — Build a cross-surface evidence-and-repair coordinator: on a terminal job failure, freeze the failed job's receipts, ask Mac and browser adapters for bounded snapshots, classify the failure, generate a repair diff with an idempotency key, and expose a single spoken approval/completion state to the pendant. The coordinator must refuse to claim success unless a postcondition probe passes.
- **owner gets:** A request that fails becomes an actionable explanation and one-tap/one-phrase recovery instead of a dead end or a second attempt made blindly.
- effort: Medium-high: new coordinator state machine, adapters for Mac/browser evidence, repair diff rendering, postcondition probes, and integration tests for duplicate delivery and retries.  ·  risk: A bad repair proposal could mutate work or repeat an action. Recover with immutable pre-repair receipts, idempotency keys, explicit action diffs, existing undo routes where available, and a hard terminal state of 'needs attention' when verification fails.
- cost: Low idle cost; approximately $0.02–$0.10 per failure depending on browser/vision evidence and repair planning.  ·  latency: Failure acknowledgement stays realtime; evidence and repair proposal add roughly 5–30 seconds.
- security: Snapshots may contain authenticated data. Keep them scoped to the owner session, redact spoken output, expire evidence bundles, and log access without exporting raw pages.
- depends on: A durable asynchronous pendant event delivery mechanism; A failure taxonomy and postcondition schema; Mac/browser adapters that return timestamped, source-labelled observations


## What it asked for

_Nothing._
## Its own summary

Recorded four concrete proposals: provenance-aware cross-surface answers, share-safe redaction, failure explanation and voice-approved repair, plus the relay evidence-and-repair coordinator. The failure-recovery capability is the highest-value one: it turns unattended Mac/browser failures into verified, recoverable conversations on the worn pendant rather than silent dead ends.

**Biggest unknown:** Whether the existing Mac/browser adapters expose enough timestamped, source-labelled evidence and postcondition checks to implement the coordinator without adding new local adapters.

