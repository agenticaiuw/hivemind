# Harness derivation — faculty-perception — round 221

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac and fleet state** — At 2026-08-09T00:36Z the Mac agent is healthy and ready: Accessibility, Screen Recording, and required automation permissions are granted; browser extension online in Safari with 3 tabs and one pending command; relay reachable with D1 store and Mac bridge online. Device discovery shows only home-macbook-bridge online and cloudflare-contract-test offline; no pendant is registered.
  - evidence: GET /ops/status HTTP 200 and GET /machine-context HTTP 200; discover(devices) returned Safari on MacIntel, home-macbook-bridge online, cloudflare-contract-test offline.

## Capabilities it proposed

### ""Is the system's picture of the world internally consistent right now?" Give me contradictions such as a stale timezone, a device claimed online by one surface but absent from the registry, or a browser action with no matching receipt, with source, age, and confidence for every side."
- **useful because:** Today each surface can be locally truthful while the unified mind is wrong. This turns perception into an active contradiction detector instead of silently selecting whichever stale fact appears first. It would have caught the pinned machine-originated America/Chicago preference against the Mac's authoritative America/New_York, and would prevent treating the online Mac bridge as evidence that a pendant exists.
- **path:** mac-planner → relay-realtime → browser-extension → faculty-perception
- **model tier:** background/cheap model for periodic comparison; realtime only when the owner asks a question about the current state
- **latency:** 5-15 seconds for an on-demand scan; under 1 second to answer from a cached scan less than 60 seconds old
- **cost:** Usually under $0.01 per scan; dominated by one compact synthesis call after local/relay reads, not by model generation
- **security:** Read-only evidence only. Do not copy page contents or secrets into the contradiction record; retain identifiers, hashes, timestamps, and redacted field paths. A contradiction must never trigger an action or rewrite a fact without owner confirmation.
- **missing:** A normalized observation envelope with source, observedAt, expiresAt, and confidence across /ops/status, /machine-context, /pipeline, relay device status, browser receipts, and memory facts; A comparator that understands authority (for example /etc/localtime outranks a machine-written preference) and distinguishes absence from unobserved; A bounded, authenticated cross-surface report route

### ""Why did you think that was true when you acted?" Show me a time-ordered evidence replay for one claim or action: what the relay, Mac, browser, and (when present) pendant each reported at the decision time, what was missing, and which later observation proved or contradicted it."
- **useful because:** A present-day status page cannot explain a past mistake: it only shows the world after it changed. This gives the owner an honest postmortem and lets judgement distinguish a bad decision from a good decision made on stale or incomplete evidence. It is especially valuable for claims like 'the page was read', 'the reminder was created', or 'the pendant heard it'.
- **path:** faculty-perception → relay-realtime → mac-planner → browser-extension → faculty-judgement
- **model tier:** background/cheap model assembles the timeline; use the expensive realtime tier only to answer a live follow-up
- **latency:** 2-5 seconds for a bounded replay of one job/claim; never scan unbounded history
- **cost:** Under $0.02 per replay when the event join is precomputed; storage/indexing dominates, not inference
- **security:** Evidence may contain URLs, page claims, or private automation fields. Store redacted excerpts plus hashes and source links, enforce per-owner authorization, and clearly label reconstructed timelines where a source was not recorded. Never infer a missing event as success.
- **missing:** Immutable observation envelopes emitted at decision boundaries (not just current snapshots) with monotonic sequence, wall-clock estimate, source, and correlation ID; A cross-surface correlation key carried through relay jobs, Mac action ledger steps, browser command/result, pipeline run, and future pendant telemetry; A bounded replay endpoint that returns raw evidence and explicitly separates observed, inferred, and unknown

### ""Before you act, give me a fresh witness certificate; after you act, prove the state changed." For any consequential request, require independent witnesses for the target and authorization, then perform a bounded postcondition check across the relevant surface and return pass, fail, or unknown—not a guessed success."
- **useful because:** The system currently lets one stale snapshot or a Mac-side completion stand in for reality. A fail-closed witness certificate would prevent costly false positives: a browser command is not complete until its result matches the intended state, a relay job is not heard until the device reports playback, and a Mac action is not success merely because a process returned. This is the strongest single trust feature the owner could get.
- **path:** faculty-perception → faculty-judgement → faculty-action → mac-planner → browser-extension → relay-realtime
- **model tier:** Cheap deterministic rules and hashes for witnesses/postconditions; background model only resolves natural-language expected state; realtime is reserved for explaining an unknown or requesting confirmation
- **latency:** 1-3 seconds for local/browser checks, up to 10 seconds when relay/device evidence is needed; consequential actions should wait rather than guess
- **cost:** Usually pennies or less; most work is existing authenticated reads and deterministic comparison, with model cost only for ambiguous postconditions
- **security:** A certificate must bind target, authorization scope, freshness, precondition hashes, action/job ID, and postcondition evidence; expire quickly and be single-use. Do not expose private browser values in certificates. Unknown must be a terminal outcome unless the owner confirms a retry.
- **missing:** A shared certificate schema and correlation ID accepted by judgement/action, with freshness and authority rules; Postcondition adapters for browser DOM/state, macOS app state, relay job state, and the future pendant playback event; A policy defining which actions require two independent witnesses and which may use one trusted local witness

