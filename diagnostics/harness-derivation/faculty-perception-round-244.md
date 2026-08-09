# Harness derivation — faculty-perception — round 244

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac and browser observability** — At 2026-08-09T02:15Z the Mac agent reports Accessibility and Screen Recording granted, all required permissions ready, computer-use loop enabled with vision model and 25 max steps; Safari browser bridge online with 2 tabs, YouTube active, zero pending commands. Relay reachable, D1-backed, Mac bridge online; no pendant appears in live devices inventory.
  - evidence: read_continuity_snapshot since 2026-08-09T01:00Z include relay,pipeline: HTTP 200 GET /ops/snapshot; status.permissions.ready=true, accessibility.trusted=true, screenRecording.granted=true, browser online Safari tabCount=2, pendingCommands=0, relay reachable/store=d1/macBridgeOnline=true.

## Capabilities it proposed

### "Before I rely on that, prove it: show me the exact source, what the Mac/browser/relay currently observe, how fresh each observation is, and say UNKNOWN instead of smoothing over a disagreement."
- **useful because:** This would be the system's most valuable perception primitive: it prevents a confident voice answer from turning a stale browser page, a Mac-side completion, or relay socket delivery into a false fact. It uses the newly live visual permissions to verify the final UI state, while preserving source and freshness per claim.
- **path:** browser → mac → relay → pendant
- **model tier:** Use a cheap background verifier for hashes, timestamps, and cross-source comparison; escalate only unresolved contradictions to the realtime model for the spoken explanation.
- **latency:** 2-5 seconds for existing telemetry and browser evidence; up to 15 seconds when a fresh Mac visual verification is required.
- **cost:** Usually under one cheap text-model call; the dominant cost is one optional vision screenshot and browser/Mac round trip, not realtime tokens.
- **security:** Browser evidence may contain private logged-in content and screenshots may expose secrets. Store redacted content hashes and claim snippets by default, require confirmation before exposing page bodies, and never treat relay-admin delivery as owner-heard.
- **missing:** A relay-to-Mac evidence bridge: read_web_page must return a stable request ID and content hash, then the Mac must mint the existing evidence capsule and browser provenance record.; A claim-level response schema linking each assertion to capsuleId/contentHash, observer, capturedAt, and freshness/unknown reason.; When a pendant exists, firmware playback events must join the same artifact ID; the current registry and job completion are not hearing evidence.

### "Tell me when the system's bodies disagree about reality — for example the browser is alive but the Mac bridge is stale, a relay job says complete while playback is unconfirmed, or a device vanished without a heartbeat — and show me which sensor wins and why."
- **useful because:** The current surfaces each publish local truth with different clocks and failure modes. A contradiction detector would catch silent split-brain states before judgement or action relies on them, rather than producing another optimistic aggregate.
- **path:** relay → mac → browser → pendant
- **model tier:** Run deterministic comparison and freshness rules in the background; use a cheaper text model only to compress a multi-conflict explanation. Realtime is reserved for speaking an already-established alert.
- **latency:** Continuous checks every 30-60 seconds; alert within one minute of a contradiction, with no model call for ordinary agreement.
- **cost:** Near-zero model cost during agreement; occasional low-cost summarization when multiple conflicts coexist. Storage is a bounded ring of conflict records.
- **security:** Do not expose URLs, screenshots, or job contents in the alert unless asked. Device absence is not automatically failure because pendant registration and heartbeat are structurally incomplete today; label sensor coverage and confidence explicitly.
- **missing:** A normalized observation envelope with source, observedAt, receivedAt, monotonic sequence, clock domain, and declared coverage.; A policy table for precedence (device playback over relay socket bytes; direct browser heartbeat over stale Mac cache) and an explicit no-winner state.; A relay endpoint or scheduled worker that compares registry, Mac snapshot, browser heartbeat, pipeline, and eventual pendant beacon without requiring the realtime voice process.

### "When I come back, show me a forensic before/after of the things that changed while I was gone: the exact browser tab state, Mac UI state, relay job state, and any wearable audio that was actually played — not just a list of completed jobs."
- **useful because:** A time-bounded return snapshot answers the owner's real question ('what changed?') with visual and delivery evidence, while distinguishing observed transitions from inferred or missing ones. It is more useful than a best-effort digest because it captures the boundary state before it is overwritten by count-capped stores.
- **path:** pendant → mac → browser → relay
- **model tier:** Use deterministic snapshot/diff and local redaction first; a cheap summarizer turns the resulting change set into a short briefing. Realtime only speaks it when the owner asks through the wearable.
- **latency:** Take a lightweight baseline on departure and a delta on return in under 3 seconds; visual recapture can add 5-10 seconds for selected changed tabs.
- **cost:** Low: bounded JSON state and hashes dominate, with one cheap summarization call per return. No continuous screenshots; capture only transitions and explicitly selected tabs.
- **security:** Snapshots can contain private page text and screen images. Encrypt or redact at capture, retain hashes plus small snippets, and require confirmation to reveal sensitive changes. A missing pendant event must be shown as missing, never as no playback.
- **missing:** A departure/return boundary signal from the pendant or an explicit Mac/browser presence signal.; A durable, bounded transition store that records pre/post observations and source clocks, rather than reconstructing from count-capped logs after the fact.; The relay-to-Mac browser provenance bridge and a device-originated played/interrupted event keyed to each audio artifact.

