# Harness derivation — relay-realtime — round 19

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Keep an eye on this website and let me know when anything important changes.”"
- **useful because:** The owner gets passive awareness without babysitting pages, and the pendant can deliver a quick summary when they’re away from the Mac.
- **path:** relay → browser → mac-bridge → dashboard
- **model tier:** Cheap background model for periodic diffing and summarization; realtime model only for the follow-up conversation when the owner asks what changed.
- **latency:** Diffing can take seconds to minutes; it’s not interactive. Alert playback should be near-instant once the alert exists.
- **cost:** Dominated by browser fetch + diff + summary tokens. Realtime cost only when the owner responds or asks for more detail.
- **security:** Authenticated sites should be opt-in per origin. Redact sensitive fields in summaries. Any irreversible action (like triggering a purchase) must require explicit confirmation.
- **missing:** A scheduler/queue to run periodic checks; A storage-backed alert queue and retention policy; A routing rule to prefer server-side browser for public pages and Mac session only for authenticated origins


## Changes it proposed to its own stack

### `integration` — Add a relay-owned job scheduler using Cloudflare Cron Triggers plus Durable Object alarms to run periodic tasks (web diffs, inbox checks, maintenance), with a small job table in D1 and a per-job state machine. Jobs create alert artifacts (text + optional audio) stored in R2 and indexed for the pendant.
- **owner gets:** They can set routines once and get results later without keeping the Mac awake or being online. It turns the system into something that works while they live their life.
- effort: Medium to high: new DO, D1 schema, retry semantics, idempotency, and an alert format shared across surfaces.  ·  risk: Bad scheduling could spam, duplicate, or miss jobs. Mitigate with idempotency keys, backoff, and a dashboard view of upcoming/failed jobs. Provide a kill switch per job.
- cost: Low per run; cost scales with job count and browser usage. Storage costs for alerts in R2.  ·  latency: Background work; realtime unaffected except for quick status checks.
- security: Jobs can touch authenticated sessions; require per-origin enrollment and confirmation gates for irreversible actions.
- depends on: Define a job schema and alert artifact format; Implement origin allowlist and auth mode selection

### `model-routing` — Adopt a strict routing policy: realtime relay only for intent capture, clarification, and immediate reversible actions; mac_delegate for multi-step tasks; server_browser_actions for public web research; background model for scheduled diffing and summarization. Add a confirmation checkpoint for any irreversible action.
- **owner gets:** Lower latency and lower cost: they get fast conversational control without paying for the expensive tier to do slow work, and risky actions get a clear yes/no moment.
- effort: Low to medium: define policy, implement in planner/relay, add guardrails.  ·  risk: Over-routing could send tasks to a tier that lacks context. Mitigate with receipts and fallback to mac_delegate when the job fails or needs auth.
- cost: Reduces expensive realtime usage; shifts work to cheaper tiers.  ·  latency: Improves perceived responsiveness; background tasks may complete later by design.
- security: Confirmation checkpoints reduce harm from misinterpretation; origin allowlists limit data exposure.
- depends on: Handshake schema for job receipts and status reporting; Policy enforcement in mac-planner and browser harness


## What it asked for

_Nothing._
## Its own summary

I confirmed what’s in the stack: the relay runs on a Cloudflare Worker with D1/R2 backing, the voice agent still only has five production tools, and new grants include relay intent routing, server-side browser actions, and job status checks. I proposed a concrete capability (change monitoring with pendant alerts), plus two enabling changes: a scheduler/queue and a routing policy that prefers cheaper tiers and requires confirmation for irreversible actions.

**Biggest unknown:** There is still no defined job/alert schema, no scheduler implementation, and no clear auth enrollment mechanism for monitoring authenticated sites. Those need to be designed and built, and I need a way to store and deliver alert artifacts to the pendant safely.

