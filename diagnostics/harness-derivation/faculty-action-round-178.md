# Harness derivation — faculty-action — round 178

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent-and-browser-readiness** — Live Mac agent is ready with Accessibility and Screen Recording granted, full-control and vision loop enabled (vision upload consent false), Safari browser bridge online with 9 tabs and zero pending commands. Relay reachable and Mac bridge online.
  - evidence: GET /ops/status HTTP 200 at round 178; permissions.ready=true, accessibility.trusted=true, screenRecording.granted=true, browserExtension.online=true, relay.reachable=true.

## Capabilities it proposed

### "“Do that, then give me an independently checkable proof I can replay later.” After a Mac or browser action, bind the executor receipt to a fresh faculty-perception verification and deliver a compact evidence receipt to the pendant; later I can ask for the proof without rerunning the action."
- **useful because:** This is the single most useful missing behavior for trustworthy agency: a successful API receipt is not evidence that the owner’s file, browser field, or app state actually changed. The owner gets a durable, replayable answer rather than “I think I did it.”
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-action → faculty-perception
- **model tier:** Use the realtime model only to summarize the owner’s request and speak the result; use the cheaper background tier to canonicalize receipts and hashes. faculty-perception performs the independent read-only check.
- **latency:** Action path unchanged; verification adds 1–3 seconds after execution. Spoken proof should arrive within 5 seconds, with a pending chime if the Mac is slow.
- **cost:** Roughly one low-cost perception call plus storage per action; realtime tokens only for a short spoken summary. Dominant cost is screenshot/browser-state acquisition, not synthesis.
- **security:** Evidence defaults to hash-only and stores no page secrets or message bodies. Private/secret locators require explicit owner confirmation; expired receipts are marked unverifiable rather than guessed. A verification must never mutate state.
- **missing:** A correlation field carrying operation_id and step_id from faculty-action receipts into faculty-perception verification; A durable evidence-receipt store with expiry and redaction policy; Pendant retrieval command for a receipt by spoken reference

### "“Watch that task while I’m away and interrupt me only if it is stuck, unsafe, or needs my decision.” The relay should supervise a long-running Mac/browser job, detect heartbeat and postcondition stalls, and ask for a physical pendant decision to retry, cancel, or continue."
- **useful because:** Today a delegated task can sit failed or ambiguous while the owner is away. This turns the always-awake relay and worn device into a useful watchdog: the owner is interrupted for decisions, not routine progress, and never loses a job silently.
- **path:** relay-realtime → relay → mac-planner → mac-vision → browser-extension → faculty-action → faculty-perception → pendant
- **model tier:** A cheap scheduled/background worker evaluates heartbeats, deadlines, and deterministic receipts. Realtime is invoked only when a human-facing escalation needs concise speech.
- **latency:** Heartbeat evaluation every 15–30 seconds; escalation delivered within one interval. No conversational model on healthy heartbeats.
- **cost:** Minimal storage and background inference; roughly one cheap evaluation per interval per active job. Realtime cost only on escalation.
- **security:** The watchdog may cancel or retry only within the owner’s action policy and never silently approve irreversible work. Pendant approval uses the existing physical transaction latch; browser secrets stay on the browser surface. Escalations include job identity and risk, not sensitive content.
- **missing:** A relay scheduler that consumes job heartbeats and deadlines; A normalized stalled/unsafe/needs-decision event from Mac and browser executors; Watchdog policy data keyed by action risk, defaulting to stage-for-approval

### "“When the Mac is unavailable, keep my spoken follow-up attached to the task and continue it automatically when the link returns.” A press-and-speak correction should become a typed, ordered continuation of the active Mac/browser job, not a separate orphan memo."
- **useful because:** A dropped USB, sleep, or network link currently breaks conversational continuity exactly when the owner is mobile. The owner can say “actually use the other attachment” or “stop that” once; the system delivers it in order when the acting surface returns, without repeating the whole request.
- **path:** pendant → ESP32 audio bridge → relay-realtime → relay → mac-planner → browser-extension → faculty-action
- **model tier:** On-device capture and relay queueing are deterministic. A cheap background tier transcribes/normalizes the short follow-up; realtime is unnecessary unless the owner is actively conversing.
- **latency:** Immediate local acknowledgement; queue write under 100 ms. Resume within one relay polling interval after reconnection, with a spoken confirmation only after executor acceptance.
- **cost:** Small transcription and queue cost per interruption; no model spend while connected and idle. Audio is uploaded only when it cannot be sent live, honoring the existing failure-path storage rule.
- **security:** Follow-ups are scoped to an opaque active-job ID, expire, and are rejected if the job is already committed or cancelled. Never execute locally on the pendant. A destructive correction still enters physical approval. Queued audio is encrypted and deleted after relay acknowledgement.
- **missing:** A typed continuation envelope extending the existing OUTBOX manifest with target operation/step and expiry; Executor semantics for pause/resume and exactly-once follow-up delivery; A reconnection handshake that reports whether the active job is still safely mutable

