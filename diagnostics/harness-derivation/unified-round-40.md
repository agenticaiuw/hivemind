# Harness derivation — unified — round 40

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **current connectivity** — The Mac bridge is online, but the authenticated browser extension is offline with zero tabs. Any cross-surface privacy or continuation behavior must tolerate browser absence and fail closed rather than assume a live tab.
  - evidence: discover:devices returned home-macbook-bridge online (last seen 2026-08-07T10:38:04.103Z) and home-chrome offline, 0 tab(s); probe_http GET /browser/status previously returned online:false.

## Capabilities it proposed

### "“Keep me safe from accidental exposure: when I move from speaking privately to using my Mac or browser around other people, pause sensitive work, mute private audio, and resume only when I explicitly say it’s okay—without losing my place.”"
- **useful because:** The pendant is the only surface continuously with the owner, while the Mac/browser may display or submit private information. A single privacy state shared across pendant, relay, Mac, and authenticated browser prevents a notification, screen, spoken response, or queued browser action from exposing secrets, and makes interruption recoverable rather than silently failing.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard-ux
- **model tier:** Realtime handles only the short spoken privacy-state command and acknowledgement. A cheap background policy worker evaluates queued work and produces a redacted continuation card; deterministic firmware and harness gates enforce the pause, not an LLM.
- **latency:** Pendant LED/audio acknowledgement under 250 ms locally; relay state propagation under 1 s when connected. On link loss, the pendant remains latched private locally and the Mac/browser fail closed until an explicit resume command is received.
- **cost:** Roughly $0.001–$0.01 per transition depending on whether transcription is needed; most transitions are local button/gesture events and cost no model call. Storage and event fan-out dominate engineering cost, not inference.
- **security:** The privacy state itself must be non-sensitive and tamper-evident; never upload raw ambient audio or infer a bystander’s identity. Sensitive queued payloads remain encrypted and are replaced in UI/audio with generic placeholders while latched. Resuming browser submissions, sending mail, or revealing secrets still requires the existing confirmation policy plus an explicit resume. A visible pendant LED and Mac menubar indicator show the latch.
- **missing:** A shared privacy-state protocol and fail-closed middleware consumed by Mac output, screen/UI automation, browser commands, and relay audio.; A pendant-local privacy latch firmware skill with button/gesture trigger, persistent state across reconnects, and local mute control.; Browser extension hooks to hide/redact sensitive tabs and refuse queued commands while latched.; Mac audio/display integration that can suppress TTS, notifications, screenshots, and computer-use actions.; A user-configurable safe allowlist for harmless actions (for example, timer or emergency call) and a recovery test matrix for power loss, reconnect, and stale resume tokens.

### "“For the next ten minutes, finish this one task using my private accounts, but only the exact fields we just discussed—and revoke access automatically when I double-press the pendant, walk away, or the task ends.”"
- **useful because:** Today consent is mostly a conversational moment; it can outlive the owner’s attention, the active browser tab, or the original intent. A wearable-issued, short-lived consent envelope would let the owner delegate a precise task across relay, Mac, and authenticated browser without granting broad standing access. The owner gets physical, understandable control over private automation rather than trusting a hidden session indefinitely.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard-ux
- **model tier:** Realtime interprets the spoken task and confirms the proposed scope. A cheaper background policy service compiles the scope into deterministic capabilities and checks every action. Firmware handles the physical revoke gesture and link-loss default; no model should decide whether a token remains valid.
- **latency:** Scope preview and pendant acknowledgement under 500 ms after the spoken request. Action authorization checks under 50 ms locally on Mac/browser. Revoke reaches every surface within 1 second when connected; pendant and Mac independently deny once the lease expires or link-health threshold is exceeded.
- **cost:** About $0.002–$0.02 per delegation, dominated by one scope-extraction/confirmation turn; subsequent checks are local signature verification and effectively free. Engineering cost is in policy enforcement and browser/Mac integration, not inference.
- **security:** The envelope must contain only a task identifier, allowed principals/sites, permitted fields/actions, expiry, and a revocation nonce—not passwords or raw private content. It must be non-transferable, hardware-bound to the pendant, single-use where possible, and auditable. Ambiguous scope, new domains, changed form fields, destructive actions, or sending/submitting still require a fresh confirmation. Revoke must win during races, and stale offline clients must fail closed.
- **missing:** A signed capability-token format and policy evaluator shared by relay, Mac harness, and browser extension.; Pendant firmware support for double-press revoke, lease display, and link-loss fail-closed behavior.; Browser enforcement at navigation, DOM read, field fill, and submit boundaries, not merely at command-queue level.; Mac enforcement for shell, GUI, clipboard, screen capture, and network actions with per-action scope checks.; A scope-preview UI/audio receipt showing exactly which account, site, fields, and expiry the owner authorized.; A durable revocation ledger and race-condition tests proving that queued actions cannot execute after revoke.


## What it asked for

_Nothing._
