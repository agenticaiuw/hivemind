# Harness derivation — browser-extension — round 22

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-extension health** — The live browser bridge is offline and has no current tab, but the persistent browser-session store still contains three stale tab bindings. A browser_navigate through POST /execute waited 45,334 ms before returning offline failure; this is a verified current defect, not merely an unavailable page.
  - evidence: GET /browser/status at 2026-08-07T09:11Z: online=false, tabId=null, tabCount=null. GET /browser/sessions lists tabIds 320512/230928/229550. POST /execute browser_navigate https://example.com returned offline failure after 45,334ms with receipt rcpt_13e8c960-9abc-4f71-8d2f-af75932633c4.

## Capabilities it proposed

### "When a watched private webpage changes in a way that matters, interrupt me on the pendant with the exact evidence, let me say “snooze” or “handle it,” and leave the full reviewable task on my Mac without sending or submitting anything."
- **useful because:** This turns authenticated page watching into an actionable alert instead of another unread briefing. The browser supplies access no other node has, the Mac preserves source evidence and prepares reversible work, the relay decides whether the owner is reachable, and the pendant gives a quick hands-free response.
- **path:** browser → mac-bridge → relay → pendant → dashboard
- **model tier:** Use a cheap background model to normalize and prioritize page diffs; use realtime only for the pendant's short interruption and intent (“snooze”/“handle it”); use the Mac planner for cross-tab preparation and evidence packaging.
- **latency:** Page diff processing can take seconds in the background. Once a threshold is crossed, relay-to-pendant delivery should begin within 2 seconds; a spoken response should be acknowledged locally immediately and fully processed within 5 seconds.
- **cost:** Low per change: one small extraction/diff model call and a short realtime turn only when the owner responds. Storage and notification delivery dominate at scale, not inference.
- **security:** Only the authenticated browser session reads page content. Send a minimized excerpt and source URL to the Mac/relay, redact secrets and volatile fields, and retain the full DOM locally with provenance. “Handle it” may fill reversible fields, but any send, submit, purchase, or deletion remains a deliberate stop-and-show step.
- **missing:** Durable authenticated page-watch definitions with semantic diff and recovery state; A relay notification channel that can target the pendant outside an active voice turn; Pendant alert intents and snooze state persisted across dropped links; A Mac review queue that binds every diff to URL, timestamp, and quoted evidence; Dashboard controls for priority thresholds, quiet hours, and watch pause/resume

### "When I say “save this private page for later,” capture the relevant section from my logged-in Safari page, turn it into a short cited audio capsule, and make it playable from the pendant even if my Mac or Safari is offline later."
- **useful because:** Today, authenticated browser information is trapped in a live Safari tab and cannot reliably follow the owner into a commute or survive closing the laptop. This would let them safely carry appointment details, instructions, account notices, or order information with source evidence, without granting any other node access to their browser session.
- **path:** browser → mac-bridge → relay → pendant → dashboard
- **model tier:** Use a background/cheap model on the Mac to extract and summarize the selected page region; use a slower speech-generation path to create the audio capsule; reserve realtime for a brief pendant playback-control conversation only.
- **latency:** Capture and summarize within 10 seconds while the page is open; audio generation can finish within a minute. Pendant playback should begin from locally cached chunks within 300 ms, including during a later Mac/link outage.
- **cost:** One small extraction/summarization call and one short TTS generation per capsule; storage and audio transfer are the main recurring costs. Replays should incur no model cost.
- **security:** Raw authenticated page content stays on the Mac/browser side and is discarded after extraction. The relay receives only an encrypted capsule, minimized quoted evidence, source URL, sensitivity label, and expiry. Capsules must have explicit TTLs, local deletion, and no transcript indexing by default; secrets such as passwords, recovery codes, and payment data must be automatically excluded. Playback or deletion is safe, but sharing or forwarding a capsule must be a separate explicit action.
- **missing:** A browser action that captures a user-selected DOM region plus stable source evidence instead of only a transient page read; An encrypted capsule store with per-item TTL, revocation, and device-bound keys; A relay-to-pendant download/cache protocol that resumes after dropped links and supports offline playback; A TTS job path for private capsules with redaction and provenance metadata; Dashboard and pendant controls for capsule list, expiry, playback, and immediate purge

