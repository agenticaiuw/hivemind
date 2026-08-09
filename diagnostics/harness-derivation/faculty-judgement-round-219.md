# Harness derivation — faculty-judgement — round 219

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Give me one morning brief that is actually trustworthy: combine my day, urgent mail, and the three most important world/US headlines, tell me what you could not read, and let me play it later without duplicating or losing it.”"
- **useful because:** The owner has several daily routines at 07:00/07:30 that currently complete independently, while calendar permission failures can look like an empty day and audio completion is not yet reconciled with playback. This would produce one honest brief, not four plausible-looking jobs, and would prove whether it was downloaded and heard.
- **path:** relay → mac → browser → pendant
- **model tier:** Background model for gathering, ranking, and citation; realtime model only for a one-sentence spoken handoff or owner follow-up.
- **latency:** Prepare within 90 seconds of the scheduled time; spoken handoff under 2 seconds; later playback starts within 1 second after the owner's press.
- **cost:** Roughly $0.03–$0.12 per brief, dominated by headline retrieval/summarization and optional TTS; deduplication and permission checks are deterministic.
- **security:** Calendar/mail contents must stay on the Mac unless the owner's disclosure policy permits otherwise. If EventKit returns an empty pair without a readable grant, say “calendar unavailable” rather than “clear.” Never speak secret-class content; require confirmation for external publication. Deduplicate by a durable brief id and item ids so a retry cannot create a second briefing.
- **missing:** A scheduler/coordinator that supersedes or coalesces the four existing morning routines; A real join between relay job id, Mac job id, brief item id, and pendant artifact id; A delivery-aware brief store that records downloaded/started/finished ACKs and marks undelivered items for catch-up; A policy value for which mail/calendar detail may be spoken aloud

### "“When I ask for the top world and US news from the last 12 hours, give me three genuinely distinct developments, not three copies of one wire story, and tell me when a headline is uncertain or has changed.”"
- **useful because:** This directly answers the owner's repeated request while solving the common failure mode of headline lists: source duplication, stale articles, and confident synthesis from a single unverified report. The owner gets a compact spoken result with a visible/clickable evidence trail and an honest uncertainty label.
- **path:** relay → browser → mac → pendant
- **model tier:** Cheap background model for clustering and temporal comparison; the realtime model only turns the final ranked items into the short spoken answer.
- **latency:** Under 45 seconds for a fresh 12-hour scan; under 2 seconds to speak the prepared result; refresh only on explicit owner request or a scheduled watch.
- **cost:** About $0.01–$0.06 per scan, dominated by fetching article pages and one small clustering/synthesis call; cache article hashes and summaries to avoid repeat cost.
- **security:** Use public research sources by default and never submit forms or log into sites just to obtain news. Retain URL, publisher, timestamp, and a short redacted evidence digest—not full article text by default. A low-confidence or single-source item should be labeled, not silently promoted.
- **missing:** A durable news-cluster record keyed by canonical event, publisher set, and observed timestamps; A source-health and freshness check that distinguishes a fetch failure from “no news”; A citation-preserving spoken renderer that can map each spoken sentence to its evidence; A deduplication policy the owner can tune (for example, two independent publishers before calling a development confirmed)

### "“Before I rely on you, tell me in one sentence whether the pendant, audio path, Mac, and browser are actually ready—and name the one thing that is not.”"
- **useful because:** Today “online” is fragmented: the Mac bridge can be online while the pendant is unregistered, browser heartbeats can be stale, audio can be queued but never played, and the pendant has no battery gauge. A single truthful readiness verdict would stop the owner from trusting a briefing or action that cannot reach them.
- **path:** pendant → relay → mac → browser
- **model tier:** Deterministic health evaluator; use the realtime model only to verbalize the already-typed verdict.
- **latency:** Under 500 ms for cached status and under 3 seconds when a fresh diagnostic probe is needed.
- **cost:** Near-zero model cost; a few local/relay reads. Diagnostics and optional UART parsing dominate CPU, not tokens.
- **security:** Return only operational facts (connected/disconnected, queue age, last ACK, permission state), never message content or credentials. Fail closed: unknown battery must be reported as unknown, not inferred. A stale heartbeat must not be presented as current.
- **missing:** A unified typed health snapshot with freshness timestamps and provenance; A pendant transport-status source for LTE registration and local battery; currently the device is USB-testable but not LTE-registered and there is no battery gauge; Automatic browser lease sweeping so stale online state cannot persist; A small readiness route that composes the snapshot and exposes the blocking reason

