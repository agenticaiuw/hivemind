# Escrow + mechanical ship agent — working log (2026-08-12)

Owner's instruction on record: "we likely gonna keep updating the extension,
make sure this issue doesn't happen again" (pairing wiped by extension updates
on 2026-08-10 and 2026-08-12).

## Job 1 — scripts/ship-safari-extension.sh
- New strict script (set -euo pipefail), 8 echoed steps: version guard →
  package.mjs → rsync --delete into Shared (Extension)/Resources → xcodebuild
  Release (derivedDataPath build) → rsync --delete of Contents/ INTO the
  installed bundle (never rm/ditto-merge; bundle root never deleted — that is
  the credential-wiping move) → lsregister -u the derivedData copy only →
  verify (one pluginkit row, enabled, ~/Applications; codesign; manifest
  version grep) → "quit and reopen Safari".
- Guard trip proven at 1.7.0==1.7.0 (exit 1), and again post-ship at 1.7.1.

## Job 2 — credential escrow
- SafariWebExtensionHandler.swift: escrow:store/fetch/clear, JSON Data blob in
  the appex's standard UserDefaults (sandbox container survives Safari
  storage resets). No App Group exists in the project (no .entitlements, no
  application-groups in pbxproj; ENABLE_APP_SANDBOX=YES) — suiteName would
  fail silently, so standard defaults by design.
- pairing.js: pure shouldEscrow(lifetime) (session → never) and
  escrowRestorePlan(values, now) (reuses credentialExpiryCheck).
- background.js: escrowSend with one-shot Chromium latch
  (sendNativeMessage('application.id', …) in try/catch); store after
  successful pair:run (non-session only); restore in startPeers after
  enforceCredentialLifetime when no agentToken; escrow:clear whenever
  storage.onChanged sees agentToken removed (covers expiry wipe and any
  future unpair UI).

## Tests / ship
- browser-extension: 194/194 pass (node --test), incl. 2 new escrow tests in
  test/pairing.test.js; popup-lifecycle.test.js source-shape assertions intact.
- Shipped 1.7.0 → 1.7.1 via the new script. pluginkit UUID unchanged
  (715C469E-…) — storage identity preserved. Installed appex resources at
  1.7.1 with escrow-wired background.js; appex binary contains the new
  handler. Full-package `npm test` result recorded by orchestrator.
