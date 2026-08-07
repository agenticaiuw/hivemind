# Harness derivation — mac-planner — round 81

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If the browser is unavailable, do the safe equivalent on the Mac when possible; otherwise keep my request until the browser returns, then tell me exactly what happened.”"
- **useful because:** Today the Mac agent reports five pending browser commands while the extension is offline. The owner gets failure after a 45-second wait, even when a read-only Mac-native path could have answered immediately. This would make the pendant dependable across link and app outages without pretending an authenticated browser session exists.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the cheap background/router tier for capability detection and queue management; use realtime only to acknowledge the owner and speak the final concise result. No model is needed for deterministic fallback selection.
- **latency:** Immediate acknowledgement under 1 second; Mac-native fallback under 5 seconds; browser retry with exponential backoff up to a user-configured deadline, then a clear expiration notice.
- **cost:** Near-zero model cost for routing; roughly $0.0001–$0.001 per eventual natural-language status if a text model is used. Dominant cost is noneconomic polling and any browser page extraction.
- **security:** Never substitute a Mac-native page for a browser-authenticated page unless the route is explicitly marked read-only and equivalent. Preserve session affinity, redact page contents in relay telemetry, expire queued commands, and require the existing owner policy for mutations (which currently allows maximum control). Tell the owner whether the result came from browser, Safari/Chrome automation, or was only queued.
- **missing:** A deterministic fallback matrix declaring which browser intents have safe Mac equivalents; Durable queued-command expiry and retry state tied to the existing browser command id; A browser-online event/heartbeat transition that wakes queued work instead of waiting on fixed polling; A provenance field in the spoken/dashboard receipt identifying the execution surface

### "“If I get interrupted, save this task and continue it later from the exact next safe step—across my pendant, Mac, and browser—without repeating anything or losing the result.”"
- **useful because:** Today a task can span a spoken request, a Mac job, and an authenticated browser session, but a dropped bridge, sleeping Mac, or crash can leave the owner unsure whether a step happened. The owner should be able to resume a real workflow rather than restart it and risk duplicate messages, files, or submissions.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use a deterministic durable workflow/state-machine service for checkpoints, idempotency, retries, and reconciliation. Use the inexpensive background model only to summarize a checkpoint for the owner; reserve realtime for the brief spoken acknowledgment.
- **latency:** A checkpoint must be written before each side effect, adding under 100 ms locally or under 500 ms round-trip. Resume acknowledgment under 2 seconds; reconciliation can run in the background.
- **cost:** Negligible model cost for the state machine; roughly $0.0001–$0.001 only when generating a spoken checkpoint summary. Storage and retries dominate, not inference.
- **security:** Persist only action metadata and redacted outputs by default, never cookies or raw authenticated page contents. Bind checkpoints to the owner, session, and target surface; use idempotency keys and pre/post-condition hashes; expire abandoned workflows. The dashboard and pendant must clearly distinguish committed, uncertain, and not-started steps.
- **missing:** A durable cross-surface workflow record with ordered checkpoints and idempotency keys; A reconciliation protocol for the ambiguous case where a side effect completed but its receipt was lost; Resume signals from relay, Mac bridge, and browser heartbeat rather than polling alone; A user-facing checkpoint timeline and a repair operation for steps that cannot be reconciled automatically


## Changes it proposed to its own stack

### `mac-harness` — Implement the granted mac_readonly_inspect tool as a real read-only adapter over the existing /observe and narrowly scoped inspection routes. Support running_apps, foreground_app, accessibility_enabled, browser_tabs, and list_directory with bounded limits, and return an explicit implementationUnavailable error only for unsupported operations. Add a startup self-test that compares tool output with GET /observe without exposing bearer tokens or page bodies.
- **owner gets:** The system currently grants inspection in the interface but every call fails because there is no implementation. The owner and all agents therefore cannot reliably answer basic questions like what app is foreground, whether input can reach the screen, or whether the browser is connected. This is especially harmful because UI actions can report success while doing nothing.
- effort: Small-to-medium: implement the adapter, route mapping, bounds/redaction, and tests for the five operations; no new Mac permissions required for the non-UI observations already exposed by /observe.  ·  risk: A faulty adapter could over-report state or leak directory names. Keep it read-only, cap result sizes, use the existing /observe redaction policy, and return timestamps plus source route. Recovery is simply disabling the tool; existing execution paths are unaffected.
- cost: Negligible API cost and disk use; one local HTTP request per inspection.  ·  latency: Typically under 200 ms locally; directory listings may take longer but remain bounded.
- security: No additional authority. Do not implement this by shelling out arbitrary commands; use the existing authenticated agent routes and approved path validation.
- depends on: The tool schema already granted for mac_readonly_inspect; GET /observe is live and read-only; A small server-side mapping from operation names to observation fields


## What it asked for

_Nothing._
## Its own summary

Discovered live state: Mac bridge is online, but AI Pendant Agent is not Accessibility-trusted or Screen-Recording-authorized, so UI actions are explicitly unreliable; browser extension is offline with 5 pending commands and 3 durable sessions. The newly granted mac_readonly_inspect interface exists only as a schema and currently returns implementationUnavailable. Proposed a cross-surface degraded-mode router (Mac-native safe fallback or durable browser retry) and implementation of the read-only inspection adapter, and informed faculty-perception.

**Biggest unknown:** Whether the owner wants to manually repair TCC for the exact AI Pendant Agent binary and reconnect the browser extension; neither can be fixed from this harness.

