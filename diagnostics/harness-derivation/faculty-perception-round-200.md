# Harness derivation — faculty-perception — round 200

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **current Mac/browser reachability** — At 2026-08-08T23:05Z the Mac agent reports accessibility and screen recording granted, permissions.ready=true, browser extension online with 5 Safari tabs and 0 pending commands; relay reachable and Mac bridge online. Devices inventory still contains no nRF pendant, only home-macbook-bridge online and cloudflare-contract-test offline.
  - evidence: read_continuity_snapshot(include=[relay,pipeline], since=2026-08-08T22:50:00Z) resolved to GET /ops/snapshot HTTP 200; discover:devices returned the same device set.

## Capabilities it proposed

### "“Did you actually change that page, or did the browser only say it succeeded?”"
- **useful because:** Today browser execution, Mac receipts, and browser evidence are separate. This would give the owner a verifiable answer based on before/after observations rather than a green action response, including “unknown” when the extension never reports back.
- **path:** browser-extension → mac-planner → faculty-perception → faculty-action
- **model tier:** background for evidence assembly; realtime only to answer the owner’s follow-up
- **latency:** Initial action unchanged; verification within 2–5 seconds after the extension result, or an explicit timeout
- **cost:** Low API cost; mostly local hashing and one bounded browser read, with model use only for ambiguous semantic comparison
- **security:** Page values may contain secrets. Store hashes and redacted snippets by default; require confirmation before exposing sensitive before/after values. A missing browser result must remain unknown, never success.
- **missing:** Mount the existing browserProvenance routes; Make browser commands carry a stable operation/attempt join key into POST /browser/result/:commandId; A verifier that compares pre/post evidence capsules and emits verified|contradicted|unknown

### "“Before I rely on you, are all the parts you need actually available right now?”"
- **useful because:** The live state is fragmented: Mac agent and browser are online and permissions are ready, relay is reachable, but no pendant is registered. A single answer should distinguish usable Mac/browser automation from unavailable wearable delivery, rather than implying the whole system is healthy.
- **path:** faculty-perception → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** background snapshot classifier; realtime voice only formats the short answer
- **latency:** Under 1 second from cached heartbeats, with a freshness timestamp and a recheck only for stale components
- **cost:** Near-zero model cost; bounded reads of existing diagnostic endpoints
- **security:** Do not expose tab URLs or memory contents in the spoken summary. Treat stale/absent as unknown or unavailable, not offline unless the authoritative endpoint says so.
- **missing:** A small availability policy that maps each surface to usable|degraded|unknown|unavailable; A non-truncated, freshness-stamped response derived from GET /ops/status, GET /browser/status, GET /v1/devices/status, and GET /health; A voice-safe renderer that says “Mac/browser usable; pendant unavailable” without leaking diagnostics

### "“Tell me if anything you remember is machine-invented, stale, or contradicts the Mac before you use it.”"
- **useful because:** A machine-origin timezone fact is currently pinned at high confidence and injected into every context projection even though it contradicts /etc/localtime. This capability prevents invisible bad facts from steering routines, quiet hours, and actions; it reports the conflict and asks the owner instead of silently choosing.
- **path:** faculty-perception → faculty-judgement → mac-planner → relay-realtime
- **model tier:** background rule-based scan, with a cheap model only for explaining genuinely ambiguous conflicts
- **latency:** Run on memory refresh and before any time-sensitive routine/action; under 300 ms for deterministic checks
- **cost:** Negligible API cost; local comparison of provenance, confidence, expiry, and authoritative machine state
- **security:** Do not read or speak unrelated private facts. Surface only the conflicting key, provenance, and consequence. Never auto-delete or rewrite owner memory; correction requires owner confirmation.
- **missing:** A provenance-aware conflict scanner over memory projection and machine authorities; A durable conflict record with first-seen, last-seen, affected decisions, and resolution state; A judgement gate that blocks use of unresolved high-impact conflicts such as timezone or identity

### "“I plugged the pendant and audio bridge into this Mac—prove the whole path works before I trust it.”"
- **useful because:** A USB-connected pendant is a bench reality even though the relay currently has no pendant device. This would discover both serial devices, read the firmware health frame, run a short loopback/audio-quality test, verify relay registration and heartbeat, and clearly separate “wired and locally healthy” from “registered and remotely deliverable.”
- **path:** mac-terminal → faculty-perception → faculty-action → relay-realtime → unified
- **model tier:** background deterministic test runner; realtime only summarizes the verdict
- **latency:** 30–90 seconds for discovery, handshake, and a bounded audio test; never wait indefinitely for LTE
- **cost:** Negligible API cost; local serial I/O and one relay status read dominate
- **security:** USB test commands must be read-only or explicitly confirmed before flashing/resetting. Never upload raw microphone audio; upload only counters and a signed health frame. Treat a Mac serial path as bench-only, not proof of wearable operation.
- **missing:** A bounded macOS serial reader for /dev/cu.usbmodem* and /dev/cu.usbserial-*; A firmware diagnostic command that returns the accepted offline-reality-beacon and capture-integrity fields over USB; A relay-side pairing/heartbeat check that does not mistake Mac-bridge liveness for pendant liveness; A pass/fail report with independent local, relay, and audio verdicts

