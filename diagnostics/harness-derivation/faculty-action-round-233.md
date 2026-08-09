# Harness derivation — faculty-action — round 233

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live device availability** — The live device inventory currently shows Safari online and home-macbook-bridge online, but no LTE-registered pendant; the mobile entry is offline. Deferred workflows and UART drafting can be designed now, while field pendant delivery still needs registration.
  - evidence: discover(devices) returned Safari on MacIntel online, home-macbook-bridge online, cloudflare-contract-test mobile offline; no pendant entry.

## Capabilities it proposed

### "When I say “handle this later,” let the pendant capture the intent, the relay hold it until my Mac and browser are available, then execute one reversible step at a time and tell me exactly which step was verified, which was not, and what I can retry."
- **useful because:** This is the single most useful missing behavior: an intent survives a disconnected wearable and does not silently turn into an unverified multi-app side effect. It joins the only surfaces that respectively hear the request, wait forever, hold authenticated browser sessions, act on the Mac, and independently establish truth.
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision → mac-terminal → faculty-judgement → faculty-perception → faculty-action
- **model tier:** Realtime only for capture/brief acknowledgement; relay background orchestration and cheap local planner for execution; faculty-perception verifier only after each step. Escalate to a stronger model only when a step is ambiguous.
- **latency:** Acknowledge capture in under 1 second. Resume when surfaces return, with 2 seconds between checkpoints; no deadline hidden from the owner. A 5–10 step task may take minutes.
- **cost:** About $0.01–$0.08 per resumed task depending on ambiguity; most steps use local routing and verification, with model tokens dominating only ambiguous checkpoints.
- **security:** The relay stores a redacted intent, not page secrets. Each step has an idempotency key, expiry, risk tier, and postcondition. Irreversible actions remain staged for the existing physical transaction approval latch. If verification is unknown, stop rather than report success. Requires explicit owner policy for which risk classes may run unattended.
- **missing:** A durable workflow/checkpoint object that links intent, step IDs, retries, expiry, and verifier receipts across relay and Mac jobs; An executor adapter that can resume a specific step without replaying prior successful steps; A single owner-visible timeline that combines Mac/browser receipts with faculty-perception proofs

### "When the pendant or bridge detects a hardware fault, say “file this bug,” and have the system collect a bounded, redacted UART/bridge diagnostic, correlate it with the exact firmware/audio receipt, draft an issue on my Mac, and let me review or approve it before anything leaves the machine."
- **useful because:** The owner already wants the pendant to file its own bug reports, but a raw log is not an actionable report. This turns a wearable failure into a reproducible issue with hardware identity, timing, codec counters, and an honest statement of what was not measured—without exfiltrating unrelated logs.
- **path:** pendant → relay-realtime → mac-terminal → mac-planner → faculty-perception → faculty-action
- **model tier:** Cheap background model summarizes bounded diagnostics; realtime only acknowledges capture. Never use the expensive tier for routine log redaction or formatting.
- **latency:** Capture locally in under 2 seconds; produce a reviewable draft within 30 seconds after the Mac bridge is online. Upload only after owner approval.
- **cost:** Roughly $0.002–$0.02 per report; storage and local parsing dominate, not model inference.
- **security:** UART may contain credentials or audio fragments. Apply allowlisted field extraction, byte and time bounds, secret scrubbing, and a preview-before-upload gate. Keep raw logs local and delete them by retention policy. Never auto-post to a public tracker.
- **missing:** A read-only bounded UART/bridge diagnostics operation with structured exit status and device identity; A firmware fault-envelope event containing counters, reset reason, and opaque correlation ID rather than raw audio; A local issue-draft destination and explicit approve/send policy

### "Let me say “use the private browser session to do this, and leave no sensitive trace.” The pendant should carry only an opaque task token, the relay should never receive page contents, the Mac/browser should perform the task in a temporary isolated workspace, and I should receive proof that drafts, downloads, clipboard contents, and temporary files were either retained by my instruction or erased."
- **useful because:** Today the browser can reach logged-in private sessions, but the owner cannot ask for a sensitive task with a strong, inspectable confidentiality boundary spanning pendant, relay, Mac, and browser. This would make high-value actions possible without treating the relay or model context as a second browser.
- **path:** pendant → relay-realtime → browser-extension → mac-terminal → mac-planner → faculty-perception → faculty-action
- **model tier:** Realtime handles only the short command and confirmation. Local Mac/browser execution and deterministic secret-scrubbing do the work; use a background model only to classify whether requested output is sensitive.
- **latency:** Acknowledge in under 1 second; establish the isolated workspace in under 3 seconds; return a cleanup receipt within 2 seconds after completion.
- **cost:** Typically under $0.01 per task; local isolation, hashing, and cleanup dominate rather than inference.
- **security:** The system must fail closed if the browser cannot guarantee session isolation or cleanup. Never send page text, form secrets, cookies, clipboard contents, or downloaded files to the relay. A cleanup receipt must distinguish erased, retained by instruction, and unknown. Sensitive sends and irreversible actions still require explicit approval.
- **missing:** A browser command mode that returns structured success and cleanup attestations without exposing page contents; A Mac sandbox/temp-workspace lifecycle with clipboard and download quarantine; A redaction-and-retention contract shared by relay, browser, Mac, and verifier; An owner-visible policy for which sensitive operations are permitted

