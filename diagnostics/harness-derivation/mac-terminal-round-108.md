# Harness derivation — mac-terminal — round 108

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-browser execution reliability** — Authenticated /journal shows 120 retained jobs, 146 actions, 18 failures, and browser_navigate idempotency key act_36a2da2b0b8c failed 8/8; failures consume ~45 seconds and distinguish bridge offline from online-but-no-answer timeout. All 0 actions are currently undoable; 112 actions lack tier attribution.
  - evidence: GET /journal at 2026-08-07T14:11:49Z and GET /logs show browser_navigate failures with explicit offline/timeout reasons and 45,3xx ms durations.
- **browser bridge health gap** — GET /browser/status reports online=true but tabId/windowId/tabCount/browserName/extensionVersion are null or empty and pendingCommands=9; this explains why a binary online flag cannot distinguish usable bridge from stalled extension.
  - evidence: GET /browser/status at 2026-08-07T14:12:20.503Z returned device home-chrome with online true, lastSeenAt current, but no tab/window identity and 9 pending commands.

## Capabilities it proposed

### "If something I asked you to do in Safari gets stuck, recover it automatically when possible; otherwise tell me in one short pendant message what is blocked, what you tried, and whether anything changed."
- **useful because:** Today a browser navigate can spend ~45 seconds timing out, and repeated attempts cannot distinguish an offline extension from Safari being blocked. A worn-device alert plus Mac-side diagnosis would turn silent stalls into a trustworthy result, without asking the owner to watch the Mac.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background for failure classification and concise notification; deterministic health probes and retry orchestration first, escalating to planner only when diagnosis is ambiguous
- **latency:** Emit an immediate deterministic 'still working' or 'blocked' status within 2 seconds of a bridge failure; run one bounded recovery attempt within 15 seconds; final pendant summary within 30 seconds. Never replay a non-idempotent browser write automatically.
- **cost:** Usually $0 for status/retry logic; roughly 1 small-model call only for ambiguous multi-signal diagnosis, under $0.01 per incident. Main cost is a short Mac/browser round trip, not tokens.
- **security:** Private URLs, tab metadata, and failure snippets stay in the authenticated local-agent path; do not send page contents to the relay unless needed for the owner's spoken summary. Recovery may reopen Safari or reattach a tab, so record each attempted action and whether it had a write effect; automatic retries are limited to reads/navigation explicitly marked idempotent.
- **missing:** A bridge-health handshake that reports polling age, active tab, modal/blocker state, and a request correlation id; A failure classifier mapping offline, no-answer timeout, and page-load timeout to distinct recovery recipes; A durable retry lease that prevents duplicate browser writes and links recovery receipts to the original job; Pendant push events for job state transitions, not only final responses

### "When Safari says an action timed out, tell me whether it actually took effect anyway—without repeating it—and keep checking until you can prove the final state or tell me exactly what remains unknown."
- **useful because:** The owner currently gets an ambiguous 45-second browser failure: the bridge can be online but not answer, and there is no reliable way to know whether a click or navigation partially happened. This capability resolves the dangerous 'did it go through?' question across the wearable, relay, Mac, and authenticated browser, without blindly replaying a possibly successful action.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic reconciliation first (request/receipt correlation, tab state, page fingerprint, and bounded follow-up read); use background model only to interpret conflicting page evidence; reserve realtime planner for an owner asking follow-up questions.
- **latency:** Speak an immediate uncertainty notice in under 2 seconds, perform the first verification within 10 seconds, and continue bounded background verification for up to 5 minutes. The owner can leave and receive a final pendant notification when evidence settles.
- **cost:** Most cases require no model call; roughly $0.001–$0.01 only for ambiguous page-state interpretation. Cost is dominated by authenticated Safari round trips and retained evidence, not inference.
- **security:** Verification must stay in the owner's authenticated Safari session; send only a concise result and redacted evidence summary to the relay/pendant. Never retry a write during reconciliation. Preserve before/after screenshots or field hashes under the existing retention policy, and explicitly label 'not provable' rather than infer success.
- **missing:** A durable uncertain-outcome state distinct from failed/succeeded, with a reconciliation deadline; A transaction correlation token carried from pendant request through Mac dispatch, browser command, and page observation; A browser-side read-only postcondition checker that can reattach the original tab and compare semantic state without replaying the action; A pendant event for 'verified succeeded', 'verified unchanged', and 'could not prove' outcomes


## Changes it proposed to its own stack

### `browser-harness` — Add a bridge watchdog and failure-aware executor around browser actions. Before dispatch, issue a cheap local health snapshot (extension polling age, Safari frontmost/window state, tab/session id); attach it to the existing job and receipt. On timeout, stop waiting at a short staged deadline, classify offline vs no-answer vs page-load, and run a single read-only reattach/retry when the action is idempotent. Persist the original request id, retry lease, health snapshots, and final effect verdict so the dashboard and pendant can explain exactly what happened. Keep FULL_CONTROL_MODE and unrestricted capability unchanged; this is telemetry and recovery, not a blocking policy.
- **owner gets:** Safari failures become fast, legible, and recoverable instead of burning 45 seconds and leaving uncertainty about whether a page changed. The owner can trust 'nothing changed' because it is backed by a receipt and pre/post health evidence, while successful reads recover without manual extension toggling.
- effort: Medium: browser bridge heartbeat endpoint and polling-age state; executor state machine for staged deadlines and idempotent retry; receipt schema extension; tests for offline, modal, timeout, and successful reattach; dashboard/pendant event formatting.  ·  risk: A false idempotency classification could duplicate a write, so only actions explicitly declared read/navigation-safe may retry; all others fail once with evidence. A watchdog may misdiagnose a slow page, recovered by preserving the original timeout as a final deadline and never discarding raw bridge errors.
- cost: Negligible storage (a few KB per failed job, subject to existing retention); no model cost for normal paths. One background model call only when deterministic signals conflict.  ·  latency: Health probe adds under 200 ms; staged timeout returns a progress event quickly while retaining a bounded overall deadline. Successful retries add at most one bridge round trip; failed actions avoid repeated 45-second blind waits.
- security: Health metadata is local and authenticated; do not capture DOM or page text in watchdog snapshots. Correlate by opaque request/tab ids and apply existing receipt retention/deletion.
- depends on: Authenticated browser extension heartbeat/polling-age signal; Explicit per-action idempotency/effect metadata in browser command queue; Pendant job-transition push channel; Existing action receipts and /journal observability


## What it asked for

_Nothing._
## Its own summary

Discovered a concrete reliability gap rather than proposing shell restrictions. Live /journal shows 146 retained actions with 18 failures; browser_navigate failed 8/8, each consuming about 45 seconds. /browser/status says online=true while exposing no tab/window/browser identity and 9 pending commands, so the current health signal is not actionable. I recorded this and proposed a cross-surface Safari recovery capability plus a browser-harness watchdog: staged deadlines, offline/no-answer/page-load classification, one safe retry only for idempotent reads, and receipt-linked evidence. FULL_CONTROL_MODE remains unrestricted as required.

**Biggest unknown:** The browser extension's actual polling/heartbeat and tab-attachment contract is still missing. I still need (from implementation, not more authority): a heartbeat with polling age and modal/tab state, explicit per-action idempotency/effect metadata, a retry lease/correlation protocol, and pendant push for intermediate job states. No additional shell permission is needed.

