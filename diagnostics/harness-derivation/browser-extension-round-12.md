# Harness derivation — browser-extension — round 12

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Check my logged-in web accounts for anything urgent, summarize it, and draft (but do not send) any replies that need my attention."
- **useful because:** This uses the browser's unique access to authenticated pages, turning scattered inbox/task systems into one concise audio-friendly brief while preserving the owner's control over outbound communication.
- **path:** relay-realtime receives the request and speaks a short confirmation → Mac browser harness opens the relevant existing Safari tabs or navigates to approved services, reads pages, and creates drafts → dashboard and iOS show extracted items, citations, and the exact unsent drafts → pendant plays the finished summary as audio
- **model tier:** Use a cheap background planner/extractor for page parsing and deduplication; use realtime only for the initial conversation and final concise narration. Escalate ambiguous interpretation to the planner model, not the realtime model.
- **latency:** A 30–90 second background run is acceptable; return partial results service-by-service if one site is slow. Never wait synchronously in a voice turn for the whole sweep.
- **cost:** Typically low: a few planner calls plus page text tokens; materially cheaper than narrating every page. Audio cost is one short summary, not a continuous browser session.
- **security:** Reading private pages is expected, but credentials and page contents must stay on the Mac/relay job scope and not enter durable memory by default. Drafting is reversible; sending mail, posting, or changing account state must stop and display the exact target and content for explicit confirmation.
- **missing:** A first-class authenticated-account sweep job with per-site allowlist and deduplication; A browser result format that preserves URL/title/quoted evidence for citations; A draft artifact state distinct from an executable send action; A background-job-to-audio notification path on the pendant

### "Every weekday morning, check my logged-in calendar, task board, and travel reservations, then tell me the three things I need to know and prepare a suggested plan."
- **useful because:** It provides a personalized morning brief from sources that public search cannot access, without forcing the owner to open multiple services.
- **path:** Mac scheduler runs while the Mac is awake and invokes browser navigation/read actions for the configured services → planner model normalizes events, detects conflicts, and generates a three-item brief → dashboard/iOS show source links and editable plan details → pendant receives a short audio notification and plays it on demand
- **model tier:** Scheduled extraction and conflict detection use a cheaper slower model. Realtime only handles follow-up questions when the owner asks about the brief.
- **latency:** Run 1–3 minutes before the chosen delivery time; tolerate a stale-source warning rather than blocking the entire brief.
- **cost:** Low-to-moderate per weekday, dominated by authenticated page extraction and planner context. Cache unchanged pages and send only deltas to keep token cost down; one short audio rendering per brief.
- **security:** Store only normalized dates, titles, locations, and links—not full page text or credentials. Travel and calendar data is sensitive; service access should be explicitly configured. Planning is safe, but booking, canceling, or inviting attendees requires confirmation.
- **missing:** Per-routine browser account/service configuration and selectors resilient to UI changes; Delta cache with expiration and source freshness indicators; A durable audio notification/queue for scheduled results; Timezone and sleep/wake handling when the Mac is offline

### "Watch this logged-in page for a meaningful change and tell me when it happens, with the before-and-after evidence."
- **useful because:** It turns browser access into an asynchronous monitor for shipment status, appointments, application portals, price/availability, or account notices without requiring the owner to remember to check.
- **path:** owner creates the monitor from voice or dashboard with URL, cadence, and change description → Mac scheduler runs browser reads on the Safari session and compares normalized page sections → relay stores a compact diff and sends a pendant audio notification plus dashboard evidence → owner can open the cited page and decide whether to act
- **model tier:** Use deterministic text/DOM hashing and a cheap extraction model for routine diffs; call the planner model only when the change is semantically ambiguous. Realtime is used only for the notification conversation.
- **latency:** Cadence can be 15 minutes to daily depending on the use case; alert within one polling cycle, not real-time streaming.
- **cost:** Low when hashes and targeted selectors avoid full-page model calls; cost scales with polling frequency and page size. Audio is only generated on meaningful changes.
- **security:** Repeated private-page access and notifications can reveal sensitive information to anyone near the pendant. Require explicit monitor setup, allow pause/delete, minimize stored snapshots, and never auto-submit or purchase based on a change.
- **missing:** Persistent monitor definitions and per-monitor cadence; Stable selector/region extraction with login/session failure detection; DOM/text diff and sensitive-content redaction; Notification queue with deduplication and quiet hours


## Changes it proposed to its own stack

### `browser-harness` — Add a durable browser job runner with two backends: the authenticated Safari bridge for owner-private pages and Cloudflare Browser Run for public pages. Represent each step as navigate/read/extract/click/type, persist evidence (URL, title, timestamp, selected text), retry transient failures, and expose a job result stream to the planner.
- **owner gets:** Private work keeps using existing logins, while public research no longer wakes or monopolizes the Mac. Results become auditable instead of being an opaque summary.
- effort: Medium-high: job state machine, backend selection, evidence schema, retries, and Safari-tab bootstrap/selection.  ·  risk: A stale tab or changed website can extract the wrong data; mitigate with URL/domain constraints, visible evidence, freshness checks, and stopping on unexpected forms. Recover by retrying or asking the owner to inspect the page.
- cost: Lower average token and Mac usage for public research; Cloudflare browser execution adds per-run infrastructure cost. Persisted evidence increases storage modestly.  ·  latency: Public jobs can run in parallel and usually improve latency; private Safari jobs remain bounded by extension polling and a 45-second command timeout.
- security: Critical separation: never send Safari cookies/page contents to the server-side browser backend. Domain allowlists and redaction are needed before evidence enters D1 or model context.
- depends on: A working browser command enqueue route (currently the available enqueue wrappers are stubs); Cloudflare Browser Run credentials/configuration; Evidence redaction and retention policy

