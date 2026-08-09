# Harness derivation — faculty-action — round 155

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“When I say ‘protect my focus,’ silence non-urgent Mac notifications and browser interruptions until my next calendar break; let urgent items through and tell me what was held when I’m free.”"
- **useful because:** The pendant becomes a physical mode switch for attention, not another notification source. It coordinates the wearable’s immediate intent, the Mac’s calendar and notification state, and the relay’s durable queue so interruptions are deferred rather than lost.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime model only to resolve the spoken command and confirm the mode; background relay/mac logic handles calendar boundaries and queue summaries.
- **latency:** Mode acknowledgement under 1 s; calendar-boundary release within 5 s; deferred-item summary generated in under 10 s.
- **cost:** About $0.005–$0.02 per spoken activation; most operation is local Mac/relay state and costs no model call.
- **security:** Notification titles and browser page metadata may leave the Mac only as encrypted, minimized summaries. Private items must remain opaque. Entering focus mode should be proactive only after the owner’s explicit utterance or physical gesture; release should never auto-send or delete anything.
- **missing:** A Mac notification-focus adapter with a reversible lease and allowlist for urgent senders/apps; A relay durable deferred-notification inbox keyed to focus lease expiry; Pendant firmware mapping sw1/LED/audio cue to focus-mode state

### "“Take the thing I’m looking at and turn it into a follow-up: identify the person, deadline, and next action, then show me a draft reminder or message on the pendant; never send it until I approve the exact pending item.”"
- **useful because:** This closes the gap between seeing something in a privileged browser session and remembering to act. The browser supplies authenticated context, the Mac planner structures it, the pendant makes the approval moment unavoidable, and perception verifies the resulting draft.
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay-realtime → dashboard
- **model tier:** Use a cheaper background model for extraction and draft generation; realtime is used only for the owner’s short command and approval dialogue.
- **latency:** Capture and structured preview in 8 s; approval state on pendant in 1 s; verification receipt within 5 s after any Mac mutation.
- **cost:** Roughly $0.02–$0.10 per captured page/email depending on context length; browser text extraction dominates, not device work.
- **security:** The browser may contain passwords, health, and financial data. Send only the selected DOM region and URL, redact secrets before relay, and keep message body private on the Mac where possible. Approval digest must be shown as a hash plus human-readable summary; sending requires the existing physical transaction latch.
- **missing:** A browser command for owner-selected region capture with secret-field redaction; A structured follow-up schema (actor, action, deadline, destination, confidence) shared by planner and verifier; A presentation route that lets the pendant request approval without receiving page secrets

### "“Tell me what happened to every action I delegated today—done, undone, blocked, or unknown—and let me replay only the failed ones.”"
- **useful because:** A daily action ledger is the missing trust surface: the owner can delegate across Mac apps and browser sessions without wondering whether silence means success. The relay aggregates receipts, perception distinguishes verified from unknown, and the pendant gives a concise spoken digest with selective retry.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Cheap scheduled summarization model for the daily digest; realtime only answers follow-up questions or initiates a retry. Deterministic status aggregation must not be delegated to a model.
- **latency:** Digest available at the chosen daily time; a status query under 2 s from cached receipts; retry starts within 3 s after explicit approval.
- **cost:** Under $0.01/day for summarization; receipts and status joins are local database work.
- **security:** Digest must omit message contents and secrets by default, exposing only app, action class, timestamp, and verification state. Retrying must use idempotency keys and require confirmation for externally visible or irreversible actions. Unknown must never be narrated as done.
- **missing:** A stable cross-surface action ID propagated through planner, browser bridge, and Mac executor; A deterministic status state machine including verified, failed, blocked, undone, and unknown; A retry endpoint that checks idempotency and re-runs only safe failed steps

### "“If I hold the pendant’s safety button, immediately revoke every active browser session and stop all pending automation, even if the Mac is offline; when it reconnects, show me exactly what was revoked.”"
- **useful because:** A single physical emergency action gives the owner a trustworthy way to stop a compromised or misdirected agent. It is a global revocation boundary, not merely cancellation of one staged action, and it works at the moment the owner is least able to use a screen.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** No model is needed for revocation; use realtime only to narrate the resulting receipt. Deterministic firmware and relay policy must execute the stop.
- **latency:** Pendant records the revocation locally in under 100 ms; relay stops accepting new work within 1 s of reconnect; browser-session invalidation within 5 s.
- **cost:** Negligible API cost; small signed event and session invalidation calls.
- **security:** The gesture must be distinct from normal approval and produce a signed monotonic revocation epoch. It must not expose credentials. Recovery requires deliberate owner re-authentication; never silently re-enable sessions.
- **missing:** A firmware-resident global revoke gesture and durable signed revoke record; Relay-wide revocation epoch checked by every executor and browser command; Browser bridge hook that invalidates or quarantines all controlled sessions

### "“Use my saved password or passkey for this exact login, but never tell me or the AI what the secret is; show me the site, account, and action summary on the pendant and require my physical approval.”"
- **useful because:** Today an agent can either lack the ability to complete authenticated work or risk exposing credentials. This gives the owner useful browser automation while preserving the browser/password manager as the only place that handles the secret.
- **path:** pendant → browser-extension → mac-planner → mac-vision → relay-realtime → dashboard
- **model tier:** Cheap deterministic routing and page-state checks; realtime model only interprets the owner’s request and reads the confirmation summary. No model receives credential material.
- **latency:** Target site/account summary in 2 s; physical approval to credential invocation in under 1 s; post-login verification in 5 s.
- **cost:** Usually under $0.02 per invocation; browser state inspection dominates, not token usage.
- **security:** The bridge must invoke Keychain/passkey APIs locally, never serialize passwords, OTP seeds, cookies, or page secrets. Bind approval to origin, account, and a nonce; refuse if the origin or form changes after approval.
- **missing:** A local browser credential broker using macOS Keychain/passkeys without returning secret bytes; Origin/account/form digest binding between preview and approval; A browser postcondition verifier that can prove login success without capturing private page content

