# Harness derivation — mac-planner — round 132

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Don't interrupt me at the wrong time. Collect anything urgent from my pendant, Mac, calendar/mail, and logged-in browser, decide whether it can wait, and deliver it through the right surface when I'm actually available. If I miss it, leave one sourced, expiring queue item I can acknowledge later."
- **useful because:** Current briefs and page watches can find information but cannot arbitrate attention across surfaces. This would prevent stale browser alerts during meetings, avoid repeated spoken interruptions, and preserve one auditable handoff from discovery to delivery and acknowledgment.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background/cheap model for event normalization, deduplication, urgency scoring, and capsule composition; realtime tier only for the brief spoken handoff or a live follow-up question.
- **latency:** Event ingestion under 5 seconds; quiet-mode decisions under 1 second; spoken handoff under 2 seconds after an availability event; background reconciliation can take minutes.
- **cost:** Usually <$0.01 per event batch using a cheap model; realtime cost only when the owner answers or requests explanation. Dominant cost is browser extraction and repeated context, reduced by hashes and compact citations.
- **security:** Calendar/mail/browser content is private and should remain local or authenticated relay paths; capsules must carry source URLs/snippet hashes, sensitivity labels, expiry, and delivery audit. Never infer urgency from an offline or unauthenticated browser. Require explicit owner action for any send/submit; acknowledgment is not approval to mutate external systems.
- **missing:** A shared attention-state event schema (pendant availability, quiet hours, meeting/foreground state, browser health, urgency, expiry).; A relay-side durable attention queue with deduplication, leases, acknowledgment/snooze/expire, and exactly-once delivery receipts.; Pendant availability/quiet-mode events and a low-friction acknowledge/snooze gesture.; Mac read-only implementations (the granted mac_readonly_inspect and mac_read_sources currently return schema-only errors) plus a foreground/meeting signal.; Browser liveness envelope and command epoch integration so stale/offline tabs cannot generate current alerts.; A dashboard view showing queued capsules, provenance, expiry, and delivery history.

### "When I'm in a meeting or around other people, keep private browser, mail, and calendar details out of spoken responses. Tell me only that something needs attention, and put the details in a local Mac review panel until I explicitly unlock them."
- **useful because:** Timing/quiet-mode alone does not prevent accidental disclosure: a perfectly timed voice alert can still speak a subject line or account detail aloud. This creates a cross-surface privacy boundary while retaining useful awareness.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Cheap/background classifier for sensitivity labels and meeting-state reconciliation; realtime model only produces a generic redacted sentence. No model should receive full content when a local rule can redact it.
- **latency:** Privacy decision must complete before any spoken payload (<100 ms after an event); local review panel can update within 2 seconds; unlock and detail retrieval may take 1–3 seconds.
- **cost:** Near-zero for rule-based redaction; <$0.005 only for ambiguous sensitivity classification. Main cost is local/browser extraction, not generation.
- **security:** Sensitive payloads remain on the Mac or authenticated browser session; relay receives opaque item IDs, urgency, and redacted text by default. Meeting detection should use Calendar/foreground signals, not microphone capture. Explicit unlock is scoped, time-limited, and logged; never read full content aloud while privacy lock is active.
- **missing:** A privacy-state contract shared by pendant, relay, and Mac (public, private, meeting, unlocked-until).; Local Mac review panel/API that can hold encrypted detail payloads and release them only after a deliberate unlock gesture.; Browser/Mail/Calendar sensitivity metadata and redaction before relay serialization.; A pendant privacy-lock and scoped unlock gesture that works offline and survives reconnect.


## Changes it proposed to its own stack

