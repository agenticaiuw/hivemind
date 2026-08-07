# Harness derivation — mac-terminal — round 145

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac execution truth** — At 2026-08-07T18:32Z the Mac bridge and Safari extension are online, but AI Pendant Agent Accessibility is untrusted, Screen Recording is false, input reachability failed, and /observe explicitly says UI clicks/type/keys report success while doing nothing. Browser has three durable sessions including Gmail and stale probe tabs.
  - evidence: GET /ops/snapshot and GET /observe returned 200 with these fields.

## Capabilities it proposed

### "When something I asked you to do fails or seems not to happen, tell me exactly where it stopped—pendant, relay, Mac, browser, or external site—show the evidence and retry only the failed stage."
- **useful because:** Today /ops/snapshot shows a dangerous split: the bridge and browser are online, but Accessibility is false and UI actions can report success while doing nothing; the browser's active tab is even a failed example.com page while Gmail is another durable session. A single cross-surface incident answer prevents repeated blind retries and makes the system trustworthy.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background for correlation and classification; realtime only to speak the short result to the owner
- **latency:** Under 3 seconds for an existing request; up to 15 seconds if fetching all stage records
- **cost:** Usually one cheap background call (roughly 2k–4k prompt tokens); most work is deterministic joins across existing records
- **security:** Do not include page contents or secrets in the incident summary unless they were already in the owner's request. External side effects must never be retried automatically; retry only idempotent reads or explicitly marked reversible steps.
- **missing:** A cross-surface correlation index that links relay request IDs, Mac job IDs, browser command IDs, pipeline IDs, and receipts; A stage-state contract with terminal states (completed, failed, indeterminate, not-reached) and retry-safe metadata; A single endpoint that returns an ordered incident timeline rather than requiring separate /jobs, /journal, /logs, and browser records

### "Use the button on my pendant to confirm or cancel the exact Mac or browser action you just prepared, even when the pendant is only USB-connected to my Mac and the relay has not registered it."
- **useful because:** The wearable is physically present and testable now, while the Mac agent lacks trustworthy Accessibility (UI input currently reports success while doing nothing). A physical button gives the owner an unambiguous local decision channel and lets a prepared transaction survive a browser tab change or a lost voice session; it is more reliable than asking the owner to find a confirmation window.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** deterministic state machine for arm/confirm/cancel; background model only to compose the spoken description
- **latency:** Button acknowledgment under 300 ms over USB; spoken summary under 2 seconds
- **cost:** Near-zero model cost for confirmation; one short background call only when translating a complex action plan
- **security:** The button must confirm a displayed/hash-bound plan, never a mutable natural-language intent. Bind confirmation to request ID, target tab, and parameter hash; expire it after 60 seconds and cancel on tab/session change. Never transmit page secrets over the serial link.
- **missing:** A Mac USB-serial gateway for /dev/cu.usbmodem00096003658* that frames pendant button events and sends LED/ack state; A durable pending-action record shared by Mac planner, browser bridge, and relay, including a canonical plan hash and expiry; Pendant firmware support for distinct short-press confirm, long-press cancel, and success/failure LED patterns

### "For any answer or action involving my Mac, browser, pendant, or relay, tell me in one glance which surfaces and data were actually used, what stayed local, what left the Mac, and how fresh each fact was."
- **useful because:** The owner cannot currently distinguish a response based on live Gmail, a stale browser tab, Mac state, or model inference. A compact data-and-freshness receipt would make private-device automation understandable without forcing them to inspect logs, especially when a browser session or relay is online but its contents are stale or unreachable.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic provenance assembly; use the inexpensive background tier only to compress the receipt into spoken language.
- **latency:** Under 500 ms for the structured receipt and under 2 seconds for spoken compression.
- **cost:** Near-zero model cost when rendered from typed events; occasional 1k-token background summarization.
- **security:** The receipt itself must not reproduce secrets or page contents. Store source identifiers, sensitivity labels, timestamps, and transfer destinations; redact URLs, account names, and snippets according to sensitivity policy. Owner must be able to delete receipts.
- **missing:** A typed provenance event emitted by every relay, Mac, browser, and pendant operation; A local-versus-remote transfer ledger with sensitivity labels and freshness/expiry timestamps; A spoken and dashboard renderer for provenance receipts

