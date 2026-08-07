# Harness derivation — mac-planner — round 11

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Every morning, give me a concise briefing of today’s calendar, unread priority messages, weather, and the files I need for my first meeting; let me ask follow-ups and open anything I mention.”"
- **useful because:** It turns scattered desktop and web state into an actionable briefing without making the owner hunt through apps. The Mac bridge can inspect local meeting files and open the exact document on request; the browser/server handles authenticated web sources.
- **path:** relay-realtime receives the spoken request and plays a short answer → scheduled relay job gathers calendar/mail/weather via browser/server integrations → Mac planner uses accessibility APIs to read only explicitly configured apps and locate/open local files → dashboard shows source links, last refresh, and a per-item privacy scope
- **model tier:** Scheduled collection and summarization use a cheap background model; realtime is used only for the owner’s spoken follow-up. Deterministic extraction/ranking should happen before the model so few tokens are sent.
- **latency:** Briefing ready by the scheduled time; spoken follow-up under 2 seconds for cached items, up to 5 seconds when a fresh browser or Mac read is needed.
- **cost:** Roughly $0.01–$0.05 per daily briefing depending on message/calendar volume; dominant cost is source text, so send changed items and fixed-length snippets only. Audio cost is limited to the short response.
- **security:** Mail and calendar are sensitive. Default to metadata and sender/subject, with body access scoped per source and a visible allowlist. Never send attachments or unrelated local files to the relay. Opening a file is reversible and can be automatic; sending, deleting, replying, or changing events requires explicit confirmation. Keep an audit trail and expiry for cached content.
- **missing:** First-party calendar/mail connector or browser-extension source adapters; A scheduled-job API with incremental cursors and per-source scopes; Mac accessibility readers that return structured app data rather than screenshots; Per-item redaction and retention policy in the relay

### "“Prepare me for my next meeting: find the agenda and related local documents, summarize the open decisions and prior action items, and put the three most relevant files in a folder I can open.”"
- **useful because:** It removes repetitive search across calendar notes, local folders, and web links, producing a bounded packet rather than an unreviewable dump.
- **path:** relay or dashboard accepts the meeting name/time → background model resolves the calendar event and asks Mac planner for structured local-file search → Mac planner searches configured project roots and reads only matching documents, then creates a dated packet folder and an index note → browser bridge fetches linked agenda pages when authenticated access is needed → dashboard and pendant report sources and offer an ‘open packet’ action
- **model tier:** Use deterministic filename/full-text search and a cheap background model for extraction and deduplication. Use realtime only if the owner asks a conversational follow-up. Escalate to the stronger model only for conflicting or highly technical documents.
- **latency:** 1–3 minutes for a complete packet; cached meeting metadata and opening the result should be near-instant.
- **cost:** About $0.02–$0.15 per packet, dominated by document text extraction and summarization; cap input by selecting relevant sections and local incremental hashes.
- **security:** Local project files and meeting content may be confidential. Require an initial project-root allowlist, keep processing on the Mac where possible, and send only extracted passages needed for the summary. Creating a folder/index is a reversible, low-risk mutation and can be automatic; sharing, emailing, or moving originals requires explicit confirmation.
- **missing:** Structured local search/read API with root allowlists and file-type limits; Calendar-event resolver and link extraction; A background job queue and completion notification; Document parsing/OCR for common formats


## Changes it proposed to its own stack

### `mac-harness` — Replace FULL_CONTROL_MODE's undifferentiated execution path with a typed action broker: structured read/open/search actions by default, and separate mutation/destructive/secret-access actions carrying an expiring confirmation token. Add immutable local audit records (request, target, result, timestamp), idempotency keys, bounded output, and an undo/rollback plan where possible. Keep accessibility ui_* as the preferred targeting mechanism.
- **owner gets:** The owner keeps broad automation, but a mistaken or malicious instruction is less likely to delete files, send messages, or expose credentials. They can see exactly what happened and recover from supported mutations.
- effort: Medium: modify local-agent executor and bridge schema, add policy tests and dashboard audit view; migrate existing action types incrementally.  ·  risk: Some existing automations may fail when they use arbitrary shell or scripts; compatibility mode can be opt-in for a short migration window. Audit storage itself must not capture secrets; redact arguments and cap output.
- cost: Negligible API cost; modest local disk for rotating audit logs (for example, 10–50 MB).  ·  latency: Reads remain near-current latency; confirmation adds a human round trip only for risky actions. Token validation is sub-millisecond.
- security: Major improvement: current FULL_CONTROL bypasses actionRisk entirely, allowing arbitrary shell, AppleScript, network, and destructive operations without confirmation. Typed allowlists and secret redaction reduce blast radius.
- depends on: Define shared action-risk taxonomy and confirmation-token endpoint; Add dashboard/pendant confirmation UX; Provide migration mapping for existing run_shell/run_applescript jobs

