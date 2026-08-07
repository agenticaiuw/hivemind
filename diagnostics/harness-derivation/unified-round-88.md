# Harness derivation — unified — round 88

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I walk away and come back, let me say “where were we?” and hear the exact unfinished thread: what I said on the pendant, what the Mac/browser already found or changed, what still needs my approval, and a one-tap/one-press way to resume it."
- **useful because:** Today a dropped link, closed laptop, or interruption strands work across surfaces. This would make the pendant a reliable continuity point: it preserves intent and evidence without replaying private page contents aloud, and resumes only from a known checkpoint rather than guessing.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use the cheap background model to compact completed steps and evidence into a handoff manifest; use realtime only for the brief spoken “where were we?” exchange and approval clarification. Mac/browser agents execute resumed reversible steps; relay persists and reconciles the manifest.
- **latency:** Return a spoken continuity summary in under 2 seconds from relay state; refreshing stale Mac/browser evidence may take up to 10 seconds and must be labeled as a refresh. Resume should wait for explicit confirmation at any external side effect.
- **cost:** About $0.002–$0.01 per handoff/resume, dominated by a small background summarization and any refreshed browser extraction; no model call is needed for a simple status lookup.
- **security:** Persist intent, step state, hashes, and source references—not raw private page text or audio by default. Require the pendant button/voice confirmation for sending, purchasing, deleting, or submitting. Expire stale evidence and invalidate approval if the tab, value, recipient, or source hash changes. Spoken summaries should redact secrets and private page contents unless explicitly requested.
- **missing:** A durable cross-surface handoff-manifest schema with step checkpoints, evidence hashes, expiry, and approval invalidation; A local pendant moment-marker/checkpoint buffer and resume gesture (the requested moment_marker_buffer and task_checkpoint_gesture are still pending); A defined interruption/urgency and privacy policy (owner context is still needed); A relay API that can atomically attach Mac/browser receipts to a pending handoff and expose it to realtime audio

### "For the next hour, handle routine incoming requests for me within rules I say out loud—triage them, draft replies, and suggest calendar changes—then bring me only exceptions or anything that would commit me."
- **useful because:** The owner gets temporary, bounded delegation instead of either micromanaging every notification or granting an unsafe permanent automation. The worn pendant defines the scope and expiry; the relay keeps working if the Mac sleeps; Mac and private browser sessions inspect the owner’s actual accounts; the owner approves only exceptions and commitments.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheap background model for classification, rule matching, and draft preparation. Use realtime only to capture the spoken delegation scope and answer exception questions. Use the local Mac/browser agents for authenticated reads and reversible draft/calendar preparation.
- **latency:** Acknowledge the delegation locally in under 2 seconds. Process routine arrivals asynchronously within a few minutes; surface urgent exceptions within 30 seconds when the link is available. Never wait for model completion before enforcing the expiry locally at the relay.
- **cost:** Approximately $0.01–$0.05 per hour-long delegation window, dominated by periodic authenticated-page/message extraction and draft generation; simple rule checks and expiry are nearly free.
- **security:** The spoken scope must compile into an explicit allowlist (people, accounts, actions, time window, spending/calendar limits), shown on the dashboard and summarized back by audio. Never send, purchase, delete, accept an invitation, or make a binding commitment automatically. Store drafts and evidence encrypted with short retention; revoke immediately on a second button press or spoken stop; reject stale or changed page state. Private browser content must stay on the Mac/browser bridge and relay should receive only normalized fields needed for triage.
- **missing:** A capability-lease primitive shared by relay, Mac, and browser, with monotonic expiry, revocation, and an auditable scope hash; An event intake connector for new Mail/Messages/calendar/browser notifications that can wake the relay without polling every page; A policy compiler that turns spoken limits into typed action classes and routes uncertain items to an exception queue; Owner-defined defaults for who counts as routine, acceptable calendar moves, quiet hours, and escalation urgency


## Changes it proposed to its own stack

