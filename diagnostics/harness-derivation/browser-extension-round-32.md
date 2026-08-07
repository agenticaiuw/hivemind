# Harness derivation — browser-extension — round 32

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser availability** — Live /browser/status currently reports online=false; only home-chrome is registered with no tab and 2 pending commands. The previously real Safari registration is not currently visible, so authenticated work cannot run until its heartbeat returns.
  - evidence: GET /browser/status HTTP 200 body at round 32: devices=[home-chrome tabId:null tabCount:null online:false], pendingCommands=2.

## Capabilities it proposed

### "If a logged-in browser task gets interrupted, keep my place and ask me to recover it: after I re-authenticate or solve the prompt in Safari, resume safely from the last completed step and tell me exactly what changed."
- **useful because:** Authenticated workflows fail in real life when sessions expire, tabs disappear, or a site asks for 2FA/CAPTCHA. Today a timeout leaves the owner unsure whether anything happened and retries can duplicate a form or purchase. This makes the pendant, relay, Mac, and private browser cooperate to recover without losing state or repeating side effects.
- **path:** browser → mac-bridge → relay → pendant → dashboard
- **model tier:** Use a cheap background model for checkpoint classification, diffing, and retry planning; use realtime only for the pendant's brief interruption/re-auth conversation. Escalate to the stronger planner only when the page structure or recovery outcome is ambiguous.
- **latency:** Detect interruption within one poll (roughly 5–15 seconds); pendant notification under 10 seconds. Resume within 30 seconds after Safari heartbeat and owner re-authentication. No waiting on the owner during ordinary reversible steps.
- **cost:** About $0.01–$0.05 per interrupted task, dominated by one or two page extraction/classification calls; normal successful tasks add only storage and polling cost.
- **security:** Private page excerpts and checkpoint metadata leave Safari only to the local Mac agent and relay job record; redact tokens and form secrets. Never capture or transmit OTP/password values. Pause at authentication, CAPTCHA, payment, send, or submit boundaries and show the exact pending action; recovery may resume only already-authorized reversible steps. Keep an append-only before/after receipt to prevent duplicate side effects.
- **missing:** Durable browser job/checkpoint runner with per-step idempotency keys and tab/session affinity (the current queue can time out and has pending commands but no owner-facing recovery state).; Safari extension heartbeat and a reattach/foreground-tab command that can identify the resumed tab after the real extension reconnects.; A relay-to-pendant notification/ack path for 'reauthenticate now' plus quiet hours and expiry.; A recovery state machine that distinguishes no-result timeout, completed-but-unreported, authentication wall, and genuine site error.

### "When I am looking at a private Safari page, let me ask from the pendant, “What does this mean?” or “What am I supposed to do next?” and answer from the exact text and controls currently visible—without making me read the screen aloud or send the page anywhere."
- **useful because:** The browser is the only node with the owner's private logged-in context, while the pendant is the only node available when the owner's hands and eyes are occupied. Today those contexts are disconnected: the owner must switch to the Mac, copy a URL or quote text, and explain where they are. This gives a grounded spoken explanation of the current page, including what is visible and what is actionable, without turning it into an autonomous transaction.
- **path:** pendant → relay → browser → mac-bridge → dashboard
- **model tier:** Use a low-cost background/fast model to normalize the DOM and accessibility tree; use realtime only for the short spoken question and answer. Use the expensive planner only if the page has conflicting regions or the owner asks a multi-step interpretation.
- **latency:** Capture the active tab and visible-region semantics in under 2 seconds, answer in 3–6 seconds, and stream the first spoken sentence as soon as the relevant evidence is available.
- **cost:** Roughly $0.005–$0.03 per question, dominated by sending a compact accessibility/text projection to the model; screenshots should be optional rather than default.
- **security:** Only the active tab's visible, user-requested region is read; page text is retained ephemerally and never added to general memory. Exclude password fields, hidden DOM, cookies, local storage, and cross-origin frames. State the source URL/title in the answer and never click, type, or submit from this conversational mode.
- **missing:** A browser command that returns the active tab's viewport plus accessibility tree/DOM region in one typed, bounded payload (not just a generic page dump).; A relay correlation path that binds a pendant utterance to the owner's current Safari tab and rejects stale tab snapshots.; A compact redaction and ephemeral evidence buffer for private-page answers.; A spoken-answer protocol that can cite a visible label or control without reading sensitive neighboring fields.


## Changes it proposed to its own stack

