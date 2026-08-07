# Harness derivation — mac-terminal — round 40

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac diagnostics grant** — The granted mac_read_diagnostics schema is present but has no implementation yet; a call for os_version, hardware_model, current_user, disk_space, and local_agent_health returned an implementation error. Therefore I cannot verify live host or agent state through the narrow diagnostic tool this round.
  - evidence: mac_read_diagnostics call returned: 'This tool was granted a schema but has no implementation yet.'

## Capabilities it proposed

### "“If the Mac work fails while I’m away, fix the harmless failures automatically and tell me exactly what ran, what failed, and what I need to do.”"
- **useful because:** Today unattended shell work can leave the owner with an opaque failure and no way to distinguish a lost connection from a command that partially changed the machine. This joins the pendant’s request/notification, relay’s durable job state, Mac execution, and browser session context when a failure involves a logged-in page.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheap background model or deterministic classifier for exit codes, timeouts, and known dependency failures; invoke realtime only when the owner asks follow-up questions or approves an ambiguous recovery. The browser extension contributes authenticated-page evidence but never retries an unknown submit.
- **latency:** Acknowledge on the pendant immediately; retry eligible idempotent work within seconds. Deliver a concise completion/failure notification in under 30 seconds for normal commands; deeper diagnosis can continue asynchronously.
- **cost:** Usually <$0.01 per invocation: local execution and deterministic classification dominate, with a small background-model call only for an unfamiliar failure. Realtime cost is reserved for conversational follow-up.
- **security:** The report must not read like proof that a mutation was undone: include exit status, receipt, and explicit partial-effect/unknown state. Output and authenticated page content may contain secrets; keep raw artifacts on the Mac, send only redacted tails/digests and cited URLs to relay, and require explicit owner confirmation before any browser submission or irreversible retry.
- **missing:** Execution capsules with exit code, bounded redacted output, cwd, timeout, and failure class; Explicit opt-in idempotency metadata and a retry worker; Relay notification that can reference capsule/job IDs and distinguish partial success; Browser-side page-state checkpointing for failures after navigation or form fill; Dashboard view of command timeline, retry attempts, and undoability

### "“When something went wrong, show me a private, replayable movie of what every part of the pendant, relay, Mac, and browser believed happened, then let me ask ‘what if we retry just that step?’ without touching the real system.”"
- **useful because:** The owner currently gets separate action receipts and job statuses, but cannot reconstruct a causal incident across devices or safely test a recovery. A replayable incident view would turn opaque partial failures into an understandable, reviewable event, especially when the owner was away from the Mac.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Use deterministic event stitching, snapshots, and a local simulator for the replay. Use a cheap background model only to narrate the timeline and suggest candidate recoveries; reserve realtime for the owner's spoken follow-up.
- **latency:** Capture is synchronous with each event (milliseconds). Build the incident timeline within 5 seconds after completion; simulation of a proposed retry should return within 10 seconds without executing anything.
- **cost:** Low: event stitching and simulation are local. A short narration costs roughly <$0.01 with a background model; no realtime call unless the owner asks conversationally.
- **security:** The replay may contain private screen text, authenticated URLs, shell output, and voice metadata. Keep raw frames and output on the Mac, redact secrets, transmit only event summaries by default, and make export a deliberate owner action. Simulation must be strictly side-effect-free and clearly labeled as hypothetical.
- **missing:** A cross-surface event envelope with monotonic timestamps, causal parent IDs, and snapshot references; Content-addressed, local-only before/after snapshots for Mac files/settings and browser DOM regions; A side-effect-free action simulator that can evaluate a retry against captured state; Incident assembly API and dashboard timeline/replay UI; Relay/pendant protocol for requesting and narrating an incident without reopening microphone capture


## Changes it proposed to its own stack

### `mac-harness` — Add an execution-capsule layer around every run_shell and typed Mac action. Persist a bounded, redacted record containing normalized command/argv, cwd, timeout, environment key fingerprint (never values or secrets), start/end timestamps, exit code or signal, stdout/stderr byte counts plus tail/digest, host/app identity, and files/URLs/settings named by the action. Classify failures as transient (timeout/agent disconnect), dependency (missing binary/permission), semantic (nonzero result), or likely destructive/unknown. For transient failures, automatically retry only commands explicitly marked idempotent or read-only; otherwise return a diagnosis and a copyable rerun recipe. Link capsule IDs to existing action receipts, jobs, journal, and relay status, with retention/redaction controls.
- **owner gets:** When a voice request fails after the owner walks away, the system can explain what actually happened instead of saying only “failed,” retry harmless status work, and provide an exact rerun or recovery path. This makes unattended Mac work dependable without reducing the owner's deliberately unrestricted access.
- effort: Medium: executor wrapper and schema, redaction/digest utility, bounded artifact storage, failure classifier, retry worker, and dashboard/relay rendering; add integration tests for timeout, nonzero exit, disconnect, and secret-containing environments.  ·  risk: Command output can contain private data, and even bounded tails may expose secrets; redact common token patterns and make retention configurable, with an explicit raw-output opt-in. Misclassifying a command as idempotent could duplicate an external effect, so retry eligibility must be opt-in metadata rather than inferred from text. Capsule persistence itself can consume disk; enforce byte/age quotas and degrade to metadata-only.
- cost: Negligible model cost. Small local disk writes per action (typically 2–20 KB metadata/tails); no extra cloud call unless the relay requests diagnosis. A cheap background classifier can handle known failure classes; use the expensive model only when diagnosis is ambiguous.  ·  latency: ~1–5 ms local bookkeeping on success; retries add latency only for explicitly idempotent transient failures. Relay response can stream the initial failure immediately while diagnosis/retry continues.
- security: Improves auditability but creates a new sensitive artifact. Store locally, encrypt/permission it like job history, redact env/output, hash rather than retain full files, and never transmit raw stdout to the relay by default.
- depends on: Existing action receipts and job/journal IDs (implemented); A bounded local capsule store and redaction utility; Explicit idempotency metadata on action plans; Relay/dashboard support for capsule summaries


## What it asked for

_Nothing._
## Its own summary

Round 40 produced a new Mac-harness proposal beyond implemented receipts: execution capsules that capture redacted command context, exit/signal, bounded output digests, failure classes, and opt-in idempotent retries, linked across jobs/journal/relay. I also proposed the owner-facing cross-surface capability: harmless failures are repaired while away and the pendant reports exactly what ran, what failed, and whether effects are partial or unknown. The granted mac_read_diagnostics tool was tested but is still a stub, so live host/agent verification remains unavailable.

**Biggest unknown:** Whether the current executor/result schema already exposes exit code, cwd, timeout, and stdout/stderr for run_shell; the peer was asked, but no reply is available this round. I still need the diagnostics tool implementation and the capsule/retry worker plus relay/dashboard rendering.

