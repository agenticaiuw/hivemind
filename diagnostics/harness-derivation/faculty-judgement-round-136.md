# Harness derivation — faculty-judgement — round 136

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“When I say approve, show me the exact action on my Mac, then let me confirm it with one deliberate tap on the pendant—only after that may you send, buy, delete, or submit.”"
- **useful because:** A spoken yes is easy to trigger accidentally and is awkward while away from the keyboard. A physical tap gives the owner a fast, unambiguous final consent while the Mac/browser can prove what is about to happen. This is the single most useful trust boundary for making the hive safe enough to use daily.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only for the spoken summary; deterministic relay/device code verifies the nonce and action hash, and the Mac/browser agents execute after approval.
- **latency:** Under 2 seconds from spoken approval to a short pendant prompt; under 1 second after the tap. Most time is USB/BLE/serial round-trip, not model inference.
- **cost:** About $0.001–$0.01 per approval, dominated by the short realtime turn; verification and action routing are negligible.
- **security:** The pendant must display or speak a compact action digest, bind a one-time nonce to the exact typed action and account/session, expire it quickly, and reject stale/replayed taps. Never treat a lost or disconnected pendant as approval. Sending mail, purchases, deletion, and form submission require this gate; reversible local actions may remain voice-only.
- **missing:** signed pendant challenge-response over the current USB serial link (and LTE later); relay action-hash approval endpoint; Mac/browser executor gate that refuses an unapproved hash; owner-visible approval history

### "“If my pendant is lost or I hold its button for five seconds, lock down my private sessions everywhere and erase any queued recordings or spoken briefings; tell me what was revoked when I recover.”"
- **useful because:** A worn device can expose private audio and authorize actions. Today loss is a privacy emergency with no single physical response. A local long-press must work offline, while the relay and Mac revoke browser sessions and clear sensitive queues as soon as they can reconnect.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** No expensive model for the emergency path. Firmware and relay perform deterministic revocation/erase; a cheap background model may compose the recovery report afterward.
- **latency:** Local erase and lock indication within 1 second; relay/Mac revocation on next link heartbeat, target under 10 seconds. Recovery report can take minutes.
- **cost:** Near-zero API cost for the emergency path; a few cents only if a recovery report needs summarization.
- **security:** Require a deliberate long press and haptic/LED confirmation to avoid pocket activation, but do not require network access. Store only a small revocation epoch and erase queued PCM/audio plus bearer credentials locally. Relay must invalidate sessions and browser commands idempotently; recovery must not reveal secrets on an untrusted replacement device.
- **missing:** firmware long-press handler and secure local wipe; relay device-revocation epoch and token invalidation; Mac endpoint to clear pending jobs/audio and lock private browser sessions; recovery receipt that lists categories, not secret contents

### "“When I arrive somewhere or start a focused block, make my devices agree on the same privacy mode: hush non-urgent pendant audio, pause browser watchers, defer Mac notifications, and give me one short catch-up when I leave.”"
- **useful because:** The owner should not have to silence three surfaces independently when entering a meeting, shared room, or deep-work block. The pendant is the only always-with-them trigger; the relay can coordinate policy while the Mac and browser apply it locally, then restore state without losing queued work.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic policy/routing for mode changes; a cheap background model composes the deferred catch-up. Realtime is used only if the owner asks a follow-up question.
- **latency:** Mode latch within 2 seconds of a pendant button gesture or spoken command; catch-up generation can complete asynchronously in under 1 minute.
- **cost:** Usually <$0.005 per transition; summarization is the dominant cost and should be batched into one short digest.
- **security:** Modes must be explicit, reversible, and visible in the dashboard/pendant LED. Never suppress emergency alarms or an already-approved destructive-action confirmation. Location should remain on-device unless explicitly enabled; default triggers are button, calendar focus state, or Mac lock/unlock rather than GPS.
- **missing:** shared mode policy and state endpoint; pendant offline mode latch with persistence; Mac notification/focus adapter; browser-watch pause/resume semantics that preserve baselines; deferred-audio queue with priority and expiry

### "“Know when I am still wearing the pendant: lock my Mac’s private browser sessions and stop sensitive audio when it is set down, then restore my place when I put it back on.”"
- **useful because:** A worn device can serve as a physical presence key. Today a forgotten pendant can leave logged-in pages and queued speech exposed, while removing it needlessly loses context. Automatic proximity loss protection gives the owner privacy without requiring them to remember a command.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic device/relay policy; no model on lock or restore. A cheap background model may summarize what was deferred after reattachment.
- **latency:** Detect removal in 3–10 seconds and lock/silence within 2 seconds of a confirmed absence; restore a recovery card within 30 seconds of reattachment.
- **cost:** Negligible API cost; periodic presence beacons and a small recovery record dominate storage, not inference.
- **security:** Use a cryptographic proximity lease, not Bluetooth RSSI alone, and require a short stable absence window to prevent accidental locking. Never unlock solely because the pendant is nearby if the Mac session is already locked; restoration must require local Mac authentication. Do not transmit raw audio or location.
- **missing:** pendant-worn/removal signal or a dedicated capacitive/proximity sensor; signed presence lease and expiry in relay; Mac lock/private-session adapter and browser pause/resume contract; recovery-card storage that preserves task position without secrets