### ""What happened in the right order while you were disconnected?" Reconstruct a tamper-evident event sequence spanning pendant-offline speech, relay conversations, Mac actions, and browser changes, using sequence continuity and later time anchors; show relative order when wall-clock time is unknowable instead of inventing timestamps."
- **useful because:** The system currently cannot honestly order an offline pendant utterance against Mac or relay events: the pendant clock is zoneless, and later stores retain disconnected records with incompatible timestamps. The owner needs to know whether an action followed a request, preceded it, or merely happened nearby—not receive a falsely precise timeline.
- **path:** faculty-perception → relay-realtime → mac-planner → browser-extension → faculty-judgement → faculty-action
- **model tier:** Deterministic sequence/clock reconciliation first; a cheap background model summarizes the resulting partial order. Realtime is only for explaining an ambiguity during a live conversation.
- **latency:** Under 2 seconds for an existing event window; under 10 seconds to reconcile a newly reconnected pendant batch.
- **cost:** Under $0.01 per reconciliation; storage and device firmware changes dominate, not inference.
- **security:** Use signed, monotonic sequence chains and explicit uncertainty intervals; never claim a wall-clock instant without an anchor. Encrypt offline utterance metadata, omit audio by default, and let the owner revoke a segment. A broken chain must be reported, not repaired silently.
- **missing:** A pendant-side append-only sequence chain with boot/session IDs, monotonic counters, and hash links for utterance boundaries and local events; A reconnect handshake that anchors the pendant monotonic timeline to relay and Mac clocks while preserving clock uncertainty and detecting rollback/replay; A partial-order event model and owner-facing renderer that distinguishes observed order, inferred order, and incomparable events

### ""How many independent witnesses actually know this—not how many copies repeat it?" For any important claim, show the evidence-dependency graph, collapse mirrored reports from the same source, and tell me whether confidence comes from one origin or genuinely independent observations."
- **useful because:** The hive can currently mistake relay state copied from the Mac, a browser receipt copied into a job, and a dashboard projection for three confirmations. The owner needs confidence that reflects independent physical observation, especially before trusting device presence, browser state, or completion.
- **path:** faculty-perception → faculty-judgement → relay-realtime → mac-planner → browser-extension
- **model tier:** Deterministic provenance graph and source-equivalence rules; cheap background model explains the graph in plain language.
- **latency:** Under 2 seconds for a bounded claim; recompute only when a source observation changes.
- **cost:** Negligible model cost after provenance edges exist; the main cost is emitting and retaining compact source lineage.
- **security:** Expose source classes and hashes, not private payloads. Do not let an untrusted browser page declare itself an independent witness. Preserve source lineage across relay forwarding and expire confidence when the originating observation expires.
- **missing:** Lineage metadata propagated through relay jobs, Mac ledgers, browser commands/results, pipeline events, and future pendant telemetry; A source-equivalence registry distinguishing direct device observation, Mac inference, relay forwarding, and UI projection; A confidence API that returns independent-witness count, dependency edges, freshness, and unknowns

### ""Can I trust the device that reported this?" Verify the identity and software provenance of the pendant, Mac bridge, relay, and browser extension for each evidence-bearing answer, flag unexpected firmware/build or extension changes, and quarantine observations from an untrusted component."
- **useful because:** A perfect event ledger is still misleading if an old firmware, replaced extension, or impersonating device can emit it. The owner should know whether a claim came from the expected binary and session before relying on it for private data or real-world action.
- **path:** faculty-perception → relay-realtime → mac-planner → browser-extension → faculty-judgement
- **model tier:** Deterministic signature and attestation checks; background model summarizes risks. Never use the expensive realtime model to decide cryptographic trust.
- **latency:** Under 500 ms when manifests are cached; under 5 seconds after a component reconnects or rotates identity.
- **cost:** Less than $0.01 per check; cryptographic verification and manifest storage dominate.
- **security:** Use device-bound keys, signed build manifests, nonce-based handshakes, and key rotation/revocation. Do not upload raw firmware or private keys. Fail closed for action authorization but retain a clearly marked diagnostic record for recovery.
- **missing:** Per-component signing keys and a trust registry for pendant firmware, Mac agent binary, relay deployment, and browser extension; Nonce-based attestation endpoints and a signed build/version manifest carried into every observation envelope; A quarantine and recovery policy that lets the owner re-pair or revoke a component without deleting unrelated history


## What it asked for

_Nothing._
## Its own summary

Fresh discovery: the Mac agent is now fully permission-ready (Accessibility, Screen Recording, and automation all granted), Safari/browser bridge is online with 3 tabs and 1 pending command, relay is reachable on D1, and the only registered hardware remains the online Mac bridge—no pendant. I recorded that verified state. I proposed three new owner-facing capabilities: (1) an authority-aware contradiction detector across Mac, relay, browser, pipeline, and memory; (2) evidence replay explaining what each surface knew at a past decision; and (3) a fail-closed, multi-witness precondition/postcondition certificate for consequential actions. The third is the most useful: it makes unknown a real outcome instead of calling Mac-side completion success.

**Biggest unknown:** The pendant remains entirely unobserved: no registration, heartbeat, or playback evidence exists. To complete the hive's perception loop, the remaining need is a real pendant connection plus a device-originated, correlated playback event; separately, the proposed cross-surface certificates need one shared correlation ID and adapters between existing ledgers rather than more isolated status endpoints.

