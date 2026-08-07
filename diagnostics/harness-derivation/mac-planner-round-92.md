# Harness derivation — mac-planner — round 92

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac_readonly_inspect** — The granted read-only inspection tool is present in the agent schema but currently returns an implementation error for running_apps and browser_tabs, so it cannot yet supply the foreground-app/current-tab evidence needed for a context handoff packet.
  - evidence: Parallel calls to mac_readonly_inspect(operation=running_apps) and operation=browser_tabs returned: 'This tool was granted a schema but has no implementation yet.'

## Capabilities it proposed

### "“I’m switching tasks—make me a handoff packet.”"
- **useful because:** A single pendant trigger would preserve the exact work context the owner is leaving: current meeting/calendar context, relevant unread/recent mail, the authenticated browser page they were viewing, and a concise list of unfinished Mac work. It would save a cited, redacted packet in ~/AI-Pendant-Workspace and put a short audio summary in the pendant queue, so the owner can resume later or hand the context to another surface without reconstructing it.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use the realtime tier only to interpret the short spoken trigger and return the confirmation; use a cheaper background model to rank/extract the packet and generate its summary. No microphone needs to remain open after the trigger.
- **latency:** Acknowledge the pendant trigger in under 1 second; produce the packet in 5–15 seconds, with a durable job status if the browser or Mac is offline.
- **cost:** Roughly $0.01–$0.05 per packet, dominated by background extraction/summarization and any browser-page content; relay/D1/R2 costs are negligible at normal use.
- **security:** Read-only by default. Restrict browser collection to the current explicitly open tab/session, redact secrets and credentials before persistence, mark every field with URL/source/timestamp/TTL, and never include captured secret-mode facts. Saving locally is allowed, but the owner should get a spoken list of sources and a dashboard delete action. No email, form submission, or file deletion occurs.
- **missing:** A pendant trigger/event that starts a server-side durable packet job and queues its result for later audio playback; A browser bridge operation that returns current-tab identity plus bounded, redacted semantic text with provenance; A shared packet schema and redaction pass joining mac_read_sources, browser evidence, and Mac job/context records; A reliable local file write/atomic replace path for ~/AI-Pendant-Workspace handoff artifacts; Implementation of the granted mac_readonly_inspect tool (especially foreground app and browser tabs), or an equivalent read-only route

### "“Are my plans still valid?”"
- **useful because:** Today the owner must manually compare Calendar, recent Mail, and authenticated browser pages when reservations, meetings, deliveries, or appointments change. This capability would detect contradictions across those sources, explain exactly what disagrees, identify the most reliable/latest evidence, and prepare a reviewable correction plan without silently changing anything.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use the realtime tier only for the short question and spoken result. A cheaper background model performs source comparison, date/entity normalization, contradiction classification, and evidence ranking.
- **latency:** Speak an acknowledgement within 1 second; return an answer within 10–20 seconds. If a browser source is unavailable, return a partial result with the missing source explicitly named.
- **cost:** Approximately $0.02–$0.08 per investigation, dominated by reading and comparing authenticated page text and generating the evidence-backed explanation.
- **security:** Read-only unless the owner separately asks to change a calendar event or draft a reply. Restrict browser reads to explicitly bound sessions/pages, redact credentials and secret-mode memory, keep evidence snippets minimal, and attach source URLs/timestamps. Any proposed correction must show before/after values and require the owner's existing confirmation policy before sending or mutating.
- **missing:** A durable cross-source contradiction record keyed by normalized person/event/reservation and observation time; Common entity/date normalization and source-precedence rules shared by Calendar, Mail, and browser extraction; A browser extraction result containing bounded text, semantic fields, URL, tab identity, and observedAt timestamp; A spoken-result and dashboard evidence view that can cite disagreement and let the owner mark one source as authoritative


## Changes it proposed to its own stack

### `integration` — Add a durable Context Handoff Job protocol between pendant/relay, browser bridge, and Mac planner. A job has a triggerId, source allowlist, per-source TTL, sensitivity/redaction policy, evidence records (surface, tabId/app, URL/path, observedAt, content hash), and a deterministic output manifest. The relay fans out bounded reads to mac_read_sources and the browser bridge, polls Mac job receipts, runs redaction/summary in the background tier, writes an atomic Markdown+JSON packet under ~/AI-Pendant-Workspace/handoffs/<id>/, and publishes a compact audio summary plus a dashboard link. If any source is offline, the packet is still committed with explicit gaps and a retryable status rather than silently mixing stale context.
- **owner gets:** Task switching stops losing the state of work. The owner gets a trustworthy, resumable handoff rather than a vague AI summary, and can see exactly which calendar/mail/tab/file observations support it.
- effort: Medium: shared schema, relay durable job state, Mac atomic writer, browser current-tab extraction, redaction tests, and pendant queue integration.  ·  risk: Authenticated page text or private mail could be persisted incorrectly, or stale observations could look current. Mitigate with source allowlists, short TTLs, field-level sensitivity labels, hashes/provenance, explicit partial status, and a one-command delete/undo of the packet. Failure recovery resumes by triggerId without duplicating files.
- cost: Small background-model and storage cost per handoff; no realtime generation beyond the trigger acknowledgment. Local disk usage is bounded by a configurable retention sweep.  ·  latency: Immediate acknowledgment; 5–15 seconds for a complete packet, with durable completion notification if a source is slow.
- security: Improves security by making provenance and redaction mandatory at the integration boundary; it does not expand permissions beyond existing read-only Calendar/Mail/browser access and local file writing.
- depends on: Implementation of mac_readonly_inspect or an equivalent foreground-tab read route; A relay durable-job/audio-queue endpoint for asynchronous completion; Browser bridge current-tab bounded extraction with provenance; Atomic local packet writer and packet retention/delete policy

### `integration` — Create a cross-source commitment reconciliation layer. Normalize Calendar events, Mail commitments, and authenticated browser records into typed claims (subject, time range, location, status, source, observedAt, confidence), cluster claims by entity, detect conflicts and supersession, and emit an evidence bundle rather than a single merged fact. Add explicit source-precedence rules, freshness windows, and an owner-resolvable 'accept this source' decision that records the decision without altering the underlying systems.
- **owner gets:** The owner can ask whether a plan is still valid and receive an honest answer when systems disagree, instead of acting on a stale calendar entry or missing an email change.
- effort: Medium-to-high: schema and normalization, browser extraction contract, conflict classifier, evidence UI/audio rendering, and tests for timezone, recurring events, cancellations, and duplicate reservations.  ·  risk: Incorrect entity matching or precedence could produce false certainty. Always expose competing claims, use uncertainty language, expire stale claims, and never mutate source systems from reconciliation alone. Recovery is to discard the derived bundle and recompute from fresh reads.
- cost: Small durable storage cost; background model calls are modest but scale with the number of sources and claims compared.  ·  latency: Adds several seconds for parallel reads and normalization; realtime response should remain a brief acknowledgement while the background job completes.
- security: Creates a sensitive derived view combining Mail, Calendar, and private browser data. Encrypt or access-control evidence bundles, minimize retained snippets, apply field-level redaction, and provide deletion/retention controls.
- depends on: Typed browser extraction with provenance; Shared temporal/entity normalization library; Durable reconciliation job and evidence-bundle storage; Dashboard and pendant rendering for competing claims


## What it asked for

_Nothing._
