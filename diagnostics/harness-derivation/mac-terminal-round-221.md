# Harness derivation — mac-terminal — round 221

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac/relay routing cost** — The live Mac agent is fully ready (full control, browser online, relay reachable), but all 6 recent requests used planner tier at ~9,743 prompt tokens and ~3.7s average; deterministic/background tiers have zero requests.
  - evidence: GET /routing returned totalRequests=6, planner.requests=6, planner.avgLatencyMs=3700, planner.avgTokensPerRequest=9743, deterministic.requests=0, background.requests=0; GET /ops/status returned fullControlMode=true, browserExtension.online=true, relay.reachable=true.

## Capabilities it proposed

### "When I say “finish this” on the pendant, carry out the whole task across my Mac and logged-in browser, then tell me exactly what changed—even if the Mac or link drops halfway."
- **useful because:** This is the core hive behavior: the pendant supplies intent and continuity, Safari supplies authenticated reach, the Mac performs local work, and the relay makes the result returnable. Today a dropped link can leave the owner unsure whether a browser download, file edit, or app action happened.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Realtime only for the short intent clarification and final spoken result; background planner/model for decomposition, verification, and retry.
- **latency:** Acknowledge dispatch locally in under 500 ms; begin visible work within 3 s; return first progress within 10 s; long tasks continue asynchronously and survive reconnect.
- **cost:** One realtime turn plus 2–6 cheap planner/verification calls; roughly $0.03–$0.20 depending on browser vision retries, with Mac/browser execution dominating wall time.
- **security:** The task may use logged-in browser sessions and local files. Keep browser evidence capsules and Mac receipts scoped to the job, redact secrets from spoken/log output, and require explicit confirmation only where the existing owner policy already demands it; never claim completion without a postcondition check.
- **missing:** A durable cross-surface transaction record linking pendant turn ID, relay job, Mac job, browser command IDs, and final evidence; A resumable executor that can retry only unconfirmed steps after reconnect and reconcile interrupted Mac jobs; A verifier that checks user-visible postconditions (download exists and is complete, page state changed, file hash changed) before announcing success; A pendant protocol message for progress milestones and final evidence summary

### "After my Mac wakes or restarts, tell me which pendant requests actually finished, which are unknown, and resume only the safe unfinished parts without repeating side effects."
- **useful because:** The current system can leave jobs permanently marked processing, cannot interrupt a shell child, and has no retry or job-to-ledger join. This would turn a silent failure into a truthful morning report and prevent duplicate downloads, messages, edits, or purchases.
- **path:** relay → mac-planner → pendant → dashboard → browser-extension
- **model tier:** Cheap background reconciliation and deterministic checks; realtime only when the owner asks for the spoken status or must resolve an ambiguous side effect.
- **latency:** Reconcile within 15 s of Mac-agent boot or reconnect; spoken status in under 2 s from cached state; resume safe work within 30 s.
- **cost:** Near-zero model cost for ledger/state matching; at most one cheap verifier call per interrupted step. Browser verification or vision is the dominant cost, approximately $0.01–$0.10 per recovered job.
- **security:** Never infer success from a missing process. Mark side effects unknown until a concrete postcondition or receipt proves them. Do not replay email, deletion, payment, or browser submission steps automatically; preserve sensitive URLs and shell output locally and speak only a redacted summary.
- **missing:** Boot-time reconciliation that closes or marks stale pendant-jobs records and joins each ledger to its job ID; Per-action idempotency keys and postcondition probes for shell, browser, and file actions; A recovery planner that classifies steps as proven-complete, safely-rerunnable, or owner-required; A reconnect briefing message delivered to the pendant and persisted in the dashboard

