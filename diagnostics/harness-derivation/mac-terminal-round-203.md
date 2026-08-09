# Harness derivation — mac-terminal — round 203

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Is my pendant ready for a real walk right now?”"
- **useful because:** The Mac can answer this today only in fragments. A single spoken answer should combine the physically connected nRF9160 and ESP32 bench frames, the local agent/relay reachability, and the last successful audio-path exercise, then say exactly what is missing instead of claiming wearable readiness. This turns the current USB-connected hardware into a useful pre-departure check.
- **path:** pendant → mac-planner → relay-realtime → mac-bridge
- **model tier:** background for the serial/frame parser and cached readiness report; realtime only to phrase the final short answer
- **latency:** Under 5 seconds when USB is present; under 1 second if the last good frame is younger than 30 seconds
- **cost:** About $0.001–$0.01 per invocation; most runs should be local parsing and cached status, with model spend only for an ambiguous fault
- **security:** Read-only USB diagnostics and authenticated local health only. Do not upload raw UART logs or credentials; send relay only a compact pass/fail matrix and timestamps. LTE registration must be reported separately from USB bench readiness.
- **missing:** A production wrapper that invokes the already-granted bounded USB serial diagnostic on both live ports and parses the existing dual-chip capture framing; A readiness record with separate fields for nRF health, ESP32 audio bridge, relay reachability, and LTE registration; A relay voice intent that requests this diagnostic and returns its compact result

### "“When I say ‘pick up where I left off,’ restore the exact work context I had on the Mac and browser, then tell me what changed since I stopped.”"
- **useful because:** A wearable has no screen, and the owner should not have to remember which Safari tab, app window, project, and pending action mattered. The Mac captures the active app and browser session, the browser supplies authenticated page state, and the relay compares the saved context with the live one before speaking a useful delta. This is a genuine handoff between bodies, not a Mac-only shortcut.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-bridge
- **model tier:** background model computes the context delta; realtime is used only for the short conversational response
- **latency:** Initial restore within 4 seconds; spoken delta within 2 seconds after the context snapshot
- **cost:** $0.002–$0.02 per handoff, dominated by one compact delta summary; snapshots and hashes should remain local
- **security:** Authenticated page text must stay on the Mac unless the owner explicitly asks for details. Persist opaque session/context IDs, titles, URLs and content hashes by default; redact tokens, form fields, and page bodies. Restoring a tab is reversible, but typing or submitting must never be inferred from this request.
- **missing:** A durable context checkpoint that joins active Mac app/window, browser session/tab, project, and last action receipt under one owner-visible checkpoint ID; A diff endpoint that compares a checkpoint with current machine/browser state and reports changed/not-found/blocked items; A pendant intent path mapping the spoken phrase to checkpoint restore without requiring a screen

### "“Why didn't that happen, and can you safely try the unfinished part once?”"
- **useful because:** Today the pendant can show a stale state, the relay can know a job ID, and the Mac has receipts, but the owner cannot get one truthful explanation spanning all three. A cross-surface failure explainer would distinguish never dispatched, queued offline, browser command rejected, shell nonzero exit, timed out, or completed-but-not-visible, then offer a bounded retry of only the failed idempotent step. This is the difference between a trustworthy assistant and silent automation.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-bridge
- **model tier:** background model classifies the durable receipt chain; realtime only answers the follow-up question and confirms the exact retry scope conversationally
- **latency:** Under 2 seconds for an existing job; retry starts immediately and returns a progress beacon rather than holding the voice turn open
- **cost:** $0.001–$0.01 per diagnosis; retries should be local action execution with no model call when the receipt declares the step idempotent
- **security:** Expose only the requesting owner's jobs and redact shell command arguments, tokens, and page contents. Never retry a non-idempotent or irreversible step automatically. The pendant must say “not retried” when the system cannot prove scope; this is a safety invariant, not a confirmation gate for ordinary work.
- **missing:** A durable correlation key carried from pendant turn to relay job to Mac job, action receipt, and browser provenance record; Shell receipts that preserve original-vs-rewritten action, exit code/signal, timeout reason, and a redacted environment fingerprint; An idempotency-aware retry endpoint that accepts one receipt/action ID and refuses ambiguous multi-step replay; A pendant query/response path that can render diagnosis and retry progress without requiring the Mac screen

