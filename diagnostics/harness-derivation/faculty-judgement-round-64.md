# Harness derivation — faculty-judgement — round 64

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “pause this and come back later,” save exactly where we are across my pendant, Mac, and browser, then later give me a 20-second spoken recap and let me resume without reconstructing the task."
- **useful because:** Real interruptions currently destroy context: the owner has to remember which tabs, draft, approval, and audio item were in progress. This would turn an interruption into a safe handoff, preserving the pending action without sending or submitting anything accidentally.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Use the cheap background model to compile the handoff and recap; use realtime only when the owner asks to resume or correct it. No model call is needed for the raw snapshot.
- **latency:** Capture in under 2 seconds; later recap begins within 1 second of the owner's request. Compilation can finish asynchronously in 5–15 seconds.
- **cost:** About $0.001–$0.01 per handoff depending on recap length; dominant cost is the one short background summarization, not state capture.
- **security:** The packet may contain private page text, draft contents, and task identifiers. Encrypt at rest, apply short retention (for example 7 days), omit secrets and full page bodies by default, and require confirmation before resuming any irreversible step. If a tab, job, or approval changed, say so and stop rather than replaying stale intent.
- **missing:** A durable cross-surface handoff record linking pendant audio position, relay job id, Mac job id, browser session/tab ids, pending approval, and explicit next action; A resume validator that compares the saved evidence/version with current browser and Mac state; A pendant resume control that can announce the recap and select resume, inspect, or discard offline

### "Make sure my scheduled brief actually reaches me. If the pendant cannot play it, keep a durable copy, retry when the link returns, and tell me exactly what was missed instead of claiming it was delivered."
- **useful because:** A completed background job is not the same as a useful result in the owner's ears. This closes the real-world gap between research, TTS, transport, and playback, especially when the pendant is offline or a stream underruns.
- **path:** relay-realtime → pendant → mac-planner → unified
- **model tier:** No expensive reasoning for the normal path: deterministic delivery receipts and a cheap background repair policy. Use realtime only to explain a failure or offer the queued item.
- **latency:** Acknowledge enqueue immediately; detect a failed or unconfirmed delivery within 10 seconds; retry on reconnect without waking the owner unless the item is marked urgent.
- **cost:** Usually below $0.001 per item for metadata and retry; TTS/audio transfer dominates, and retries should reuse the retained audio rather than regenerate it.
- **security:** Audio briefings can contain private calendar/mail data. Encrypt retained objects, use per-item expiry and deletion, never expose audio URLs in spoken logs, and distinguish delivered-to-device from actually-played. Urgent retries need an owner-configurable quiet-hours policy.
- **missing:** A durable delivery state machine with hop-level receipts: generated, transferred, decoded, buffered, played, failed, and expired; A pendant-side playback acknowledgement/underrun event and reconnect replay cursor; A relay watchdog that reconciles scheduled-job completion with audio delivery, deduplicates retries, and produces a human-readable missed-item receipt

### "I’m with other people—switch to discreet mode. From now on, keep private names, message text, account details, and page contents off the speaker and show me only safe summaries or a vibration cue until I turn it off."
- **useful because:** The pendant is worn in public, where a normally helpful spoken answer can disclose sensitive information. One explicit physical mode should constrain every surface, not just the voice reply, and should survive a dropped connection.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Deterministic policy enforcement and redaction first; a small background model may classify a response's disclosure risk. Realtime is only for the short safe spoken response.
- **latency:** The physical toggle must take effect locally in under 100 ms and propagate to relay/Mac/browser within 2 seconds. No network round trip may be required to suppress pendant playback.
- **cost:** Negligible per toggle; modest background classification cost only for ambiguous generated content, approximately $0.0005–$0.003 per response.
- **security:** Fail closed on unknown mode state: suppress content rather than speak it. Store only mode transitions, not the private text used for redaction. Browser and Mac agents must receive the policy before extraction or display, and the owner must explicitly turn the mode off.
- **missing:** A pendant-local discreet-mode latch and visual/haptic confirmation; A signed policy token propagated to relay, Mac, and browser that gates extraction, display, TTS, and queued replay; A redaction contract with tested categories (people, message bodies, account identifiers, secrets) and an owner-visible audit of what was withheld

### "I lost my pendant. Lock it and revoke its access everywhere now—stop queued audio, invalidate browser and Mac control, and tell me what was successfully frozen. If it comes back, make me re-pair it before anything resumes."
- **useful because:** A wearable carries private audio and acts as an authenticated doorway into the owner's Mac and logged-in browser. Losing it should not leave previously queued briefings playable or an unattended device able to authorize actions.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Use deterministic security logic and signed revocation events; no language-model call is needed except an optional short explanation of the freeze receipt.
- **latency:** Relay-side revocation within 1 second; propagate to Mac and browser within 5 seconds. The pendant should enter a local locked state on its next contact and never resume automatically after reconnect.
- **cost:** Negligible API cost; one small durable security event and delivery receipt per lock/unlock. Main engineering cost is protocol and recovery testing.
- **security:** Revocation must be authenticated through a second trusted channel, such as the owner's Mac or an already-authenticated voice session, and must be idempotent. Do not reveal private queued-item names in the lock receipt. Offline pendant behavior needs a local lock timeout or owner-set PIN, with secure deletion of cached audio and credentials.
- **missing:** A device identity and key lifecycle with per-pendant certificates, rotation, and a revocation list; A relay-to-Mac/browser kill switch that cancels queued commands and invalidates active sessions, not merely future requests; A pendant secure-lock state with encrypted cache wipe, reconnect quarantine, and explicit re-pairing ceremony; A signed, cross-surface freeze receipt proving which queues, sessions, and credentials were actually revoked


## Changes it proposed to its own stack

### `firmware` — Add a pendant-local discreet-mode latch toggled by a long press, with immediate haptic/LED confirmation, a monotonic mode generation number, and fail-closed playback: queued or incoming audio is muted unless the packet is explicitly marked safe. On reconnect, publish only the mode generation and transition timestamp, not private content.
- **owner gets:** The owner can prevent an accidental spoken disclosure instantly, even when the relay or Mac is unavailable, and know from haptic feedback that the protection is active.
- effort: Medium: button-state handling, a small persistent flag, packet metadata, and integration tests for offline toggle, reboot, reconnect, and queued-audio suppression.  ·  risk: A false active state could silence useful audio; recover with a distinct double-tap override and a clear haptic pattern. A reboot must preserve the safer state. This does not solve server-side redaction by itself.
- cost: No API cost; a few kilobytes of flash/RAM and negligible power beyond the LED/haptic pulse.  ·  latency: Under 100 ms local response; no added network latency for suppression.
- security: Improves confidentiality by failing closed locally. The mode token must be authenticated so a stale or forged relay packet cannot disable it.
- depends on: A defined safe-content marker and signed discreet-mode policy token in the relay/audio protocol; A server-side redaction gate for Mac/browser outputs


## What it asked for

_Nothing._
