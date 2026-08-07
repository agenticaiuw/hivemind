# Harness derivation — mac-planner — round 69

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If you can’t safely verify a Mac or browser action, tell me what is blocked, leave a resumable task, and finish it automatically when the right device comes back.”"
- **useful because:** Today /observe shows the Mac bridge online but Accessibility untrusted, so UI actions can report success while doing nothing; the browser extension is offline with pending commands. This gives the owner a truthful spoken answer instead of a false completion, preserves the exact intent, and resumes only the incomplete portion when reachability and postconditions are verifiable. It is specifically a wearable-to-relay-to-Mac/browser recovery path, not just a Mac automation feature.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the cheap background model for queue classification, retry scheduling, and receipt summarization; use realtime only for the owner's immediate one-sentence status and follow-up.
- **latency:** Immediate status in under 2 seconds; enqueue in under 1 second; resume on reconnect with bounded exponential backoff. No polling while a surface is offline.
- **cost:** About $0.001–$0.01 per recovery event, dominated by a short realtime response only when speaking to the owner; retries and receipts should be deterministic.
- **security:** Do not transmit page contents or file contents in the spoken error; keep sensitive payloads on the originating device. Preserve owner policy of no approval gate for ordinary actions, but never claim success without a verified postcondition. Destructive actions remain represented as pending exactly as requested, not silently retried.
- **missing:** A durable cross-surface intent record containing action step, idempotency key, required surface, reachability evidence, and postcondition; Mac-side preflight/postcondition adapters for Accessibility, browser connectivity, and typed read-only verification; Pendant/relay event delivery for a compact blocked/resumed/completed notification; Dashboard view of blocked tasks and the concrete fix (for example, grant Accessibility to AI Pendant Agent)

### "“Continue this on my pendant from where I left off on the Mac—read the selected page or document aloud, let me interrupt with a question, and resume at the same paragraph later.”"
- **useful because:** Today the Mac, browser, relay, and pendant can each handle pieces, but none shares a durable semantic playback position tied to the exact source selection. This would let the owner move from desk reading to hands-free listening and back without losing their place, while questions remain anchored to the passage they actually heard.
- **path:** mac-bridge → browser → relay → pendant → dashboard
- **model tier:** Use a cheaper background model to segment and index the source and maintain paragraph offsets; use realtime only for interruption questions and low-latency spoken replies.
- **latency:** Start playback within 3 seconds for a local file or already-open tab; resume position within 1 paragraph after reconnect. Question answers should begin within 1.5 seconds when the cached passage is sufficient.
- **cost:** About $0.002–$0.02 per session, dominated by speech synthesis and occasional passage summarization; position updates and local indexing are negligible.
- **security:** Keep authenticated page text on the Mac/browser unless the owner explicitly asks for remote processing. Bind a playback token to the browser tab/document hash and expire it when the source changes. Never speak secrets from an unrelated tab; show source title and paragraph provenance in the dashboard.
- **missing:** A shared source-anchor format: document/tab identity, content hash, paragraph or text-range offset, and spoken-audio timestamp; Mac/browser extraction of the current selection or readable region without requiring focus theft; Relay audio queue metadata and durable per-owner resume position; Pendant controls/events for pause, rewind one paragraph, ask-a-question, and resume; A source-change detector that marks an anchor stale instead of silently continuing from the wrong text


## Changes it proposed to its own stack

### `integration` — Add a cross-surface execution attestation protocol. Before each UI/browser step, the Mac bridge and browser bridge publish a short-lived capability lease (binary identity, permission state, tab/session identity, and probe timestamp). Each action receipt must reference the lease and include an independently checked postcondition; if the lease expires or the postcondition is absent, the step is recorded as unverified and the durable job pauses at that exact step. The relay can then send the pendant a compact blocked/resume event and the dashboard can show the one concrete repair. On reconnect, retry only the unverified step using its idempotency key, never the already-attested steps.
- **owner gets:** The owner stops hearing “done” when the AI Pendant Agent lacks Accessibility—as observed now—and can recover browser work after the extension returns without duplicate clicks, submissions, or file writes. It makes the whole hive truthful even when one node disappears.
- effort: Medium: shared receipt schema and lease endpoint, Mac/browser preflight probes, relay state machine, and dashboard timeline; add failure-injection tests for permission loss, tab replacement, and disconnect during a click.  ·  risk: A stale or overly strict lease could pause harmless work; recover by short leases for UI mutation but allow read-only inspection with a separate lease class. A missing postcondition may create more pauses rather than false success, which is the intended safe failure. No action is blocked by an approval gate; this is verification and retry control.
- cost: Negligible API cost (mostly deterministic JSON and probes); roughly 1–3 KB of receipt metadata per action, with retention/compaction required.  ·  latency: Adds roughly 50–200 ms for a local preflight and postcondition check; avoids 45-second browser blocking waits by making progress resumable.
- security: Capability leases limit replay across devices and bind receipts to a binary/session, while avoiding page-content export. Lease metadata may reveal app/tab names, so retain it briefly and redact URLs in spoken output.
- depends on: Existing action receipts and idempotency journal; A non-blocking browser progress/polling API (the still-open defect in chg-14accc01); Accessibility permission corrected for AI Pendant Agent, or an explicit truthful untrusted state


## What it asked for

_Nothing._
## Its own summary

Discovered the live Mac state and recorded two non-duplicate additions: a user capability for truthful resumable cross-device recovery, and an integration change introducing short-lived capability leases plus independently verified postconditions. Current evidence: Mac bridge online, but AI Pendant Agent Accessibility is untrusted/events are rejected; browser extension is offline with pending commands.

**Biggest unknown:** Whether the owner will grant Accessibility to the exact AI Pendant Agent binary and when the browser extension will reconnect; without those, UI/browser completion cannot be truthfully verified.

