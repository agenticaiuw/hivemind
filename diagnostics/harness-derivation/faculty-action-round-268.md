# Harness derivation — faculty-action — round 268

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If this task is going to touch several apps, carry it through as one operation and stop safely if any step cannot be proven.”"
- **useful because:** The owner gets an honest all-or-nothing-feeling workflow rather than a sequence that silently half-completes: browser edits, Mac file/message changes, and relay delivery are linked, each step is independently checked, and an incomplete operation is left in a resumable or compensating state.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** background for planning and compensation; realtime only for the spoken request and urgent stop signal
- **latency:** Plan acknowledgement under 2 seconds; each step may take normal app latency; stop/abort signal must be accepted within 1 second when the Mac/browser is reachable.
- **cost:** Roughly 1–3 cheap model calls per operation plus existing Mac/browser calls; cost is dominated by verification and any compensating action, not audio.
- **security:** Never claim the whole operation succeeded from executor receipts alone. Each mutation needs a fresh postcondition check and provenance. Compensation must be reversible and staged when it could destroy data. Do not send secrets or page contents to the pendant; show only a redacted operation summary and status.
- **missing:** A first-class operation coordinator that models dependencies and compensating steps across POST /execute, browser commands, and relay delivery; A way to attach compensation metadata and verified-step receipts to one operation ID; An owner-visible state for partial completion and a safe resume/abort choice

### "“Save this moment so I can find it later.”"
- **useful because:** A press on the worn device would capture the owner's intent even offline, while the Mac preserves the surrounding actionable context: the current app or browser session, URL/title, active project, and a short timestamped voice note. Later the owner can ask for “the moment about that page” and receive a linked, searchable record instead of an orphaned audio file.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** realtime only to acknowledge the press; background model for later labeling and retrieval
- **latency:** Haptic acknowledgement under 300 ms locally; context snapshot within 2 seconds when connected; offline bookmark durable immediately and syncs later.
- **cost:** Near-zero for the local event and existing snapshots; one inexpensive background embedding/labeling call per bookmark batch.
- **security:** Capture only metadata and the owner's explicitly recorded audio; browser content must be redacted or limited to title/domain unless the owner asks for the page. Encrypt queued records, expire sensitive URLs, and make deletion propagate to relay and Mac indexes.
- **missing:** A cross-surface bookmark envelope that binds pendant event ID to Mac observation and browser session identity; A consent/configuration setting for what contextual fields may be attached; Retrieval that searches bookmark events together with context-graph entities and audio transcripts

### "“If I’m moving or I put the pendant away, don’t start anything risky—just tell me what needs my attention later.”"
- **useful because:** The pendant can detect a physical change of context that the Mac cannot: walking, pocketing, or deliberate face-down handling. Risky browser/file/message operations are paused before mutation, while harmless reminders can be queued. This prevents a spoken request made in a noisy doorway or while rushing from becoming an irreversible action.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** device firmware for motion/gesture classification and immediate local gating; cheap background model for policy classification; realtime only for a concise warning
- **latency:** Local gate under 150 ms from the qualifying gesture; relay/Mac policy decision under 1 second; queued attention item visible after connectivity returns.
- **cost:** Negligible device compute and one small policy call only when a task is pending; no model call for ordinary stillness.
- **security:** Motion is a safety signal, not proof of identity or consent. Never silently cancel a safety-critical action; report deferred/unknown status. Store only coarse motion class and event time, not raw IMU streams. The pendant must be able to block transmission of a staged high-risk operation without receiving secrets.
- **missing:** Firmware integration for the owned LSM6DSOX on i2c2 and a bounded motion classifier; A relay policy hook that converts motion state into pause/defer/cancel semantics for staged Mac/browser operations; Owner-configurable action classes and quiet-time behavior, defaulting conservatively

### "“When I’m wearing the pendant, keep my private work available; when it leaves me, protect every screen and pending action automatically.”"
- **useful because:** This would create a real wearable privacy boundary across the Mac, browser sessions, relay, and phone rather than trusting a stale login. Leaving the pendant, losing its authenticated presence, or triggering a deliberate privacy gesture would immediately freeze staged actions and put sensitive surfaces into a protected state; returning would restore only after a fresh physical attestation.
- **path:** pendant → relay → mac-planner → browser → ios → dashboard
- **model tier:** Device/relay cryptography and local policy for presence decisions; no model call for the security path; background model only for explaining what was protected.
- **latency:** Presence loss should gate new mutations within 1 second and freeze pending high-risk operations within 2 seconds. Restoration may require an explicit physical gesture and take up to 5 seconds.
- **cost:** Negligible inference cost; engineering and security-review cost dominate. A secure element would add roughly $2–$8 per unit and low standby power.
- **security:** Presence must not be treated as consent to execute an action. Use challenge-response, replay protection, expiry, and explicit separation between ‘present’, ‘approved’, and ‘owner authenticated’. Never transmit page contents or credentials to the pendant. Fail closed for staged high-risk operations, but preserve recoverable drafts.
- **missing:** A hardware-backed key store or secure element on the pendant/bridge; A short-range presence transport (BLE/UWB-class) with authenticated challenge-response; LTE alone cannot provide proximity; Mac/browser/iOS privacy-control hooks that can freeze or redact sensitive surfaces; A policy and recovery path for battery loss, link loss, and intentional handoff

### "“Let Alex handle just this one task, without giving them access to my account or the rest of my computer.”"
- **useful because:** The owner could delegate a narrowly scoped real-world task—such as choosing a meeting time or filling a non-sensitive form—without sharing credentials, browser cookies, or a full remote session. The pendant confirms the delegation, the relay issues a one-time capability, and the Mac/browser enforces the allowed action and expiry.
- **path:** pendant → relay → mac-planner → browser → ios → dashboard
- **model tier:** Background model for extracting the requested scope and presenting a plain-language summary; deterministic policy and capability enforcement for execution.
- **latency:** Draft the delegation in under 3 seconds; recipient access should begin within 10 seconds; revoke should take effect within 2 seconds while connected.
- **cost:** One inexpensive planning call plus ordinary relay/browser operations; cryptographic tokens and policy checks dominate neither latency nor API cost.
- **security:** Use least-privilege, single-purpose, expiring capability tokens bound to recipient identity and exact resource/action. No credential or cookie export. Require physical pendant confirmation for creation and revocation, log every attempt, and make sensitive actions impossible even if the recipient asks for them.
- **missing:** A capability-token service enforced at the browser and Mac action layers; Recipient identity and invitation/revocation workflow; Browser session isolation for delegated work; A pendant-friendly redacted scope display and confirmation protocol


## What it asked for

_Nothing._
