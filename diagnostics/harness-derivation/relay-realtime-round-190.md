# Harness derivation — relay-realtime — round 190

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If I get stuck, listen for what I’m doing and suggest the next step.”"
- **useful because:** This would feel like a real companion: if the owner hesitates or repeats themselves, the system can offer a gentle, context-aware nudge rather than forcing them to explicitly ask for help.
- **path:** relay → mac-bridge → mac-vision → browser-extension
- **model tier:** Realtime for conversational glue; mac-vision/browser work is planned by mac-planner; suggestions come from a cheaper planning model.
- **latency:** Nudge should arrive within a couple seconds of a detected stall; otherwise remain silent.
- **cost:** Mostly planning and occasional page/app inspection; keep inspections small and capped to avoid expensive loops.
- **security:** Only inspect apps/tabs when there’s an explicit stuck signal (e.g., repeated request or explicit “help”), and avoid reading sensitive fields like passwords or tokens.
- **missing:** A reliable stall signal (e.g., explicit “help” utterance or repeated failure detected in job receipts); A lightweight, privacy-safe inspection mode for mac-vision/browser that returns only what’s needed for guidance

### "When I arrive at a place, give me the right handoff for that place: read my pendant location, inspect the Mac and authenticated browser, and tell me only what is relevant now; if I say 'set up here', open the appropriate apps and tabs."
- **useful because:** The pendant is the only surface that knows where the owner physically is, while the Mac and browser know what work is waiting. This turns location changes into useful, timely context instead of requiring the owner to remember which tools to open.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Background model for geofence classification and ranking; relay-realtime only for the spoken handoff; mac-planner for actions.
- **latency:** Speak an initial arrival summary within 3 seconds of a confirmed geofence event; setup actions may take up to 30 seconds.
- **cost:** About $0.01-$0.05 per arrival, dominated by one planner/context call; geofence evaluation is near-zero cost.
- **security:** Location and authenticated browser context leave the pendant/relay and Mac. Store coarse place labels rather than raw tracks; require an explicit first-time place enrollment and provide an off switch. Opening tabs/apps is reversible, but sending or editing external content must never be implicit.
- **missing:** pendant location/geofence event and coarse-place persistence; Worker Cron/Durable Object alarm or event consumer for arrivals; cross-surface context snapshot combining Mac state and browser inspections; place-specific setup routine and inbox delivery when the Mac is offline

### "Let me say 'watch this' about a live browser page or Mac task, then later tell me when the exact condition changes — for example a ticket is assigned, a price drops, or a deployment turns green — with a short spoken explanation and a link or action ready."
- **useful because:** Today the owner must repeatedly ask for status. A durable watch combines the browser's authenticated session, the Mac's local state, and the always-awake relay into a useful asynchronous capability that survives ending the voice session.
- **path:** pendant → relay → browser-extension → mac-planner → mac-vision → dashboard
- **model tier:** Cheap background polling/diff model; relay-realtime only interprets the initial request and speaks the alert; use a stronger model only when a change needs explanation.
- **latency:** Create a watch acknowledgement in under 2 seconds; detect ordinary changes within 1-5 minutes; deliver the alert as soon as the condition is confirmed.
- **cost:** Roughly $0.02-$0.20 per watch per day depending on polling frequency and page complexity; browser polling and model calls dominate.
- **security:** Authenticated page contents and local task state are sensitive. Encrypt watch snapshots, minimize diffs, expire watches by default, and make the spoken alert disclose what changed without reading secrets aloud. Never perform the resulting action automatically.
- **missing:** durable watch records with expiration and deduplication; browser and Mac polling worker while the owner is offline; semantic diff/condition evaluator for page and task state; reliable push delivery to the pendant and paired phone

### "When I say 'recover my work', reconstruct the last coherent state of a task across my voice conversation, Mac actions, browser tabs, and job receipts, then give me a two-sentence resume point and offer the next concrete action."
- **useful because:** A dropped connection, context switch, or unfinished multi-step task currently forces the owner to remember what happened. This is the single most valuable everyday capability: the worn front door can recover intent, while the Mac/browser can recover actual state and receipts rather than guessing from conversation alone.
- **path:** pendant → relay → mac-planner → browser → mac-vision → dashboard
- **model tier:** Background synthesis over structured receipts and snapshots; relay-realtime performs only the short spoken summary and dispatches the selected next action.
- **latency:** Return a trustworthy resume point within 5 seconds; if state collection needs a live Mac/browser round trip, say what is known immediately and complete within 20 seconds.
- **cost:** About $0.03-$0.15 per recovery, dominated by state collection and synthesis; subsequent action planning is an additional planner call only if requested.
- **security:** The reconstruction may expose private tabs, text, or commands. Scope it to the owner's authenticated session, redact secrets and tokens, retain provenance for each statement, and distinguish observed state from inference. Do not claim completion without a receipt.
- **missing:** a unified cross-surface task/session identity; read-continuity snapshot that joins voice, plan, execute, browser, and Mac receipts; provenance-aware synthesis with confidence and stale-state labels; a resume protocol that can hand the chosen next action to Mac or browser and return its receipt


## What it asked for

_Nothing._
