# Harness derivation — faculty-perception — round 194

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac perception prerequisites** — The exact AI Pendant Agent identity now has Accessibility and Screen Recording granted; /ops/status reports permissions.ready=true, requiredMissing=[], fullControlMode=true, computerUse.loopEnabled=true, and browser extension online on Safari tab 3583395 at discord.com. The relay is reachable and Mac bridge online, but the device table still shows no nRF9160 pendant; only home-macbook-bridge is online.
  - evidence: GET /ops/status HTTP 200 at 2026-08-08 round 194; GET /health HTTP 200; discover:devices in this round

## Capabilities it proposed

### "Before you act on anything, tell me whether each important claim is fresh, authoritative, and actually supported: what you observed, when, where it came from, and what remains unknown."
- **useful because:** This is the single most useful perception capability: it prevents the system from turning stale machine facts, browser text, relay acceptance, or a Mac-side completion into confident action. It gives faculty-judgement a typed reality fence rather than a vague confidence score.
- **path:** relay-realtime → mac-planner → browser-extension → unified → faculty-perception → faculty-judgement
- **model tier:** Cheap deterministic aggregation first; use the realtime model only to explain conflicts in the owner's words. No model call for freshness, source precedence, or missing-writer checks.
- **latency:** Under 300 ms from cached snapshots; under 2 s if a live browser or Mac observation is needed.
- **cost:** Near-zero API cost for the normal path; occasional explanation uses a few hundred realtime input/output tokens. Dominant cost is context transfer if raw snapshots are resent, so pass compact claim records.
- **security:** Never expose page bodies or secrets merely to explain freshness. Treat browser content as untrusted, preserve source and capture timestamps, and require judgement confirmation when the only support is stale, machine-originated, or relay-side socket delivery.
- **missing:** A claim-level observation schema with source, observedAt, authority, freshness policy, and explicit unknown reason; A Mac route that returns bounded browser/session and permission observations in one compact response; A relay-to-Mac join key for jobs, browser evidence, and playback events

### "Tell me when the browser context I am relying on has drifted: the tab, account/session, URL, title, or page content changed since the evidence you used."
- **useful because:** A browser answer can be perfectly captured and still become wrong a minute later. Drift detection lets the system say 'that was true on Discord tab X at time Y, but this is now tab Z' before sending a message, purchasing, or summarizing a page.
- **path:** browser-extension → mac-planner → faculty-perception → faculty-judgement → relay-realtime
- **model tier:** Deterministic URL/title/tab identity and content-hash comparison; a cheap background model may summarize the semantic change only when the owner asks.
- **latency:** Event-driven heartbeat/poll update in under 1 s; owner-facing explanation under 2 s.
- **cost:** No model cost for detection; roughly 100–300 tokens only for an on-demand semantic-change explanation.
- **security:** Hash redacted page content rather than storing raw secrets; pseudonymize account/session identifiers; do not treat a URL or title as proof of login identity. Any action based on a drifted or login-wall page requires fresh confirmation.
- **missing:** A persistent, bounded browser-observation baseline keyed by extension/session/tab; A content-hash and login-wall transition event from the browser bridge; A judgement policy defining which changes invalidate a claim versus merely lower confidence

### "Is my pendant physically present and healthy right now, or am I only seeing a stale relay/Mac record? If it spoke, did the device actually play the audio?"
- **useful because:** Today the relay can be online while no pendant is registered, and a completed job means the Mac finished, not that the owner heard it. This capability gives a decisive bench-and-product truth: USB presence now, relay registration separately, and device-reported playback separately.
- **path:** mac-terminal → mac-planner → relay-realtime → faculty-perception → faculty-judgement → unified
- **model tier:** Deterministic serial probe, relay registry read, and monotonic beacon/playback-event comparison; no language model unless the owner asks for a narrative.
- **latency:** USB/relay diagnostic under 2 s; playback verdict becomes available within one device heartbeat or offline queue flush.
- **cost:** No model cost; negligible relay storage and a few hundred bytes per bounded device-health sample.
- **security:** Never claim hearing from relay socket writes. Authenticate the device event with its scoped credential, bind it to an artifact ID, and expose the distinction between connected, registered, received, started, finished, and interrupted.
- **missing:** A production serial diagnostic action for the currently granted Mac agent (the accepted mac_usb_serial_diagnostics grant is not yet callable as a tool); Firmware emission of authenticated playback lifecycle events using the accepted audio_delivery_ack_queue behavior; Relay registry/device-auth wiring that lets the pendant heartbeat without sending the admin key; A compact UI/voice vocabulary for physically present versus relay-visible versus owner-heard

