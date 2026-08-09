# Harness derivation — faculty-perception — round 164

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **macOS control permissions** — Live Mac agent reports Accessibility trusted, Screen Recording granted, all required automation grants present, permissions.ready=true, and computer-use loop enabled with vision model configured (vision upload consent false).
  - evidence: GET /ops/status and GET /ops/snapshot at 2026-08-08T02:53Z returned permissions.requiredMissing=[], ready:true; computerUse.loopEnabled:true, visionModelConfigured:true.

## Capabilities it proposed

### "“Did you actually do that?” — verify the last computer task instead of merely telling me it completed."
- **useful because:** Today a Mac job can be marked complete even when the browser or visible application did not change. This gives the owner a trustworthy answer with before/after evidence, or an explicit unknown, rather than confident fiction.
- **path:** mac-planner → mac-vision → browser-extension → relay-realtime → faculty-perception
- **model tier:** Use the cheap local planner for the action and a small vision model for before/after comparison; reserve realtime for the spoken verdict only.
- **latency:** 3–8 seconds after the action: one receipt read plus one targeted screenshot/browser inspection; do not continuously watch the screen.
- **cost:** About $0.01–$0.05 per verification, dominated by one vision comparison; browser-only checks are near-zero model cost.
- **security:** Screenshots may contain private data and must remain local; redact passwords and payment fields before any model call. Require confirmation before retrying or undoing a failed action. Report 'not verifiable' when the target app is occluded.
- **missing:** A standard verification contract mapping each action to an observable postcondition; Before-state capture attached to the action ledger; A local redaction-and-diff worker that emits evidence confidence without uploading raw screenshots

### "“I’m leaving my Mac — is anything risky or unfinished?”"
- **useful because:** The owner gets a single honest departure check: active browser sessions, unsaved or half-completed work, pending Mac jobs, relay delivery uncertainty, and permission or device anomalies. It prevents leaving a browser logged in or assuming a spoken task finished.
- **path:** faculty-perception → mac-planner → browser-extension → relay-realtime
- **model tier:** Cheap deterministic collectors first; a small text model ranks and explains only the findings. Realtime speaks the short verdict when requested.
- **latency:** Under 2 seconds from cached state; up to 6 seconds if a fresh browser inspection and job/relay reads are required.
- **cost:** Under $0.01 per check when deterministic; roughly $0.02 if a model must summarize ambiguous findings.
- **security:** Never read page bodies by default. Return host/title and risk class, not sensitive tab text. Treat a logged-in tab as a warning, not an instruction to sign out; signing out or closing tabs always requires confirmation.
- **missing:** A read-only departure snapshot route with one common schema and freshness timestamps; An explicit policy for what counts as risky (logged-in tabs, pending destructive actions, stale relay delivery, unsaved editor state); A spoken output that distinguishes observed facts from inferred risk

### "“When the pendant comes back, bring me up to date on everything I said offline, and ask before acting on anything stale.”"
- **useful because:** An offline wearable should not lose the owner's words or silently execute an old intent after reconnecting. The owner receives a compact transcript/quality summary, sees which requests are still actionable, and can approve, discard, or amend each one.
- **path:** pendant → relay-realtime → mac-planner → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Firmware stores only bounded audio/quality metadata; relay performs cheap transcription and deduplication; use the expensive model only for ambiguous intent extraction and conflict explanation.
- **latency:** Reconnect health frame immediately; first digest within 5 seconds; each approval response under 1 second after the owner chooses.
- **cost:** About $0.01–$0.08 per reconnect depending on stored speech minutes; transcription dominates, while metadata-only reconnects cost almost nothing.
- **security:** Offline recordings are sensitive and must be encrypted at rest and uploaded only after authenticated pairing. Never replay or execute an offline intent solely because it was transcribed. Show capture time as monotonic/unknown when the pendant has no trusted timezone; expire intents after a configurable age.
- **missing:** A pendant-originated offline utterance envelope with monotonic sequence, capture-integrity verdict, and authenticated upload; Relay idempotency and conflict resolution for reconnect batches; A Mac/relay review queue that links each proposed intent to its source audio and lets the owner approve or discard

### "“Lock everything down.” One physical pendant gesture should instantly put the whole hive into a reversible read-only safety mode."
- **useful because:** When the owner is driving, in public, or worried that a command was misunderstood, they need one dependable way to stop the system from changing files, sending messages, spending money, or mutating browser sessions. Today safety is fragmented across Mac jobs, relay work, and browser commands; there is no owner-controlled global brake.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → faculty-perception → faculty-action
- **model tier:** No expensive model for the lock itself: firmware gesture plus signed relay policy update and deterministic enforcement. Use realtime only to confirm the state in speech; use a cheap model later to summarize blocked attempts.
- **latency:** The pendant should enter local lock state immediately; relay, Mac, and browser enforcement should converge within 1 second when connected. Offline, the pendant must still block locally queued actions.
- **cost:** Near-zero per activation; occasional small relay storage and event costs. No model call is needed to enforce the policy.
- **security:** The gesture must be hard to trigger accidentally but usable under stress, and unlock must require explicit physical confirmation plus a short spoken/displayed challenge. Every surface must fail closed if the policy is stale or cannot be verified. Preserve read-only perception and emergency owner-approved actions, but never silently discard blocked work; retain bounded, redacted receipts.
- **missing:** A signed, monotonic global policy token understood by relay, Mac agent, and browser extension; A firmware button/gesture and offline enforcement state that survives link loss; A single enforcement middleware for Mac actions, relay jobs, and browser mutations, with blocked-action receipts; A clear unlock protocol and an owner-visible audit of what was prevented

