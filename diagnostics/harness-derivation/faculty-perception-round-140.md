# Harness derivation — faculty-perception — round 140

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-permissions** — At 2026-08-08T01:33Z, the Mac agent reports Accessibility and Screen Recording granted, all required automation permissions granted, permissions.ready=true; browser bridge online with 9 Safari tabs and zero pending commands.
  - evidence: GET /ops/snapshot HTTP 200, payload.status.permissions and payload.browser
- **live-device-registry** — At 2026-08-08T01:32:57Z, the live device discovery contains only home-macbook-bridge online and cloudflare-contract-test offline; no nRF9160 pendant is registered.
  - evidence: discover(devices), fresh at round 140
- **pipeline-contradiction** — The current pipeline history contains an old nrf9160 event claiming 'Held alerts surfaced' (2 alerts, microSD) and a relay_result saying response accepted for the nRF9160, but those runs are historical (2026-08-07) and the current device registry has no pendant; the pipeline status is therefore not proof of present pendant delivery.
  - evidence: GET /pipeline HTTP 200 plus discover(devices) round 140
- **continuity-tool-unresolved** — The granted read_continuity_snapshot tool does not resolve against the live capability inventory; resolver selected no capability (best GET /ops/snapshot score 0.447), so a single cross-surface continuity read is currently unavailable despite appearing granted.
  - evidence: read_continuity_snapshot call error round 140

## Capabilities it proposed

### "Before you tell me something arrived, finished, or was heard, tell me whether the evidence is internally consistent — and point out exactly what conflicts."
- **useful because:** Today a historical pipeline row can say the nRF9160 surfaced alerts or accepted audio while the live registry has no pendant. This would stop the system from presenting stale, impossible, or Mac-authored completion as present reality, which is the most important trust function this mind can provide.
- **path:** relay-realtime → mac-planner → browser-extension → unified → faculty-perception
- **model tier:** background cheap verifier (small model or deterministic rules); escalate only the contradiction explanation to realtime when speaking
- **latency:** Under 300 ms for deterministic checks on every status answer; under 1.5 s for a short natural-language explanation
- **cost:** <$0.001 per check when rule-based; <$0.01 only when a language explanation is needed. Dominant cost is explanation, not reads.
- **security:** Reads only authenticated operational metadata; never expose page bodies, credentials, or tab content. Treat device-reported, Mac-authored, relay-accepted, and inferred states as separate provenance classes. Require confirmation before any action based on a contradicted claim.
- **missing:** A live resolver for the already-granted read_continuity_snapshot (currently unresolved) or an equivalent single authenticated read; A typed event provenance field distinguishing device-observed from Mac-authored and historical records; A contradiction policy that marks a claim unknown rather than silently choosing a winner

### "If an answer or automation would send browser content off the Mac, warn me with the exact tab, domain, sensitivity, and destination before it leaves — and tell me when nothing was sent."
- **useful because:** The browser currently holds authenticated sessions (including an OpenAI billing tab). A cloud relay read and a Mac-side browser read have radically different exposure, but today the owner cannot ask which one happened. A wearable prompt needs a crisp privacy boundary, not a vague 'untrusted' label.
- **path:** browser-extension → mac-planner → relay-realtime → unified → faculty-perception → faculty-judgement
- **model tier:** Deterministic domain/session classifier first; cheap background model only for ambiguous page sensitivity; realtime speaks only the final warning.
- **latency:** 150 ms for known domains and tab metadata; under 1 s for ambiguous classification; block or ask before transfer, never after.
- **cost:** Near-zero for URL/title and policy checks; <$0.005 for an ambiguous classification. Network/API cost is dominated by any cloud read that must be withheld or retried.
- **security:** Default-deny for passwords, billing, health, messages, private documents, and pages with login walls. Do not transmit page text to classify it; use URL/title/extension metadata locally. The warning itself must not quote sensitive content. Owner confirmation required for every cross-boundary transfer unless an explicit per-domain policy exists.
- **missing:** A preflight interception hook before read_web_page, browser research, and relay routine composition; A local sensitivity classifier and owner policy store; A durable receipt stating destination, tab pseudonym, content hash/length, and whether bytes crossed the boundary

