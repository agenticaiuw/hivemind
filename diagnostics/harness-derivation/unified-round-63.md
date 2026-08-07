# Harness derivation — unified — round 63

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **privacy coordination gap** — Live capability manifest has browser, jobs, pipeline, notifications and ops groups but no privacy-latch, privacy-epoch, or cross-surface convergence route; existing pieces cannot currently enforce a single privacy pause.
  - evidence: GET /capabilities returned route groups and undocumented groups; none named privacy or latch, while browser/jobs/pipeline are present.

## Capabilities it proposed

### "“Privacy pause.” Instantly make the whole hive stop exposing private content, then restore it when I unlock the pendant."
- **useful because:** One spoken phrase or physical gesture should protect the owner across the surfaces that can leak information: mute pendant output, stop relay audio/transcripts and queued notifications, obscure or lock authenticated browser tabs on the Mac, and prevent Mac/browser actions until resumed. Today each surface can be protected separately, leaving race windows and requiring the owner to remember several controls.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** No model for the lock/unlock transition; a cheap background model may summarize the paused state for later. Realtime is only used to recognize the explicit phrase when the audio link is already active.
- **latency:** Local pendant mute and latch under 100 ms; relay and Mac/browser convergence target under 1 s, with an explicit receipt listing any surface that did not acknowledge. Restore only after a deliberate pendant button gesture or spoken unlock plus local confirmation.
- **cost:** Negligible API cost during the pause; implementation/storage and one status event dominate. Optional paused-state summary should use a cheap background model, under $0.01 per event.
- **security:** The lock must fail closed: no transcript, audio queue, browser command, screenshot, or notification should proceed after the latch is asserted. Do not send secrets to the model to implement the lock. Unlock must require a local pendant gesture (voice-only unlock is insufficient when the owner may be observed); browser tabs should be blurred/covered rather than closed, and all state transitions need an auditable receipt.
- **missing:** A single signed privacy-latch event protocol shared by pendant, relay, Mac harness, and browser bridge; Local pendant privacy latch firmware with offline mute and durable locked state; Mac/browser handlers that acknowledge mute, suppress screenshots/results, and hide authenticated tabs; A convergence/receipt endpoint and dashboard indicator for partial failures

### "“Use the code from my authenticator on this page, but never show or tell it to me.”"
- **useful because:** The owner can complete sensitive authenticated workflows without the AI, transcript, screenshots, relay, or Mac logs ever receiving the secret. The browser reads the OTP or password locally, the Mac types it into the verified target field, and the pendant reports only that the field was filled and whether submission succeeded. This is more than staged form filling: it creates a secret-blind execution path across the browser, Mac, relay, and pendant.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant → dashboard
- **model tier:** Use a cheap planner for field-target verification and workflow orchestration. Never send the secret to any model. Realtime is only for the owner's command and a one-sentence result.
- **latency:** Target verification under 1 s and local secret transfer/type under 500 ms. Require confirmation before final submission unless the owner has explicitly allowed that site and action class.
- **cost:** Usually under $0.01, dominated by one planner call; secret extraction, transport, and typing are local and model-free.
- **security:** The browser extension must retrieve secrets only from an explicitly approved authenticator/password source, bind them to an origin and DOM field fingerprint, and zero memory immediately after typing. The relay and model receive only opaque operation IDs and success/failure. Never expose the value in screenshots, DOM extracts, logs, receipts, crash reports, or spoken audio. Abort if the origin, field, or focus changes. Destructive submission still requires the owner's confirmation.
- **missing:** A browser-native secret broker that returns a one-time value only to a verified origin and field fingerprint; A Mac typing primitive that accepts an opaque secret handle without exposing text to the planner, shell, accessibility logs, or receipts; Redaction and zeroization guarantees in browser, relay, and Mac harnesses; A policy store for per-origin approval and submission confirmation


## Changes it proposed to its own stack

### `firmware` — Implement a signed, monotonic Privacy Epoch protocol. The pendant keeps a two-state latch (OPEN/PRIVATE) in retained flash, mutes playback and rejects non-unlock commands locally, and emits {epoch, state, reason, counter, expiresAt} over the existing link. Relay, Mac harness, and browser bridge must treat the highest epoch as authoritative, acknowledge it independently, fail closed on stale/missing acknowledgements, and attach the epoch to every queued audio item, screenshot, browser result, and action receipt so pre-pause data cannot be replayed after resume.
- **owner gets:** A single physical privacy gesture becomes trustworthy across the entire system—even during a dropped link or a race with an in-flight browser/Mac action—so the owner can safely say “privacy pause” in a meeting without checking several devices.
- effort: Medium-high: firmware state machine plus retained counter, relay schema and fan-out, Mac/browser acknowledgement hooks, and race/fault-injection tests for disconnects and in-flight actions.  ·  risk: A stale latch could leave the system muted or block useful automation. Recover with a local long-press unlock, visible LED state, bounded epoch expiry only for OPEN recovery (never automatic privacy exit), and a dashboard showing which surface failed to converge.
- cost: No per-event model cost; small flash/RAM footprint and a few relay/D1 records per transition.  ·  latency: Pendant local mute under 100 ms; cross-surface convergence normally under 1 s, bounded by Mac/browser heartbeat.
- security: Strongly positive: signed monotonic epochs prevent replay and fail closed. Requires key provisioning and careful avoidance of logging sensitive payloads in receipts.
- depends on: local_privacy_latch pendant skill; privacy_convergence_check and incident_diagnostics tools; Mac Accessibility/Screen Recording permission for tab obfuscation; browser bridge support for pause acknowledgements and suppression of in-flight results

### `browser-harness` — Add a SecretHandle channel between the authenticated browser extension and the Mac typing harness. The extension verifies origin, DOM field fingerprint, focus, and one-time expiry, then transfers only an opaque handle over an authenticated local channel. The Mac consumes the handle in a native secure-input primitive; planner, relay, screenshots, accessibility event logs, action receipts, and crash telemetry see only handle ID, field metadata, and outcome. Zeroize the handle after one successful or failed attempt and invalidate it on navigation or focus change.
- **owner gets:** The owner can sign in, enter an OTP, or complete another sensitive step by voice without the AI ever learning or repeating the secret, while still getting hands-free help with the surrounding workflow.
- effort: High: browser extension secret-source adapters, origin/field attestation, native secure-input API, memory zeroization, and adversarial redaction tests across logs, screenshots, retries, and crashes.  ·  risk: A compromised or misidentified field could receive a secret. Recover by requiring origin plus field attestation, refusing ambiguous matches, expiring handles quickly, and making final submission confirmation explicit. If the channel fails, leave the field untouched rather than falling back to plaintext typing.
- cost: No secret-related model tokens; modest engineering and local cryptographic/key-management cost.  ·  latency: Adds roughly 100–500 ms for attestation and secure typing; avoids repeated model calls and retries.
- security: Strongly positive if implemented as fail-closed opaque handles; requires OS keychain-backed channel authentication and strict secret redaction in every harness component.
- depends on: Mac Accessibility permission for secure typing; browser extension access to an approved password-manager/authenticator source; local authenticated browser–Mac channel; secret-aware receipt and telemetry redaction


## What it asked for

_Nothing._
