# mac-settings-agent — Browser Bridge tab in the Mac menu-bar app

Task: move the extension popup's stripped-out settings to the Mac desktop app
(owner, 2026-08-12: "maybe we can still keep settings but move them to the
macbook app instead"). Files claimed: software/mac-menubar/** only. Did NOT
touch browser-extension/, safari-browser-extension/, local-agent/, cloud-relay/.

## What shipped (all in software/mac-menubar/Sources/main.swift)

- Third window tab "Browser Bridge" beside Dashboard / This Mac
  (NSSegmentedControl in the toolbar; tab enum replaced the old Bool with a
  one-time migration from the "ShowThisMacTab" default).
- BrowserBridgeView (SwiftUI, matches ActivityView's ink/chip/card style):
  - PAIRED BROWSERS — GET /browser/status: per device the deviceId
    (extensionId), online/offline dot, device/browser name, extension
    version, current tab title, "seen Xs ago"; userAgent as tooltip.
  - PAIRING — display-only guidance (pairing happens in the extension popup)
    plus three configured/missing rows: pairing code on disk (bool from the
    repo .env, value never shown), agent credentials (/ops/status
    agent.tokenConfigured), relay pairing (/ops/status
    relay.payload.pairingRequired).
  - ACTIONS — Open Dashboard (existing behavior), Restart Agent (existing
    launchctl kickstart -k gui/501/com.aipendant.agent), and a deliberately
    DISABLED "Revoke a paired browser" row: the agent exposes no revoke route
    (local-agent/browserBridge.js only ages heartbeats out internally), and
    this app doesn't invent agent endpoints.
- Polling only while the tab is in front (AgentModel.startBridge/stopBridge):
  /browser/status every 3s, /ops/status every 9s (it round-trips the relay).

## Auth fix that rode along

AgentEnv.loadToken() looked only for AGENT_TOKEN= in the repo .env — which has
been PAIRING_CODE-only since 2026-08-09, so the token was nil on a current
checkout. It now derives AGENT_TOKEN exactly like software/load-pendant-env.mjs:
HMAC-SHA256 keyed by PAIRING_CODE over "aipendant:agent-token", hex digest
(CryptoKit HMAC<SHA256>). Explicit AGENT_TOKEN= still wins. Verified
bit-identical against node on a test vector, and the derived token
authenticated live against the running agent's /browser/status.

## Verification

- bash build.sh: success (one pre-existing deprecation warning, untouched code).
- Installed via ditto to /Applications/AI Pendant.app (its existing home),
  after osascript quit; relaunched with open.
- pgrep after 3s and again after 7s: alive, pid stable; codesign --verify ok.