### `memory` — Unify fleetContext and the knowledge graph behind a scoped memory service that stores facts with provenance, sensitivity, confidence, expiry, and last-used timestamps. At request time retrieve only a small task-relevant packet; maintain rolling session summaries instead of replaying full history. Add explicit ‘forget this’ and per-surface visibility controls.
- **owner gets:** The assistant remembers useful preferences and ongoing projects without repeatedly making the owner pay for or expose irrelevant history. Sensitive Mac facts do not silently appear in pendant or iOS conversations.
- effort: Medium-high: schema migration, retrieval/ranking, redaction, surface policy, and backfill of existing sessions.  ·  risk: Bad retrieval or stale facts could cause wrong actions. Show provenance and confidence, expire volatile facts, and allow correction/forgetting; retain raw history only under the existing retention policy.
- cost: Likely lowers token spend per turn substantially; embedding/index cost is small relative to repeated prompt tokens. No audio cost change.  ·  latency: Adds a local/D1 retrieval step (tens to low hundreds of ms), offset by smaller model prompts.
- security: Sensitivity labels and surface scopes reduce cross-device leakage. Encryption/access controls and strict deletion semantics are required; never index raw secrets or credential stores.
- depends on: Define memory sensitivity classes and per-surface policy; Add D1 indexes/retrieval endpoint; Update all surfaces to consume one compact context packet

### `model-routing` — Introduce a policy router that classifies requests into realtime dialogue, deterministic Mac/browser execution, cheap background summarization, or high-reasoning escalation. Cache stable system/integration context, pass only retrieved snippets, and let long jobs return a job ID plus completion notification rather than holding the voice turn open.
- **owner gets:** Simple actions feel immediate and inexpensive, while long research continues without making the owner wait or pay for a realtime model. Results arrive when ready and can be opened from any surface.
- effort: Medium: intent/risk classifier, job state machine, model budgets, and consistent result cards across web/menubar/iOS/pendant.  ·  risk: Misclassification could send a sensitive action down the wrong path or produce a weak summary. Use conservative escalation for uncertainty, enforce action policy independently of model choice, and allow “use the careful model” override.
- cost: Should reduce realtime-token and audio spend by routing routine work to cheaper models; background jobs add modest worker/model calls.  ·  latency: Immediate acknowledgment under a second; background completion varies by task. Cached deterministic actions remain fast.
- security: Routing is not authorization: every executor still enforces scopes and confirmations. Job payloads need encrypted storage, TTLs, and no secrets in notification text.
- depends on: Typed action broker and risk taxonomy; Unified job/result schema across relay and Mac bridge; Background worker/scheduler and notification channel

### `dashboard-ux` — Add a unified Jobs and Approvals view shared by web, menubar, and iOS: each job shows purpose, sources accessed, files/apps touched, risk level, estimated cost, progress, result, expiry, and one-tap approve/deny/cancel. Pendant receives only a terse notification and can approve predefined low-risk actions, while detailed evidence remains on screens.
- **owner gets:** The owner can start work from voice, see what the assistant is doing, stop it before a risky step, and retrieve completed results later without repeating the request.
- effort: Medium: shared SvelteKit components, Worker job endpoints, Mac bridge status callbacks, and notification/deep links.  ·  risk: A confusing approval screen could cause accidental approval. Use plain-language previews, default deny for destructive actions, short-lived tokens bound to exact action hashes, and show changed-file/message recipients before execution.
- cost: Small storage/UI cost; reduces repeated voice turns and therefore can lower API/audio cost.  ·  latency: No impact on safe immediate actions; status updates should stream within a few seconds for long jobs.
- security: Makes authorization auditable and phishing-resistant if tokens are action-bound and single-use. Avoid displaying sensitive content in push notifications or shared screens.
- depends on: Typed action broker; Unified job/result schema; Cross-surface authentication and notification/deep-link support


## What it asked for

_Nothing._
## Its own summary

I proposed four owner-facing improvements: a scheduled morning briefing, meeting-preparation packets from calendar/local docs/web, a model/job router for cheap asynchronous work, and a unified cross-surface jobs/approvals dashboard. I also proposed the critical Mac harness hardening (typed allowlisted actions, confirmation tokens, immutable redacted audit, bounded output) and scoped, provenance-aware memory retrieval to reduce both leakage and repeated prompt cost. These are grounded in the confirmed stack: FULL_CONTROL currently bypasses all risk checks, one shared SvelteKit dashboard serves web/menubar/iOS, D1/R2 back the relay, and the Mac bridge is polled for jobs.

**Biggest unknown:** I still need the owner’s actual configured apps, project-root allowlist, calendar/mail providers, preferred briefing time, and notification preferences to turn these into deployable routines. I also need the existing bridge job/result schema and authentication details to specify the typed-action and approval protocol without guessing. No further physical-device proposal is justified from my Mac role without pendant/I/O specs.

