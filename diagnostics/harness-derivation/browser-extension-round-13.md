# Harness derivation — browser-extension — round 13

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Every morning, check my private calendar, travel reservations, and important account notifications in Safari, then give me a concise spoken briefing with links and only flag things that need my attention."
- **useful because:** Combines authenticated sources the server cannot access into one hands-free briefing, while avoiding costly realtime browsing during conversation.
- **path:** browser → relay → pendant → dashboard
- **model tier:** Background planner (cheap batch model) runs browser reads and deduplication; realtime model only speaks the final 30–60 second summary. Use server web search only for public context.
- **latency:** Runs asynchronously in 2–5 minutes; cached result is ready before the owner's routine. Playback starts immediately when requested.
- **cost:** Low: a handful of browser page extracts plus a short summary; dominant cost is model tokens from changed private pages, reduced by hashes and per-site cursors.
- **security:** Private calendar/account content leaves Safari through the local bridge to the Worker. Store only extracted event/task summaries, not page bodies; encrypt in transit/storage. Never click external links that trigger actions; read-only by default and require confirmation for any booking, cancellation, or reply.
- **missing:** Scheduled job trigger with per-site authenticated browser session; Browser extraction normalization and change hashing; Encrypted per-user secret/session policy and retention controls

### "When I ask, find the exact information on a logged-in website—such as my latest bill, a delivery status, or an insurance claim—and read me the answer, citing the page and date."
- **useful because:** Authenticated lookup is the browser tier's unique advantage over public search and avoids making the owner manually hunt through portals.
- **path:** pendant → relay → browser → dashboard
- **model tier:** Realtime model classifies intent and confirms the target site; browser agent performs deterministic navigation/extraction; cheap model compresses the result. Escalate to realtime only for ambiguous follow-up conversation.
- **latency:** First answer in 10–30 seconds; if a site is slow, return a progress notification and finish asynchronously.
- **cost:** Low to moderate per lookup; browser latency dominates, while bounded DOM extraction and a short answer keep token cost small.
- **security:** Do not expose full account numbers, health data, or page dumps in audio; redact sensitive fields and speak only requested values. Read-only actions need no confirmation; changing settings, downloading documents, or sending anything requires explicit confirmation.
- **missing:** Site-specific extraction schemas with redaction; Tab/session isolation and sensitive-field redaction before model input; Progress and timeout events surfaced to pendant

### "Draft a form, email, or support request from information on this private webpage, fill it in, and show me exactly what will be submitted before I approve it."
- **useful because:** Turns authenticated browser access into useful work while preserving a hard safety boundary before irreversible external actions.
- **path:** browser → dashboard → relay → pendant
- **model tier:** Background planner extracts facts and drafts with a cheap model; realtime is used only to resolve ambiguities and present the final concise preview.
- **latency:** Draft within 30–60 seconds. Pause indefinitely at the submit/send button until approval; after approval, a deterministic browser action completes it and returns confirmation.
- **cost:** Moderate for long forms; minimize by extracting only relevant labels/values and using local template filling. Browser time and page complexity dominate.
- **security:** A malicious page could inject instructions; treat page text as untrusted data and never let it override policy. Display recipient, fields, attachments, amount, and final body. Require explicit one-time confirmation immediately before submit/send/purchase; never reuse approval.
- **missing:** Structured action preview/approval protocol; DOM field mapping with origin and recipient display; Prompt-injection isolation for webpage content

### "Watch my authenticated order, appointment, and account pages for changes, and tell me only when a meaningful change happens—never pollute my daily briefing with unchanged pages."
- **useful because:** A private-site change detector saves repeated manual checks and uses the browser only when necessary, especially for delivery, appointment, and billing portals that require login.
- **path:** browser → dashboard → relay → pendant
- **model tier:** Cheap scheduled worker compares normalized DOM/content hashes and extracts changed fields; realtime is not involved unless the owner asks a follow-up. Use background model only when a change needs semantic classification.
- **latency:** Polling cadence configurable from 15 minutes to daily; notification within one polling cycle. Respect site rate limits and back off on errors.
- **cost:** Low when hashes are compared locally and unchanged pages skip model calls; browser requests and scheduled Worker invocations dominate.
- **security:** Watching pages can reveal sensitive health/financial information. Keep per-site allowlist, minimize stored diffs, redact identifiers, provide pause/delete controls, and never follow newly appearing links or trigger actions automatically.
- **missing:** Scheduled browser jobs with rate-limit/backoff; Normalized page snapshot hashing and semantic diff; Notification deduplication and per-site sensitivity controls


## Changes it proposed to its own stack

