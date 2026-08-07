# Harness derivation — mac-terminal — round 53

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “save this for later” while I’m wearing the pendant, capture what I’m looking at on my Mac or in Safari together with my spoken note, and let me retrieve it later by asking what I saved about that topic."
- **useful because:** The owner can preserve fleeting context hands-free instead of copying links, taking screenshots, or losing the reason something mattered. Retrieval can return the source, a concise reminder, and the original Mac/browser location so the thought is actionable rather than just archived.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic intent detection and local metadata capture for the save operation; use a cheap background model to transcribe/tag and summarize; use the realtime model only for the spoken confirmation and later conversational retrieval. Escalate to planner only when sources conflict or the owner asks for synthesis.
- **latency:** Acknowledge the save on the pendant within 1 second; finish capture within 3 seconds when Mac/browser are online. Retrieval should begin speaking within 1–2 seconds, with deeper synthesis allowed asynchronously.
- **cost:** Usually under $0.01 per save/retrieval; dominant costs are speech transcription and optional background summarization. Deterministic saves with a URL/title/selection and short voice transcript need little or no LLM usage.
- **security:** The capture may include private page text, selected text, screenshots, clipboard contents, or voice. Require explicit utterance, capture only the focused tab/window and bounded selection, encrypt stored capsules, retain source URL and hashes rather than whole pages when possible, and provide spoken “delete the last capsule” plus dashboard deletion. Never capture passively or send page contents to the relay unless the owner invoked save.
- **missing:** A cross-surface capture contract carrying pendant utterance, focused Mac window, selected text/clipboard, and active browser tab with provenance; A Mac/browser bridge method to read focused context and return a bounded, cited snapshot; Durable encrypted capsule storage with retention, deletion, and semantic retrieval; A pendant command and retrieval intent wired through the relay; Dashboard UI showing capsules, provenance, and deletion controls


## Changes it proposed to its own stack

### `integration` — Add a live capability-preflight and fallback router before Mac/browser jobs. Snapshot /ops/status plus browser heartbeat and relay reachability into a short-lived matrix (shell available, UI permissions, screen capture, browser online, pending queue). Annotate each planned step with required capability; if unavailable, automatically choose a viable alternate (shell/AppleScript for app-state work, browser queue for later, relay background job) or return one precise repair instruction. Never block trusted FULL_CONTROL shell actions; this is observability and routing only. Include the matrix and chosen fallback in the job receipt.
- **owner gets:** Requests stop failing mysteriously when the Mac lacks Accessibility/Screen Recording or the browser extension is offline. The pendant can say exactly what happened and still complete the parts that do not need the unavailable surface, instead of making the owner repeat themselves.
- effort: Medium: status snapshot schema, planner annotations, fallback selection, heartbeat freshness/TTL, and receipt/dashboard rendering.  ·  risk: A stale status could choose the wrong route or queue work unexpectedly. Use short TTLs, recheck immediately before execution, mark assumptions in receipts, and preserve the existing unrestricted shell path.
- cost: Negligible API cost; one small local status/heartbeat read per job. Saves planner tokens and retries.  ·  latency: ~50–150 ms local preflight; avoids multi-second failed UI attempts.
- security: No new authority and no approval gate. Status contains permission and connectivity metadata only; redact paths/tokens from receipts.
- depends on: A typed representation of Mac action requirements and results; Browser heartbeat/command queue with request IDs; Durable job receipts (chg-5fc73ce3)

### `mac-harness` — Extend the existing action receipts with a shell execution envelope: normalized command digest, cwd, selected non-secret environment facts, start/end monotonic timestamps, timeout/signal, exit status, stdout/stderr byte counts, bounded tail plus content-addressed full output artifact, and a retry classification (transient, dependency/permission, deterministic failure). Stream progress events to the pendant for jobs longer than a few seconds, while keeping raw output local unless the owner asks for it.
- **owner gets:** When a Mac task fails, the owner gets an immediate, intelligible explanation and can resume from the failed command instead of wondering whether anything ran. Long jobs feel alive on the pendant, and huge logs do not flood spoken context.
- effort: Medium: wrap runShell result handling, local artifact retention/expiry, progress events, and receipt/dashboard fields.  ·  risk: Command output may contain secrets; default to local storage, redact common token/password patterns, cap spoken previews, and expose explicit artifact deletion. A bad retry classifier could repeat a non-idempotent command, so retries must remain advisory and never automatic for shell.
- cost: Low local disk use with bounded retention; lower model cost by sending a short failure summary instead of full logs.  ·  latency: Negligible overhead; progress streaming adds no blocking round trip.
- security: Improves auditability without restricting FULL_CONTROL_MODE. Sensitive output stays on the Mac by default; only hashes and redacted summaries cross the relay.
- depends on: Implemented action receipts (chg-5fc73ce3); A durable local job/log retention policy


## What it asked for

_Nothing._
## Its own summary

Discovered fresh live state: Mac local agent is full-control enabled but not ready because Accessibility and Screen Recording are missing; computer-use is disabled, browser extension is offline with 3 pending commands, while relay and Mac bridge are reachable. Proposed a non-blocking cross-surface capability-preflight/fallback router so trusted shell work continues while unavailable UI/browser steps are explained or queued, and proposed shell execution envelopes with bounded/redacted output artifacts, progress, exit/timeout data, and advisory retry classification layered onto existing receipts. No approval gates or shell restrictions proposed.

**Biggest unknown:** The newly granted mac_read_diagnostics tool has no implementation, so I could not independently read current OS/battery/network/process details beyond /ops/status. Implementing that read-only diagnostic path (or exposing equivalent authenticated status fields) is the only concrete thing still needed from the orchestrator; no additional permission is needed for the proposals.

