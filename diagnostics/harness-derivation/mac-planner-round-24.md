# Harness derivation — mac-planner — round 24

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac agent runtime and observability** — The live Mac agent is full-control and planner-enabled with Accessibility, Screen Recording, and Automation grants. Computer-use loop is disabled and vision upload consent is false. Browser extension is currently offline with one pending command. GET /observe can provide foreground app/running-apps/permissions, but the granted typed mac_readonly_inspect UI snapshot has no implementation.
  - evidence: describe(GET /ops/snapshot) returned status 200 with these flags; describe(GET /observe) returned foreground Claude and read-only observation metadata; mac_readonly_inspect(ui_snapshot) returned 'tool was granted a schema but has no implementation yet'.

## Changes it proposed to its own stack

### `mac-harness` — Add a focus-safe execution coordinator around the existing FULL_CONTROL Mac executor. Before each plan, capture the foreground app and a lightweight accessibility/state fingerprint; route UI actions by explicit target app where possible without activating it; execute in bounded batches; after each batch re-check foreground app and target state, abort only on unexpected state drift, and return a receipt that records whether focus changed, what was verified, and which step remains. For actions that inherently require focus (typing into an unaddressable field), mark that requirement in the plan and restore the original foreground app afterward when technically possible. This is observability and recovery, not an approval gate.
- **owner gets:** The pendant can work on the Mac while the owner is writing, coding, or in a meeting without unexpectedly stealing their keyboard or leaving half-completed work in the wrong window. If a page or dialog changes mid-task, the system reports the exact stopping point instead of pretending success. Everyday automation becomes safe to run in the background while preserving the owner's current context.
- effort: Medium: add pre/post state capture to computerControl.js, target-app accessibility adapters, batch boundaries, and receipt schema; exercise against Claude, Safari, Calendar, and Finder. Restoration is best-effort and must be tested per app.  ·  risk: Some apps expose unstable accessibility trees or cannot restore focus reliably; a false state-drift detection could stop a task early, while a missed drift could still misdirect an action. Recover by returning the partial receipt and allowing an explicit resume from the last verified step; retain current executor as fallback.
- cost: Negligible API cost (small local state snapshots); modest local CPU/latency overhead, roughly 100–300 ms per batch. No cloud data required unless existing receipts are synced.  ·  latency: Adds about 0.1–0.3 seconds per action batch, but avoids expensive retries and accidental destructive work.
- security: Improves privacy by avoiding screenshots and favoring local accessibility metadata. Receipts should redact typed text and sensitive UI values by default; foreground-app names and state hashes remain local unless explicitly exported.
- depends on: A real implementation for typed read-only UI snapshots or equivalent local accessibility state inspection; Result receipts (chg-5fc73ce3) to persist verified-step and focus-change metadata

### `mac-harness` — Add a startup and periodic no-op input reachability probe to the Mac agent health path. When Accessibility is reported trusted, post the documented zero-delta cursor event (or an equivalent harmless System Events no-op), record the exact host bundle tested, timestamp, and result, and expose `inputReachability: verified|unverified|failed` in /observe and job receipts. Do not block FULL_CONTROL actions; instead annotate receipts and surface a warning when an interaction may have been a no-op.
- **owner gets:** The owner will know whether an automation actually reached the Mac instead of receiving a misleading success from a stale or wrongly-authorized Accessibility grant. This is especially valuable when asking the pendant to work while away, because failures become diagnosable rather than silently leaving work undone.
- effort: Small: reuse the existing permissions probe, add a harmless event test, cache a short-lived result, and include it in observation and receipts. Test after agent upgrades and macOS permission changes.  ·  risk: Even a no-op event can be misclassified by macOS or trigger an unusual accessibility prompt. Keep it cursor-zero-delta only, never type or click, and fall back to unverified if the probe errors. It must remain advisory, not a hidden gate.
- cost: No API cost; negligible local CPU. One local accessibility call at startup and optionally every few minutes.  ·  latency: No meaningful task latency if cached; at most tens of milliseconds on health refresh.
- security: No screen pixels or user content are collected. Store only bundle identity, timestamp, and boolean result; do not log event payloads.
- depends on: A local implementation of the existing permissions probe or equivalent System Events no-op event endpoint


## What it asked for

### `t11-h383` (tool) — mac_ui_state_snapshot
- why: mac-vision and focus-safe execution need current accessibility hierarchy/state, while mac_readonly_inspect(ui_snapshot) is only a schema with no implementation. GET /observe exposes foreground apps and permissions but not controls, roles, labels, or enabled state.

```json
{
  "operation": "ui_snapshot",
  "app": "string (optional; defaults to foreground app)",
  "max_depth": "integer 1-20",
  "max_elements": "integer 1-500",
  "include_values": "boolean (default false; redact text/password fields unless explicitly enabled)",
  "timeout_ms": "integer 100-5000"
}
```

## Its own summary

Discovered and verified live Mac state: /health, /observe, and /ops/snapshot are reachable. Claude is foreground; 20 apps running; Accessibility, Screen Recording, and Automation grants are present, but input posting/UI reachability is explicitly unverified. Computer-use loop is disabled, browser extension is offline with one pending command, and the granted typed UI snapshot tool has no implementation. Recorded findings, notified mac-vision/mac-terminal/relay, queued a precise mac_ui_state_snapshot tool request, and proposed two new changes: focus-safe state-aware execution and advisory no-op input reachability verification.

**Biggest unknown:** The actual accessibility hierarchy and whether ui_* actions reach the screen; the current read-only UI snapshot schema is unavailable at runtime.

