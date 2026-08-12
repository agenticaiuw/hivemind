# browser-runs-dashboard-agent — browser-local runs reach the dashboard

Owner's question (2026-08-12 1:37 PM, verbatim): "why didn't my question in
the browser extension carried to the dashboard?"

## Root cause (live-verified, not guessed)

The ingest the task asked me to design ALREADY EXISTED and WORKED:
console-engine.js records claim+verdict mesh mail (`browser.task.record`,
addressed '@relay', authenticated with the browser node's own pdt_ token), and
cloud-relay/browserTaskHistory.js folds it into relay_jobs as a never-claimable
`btask_` row. Production proof: the owner's exact run was already stored —
`btask_930d46ec-e4e6-4351-b475-3d128ce29da4`, "what's my latest personal
gmail", status `read_only`, reply "Your latest email is from Wells Fargo…".

The invisibility was READ-side: the dashboard's Recent/hero feed polls
`/v1/ops/voice-runs` (via the Worker's `/api/runs`), whose membership was
`type: 'plan'` only. The row sat in `/v1/ops/history` while the feed the owner
watches never looked at it. Secondary gap: the Worker's `/api/runs` publicRun
dropped `jobStatus` and `reply`, so even a listed browser run would have
rendered "No answer recorded".

## Decision

No new relay route. Reuse the existing mesh-envelope ingest (it is deployed,
tested — auth boundary + size caps live in browserTaskHistory.js /
nodeMailbox) and fix feed membership instead:

- cloud-relay/history.js: new pure `operatorRunForRow(job)` — the ONE
  membership rule (plan → voiceRunForJob, browser_task → browserTaskRunDetail).
  Owner's question recorded verbatim in its WHY comment.
- cloud-relay/server.js: `/v1/ops/voice-runs` and `/v1/ops/voice-runs/latest`
  now list `type: ['plan', BROWSER_TASK_JOB_TYPE]` through that rule, so the
  cheap freshness probe also trips on a browser answer.
- dashboard-sveltekit `/api/runs` publicRun: pass through `jobStatus` (honest
  verdict vocabulary — read_only/incomplete/needs_approval, read by runState
  before `status`) and `reply` (the extension's ledger headline; replyText's
  first candidate).
- browser-extension/src/console-engine.js: recordRunToHive is now
  fire-and-forget at all 8 settle/claim call sites (`void`, body fully
  swallows failures) — reporting can never block or fail the visible run;
  relay fold is idempotent either order.

## Tests

- cloud-relay/browserTaskHistory.test.js +3 tests (20 total in file): feed
  membership for a folded browser row (honest status, reply, executedBy,
  claimable:false), plan-row parity via deepEqual with voiceRunForJob, and a
  feed/history can-never-disagree sweep. Full simulator suite: 2731/2731 pass.
- Extension suite 230/230; dashboard svelte-check 0/0, tests 45/45 (build
  included).

## Ship + deploy verification

- Relay: `npx wrangler deploy` → version 487876c3-d529-4b80-a368-c1df33547f81.
  Live: `/v1/ops/voice-runs` now returns the owner's btask row FIRST with the
  Wells Fargo reply; `/latest` reports it (probe will trigger dashboard
  refresh).
- Dashboard: build:agent + deploy:cloudflare → version
  669b6d5d-6c03-4559-bb01-83b8bb2bfc40.
- Extension: manifest 1.7.8 → 1.7.9, scripts/ship-safari-extension.sh
  succeeded — installed manifest 1.7.9, codesign valid, pluginkit UUID
  unchanged (pairing preserved). Safari relaunch left to the orchestrator per
  instructions.
