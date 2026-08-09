# Harness derivation — mac-terminal — round 183

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “save this work” on the pendant, make a resumable handoff of exactly what I am doing: the active Mac app/window, Safari tab and page state, project and git diff, current terminal jobs, and the last voice turn. Later I can say “continue that” and the relay restores the right browser/Mac context and asks only the next unresolved question."
- **useful because:** A timestamp marker cannot recreate a task. This turns walking away, closing the lid, or losing LTE into a real resume point rather than a memory search.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Background model builds and compresses the handoff capsule; realtime is used only for the short capture acknowledgement and resume dialogue.
- **latency:** Acknowledge the button/voice in under 500 ms; capture capsule in under 5 s; resume context in under 3 s.
- **cost:** About $0.01–$0.04 per capture/resume depending on transcript and page-state compression; Mac/browser collection dominates latency, not tokens.
- **security:** Capsule may contain page titles, selected text, code and terminal output. Keep it local by default, encrypt at rest, redact secrets, and require explicit owner wording before capturing page content or terminal output.
- **missing:** A Mac snapshot endpoint combining foreground window, active terminal jobs, project/git state and a stable browser session handle; A browser extension export of resumable page state (not just inspection); A relay capsule store with expiry, encryption and conflict-safe resume tokens; A resume executor that can restore/focus the Mac and browser without duplicating prior side effects

### "Run a spoken task as a cross-device flight: show me each meaningful step on the pendant, execute the Mac shell/browser actions, then independently verify the result on the other surface before telling me it worked. If verification fails, keep the task open and explain what is actually true instead of claiming success."
- **useful because:** The most dangerous failure today is a command that returns success while the real-world change did not happen, or a browser action that landed in the wrong session. Independent cross-surface proof would make voice control dependable enough for consequential daily work.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Cheap deterministic verifiers inspect exit status, targeted file/app state and browser DOM; realtime speaks only the concise progress and final truth.
- **latency:** Immediate dispatch indication under 500 ms; each step under its normal tool latency; final proof within 2 s after the last action.
- **cost:** $0.005–$0.03 per task; deterministic checks are cheap, with model cost only for ambiguous verification.
- **security:** Verification can expose private DOM or command output. Send hashes/structured claims to relay where possible, retain raw evidence locally, and require confirmation only for the underlying owner policy's high-impact actions (not for verification).
- **missing:** A cross-surface task ID and step dependency protocol shared by relay, Mac and browser; Typed verifier actions (process exit code, file hash, active app state, browser assertion) alongside existing free-form execution; Pendant progress frames that distinguish dispatched, verified, contradicted and unknown; A durable evidence receipt joining POST /execute jobs to browser command results

### "Tell me “what is blocking me?” and have the system diagnose the live bottleneck across my Mac and browser: stalled shell jobs, failing tests, unsaved editor changes, a browser page waiting for input, network/auth problems, or a pending action. Give me one recommended next action and let me say “do it” to carry it out."
- **useful because:** This is the highest-value everyday use of the hive: the pendant hears the question, while only the Mac and authenticated browser can see the real obstruction. It replaces vague status reports with an actionable diagnosis.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Perception uses cheap structured probes first; judgement uses a slower model to rank blockers; realtime is reserved for the spoken answer and execution confirmation.
- **latency:** First answer in 3 s from cached probes; refresh only the implicated surface, then offer action in under 5 s.
- **cost:** $0.01–$0.06 per diagnosis; most probes are local and deterministic, model cost is dominated by correlating evidence.
- **security:** Do not upload full terminal output or authenticated page bodies by default. Return redacted facts and provenance; browser content and destructive fixes require explicit owner confirmation.
- **missing:** A shared live-observation schema for Mac jobs, focused app, browser session state, network and pending relay work; A blocker-ranking model with evidence links and freshness timestamps; A one-action remediation planner that can safely hand off to POST /execute or browser commands; Spoken provenance: the pendant must say which surface observed each blocker

### "Say “make me a decision packet on this” while I’m looking at any Safari page, and have the hive turn that live page plus relevant authenticated tabs, local project files and current Mac state into a concise, cited packet: competing options, recommendation, unresolved risks, and a ready-to-run action plan. Let me ask follow-up questions by voice while the source tabs remain pinned to the packet."
- **useful because:** Today the browser, Mac shell and pendant can each retrieve or act, but they cannot jointly turn the owner’s actual authenticated context into a durable decision artifact with traceable evidence. This would collapse research, judgment and execution planning into one interaction without requiring the owner to copy sensitive material between surfaces.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Background model extracts and cites sources; judgement model compares options and identifies uncertainty; realtime only handles the owner’s spoken follow-ups and reads the final recommendation.
- **latency:** Acknowledge capture in under 500 ms, show source collection progress within 2 s, and produce a first packet in under 30 s; follow-up answers under 3 s from the cached evidence graph.
- **cost:** Roughly $0.05–$0.30 per packet depending on number of pages and local artifacts; browser extraction and evidence storage dominate, with follow-ups cheap against the cached packet.
- **security:** Authenticated tabs, source text and local files are highly sensitive. Keep raw evidence on the Mac/browser session, send only selected excerpts and hashes to the relay/model, display every source and freshness timestamp, expire packets automatically, and never silently include a tab merely because it is open.
- **missing:** A browser-side evidence capture/export API that can preserve authenticated page provenance and selected excerpts without exposing cookies; A Mac evidence collector for local files, project state and command outputs with per-source consent and secret redaction; A durable evidence graph linking excerpts, claims, counterclaims and generated actions; A packet artifact and dashboard/pendant navigation model that supports citations and voice follow-up; A cross-surface inclusion protocol so the owner can say “this page and the repo” and both surfaces resolve the same task

