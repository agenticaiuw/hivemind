# Harness derivation — mac-planner — round 287

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-device-status** — The Mac bridge is online, Safari has one online tab, while the nRF9160 pendant and iOS probes are offline; the pendant is therefore currently usable as a USB bench target only, not as an LTE relay endpoint.
  - evidence: discover(devices) returned home-macbook-bridge online, Safari on MacIntel online, nrf9160-pendant offline, and iOS probes offline.

## Capabilities it proposed

### "“I pressed the bookmark button while looking at this. Turn that moment into a follow-up I can actually use.”"
- **useful because:** The existing bookmark is durable, but today it is only a marker. This closes the loop: the worn device identifies the moment, the relay gathers the active Mac/browser context, and the Mac leaves the owner with a dated, reviewable action packet rather than a mysterious timestamp. It works even when the pendant is LTE-off because the Mac is the currently connected test surface.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the realtime tier only to acknowledge the button event; use a cheaper background model to summarize and extract one next action from the captured context.
- **latency:** Acknowledge locally immediately; capture context in under 5 seconds; produce the packet within 20 seconds. Never block the owner on model completion.
- **cost:** About $0.01–$0.04 per bookmark depending on captured page length; browser/page text dominates, not the short model call.
- **security:** Capture only the foreground app, active tab URL/title and explicitly bounded snippets; redact page secrets and do not submit forms. File/reminder creation is local and reviewable; sending email or mutating an authenticated site is out of scope. The owner must configure which apps/domains may be captured.
- **missing:** A relay event consumer that joins offline_moment_bookmark records to a near-time Mac/browser snapshot; A bounded context-capture policy (app/domain allowlist and redaction) rather than unrestricted page export; A first-class 'action packet' record linking the bookmark, evidence, generated task and outcome

### "“The pendant is plugged into my Mac—run the complete bench health check and tell me exactly what failed, without sending any microphone audio anywhere.”"
- **useful because:** The hardware is physically available now but LTE is not registered. A one-command bench flight check would turn an attached development pendant into a trustworthy instrument: exercise the synthetic uplink and 24 kHz playback fixture, collect counters, compare them with numeric acceptance limits, and return a plain-language pass/fail report. This catches codec, framing, clock and drop regressions before the owner relies on the device away from the Mac.
- **path:** pendant → mac-bridge → relay → dashboard
- **model tier:** No expensive realtime model is needed. Use deterministic parsing and threshold checks first; use a cheap background model only to explain a failed counter in human terms.
- **latency:** Start within 2 seconds of the request and report in under 60 seconds. The fixture itself is bounded and must be abortable by the physical button.
- **cost:** Negligible model cost (typically $0–$0.01); the dominant cost is the local test run and stored receipt, not tokens.
- **security:** The fixture must generate synthetic frames only and prove that no microphone path was opened. Accept only an allowlisted diagnostic command and a fixed serial-device identity; do not expose a general serial shell. Store redacted counters and hashes, not raw audio. Firmware flashing and arbitrary writes remain separate owner-controlled operations.
- **missing:** A narrow Mac bench-runner capability that can invoke the existing USB diagnostic trigger and collect a bounded serial log (not a general serial session); A parser/acceptance profile for the measured criteria: alias rejection, encode/decode duration, mic drops, tx starvation, clipping and silent preamble; A signed test receipt linking firmware build, fixture version, device identity and timestamp

### "“When I latch privacy on the pendant, freeze every remote action and browser command immediately; when I unlatch, show me what was held and let me resume only the safe ones.”"
- **useful because:** The local privacy latch already protects the microphone and speaker, but a remote browser command or Mac job could still continue while the owner believes privacy is active. This makes the physical latch a true cross-surface safety boundary: queued automation is halted, in-flight work is marked interrupted, no new context is captured, and recovery is explicit rather than silently replaying stale authenticated actions.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic state propagation and cancellation; use no model for the safety transition. A background cheap model may summarize held jobs after the owner asks to review them.
- **latency:** Local LED/latch state is immediate; relay fan-out target under 500 ms when connected. Offline behavior must be fail-closed for queued work, with reconciliation on reconnect.
- **cost:** Near-zero inference cost; small durable state and cancellation receipts dominate.
- **security:** The latch state must be signed or otherwise authenticated per device and monotonic against replay. Do not claim cancellation after an irreversible remote side effect; classify jobs as not-started, interrupted, or completed and surface that distinction. Never store raw page/audio context merely because a job was paused. The owner chooses whether unlatching permits automatic resumption; default should be manual review.
- **missing:** A relay-wide privacy fence consumed by the Mac job queue and browser command queue; Cancellation checkpoints and idempotency keys for in-flight Mac/browser operations, including an explicit interrupted receipt; A reconnect reconciliation protocol so the pendant's offline latch transition cannot be lost or reordered

