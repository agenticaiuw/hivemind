# Harness derivation — relay-realtime — round 138

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Check my open tabs and accounts for anything urgent and draft responses, but don’t send anything."
- **useful because:** It saves time and reduces anxiety by surfacing only what matters, while keeping control with the owner.
- **path:** browser → mac-bridge → relay
- **model tier:** Cheaper planner/extractor for page analysis; relay only for conversational control.
- **latency:** Spoken acknowledgement fast; analysis can take longer and return a concise summary.
- **cost:** Dominated by browser automation time and page extraction tokens.
- **security:** Authenticated pages contain sensitive data. Must preserve provenance, avoid exfiltration, and require explicit approval before any submission.
- **missing:** Reliable browser command queue with typed results; Page-watch/watch definitions; Sandboxed server-side browser execution for public pages

### "Give me a hands-free quick status: what’s running, what’s queued, and anything I should know right now."
- **useful because:** While wearing the pendant, the owner can get oriented without opening the laptop.
- **path:** relay → mac-bridge → pendant
- **model tier:** Realtime only; this is a short spoken report.
- **latency:** Under a second for acknowledgement; a few seconds for status aggregation.
- **cost:** Low; dominated by status reads.
- **security:** Status should not leak sensitive content; only report task names and states.
- **missing:** A unified status endpoint across relay jobs and Mac agent state; Implemented relay_job_status for reliable summaries

### "“I’m away from my desk—take this half-formed thought, find the relevant project context, turn it into the right artifact, and tell me exactly what you created.”"
- **useful because:** The owner can convert an idea spoken while walking into a usable issue, note, code TODO, or document without remembering where the project lives. The pendant supplies intent and continuity; the Mac supplies local files and apps; the browser supplies authenticated project context; the relay makes the result understandable over voice.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension
- **model tier:** Realtime relay for capture and brief clarification; background mac-planner for artifact selection and construction; cheap summarizer for the spoken receipt.
- **latency:** Acknowledge in under 1 second, then deliver a completion receipt within 30 seconds for ordinary projects; long work may continue with a later voice notification.
- **cost:** Roughly $0.03–$0.15 per invocation, dominated by planner/tool turns and any browser context extraction; realtime model should only handle the short conversational envelope.
- **security:** The spoken idea and selected local/browser context leave the pendant and may include private code or work data. The system must state which artifact and sources were used, avoid silently publishing or sending externally, and provide an undoable receipt for mutations.
- **missing:** A cross-surface context resolver that maps a spoken project reference to local files, open authenticated tabs, and recent relay history; An artifact-intent classifier and constructors for issue/note/TODO/document across Mac and browser surfaces; A durable completion-notification path to the pendant; A compact, spoken artifact receipt with source citations and undo linkage

### "“I’m in the middle of something on my Mac. Listen to this question, inspect what I’m currently looking at, and answer without taking over; if I say ‘do it’, apply the smallest fix and report what changed.”"
- **useful because:** This is the single most useful everyday capability: the pendant becomes a safe remote pair-programmer and computer companion while the owner remains in flow. It combines live speech, the Mac’s current UI/local state, and the browser’s authenticated page into one context, while separating explanation from execution so a spoken follow-up can turn advice into action.
- **path:** pendant → relay → mac-vision → mac-planner → mac-terminal → browser-extension
- **model tier:** Realtime model handles the short question and answer; mac-vision or read-only inspection gathers current UI state; mac-planner/mac-terminal performs the explicitly requested minimal mutation; a cheap verifier checks the resulting state.
- **latency:** Answer from current visible context within 3–8 seconds; after “do it”, execute and verify within 15 seconds for a small fix, with immediate spoken progress if longer.
- **cost:** Approximately $0.05–$0.30 per interaction, dominated by screen/context acquisition and planner turns; cache the current inspection during the conversational turn to avoid resending it.
- **security:** Screen contents can expose secrets, and a spoken “do it” can mutate code or browser state. The system must scope execution to the immediately discussed target, preserve before/after receipts, never submit or send external communications implicitly, and make spoken scope explicit.
- **missing:** A live current-context snapshot API joining focused Mac window, terminal state, and active authenticated browser tab; A relay conversation state that binds “it/this/the error” to a cited inspected target; A strict explain-then-apply state machine with before/after verification (not a permission gate); A functioning mac-vision loop and low-latency push of progress/completion back to the pendant

