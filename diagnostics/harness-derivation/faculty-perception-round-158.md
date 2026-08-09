# Harness derivation — faculty-perception — round 158

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac-agent observability and permissions** — At 2026-08-08T02:34Z, GET /ops/snapshot reports local agent v0.5.0 healthy, relay reachable, browser extension online with 9 Safari tabs and 0 pending commands, and permissions.ready=true with Accessibility and Screen Recording granted for com.aipendant.agent. GET /v1/devices/status is not a Mac-agent route (404), so it cannot establish pendant registry state.
  - evidence: Authenticated GET /ops/snapshot HTTP 200; authenticated GET /v1/devices/status HTTP 404.

## Capabilities it proposed

### ""Did that actually happen while I was away, and if not, exactly where did it stop?""
- **useful because:** The current system can show a completed Mac/relay run even when no pendant is present, and browser work can be queued without execution. This gives one short, causal answer with evidence rather than a misleading completed badge.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background for reconstruction; realtime only to speak the final one-sentence verdict
- **latency:** Under 3 seconds for a recent event; up to 10 seconds for a bounded historical reconstruction
- **cost:** About $0.01–$0.04 per reconstruction; dominated by a small background model over event metadata, not audio or page bodies
- **security:** Return metadata and redacted error classes by default; never expose browser content or secrets in the spoken verdict. Require confirmation before retrying or changing anything.
- **missing:** A causal event-graph endpoint joining relay job, Mac ledger/pipeline, browser command/receipt, permissions snapshot, and (when available) pendant playback evidence; A stable correlation ID propagated across those surfaces; An explicit unknown state when the pendant is absent, rather than inferring failure

### ""Prove what I saw on that page, and tell me if it changed before you acted.""
- **useful because:** Relay browser reads currently return untrusted text with no ID, hash, or persistence, while the Mac already has content-addressed evidence capsules and grounded-claim provenance. This makes browser-based decisions auditable and prevents acting on stale or untraceable page text.
- **path:** browser-extension → mac-planner → relay → dashboard
- **model tier:** background model for hashing, redaction classification, and claim linkage; realtime only for the owner's question
- **latency:** Add less than 500 ms to a browser read when the Mac is available; asynchronous capsule upload is acceptable
- **cost:** Near-zero model cost for hash/linking; occasional small background model cost for redaction/claim classification
- **security:** Redact secrets before transport; retain only hashes and bounded snippets on the relay; respect capsule expiry/revocation; require confirmation before an action grounded only in an untrusted relay read.
- **missing:** Relay read_web_page must return a stable read ID and content hash; A relay-to-Mac transport that invokes the existing mintCapsule and recordExtraction modules; Mount browserProvenance routes, currently unmounted, and expose the linked receipt to judgement

