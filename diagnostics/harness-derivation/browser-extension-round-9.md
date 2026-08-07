# Harness derivation — browser-extension — round 9

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Check my authenticated work sites and inboxes for anything urgent, summarize it, and leave me a short audio briefing.”"
- **useful because:** The browser can access pages behind existing Safari logins that search cannot. A scheduled, read-only sweep turns scattered dashboards and inboxes into an actionable briefing without making the owner wait or repeatedly navigating.
- **path:** dashboard scheduler/configuration → Mac Safari extension for authenticated pages → relay job queue/D1 and R2 audio → pendant playback notification
- **model tier:** Use a cheap background model for extraction, deduplication, and summarization; use realtime only if the owner interrupts with a follow-up. Browser actions are deterministic templates plus read-only DOM extraction, not vision/model calls unless a site layout changes.
- **latency:** Run asynchronously; 1–5 minutes per site is acceptable. Notify only when the digest is ready, with a same-day freshness timestamp.
- **cost:** Low: a handful of browser commands and a small background-model summary; audio generation dominates variable cost, so generate one compressed briefing rather than per-item clips.
- **security:** Read-only allowlist by origin and path; never expose cookies or raw page dumps to the model when redaction can extract fields locally. Do not open links that trigger state changes. Require explicit setup approval for each site and a visible run log; pause on MFA, suspicious redirects, or permission prompts. Data leaves the Mac only as minimized extracted text and the final audio.
- **missing:** Per-site extraction templates and origin/path allowlists; A scheduler and durable job status UI; Local redaction/classification before relay upload; Audio briefing generation and pendant playback/notification

### "“Fill out this web form from my notes, but stop before submitting and show me exactly what will be sent.”"
- **useful because:** It eliminates repetitive authenticated data entry while preserving a clear safety boundary. The owner gets a field-by-field preview and can correct errors before any external side effect.
- **path:** pendant voice request → dashboard preview with diff and source URL → Safari extension to navigate/type/select → relay confirmation token service
- **model tier:** Cheap background model maps notes to typed fields and validates formats; realtime is only for conversational corrections. Deterministic browser runner performs typing. No submission is allowed in this capability.
- **latency:** Preview within 10–30 seconds for ordinary forms; pause indefinitely awaiting confirmation.
- **cost:** Low to moderate: browser interaction plus small extraction/mapping prompt; avoid screenshots and full-page tokens by extracting labels and values only.
- **security:** Classify fields (personal, secret, financial, health). Never type passwords, one-time codes, payment details, or secrets from model-generated text. Display exact origin, every field/value, attachments, and side effects; redact secrets in logs. Submit is hard-blocked unless a separate future capability has an exact, expiring confirmation token.
- **missing:** Typed form-schema extraction and field classification; Preview/diff UI shared by web, menubar, and iOS; Browser command evidence and exact-manifest confirmation binding; A hard block preventing submit/enter-key navigation

### "“Watch this authenticated page and tell me when the status, price, or availability changes.”"
- **useful because:** It replaces manual checking of portals, reservations, deliveries, and project dashboards, alerting only on meaningful changes with evidence and a link back to the exact page.
- **path:** dashboard watch creation and diff history → Mac Safari extension for authenticated reads → background scheduler/job queue → pendant notification and optional audio summary
- **model tier:** Cheap scheduled worker compares normalized, locally extracted fields; use a small model only to explain a semantic change. Realtime is unnecessary unless the owner asks a follow-up.
- **latency:** Polling cadence from 15 minutes to daily depending on site limits; alert within one polling interval, not instant.
- **cost:** Low when using hashes/structured fields and skipping unchanged pages; model and audio costs only on changes.
- **security:** Read-only paths and rate limits prevent accidental interaction and account lockout. Store diffs, not entire pages; redact personal/order/payment data. Never auto-book or purchase when availability appears—offer a link and require a fresh explicit action.
- **missing:** Durable scheduler with per-site rate limits; Normalized field extraction/diff engine; Change alert routing and retention controls; Site-specific allowlist/recipe UI


## Changes it proposed to its own stack

### `browser-harness` — Replace generic browser action results with a typed, policy-enforcing runner: classify commands as read-only or mutating; enforce origin/path allowlists; capture tabId, URL/origin, DOM evidence hash, timestamps, and normalized action manifests; redact secrets locally; re-check origin and DOM immediately before each action; hard-block submit/send/purchase/booking/delete/account/security operations by default.
- **owner gets:** Browser help becomes trustworthy: it can research and prepare work quickly without accidentally sending messages, spending money, or changing accounts, and the owner can see exactly what happened.
- effort: Medium: extension protocol/result schema, local-agent policy engine, dashboard evidence viewer, tests against common forms and redirects.  ·  risk: False positives may stop harmless interactions; recover with an owner-visible override path for explicitly allowlisted low-risk mutations. A stale DOM or redirect must fail closed rather than act on the wrong page.
- cost: Small per-run metadata overhead; no meaningful model-token increase because evidence is structured and redacted before upload.  ·  latency: Adds milliseconds to local checks plus one DOM revalidation per action; avoids expensive retries and unsafe recovery.
- security: Strongly improves containment: cookies remain in Safari, sensitive fields are not logged, and confirmations bind to the exact tab/origin/fields rather than a vague request.
- depends on: A confirmation-token service for any future permitted mutation; A shared dashboard preview/evidence component

### `memory` — Add a browser-site capability registry in the knowledge graph: per origin, allowed paths, login/session status (never credentials), extraction recipe, sensitivity class, last successful run, and owner-approved schedules. Inject only the relevant site policy into each browser job instead of the full fleet context.
- **owner gets:** Requests like “check my billing portal” become reliable and brief: the system remembers what to read, what not to touch, and when it last checked, without repeatedly asking or leaking unrelated context.
- effort: Medium: schema/API, dashboard editor, local-agent policy cache, migration from prompt-written surface context.  ·  risk: An outdated recipe or permission could expose stale or wrong data; expire recipes after layout/origin changes, require reapproval for new paths, and fail closed on uncertainty.
- cost: Reduces recurring prompt tokens and page-context upload; small D1 storage cost.  ·  latency: Faster setup and fewer model calls; occasional reapproval adds delay only after site changes.
- security: Least-privilege per-site policy and explicit expiry reduce cross-site data leakage; store no cookies or credentials.
- depends on: Typed browser evidence/policy engine; Dashboard controls for origin/path and sensitivity approvals


## What it asked for

_Nothing._
## Its own summary

I aligned with mac-planner on a fail-closed browser safety contract: typed read-only vs mutating evidence, hard blocks for send/payment/booking/delete/account changes, exact one-use confirmation manifests, origin/DOM revalidation, session isolation, local redaction, and timestamps. I proposed three owner-facing capabilities: scheduled authenticated read-only briefings with audio, form completion previews that never submit, and change/availability monitoring. I also proposed a typed browser policy/evidence harness and a least-privilege per-site memory registry. Remaining implementation needs are a confirmation-token service, shared evidence/preview UI, per-origin allowlists and extraction recipes, local sensitive-data redaction, a scheduler/diff engine, and audio notification/playback integration. Current Safari has no tab, so browser navigation must remain explicit and fail closed on MFA, redirects, or missing tabs.

**Biggest unknown:** Whether the existing local-agent/browser bridge can expose structured DOM fields and enforce policy before typing, or only return opaque extension results; this determines how much redaction, evidence capture, and safety enforcement must be added to the extension versus the Mac agent.

