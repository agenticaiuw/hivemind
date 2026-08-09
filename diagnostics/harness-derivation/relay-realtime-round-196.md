# Harness derivation — relay-realtime — round 196

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “run my focus block,” make my Mac and browser become a temporary focus environment: preserve and close distracting tabs/apps, start the named project, silence non-urgent notifications, and restore exactly what was changed when I say “end focus.”"
- **useful because:** The owner gets a reliable, reversible transition into deep work from the worn pendant, without manually reconstructing their workspace afterward. The important value is the cross-surface snapshot-and-restore guarantee, not merely launching an app.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension
- **model tier:** Realtime handles the short voice exchange and confirmation of the project; mac-planner performs the multi-step reversible workflow, with mac-terminal collecting an exact pre-state and browser-extension applying tab changes.
- **latency:** Acknowledge within 1 second; establish the workspace within 15 seconds; restoration within 10 seconds after the spoken end command.
- **cost:** About $0.02–$0.08 per invocation, dominated by one planner call; terminal and browser actions are local.
- **security:** The snapshot must exclude secrets and page contents, and restoration must be scoped to the same Mac/browser profile and session. If the Mac disappears, the relay must say the block was not established rather than pretending. Closing tabs or muting notifications is reversible, but the owner should be told which mutations were applied.
- **missing:** A first-class workspace snapshot/restore record with a durable job id and per-action receipts; Mac actions for notification focus mode and lossless Safari tab/window restoration; A browser-extension batch operation that tags changes with the focus-block id

### "While I am traveling, watch my itinerary and only interrupt me when a change requires a decision: read the authenticated airline and lodging pages in my browser, compare them with Calendar and Mail on my Mac, explain the conflict over the pendant, and—after I answer—update the affected calendar items and draft or send the needed messages."
- **useful because:** This turns the hive into an agent that protects the owner's time rather than a voice remote. It can reconcile information that is split between authenticated browser sessions and local productivity data, then act while the owner is away from the Mac.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision
- **model tier:** A background/cheap model performs periodic change detection and cross-source reconciliation; realtime is used only for the interruption and the owner's answer; mac-planner executes calendar and messaging changes.
- **latency:** Change detection can be within 5 minutes; an owner-facing interruption should be generated within 30 seconds of a confirmed high-impact change; a spoken answer should produce a draft/update within 20 seconds.
- **cost:** Roughly $0.10–$0.40 per travel day, dominated by authenticated page reads and one reconciliation call; substantially cheaper than polling with realtime.
- **security:** Browser credentials and travel details remain on the browser/Mac surfaces; relay receives normalized deltas, not full pages. Sending messages or making paid itinerary changes must be represented distinctly in receipts and never be silently inferred from an ambiguous spoken answer. Expired trips and stale sessions need hard suppression.
- **missing:** A real scheduler/worker with durable alarms and deduplicated watches; Authenticated browser page-watch support that can extract itinerary deltas without uploading full page content; A cross-source entity matcher for flights, reservations, dates, and time zones; A pendant delivery path that can queue a decision request and correlate the spoken answer to its watch

### "If I say “I lost my pendant,” immediately quarantine that device: revoke its relay credentials, stop delivering queued audio or alerts to it, invalidate active browser and Mac handoffs, preserve an audit record, and let me re-pair a replacement by speaking a recovery phrase on my Mac."
- **useful because:** A wearable is easy to misplace and can otherwise become a live microphone and a path to private notifications. One spoken incident command should protect the owner across the relay, device inbox, browser session, and Mac rather than requiring them to find four separate controls.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only recognizes the explicit loss command and reports completion; deterministic relay security code performs revocation and queue quarantine; Mac/browser agents handle local token invalidation and re-pairing.
- **latency:** The relay-side quarantine must take effect in under 2 seconds, before any new inbox item is delivered. Mac/browser cleanup can finish within 30 seconds and report independently.
- **cost:** Under $0.01 per incident; this is mostly authenticated state mutation rather than model inference.
- **security:** The loss phrase must be unambiguous and require a previously enrolled recovery factor for re-pairing. Quarantine must fail closed if any surface is unreachable, with a durable receipt. It must distinguish device credentials from the owner's other sessions and never delete evidence needed for audit or recovery.
- **missing:** Per-device credential rotation and revocation with an atomic delivery deny-list; A relay-side quarantine state checked by every audio, inbox, and event-delivery path; Mac/browser local credential cleanup and a replacement-device enrollment flow; A dashboard view showing the last known device, revocation time, and surviving queued data


## What it asked for

_Nothing._
## Its own summary

Recorded three non-overlapping owner-facing capabilities: a reversible pendant-launched focus workspace spanning Mac and browser; a travel-day itinerary guardian reconciling authenticated browser data with Mac Calendar/Mail and interrupting only for decisions; and a spoken lost-pendant quarantine/recovery flow that revokes delivery and credentials across the entire hive. Each names the concrete missing scheduler, watch, snapshot, credential, and delivery primitives rather than pretending they exist.

**Biggest unknown:** Whether the existing browser watch and device-status routes already have enough semantics to support these proposals; the recorder flagged several route names as only partially observed, so implementation should verify their live contracts before design.