### `memory` — Replace raw browser-page insertion into context with expiring, source-backed facts: store only normalized facts plus source URL, observedAt, confidence, and sensitivity class; keep full extracts in short-lived encrypted job artifacts and prune them automatically.
- **owner gets:** The assistant remembers useful outcomes without repeatedly exposing private page contents or paying to resend large histories on every turn.
- effort: Medium: schema migration, extraction contract, TTL/pruning worker, and surface prompt generation from the graph rather than hand-written per-surface sections.  ·  risk: Over-aggressive normalization can lose nuance or retain a wrong fact. Keep source links, confidence, and user-visible correction/delete controls; never treat low-confidence facts as actions.
- cost: Reduces recurring context-token costs and D1 growth; modest extraction overhead per job.  ·  latency: Slightly slower first extraction, faster subsequent conversations due to smaller context.
- security: Strong improvement through minimization and TTLs; sensitive classes (health, finance, private messages) should default to no durable retention.
- depends on: A typed browser evidence/result schema; A unified context-builder used by web, menubar, iOS, and pendant; Retention/deletion controls in the dashboard

### `dashboard-ux` — Add a Jobs inbox shared by web, menubar, and iOS: each job shows status, source links, last update, evidence snippets, sensitivity, proposed actions, and a prominent 'ready to send/submit' preview. Include per-routine pause/run-now/edit controls and a delivery preference for pendant audio.
- **owner gets:** The owner can see what the assistant did while away, listen to completed work, correct a draft, and confidently approve irreversible actions without reconstructing hidden browser activity.
- effort: Medium: shared SvelteKit components, job APIs, audio queue UI, and action-preview state.  ·  risk: Too much detail can overwhelm; default to a three-line summary with expandable evidence. An incorrect status could cause mistaken approval, so show freshness and exact destination prominently.
- cost: Small UI/API cost; reduces repeated conversational explanations and therefore token/audio spend.  ·  latency: No effect on execution; dashboard updates should stream or poll every few seconds for active jobs.
- security: Private job details must inherit account/user auth, use short-lived artifact URLs, and redact secrets from previews. Approval should be explicit for send/purchase/submit despite unrestricted underlying access.
- depends on: Durable background job/artifact model; Audio notification queue; Unified auth and sensitivity metadata

### `interaction` — Make browser work explicitly two-phase: 'inspect' returns a concise result with citations and a proposed action; 'apply' repeats the exact destination, fields/content, and irreversible effect, then waits for owner confirmation. Allow the owner to say 'continue' only for that displayed proposal, while reversible navigation/filling can proceed immediately.
- **owner gets:** They get fast hands-off research and form preparation without accidental messages, purchases, or submissions, and can understand exactly what will happen before committing.
- effort: Medium: action-plan state tied to browser job IDs, confirmation expiration, and voice/dashboard rendering.  ·  risk: Confirmation could be misapplied to a changed page; bind it to URL, target, and content hash, and invalidate after page changes or timeout.
- cost: Slightly more planner/UI tokens for previews, offset by fewer retries and accidental actions.  ·  latency: No added delay for inspection; one short confirmation turn before irreversible execution.
- security: Materially reduces high-impact mistakes while preserving maximum access for reversible actions; no broad capability gate is introduced.
- depends on: Evidence-backed browser jobs; Shared Jobs inbox; Working browser command enqueue path


## What it asked for

_Nothing._
## Its own summary

I proposed concrete browser-first capabilities: authenticated account triage with unsent drafts, weekday calendar/task/travel briefs, logged-in page-change monitors, and a two-phase inspect/apply interaction. I also proposed a durable dual-backend browser job runner, evidence-backed expiring memory, and a shared Jobs inbox across web/menubar/iOS with pendant audio delivery. These designs use cheap background extraction/planning for scheduled and page-parsing work, reserving realtime for short conversations and notifications; they minimize page/audio/context costs and stop before irreversible sends, purchases, or submissions. The most important implementation dependency is a real browser command enqueue path: Safari is online, but the available enqueue wrappers remain stubs. I informed mac-planner to prioritize that and to keep Safari-private data separate from server-side public browsing.

**Biggest unknown:** Whether the orchestrator will provide a functioning browser enqueue endpoint (POST /execute dispatch through the Mac bridge) this round. Without it I can design browser workflows but cannot execute or validate them. Other needed pieces are durable browser evidence/job artifacts, an audio notification queue, and unified sensitive-data retention controls.

