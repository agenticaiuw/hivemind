# Harness derivation — mac-terminal — round 68

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac readiness and browser failure mode** — Live Mac agent is v0.5.0 with FULL_CONTROL_MODE and planner enabled, but computer-use loop disabled; Accessibility and Screen Recording are ungranted, so /ops/status reports ready:false. home-chrome is offline with 5 pending browser commands. A browser_read_page job waited ~45 seconds before returning a typed offline failure; preflight does not currently prevent dispatch.
  - evidence: GET /ops/status HTTP 200; GET /jobs HTTP 200 showing local_5336393e... browser_read_page failed after 45,050ms and local_6599532f... browser_navigate failed after 45,158ms.

## Capabilities it proposed

### "“Before you start, tell me whether the Mac, browser, relay, and pendant can actually do this—and if one is unavailable, keep going with the best safe route and tell me exactly what I need to fix.”"
- **useful because:** Today a browser read can sit for ~45 seconds and then fail because the extension is offline, while /ops/status already knew the browser was offline and Mac readiness was false. The owner should get immediate, actionable reachability rather than a mysterious timeout, and long work should be able to continue on another body when privacy and task requirements permit.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic local preflight for health, permissions, and route selection; background gpt-4.1-mini only to turn a typed failure into a concise spoken explanation; realtime only for the live interruption/answer.
- **latency:** Under 250ms to report readiness and choose a route; asynchronous repair hints and durable-job updates can arrive later. No planner-tier call for health checks.
- **cost:** Near-zero for normal requests (local GETs and typed rules). A few cents or less only for unusual natural-language recovery explanations; the dominant saving is avoiding planner retries and 45-second doomed browser waits.
- **security:** Authenticated tabs must never fall back to public browsing or relay fetches unless the task is explicitly public. Surface permission state and failure reasons without sending page contents. Opening System Settings is okay as a hint, but permission changes remain the owner's action under the existing maximum-access policy.
- **missing:** A shared prerequisite/route registry mapping action types to /ops/status and /browser/status facts; Fast-fail dispatch before browser commands and retry-on-heartbeat-change; Pendant/relay notification for typed reachability failures and repair hints; The granted mac_read_diagnostics tool needs an implementation; current invocation returns 'no implementation yet'; The owner must bring home-chrome online and grant Accessibility/Screen Recording if GUI vision is desired

### "“Show me exactly what happened across the pendant, relay, Mac, and browser when my request went wrong—and tell me the one thing I should do next.”"
- **useful because:** Today the owner can see isolated job receipts and typed failures, but cannot reconstruct one causal timeline across the spoken request, relay delivery, model routing, Mac dispatch, browser heartbeat, and final outcome. When something fails or partially succeeds, they are left to infer whether the problem was the pendant, network, relay, Mac permissions, browser session, or the action itself. A single evidence-backed incident replay would make the system trustworthy and recoverable rather than merely capable.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic event correlation and causal classification first; use background gpt-4.1-mini only to summarize the correlated incident in owner language. Reserve realtime for answering a spoken follow-up while the replay is already available.
- **latency:** Maintain an append-only event timeline during execution with sub-100ms local writes. Produce a normal replay in under 2 seconds; large incidents may be assembled asynchronously while the pendant gives a short preliminary status.
- **cost:** Low: correlation is local/relay work and does not require an LLM. A short background summary costs only a small fraction of planner-tier work; the main cost is bounded event storage and dashboard rendering.
- **security:** Events must contain references, hashes, and redacted metadata rather than raw authenticated page contents, shell output, audio, or secrets. The owner should be able to delete an incident and its linked artifacts. Cross-device correlation IDs must not become a way for unrelated users or sessions to join histories.
- **missing:** A single end-to-end correlation ID propagated from pendant speech through relay, routing, Mac jobs, browser commands, and receipts; Durable, ordered event envelopes with monotonic timestamps, source surface, parent event, redaction class, and retention policy; A causal correlator that distinguishes unavailable surface, transport loss, planner failure, executor failure, partial completion, and confirmed completion; Cross-surface incident replay in the dashboard and a compact spoken explanation/next-step response; A recovery link from each failure node to the exact retry, undo, or owner-side repair action that is valid for that state

