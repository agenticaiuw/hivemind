# Harness derivation — faculty-perception — round 137

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac and browser observability** — At 2026-08-08T01:18Z, GET /ops/snapshot reports Mac agent and relay reachable, permissions.ready=true with Accessibility, Screen Recording, and listed automation grants; browser extension online with 9 tabs and zero pending commands. GET /observe independently reports inputReachability.status=verified and eventsPost=true.
  - evidence: Authenticated GET /ops/snapshot and GET /observe both returned HTTP 200 with the stated fields; GET /browser/status returned online:true, tabCount:9, pendingCommands:0.

## Capabilities it proposed

### "Tell me what is true right now across my Mac, browser, relay, and pendant—and distinguish observed facts, stale reports, and unknowns."
- **useful because:** This would be the system's single most useful perception function: the owner gets one honest state-of-world answer instead of inferring from five dashboards, with contradictions exposed rather than silently merged.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Background/cheap model for collection and normalization; realtime model only turns the resulting evidence card into a spoken answer.
- **latency:** Under 2 seconds when all surfaces respond; return partial results with per-source freshness after 4 seconds.
- **cost:** About $0.001–$0.01 per invocation; dominated by no model call if the evidence card is rendered deterministically.
- **security:** Must return metadata and scoped excerpts, not page bodies or secrets; browser tab URLs/titles and foreground app are sensitive. Device claims must be cryptographically tied to a device session. Never label relay socket delivery as hearing.
- **missing:** A real resolved continuity-snapshot tool or authenticated aggregator route (the granted tool currently fails resolution); Pendant-originated reality-beacon transport and registry heartbeat; A common event ID/clock normalization layer; Explicit classification schema: observed, reported, stale, contradicted, unknown

### "Before you act on what I said, tell me whether the context you are using is still fresh enough—and recapture it if the browser, document, or device has changed."
- **useful because:** It prevents the most dangerous perception failure: a correct plan applied to a different tab, changed document, stale screen, or disconnected wearable. The owner gets a short reason for any pause instead of a mysterious refusal.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension
- **model tier:** Cheap deterministic freshness/quorum checks; escalate to the realtime model only when sources disagree and the owner must decide.
- **latency:** 150–500 ms for checks; up to 2 seconds for a browser/document recapture.
- **cost:** Typically <$0.002; browser inspection and hashing dominate, not model tokens.
- **security:** Do not transmit full document text to relay; use local content hashes, redacted capsules, tab/session pseudonyms, and sensitivity labels. A stale or missing device signal must fail closed for actions that depend on spoken confirmation.
- **missing:** A mounted semantic AX selected-text/document identity route (current /observe proves reachability but exposes no selection identity); A relay-visible device freshness beacon with monotonic counter; A standard precondition result consumed by faculty-action; Browser capsule/hash reporting for relay-originated reads (the relay currently mints no ID/hash)

### "When I leave my Mac or lose the pendant, save a compact handoff of what changed; when I reconnect, tell me only the changes that are still actionable and show where each came from."
- **useful because:** A reconnect should feel like resuming one mind, not discovering that browser work, Mac jobs, and spoken alerts diverged. This is a handoff checkpoint created at the boundary, not another best-effort history digest.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Background model summarizes only the bounded delta; deterministic code computes changed IDs, statuses, and freshness. Realtime speaks the final 2–3 sentence handoff.
- **latency:** Checkpoint within 1 second of a bridge/browser/device disconnect; reconnect brief under 3 seconds.
- **cost:** <$0.01 per reconnect, usually <$0.003 because unchanged items are hash-compared and omitted.
- **security:** Persist only hashes, job IDs, action receipts, and redacted titles by default; never copy page bodies or audio onto the pendant. Handoff records need expiry, owner-visible deletion, and explicit unknown states for work not observed during the gap.
- **missing:** A durable cross-surface handoff record with monotonic sequence and source watermarks; Actual pendant reconnect/heartbeat and a device-to-relay upload path; A browser event stream that reports tab/session changes, not just current status; A playback acknowledgement path so pending spoken items are not falsely called heard

### "Give me a confidence number that means something: how often has this kind of observation been right before, and what evidence would change your mind?"
- **useful because:** Today confidence is prose and intuition. A calibrated, source-specific confidence lets the owner know when to trust a claim, when to wait, and which missing observation would resolve it—especially for browser state, relay delivery, and device health.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Background model periodically calibrates probabilities from recorded observations and later verified outcomes; realtime only explains the current score.
- **latency:** Under 300 ms to read a score; calibration can run hourly or overnight.
- **cost:** <$0.01 per calibration batch; storage and outcome matching dominate, not inference.
- **security:** Store aggregate calibration buckets rather than raw conversations or page content. Never let confidence override a required confirmation or claim certainty when the reference outcome is missing.
- **missing:** A durable observation-outcome join keyed by source, claim type, and monotonic event IDs; Explicit outcome labels for device heard, browser mutation applied, and relay delivery completed; A UI contract that distinguishes calibrated probability from model self-confidence