### "“Take care of this while I’m away; only interrupt me if you need a decision, and tell me exactly what proves it’s finished.”"
- **useful because:** Today the owner must keep asking whether a multi-step browser/Mac task is still running, whether a page changed, and whether the final result actually happened. This would let the pendant hand off one bounded intent, let the Mac and authenticated browser continue across ordinary delays, and let the relay wake the owner only for a real ambiguity. Completion would be a proof bundle—receipt, resulting page state, and relevant local artifact—not an optimistic “done.”
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-bridge
- **model tier:** background model plans and supervises the multi-step work; realtime is reserved for the rare decision interrupt and final spoken proof summary
- **latency:** Dispatch acknowledgement under 2 seconds; supervision is asynchronous for minutes or hours; decision prompts reach the pendant within 5 seconds of a blocker
- **cost:** $0.01–$0.10 per task, dominated by occasional replanning and authenticated page reads; polling should be event-driven and local where possible
- **security:** The task must have an explicit scope, expiry, and allowed surfaces. Never silently broaden from one site/file/project to another. Persist only task metadata and evidence hashes by default; send page text or screenshots to the relay only when needed for a decision. A task that cannot produce proof must end as incomplete, not successful.
- **missing:** A durable supervisor that survives Mac-agent restarts and reconnects, with leases, expiry, and one active step per task; Browser and Mac event hooks that wake supervision on page mutation, download completion, job completion, or loss of session rather than polling blindly; A proof-bundle schema joining action receipts, browser provenance/evidence capsules, and resulting local artifacts; A pendant decision protocol for a small typed set of blockers (choose, retry, stop, or provide missing input), plus a final proof card rendered as speech; A relay scheduler/queue that can hold the task while the pendant and Mac are temporarily offline


## Changes it proposed to its own stack

### `mac-harness` — Make each run_shell dispatch produce a truthful execution envelope: preserve the submitted action and the rewritten action side by side, record argv/cwd plus a redacted environment fingerprint, capture exit code or terminating signal and timeout separately from the human message, attach the action receipt to its job and ledger IDs, and persist a bounded stdout/stderr tail. Feed the envelope to the relay so the pendant's status beacon can say failed, timed out, or completed rather than merely stale.
- **owner gets:** When an unattended Mac action fails, the owner gets a precise answer and a recoverable next step instead of “something went wrong.” It also prevents the system from claiming that the command it recorded is the command it actually ran.
- effort: Medium: executor/computerControl receipt schema, orchestrator ledger close/join, job serialization, and relay projection; no model training required.  ·  risk: Existing receipt readers may reject new fields; migrate additively and keep old records readable. Redaction must be tested against AGENT_TOKEN, relay keys, and LLM keys. A bounded tail can omit the decisive line, so preserve hashes and byte counts.
- cost: Negligible storage increase if tails are capped; no recurring API cost. Engineering cost is several days across Mac agent and relay.  ·  latency: Under 10 ms for metadata; no meaningful command latency change.
- security: Improves security by preventing secret-bearing environments from entering logs while making execution auditable. It does not narrow the owner's deliberate full-control policy.
- depends on: A stable job↔ledger correlation key (planMeta.jobId is currently null); orchestrator must call closeLedger on every terminal path; A relay projection for the new execution envelope


## What it asked for

_Nothing._
## Its own summary

Round 203 produced three owner-facing capabilities and one stack change. (1) “Is my pendant ready for a real walk?” combines live nRF9160/ESP32 USB health, relay reachability, audio-path history, and LTE-vs-USB truth; it is especially actionable because the hardware is connected now. (2) “Pick up where I left off” restores a joined Mac/browser context and speaks only the delta; the recorder noted this is connective work close to an existing idea, so the missing checkpoint/diff semantics must be the actual implementation target. (3) “Why didn't that happen, and can you safely try the unfinished part once?” correlates pendant state, relay job, Mac receipt, and browser provenance, with retry only when idempotency is proven. I also proposed truthful shell execution envelopes (original vs rewritten action, exit code, timeout, redacted env fingerprint, job↔ledger join, bounded output) without changing the owner's deliberate full-control policy. I tested the newly granted mac_usb_serial_diagnostics: it still cannot resolve against the live inventory, so no serial frame was read. The readiness capability therefore still needs an implemented host wrapper/parser, not another schema grant.

**Biggest unknown:** Whether the connected nRF9160 and ESP32 are actually emitting usable diagnostic frames. The physical ports are known, but the granted serial tool has no implementation; until a bounded host-side serial reader exists, “ready for a real walk” can only report Mac/relay health and cannot truthfully validate the audio hardware.

