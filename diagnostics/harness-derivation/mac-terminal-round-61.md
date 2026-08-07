# Harness derivation — mac-terminal — round 61

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **granted Mac diagnostics** — The newly granted mac_read_diagnostics, mac_readonly_diagnostics, mac_readonly_diagnostics_impl, and safe_mac_command interfaces all exist in schema but return an implementation-missing error, so no live Mac validation is possible this round.
  - evidence: Parallel calls in Round 61 to each tool returned: 'This tool was granted a schema but has no implementation yet. Report what you would have done with it.'

## Capabilities it proposed

### "When something you did on my Mac fails, tell me what happened and give me the safest concrete way to finish it."
- **useful because:** Today a failed unattended shell or browser step leaves the owner to reconstruct context. This creates a spoken, evidence-backed incident packet: exact task chain, failure point, relevant Mac/browser state, and a proposed next step, while preserving the owner's maximum-access policy and avoiding an opaque retry.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use the cheaper background model to assemble and classify the transcript; use realtime only when the owner asks from the pendant and needs a concise explanation. Escalate to the stronger model only for ambiguous multi-surface diagnosis.
- **latency:** Background incident packet within 5 seconds of terminal failure; pendant answer under 2 seconds when the transcript is already indexed. A fresh browser/Mac verification may take up to 15 seconds.
- **cost:** About $0.002–$0.02 per incident depending on transcript size and whether a browser verification is needed; storage/indexing and browser re-check dominate, not the short explanation.
- **security:** Receipts can expose private command output, paths, authenticated URLs, and account data. Keep raw evidence on the Mac, send redacted excerpts and hashes to relay, require explicit owner request before fetching full output, and never execute a suggested retry automatically. Expire incident packets.
- **missing:** Shell execution transcript with bounded stdout/stderr, exit classification, and correlation IDs; Cross-node incident packet API and relay retrieval; A Mac-side verification step that can check postconditions without changing state; Dashboard/pedant rendering for evidence, proposed next step, and explicit retry

### "Do this when the right moment arrives: wait until my Mac is idle, I'm not in a meeting, the right logged-in page is open, and I'm on trusted Wi‑Fi; then carry out the reversible steps and tell me what happened."
- **useful because:** The owner cannot currently express a multi-surface condition and have the system safely wait for it. This would prevent actions at disruptive or stale moments—for example, preparing a form only when its authenticated tab is present and the owner is not presenting—while allowing the relay to keep watching after the Mac temporarily disconnects.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheap background model to compile the request into typed predicates and a step plan. Use realtime only for the initial spoken request and completion alert; use the stronger model only when a predicate is ambiguous or the page changed materially.
- **latency:** Predicate evaluation every 15–60 seconds, with event-driven wakeups from browser heartbeat and Mac state changes. After all conditions hold, begin within 2 seconds and provide a completion or refusal notice within 10 seconds.
- **cost:** Roughly $0.001–$0.01 per armed task; most cost is one-time plan compilation and occasional semantic page re-checks. State monitoring should be local/event-driven rather than model-polled.
- **security:** The system observes meeting state, network identity, active windows, and authenticated page metadata. Keep raw state on the Mac/browser, expose only predicate results to the relay, encrypt the durable plan, expire it automatically, and never treat a changed page or untrusted network as satisfying the original predicate. The action plan must remain reversible and produce a receipt.
- **missing:** A durable conditional-trigger engine distinct from clock-based routines; Typed Mac predicates for idle/lock/presentation/audio/network state; Browser predicates based on authenticated tab identity and semantic page fingerprint; Relay-side lease, reconnect, deduplication, and expiry handling; Pendant notification and dashboard controls to pause, inspect, or cancel an armed task


## Changes it proposed to its own stack

### `mac-harness` — Add an append-only, observability-first shell execution transcript around the existing unrestricted FULL_CONTROL runShell path (do not gate or narrow it): before launch record a command fingerprint, cwd, selected non-secret environment metadata, timeout, and parent job/plan IDs; during execution sample bounded stdout/stderr and child-process milestones; after exit record status, duration, signal, output hashes, files/artifacts explicitly reported by the command, and a normalized failure class. Emit the same receipt ID to the relay, pendant interaction, browser session, and Mac journal. Add a 'diagnose/retry' operation that can suggest a corrected command from the transcript but never silently replays it, plus automatic redaction of token-shaped values in logs.
- **owner gets:** When something runs unattended while the owner is away, they can tell exactly what happened, why it failed, what it touched, and whether a retry is safe instead of hearing only 'command failed.' Cross-surface IDs let a spoken pendant request, browser tab, and Mac process be traced as one task, which is not provided by basic action receipts.
- effort: Medium: wrapper and journal schema in local-agent, bounded stream capture, secret redaction tests, process-group metadata, and relay/pendant receipt propagation. No executor policy change.  ·  risk: Output may contain sensitive data even after redaction; cap size, redact common credentials, and permit per-job purge. Process sampling can miss short-lived children. Hashes prove sameness, not semantic safety. Retry suggestions could be wrong, so retries remain explicit commands and retain the original transcript.
- cost: Negligible API cost; local disk roughly 2–20 KB per command after bounded capture, with configurable retention and compression. Small CPU overhead for hashing and process sampling.  ·  latency: ~10–50 ms startup/finalization overhead; streaming is asynchronous and should not materially delay commands.
- security: Improves accountability without restricting owner-approved maximum access. Store raw output only locally by default; send summarized/redacted receipt cross-node. Treat command text, cwd, and artifact paths as sensitive metadata.
- depends on: Existing action receipts/journal (chg-5fc73ce3); Durable job IDs and cross-surface correlation IDs; A real implementation of the newly granted read-only diagnostics is helpful for validation but not a runtime dependency


## What it asked for

_Nothing._
## Its own summary

Recorded a new conditional, multi-surface automation capability: the owner can arm a reversible task that waits for simultaneous Mac, meeting, browser-session, and trusted-network predicates, survives reconnects, then executes and reports. This is distinct from clock-based routines and ordinary durable jobs.

**Biggest unknown:** The existing routine and browser infrastructure may already contain partial predicate support, but the available tools were removed before I could inspect their contracts; the proposal explicitly identifies the missing conditional-trigger and cross-surface lease layer.

