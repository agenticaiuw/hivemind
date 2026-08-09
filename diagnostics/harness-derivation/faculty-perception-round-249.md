# Harness derivation — faculty-perception — round 249

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **current live surfaces and permissions** — Live discovery now shows nrf9160-pendant in the device table, but it is OFFLINE (last seen 2026-08-09T02:56:31.366Z); home-macbook-bridge is ONLINE. The Mac agent is fully ready: Accessibility and Screen Recording are granted, automation grants are present, browser extension online with Safari YouTube tab, and relay reachable with D1 store. The local Mac agent does not expose GET /v1/devices/status (404); that route is relay-only.
  - evidence: discover(devices) live table; read_continuity_snapshot(include relay,pipeline) invoked GET /ops/snapshot HTTP 200 showing permissions.ready=true, accessibility.trusted=true, screenRecording.granted=true, relay.reachable=true; probe_http GET /v1/devices/status returned Mac-agent 404.

## Capabilities it proposed

### ""Is the pendant genuinely usable right now, or is it only registered on paper? Run the shortest end-to-end readiness check and tell me exactly what passed, what failed, and the last timestamp for each link.""
- **useful because:** The current table can show a stale nrf9160-pendant row as offline, while the Mac bridge and relay are healthy. This gives the owner a trustworthy go/no-go answer instead of confusing registration with a wearable that can hear and respond.
- **path:** pendant → mac → relay → browser
- **model tier:** background for the routine check; realtime only if the owner asks during a conversation
- **latency:** 5-10 seconds for a normal check; up to 30 seconds for a USB audio loopback
- **cost:** Usually <$0.01: mostly local diagnostics and HTTP reads; a loopback may use one short TTS/STT transaction.
- **security:** USB serial access must be restricted to the known nRF9160 and ESP32 ports; do not upload raw microphone audio. Relay credentials remain server-side. Require confirmation before flashing firmware or changing pairing.
- **missing:** A production read-only serial health action (the granted mac_serial_exchange capability is not yet callable);; relay endpoint exposed to the Mac for authoritative device status;; a bounded end-to-end test command that emits a nonce and verifies it at the bridge, not merely socket bytes.

### ""Did that actually happen? Show me the evidence chain, not just 'completed': the Mac action receipt, browser result or capsule if relevant, relay acceptance, and whether the pendant reported playback or only went offline.""
- **useful because:** Today a completed job can mean only that the Mac acted, and relay delivered means only bytes were written to a socket. A cross-surface evidence chain would let the owner distinguish executed, accepted, received, and physically played without false certainty.
- **path:** mac → browser → relay → pendant
- **model tier:** background for assembling the chain; realtime only to summarize a just-finished action
- **latency:** Under 2 seconds from local ledgers; under 8 seconds if relay and browser records must be fetched
- **cost:** <$0.01 per query; no model call is needed unless records conflict or need a spoken explanation.
- **security:** Evidence should expose redacted identifiers and hashes, not page secrets or bearer tokens. Browser capsule bodies should be withheld when revoked/expired. Never upgrade socket delivery to playback without a device-originated event.
- **missing:** A mounted browser provenance route and a relay-to-Mac capsule/reporting bridge;; a common correlation ID propagated through Mac ledger, browser result, relay job, and pendant event;; the already-granted audio_delivery_ack_queue wired to a readable relay/Mac projection;; a relay-side reader for the defined played event.

### ""Before you schedule or describe anything relative to time, tell me if the system's stored preferences disagree with the Mac's actual clock or timezone, and quarantine machine-derived contradictions until I confirm them.""
- **useful because:** A pinned machine-origin preference currently says America/Chicago while the Mac is actually America/New_York, and it is injected into context with high confidence. This prevents wrong routine times and misleading phrases such as 'this morning' without making the system silently rewrite an owner fact.
- **path:** mac → relay → pendant → browser
- **model tier:** background on context refresh and before scheduled routines; realtime only when a time-sensitive request is being answered
- **latency:** Under 200 ms for a local preflight; under 2 seconds if relay and routine state need reconciliation
- **cost:** <$0.01 per check; deterministic comparison, no model required except to explain a conflict
- **security:** Treat stored facts as sensitive personal data. Show provenance (machine versus owner) and the conflicting values, but never mutate or delete the owner's memory without confirmation. A pendant has no authoritative timezone, so do not infer one from its zoneless clock.
- **missing:** A context-projection veto/quarantine hook before preferences enter the prompt;; a typed machine-fact health endpoint exposing source.origin, confidence, expiry, and last-used time;; routine creation and firing paths that consume the same timezone verdict;; a small relay notice state so a conflict found while the Mac sleeps is not silently lost.

### ""If the pendant drops mid-conversation, keep the conversation going through my Mac or iPhone, then return to the pendant when it reconnects without losing what I said or hearing the answer twice.""
- **useful because:** The owner should not experience a hard conversational failure merely because the wearable briefly loses radio or power. A relay session can preserve the turn while the Mac or mirrored iPhone becomes a temporary audio body, then reconcile the handoff when the pendant returns.
- **path:** pendant → relay → mac → iOS
- **model tier:** realtime for the active handoff and conversation; background only for post-handoff reconciliation
- **latency:** Detect failure within 1 second and begin alternate audio within 2 seconds; restoration to the pendant can be eventual
- **cost:** Usually one realtime session with no additional model call; <$0.02 beyond the active turn. iPhone/Mac audio transport dominates engineering cost, not inference.
- **security:** Only hand off to pre-authorized local outputs, never arbitrary nearby speakers. Mute the old route before opening the new one to prevent duplicate or private speech. Require confirmation before routing sensitive content to a room speaker. Persist only encrypted turn IDs and byte offsets, not raw audio.
- **missing:** A relay session migration protocol carrying turn sequence, capture offset, and playback offset;; Mac/iOS audio sink and microphone adapters that can be selected without restarting the model session;; pendant-originated reconnect and playback watermarks;; a privacy policy for choosing headphones versus speakers when the wearable is absent

