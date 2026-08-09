# Harness derivation — mac-terminal — round 171

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live surfaces** — The live inventory now shows Safari on MacIntel with 9 tabs online and home-macbook-bridge online; cloudflare-contract-test mobile remains offline. Browser inspections are currently empty.
  - evidence: discover:devices returned Safari on MacIntel browser online (9 tabs), home-macbook-bridge online, cloudflare-contract-test offline; GET /browser/inspections returned {ok:true, inspections:[]}.

## Capabilities it proposed

### "“Continue the task I started on my Mac, even if the agent or browser crashed.”"
- **useful because:** The owner gets real continuity instead of a dead 'failed' notification: the pendant identifies the unfinished job, the relay finds its durable journal/ledger, the Mac restores the exact project and browser checkpoint, and the browser extension verifies what is still on screen before the next action. It can safely resume a half-completed research, filing, or web workflow rather than repeating side effects blindly.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension
- **model tier:** Background model reconstructs the checkpoint and proposes the next step; realtime is used only for the short spoken status and any interruption.
- **latency:** 5–15 seconds to reconstruct and inspect; then actions stream as ordinary Mac/browser work.
- **cost:** ~$0.01–$0.05 per resume, dominated by vision/browser inspection context; no model call if the durable checkpoint proves the next deterministic step.
- **security:** The checkpoint can contain authenticated page titles, file paths, and task text. Keep raw screenshots and command output on the Mac; send the relay only a redacted summary and opaque job ID. Do not replay a side effect whose postcondition is unknown; mark it 'needs recovery' and ask the owner verbally before continuing that one step.
- **missing:** Boot-time reconciliation of processing jobs and open ledgers; A job↔ledger join and an explicit per-step postcondition/checkpoint record; Process-group cancellation and idempotent retry for run_shell; A browser checkpoint endpoint that records inspected tab/frame identity and last verified DOM state

### "“Check my authenticated work sites and tell me only what changed that actually needs me today.”"
- **useful because:** This turns the previously denied portal briefing into the correct browser-owned workflow. The browser extension can see sessions that the relay and Mac cannot, compare the current page against a private per-site baseline, and the pendant can deliver a short interruption-free spoken list. The owner does not have to expose passwords or manually copy portal pages into chat.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Background model performs site-by-site diffing and priority ranking; realtime only speaks the final two or three actionable items.
- **latency:** Under 30 seconds after the owner asks; site inspection is parallelized and bounded to 5 seconds per tab.
- **cost:** ~$0.02–$0.10 per request, mostly DOM/text extraction and ranking; screenshots are used only when a page is visual or ambiguous.
- **security:** Authenticated content stays in the extension until it has been reduced to an owner-approved summary. Never send cookies, tokens, hidden form values, or full page HTML to the relay. Site allowlists and a local encrypted baseline are required; any suggested reply or mutation is returned as a draft, not silently submitted.
- **missing:** Per-site authenticated-session allowlist and encrypted local baselines; A browser diff/priority endpoint that can inspect several existing tabs without copying secrets; A scheduler that runs only when the browser session is present and reports stale/unavailable sites truthfully; Relay payload redaction for browser-derived summaries

### "“Run this long Mac job and keep me informed; if it fails, recover it without me staring at the screen.”"
- **useful because:** The pendant becomes a remote operator, not a one-shot command button. The Mac starts the work, emits milestone receipts, and on failure captures the failing step and a bounded diagnostic; the relay speaks only meaningful transitions. The owner can say 'retry the safe step' or 'stop' while away from the laptop, and a dead Mac process cannot be mistaken for completion.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Cheap background worker watches receipts and classifies recoverable failures; realtime is reserved for a concise alert or the owner's spoken intervention.
- **latency:** Immediate dispatch acknowledgement under 1 second; milestone alerts within 2 seconds of receipt; recovery begins within 5 seconds of a retry instruction.
- **cost:** ~$0.005–$0.03 per job when deterministic receipt rules handle progress; model cost appears only on an ambiguous failure.
- **security:** Command text, paths, and output may contain secrets. Store full logs locally and send the relay a redacted error plus job ID. Recovery must use action idempotency/postconditions, never blind whole-job replay; destructive or externally visible steps remain explicitly described to the owner even though the Mac policy permits maximum access.
- **missing:** A real-time per-step event stream including exit code, pid/process-group, effective command after rewrites, and bounded stdout/stderr; Cancellation wired to the child process group rather than only the between-step abort signal; Retry/idempotency engine connected to /execute; Boot reconciliation that marks orphaned processing jobs and closes ledgers; Pendant command correlation for spoken retry/stop intents

### "“Undo the last thing you did, even if it happened in Safari or through a Mac app.”"
- **useful because:** Today undo only covers a small set of local actions. The owner should get a semantic reversal: identify the last externally visible action, explain its evidence and reversibility, then perform the compensating action—restore a moved file, revert an edit, withdraw a queued browser change, or draft a correction—across the browser and Mac. The pendant gives one concise spoken result instead of forcing the owner to remember which surface acted.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension
- **model tier:** Background model builds and checks a compensation plan from receipts; realtime only handles the owner's short undo request and result.
- **latency:** Under 5 seconds to identify the candidate and describe the reversal; under 20 seconds for a reversible local/browser compensation.
- **cost:** ~$0.01–$0.06 per invocation; dominated by reconstructing the action and checking the current browser/app state.
- **security:** A reversal can itself have consequences. Never claim success without a postcondition check; preserve the original receipt and compensation receipt locally. Do not automatically send external corrections or cancel financial/legal actions—speak the proposed compensation and require an explicit owner instruction for those exceptional classes.
- **missing:** A typed compensation registry for Mac and browser actions, including postconditions; Cross-surface receipt ordering with stable action IDs and effect scope; Browser extension support for reversing its supported mutations rather than only reporting them; A pendant utterance/intention route that addresses a specific receipt