### "“When I am in a conversation, let me say ‘mark that’ and have the pendant save only the next ten seconds of speech locally, then ask whether to keep, transcribe, or erase it when I am alone.”"
- **useful because:** People often need to capture a fleeting name, instruction, or idea but should not record an entire room by accident. A bounded, locally held clip makes capture useful in social settings while giving the owner a clear disclosure boundary and a later private decision.
- **path:** pendant → audio → relay-realtime → mac-planner → dashboard
- **model tier:** Firmware handles the ring buffer and erase; a cheaper background model transcribes only after explicit keep. Realtime is unnecessary unless the owner asks for immediate playback.
- **latency:** Button/phrase arms capture immediately; ten-second clip closes locally. Transcription can be deferred until the owner reconnects or requests it.
- **cost:** Zero cost if erased; a few cents for transcription/summarization of a kept clip. Local flash and transfer are the main resource costs.
- **security:** Default to erase on timeout and keep the clip encrypted on the pendant. Announce an unobtrusive recording indicator, never upload automatically, and require explicit keep before server processing. This is not a covert recording feature.
- **missing:** firmware bounded encrypted ring buffer and capture latch; audio bridge command for clip finalize/playback; relay upload endpoint with erase-before-upload semantics; owner-facing keep/transcribe/erase decision flow

### "“Before I leave home, tell me what I am likely to forget based on today’s calendar and the things I normally carry, but only interrupt me when the confidence is high.”"
- **useful because:** A calendar can tell the system where the owner is going, while the pendant is the last-mile reminder surface. Combining routine patterns with the Mac’s local context could prevent forgotten badges, chargers, documents, or equipment without turning every departure into a noisy checklist.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** Cheap background model builds and updates a personal carry-pattern model; deterministic rules gate the interruption. Realtime only speaks the one or two high-confidence items.
- **latency:** Prepare asynchronously 15 minutes before likely departure; speak in under 3 seconds when the owner asks “anything before I go?”
- **cost:** A few cents per day for calendar/routine classification; most runs are local rule evaluation.
- **security:** Keep carry habits local by default, never infer sensitive destinations aloud in public, and let the owner delete learned item associations. Do not use location tracking unless explicitly enabled.
- **missing:** departure inference from calendar/Mac presence without continuous location upload; private carry-item pattern store with confidence/decay; pendant one-shot reminder delivery and dismissal state; calendar/event access normalized with owner-controlled sensitivity


## Changes it proposed to its own stack

### `relay` — Introduce a typed ActionEnvelope carried unchanged across relay, Mac, browser, and pendant: action ID, actor surface, exact arguments hash, reversibility class, required confirmation level, expiry, and result evidence requirements. Executors must reject envelopes whose hash, expiry, or approval token does not match, while the relay stores a compact append-only decision record.
- **owner gets:** The owner gets a trustworthy answer to “what exactly did you approve, and what actually happened?” instead of a vague success receipt. It also makes the physical pendant approval and panic revocation enforceable rather than conversational promises.
- effort: Medium: shared schema, relay validation, adapters in Mac/browser executors, and a small receipt viewer.  ·  risk: Older clients may omit fields or become unable to execute; support a versioned envelope and fail closed only for sensitive actions. If evidence capture fails, report unverified instead of claiming success.
- cost: Negligible storage and compute; one short hash/receipt per action. No model call required.  ·  latency: Adds milliseconds of hashing/validation; no perceptible conversational delay.
- security: Strongly improves replay resistance and cross-surface authorization. Hash only canonicalized arguments and avoid storing sensitive payloads in the append-only record.
- depends on: pendant challenge-response approval; relay device-revocation epoch; typed result/evidence adapters for Mac and browser


## What it asked for

### `s10-gufl` (skill) — offline_privacy_panic_wipe
- does: A deliberate five-second button hold enters a local panic state: stop microphone capture, discard queued PCM and generated audio, revoke/rotate locally cached auth material, emit a red LED pattern, and persist only a tiny revocation epoch so the relay/Mac can invalidate remote sessions on reconnect. A short press after recovery acknowledges the state but cannot restore erased data.
- must be on-device because: Loss, theft, or a disconnected USB/LTE link is exactly when the action must still work. The firmware is the only surface physically in the owner's hand and can erase local data before any network round trip.
- trigger: Five-second continuous button hold, with LED progress and a second release confirmation; must be cancellable before release. Also expose a server-requested wipe event for a remotely declared loss.
- storage: Persist one 32-bit revocation epoch, one panic-state byte, and a monotonic event counter in nonvolatile storage (well under 128 B). Erase audio/application queue files and invalidate in-RAM credentials; do not retain content.
- RAM budget: Approximately 2–4 KB for debounce/progress state, wipe bookkeeping, and command parsing; no model or audio buffering beyond existing buffers. Must fit within the 211,608 B application RAM budget.

## Its own summary

Round 136 produced three new owner-facing capabilities: a physical pendant approval gate for sensitive actions, an offline lost-device panic wipe/session revocation path, and a synchronized privacy/focus mode across pendant, relay, Mac, and browser. I also proposed the typed ActionEnvelope needed to make approval hashes, expiry, evidence, and revocation enforceable, and queued the firmware skill for the five-second offline wipe. What remains is implementation: signed pendant challenge-response, relay revocation/approval endpoints, executor enforcement, notification/watch pause semantics, and a compact owner-visible recovery/approval history. The current perception is still that Accessibility/Screen Recording are unavailable and Gmail frame access is untrusted, so these designs deliberately fail closed rather than claiming actions happened.

**Biggest unknown:** Whether the pendant firmware currently has a secure nonvolatile credential/epoch region and a reliable long-press/LED timing path; that determines whether panic wipe can be shipped without a firmware storage-layout change.

