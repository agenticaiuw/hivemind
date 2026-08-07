# Harness derivation — mac-terminal — round 143

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“This CI failure email looks bad—investigate it and prepare the smallest fix, but don’t push or send anything.”"
- **useful because:** The owner currently has to bridge Gmail, the GitHub run, and the local checkout manually. The wearable can identify the incident, Safari can open the authenticated run and collect logs, the Mac terminal can inspect the matching branch/tests and run focused reproduction, and the relay can return one evidence-backed diagnosis plus a reviewable patch/diff. It turns a noisy failure notification into a ready-to-review fix without taking an irreversible step.
- **path:** relay-realtime → browser-extension → mac-terminal → mac-planner → pendant
- **model tier:** background for email/run extraction and deterministic repo/test commands; planner only to reconcile browser evidence with terminal output; realtime only for the spoken result
- **latency:** 30–90 seconds for first diagnosis; longer tests continue as a durable Mac job and the pendant gets a completion beacon
- **cost:** Usually one background call plus a short planner reconciliation (roughly 3–8k input tokens total); terminal and browser work dominate wall time, not model cost
- **security:** Authenticated Gmail/GitHub content and local source stay on the Mac/browser bridge; never transmit full logs when cited excerpts and hashes suffice. Do not push, open a PR, or send mail without an explicit later request.
- **missing:** incident correlation contract linking a Gmail message, authenticated run URL, checkout/branch, and local job; focused test/reproduction recipe with bounded resource limits; diff artifact and cited evidence bundle exposed to the review UI

### "“Before I run this command, tell me what it is likely to change or break.”"
- **useful because:** A terminal command has consequences outside the shell: open Safari tabs may contain the deployment or issue it affects, the checkout may have uncommitted work, and recent CI history can reveal blast radius. The Mac computes a dry-run/state diff, browser reads only already-open authenticated issue/deploy context, relay reconciles conflicts, and the pendant speaks a compact impact preview. This is a decision aid, not an approval gate, and it works even with the owner's maximum-access policy.
- **path:** mac-terminal → mac-planner → browser-extension → relay-realtime → pendant
- **model tier:** deterministic for git/status/command classification and structured diffs; background for extracting relevant browser and CI context; planner only when sources disagree
- **latency:** Under 5 seconds for local-only commands; under 20 seconds when authenticated browser context is relevant
- **cost:** Local status path can be zero-model; background reconciliation generally 1–3k input tokens; planner escalation is uncommon
- **security:** The command is not executed by this capability. Shell text and environment-sensitive paths remain local; browser content is limited to the selected open tabs. Present uncertainty and stale-source timestamps rather than claiming safety.
- **missing:** non-executing shell inspection/impact analyzer that understands argv, cwd, git diff, and declared side effects; cross-source impact graph for local checkout ↔ open issue/CI/deploy tabs; compact spoken impact schema with confidence and stale warnings

### "“I’m holding the pendant—capture a health report for this Mac and the pendant/bridge, and tell me if anything is actually disconnected.”"
- **useful because:** This is actionable today while both boards are USB-attached, without pretending LTE registration exists. A button/voice request makes the Mac collect serial-port presence, bridge/pendant heartbeat, local-agent health, battery/network, and recent job state; the relay correlates timestamps and the pendant/ESP32 speaks a short truthful report. It replaces guesswork such as 'online' flags that can be stale and gives the owner an immediate physical-link diagnosis.
- **path:** pendant → mac-terminal → mac-planner → relay-realtime → unified
- **model tier:** deterministic diagnostics and correlation first; background summarizer only for a human sentence; realtime for the final spoken response
- **latency:** 2–5 seconds for USB and agent health; up to 10 seconds if serial devices need a fresh probe
- **cost:** Zero LLM calls for structured checks; at most a few hundred background tokens for wording. USB probing and serial handshake dominate.
- **security:** Report device identifiers only as needed, never serial payloads or unrelated shell output. Distinguish USB-present, process-alive, heartbeat-fresh, and relay-registered states; do not infer LTE from USB presence.
- **missing:** implemented bounded USB serial inventory and handshake route for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; shared freshness/connection-state schema consumed by relay and pendant; offline-capable pendant request/response framing over the existing USB path

### "“What changed on my Mac and in my open browser sessions since yesterday that might matter to me?”"
- **useful because:** Today the owner must inspect many unrelated signals manually. The Mac can compute meaningful deltas in repositories, applications, connectivity, and local jobs while Safari contributes changes from already-open authenticated pages; the relay deduplicates them and the pendant speaks only items with a plausible consequence. This is a personal change radar, not a generic morning briefing or page watch.
- **path:** mac-terminal → mac-planner → browser-extension → relay-realtime → pendant
- **model tier:** deterministic local/browser fingerprints first; background model for clustering and importance ranking; realtime only for delivery
- **latency:** 10–30 seconds on demand; background snapshotting can happen hourly without realtime inference
- **cost:** Most snapshots are hashes and metadata; approximately 1–4k background input tokens only when deltas exist
- **security:** Keep file contents and authenticated page text local unless selected for explanation; expose paths, URLs, timestamps, and confidence rather than secrets. The owner chooses watched folders and tabs.
- **missing:** cross-surface baseline snapshots with owner-configurable scope and retention; semantic diffing for local job/app/repository state alongside browser fingerprints; deduplication and consequence ranking that distinguishes routine churn from actionable change