### "“If I tell you something while the network or Mac is unavailable, remember it on the pendant, acknowledge that it is safely queued, and carry it out or ask me about it when the connection returns—without losing or duplicating it.”"
- **useful because:** The owner wears the pendant precisely when the rest of the system may be unreachable. Today a dropped relay, sleeping Mac, or offline browser can turn a spoken request into uncertainty: there is no durable local acknowledgment that the intent was captured, nor a guaranteed once-only handoff when connectivity returns. An offline intent mailbox would make the pendant dependable in the moments the owner relies on it most.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Pendant stores and acknowledges a compact intent envelope without invoking a model. Relay performs deduplication and dispatch on reconnection; background gpt-4.1-mini interprets queued text only when needed. Realtime is used only for the initial spoken acknowledgment if the link is available.
- **latency:** Local capture and audible/LED acknowledgment under 300ms when disconnected. Reconciliation begins within one heartbeat after reconnect; the owner receives a queued, dispatched, or needs-review state rather than waiting synchronously.
- **cost:** Very low: bounded flash writes and relay D1 metadata dominate; no LLM cost for simple captured utterances. Background interpretation is charged only for ambiguous queued intents.
- **security:** The pendant must not retain raw audio longer than necessary; store encrypted text or a short content hash plus encrypted payload, with a visible retention limit and physical/button deletion. High-impact or privacy-sensitive actions remain pending for review rather than executing solely because connectivity returned. Sequence numbers and idempotency keys prevent duplicate reminders, messages, or browser submissions.
- **missing:** A pendant-side encrypted intent queue that survives link loss and power cycling within available flash/RAM limits; A local acknowledgment state and retry/backoff protocol over the pendant link; Relay ingestion with device sequence numbers, idempotency keys, ordering, and explicit queued/dispatched/expired states; A reconnect reconciler that hands work to the Mac or authenticated browser only after current reachability is verified; A pendant/dashboard view for queued intents, expiration, deletion, and conflicts when the owner later gives a revised instruction


## Changes it proposed to its own stack

### `integration` — Build a live capability-preflight and recovery layer for every Mac/browser job. Before dispatch, consume GET /ops/status, GET /browser/status, and GET /capabilities to produce a per-action prerequisite map (browser polling, app reachability, Accessibility, Screen Recording, relay reachability). If a prerequisite is absent, fail in <1s with a typed reason instead of spending 45s on a doomed browser command; select an alternate route when one exists (for example public-page research through relay/browser-run, authenticated work only through the private bridge). For recoverable local states, enqueue a repair hint as a Mac job (open the relevant app/settings pane, never silently change permissions), and push the state plus exact next step to the pendant/relay. Record the preflight snapshot and route decision alongside the existing action receipt so later retries know whether the environment changed.
- **owner gets:** The owner gets an honest answer immediately instead of waiting nearly a minute for a browser action that could never run, and can fix the Mac from a spoken instruction. Work can continue through whichever body is actually online, while private authenticated work is clearly distinguished from public fallback. When the owner leaves and returns, the receipt explains both what was attempted and why it was or was not reachable.
- effort: Medium: a shared preflight module in the Mac executor, typed health-to-prerequisite rules, fast-fail/error taxonomy, retry invalidation when heartbeat or permissions change, dashboard status card, and relay/pendant notification plumbing. No confirmation gate or reduction of FULL_CONTROL_MODE.  ·  risk: A stale health snapshot could incorrectly reject a newly recovered surface or choose an unsuitable fallback; cap snapshots at dispatch, recheck only after failure, and permit explicit retry. Repair hints must be non-mutating by default (open settings/app only); never claim authenticated browser work was completed through a public route. Existing jobs and receipts remain valid if the preflight module is unavailable.
- cost: Negligible API cost: health endpoints are local reads; one small background-model call only when converting a typed failure into a spoken explanation. Saves expensive planner retries and avoids 45s wasted execution waits.  ·  latency: Adds roughly 10–50ms local preflight and removes tens of seconds from known-doomed actions. Recovery notifications can be asynchronous through the relay.
- security: Improves security observability without restricting the owner's deliberate maximum-access policy: permissions and route state are surfaced, not changed. Preflight logs should hash/redact URLs, command text, and permission details where sensitive; authenticated content never goes to a public fallback.
- depends on: GET /ops/status; GET /browser/status; GET /capabilities; GET /jobs; POST /execute; GET /pipeline; GET /pipeline/stream


## What it asked for

_Nothing._
## Its own summary

Recorded two capabilities unavailable today: end-to-end incident replay across pendant/relay/Mac/browser, and an encrypted pendant-side offline intent mailbox with once-only reconnect reconciliation. Both require new cross-surface event/state plumbing rather than merely exposing existing isolated routes.

**Biggest unknown:** Whether the pendant’s available flash and firmware task budget can support the encrypted offline intent queue without displacing audio or telemetry.

