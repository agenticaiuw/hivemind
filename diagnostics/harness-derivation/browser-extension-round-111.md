# Harness derivation — browser-extension — round 111

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser bridge live state round 111** — Safari is not currently registered/online; GET /browser/status reports only home-chrome offline and pendingCommands=10. Three stale browser sessions remain in /browser/sessions, but POST /execute browser_navigate timed out after 20 seconds, so those sessions are not usable.
  - evidence: GET /browser/status HTTP 200; GET /browser/sessions HTTP 200; POST /execute browser_navigate https://example.com returned No response within 20s.

## Capabilities it proposed

### "“Remember this private page for me, and bring it back when it becomes relevant.” From the pendant or Safari, I can specify a page/selection and a time or condition; later the system resurfaces the exact evidence with a link and suggested next step."
- **useful because:** Today a logged-in page disappears into a tab. This turns a fleeting browser discovery into a reliable, reviewable handoff: Safari supplies private context, the relay keeps the trigger alive, the Mac relates it to local work, and the pendant resurfaces it at the right moment without silently acting.
- **path:** browser-extension → relay-realtime → mac-planner → unified → dashboard-ux
- **model tier:** Use a cheap background model to normalize the selected excerpt, classify a trigger, and periodically match it against events/jobs. Use realtime only for the pendant capture and the eventual spoken alert; use the Mac planner only when local Calendar/files are needed.
- **latency:** Capture should acknowledge in under 2 seconds and show the quoted excerpt immediately. Matching can run hourly or on local events. Resurfacing should produce a 5–10 second pendant alert, with a dashboard review in under 3 seconds.
- **cost:** About $0.002–$0.02 per capture/match cycle depending on excerpt length and matching cadence; dominant cost is repeated semantic matching. Exact URL, hash, and short excerpt can avoid sending whole pages or repeated context.
- **security:** Private page text must be opt-in and encrypted at rest with a per-item retention/expiry. Default to storing URL, title, selection hash, and a short quoted excerpt; never capture passwords or form fields. A resurfaced item should open the existing Safari session, and any follow-up submission remains a separate explicit action. Show source URL, timestamp, and excerpt before any Mac mutation.
- **missing:** A working Safari heartbeat/command queue (currently /browser/status is offline with 10 pending commands and POST /execute browser_navigate times out); A browser selection/excerpt capture action returning stable DOM locator and source hash; A durable trigger/matching store that can join browser items to Calendar/Mail/local Mac events; Per-item encrypted retention, expiry, and deletion controls; A pendant inbox/notification primitive with deep-link handoff to Safari

### "“Lock my private browser whenever I’m away from my pendant, and bring it back when I return.” Safari should automatically obscure or suspend designated sensitive tabs when pendant proximity is lost, restore them on return, and let a physical pendant action lock everything immediately."
- **useful because:** A logged-in browser is currently an unattended window into the owner’s accounts. This gives the owner practical, automatic privacy when they walk away from the Mac—without relying on remembering a keyboard shortcut or closing every tab—and uses the pendant as the one device that is always with them.
- **path:** pendant → browser-extension → mac-planner → relay-realtime
- **model tier:** No model is needed for proximity, locking, or restoration. Use the relay only for durable device-state coordination and an optional spoken warning; use a cheap background model only to classify which tabs are sensitive when the owner explicitly asks for automatic classification.
- **latency:** Lock within 1–2 seconds of a confirmed proximity loss; restore within 2 seconds of return after a short debounce. Must work locally during a relay outage, with queued state reconciliation when connectivity returns.
- **cost:** Negligible per-event API cost; the main cost is extension/pendant firmware and platform integration. Optional tab classification would be under $0.01 per batch and should not be on the hot path.
- **security:** The lock decision must fail closed locally, without transmitting page contents. Store only device presence, tab identifiers, and an owner-selected sensitivity label. Do not destroy or navigate tabs; use Safari’s native tab/private-window hiding or an extension overlay and preserve unsaved form state. Require explicit opt-in per tab/domain, a local emergency-unlock path, and audit lock/restore events. If the pendant is lost, the owner needs a separate Mac fallback passcode.
- **missing:** A pendant BLE/proximity identity signal exposed to the Mac bridge and browser extension, with debouncing and lost-device behavior; A Safari extension command that obscures/suspends a tab or window without navigating or discarding its state, plus a reliable restore command; A local fail-closed watchdog on the Mac that continues locking while relay/network access is down; Per-domain/tab sensitivity labels and an emergency unlock/fallback passcode flow; A durable reconciliation record so relay and dashboard can show the last lock state without storing page content


## Changes it proposed to its own stack

### `browser-harness` — Add a durable PrivatePageItem pipeline between browser results and jobs: browser_read_page/browser_snapshot may optionally return an owner-selected excerpt plus URL, tabId, DOM locator, timestamp, and content hash; POST /private-page-items stores only the opted-in excerpt with expiry and encryption metadata. A background matcher consumes /pipeline/events and Calendar/Mail/job events, emits a cited resurfacing job when its explicit time/condition matches, and marks each item delivered/snoozed/deleted. Keep the current /execute action receipts and tab/session affinity attached to every item.
- **owner gets:** The owner can stop losing useful discoveries in private tabs and receive the exact passage at the moment it matters, rather than a vague reminder or a full-page reread.
- effort: Medium: extension selection capture, one durable store/schema, event matcher, and pendant/Mac deep-link notification; include migration-free fallback to URL-only items.  ·  risk: A selector can become stale, a page can change, or sensitive text can be captured accidentally. Mitigate with hash/quoted evidence, selector failure notices, redaction of password/form controls, expiry defaults, and an item-level delete endpoint. If matching fails, retain the item in a review queue rather than silently dropping it.
- cost: Low storage and background-model cost; roughly $0.002–$0.01 per item per day depending on event volume. Encryption/key handling and extension changes dominate engineering cost.  ·  latency: Capture acknowledgement under 2 seconds; matching is asynchronous (event-driven plus hourly sweep). Opening the cited page takes normal Safari navigation latency.
- security: Adds persisted private-page data, so default URL/title/hash only, explicit excerpt opt-in, short retention, encryption at rest, and visible source/expiry. Never auto-submit or transmit captured form/password fields.
- depends on: Restore Safari heartbeat and clear the 10 stale pending browser commands; current /browser/status is offline and browser_navigate via /execute times out.; Expose an extension action for user-selected text or a bounded semantic region.; Add encrypted item storage and a pendant notification/deep-link route.


## What it asked for

_Nothing._
## Its own summary

Discovered a live regression: Safari is offline, only stale home-chrome is registered, 10 browser commands are pending, and browser navigation through /execute times out. Reported it to mac-planner. Proposed and decomposed a new cross-surface PrivatePageItem handoff: opt-in excerpt capture from authenticated Safari, durable encrypted retention/expiry, event matching against Mac/relay activity, and cited pendant resurfacing.

**Biggest unknown:** Whether the Safari extension process is stopped, disconnected, or blocked behind the 10-command queue; restoring heartbeat/queue health is required before validating any private-page workflow.

