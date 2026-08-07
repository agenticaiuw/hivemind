# Harness derivation — unified — round 91

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Did that actually happen?” — Give me one end-to-end, evidence-backed status for any request I made, including what was attempted on the Mac/browser/relay, what changed, whether it was delivered to my pendant, and what remains; if evidence conflicts, say so instead of guessing."
- **useful because:** Today a Mac job receipt can say completed while the browser is offline, a pipeline artifact is only historical, or the spoken result was never delivered. The owner needs one trustworthy answer without remembering which surface performed the work. This is read-only and makes failures actionable rather than silently reported as success.
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision → mac-terminal → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** background/cheap model for receipt correlation and summarization; realtime only when the owner asks verbally and needs the one-sentence answer
- **latency:** Under 2 seconds from cached indices; up to 10 seconds when reconciling live Mac/browser/pipeline state. No polling loop unless explicitly requested.
- **cost:** About $0.002–$0.01 per status query; dominated by correlation context and any live Mac round trip, not generation.
- **security:** Read-only, but receipts may contain private URLs, snippets, calendar/mail metadata, or command output. Redact secrets and destructive payloads by default; require explicit confirmation before offering a retry of any irreversible step. Persist hashes and provenance, not full private page contents, and retain only per the existing receipt-retention policy.
- **missing:** A durable cross-surface commitment/evidence index keyed by request and idempotency key; A delivery acknowledgement from relay to pendant (not merely an accepted audio artifact); A normalized event schema linking Mac jobs, browser commands, pipeline audio/events, and spoken response IDs; A conflict policy that distinguishes accepted, executed, delivered, heard, and unknown

### "“Mark this for later.” Capture the exact moment across my pendant, Mac screen, and active browser tab, then bring it back when I return to that project or page—showing what I saw, what I said, and why I marked it, without me having to remember where it came from."
- **useful because:** People lose the reasoning behind half-finished work, not just the URL. A durable, privacy-preserving context bookmark would let the owner leave a thought while walking away and recover it at the right computer context days later. This is more than a note or task: it preserves the multimodal state and reconnects it to the project when the owner returns.
- **path:** relay-realtime → pendant → mac-planner → mac-vision → browser-extension → mac-terminal → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Use a cheap background model to extract entities, project/page fingerprints, and a concise explanation; use realtime only to acknowledge the mark and answer a later spoken retrieval request.
- **latency:** Acknowledge the mark in under 1 second; snapshot and indexing may finish within 10 seconds. Resurfacing should appear within 3 seconds of a matching project/page context.
- **cost:** Roughly $0.003–$0.02 per mark and resurfacing, dominated by screenshot/audio transcription and embedding; use local hashing and short transcripts to minimize cloud tokens.
- **security:** Screen captures, browser URLs, and voice may contain secrets. Encrypt the packet, redact password/payment fields, keep raw audio/screenshots on the Mac by default, upload only hashes and extracted text unless explicitly enabled, and provide one-button deletion. Never use a mark as authorization for a later external action.
- **missing:** A cross-surface context-bookmark record linking a timestamped pendant utterance, Mac visual state, browser tab/session, active project, and semantic fingerprint; A local Mac capture path that can take a screen/window snapshot without Accessibility and a browser extension payload that can provide DOM/title/URL context; A privacy/redaction pipeline for screenshots, audio transcripts, and logged-in page data; A context-match trigger that can resurface bookmarks on project/page return without interrupting the owner at unrelated times; A retention and deletion UI showing exactly what each bookmark contains


## Changes it proposed to its own stack

### `model-routing` — Add a live capability-admission layer before planning: compute a short-lived matrix from device heartbeats, /ops/status permissions, /browser/status, relay health, and pipeline state; annotate each requested step as available, degraded, queued-until-reconnect, or owner-blocked. The planner must not claim completion for a blocked step, must choose AppleScript/high-level Mac actions when Accessibility is false, and must persist a resumable intent for private-browser work while Chrome is offline. Include the matrix and reason in the eventual receipt.
- **owner gets:** The owner gets an honest answer immediately: “I can do the Calendar part now; browser is offline and GUI control is blocked by a Mac permission, so I queued that part.” They stop losing time to opaque failures and do not have to repeat requests when the browser or pendant reconnects.
- effort: Medium: typed availability schema, planner admission pass, heartbeat TTLs, queue/resume integration, and tests for stale or contradictory device status.  ·  risk: A stale heartbeat could incorrectly queue or skip work. Use short TTLs, fail closed for irreversible actions, and expose the exact blocker; on restart replay only idempotent read-only intents and mark the rest needs-review.
- cost: Negligible API cost; one small routing call and durable metadata per request. No new hardware cost.  ·  latency: Adds roughly 50–150 ms for cached status; avoids expensive model calls and futile Mac/browser retries.
- security: Improves security by preventing actions when required permissions/session ownership are absent. Availability metadata must not expose private URLs or account details to the pendant; retain only capability state and reason codes.
- depends on: A durable intent/job record with idempotency keys; Heartbeat/status endpoints for pendant, relay, Mac, and browser; A resume policy distinguishing read-only, reversible, and irreversible actions; Owner-visible receipts that include blockers rather than generic failure

### `integration` — Create a signed cross-surface context-epoch stream. The Mac agent emits an epoch whenever the active project, window, or browser tab meaningfully changes; the browser extension contributes a sanitized page fingerprint; the pendant contributes only an explicit mark ID and timestamp. The relay joins these events into a bookmark packet and evaluates matches when a later epoch resembles the marked one. Keep raw screen/audio local and transmit only signed IDs, fingerprints, and owner-approved excerpts.
- **owner gets:** Returning to a project would automatically restore the reasoning and evidence attached to the exact moment they left, even if the original tab moved or the Mac restarted. It turns scattered unfinished work into something recoverable without surveillance or a cloud copy of the owner's screen.
- effort: Medium-high: event schema and signatures, Mac/browser epoch emitters, local packet storage, relay matching, restart/replay handling, and a deletion/export surface.  ·  risk: A weak fingerprint could resurface an irrelevant or sensitive bookmark. Require confidence thresholds, show the source context before interrupting, expire unmatched packets, and allow the owner to disable capture globally or per app/site. Signed sequence numbers prevent replay and duplicate marks.
- cost: Small background storage and embedding cost; raw artifacts remain local, so cloud egress is low. No new per-invocation realtime spend.  ·  latency: Negligible event overhead; matching can run asynchronously and notify only after a high-confidence return context.
- security: Improves privacy versus uploading ambient state, but signed fingerprints can still reveal project names. Encrypt at rest, scope keys per device, omit sensitive domains by default, and make deletion cryptographically complete across relay and Mac.
- depends on: A local context-bookmark packet format and retention policy; Browser extension support for sanitized tab fingerprints; Mac active-project/window observation that works without Accessibility where possible; Relay replay protection and device-key provisioning; An owner-visible review/delete interface


## What it asked for

_Nothing._