### "“My service is down. Check the authenticated dashboards and the logs on my Mac, tell me the likely cause in plain English, and if it is a safe recovery, fix it and stay with me until it is verified.”"
- **useful because:** The owner can start a real incident while away from the desk with one sentence. The browser contributes private monitoring/deployment context, the Mac contributes local logs and control-plane access, and the pendant keeps the owner informed through a concise voice conversation instead of requiring a laptop. No single existing node can correlate those sources and verify recovery end to end.
- **path:** pendant → relay → browser-extension → mac-terminal → mac-planner → dashboard
- **model tier:** Realtime relay handles acknowledgement, clarification, and concise progress; a cheaper background diagnosis model correlates logs and dashboard evidence; mac-planner/mac-terminal performs the recovery and a deterministic verifier checks health.
- **latency:** Acknowledge in under 1 second, first diagnosis in 10 seconds, and speak progress every 15 seconds; safe recoveries should be verified within 60 seconds, with long incidents continuing asynchronously.
- **cost:** Approximately $0.10–$0.60 per incident, dominated by repeated log/dashboard reads and planner turns; realtime token use stays small by summarizing evidence between updates.
- **security:** This may expose production secrets and could cause destructive operational changes. Keep raw logs on the Mac/browser surface, redact credentials before relay/model transfer, record every command and evidence citation, constrain automatic recovery to an owner-defined safe command set, and require an explicit spoken confirmation for irreversible or externally visible operations.
- **missing:** A cross-surface incident session that joins authenticated dashboard evidence with Mac logs under one incident ID; Allowlisted diagnostic and recovery command metadata with deterministic health probes; Streaming progress and evidence receipts to the pendant; A diagnosis/verifier worker that can continue after the realtime turn ends; Secret redaction at the Mac and browser boundaries


## Changes it proposed to its own stack

### `browser-harness` — Add a durable browser command queue with typed results and provenance (tabId, URL, timestamp, DOM locator) and support for server_browser_actions fallback when the Mac is offline.
- **owner gets:** Browser automation becomes trustworthy and resilient; tasks can continue even if the Mac sleeps.
- effort: High: queue, result typing, provenance, retries, and Cloudflare Browser Run integration.  ·  risk: Automation could drift on page changes; mitigate with typed extraction and explicit irreversible checkpoints.
- cost: Moderate; dominated by browser runtime and extraction tokens.  ·  latency: Queueing adds delay but enables reliability and parallelism.
- security: Strong isolation for public browsing; strict handling of authenticated sessions; never exfiltrate secrets.
- depends on: server_browser_actions implementation; session binding in browser harness


## What it asked for

### `s19-75il` (skill) — spoken_status_interrupt
- does: Allows the pendant button to interrupt any long spoken status report and request a shorter summary or next item.
- must be on-device because: It depends on immediate button press handling and local audio playback control, especially when network is slow.
- trigger: button press during playback
- storage: none
- RAM budget: ~2–5 KB for state machine and debounce; minimal buffers only

## Its own summary

Recorded three new owner-facing capabilities: voice-to-artifact capture from a spoken half-formed thought; cross-surface change briefing since the last checkpoint; and wearable incident response that correlates authenticated dashboards with Mac logs and verifies recovery. The most useful is the explain-then-apply live companion, but it collided with existing resume/current-context ideas and was not recorded, so I did not count or restate it. The recorded proposals deliberately identify the missing connective layers rather than pretending the existing routes already provide them.

**Biggest unknown:** Whether the backlog already contains a more specific version of the incident-response capability or the checkpointed cross-surface change briefing; the recorder accepted both, but flagged them as connective work around existing primitives.