### "When the Mac, browser, and relay disagree about what is true, show me the conflicting evidence and ask exactly one useful question instead of silently choosing a version."
- **useful because:** A live bridge can coexist with an unusable UI, a browser heartbeat can be fresh while the active tab is stale, and model summaries can disagree with page state. Today the owner has to notice these contradictions themselves. Evidence-ranked conflict handling prevents confident wrong actions and makes one short pendant interaction resolve ambiguity.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → dashboard
- **model tier:** Deterministic contradiction detection and source ranking; background model for phrasing one clarifying question; realtime only for the spoken exchange.
- **latency:** Detect conflicts within 1 second; ask the owner within 2 seconds; resume the plan immediately after the answer.
- **cost:** Usually no model call for detection; roughly 1k–2k background tokens to phrase the question.
- **security:** Show only the minimum conflicting fields, never raw private page contents. A clarification answer must be bound to the pending task and expire when the underlying sources change.
- **missing:** A shared fact identity and version format across Mac, browser, relay, and pendant telemetry; Conflict rules that distinguish stale, unreachable, contradictory, and lower-confidence observations; A pendant response protocol for selecting one of two evidence-backed choices

### "Let me demonstrate a repetitive task once on my Mac or in Safari, then have you turn it into a reusable routine with the changing fields identified, a preview of the next run, and a spoken way to invoke it from the pendant."
- **useful because:** The owner should not need to know route names, selectors, AppleScript, or planner syntax. A single real demonstration can capture the browser tab, Mac application, values entered, and resulting state, then turn an otherwise bespoke workflow into something callable hands-free. This is a genuinely new use of the whole hive: pendant names it, browser and Mac observe it, relay stores it, and the planner generalizes it.
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay-realtime → dashboard
- **model tier:** Planner-tier model only for segmenting and generalizing the demonstration; deterministic capture, replay validation, and routine scheduling; background tier for naming and summarizing the routine.
- **latency:** Capture with no perceptible delay; generate a draft routine within 10 seconds; preview replay within 5 seconds.
- **cost:** One planner call of roughly 8k–12k prompt tokens per demonstrated workflow, then near-zero cost for deterministic invocations.
- **security:** Never capture passwords, payment fields, private page text, or keystrokes outside explicitly selected steps. Mask sensitive values, require the owner to approve the generated routine, and run a dry preview before any external submission. Store the routine locally with encrypted relay backup only if requested.
- **missing:** A demonstration recorder that captures typed actions, browser DOM targets, Mac app state, and before/after observations as one trace; A trace generalizer that marks constants versus owner-supplied variables and emits a typed routine graph; A replay simulator and routine editor with per-step redaction, provenance, and invocation permissions


## Changes it proposed to its own stack

### `model-routing` — Add a live execution-feasibility compiler before planning: consume /ops/snapshot and /observe, annotate each planned step with reachable=true/false/indeterminate, and rewrite only the execution mechanism (for example, use browser DOM commands or AppleScript instead of UI clicks when Accessibility is untrusted). If no safe equivalent exists, return a precise blocked-at-preflight result instead of executing a no-op. Re-evaluate after every step because foreground app, tab, permissions, and bridge status can change.
- **owner gets:** The owner stops hearing false success. On this Mac right now, Accessibility is explicitly untrusted, synthesized events are rejected, and UI clicks/type/keys can report success while doing nothing. The agent should automatically choose a route that can actually reach the target—or say it cannot—rather than wasting the owner's time.
- effort: Medium: typed feasibility annotations in planner output, adapters for browser/AppleScript/shell, and post-step observation checks. No new model required.  ·  risk: A feasibility heuristic could reject a route that would work or choose an unexpected equivalent. Recover by preserving the original plan, recording the rewrite, and allowing an explicit force-full-control mode. Never silently convert a write into a read.
- cost: Small deterministic overhead; saves expensive planner retries and reduces unnecessary vision/model calls.  ·  latency: Adds roughly 100–300 ms for local snapshot and postcondition checks; avoids multi-second blind retries.
- security: No new authority and no gates. It reduces accidental external side effects by preventing execution through a known-unreachable UI path; shell remains unrestricted per owner policy.
- depends on: The live /ops/snapshot and /observe payloads must expose stable capability and postcondition fields, not only prose; A typed postcondition schema for open_app, browser navigation/extraction, UI input, and shell actions; A route-rewrite audit record attached to the existing job receipt


## What it asked for

_Nothing._