### "Let me say “for the next hour, calendar changes are okay, messages are never okay, and purchases always need me.” The system should issue a temporary, visible action policy that applies across the relay, Mac, browser, and pendant, expires automatically, and can be revoked with one safe gesture."
- **useful because:** The owner currently cannot express a short-lived exception without relying on an unspecified permanent policy. A bounded policy lease makes proactive automation practical while preventing an old approval from silently widening into a different action class.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-judgement → faculty-action
- **model tier:** Realtime parses the spoken policy; deterministic policy evaluation executes it. No expensive model should sit in the authorization path.
- **latency:** Policy acknowledgement and haptic confirmation within 1 second; every action consults the lease synchronously before execution; expiry and revocation take effect within one action poll.
- **cost:** Well under $0.01 per policy lease; cryptographic signing and local policy checks dominate.
- **security:** A lease must be signed, scoped to exact action classes and destinations, have an absolute expiry, and default to deny on clock uncertainty or link loss. The pendant should display only a compact policy ID and risk pattern, never secrets. Revocation must be safe and idempotent.
- **missing:** A canonical cross-surface policy-lease schema and evaluator; A monotonic/absolute expiry strategy that remains safe across relay, Mac, and pendant clock differences; A way for each executor to prove which policy lease authorized a step; Firmware handling for policy-expired and policy-revoked outcomes

### "Let me say “remind me when I start walking.” The pendant should detect only the transition from still to walking locally, send a tiny signed event without audio or location, and have the relay deliver the reminder once—then forget the motion trace."
- **useful because:** This gives the owner a genuinely wearable reminder trigger without GPS, phone presence, or continuous cloud sensing. It uses the pendant's owned IMU while preserving privacy: the relay receives one transition, not a movement history.
- **path:** pendant → relay-realtime → mac-planner → faculty-judgement
- **model tier:** A tiny deterministic firmware classifier handles still→walking; the relay and Mac use existing reminder/routine machinery. No model inference is needed for the trigger.
- **latency:** Detect the transition within 1–2 seconds; deliver the reminder within 5 seconds when connected; queue one event safely if disconnected.
- **cost:** Negligible inference cost; firmware work and small authenticated event storage dominate.
- **security:** Do not infer identity, location, gait, or health. Store only a coarse event type, monotonic event ID, and expiry. Require explicit opt-in per reminder, rate-limit false triggers, and provide a pendant cancel gesture. Motion data must never leave the device.
- **missing:** An IMU firmware classifier and calibration flow using the owned LSM6DSOX on enabled i2c2; A signed, deduplicated motion-transition event in the existing typed outbox; A reminder trigger condition supporting device events rather than only wall-clock schedules; A way to inspect, disable, and expire active motion-triggered reminders


## Changes it proposed to its own stack

### `hardware` — Add the owner's intended jewellery-style rotary crown/encoder and one deliberate confirmation button to the pendant revision, with a low-power wake-capable input and tactile detents. Reserve encoder events for menu selection, repeat-last-answer, and choosing among pending action outcomes; keep sw0's active-edge recording path unchanged. Integrate the existing DRV2605L and IMU on enabled i2c2 for silent haptic state/error patterns.
- **owner gets:** A wheel gives the owner a reliable way to select among several pending items or answers without inventing another ambiguous long-press gesture. It makes the pendant feel like jewellery rather than a gadget and allows safe cancel/choose/repeat interactions while preserving instant recording.
- effort: Medium-high: mechanical enclosure and crown, debounce/wake firmware, event protocol, and i2c2 devicetree/CMake integration. Prototype on the bench before a gold enclosure.  ·  risk: False detents or wake storms could drain the 500 mAh battery; an encoder fault must never trigger an action. Recover by defaulting to no-op, keeping sw0 recording unchanged, and requiring the existing physical approval latch for side effects.
- cost: Approximately $5–$20 incremental parts/PCB/mechanics for a prototype; encoder draw is negligible, haptic/IMU add intermittent tens of mW. Gold enclosure cost is separate.  ·  latency: Selection feedback under 100 ms locally; no impact on 24 kHz codec path if events are interrupt-driven and haptics are rate-limited.
- security: Improves security by making selection and cancellation distinct from approval. No secrets need enter the pendant.
- depends on: owner choosing the encoder geometry and second-button placement; i2c2 enabled for the already-owned DRV2605L and LSM6DSOX; rotary event schema shared with relay and Mac UI; physical_transaction_approval_latch


## What it asked for

_Nothing._
