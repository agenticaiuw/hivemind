# Harness derivation — faculty-action — round 38

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **action reachability** — Mac bridge and relay are online, but Accessibility and Screen Recording are untrusted/missing, browser extension is offline with 3 pending commands, and a browser action recently waited ~45 seconds before failing. Existing receipts record failed attempts but lack a preflight barrier.
  - evidence: GET /ops/status at 2026-08-07T10:49Z; GET /jobs shows browser_navigate failure from 10:02:49 to 10:03:34 with extension-offline reason.

## Capabilities it proposed

### "“Ask me on the pendant before you send, delete, buy, or submit—and only do it after I physically confirm.”"
- **useful because:** The owner can approve an irreversible action without returning to the Mac, while a spoken yes alone cannot be accidentally replayed or confused with dictation. The action remains bound to the exact preview they saw/heard.
- **path:** faculty-judgement creates a typed transaction preview and risk classification → relay stores a one-time confirmation nonce and sends a short spoken summary to the pendant → pendant displays the risk via its single LED pattern and waits for a deliberate second-button press → relay forwards the signed confirmation to mac-planner → browser-extension or mac-vision executes only if the preview hash, tab/session, lease, and nonce still match → faculty-action returns a before/after receipt to the pendant and Mac workbench
- **model tier:** Use the normal planner/judgement tier to draft and classify; use realtime only for the short spoken preview and confirmation exchange. No model call is needed to validate the nonce or execute the already-approved typed plan.
- **latency:** Preview within 2 seconds; confirmation acknowledgement under 300 ms; execution feedback as soon as the Mac/browser receipt arrives.
- **cost:** Under $0.01 per confirmation, dominated by realtime audio turns; nonce validation and dispatch are local/relay metadata only.
- **security:** Never accept a spoken confirmation for high-risk actions, never reveal secrets in the LED or spoken summary, expire the nonce after 60 seconds or any plan edit, and require re-preview after tab navigation or field changes. A lost link must leave the action unexecuted, not retry blindly.
- **missing:** Pendant firmware button gesture and LED confirmation state machine; Relay endpoint for nonce issuance, expiry, and signed confirmation; Mac/browser executor gate that verifies preview hash and lease immediately before side effects; Receipt UI that makes the exact pending transaction audible and reviewable

### "“If I long-press the pendant, stop anything you’re about to do everywhere.”"
- **useful because:** The owner gets a single physical emergency brake for queued Mac, browser, and relay work—even when the screen is locked, the browser is unavailable, or speech recognition is wrong. It prevents a stale plan from executing after circumstances change.
- **path:** Pendant firmware detects a held-button emergency gesture and gives an unmistakable LED/haptic warning → Relay immediately marks the paired owner's action leases revoked and broadcasts cancellation to the Mac bridge → mac-planner cancels cancellable jobs and prevents new side effects until the lease epoch changes → browser-extension drops pending commands and returns cancellation receipts for each tab/session → faculty-action reports what was stopped and identifies any step that had already become irreversible
- **model tier:** No model is needed for detection, revocation, or cancellation. Use the cheaper planner tier only to summarize the resulting receipts; realtime may speak the short emergency acknowledgement.
- **latency:** Local gesture acknowledgement under 150 ms; relay lease revocation under 500 ms; all reachable surfaces blocked within 1 second.
- **cost:** Negligible API cost; a small authenticated control message and receipt per active job. Hardware cost is covered by the haptic/button production change.
- **security:** Require a distinctive hold duration and local debounce to avoid accidental cancellation, but do not require network or speech. Authenticate the device control channel, persist a monotonic lease epoch to defeat replay, and fail closed when the relay cannot be reached. The owner must be told explicitly if an irreversible step already completed.
- **missing:** Pendant offline emergency-stop firmware state; Relay-wide action-lease epoch and cancellation broadcast; Mac and browser executors that honor revocation between every side effect; A concise cross-surface cancellation receipt


## Changes it proposed to its own stack

### `integration` — Add a reachability-and-proof preflight barrier to every faculty-action job. Before dispatch, query Mac readiness (Accessibility/Screen Recording), browser bridge heartbeat/tab affinity, relay connectivity, and pendant link; classify each planned step as executable, queueable, or blocked. For blocked steps, fail in under 2 seconds with the exact missing surface and a one-tap recovery instruction instead of waiting 45 seconds. On reconnect, resume only idempotent queued steps under a short action lease, then attach before/after evidence and an honest receipt; never emit success from a plan or an unverified GUI attempt.
- **owner gets:** Today a browser request can burn nearly a minute and still report only that the extension is offline, while GUI permissions can make a visual result untrustworthy. The owner gets fast, truthful answers, automatic continuation after a dropped link, and no accidental duplicate actions.
- effort: Medium: typed readiness contract in Mac agent/relay, preflight middleware in job runner, browser heartbeat integration, idempotency/lease persistence, and pendant LED/voice status mapping; add integration tests for offline, reconnect, and permission-denied cases.  ·  risk: A stale readiness result could incorrectly block or resume work. Use short TTLs, recheck immediately before each side effect, persist lease ownership, and default to blocked on uncertainty. Recovery is cancel/retry from the receipt UI; irreversible steps still require explicit confirmation.
- cost: Negligible API cost (small status probes); roughly 1–2 KB metadata per job/receipt in local JSON or D1.  ·  latency: Adds ~100–400 ms when surfaces are healthy, but turns current 45-second browser timeouts into <2-second actionable failures.
- security: Improves safety by preventing untrusted GUI success and duplicate retries; readiness metadata must not include page contents or secrets, and leases must be scoped to the paired owner/device.
- depends on: chg-5fc73ce3 receipt/undo storage; chg-14accc01 browser request IDs and tab affinity; browser heartbeat/poll route; relay-to-Mac authenticated pairing

### `hardware` — Design the production pendant with a small haptic actuator and a secure element alongside the button/LED. The relay issues a one-time transaction challenge; the pendant verifies the challenge, renders a distinct vibration pattern, and signs the owner's deliberate button gesture with a device key. Mac/browser actions accept the signature only when it matches the exact preview hash and expiry, while the relay records the signed authorization and final receipt.
- **owner gets:** They can safely approve a consequential action while walking, driving, or away from a screen: a tactile pattern tells them this is an approval request rather than ordinary conversation, and a physical gesture cannot be forged by replaying audio. The same pendant can prove which exact action they approved.
- effort: High: choose a production wearable MCU/secure-element design, add haptic and power drivers, implement challenge signing and anti-replay firmware, expose verification through relay and Mac/browser executors, and validate usability and battery life.  ·  risk: A lost pendant or compromised pairing could authorize actions. Require physical re-pairing, key revocation, short-lived challenges, local lockout after repeated failures, and server-side confirmation of preview hash, owner/device pair, and expiry. Firmware update and recovery-key procedures are required.
- cost: Approximately $2–$6 incremental BOM for secure element, haptic motor, driver, and mechanical changes; modest battery impact from brief haptic pulses and cryptographic operations; negligible per-action API cost.  ·  latency: Adds roughly 100–300 ms for challenge verification/signature validation, with immediate tactile feedback before network execution.
- security: Moves high-risk authorization from replayable voice to hardware-backed user presence, without sending private page contents to the pendant. Requires secure manufacturing, key provisioning, revocation, and signed firmware updates.
- depends on: A typed transaction preview and risk classifier; Relay challenge/nonce service; Mac/browser executor verification gate; Signed firmware update and device-pairing infrastructure


## What it asked for

_Nothing._
