# Harness derivation — mac-planner — round 46

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-and-browser-readiness** — Mac local agent is live (v0.5.0) with FULL_CONTROL_MODE and relay reachable, but readiness is false because Accessibility and Screen Recording permissions are missing. Browser extension home-chrome is offline with 3 pending commands. The granted mac_readonly_inspect tool is present in the tool layer but its implementation currently returns an error.
  - evidence: GET /ops/snapshot returned accessibility.trusted=false, screenRecording.granted=false, browser.online=false/pendingCommands=3; direct mac_readonly_inspect calls returned 'tool was granted a schema but has no implementation yet'.

## Capabilities it proposed

### "When I say “I’m presenting” (or press the pendant button), hide distracting Mac/browser interruptions for this meeting, keep only genuinely urgent alerts reachable through the pendant, and restore everything afterward with a concise missed-items summary."
- **useful because:** It coordinates the worn device, always-on relay, Calendar/Mail, Mac UI, and authenticated browser sessions into a temporary attention boundary. Today each surface can act alone, but none can preserve the owner's focus across a presentation and reliably restore the prior state.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime only for the short activation/exception conversation; a cheaper background model classifies alerts, compares pre/post state, and writes the restoration receipt.
- **latency:** Activation acknowledgement under 1 second; Mac/browser quieting within 3 seconds; restoration within 10 seconds after the owner ends the mode; summary can arrive asynchronously.
- **cost:** Low per use: one short realtime turn plus background classification of only newly arrived Mail/browser events. Dominant cost is extracting and normalizing authenticated page changes, not the pendant interaction.
- **security:** The system must snapshot notification settings, open windows/tabs, and any temporary browser mutations before changing them; private Mail and logged-in pages stay on-device or in the authenticated browser bridge. Never dismiss, archive, or send anything. Ending mode should restore only changes made by this mode, with a receipt and recovery action if restoration fails.
- **missing:** A pendant event/voice intent for start/end attention mode with offline acknowledgement; A Mac bridge transaction that snapshots and restores notification/focus settings and window/tab state; A browser session API for temporary per-tab quieting and post-mode delta extraction; Relay scheduler/state store for mode expiry, crash recovery, and quiet-hours policy; A unified urgency classifier with explicit source citations and a dashboard showing the pre/post diff

### "When I press the pendant twice and say “private moment,” make the whole hive safe to use around other people: the Mac and browser should hide notification previews and sensitive tab content, the relay should speak only minimal status, and pressing again should restore my exact prior state and show me what was suppressed."
- **useful because:** The owner can have a trusted assistant in public without accidentally exposing Mail, logged-in pages, calendar details, or spoken content to bystanders. This is a coordinated privacy boundary across the wearable, relay, Mac, and browser—not merely a Mac Focus toggle.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime handles only the short activation/deactivation exchange; a small background rules engine applies deterministic redaction and produces the suppression receipt. No expensive model is needed for ordinary transitions.
- **latency:** Local acknowledgement immediately; Mac notification and browser masking within 1 second; relay speech policy within 500 ms; restoration within 3 seconds after deactivation.
- **cost:** Near-zero model cost for activation and restoration. Occasional background summarization of suppressed event counts is the dominant cost and can use a cheap model or deterministic templates.
- **security:** The privacy policy must fail closed: if Mac/browser state cannot be snapshotted or restored, do not expose new content and announce only a generic failure. Sensitive text must never be sent to the relay merely to decide whether to redact. Store hashes/counts rather than suppressed content. Restoration must be scoped to changes made by this mode, with a visible audit receipt.
- **missing:** Pendant firmware gesture and offline privacy-state latch with haptic/LED acknowledgement; Relay-wide content policy that can switch the voice agent to metadata-only responses; Mac transaction API for atomic snapshot, notification-preview suppression, and restoration; Browser bridge support for masking authenticated tab previews and page text without closing sessions; A local, deterministic sensitivity/redaction policy and recovery receipt surfaced in the dashboard


## Changes it proposed to its own stack

### `mac-harness` — Implement the granted mac_readonly_inspect bridge as a genuinely side-effect-free service: running-apps and foreground-app via NSWorkspace, accessibility_enabled via AXIsProcessTrusted, ui_snapshot via Accessibility APIs with redacted role/title/value metadata, browser_tabs through the existing authenticated browser bridge, and bounded list_directory restricted to approved paths. Return a typed receipt with timestamp, permission state, truncation, and failure reason; do not silently fall back to screenshots or shell.
- **owner gets:** The agent can currently be asked what is on the Mac, but the newly granted inspection contract returns “no implementation.” Implementing it lets the owner get truthful, low-risk answers and lets cross-device routines decide whether to interrupt, act, or wait without stealing focus or changing anything.
- effort: Medium: native Mac helper plus browser-bridge adapter, schema tests, redaction tests, and permission/error handling.  ·  risk: Accessibility metadata can contain secrets and UI values; default to role/title and redact text, require explicit include settings for values, cap output, and log only hashes. If an adapter fails, report unknown rather than guessing. Recovery is restartable because all operations are reads.
- cost: No meaningful model cost; small local CPU/RAM overhead per inspection and modest engineering time.  ·  latency: Target under 300 ms for app/foreground/permission, under 1 s for bounded UI snapshot or directory listing, and under 2 s for browser-tab reconciliation.
- security: Improves security by removing pressure to use arbitrary shell or screenshots for state discovery; still needs strict path allowlists, redaction, and account/session scoping.
- depends on: A native Mac read-only helper with Accessibility permission handling; An authenticated browser-tab read API; A shared redaction and receipt schema


## What it asked for

_Nothing._
## Its own summary

Recorded a new cross-surface capability: a pendant-triggered privacy shield that fails closed, masks Mac/browser content, restricts relay speech to minimal status, and restores exact prior state with an audit receipt. This is distinct from ordinary focus/presentation mode because it is designed for bystander privacy and prevents sensitive content from reaching the relay for classification.

**Biggest unknown:** Whether the pendant firmware can distinguish and reliably acknowledge a double-press gesture offline without disrupting its existing voice interaction state.

