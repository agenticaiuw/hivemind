# Harness derivation — unified — round 267

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live surface availability** — At round 267, Safari on MacIntel and home-macbook-bridge are online; nrf9160-pendant and all listed browser_node/mobile probe devices are offline. Any owner-facing freshness claim must label pendant/browser-node data unavailable rather than infer absence.
  - evidence: discover(category=devices) returned Safari on MacIntel online, home-macbook-bridge online, nrf9160-pendant offline, task30-probe-browser/task30-probe-browser-b offline, and iOS probe devices offline.

## Capabilities it proposed

### "When I ask what happened to a request, give me one compact answer that distinguishes planned, dispatched, completed, undone, failed, and merely claimed by the relay, and tell me what evidence is missing."
- **useful because:** Today job records, action receipts, browser results, and audio delivery acknowledgements are separate. Owners hear promises that can be mistaken for completion; this produces a trustworthy outcome rather than a plausible sentence.
- **path:** relay → mac-bridge → browser → pendant
- **model tier:** deterministic aggregation first; background model only to summarize conflicting evidence
- **latency:** Under 1 second for existing job IDs; under 3 seconds when browser/audio evidence must be joined
- **cost:** <$0.002 per query; route reads and receipt joins dominate, with no model call in the common case
- **security:** Redact page contents and sensitive action parameters. Never infer success from a plan or relay claim alone. If evidence conflicts, say unresolved and provide the exact next safe observation; mutation and undo remain separately confirmed.
- **missing:** A stable cross-surface correlation key shared by relay jobs, Mac jobs, browser commands, and audio artifacts; A typed outcome reducer with precedence rules and an explicit unknown state; A single owner-facing route that joins GET /jobs/:jobId/receipts with browser and pipeline receipts

### "Before I trust a spoken answer, tell me whether it came from a live browser session, a current Mac observation, a cached relay record, or an old memory—and let me ask for a fresh check."
- **useful because:** Safari and the Mac bridge can be online while the pendant and browser nodes are offline, and the owner has already received repeated failed probes. A freshness/provenance envelope prevents stale cached context from sounding like present truth.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** deterministic freshness/provenance classification; realtime phrasing only
- **latency:** Immediate provenance label from cached state; fresh checks within 5 seconds when the relevant surface is online
- **cost:** Negligible model cost; one or two authenticated status reads per refresh
- **security:** Do not reveal URLs, page contents, or private data merely to explain freshness. Fresh-check requests must be read-only unless separately confirmed; stale or failed observations must remain visibly distinct from absence.
- **missing:** A common evidence envelope with observedAt, source, freshness TTL, and failure reason; A spoken/UI convention for labeling cached versus live facts; A safe refresh coordinator that queries only the requested surface

### "Run a no-side-effect rehearsal of my next scheduled routine and tell me which inputs are available, which actions would need confirmation, and where it would stop if a surface is offline."
- **useful because:** Scheduled routines currently report completed/failed but give the owner no way to inspect tomorrow's behavior without actually firing it. A shadow run makes browser, Mac, relay, and pendant dependencies visible before an unattended action happens.
- **path:** relay → mac-bridge → browser → pendant
- **model tier:** deterministic planner and permission classifier; background model only to explain the resulting plan
- **latency:** Under 5 seconds for a routine plan; never wait on an offline surface beyond its health timeout
- **cost:** <$0.005 per rehearsal; mostly local route reads, with optional one background explanation
- **security:** Strictly forbid writes, sends, purchases, file deletion, or browser submission in shadow mode. Redact page text and secrets. If a routine contains an unclassifiable action, fail closed and label it rather than simulating success.
- **missing:** A true dry-run executor that invokes observation steps but blocks all mutation actions; A dependency graph linking routine steps to required surface health and permissions; A receipt format distinguishing observed input, simulated action, blocked action, and unknown outcome