### "How much of the last day can you actually account for? Give me a coverage certificate with the oldest surviving record, every blind interval, clock uncertainty, and the reason each gap cannot be reconstructed."
- **useful because:** The system currently mixes count-capped Mac history, 24-hour relay jobs, unpruned announcements, and a non-existent pendant stream. The owner needs to know whether 'nothing happened' means nothing happened or evidence was overwritten; this turns absence into a measured boundary instead of a guess.
- **path:** faculty-perception → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Deterministic aggregation and interval arithmetic; use a cheap background model only to phrase the final certificate.
- **latency:** Under 500 ms from local stores and relay metadata; no network retry longer than 2 s, with the certificate marking that source unknown.
- **cost:** <$0.002 per request with deterministic computation; relay read dominates latency, not tokens.
- **security:** Expose metadata and retention boundaries, not page bodies, audio, or secrets. Preserve source-local timestamps and explicit timezone/clock-skew assumptions. Never report an empty interval as quiet unless all relevant sources are live and retained across it.
- **missing:** One authenticated endpoint that reports source freshness, retention policy, oldest available record, and offline high-water marks together; A durable monotonic clock/sequence from the pendant when it exists; A schema for explicit unknown intervals and source failure reasons

### "When the pendant is plugged into my Mac by USB, run a one-minute 'bench truth' session: prove which firmware is connected, send a test utterance, receive a test reply, and show exactly which stages were observed versus merely accepted. Do not count this as me wearing the device."
- **useful because:** The owner has firmware and bridge hardware that can be exercised before LTE registration, but today there is no honest way to distinguish a real end-to-end device test from historical nRF9160 rows. A tagged bench session would make hardware progress measurable without contaminating live presence or delivery claims.
- **path:** mac-terminal → mac-planner → relay-realtime → unified → faculty-perception → faculty-action
- **model tier:** Deterministic serial protocol and test assertions; use realtime only to narrate the final pass/fail result.
- **latency:** One minute for the complete test, with a visible heartbeat every 5 seconds; never block normal Mac work.
- **cost:** No model cost for the test; negligible relay traffic. Dominant cost is implementation of a USB serial adapter and a disposable relay test namespace.
- **security:** Bench mode must use a test device identity and test audio, never the owner's live announcement queue or production history. Require physical USB presence and an explicit start command; redact captured audio from receipts.
- **missing:** USB serial health/read and write adapter for the nRF9160 and ESP32 paths; A relay test namespace that cannot mark production jobs delivered; Firmware test frames for receive/playback and a bench-only device identity; A receipt schema separating observed hardware stages from relay acknowledgements

### "For any fact you tell me from a browser page, file, or relay result, give me a compact verification card I can ask for later: source, observation time, content hash, exact surface that saw it, and whether it was asserted, extracted, or independently confirmed."
- **useful because:** Today relay browser text can be spoken or stored without an ID or hash, while Mac evidence capsules exist only on some paths. The owner cannot later ask 'which page did that come from, and did it change?' This makes spoken knowledge auditable without replaying private page content.
- **path:** browser-extension → mac-planner → relay-realtime → unified → faculty-perception
- **model tier:** No model for card creation: hash and provenance are deterministic; a cheap model may summarize only when the owner asks for an explanation.
- **latency:** Under 100 ms added to a local read; under 300 ms for relay metadata. Never wait on a second page fetch just to issue a card.
- **cost:** Negligible compute and token cost; bounded local storage is the main cost.
- **security:** Hash redacted content, never persist raw secrets in the card, pseudonymize tab/session identity, and honor capsule revocation and expiry. A hash proves continuity, not truth; label source authenticity and extraction confidence separately.
- **missing:** A relay response contract carrying a stable read ID and content hash; A transport from relay reads into the existing Mac evidence-capsule store; Mounting of the existing browser provenance routes; A user-facing lookup and revocation view

