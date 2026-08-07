# Harness derivation — relay-realtime — round 84

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I ask a spoken question about something that spans my Mac and a logged-in website—like “did the deploy finish and is the incident closed?”—give me one concise answer that reconciles both sources, includes which source was freshest, and says when they disagree instead of guessing."
- **useful because:** Today the pendant can hand a task to either the Mac or browser, but cannot establish truth across both. This prevents false reassurance when a local command succeeded but the web dashboard has not updated (or vice versa), especially while the owner is away from the desk.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use relay-realtime only to classify the short spoken question and present the result; use the cheaper background/planner tier to query and normalize the Mac and browser evidence, then have relay-realtime synthesize the final low-latency spoken response.
- **latency:** Acknowledge immediately; return a first answer within 5 seconds for two read-only sources, with a clearly marked partial result if one surface is offline. Do not block the owner’s conversation on a slow or unavailable source.
- **cost:** Usually 1 realtime turn plus one planner/reconciliation call; roughly $0.01–$0.05 per query depending on evidence length. The dominant cost is sending normalized excerpts, not the short spoken intent.
- **security:** Browser evidence may contain authenticated work data and Mac output may contain secrets. Keep raw page text and shell output on their originating surfaces; send only minimal cited fields, timestamps, source identifiers, and confidence to the relay. Never claim agreement when a source is stale; expose disagreement. Read-only by default and no action should be triggered by this capability.
- **missing:** A cross-surface read/reconciliation job that can query the authenticated browser tab and Mac status/diagnostics in one request; A typed evidence envelope with source, observedAt, freshness/TTL, citation, and confidence fields; A relay response formatter that can speak agreement, disagreement, partial, and stale states without inventing facts; An online/offline policy and bounded timeout for each surface

### "I’m walking away from my Mac—tell me whether I’m leaving behind unsaved work or a browser task that needs attention, and give me a short handoff summary I can pick up from the pendant later."
- **useful because:** The pendant is worn precisely when the Mac becomes unattended. Existing status checks can say whether a machine is online, but they do not join unsaved local work, active browser workflows, and pending agent jobs into a departure-safe brief. This would prevent the owner from discovering later that a document, form, or delegated task was stranded.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheap planner/read-only worker to collect and classify state; use relay-realtime only for the spoken departure request and concise result. No computer-use model is needed unless the owner explicitly asks to repair something.
- **latency:** Speak an immediate acknowledgement and return within 6 seconds, using per-surface deadlines. If the Mac or browser is offline, say exactly which part could not be checked rather than waiting indefinitely.
- **cost:** One short realtime turn and one bounded read-only fan-out, approximately $0.01–$0.04 per invocation; collection and normalization dominate, while the spoken synthesis is small.
- **security:** The brief can reveal document names, URLs, and work context. Keep detailed titles and page contents on the Mac/browser; transmit only redacted labels and actionable state. Never close apps, submit forms, or alter files as part of a departure check. Retain the handoff summary encrypted with a short expiry and allow the owner to clear it by button or voice.
- **missing:** A read-only Mac unsaved-work/app-state inspection with explicit confidence (not merely machine health); A browser-extension snapshot of active tabs and whether a queued command or form is incomplete; A durable, expiring handoff record addressable from the pendant in a later voice turn; A redaction layer and unified pending-job join across Mac, browser, and relay

### "Why didn’t that thing I asked for happen? Explain the failure in plain language, distinguish a bad plan from an offline Mac/browser or a stale result, and tell me the next safe recovery step without retrying automatically."
- **useful because:** A job status is not an explanation. When the owner is away from the Mac, opaque failures force them to repeat requests or open a dashboard. A causal, evidence-backed explanation would turn receipts and logs into a useful spoken diagnosis while avoiding duplicate side effects.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheaper background diagnostic/reconciliation model to inspect the existing job, receipt, event, and surface-health records; reserve relay-realtime for the short clarification-free spoken answer.
- **latency:** Acknowledge immediately and provide a diagnosis within 8 seconds, with a partial explanation if one source times out. Never wait forever for a disconnected surface and never silently retry a mutation.
- **cost:** One diagnostic planner call plus a short realtime response, approximately $0.01–$0.05 per invocation. Log and receipt extraction is the main token cost.
- **security:** Diagnostics may include command lines, URLs, and private output. Redact secrets before relay transmission and cite opaque job/receipt IDs rather than raw payloads. Recovery recommendations must be explicitly non-executing; any retry or undo remains a separate owner request.
- **missing:** A causal event graph linking plan, dispatch, surface connectivity, action receipt, and resulting observation; Typed failure taxonomy separating validation, transport, timeout, stale observation, and downstream execution errors; A safe recovery recommender that can identify whether retry, refresh, undo, or human inspection is appropriate without performing it; Redacted spoken-safe diagnostic summaries with citations and timestamps


## Changes it proposed to its own stack

