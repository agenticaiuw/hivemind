# Harness derivation — faculty-judgement — round 49

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I have too many competing commitments—tell me what to do first, what to defer, and prepare the messages or reschedules, but don’t send anything without me.”"
- **useful because:** Today the system can collect calendar, mail, browser, and notes, but it does not make the life-level judgement when obligations conflict. This would turn scattered signals into a ranked decision with explicit tradeoffs, preserve the owner's agency, and produce ready-to-review changes rather than generic summaries.
- **path:** relay-realtime → pendant → faculty-perception → faculty-judgement → mac-planner → browser-extension → mac-terminal → relay-realtime
- **model tier:** gpt-5.6-luna for the one-time cross-source synthesis and conflict explanation; background extraction and deadline calculations should use a cheaper scheduled model; gpt-realtime-2.1 only for the short spoken clarification and final choice.
- **latency:** Under 10 seconds for an initial ranked answer from cached facts; up to 2 minutes in background to inspect authenticated calendar/mail/browser and calculate travel, preparation, and dependency constraints. Pendant interaction should remain one short question at a time.
- **cost:** Roughly $0.03–$0.15 per invocation depending on authenticated-page inspection and context size; model synthesis dominates, while local calendar/file parsing is negligible.
- **security:** Private calendar, mail, notes, and logged-in pages leave the Mac/browser only as needed for extraction. Never send mail, cancel/reschedule, or disclose sensitive details without confirmation. Show each recommendation's source, assumptions, deadline, and confidence; if data is stale or surfaces disagree, ask instead of silently optimizing.
- **missing:** A durable obligation/commitment graph joining calendar events, mail asks, browser tasks, reminders, and notes with provenance and deadlines.; A conflict evaluator that models preparation time, travel buffers, dependencies, owner priorities, and reversible versus irreversible choices.; A review packet containing ranked options, tradeoffs, draft messages/reschedule forms, and a single explicit approval boundary.; Reliable authenticated browser and Mac readiness/preflight signals so unavailable sources are disclosed rather than treated as empty.; A pendant-friendly follow-up state that remembers the unresolved decision across interruptions and offline periods.

### "“When I’m in a meeting, driving, or clearly overloaded, protect my attention: let only truly urgent things through, keep the rest moving, and show me what you deferred afterward.”"
- **useful because:** The owner currently has separate notifications, calendar entries, browser work, and pendant conversation, but no system that understands their momentary social and cognitive bandwidth. This would prevent interruptions without silently losing obligations: it would classify urgency, defer routine work, prepare reversible follow-ups, and return a compact accountability digest when the owner is available.
- **path:** pendant → relay-realtime → faculty-perception → faculty-judgement → mac-planner → browser-extension → mac-terminal
- **model tier:** Use a cheap background classifier for routine urgency scoring and context aggregation; use gpt-5.6-luna only when signals conflict or a consequential deferral needs explanation; use realtime solely for a brief spoken override such as “let this through” or “I’m free now.”
- **latency:** Local attention state should change within 1–2 seconds of a meeting, driving state, or pendant override. Routine triage can run asynchronously; the owner should receive a three-item recovery digest within 30 seconds of becoming available.
- **cost:** Approximately $0.01–$0.08 per context episode; most work is local event correlation, with model cost driven by ambiguous messages and cross-source classification.
- **security:** Meeting presence, notification content, browser titles, and possibly audio-derived state are sensitive. Process presence locally where possible, transmit only urgency features, never record meeting audio by default, and require explicit setup for driving or automatic deferral. Never send or reschedule communications without approval. Every suppressed item needs a visible reason, timestamp, and recovery path.
- **missing:** A shared attention-state signal combining pendant interaction, calendar meeting presence, Mac focus/activity, and optional owner-declared driving or deep-work mode.; A durable notification/obligation holding queue with urgency, expiry, dependencies, and an unmissable escalation path.; A policy engine that distinguishes interruption-worthy emergencies from merely important work and learns only from explicit owner corrections.; Cross-surface deferral actions that can save drafts, create reminders, and preserve browser task state without submitting or sending anything.; A post-state-change accountability digest with proofs that nothing was silently dropped.