### "If I lose my pendant or Mac, let me say “lock my browser” from any trusted device and immediately stop all browser commands, revoke private-page capsules, and leave Safari sessions untouched but inaccessible to the AI until I unlock it."
- **useful because:** The owner cannot currently cut off AI access to authenticated Safari sessions from the wearable or relay. This provides an emergency privacy control that works when the Mac is unattended or the pendant is separated, without logging the owner out of websites or destroying their own browser state.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** No model is needed for the lock path: use a deterministic relay control-plane command. Realtime is only needed to interpret a spoken unlock phrase; background work can reconcile queued jobs and receipts afterward.
- **latency:** The relay should set the global lock and reject new browser commands within 1 second. The Mac should cancel in-flight browser work and purge relay-held capsule material within 5 seconds of reconnecting; while disconnected, the relay lock still holds.
- **cost:** Negligible inference and API cost; a small durable lock record and key-revocation event are the main resources.
- **security:** Lock must be fail-closed for browser automation, page watches, extraction, and private capsule retrieval, while not claiming to log out Safari. Unlock requires a trusted device plus a non-replayable challenge or physical pendant gesture—not voice alone. Existing queued commands must be canceled and their results marked suppressed; preserve audit receipts without preserving page content.
- **missing:** A relay-owned browser lock with monotonic generation number and durable revocation state; Mac/browser bridge enforcement that checks the lock before polling, executing, and returning results; Pendant trusted-device identity and a physical unlock gesture; Encrypted capsule key hierarchy supporting immediate revocation; A dashboard showing lock state, affected sessions, canceled work, and unlock audit history


## Changes it proposed to its own stack

### `browser-harness` — Add an extension-lease health gate and circuit breaker around browser execution. Before enqueueing, resolve the requested device/session to a heartbeat newer than a short TTL; mark browser sessions stale when their device disappears or tabId is absent; fail offline requests immediately with a structured retryAfter/status endpoint instead of waiting the 45-second command lease. After repeated lease failures, suppress automatic page-watch retries until a fresh heartbeat arrives, then revalidate tab/session affinity before resuming.
- **owner gets:** A browser request will tell the owner within a second that Safari is unavailable instead of sounding like the system is working for 45 seconds. Stale tabs will not be mistaken for logged-in access, and page watches will stop wasting time and producing misleading failures while Safari is closed.
- effort: Moderate: browserBridge preflight and circuit state, browserSessions stale reconciliation, a small status/heartbeat contract, and tests for offline/online transitions. Complements the existing queue/progress work rather than replacing it.  ·  risk: A transient heartbeat gap could reject a request that would have succeeded; use a short grace window and allow explicit retry. On recovery, reattach only to a newly verified tab, never an old tabId. No browser data is exposed by the health check.
- cost: Negligible API cost; avoids 45-second worker occupancy and repeated failed watch invocations.  ·  latency: Offline failure drops from ~45 seconds to roughly one health-check round trip; online actions are unchanged except for a small preflight check.
- security: Positive: prevents dispatching private-page commands to stale or misidentified tabs. Heartbeat metadata remains device/session state, not page content.
- depends on: A reliable browser command queue with request IDs and resumable progress (chg-14accc01); A durable authenticated page-watch service should honor the circuit breaker (chg-e767dfc0)

### `hardware` — Design the production pendant with a low-power ERM/LRA haptic actuator and a dedicated wake-capable haptic driver, while retaining the single button and LED. Add a compact alert protocol: distinct short patterns for private-page change, completion, and offline/error; a button press acknowledges/snoozes the alert without opening a voice turn. Keep audio on the existing full-duplex I2S path and place haptics on the currently unused I2C bus.
- **owner gets:** Important private-web changes can reach the owner while the pendant is in a pocket or noisy room, and they can be dismissed hands-free from the browser workflow without requiring speech or a screen. The owner gets a genuinely wearable alert surface rather than an LED that is easy to miss.
- effort: Moderate hardware revision and enclosure/acoustic testing; firmware driver, pattern/state machine, and relay event mapping. Prototype can use an I2C haptic breakout before the product PCB.  ·  risk: Added vibration may be distracting or drain the battery; provide quiet hours, intensity limits, and a physical opt-out. A missed acknowledgment must not be interpreted as approval to send/submit anything. Recovery is to fall back to LED/audio and replay the alert on the next connection.
- cost: Roughly $1–3 BOM increase for actuator/driver plus PCB/enclosure work; tens of mW only during brief alerts, near-zero idle draw. No meaningful inference cost.  ·  latency: A locally buffered haptic pattern can start within tens of milliseconds after relay delivery; no realtime model call is needed for acknowledgment.
- security: No page content needs to be stored on the pendant; carry only opaque alert IDs and state. Haptic acknowledgment is non-destructive and cannot authorize high-impact browser actions.
- depends on: Cross-surface private page-change alert capability; Pendant event delivery and durable snooze/ack state; Battery and enclosure validation for the production wearable


## What it asked for

_Nothing._
