# Harness derivation — unified — round 101

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I put the pendant back on, say “catch me up,” and get one short, prioritized spoken digest of anything that happened while I was away across the Mac job queue, authenticated browser watches, and pendant-held alerts—with source, age, and a clear resume/cancel choice for unfinished work."
- **useful because:** Today results are split across relay jobs, browser state, pipeline history, and held offline alerts. This gives the owner one reliable re-entry point after sleep, meetings, or a dropped connection, without replaying stale actions or forcing them to inspect a dashboard.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background for assembling and ranking the digest; deterministic reducers for status, age, deduplication, and resume/cancel eligibility; realtime only for the spoken request and final delivery
- **latency:** Under 3 seconds for the first spoken sentence; detailed evidence can continue in the background. Never block on the browser if it is offline—say that explicitly and use its last cited state.
- **cost:** Usually one cheap background call (~2–4k input tokens, <200 output tokens); deterministic job/watch/alert reads dominate latency, not model cost. No planner-tier call unless the owner asks for interpretation.
- **security:** Only authenticated browser evidence already held by the bridge may be summarized; do not expose page contents in logs or audio beyond the owner's request. Resume must be bound to a specific unfinished job revision and require confirmation for irreversible actions. Offline or stale browser records must be labeled, never silently replayed.
- **missing:** A unified catch-up reducer over jobs, watches, pipeline alerts, and receipts; A durable per-item seen/acknowledged cursor shared by relay and Mac; Reconnect reconciliation that classifies stale, duplicate, read-only, and resumable work; A pendant phrase/gesture for resume versus cancel

### "After I approve something consequential, verify that it actually took effect across the services involved—not merely that the click or API call succeeded. Tell me when the external confirmation, receipt, calendar change, or account state agrees, and alert me if the surfaces disagree."
- **useful because:** A local execution receipt can say a button was clicked while the transaction still failed, queued, or produced a different result. The pendant, always-awake relay, Mac mail/calendar, and private browser are uniquely able to verify the real-world outcome and catch silent failures without making the owner inspect each service.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** deterministic polling and typed evidence matching first; background model only to reconcile ambiguous confirmations; realtime only to announce an urgent mismatch or answer a follow-up
- **latency:** Acknowledge the local action immediately, then verify within the service's normal confirmation window (seconds to an hour). Speak only on confirmed success, timeout, or contradiction; keep intermediate polling silent.
- **cost:** Low: mostly deterministic browser/Mac reads and scheduled relay checks; one background call (~1–3k input tokens) only when evidence needs semantic reconciliation. No planner-tier call for ordinary confirmations.
- **security:** Never infer success from a screenshot or a single redirect. Bind verification to the exact target/account/session and redact payment, health, and message contents from logs and spoken receipts. Require confirmation before any corrective retry, cancellation, or duplicate submission.
- **missing:** A typed outcome contract per action family (purchase, form submission, booking, message draft, reminder); Cross-surface correlation keys for a staged action, resulting receipt/email/event, and account state; A durable verification deadline and retry policy in the relay; Deterministic contradiction and duplicate-submission detection


## Changes it proposed to its own stack

### `integration` — Add a cross-surface approval-intent ledger. Every staged Mac or browser mutation receives an immutable action hash, target surface/session/tab identity, before-state evidence hash, expiry, and risk class. A pendant approval references that exact hash; the relay and Mac executor reject approvals after reconnect, state drift, expiry, duplicate use, or target mismatch, and return a spoken receipt explaining the refusal. Keep read-only and reversible actions flowing without a gate.
- **owner gets:** The owner can safely say “approve it” from the pendant even after walking away or losing the browser link, without risking that approval being applied to a different tab, changed form, or newly queued action.
- effort: Medium: shared ledger schema and verifier in relay/Mac agent, browser bridge identity checks, executor integration, and pendant receipt plumbing; add fault-injection tests for reconnect, duplicate delivery, and changed page state.  ·  risk: A legitimate approval may expire or be refused after a harmless page refresh; recover by presenting a fresh preview and requiring a new approval. Never fall back to position-based or latest-action approval.
- cost: Negligible storage and deterministic CPU; no additional model call. Small relay D1 and Mac journal growth per staged mutation.  ·  latency: A few milliseconds for hash/ledger verification; browser confirmation still depends on extension reconnection.
- security: Strongly reduces confused-deputy and replay risk. Store hashes and minimal metadata, not secrets or full page contents; redact sensitive field values from receipts.
- depends on: Browser reconnect reconciliation (browser currently offline with 9 pending commands); A durable staged-action/precondition representation shared by /execute and browser form-fill routes; Pendant-to-relay approval event carrying an action hash; Owner decision on expiry window for approvals

### `integration` — Add an outcome-verification protocol, distinct from execution receipts. Each staged action declares an expected external effect and correlation selectors (for example confirmation email/order ID, calendar event UID, or changed account field), an observation window, and an idempotent status probe. The relay schedules probes after Mac/browser execution, joins evidence from authenticated tabs plus Mail/Calendar, classifies confirmed/failed/pending/contradictory, and emits one durable result linked to the original action hash. A corrective action is never automatic.
- **owner gets:** They learn whether the thing they asked for really happened in the outside service, rather than receiving a misleading “done” because their Mac only completed the final click.
- effort: Medium-high: define outcome contracts for the first few action families, implement browser and AppleScript observers, durable relay timers, correlation/duplicate detection, and test delayed emails, redirects, retries, and partial failures.  ·  risk: Some services confirm slowly or never; the system could report pending too often. Recover with explicit deadlines and a “check again” option. False confirmation is more dangerous than timeout, so require two independent signals for high-impact actions where possible.
- cost: Small D1 records and periodic read traffic; background-model cost only for ambiguous evidence. No realtime-model increase.  ·  latency: No delay to the owner's immediate acknowledgement. Final status arrives asynchronously according to each service's confirmation time; browser-offline periods extend it.
- security: Reads remain in the authenticated browser/Mac boundary. Persist only correlation IDs, hashes, timestamps, and redacted evidence summaries; never store full payment or message content in the relay.
- depends on: A cross-surface action hash/manifest (so observations cannot attach to the wrong action); Browser reconnect and tab/session reattachment; Typed outcome contracts and service-specific read-only probes; A durable relay scheduler and notification path to the pendant


## What it asked for

_Nothing._
## Its own summary

Discovered the live stack is healthy for relay/Mac/audio but not browser: home-chrome is offline with 9 queued commands and no tab/session identity. /ops/snapshot confirms 24 kHz mono PCM is currently rendered and accepted end to end (24,000 Hz, 16-bit, no clipping), while computer-use remains disabled because Accessibility and Screen Recording are absent. I recorded two forward proposals: a cross-surface “catch me up” spoken re-entry digest, and an action-hash approval ledger that prevents stale or replayed pendant approvals after reconnect/state drift.

**Biggest unknown:** Whether the owner will reconnect the browser extension and manually grant Accessibility/Screen Recording to AI Pendant Agent; without those, authenticated browser actions and vision-based GUI automation cannot be validated. I still need the owner's acceptance thresholds for the 24 kHz audio path and approval-expiry policy before treating those as production-ready.

