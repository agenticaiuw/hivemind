# Harness derivation — unified — round 39

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “handle this,” first tell me whether every handoff needed is actually ready; if not, keep my request safely queued and tell me exactly what is blocked, then continue automatically when it becomes possible."
- **useful because:** Today the Mac reports full-control planning while Accessibility and Screen Recording are untrusted, and the browser is offline with pending commands. A cross-surface readiness contract prevents the pendant from claiming completion, preserves intent during outages, and resumes only when the exact browser/Mac/session prerequisites return.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Deterministic readiness evaluation and queueing on relay/Mac; background model only to summarize blockers. Realtime only for the immediate spoken acknowledgement.
- **latency:** Under 300 ms for readiness verdict and spoken acknowledgement; resume work within one heartbeat after prerequisites recover.
- **cost:** Negligible for deterministic checks; roughly $0.001–$0.01 only when a background model turns multiple blockers into a concise explanation. Dominant cost is not inference but durable queue/state and heartbeats.
- **security:** Do not expose tokens or page contents in blocker reports. Bind queued intent to owner/session and an expiry; never auto-resume irreversible steps without renewed approval. Require same browser tab/session and Mac permission fingerprint at resume.
- **missing:** Typed cross-surface readiness contract (permissions, online state, session affinity, freshness, audio delivery) with reason codes; Durable intent lease and resume cursor shared by relay and Mac job runner; Pendant notification for queued/blocked/resumed/failed states; A pre-execution gate that rejects plans when status claims conflict (for example fullControlMode=true but ready=false); Fresh post-resume perception and completion proof before announcing success

### "Give me a private mode for the next few minutes: keep what I say and what you find on my Mac and logged-in sites out of shared displays and cloud history, use only the minimum needed to answer, and tell me when private mode has ended."
- **useful because:** The owner cannot currently establish a trustworthy privacy boundary across a worn microphone, relay, Mac screen, and authenticated browser session. A single spoken request should prevent accidental projection, persistence, screenshots, browser mutations, and unnecessary cloud retention while still allowing useful assistance.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Deterministic privacy policy enforcement on relay, Mac, and browser; a small background model may classify whether a requested operation needs a redacted or local-only path. Realtime is used only to acknowledge activation and expiry.
- **latency:** Activation and enforcement within 200 ms of the pendant gesture or spoken command; end-of-mode confirmation within one second.
- **cost:** Near-zero inference for policy enforcement. Occasional classification costs roughly $0.001–$0.01 per request; storage and audit indexing dominate rather than model calls.
- **security:** The privacy mode must be enforced below the planner, not merely stated in a prompt. It needs a pendant-local indicator, relay no-retain/no-training/no-R2 flag, Mac screen-capture and clipboard suppression, browser redaction for sensitive fields, and a clear fail-closed behavior when a surface cannot attest compliance. The owner must be able to cancel with the physical button, and expiry must be explicit.
- **missing:** End-to-end privacy lease signed by the pendant and honored by relay, Mac, browser, and dashboard; Pendant-local privacy indicator and fail-closed button gesture; Relay storage/logging policy that actually omits or cryptographically deletes private audio, transcripts, and screenshots; Mac/browser enforcement hooks for display capture, clipboard, screenshots, history, and sensitive-field redaction; A verifiable privacy receipt stating which surfaces complied, what was retained, and when the lease expired


## Changes it proposed to its own stack

### `integration` — Add a signed readiness snapshot exchanged before every cross-surface job. It must include per-surface online/permission/session freshness, capability claims, blockers, and a monotonic snapshot ID. The executor rejects stale or internally contradictory snapshots (e.g. fullControlMode=true with ready=false), emits a durable blocked receipt, and rechecks before resume and after execution.
- **owner gets:** The owner gets an honest answer instead of a confident “done” when the browser is offline or Mac permissions prevent control, while requests survive a dropped LTE/Mac link and resume safely later.
- effort: Medium: shared schema and validator in relay/Mac, job state transitions, heartbeat projection, dashboard display, and pendant notification hooks; add fault-injection tests for stale, contradictory, and mid-job loss cases.  ·  risk: A false blocker could delay harmless work; recover with explicit “run anyway” only for reversible actions and expiry-based re-evaluation. Never auto-bypass permission or approval gates.
- cost: Small deterministic CPU/D1 writes; no model call for checks. Dashboard and notification payloads add modest storage only.  ·  latency: ~10–50 ms local validation plus one relay round trip when remote; prevents much larger retries and misleading completion conversations.
- security: Improves security by binding actions to permission/session fingerprints and preventing confused-deputy execution; snapshots must omit secrets and page content.
- depends on: Durable cross-surface intent/job lease; ActionProof with fresh post-execution perception; Pendant durable notification/alert queue; Browser and Mac heartbeat freshness fields

### `hardware` — Add a normally-open, hardware-controlled microphone power/data disconnect and a bi-color privacy LED to the pendant audio front end. The disconnect is controlled by a physical privacy gesture and defaults to microphone-off whenever the privacy lease is absent, expired, or cannot be attested by the relay; firmware reports the latch state but cannot silently override it.
- **owner gets:** The owner gets a privacy boundary they can trust even if the relay, firmware, or model misbehaves: nearby speech cannot enter the system while the latch is off, and the visible indicator makes the state unambiguous.
- effort: Medium hardware revision plus firmware driver, enclosure/button gesture design, audio-path validation, and end-to-end tests for brownouts, dropped LTE, and reboot recovery.  ·  risk: The microphone could remain disabled unexpectedly and make conversations appear unresponsive. Recover with a deliberate long press, clear LED/audio feedback, and a startup self-test; fail safe to off rather than silently recording.
- cost: Roughly $1–$3 in switch/FET/LED and PCB changes at volume; negligible steady-state power, with a few milliwatts only while the indicator is lit.  ·  latency: Immediate local cutoff; no network round trip. Re-enabling capture may take one audio-frame startup period.
- security: Strongly improves physical privacy by making capture impossible in the off state. The control path must be isolated from ordinary application commands and audited; LED state must not be software-faked without reading the latch.
- depends on: End-to-end privacy lease and attestation protocol; Pendant firmware privacy gesture and state persistence; Audio front-end schematic access and production hardware revision


## What it asked for

### `c8-k71e` (context) — queued_action_resume_policy
- why: The readiness/intent-lease capability needs to know whether reversible work may resume automatically after a browser or Mac outage, and which classes always require a fresh spoken approval.
- would change: I would encode the correct resume gate and avoid either surprising the owner with automatic actions or needlessly asking them to repeat safe work; absent policy, I will require fresh approval for all irreversible actions and only auto-resume reversible ones with an unexpired lease.

