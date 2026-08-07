# Harness derivation — mac-terminal — round 66

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If something can’t run on my Mac, tell me exactly why, fix what can be fixed, and give me the best fallback instead of just failing.”"
- **useful because:** The Mac currently reports ready:false (Accessibility and Screen Recording missing) and the browser bridge is offline with five pending commands. Today an action can spend ~45 seconds failing with only “extension offline.” A cross-node readiness-and-recovery turn would let the pendant ask in plain speech, the relay retain the request while the Mac is unavailable, the Mac run cheap health checks, open the exact System Settings pane or restart/re-poll the bridge when appropriate, then either retry idempotently or hand the work to shell/relay/public-web fallback. The owner gets a useful answer and a completion receipt rather than a dead end.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic checks and retry policy first; gpt-4.1-mini only to explain a multi-fault diagnosis or choose among safe fallbacks; reserve realtime for the spoken interaction.
- **latency:** Health check under 1 second; bridge re-poll/retry up to 10 seconds; permission repair is user-paced. Speak the diagnosis immediately, then deliver a later pendant receipt when queued work completes.
- **cost:** Usually $0 model cost for /ops/status and typed checks; roughly $0.001–$0.01 only when a compact multi-fault explanation needs gpt-4.1-mini. Dominant cost is not tokens but waiting for the bridge or a queued Mac job.
- **security:** Diagnostics may reveal app names, host state, and permission status; keep them local and send only a terse fault code to relay. Opening System Settings is reversible, but changing permissions remains the owner's action. Retry only actions marked idempotent and preserve the existing job receipts; never duplicate a submit/send step after an ambiguous timeout.
- **missing:** A readiness contract that returns machine-readable blockers, capability-specific fallbacks, and an idempotency/retry classification; A bridge watchdog that converts offline/heartbeat state into a bounded re-poll or reconnect attempt; A durable cross-node retry envelope linking pendant request, relay job, Mac job, browser command, and final receipt; A dashboard panel showing blocker, attempted repair, fallback, and whether work is queued or abandoned

### "“Put what I just said into the thing I’m looking at.”"
- **useful because:** Today the pendant can hear an instruction and the Mac can type, while the browser can access authenticated tabs, but there is no trustworthy handoff of the immediately preceding spoken content to the currently focused Mac or browser field. This capability would make the pendant a hands-free keyboard: capture the utterance, resolve the active destination on the Mac, preview the exact text and target, then insert it into the focused app or authenticated tab and return a spoken receipt. It is especially useful for long addresses, notes, ticket updates, and form fields while the owner’s hands are occupied.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Use deterministic active-window/tab and field metadata where possible; use gpt-4.1-mini only to normalize dictated text or resolve ambiguity. Realtime handles only the short capture and spoken confirmation; no planner-tier call for straightforward dictation.
- **latency:** Capture acknowledgment under 300 ms; destination lookup under 1 second; show/announce a preview before insertion; insertion and receipt under 2 seconds when the Mac/browser bridge is online. If disconnected, relay retains the utterance and resumes on heartbeat.
- **cost:** Near-zero for transport, focus lookup, and typed insertion; about $0.0005–$0.003 for optional compact normalization. The dominant cost is speech transport/TTS, not reasoning.
- **security:** The utterance may contain passwords, health data, or private work content. Encrypt the relay envelope, retain it only until delivery or explicit save, and never log raw text in general activity logs. Require an unmistakable preview/confirmation for sensitive-looking values or destinations such as payment, password, or message-send fields; insertion itself must never submit or send. Include app, tab URL, field label, and text hash in the local receipt, not the full secret.
- **missing:** A focus-intent protocol that reports the active Mac app/window and, for browser tabs, the focused field label/DOM locator without exposing full page contents; A short-lived encrypted voice-to-text envelope linking one pendant utterance to one Mac/browser insertion, with replay protection and delivery acknowledgment; A typed insert_text_at_focus action implemented by the Mac agent and browser extension, distinct from submit/send; A privacy-preserving preview channel that lets the pendant speak the target and text summary before insertion; A lease/timeout policy so a queued utterance cannot be inserted after the owner has changed focus


## Changes it proposed to its own stack