### `browser-harness` — Add a reliable browser command queue with request IDs, idempotency keys, tab/session affinity, typed results (page metadata, extracted text, screenshots), and explicit irreversible-action checkpoints. Replace the current single 45-second wait with progress events and resumable polling.
- **owner gets:** Private-site tasks stop timing out or acting on the wrong tab, and the owner gets understandable progress instead of a silent failure.
- effort: Medium: bridge and extension protocol changes plus dashboard/pedant progress handling.  ·  risk: Queued duplicate commands could double-click; enforce idempotency and cancel-on-timeout. Extension disconnects should leave the page untouched and mark the task unknown rather than retrying writes.
- cost: Small Worker/storage overhead; lower model cost from fewer retries and smaller typed extracts.  ·  latency: Same best-case latency; better long-page tasks can continue asynchronously rather than blocking 45 seconds.
- security: Per-tab origin/session binding and action audit logs reduce cross-site leakage; screenshots should be opt-in and short-lived.
- depends on: Structured browser action/result schema; Dashboard approval UI

### `model-routing` — Route public web research to web_search, authenticated read-only lookups to a cheap browser-extraction model, long multi-page workflows to background planner, and reserve realtime for intent, ambiguity, and spoken delivery.
- **owner gets:** Answers arrive faster and cost less without sacrificing conversational quality where it matters.
- effort: Low to medium: routing policy, token budgets, and evaluation set of browser tasks.  ·  risk: Cheap model may miss nuance; use confidence thresholds and escalate when extraction conflicts or sensitive fields appear.
- cost: Material reduction in realtime tokens and audio duration; browser work remains bounded by changed content only.  ·  latency: Public answers faster; private workflows may complete asynchronously but do not hold the conversation open.
- security: Sensitive page text can be processed by a restricted model path with redaction and no long-term retention.
- depends on: Sensitive-field redaction; Task confidence and escalation policy

### `dashboard-ux` — Create a unified task timeline showing source site/origin, extracted facts, pending approval cards, exact submit payload, model used, and retention/deletion controls; mirror a compact approval prompt in the pendant audio flow.
- **owner gets:** The owner can trust what happened, approve risky actions knowingly, and recover from a failed browser task without repeating it.
- effort: Medium across SvelteKit dashboard, iOS/WKWebView, and relay event schema.  ·  risk: Too much detail could overwhelm; default to a concise summary with expandable evidence and redact sensitive values by default.
- cost: Minimal UI/storage cost; reduces expensive repeated interactions and accidental actions.  ·  latency: No impact on execution; approval rendering should be instant from stored task state.
- security: Makes recipient, origin, and data egress visible; supports deletion of page extracts and audit history.
- depends on: Typed browser result schema; Action checkpoint protocol; Per-task retention metadata

### `memory` — Store browser tasks as short-lived provenance records: origin, timestamp, normalized facts, confidence, redaction class, approval state, and content hash—not raw authenticated page text. Automatically expire raw extracts quickly and let the owner delete a site’s history from every surface.
- **owner gets:** The assistant can remember useful facts and avoid repeating work without quietly retaining private account pages or leaking them into future conversations.
- effort: Medium: D1 schema, retention worker, redaction pipeline, and shared SvelteKit controls.  ·  risk: Over-aggressive expiry could lose evidence needed to resolve a task; retain a user-visible minimal audit record and let active tasks pin data temporarily.
- cost: Lower storage and future prompt-token costs; small scheduled cleanup cost.  ·  latency: Negligible; hashes and summaries make later lookups faster.
- security: Substantially reduces blast radius of a compromised Worker or prompt injection; provenance prevents confusing one site's facts with another's.
- depends on: Typed browser results; Sensitive-field classifier; Unified task timeline


## What it asked for

### `c13-guqs` (context) — owner's first authenticated browser workflows and sensitivity preferences
- why: No real user workflow has been observed, so prioritization is based on generic high-value private lookups. Knowing the owner's actual sites, routine, and sensitive categories would let me design safer, more useful browser automations.
- would change: I would propose site-specific extraction/redaction rules and schedules rather than generic browsing, and would exclude categories the owner does not want read aloud or stored.

## Its own summary

Browser tier proposals are complete: authenticated morning briefings, on-demand private lookups, draft-and-preview forms, change watchers, reliable tab-bound/idempotent command queuing, cheaper model routing, approval-focused dashboard UX, and short-lived provenance memory. I informed mac-planner and relay-realtime that browser access is uniquely valuable for logged-in pages, while public research belongs to web_search. All irreversible browser actions should stop before submit/send/purchase and show the exact payload.

**Biggest unknown:** The owner's actual authenticated sites, routines, and categories they do not want spoken or retained. I requested that context; until it arrives, site-specific workflows and redaction policies remain generic.

