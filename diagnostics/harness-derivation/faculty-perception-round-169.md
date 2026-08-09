# Harness derivation — faculty-perception — round 169

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/relay/browser continuity snapshot** — GET /ops/snapshot is live and currently reports Mac agent ready with Accessibility and Screen Recording granted, relay reachable with D1 store and Mac bridge online, and Safari browser extension online on X (tabCount 9, pendingCommands 0). Local agent reports no pendant registry route; GET /v1/devices/status is 404 on Mac agent.
  - evidence: Authenticated GET /ops/snapshot returned status 200 at round 169; authenticated GET /v1/devices/status returned 404; snapshot timestamps 2026-08-08T03:07:27Z.

## Capabilities it proposed

### "“Before you act, prove that this is still the exact page and state I authorized—not merely the same URL.”"
- **useful because:** Prevents stale-tab and wrong-account mistakes. The browser extension observes the authenticated DOM while the Mac evidence store records a redacted, content-addressed capsule; judgement can refuse when the page, account, or relevant control changed.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → faculty-perception
- **model tier:** Cheap background hashing and deterministic comparison; realtime model only explains a mismatch to the owner.
- **latency:** 1–3 seconds for an on-demand check; under 300 ms when a recent capsule is available.
- **cost:** Usually <$0.002 per check; dominant cost is no model call, with occasional vision escalation <$0.02.
- **security:** Keep raw authenticated DOM local; send only capsule ID, content hash, redacted locator, and mismatch category to the relay. Require explicit confirmation if the account or target control differs.
- **missing:** A mounted browserProvenance route (the module exists but is currently unmounted); A relay-visible capsule ID/hash transport for relay-originated reads; A deterministic stale-evidence gate consumed by faculty-judgement

### "“Can I trust you right now? Give me a one-sentence confidence report before you answer, including what you can actually observe and what is stale or unavailable.”"
- **useful because:** The owner currently cannot distinguish a live Mac/browser observation from historical pipeline data or an absent pendant. A pre-answer reality report would prevent fabricated certainty: it would explicitly say, for example, that the browser is live, the relay is reachable, and the pendant is not registered.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → faculty-perception → faculty-judgement
- **model tier:** Deterministic freshness and capability evaluation; no expensive model call unless the owner asks for an explanation.
- **latency:** Under 250 ms from a cached snapshot; under 2 seconds when refreshing browser and relay state.
- **cost:** Near-zero model cost; one bounded authenticated snapshot and optional browser inspection per answer.
- **security:** Expose only capability/freshness classes and provenance IDs, never URLs, page text, tokens, or private device metadata by default. Mark absent as unknown/unavailable rather than offline.
- **missing:** A real implementation of the continuity snapshot resolver (the granted tool is unresolved; GET /ops/snapshot is the nearest live route); A freshness policy distinguishing live device telemetry, count-capped history, and inferred state; A mandatory judgement preflight that carries the confidence sentence into the spoken response

### "“After any task, show me exactly what data left my Mac or browser, which surface received it, and what will remain stored.”"
- **useful because:** The relay can currently retain scraped page text in announcements without a source URL, while browser capsules and Mac ledgers have different retention rules. A per-task egress receipt would let the owner safely use authenticated browser and voice automation without guessing where speech, page text, or evidence went.
- **path:** browser-extension → mac-planner → relay-realtime → relay → faculty-perception → dashboard
- **model tier:** Deterministic data-flow accounting and retention lookup; a cheaper text model may turn the receipt into a short spoken summary.
- **latency:** Under 1 second after a task; asynchronous completion is acceptable for large jobs.
- **cost:** <$0.003 per receipt; storage is bounded metadata, with no need to duplicate content.
- **security:** The receipt itself must redact secrets and distinguish observed, transmitted, and persisted data. Never include raw passwords or page bodies; require confirmation before sending a sensitive capsule to relay.
- **missing:** A single egress ledger joining browser command, Mac action, relay request, capsule, and announcement IDs; Relay hooks that report whether request content was persisted and its actual expiry/deletion behavior; A dashboard and spoken formatter for the receipt