### `browser-harness` — Add an interruption-safe browser transaction journal and recovery protocol. Before every browser step, persist a step id, tab/session binding, normalized target fingerprint, expected effect, and idempotency key; after it, persist typed result plus before/after evidence. On timeout, extension disconnect, login wall, CAPTCHA, or tab replacement, classify the checkpoint as unknown/completed/blocked, stop issuing mutations, and expose a re-authenticate-and-resume token. When the same Safari session reconnects, verify the target fingerprint and resume only from the first unconfirmed step; reconcile late results so a timed-out click cannot be replayed blindly.
- **owner gets:** A lost Wi-Fi link or expired login should not turn a carefully prepared task into either abandoned work or duplicate submissions. The owner gets one clear pendant prompt and can continue where they left off, with proof of what did and did not happen.
- effort: Medium-high: browserBridge/session schema, extension reconnect/foreground-tab support, durable journal, recovery API, and integration tests for late results and tab replacement.  ·  risk: A faulty fingerprint could resume on the wrong page or falsely treat an action as complete. Default to pausing on mismatch; retain the journal and provide explicit restart-from-step and undo where supported. Recover by reconciling the page before any further mutation.
- cost: Negligible per-step storage (small JSON plus hashes); roughly one cheap classification call only on interruption. No extra model call on ordinary read/navigation steps.  ·  latency: A few milliseconds of local journaling per step; reconnect reconciliation adds one page read, typically 1–5 seconds before resuming.
- security: Improves auditability but stores sensitive URL/DOM evidence. Encrypt or redact journal fields, TTL page excerpts, never store password/OTP values, and scope records to the browser session/job.
- depends on: Durable browser job runner (chg-16bc5dee); Reliable browser command queue with request IDs and typed results (chg-14accc01); Safari extension heartbeat/reattachment support; Owner-facing relay/pendant interruption notification

### `hardware` — Add a tiny coin vibration motor and a low-power notification controller to the pendant, with a single reserved haptic pattern for 'private browser task needs you' (reauthentication/CAPTCHA/ambiguous checkpoint). Keep audio/LED behavior unchanged; the relay can push a short event while the main voice path is idle, and the existing button can start the spoken recovery conversation.
- **owner gets:** The owner may be away from the Mac or wearing headphones. A browser task blocked behind a login should reach them without exposing page contents on a speaker or requiring them to keep a dashboard open; one discreet vibration tells them to tap and resolve it.
- effort: Medium hardware revision and firmware driver; add relay push/event acknowledgement and battery testing. This is prototype hardware, so reserve a GPIO and power rail in the next board spin.  ·  risk: Extra power draw and nuisance alerts could cause fatigue. Rate-limit to one escalation per job, respect quiet hours, use distinct patterns for urgent versus expired tasks, and fall back to LED/audio when the motor is unavailable.
- cost: Approximately $0.50–$2 in components and under 10 mA during vibration bursts; near-zero API cost. Battery impact is negligible if events are sparse.  ·  latency: Sub-second local alert after relay push; no effect on voice latency.
- security: Haptic payload contains only an opaque job class and urgency, never URL, title, or page text. Require encrypted authenticated device events.
- depends on: Durable browser interruption/recovery journal; Relay-to-pendant push channel and acknowledgement; Firmware GPIO/power budget and quiet-hours state

### `browser-harness` — Add a privacy-scoped active-viewport evidence API for conversational questions. The extension should return, for one active tab and one request nonce, the viewport bounds, visible accessibility tree, rendered text labels, focused control, and source coordinates; redact password/OTP inputs and omit hidden or offscreen DOM. Bind the snapshot to tabId, URL, frame, timestamp, and a short TTL, then invalidate it on navigation or focus change. Expose only this projection to the relay so a pendant question can be answered from what the owner is actually viewing.
- **owner gets:** The owner can ask for help with a confusing private page hands-free and receive a precise explanation of the current controls, rather than a vague answer based on an entire stale page or having to disclose the page manually.
- effort: Medium: Safari extension accessibility/viewport capture, redaction and focus tracking, typed relay schema, and a small conversational routing path.  ·  risk: Accessibility trees can contain unexpected private text, and a stale snapshot could describe the wrong page. Enforce nonce/TTL/tab affinity, redact sensitive controls before leaving Safari, and return 'page changed—please retry' rather than guessing.
- cost: Small local CPU/storage cost; compact text projections reduce model tokens and should lower per-question API cost. No screenshot upload unless explicitly requested.  ·  latency: One extension round trip, generally under 2 seconds; focus-change invalidation avoids expensive retries.
- security: This creates a new private-page data path, so encrypt in transit, keep evidence in memory only, avoid logs and general memory, and record only a hash plus metadata for observability.
- depends on: Working Safari extension heartbeat and command enqueue path; Typed active-tab/viewport result schema; Relay routing that correlates the pendant utterance with the current browser device


## What it asked for

_Nothing._
## Its own summary

Discovered the live browser bridge is currently offline: /browser/status shows only the never-used home-chrome device, no tab, and two pending commands; the real Safari heartbeat is absent. I recorded this and proposed a new cross-node capability: interruption-safe authenticated browser recovery, with durable per-step evidence/idempotency, relay + pendant re-auth prompts, Safari reattachment, and safe resume after login/tab/network failures. I also proposed the browser journal implementation and a discreet haptic pendant alert for blocked private tasks, and told mac-terminal about the gap.

**Biggest unknown:** Whether the real Safari extension will reconnect and whether its command enqueue path is actually implemented end-to-end; without that heartbeat, authenticated page extraction and recovery testing cannot be validated. The durable browser runner, reconnect/reattach protocol, relay push-to-pendant acknowledgement, and haptic hardware/firmware do not yet exist.

