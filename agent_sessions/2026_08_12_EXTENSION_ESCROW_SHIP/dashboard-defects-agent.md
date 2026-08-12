# dashboard-defects-agent — 2026-08-12

Two defects in `software/dashboard-sveltekit`. Both fixed, checked, built twice, deployed.

## 1 · Approval-card flicker (root cause + fix)

**Mechanism.** The Worker's `/api/jobs` route has two sources and switches
between them silently per request: it asks the Mac's jobTracker through the
relay ops proxy first (`opsProxy` — a real round trip that loses races whenever
the bridge is mid-cycle or two polls overlap), and on any proxy failure falls
back to the relay's own `/v1/ops/history`. The four parked `plan_ready` Outlook
jobs from Aug 11 exist **only** in jobTracker — relay history never sees a
Mac-parked plan — so a mac-agent poll returned them and a fallback poll
returned a list without them. The client (`refreshJobs` in `+page.svelte`, and
`JobsPanel`) replaced `jobs` wholesale with whichever answer landed last, and
`pendingApprovals(jobs)` flipped 4 → 0 → 4 with it. With page-level polls every
15 s, a 5 s freshness probe and the panel's 6 s poll all in flight, the cards
flashed on and off seconds apart. The agent build cannot flicker this way (one
source; failures throw and callers keep state) — this was the deployed Worker.

**Fix (`src/lib/dataSource.ts`).** A module-level latch of the last
mac-agent-origin list. A healthy answer replaces the latch wholesale (so
approve/dismiss/finish really clears the screen); a `relay-history` fallback
answer may only ADD what it knows — the merge carries over every latched row
the fallback is structurally blind to (parked plans above all, plus Mac-local
and agent-initiated work), while dropping latched `source: "pendant"` rows the
fallback already represents under relay ids, so nothing renders twice. An
empty or failed poll can no longer blank out records a healthy poll just
proved exist.

**Stale parks go quiet (`runState.ts`, `+page.svelte`, `ApprovalCard.svelte`,
`globals.css`).** `STALE_APPROVAL_AFTER_MS = 1 h`; `pendingApprovals` stamps
`stale` per card. The page splits fresh (amber banner, aria-live announcement)
from stale (always-compact grey cards, clock icon, "Still parked · since …",
Dismiss in the lead slot wired to the existing `POST /jobs/:id/dismiss` path,
Approve demoted to the quiet outline, no live region). The Jobs tile turns
amber only for fresh parks, though its count still names every open decision.

## 2 · Fleet map missing EXT—RLY edge

The aggregator's static `EDGES` list predates the extension joining the relay
mesh (`browser_node` role, socket to `/v1/node/socket`), so no feed — live or
snapshot — carried Extension—Relay and the ring drew the extension hanging off
the Mac alone. Fixed in `src/routes/hive/+page.svelte`: a `graphEdges` derived
synthesises the intended-topology edge `ext-relay` ("mesh socket") whenever the
feed lacks it, deriving liveness exactly the way the pendant/iOS heartbeats
already do — from the relay's `relay.devices` rows (which the ~8 s snapshot
push retains, capped at 15). An online `browser_node` row lights/pulses the
edge; absent or offline leaves `lastActivityAt` null, the same grey down edge
the pendant gets. If the aggregator ever adds the edge itself, the id check
makes the synthesis a no-op.

## Verification

- `npm run check` — 0 errors, 0 warnings.
- `npm test` — 45/45 (includes the rendered-HTML and hive-feed suites).
- `npm run build:agent` — done; `ext-relay` / `mesh socket` / `browser_node` /
  "Still parked" all grep-confirmed in `build-agent/_app/immutable/nodes/`.
  The live agent at `127.0.0.1:8000/dashboard` already serves the new entry
  hashes (start.R86YECSX.js / app.C1NQar-L.js).
- `npm run deploy:cloudflare` — worker `ai-pendant-dashboard` deployed,
  version `141ff39c-0618-4eb7-bf76-7d93f8d3d2c5`; `ext-relay` present in the
  uploaded client bundle (`.svelte-kit/output/client/_app/immutable/nodes/`).

Optional follow-up (not required for the fix): teach the aggregator
(`ai-pendant-simulator/hive-dashboard/server.mjs`) the same `ext-relay` edge +
`touchEdge` from `browser_node` device rows, for pulse fidelity on its own
activity events.
