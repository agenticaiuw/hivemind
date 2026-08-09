# Harness derivation — faculty-perception — round 135

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac perception state** — At 2026-08-08T01:09:49Z, /ops/status and /observe report AI Pendant Agent permissions.ready=true, Accessibility trusted, Screen Recording granted, inputReachability=verified, browser extension online with 9 Safari tabs and zero pending commands. Relay is reachable and mac bridge online. The granted read_continuity_snapshot tool itself currently fails resolver resolution; nearest live route is GET /ops/snapshot.
  - evidence: GET /ops/status HTTP 200; GET /observe HTTP 200; read_continuity_snapshot returned unresolved with nearest GET /ops/snapshot.

## Capabilities it proposed

### "“Before you tell me something is done, prove what is true right now and say exactly what you cannot know.”"
- **useful because:** The system currently exposes many completion-looking states that are not owner-heard or externally verified. This would turn perception into an honest, usable contract: every consequential answer carries an observed-at time, source surface, freshness, and explicit unknowns instead of silently treating relay acceptance or Mac completion as reality.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → unified → faculty-perception → faculty-judgement
- **model tier:** Cheap background summarizer for routine snapshots; realtime only when the owner asks a live truth question.
- **latency:** Under 1.5 s for a normal status claim; up to 4 s when browser and relay reads are both required.
- **cost:** Usually <$0.01 per query; network reads dominate latency, not model tokens.
- **security:** Do not include page bodies or secrets in the spoken claim. Browser evidence must be redacted and content-addressed; stale or missing surfaces must be reported as unknown, never inferred.
- **missing:** A callable resolver for the already-granted continuity snapshot (the current grant fails and only /ops/snapshot is reachable); A shared claim envelope with observedAt, source, freshness, confidence, and unknowns; A device-originated playback event remains missing, so heard/heard-not must stay unknown

### "“I plugged the pendant into my Mac—bring it up, test the microphone and speaker locally, and tell me whether it is actually ready before trying the relay.”"
- **useful because:** The nRF9160 and ESP32 are physically USB-attached but the relay has no pendant registration. A guided local bring-up would make the hardware useful today: identify both serial devices, run a no-network audio loopback and codec health test, capture firmware/boot identity, then separately attempt pairing and report which boundary failed.
- **path:** mac-terminal → mac-planner → relay-realtime → faculty-perception → faculty-action
- **model tier:** Background/cheap model for deterministic diagnostics and report assembly; realtime only for the spoken go/no-go interaction.
- **latency:** Local enumeration and loopback verdict under 20 s; relay registration attempt under 10 s after explicit owner confirmation.
- **cost:** Negligible API cost; roughly 30–60 s of Mac CPU/USB activity. No cloud inference needed for the measurements.
- **security:** Never upload raw microphone audio or firmware secrets. Pairing/admin credentials must remain in local keychain/config; relay registration requires explicit confirmation. Flashing firmware must be a separate, high-friction action.
- **missing:** A Mac allowlisted serial diagnostic/loopback action for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A stable local readiness schema joining both chip identities, audio metrics, and relay registration state; A safe pairing flow using a scoped pendant credential rather than the shipping admin WebSocket key

### "“Check the public page against the signed-in page, explain any difference, and only act if the evidence still matches.”"
- **useful because:** The relay can read public pages while the browser extension can see authenticated sessions, but today those readings do not share a durable identity or hash. A discrepancy-aware comparison would catch login walls, personalized prices, stale tabs, and changed terms before the Mac changes anything.
- **path:** relay-realtime → browser-extension → mac-vision → mac-planner → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Cheap background model for extraction and diff; realtime only for the owner's interactive decision.
- **latency:** 3–6 s for two page reads and a structured diff; action starts only after an explicit confirmation when differences affect money, privacy, or commitments.
- **cost:** <$0.03 per comparison, dominated by browser rendering and authenticated tab capture; no need for the expensive realtime tier.
- **security:** Authenticated content stays on the Mac; relay receives only redacted fields needed for comparison. Never treat a public-page hash as proof of an authenticated page. Require confirmation for purchases, submissions, deletion, or policy acceptance.
- **missing:** Relay read_web_page must return a stable request/capsule identifier and content hash; A Mac bridge call that mints the existing evidence capsule and browser-provenance record for relay-originated reads; A structured field extractor with source-specific sensitivity labels and a freshness cutoff

### "“While I’m away, watch the signed-in pages and Mac apps I authorize; when something materially changes, tell me only the change, show the before/after evidence, and tell me whether I need to act.”"
- **useful because:** Today the system can read a page or execute a task, but it cannot reliably distinguish a meaningful state transition from a repeated observation across authenticated browser sessions and local apps. The owner would get a quiet, actionable radar for changed bills, appointments, delivery dates, account notices, or documents instead of duplicate briefings and stale summaries.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Background model for periodic extraction and semantic diff; realtime only when the owner asks for the current change ledger or speaks an approval.
- **latency:** Polling can be hourly or event-driven; a newly detected change should reach the owner within 30 seconds when online.
- **cost:** <$0.05 per monitored source per day with change-triggered summarization; browser/app reads and storage dominate.
- **security:** Monitoring is opt-in per site/app and field. Keep authenticated bodies on the Mac, redact secrets before relay transfer, encrypt the before/after hashes and excerpts, and require confirmation for any resulting action.
- **missing:** A durable per-source snapshot/diff store with owner-attention watermarks, not just page-read receipts; Browser extension events for DOM/network changes and Mac app adapters for Calendar, Mail, Reminders, and Files; A cross-surface scheduler and deduplication policy that can distinguish changed, acknowledged, and merely re-read