### "“Never speak a private answer aloud when my screen or surroundings suggest someone else could hear it; switch to a discreet notification and tell me why.”"
- **useful because:** The system currently knows the focused app, browser tab, audio path, and queued announcements independently, but it does not treat them as a privacy decision. This would prevent a wearable from reading passwords, health, finance, or private messages aloud while the owner is presenting, messaging, or using a shared computer.
- **path:** faculty-perception → faculty-judgement → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Deterministic policy engine with a small classifier only for app/tab sensitivity; no realtime model call for ordinary turns
- **latency:** Under 150 ms before speech begins; fall back closed when context is stale or unavailable
- **cost:** Near-zero recurring model cost; local focused-app/browser metadata and a relay-side speech gate dominate
- **security:** The privacy classifier must operate on metadata and redacted titles, not page bodies by default. Fail closed for stale context, and require explicit owner confirmation to override. Log only the policy decision and reason, never the secret answer.
- **missing:** A pre-speech privacy gate that can cancel or reroute relay audio; A normalized sensitivity policy covering focused Mac app, browser origin, and owner-declared quiet/public contexts; A discreet output channel with a visible or haptic acknowledgment so the owner knows an answer was withheld; An explicit distinction between owner-heard confirmation and bytes merely sent to a socket

### "“Before you send, buy, post, or edit anything, prove which account and workspace this browser is using—and stop if it is not the one I named.”"
- **useful because:** A successful browser click is not enough: the same site can hold several accounts, organizations, or workspaces. The owner needs protection against acting in a personal account, wrong Discord server, or wrong cloud project, especially when the browser session is private and no other node can inspect it.
- **path:** browser-extension → faculty-perception → faculty-judgement → faculty-action → mac-planner
- **model tier:** Deterministic account/workspace identity checks from page origin, visible identity markers, and authenticated browser evidence; model only resolves ambiguous labels
- **latency:** 1–3 seconds before a consequential action; no action proceeds while identity is unknown
- **cost:** Low; one bounded browser observation and local comparison per protected action
- **security:** Never store cookies, tokens, or full page content. Persist only a redacted identity assertion, origin, timestamp, and content hash. Treat an unverified identity as a hard stop, not a guess.
- **missing:** A browser identity-observation contract that exposes redacted account/workspace markers; A user-owned allowlist of acceptable identities per destination; An action gate joining identity evidence to the exact operation attempt; A revocation path when the browser session changes accounts

### "“If another person starts talking near me, stop reading private material aloud and wait until I’m alone or explicitly resume.”"
- **useful because:** Screen context cannot detect a roommate, coworker, or stranger standing nearby. A local acoustic privacy boundary would protect spoken answers even when the Mac looks safe, while preserving ordinary conversation through a short, explainable pause.
- **path:** pendant → ESP32 audio bridge → relay-realtime → faculty-perception → faculty-judgement
- **model tier:** Tiny on-device voice-activity/co-presence classifier for the first decision; relay model only handles the owner’s explicit resume request
- **latency:** Detect competing speech within 300 ms and mute before the next sensitive phrase; resume only after a stable quiet window plus owner intent
- **cost:** No per-event API cost; firmware work and a small calibration/storage budget dominate
- **security:** Raw ambient audio must stay on-device and be discarded immediately. Persist only counters and a privacy-state transition. False positives should delay speech, never leak it; an owner button gesture must provide an explicit override.
- **missing:** A local co-presence detector distinct from owner VAD, calibrated against the ESP32 microphone path; A relay protocol carrying privacy-state and mute/resume reason, not ambient recordings; A pre-speech classification of sensitive versus ordinary responses; A durable but minimal owner-visible record explaining each suppression


## What it asked for

_Nothing._
## Its own summary

Fresh discovery changed an important fact: the exact AI Pendant Agent now has Accessibility and Screen Recording, permissions.ready=true; Safari’s browser bridge is online with 5 tabs and no pending commands; relay and Mac bridge are reachable. There is still no registered nRF pendant. I recorded that verified state. I proposed four owner-facing capabilities: evidence-backed browser-change verification (kept distinct from mere job completion), an availability answer that says which surfaces are usable versus unavailable, detection of machine-origin memory conflicts before they steer decisions, and a USB bench test that proves local pendant/audio health separately from relay delivery.

**Biggest unknown:** The remaining decisive gap is physical/device truth: no live pendant telemetry or bounded serial reader exists in the callable inventory, so I cannot establish whether either USB chip is connected, healthy, or registered. I still need the serial diagnostic capability and a device-originated relay heartbeat/playback report; until then, relay acceptance and Mac-bridge liveness must not be reported as pendant availability or hearing.

