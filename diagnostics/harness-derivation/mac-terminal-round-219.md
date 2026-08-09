# Harness derivation — mac-terminal — round 219

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Take this thought and make it real: capture what I’m saying, turn it into a dated project note in the right local repository, and show me the resulting diff before you tell me it’s done.”"
- **useful because:** This is the most useful missing end-to-end behavior: a thought spoken while walking becomes a reviewable artifact, not a transcript lost in chat. The pendant supplies the only moment when the idea exists, the relay preserves it through disconnects, the Mac finds the correct project and writes it, and the owner receives evidence rather than a confident claim.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only for the short capture/acknowledgement; a cheaper background model structures the note and chooses the repository. The Mac planner performs file discovery and the final diff.
- **latency:** A local capture acknowledgement under 500 ms; durable task creation under 3 s when connected. Repository discovery and note generation may take 10–30 s, with progress delivered asynchronously.
- **cost:** About $0.01–$0.05 per thought depending on transcription and structuring; most cost is the background model, not realtime. Mac and relay execution are local/Worker work.
- **security:** The spoken thought and selected project path leave the pendant for relay processing. Never upload unrelated repository contents: send only the bounded candidate filenames and the proposed patch. The owner must be able to say “show diff” and “discard,” and completion must include the exact path, hash, and diff summary.
- **missing:** A durable capture-to-artifact job type that joins the pendant turn ID, relay task, Mac job, and final file hash; A repository selection and bounded context reader that can propose a note without shipping the whole tree; A diff/evidence response that can be rendered as speech plus dashboard detail

### "“Run that Mac task, and if it fails, diagnose the actual failure, retry only a safe corrected form, then tell me exactly what ran and what changed.”"
- **useful because:** Today a failed shell action loses the exit code, cannot be cancelled while running, is never retried, and can leave a job stuck after a restart. This turns the Mac from a fire-and-forget executor into a dependable limb: the pendant can acknowledge the request, the relay can keep the task alive, and the Mac can produce an honest recovery trail.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** Use a cheap background model for stderr classification and retry planning; reserve realtime for the initial request and a terse failure/completion announcement. A deterministic executor should handle timeout, exit code, process group, and idempotency checks.
- **latency:** Initial dispatch acknowledgement under 1 s. A first failure report within 2 s of process exit; one bounded retry within 15 s. Never wait silently through the current 120 s timeout.
- **cost:** Usually under $0.01 for classification; shell execution dominates no API cost. Realtime is used only twice at most.
- **security:** The existing shell deliberately has unrestricted environment and network access, so receipts must redact environment values and secrets while recording a fingerprint of inherited variables. Retrying mutations can duplicate side effects: retries require an explicit idempotency classification, and the owner must receive the original command, exit status, stderr, and proposed correction before any non-idempotent retry.
- **missing:** Capture real exit code, signal, pid/process group, argv, timeout reason, and bounded stdout/stderr in the shell receipt; Wire executionContext's existing retry/idempotency engine into POST /execute and make cancellation terminate the process group; Boot-time reconciliation of processing jobs and closure/join of the action ledger to its job ID; A recovery planner that distinguishes safe read-only retries from irreversible mutations

### "“Prove that.”"
- **useful because:** A spoken answer is not trustworthy merely because it sounds certain. This lets the owner challenge any answer or action and receive the actual source chain: browser page and timestamp, local file or shell receipt, model transformation, and whether the source is stale. It is a cross-surface capability no single node can provide because the claim may span an authenticated browser tab, Mac state, relay memory, and a spoken response.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Use a cheap deterministic provenance resolver first; use a background model only to summarize conflicting evidence. Realtime speaks a two-sentence answer and points the owner to the dashboard evidence bundle.
- **latency:** Resolve a recent claim in under 2 s; older multi-source traces under 8 s. If evidence is missing, say so immediately rather than fabricate a citation.
- **cost:** Near-zero API cost for indexed records; at most $0.01 when summarization of several evidence items is needed. Storage and hashing are the main costs.
- **security:** Do not expose browser page contents or secrets to the relay unless the claim requires them. Return least-privilege excerpts, origin/title/URL, local path and hash, and a redacted command receipt. Authenticated browser evidence must remain scoped to the owner’s session and never be searchable by another surface.
- **missing:** A unified claim ID and provenance graph joining relay responses, browser provenance records, Mac action receipts, memory findings, and file hashes; A resolver that can answer which evidence supports one spoken sentence and label stale, contradictory, or absent evidence; A dashboard/easy spoken rendering that shows the source chain without dumping sensitive page text

