# Harness derivation — unified — round 43

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Before I leave my Mac, tell me whether this request can actually be completed across my private browser and computer; if not, queue only the safe parts and tell me exactly what I must fix."
- **useful because:** The owner gets a reliable go/no-go answer instead of discovering later that the browser is offline or macOS permissions prevent the task. It turns the pendant into a trustworthy preflight for work that crosses devices, while preserving private-page access and never pretending a blocked action succeeded.
- **path:** pendant → relay → mac-bridge → browser → dashboard-ux
- **model tier:** Use the realtime model only to understand the short spoken request and give the immediate spoken verdict; use the cheaper planner/background worker for capability checks, decomposition, queueing, and receipts.
- **latency:** Spoken preflight verdict within 2 seconds when bridge/browser heartbeats are cached; up to 10 seconds for a fresh browser/Mac probe. The owner tolerates a short spoken explanation and a dashboard card with blocked prerequisites.
- **cost:** About $0.01–$0.05 per invocation depending on the realtime turn; most work is deterministic readiness probes and costs negligible D1/relay compute. Avoid sending page contents unless the requested task requires them.
- **security:** Readiness probes expose only device capability, permission, session presence, and freshness—not page contents or credentials. Any queued step is limited to reversible work; browser submission, messages, purchases, and other irreversible actions require an explicit later approval and a fresh readiness check.
- **missing:** The readiness-lease/handoff protocol described above; A durable typed queue that can represent blocked versus safe-to-run steps; A pendant event for spoken status plus explicit approval/cancel; Browser extension reconnect and Mac permission remediation flow; A dashboard preflight card showing each prerequisite, timestamp, and fix

### "Use my logged-in accounts to answer this, but keep the raw pages and messages on my Mac; tell me exactly which facts you had to share with the cloud, if any."
- **useful because:** Today the owner cannot reliably combine pendant voice, private browser sessions, and cloud reasoning while controlling what leaves the machine. This gives them useful account-aware assistance with a default local privacy boundary and an understandable release receipt instead of an all-or-nothing choice between no help and full-page upload.
- **path:** pendant → relay → mac-bridge → browser → dashboard-ux
- **model tier:** Use a cheaper background/local planner for extraction, classification, and evidence minimization; use realtime only for the short spoken request and final response. Escalate to a stronger model only when the owner explicitly permits a specific raw field.
- **latency:** Initial answer in 2–5 seconds for local extraction plus compact reasoning; a raw-content escalation may take another 1–3 seconds and must be announced before it occurs.
- **cost:** Usually lower than today because only compact evidence is sent; approximately $0.005–$0.03 for ordinary requests, dominated by model reasoning rather than transport or storage.
- **security:** Raw page content, credentials, cookies, and unrelated fields stay local by default. Every exception is scoped to a task, field, source, and expiry, with a spoken/dashboard confirmation for sensitive categories. The local Mac remains trusted and must support a global cloud-escalation kill switch.
- **missing:** A local-first field classifier and redaction engine; A typed minimum-evidence envelope understood by relay and planners; Per-task cloud-release confirmation and revocation; An append-only release receipt visible on the dashboard and summarized through the pendant; Relay enforcement rejecting undeclared raw private content


## Changes it proposed to its own stack

### `integration` — Add a cross-surface readiness lease and truthful handoff protocol. Before any job that spans relay, Mac, or authenticated browser, the relay requests a short-lived capability snapshot (bridge heartbeat, Accessibility/Screen Recording readiness, browser session presence, consent state). The planner must attach that snapshot to its plan, classify each step as executable/queueable/blocked, and emit a typed handoff receipt. If a surface disappears mid-job, checkpoint only after a verified result, pause safely, and have the pendant speak the exact blocked step and recovery condition rather than claiming completion. On reconnect, resume from the last receipt with idempotency keys and require fresh approval for any irreversible step.
- **owner gets:** The owner can ask once while away from the desk and trust that the system will either finish, wait, or clearly say what it could not do. Today's live state already shows the Mac bridge online but not ready (Accessibility and Screen Recording missing) and the browser offline with three pending commands; without this protocol, a spoken request can silently stall or be misreported.
- effort: Medium-high: typed readiness schema and lease endpoint in relay, planner precondition enforcement, durable checkpoint/receipt records, pendant status utterances, reconnect tests across browser/Mac loss.  ·  risk: A stale lease could incorrectly permit work; keep leases short, revalidate before every side-effect, and default to blocked. Crashed jobs may remain paused; expose resume/cancel and an operator reconciliation view. No automatic irreversible action after reconnect.
- cost: Small D1/R2 and telemetry overhead; no additional model call for readiness. One compact snapshot (~1–2 KB) per job step.  ·  latency: Adds roughly 50–150 ms for cached readiness and one revalidation before side effects; avoids long silent hangs.
- security: Improves security by making consent and permission state explicit, never exporting page contents in readiness snapshots, and preventing execution when local privacy/permission gates are absent.
- depends on: A durable job/checkpoint store and receipt/undo records; A common typed planner/action schema across relay and Mac local agent; Pendant status/approval event path

