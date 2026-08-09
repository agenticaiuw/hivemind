# Harness derivation — mac-terminal — round 214

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live USB diagnostic access** — The granted mac_usb_serial_diagnostics schema still does not resolve against the live inventory; no bounded serial reader is callable. The only known route to the attached nRF9160/ESP32 remains run_shell via POST /execute, whose receipt lacks exit code and robust provenance.
  - evidence: Called mac_usb_serial_diagnostics for /dev/cu.usbmodem00096003658*, /dev/cu.usbserial-0287A9CA with 500ms/4096 bytes; resolver returned unresolved (best action:get_mac_status score 0.226).

## Capabilities it proposed

### "“Can I close the lid and walk away, or is anything on my Mac still relying on it?”"
- **useful because:** The owner needs a trustworthy answer before leaving: an in-flight shell, browser session, audio bridge capture, relay handoff, or queued pendant request may fail when the Mac sleeps. A single answer should distinguish work that is durably handed to the relay from work that still requires this Mac and say what will happen, rather than treating an online heartbeat as proof.
- **path:** pendant → mac-planner → browser-extension → relay-realtime
- **model tier:** background deterministic aggregation; realtime only for the short spoken answer
- **latency:** Under 2 seconds from a button press or voice question
- **cost:** No model call for normal cases; a small summarization call only when several jobs have mixed sleep behavior
- **security:** Return job names and coarse state, not command contents or browser page text. Do not change power settings or cancel anything without a separate request.
- **missing:** A sleep-impact contract on every job/action type (survives relay, requires Mac awake, or resumable); A live aggregator joining Mac jobs, browser command leases, pipeline/audio state, and relay job ownership; A pendant-readable cached verdict with age and an explicit unknown state when heartbeat data is stale; A Mac sleep/wake notification path to re-evaluate the verdict after lid events

### "“Why do you believe that, and what exactly did you observe?”"
- **useful because:** The owner should be able to challenge a spoken answer and hear a compact evidence chain: which Safari page or Mac command supplied it, when it was observed, whether it was transformed by a model, and whether the source is now stale. This is especially important when the Mac can act with full control and the pendant is offline or reconnecting.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Cheap deterministic provenance assembly first; realtime model only compresses the chain into a spoken explanation
- **latency:** 1–3 seconds for the evidence chain; never block on a fresh browser or shell read unless the owner explicitly asks to refresh
- **cost:** Usually zero additional model calls; a short realtime completion for natural-language narration
- **security:** Redact credentials, command arguments marked sensitive, page form values, and raw audio. Scope the response to evidence already used for this owner/session, and preserve source URLs/timestamps without uploading full page contents.
- **missing:** A unified claim ID carried from browser findings, Mac action receipts, pipeline events, and relay responses; A read-only evidence-trace endpoint that joins browser provenance with Mac job/journal records and marks freshness; A pendant speech/UI response format for 'observed', 'inferred', and 'unknown' rather than presenting all three as fact; A retention policy for compact evidence capsules and their source hashes

### "“Package this failure so someone else can reproduce it exactly.”"
- **useful because:** Today a failed voice or hardware interaction leaves scattered Mac job text, partial UART logs, browser state, firmware versions, and timing context. The owner cannot hand an engineer one trustworthy incident without manually collecting and interpreting all of it. A reproducibility capsule would turn a frustrating failure into a portable, privacy-filtered case that can be replayed or diagnosed later.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → unified
- **model tier:** Deterministic collection and hashing first; use a cheaper background model to write the human summary, reserving realtime only if the owner asks follow-up questions
- **latency:** 10 seconds for local collection and capsule sealing; under 2 seconds to read back its summary
- **cost:** Minimal storage and hashing cost; one small background summarization call per explicitly requested capsule
- **security:** Default to metadata, hashes, typed errors, timing, firmware/build IDs, and redacted excerpts. Never include raw microphone audio, credentials, browser form values, or full shell environment unless separately selected. Capsules must be encrypted at rest and have explicit expiry.
- **missing:** A cross-surface incident ID propagated through pendant turn, relay job, Mac job/receipt, browser command, and UART capture; A deterministic collector that snapshots firmware/build identity, link state, timing counters, and relevant bounded logs without mutating devices; A replay manifest that distinguishes safe read-only steps from actions requiring a fresh owner decision; Encrypted capsule storage and a share/export operation with field-level redaction and provenance

