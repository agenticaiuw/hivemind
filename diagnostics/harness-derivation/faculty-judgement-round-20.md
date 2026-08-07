# Harness derivation — faculty-judgement — round 20

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I have to go—keep this moving, and when I’m back tell me only what changed and what you still need from me.”"
- **useful because:** Today a half-finished task loses context when the owner walks away, while Mac/browser claims may be unverified. This creates a safe, presence-aware handoff: capture the exact task and evidence at departure, continue only reversible work while away, then deliver a short delta and surface the smallest set of decisions on return.
- **path:** pendant: spoken departure/return plus long-press checkpoint and concise audio delta → relay: durable task lease, checkpoint, expiry, cancellation, and event stream → mac-planner/mac-terminal: continue allowlisted reversible work and write typed receipts → browser-extension: continue authenticated reads/drafts only, preserving tab/session provenance → mac-vision: attempt UI work only when accessibility/screen recording are trusted; otherwise mark blocked rather than claiming success → unified: reconcile checkpoint, receipts, and fresh evidence into a return brief
- **model tier:** Background model for checkpoint reconciliation and delta summarization; realtime only for the departure/return conversation and clarification.
- **latency:** Departure acknowledgement under 1 second; safe continuation asynchronous; return brief ready within 2–5 seconds from the latest checkpoint, with stale evidence explicitly labeled.
- **cost:** About $0.01–$0.05 per handoff depending on browser/Mac extraction; dominated by authenticated page reads and final summarization, not the short voice turns.
- **security:** The lease must expire and be cancellable; never send mail, delete, purchase, or submit forms while away. Private page contents stay on the authenticated browser path; receipts should store hashes/snippets rather than whole pages. Require explicit confirmation when the owner returns for any irreversible step.
- **missing:** A durable cross-surface checkpoint/lease protocol with idempotent resume and expiry; A pendant long-press/offline checkpoint event and return-presence signal; Typed evidence freshness and blocked-state receipts from Mac and browser; Implementation of the requested resume packet and intent-continuity primitives; A return brief action that can cancel, resume, or approve the next step

### "“Warn me before my commitments collide, and give me the smallest fix I can approve.”"
- **useful because:** The owner currently has separate calendars, mail threads, task boards, reservations, and browser sessions, so collisions are discovered by the owner at the worst moment. This capability builds a cross-source constraint map: travel time, preparation time, promised replies, deadlines, and quiet hours are reconciled into one forecast. It warns only on a high-confidence impending collision, explains the evidence, and offers one reversible fix (reschedule draft, delegation draft, or reminder) instead of flooding the owner with another generic briefing.
- **path:** relay: continuously maintains a time-bounded constraint graph and schedules only high-confidence collision checks → browser-extension: reads authenticated reservations, task boards, and work portals with source URL/tab provenance → mac-planner/mac-terminal: reads local calendars, mail exports, notes, and timezone/travel data; creates drafts or reminders but never sends → pendant: delivers a short interruption only when the collision is near and consequential; otherwise queues it for the next brief → unified: ranks conflicts, detects duplicate/contradictory commitments, and asks one clarifying question when evidence is ambiguous
- **model tier:** Cheaper background model for extraction, normalization, and periodic constraint solving; realtime model only for the owner's spoken clarification and approval.
- **latency:** Normal checks can run asynchronously in seconds to minutes. A high-confidence collision alert should reach the pendant within 10 seconds of new evidence; spoken explanation under 2 seconds.
- **cost:** Approximately $0.02–$0.10 per day for a modest set of sources; extraction and authenticated page reads dominate, while the graph check itself is cheap.
- **security:** Private mail, calendars, reservations, and task data must remain source-scoped and be minimized in relay projections. Never infer or expose sensitive relationship details in a spoken alert. Creating a reminder or draft is allowed by owner policy; sending, canceling, buying, or moving an appointment requires explicit confirmation. Every warning needs cited source snippets and freshness timestamps to avoid acting on stale UI.
- **missing:** A temporal constraint graph with explicit uncertainty, travel/preparation buffers, and source provenance; Connectors that normalize authenticated browser pages and local Mac data into typed commitments; A collision severity policy tied to the owner's interruption preferences and quiet hours; A review surface showing the conflicting items and one-click draft/reminder alternatives; Freshness-aware conflict receipts so stale or unverified Mac/browser state cannot trigger an alert


## Changes it proposed to its own stack