### "“Know when I can be interrupted, not just what time it is: hold non-urgent results while I’m speaking or in a meeting, then give me one prioritized handoff when I’m free.”"
- **useful because:** A fixed quiet-hours rule cannot tell that the owner is currently talking, presenting, driving a browser workflow, or has just become available. The pendant’s local speech boundary signal, the Mac’s active calendar/session state, and the relay’s queued work can jointly avoid breaking concentration without losing results.
- **path:** pendant → mac-planner → browser-extension → relay → relay-realtime → faculty-perception → faculty-judgement
- **model tier:** Deterministic local VAD plus calendar/session signals for interruptibility; a cheap background model ranks the eventual handoff, with realtime reserved for the actual spoken delivery.
- **latency:** Local suppression decision under 100 ms; availability transition and handoff within 2 seconds.
- **cost:** <$0.01 per handoff; most decisions are local rules and event metadata, not model inference.
- **security:** Speech leaves the pendant only as quality/boundary metadata unless the owner is actively conversing. Calendar titles and browser state stay on the Mac; relay receives only urgency, queue IDs, and a coarse availability state. Emergency overrides require an explicit owner policy.
- **missing:** A cross-surface interruptibility state with lease/expiry and source confidence; A pendant-to-Mac local VAD event channel that works while the relay is unavailable; A scheduler/announcement policy that consumes that state instead of only clock-based quiet hours; An owner-configurable emergency and meeting override policy

### "“Forget everything from that task everywhere, and prove what was erased, what was only tombstoned, and what you could not reach.”"
- **useful because:** Today task data is split across relay announcements, Mac jobs/pipeline/action ledgers, browser spool/provenance, evidence capsules, and audio stores with incompatible retention and deletion behavior. The owner cannot make a dependable deletion request or distinguish actual erasure from expiry filtering.
- **path:** relay → mac-planner → browser-extension → relay-realtime → faculty-perception → faculty-action → dashboard
- **model tier:** Deterministic deletion planner and verifier; no realtime model needed except to clarify an ambiguous task reference.
- **latency:** Immediate acknowledgement under 500 ms; verification within 10 seconds, with explicit pending/unreachable states.
- **cost:** <$0.01 per deletion receipt; storage cost is bounded tombstone metadata.
- **security:** Require owner confirmation for broad deletion. Authenticate every target store, never claim deletion from a failed request, preserve only opaque receipt IDs and legally/operationally required tombstones, and clearly disclose third-party browser or relay retention beyond our control.
- **missing:** A task-wide deletion index linking job, pipeline, browser, evidence, audio, announcement, and action-ledger records; Authenticated delete/ redact routes for each store, including relay announcements and audio; A verifier that checks physical absence versus read-side expiry and returns an honest deletion receipt

### "“If I long-press the pendant, instantly make the whole system private: stop listening, cancel pending browser work, cut relay delivery, and show me that it happened.”"
- **useful because:** A physical privacy action is available even when the owner cannot reach the Mac or speak safely. It closes the gap between local microphone capture, queued relay announcements, browser commands, and Mac jobs instead of assuming one software surface is reachable.
- **path:** pendant → relay-realtime → relay → mac-planner → browser-extension → faculty-action → faculty-perception
- **model tier:** Firmware-local kill switch for the first response; deterministic authenticated fan-out and receipt aggregation afterward.
- **latency:** Pendant microphone mute and local LED confirmation under 100 ms; remote cancellation fan-out under 2 seconds when connected; queued cancellation on reconnect otherwise.
- **cost:** Negligible per invocation; a few kilobytes of bounded state and one authenticated control event.
- **security:** The gesture must be local and independent of the relay. Use a device-held key, monotonic nonce, and fail-closed semantics. Never erase evidence silently; distinguish mute, cancel, revoke, and delete, and require a separate deliberate gesture for destruction.
- **missing:** Firmware panic/privacy gesture and persistent local state; Relay fan-out endpoint that revokes active speech delivery and marks queued announcements blocked; Mac/browser listeners that cancel pending commands and stop new capture; A signed multi-surface receipt reporting which surfaces acknowledged and which remained unreachable


## What it asked for

_Nothing._
## Its own summary

Round 169 established live truth: GET /ops/snapshot reports Accessibility and Screen Recording now granted, all required automation permissions ready, relay reachable on D1, Mac bridge online, and Safari extension online with 0 pending commands on an X tab (9 tabs total). The local Mac agent still does not expose /v1/devices/status; the continuity tool remains unresolved by the runtime, so direct GET /ops/snapshot is the usable fallback. I recorded three new capabilities: pre-action page identity proof, an owner-facing real-time trust/confidence sentence, and a per-task data-egress/retention receipt. A fourth proposal (first-failing-layer diagnosis) was rejected as an existing backlog duplicate, so I did not rephrase it.

**Biggest unknown:** Whether an nRF9160 pendant is physically connected or producing telemetry remains unknown to the live Mac agent; relay-side registry must be queried through the remote relay rather than localhost, and the existing granted snapshot tool cannot currently resolve.