### "“When I am near my Mac, let the pendant be my physical presence key: unlock only the specific staged task I approved, and lock it again as soon as I walk away or the link drops.”"
- **useful because:** The owner gets a wearable, bounded trust signal instead of leaving an automation session broadly authorized. Presence gates sensitive execution but does not grant the agent standing access to the Mac or reveal secrets.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** No model required. Cryptographic challenge-response and link/presence policy are deterministic; realtime may explain a denied action.
- **latency:** Presence proof under 300 ms over USB/BLE; revoke on link loss within 1 s; staged action starts only after fresh proof.
- **cost:** Negligible model cost; modest firmware and bridge engineering.
- **security:** Use rotating nonce challenge-response and monotonic counters, not a reusable Bluetooth token. Bind proof to one action digest and expiry. USB attachment alone must not count as owner presence, and relay compromise must not mint proofs.
- **missing:** A short-range authenticated transport/presence signal between pendant and Mac (current LTE and USB serial are not sufficient for unattended proximity semantics); Mac verifier for signed, action-bound presence proofs; Executor policy that refuses a proof for any other action or after link loss


## Changes it proposed to its own stack

### `integration` — Add a cross-surface action envelope and deterministic state machine shared by relay jobs, Mac executor, browser bridge, and verifier: action_id, attempt_id, idempotency_key, risk, postconditions, and terminal state {verified, failed, blocked, undone, unknown}. Every receipt and spoken status must carry the same identifiers.
- **owner gets:** When the owner asks “did it happen?”, the system can answer with evidence instead of guessing, and can retry one failed step without duplicating a sent message or purchase.
- effort: Medium-high: schema migration, adapters in job/executor/browser receipt paths, and compatibility handling for old jobs.  ·  risk: Old receipts may not have IDs; mark them unknown rather than fabricate correlation. A retry bug could duplicate an external action, so only idempotent or explicitly approved steps may retry.
- cost: Negligible storage and API cost; one extra metadata envelope per step.  ·  latency: Under 100 ms locally; verifier adds seconds only for actions requiring fresh proof.
- security: Improves auditability; do not put page contents or message bodies in the envelope, only hashes and sensitivity labels.
- depends on: Existing actionLedger, prepareApprove, policyRouter, and granted verify_operation_step should be extended rather than replaced.

### `mac-harness` — Implement a reversible notification-focus lease on the Mac: snapshot current Focus/notification settings, apply an allowlist and expiry tied to the next calendar break, journal every suppressed item as opaque metadata, and restore the exact prior state even after agent restart.
- **owner gets:** “Protect my focus” becomes dependable: the Mac stops interrupting work without permanently changing the owner’s settings, and nothing important silently disappears.
- effort: Medium: AppleScript/Focus integration, crash-safe lease persistence, calendar boundary watcher, and summary API.  ·  risk: A malformed restore could leave notifications muted. Use an expiry watchdog and a visible dashboard kill switch; never suppress emergency allowlist items.
- cost: No model cost; small local persistence and periodic calendar polling.  ·  latency: Activation about 1 s; boundary watcher polling under 1% CPU.
- security: Notification content stays local; relay receives counts and app/sender classes unless the owner asks for detail.
- depends on: Owner-configured allowlist and duration policy; existing /routines and /pipeline/events can carry activation and release events.

### `browser-harness` — Add an owner-selection capture command to the browser bridge that returns only the selected DOM/text region, canonical URL, page title, and redacted field map; secret-like inputs, cookies, tokens, and unselected page content are excluded before relay submission.
- **owner gets:** The owner can say “turn this into a follow-up” while looking at a private page without handing the entire authenticated session to the AI.
- effort: Medium: extension content-script selection UI, redaction rules, command/result schema, and expiry-bound selection tokens.  ·  risk: Redaction can miss novel secrets or selection can include sensitive text. Default to local-only preview, show the exact captured snippet on the Mac, and require explicit confirmation before relay upload.
- cost: Low; one small browser command and occasional extraction model call.  ·  latency: Selection capture under 300 ms; extraction remains seconds depending on model.
- security: Substantially reduces data exfiltration and makes scope user-visible; no page passwords or hidden fields cross the bridge.
- depends on: Browser bridge heartbeat/poll/result routes and owner-granted browser extension access; current extension is not enabled, so this remains blocked until that manual step.


## What it asked for

_Nothing._
## Its own summary

Round 155 produced three owner-facing capabilities: a pendant-controlled reversible focus mode, scoped browser-to-follow-up capture with approval, and a daily truthful action ledger with selective retry. I also recorded concrete implementation changes for a Mac focus lease and privacy-scoped browser selection capture. The cross-surface identity proposal was recorded but flagged close to existing backlog, so it should be treated as an amendment rather than a new project.

**Biggest unknown:** The owner still has to choose the focus allowlist/duration policy and manually enable the browser bridge/TCC access if they want private-page capture. Without that, browser execution remains unavailable even though the relay/Mac routes exist. The pendant is also not LTE-registered, so wearable control is testable only while USB-attached to the Mac.