### `integration` — Add a presence-bound task lease and checkpoint envelope shared by pendant, relay, Mac, and browser. On departure it atomically records goal, completed steps, evidence references, blocked/unverified claims, allowed reversible actions, expiry, and pending decisions. Workers heartbeat receipts under that lease; on expiry or cancellation they stop. On return, the relay computes a delta since the checkpoint and exposes three explicit operations: hear brief, resume safe work, or approve the named irreversible step.
- **owner gets:** Walking away no longer means restarting or trusting a false “done” report. Returning gives one honest, short update and preserves the owner's control over consequential actions.
- effort: Medium-high: protocol/schema plus relay persistence, pendant event, Mac/browser adapters, and integration tests for disconnects, duplicate receipts, stale evidence, and cancellation.  ·  risk: A worker could continue after the owner expects it stopped, or a lost return event could leave work paused. Use short leases, server-side cancellation, idempotency keys, visible LED/audio acknowledgement, and default-stop on missing heartbeat. Recover by replaying the last checkpoint and receipts.
- cost: Negligible storage and relay compute; roughly 1–2 KB per checkpoint plus small heartbeat records. Summaries use a cheaper background model; no extra realtime spend except the spoken acknowledgement.  ·  latency: Departure event is immediate; heartbeats add tiny relay traffic. Return reconciliation is typically sub-second for receipts, with browser/Mac freshness checks adding seconds.
- security: Improves least-privilege and auditability by binding actions to an explicit time-limited authorization. Do not copy private page bodies into the relay; retain provenance and redacted hashes. Irreversible operations remain confirmation-gated.
- depends on: durable cross-surface job/event persistence primitives; requested resume_packet and intent_continuity_ledger capabilities; local interruption gate or equivalent pendant departure/return event; typed Mac/browser receipts that distinguish attempted, verified, and blocked

### `context` — Introduce a temporal-commitment graph and collision evaluator as a shared context primitive. Normalize events, deadlines, promised replies, travel legs, preparation blocks, and quiet hours into interval objects with provenance, confidence, freshness, and owner-editable buffer rules. Emit a collision only when independent evidence supports it; attach the minimum conflicting evidence and a ranked set of reversible remedies. Expire graph edges automatically when their source is stale or a receipt confirms resolution.
- **owner gets:** The owner gets an early, trustworthy warning about a real conflict rather than discovering it manually or being interrupted for every calendar change. They can approve the smallest fix without reconstructing the situation across five apps.
- effort: High: source adapters, interval/uncertainty model, deduplication, recurrence handling, timezone and travel calculations, policy evaluation, and a Mac/browser review UI with tests against stale and contradictory sources.  ·  risk: False positives could create alarm fatigue; false negatives could be worse. Start in observe-and-suggest mode, require two-source corroboration for high-impact alerts, show uncertainty, let the owner dismiss/correct each rule, and keep a complete explanation/undo trail. If a source is inaccessible, report unknown rather than assuming free time.
- cost: Small persistent graph storage and background compute. Extraction from logged-in pages and occasional travel estimation dominate API cost; use a low-cost model for normalization and reserve realtime for owner dialogue.  ·  latency: Incremental source updates can evaluate in under a second after normalization; authenticated page refreshes and travel calculations may take seconds. Pendant alerts should be queued if connectivity is absent.
- security: Sensitive commitments are compartmentalized by source and projected as minimal intervals plus redacted labels. The relay should not retain full mail/page bodies. Remedies remain drafts/reminders until owner confirmation, and all alerts carry provenance and freshness.
- depends on: typed context projection with provenance, confidence, and TTL; authenticated browser and Mac read adapters; owner interruption/quiet-hour policy; a review/approval surface for suggested remedies


## What it asked for

### `s4-9h9h` (skill) — offline_handoff_marker
- does: A long press records a departure/return marker locally, plays distinct acknowledgement tones, and queues a compact checkpoint event (timestamp, marker type, current conversation/job id if available, and cancel/resume intent). It must survive a dropped link and upload idempotently when connectivity returns.
- must be on-device because: The owner needs to signal “I’m leaving” or “I’m back” at the moment it happens, even when the relay or Mac is unreachable. Only firmware can guarantee immediate tactile/audio acknowledgement and durable offline capture.
- trigger: Single-button long press (departure), second long press (return), with optional server push to clear or cancel a pending marker.
- storage: Append-only compact records in local flash: roughly 32–64 bytes each, bounded queue of 64 markers (<4 KB), with sequence number and CRC; erase after confirmed relay receipt.
- RAM budget: ~2–4 KB for queue buffers, debounce/state machine, and upload framing—well within 211,608 B application RAM. No speech recognition or model runs on-device.

## Its own summary

Round 20 adds a genuinely cross-surface “walk away / come back” capability: the pendant creates an offline handoff marker, the relay holds a presence-bound expiring lease, Mac/browser continue only reversible work with verified-vs-blocked receipts, and return produces a concise delta plus explicit approval for anything irreversible. I also proposed the shared checkpoint/lease envelope and queued the firmware skill offline_handoff_marker. Still needed to ship it: durable cross-surface event/job persistence, resume-packet and intent-continuity implementations, typed Mac/browser receipts, and the pendant long-press event. Current perception says Mac UI and browser are not trustworthy/online, so those surfaces must fail closed rather than report success.

**Biggest unknown:** The orchestrator’s newly acted-on grants are not visible yet (granted category is empty), and the exact cross-surface persistence/receipt primitives remain unspecified; implementation should wait for those contracts rather than inventing incompatible schemas.