### `hardware` — Add a small secure element (for example, an I2C Ed25519/ECDSA device) to the production pendant and bind each pendant identity to a relay pairing record. The pendant signs conversation-start, approval, cancel, and status-ack events locally; the relay rejects replayed or unpaired events and can revoke one pendant without rotating the whole fleet. Keep private keys non-exportable and use the currently free I2C bus.
- **owner gets:** A lost pendant or copied API token should not let someone trigger actions on the owner's Mac or browser. The owner can revoke one wearable and trust that a physical approval spoken or pressed on their pendant is really theirs.
- effort: Medium hardware spin plus firmware driver, provisioning workflow, relay signature verification, and recovery/re-pair UX. Add secure-element fault and battery-brownout tests.  ·  risk: Provisioning mistakes could lock out a legitimate owner; provide a one-time physical recovery pairing flow and relay-side revocation/recovery codes. Added bus failures must fail closed for approvals but still permit non-sensitive status playback.
- cost: Roughly $0.30–$1.50 BOM increase and a few mW only during signing; negligible per-request API cost. I2C is currently free, so no audio-bus contention.  ·  latency: Typically tens of milliseconds per signature, only on control events, not on streaming audio.
- security: Strongly improves device authentication and replay resistance. It does not replace end-to-end audio encryption or Mac/browser permission gates; signatures must cover job ID, action hash, nonce, and expiry.
- depends on: A relay pairing/revocation endpoint with nonce tracking; Firmware control-event signing support; A documented physical recovery/re-pair procedure

### `context` — Build a local-first private-context firewall between the Mac/browser surfaces and the relay. For each task, the local agent should classify page, file, calendar, and message fields, satisfy the plan from on-device extracts where possible, and send the relay only the minimum redacted evidence (field type, normalized value, source reference, confidence, and expiry). Require an explicit per-task escalation when raw content must leave the Mac, record the exact fields released, and make the redaction policy inspectable and revocable from the dashboard.
- **owner gets:** The owner could use the pendant with private mail, health, finance, and logged-in websites without routinely shipping their full pages and documents to a cloud model. They would still get cross-device help, but with a clear answer to “what did you send?” and the ability to revoke future use of a sensitive source.
- effort: High: local classification and extraction library, typed redacted-evidence protocol, relay enforcement that rejects undeclared raw payloads, policy UI, audit records, and fallback behavior for tasks that genuinely need exact text.  ·  risk: Over-redaction can make answers less useful; show the missing field and offer a one-time, narrowly scoped escalation. Misclassification could leak sensitive content; default unknown fields to local-only, encrypt audit records, and provide a kill switch that disables cloud escalation entirely.
- cost: Moderate local CPU/storage and D1 audit overhead; likely reduces model-token cost by sending compact evidence instead of whole pages. No raw private content is retained by the relay unless explicitly approved.  ·  latency: Adds roughly 100–500 ms for local extraction/classification on ordinary tasks; substantially faster and cheaper for large pages because full content need not be uploaded.
- security: Creates a meaningful data-minimization boundary, with field-level release receipts and revocation. It must not be marketed as protection from a compromised Mac; the local agent and its policy store remain trusted components.
- depends on: A typed cross-surface evidence and provenance schema; Local browser/Mac extraction hooks that can classify content before relay upload; Dashboard policy and release-receipt UI; Relay request validation and encrypted audit storage


## What it asked for

_Nothing._
