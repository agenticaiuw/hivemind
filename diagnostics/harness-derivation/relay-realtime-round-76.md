# Harness derivation — relay-realtime — round 76

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Handle this task across my Mac and authenticated browser, and if you hit a decision or an unclear screen while I'm away, ask me on the pendant with the exact choices; when I answer, continue and tell me what was done."
- **useful because:** Today a delegated task either fails silently at the first ambiguous page or requires the owner to return to the Mac. This gives the worn pendant a real role as an exception-resolution channel: the Mac planner and browser can work unattended, while the owner can resolve only the one decision that genuinely needs their knowledge, then receive a concise completion receipt.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Use gpt-5.6-luna/mac-planner for the durable goal and state machine, gpt-4.1-mini/mac-vision or browser extraction for page/UI interpretation, and relay-realtime only for the short spoken clarification and answer normalization. Do not spend the realtime tier on planning or polling.
- **latency:** Immediate acknowledgement under 1 second; an exception prompt should reach the pendant within 5 seconds of detection; after the owner's answer, resume within 10 seconds where the Mac/browser are online. The job may otherwise run asynchronously.
- **cost:** About $0.03–$0.20 per task depending on planner turns and screenshots; realtime clarification is a small fraction, while browser/page interpretation and repeated planner context dominate.
- **security:** The browser may expose authenticated private content in an exception snapshot, so send only a cropped/textual minimum to the relay and retain full page data locally. Bind every answer to a jobId, session/tab, and expiring question nonce; stale or duplicated answers must not resume a different task. The owner has requested maximum access and no general gates, but the system should still make the exact pending mutation and target visible in the spoken prompt and receipt.
- **missing:** A durable cross-surface job state machine that can pause on needs_owner_input and resume without losing planner/browser context; A browser/Mac event callback that reports ambiguity, authentication expiry, CAPTCHA, or conflicting choices to the relay; A pendant prompt/answer protocol (including timeout, repeat, and offline buffering) rather than one-shot speech; A typed question payload with jobId, evidence excerpt, options, recommended option, and answer nonce; A resume endpoint and idempotency semantics across POST /plan, POST /execute, browser command results, and action receipts

### "What changed in my work since I last checked? Compare the project on my Mac, the relevant authenticated browser tabs, and what I told you by voice; give me only new decisions, blockers, and next actions, with where each fact came from."
- **useful because:** The owner currently has to remember which surface contains which piece of state and manually reconcile them. A single spoken delta brief would turn the pendant into a continuity layer between offline voice context, Mac artifacts, and authenticated web work, rather than another isolated command interface.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheaper background planner/summarizer for collection and comparison; use relay-realtime only to collect the short scope (project/name/time window) and deliver the final spoken brief. Use browser extraction and Mac read-only inspection as evidence producers, then a judgement pass to rank deltas.
- **latency:** A small scope should acknowledge immediately and return in 15–45 seconds; larger comparisons can run asynchronously and notify the pendant when ready. No continuous polling is needed for the spoken request.
- **cost:** Roughly $0.05–$0.30 per brief; browser and Mac evidence collection plus long-context comparison dominate, while realtime speech remains inexpensive.
- **security:** Authenticated browser text and private Mac files must stay scoped to explicitly named project sources, with source-level citations and redaction before any cross-surface model call. Preserve a manifest of what was read and a timestamp so the owner can distinguish observed changes from model inference. Never claim no change when one surface was offline.
- **missing:** A cross-surface snapshot/diff API with stable document, tab, file, and voice-event identifiers; Read-only Mac project inspection and browser-tab extraction that return normalized evidence plus timestamps, not just UI screenshots; A durable per-project baseline so 'since last checked' has a defined checkpoint and can be reset by voice; A provenance-aware summarizer that marks unavailable, inferred, and directly observed facts separately; A relay response format that can stream a short spoken result while retaining the detailed cited brief in the dashboard


## Changes it proposed to its own stack

### `relay` — Add a self-describing /capabilities (or /surface) endpoint for the relay that lists its routes, tools, and current intent-routing contract, plus a versioned schema for tool availability. Expose it to the relay agent via probe_http so the live surface can be inventoried without relying on other agents' route tables.
- **owner gets:** The pendant feels more reliable: when something fails, the relay can quickly tell the owner what it can currently do, what’s down, and where the request is being sent, instead of guessing or re-deriving. It reduces "I tried, but I don’t know why it didn’t work."
- effort: Medium. Adds a read-only endpoint and a small registry; requires wiring into the relay deployment pipeline and keeping tool metadata in sync.  ·  risk: Low. Main risk is exposing too much internal detail; mitigate with public vs internal views and no secrets. If the endpoint is wrong, it misleads routing; add tests and a version field.
- cost: Minimal API cost; a cheap GET. No new expensive model usage.  ·  latency: Improves troubleshooting latency; no extra latency for normal requests if cached.
- security: Must avoid leaking tokens, owner data, or internal stack traces. Provide only capability names, versions, and health summaries.
- depends on: The relay surface must support a probe_http-visible endpoint under /v1 or similar.


## What it asked for

_Nothing._
## Its own summary

Recorded two owner-facing capabilities: (1) a durable Mac/browser task that can pause on a precise ambiguity, ask one nonce-bound question over the pendant, resume, and deliver a receipt; (2) a provenance-backed cross-surface work-change brief combining Mac, authenticated browser, and voice history. Both require missing durable state, evidence normalization, callback/resume, and pendant prompt plumbing rather than pretending current one-shot tools can do it.

**Biggest unknown:** The backlog may already contain close variants of both ideas; the proposal recorder flagged similarity to existing return-to-work and clarification concepts. I did not re-discover or re-probe because the user explicitly ended discovery for this round.