### `relay` — Implement the granted relay_route_intent schema as a real routing primitive: accept a concise intent label plus utterance, map to a target agent (mac-planner or mac-vision) with a stable job record, and emit a job id that relay_job_status can query. Include minimal, typed context fields (locale/time/session) and a pass-through for downstream constraints.
- **owner gets:** The owner can speak naturally (“open Safari and search for…”) and hear a crisp confirmation that the request was routed and is progressing, even if the Mac is asleep or slow. This reduces confusion and repeated commands during voice use.
- effort: Medium. Requires wiring a new route/handler in the relay, job record storage, and a small intent-to-target mapping table. Downstream can stay unchanged because routing still delegates via existing tools.  ·  risk: Misrouting could cause surprising actions. Mitigate with conservative intent mapping, and default to mac_delegate for ambiguous requests. Recovery: job receipts and undo-last on the Mac side.
- cost: Low per invocation; dominated by downstream planning/execution if invoked. Relay-side cost is a small write to job storage and a log entry.  ·  latency: Small added overhead (<30ms) for job bookkeeping; overall latency still dominated by downstream actions.
- security: Low incremental risk if job records store minimal utterance text and avoid secrets. Ensure logs redact sensitive substrings when possible.
- depends on: relay job record storage (durable object or KV) and a stable job id format

### `integration` — Implement server_browser_actions as a real, sandboxed browser-run backend that the relay can call when the Mac is offline: open a URL, perform high-level actions, extract structured results, and return a concise spoken summary plus citations. Add guardrails: only allowlisted domains by default and explicit owner opt-in lists.
- **owner gets:** The owner can ask the pendant to quickly check a public page (weather, package status, documentation) without relying on their Mac being awake, and without waiting for a full browser session on the laptop.
- effort: Medium to high. Requires wiring to a browser-run service, action schema validation, extraction templates, and a summarizer. Also needs a domain allowlist mechanism and a way to return citations.  ·  risk: If unrestricted, it could exfiltrate data or perform unintended actions on the web. Mitigate with allowlists, read-only actions by default, and explicit opt-in for interactive actions.
- cost: Moderate per invocation; dominated by browser runtime minutes and extraction. Relay cost is orchestration and summarization.  ·  latency: Higher than a simple web_search; acceptable for a “check something” flow but not for conversational back-and-forth.
- security: Medium. Needs strict URL and action validation, no credentialed sessions by default, and careful handling of any returned content.
- depends on: a browser-run provider integration and an allowlist/permission model for domains and action types

### `routines` — Add a scheduler layer (cron triggers or durable object alarms) to support delayed and recurring jobs, with routing to mac-planner or server-side read-only tasks. Provide a simple voice interface: “remind me to…” uses existing reminders; “check X every morning” becomes a routine job whose results are summarized to the owner.
- **owner gets:** The owner can set and forget recurring checks (like monitoring a build status page, a repo CI status, or a daily briefing) without keeping the Mac open or re-asking each day.
- effort: High. Requires job definitions, persistence, execution workers, result storage, and notification delivery via the relay/pendant.  ·  risk: Unexpected repeated actions if a routine is misconfigured. Mitigate with clear routine summaries, easy disable/undo, and strict separation between read-only checks and mutating actions.
- cost: Variable; dominated by routine frequency and downstream calls. Needs quotas to avoid runaway cost.  ·  latency: Not latency-sensitive; runs in background. Relay is only used for delivery when there’s something to say.
- security: Medium. Needs careful scoping of what routines can access and strong audit logs. Credentialed workflows must remain on the appropriate surface (browser sessions on the Mac/browser harness).
- depends on: durable job runner, routine definition storage, and a delivery path from background workers to the relay/pendant

### `relay` — Add a read-only failure-forensics correlator that joins a job’s plan, dispatch events, surface-health snapshots, action receipts, and post-action observations by jobId/requestId/commandId. Emit a typed causal record (blocked-before-dispatch, transport failure, timeout, execution error, stale observation, or unknown), with redacted evidence references and a non-executing recommended next step. Expose it to the realtime relay as a bounded diagnostic query, not as an automatic retry path.
- **owner gets:** When the owner asks why something failed, the pendant can explain what actually happened instead of merely saying “the job failed” or accidentally doing it twice. This is especially valuable while the owner is away from the Mac and browser.
- effort: Medium: define the correlation schema, add event joins and redaction, cover missing/late events, and add tests for partial connectivity and duplicate command IDs.  ·  risk: Incorrect correlation could misattribute a failure or suggest the wrong recovery. Fall back to “insufficient evidence,” include timestamps and source references, and keep the feature strictly read-only. Recovery is performed only by a separate explicit request.
- cost: Low recurring API cost; mostly server-side indexed event joins and a small diagnostic-model call only when requested. Storage grows with compact correlation metadata rather than raw page or shell output.  ·  latency: Typically under 1–2 seconds for indexed records; cap source waits and return a partial diagnosis when a Mac or browser is offline.
- security: Potentially sensitive logs must be redacted before leaving their source surface. Restrict relay output to minimal evidence snippets, opaque identifiers, timestamps, and classifications; apply short retention to assembled diagnostic records.
- depends on: A stable shared correlation envelope for jobId, requestId, commandId, surface, observedAt, and freshness; Indexed access to existing job/receipt/log/ops records; A tested redaction policy for Mac command output and authenticated browser data


## What it asked for

_Nothing._
## Its own summary

Recorded three new owner-facing gaps and one concrete relay change: cross-surface truth reconciliation, departure handoff briefs for unattended Mac/browser work, and evidence-backed failure explanations; plus the causal failure-forensics correlator needed to make existing jobs/receipts/logs useful together. These are explicitly read-only and avoid automatic retries or mutations.

**Biggest unknown:** Whether the existing Mac and browser surfaces already expose enough unsaved-work, active-tab, and post-action observation data to implement the departure brief and freshness reconciliation without new local instrumentation.

