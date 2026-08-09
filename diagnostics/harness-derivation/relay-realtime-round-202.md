# Harness derivation — relay-realtime — round 202

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I’m tethered over USB, sync everything that’s waiting and then summarize what changed."
- **useful because:** While LTE is unregistered, USB tether is the fastest reliable path. This makes the pendant feel dependable: queued memos, alerts, and receipts get reconciled and the owner hears what actually updated.
- **path:** relay → mac-bridge → browser
- **model tier:** Realtime for a quick spoken summary; mac-planner for the sync orchestration; cheaper model for reconciliation logic if it’s long-running.
- **latency:** A brief spoken acknowledgement immediately; sync can take seconds, then a short summary.
- **cost:** Moderate; dominated by device I/O and reconciliation, not LLM tokens.
- **security:** USB sync touches local data and potentially credentials. Keep payloads minimal, encrypt where possible, and log receipts without leaking content.
- **missing:** A stable relay route/state machine for USB sync and receipts (the mac-planner asked about this; it needs a real endpoint to target).; A typed manifest for outbox/inbox item kinds so we don’t invent multiple queues.; Clear receipt semantics for exactly-once delivery across relay and Mac.

### "Give me a quick status snapshot: what’s connected, what’s queued, and what’s next."
- **useful because:** A single spoken snapshot reduces uncertainty. The owner doesn’t have to ask three different questions to understand if the system is healthy and what it’s doing.
- **path:** relay → mac-bridge
- **model tier:** Realtime model to compose a concise spoken status from live counters.
- **latency:** Under a second when cached; a few seconds if it must query multiple sources.
- **cost:** Low; dominated by a small number of status probes, not generation.
- **security:** Status can reveal sensitive context (active job names, connected devices). Use generic labels and avoid reading detailed job content unless asked.
- **missing:** A relay-visible status route for the relay surface itself (the relay can’t inventory its own capabilities).; A unified health snapshot that merges Mac, device, and relay counters into one response.

### "“Why did you do that?” — For any recent action you took on my Mac or in my browser, give me a short spoken explanation grounded in the exact evidence you used (page text, tab/app state, and action receipt), and if it was wrong, undo it or tell me precisely why undo is unavailable."
- **useful because:** Trust is the limiting factor for a wearable that can act while the owner is away. Today receipts and undo are separate primitives; the owner cannot interrogate one coherent causal record from the pendant. This would make mistakes understandable and recoverable without opening the Mac.
- **path:** pendant → relay → mac-planner → browser-extension → mac-terminal
- **model tier:** Realtime model only for the spoken question and a concise synthesis; cheap background summarization should index the existing evidence and receipts.
- **latency:** Under 2 seconds to acknowledge, under 8 seconds for a first spoken explanation; undo should begin immediately after the owner says “undo it.”
- **cost:** Roughly one realtime turn plus a small background summarization call; about $0.01–$0.05 per investigation, dominated by speech and evidence synthesis.
- **security:** Evidence may contain private page text or command output. Keep raw evidence on the relay/Mac, send only the minimum quoted excerpts to the realtime model, and never claim an action was undone without a verified undo receipt.
- **missing:** A durable causal evidence bundle linking plan inputs, observations, chosen actions, and outcomes; A relay query that resolves “that action” to a job and returns its evidence, not just its status; A spoken explanation/undo orchestrator that can call /jobs/:jobId/undo and verify the result

### "“Give me a private handoff.” — While I am away from my Mac, let me dictate a sensitive task on the pendant, have the relay hold it encrypted, and release it to the Mac or authenticated browser only when the pendant and the intended device are both present again; then tell me exactly what was released and what remains sealed."
- **useful because:** A wearable is useful away from the desk, but sending sensitive dictated material immediately to a cloud relay or unattended Mac is often the wrong tradeoff. This creates a deliberate, physical-presence handoff rather than forcing the owner to choose between losing the task and exposing it.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Realtime model extracts only a task envelope and sensitivity label; encryption, presence checks, and release policy are deterministic. Use a cheaper background model to summarize the sealed queue after release.
- **latency:** Immediate local acknowledgement in under 500 ms; release and confirmation within 5 seconds after the paired device is detected.
- **cost:** Negligible per task beyond one short realtime classification, roughly $0.002–$0.01; storage and cryptographic key management dominate engineering cost, not inference.
- **security:** This is specifically about keeping secrets sealed. Use device-bound keys, nonce-protected records, expiry and explicit deletion, and never put plaintext dictated content in logs, analytics, or spoken notifications. Presence must be cryptographic pairing, not merely a network IP.
- **missing:** Pendant-side encrypted sealed-record support and a physical release gesture; Relay encrypted-at-rest queue with device-bound key exchange and expiry; USB/LTE pairing and presence attestation for the real nRF9160 and ESP32-connected setup; Mac/browser release endpoints that acknowledge exact record hashes and receipt them