### "“If the environment or link makes part of your answer hard to hear, recover it automatically instead of making me ask again.”"
- **useful because:** The owner currently receives an audio artifact, but the system does not know whether playback was interrupted, checksum-failed, or intelligible in the real environment. This would turn delivery telemetry into a listener-facing guarantee: replay only the missing sentence, adapt the next encoding, and avoid repeating content already heard.
- **path:** pendant → relay → mac → browser
- **model tier:** Deterministic packet/audio-quality controller for loss, underruns, ACK gaps, and ambient-noise estimates; realtime model only regenerates a short replacement when the missing span cannot be recovered.
- **latency:** Detect a failed segment within 1 second; recovery begins within 2 seconds; no full-response regeneration unless repair fails.
- **cost:** Usually negligible; one small model/TTS call only for irrecoverable text spans. Radio retransmission and local DSP dominate.
- **security:** Use opaque artifact and sentence identifiers, never upload raw microphone recordings for quality analysis. Do not replay sensitive content automatically in a changed context; re-check the spoken-content policy before recovery. Preserve an audit trail of which spans were heard versus replayed.
- **missing:** A semantic map from spoken spans to audio packet ranges; Authenticated playback-position and interruption ACKs joined to the artifact (the current ACK primitive needs this binding); A local ambient-noise/intelligibility estimator or an explicit owner quality signal; A repair protocol that can request only missing spans and prevents duplicate playback

### "“Tell me what is on the page I am looking at, what decision it is asking me to make, and what would happen if I choose each option—without clicking anything.”"
- **useful because:** The owner can currently read or operate browser pages through separate actions, but cannot reliably obtain a concise, hands-free decision explanation grounded in the live page. This capability would make the pendant useful while the owner's eyes or hands are occupied, while keeping the action itself untouched until explicitly requested.
- **path:** pendant → browser → mac → relay
- **model tier:** Vision/language model on the browser snapshot for extraction and option comparison; deterministic policy layer strips secrets and guarantees read-only mode; realtime model speaks the final short explanation.
- **latency:** Snapshot and explanation in under 8 seconds; spoken response under 2 seconds after the page is captured.
- **cost:** Approximately $0.02–$0.15 per request depending on screenshot/vision tokens; browser extraction and redaction are the main cost drivers.
- **security:** Read-only by construction: no clicks, typing, navigation, or form submission. Never send passwords, OTPs, payment fields, or hidden page data to a model. Include the page URL/title and capture time in provenance, and say when the page changed during analysis.
- **missing:** A browser snapshot-to-pendant explanation route that guarantees no mutation actions; Reliable field-level secret detection before vision/model upload, including image-rendered secrets; A typed representation of options, consequences, and uncertainty rather than free-form prose; A stale-page recheck before any later owner-authorized action

### "“Show me exactly what you remember about me, grouped by source and expiry, and let me export or correct one fact without exposing unrelated private data.”"
- **useful because:** The owner projection currently hides details upstream, while memory is spread across facts, graph entities, evidence capsules, browser provenance, relay context, and inherited text. The owner cannot audit the actual retained state or safely correct one item. A scoped audit/export would make memory inspectable and portable without dumping the whole private store into a conversation.
- **path:** relay → mac → browser → pendant
- **model tier:** Deterministic store projection, source-link traversal, redaction, and export; a language model may summarize only after the typed records and permissions are resolved.
- **latency:** Common fact lookup under 2 seconds; full audit/export under 15 seconds; correction receipt immediately after each store confirms it.
- **cost:** Near-zero model cost for structured views; optional summaries cost less than $0.02. Disk traversal and encryption dominate.
- **security:** Require local-dashboard confirmation for full exports; spoken relay can reveal only a narrow selected fact. Encrypt exports with an owner-provided key, exclude secrets by default, and show every omitted store or unlinked copy. Corrections must preserve an auditable tombstone without retaining the old value in prompts.
- **missing:** A cross-store memory inventory with provenance, sensitivity, expiry, and last-used fields; A safe correction operation that updates or retracts all linked copies atomically; A portable encrypted export/import format with explicit inclusion scopes; A dashboard-only authorization boundary for full-fidelity inspection


## Changes it proposed to its own stack

### `hardware` — Add a low-power I2C fuel-gauge IC (for example MAX17048-class) to the pendant revision, expose its percentage/voltage through the existing device telemetry envelope, and make the relay retain the last trusted sample with an age. Do not estimate charge from modem voltage or report a percentage when the gauge is absent.
- **owner gets:** The owner can ask “what is the battery percentage?” and currently the honest answer is unavailable. A real gauge lets the system warn before a brief or conversation is lost, and lets readiness say whether the pendant—not merely the Mac—is safe to rely on.
- effort: Moderate hardware respin: add IC, I2C routing, decoupling, firmware driver, calibration across charge/discharge, telemetry schema, and a dashboard/voice display. Prototype power measurements and validate at cold/low-voltage corners.  ·  risk: Board respin and gauge drift could produce false confidence; mitigate with voltage/age validity flags, a low-battery hysteresis policy, and explicit unknown state during calibration. Firmware must continue operating if the gauge is missing or unreadable.
- cost: Approximately $1–$3 BOM increase at low volume and a few hundred µA or less depending on gauge mode; negligible API cost. Engineering and board-turn cost dominate.  ·  latency: A local I2C read is tens of milliseconds; no meaningful conversational impact if telemetry is periodic.
- security: Battery data is low sensitivity, but signed device identity and monotonic telemetry timestamps should prevent stale or spoofed health reports.
- depends on: A telemetry field carrying battery_percent, battery_voltage, measured_at, and validity; A relay/device health snapshot that reports age and unknown state; A power budget review for the live pendant board and its existing regulator


## What it asked for

_Nothing._