### "“Explain what I’m looking at on my screen, privately, and point me to the exact source.”"
- **useful because:** The owner can ask through the pendant while a sensitive page is open and receive a grounded spoken explanation without sending a raw screenshot or authenticated page to the relay. Mac vision reads the pixels, the browser extension supplies the accessible text and URL/title, and the answer cites the exact visible region or DOM element. If asked, it can then open the cited source or copy only the selected fact.
- **path:** pendant → relay-realtime → mac-vision → browser-extension → mac-planner
- **model tier:** A local/cheap vision-text pass fuses DOM and pixels; realtime is used only for the short spoken answer.
- **latency:** 2–4 seconds for ordinary pages; up to 8 seconds for dense visual documents.
- **cost:** ~$0.005–$0.04 per request, with local extraction avoiding repeated cloud image tokens.
- **security:** Raw screen pixels and authenticated DOM remain on the Mac. Send the relay only a redacted question, answer, and source locator; source locators must not include query-string tokens. Blur password/payment fields before any model sees them, and refuse to read hidden or off-screen content.
- **missing:** A local multimodal fusion service joining a screenshot region to browser DOM coordinates; A redaction/secret-field detector that runs before model invocation; A source-locator protocol understood by the pendant response renderer

### "“Hand this unfinished task to my future self tomorrow, with exactly what I saw and what remains.”"
- **useful because:** Instead of a reminder with no context, the owner gets a sealed, resumable handoff capsule: the pendant records the intent, the Mac captures the relevant project and app state, the browser extension records only the permitted tab identity and evidence, and the relay delivers a compact brief at the chosen time. Opening it restores the task without reconstructing the whole conversation.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision
- **model tier:** Background model compresses and redacts the capsule; scheduled delivery uses a cheap model, with realtime only for the spoken capture and reminder.
- **latency:** Capture acknowledgement under 2 seconds; capsule generation under 10 seconds; restore under 15 seconds.
- **cost:** ~$0.01–$0.05 per handoff, mostly state compression; scheduled delivery costs pennies or less.
- **security:** Capsules may contain private page titles, paths, and snippets. Encrypt them locally, store an expiry and allowed surfaces, and exclude passwords, cookies, and full screenshots by default. The spoken reminder should reveal only the capsule title until the owner asks to open it.
- **missing:** A first-class encrypted handoff-capsule store with expiry and surface permissions; A Mac snapshot adapter for foreground app, project, and relevant window state; A browser evidence adapter that stores stable locators plus a redacted excerpt; A restore planner that validates state before reopening or editing anything


## Changes it proposed to its own stack

### `mac-harness` — Replace the shell execution internals with a durable command envelope: preserve original and effective (rewrite-resolved) command, use execFile/argv where possible while retaining an explicit raw-shell escape hatch, record redacted environment fingerprints, capture exit code/signal/pid/process-group and bounded stdout/stderr, pass AbortSignal to the child process group, close the ledger with the jobId, and reconcile processing/open records at boot. Expose one append-only per-step event stream consumed by pendant and relay.
- **owner gets:** When the owner asks the pendant to do something while away from the Mac, they will know what actually ran, whether it finished, and can stop or resume a stuck task. A crash will no longer leave a job falsely marked 'running' forever or cause an unsafe blind replay.
- effort: Medium-high: executor/computerControl, jobTracker, actionLedger, orchestrator, and bridge event plumbing; add migration for existing records and integration tests around rewrites, SIGTERM, restart, and retry.  ·  risk: Changing exec semantics can break shell-dependent commands; preserve raw-shell mode and compare old/new envelopes in shadow logging first. A process-group kill may terminate grandchildren intentionally; record the tree and offer recovery from the last settled step. Reconciliation must distinguish an orphan from a still-running external process.
- cost: Negligible API cost; modest local disk for capped event/receipt records (roughly <1 MB per rolling history).  ·  latency: Tiny dispatch overhead (<100 ms); event emission is local and asynchronous. Restart recovery becomes faster because stale jobs are identified at boot.
- security: Better than today: current run_shell inherits AGENT_TOKEN and model keys and records none of that. Record only a hash/name allowlist of environment keys, never values; keep full stdout local and redact relay events.
- depends on: Define the job↔ledger correlation field and close-ledger lifecycle; Choose a stable child-process runner with AbortSignal/process-group support; Add relay/pipeline subscription for per-step events


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing capabilities: resume a crashed Mac/browser task from a verified checkpoint; browser-owned authenticated work-site change triage (the correct re-file of the previously denied portal briefing); and a wearable long-job operator with truthful milestones, recovery, and spoken retry/stop. I also proposed the underlying Mac execution-envelope change, but the recorder flagged it as close to an existing observability idea, so it should be treated as a refinement rather than a separate feature. Live discovery confirms Safari (9 tabs) and the Mac bridge are online; browser inspections are empty, and the test mobile device is offline. I still need implementation—not another wrapper—of the missing joins: job↔ledger correlation and boot reconciliation, per-step event streaming, child-process cancellation/retry, browser authenticated diff baselines, and pendant intent correlation. The previously queued mac USB-serial diagnostics request remains the only access request; I will not re-ask for it.

**Biggest unknown:** Whether the browser extension can expose stable authenticated tab/frame identity and a redacted DOM-diff baseline without leaking session content; that determines whether the portal-triage capability can be built safely rather than merely planned.

