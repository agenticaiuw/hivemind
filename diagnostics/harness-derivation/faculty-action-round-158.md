# Harness derivation — faculty-action — round 158

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/browser action surface** — As of this round, home-macbook-bridge is online with fullControlMode and llm/computer-use planner enabled; browser bridge is online on Safari with 9 tabs, pendingCommands=0, and no queued browser affinity. Vision upload consent remains false, so page screenshots should not be assumed available to relay.
  - evidence: GET /ops/snapshot returned agent version 0.5.0, fullControlMode:true, computerUse.loopEnabled:true, visionUploadConsented:false; GET /browser/status returned online:true, tabCount:9, pendingCommands:0.

## Capabilities it proposed

### "“Finish this online task for me, but stop before anything consequential and ask me on the pendant.” The system should turn a spoken goal into a browser/Mac plan, show a short risk summary, require the pendant’s deliberate approval, execute only the approved step, independently verify the resulting page/file state, and tell me whether it is verified, failed, or unknown—even across a Mac sleep or link drop."
- **useful because:** This is the core hand-to-world capability: the owner can delegate an outcome rather than micromanage clicks, while the pendant remains the non-forgeable consent boundary and perception independently prevents false success claims.
- **path:** relay-realtime → faculty-judgement → faculty-action → faculty-perception → mac-planner → mac-vision → browser-extension → mac-terminal → dashboard
- **model tier:** Realtime only for the short spoken exchange and approval prompt; a cheaper background planner handles decomposition and recovery; faculty-perception uses deterministic/browser inspection where possible.
- **latency:** Initial plan and spoken risk summary under 5 s; approval-to-execution under 3 s; verification under 5 s, with durable pending state across sleep/link loss.
- **cost:** Typically one realtime turn plus 1–3 cheap planning/verification calls; roughly $0.01–$0.08 per task depending on page complexity, dominated by vision/browser observations.
- **security:** Page contents and secrets stay on the Mac/browser; relay receives only a redacted risk summary and postcondition evidence. Never put credentials in pendant payloads. Require physical approval for irreversible or externally visible steps; expiry, digest mismatch, replay, and unknown outcomes must fail closed.
- **missing:** A production orchestration primitive that binds operation/step IDs across planner, action, pendant approval, and independent verifier; Mac sleep/link-recovery handling that resumes a pending transaction without replay; Owner-defined risk policy for which action classes may execute without approval

### "“I’m in focus/meeting mode until [time]; only interrupt me for something urgent, and let me release the queue with one press.” The Mac should infer calendar/app state, the relay should classify incoming alerts, and the pendant should give a quiet urgency cue and retain a durable queue that I can review or dismiss later."
- **useful because:** The owner gets protection from interruptions without losing important events: the worn device is the one surface that can signal urgency while the Mac is occupied, and the relay can keep the policy alive when the Mac sleeps.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → faculty-judgement → faculty-action → dashboard
- **model tier:** Cheap background classifier for incoming notifications and calendar context; realtime only when the owner asks for the queue or changes policy.
- **latency:** Urgent alert decision within 2 s of arrival; nonurgent items queued immediately; policy changes acknowledged in under 1 s.
- **cost:** Near-zero for local calendar/app state; approximately $0.001–$0.01 per burst of classified alerts, dominated by model calls for ambiguous messages.
- **security:** Default deny for notifications containing secrets; keep full content on Mac and store only sender/category/deadline hashes in relay/pendant queue. Quiet hours and focus windows use America/New_York for Mac-resolved schedules, never an invented pendant timezone. Require explicit owner policy before suppressing calls or alarms.
- **missing:** An alert-ingress adapter for Mail/Messages/calendar and a compact urgency envelope to the relay; A pendant notification mode distinct from recording/agent-audio LED states; A small queue-review interaction (sw1 or product hardware with gesture headroom) and policy settings UI

### "“When I say ‘follow up on that,’ remember the exact commitment and bring it back at the right time.” The pendant should capture a short spoken commitment, the relay should extract person/topic/deadline and confidence, and the Mac should reconcile it against Mail, Messages, Calendar, and reminders before presenting a draft follow-up for my approval."
- **useful because:** It converts fleeting spoken intent into a reliable, context-aware follow-up instead of a raw audio dump: the owner gets the right reminder and a prepared draft without the system silently sending anything.
- **path:** pendant → relay-realtime → faculty-judgement → faculty-perception → mac-planner → mac-terminal → browser-extension → dashboard
- **model tier:** Realtime for capture acknowledgement only; a cheaper background model extracts entities and schedules; deterministic AppleScript/search reads reconcile context; realtime is reserved for ambiguity resolution.
- **latency:** Acknowledge capture under 1 s; extraction under 10 s; reconcile when the deadline window opens; draft retrieval under 3 s.
- **cost:** About $0.005–$0.03 per captured commitment, dominated by extraction and later ambiguity resolution; local app reads add no API cost.
- **security:** Audio remains on Mac/relay only until extraction and is deletable. Drafts are never sent automatically. Hash or redact message bodies in relay memory; browser session content stays in the browser surface. Use explicit timezone/locale for deadlines and refuse zoneless pendant timestamps rather than guessing.
- **missing:** A durable typed commitment record linking capture, extracted fields, source evidence, deadline, confidence, and draft; Read-only Mail/Messages/Calendar reconciliation with provenance; A follow-up draft approval flow integrated with the physical transaction latch

