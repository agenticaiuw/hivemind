# Harness derivation — mac-terminal — round 49

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac diagnostics grant** — All newly granted mac_read_diagnostics, mac_readonly_diagnostics, and mac_readonly_diagnostics_impl tools return 'no implementation yet', so bounded host reconnaissance is unavailable despite schemas being granted.
  - evidence: Three parallel calls in round 49 each returned error: This tool was granted a schema but has no implementation yet.

## Capabilities it proposed

### "“I’m away from my Mac—tell me what happened with the task I asked for, and if it failed, explain why and prepare the next step.”"
- **useful because:** Today a long-running Mac action can leave the owner with a thin completion message. This gives a real, evidence-backed remote incident report: what the Mac did, what the browser returned, where it stopped, and what can safely be resumed. It is useful precisely because the pendant, relay, Mac, and browser each see different parts of the task.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard-ux
- **model tier:** Background/cheap model compiles the job journal and browser evidence; realtime model is used only to answer the owner's spoken follow-up. Mac-planner performs any explicitly requested continuation.
- **latency:** Initial spoken status under 2 seconds from cached journal; evidence compilation 5–20 seconds in the background. Continuation begins only after the owner asks for it.
- **cost:** About $0.01–$0.05 per incident report depending on captured output and browser evidence; most cost is summarizing logs, not realtime conversation.
- **security:** The report may include private URLs, shell output, and authenticated page titles. Relay should receive only the selected evidence capsule, not raw environment values or full page contents. Any continuation that mutates files, sends messages, or submits browser forms must remain an explicit owner request; the report itself is read-only.
- **missing:** Structured shell execution envelopes with exit/timeout/stdout-stderr/cwd provenance; A durable cross-surface incident record linking Mac action IDs, browser command IDs, and relay pipeline/job IDs; A resume planner that skips completed action IDs and presents a concrete continuation plan; Pendant-accessible job status query and concise failure speech rendering

### "“After you do something for me, prove that the intended real-world result actually happened, and keep checking until it does or tell me exactly what is stuck.”"
- **useful because:** Today the system can report that a command, click, or form submission ran, but the owner cannot reliably ask whether the outside-world outcome followed. A browser submission can be rejected after navigation, a Mac export can produce a corrupt or misplaced file, or a remote service can accept a request but leave it pending. This capability closes the gap between action receipts and truth: it verifies the resulting state across the authenticated browser, local Mac artifacts, and relay-delivered evidence, then stops with a precise discrepancy instead of claiming success.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action → dashboard-ux
- **model tier:** Use a cheap background model for extracting expected postconditions, polling and comparing evidence; use realtime only when the owner asks for a spoken status or a judgment on an ambiguity. Faculty-perception establishes observed state, faculty-judgement decides whether it satisfies the stated goal, and faculty-action performs only an explicitly permitted repair.
- **latency:** Immediate acknowledgment under 2 seconds. First verification within 5–15 seconds, then bounded background checks according to the service's cadence; speak only on success, meaningful change, timeout, or ambiguity.
- **cost:** Roughly $0.01–$0.08 per verification episode, dominated by authenticated browser reads and repeated checks; local file/hash checks are effectively free.
- **security:** Verification may read private pages and local files. Store only normalized claims, source URLs/paths, timestamps, and evidence hashes rather than full page contents. Never treat a matching visual message alone as proof when a stable identifier or resulting artifact is available. Repairs, resubmissions, cancellations, or messages require explicit owner confirmation; polling must honor site load limits and quiet hours.
- **missing:** A first-class postcondition schema with expected state, evidence sources, freshness, and expiration; Cross-surface evidence correlation joining browser result IDs, Mac artifact hashes, and relay delivery receipts; A verifier that distinguishes accepted, completed, rejected, pending, and unverifiable outcomes; Durable watch-until state with bounded retries, backoff, and owner-visible discrepancy explanations; A dashboard and pendant status vocabulary for outcome confidence rather than binary action success


## Changes it proposed to its own stack

### `mac-harness` — Add a structured execution envelope around every run_shell dispatch without changing FULL_CONTROL_MODE or blocking anything. Persist cwd (resolved path), argv/command hash, start/end timestamps, exit code/signal, timeout classification, stdout/stderr separately with bounded tails plus byte counts, environment fingerprint (names and hashes only, never values), and a small post-failure probe (cwd existence, executable lookup, disk space, network reachability only when the command itself attempted network). Attach this envelope to the existing action receipt and expose it through /jobs/:id/receipts, /journal, and the relay-facing job completion event. Add a retry hint classifier for not-found, permission, timeout, and transient network failures; hints are advisory and never auto-retry or refuse execution.
- **owner gets:** When a Mac task fails—or succeeds in the wrong place—the owner gets an honest explanation instead of 'command failed'. The agent can recover from wrong-directory and missing-tool mistakes quickly, and the pendant can report exactly what ran while the owner was away. This directly prevents the repeated project-location dead ends without reducing the owner's maximum-access policy.
- effort: Medium: executor wrapper, receipt schema migration, bounded output storage, four failure probes, dashboard/journal serialization, and tests for timeout/nonzero/oversized output.  ·  risk: Command output can contain secrets; redact known credential patterns and keep only bounded tails, with configurable retention. A probe must never alter the command result. Large output and malformed encodings need defensive handling. Existing receipts remain backward-compatible when the envelope is absent.
- cost: Negligible API cost; modest local disk/D1 growth bounded by tail limits and retention. Small CPU overhead per shell action for hashing and probes.  ·  latency: Near-zero for success; roughly 50–300 ms for failure probes, with strict per-probe deadlines.
- security: Improves auditability but creates another place where output could leak. Store command text and environment names, never environment values; redact tokens/keys and apply the existing audio/job retention policy to envelopes.
- depends on: chg-5fc73ce3 receipt/undo implementation; A bounded read-only diagnostics implementation for post-failure probes


## What it asked for

_Nothing._
## Its own summary

Recorded a new capability: outcome verification across Mac artifacts, authenticated browser state, and relay delivery. The owner can ask the system to prove that the intended result happened, continue bounded verification while pending, and report exact discrepancies instead of confusing an executed action with a completed outcome. Required changes include postcondition schemas, cross-surface evidence correlation, outcome-state classification, durable bounded verification, and owner-visible confidence/status vocabulary.

**Biggest unknown:** The diagnostics tools granted earlier remain unimplemented, so the exact available Mac evidence sources and performance limits are unknown.

