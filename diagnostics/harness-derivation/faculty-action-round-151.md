# Harness derivation — faculty-action — round 151

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Run the pending hardware check and tell me, in one spoken sentence, whether the pendant and audio bridge are actually healthy.” The Mac, while the chips are USB-connected, captures bounded UART diagnostics from both serial devices, runs the 24 kHz audio probe, correlates timestamps, and speaks only measured pass/fail plus the next repair step."
- **useful because:** The owner currently has to be physically present with two cables and know which logs and counters matter. This makes the wearable and bridge self-testable today, without pretending LTE registration exists or claiming health from labels.
- **path:** pendant → mac-terminal → mac-planner → relay-realtime → unified
- **model tier:** background for parsing/correlating bounded logs; realtime only to turn the resulting receipt into the short spoken sentence
- **latency:** 20–60 seconds for capture and probe; under 2 seconds to speak the receipt once available
- **cost:** <$0.03 per invocation; most cost is local serial capture and the already-available on-device audio measurement, not model tokens
- **security:** UART may contain identifiers or network diagnostics; keep raw logs on the Mac, send relay only hashes, counters, and a redacted receipt. Never flash, reset, or mutate hardware without explicit confirmation.
- **missing:** A typed Mac route for enumerated serial devices and bounded read-only UART capture (nRF9160 and ESP32 bridge); A receipt schema joining UART timestamps to audio_path_probe measurements; Owner-approved firmware log verb or stable diagnostic framing

### "“Finish that task, but if one step failed, repair only that step and prove the final state.” The action worker resumes a failed Mac/browser job from its durable receipt, rechecks the browser tab/session capsule, retries only an idempotent step, and independently verifies every changed file, field, or URL before reporting done."
- **useful because:** Today a queued job can be reported as failed or done, but recovery still forces the owner to reconstruct what happened. This gives the action facet a safe, truthful repair loop rather than blind replay or a vague retry.
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision → faculty-perception → faculty-action → unified
- **model tier:** background/local planner for selecting an idempotent retry; realtime only for the owner-facing status
- **latency:** Immediate receipt lookup; 5–30 seconds for a single bounded repair; stop and ask if postconditions or session identity are ambiguous
- **cost:** <$0.05 per repair; local browser/Mac actions dominate latency, with one small planning call only when needed
- **security:** Never replay sends, purchases, deletions, or form submissions automatically. Require the existing physical transaction approval latch for high-risk retries; redact private page content and use hash-only verification where possible.
- **missing:** A durable per-step retryability/idempotence flag and compensation metadata in job receipts; A resume route that accepts job_id plus step_id and refuses completed/non-idempotent steps; Action-ledger linkage from executor receipt to verify_operation_step provenance

### "“Continue the thing I started earlier, wherever it stopped.” The pendant gives a short spoken checkpoint; the relay hands an opaque continuation token to the Mac, which restores the exact application/browser tabs and resumes only from the last verified boundary, even after sleep or a dropped connection."
- **useful because:** Long tasks currently become a vague success/failure conversation when the owner is away. This would let the owner leave a task, return hours later, and continue without repeating actions or exposing a full transcript.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-action → unified
- **model tier:** background/local planner for checkpoint selection; realtime only for the short checkpoint and owner command
- **latency:** Under 2 seconds to report checkpoint; 10–30 seconds to restore and resume one bounded segment
- **cost:** <$0.04 per continuation; local state restoration dominates
- **security:** Continuation tokens must be opaque, expiring, device-bound, and incapable of authorizing a new action by themselves. Revalidate tab identity and permissions before resuming; require physical approval for any consequential step.
- **missing:** A durable checkpoint graph with verified boundaries, not just a terminal job status; A resume-token route that restores app/tab identity without replaying prior mutations; Cross-surface wake/availability signaling and explicit stale-token semantics