### "“Before you send anything off this Mac, show me exactly what will leave and what will stay local.”"
- **useful because:** The owner has deliberately chosen maximum Mac capability, but today there is no unified, truthful answer about data egress: a shell environment, browser page, audio turn, job output, or relay context can cross different boundaries. This capability makes privacy legible without imposing a gate; the owner can inspect the proposed payload, then decide whether to proceed.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → unified
- **model tier:** Deterministic payload accounting and redaction first; a small model summarizes the manifest in plain language, with realtime only for the spoken response
- **latency:** Under 2 seconds for a normal action; up to 5 seconds for a browser/page or audio-context manifest
- **cost:** Low: hashing and byte counts locally, plus an occasional short summarization completion
- **security:** The preview itself must not transmit the sensitive payload it describes. Keep raw values local, show names/types/byte ranges and redaction reasons, and make the manifest tamper-evident. This is transparency, not an approval gate.
- **missing:** A pre-dispatch data-flow manifest spanning shell, browser, audio, relay, and model calls; A classifier that identifies secrets, credentials, page form values, raw audio, and private files before serialization; A durable link between the preview manifest and the exact dispatched payload, including transformations and truncation; A pendant-readable diff showing local-only, relay-bound, model-bound, and discarded fields


## Changes it proposed to its own stack

### `mac-harness` — Add a persistence-only secret boundary for run_shell: execute with the owner's full inherited environment unchanged, but record an environment manifest containing variable names, value lengths, and stable HMAC fingerprints for configured secret variables rather than values. Apply the same redaction to stdout/stderr before they enter pendant-jobs.json, activity logs, receipts, or relay payloads, while retaining the unredacted stream only in a short-lived local diagnostic file when explicitly requested.
- **owner gets:** The Mac keeps its power, but a later job inspection will not accidentally expose relay tokens or API keys that a command printed. The owner still gets maximum shell capability and can tell whether environment drift caused a failure.
- effort: Medium: centralize redaction at the executor/result persistence boundary, add secret-pattern configuration and tests for logs, receipts, and relay responses.  ·  risk: Over-redaction could hide useful diagnostics; preserve a local opt-in raw capture and mark redaction spans. A missed persistence path could still leak, so test every store.
- cost: Negligible CPU and storage overhead; no model cost.  ·  latency: Sub-millisecond to low milliseconds per command result.
- security: Reduces accidental credential exfiltration without adding an approval gate or restricting execution.
- depends on: Existing POST /execute run_shell path; Existing pendant-jobs.json, activity log, receipts, and relay result serialization

### `mac-harness` — Create a shell invocation provenance envelope that records both the planner-submitted action and the executor-dispatched action whenever normalization rewrites it (for example, overlay or research-CLI interception), plus a monotonic invocation sequence, resolved cwd, timeout, and parent job/ledger identifiers. Expose it through GET /jobs/:jobId/receipts and GET /journal/:jobId without changing what executes.
- **owner gets:** When the agent says it ran one thing but the Mac actually ran a rewritten action, the owner can see the truth and reproduce or explain the result instead of debugging a misleading command history.
- effort: Medium: preserve an immutable pre-dispatch copy before computerControl normalization, attach the generated action and IDs to the existing receipt, and repair the missing planMeta.jobId join.  ·  risk: Capturing command text can expose private data; apply the existing sensitive-parameter withholding and cap long strings. A rewrite bug could still execute incorrectly, but it will no longer be invisible.
- cost: Small JSON growth per action; no model cost.  ·  latency: Negligible.
- security: Improves auditability without narrowing FULL_CONTROL_MODE; sensitive command fields remain withheld or hashed according to current receipt policy.
- depends on: POST /execute; GET /jobs/:jobId/receipts; GET /journal/:jobId; Existing action receipt and ledger stores


## What it asked for

_Nothing._
## Its own summary

Round 214 produced four non-duplicate deliverables: (1) persistence-only secret redaction for unrestricted shell execution, preserving full runtime capability while keeping env values out of jobs/receipts/logs; (2) immutable shell provenance showing submitted versus rewritten action and repairing the job↔ledger join; (3) owner-facing “Can I close the lid?” aggregation across Mac jobs, Safari leases, audio/pipeline state, relay handoff, and pendant-cached stale/unknown status; and (4) owner-facing “Why do you believe that?” evidence tracing across browser provenance, Mac receipts, and relay answers. I also verified and recorded that the newly granted USB diagnostic schema still cannot resolve: attached chips are real, but no callable serial reader exists.

**Biggest unknown:** Whether the existing browser provenance routes and any workbench sleep/lease metadata are actually live on this surface; the resolver reported them as unobserved, so those pieces still need route inventory and implementation. The immediate practical gap remains bounded USB UART capture/parsing for the two physically attached chips.