### "“For every consequential action you took, let me replay the exact evidence, decision, permission, and result—and show me the point where reality diverged if it failed.”"
- **useful because:** Current receipts can describe an action, but they do not give the owner a human-readable causal replay spanning browser evidence, Mac postconditions, relay state, and (when present) physical playback. A replayable chain would make the system auditable after the fact without requiring the owner to trust its success labels.
- **path:** faculty-perception → faculty-judgement → faculty-action → mac-planner → mac-vision → browser-extension → relay-realtime → unified
- **model tier:** Cheap background indexing and summarization; use realtime only for an interactive replay question.
- **latency:** Receipt creation adds under 200 ms; replay should open in under 2 seconds.
- **cost:** <$0.01 per action plus bounded local storage; hashing and indexing dominate, not model inference.
- **security:** Evidence must be redacted and access-controlled by owner session. Never retain raw passwords, payment data, or full page bodies solely for replay. Tamper-evident hashes should reveal alteration without exposing content.
- **missing:** A single append-only cross-surface event graph linking evidence capsule, decision, approval, action, postcondition, and delivery/playback states; Stable IDs emitted by relay browser reads and device playback events; A dashboard/voice query that explains missing links as unknown rather than manufacturing a success


## Changes it proposed to its own stack

### `integration` — Make the read_continuity_snapshot grant resolve deterministically to the live GET /ops/snapshot route (with the existing include/maxItems filtering applied server-side), and add a contract test that rejects nearest-match resolution when the requested tool name is granted.
- **owner gets:** The owner can ask one question about what happened while away and receive a real cross-surface answer instead of a tool-resolution error or a model guessing from separate endpoints.
- effort: Small: resolver alias plus one bounded response adapter and tests.  ·  risk: A route schema drift could break the adapter; recover by returning a typed stale/unavailable result rather than falling back to inference.
- cost: Negligible.  ·  latency: One request instead of multiple model-driven probes; likely lower latency.
- security: No new authority; preserve the existing bearer-authenticated read-only scope.
- depends on: GET /ops/snapshot

### `relay` — Add a relay-issued, signed observation receipt for every browser read and routine composition: receiptId, observedAt, source URL, redacted content hash, truncation flag, and expiry; transmit only the receipt and redacted fields to the Mac provenance bridge, never raw authenticated content.
- **owner gets:** When the system quotes a page or schedules an announcement, the owner can tell which page version it saw and whether the evidence was stale or truncated, instead of trusting an untraceable sentence retained indefinitely.
- effort: Medium: relay signing/key rotation, Mac bridge ingestion, and routine receipt links.  ·  risk: Key loss or clock skew could make receipts unverifiable; retain a key-id and classify unverifiable receipts as unknown, never valid.
- cost: Small cryptographic CPU/storage overhead; <$0.01 per read.  ·  latency: Tens of milliseconds for hashing/signing.
- security: Improves integrity but creates durable metadata about visited URLs; redact query strings and enforce the existing capsule TTL.
- depends on: relay browser-read provenance; Mac evidence capsule store; browserProvenance route mounting

### `interaction` — Add a physical “context handoff” protocol: when the owner leaves the Mac, the pendant can announce a compact, prioritized handoff of unresolved decisions and changed facts; on return, a spoken check-in asks only about items whose evidence changed or whose deadline is near, with a local monotonic sequence preventing repeats.
- **owner gets:** The owner would stop hearing the same stale reminders after reconnecting and would not lose the one decision that changed while they were away. The handoff is useful even when the relay is unavailable because the pendant can carry the compact index locally, while the Mac supplies the authoritative detail when reachable.
- effort: Large: firmware ring-buffer integration, relay/Mac handoff protocol, event ordering, and an owner-facing prioritization policy.  ·  risk: A false priority or clock mismatch could hide something important. Recovery is a visible “unverified handoff” state and a manual full review command; never delete source records when compacting the handoff.
- cost: Low ongoing API cost; a few KB of nonvolatile pendant state and modest firmware work. Do not write routine data to the SD failure buffer.  ·  latency: Immediate local prompt on reconnect; detail hydration takes 1–3 seconds when Mac/relay are online.
- security: The pendant stores only opaque IDs, priorities, and monotonic sequence numbers; sensitive details remain on the Mac/relay and require authenticated hydration.
- depends on: offline-reality-beacon; offline-capture-integrity-sentinel; audio_delivery_ack_queue; a durable cross-surface event graph; owner-defined interruption priorities


## What it asked for

_Nothing._
## Its own summary

Established fresh truth: the Mac agent is fully ready now (permissions.ready=true, Accessibility and Screen Recording granted, inputReachability verified), Safari bridge is online with 9 tabs and zero pending commands, and the relay/mac bridge are reachable. The newly granted continuity tool is not actually callable: its resolver fails and only identifies GET /ops/snapshot as a near match. I recorded that fact and proposed a deterministic resolver, a truth-bound owner answer envelope, a USB pendant bring-up workflow, and signed relay browser observation receipts. The owner-facing highest-value capability is an answer that proves each consequential claim with source/time/freshness and names what remains unknown.

**Biggest unknown:** There is still no live, device-originated proof that an nRF9160 pendant is registered, received bytes, or played audio. The Mac agent cannot reach the relay's /v1/devices/status route directly, and continuity history remains unavailable through the broken tool binding; until those gaps are fixed, 'completed' must not be described as 'heard'.

