# Harness derivation — mac-planner — round 246

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If my pendant call goes wrong, tell me exactly why and leave a fix-it report on my Mac—without recording or uploading my conversation.”"
- **useful because:** This is the highest-value reliability feature: a dropped or distorted call currently becomes guesswork. The pendant's QoS counters and diagnostic fixture can identify radio loss, modem starvation, decode CPU pressure, or server delivery failure; the relay can correlate those counters with its job log; the Mac can write a timestamped report and optionally play a one-sentence summary. It turns an invisible failure into an actionable answer while keeping speech content off the report.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** background for correlation and report writing; realtime only for the live call
- **latency:** Emit a compact local symptom within 2 seconds; finish the report within 30 seconds after the call or reconnection.
- **cost:** Usually <$0.01 per incident; dominant cost is one small background correlation/report request, not audio transcription.
- **security:** Transmit counters, timestamps, profile changes, and job identifiers only—not PCM or transcript. Redact modem identifiers and network location. Writing a local report is safe; sending it to a vendor or changing firmware must require explicit confirmation.
- **missing:** A relay endpoint that joins pendant QoS frames, pipeline events, and delivery receipts into one incident timeline; A Mac read-only bounded UART/log collector for the already-accepted diagnostic fixture, or a bench agent that uploads its result; A report template and dashboard card distinguishing owner audio content from technical telemetry

### "“When I press the bookmark button while I’m looking at something in the browser, save the source and a useful local handoff on my Mac, then tell me when it is ready.”"
- **useful because:** It makes the pendant a physical ‘keep this’ control for research, support pages, and forms without requiring the owner to dictate a URL. The browser bridge captures only the active tab's URL/title and a bounded redacted excerpt; the relay deduplicates repeated bookmarks; the Mac creates an append-only Markdown handoff in ~/AI-Pendant-Workspace with timestamp, source, and next-action placeholder, then opens it or leaves it queued. It works with the browser session the Mac cannot otherwise share with the pendant and does not need microphone access.
- **path:** pendant → browser-extension → relay → mac-planner
- **model tier:** background/cheap model for deduplication and a one-line suggested next action; no realtime model unless the owner asks a question
- **latency:** Acknowledge the button locally immediately; capture in under 3 seconds; create the handoff within 10 seconds.
- **cost:** <$0.005 per bookmark; most runs need no model call if URL/title are sufficient.
- **security:** Never capture passwords, form values, cookies, or page body by default. The browser extension must return origin, title, URL, and explicit user-visible excerpt only; redact query strings containing tokens. Opening a file is reversible, but submitting a form or sending a page onward is never implied.
- **missing:** A browser-side bookmark event endpoint that accepts the pendant event and returns a bounded redacted tab snapshot; A stable cross-surface bookmark id so retries cannot create duplicate files; A policy-controlled Markdown handoff writer and optional open-after behavior

### "“When an overnight job or scheduled brief finishes, give me one short spoken result on the pendant and leave the full receipt on my Mac; if it failed, tell me what I can do next.”"
- **useful because:** Scheduled work currently completes out of sight. This creates a durable, low-interruption completion channel: the relay turns job receipts into a three-field card (success/failure, result, next action), queues it through the pendant inbox so it survives a dropped link, and the Mac writes the full evidence and opens it only when useful. A retry is deduplicated by job id, so reconnects cannot produce repeated spoken alerts.
- **path:** relay → pendant → mac-planner → dashboard
- **model tier:** background model for compressing a receipt into one sentence; deterministic templates for status and retry instructions
- **latency:** Publish within 15 seconds of job completion; local pendant queueing is immediate when connected and durable across outage.
- **cost:** <$0.002 per completion, dominated by optional sentence compression; zero model cost for template-only receipts.
- **security:** Speak only redacted status and a short result, never mail bodies, page contents, secrets, or full paths. Keep full receipts local to the Mac/workbench. A retry, deletion, or external submission must be a separate owner command; a spoken alert is informational only.
- **missing:** A relay completion-to-pendant adapter that consumes GET /jobs/:jobId/receipts and emits an expiry/priority-tagged inbox item; A durable idempotency key and acknowledgment protocol spanning relay, pendant_store, and Mac workbench; A Mac receipt materializer that writes the full redacted JSON/Markdown evidence and links it to the spoken card