### "“Rehearse this workflow without touching my real accounts or files, then show me exactly what would happen.”"
- **useful because:** The owner cannot safely explore a consequential multi-surface workflow today. A true rehearsal would combine a temporary Mac workspace, a browser session with network writes intercepted or mocked, and the relay’s planner, then return the proposed file diff, navigation/form steps, and external side effects before anything real is changed. This is more than a plan: it proves the steps against realistic state while preserving the real account.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** A deterministic sandbox runner performs filesystem copy-on-write and browser request interception; a cheaper background model explains the resulting diff and side-effect list. Realtime only handles the spoken request and completion notification.
- **latency:** Create the rehearsal in under 5 s; finish ordinary workflows in 15–60 s. Long browser workflows should stream step progress and remain cancellable.
- **cost:** $0.01–$0.10 for explanation; local copy-on-write storage and intercepted browser execution dominate. No external mutation should occur during rehearsal.
- **security:** The sandbox must never reuse write-capable cookies or leak secrets into the temporary profile. Network requests need an explicit allowlist and mutation interception, with credentials redacted from traces. The result must label simulated responses and never claim an external action occurred.
- **missing:** Disposable copy-on-write Mac workspaces with cleanup and a manifest of touched paths; A browser harness mode with isolated profile, request interception, synthetic responses, and a complete step trace; A cross-surface effect ledger that classifies filesystem, browser, network, and account mutations; A promotion step that can apply only the reviewed file/browser plan to the real surfaces

### "“Keep working on this across my Mac and browser until it is genuinely done, but stop at these boundaries: no purchases, no messages sent, and no more than three retries; tell me when you hit a boundary.”"
- **useful because:** Today autonomy is either a one-shot action or an opaque long-running delegation. The owner cannot express a durable contract that spans the pendant, relay, Mac, and authenticated browser while preserving explicit stop conditions. This would make unattended work useful without pretending every intermediate success is completion.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** A deterministic contract engine enforces attempt counts, deadlines, mutation classes, and stop conditions; a background model chooses the next step and interprets results. Realtime is only for contract creation, boundary alerts, and final status.
- **latency:** Contract acknowledgement under 1 s; progress events within 2 s of each step; boundary alerts immediately. The workflow may run for hours or until its deadline while the relay remains awake.
- **cost:** $0.02–$0.15 per workflow depending on retries and model planning. Most steps are local Mac/browser execution; storage is a compact contract and event log.
- **security:** Boundaries must be machine-enforced, not merely included in a prompt. Browser and Mac actions need typed effect labels, immutable attempt counters, deadline handling, and a durable pause state. Never treat a missing heartbeat as completion; an expired contract must report unfinished work and preserve evidence.
- **missing:** A durable cross-surface execution contract with deadline, retry budget, forbidden effect classes, and completion predicates; A shared event stream and lease so relay, Mac, and browser cannot concurrently perform duplicate steps; Machine-readable effect classification for browser and shell actions, including attempted and actually observed mutations; A resume/pause UI and spoken boundary alert that survives relay or Mac restart


## Changes it proposed to its own stack

### `mac-harness` — Implement a real bounded dual-UART bench harness on the Mac for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA. It should autodiscover the exact nRF9160 and ESP32 ports, capture framed health/counter lines for a bounded interval, decode timestamps/CRC/sequence gaps, and emit one signed JSON receipt plus raw logs. Integrate it as a typed read-only action rather than relying on an unresolved capability schema.
- **owner gets:** Today the chips are physically connected and testable, but the system cannot tell the owner whether both boards are alive, whether audio frames are crossing the bridge, or which side dropped a frame. This makes the newly real wearable bench usable instead of leaving the owner to interpret ad-hoc terminal output.
- effort: Moderate: reuse diagnostics/start_dual_capture.sh and diagnostics/dual_chip_autocapture.sh, add a small framing parser and a narrow local-agent action, then expose the receipt in the dashboard.  ·  risk: A noisy or stale UART line could be mistaken for health; require fresh sequence/timestamp evidence and report UNKNOWN when absent. Never flash or write to either port from this action. Keep raw logs bounded and rotate them.
- cost: No API cost; roughly 1–2 days engineering and a few MB per captured session. No hardware or ongoing power cost beyond the existing USB connection.  ·  latency: A 1–3 second bounded capture gives a useful result; autodiscovery adds under 500 ms.
- security: Read-only USB access. Raw UART logs may contain identifiers, so keep them local by default and send only the summarized receipt to relay/dashboard.
- depends on: A real local-agent typed action or route for bounded serial diagnostics; A documented health/counter frame format from both firmware images; The existing dual-chip capture scripts


## What it asked for

_Nothing._
## Its own summary

This round I recorded four non-duplicate items: (1) spoken thought → structured project note with a bounded diff and evidence, (2) failure-aware Mac execution with real exit status, safe retry, cancellation and crash recovery, (3) a cross-surface “Prove that” provenance chain for spoken claims, and (4) a real bounded dual-UART bench harness. Live discovery confirms Safari is online, the Mac bridge is online, and the pendant itself is still offline. I attempted the granted USB diagnostic call, but it remains unresolved because no serial capability exists in the live inventory; the only current route is unrestricted run_shell. The owner still needs an implemented typed serial diagnostic action, plus documented health/counter frame formats from both firmware images. I did not ask again for the pending run_bench_health_check.

**Biggest unknown:** Whether the current nRF9160 and ESP32 firmware already emit machine-parseable health/sequence/CRC frames on their USB UARTs; without that format, a bounded harness can capture logs but cannot honestly classify audio-link health.

