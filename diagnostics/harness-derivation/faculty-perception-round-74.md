# Harness derivation — faculty-perception — round 74

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent-perception** — At 2026-08-07T12:53:48Z, /observe reports the running AI Pendant Agent has Accessibility trusted=false, Screen Recording=false, inputReachability.status=failed, and uiActionsWillReachTheScreen=false; AppleScript automation grants are present. Therefore UI receipts from ui_click/ui_menu/type_text/press_keys are explicitly untrusted, while AppleScript/browser paths remain viable.
  - evidence: GET /observe HTTP 200: accessibility.trusted=false; inputReachability.status=failed; consequence says synthesized UI events do nothing; automationMissing=[]
- **cross-surface-state** — The owner memory says timezone America/Chicago, while live /machine-context reports machine timezone America/New_York. This is an unresolved authority conflict that can shift scheduled routines and spoken time/date answers by one hour; no authoritative resolution is established.
  - evidence: owner remembered.text says timezone America/Chicago; GET /machine-context reports machine.timezone=America/New_York
- **pipeline-perception** — Live Mac pipeline contains a completed 24 kHz mono PCM TTS response (75,734 bytes, 1,578 ms, zero clipped samples) uploaded to relay, but also has an older nrf9160 run still status=processing and a browser bridge with 7 pending commands despite no active tab metadata. These are stale/orphan indicators requiring reconciliation before claiming work is complete.
  - evidence: GET /pipeline and GET /browser/status HTTP 200: TTS event sampleRate=24000, pcmBytes=75734, clippedSamples=0; pipeline run job_27616... status=processing; browser pendingCommands=7 with tabId/windowId null

## Capabilities it proposed

### "“Is everything actually ready right now?” (or “What can you truthfully do for me at this moment?”)"
- **useful because:** The owner currently gets optimistic completion states even when UI input is guaranteed not to reach the screen, browser commands are orphaned, a pipeline run is stuck processing, or device and memory disagree about timezone. This gives one concise, evidence-backed readiness report with explicit unknowns instead of false confidence.
- **path:** faculty-perception → relay-realtime → mac-planner → browser-extension → mac-terminal → unified
- **model tier:** deterministic first; use background model only to compress conflicting evidence into one short spoken sentence, never realtime unless the owner is actively asking
- **latency:** Under 2 seconds for probes and deterministic reconciliation; under 4 seconds if a background summary is needed.
- **cost:** Near-zero for route probes and rule checks; roughly 2k input tokens only for unusual conflict summarization.
- **security:** Reads operational metadata (permissions, queue state, browser tab metadata, pipeline telemetry), not page contents by default. Must label stale data and never infer success from UI action receipts when /observe says inputReachability failed. Timezone changes require owner confirmation before mutating routines.
- **missing:** A typed cross-surface truth/reconciliation endpoint that correlates timestamps, job IDs, and authority rules; An explicit owner-confirmed timezone authority (memory currently says America/Chicago; machine says America/New_York); Pendant-side live diagnostics/continuity snapshot, which is still unavailable to perception

### "“Did that actually reach my ears?” — and, if not, replay only the missing part when the connection returns."
- **useful because:** Today the system can prove that Mac TTS rendered PCM and the relay accepted bytes, but it cannot distinguish “uploaded,” “downloaded,” “speaker started,” and “owner likely heard it.” A wearable-specific delivery receipt would prevent silently lost reminders, alerts, and spoken answers, especially when LTE drops or the pendant is out of earshot.
- **path:** faculty-perception → relay-realtime → mac-planner → unified → faculty-judgement → faculty-action
- **model tier:** Deterministic telemetry and sequence validation; use the realtime model only if the owner asks for a natural-language explanation of a failed delivery. No model is needed to decide whether playback was acknowledged.
- **latency:** Receipt should arrive within 1 second of playback completion when connected; offline receipts persist locally and reconcile within 10 seconds of reconnection.
- **cost:** Near-zero inference cost; small relay D1 writes and a few hundred bytes of telemetry per utterance. Main cost is firmware and protocol engineering, not tokens.
- **security:** Transmit delivery metadata (utterance ID, byte count, start/end times, underrun count, volume/mute state, and optional coarse acoustic confidence), never microphone recordings. Do not claim the owner heard speech from playback completion alone; expose confidence and require confirmation before replaying potentially sensitive content in public.
- **missing:** Pendant firmware playback receipt with cryptographically bound utterance ID, byte-range completion, underrun/mute/interruption reason, and monotonic clock; Relay protocol for durable receipt upload, deduplication, and gap-aware replay requests; A perception/judgement rule that separates rendered, uploaded, downloaded, started, completed, and likely-audible states; An owner-facing replay policy that can resume from the first unacknowledged audio segment without duplicating already heard content


## Changes it proposed to its own stack

### `context` — Add a read-only perception reconciler that polls /observe, /ops/status, /machine-context, /pipeline, /browser/status, /jobs and /routing; normalizes each fact to {value, source, observedAt, freshness, authority}, emits contradictions (timezone mismatch, permission-vs-receipt mismatch, orphaned browser commands, stuck pipeline runs), and produces a machine-readable readiness snapshot for judgement. It must never execute, block, or silently repair actions.
- **owner gets:** Before the pendant says “done,” the owner gets an honest answer about what is reachable, what actually happened, and what remains unknown—especially avoiding fake GUI success and wrong local time.
- effort: Moderate: schema, route adapters, freshness/authority rules, and tests against stale pipeline/browser fixtures; no model needed for the core.  ·  risk: A bad authority rule could mark a healthy surface degraded or expose stale alarms. Recover by retaining raw evidence, showing source timestamps, and making the reconciler advisory-only.
- cost: Negligible API cost; one small deterministic request per readiness check. Storage is a compact snapshot plus event deltas.  ·  latency: ~100–500 ms when local routes are healthy; relay/pendant probes may add seconds and should be parallel with bounded timeouts.
- security: Operational metadata only by default; do not include page text, secrets, or audio payloads. Timezone and permission changes remain confirmation-gated.
- depends on: Define timezone authority with the owner (America/Chicago vs live machine America/New_York); Add pendant diagnostics/continuity snapshot access so readiness is not Mac-only; Define freshness windows and terminal-state rules for pipeline and browser jobs


## What it asked for

_Nothing._
## Its own summary

Established fresh live truth: the Mac agent is reachable and AppleScript/browser automation is available, but Accessibility and Screen Recording remain ungranted for the actual AI Pendant Agent binary; /observe explicitly says synthesized UI actions do nothing, so their receipts are untrustworthy. The 24 kHz PCM response path is demonstrably healthy (24,000 Hz mono, 75,734 bytes, zero clipping), while an older pendant pipeline run is still processing and the browser bridge has 7 pending commands with no tab/window metadata. Also found an unresolved timezone contradiction: owner memory says America/Chicago, live machine context says America/New_York. Recorded all three findings, notified faculty-judgement, and proposed a deterministic cross-surface readiness reconciler.

**Biggest unknown:** Pendant-local live diagnostics and continuity state remain unavailable, so I cannot establish whether the physical device received, retained, or played the apparently successful relay audio. The owner must also resolve which timezone is authoritative before time-sensitive routines are trusted.