### "For any important claim, prove it with two independent witnesses—or tell me exactly why only one witness exists and what I can check myself."
- **useful because:** A Mac receipt saying an action ran is not proof that the browser changed; a relay saying bytes were sent is not proof that audio was heard. Independent witnesses make perception useful for consequential decisions instead of merely persuasive.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Deterministic witness policy and hash comparison; a cheap model summarizes disagreements, with realtime reserved for speaking the verdict.
- **latency:** 1 second for existing witnesses; up to 3 seconds to request a second observation.
- **cost:** <$0.005 per claim; extra browser/screen observations dominate.
- **security:** Witnesses must be scoped to the same artifact and time window, with redacted hashes instead of secret values. A missing witness yields unknown, never inferred success. Require owner confirmation when disagreement concerns external side effects.
- **missing:** A shared artifact identity and observation envelope across Mac, browser, relay, and pendant; A device-originated playback/consumption witness; Relay-to-Mac provenance transport for browser reads; A policy engine that can request a second read without executing or mutating

### "Watch this outcome, not just this app: tell me only when the real-world condition becomes true, and show the smallest evidence that it changed."
- **useful because:** The owner should be able to delegate a perception problem such as 'tell me when the refund is actually posted' or 'when the file is synced,' across a logged-in browser, Mac filesystem, and relay, without repeated polling announcements or false positives from a stale tab.
- **path:** pendant → relay → mac-planner → browser-extension → mac-terminal → dashboard
- **model tier:** Cheap scheduled/event-driven observers evaluate structured predicates; background model extracts a predicate once; realtime only delivers the verified transition to the pendant.
- **latency:** Seconds for browser/Mac events, bounded by the source's update cadence; no more than 5 seconds after a verifiable change is observed.
- **cost:** <$0.01 per watch-day for event-driven sources; scheduled web checks and browser session wakeups dominate.
- **security:** Watch definitions and evidence may expose private accounts. Keep evaluation local where possible, redact values, encrypt state, cap retention, and require confirmation before watches that could trigger external actions.
- **missing:** A durable semantic predicate format with source-specific evaluators; Browser event/change notifications and authenticated page evidence capsules; Mac filesystem/app observers that emit post-change hashes; Relay scheduler support for cross-surface watches and a device-aware notification policy; A real pendant link/ack path so notification state is not confused with hearing


## Changes it proposed to its own stack

### `context` — Add an event-triggered observation journal: on browser tab navigation/title change, foreground-app change, job state transition, relay connectivity transition, or pendant beacon sequence change, capture a small signed observation tuple (source, monotonic sequence, wall time, identity/hash, freshness, redaction class) and publish it to one bounded append-only stream. Do not poll page bodies or audio; capture only deltas and hashes.
- **owner gets:** The assistant can say exactly what changed while the owner was away or before an action, rather than presenting a current snapshot that hides the transition that caused a mistake.
- effort: Medium: browser extension and Mac observer emitters, relay ingestion, bounded storage, and a reader joining source watermarks. No new model training.  ·  risk: Event storms, clock skew, and duplicate delivery could create false changes. Use per-source monotonic sequence, debounce, capped payloads, and visibly mark gaps; recover by taking a fresh full observation.
- cost: Negligible storage and network for metadata; roughly <$0.001 per transition. No page body/audio leaves the Mac unless separately requested.  ·  latency: Sub-second event capture; no impact on normal actions if ingestion is asynchronous.
- security: Improves provenance but increases metadata retention (app names, tab URLs, job IDs). Hash/redact at source, encrypt at rest, short TTL, and owner deletion control.
- depends on: A real common event envelope and source watermarks; Mounted browser provenance routes; Relay ingestion endpoint; current /ops/snapshot and /browser/status are reads only


## What it asked for

_Nothing._
## Its own summary

Fresh probes established a materially better live truth boundary: the Mac agent is reachable; Accessibility, Screen Recording, automation, and input posting are all verified; Safari's bridge is online with 9 tabs and zero pending commands; relay is reachable; and there is still no live nRF9160 pendant. I recorded that evidence, informed action and planner agents, and proposed (1) a cross-surface observed/reported/unknown state-of-world answer, (2) freshness checks before context-dependent actions, (3) reconnect handoff deltas, plus an event-triggered observation journal. The most important gap is not another dashboard: it is a reliable transition/provenance stream and a real pendant-originated heartbeat/playback signal.

**Biggest unknown:** The newly granted read_continuity_snapshot does not resolve at runtime (nearest routes are /ops/snapshot and /pipeline), and no current route can establish USB serial presence, pendant identity, monotonic counter, or disconnect timing. Until those are implemented, I cannot honestly claim a pendant is connected, that an owner heard audio, or that a cross-surface timeline is complete.