### "“Did anything I just ran expose a secret or personal data outside this Mac?”"
- **useful because:** The current unrestricted shell is intentional, but the owner has no practical way to know whether a command, browser action, or generated artifact sent credentials, tokens, private files, or identifying data to an external destination. A local detector can inspect command arguments, process/network destinations, browser uploads, and job artifacts, then give the pendant a concrete answer and remediation steps without blocking execution.
- **path:** mac-terminal → mac-planner → browser-extension → relay-realtime → pendant
- **model tier:** deterministic secret-pattern, destination, and artifact analysis first; background model only to summarize ambiguous findings; realtime for urgent notification
- **latency:** Under 5 seconds after a completed action; deeper artifact review can continue as a background job
- **cost:** Usually no model call; ambiguous cases cost roughly 1–2k background input tokens. Local event and artifact inspection dominate.
- **security:** The detector must itself never upload raw secrets. Keep raw evidence on the Mac, send only a redacted finding, destination, confidence, and remediation. It should warn, not silently modify or revoke anything.
- **missing:** local process/network/upload observation tied to Mac and browser job IDs; redaction-safe secret and personal-data classifier with destination provenance; cross-surface artifact lineage from shell output to browser uploads or relay storage; remediation actions such as local deletion, credential rotation draft, or browser tab closure

### "“What did you and the other surfaces actually do for me today, and what changed in the outside world?”"
- **useful because:** Current job records are fragmented by Mac, browser, relay, and wearable, so the owner cannot reliably distinguish planned, attempted, completed, failed, or externally effective actions. A spoken request should produce one chronological, evidence-linked ledger: commands run, pages read, drafts created, messages sent, files changed, and actions that had no effect. It should include gaps and stale connectivity instead of inventing continuity.
- **path:** relay-realtime → mac-terminal → mac-planner → browser-extension → pendant → unified
- **model tier:** deterministic event join and receipt status first; background summarization for the short narrative; planner only for conflicting or missing evidence
- **latency:** Under 10 seconds for a day of normal activity; older periods can be asynchronous
- **cost:** Low: event joining is deterministic; approximately 1–3k background input tokens for compression and conflict wording
- **security:** The ledger is highly sensitive. Store full evidence locally or encrypted; relay receives typed events and redacted excerpts. Clearly separate observed effects from intended actions and mark browser/private data access.
- **missing:** globally unique action/event IDs across pendant, relay, Mac, and browser; effect-state vocabulary covering planned, started, completed, failed, canceled, unknown, and externally-confirmed; tamper-evident local ledger with retention and owner export/deletion controls; reconciliation for offline USB periods and stale browser heartbeats


## Changes it proposed to its own stack

### `mac-harness` — Add a failure-recovery loop specifically for shell jobs: after a nonzero exit or timeout, classify the failure into environment, dependency, transient network, test assertion, permission, or unknown; collect only targeted diagnostics; generate up to two alternative commands with their expected side effects; run only alternatives that are mechanically reversible or read-only; then attach a concise 'recovered / not recovered / needs owner' result to the original job. Never silently rerun a mutating command.
- **owner gets:** A failed command becomes progress instead of a dead end: common missing-directory, stale-process, or transient-network failures self-diagnose, while genuinely risky or ambiguous failures arrive with a concrete next step and evidence.
- effort: Medium-high: failure taxonomy, bounded retry planner, command-side-effect metadata, and job linkage.  ·  risk: A supposedly read-only retry can still be wrong; enforce a conservative allowlist for automatic alternatives and stop on uncertainty. Cap attempts, runtime, and network retries; preserve the original failure unchanged.
- cost: Most cases deterministic; occasional background model call for classification/alternative generation, roughly 1–3k input tokens.  ·  latency: Adds 0–30 seconds only after failures; successful commands are unchanged.
- security: No new authority beyond existing FULL_CONTROL_MODE. Diagnostics must redact secrets and avoid copying full environment variables to relay.
- depends on: Existing GET /jobs and job receipts; Existing mac_run_actions run_shell execution; A structured side-effect classifier for candidate retry commands; Durable job linkage for parent and recovery attempts


## What it asked for

_Nothing._
## Its own summary

Recorded three new owner-facing capabilities: a cross-surface change radar, post-action privacy/exfiltration reporting, and a unified daily AI effect ledger. Each names the Mac/browser/relay/pendant behavior and the missing implementation needed; none requires narrowing FULL_CONTROL_MODE.

**Biggest unknown:** Whether the existing event and receipt records contain enough stable identifiers to join Mac, browser, relay, and pendant activity without adding a new cross-surface event identity.

