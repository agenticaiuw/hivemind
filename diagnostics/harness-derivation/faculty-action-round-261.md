# Harness derivation — faculty-action — round 261

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If the result is uncertain, recover it safely.” After any Mac or browser action whose postcondition cannot be verified, tell me exactly what is unknown on the pendant, offer only safe choices (inspect again, undo, retry, or leave untouched), and carry out the selected recovery while preserving the original operation’s audit trail."
- **useful because:** Today execution can stop at an ambiguous receipt and leave the owner to guess whether to retry (risking duplicates) or do nothing (leaving work unfinished). This makes uncertainty an actionable, owner-controlled state rather than a false completion or silent failure.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Realtime only for the short spoken explanation; background Mac/browser agents perform inspection and recovery.
- **latency:** Initial uncertainty notice under 2 seconds; inspection 3–8 seconds; retry/undo bounded to the existing job timeout.
- **cost:** ~$0.01–$0.05 per recovery, dominated by one verification or local-agent turn; no model call for simple status rendering.
- **security:** Never auto-retry side-effecting actions. Undo must be offered only when the receipt declares reversible. Do not send page contents or secrets to the pendant; show a redacted human summary and operation hash. Owner confirmation required for retry and any irreversible choice.
- **missing:** A recovery-state machine keyed by operation_id and step_id, with explicit safe actions and expiry; A verifier result schema that distinguishes not-found, stale evidence, contradictory evidence, and inaccessible surface; A single recovery UI/haptic vocabulary for unknown versus verified outcome

### "“Make this appointment happen everywhere.” Given an approved calendar change, update the calendar, the relevant browser booking page, and a prepared message, then return one cross-surface receipt showing each independently verified state and any surfaces intentionally left unchanged."
- **useful because:** A real-world appointment is not complete when one calendar entry changes: the booking site, reminder, and human communication often drift. This gives the owner one dependable outcome instead of three uncertain partial actions.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Background/standard model plans the workflow; realtime is used only if the owner is speaking live. Deterministic adapters execute each typed step.
- **latency:** 15–45 seconds for three surfaces; announce progress after each step and never block the pendant conversation on a slow browser.
- **cost:** ~$0.03–$0.12 per run, primarily planner and browser-verification turns; calendar/message adapters are low-cost.
- **security:** Booking and sending are separate risk classes. Draft message and booking submission require explicit physical approval; calendar edits may remain staged per owner policy. Secrets stay in the browser session. Each step must have a fresh postcondition verifier and idempotency key.
- **missing:** Typed cross-surface appointment object with timezone, participants, and idempotency key; Adapters that map booking confirmation to calendar and draft-message fields without exposing secrets; A dependency-aware executor that halts downstream steps when an upstream booking is unverified

### "“When I bookmark this moment, make it findable later.” Press the pendant’s bookmark button during a conversation; attach a short locally generated timestamped audio excerpt and motion/context markers, then have the Mac index it against the active app, browser URL, and nearby transcript without storing a continuous recording."
- **useful because:** A bookmark currently marks a moment but does not make the moment recoverable. This turns the one deliberate physical action into a durable, privacy-bounded pointer that can answer “what was I looking at/hearing then?” weeks later.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Small background model indexes and summarizes only the bounded excerpt; realtime is not needed. Local deterministic capture handles timestamps and hashes.
- **latency:** Haptic acknowledgment immediately; index within 10 seconds after link recovery; search results under 2 seconds locally.
- **cost:** ~$0.005–$0.03 per bookmark, dominated by optional transcription/embedding; storage is bounded by excerpt duration and failure-path rules.
- **security:** Never capture continuous audio. sw1 creates a bounded event, with configurable pre/post-roll and a hard byte/time cap. Browser URLs and transcript snippets are private by default, encrypted at rest, and redacted from pendant payloads. Upload only after owner policy permits; delete raw excerpt after verified indexing if configured.
- **missing:** Firmware event envelope for a bookmark with monotonic ID, bounded audio window, and sensor metadata; A Mac-side correlation service joining bookmark time to /observe and browser session state; Search/index retention controls and a user-visible delete path