### "While I was away, did anyone—or any part of you—open, read, change, or send anything sensitive? Give me a privacy audit with actors, timestamps, and action types, but do not show me the sensitive contents unless I explicitly ask."
- **useful because:** Today the owner can inspect scattered jobs, browser commands, receipts, and relay traces, but cannot obtain a trustworthy, content-minimizing account of access. This would reveal accidental exposure or an unexpected agent action without copying the private material into another briefing.
- **path:** browser → mac → relay → pendant
- **model tier:** Use deterministic event correlation, redaction, and actor classification in the background; use a low-cost text model only to summarize an unusual access chain. Realtime is unnecessary except when the owner asks verbally.
- **latency:** Under 5 seconds for a bounded recent audit; under 30 seconds for a historical window after indexing.
- **cost:** Low recurring cost: hashes, actor IDs, and event metadata dominate; model use only for anomaly summaries. Sensitive bodies stay local and are not sent to the model by default.
- **security:** The audit itself is sensitive and must use pseudonymous actor IDs, encrypted local storage, strict retention, and explicit confirmation for content reveal. It must distinguish observed access from inferred access and report missing telemetry instead of claiming no access.
- **missing:** A tamper-evident, append-only cross-surface access ledger with event IDs, actor identity, source clock, target classification, and redacted action outcome.; Browser-extension and Mac agent hooks that emit read/access events for tabs, files, messages, and automation—not merely command completion.; Relay-side audit events for voice turns, browser-rendering reads, announcements, and job payload access, plus a signed ingest path from a future pendant.; A query route that returns redacted audit records and coverage gaps without exposing raw bodies.

### "At any past moment, show me the exact belief state you were operating from: which facts, permissions, device states, and browser observations were available then, what you did not know, and why the next action was reasonable at that time."
- **useful because:** A present-day log cannot answer whether an error was understandable when it happened; current state overwrites the evidence. This temporal accountability view lets the owner distinguish bad judgement from stale or missing perception and challenge an action without exposing every raw conversation.
- **path:** relay → mac → browser → pendant
- **model tier:** Construct the historical state deterministically from signed observation and decision envelopes; use a cheap summarizer for the owner-facing explanation. Realtime should only narrate the already reconstructed timeline.
- **latency:** Immediate for a recent event; up to 20 seconds for a long historical chain or a cross-device clock reconciliation.
- **cost:** Moderate local storage for compact state deltas; low model cost. The expensive part is retaining signed metadata, not inference.
- **security:** Historical belief states may contain private claims and secrets. Redact values into classifications and hashes by default, enforce per-owner access, encrypt the ledger, and make uncertainty and clock skew visible rather than fabricating an exact order.
- **missing:** A signed decision envelope emitted before each action containing input observation IDs, model/policy version, permissions snapshot, uncertainty, and intended effect.; Immutable cross-surface observation deltas with both device monotonic time and relay receipt time; current count-capped traces are not sufficient.; A clock-reconciliation and causal-link layer joining browser commands, Mac ledger steps, relay jobs, and future pendant events.; An owner-facing historical query route with redaction and explicit coverage gaps.

### "Forget this subject everywhere: find every copy, derived summary, browser capsule, audio recording, queued announcement, and Mac trace that came from it; delete or irreversibly redact what policy allows, and show me what remains and why."
- **useful because:** The owner cannot currently know where one sensitive interaction propagated, much less obtain a complete deletion receipt. A subject-level erasure capability would turn privacy from scattered retention settings into a verifiable end-to-end operation across the hive.
- **path:** relay → mac → browser → pendant
- **model tier:** Use deterministic content hashes, provenance links, and retention policy evaluation for discovery and deletion; use a cheap model only to identify semantically derived summaries when hashes cannot match. Realtime is only the conversational front end.
- **latency:** Preview in under 10 seconds; destructive execution may take minutes and must remain resumable until every surface reports a receipt.
- **cost:** Moderate storage/indexing cost and occasional low-cost semantic matching; no realtime cost beyond the owner's request. The dominant work is securely sweeping D1, Mac files, browser evidence, audio, and offline queues.
- **security:** This is destructive and must require explicit confirmation after a complete preview. Preserve only minimal tombstones and legal/operational audit metadata; never delete an unrelated artifact on a fuzzy match. Offline pendant data must be reported as pending rather than claimed erased.
- **missing:** A shared content lineage ID propagated from voice turn through relay job, browser read, Mac action, announcement/audio artifact, and future pendant playback.; Deletion and redaction APIs with receipts on D1, Mac stores, browser capsule/provenance stores, audio retention, and pendant nonvolatile queues.; A policy engine that distinguishes owner content, derived content, immutable audit tombstones, and data that cannot yet be reached because a device is offline.; A final cross-surface erasure certificate listing verified deletions, remaining tombstones, and unresolved offline items.


## What it asked for

_Nothing._
## Its own summary

Fresh discovery changed an important constraint: the exact AI Pendant Agent now has Accessibility and Screen Recording, permissions.ready=true, computer-use vision enabled, Safari bridge online with two tabs, relay reachable on D1, and Mac bridge online. There is still no registered pendant. I recorded that live fact and proposed three non-duplicate capabilities: (1) the system's trust boundary—claim-level proof with source/hash/freshness and explicit UNKNOWN; (2) a cross-body contradiction detector for browser/Mac/relay/pendant disagreements; and (3) a departure/return forensic before-after showing actual UI, job, and playback transitions. The single most useful is the first, because every other action depends on not mistaking stale or socket-level state for reality.

**Biggest unknown:** The pendant remains physically absent from the relay registry, so no live wearable boundary signal or playback telemetry can be verified. To complete these capabilities, the system still needs the relay-to-Mac browser provenance transport, a bounded transition store plus departure/return signal, and a device-originated playback event keyed to each audio artifact. Accessibility no longer needs owner action; it is live now.

