# Harness derivation — mac-planner — round 131

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac/browser execution truth at round 131** — Live /ops/status reports mac bridge online but ready=false because Accessibility and Screen Recording are missing; /observe explicitly says UI actions report success while doing nothing. Browser extension home-chrome is offline with 10 pending commands. Browser sessions remain durable (3 tabs), so stale commands could target private sessions after reconnect.
  - evidence: GET /ops/status 200 at 2026-08-07T14:24:06Z; GET /observe 200 at 14:24:06Z; GET /browser/status 200 showing online=false,pendingCommands=10.

## Capabilities it proposed

### "“Make sure that actually happened everywhere I asked, and tell me if anything is out of sync.” After an action spanning my Mac and a logged-in browser, reconcile the intended end state against independent observations, identify partial completion or conflicting state, and prepare the smallest repair plan without silently retrying."
- **useful because:** Today a receipt can say an action completed even when Mac input never reached the screen, while browser commands can remain queued against a private session. The owner needs an end-state guarantee, not merely an execution log: one answer showing which surfaces agree, which do not, and what repair would change.
- **path:** pendant → relay → mac-vision → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Use the realtime model only for the owner's live request and concise spoken status; use a cheaper background model for reconciliation, evidence comparison, and repair-plan generation. Use deterministic checks before any model interpretation.
- **latency:** Acknowledge the request within 1 second; perform quick local checks within 5 seconds. Allow background reconciliation to continue after the conversation and notify the pendant when evidence converges or a repair decision is needed.
- **cost:** Usually one low-cost background text-model invocation plus deterministic Mac/browser reads; roughly $0.01–$0.05 per reconciliation depending on page evidence size. Realtime cost is limited to the initial request and final short status.
- **security:** Authenticated page contents and local application state must stay scoped to the requested job and be minimized in relay events. Never replay a stale browser mutation merely because the intended state is absent; distinguish unknown from false and require explicit owner confirmation for a repair that could duplicate an external side effect. Store hashes and provenance rather than full sensitive content where possible.
- **missing:** A cross-surface end-state assertion schema that describes the intended result independently of the action list; Independent postcondition readers for Mac files/apps and browser DOM/session state; Receipt-to-observation reconciliation with confidence, freshness, and conflict states; A repair planner that understands non-idempotent external effects and produces a reviewable diff; Relay and pendant notification support for partial, conflicting, and finally-verified outcomes


## Changes it proposed to its own stack

### `integration` — Add a reachability-aware execution envelope spanning relay, Mac agent, and browser bridge. Before dispatch, stamp each action with surface, session/tab affinity, idempotency key, and a short lease. The Mac agent must consult live /ops/status and /observe: accessibility-dependent UI actions become explicitly blocked/unverified when uiActionsWillReachTheScreen=false (never successful receipts), while AppleScript/read-only actions remain eligible. Browser commands queued while offline are quarantined as stale after the lease, not replayed blindly; on heartbeat they are resumed only if their idempotency key and tab/session still match. Emit one durable state transition (planned → dispatched → verified/blocked/expired) to the relay so the pendant can say exactly what happened and what needs reconnecting.
- **owner gets:** The owner stops hearing 'done' when nothing happened, avoids ten old browser commands firing at once after reconnect, and gets a concise pendant notification naming the one blocked prerequisite. Safe read-only work can still proceed through AppleScript even when GUI input or Safari is unavailable.
- effort: Medium-high: shared action envelope/schema, status preflight, browser queue lease/quarantine, relay state projection, and migration of receipts; add fault-injection tests for disconnect/reconnect and stale tabs.  ·  risk: A conservative status check could mark an action blocked during a transient probe failure, and lease expiry could leave work pending. Recover by retaining the plan and idempotency key, exposing explicit retry/resume, and never deleting the user's requested work. Existing maximum-access policy remains unchanged; this adds truthfulness/observability, not an approval gate.
- cost: Negligible API cost; a few D1/local JSON state writes per action and one reconnect notification. Engineering/storage cost is the dominant cost.  ·  latency: ~100–300 ms for status/lease checks; no extra model call. Reconnect may delay work until a heartbeat and verification arrives.
- security: Improves safety against stale authenticated-tab replay and false success. Preserve URL/tab metadata minimization and do not transmit page content in status events; idempotency keys must not contain secrets.
- depends on: A shared action-envelope contract between /execute, browser command queue, and relay job records; A browser heartbeat/reconnect handler that reports tab/session identity; A verified distinction between read-only AppleScript and accessibility-dependent UI actions; Relay durable job-state projection and pendant notification path

### `integration` — Create a cross-surface postcondition-and-witness layer, not another action queue. Every planned multi-surface job must carry declarative assertions such as file hash changed, app state contains a named value, or a browser session's specific DOM region equals an expected normalized value. After execution, independent adapters collect fresh witnesses from the Mac agent and authenticated browser, attach timestamps/tab IDs/file identities, and classify each assertion as verified, contradicted, or unknown. The relay stores the compact assertion result and the pendant speaks only the delta; action receipts remain evidence of attempted steps, never proof of the final state.
- **owner gets:** The owner can ask for an outcome and know whether it is true across the places that matter, even when a UI action was swallowed or a browser disconnected. Partial completion becomes visible without blindly repeating a payment, submission, message, or file mutation.
- effort: High: define a small assertion language, implement Mac and browser witness adapters, bind observations to job/session identity, add freshness and conflict handling, and test non-idempotent failures. This is deliberately separate from the existing executor and receipt/undo mechanisms.  ·  risk: A witness can be stale, ambiguous, or unavailable; incorrectly declaring success is worse than declaring unknown. Require source timestamps and identity binding, use an explicit unknown state, expire assertions, and make repair a separate reviewed plan. No automatic retry of irreversible effects.
- cost: Small deterministic compute and local/relay storage cost per assertion; background model cost only when normalizing conflicting textual/page evidence. Data volume can be kept low with hashes, normalized fields, and cited snippets.  ·  latency: Adds roughly 1–5 seconds for independent postcondition reads after an action; complex browser pages may continue in background. Initial acknowledgment remains immediate.
- security: Witnesses must be scoped to the initiating job and redact page content, email bodies, and secrets. Do not copy full authenticated DOMs to the relay; retain local evidence references and short hashes where possible.
- depends on: A shared postcondition schema between /plan and /execute; Independent read-only Mac and browser inspection adapters; Relay persistence for assertion results and expiry; Pendant phrasing for verified/contradicted/unknown outcomes; Existing job receipts, journal records, and browser session identity


## What it asked for

_Nothing._
## Its own summary

Recorded two new, non-backlog ideas: (1) an owner-facing cross-surface outcome reconciliation capability, and (2) the missing postcondition-and-witness integration layer that independently verifies Mac and authenticated-browser end states instead of treating action receipts as proof. These address the current false-success and stale-session failure modes without proposing another approval gate or action queue.

**Biggest unknown:** Which concrete owner workflows deserve first-class postconditions (for example, a file export plus browser upload, or a calendar change plus local note) and which external effects must always remain 'unknown until manually checked' rather than being machine-verified.

