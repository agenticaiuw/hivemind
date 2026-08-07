# Harness derivation — faculty-perception — round 40

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **macOS control and perception permissions** — As of 2026-08-07T11:02:24Z, the running AI Pendant Agent (com.aipendant.agent at /Users/evanliu/Applications/AI Pendant Agent.app) is not trusted for Accessibility and has no Screen Recording permission. /observe's zero-delta input probe failed; ui_actions_will_reach_the_screen=false. /ops/status reports computerUse.loopEnabled=false and visionUploadConsented=false. Automation grants are present, but these do not make pixel/UI input trustworthy.
  - evidence: GET /ops/status HTTP 200 and GET /observe HTTP 200 at 2026-08-07T11:02:24Z; observe explicitly says synthesized events are accepted only by a different binary and UI action receipts cannot be trusted.
- **time-zone state is contradictory** — The owner memory projection says authoritative timezone America/Chicago, while live GET /machine-context reports machine timezone America/New_York. This is unresolved; perception must not silently use either one for scheduling or time claims.
  - evidence: discover:owner live remembered.text says timezone America/Chicago; GET /machine-context HTTP 200 returns machine.timezone=America/New_York at this round.

## Capabilities it proposed

### "“What is actually true right now?” (and optionally “Is anything stale or contradictory?”)"
- **useful because:** Today different surfaces can confidently report incompatible realities: the owner profile says America/Chicago while /machine-context reports America/New_York; the browser is offline with three stale sessions; and Mac UI action receipts can say success while /observe proves events never reach the screen. A single evidence-backed reality snapshot would prevent the mind from acting on stale or untrusted state, and would tell the owner exactly what needs repair.
- **path:** pendant → relay → mac-bridge → browser → dashboard-ux
- **model tier:** Use a cheap background text model to normalize and reconcile telemetry; use realtime only to speak the short result. No screenshot or raw audio needs to leave the device: send typed health facts, timestamps, permission states, link loss counters, and browser session metadata.
- **latency:** 2–5 seconds for a manual spoken query; scheduled health sweep can run every 15 minutes without involving realtime. The response should be one sentence plus an optional dashboard evidence view.
- **cost:** Roughly $0.001–$0.01 per manual check depending on model/context; scheduled checks dominate volume but can use a small model. Relay storage is a few KB per snapshot, retained briefly.
- **security:** Do not include page contents, credentials, microphone audio, or secrets in the snapshot. Browser URLs/titles may be sensitive, so redact by default and retain only hashes and session identifiers. Mark each fact with observedAt, source, TTL, and confidence; if sources conflict, report the conflict rather than choosing silently. This is diagnostic/read-only and must never trigger repair actions.
- **missing:** A cross-surface typed health-snapshot endpoint and schema (pendant link/audio/pipeline counters, relay reachability, Mac permission/input probe, browser online/session freshness).; A reconciliation worker that computes freshness windows and explicit contradictions, rather than relying on hand-written fleetContext.; A dashboard timeline showing each assertion, source, timestamp, expiry, and why it was downgraded or rejected.; Pendant firmware telemetry for link quality, dropped uplink/downlink packets, SD fallback occupancy, and audio-path state, emitted as compact counters over the existing TLS WebSocket.

### "“Privacy lock.” (or hold the pendant button for three seconds)"
- **useful because:** The owner should be able to instantly make the entire hive stop listening, transmitting, acting, and exposing authenticated browser state—even if the Mac is busy, the relay is mid-job, or the network is unavailable. Today there is no single physical, offline control that reaches every surface and leaves unmistakable proof that the lock is active.
- **path:** pendant → relay → mac-bridge → browser → dashboard-ux
- **model tier:** No model is needed for activation or enforcement. A cheap background model may summarize interrupted work later; realtime should only acknowledge the lock after the pendant has locally latched it.
- **latency:** The pendant must mute microphone capture and stop uplink within 100 ms locally. Relay, Mac, and browser revocation should converge within 2 seconds when connected; offline devices must enforce the local lock and apply revocation on reconnect.
- **cost:** Negligible per-use API cost. Engineering cost is in a signed revocation protocol, firmware state machine, and browser/Mac integration; retained lock events are a few hundred bytes each.
- **security:** The lock must be fail-closed, survive reconnect and reboot, and be impossible for a remote job or model to override. Use a device-held key and monotonic lock epoch; every relay/Mac/browser command must reject epochs older than the current one. Do not upload audio or page content while locked. Dashboard should show last-seen status and explicitly distinguish “all surfaces confirmed locked” from “lock pending because a device is offline.” Resume requires a deliberate physical gesture plus spoken or dashboard confirmation, depending on owner policy.
- **missing:** A pendant firmware privacy-lock state with local microphone/uplink cutoff, LED/haptic indication, reboot persistence, and a physical resume gesture.; A signed, monotonic lock-epoch protocol shared by pendant, Cloudflare relay, Mac bridge, and browser extension; queued jobs and pending browser commands must be cancelled or quarantined on receipt.; A Mac agent hook that revokes active UI/browser leases and refuses new UI or shell work while locked, while preserving only a local lock-status endpoint.; A browser-extension hook that closes or freezes authenticated control channels without destroying the owner’s tabs, then reports confirmation state.; A dashboard privacy panel showing per-surface lock acknowledgements, offline exceptions, and a tamper-evident event timeline.


