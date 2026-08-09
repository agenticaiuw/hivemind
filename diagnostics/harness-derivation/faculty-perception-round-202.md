# Harness derivation — faculty-perception — round 202

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac perception prerequisites** — The exact AI Pendant Agent binary now has Accessibility and Screen Recording granted; /ops/status reports permissions.ready=true, requiredMissing=[], computer-use loop enabled, browser extension online, and relay reachable. Browser currently exposes a live Safari tab on YouTube (2 tabs total). This supersedes the earlier denied-permission state.
  - evidence: Authenticated GET /ops/status returned hostFingerprint com.aipendant.agent|~/Applications/AI Pendant Agent.app, accessibility.trusted=true, screenRecording.granted=true, ready=true; browser online=true; relay reachable=true; GET /health returned agent version 0.5.0.

## Capabilities it proposed

### ""What is true right now across my Mac, browser, relay, and pendant—and what is only inferred?" Give me one short spoken situation report with each claim tagged by source, age, and confidence, call out contradictions, and never call a job complete merely because the Mac finished."
- **useful because:** This is the system's single most useful perception capability: it prevents the owner from acting on a stale browser tab, a relay record, or a Mac-side 'completed' status mistaken for something the owner actually heard. It uses the hive's physically different vantage points rather than giving another Mac-only dashboard.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → faculty-perception
- **model tier:** Use a cheap structured summarizer over the live snapshot; reserve realtime only for the owner's spoken follow-up. No expensive model is needed to classify freshness, provenance, or unknown.
- **latency:** Under 2 seconds when asked; stream the first verified facts within 500 ms and fill in slower browser/relay details afterward.
- **cost:** Near-zero model cost for deterministic normalization; roughly 1–3k input tokens only when a natural-language synthesis is needed. Dominant cost is the existing snapshot/browser reads, not inference.
- **security:** Do not expose page bodies, secrets, or credentials in the spoken report. Browser claims must carry tab/session provenance; relay completion must be labeled socket-accepted versus device-played. Mutating actions require the existing confirmation policy.
- **missing:** A versioned cross-surface claim envelope with observedAt, source, freshness, confidence, and unknownReason; A real pendant branch once a device registers; today the live check must honestly say no pendant is registered; A reducer that joins GET /ops/snapshot and GET /pipeline with browser inspection and relay device/job state without pretending truncated exports are complete

### ""Why do you believe that?" For any browser-derived answer or action, show me the exact page/tab, capture time, content hash, redaction status, and the chain from browser observation to plan, Mac action, relay job, and spoken result."
- **useful because:** It turns an opaque answer into an auditable one. The owner can distinguish a live authenticated tab observation from an old or public relay read, catch page changes before acting, and revoke sensitive evidence without exposing the page body.
- **path:** browser-extension → mac-planner → relay-realtime → mac-vision → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Deterministic joins and hashes first; a small text model only summarizes the chain when asked. Realtime is only for the spoken explanation.
- **latency:** Under 1 second for an existing capsule/ledger lookup; up to 3 seconds to assemble a new browser capture and its action receipt.
- **cost:** Low: hashes, local JSON lookups, and existing receipts dominate; no model call for the normal path, under 1k tokens for a narrated explanation.
- **security:** Keep capsule bodies local and redacted; spoken output should default to metadata and a short digest, never secrets. Require confirmation before revealing sensitive claims or replaying page text. Relay reads must be marked untrusted until linked to a local capsule.
- **missing:** Mount the existing browserProvenance routes and make every relay browser read return a stable request ID/content hash that the Mac can turn into the existing evidence capsule; A mandatory join record linking capsuleId to commandId, ledgerId, jobId, sessionId, and receiptId for all browser-originated plans; A revocation check in judgement/action before using a previously captured claim

### ""Can I unplug and wear the pendant now?" Run a bench-to-worn readiness check: inspect the USB-connected nRF9160 and audio bridge, verify firmware health and audio loopback, verify relay registration/heartbeat, then report exactly what will still be unknown after unplugging."
- **useful because:** The owner has hardware source and a real bench but no registered pendant. This prevents the dangerous false handoff where a successful Mac-cabled test is mistaken for an LTE-independent wearable. It gives a concrete go/no-go answer and identifies the first missing link instead of merely saying offline.
- **path:** mac-terminal → mac-planner → relay-realtime → relay → pendant → faculty-perception
- **model tier:** Use deterministic diagnostics and thresholds; no frontier model. A small summarizer can turn measurements into one spoken sentence.
- **latency:** 30 seconds maximum for serial probes and a short loopback; relay checks should return in under 2 seconds.
- **cost:** Negligible API/model cost; local serial reads and a few authenticated relay GETs dominate. Bench power and USB time are the real costs.
- **security:** Read-only serial protocol with strict byte/time bounds; never flash firmware or transmit credentials. Report that USB presence is not LTE registration and do not claim a pendant is online from Mac-bridge health.
- **missing:** The granted mac_usb_serial_diagnostics capability must be implemented/exposed as a bounded read-only route; current inventory still has no serial/USB route; A firmware diagnostic response that includes the accepted offline-reality-beacon frame and loopback counters; A relay-side device identity/heartbeat path emitted by the pendant itself, not inferred from the Mac bridge; A repeatable acceptance profile for mic quality and 24 kHz downlink before unplugging