### "“Run this as a reversible experiment.” — Before changing my files, settings, browser state, or messages, show me a spoken prediction of the observable changes and a rollback plan; execute in an isolated snapshot or transaction where possible, then report which predicted changes actually occurred and let me revert the whole experiment with one phrase."
- **useful because:** The owner wants maximum access, but maximum access without a way to understand blast radius is hard to trust. A whole-experiment boundary is more useful than a per-click confirmation: it preserves speed while making multi-step changes inspectable and collectively reversible.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → mac-terminal
- **model tier:** Realtime model frames the experiment and speaks the result; deterministic planners and shell/browser adapters perform snapshots, diffs, and rollback. Use a cheaper background model for large diffs.
- **latency:** Prediction in under 3 seconds for a short plan; execution can run asynchronously, with a compact pendant update as soon as the first verified receipt arrives.
- **cost:** One realtime framing call plus optional background diff summarization, roughly $0.01–$0.08 depending on changed files/page state; storage for snapshots is the dominant cost.
- **security:** Snapshots can duplicate secrets. Store locally where possible, encrypt relay-held artifacts, redact spoken diffs, expire snapshots, and make rollback idempotent. Do not pretend arbitrary external side effects (sent mail, purchases) are reversible; label them as irreversible before execution.
- **missing:** Transaction/snapshot adapters for filesystem, macOS preferences, browser storage and app state; A cross-action experiment ID joining /plan, /execute, receipts, observations and rollback; A diff-and-rollback planner with explicit irreversible-side-effect detection; A pendant command path for “revert experiment <recent description>”

### "“Use my personal lens for this.” — Let me switch, from the pendant, which private context the hive may use (personal, work, travel, or no-history), and have the relay enforce that lens consistently across its speech context, Mac actions, browser tabs, logs, and follow-up notifications until I switch it back."
- **useful because:** The owner cannot safely wear a context-free agent everywhere. A single spoken privacy mode should prevent accidental mixing of work and personal material, rather than relying on each downstream agent to remember a preference or on the owner to explain it every turn.
- **path:** pendant → relay → mac-planner → browser-extension → mac-terminal
- **model tier:** Realtime model recognizes only the explicit lens switch and confirms it; enforcement is deterministic at the relay and adapters. No expensive model is needed for ordinary routing.
- **latency:** Mode change acknowledgement in under 1 second; enforcement must apply before the next transcript or action leaves the pendant.
- **cost:** Near-zero inference cost after setup; roughly $0.001 or less per switch. Engineering cost is policy propagation and audit testing.
- **security:** A lens must fail closed when missing or stale, be visible in every spoken confirmation, and never be inferred from location or calendar. Redact excluded context at ingestion rather than merely hiding it in prompts; retain an audit trail of mode changes without retaining excluded content.
- **missing:** A relay-owned, versioned context-lens state with TTL and explicit reset; Ingress filtering for audio/transcripts and egress filtering for Mac/browser actions and notifications; Mac/browser adapters that expose and enforce lens-scoped app/tab/session allowlists; Pendant LED/audio confirmation and offline persistence of the selected lens


## Changes it proposed to its own stack

### `relay` — Implement a first-class context-lens firewall at relay ingress/egress: a signed lens state (personal/work/travel/no-history) with TTL and explicit reset, applied before transcript persistence, model-context assembly, Mac/browser dispatch, and event-push text. Every job and receipt carries the lens version; adapters reject mismatched or absent versions. The pendant gets a compact state acknowledgement and retains the last lens offline until the owner changes it.
- **owner gets:** The owner can wear the agent in mixed settings without accidentally exposing work material to a personal task or vice versa; one spoken mode change becomes a reliable boundary across the entire hive.
- effort: High: relay state machine, redaction at ingestion, propagation through planner/browser/mac contracts, firmware acknowledgement, and adversarial tests for stale or missing lens state.  ·  risk: A false or stale lens could suppress useful context or leak the wrong one. Fail closed on uncertainty, provide an explicit spoken reset, and preserve only metadata needed to diagnose enforcement—not excluded content.
- cost: Small ongoing storage and CPU cost; one extra short metadata object per job. No meaningful model cost after the explicit switch.  ·  latency: Under tens of milliseconds for policy checks; no additional model turn for ordinary requests.
- security: Strongly positive if filtering occurs before persistence and dispatch. Requires careful key/signature handling so a compromised adapter cannot silently change the lens.
- depends on: A durable relay session/context state route; Lens-aware Mac and browser adapters; Pendant-side acknowledgement and offline persistence of the selected lens


## What it asked for

_Nothing._
