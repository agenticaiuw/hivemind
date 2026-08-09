# Harness derivation — faculty-perception — round 152

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac observability and permissions** — At 2026-08-08T02:13Z /ops/snapshot reports Mac agent healthy, Accessibility and Screen Recording granted, all required permissions ready, relay reachable with D1, browser extension online on Safari tab x.com, and zero pending browser commands. The registered relay devices still do not include a pendant; pipeline contains historical nrf9160 events, not proof of a live device.
  - evidence: GET /ops/snapshot HTTP 200 at 2026-08-08T02:13Z; GET /browser/status HTTP 200; discover devices lists only home-macbook-bridge and cloudflare-contract-test; GET /pipeline shows dated historical nrf9160 entries.

## Capabilities it proposed

### "“Is the system telling me something contradictory right now, and which claim should I trust?”"
- **useful because:** Today the dashboard can simultaneously show a healthy Mac, historical nrf9160 pipeline events, and no registered pendant; a completed run can coexist with no playback evidence. This capability produces a ranked contradiction report instead of silently choosing one story, explicitly separating live observations, historical telemetry, and unknowns before the owner relies on an answer or action.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → unified → faculty-perception → faculty-judgement
- **model tier:** background for continuous comparison; realtime only when the owner asks or before a consequential action
- **latency:** Under 2 seconds from cached snapshot; up to 10 seconds for a fresh cross-surface read
- **cost:** About $0.002–$0.01 per on-demand report; dominated by one small reasoning call, not device I/O
- **security:** Must expose only metadata and redacted snippets, never browser secrets or raw audio. A contradiction is not permission to act; destructive or external actions still require confirmation.
- **missing:** A normalized observation schema with observedAt, source, freshness, claim, and confidence; A contradiction engine that knows structural caveats (historical pipeline nrf9160 events do not establish a registered pendant; relay accepted audio does not establish hearing); One authenticated aggregator route or in-process reader joining /ops/snapshot, /pipeline, relay device status, browser status, and job receipts

### "“Is the pendant physically connected and exchanging real audio with this Mac right now? Prove it with a fresh test, or tell me exactly what is missing.”"
- **useful because:** The relay registry cannot answer this: the pendant has never registered, while the nRF9160 and ESP32 are physically USB-attached hardware in the build environment. A perception-only lab probe would distinguish source-level support, serial presence, firmware identity, live bridge audio counters, relay reachability, and actual playback—rather than mistaking historical pipeline records for a live wearable.
- **path:** mac-terminal → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** cheap deterministic probe and classifier; use realtime only to explain an ambiguous result to the owner
- **latency:** 5–15 seconds for serial enumeration and a bounded loopback; never wait indefinitely on a missing chip
- **cost:** <$0.001 per probe; cost is local serial/audio I/O, with no model call unless interpretation is ambiguous
- **security:** Serial paths and firmware logs may contain identifiers; return stable pseudonyms and counters, not credentials or raw microphone audio. Require explicit consent before any active audio test that plays sound or transmits.
- **missing:** A read-only Mac route that enumerates the known USB serial paths, identifies chip/firmware build, and reads bounded health counters; A safe test protocol with nonce-correlated uplink/downlink frames and a timeout, without writing routine data to the SD failure buffer; A relay-side correlation record that distinguishes USB-local exchange from LTE/relay delivery

### "“Before you act on what you read in my browser, re-check that the exact page and account still show it, and show me the evidence you used.”"
- **useful because:** A browser result can be stale, come from the wrong tab, or be a login wall while the Mac agent still has a valid-looking job. This pre-action perception gate would re-inspect the session-affine tab, compare a redacted content hash and locator to the earlier claim, and downgrade or stop when the page, account, or value changed. It makes browser automation trustworthy without granting the model authority to decide whether a changed value is acceptable.
- **path:** browser-extension → mac-vision → mac-planner → faculty-perception → faculty-judgement → faculty-action → relay-realtime
- **model tier:** deterministic hash/locator comparison first; cheap text model only for semantic equivalence; realtime only for spoken explanation
- **latency:** 1–3 seconds for an extension inspection; under 6 seconds if a visual fallback is needed
- **cost:** <$0.003 per check when DOM/text is available; visual fallback dominates cost and latency
- **security:** Keep secrets and full page bodies on the Mac; send only redacted claims, hashes, locator metadata, and a small masked excerpt to judgement. Never treat an extension-reported URL alone as proof of account identity.
- **missing:** A mounted browser provenance route and a join from browser commandId/receiptId to an evidence capsule (the schema exists but the route is unmounted); A freshness policy per action type (for example, recheck payment totals and messages immediately, research claims within a bounded age); An action hook that refuses to execute when session affinity, locator, hash, or account checks fail