### "Tell me immediately if an app update, restart, or identity change has silently removed the Mac permissions needed to see or control my screen, browser, or automation targets."
- **useful because:** Perception is only as truthful as its observation channel. The exact agent is healthy now, but a future bundle/executable change could make screenshots or input fail while the system continues speaking as if it saw the screen. This turns a silent blind spot into an explicit, timestamped reality change.
- **path:** mac-planner → mac-vision → browser-extension → faculty-perception → relay-realtime → unified
- **model tier:** Deterministic permission and host-identity checks on every session start and before vision/input; no language model.
- **latency:** Under 150 ms at startup and before each sensitive observation; voice warning under 1 s.
- **cost:** No model/API cost; a few local system queries per session.
- **security:** Report only grant state and binary fingerprint, never TCC database contents or unrelated app data. A missing grant must fail closed for screen/input claims, while still allowing AppleScript routes whose grants remain valid.
- **missing:** A startup/ preflight hook that compares the currently running bundle and executable fingerprint against the last known-good identity; A durable permission-state transition record exposed to faculty-perception; A policy preventing vision/action claims after a failed preflight

### "Show me exactly what the system knew at the moment it acted: the browser or Mac observation it relied on, the model input, the action it chose, which body delivered it, and every unresolved gap—replayable later without pretending current state was true then."
- **useful because:** A current status page cannot answer why an old action was reasonable or where it went wrong. A temporal replay would let the owner audit a mistaken message, purchase, deletion, or spoken answer from the actual historical evidence rather than from reconstructed present-day state.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Deterministic event reconstruction and hash verification first; use a cheap text model only to narrate the replay. Never resend full historical context to the expensive realtime tier unless the owner requests it.
- **latency:** Index lookup under 500 ms; a human-readable replay under 3 s.
- **cost:** Low ongoing storage cost for compact event envelopes and hashes; occasional narration costs a few hundred tokens. Raw page/audio bodies should remain local and be fetched only on explicit request.
- **security:** Encrypt historical envelopes, redact secrets before persistence, bind every event to a session and artifact hash, and clearly label reconstructed gaps. The replay must never imply an action succeeded merely because an intent was recorded.
- **missing:** An immutable cross-surface event envelope with observedAt, actor/body, artifact hash, model-turn ID, action ID, and outcome state; Versioned prompt/context references so a historical decision can be replayed without retaining every secret; A bounded local index joining Mac ledgers, browser provenance, relay jobs, pipeline traces, and device playback events

### "Keep one conversation when I move between bodies: if the pendant disappears, continue on the Mac; if the Mac sleeps, resume on the relay or browser—and tell me which body heard, saw, or spoke each turn instead of blending them together."
- **useful because:** The hive is only meaningfully different from a Mac assistant if its identity and perception survive movement between physically different surfaces. Today a relay session, Mac session, browser tab, and absent pendant can be mistaken for one continuous observer without a reliable handoff.
- **path:** relay-realtime → mac-planner → browser-extension → unified → faculty-perception → faculty-judgement
- **model tier:** Deterministic session handoff and monotonic sequence reconciliation; use the realtime model only to make a short spoken handoff notice when continuity is interrupted.
- **latency:** Handoff detection under 2 s after a heartbeat/session loss; resume under 5 s.
- **cost:** Negligible model cost for normal handoffs; a short voice notice costs a few dozen realtime tokens. Main cost is a small durable session ledger.
- **security:** Require explicit device/session possession proofs, never transfer browser secrets or audio buffers to an untrusted body, and mark every turn with the body that actually observed or delivered it. A resumed session must not claim the pendant heard prior speech.
- **missing:** A shared conversation epoch and sequence protocol across relay, Mac, browser, and pendant; A body-specific capability/authority declaration and handoff acknowledgement; A durable per-turn body provenance record with explicit interrupted/unknown states

### "Quietly test whether each perception channel is still real before I depend on it: verify the browser can return the same page marker, the Mac can observe the focused app, the relay can reach the bridge, and the pendant can report its beacon—without taking an action or recording private content."
- **useful because:** A green online flag is not proof that the observation path works. A non-destructive reality canary would catch stale browser heartbeats, dead screenshots, broken relay joins, and a disconnected wearable before the system confidently answers from a blind channel.
- **path:** mac-vision → mac-planner → browser-extension → relay-realtime → unified → faculty-perception
- **model tier:** Deterministic synthetic probes and signed expected markers; no language model. The probe should compare channel identity and freshness, not inspect arbitrary user content.
- **latency:** On demand under 3 s; optional low-rate background check every 10 minutes while the system is active.
- **cost:** No model cost; tiny local/relay telemetry overhead. Pendant beacon traffic should remain within the accepted low-rate heartbeat budget.
- **security:** Use synthetic test pages or local markers, never probe private tabs, never click or mutate anything, and make the result explicit that channel liveness is not evidence about page content or owner hearing.
- **missing:** A read-only synthetic browser marker endpoint and Mac observation canary; A relay challenge/response tied to the current bridge session; Pendant beacon challenge response and a local-only fallback when the pendant is absent; A bounded canary result store with freshness and failure reason


## What it asked for

_Nothing._
