# Harness derivation — faculty-judgement — round 240

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Give me a morning briefing I can trust: tell me what you actually checked, never call an unreadable source 'clear,' and only count an item as delivered when I really heard it."
- **useful because:** Today a denied EventKit read can become 'calendar is clear,' the briefing scheduler is not running, and server-side completion does not prove pendant playback. This closes the loop from source health through judgement to physical delivery, so the owner gets an honest brief or an explicit incomplete/retry state rather than confident fiction.
- **path:** relay → mac-planner → browser → pendant
- **model tier:** background for source gathering and cheap deterministic checks; realtime only for the spoken summary and owner follow-up
- **latency:** Prepare by the configured morning time; source reads may take up to 2 minutes, with a concise spoken result within 3 seconds once ready. Retry missing sources in the background rather than blocking speech.
- **cost:** Low-to-moderate: one background synthesis call per briefing plus existing Mac/browser reads; delivery verification and completeness checks are deterministic and dominate no model cost.
- **security:** Speak only the selected, redacted items after the attention policy permits it. A missing permission must be reported as unreadable, never interpreted as empty. Keep evidence references and source-health metadata in the receipt, not raw mail/calendar bodies in the relay. Require explicit owner policy for whether private content may be spoken; conservative default is queue or title-only.
- **missing:** A real scheduler invocation for briefing triage/morning brief (the policy route exists but nothing fires it); An authoritative EventKit calendar/reminder permission probe or the existing empty-pair corroboration wired into every briefing reader; A production implementation of attention_arbitrate and a durable decision receipt; A production consumer for pendant delivery ACKs that marks an item heard only after playback_finished and handles interruption/retry

### "If I ask you to do something on my Mac and the laptop sleeps or the browser disconnects, keep ownership of the task, recover it when the surface returns, and tell me exactly whether it finished, was retried, or needs me."
- **useful because:** A delegated job can remain permanently 'processing' after a Mac crash because relay jobs have no lease or requeue sweep. The owner currently has to guess whether an action happened and risks asking twice. A durable lease with idempotent recovery turns dropped connectivity into a transparent delay instead of lost work or duplicate side effects.
- **path:** relay → mac-planner → browser → pendant
- **model tier:** Cheap deterministic relay worker for leases, retry classification, and receipts; use the realtime model only when a human-readable explanation or ambiguity needs resolving.
- **latency:** Immediate acknowledgement; reclaim an orphan after a short lease (for example 2–5 minutes), then retry only idempotent/reversible steps. Escalate to the pendant on the next available connection; never hold the owner waiting synchronously.
- **cost:** Very low model cost; storage and periodic relay sweeps dominate. A single explanation call is needed only for a non-classifiable failure.
- **security:** Lease ownership must be scoped to the exact job and step, with fencing tokens so an old Mac cannot continue after reassignment. External or destructive actions must not auto-retry; route them to a pending approval/revalidation state. Receipts must distinguish attempted, committed, and merely prepared, and expose provenance without leaking page contents.
- **missing:** relay_jobs lease_until, attempt/fencing fields, and a requeue sweep modeled on the working routine lease; A durable relay-job-id to Mac-job-id mapping (currently only telemetry localJobId); Step-level idempotency and a receipt that records committed versus attempted effects across Mac and browser; A relay worker or reconnect hook that claims requeued jobs when the Mac/browser comes online

