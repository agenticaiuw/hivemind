# Harness derivation — relay-realtime — round 226

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Tell me if the thing I asked you to do is stuck, and why.”"
- **useful because:** Completion is not enough; the owner needs to know when a task is stalled (waiting for a login, blocked by permissions, or failing repeatedly) so they can step in quickly, especially when they’re away from the Mac.
- **path:** relay-realtime → faculty-perception → faculty-action → mac-planner → browser-extension → pendant
- **model tier:** relay for user-facing status; background tier for periodic checks and classification
- **latency:** Quick spoken answer (<1s) when asked; background detection can run at a low cadence to reduce cost.
- **cost:** Moderate: periodic status checks while a job is active; dominant cost is status polling and any page checks required to classify the block.
- **security:** Do not expose sensitive content from pages or documents. Summaries should be minimal and only state the blocking reason (auth needed, permission denied, repeated failures, waiting on user input).
- **missing:** A standardized taxonomy of job failure/blocked states across Mac actions and browser actions.; A watcher that can inspect job receipts/logs to classify ‘blocked’ vs ‘failed’ vs ‘running’ without bespoke per-job logic.; Optional: a browser-side page-watch integration for detecting auth prompts when a web task stalls.

### "“If I start a task that needs a login or approval, ask me for it once, then resume automatically.”"
- **useful because:** This bridges the wearable and the Mac/browser: the owner can approve a prompt from anywhere, and the system can continue without losing context or forcing them to babysit.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → faculty-action
- **model tier:** relay for the prompt and confirmation; cheaper planner tier to resume work
- **latency:** Prompt must arrive quickly (<2s). Resume timing depends on user response and task complexity.
- **cost:** Low to moderate: one interruption event plus resuming the job. Dominant cost is the resumed task execution.
- **security:** Treat approvals as high-risk. Require explicit confirmation for sending emails, purchases, or destructive actions. Log what was approved and why.
- **missing:** A resumable job model that can pause on an auth/approval checkpoint and continue after confirmation.; A secure, auditable approval channel to the pendant/phone, with replay protection and expiry.; A way to serialize minimal task state so the Mac/browser can pick up where it left off.

### "When I say “handle this errand,” have the pendant, relay, my authenticated browser, and my Mac carry a bounded transaction from research through checkout, stopping only when a condition I set is met and telling me exactly what happened."
- **useful because:** The owner can complete real-world errands while away from the desk instead of manually moving search results, sessions, and decisions between devices. It is materially more useful than a search or a Mac action because the wearable supplies intent and approval, the browser supplies private sessions, and the Mac supplies local execution.
- **path:** pendant → relay → browser-extension → mac-planner → mac-vision
- **model tier:** Realtime relay for clarification and concise spoken checkpoints; background mac-planner/browser workers for research, comparison, and execution; mac-vision only when a page cannot be represented structurally.
- **latency:** Acknowledge in under 1 second; research may take 30–120 seconds; ask one spoken checkpoint only at the owner-defined boundary; final receipt within 10 seconds of completion.
- **cost:** Roughly $0.03–$0.20 per errand, dominated by planner/browser calls and vision fallbacks; realtime speech should be limited to intent and checkpoint turns.
- **security:** Private browser cookies and purchase details remain on the paired browser/Mac unless a cloud browser is explicitly provisioned. The owner defines a maximum price, recipient, or other constraint; crossing it pauses for pendant confirmation. Persist an immutable action receipt and make retries idempotent to avoid duplicate orders.
- **missing:** A durable cross-surface transaction object with constraints, checkpoints, idempotency keys, and resumable state; A browser worker that can operate authenticated sessions when the Mac is asleep or offline; A pendant protocol for compact checkpoint questions and explicit approval replies; Receipt reconciliation across browser and Mac actions

### "When I dictate a thought while walking away from my desk, attach it to the exact project and place I was working in, then prepare the next action on my Mac so I can resume without reconstructing my context."
- **useful because:** A voice memo alone becomes another inbox. This would turn a fleeting thought into a resumable handoff: the wearable captures the thought, the relay resolves what it refers to, and the Mac reopens the relevant project and prepares—not silently executes—the next step.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Realtime relay for capture and one disambiguation question; cheaper background model for entity/project linking; mac-planner for reversible resume preparation; mac-vision for confirming the visible workspace.
- **latency:** Capture acknowledgement under 1 second; linking and preparation within 30 seconds after connectivity; if confidence is low, ask at the next pendant interaction rather than guessing.
- **cost:** About $0.01–$0.06 per handoff, mostly context linking and one planner call; no model call needed for the initial memo acknowledgement.
- **security:** The thought and inferred project context may be sensitive. Store only the transcript plus a narrow project reference, expose confidence and source evidence, and never send or publish anything as part of resume preparation. The owner can discard the handoff from the pendant.
- **missing:** A Mac-side workspace checkpoint containing focused app, document identity, browser tabs, and unsaved-work indicators; A resolver that links a short spoken thought to that checkpoint and memory projection with confidence; A typed resumable handoff record connecting pendant outbox, relay job, and Mac preparation; A pendant affordance to accept, reject, or discard the proposed resume target

### "Let the pendant act as my interruption gate: summarize who or what needs me, let me say “later,” “draft a reply,” or “mute this,” and carry that decision through my Mac notifications and authenticated browser without opening a dozen apps."
- **useful because:** The owner is often away from the Mac and cannot inspect every notification. A single spoken triage loop reduces attention switching while still allowing the owner to defer, draft, or silence an interruption across whichever surface generated it.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Realtime relay for the spoken triage exchange; background classifier for urgency and duplicate grouping; Mac planner for notification and draft actions; browser extension for web-originated alerts.
- **latency:** Surface a new urgent item within 5 seconds of ingestion; answer a spoken triage command in under 2 seconds; batch low-priority items into a digest rather than interrupting.
- **cost:** Approximately $0.01–$0.08 per triage batch, dominated by classification and any vision/browser inspection; realtime tokens stay small because only summaries reach the relay.
- **security:** Notification text can contain highly private content. Keep raw payloads local where possible, send only redacted summaries to the relay, preserve the original source and intended target in every action, and require explicit confirmation only for sending or destructive changes. “Mute” must be reversible and time-bounded.
- **missing:** A cross-surface notification intake and deduplication stream; A privacy-preserving summarizer with source links and urgency evidence; Mac notification controls and browser-originated event hooks; A durable triage decision record with expiry, undo, and spoken result delivery


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities: bounded cross-surface errands with constraints and receipts; project-aware voice-to-Mac resumption; and a spoken interruption gate spanning Mac and authenticated browser. The first is the highest-leverage capability because it turns the pendant into a trustworthy front door for real transactions, not merely a remote control. They require new connective state and workers between existing plan/execute/jobs/browser pieces, plus durable receipts, privacy boundaries, and explicit checkpoint delivery.

**Biggest unknown:** Whether the existing workbench handoff and browser-session routes already expose enough state to implement the project-aware resume flow, or need a new durable cross-surface handoff/transaction coordinator.

