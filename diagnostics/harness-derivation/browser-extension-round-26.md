# Harness derivation — browser-extension — round 26

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser bridge availability** — No usable browser device is online. GET /browser/status reports online=false, only home-chrome with no tab, and 2 pending commands; browser session records are stale and do not prove extension reachability.
  - evidence: Live GET /browser/status at 2026-08-07 round 26 returned online=false and home-chrome tabId/windowId null; browser_command_enqueue(get_active_tab) returned implementation error.

## Capabilities it proposed

### "“When I’m on a private website, hand the useful facts to my pendant and Mac without making me explain or copy anything—and let me ask follow-up questions about exactly where each fact came from.”"
- **useful because:** The browser is the only node with the owner’s authenticated sessions, while the pendant is the only node continuously available and the Mac can organize artifacts. A provenance-carrying handoff makes private-page context immediately useful in voice and desktop work without leaking full pages or requiring copy/paste.
- **path:** browser → mac-bridge → relay → pendant → dashboard
- **model tier:** Use a cheap background extractor for page normalization and redaction; use realtime only for the owner’s spoken follow-up. The Mac stores the handoff capsule and citations; relay streams only the selected snippets to the pendant.
- **latency:** Capture and index in under 2 seconds after a browser read; spoken follow-up under 800 ms when the capsule is already local. Recompute extraction only on demand.
- **cost:** About $0.001–$0.01 per page handoff depending on OCR/LLM extraction; most cost is optional semantic extraction, not transport or hashing.
- **security:** Private content must not be sent wholesale to the relay or model. Create an on-Mac capsule containing minimal selected fields, URL/title, timestamp, DOM locator, source-snippet hash, sensitivity labels, and expiry; relay receives only fields explicitly requested for speech. Never persist cookies or page HTML. Require confirmation before any browser mutation or external transmission, while local owner-approved read/click remains allowed.
- **missing:** A browser-to-Mac handoff endpoint that accepts typed, redacted provenance capsules; A shared capsule schema with field-level sensitivity, TTL, and source locator/hash; Pendant query routing that can resolve follow-ups against an on-Mac capsule; Dashboard view showing active capsules and allowing immediate revocation; Functional browser command enqueue and a live Safari heartbeat (currently unavailable)

### "“If I lose Wi‑Fi or leave my Mac, keep the private page I’m viewing available for a voice question later, and sync the answer when the connection returns.”"
- **useful because:** Today authenticated browser context disappears when the bridge, Mac, or network is unavailable. The browser is uniquely positioned to capture a minimal, owner-selected page excerpt while the login is live; the pendant can then remain useful offline and reconcile the question later instead of losing the thread.
- **path:** browser → mac-bridge → pendant → relay → dashboard
- **model tier:** Use on-device/browser-local extraction and hashing first; use a cheap background model on the Mac for indexing and answer preparation after reconnection. Use realtime only if the owner asks a live follow-up while connected.
- **latency:** Capture in under 1 second; offline pendant acknowledgement under 150 ms; queue reconciliation within 30 seconds after connectivity returns.
- **cost:** Usually under $0.002 per captured page for local extraction and a small background indexing call; storage and sync dominate rather than inference.
- **security:** Capture must be explicit (a browser toolbar action or pendant command), never whole-page by default. Store only selected text/regions, URL, timestamp, sensitivity, and a content hash in an encrypted local capsule; enforce TTL and a visible revoke/delete control. Do not transmit private content to the relay until connectivity returns and the owner’s routing policy permits it. Never capture passwords, payment fields, or cookies.
- **missing:** A browser extension capture action that sends a selected region plus provenance to the Mac agent; An encrypted, bounded offline capsule queue shared by the Mac and pendant; Pendant-side offline query/acknowledgement storage and reconnect reconciliation; A sync protocol with deduplication, TTL expiry, and conflict handling; Dashboard controls for selecting, reviewing, and deleting pending private capsules; A working Safari heartbeat and command enqueue implementation to perform the initial capture


## Changes it proposed to its own stack

### `browser-harness` — Add semantic browser-session resurrection. Persist a per-session recovery recipe (origin, title pattern, stable landmarks, login-state hints, and last known tab/window metadata) plus a short-lived encrypted tab handoff token. After Safari restarts or tab IDs change, the bridge should reacquire the matching tab by origin/landmarks, verify the page identity, and emit a new tab binding before executing queued reads. If multiple candidates match, return a typed ambiguity result rather than guessing.
- **owner gets:** Private work does not silently break when Safari restarts, a tab is restored with a new ID, or a window is rearranged. The owner can ask about an ongoing authenticated page hours later and receive the right page instead of a stale-tab error or an answer from the wrong account.
- effort: Medium: recovery metadata store, bridge reacquisition algorithm, identity verification, and tests across Safari restart/tab duplication.  ·  risk: A wrong candidate could expose another logged-in page; mitigate by requiring origin plus multiple stable landmarks and fail closed on ambiguity. Recovery metadata may become stale; expire it and fall back to a fresh navigate. No page HTML or cookies are persisted.
- cost: Negligible API cost; a few KB of encrypted metadata per session and one extra local bridge lookup on recovery.  ·  latency: Usually adds <300 ms to a recovered action; no cost on a healthy bound tab.
- security: Improves safety by preventing accidental cross-tab execution, but stores sensitive origin/title hints locally; encrypt at rest, apply TTL, and never include credentials.
- depends on: A functioning browser command enqueue path and Safari heartbeat; The existing browser session store and typed result receipts; A page identity verifier that can inspect title/origin/landmarks before running the requested action


## What it asked for

_Nothing._
## Its own summary

Discovered that the browser bridge is still unusable despite stale session records: live status is offline, Safari is not registered/heartbeating, home-chrome has no tab, two commands are pending, and every enqueue wrapper still returns an implementation error. I proposed a new cross-node capability: provenance-carrying, sensitivity-limited browser facts handed from authenticated Safari to the Mac, relay, and pendant for voice follow-ups. I also proposed semantic browser-session resurrection so Safari restarts/tab-ID changes do not break authenticated work or risk acting in the wrong tab. I notified mac-planner and recorded the live defect.

**Biggest unknown:** Whether the real Safari extension is running and merely failing to heartbeat, or whether the bridge/extension deployment has been removed; I cannot distinguish those without a functioning enqueue/heartbeat path or a Mac-side operator checking Safari.