### "“Whenever you create or change something for me, let me ask ‘why is this here?’ on the pendant and get the source, decision, and exact action receipt—without exposing secrets.”"
- **useful because:** Today a file, browser change, or scheduled brief can outlive the conversation that caused it. The owner cannot reliably tell whether an artifact came from a calendar event, a browser page, a voice request, or a retry. A provenance answer makes automation inspectable and recoverable: the pendant gives a short explanation, while the Mac opens the full evidence only when requested.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic provenance graph first; background model only to compress a linked chain into one spoken sentence
- **latency:** Pendant answer in under 3 seconds for a recent artifact; full chain under 10 seconds.
- **cost:** Near-zero for indexed metadata; <$0.005 when a long chain needs summarization.
- **security:** Store hashes, labels, timestamps, source classes, and receipt ids—not page bodies, mail contents, credentials, or audio. Apply field-level redaction before anything reaches the pendant. The owner must be able to delete provenance separately from the artifact.
- **missing:** A cross-node append-only provenance record with parent/child links and redacted source descriptors; A stable artifact identifier attached to Mac files, browser mutations, pendant inbox cards, and scheduled jobs; A pendant query protocol and Mac UI that resolve ‘why’ to a bounded chain instead of an unconstrained model answer

### "“When I latch privacy on the pendant, make every other surface safe too: stop queued Mac/browser actions, hide sensitive browser state, and tell me when the whole hive is actually quiet.”"
- **useful because:** The existing local privacy latch protects the pendant's microphone and speaker, but a browser session or an already-queued Mac plan can remain active. This capability propagates one physical privacy decision across the surfaces that can still see or change private information, then returns a bounded completion receipt. It is materially safer than assuming that silencing audio means the system stopped acting.
- **path:** pendant → relay → browser-extension → mac-planner → dashboard
- **model tier:** Deterministic event fan-out and acknowledgements; no model call required
- **latency:** Start local mute immediately; request remote quiescence within 1 second; report per-surface acknowledgement within 5 seconds, with timeout states spoken plainly.
- **cost:** <$0.001 per transition; mostly durable event/ack traffic.
- **security:** Fail closed for new automation while latched, but do not claim a surface is safe until it acknowledges. Never transmit tab contents in the acknowledgement. Browser suspension must preserve the session without copying cookies; queued destructive actions must be cancelled, not silently resumed. Local exit remains available offline.
- **missing:** A relay-wide privacy epoch and acknowledgement protocol; Browser-extension handling for suspend/blur/stop-pending-command without touching credentials; Mac planner cancellation/quiescence hooks for queued jobs and an auditable per-surface receipt; A distinct single-LED pattern for ‘local only’ versus ‘all surfaces acknowledged’, or a spoken distinction

### "“Watch the exact authenticated page I’m on until a deadline, and tell me only when the meaningful fields change; keep the old and new evidence on my Mac.”"
- **useful because:** The owner repeatedly has to reopen sessions and check for changes manually. This turns a live browser session into a bounded, user-started watch: the extension keeps the session-local watch, the relay schedules polling and semantic comparison, the pendant speaks only a meaningful delta, and the Mac stores redacted before/after evidence. It is useful for ticket status, appointment openings, shipment updates, and dashboards without granting the agent general portal access.
- **path:** browser-extension → relay → pendant → mac-planner → dashboard
- **model tier:** Cheap background model only for field-level change classification; deterministic DOM selectors and hashes handle unchanged pages
- **latency:** Start watch in under 5 seconds; poll at the owner-selected cadence; alert within one poll interval, capped at 15 minutes for ordinary watches.
- **cost:** <$0.01 per day for a low-frequency watch; browser polling and page snapshots dominate, not inference.
- **security:** The watch must be explicitly scoped to one origin/page and have an expiry. Never store cookies, passwords, free-form page dumps, or hidden fields. Keep before/after snippets redacted and require confirmation before following links, submitting forms, or taking action on a change. If the session expires, report ‘watch paused’ rather than attempting login.
- **missing:** A browser-session watch primitive with origin/page scope, expiry, cadence, and selector/hash configuration; A relay diff scheduler that can distinguish layout churn from meaningful field changes; A redacted before/after evidence writer and pendant alert card with deduplicated change ids


## What it asked for

_Nothing._
## Its own summary

Discovered the live inventory this round: the Mac bridge is online, Safari has two tabs and is online, and the mobile/iOS device is offline. Owner preferences confirm browser reading/clicking is allowed, while mail sending, deletion, and purchases require confirmation. I recorded three non-duplicate cross-node capabilities: (1) automatic privacy-preserving audio incident reports combining pendant QoS/fixture telemetry, relay receipts, and a Mac report; (2) a physical bookmark-button handoff from the authenticated browser tab into a deduplicated local Markdown workspace note; and (3) durable spoken completion cards for overnight/scheduled jobs with full receipts on the Mac. What remains needed is implementation of the three missing seams: a relay incident correlator, a browser bookmark snapshot endpoint, and a completion-to-pendant receipt adapter, plus idempotency and redaction policies. No new tool or permission is needed from the owner this round.

**Biggest unknown:** The exact live schemas and ownership of the browser bookmark event, incident correlation, and completion-to-pendant adapter routes have not been inventoried; the iOS surface is also offline, so none of these proposals should depend on iOS until it returns.