### "“Use my saved address/card/account details to complete this form, but do not show the values to the model, relay, logs, or pendant.” The browser should fetch only the requested fields from a local vault, fill them directly, and provide me a field-level audit of what was used before any submission."
- **useful because:** Today the owner must choose between manually entering sensitive data and exposing it to an AI workflow. This would make routine forms practical without turning the model, relay, browser history, or pendant into a secret store.
- **path:** browser-extension → mac-planner → mac-terminal → faculty-judgement → faculty-action → faculty-perception → relay-realtime → pendant
- **model tier:** Cheap deterministic field matching and local policy evaluation; realtime only for the spoken request and concise audit. No model should receive secret field values.
- **latency:** Vault lookup and field fill in under 3 seconds; audit before submission in under 2 seconds.
- **cost:** Near-zero API cost for local vault operations; at most $0.001–$0.01 for ambiguous field labeling, without transmitting values.
- **security:** Secrets remain in macOS Keychain or an equivalent local vault. Use per-field capability tokens, origin and form-binding, redacted logs, expiry, and physical confirmation for submission. Reject unexpected fields, cross-origin navigation, and replayed fill tokens.
- **missing:** A browser-bridge primitive for local secret injection that returns only redacted field identities; Origin/form-schema binding and per-field policy enforcement; A local vault adapter with audit receipts that never contain values

### "“Only let this assistant act while my pendant is physically present.” The Mac should cryptographically challenge the nearby pendant before every sensitive session or action, show the current presence state, and immediately revoke outstanding authority when the USB/BLE link disappears."
- **useful because:** A stolen or unattended Mac/browser session should not remain an authorized hand after the owner walks away. This gives the owner a simple physical-presence guarantee rather than relying on a forgotten browser tab or software lock.
- **path:** pendant → mac-planner → mac-terminal → browser-extension → relay-realtime → faculty-action → dashboard
- **model tier:** No model required for the challenge, presence lease, or revocation; realtime can explain state changes to the owner.
- **latency:** Presence challenge under 250 ms locally; revocation within 1 second of link loss; no cloud round trip required while USB-attached.
- **cost:** Negligible API cost; implementation cost is firmware/agent protocol work and possibly a BLE-capable product board if USB-only presence is insufficient.
- **security:** Use a hardware-held private key, monotonic challenge, short lease, and fail-closed revocation. Never treat an LTE registration or a stale relay heartbeat as local presence. Do not expose device identifiers in spoken replies or browser pages.
- **missing:** Pendant-attested challenge/response protocol; Mac agent hooks that revoke browser and action capabilities on lease expiry; A real proximity transport beyond today’s USB serial if presence must work away from the Mac

### "“This information is sensitive; keep it only until the task is done, then prove that it is gone everywhere.” The system should attach an expiration and purpose to a capture, draft, browser session, or relay record, automatically purge copies across the pendant queue, relay, Mac context, and browser artifacts, and return a deletion receipt listing every surface reached."
- **useful because:** Today deletion is fragmented: removing a recording or draft does not establish that derived context, queued copies, browser artifacts, or relay caches disappeared. Purpose-bound expiry would let the owner safely use the system for sensitive one-off tasks.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → faculty-perception → faculty-action → dashboard
- **model tier:** Deterministic retention/purge engine; no model needed except optional classification of sensitivity during capture.
- **latency:** Apply retention policy at creation; purge at expiry within seconds; deletion receipt available within 5 seconds of completion or clearly marked incomplete.
- **cost:** Minimal API cost; storage-index and purge implementation dominate. Large audio blobs may require background deletion verification.
- **security:** Deletion must cover plaintext, derived transcripts, embeddings, logs, browser downloads, and offline queues. Use authenticated tombstones, idempotent purge, bounded retry, and an explicit 'unable to verify deletion' result. Never claim cryptographic erasure where filesystem/cloud guarantees are unavailable.
- **missing:** A cross-surface retention manifest with purpose, expiry, and sensitivity; Purge adapters for relay storage, Mac context/journal, browser artifacts, and pendant outbox/inbox; A deletion verifier that reports coverage and residual uncertainty


## What it asked for

_Nothing._