### "“I’m around other people.” Make private information disappear everywhere until I explicitly restore it."
- **useful because:** Today a private browser tab, spoken response, notification, or screen can remain exposed even if the owner realizes someone is nearby. A single privacy state should coordinate the pendant, Mac display/audio, relay speech, and browser sessions instead of relying on app-by-app behavior.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception
- **model tier:** Deterministic policy and redaction; no model needed to enter privacy mode. A small classifier may label which queued outputs are sensitive when deciding what to suppress.
- **latency:** Local pendant and Mac audio/display response under 250 ms; browser and relay convergence under 1 second.
- **cost:** Negligible per event; optional local classifier adds less than $0.01 per queued item and should not run on raw screen content by default.
- **security:** Presence must be cryptographically authenticated, not inferred from Wi-Fi or a camera. Sensitive content already on screen must be blurred or replaced locally; never upload it for classification. Privacy mode must fail closed on stale heartbeats, and restore must be explicit so a dropped pendant cannot expose content.
- **missing:** A secure proximity/presence signal from the wearable (or a deliberate physical privacy gesture if radio presence is unavailable); A shared privacy policy token and expiry semantics across relay, Mac, and extension; Local browser redaction/placeholder behavior for sensitive tabs and a Mac audio/display mute curtain; A bounded queue for suppressed speech and notifications, with explicit owner-controlled release

### "“Forget what happened in the last hour.” Erase the selected conversation, recordings, browser evidence, and action traces everywhere, then prove what was actually removed."
- **useful because:** The owner cannot currently make one request that reaches relay audio, Mac pipeline files, browser provenance, announcements, and model context together; some stores are count-capped or retained indefinitely. This gives them a practical privacy control with a bounded, honest deletion receipt instead of a promise to forget.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → faculty-perception → faculty-action
- **model tier:** Deterministic deletion and cryptographic tombstones; no model should decide what to erase. Use a cheap model only to resolve a human time range into explicit records, then ask for confirmation.
- **latency:** Preview under 2 seconds; confirmed deletion receipt within 10 seconds, with offline pendant deletion acknowledged separately when it reconnects.
- **cost:** Usually under $0.02; dominated by relay/database writes and optional re-encryption, not inference.
- **security:** Require explicit confirmation showing the exact stores and time bounds. Do not claim deletion where a provider backup or an unmounted store cannot be reached. Tombstones must prevent replay after reconnect, and the receipt must omit the sensitive content it describes.
- **missing:** A cross-surface deletion manifest with stable record IDs and coverage status; Relay deletion/tombstone routes for announcements, audio, jobs, and context; current announcements and audio are not automatically swept; Mac deletion adapters for pipeline, jobs, action ledger, browser spool, evidence capsules, and provenance; Pendant-side encrypted queue/tombstone handling for data created while offline


## Changes it proposed to its own stack

### `relay` — Replace the pendant WebSocket's shared admin API key with a paired, device-scoped credential and challenge-response handshake. The relay should issue a short-lived session token with only pendant speech/event scopes; firmware should never transmit RELAY_API_KEY, and the relay should record the device identity used for every event.
- **owner gets:** If the pendant key leaks, it currently represents the relay administrator. This change limits a lost or reverse-engineered pendant to its own audio and telemetry instead of letting it control the owner's whole system.
- effort: Medium: relay handshake/auth middleware, credential rotation and migration, firmware credential storage and reconnect logic, plus an integration test against the live Mac bridge.  ·  risk: A bad migration could strand the pendant. Keep an emergency time-limited compatibility flag, dual-accept old/new credentials during pairing only, and expose a clear 'credential upgrade required' state rather than silently failing.
- cost: Negligible runtime/API cost; a few hundred bytes of firmware flash/RAM and no meaningful power increase.  ·  latency: Adds one challenge-response round only at connect/reconnect (typically <300 ms); no per-audio-frame overhead.
- security: Major improvement: removes admin authority from the wearable path, binds telemetry to a device, and enables revocation without rotating every relay client.
- depends on: A real nRF9160 registration/pairing flow (currently no pendant is in the registry); A defined pendant event schema for the accepted playback acknowledgement; Firmware storage for a scoped credential without writing routine metadata to the SD failure buffer


## What it asked for

_Nothing._
## Its own summary

Established fresh truth: the Mac agent is now fully permission-ready (Accessibility, Screen Recording, automation), computer-use vision loop is enabled, and Safari's browser bridge is online with 9 tabs. The pendant is still absent from the discovered device table; GET /v1/devices/status is not a Mac-agent route. The granted read_continuity_snapshot tool did not resolve at runtime; direct GET /ops/snapshot works. Proposed three owner capabilities: evidence-backed “Did you actually do that?”, a departure-risk check, and offline-pendant reconnect review with approval; also proposed replacing the pendant's shared admin WebSocket key with scoped paired credentials.

**Biggest unknown:** The pendant's actual registration/pairing and authenticated offline-upload path remain untestable. I still need a real pendant identity/heartbeat and a resolvable continuity snapshot surface; until then, pendant delivery, playback, and offline intent claims must remain unknown.

