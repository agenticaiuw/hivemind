# Harness derivation — faculty-perception — round 69

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **current Mac/relay/browser reachability and permissions** — At 2026-08-07T12:36Z, Mac local agent and relay are reachable; mac bridge last seen 12:36:35Z. Chrome browser bridge is offline with 5 pending commands. Mac accessibility and screen-recording are not granted, while listed automation grants are present; permissions.ready=false and computer-use loop is disabled.
  - evidence: GET /ops/status returned HTTP 200 with these fields.
- **audio path as currently implemented** — Pendant audio remains prototype: I2S capture is 15,625 Hz; uplink Opus is 16 kHz/16 kbps; playback decodes at 24 kHz in 60 ms frames and outputs through a 31,250 Hz I2S wire clock. A completed pipeline run rendered 24,000 Hz mono PCM successfully, while a live capture run reported 15,625 Hz input.
  - evidence: get_hardware_spec(audio) plus GET /pipeline HTTP 200 event metadata.
- **timezone disagreement** — Owner memory states America/Chicago, but live Mac /machine-context reports America/New_York. The authoritative timezone is unresolved; scheduling or spoken time must not silently pick one.
  - evidence: discover(owner) remembered.timezone and GET /machine-context machine.timezone.
- **duplicate page-watch reports** — The activity log contains multiple completed reports for the same Order 42 watch, each repeating Processing → Shipped and each marked acknowledged=false, at several timestamps within about an hour. This demonstrates duplicate surfacing in the current watch path, not merely a hypothetical risk.
  - evidence: GET /logs HTTP 200 returned repeated page watch: Order 42 results with distinct report IDs and identical change payloads.

## Capabilities it proposed

### "“Give me one trustworthy status snapshot of my pendant, Mac, relay, and browser—and point out any contradictions or stale readings instead of guessing.”"
- **useful because:** Today the system can report each surface separately, but it can silently present conflicting timezone and audio facts, or imply browser work is available while the extension is offline. A single evidence-ranked snapshot lets the owner know what is actually reachable before relying on an answer.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for periodic health snapshots; realtime only when the owner asks verbally
- **latency:** under 2 seconds for cached status; under 8 seconds for a fresh cross-surface probe
- **cost:** <$0.01 per on-demand snapshot; dominated by no model call for normal typed comparisons, with a small text summary only when contradictions need phrasing
- **security:** Expose only operational facts (reachability, freshness, sample rates, permission state), never tokens, page contents, or secret memory. Require confirmation before changing device or permission state.
- **missing:** A typed cross-surface health schema with timestamps, source, freshness TTL, and contradiction rules; Pendant-side telemetry endpoint feeding capture/playback/link state into the same snapshot; A durable alert deduplication/ack state so stale or repeated reports are distinguishable from new facts

### "“Find whichever one I’m looking for—my pendant or my Mac—and make it identify itself without changing anything else.”"
- **useful because:** A wearable and the computer it controls are easy to misplace. Today neither node can establish a reliable two-way find flow: the Mac cannot command the pendant to emit a distinctive local signal, and the pendant cannot ask the Mac to identify itself while the owner is away from the desk. This would turn the hive into a practical physical locator rather than only a remote-control system.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** No expensive model for the locate operation; deterministic routing and a short realtime confirmation only if the owner asks by voice.
- **latency:** Start the target signal within 2 seconds when the target is online; report unreachable/stale within 5 seconds.
- **cost:** Negligible API cost; one small relay command and receipt. Hardware cost is near-zero if the existing pendant playback/LED/button are used; optional louder buzzer or vibration motor would be roughly $2–$8 and under 100 mW while active.
- **security:** Require paired-device authentication and a local physical confirmation for unattended pendant ringing if the owner marks it private. Do not reveal location or network identifiers; rate-limit repeated locate requests.
- **missing:** A paired-device locate protocol with authenticated target selection and expiry; Pendant firmware command for distinctive beep/LED/vibration plus acknowledgement and timeout; Mac-side safe identify action (audible alert or notification) and receipt reporting; A last-seen/freshness contract so the system says 'not reachable' rather than claiming it found the device


## Changes it proposed to its own stack

### `context` — Add a cross-surface evidence reconciler that ingests typed observations from /ops/status, /machine-context, /pipeline, /browser/status, and job receipts; preserves every source timestamp, computes freshness, emits explicit conflicts (for example Chicago vs New York or 15,625 Hz capture vs 24 kHz playback), and forces downstream judgement to say unknown when no authority wins. Deduplicate identical watch reports by semantic fingerprint until acknowledged or materially changed.
- **owner gets:** The owner gets fewer confident-but-wrong answers and stops hearing the same alert repeatedly. Time, reachability, and audio claims become visibly sourced rather than blended from stale context.
- effort: Medium: schema, TTL policy, conflict rules, semantic fingerprints, and dashboard/voice rendering; no new model required for the core.  ·  risk: An overly strict conflict rule could produce too many 'unknown' answers; recover with per-field authority and explicit owner confirmation. Deduplication must not hide a real recurrence, so retain raw events and reopen only on changed evidence.
- cost: Negligible API cost; small D1/local JSON storage for observations and fingerprints.  ·  latency: Milliseconds for local typed comparison; a few seconds only if a fresh probe is requested.
- security: Improves privacy by passing compact metadata rather than page contents; source IDs and timestamps still need access control.
- depends on: Pendant telemetry endpoint for capture/link/playback facts; An authoritative timezone setting or owner-confirmation flow; Persistent acknowledgement semantics for watch reports


## What it asked for

_Nothing._
## Its own summary

Established and recorded four new live facts: Mac/relay reachable but browser offline with 5 queued commands; Accessibility and Screen Recording remain absent and computer-use disabled; audio capture is still 15,625 Hz despite a working 24 kHz playback/TTS leg; live Mac timezone conflicts with owner memory; repeated identical page-watch reports are being emitted unacknowledged. Proposed a cross-surface evidence reconciler and trustworthy status snapshot, with deduplication and explicit unknown/conflict handling. Still needed: owner-selected authoritative timezone, pendant telemetry for capture/link/playback, durable alert acknowledgement/dedup semantics, and owner enabling the exact agent’s TCC permissions if GUI automation is desired. I did not re-request denied permissions or already-pending tools.

**Biggest unknown:** The pendant’s current live telemetry and the authoritative timezone remain unavailable; therefore end-to-end 24 kHz capture status and time-sensitive scheduling cannot yet be asserted.

