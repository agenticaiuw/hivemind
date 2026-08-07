# Harness derivation — faculty-judgement — round 104

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“When I make an important decision, remember what I expected, then later tell me whether reality matched—and what I should learn.”"
- **useful because:** The assistant currently helps choose and execute, but forgets the quality of the choice once the job receipt is closed. A private decision scorecard would turn calendar/mail/browser outcomes and the owner's own follow-up into learning, without pretending hindsight was foreseeable. It is useful for travel choices, purchases, work commitments, and recurring technical bets.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Background model for extracting options, assumptions, and measurable forecasts; realtime only for the owner's short capture and later spoken summary. Use deterministic matching and receipts before asking a model to interpret outcomes.
- **latency:** Capture acknowledgement under 1 second when spoken into the pendant; background scorecard compilation under 2 minutes; review reminder is scheduled and can wait until the next connected period.
- **cost:** Roughly $0.01–$0.08 per decision lifecycle, dominated by one extraction pass and one outcome synthesis; deterministic event matching should be free and avoid repeated context resend.
- **security:** Decision records can expose health, finances, or work plans. Keep raw audio local/short-lived, store a redacted structured record, encrypt it, and never use private browser content outside the specific record. Outcome collection must be read-only; ask before sending anything or changing a calendar/task. Show provenance and let the owner delete/export a record.
- **missing:** A durable decision_record schema containing options, chosen option, assumptions, confidence, expected observable outcomes, review date, sensitivity, and provenance; An outcome collector that correlates later Mac events, authenticated browser reads, calendar/mail changes, and owner corrections without broad surveillance; A scoring/review worker with explicit uncertainty and a dashboard/pendant review card; A user-facing delete/export and correction flow, plus a policy for records that should never leave the Mac

### "“Help me run a small, reversible experiment on my life or work, then tell me whether it actually helped.”"
- **useful because:** The owner gets evidence about habits and workflows instead of generic advice: define one change, a baseline, a success measure, and a stop date; collect only the signals they approve; ask brief pendant check-ins; and compare before/after with uncertainty. This is not a reminder, task list, or decision log—it closes the loop on whether a change caused a benefit.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheaper background model to design the experiment and summarize results; use realtime only for the owner's brief setup/check-ins. Deterministic local aggregation should handle timestamps and metrics before any model sees them.
- **latency:** Setup should take under two minutes conversationally; check-ins under 10 seconds; collection runs asynchronously for the chosen period; final report is ready within five minutes of the stop date.
- **cost:** About $0.03–$0.20 per experiment, dominated by setup and final synthesis; local metric aggregation and scheduled checks should be effectively free.
- **security:** Behavioral data can reveal health, work performance, and private browsing. Require explicit per-signal consent, default to local Mac aggregation, send only derived counts/means to relay, pause collection on request, and show every source used. Never infer sensitive traits or change routines automatically; experiments involving purchases, messages, or health require confirmation and may be disallowed.
- **missing:** An experiment_spec record with baseline window, intervention, metric definitions, consented sources, cadence, stop date, and success threshold; A local metric adapter on Mac for approved calendar, app, file, and browser signals, with privacy-preserving aggregation; A pendant check-in schedule that survives link loss and queues answers for later sync; A before/after analysis worker that reports confounders, missing data, and uncertainty rather than claiming causation; A dashboard to pause, edit, delete, and export an experiment


## Changes it proposed to its own stack

