# Harness derivation — relay-realtime — round 115

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Handle that for me, and tell me what happened — even if my Mac is asleep."
- **useful because:** This turns the pendant into a dependable front door: you can hand off a task while away, and later get a clear status update without re-explaining. It reduces friction and avoids duplicate work.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** Realtime for the initial voice exchange; a cheaper planner tier for the Mac/browser work; relay uses a lightweight status read path for follow-ups.
- **latency:** Sub-second for acknowledgement; seconds to queue; status checks should be immediate if already recorded; no long waits in the pendant loop.
- **cost:** Low for status reads; moderate for planning/execution; dominated by downstream tool calls and any page automation, not the relay.
- **security:** Tasks and status metadata leave the device; sensitive content may appear in utterances or receipts. Status should be read-only, and receipts should not be altered by the relay.
- **missing:** Implement relay_route_intent so the relay can route without inventing a protocol; Implement relay_job_status backed by durable relay job records; Implement server_browser_actions or explicitly disable it until available; Durable job runner/receipt storage so status exists when the Mac is offline

### "Start something on my pendant, then let me continue it from whichever surface I reach next—my Mac, an authenticated browser tab, or the pendant—by saying things like “continue that,” “use the second option,” or “stop it,” without repeating the request."
- **useful because:** The owner is physically away from the Mac much of the day. Today a voice request, a Mac job, and a browser command are separate worlds; a handoff loses the conversational referent and forces re-explanation. This would make the hive feel like one persistent assistant rather than several tools, while preserving the owner’s ability to interrupt or redirect work from the wearable.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use relay-realtime only for the short spoken handoff/clarification and reference resolution. Use the cheaper background model in mac-planner for plan repair and summarizing state; use mac-vision/browser-extension only for the concrete observation or action.
- **latency:** A spoken continuation should resolve in under 700 ms when state is already cached; a new downstream observation may take 2–8 s and should produce an immediate pendant acknowledgement plus a later completion event.
- **cost:** About $0.01–$0.05 per continuation, dominated by background planning and any browser/page vision; reference resolution itself should be a small relay inference and not a full realtime turn.
- **security:** The relay must never guess across unrelated tasks: every handoff needs a durable task identity, surface, timestamp, and cited last state, with explicit ambiguity reporting. Browser credentials remain in the authenticated browser session; Mac files remain on the Mac. Stopping a task must cancel queued downstream work and record the cancellation receipt.
- **missing:** A durable cross-surface task identity and event log that links one voice run to Mac plans, Mac actions, browser commands, observations, and receipts; A compact state projection readable by relay-realtime so pronouns such as “that” and ordinal references such as “the second option” resolve without resending the entire transcript; A bidirectional handoff protocol: each surface must publish typed progress/choices and accept continuation, redirect, and cancel events; Pendant UX for selecting among genuinely ambiguous active tasks with one button/LED pattern and a short spoken disambiguation; Retention and redaction rules for the shared task projection

### "When I ask for something that requires a choice—like booking travel, buying equipment, or replying to an opportunity—have the hive gather live options from my authenticated browser, check my local calendar/files/preferences on the Mac, tell me the best two choices with the reasons over the pendant, and carry out whichever one I name."
- **useful because:** Today the owner can search in one place and act in another, but cannot get a trustworthy recommendation that combines private local constraints with live authenticated web state. This turns the pendant into a practical decision front door: it does the tedious evidence gathering while the owner is away, then a short spoken choice completes the task.
- **path:** pendant → relay → browser-extension → mac-planner → mac-vision → dashboard
- **model tier:** Use a cheap background model for option extraction, constraint matching, and citation packing. Use relay-realtime only to ask the final narrow choice and normalize the owner’s answer. Use mac-planner/browser-extension for execution; mac-vision only when a page cannot expose structured controls.
- **latency:** Acknowledge immediately; assemble a recommendation in 10–30 seconds depending on authenticated pages and local reads. The spoken comparison should be under 15 seconds, with execution status delivered asynchronously.
- **cost:** Roughly $0.03–$0.20 per invocation; browser page loads and occasional vision dominate, not the short realtime turn.
- **security:** Private calendar/files and authenticated browser contents must be joined only in a transient, encrypted evidence bundle with per-field provenance and automatic expiry. Never send browser cookies to the model. Before execution, the spoken choice must bind to an exact option fingerprint (price, recipient, date, URL) so a changed page cannot silently substitute. Keep the owner’s maximum-access policy—no unnecessary approval gate—but refuse to execute if the selected option no longer matches its cited evidence.
- **missing:** A cross-surface evidence-bundle format with source citations, freshness timestamps, option fingerprints, and redaction labels; A local-constraint adapter that can expose only the relevant calendar/files/preferences to the planner without uploading whole databases; Browser extraction of authenticated, multi-page options plus a stable revalidation operation immediately before action; A spoken disambiguation schema that compresses options into recognizable labels and maps “the cheaper one” or “Friday evening” to the fingerprint; An execution transaction that revalidates the fingerprint, performs the Mac/browser action, and emits a receipt tied to the evidence bundle


## Changes it proposed to its own stack

### `integration` — Add a cross-surface Evidence-and-Choice transaction layer. Browser and Mac adapters publish normalized options as signed records containing source URL/path, extracted claims, freshness, and an option fingerprint. A background adjudicator joins those records with narrowly scoped local constraints, while relay-realtime receives only a compact spoken-choice packet. The selected fingerprint is re-read and revalidated at execution time; the resulting action and receipt point back to the exact evidence used.
- **owner gets:** The owner can make a consequential choice from the pendant without manually shuttling browser pages, calendar details, and local documents between agents, and cannot accidentally act on a stale price, date, recipient, or account state.
- effort: Medium-to-high: define the record schema and signing/expiry rules; add browser and Mac adapters; implement constraint scoping and revalidation; add relay phrasing and choice parsing; test page changes and partial failures across all surfaces.  ·  risk: A parser could omit an important condition or an option could change between comparison and execution. Recover by requiring citations and freshness, refusing fingerprint mismatches, retaining the original evidence/receipt for replay, and speaking a concise “changed—here are the new options” result instead of silently substituting.
- cost: Small background-model cost for extraction and matching (roughly $0.02–$0.15 per decision); storage is short-lived metadata. Browser page loads and occasional vision are the dominant costs.  ·  latency: Adds 1–3 seconds for normalization and final revalidation, but relay can acknowledge immediately and deliver the comparison asynchronously.
- security: Improves security through least-data constraint projection, encrypted short-lived bundles, provenance, and exact-option binding. It introduces a sensitive join point, so bundles must be scoped, access logged, expired, and never contain browser cookies or whole local databases.
- depends on: A durable cross-surface task identity/event stream; Typed browser and Mac observation adapters; A relay-readable spoken-choice packet and parser; Execution receipts that accept evidence fingerprints; A revalidation hook immediately before browser or Mac mutation


## What it asked for

_Nothing._
## Its own summary

Recorded two nontrivial additions. First: a single cross-surface task identity so a pendant request can be continued, redirected, or stopped from the Mac or an authenticated browser without re-explaining it. Second: an evidence-and-choice transaction layer that joins live authenticated browser options with narrowly scoped Mac constraints, presents fingerprinted choices over the pendant, and revalidates the selected choice before execution. The latter was also recorded as an integration change with provenance, expiry, and receipts.

**Biggest unknown:** Whether the existing backend already has an undocumented durable task/event identity and typed observation schema; if it does, the remaining work is wiring and projection rather than inventing storage. No further discovery was performed per instruction.