### `relay` — Add an attention-envelope and durable attention-queue protocol between event ingestion and delivery. Each item has eventId, source, observedAt, freshness deadline, urgency/reason, sensitivity, required surface, quiet-policy result, browser command epoch, dedupe key, capsule URL/snippet hash, and state {queued,snoozed,delivered,acknowledged,expired,blocked}. Accept availability transitions from pendant and Mac, re-evaluate only on meaningful transitions, and emit one delivery receipt plus an owner-visible explanation.
- **owner gets:** The owner gets one calm, trustworthy place for things that need attention instead of duplicate voice alerts and stale browser findings. They can understand why something was held back and recover missed items after reconnecting.
- effort: Medium: shared schema, D1/R2 queue and lease worker, event reducer, relay delivery adapter, and dashboard endpoint; add contract tests for offline tabs, meeting quiet mode, reconnect, duplicate events, and expiry.  ·  risk: A bad urgency rule could delay something important or spam the owner. Recover with conservative defaults (urgent safety/security events may break quiet mode; everything else queues), visible reason codes, expiry warnings, and replayable event logs. Do not mutate external systems.
- cost: Low background storage/compute; roughly one small D1 row and occasional R2 capsule per item. Cheap model only for ambiguous ranking; no new realtime call for routine queue operations.  ·  latency: Sub-second state re-evaluation and seconds-to-minutes for background extraction; reconnect delivery is immediate once a lease is acquired.
- security: Private snippets remain encrypted/local where possible; source permissions and sensitivity travel with the envelope. Browser session tokens never enter the capsule. Dashboard and acknowledgment endpoints require bearer auth.
- depends on: Browser extension typed liveness states and command epoch; Pendant availability/acknowledge event skill; Working implementations of mac_read_sources and mac_readonly_inspect; A relay durable queue/receipt store

### `integration` — Add a cross-surface intent-claim coordinator for every owner request. Normalize the request into an intentId, then let relay, Mac, and browser workers advertise capabilities and acquire short leases on individual subtasks (read, draft, execute, deliver). Claims include dependency edges, idempotency key, cancellation epoch, and expected side effects; a coordinator prevents two surfaces from acting on the same intent, merges receipts into one causal timeline, and reassigns only expired or explicitly cancelled leases. A pendant interruption or reconnect advances the cancellation epoch rather than starting a duplicate run.
- **owner gets:** The owner can say one thing naturally while several surfaces work, without getting duplicate drafts, two browser submissions, repeated notifications, or a Mac action racing a browser action. If a laptop sleeps or the browser disconnects, work resumes safely and the owner receives one coherent result instead of conflicting reports.
- effort: High: intent normalization, lease store, dependency-aware scheduler, cross-surface receipt correlation, cancellation/reassignment protocol, and failure-injection tests for reconnects, duplicate voice turns, stale browser epochs, and Mac sleep.  ·  risk: A lease bug could strand work or incorrectly suppress a needed action. Recover with short bounded leases, visible pending/blocked states, deterministic idempotency keys, append-only receipts, and a manual retry that starts a new intent generation. It must coordinate execution, not silently authorize high-impact actions.
- cost: Low persistent storage and queue compute; cheap model only for ambiguous intent decomposition. Avoids duplicate model/browser/Mac work, likely reducing cost overall.  ·  latency: Adds tens of milliseconds for claim acquisition; parallel subtasks remain parallel. Recovery waits for lease expiry unless a cancellation/reconnect event arrives.
- security: Claims carry capability and sensitivity labels but never session secrets. Workers receive only their subtask's minimum context. Every external mutation remains attributable to one intent generation and one surface receipt.
- depends on: A shared intentId/idempotency-key format across relay jobs, POST /execute, browser command queue, and pendant events; A durable lease/claim store and event stream; Receipt correlation that can link GET /jobs/:jobId/receipts with browser and Mac results; Explicit cancellation/reconnect epochs from the browser extension and pendant


## What it asked for

_Nothing._
## Its own summary

I found and recorded two genuinely useful cross-surface gaps beyond the existing page-watch/briefing backlog: (1) attention escrow, which combines browser health/epoch, Mac availability/meeting context, pendant availability, urgency, expiry, and acknowledgment into one deduplicated delivery queue; and (2) a privacy boundary mode that lets the system alert me generically while keeping mail/calendar/browser details local until an explicit, scoped unlock. I aligned the first with browser-extension's proposed liveness states and told judgement/action agents about both. The immediate blocker is not a missing route: the newly granted mac_readonly_inspect and mac_read_sources are schema-only and return implementation errors, so the Mac cannot yet provide the context these cross-surface decisions need. The existing FULL_CONTROL path also still has no gates, but that matches owner policy.

**Biggest unknown:** Whether the orchestrator will implement the granted Mac read-only adapters and pendant privacy/availability events; without those, attention and privacy decisions must remain conservative and cannot reliably distinguish a meeting, offline browser, or safe delivery moment.