### "Before I rely on you today, run a readiness check: tell me whether the pendant, relay, Mac, browser session, permissions, scheduled briefings, and outstanding jobs are actually usable, and give me one concrete repair for each problem."
- **useful because:** The system exposes these facts in separate places and several reports are dangerously optimistic: calendar denial can look like an empty day, browser lease sweeping is not started, and relay/Mac connectivity and audio delivery are not joined. The owner needs a single truthful go/no-go answer before entrusting the system with a deadline, not a tour of status endpoints.
- **path:** pendant → relay → mac-planner → browser
- **model tier:** Deterministic probes and provenance-backed rules for the readiness verdict; background model only turns failures into a prioritized human plan. Realtime is reserved for the short spoken result.
- **latency:** Under 10 seconds for the common path, with bounded parallel probes. Slow permission or browser checks become 'unknown—checking' and finish asynchronously; never turn a timeout into ready.
- **cost:** Very low: parallel HTTP/device probes and deterministic classification; at most a small synthesis call for the spoken repair list.
- **security:** Return capability and freshness metadata, not page contents, mail bodies, or credentials. Separate unavailable, unauthorized, stale, and healthy states. Any repair that mutates settings, cancels jobs, or changes schedules must be staged and owner-confirmed; diagnostic reads are safe by default.
- **missing:** A unified readiness schema with freshness, provenance, and explicit unknown versus healthy states; An actual live pendant/relay registration and authenticated device-health surface (USB bench presence is not shipping LTE availability); A scheduler/lease supervisor health signal for briefing and delegated jobs; A single repair planner that maps each failed check to a reversible, owner-approved action


## Changes it proposed to its own stack

### `hardware` — Add a low-power wear-state channel to the next pendant revision: a capacitive skin-contact electrode in the enclosure (with an IMU fallback for worn-versus-resting classification), sampled locally and reported as a signed coarse state {worn, probably_worn, resting, unknown}. Make the audio path fail closed for private speech when state is resting or unknown; do not transmit raw sensor traces. Expose hysteresis and an owner override only through the existing physical approval mechanism, not voice alone.
- **owner gets:** The pendant could know whether it is actually on the owner's body instead of guessing from an unavailable 'wearing' signal. Private reminders and confirmations would stop being spoken into a room after the owner takes it off, while ordinary queued alerts could still wait safely. This is a new physical boundary, not another timing preference or server-side privacy promise.
- effort: New pendant PCB/enclosure electrode, analog front end or capacitive-sense controller, firmware calibration and signed state frames, relay/Mac policy integration, and testing across clothing, skin tones, charging surfaces, and pocket placement. The current nRF9160 board and ESP32 audio bridge have no wear sensor, so this cannot be enabled by firmware alone.  ·  risk: False resting could suppress useful speech; false worn could expose private speech. Fail closed on uncertainty, provide a nonverbal LED indication, and let the owner deliberately override for one item with the existing physical approval latch. Sensor data must not become a retained behavioral history.
- cost: Roughly $2–$8 BOM increase plus PCB/enclosure revision; negligible average power for capacitive sensing, with short IMU bursts if used. No per-invocation API cost.  ·  latency: Under 100 ms to update state locally; require a short hysteresis window (about 1–2 seconds) to avoid transitions while handling the pendant. No model round trip on the speech path.
- security: Improves local disclosure safety but is not proof of privacy: a worn pendant can still be overheard. Signed coarse state prevents a stale relay claim from authorizing private speech; no raw capacitance, motion, or location leaves the device.
- depends on: A policy table that distinguishes private speech from public/normal alerts and names the fail-closed behavior; An audio-output enforcement point before every pendant synthesis/download, not only briefingTriage; A signed state field carried through relay-to-pendant audio envelopes; Owner-facing indication and the existing physical approval path for one-shot overrides


## What it asked for

_Nothing._
## Its own summary

This round produced three non-duplicate owner capabilities: (1) a source-complete, playback-verified morning briefing that never treats unreadable data as clear; (2) lease-based recovery and truthful status for delegated Mac/browser jobs after sleep or disconnect; and (3) a cross-surface readiness check that gives a go/no-go answer and one repair per failure. I also attempted source-wide forgetting, but the recorder correctly identified it as an existing backlog idea rather than restating it.

**Biggest unknown:** The remaining product decisions are owner policy values, not more infrastructure discovery: which content may be spoken aloud, what counts as urgent, and which destinations are trusted. Technically, the largest unknowns are whether the granted arbiter/delivery tools are actually wired in production and whether the pendant has a live authenticated LTE health surface; current hardware is USB-bench-only, not shipping transport.