### `integration` — Replace the single ambiguous agent.permissions.ready boolean in /ops/status with a capability matrix and stable blocker codes. Report independent readiness for shell, AppleScript/automation, accessibility UI control, screen capture, browser bridge, relay link, and audio; include observedAt, remediation URL/action, and whether each blocker affects the requested action. Preserve ready for compatibility as “all required capabilities,” but make requiredMissing/optionalMissing derive from the matrix. Have /execute attach the preflight snapshot to every failed receipt so a stale global status cannot explain a route-specific failure.
- **owner gets:** The live Mac says ready:false while requiredMissing is empty, and a browser job says only “extension offline” after 45 seconds. The owner needs to know immediately whether a task can proceed through shell, AppleScript, UI vision, or browser—and what single thing to fix—instead of treating the whole Mac as unavailable or retrying blindly.
- effort: Small-to-moderate: define blocker vocabulary, compute matrix from existing permission and heartbeat probes, add compatibility fields, attach snapshot IDs to receipts, and add dashboard badges. No executor policy or approval change.  ·  risk: Permission probes may be stale or disagree with reality; include timestamps and an unknown state rather than claiming ready. Do not expose raw tokens or private URLs. Existing clients that interpret ready as a hard gate must be updated to use per-action capability, while old clients retain the compatibility field.
- cost: No model cost; a few hundred bytes per status/receipt and negligible local computation.  ·  latency: Adds only local probe time, preferably cached for 5–30 seconds; failed jobs return immediately with the cached blocker instead of waiting for an impossible browser poll.
- security: Makes permission and connectivity posture more visible to relay/dashboard; send only capability codes and timestamps off-device, never detailed app or account metadata.
- depends on: GET /ops/status; GET /ops/snapshot; GET /browser/status; Existing action receipts at GET /jobs/:jobId/receipts; Existing Mac permission and relay heartbeat probes

### `interaction` — Add a cross-surface focus lease for hands-free dictation. When the pendant starts a “put this there” utterance, the Mac agent and browser extension publish a signed snapshot containing active app/window, browser tab identity, focused-field locator, and a short expiry. The relay binds exactly one encrypted utterance envelope to that lease. Before insertion, the Mac agent verifies the same app/tab/field is still focused; if not, it pauses and asks the pendant rather than typing into a new destination. Record only a text hash and destination metadata in the receipt, with a local one-shot undo for insertion where the host supports it.
- **owner gets:** It prevents the uniquely dangerous failure of hands-free input landing in the wrong window after the owner switches focus. The owner can dictate once, glance or listen to a concise target preview, and trust that a later bridge reconnect will not paste stale private words into an unrelated document or message.
- effort: Moderate: focus metadata adapters for macOS accessibility and the browser extension, signed lease/envelope storage in relay D1, expiry and replay checks, typed insertion plus local undo, and pendant preview/receipt phrasing.  ·  risk: Some apps expose no reliable field identity; classify those targets as unknown and require an explicit second confirmation rather than guessing. Accessibility metadata can include sensitive window titles and URLs, so keep full snapshots local and send only opaque lease IDs through relay. Recover interrupted delivery by expiring the envelope, never by silently replaying it.
- cost: Negligible model cost; small D1/local metadata records and one short-lived encrypted text payload per use. No hardware cost.  ·  latency: Adds roughly 100–300 ms for lease validation; avoids delayed incorrect insertion and expensive recovery.
- security: Improves confidentiality by making text single-use, destination-bound, expiring, and hash-audited. It introduces a sensitive transient payload, which should be encrypted at rest and deleted after acknowledgment or expiry.
- depends on: The proposed focus-intent protocol and typed insert_text_at_focus action; Existing browser heartbeat/poll/result routes; Existing Mac action receipts and relay persistent state


## What it asked for

_Nothing._
## Its own summary

Discovered live Mac state and recorded a new integration change: replace ambiguous /ops/status ready:true/false with a capability matrix and stable blocker codes, attach the preflight snapshot to failed receipts, and return route-specific readiness immediately. Live state is fullControlMode=true, relay reachable, browser extension offline with 5 pending commands, and permissions.ready=false despite requiredMissing=[] (Accessibility and Screen Recording are absent). A second recovery capability was proposed but recognized as overlapping existing fallback work; I did not restate it. I also informed mac-planner of the status inconsistency and missing diagnostic implementations.

**Biggest unknown:** The newly granted diagnostic interfaces still have no implementation, so I cannot verify host-level permission/process/network details beyond /ops/status. I still need an implemented bounded Mac diagnostics call and the local-agent job/journal lifecycle contract to validate the proposed preflight and receipt changes end to end.