### "“Use the Mac screen to act, but never send screenshots off this Mac.” Run the computer-use loop with local-only visual evidence, and fall back to AppleScript/browser DOM actions when local vision cannot resolve the target; ask before enabling cloud vision."
- **useful because:** The Mac is now Accessibility- and Screen-Recording-ready, but live status reports visionUploadConsented=false. This gives the owner useful GUI control without silently exporting private screens, while making the boundary explicit instead of failing mysteriously.
- **path:** mac-vision → mac-planner → browser-extension → faculty-perception → faculty-action → relay-realtime
- **model tier:** Use deterministic AppleScript and browser DOM inspection first. A local vision model, if installed, handles screenshots; realtime only explains a blocked step or asks for consent. Never upload screen pixels by default.
- **latency:** DOM/AppleScript actions under 2 seconds; local vision under 5 seconds; cloud-vision consent prompt may pause until the owner answers.
- **cost:** No API vision cost in local-only mode; local CPU/GPU is the dominant cost. Cloud mode costs per screenshot and is opt-in.
- **security:** Screen pixels remain on the Mac in default mode. Cloud upload requires per-job consent, redaction of secrets, and a visible audit event. GUI mutations still require the existing policy/physical approval path when risky.
- **missing:** A local screenshot inference provider or explicit deterministic fallback contract; A per-job vision-upload consent state surfaced to faculty-action; A perception result that identifies whether evidence was DOM, AppleScript, or local/cloud pixels

### "“Before you send or submit anything, prove that the page and account are still the ones I approved.” Bind an approval to a browser origin, tab identity, account fingerprint, and a short validity window; refuse if navigation, login, or meaningful form changes occur before submission."
- **useful because:** A physical approval can be genuine yet stale: a tab may navigate, an account may switch, or a checkout form may change after the owner approves. This gives the owner protection against time-of-check/time-of-use failures that ordinary confirmation does not catch.
- **path:** pendant → browser-extension → mac-vision → faculty-perception → faculty-action → relay-realtime
- **model tier:** Deterministic browser metadata and cryptographic hashes do the checking. Realtime only explains a refusal. No expensive model is needed unless the page must be semantically re-inspected.
- **latency:** Under 300 ms for URL/tab/account/hash checks; semantic re-inspection may add 2–5 seconds. Refuse closed-loop rather than guessing.
- **cost:** Negligible API cost; dominant cost is an occasional browser inspection. Storage is a small approval envelope and precondition digest.
- **security:** Never store credentials or page bodies in the envelope. Account fingerprints must be salted and opaque. Approval expires quickly and is single-use. Any mismatch cancels submission and requires a fresh approval.
- **missing:** A canonical browser precondition digest covering origin, tab, account identity, and relevant field structure; A browser-side atomic check immediately before submit; A refusal event that the pendant can explain without exposing private page contents

### "“For my most sensitive actions, require both my pendant gesture and my Mac’s local biometric unlock.” Use the pendant as the physical intent witness and Touch ID/macOS authentication as a second, independent presence check before committing."
- **useful because:** The pendant proves that the owner deliberately gestured, but a stolen or unattended pendant should not be enough for a high-impact action. Two physically different factors make account deletion, money movement, credential changes, and public posting materially safer without requiring the pendant to receive secrets.
- **path:** pendant → mac-planner → mac-terminal → browser-extension → faculty-judgement → faculty-action → relay-realtime
- **model tier:** Deterministic policy and macOS authorization APIs; no realtime model on the commit path. Realtime only speaks the request and result.
- **latency:** One extra local authentication prompt, normally under 10 seconds. Approval expires if Touch ID is not completed promptly.
- **cost:** Near-zero API cost; implementation is local macOS authorization integration plus a small relay transaction record.
- **security:** The relay must receive only a signed success/failure assertion, never biometric data. The pendant still never receives passwords or page contents. The owner chooses which risk classes require dual approval; unknown policy entries default to staged approval.
- **missing:** A macOS LocalAuthentication/Touch ID assertion route in the agent; A policy field selecting dual-factor action classes; A transaction protocol that binds the biometric assertion to the exact pendant approval digest

### "“Let me take over exactly where you stopped, without showing me the whole private screen.” When an action is blocked or uncertain, deliver a pendant-sized handoff containing the reason, the safe next decision, and a resumable opaque checkpoint; I can approve, edit, or abandon it by voice or button."
- **useful because:** A failed computer-use task currently forces the owner to reconstruct context from a Mac screen. This makes interruption recoverable while preserving privacy: the owner gets the minimum decision surface and can resume the same operation rather than restarting it blindly.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-action
- **model tier:** Background tier compresses executor state into a structured checkpoint; realtime handles only the owner’s short spoken choice. Deterministic executor state, not a model, controls resume safety.
- **latency:** Checkpoint generation under 2 seconds after a block; pendant summary under 10 seconds. Resumption must verify the checkpoint before any mutation.
- **cost:** Small background summarization and durable state cost per blocked task. No screenshot or page-body upload is needed for the normal path.
- **security:** Checkpoint contains opaque locators and redacted state, not credentials or full page contents. It expires, is bound to the job and browser session, and cannot resume after an account/origin change without fresh verification and approval.
- **missing:** A resumable checkpoint schema with safe/unsafe boundaries between steps; A privacy-preserving state compressor that emits decision-relevant facts only; Executor support for resume-from-checkpoint with independent postcondition verification


## What it asked for

_Nothing._
