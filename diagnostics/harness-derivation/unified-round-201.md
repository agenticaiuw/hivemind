# Harness derivation — unified — round 201

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Before you do anything sensitive, tell me exactly what data would leave my Mac, which browser tab or app it comes from, and wait until I approve the minimized version.""
- **useful because:** This gives the owner a data-boundary they can understand and control before a browser/Mac action, rather than trusting a generic approval prompt. It is a new policy layer over existing action approval: it compares the requested action's actual inputs and destinations, strips unrelated page/app content, and makes the pendant the physical consent surface.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Deterministic classifier for destinations, fields, and redaction; background model only to explain the resulting manifest in plain language; realtime model is not needed unless the owner asks follow-up questions.
- **latency:** Under 500 ms for manifest generation from already-bound tab/app state; under 2 s for a spoken explanation. Any uncertain classification pauses rather than guessing.
- **cost:** Usually <$0.01 per invocation; deterministic extraction dominates, with occasional small background-model explanation.
- **security:** The manifest must contain hashes, field categories, and destination identities rather than raw secrets. Browser/app bindings are least-privilege and expire. Confirmation is required whenever data crosses off-machine or includes credentials, health, financial, or private conversation data. The pendant receives only a redacted summary and nonce.
- **missing:** A data-flow manifest emitted by browser_run_actions/mac_run_actions before execution; A redaction/classification policy with owner-editable sensitivity categories; A relay record binding the minimized payload hash to the physical_transaction_approval_latch nonce; A dashboard view showing the exact outbound fields and destination

### ""I stopped halfway through something yesterday—put me back at the exact point, with the right browser tab, Mac app, files, and the last thing I said, but don't repeat any action.""
- **useful because:** This is the highest-value everyday capability: the owner can resume real work after sleep, travel, crashes, or a dropped link without reconstructing context. It deliberately restores state and evidence, not actions: it opens only the recorded app/tab/file targets, reports what changed since the checkpoint, and asks before any mutation.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic checkpoint join and world-diff first; background model summarizes the handoff. Realtime is used only for the owner's live spoken request.
- **latency:** Return a spoken checkpoint summary within 2 s; open/read-only rehydration within 5 s. Never auto-submit, type, send, or replay an unrepeatable step.
- **cost:** <$0.02 per resume; most work is local state reads and hashes, with a small summary-model call.
- **security:** Checkpoint records store opaque app/tab bindings, file hashes, action receipts, and owner-approved labels—not page secrets or raw audio. Every target is revalidated against current world state; if it moved, say so and stop. Resume decisions use replaySafety (idempotent/additive only), never reversibility alone.
- **missing:** A durable checkpoint record that joins the pendant's sw1 marker to a relay job/session and Mac/browser bindings; A read-only rehydration executor that can open targets without replaying mutations; A world-diff and stale-target refusal response exposed to the pendant; An owner-visible list/delete control for checkpoint metadata

### ""Run a quiet overnight check and tell me in the morning whether the pendant, relay, Mac, browser, and audio path are all trustworthy—or exactly which one is not.""
- **useful because:** The owner gets a single actionable confidence result instead of discovering at conversation time that a browser bridge is stale, a relay job is leased forever, or audio is silently dropping. It tests without transmitting private content, records evidence, and recommends one bounded repair or asks for confirmation.
- **path:** relay-realtime → pendant → mac-planner → browser-extension → dashboard
- **model tier:** Scheduled deterministic probes and the existing audio validator/fault test; background model converts evidence into a short morning report. No realtime model for the overnight run.
- **latency:** Scheduled checks finish within 90 s and do not delay conversation. Morning answer is under 1 s from cached evidence.
- **cost:** <$0.05/night; probes and validators dominate, with one small summary call.
- **security:** Synthetic audio only, never room capture. Browser checks are restricted to explicitly bound sessions and read-only pages. Reports redact URLs, tokens, page contents, and file paths. Repairs are dry-run first; waking a bridge, clearing a lease, or changing settings requires explicit confirmation.
- **missing:** A scheduled multi-surface probe routine with correlation IDs; A pendant-side signed heartbeat containing privacy latch, link, and audio readiness only; A policy that maps validator results to TRUSTED/DEGRADED/BLOCKED without hiding unknowns; A morning report delivery path that works when the pendant is offline and the Mac reconnects

