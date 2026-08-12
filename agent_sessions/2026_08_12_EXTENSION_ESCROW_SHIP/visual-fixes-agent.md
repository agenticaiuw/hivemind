# Visual fixes agent — 2026-08-12 (night)

Subagent log. Two owner-reported visual defects, both fixed and verified.

## 1. Dashboard logo green glow — removed

- Cause: `.brand-mark` in `software/dashboard-sveltekit/src/globals.css` carried
  `box-shadow: 0 12px 35px rgba(80, 218, 142, 0.22);` — a green halo around the
  header/login pendant mark. Removed that one declaration; logo, size, and
  gradient background untouched.
- `npm run build:agent` → `build-agent/_app/immutable/assets/0.6iu2xcvK.css`
  has no box-shadow on `.brand-mark`, zero traces of the green rgba/hex.
- `npm run deploy:cloudflare` → built `.svelte-kit/cloudflare/` (same clean
  `.brand-mark` rule) and deployed worker `ai-pendant-dashboard`, version
  `31087d4f-051d-4588-9fa9-f2d4cc90fa6b`.
- Live check: localhost:8000/dashboard serves the new hashed CSS without the rule.

## 2. Wrapper app green "P" icon — real root found

- The task premise was slightly off: the app target's
  `Shared (App)/Assets.xcassets/AppIcon.appiconset` was NOT stale — all 11 PNGs
  byte-match fresh `sips` derivations of `assets/icon/pendant-1024.png`
  (verified with `cmp`), and `scripts/sync-icons.mjs` already fans it out.
- The actual stale asset: `Shared (App)/Resources/Icon.png` — a loose 512px
  green "P" (mtime Aug 2) shown at 128px by the app window's
  `Base.lproj/Main.html` (`<img src="../Icon.png">`). The 2026-08-10
  unification missed it because it lives outside every asset catalog.
- Fix: extended `scripts/sync-icons.mjs` with
  `resize(512, 'Shared (App)/Resources/Icon.png')` (+ comment), ran the script.
  41 files regenerated; only Icon.png changed content — proof nothing else had
  drifted and nothing of the shipping agent's was disturbed.
- Did NOT run xcodebuild, did not touch ~/Applications, src/*.js, package.mjs,
  popup files, or manifest.json — the 1.7.5 ship will bake the new Icon.png in.

## Commit

Left to the orchestrator: the tree carries the ship agent's in-flight edits
(popup.js, page-engine.js, popup-lifecycle.test.js); committing now would sweep
them up mid-flight.
