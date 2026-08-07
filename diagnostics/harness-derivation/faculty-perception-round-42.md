# Harness derivation — faculty-perception — round 42

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-vision reachability** — At 2026-08-07T11:08:50Z the Mac agent reports Accessibility trusted=false and Screen Recording=false; /observe says synthesized events are not accepted from com.aipendant.agent and UI actions may report success while doing nothing. Computer-use loop is disabled and vision upload consent is false.
  - evidence: GET /ops/snapshot and GET /observe live responses
- **browser availability** — At 2026-08-07T11:08:50Z home-chrome is offline with no active tab metadata and 3 pending browser commands; the Mac bridge and relay are reachable. The Mac agent nevertheless has 3 durable browser sessions and tabs including time.is/UTC and two test forms.
  - evidence: GET /ops/snapshot and GET /observe live responses
- **pendant continuity** — The pipeline contains recent nRF9160 offline-store events: a moment bookmark held while link_at_capture=down, then held alerts surfaced (2 alerts, later 1 alert) after reconnect. A cloud reply also arrived late and was forwarded after connection recovery.
  - evidence: GET /pipeline live response events from source nrf9160 and cloud-relay
- **audio output** — A recent cloud-relay spoken reply completed as 24,000 Hz mono s16le PCM, 164,650 bytes, 3,430 ms, with zero clipped samples; relay accepted it for the nRF9160. Input telemetry for that job was 15,625 Hz PCM, 937,500 bytes, 1,441 ms.
  - evidence: GET /pipeline live response, pipeline job_165a9c9a... events

## Capabilities it proposed

### "“When I get back online, tell me what happened while I was away—what the pendant captured, what arrived late, and what still needs my attention—once, in order.”"
- **useful because:** The pendant already records offline bookmarks and holds alerts, while the relay/Mac can receive late replies and browser/account changes. Today these are separate events, so reconnection can produce duplicates or omit the offline context. A single evidence-backed recovery brief would restore continuity without making the owner remember what was disconnected.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic event reconciliation and deduplication first; use a cheaper background text model only to summarize unresolved items. Realtime is unnecessary unless the owner asks during a live reconnection.
- **latency:** On link restoration, emit an initial spoken 1–2 sentence summary within 2 seconds; enrich with Mac/browser evidence within 10–30 seconds. No blocking of normal pendant use.
- **cost:** Near-zero model cost when only event templates apply; roughly $0.01–$0.05 for an occasional background summary, dominated by browser/account extraction and TTS audio generation.
- **security:** Private browser/account data would leave the browser only as extracted fields and source hashes; keep sensitive values local and require confirmation before any action. Show event timestamps, source (pendant/relay/Mac/browser), and a quiet dedupe ledger so an alert is not repeated after acknowledgement.
- **missing:** A durable cross-surface continuity event schema with capture time, observed time, source, link state, urgency, and acknowledgement ID; Relay-to-pendant reconnect hook that requests the held-event inventory and returns acknowledgement receipts; Mac/browser collectors that can contribute only changes since the last confirmed continuity watermark; A compact spoken recovery-brief renderer and dashboard timeline for review

### "“If I approve something on the pendant while I’m offline, carry out exactly that approved action when the Mac reconnects—tell me if anything changed first.”"
- **useful because:** Today an offline spoken approval cannot safely travel across the pendant, relay, Mac, and private browser session: replaying raw intent later risks acting on a changed page or changed parameters, while discarding it makes the pendant unreliable away from the Mac. A signed, human-readable approval envelope would let the owner make progress without being near the computer while preserving the exact boundary of consent.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic envelope creation, hashing, expiry, and precondition comparison; use a cheaper background model only to render a concise explanation of differences. Realtime is not needed except for the initial spoken confirmation.
- **latency:** Pendant should acknowledge local capture immediately; relay queues it durably. On reconnect, compare preconditions in under 5 seconds and speak either executed, expired, or changed—never wait indefinitely or silently execute.
- **cost:** Near-zero model/API cost for envelope validation; occasional background explanation about $0.01–$0.03. Dominant costs are durable storage and browser/Mac verification, not inference.
- **security:** The envelope must contain an action digest, exact parameters, allowed surface/session, creation time, expiry, and owner confirmation transcript hash—not reusable secrets. Mac/browser must re-read the target and stop on any meaningful change, authentication change, or irreversible action. Destructive actions still require a fresh online confirmation; dashboard must show pending, compared, executed, and rejected receipts.
- **missing:** A pendant-side offline approval record with monotonic ID, local timestamp, action digest, and tamper-evident storage; Relay support for encrypted, idempotent approval-envelope queuing and delivery acknowledgements; Mac/browser precondition snapshots and a verifier that compares the approved target against the live private page before execution; A cross-surface policy distinguishing reversible approvals from approvals that must expire or be reconfirmed online; A dashboard and spoken status vocabulary for pending, changed, expired, executed, and rejected envelopes


