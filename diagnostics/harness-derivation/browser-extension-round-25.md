# Harness derivation — browser-extension — round 25

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’m looking at this page—tell me what matters, and if I say ‘the second option’ or ‘fill that in,’ use the thing I’m pointing at.”"
- **useful because:** Today the owner must switch between speaking to the pendant and manually describing or operating an authenticated Safari page. This would make the pendant a hands-free co-pilot for the exact private page in front of them: it can ground references such as “that,” “the red warning,” and “the second row” in the current browser view, while keeping the browser session on the owner’s Mac.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime model handles short spoken references and turn-taking; a cheaper background model normalizes the page’s visible DOM/accessibility tree and maintains stable element labels; the Mac/browser harness performs the requested interaction.
- **latency:** Under 700 ms for page-context acknowledgement and under 2 s for a grounded read or reversible fill; refresh the page grounding after every navigation, scroll, or mutation.
- **cost:** Roughly $0.01–$0.05 per interaction depending on realtime audio duration and page extraction; DOM/accessibility extraction and compact grounding dominate, not the browser command itself.
- **security:** Only the visible/explicitly requested region should leave the Mac; redact passwords, payment fields, tokens, and hidden DOM before relay/model transmission. Bind element labels to tabId, URL, and a short-lived page fingerprint so stale speech cannot target a different page. Show a compact action receipt on the pendant/dashboard and stop at irreversible submits or sends with the prepared payload visible.
- **missing:** A browser extension command for a live, redacted accessibility/DOM viewport snapshot with stable short-lived element IDs and optional owner-selected region; A low-latency relay stream that associates each voice turn with the current Safari tab and page fingerprint; Mac planner grounding that resolves deictic speech (that/this/second option) against the latest snapshot and regenerates plans when the page changes; Pendant/dashboard rendering of a small page preview or numbered element list plus action receipts


## Changes it proposed to its own stack

### `browser-harness` — Add an offline-aware browser command escrow and wake-up loop. When Safari is offline, do not leave POST /execute blocked behind a 45-second waiter or strand its two pending commands: persist each command as a leased, stateful item (queued, dispatched, acknowledged, result, expired), immediately return a jobId to the Mac planner, and have the relay notify the pendant of 'waiting for Safari'. On the next extension heartbeat, reconcile device/tab identity, discard expired leases, and resume only idempotent steps (navigate/read/extract); if the step was a click/type, re-read the page and require the planner to regenerate it from current evidence. Emit a compact result/evidence event to the Mac and a spoken completion/failure update to the pendant.
- **owner gets:** A browser request made while the Mac or Safari is asleep would become dependable background work instead of a mysterious timeout. The owner can leave home, let the browser reconnect, and receive a concise answer when the private page was actually checked—without duplicate clicks or silently acting on a stale tab.
- effort: Medium-high: durable queue/lease schema, heartbeat-triggered dispatcher, restart recovery, and planner/pendant job-status wiring; test disconnects between every browser step.  ·  risk: A reconnect can expose a changed page or stale login. Never replay mutation steps; revalidate read evidence and mark ambiguous commands for review. Recover orphaned jobs with lease expiry and an operator-visible receipt; preserve the existing no-approval-gate policy for execution.
- cost: Small D1/R2 and relay storage cost; negligible model cost for retries, with most cost avoided by not re-running whole jobs. One short status event per transition.  ·  latency: Immediate job acknowledgement; completion latency is bounded by the next Safari heartbeat rather than a 45-second HTTP timeout. Revalidation adds one read before any resumed mutation.
- security: Job capsules must contain opaque session/device references, not cookies or page secrets; encrypt sensitive extracted evidence at rest and scope dispatch to the registered Safari device/tab affinity.
- depends on: chg-16bc5dee durable browser job runner and result stream; chg-14accc01 replacement for the blocking 45-second browser wait; Safari extension heartbeat/device registration and a functioning browser poll/result path


## What it asked for

_Nothing._
## Its own summary

Discovered the live browser fleet is currently unusable: Safari is offline, home-chrome is also offline with no tab, and two commands are pending. I recorded a new browser-harness change: offline-aware command escrow with leases, heartbeat wake-up, restart recovery, and safe replay rules, so private browser work returns a job immediately and resumes only after fresh evidence. I also notified relay-realtime that pendant status/completion events are needed.

**Biggest unknown:** Whether the Safari extension will reconnect and whether the two pending commands are legitimate recoverable work or stale requests; the current status endpoint does not expose their command IDs or ages.