### "Tell me immediately when the pendant, audio bridge, Mac agent, browser, or relay stops being reachable, and say which link failed, when it last produced a real signal, and whether the owner-facing conversation is still safe to use."
- **useful because:** 'Relay reachable' and 'pendant online' are currently conflated, while a USB-attached board, ESP32 audio bridge, Mac process, browser session, and cloud relay fail independently. The owner needs a local alarm that does not falsely claim a wearable is alive just because the Mac bridge is healthy.
- **path:** mac-terminal → mac-planner → relay-realtime → browser-extension → unified → faculty-perception
- **model tier:** Firmware counters and deterministic heartbeat monitor; no LLM unless the owner asks for a diagnosis.
- **latency:** Detect USB or bridge loss within 2 seconds; relay/browser freshness within their heartbeat interval; speak a concise warning within 1 second after detection.
- **cost:** Near-zero model/API cost; modest local polling and one bounded event record per transition.
- **security:** Do not upload raw audio or serial payloads. Authenticate device identity, distinguish physical USB presence from LTE registration, rate-limit spoken alarms, and require confirmation before switching to an alternate output path.
- **missing:** Read-only USB serial health for both connected boards; A signed per-surface heartbeat with monotonic sequence and last-good timestamp; A local state machine that distinguishes absent, stale, degraded, and healthy; A notification path that survives relay loss (Mac audio or local UI)


## Changes it proposed to its own stack

### `context` — Make every operational event carry an immutable observedAt, sourceClock, provenance (device|mac|relay|inferred), and freshness class; have /pipeline and /jobs derive labels such as historical, stale, relay-accepted, device-received, and device-played instead of one overloaded completed/processing status. A status from a prior day must never appear as current merely because it remains in the capped store.
- **owner gets:** When they ask 'did it happen?', the answer will distinguish 'the Mac generated it yesterday' from 'the pendant reported hearing it now'. The current pipeline already demonstrates the danger: an old nRF9160 alert and relay acceptance remain visible while no pendant is registered.
- effort: Medium: event schema migration plus derived-status changes in local-agent/pipelineTrace and relay job presentation; no new audio protocol required for the first phase.  ·  risk: Older records lack provenance and may be relabeled unknown rather than falsely upgraded; consumers expecting completed may need compatibility mapping. Recovery is a read-only migration with a feature flag and rollback to existing labels.
- cost: Negligible API cost; a few bytes per event and one bounded migration.  ·  latency: Sub-millisecond derivation locally; no extra model call.
- security: Improves provenance separation; do not include raw page/audio content. Device-originated fields must be authenticated and cannot be supplied by the Mac bridge.
- depends on: A single live continuity snapshot or equivalent source reads; Defined device-originated event authentication; An explicit played/received event if owner-heard status is to exist


## What it asked for

_Nothing._
## Its own summary

Fresh perception pass established: Accessibility and Screen Recording are now granted and the Mac/browser surfaces are live (Safari bridge: 9 tabs, 0 pending commands); only the Mac bridge is online in the device registry, with no nRF9160 pendant. The pipeline contains historical nRF9160 and relay-accepted records that cannot establish current delivery. I recorded these facts and proposed four new items: an internal-consistency verifier (the single most useful), a browser cross-boundary privacy preflight, a measured coverage certificate for blind intervals, and provenance/freshness labels that prevent stale 'completed' states from masquerading as live truth.

**Biggest unknown:** The granted read_continuity_snapshot tool still cannot resolve against the live inventory (best matches were /ops/snapshot and /pipeline), so I could not obtain one atomic cross-surface read. I still need that resolver wiring or an equivalent endpoint exposing freshness, retention, offline high-water marks, pending work, and provenance in one authenticated response. I also need confirmation of whether /v1/devices/status and /catchup are reachable from this agent rather than merely described in prior context.