## Changes it proposed to its own stack

### `mac-harness` — Make the Mac agent enforce an input-reachability precondition for every UI action: cache the exact running binary identity, run a zero-delta probe at startup and before each UI batch, and return a typed blocked result (not success) whenever Accessibility or Screen Recording is untrusted. Include the permission identity mismatch and remediation in the receipt; never let ui_click/type_text/press_keys execute as apparent success.
- **owner gets:** The owner currently cannot trust whether a GUI request happened: live observation says synthesized events are rejected, yet UI actions may report success while doing nothing. This prevents silent failures and misleading completion receipts.
- effort: Medium: action dispatcher gate, permission identity verification, receipt/status schema, and a small regression harness covering revoked permissions and wrong-binary grants.  ·  risk: Some legitimate actions will be blocked until permissions are fixed; recovery is explicit regrant guidance and a non-UI fallback where available. Probe itself must remain no-op and never disturb the cursor.
- cost: No model cost; negligible local CPU. Avoids wasted model calls and repeated failed actions.  ·  latency: Adds tens of milliseconds per UI batch for the probe; substantially reduces false completion and retries.
- security: Improves safety by refusing unverified GUI actions. Does not grant permissions or upload screenshots; Screen Recording remains opt-in.
- depends on: Grant Accessibility and Screen Recording to the exact running com.aipendant.agent binary, or expose a clear permission-repair path; Typed action receipts consumed by judgement/action surfaces

### `firmware` — Add an explicit ingress-audio contract and telemetry: the pendant must label every captured stream with its actual sample rate, and the relay/ Mac path must either preserve 24 kHz end-to-end or explicitly resample 15.625 kHz input to 24 kHz with quality/latency metadata. Reject or quarantine unlabeled/mismatched PCM instead of silently treating it as 24 kHz.
- **owner gets:** A recent live job produced verified 24 kHz playback, but its input telemetry was 15,625 Hz. Without an explicit contract, the owner can hear a technically valid response while speech quality, duration, and pitch vary unpredictably between sessions.
- effort: Medium: firmware capture metadata, relay validation, one resampling stage, and dashboard/pipeline warnings.  ·  risk: Resampling adds CPU and a small delay; old clients may be rejected until version-gated. Recovery is compatibility mode with a visible warning, never silent reinterpretation.
- cost: No API cost. Moderate pendant/relay CPU; likely tens of KB transient buffers, within available RAM only after measuring current audio buffers.  ·  latency: Approximately 5–30 ms for buffered resampling, depending on implementation.
- security: Audio remains on existing relay path; metadata adds no new owner content. Validation reduces accidental mis-decoding.
- depends on: Authoritative 24 kHz implementation status; Pendant audio capture diagnostics and actual firmware buffer budget; A shared typed audio-format schema across nRF9160, relay, Mac TTS, and playback


## What it asked for

_Nothing._
## Its own summary

Fresh live perception established: Mac UI automation is not trustworthy (Accessibility and Screen Recording false; events rejected despite apparent success), Chrome bridge is offline with 3 queued commands while relay/Mac remain online, and the pendant has real offline continuity events (bookmark/held alerts) that surface after reconnect. A recent response playback is genuinely 24 kHz mono with zero clipping, but the same job reports 15,625 Hz input, exposing an audio-contract mismatch. I recorded four evidence-backed findings, messaged judgement/peer agents, and proposed a cross-surface reconnect recovery brief plus hard UI reachability gates and explicit audio-format validation/resampling.

**Biggest unknown:** I still need authoritative pendant diagnostics and continuity acknowledgement/retention semantics to know whether held bookmarks and alerts can be safely deduplicated and acknowledged. The exact Accessibility/Screen Recording grant for the running binary also remains unresolved, and current 24 kHz ingress implementation/buffer limits are unknown.

