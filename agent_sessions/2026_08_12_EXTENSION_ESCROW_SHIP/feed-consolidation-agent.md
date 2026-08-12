# feed-consolidation-agent — one device-tagged feed

Owner ruling (2026-08-12): "jobs, memory, and history are literally the same
thing … repeated 4 times. delete the entire panel with 6 different tabs below
and make sure to keep the ability to filter work or questions by nodes …
the device(s) should be the main tags … 'recent' shows cloud work only,
which should be changed."

Scope: software/dashboard-sveltekit only (relay/extension/agent owned by others).

## Plan
1. hiveFeed.js: `deviceTagsFor` (device-deduped, multi-node, DEV work folded to
   one "Agent-initiated" tag, Cloud dropped when a real device tag exists);
   widen `mergeMacLocalHistory` → `mergeHiveFeed` (fold every job except
   bridge-executed `source: "pendant"` copies; dedupe by id).
2. jobs.ts: JobView keeps `origin` and `source` separate so relay rows stay
   honestly tagged; kill duplicated This Mac/Browser tabs at the root.
3. JobsPanel: per-source tab row → device chips (single-select, right-aligned).
4. +page.svelte: delete History + Memory tiles/panels and all their plumbing;
   Jobs tile renamed Work; Recent renders the widened feed with device tags.
5. /api/runs: pass `origin` through the sanitizer (it was dropped — the reason
   every Recent row read "Cloud").
6. Tests: hive-feed device-tag + widened-merge coverage; rendered-html tile list.

## Log
- 2026-08-12: read all four views' code; confirmed relay voice-runs rows carry
  `origin` (cloud-relay/history.js) while dashboard /api/runs sanitizer drops it.
- Implemented: hiveFeed deviceTagsFor/isAgentInitiated/mergeHiveFeed (+ telemetry
  storage read so the Mac's own /pipeline pendant runs tag Pendant, not Cloud);
  JobView origin/source split; JobsPanel device chips; JobDetail + AnswerCard on
  the one classifier; +page History/Memory tiles+panels deleted, Jobs→Work,
  Recent widened; /api/runs origin passthrough; dead CSS blocks removed.
- Found while testing: hero badge said "Cloud" for the run Recent tagged
  "Pendant" (AnswerCard read origin/source strings only) — fixed by passing the
  whole run through deviceTagsFor.
- Checks: svelte-check 0 errors / 0 warnings; node tests 51/51 (24 hive-feed,
  device-tag coverage added); build:agent written and verified LIVE at
  127.0.0.1:8000/dashboard in the Browser pane (desktop + 375px mobile):
  tiles Work/System/Mac/Browser only; chips All·120 / This Mac·78 / Browser·22 /
  Pendant·13 / Agent-initiated·7 (old duplicate tabs' counts merged exactly:
  76+2, 14+8); Pendant chip click filters Finished 120→13; Recent rows tagged
  Pendant / Agent-initiated / This Mac / Browser.
- deploy:cloudflare done — version b0c41418, and the deployed worker serves the
  new chunk (grep "Agent-initiated" over the live immutable asset: hit).
- Status: DONE. Committed scoped to dashboard-sveltekit + session records only
  (memory-domains-agent has unrelated in-flight files; left untouched).