### `firmware` — Make the audio path capability-negotiated end to end instead of labeling every stream as 16 kHz: add a boot/session AudioProfile (capture_rate, codec_rate, frame_ms, bitrate, clock_source, effective_rate), validate the I2S clock and Opus encoder against it, and emit the negotiated profile plus underrun/overrun counters in each pipeline receipt. For the owner's requested 24 kHz superwideband mode, first change the nRF9160 I2S capture clock and microphone configuration to a real 24 kHz-compatible rate; if the current mic/driver cannot sustain it, reject the profile and explicitly fall back to 16 kHz rather than silently resampling or mislabeling. Relay and playback must preserve the profile and expose a short spoken 'wideband unavailable/fallback' diagnostic.
- **owner gets:** The owner gets honest, consistently higher-fidelity speech when the hardware can provide it, and a clear explanation when it cannot. Today the documented capture rate is 15,625 Hz while uplink claims 16 kHz, so a nominal '24 kHz' switch could produce misleading audio and difficult-to-debug failures.
- effort: Medium-high: firmware I2S/clock and Opus changes, relay schema/versioning, playback negotiation, and hardware-in-loop recordings across LTE-M conditions.  ·  risk: A bad clock profile can produce silence, drift, or modem stalls. Keep the old profile as a signed default, gate 24 kHz behind a lab/device capability flag, persist the last known-good profile on microSD, and automatically roll back after underrun thresholds. Verify with captured sample-rate markers and end-to-end spectral tests.
- cost: No per-call model cost; modest firmware work. Possible microphone/clock hardware revision if the current I2S mic cannot run 24 kHz, roughly $5–$20 prototype BOM impact and negligible steady-state power change, though LTE-M airtime/bitrate may increase energy use.  ·  latency: A 24 kHz profile at the same frame duration should not materially change conversational latency; higher bitrate may add LTE-M transmission time and battery drain.
- security: Audio remains sensitive. Put profile/counters in authenticated metadata, do not include raw audio in diagnostics by default, and retain recordings under the existing short-retention policy.
- depends on: Confirm the actual microphone-supported sample rates and nRF9160 I2S clock limits; Implement the pending 24 kHz audio acceptance criteria and relay profile propagation; End-to-end pendant/relay playback test with a real connected pendant

### `memory` — Add an experiment ledger whose only durable records are a consent receipt, metric definitions, daily aggregate values, missing-data markers, and owner check-in answers. Keep raw calendar/browser/app events on the Mac; have a local reducer emit signed aggregates with source/time windows, and let the relay retain only the experiment's derived series until its expiry. The analyzer must distinguish correlation from causation and refuse a conclusion when baseline or compliance is insufficient.
- **owner gets:** They can learn whether a change helped without handing the assistant a permanent diary of their browsing, files, or routines, and can trust a report that says 'not enough evidence' instead of inventing certainty.
- effort: Medium: local reducer and consent enforcement, signed aggregate schema, relay retention/expiry, and a small analysis/reporting worker.  ·  risk: A buggy reducer could leak raw events or produce misleading comparisons. Default-deny sources, test against synthetic fixtures, expose provenance for every datapoint, and make pause/delete immediate and idempotent.
- cost: Negligible storage and no recurring model cost during collection; one inexpensive background analysis per experiment.  ·  latency: No impact on live conversation; local aggregation runs incrementally and final analysis is asynchronous.
- security: Improves privacy by keeping raw events on-device, but derived behavior metrics remain sensitive; encrypt them, apply per-experiment TTL, and require explicit source consent.
- depends on: An experiment_spec and consent model; Mac-local adapters for approved data sources; A durable pause/delete path and scheduled completion trigger


## What it asked for

_Nothing._
## Its own summary

Round 104 produced two concrete next steps. First, a genuinely new owner capability: decision outcome learning—capture an important decision's options, assumptions, confidence, and forecast from the pendant, then later reconcile read-only Mac/browser/calendar/mail evidence and give a sourced calibration brief. It needs a durable decision_record schema, outcome collector, review worker, and delete/export controls; existing plan/execute/jobs/receipts/pipeline/browser/Mac routes are connective primitives, not the feature itself. Second, I specified an end-to-end negotiated audio profile for the owner's 24 kHz goal, with honest fallback because the established hardware currently captures at 15,625 Hz while uplink is labeled 16 kHz. Still needed: confirm the microphone and nRF9160 I2S clock limits, implement profile propagation and acceptance tests, and run a real connected-pendant test. Current physical blockers remain unchanged: pendant absent and browser offline; Mac bridge is online. Accessibility/browser permissions were denied and should not be re-requested.

**Biggest unknown:** Whether the installed microphone and nRF9160 I2S path can produce a genuine 24 kHz capture stream; without that hardware/driver fact, a 24 kHz setting risks being only mislabeled resampling.