### "Give me a physical privacy panic action: when I press the dedicated pendant button, immediately stop microphone capture, revoke the relay’s ability to request new work, pause browser observation, mute Mac playback, and show me exactly what was stopped. A second deliberate press should restore the previous state without losing an in-progress task."
- **useful because:** The owner needs a trustworthy way to regain privacy faster than finding the right app or browser tab, especially when the pendant is always present and authenticated sessions are open. This is not an approval gate; it is an owner-controlled emergency stop across every surface.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Firmware and deterministic relay/Mac actions do the stop and restore; no expensive model call is needed. Realtime only speaks a short confirmation after the local stop is acknowledged.
- **latency:** Local microphone cutoff and LED acknowledgement under 100 ms; relay revocation and Mac/browser stops under 1 s; spoken status under 2 s.
- **cost:** Negligible per use; a small persistent state record and one authenticated control message.
- **security:** The stop command must work without cloud connectivity and be authenticated by a device-held key. It must fail closed locally, never erase evidence or silently discard queued work, and state which surfaces were unreachable. Restore must not automatically resume recording or replay side effects.
- **missing:** A second dedicated physical privacy control or an explicitly specified existing sw1 wiring and debounce path; An offline device-to-Mac authenticated emergency frame independent of the normal audio/relay transport; Relay lease/revocation semantics that reject new work immediately and expire outstanding authority; Mac and browser emergency-stop endpoints for capture, observation, playback and queued execution; A durable pre-stop snapshot so restore is exact and observable

### "Let me say “work on this for ten minutes, then stop and tell me what you learned.” The relay should coordinate the Mac and authenticated browser, enforce the time/token/action budget across every child task, preserve the partial evidence and exact next step, and return a spoken progress report even if one surface disappears."
- **useful because:** Today a multi-step request has no owner-visible budget: it can hang on a shell process, keep browser sessions busy, or stop without a useful handoff. A time-boxed delegation lets the owner safely give the hive real work while retaining control of when it ends and what survives.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard → faculty-judgement → faculty-action
- **model tier:** Background model performs the bounded work; deterministic watchdogs enforce wall-clock, action-count and token budgets; realtime only announces start, expiry and result.
- **latency:** Start acknowledgement under 500 ms; hard stop within 1 s of deadline; final spoken summary within 3 s, with partial artifact available immediately.
- **cost:** Owner-selected budget, e.g. $0.02–$0.50 per delegation; watchdog and persistence are local, while model calls and browser extraction dominate.
- **security:** Budgets must be enforced by the relay and local agent, not trusted to model instructions. Never extend a deadline implicitly; preserve private evidence locally with expiry, and clearly mark incomplete work and actions that may have escaped before cutoff.
- **missing:** A relay-owned delegation lease with monotonic deadline, action/token ceilings and per-surface child leases; Hard cancellation that reaches shell process groups, browser commands and pipeline audio rather than merely setting a cooperative flag; A partial-result artifact schema with completed, unknown and not-started steps; A scheduler that prevents overlapping delegations from racing over the same browser session or project; Pendant status and expiry semantics for a delegation that continues after the voice turn


## Changes it proposed to its own stack

### `model-routing` — Add an evidence-first blocker router: for every spoken Mac request, run bounded read-only probes for active job state, browser session health, project state and network in parallel, then select the smallest model and surface needed. Cache each observation with a freshness budget and provenance; skip cloud/realtime reasoning when a deterministic local answer is complete, and escalate only the unresolved contradiction.
- **owner gets:** Simple questions like “is my test still running?” become nearly instant and free, while genuinely cross-device problems get the right context instead of a slow generic answer. The owner hears which machine knows the fact and how fresh it is.
- effort: Medium: define an observation schema, parallel probe fan-out, freshness/contradiction rules, and routing metrics; no change to unrestricted execution.  ·  risk: Stale cache or conflicting surfaces could mislead. Every spoken claim must include age and source, and contradictions must yield “unknown” plus a targeted refresh rather than a confident synthesis.
- cost: Reduces expensive model calls for routine status; adds only local probe traffic and a small cache.  ·  latency: Parallel probes reduce first-answer latency from serial multi-surface checks to the slowest probe; cache hits should answer in hundreds of milliseconds.
- security: Send structured, redacted facts to models rather than raw terminal/browser contents. Authenticated page bodies remain local unless the owner asks for analysis.
- depends on: A shared observation envelope with source, timestamp, freshness and evidence reference; Parallel read-only adapters for /jobs, /browser/status, /machine-context and /projects/active; A routing policy that can select local Mac, browser, background or realtime models; Pendant speech that names provenance and uncertainty


## What it asked for

_Nothing._
## Its own summary

This round produced four non-identical directions: a resumable cross-surface work capsule (the pendant captures a live Mac/browser task, not merely a timestamp); independent Mac-plus-browser proof before spoken completion; a “what is blocking me?” diagnosis that correlates live jobs, browser state and projects; and an evidence-first model router that parallelizes cheap probes and escalates only contradictions. I also proposed the genuinely useful offline USB mode, but the recorder identified it as already present in the backlog, so I did not re-submit it. The shell flight-recorder idea was also rejected as an existing observability proposal rather than restated. I asked mac-planner for current USB/browser readiness evidence.

**Biggest unknown:** The practical readiness of the two physically connected serial chips: whether an end-to-end USB audio/serial framing path already exists, and whether browser export can return resumable authenticated page state. The mac_usb_serial_diagnostics and browser_export_local_artifact requests are already queued and must not be re-asked; those results are what I still need before proposing another hardware-specific capability.