### ""For anything consequential, require a deliberate confirmation that uses two different bodies—my pendant button plus a visible Mac/iPhone confirmation—and tell me exactly what will happen before either one commits it.""
- **useful because:** A voice transcript alone is easy to trigger accidentally, while a desktop approval alone may be made by the wrong context. Requiring independent wearable intent and an authenticated local-screen confirmation makes high-impact actions safe without making ordinary conversation cumbersome.
- **path:** pendant → mac → iOS → browser → relay
- **model tier:** realtime for presenting the pending action and collecting the owner's confirmation; background for expiry and audit reconciliation
- **latency:** 2-5 seconds for a normal approval; pending approvals expire after a configurable interval
- **cost:** <$0.01 per approval; deterministic policy and local UI, with no extra model call after the action is parsed
- **security:** The relay must bind both confirmations to one nonce, principal, and action digest; replayed button events and stale browser approvals must fail. Display redacted parameters when secrets are involved. Destructive actions require explicit confirmation and cannot be approved by a relay-only fallback.
- **missing:** A signed pendant confirmation event with a monotonic counter;; a Mac/iOS approval UI that displays a canonical action digest;; relay-side two-party nonce binding and expiry;; policy classification separating reversible, sensitive, and destructive operations


## Changes it proposed to its own stack

### `integration` — Add a perception-only 'truth ladder' record for each cross-surface operation: observed_at, source, correlation ID, and one of intent_queued, mac_executed, relay_accepted, socket_sent, device_received, playback_started, playback_finished, or unknown. Derive it from existing Mac receipts, relay job state, browser results, and the pendant's offline-reality-beacon / audio-delivery queue; never infer a higher rung from a lower one. Surface stale pendant registration as 'known but not recently reachable,' not simply offline.
- **owner gets:** When the owner asks whether something happened, the system can answer precisely—'the Mac saved it, but the pendant was unreachable'—instead of saying completed when nobody heard it. It also turns the newly visible stale nrf9160-pendant row into useful reality rather than an alarming false outage.
- effort: Medium: schema and derivation in the Mac/relay perception layer, correlation propagation in existing job and browser calls, and a small firmware event adapter. No new owner-facing UI is required initially.  ·  risk: A malformed or delayed event could leave the ladder at unknown; recovery is to retain raw lower-level evidence and recompute. Never delete contradictory observations. The 90-second registry threshold must not be used as proof of physical absence.
- cost: Negligible storage (bounded records, roughly 0.5-2 KB per operation) and <$0.01/query; no routine cloud model cost.  ·  latency: Adds tens of milliseconds for local derivation; remote relay reconciliation can be eventual.
- security: High benefit if identifiers are pseudonymized and content is redacted. Do not copy audio or page bodies into the ladder; store hashes, capsule IDs, and permission-scoped links.
- depends on: the accepted offline-reality-beacon and audio_delivery_ack_queue behavior; a callable bounded USB serial diagnostic for bench verification; mounting the existing browserProvenance routes; a relay reader for the existing pendant event route and playback stage

### `interaction` — Create a cross-surface 'commit capsule' around consequential actions: before execution, capture a compact redacted snapshot of relevant Mac, browser, iOS, and relay state plus the exact intended mutation; after execution, capture independent post-state observations. Store a compensating-action plan that can be replayed in reverse order, and refuse to claim atomic success when one surface commits while another does not.
- **owner gets:** The owner gets one understandable promise—either all requested surfaces changed, or the system tells them precisely where it stopped and offers a safe recovery—rather than discovering later that a calendar, browser, phone, and relay ended up disagreeing.
- effort: High: requires a shared transaction ID, pre/post observers on each surface, reversible operation contracts, and a coordinator that handles partial failure. It should begin with a small set of supported operations and expand.  ·  risk: Some actions cannot be undone (messages sent, purchases, external edits). Those must be marked non-compensable and require confirmation before commit. Recovery must never blindly replay an old action against changed state; compare hashes and ask the owner when preconditions differ.
- cost: Small bounded local storage per transaction (roughly 5-20 KB of redacted metadata); <$0.02 per complex transaction for reconciliation, with no need for realtime inference after planning.  ·  latency: Adds 0.5-2 seconds for preflight snapshots and post-state verification; external sites may make verification slower.
- security: Snapshots must redact secrets and page bodies, retain hashes and locators only where possible, and be encrypted locally. Cross-surface correlation IDs must not be exposed to untrusted browser content.
- depends on: a shared correlation and action-digest protocol across relay, Mac, browser, and iOS; read-only post-state observers for each surface; operation-specific compensating actions; the existing Mac action ledger, browser result records, job receipts, and undo routes


## What it asked for

_Nothing._