### "“Handle this private page, but do not show its contents to the cloud.” The local Mac/browser facet extracts only a typed, minimal proposal (for example recipient, amount, and destination domain), the pendant speaks that redacted summary, and a physical confirmation authorizes the browser to perform the action; the relay receives only hashes and the final verified outcome."
- **useful because:** The owner can use logged-in banking, medical, work, or private-mail sessions without making page contents part of model context. This turns the browser session into a privacy-preserving hand rather than a data export.
- **path:** pendant → mac-vision → mac-planner → browser-extension → faculty-perception → faculty-action → relay-realtime → unified
- **model tier:** local Mac rule engine for extraction and policy; realtime only for the redacted spoken summary
- **latency:** 2–5 seconds for local extraction and confirmation; under 10 seconds for execution and verification
- **cost:** <$0.01 per invocation when extraction is local; no cloud vision/token cost for page contents
- **security:** Field extraction must fail closed on unknown pages, secrets, or ambiguous mappings. Never place passwords, full message bodies, or page screenshots in relay logs. Physical approval binds the exact redacted digest, target origin, and expiry.
- **missing:** A local typed-field extraction/policy layer in the browser bridge; A sensitivity-aware envelope that proves which fields were summarized without carrying their values upstream; Browser executor support for digest-bound confirmation and hash-only postcondition evidence


## Changes it proposed to its own stack

### `mac-harness` — Add a read-only, typed USB-device diagnostics harness on the Mac: enumerate the two known serial paths, identify nRF9160 versus ESP32 by handshake, capture bounded UART frames with byte/time limits, and expose structured results (device identity, firmware version, counters, dropped bytes, timeout) without accepting arbitrary shell strings or flashing commands.
- **owner gets:** With the pendant and audio bridge physically attached now, the owner can ask for a real hardware check and receive evidence instead of a guess. It also makes future action receipts explainable when audio or link behavior degrades.
- effort: Medium: local agent route plus allowlisted serial reader, framing tests, and redaction; no firmware change required for the first version.  ·  risk: A bad handshake could leave a serial device in an unexpected mode; use read-only open, short timeouts, and close on every path. Never expose secrets or permit write bytes. Recover by unplug/replug and mark the receipt unknown.
- cost: Negligible API cost; roughly 1–2 engineering days, no hardware cost or extra power.  ·  latency: Adds 1–10 seconds to a diagnostic request, bounded by capture timeout.
- security: Improves safety versus arbitrary run_shell, but raw UART must remain local and receipts must be redacted/hash-only.
- depends on: A stable diagnostic framing/handshake in each firmware image; A typed route resolver for serial_ports and uart_capture rather than free-form command execution

### `memory` — Add an owner-visible, cross-surface action ledger that renders each completed or uncertain mutation as a compact reversible story: intent, exact target, evidence digest, expiry of the undo window, and an available compensation action. The pendant can say “undo the last safe change”; the Mac/browser facet performs only the ledger's predeclared compensation and perception verifies the result.
- **owner gets:** When automation changes a file, draft, tab, or setting, the owner gets a trustworthy undo path instead of hunting through apps or guessing whether “that” happened. It is especially valuable when the owner was not watching the Mac.
- effort: Medium-high: extend the existing action ledger with compensation contracts, cross-surface target identifiers, and a small owner-facing history view.  ·  risk: Some actions cannot be undone or may have external side effects. Mark those explicitly, never invent compensation, expire stale entries, and require confirmation for anything beyond local reversible changes. Recovery is to leave the original state untouched and report unknown.
- cost: Low storage; <$0.02 for occasional summarization, with most work local.  ·  latency: Sub-second lookup; 5–15 seconds for a verified compensation action.
- security: Ledger entries must minimize sensitive values and use hashes for private content; the undo request must bind to the original action digest and owner session.
- depends on: Existing actionLedger and approvalHandoff need compensation metadata and a stable cross-surface target identity; verify_operation_step must accept the compensation step and return provenance; The pendant needs a compact way to disambiguate the last few safe changes


## What it asked for

_Nothing._
## Its own summary

Round 151 produced three non-duplicate action proposals: (1) a real USB-attached pendant/ESP32 self-test that combines bounded UART capture with the measured 24 kHz probe and speaks only evidence-backed health; (2) a receipt-driven repair loop that retries only idempotent failed Mac/browser steps and independently verifies postconditions; and (3) a read-only typed serial diagnostics harness, replacing unsafe/free-form shell diagnostics. The Mac bridge and Safari are currently online, while the mobile device remains offline; I did not assume LTE registration or claim hardware success. I still need a typed serial-port/UART capture route, stable read-only diagnostic framing from each firmware, per-step retry/idempotence metadata, and a durable linkage from executor receipts to verify_operation_step provenance. I asked faculty-perception to define the verification receipt shape.

**Biggest unknown:** Whether the connected USB serial devices expose a stable diagnostic handshake and bounded counters without requiring firmware changes; no live serial probe is available to this agent, and I will not flash or write to hardware.

