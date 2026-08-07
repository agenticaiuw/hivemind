# Harness derivation — mac-terminal — round 59

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac diagnostics grants** — The newly granted mac_read_diagnostics and mac_readonly_diagnostics_impl schemas are present but both return 'no implementation yet'; live host reconnaissance still cannot be performed through those interfaces.
  - evidence: mac_read_diagnostics(checks=[os_version,hardware_model,current_user,uptime,network_interfaces,wifi_status,local_agent_health,disk_space]) and mac_readonly_diagnostics_impl(command='whoami') each returned the same no-implementation error.

## Capabilities it proposed

### "When you do something on my Mac, tell me whether it actually worked; if it fails, diagnose and retry safely, and if the Mac disconnects, resume when it returns without repeating completed steps."
- **useful because:** Today shell jobs can run unattended and receipts record outcomes, but a failed or disconnected multi-step task still leaves the owner to interpret partial state. This makes Mac automation dependable while preserving the owner's deliberate maximum-access/no-gate policy: it adds verification and recovery, not blocking.
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay-realtime
- **model tier:** Use the cheap background model for job decomposition, polling, and retry classification; use realtime only to explain a live failure or ask the owner a genuinely ambiguous question. mac-vision is invoked only when a GUI postcondition needs visual confirmation.
- **latency:** Immediate acknowledgement under 1 second; normal shell verification within 2-5 seconds. Disconnect recovery is background polling (for example every 15 seconds, with exponential backoff) and should not consume realtime turns.
- **cost:** Usually <$0.01 per task when typed/shell postconditions are used; the dominant cost is occasional vision or realtime escalation, not polling. Persisting receipts and hashes is negligible.
- **security:** Commands remain unrestricted as the owner requires. Store command text, exit status, stdout/stderr digest, touched paths/apps, and verification evidence in the existing job record; redact environment secrets and avoid copying raw stdout to the pendant. Never silently repeat non-idempotent actions: resume by stable action IDs, and mark an action unknown when the connection drops during execution. Require owner confirmation only for an explicit question about an ambiguous outcome, never as a general gate.
- **missing:** A durable Mac job runner that survives local-agent restarts and reconnects, with stable action IDs and leases/heartbeats; A postcondition schema for shell, app, browser, and vision steps (exit code alone is insufficient); A reconnect protocol from pendant/relay to Mac that returns partial receipts and resumes only unresolved actions; Idempotency metadata and an unknown-outcome state for commands interrupted after dispatch; A compact owner-facing failure summary delivered through the pendant, with full evidence retained in the dashboard

### "After I ask you to do something, let me say “show me everything that changed” and get one trustworthy timeline across my Mac, browser sessions, pendant, and relay—with the exact evidence for each side effect and a way to undo only the changes I choose."
- **useful because:** Today effects are split across Mac job receipts, browser commands, relay jobs, and pendant interactions. The owner cannot answer the practical question “what did that request actually change?” across substrates, nor selectively reverse a subset. A causally linked, owner-readable change ledger would make this hive usable without requiring trust in invisible automation.
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay-realtime → unified
- **model tier:** Use a cheap background model to normalize and causally group structured events; use realtime only to answer a live spoken follow-up. The ledger itself should be deterministic, not model-generated, and the dashboard can render the detailed evidence.
- **latency:** Start speaking a compact summary within 2 seconds for recent jobs; full cross-node correlation may complete in under 10 seconds. Selective undo should report each target's status independently rather than blocking on the whole batch.
- **cost:** Low API cost, typically <$0.01 for normalization and summarization; most work is local indexing and receipt transport. Realtime cost is reserved for the owner's conversational query.
- **security:** The ledger is highly sensitive because it reveals files, URLs, account activity, and device events. Keep raw evidence on the originating device, send the relay only signed metadata and redacted excerpts, encrypt links in transit and at rest, enforce per-owner retention/deletion, and never include secrets or full page text in the pendant response. Undo must use existing reversibility declarations and explicitly report irreversible effects; it must never pretend a browser send or external side effect was reversed.
- **missing:** A shared event envelope and correlation ID propagated from pendant request through relay, Mac, browser, and returned audio; Durable cross-node append-only indexing with signatures, timestamps, source, and evidence pointers; Browser receipts that describe navigation, form mutation, and submission outcomes, not merely command completion; Relay/pendant receipts for queued jobs and delivered audio or notifications; A cross-surface selective-undo coordinator with honest per-effect reversibility and partial-failure reporting; Owner-facing timeline query and compact spoken renderer


## Changes it proposed to its own stack

### `mac-harness` — Add a bounded execution evidence ledger beside action receipts. For every run_shell/run_applescript/GUI action, record a structured outcome envelope: argv or script hash (not secret-bearing raw text by default), exit code, signal, timeout, start/end monotonic timestamps, connection/agent version, stdout/stderr byte counts plus redacted snippets, and declared postcondition checks. Keep full output only as encrypted, size-capped local artifacts with TTL; link artifacts by receiptId. Add a cheap local classifier for timeout, missing executable, permission, network, and unknown-outcome failures, and expose a single per-job timeline endpoint for relay and dashboard.
- **owner gets:** The owner can see exactly why a Mac task failed and whether it changed anything, without paying a model call to reconstruct logs from scattered job fields. It also makes resume/retry decisions honest when a connection drops and lets the system choose a faster specialized remedy instead of rerunning an expensive planner.
- effort: Medium: shared executor wrapper, redaction/TTL store, postcondition adapters for shell and common app actions, and dashboard/relay rendering. No change to FULL_CONTROL_MODE or action authorization.  ·  risk: Output may contain secrets or personal data; default to hashes/redacted excerpts, local-only encrypted artifacts, explicit deletion TTL, and never send full output to the pendant. A classifier can mislabel failures, so it must be advisory and retain raw exit facts. Ledger corruption should never prevent the underlying action result from returning.
- cost: Low storage (bounded per-job artifacts, e.g. 1-10 MB with TTL) and near-zero API cost; saves model tokens by making evidence directly queryable.  ·  latency: Under roughly 10 ms for metadata capture; postcondition checks add only the time of the check. Artifact encryption is asynchronous where possible.
- security: Improves auditability while reducing accidental secret exfiltration through redaction and local retention. Does not narrow shell capabilities or add approval gates.
- depends on: Existing actionReceipts.js and job records; A durable job/timeline endpoint (can initially be implemented over existing /jobs and /logs); A shared secret-redaction library


## What it asked for

_Nothing._
## Its own summary

Discovered the newly granted Mac diagnostic interfaces, but both are still stubs and cannot inspect the host. I recorded that finding. I proposed two useful next steps beyond the existing receipt/undo work: (1) reconnect-safe Mac jobs with postcondition verification, safe resume, and honest unknown-outcome handling across pendant, relay, planner, vision, and browser; (2) a bounded, redacted execution-evidence ledger that makes shell/GUI failures and verification directly queryable without extra model calls. I also notified mac-planner of the contract gap.

**Biggest unknown:** The actual local-agent job lifecycle/timeline and postcondition APIs remain undiscoverable because the granted diagnostics have no implementation, and the durable browser/Mac job runner is still not shipped. What I still need is an implemented read-only diagnostics endpoint plus the durable runner contract (leases, reconnect, stable action IDs, unknown outcome semantics).

