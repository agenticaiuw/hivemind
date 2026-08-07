# Harness derivation — faculty-judgement — round 66

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“For anything important, have two independent parts of my system agree it happened—or keep it pending and bring me the disagreement.”"
- **useful because:** A single receipt, DOM click, or UI observation can be falsely positive. An evidence quorum makes high-stakes personal actions dependable: for example, a Mac calendar write is checked by Calendar readback plus a durable job record; a browser submission is checked by the confirmation page plus a later authenticated record. The pendant tells the owner 'confirmed by two sources' or 'pending: sources disagree,' never silently upgrading an attempt to truth.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Cheap deterministic quorum rules first; background planner only resolves entity matching or semantic disagreement; realtime speaks the concise result and asks for help only when the conflict cannot be resolved. No expensive model for routine matching.
- **latency:** Local two-source checks <1 s; browser/account confirmation 3–10 s. The pendant can say 'still checking' immediately, then deliver a result asynchronously through relay when the owner walks away.
- **cost:** <$0.002 typical (mostly two local/browser reads); planner escalation 2–4k tokens only for ambiguous semantic conflicts. Storage is small: signed evidence pointers, hashes, timestamps, and a bounded disagreement record.
- **security:** Sources must be genuinely independent (not two views of the same untrusted click result). Store hashes and minimal excerpts, not whole private pages. For money, messages, deletion, or external submissions, quorum confirms outcome but never replaces owner approval. Expose the exact sources, freshness, and missing witness in the dashboard and spoken response.
- **missing:** A typed evidence-witness and independence model (source, claim, timestamp, freshness, confidence, correlation group); Per-action quorum policies by consequence class, with a safe pending state and expiry rather than auto-retry; Cross-surface disagreement records and a repair workflow that can request a fresh read without repeating the write; Pendant/relay protocol for announcing pending, confirmed, and disputed outcomes after link loss

### "“When I actually leave home, give me a two-minute departure check tailored to where I’m going—only interrupt me for something I can still fix, and keep the rest queued.”"
- **useful because:** A scheduled morning briefing arrives at the wrong moment and a generic meeting brief does not know whether the owner has physically started leaving. This would connect the wearable’s real-world transition with the Mac’s live commitments and private browser context: catch the forgotten badge, medication, document, or travel change while there is still time to act, without turning every reminder into noise.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheap event classifier and deterministic checklist first. Use a background planner to combine calendar, travel, and unfinished-job facts; reserve realtime for one concise, interruptible spoken alert.
- **latency:** Detect departure within 10–30 seconds; produce a first actionable check within 5 seconds of the event. Anything requiring authenticated browser reads can arrive asynchronously, with no blocking of movement.
- **cost:** Usually <$0.003 per departure, dominated by one planner call and private-account reads; deterministic local checks should be free. Battery and cellular sensing are the main non-API costs.
- **security:** Location and routine inference are highly sensitive. Keep raw location on the pendant or Mac, send only a coarse transition and destination class to relay, and make the feature opt-in with per-place quiet rules. Never announce sensitive calendar or health details aloud when others may be present; require confirmation before sending or changing anything.
- **missing:** A reliable departure-event source: pendant motion/proximity/GNSS or a paired-phone geofence, with local privacy filtering; A destination and time-window resolver joining calendar, travel, tasks, and unfinished cross-surface jobs; A ranked 'still fixable before leaving' checklist with expiry and quiet/social-context rules; A low-interruption pendant interaction for dismiss, defer, or ask-for-more without opening the Mac


## Changes it proposed to its own stack

### `integration` — Build a consequence-classified evidence-quorum coordinator between planner, Mac executor, browser bridge, journal, and pendant relay. At plan time it assigns each write a policy (single witness, dual independent witnesses, or owner-only); at runtime it records claims as requested→attempted→witnessed→confirmed/disputed/expired, groups correlated witnesses so two copies of one receipt do not count, and triggers read-only alternate-surface checks after a write. A dispute creates a durable repair ticket without replaying the write. Relay/pedant receive compact pending/confirmed/disputed events; dashboard shows each witness and freshness.
- **owner gets:** The owner stops having to remember whether 'done' meant a button was clicked, a receipt was issued, or the real-world result exists. Important actions either become independently confirmed or remain visibly pending with a safe explanation; dropped links and unavailable Mac permissions no longer turn uncertainty into a false success.
- effort: Medium-high: shared claim schema and policy registry, adapters for file/app/browser/calendar/mail outcomes, durable state transitions, event delivery, and adversarial tests for correlated evidence and duplicate writes.  ·  risk: Extra reads can expose sensitive state or delay completion; enforce least-privilege scopes, TTLs, redacted evidence, and per-action policies. A stale witness could falsely confirm, so every witness carries timestamp/freshness and source independence. Recovery is read-only recheck or owner review, never blind retry.
- cost: <$0.002 typical in model/API cost; two readbacks increase Mac/browser traffic and small durable storage. Planner escalation only for semantic entity matching.  ·  latency: Adds <1 s for local checks and 3–10 s for authenticated browser checks; immediate pendant acknowledgement remains available while confirmation is pending.
- security: Improves integrity but centralizes evidence metadata. Encrypt/redact excerpts, retain hashes/pointers only, and require owner approval for external side effects regardless of quorum.
- depends on: A typed evidence-witness schema and consequence policy; A durable cross-surface event/claim store; Adapters for readback of Mac and browser outcomes; Pending/dispute states in relay and pendant protocol

### `hardware` — Add a low-power IMU and privacy-preserving local presence/departure detector to the wearable, with optional BLE proximity to the owner's phone or a home beacon and coarse GNSS only when explicitly enabled. Emit only state transitions such as HOME, LEAVING, ARRIVED—not raw traces—to the relay. Add a long-press gesture for 'quiet this departure check' and a short press for 'tell me the next item.'
- **owner gets:** The pendant would know when a real transition is happening instead of delivering a calendar briefing at an arbitrary scheduled time. The owner gets timely, location-relevant help during the small window when a forgotten item or changed reservation can still be fixed, without surrendering a continuous location history.
- effort: Medium hardware and firmware change: select an IMU/BLE beacon strategy, implement local state classification and calibration, add encrypted transition events and battery testing, then integrate destination resolution and checklist ranking on the Mac/relay.  ·  risk: False departures could cause nuisance prompts; require hysteresis, confidence thresholds, and a dismiss cooldown. GNSS and proximity data could reveal routines; default to local coarse states, disable raw logging, and provide a physical privacy mode. If the sensor fails, scheduled and manual checks continue unchanged.
- cost: Roughly $3–10 BOM increase for IMU/proximity hardware, plus firmware and battery tuning; likely tens of milliwatts peak and negligible average draw with duty cycling. No meaningful per-event model cost beyond the capability's planner/read costs.  ·  latency: Local transition classification in under 1 second; BLE/proximity transition typically under 10 seconds. Cellular/GNSS fallback may add 10–30 seconds and should not block the owner.
- security: Reduces data leaving the device by sending transitions rather than coordinates, but adds a sensitive routine signal. Encrypt events in transit and at rest, enforce short retention, and make privacy mode visible through LED/button feedback.
- depends on: A pendant firmware event channel and durable relay event schema; Destination/time-window resolver across Mac and authenticated browser; Owner-configurable quiet hours, places, and spoken-content privacy policy


## What it asked for

_Nothing._