### `hardware` — Add a tiny ERM/LRA haptic actuator with a dedicated low-side driver and one capacitive or side button to the pendant revision; expose a three-level tactile vocabulary (acknowledged, needs approval, urgent) and wake/interrupt input. Keep the existing button and LED semantics unchanged, and drive haptics from a local queue so the relay can signal even when audio is half-duplex or the owner is in a noisy place.
- **owner gets:** They can notice an urgent browser/Mac result or approval request privately in a meeting, confirm that a command was received without speaking, and distinguish “finished” from “you must decide” by touch rather than staring at the LED or replaying audio.
- effort: Pendant PCB/mechanical revision, driver firmware, relay event mapping, and a small end-to-end test matrix for LTE loss, audio playback, and button races; moderate hardware effort plus one firmware release.  ·  risk: Motor noise can leak into the I2S microphone, false wakeups can drain power, and a stuck driver could buzz continuously. Use a hardware current limit, max-on watchdog, physical mute/disable in firmware, acoustic isolation, and fall back to the existing LED/audio path. Validate with the one existing I2S full-duplex peripheral rather than adding another audio device.
- cost: Roughly $2–$6 in parts and under 20 mA peak while vibrating (typically under 1 mA average at a few short pulses); no per-invocation API cost.  ·  latency: Local acknowledgement under 50 ms; relay-originated alerts remain link-limited and should be queued when LTE-M is unavailable.
- security: Haptic patterns reveal only urgency class, not message content; do not encode account or secret data. Require the existing button/voice confirmation for irreversible actions.
- depends on: A relay-to-pendant event channel with authenticated, replay-protected event IDs; The pending attention_queue_indicator/local_privacy_latch policy work; A defined owner interruption and urgency policy

### `relay` — Introduce a signed, append-only Capability Lease protocol. A lease contains principal, allowed surfaces, typed action classes, resource/account selectors, spending/time limits, expiry, revocation counter, and scope hash. The relay validates every Mac/browser job and pendant-originated request against the lease; agents attach the lease ID and scope hash to every receipt; any mutation of scope or revocation invalidates outstanding work atomically.
- **owner gets:** They can safely say “you may handle these routine things until 5” and trust that the permission really ends, even if a job is still queued, the Mac reconnects later, or a browser tab changes. It gives them an understandable audit trail instead of hidden standing access.
- effort: Implement D1 lease and revocation tables, signed tokens, middleware in /plan, /execute, browser command submission, and job workers, then add pendant start/stop/expiry UX and receipt display. Add crash/reconnect and clock-skew tests across relay and Mac bridge.  ·  risk: A validator bug could over-authorize or strand legitimate work. Default deny, short leases, monotonic server expiry, an emergency global revoke, and compatibility mode that permits read-only status but no mutations provide recovery. Key rotation and replay protection are required.
- cost: Negligible API cost; a few D1 reads/writes per job and roughly 1–3 KB metadata per lease/receipt. Engineering effort is substantial because all action ingress paths must share the validator.  ·  latency: Approximately 5–20 ms for a cached lease check; a cold D1 check may add under 100 ms. No extra model latency.
- security: Strongly improves least privilege and auditability, but introduces signing keys and a high-value authorization validator. Keep private page content out of leases, rotate keys, bind leases to authenticated owner/device identities, and log denials without sensitive payloads.
- depends on: A typed policy/action taxonomy shared by Mac and browser harnesses; A durable relay event/job identity and receipt linkage; Pendant-local stop/revoke handling that works during a dropped LTE link


## What it asked for

_Nothing._
## Its own summary

Discovered the live fleet and hardware, then recorded two new pieces: a resumable cross-surface handoff capability (pendant/relay/Mac/browser with evidence-hash checkpoints and approval invalidation) and a hardware revision adding discreet haptic urgency/approval signals. The current Mac bridge is online, but home Chrome is offline, so browser execution cannot be verified live this round.

**Biggest unknown:** The owner’s interruption/privacy/urgency policy and production pendant constraints remain unspecified; implementation also still needs a durable handoff-manifest plus authenticated relay-to-pendant event channel. The orchestrator’s granted category reports zero items, so no newly visible grant can be confirmed from discovery.