### ""Let me set a hard weekly budget for what you may do—money, messages, domains, files, and speaking time—and stop before you cross it, even if I asked you earlier.""
- **useful because:** Today approvals are per action, so a sequence of individually acceptable actions can still exceed the owner's real boundary. A cross-surface capability budget gives the owner cumulative control: browser purchases, Mac writes/messages, relay model spend, and pendant speaking/audio time all consume a visible allowance and fail closed when exhausted.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic counters, policy matching, and enforcement; background model may summarize usage. No realtime model is needed for accounting.
- **latency:** Budget check under 50 ms before dispatch; dashboard and spoken summaries under 1 s from cached counters.
- **cost:** <$0.01 per action; durable counter updates and policy matching dominate, not model calls.
- **security:** Counters must be append-only and idempotent by receipt/event ID so retries cannot spend twice. Policies are local-first and fail closed if the relay cannot validate them. Never expose message bodies, page contents, or file data in the usage ledger. Changes to limits require deliberate physical confirmation and an expiry/version.
- **missing:** A durable cross-surface quota ledger keyed to action receipts and audio-delivery receipts; A policy language covering spend, destination/domain, path scope, message count, model tier, and speaking minutes; Pre-dispatch enforcement hooks in browser and Mac executors plus relay job admission; A pendant/dashboard control for viewing, pausing, and physically approving policy changes


## Changes it proposed to its own stack

### `integration` — Add a correlation-id based trust probe orchestrator that runs the existing health, browser, job, pipeline, audio validation, and fleet-repair diagnostics as one read-only snapshot; persist only compact verdicts and evidence hashes, then expose the result to /briefing and the pendant. It must distinguish UNKNOWN from FAILED, expire old evidence, and offer a dry-run repair plan rather than mutating automatically.
- **owner gets:** They get one honest morning answer about whether the system is usable, with the failing surface named, instead of a reassuring but incomplete 'online' status or discovering a silent audio/browser failure during an important conversation.
- effort: Medium: a scheduled relay/Mac coordinator, adapters for existing validators, evidence-hash storage, and one dashboard/briefing renderer; no new hardware required.  ·  risk: A stale or partial probe could falsely say healthy. Require per-surface timestamps, quorum rules, UNKNOWN on missing evidence, and never treat relay acceptance as audio playback. Recovery is rerun of the specific failed probe; repairs remain confirmation-gated.
- cost: Negligible storage (a few KB per run) and <$0.05 per scheduled summary; no routine audio or SD writes.  ·  latency: Overnight run under 90 seconds; cached morning answer under 1 second. No impact on live audio.
- security: Read-only synthetic tests; no room audio, page contents, tokens, or secrets. Evidence is hashed/redacted and bound to the correlation ID.
- depends on: A scheduler caller for the existing read-only diagnostics; A compact pendant heartbeat event (privacy latch/link/audio-ready only); A policy mapping evidence to TRUSTED/DEGRADED/BLOCKED/UNKNOWN; A briefing delivery path for offline pendant periods

### `integration` — Create a fail-closed quota admission layer between planning and every executor. It evaluates a versioned owner policy against the planned action and current durable usage, reserves quota atomically before dispatch, settles the reservation from the existing job/browser/audio receipts, and releases it on a confirmed no-op. The same reservation ID must follow relay jobs, Mac actions, browser commands, and pendant audio so retries cannot double-spend.
- **owner gets:** A limit the owner sets will actually protect them across the whole hive: a browser retry cannot send a message twice, a chain of Mac actions cannot quietly exceed a file/domain allowance, and an unexpectedly verbose conversation cannot consume unlimited time or cost.
- effort: Medium-high: shared policy schema, durable reservation store, executor admission hooks, receipt settlement adapters, and dashboard/pendant controls.  ·  risk: Incorrect reservation settlement could block legitimate work or undercount usage. Use idempotency keys, expiration with explicit reconciliation, visible remaining/reserved amounts, and UNKNOWN rather than silently granting when the ledger is unavailable. Recovery is a read-only reconciliation pass before new admission.
- cost: Small persistent store and one atomic update per dispatched action; no meaningful model cost. Audio minutes are already measured by delivery receipts.  ·  latency: Adds under 50 ms to dispatch admission; no live audio-path change.
- security: Policy and counters may reveal behavioral metadata, so keep them local/redacted and encrypt relay copies. Policy edits and quota increases require physical_transaction_approval_latch; a privacy latch immediately blocks new reservations.
- depends on: The capability's versioned owner policy and durable quota ledger; A stable idempotency/reservation identifier shared by relay, Mac, browser, and pendant receipts; Pre-dispatch hooks in /plan-to-execute, browser dispatch, relay claim, and audio delivery; Owner-facing controls for policy versioning, pause, and reconciliation


## What it asked for

_Nothing._
## Its own summary

Recorded three capabilities and one integration change. The strongest is a no-replay work resumption capability: restore the exact Mac/browser context and last spoken objective after interruption, but never repeat unrepeatable actions. I also recorded a preflight data-exfiltration manifest requiring physical consent for sensitive outbound data, and a scheduled cross-surface trust report. The integration change wires existing health, browser, job, pipeline, audio, and repair evidence into one timestamped TRUSTED/DEGRADED/BLOCKED/UNKNOWN result rather than inventing another probe.

**Biggest unknown:** I still need a definitive live inventory of the workbench handoff routes and the browser/Mac pre-execution data-flow hooks. The proposal names them as dependencies because the route list observed so far is truncated and no existing action currently emits a redacted outbound-data manifest. I also need the owner's preferred overnight check time and whether a morning trust report may speak automatically or should wait for the next button press.