### "“Calibrate the pendant to my actual hearing and room, then keep speech intelligible without making it painfully loud.”"
- **useful because:** The system currently has measured codec quality and bandwidth adaptation, but not an owner-specific loudness profile. A short calibration using the Mac as a controlled reference and the pendant as the worn endpoint could compensate for speaker placement, hearing sensitivity and ordinary room noise. The result would be intelligibility and comfort, not merely a codec pass.
- **path:** pendant → mac-bridge → relay → dashboard
- **model tier:** Use deterministic tone-level and speech-in-noise scoring for calibration; use a cheap background model only to convert the measurements into a simple comfort profile.
- **latency:** A one-time calibration should take 3–5 minutes and then apply locally at call start within 100 ms. It must be repeatable without sending microphone recordings off-device.
- **cost:** Negligible inference cost; a few calibration sessions produce small numeric profiles.
- **security:** Calibration audio should be synthetic or pre-approved test speech. Persist only thresholds and profile parameters, never raw microphone data. The owner must be able to delete the profile and revert to the factory curve.
- **missing:** A firmware calibration mode that emits tagged test signals and measures local playback/capture levels; A Mac reference-level procedure with known speaker/headphone output and USB timing; A profile format and relay synchronization rule that applies gains only at packet boundaries and preserves the privacy latch

### "“When you do something in a logged-in browser for me, prove exactly what changed before you tell me it is done.”"
- **useful because:** A success message is not evidence. This would give the owner a compact before/after proof: the target identity, fields or records changed, visible confirmation, and whether the browser actually committed the action. It prevents the dangerous failure mode where an automation step reports success after only typing or navigating.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic DOM/accessibility diffs, URL and confirmation-state checks first; use the background model only to summarize the evidence in plain language. Realtime is unnecessary.
- **latency:** Generate evidence within 3 seconds after the browser reports completion; deliver a terse result to the pendant and a detailed expandable record to the dashboard.
- **cost:** Usually under $0.01 per action; evidence storage and page-diff processing dominate.
- **security:** Redact passwords, tokens and unrelated page content before persistence. Proof must never include a secret merely because it was visible in the DOM. Treat navigation-only and typed-but-unsubmitted states as distinct outcomes. Destructive or financial actions need an owner-configured confirmation policy, not an invented default.
- **missing:** A browser transaction wrapper that records pre-state, intended mutation, commit evidence and post-state under one idempotency key; A secret-aware DOM diff/redaction layer with domain-specific confirmation selectors; A pendant/dashboard receipt format that distinguishes confirmed, uncertain, interrupted and failed

### "“Before I rely on this, check whether my calendar, recent mail and the page I’m viewing agree—and tell me exactly where they conflict.”"
- **useful because:** Briefings can summarize sources, but they do not establish consistency between them. This would catch stale dates, changed meeting links, contradictory deadlines and pages that no longer match the owner’s actual commitments. The owner gets a confidence-bearing answer with quoted, redacted evidence rather than a fluent guess.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic date, URL, identifier and entity extraction first; send only the small set of candidate conflicts to a cheaper reasoning model. Reserve realtime for the owner’s spoken question and final short answer.
- **latency:** Return an initial answer in 5 seconds and a complete evidence card within 20 seconds. If a source is unavailable, say so instead of treating absence as agreement.
- **cost:** About $0.01–$0.05 per check; source retrieval and page length dominate token cost.
- **security:** Read-only by default. Scope to the active tab and an owner-selected calendar/mail window; redact message bodies and unrelated recipients. Never infer that a conflict is resolved or send an update without a separate explicit request.
- **missing:** A source-join operation that normalizes dates, people, URLs and event identifiers across Calendar, Mail and the active browser page; A contradiction result schema with evidence spans, source timestamps, freshness and unknown/unavailable states; A compact pendant presentation for multiple conflicts plus a dashboard evidence view


## What it asked for

_Nothing._
