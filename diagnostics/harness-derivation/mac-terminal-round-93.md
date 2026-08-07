# Harness derivation — mac-terminal — round 93

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac agent readiness and job diagnostics** — Live /ops/snapshot reports fullControlMode=true and llm planner enabled, but ready=false because Accessibility and Screen Recording are not granted; browser extension is offline with 7 pending commands. GET /jobs shows recent browser failures taking ~45 seconds, while command is blank in the job record and receipts only carry generic failure text. GET /observe reports 120 retained jobs, 146 actions, 16 failures, and 112 unattributed tiers.
  - evidence: GET /ops/snapshot, GET /jobs, GET /observe at 2026-08-07T13:11Z

## Capabilities it proposed

### "“Compare the information in this private browser page with my local files, tell me what conflicts, and prepare a local report I can review—without sending the private contents to the cloud.”"
- **useful because:** Today the owner must choose between manually copying sensitive material into an AI conversation or handling the comparison themselves. This would let the pendant coordinate a logged-in browser session and Mac-local file analysis while keeping raw account data and documents on the Mac, then provide a concise spoken conclusion and a reviewable artifact with citations and hashes.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-terminal → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use the realtime model only for the owner's spoken request and short answer. Use a cheaper background model for local structured extraction and conflict classification; use deterministic Mac code for hashing, parsing, redaction, and report assembly. Send only schemas, hashes, redacted snippets, and the final locally generated summary through the relay.
- **latency:** A first spoken acknowledgement in under 2 seconds; browser capture and local comparison in 10–60 seconds depending on file count; the pendant can announce completion or leave a queued audio result if the owner walks away.
- **cost:** Usually one small background-model call (roughly 2k–6k input tokens) plus negligible relay and local compute cost. Cost is dominated by extracting too much page/file text; deterministic chunking, hashes, and conflict candidates should keep the model context bounded.
- **security:** Raw authenticated page text, local file contents, cookies, and credentials must remain on the Mac. The browser bridge needs an explicit per-task tab/session binding; local reports need a private workspace and retention/deletion controls. The model should receive only redacted candidate fields unless the owner explicitly asks to disclose a passage. Creating or overwriting a report should be clearly marked and undoable; never submit anything back to the website.
- **missing:** A Mac-local comparison worker that can read selected files and browser extraction results without forwarding raw contents to the relay; A privacy-preserving evidence protocol: field schemas, local hashes, redaction, provenance, and a way for the model to request only a specific missing field; A browser capture mode that returns structured selected regions and source metadata rather than a broad page dump; A local report artifact with citations into both the browser page and source-file hashes, plus retention and deletion controls; Relay and pendant result messages that describe completion without embedding sensitive evidence


## Changes it proposed to its own stack

### `model-routing` — Turn the existing non-blocking observeBeforeAction signal into a capability-aware fallback hint for the planner. Before dispatch, collect a short-lived readiness snapshot (Accessibility, Screen Recording, browser-extension online/pending age, app automation grants, shell reachability) and annotate the action with viable alternate mechanisms. If a GUI/browser action is unavailable, the planner should automatically choose an equivalent permitted route (for example AppleScript or shell for a Mac setting, authenticated browser bridge versus public fetch) when semantics are equivalent; otherwise fail immediately with the exact missing permission/endpoint and a one-line owner fix. This is advisory routing only: FULL_CONTROL_MODE remains unrestricted and no action is refused by policy.
- **owner gets:** The agent stops wasting 45 seconds retrying a browser or GUI action that cannot work on this Mac. It either completes through another surface or tells the owner exactly why it cannot, which is especially valuable from a pendant where a generic failure is hard to act on.
- effort: Moderate: normalize existing /ops/status and browser status into a cached readiness object, make executor observations available to the planner/relay, add equivalence mappings for common Mac intents, and include the chosen route plus unavailable alternatives in the receipt.  ·  risk: Fallbacks can have different semantics (AppleScript may affect the wrong app or shell may lack UI context), so mappings must be conservative and explain the substitution. Readiness can go stale between observation and dispatch; mark timestamps and treat it as a hint, never a guarantee. Do not expose permission details or URLs beyond the authenticated owner surfaces.
- cost: Low API cost: deterministic readiness and route selection avoid planner calls and repeated failed browser timeouts. Small local status probes per job, cached for seconds.  ·  latency: Cuts known-unavailable browser attempts from ~45 seconds to immediate alternate execution or actionable failure; adds only a small preflight probe.
- security: No new authority and no gates. Permission state and route diagnostics remain local/owner-authenticated; relay receives only a concise reason and selected route. Fallback mappings must preserve existing unrestricted owner policy.
- depends on: Existing read-only /ops/status or /ops/snapshot and /browser/status endpoints; Existing non-blocking observeBeforeAction hook in action receipts; Existing executor route dispatch and relay job completion summaries


## What it asked for

_Nothing._
## Its own summary

I discovered and live-checked the Mac observability surfaces. The important current gap is readiness-aware routing: the Mac is in FULL_CONTROL_MODE, but Accessibility and Screen Recording are missing; the browser extension is offline with 7 queued commands, and browser failures consume about 45 seconds before returning a generic error. I recorded a new model-routing change that uses existing non-blocking observations to choose an equivalent available route or immediately explain the missing dependency, without adding gates or reducing owner access. I also recorded the live finding. I do not need another permission or tool this round; the remaining need is implementation of that readiness/fallback router and its tests.

**Biggest unknown:** Whether an equivalent fallback is semantically safe for each action type; this needs an explicit conservative mapping table and live verification rather than assuming shell/AppleScript/browser routes are interchangeable.

