# System tile row removal — work log (2026-08-12)

Owner order: "i told you to delete these 4 tabs in the system do that please"
(the Work/System/Mac/Browser tile row that survived fec7500's consolidation).

## Removed (software/dashboard-sveltekit)

- `src/routes/+page.svelte`: the "System" section label, the `tile-strip`
  with all four `<Tile>`s, and the system/mac/browser detail panels. State
  plumbing deleted with them: `openTile`, `toggleTile`, `systemTone`,
  `storeLabel`, `automationEntries`, `grantedAutomation`, `Tile` import.
- `src/lib/components/Tile.svelte`: deleted — +page.svelte was its only
  importer (Hive's `hv-tile-*` classes are unrelated).
- `src/globals.css`: `.tile-strip`, `.tile*` visuals, `.perm-chips`,
  `.perm-chip`, `.section-label-standalone`, and the mobile `.tile-strip`
  breakpoint. Kept `.tile-panel`/`.panel-empty` (JobsPanel shell) and
  `.system-list` (shared by JobDetail/JobAction/RoutineDetail).

## Where the load-bearing bits live now (nothing new created)

- Work tile's toggle/anchor: `JobsPanel` renders unconditionally as page
  section 5; `showJobsPanel()` just scrolls to its existing
  `tile-panel-jobs` id. Needs-you count: approval banner + the feed's
  "Needs you N" group head.
- System/Mac/Browser health: topbar dot cluster (Cloud/Bridge/Mic/Browser),
  alert strip ("Permissions · N missing"), Hive ring page per-node.

## Verification & deploy

- `npm run check`: 0 errors, 0 warnings.
- `npm test`: 51/51 pass (rendered-html test flipped to assert the tiles are
  GONE and `tile-panel-jobs` is always present).
- `npm run build:agent`: wrote build-agent.
- `npm run deploy:cloudflare`: deployed ai-pendant-dashboard, version
  b66c9479-ac1d-4dd9-b906-04ae251d64b3
  (https://ai-pendant-dashboard.evan20050827.workers.dev).

Not committed to git — parent session owns the commit alongside sibling
agents' work.