### ""Is my pendant really connected right now, or is the Mac just pretending it is?""
- **useful because:** The live agent can currently report the Mac bridge and browser, but the pendant registry is a different service and the pendant converse path does not heartbeat. A topology verdict would distinguish USB-attached source, relay socket, stale registry, and actual playback path before the owner trusts a spoken answer.
- **path:** pendant → mac-terminal → relay → dashboard → unified
- **model tier:** No LLM for detection; deterministic state classifier, with realtime speaking only the final verdict
- **latency:** Under 1 second for cached state; under 5 seconds for a fresh USB/relay probe
- **cost:** Negligible API cost; one authenticated status request and a lightweight Mac serial/USB probe
- **security:** Expose device IDs only to the owner; do not claim LTE presence from a stale registry row; serial probing must be read-only and never flash firmware or open a control session.
- **missing:** A Mac read-only USB serial inventory route for the nRF9160 and ESP32 paths; A relay endpoint consumed by the Mac agent for authoritative device status (the Mac's /v1/devices/status 404 is expected); A signed monotonic session/heartbeat frame from the pendant, using the accepted offline-reality-beacon behavior

### ""Before you click, tell me whether the page is still the one I left open, or whether it changed underneath us.""
- **useful because:** A logged-in browser tab can remain online while its URL, account, modal, or visible data changes. A pre-action drift verdict protects the owner's sessions from acting on stale state without requiring them to inspect the screen.
- **path:** browser-extension → mac-vision → mac-planner → relay → pendant
- **model tier:** Deterministic URL/tab identity plus perceptual hash first; cheap vision model only when hashes differ; realtime speaks a short warning
- **latency:** Under 300 ms for URL/DOM identity; under 2 seconds for a changed-screen comparison
- **cost:** Usually no model call; $0.001–$0.01 only on changed screenshots, dominated by vision comparison
- **security:** Screenshots stay on the Mac by default; never transmit page pixels to the relay unless explicitly allowed. Secret fields are masked. Any action after a drift warning requires owner confirmation.
- **missing:** A browser extension snapshot token containing tab identity, masked visible-state hash, and capture time; A Mac-side drift comparator integrated with action ledger preconditions; A pendant-visible warning state for drift when the owner initiated the action by button/voice

### ""For every answer or action, tell me what proof you require, what proof you actually have, and refuse to silently substitute weaker evidence.""
- **useful because:** Today the system's surfaces use incompatible meanings of success: a Mac receipt, relay acceptance, browser inspection, and device playback are treated as if they were interchangeable. The owner cannot declare an evidence standard once and have every future voice, browser, and Mac action obey it. This capability makes uncertainty an enforceable owner preference rather than a disclaimer after the fact.
- **path:** pendant → relay → mac-planner → browser-extension → unified → dashboard
- **model tier:** Deterministic policy/evidence matcher for the gate; background model only to explain conflicts in one short sentence; realtime only for the spoken decision
- **latency:** Under 150 ms when required evidence is already present; under 2 seconds when collecting bounded evidence from other surfaces
- **cost:** Usually no model cost; occasional $0.001–$0.01 explanation call when evidence conflicts
- **security:** Evidence policies themselves may reveal sensitive workflow details, so store them locally and sync only scoped policy IDs. Never weaken a requirement because a surface is offline. Confirmation is required when the owner explicitly overrides a missing proof.
- **missing:** An owner-facing evidence-policy schema with requirements such as observed_screen, Mac_execution_receipt, relay_acceptance, pendant_received, and physical_playback; A judgement gate that evaluates the policy before action and before reporting success; A common vocabulary and provenance links across browser receipts, Mac ledgers, relay jobs, and device events; A compact pendant cue for blocked/verified/owner-overridden states

### ""Before you do anything consequential, obtain two independent witnesses and tell me if they disagree.""
- **useful because:** A single surface can be stale or wrong: a browser can show an old session, the Mac can report execution without delivery, and the relay can accept work without the device hearing it. The owner should be able to require independent cross-surface corroboration for selected actions instead of trusting whichever subsystem answered first.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic quorum evaluator; background model only to summarize a disagreement; realtime speaks the brief gate result
- **latency:** Under 1 second for cached witnesses; under 5 seconds for fresh browser and relay checks
- **cost:** Negligible when witnesses are metadata; at most $0.005 for a conflict explanation
- **security:** Do not duplicate private page contents between witnesses. Quorum rules must never turn a stale witness into proof; high-risk actions remain blocked on disagreement unless explicitly overridden.
- **missing:** An owner-configurable witness-quorum policy by action class; Independent witness attestations with timestamps, hashes, and source identity; A judgement gate that blocks execution until quorum passes and records the dissent

### ""When I give you an instruction offline, hold it safely until you reconnect, then tell me whether it is still valid before doing it.""
- **useful because:** A worn device may hear an instruction while disconnected, but executing it later can be dangerous because context, prices, pages, permissions, or deadlines may have changed. The owner needs an explicit, expiring intent with conditions—not an opaque retry or a false success.
- **path:** pendant → relay → mac-planner → browser-extension → unified
- **model tier:** Pendant firmware records a compact intent envelope; background model resolves ambiguity after reconnection; judgement remains deterministic about expiry and confirmation
- **latency:** Immediate local receipt; on reconnect, under 10 seconds to validate context and ask for confirmation when needed
- **cost:** Low: a small metadata record on-device and one background planning call when the intent becomes eligible
- **security:** Never queue destructive or financial actions without a fresh confirmation. Encrypt the local envelope, set a hard expiry, bind it to the intended account/session, and discard it when conditions cannot be revalidated.
- **missing:** A pendant-resident encrypted intent envelope with monotonic expiry and owner-visible receipt; Relay/Mac reconciliation that rechecks browser state and permissions before execution; A policy separating safe idempotent actions from confirmation-required actions


## Changes it proposed to its own stack

### `hardware` — Add a low-power haptic actuator and driver on the production pendant (the prototype has one button and one LED but no haptics). Define three locally-rendered patterns: short double pulse for relay acceptance, long pulse for confirmed device playback, and three rapid pulses for an integrity/permission uncertainty verdict. The relay/Mac would send only a compact semantic cue, while the pendant owns the final physical timing.
- **owner gets:** The owner can know, without looking at a screen or trusting a spoken claim, whether a request was merely accepted, actually played, or needs repeating—especially in noisy streets or when audio is muted.
- effort: Medium hardware revision plus firmware event mapping and relay semantic cue; validate current draw, enclosure, and accessibility. Prototype with a coin ERM/LRA and a GPIO/I2C driver.  ·  risk: False reassurance if the wrong semantic state is emitted; mitigate by making 'confirmed playback' impossible unless the device's playback ledger says so, and fall back to the LED/error pattern. Mechanical noise and discomfort require adjustable intensity and a disable setting.
- cost: Roughly $1–$4 BOM increase plus PCB/layout and enclosure work; tens of mW only during pulses, negligible average draw at low event rates.  ·  latency: Local cue starts within tens of milliseconds of the semantic event; no added speech latency.
- security: Haptic patterns must not encode sensitive content; only coarse state leaves the relay. Device-local settings should control whether uncertainty cues are enabled.
- depends on: A device-originated playback state from the already accepted audio_delivery_ack_queue; A relay field carrying semantic delivery state rather than the current bytes-to-socket 'delivered' label


## What it asked for

_Nothing._