### "“Forget this everywhere.” Name a conversation, bookmark, draft, or task and have the system locate every derived copy across the relay, Mac, browser session, pipeline artifacts, and context graph; delete or cryptographically tombstone them, then report any inaccessible or retained copy instead of claiming erasure."
- **useful because:** The owner cannot reliably revoke a private thought once it has crossed surfaces. A single spoken deletion request should have the same scope as the original capture, with an honest list of anything that could not be removed.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Background model resolves references and builds the deletion set; deterministic services perform deletion and hash-based verification. Realtime is only for confirmation dialogue.
- **latency:** Acknowledge immediately; enumerate affected artifacts within 5 seconds; complete normal deletion within 30 seconds, with asynchronous receipts for offline surfaces.
- **cost:** ~$0.01–$0.08 per request, mostly reference resolution and verification; storage savings are incidental.
- **security:** Deletion itself is destructive and requires physical confirmation when it affects more than a local draft. Never send deleted content to the pendant. Preserve only minimal audit hashes and legal/system retention notices. Failed deletion must be surfaced as a failure, not tombstoned as success.
- **missing:** A provenance graph linking source captures to transcripts, summaries, embeddings, browser commands, and derived files; Deletion and tombstone APIs on every storage surface, including offline-device queues; A verifier that proves absence or explicitly reports unverifiable retention

### "“Only let this happen for the next ten minutes.” Grant a narrowly scoped, expiring permission from the pendant—such as allowing one named website to submit one form or allowing one app to read one folder—then revoke it automatically and show me a receipt of every use."
- **useful because:** Today permissions are broad, static, and easy to forget. A physical, time-limited grant lets the owner authorize useful automation without handing the system an open-ended ability to act later.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Realtime handles the short grant dialogue; deterministic policy enforcement runs locally on the Mac/browser and relay. No expensive model is needed on each use.
- **latency:** Grant acknowledgment under 1 second; enforcement adds under 50 ms; revocation must occur at expiry even if the conversational model is offline.
- **cost:** Under $0.01 per grant after implementation; cryptographic checks and ledger writes dominate, not inference.
- **security:** The grant must bind to principal, app/site, operation type, resource pattern, maximum count, expiry, and operation digest. Secrets never enter the pendant. Deny by default if clocks, relay state, or policy freshness are uncertain. Physical approval is mandatory for issuing and widening a grant.
- **missing:** A signed capability-token format understood by relay, Mac agent, and browser extension; Enforcement hooks before every side effect and read of protected resources; Monotonic expiry/revocation handling across offline links and clock disagreement

### "“Tell me when my commitments contradict each other.” Continuously compare calendar events, reminders, drafted messages, and browser bookings; when two sources imply incompatible times, locations, or promises, give me a concise pendant alert with the conflicting evidence and let me choose which source is authoritative."
- **useful because:** The owner currently has to notice conflicts manually across apps. This catches hidden double-bookings and contradictory promises before they become real-world failures, without taking action automatically.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Background model extracts structured commitments; deterministic interval/entity comparison detects conflicts. Realtime is used only to explain an alert when the owner asks.
- **latency:** Evaluate within 1 minute of a changed source; alert rendering under 2 seconds; no blocking of normal Mac/browser work.
- **cost:** ~$0.01–$0.05 per changed item, dominated by extraction; comparison itself is negligible.
- **security:** Default to on-device/local Mac processing where possible. Browser evidence remains private and is reduced to redacted fields. Never alter a source automatically. Alerts must cite source, timestamp, and confidence, and allow dismissal without exposing content on the pendant.
- **missing:** A normalized commitment schema spanning Calendar, reminders, messages, and browser confirmations; Read-only adapters and change cursors for each source; Conflict ranking, source-authority preferences, and privacy-preserving alert summaries


## Changes it proposed to its own stack

### `integration` — Add an operation quarantine coordinator between executor, perception, and the outcome beacon. Every side-effecting step enters pending, verified, unknown, or cancelled; unknown steps are frozen with a lease and cannot be retried by background workers. The coordinator exposes a redacted recovery menu and requires the physical approval latch for retrying an action that might already have happened.
- **owner gets:** The owner will never accidentally create duplicate bookings, messages, or purchases because a timeout is mistaken for failure. They get a truthful, recoverable state instead of “done” or an unexplained stall.
- effort: Medium: shared operation schema, coordinator persistence, adapters for jobs and browser commands, and pendant event rendering.  ·  risk: A quarantine bug could strand work. Recover with lease expiry, visible pending status, and a manual inspect/undo path; never auto-discard an unknown operation.
- cost: Low recurring cost; one small state write per step and occasional verifier call. No new hardware.  ·  latency: Adds <100 ms for state transitions; recovery inspection adds seconds only when needed.
- security: Improves safety by preventing duplicate retries. Store hashes and redacted summaries, not secrets or page contents; bind approvals to operation and step digests.
- depends on: verify_operation_step; GET /jobs/:jobId/receipts; POST /jobs/:jobId/undo; tactile_action_outcome_beacon; physical_transaction_approval_latch


## What it asked for

_Nothing._