### "After you submit something on my behalf, verify that the external system actually accepted the change—not just that a button was clicked—and tell me exactly what proves it or that it remains unverified."
- **useful because:** A browser command can complete locally while a site rejects, queues, or silently drops the request. The owner needs outcome semantics (server-confirmed, locally observed, queued, or unknown), especially for forms, bookings, and settings where a click receipt is not the result.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** deterministic verification ladder first; background model only to map a page's confirmation evidence to the requested intent
- **latency:** Verify within 5 seconds after submission; if asynchronous, schedule bounded follow-up checks and report pending rather than claiming success
- **cost:** <$0.01 per submission; dominated by one or two browser observations, with model use only for ambiguous confirmation text
- **security:** Never resubmit automatically. Bind verification to the original target/session and intent, redact confirmation contents, and require confirmation before any follow-up mutation. A timeout or ambiguous page must remain unknown.
- **missing:** A typed verification contract declaring acceptable evidence for each action (HTTP/server acknowledgement, durable page state, email receipt, or local-only observation); A browser before/after state capture with a stable semantic fingerprint rather than screenshots alone; A bounded follow-up scheduler that can poll read-only and attach the evidence to the original job

### "Before you act in a logged-in website, prove which account and workspace are active, compare that with the target I named, and refuse if the session identity is ambiguous or wrong."
- **useful because:** A browser can be online and authenticated to the wrong account, tenant, or profile. A successful click in the wrong workspace is worse than a visible failure, particularly for mail, purchases, and business tools.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** deterministic identity checks from bound page/session signals; realtime model only to explain a refusal
- **latency:** Under 2 seconds before any external mutation; refusal should be immediate when identity evidence is missing
- **cost:** <$0.001 per check; browser inspection only
- **security:** Treat identity as untrusted page evidence until bound to the specific tab/session. Never speak or store full account identifiers when a redacted domain/workspace label suffices. Refuse rather than guess; require the existing physical approval path for high-risk actions.
- **missing:** A browser identity-attestation primitive that returns redacted account/workspace evidence bound to a tab and timestamp; A target-identity field in action plans and receipts; A hard preflight gate in execute that cannot be bypassed by generic browser success


## Changes it proposed to its own stack

### `integration` — Add an effect-verification phase to browser/Mac jobs: before mutation, persist the requested intent and an allowed evidence recipe; after mutation, capture a redacted semantic before/after fingerprint and run bounded read-only checks. Reduce the result to server-confirmed, durable-state-confirmed, locally-observed-only, pending, or unknown, and attach it to the existing job receipt without retrying the mutation.
- **owner gets:** The owner will stop hearing 'done' when the system only knows that a click or API call occurred. Failed bookings, rejected forms, and queued changes become visible and actionable without dangerous duplicate submissions.
- effort: Medium-high: shared receipt schema, browser semantic snapshotting, per-action evidence recipes, and a read-only polling worker.  ·  risk: Sites may change markup or confirmation wording; recover by returning unknown and preserving the raw redacted evidence for inspection. Never auto-resubmit. Polling must stop at a deadline.
- cost: Small storage increase per job; usually no additional model cost, with occasional low-tier classification for ambiguous confirmation text.  ·  latency: Adds 1–5 seconds for synchronous verification; asynchronous effects become explicitly pending rather than blocking indefinitely.
- security: Semantic fingerprints and evidence must be redacted and bound to the original session/target. No new privilege should be granted; verification is read-only after the initial approved action.
- depends on: A stable cross-surface job correlation ID; A typed evidence-recipe schema and redaction policy; Browser semantic state capture beyond the current command result


## What it asked for

_Nothing._
## Its own summary

Round 267 produced three distinct capability proposals: (1) unified job outcome/evidence status across relay, Mac, browser, and audio; (2) freshness/provenance labels distinguishing live, cached, stale, and failed observations; and (3) side-effect-free rehearsal of scheduled routines. The extracted-memory inspection/erase proposal collided with an existing memory-control idea and was not restated. Live discovery found Safari and the Mac bridge online, while the pendant and browser/mobile probe nodes are offline; this was recorded as a finding.

**Biggest unknown:** The implementation still lacks the connective contracts: a cross-surface correlation key and outcome reducer, a common evidence freshness envelope, and a genuinely mutation-blocking routine dry-run executor. The owner-facing mandatory-confirmation policy and browser identity attestation remain unavailable from prior requests; I did not re-request them.