### ""Can I trust what you can see right now?" Return a perception trust verdict before answering: which sensors are live, their age, whether the screen/browser view is obstructed or stale, which sources disagree, and the exact blind spot that could make the answer wrong."
- **useful because:** The owner gets a useful refusal instead of confident hallucination when a browser heartbeat, relay snapshot, screen capture, or pendant link is stale. This is a user-facing trust control, not another status dashboard: it gates the answer that follows.
- **path:** faculty-perception → mac-vision → browser-extension → relay-realtime → pendant → unified
- **model tier:** Deterministic freshness/contradiction rules; no expensive model. Realtime only speaks the compact verdict.
- **latency:** Under 500 ms from cached health; at most 2 seconds when a fresh screen or browser probe is needed.
- **cost:** Negligible model cost; one bounded snapshot or browser status call when cache age exceeds the requested bound.
- **security:** Expose only capability state and source metadata, not page content or screenshots by default. A stale or missing sensor must lower confidence and prohibit consequential action unless the owner explicitly confirms.
- **missing:** A common freshness contract across snapshot producers (observedAt, expiresAt, source sequence); A screen obstruction/occlusion verdict from the vision loop rather than merely a successful screenshot; A policy hook in judgement/action that consumes the verdict and refuses stale-source mutations

### ""What changed since the last time you asked me to confirm?" Show only externally relevant changes across the browser, Mac, relay, and wearable: before/after values, who or what changed them, and whether the change was actually observed or merely requested."
- **useful because:** It closes the gap between an intended action and a changed world. The owner can catch a failed or partial browser/Mac action without replaying a full transcript, while perception remains honest about requested versus observed state.
- **path:** faculty-perception → faculty-action → mac-planner → browser-extension → relay-realtime → pendant
- **model tier:** Deterministic receipt and observation diff; a small summarizer produces the one-sentence spoken result. No realtime reasoning beyond narration.
- **latency:** Under 1 second from existing ledgers; up to 3 seconds for a fresh browser or screen observation.
- **cost:** Low; local diffing and existing receipts dominate, with optional sub-1k-token summary.
- **security:** Redact secrets and private page text from diffs. Treat a Mac receipt, relay socket write, and pendant playback as separate evidence levels; never collapse them into 'done'. Require confirmation for destructive or externally visible changes.
- **missing:** A durable observation checkpoint ID shared by planner, action ledger, browser provenance, relay job, and device playback telemetry; A post-action observation hook for every reversible action, not just the action receipt; A semantic diff schema that distinguishes requested, acknowledged, observed, and physically played

### ""Freeze this moment so I can resume it anywhere." Create a portable, content-addressed handoff of the exact browser tabs, visible Mac app state, active project/context, pending relay work, and wearable health at one instant; later, on another node or after an outage, say "resume that moment" to restore only the safe reversible state and show a diff of everything that changed."
- **useful because:** Today the hive remembers fragments, not a portable moment. The owner loses the relationship between what they were viewing, what they asked the relay to do, and what the Mac was changing. This gives them a true pause/resume boundary across devices and outages without pretending old state is current.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant → unified → faculty-perception → faculty-action
- **model tier:** Deterministic capture, hashing, redaction, and diffing; a cheaper text model may label the checkpoint. Use realtime only to answer the spoken resume request.
- **latency:** Capture in under 3 seconds; resume preview in under 2 seconds, with restoration requiring explicit confirmation per action.
- **cost:** Low API cost: local state reads and content hashes dominate; at most 1–2k tokens to summarize a checkpoint. Storage is bounded metadata plus redacted capsule bodies.
- **security:** Never checkpoint passwords, cookies, raw audio, or secret page bodies. Encrypt the checkpoint at rest, bind restoration to the original owner/device trust, and require confirmation before opening apps, navigating, or mutating files. A checkpoint must label unavailable or expired sources rather than silently replay them.
- **missing:** A cross-surface checkpoint schema that joins browser capsule IDs, Mac action-ledger state, relay job/context IDs, and pendant health sequence; An atomic capture barrier or per-source sequence numbers so the checkpoint can prove which observations belong to the same instant; A restore planner that supports only reversible actions and produces a preflight diff; expired/revoked evidence must remain withheld; A durable encrypted store/transport so the checkpoint can move between the Mac, relay, and a future registered pendant