### "“Before I say yes to a new commitment, tell me whether I can realistically keep it, what it will displace, and give me a smaller promise I can safely make instead.”"
- **useful because:** People routinely agree in conversation before checking calendars, preparation time, travel, existing promises, or recovery time. The owner should get an immediate, humane feasibility check rather than discovering the conflict later. This is not an auto-scheduler: it explains the tradeoff and offers wording that preserves trust without overcommitting.
- **path:** pendant → relay-realtime → faculty-judgement → faculty-perception → mac-planner → browser-extension → mac-terminal
- **model tier:** gpt-realtime-2.1 for the immediate spoken feasibility check when the owner asks; a cheaper background model can calculate calendar capacity, dependencies, and preparation estimates. Escalate to gpt-5.6-luna only for conflicting evidence or sensitive relationship wording.
- **latency:** A first answer in under 5 seconds from locally cached commitments, with a deeper cross-surface check in under 30 seconds. The owner must be able to say “tentative” and continue without blocking the conversation.
- **cost:** About $0.01–$0.06 per check; context retrieval and calendar arithmetic dominate less than model reasoning over ambiguous commitments.
- **security:** The system may process private conversations, contacts, calendar details, and work tasks. Default to explicit invocation or a physical pendant gesture, avoid continuous recording, minimize names and content sent upstream, and show which commitments caused the warning. It must never contact the other person or add a binding event without confirmation.
- **missing:** A lightweight commitment-intent signal from the pendant, such as “can I promise this?” plus an optional duration/deadline capture.; A capacity model that includes preparation, transit, recovery, deadlines, and uncertainty rather than counting only empty calendar slots.; A safe alternative generator that produces bounded promises and draft wording without sending it.; A durable record of accepted, declined, and tentative commitments with provenance and owner corrections.; A fast local cache of the owner's current commitments so the check works during a dropped relay connection.


## Changes it proposed to its own stack

### `hardware` — For the product revision, replace the prototype nRF9160-plus-ESP32 audio chain with a wearable SoC/audio front end that can capture native 24 kHz mono and run Opus encode/decode concurrently with modem work, or add a small audio DSP. Keep the relay's 24 kHz packet contract, but stop upsampling 15.625 kHz capture to claim superwideband. Validate end-to-end MOS, latency, packet loss recovery, and battery life before freezing the codec.
- **owner gets:** The owner's voice will sound genuinely clearer and more natural in both directions, especially for names and short commands, instead of only having 24 kHz playback wrapped around a narrower microphone path. It also prevents the current prototype's audio workload (about 87% of one core for simultaneous encode/decode) from causing dropped speech or sluggish interaction.
- effort: High: product audio architecture, board spin, firmware driver/codec integration, RF coexistence testing, and a field audio acceptance test. A staged prototype can first use an external 24 kHz ADC/DSP before committing to a new SoC.  ·  risk: Hardware redesign can introduce RF, driver, acoustic, and battery regressions. Recover by retaining the current nRF9160 firmware/relay codec mode as a compatibility profile and switching per-device after measured qualification; do not market the current path as native superwideband.
- cost: Prototype roughly $15–$40 additional BOM for codec/DSP, microphone, and board changes (final volume-dependent), plus engineering/NRE. Higher DSP capability may add tens of mW during calls; native hardware acceleration could instead reduce current versus the current near-saturation CPU path. API cost unchanged.  ·  latency: Potentially lower and more stable conversational latency by removing resampling and CPU contention; target <150 ms one-way audio pipeline, with a low-rate compatibility mode when radio conditions or battery require it.
- security: No new data class or cloud destination; raw audio remains on the existing pendant→relay path. New DSP firmware expands attack surface and must use signed firmware, bounded decoder buffers, and no persistent raw-audio retention.
- depends on: A measured 24 kHz end-to-end acceptance specification (capture, relay, playback, MOS, latency, loss, and power).; A relay capability/version negotiation so old pendants continue to work.; A production acoustic/RF prototype rather than treating the current development kit as final hardware.


## What it asked for

_Nothing._