### "Is the pendant and audio bridge healthy right now?"
- **useful because:** The chips are physically attached today, but there is no user-facing truth about whether both UARTs, clocks, audio framing, buttons, and the bridge are alive. A one-sentence bench verdict prevents debugging by guesswork before the device ever has LTE.
- **path:** pendant → mac-planner → relay → dashboard
- **model tier:** No realtime reasoning for the test itself: run a deterministic dual-UART health script; use a cheap model only to summarize failures. Realtime is used only if the owner asks follow-up questions.
- **latency:** Start within 1 s of the spoken/button request and report a bounded verdict within 8 s; stream a failure point as soon as the first chip times out.
- **cost:** Negligible model cost; one local diagnostic process and at most one short summary call. USB serial I/O and firmware self-test dominate latency.
- **security:** Read-only bench frames only, fixed device paths, bounded bytes/time, no firmware flashing or arbitrary network access. Include firmware build IDs and counters but redact environment and filesystem contents.
- **missing:** A real host-side serial reader/framing parser for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA (the current resolver has no serial capability); A firmware diagnostic command that returns version, reset reason, audio frame counters, button edge count, CRC/error count, and bridge heartbeat without disrupting recording; A Mac action/receipt that records per-port open/read/timeout and exit status; A relay-to-pendant response that renders the result locally when the wearable is offline from LTE

### "When you tell me something important, let me ask “prove it” and hear the exact source, timestamp, and the next thing I can do—whether it came from my browser, Mac, or your memory."
- **useful because:** The owner can distinguish a live observation from an inference or stale memory without opening a dashboard. This makes an always-available voice agent trustworthy for consequential decisions and lets them correct the specific evidence rather than arguing with a conclusion.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Cheap deterministic evidence lookup and response templates; use a planner only to select and order multiple conflicting sources. Realtime TTS delivers the short provenance answer.
- **latency:** Return the source capsule in under 2 s for one claim and under 5 s for a multi-source conflict; preserve a longer evidence view in the dashboard.
- **cost:** Usually negligible because the system already has receipts and provenance records; occasional planner synthesis costs about $0.005–$0.03 per complex claim.
- **security:** Do not read secrets aloud by default. Classify evidence sensitivity, speak host/title/time and a redacted excerpt, and require the dashboard or an explicit owner request for sensitive values. Preserve a tamper-evident link from spoken claim to source record.
- **missing:** A claim registry that assigns every spoken factual assertion a stable claim ID and evidence capsule; A cross-surface trace API joining Mac receipts, browser provenance, memory facts, and relay turns; A pendant-friendly citation format for source, age, confidence, and conflict state; Owner correction feedback that invalidates or amends the specific claim rather than silently changing global memory


## Changes it proposed to its own stack

### `mac-harness` — Instrument every run_shell action with a child-process execution record: immutable pre-dispatch command digest and redacted argv/env names, resolved cwd, pid, startedAt, finishedAt, duration, exit code, terminating signal, timeout/abort reason, bounded stdout/stderr digests, and a link to the effective action after command rewriting. Capture the original submitted action separately so tkinter/research rewrites cannot make the audit trail lie.
- **owner gets:** When something fails or silently changes the Mac, the owner can ask what actually ran, where, and why, instead of receiving only “Failed: …” with no exit code or knowing whether the command was rewritten.
- effort: Medium: replace exec with a spawn/execFile-compatible runner, add redaction and receipt fields, preserve existing unrestricted FULL_CONTROL behavior, and add tests for timeout, nonzero exit, overflow, and rewrite paths.  ·  risk: Receipt capture could leak secrets or alter shell compatibility. Redact values by default, keep raw output bounded, retain the exact command only under the existing local workspace policy, and fall back to the current executor if instrumentation fails. Do not add approval gates.
- cost: Negligible CPU/storage overhead; roughly 1–4 KB metadata per action, with existing job/ledger caps requiring compaction of old output.  ·  latency: Under 10 ms bookkeeping per action; process launch and command latency unchanged.
- security: Improves forensic visibility while preserving owner-requested maximum access. Environment values must never be persisted wholesale; record only allowlisted variable names and a hash/count summary.
- depends on: A stable action-receipt schema shared by /execute and the ledger; A correct original-action versus rewritten-action distinction in computerControl.js; Optional boot reconciliation for records left processing after a crash