## Changes it proposed to its own stack

### `mac-harness` — Make every UI-affecting action receipt carry an inputTrust verdict from the latest /observe probe. If accessibility is untrusted, screen recording is absent, or the probe is older than a short TTL, ui_click/type_text/press_keys must return blocked_or_unverified instead of success; planner and faculty-action must treat that as a hard stop. Keep automation-only actions (AppleScript, reminders, shell) separately typed so they remain usable.
- **owner gets:** The owner will stop hearing that a task succeeded when nothing reached the screen. They get an honest explanation and can still use safe non-UI automations while pixel interaction is unavailable.
- effort: Small-to-medium: extend action receipt schema, add a preflight cache/TTL and route all UI action handlers through it, then add tests for stale probe, permission loss, and successful probe.  ·  risk: Some currently working tasks will become visibly blocked rather than falsely successful; recover by granting Accessibility to the exact running binary and rerunning the probe. A probe race could conservatively block one action, which is safer than an unverified mutation.
- cost: Negligible API cost; local implementation only. A few milliseconds per action for cached preflight.  ·  latency: Typically under 100 ms when cached; a fresh probe may add under a second before the first UI action.
- security: Improves safety and auditability by preventing unverified screen mutations. Does not expand permissions or upload screenshots.
- depends on: /observe input-reachability probe being authoritative and included in action receipts; a shared typed receipt schema consumed by planner/action surfaces


## What it asked for

### `s2-i8xy` (skill) — offline-reality-beacon
- does: Maintains a compact, monotonic health frame on the pendant: firmware build ID, boot/session ID, UTC-less monotonic timestamp, WebSocket connected state, last successful relay acknowledgement, uplink/downlink packet-loss counters, audio mode, and SD fallback bytes/files. Sends the latest frame on connect/reconnect and on a low-rate heartbeat; exposes the frame in the next diagnostic response so other surfaces can distinguish “last heard” from “currently healthy.”
- must be on-device because: Only firmware can observe modem link loss, audio pipeline state, and SD fallback before the connection exists. The relay cannot infer whether silence means a healthy idle pendant or a disconnected one, and this must continue to work offline and across reconnects.
- trigger: Periodic 30-second timer, WebSocket connect/disconnect/reconnect events, audio-path state transitions, SD fallback write, and a long-press diagnostic request (not ordinary press-to-talk).
- storage: RAM: one packed frame plus counters, under 256 bytes. Persist only boot/session ID and cumulative loss/fallback counters in a small rotating record on microSD (under 4 KB); obey the owner's rule that SD is failure-buffer-only, so do not write routinely when connected.
- RAM budget: Approximately 1–2 KB including serialization and a small reconnect queue, comfortably below the 211,608 B application RAM budget. No audio buffering or cryptography beyond the existing TLS stack.

## Its own summary

Recorded a new cross-hive capability: a physical, fail-closed Privacy Lock that immediately mutes and stops pendant uplink, revokes relay/Mac/browser leases, quarantines queued work, and reports per-surface confirmation. It requires new firmware state, signed monotonic lock epochs, relay/Mac/browser enforcement, and dashboard acknowledgement tracking.

**Biggest unknown:** Whether the physical pendant has haptic feedback or only its single LED/button; the lock design can use the available LED/button regardless, but confirmation ergonomics remain unspecified.

