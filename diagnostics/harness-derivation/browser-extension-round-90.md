# Harness derivation — browser-extension — round 90

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser bridge liveness** — At round 90, /browser/status reports online:false for home-chrome only, with 9 pending commands; Safari is not listed. /browser/poll nevertheless claims a stale navigate command for home-chrome (attempts 10), so the queue can continue assigning work to an offline device.
  - evidence: GET /browser/status returned {online:false, devices:[home-chrome offline], pendingCommands:9}; GET /browser/poll returned command browser_fc12217f-842e-4751-8697-c6c71706bd52 claimedBy home-chrome attempts:10.

## Capabilities it proposed

### "When I’m looking at a private webpage, let me ask about it from the pendant and get a concise, sourced answer; keep the answer tied to that tab, and let me say “prepare that” to fill the reversible parts without sending or submitting anything."
- **useful because:** This combines the browser’s unique access to logged-in pages with the pendant’s hands-free voice and the Mac/relay’s ability to retain a short-lived task context. The owner can leave the desk, ask about the exact page they were viewing, and receive evidence rather than a generic web answer. It also turns a one-shot extraction into a safe reviewable workflow.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Realtime for the short spoken question and answer; background/cheaper model for extraction normalization and drafting. Escalate to the expensive tier only when the page is ambiguous or the owner asks for synthesis across tabs.
- **latency:** 2–5 seconds for an already-captured page context; up to 15 seconds for a fresh read of one tab. Draft/fill may take 10–30 seconds and must stop before submit/send.
- **cost:** About $0.01–$0.08 per interaction depending on page length and whether synthesis is needed; browser round trips and context tokens dominate, not the small metadata operations.
- **security:** Private DOM text must stay in the authenticated browser-to-local-agent path and only the minimum cited snippets should be sent to the model/relay. Bind context to tabId/session and expire it after roughly 15 minutes or navigation. Never speak secrets by default; redact credentials and payment data. Filling is reversible, but submission, sending, purchasing, or account changes remain an explicit final step the system does not perform.
- **missing:** A live Safari heartbeat and functioning browser command enqueue path; current status is offline and POST /execute browser navigation times out.; A short-lived page-context record containing tab/session identity, extracted snippets, source URL, timestamp, and redaction metadata, addressable from the voice turn.; A pendant-to-browser continuation intent that resolves pronouns such as “that” against the active page context and produces a reviewable fill plan.

### "Before I submit a form on a private site, compare its important fields with the matching information in my other logged-in accounts and documents, point out any conflicts with cited evidence, and prepare corrections without submitting anything."
- **useful because:** People routinely encounter stale addresses, mismatched names, duplicate account numbers, and conflicting dates across portals. Today the browser can inspect a page or fill a form, but it cannot act as a cross-account consistency checker that explains which value differs, where each value came from, and what correction would be made. This prevents expensive mistakes while keeping the owner in control of the final submission.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheaper background model for field extraction, normalization, and deterministic comparisons; use realtime only to answer the owner's spoken questions or summarize conflicts. Escalate to the expensive tier only for genuinely ambiguous identity/entity matching.
- **latency:** 15–30 seconds to inspect the active form and up to three explicitly selected authenticated sources; under 3 seconds for a spoken explanation once the comparison packet exists.
- **cost:** Roughly $0.02–$0.12 per check; browser extraction and transmitting several source snippets dominate. Deterministic field comparisons should avoid repeated model calls.
- **security:** Only inspect tabs/accounts the owner explicitly names or has selected; never search arbitrary private tabs. Keep raw values local where possible, send normalized fields plus minimal evidence, redact credentials and financial secrets, and expire comparison packets quickly. Do not change any field or submit automatically. The owner must review the proposed before/after values.
- **missing:** A multi-tab authenticated comparison packet with field-level provenance, normalization rules, and confidence scores.; A browser-side field mapper that can identify semantic form fields and corresponding source fields across heterogeneous logged-in sites.; A pendant/Mac review surface that presents conflicts compactly and accepts per-field keep/correct decisions before invoking reversible fill actions.


## Changes it proposed to its own stack

### `browser-harness` — Add a browser-bridge liveness and recovery controller: commands are leased to a device only while its heartbeat is fresh; stale claims automatically return to a pending queue, device selection prefers the real Safari registration, and an offline result is surfaced immediately instead of waiting 45 seconds. Add a startup probe that can bootstrap a tab with browser_navigate once Safari returns, plus an operator-visible count of orphaned commands.
- **owner gets:** Private-page requests will either work promptly or clearly tell the owner that Safari is unavailable. A sleeping/restarted extension will no longer strand work against the dead home-chrome registration or make the pendant appear frozen.
- effort: Moderate: bridge queue state machine, heartbeat freshness/lease expiry, deterministic device selection, and tests for restart/race conditions.  ·  risk: A command could be reclaimed while Safari is still executing, causing duplicate navigation or extraction. Use command IDs/idempotency keys and mark late results as duplicates; never replay mutations automatically. Recovery is deleting/retrying the orphaned command.
- cost: Negligible API cost; small durable queue/heartbeat metadata. No new hardware cost.  ·  latency: Offline detection in under a heartbeat interval rather than a 45-second timeout; online actions unchanged, with at most one retry for a read-only command.
- security: Improves isolation by preventing commands from being delivered to the wrong registered browser. Device identity and tab/session affinity must be enforced; do not auto-replay irreversible browser actions.
- depends on: A functioning Safari extension heartbeat and browser command enqueue implementation; Existing /browser/poll and /browser/result/:commandId semantics; Existing browser session/tab affinity and action receipts


## What it asked for

_Nothing._
## Its own summary

Round 90: I discovered that the browser grants are still schemas, not live implementations. A direct browser navigation through POST /execute timed out; live status now shows Safari absent/offline, home-chrome offline, 9 pending commands, and /browser/poll repeatedly claiming a navigate for the dead home-chrome device (attempt 10). I recorded this finding, messaged mac-planner, proposed a new cross-surface capability for asking about the exact authenticated page from the pendant and preparing reversible follow-up, and proposed a recovery controller for stale browser leases/device selection. What I still need is not another model permission: restore the real Safari heartbeat and implement the enqueue/lease recovery path so authenticated page reads can actually execute.

**Biggest unknown:** Whether Safari is merely disconnected at this moment or the extension registration/heartbeat path has regressed; until a fresh Safari device heartbeat appears, private browser workflows cannot be verified.