### ""Put the pendant in guest mode for the next hour." Let another person use the physical device for basic conversation while preventing access to my memories, browser sessions, files, routines, and announcements; when guest mode ends, provide a signed audit of everything the guest could reach and revoke the temporary trust."
- **useful because:** A wearable is physically shareable, but today its identity and the owner's context are effectively fused. This lets the owner lend it safely, use it at a demo or in a household, and recover with confidence instead of handing over a live personal agent.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Deterministic capability isolation, scoped tokens, and audit logs; use a small model only to explain the resulting access report. Realtime is only the conversation surface.
- **latency:** Enter guest mode in under 2 seconds; revoke immediately on button press or timeout; produce the access report within 5 seconds.
- **cost:** Low inference cost; dominant work is secure session/token management and bounded audit storage. No browser or Mac action should run unless explicitly granted to the guest session.
- **security:** Guest audio and transcripts must be isolated and optionally discarded. Never inherit owner cookies, memory projection, files, or voice identity. Require a local physical gesture/PIN to enter and exit, use expiring least-privilege credentials, and make revocation work while offline with a local deny-list.
- **missing:** A pendant-local guest/owner session boundary with an offline timeout and physical exit gesture; Relay credentials scoped to guest conversation only, with no access to owner memory, announcements, routines, or jobs; Mac and browser policy enforcement that rejects guest-originated actions and keeps owner sessions separate; A tamper-evident audit joining device session, relay calls, Mac/browser attempts, and revocation time


## Changes it proposed to its own stack

### `hardware` — Add a small secure element or equivalent hardware-backed key store to the pendant design, with a device-generated signing key and monotonic anti-rollback counter. Sign health frames, capture-quality verdicts, and playback lifecycle events at the device boundary; the relay verifies signatures and binds them to the registered device rather than trusting an admin bearer token or a Mac-authored snapshot.
- **owner gets:** The owner can finally know whether a statement came from the physical pendant they are wearing, whether its firmware state is fresh, and whether audio was actually played—rather than receiving a plausible but Mac- or relay-authored status.
- effort: Medium hardware revision plus firmware, pairing, relay verification, key rotation, and recovery tooling. Design it as an optional board revision with a software fallback marked unverified.  ·  risk: Key loss or damaged hardware could strand the device; provide a recovery/re-pair ceremony that invalidates the old key, and never make unsigned legacy telemetry look trusted. Secure-element supply and driver integration are additional schedule risks.
- cost: Approximately $0.50–$2 per unit in volume, plus a few milliamps only during signing; negligible per-message API cost.  ·  latency: Usually a few milliseconds per signed frame; batch counters/health data to avoid signing every audio packet.
- security: Strongly improves device authenticity, replay resistance, and provenance. It does not make content private by itself; transport encryption and redaction remain required.
- depends on: A defined signed telemetry envelope and device enrollment protocol; Relay-side verification and key revocation storage; The accepted offline-reality-beacon and playback acknowledgement firmware behaviors


## What it asked for

_Nothing._
## Its own summary

Fresh discovery materially changed the reality fence: the exact AI Pendant Agent binary now has Accessibility and Screen Recording, /ops/status says permissions.ready=true, computer-use is enabled, Safari's browser bridge is online on a YouTube tab, and the relay is reachable. I recorded that as verified and proposed three new perception capabilities: a cross-surface truth report, an evidence-chain explainer, and a USB-to-worn readiness gate; then added a sensor-trust verdict and requested-vs-observed change diff. The main remaining gaps are not basic Mac visibility: there is still no registered pendant, no callable bounded USB serial reader despite the granted request, no common freshness/claim envelope, and no device-originated playback evidence. I also confirmed that existing snapshot/provenance routes are ingredients, not joined end-to-end.

**Biggest unknown:** Whether a physical nRF9160 pendant is now connected or has registered remains unknown only outside the relay registry: live relay data still reports no pendant, and there is no callable serial probe to inspect the USB ports. Until that is built or a device heartbeats, no claim about wearable readiness, reception, or playback can be made.

