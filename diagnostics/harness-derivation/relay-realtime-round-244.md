# Harness derivation — relay-realtime — round 244

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Pick up where we left off on my computer."
- **useful because:** The owner can start a thought on the pendant and continue on the Mac or browser with the right context already loaded, saving time and mental load.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** Realtime to capture intent, then handoff to the Mac planner/browser for the heavy lifting.
- **latency:** Under a second to confirm the handoff; the Mac workflow can proceed at normal speed.
- **cost:** Moderate; dominated by context packaging and downstream planning/execution.
- **security:** Context may include sensitive memory. Only project what’s relevant to the task and avoid leaking browser-derived facts unless explicitly included.
- **missing:** Live wiring to use the memory projection output in the conversation context instead of legacy blocks.; A standard handoff envelope for task context and constraints across surfaces.

### "“Search everywhere I can reach for the thing I’m thinking of, tell me which source is authoritative, and put the right result into the app I name.” For example: “Find the latest invoice from Acme across my Mac files, logged-in browser, and relay history, tell me which one is current, and attach it to the draft in Outlook.”"
- **useful because:** Today the owner must know which surface contains information and manually shuttle results between them. This would make the worn pendant a single, source-aware front door: it searches local files, authenticated browser sessions, and relay memory, resolves conflicts by freshness and provenance, speaks a short answer, and performs the final placement on the Mac/browser. The result is useful specifically because no single node can see all three stores.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime handles intent extraction and a one-sentence answer; a cheaper background planner performs federated retrieval and provenance ranking, while mac-planner/browser-extension execute the destination action.
- **latency:** Acknowledge in under 500 ms; first answer in 5–8 s; placement may continue asynchronously with a spoken completion notice.
- **cost:** Roughly $0.01–$0.05 per request depending on document/page count; retrieval, OCR, and browser snapshots dominate rather than the realtime turn.
- **security:** Search results can contain sensitive mail, files, and logged-in pages. Keep raw content on the Mac/relay where possible, send only ranked excerpts to the realtime model, show source names in the spoken answer, and record an evidence receipt. Placement into a destination must be explicitly named by the owner; never infer a recipient or attachment target from a vague phrase.
- **missing:** A federated search contract spanning Mac files, browser sessions, relay memory, and job receipts; Content extraction and provenance IDs for local files and authenticated pages; A destination adapter that can attach or insert a selected artifact, not merely type text; A compact spoken disambiguation protocol when two sources are equally current

### "“Watch this authenticated page and, if my exact condition becomes true, carry out the whole follow-up.” For example: “When this limited-run item is back under $80, buy one, use my saved shipping details, and tell me what happened.”"
- **useful because:** The owner currently can ask for a page check or a one-off Mac action, but cannot express a durable, conditional objective that bridges a logged-in browser, a scheduled relay watch, and a Mac-side receipt. This turns the pendant into an agent that can act while the owner is away instead of requiring them to remember to ask again.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Realtime only captures the condition and summarizes the resulting decision. A low-cost scheduled worker evaluates the page and deterministic predicates; the browser extension performs the authenticated transaction; mac-planner handles local receipt/storage and exception recovery.
- **latency:** Immediate confirmation of the registered condition in under 2 s; checks within the requested cadence; completion alert within 30 s of a positive match.
- **cost:** About $0.005–$0.03 per check depending on page extraction and frequency, plus one planner call on a match. Browser session uptime and page polling dominate.
- **security:** This can create financial or contractual side effects. Store the exact predicate, item identity, maximum quantity/price, and expiry as an immutable plan; refuse if the page differs materially. The owner’s explicit spoken instruction authorizes the specified transaction, but the system must not broaden it. Keep credentials in the browser session, never in relay prompts, and emit a receipt containing before/after evidence, price, and timestamp.
- **missing:** A durable conditional-workflow record with exact predicates, expiry, idempotency, and retry state; A scheduler/worker that can run browser watches even when the Mac agent is temporarily offline; Authenticated browser execution that can return structured checkout evidence; A safe transaction adapter for saved details and a durable completion/exception notification

### "“Finish the task I started, even if the connection dropped, and tell me exactly what was already done versus what still needs doing.” For example: “I started sending the rent spreadsheet to Alex; reconcile the browser and Mac state, avoid sending twice, finish the missing steps, and give me one truthful summary.”"
- **useful because:** A dropped link currently leaves the owner guessing whether an action happened, especially when a browser submission or Mac mutation may have succeeded before the relay lost its response. This would make interrupted tasks recoverable rather than duplicated or abandoned, using the pendant as the place to resume and the Mac/browser as the sources of truth.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** A cheap reconciliation worker compares action receipts with live Mac/browser state and builds an idempotent continuation plan; realtime only asks a narrowly scoped clarification when state is genuinely ambiguous and speaks the result.
- **latency:** Acknowledge recovery intent in under 500 ms; produce a state classification in 3–10 s; long repair runs continue asynchronously and notify the pendant.
- **cost:** About $0.01–$0.08 per recovery, dominated by live browser/Mac inspection and occasional planner calls. Most unambiguous cases should be rule-based with no expensive model invocation.
- **security:** Never infer that a side effect happened from a timeout alone. Maintain a per-step idempotency key, inspect destination state before retrying, and distinguish confirmed, probably-completed, and unknown. For unknown high-impact effects, report the uncertainty instead of repeating them. Receipts should include redacted evidence and be retained only as long as needed for recovery.
- **missing:** A durable step-level action journal with idempotency keys and pre/post observations across Mac and browser surfaces; Adapters that can inspect whether a specific send/upload/form submission already occurred; A continuation planner that can safely skip confirmed steps and retry only unresolved ones; A user-facing reconciliation vocabulary for the pendant: completed, resumed, blocked, or unknown


## What it asked for

_Nothing._
## Its own summary

Recorded three distinct owner-facing capabilities: federated source-aware search and placement across relay/Mac/browser; durable conditional actions against authenticated pages; and interruption-safe reconciliation that resumes tasks without duplicate side effects. The most broadly useful is the first: it makes the pendant a single front door to information and action across otherwise isolated surfaces.

**Biggest unknown:** Whether the existing watch, receipt, and browser routes already expose enough structured state to implement the proposed conditional workflows and reconciliation without new durable worker/journal primitives; I was instructed not to discover further this round.