### "“Show me everything from my browser, Mac, relay, and wearable that was used to form this answer, and let me remove any one source before you repeat it.”"
- **useful because:** Today evidence is fragmented: browser provenance is partly unmounted, relay browser reads may have no capsule, and routine announcements can retain page text without a source URL. The owner cannot inspect or selectively retract the actual evidence chain behind a spoken answer. This would provide a human-readable causal bundle with source, timestamp, transformation, redaction, and revocation state, then regenerate the answer without the rejected source.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → unified → faculty-perception → faculty-judgement
- **model tier:** Cheap deterministic assembly and redaction; use the expensive realtime model only to explain the bundle conversationally.
- **latency:** Under 3 seconds for an existing answer; under 8 seconds when a source must be re-read and the answer regenerated.
- **cost:** $0.002–$0.01 per bundle, dominated by regeneration rather than evidence assembly.
- **security:** The bundle itself is sensitive. Keep raw content local where possible, expose only redacted excerpts and hashes, require confirmation before exporting it, and make revocation prevent future reuse rather than pretending it erases third-party copies.
- **missing:** A causal bundle ID propagated through voice turns, browser commands, Mac jobs, relay reads, pipeline events, and announcements; A relay-to-Mac evidence transport using the existing capsule and provenance schemas; A revocation-aware answer cache and regeneration path

### "“Before anything leaves my Mac or browser, tell me exactly what data is crossing to the relay, why, how long it will live, and block it if it violates my rule.”"
- **useful because:** The owner currently cannot see or control the boundary where browser text, audio, announcements, and job metadata leave the machine. In particular, relay-fetched or routine-generated page text can become durable announcement speech without a traceable source or enforced expiry. This is a user-visible privacy control, not another status page: it makes data egress explainable and stoppable.
- **path:** browser-extension → mac-terminal → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Deterministic classifier and policy engine; a small background model may classify ambiguous fields, never the realtime tier by default.
- **latency:** Less than 100 ms for known-safe metadata; under 2 seconds for a new content classification. Block rather than wait when classification is uncertain.
- **cost:** Near-zero for rules and hashes; under $0.005 for occasional local classification.
- **security:** The inspector must itself avoid copying secrets to the relay. Policies and decisions belong on the Mac, with tamper-evident receipts; owner confirmation is required for any exception or raw-content upload.
- **missing:** A single egress interception point covering browser reads, audio uploads, announcements, and Mac-to-relay job payloads; A durable, owner-editable data classification policy with deny-by-default categories; Relay enforcement that accepts a signed allow receipt and rejects unapproved content, plus actual announcement/audio deletion and retention enforcement

### "“Tell me when something you told me has become unsafe to rely on, and replace it only after checking the original source again.”"
- **useful because:** Spoken answers currently become uncatalogued memory: the owner cannot know whether a price, message state, news fact, or browser-derived instruction has changed. This capability would attach validity conditions to claims, monitor the relevant source while the owner is away, issue a concise correction on the pendant or Mac, and preserve the old claim as superseded rather than silently rewriting history.
- **path:** browser-extension → mac-planner → relay-realtime → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Background/scheduled low-cost model for monitoring and comparison; realtime only for an urgent spoken correction.
- **latency:** Owner-defined: seconds for safety-critical claims, minutes to hours for ordinary facts; correction delivery must wait for a trusted reachable surface.
- **cost:** $0.001–$0.02 per monitored claim per refresh, dominated by browser or web retrieval; use hashes and conditional checks to avoid model calls.
- **security:** Monitoring must be opt-in per claim and must not retain private page content unnecessarily. A changed source is evidence for re-review, not automatic permission to change settings, send messages, or spend money.
- **missing:** A claim registry with source locator, content hash, validity interval, consequence class, and owner policy; A scheduler that can re-open the same authenticated browser tab or source and compare it without losing session affinity; A correction/dismissal delivery protocol that records whether the owner saw the correction, not merely whether bytes were sent


## Changes it proposed to its own stack

### `context` — Add a mandatory evidence-status envelope to every faculty-perception result: each assertion carries observedAt, freshness class (live/recent/historical), source, and an explicit unknown reason; downstream judgement rejects unlabelled assertions for consequential actions. Seed it with the newly verified state that Mac permissions are ready and browser is online, while nRF9160 pipeline entries remain historical unless a device-originated heartbeat exists.
- **owner gets:** The owner stops hearing confident sentences assembled from mixed-time evidence. They get “Mac and Safari are live; this pendant event is historical; playback is unverified” in the answer itself, and actions cannot quietly turn a stale record into a present fact.
- effort: Medium: shared envelope type, adapters for pipeline/jobs/browser/relay readers, and a judgement guard; no new hardware required.  ·  risk: Some existing responses will become slower or refuse actions that used to run. Recover by allowing an explicit owner-confirmed override recorded with the same envelope; never silently fall back to unlabeled claims.
- cost: Negligible storage and token overhead; roughly 20–80 metadata tokens per assertion, cheaper than a second reasoning call.  ·  latency: Usually none with cached metadata; fresh-source checks add 1–3 seconds only when freshness has expired.
- security: Improves security by preventing stale browser or relay claims from authorizing actions; metadata must redact URLs, tokens, and raw audio.
- depends on: A shared observation envelope consumed by unified, faculty-judgement, and faculty-action; The existing GET /ops/snapshot and GET /pipeline readers; A defined freshness policy distinguishing Mac/browser liveness from relay history and pendant playback


## What it asked for

_Nothing._
