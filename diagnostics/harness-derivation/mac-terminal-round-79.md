# Harness derivation — mac-terminal — round 79

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When something I asked takes multiple steps, show me one trustworthy timeline of what the pendant heard, what the relay decided, what the Mac or browser actually did, and what remains undone — with a one-tap way to retry only the failed step."
- **useful because:** Today job receipts exist on the Mac, but the owner must reconstruct a multi-surface action from separate job records, browser command IDs, and audio/voice events. A cited timeline would make unattended work understandable and safely recoverable without repeating successful or irreversible steps.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use the realtime tier only to acknowledge the pendant request and speak a short status; use a cheaper background model (or deterministic reducer) to merge event records, classify the next retry, and generate the dashboard timeline.
- **latency:** Acknowledge within 1 second; append each event within 2 seconds; background reconciliation under 10 seconds after a job completes. Retry should be explicit and only dispatch a selected failed action.
- **cost:** Usually <$0.01 per job with deterministic event reduction; <$0.03 when a background model must summarize ambiguous failures. Storage is small JSON events plus existing receipts; dominant cost is any model-generated explanation, not transport.
- **security:** The timeline may contain private URLs, shell commands, file paths, and authenticated-page snippets. Keep raw evidence on the Mac/relay, send the pendant only a redacted status, encrypt and TTL event bundles, and require confirmation before replaying any action marked irreversible. Never infer success from a model summary when a receipt or browser result is absent.
- **missing:** A shared event envelope with correlationId, parent step, source surface, monotonic timestamp, redacted payload, and receipt/command/job references.; Relay-side append-only event journal and reducer that joins POST /pipeline/events, Mac job receipts, and browser results.; A retry endpoint that accepts a specific failed step and idempotency key, rather than rerunning the whole plan.; Dashboard timeline and pendant status summaries with explicit unknown/stale states.

### "While I’m focused, quietly decide whether a new Mac or browser notification is worth interrupting me: use what app or page it came from, my current calendar context, and urgency; tell me immediately on the pendant only when it truly matters, and leave everything else in a review queue."
- **useful because:** The owner currently has to notice and triage interruptions themselves. A Mac-only notifier cannot know the owner’s wearable availability or relay context, while the pendant cannot see desktop notifications or authenticated browser state. Combining all surfaces provides attention protection rather than another generic briefing.
- **path:** mac-planner → mac-vision → browser-extension → relay → pendant → dashboard
- **model tier:** Use deterministic rules for meeting/focus state, sender/domain, and notification metadata. Use the cheaper background tier to rank ambiguous items; reserve realtime for the short pendant alert after a high-confidence urgent result.
- **latency:** Capture and classify within 2 seconds of a notification; pendant alert within 3 seconds for urgent items. Queue low-confidence items without interrupting. Dashboard review can update within 30 seconds.
- **cost:** Near-zero model cost for common rule matches; roughly $0.005–$0.02 per ambiguous notification using a small background call. Main costs are a Mac notification observer and compact encrypted event storage.
- **security:** Notification text and authenticated page titles may contain private work or health information. Keep raw payloads on the Mac, transmit only a minimized classification and short redacted explanation to the relay/pendant, encrypt the queue, support per-app exclusions and quiet hours, and expire raw evidence quickly. Never open a browser page or send a response as a side effect.
- **missing:** A Mac notification observer that emits normalized events without stealing keyboard focus or recording screen/audio.; A shared focus/availability state combining calendar, active app/window, pendant connection, and explicit do-not-disturb commands.; A privacy-preserving urgency classifier with per-source policies, deduplication, and feedback (“important”/“not important”).; A relay push route to the pendant plus a durable review queue and dashboard controls for exclusions, retention, and correction.; A browser-extension event bridge for meaningful authenticated-site alerts that do not appear as native Mac notifications.


## Changes it proposed to its own stack

### `mac-harness` — Add a content-addressed shell transcript recorder inside the existing FULL_CONTROL executor. For every run_shell action, persist argv/command, resolved cwd, start/end timestamps, timeout, exit code, signal, bounded stdout/stderr, and SHA-256 hashes of full streams; redact environment secrets and tokenize likely credentials before the relay sees them. Link the transcript to the existing actionReceipt/actionId and relay correlation ID, expose a streaming tail plus a compact failure classification, and garbage-collect raw output by TTL while retaining hashes and summaries.
- **owner gets:** When the Mac says a job failed, the owner can see whether it timed out, used the wrong directory, lost network, or returned a nonzero result instead of asking the agent to guess and rerun. It also makes the deliberate unrestricted shell trustworthy through visibility without adding gates or reducing capability.
- effort: Medium: executor wrapper, encrypted local transcript store, redaction tests, GET transcript/tail routes, and dashboard rendering. No planner policy change required.  ·  risk: Command output can contain credentials or sensitive file contents; redaction can miss novel formats, so keep raw transcripts local by default and apply short TTL/size caps. Avoid replaying transcripts as commands. If recording fails, execution must still complete and the receipt must say observability is partial.
- cost: Negligible model/API cost; roughly tens of KB per ordinary command and bounded to a configurable per-job quota. Hashing and local append are low CPU overhead.  ·  latency: Typically <20 ms overhead before the command and buffered writes after completion; streaming tail adds small local I/O only.
- security: Improves auditability while preserving FULL_CONTROL_MODE. Raw stdout/stderr stay on the Mac unless explicitly requested; relay receives redacted bounded data and hashes. No new authorization gate.
- depends on: Existing actionReceipts linkage (chg-5fc73ce3); A local durable journal/TTL sweeper; Read-only authenticated observability route for transcript metadata and tails


## What it asked for

_Nothing._
## Its own summary

Discovered the newly granted Mac diagnostic interfaces, but all three return “schema granted, no implementation yet,” so no live host facts could be collected this round. The existing Mac receipt system is strong on per-action undoability but does not join pendant intent, relay decisions, browser command IDs, and Mac execution into one owner-readable causal chain. I recorded two forward proposals: (1) a cross-surface correlated execution timeline with selective retry, and (2) a bounded, redacted, content-addressed shell transcript linked to action receipts—improving observability without violating the owner’s deliberate FULL_CONTROL_MODE/no-gates policy.

**Biggest unknown:** Whether the relay already has an append-only event journal and correlation-ID contract connecting /pipeline/events, /execute job IDs, browser command IDs, and pendant audio events. The granted diagnostic tools also need an implementation before I can report current OS/process/network state.