### `model-routing` — Add a deterministic Mac command fast lane for narrowly typed status and follow-up queries: map requests such as “what happened to that job?”, “is Wi‑Fi/audio/battery okay?”, and “what changed?” to direct GET /jobs/:jobId, /receipts, /machine-context, /ops/status, and journal queries before invoking a model; use the model only to resolve pronouns or summarize returned evidence.
- **owner gets:** Routine questions answer in seconds and remain reliable when the expensive model is busy, while complex tasks still get full planning. The owner gets factual status rather than a costly conversational guess.
- effort: Small-to-medium: intent recognizer with confidence thresholds, job/session pronoun resolution, evidence-shaped response templates, and fallback to the existing planner below threshold.  ·  risk: A false match could answer the wrong job or omit context. Require an unambiguous job/session match, include timestamps and source labels, and fall back to the model rather than fabricate an answer.
- cost: Cuts realtime/model calls for frequent status checks, likely saving $0.01–$0.05 each and reducing context retransmission; negligible local compute.  ·  latency: Typical answer drops from model round-trip latency to one authenticated local GET, roughly sub-second to 2 s.
- security: Read-only routes only; preserve existing bearer/session protections and redact command output in summaries.
- depends on: A shared job/session pronoun resolver; Stable structured response schemas for /jobs, /receipts, /journal, and /machine-context; Truthful timestamps and exit status in shell receipts

### `context` — Introduce a server-side context lease for Mac status and active-task conversations: after the first turn, retain a compact, hash-addressed evidence bundle (job IDs, current browser tab identity, project, last receipts, and relevant machine facts) and send only a lease ID plus deltas on subsequent turns. Expire or invalidate the lease when the job, tab, project, or permission state changes; require the model to request a fresh snapshot when its hash is stale.
- **owner gets:** Follow-up questions about “that job,” “the page I was on,” or “what changed?” become materially faster and less forgetful. The owner gets continuity instead of paying for the same Mac/browser context over and over.
- effort: Medium: add encrypted context-lease storage, evidence hashes and invalidation hooks to jobs/browser/project events, and planner middleware that dereferences a lease before model invocation.  ·  risk: Stale context could cause an answer about an old tab or job. Bind every lease to explicit IDs and timestamps, reject stale hashes, and label responses with the evidence time; losing a lease should degrade to a fresh read, never fabricate continuity.
- cost: Potentially large token reduction: the live routing sample averages ~9,743 prompt tokens per planner request. A compact lease could remove most repeated context, reducing API spend and prompt latency without reducing model quality.  ·  latency: First request unchanged; follow-ups should save roughly 1–3 seconds of prompt transfer and context assembly, subject to model time.
- security: Lease contents contain local/browser metadata and possibly sensitive claims. Encrypt at rest, scope to the owner/session, avoid copying raw page text or shell environment, and revoke on logout or browser-session deletion.
- depends on: A canonical evidence capsule format shared by Mac jobs, browser results, and relay turns; Invalidation events for GET /jobs/:jobId, browser command results, active project, and machine-context refresh; Planner support for lease IDs and stale-hash refusal


## What it asked for

_Nothing._
## Its own summary

Round 221 produced four owner-visible proposals: (1) a cross-surface “finish this” transaction that carries one pendant intent through relay, authenticated Safari, and Mac with verified evidence; (2) truthful post-restart/reconnect reconciliation that resumes only safe unfinished steps; (3) a deterministic USB dual-chip bench-health verdict for the physically attached nRF9160 and ESP32; and (4) truthful shell execution envelopes with exit code, PID, timeout/signal, cwd, redacted environment metadata, and original-vs-rewritten command provenance. I also proposed a deterministic status fast lane. Fresh live evidence: Mac full-control and Accessibility are ready, Safari and relay are online, but all six recent requests used planner tier (~9,743 prompt tokens and ~3.7s average), while deterministic/background routing has zero traffic.

**Biggest unknown:** The granted serial-diagnostics schema still has no live implementation: the inventory exposes no serial capability, so I cannot directly read either attached chip this round. What is still needed is a real bounded host serial reader/framing parser plus a firmware diagnostic frame; existing dual-UART capture scripts can be used through unrestricted run_shell meanwhile. I also still need the cross-surface transaction/recovery coordinator and postcondition verifier; those are not present as a single capability.

