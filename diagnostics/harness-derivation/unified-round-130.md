# Harness derivation — unified — round 130

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What am I looking at?” (or tap the pendant twice) and have you inspect the currently focused Safari tab or Mac window, explain the important parts aloud, and offer the next reversible step without sending or submitting anything."
- **useful because:** This is the shortest path from a confusing page to help: the pendant supplies an intentional physical trigger, the Mac supplies screen/window context, Safari supplies authenticated page contents, and the relay turns it into a spoken answer. It works without Accessibility when the focused target is Safari via the browser bridge, and falls back honestly when it is not.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime for the one-sentence spoken explanation; background/cheaper model for DOM cleanup or long-page summarization.
- **latency:** Initial acknowledgement under 500 ms; cited explanation in 3–6 s; never execute a mutation without explicit spoken confirmation.
- **cost:** Typically one short realtime turn plus a cheap extraction/summarization call, roughly $0.01–$0.05; browser and Mac calls dominate latency, not tokens.
- **security:** Authenticated tab text and possibly a screenshot leave the Mac only to the relay/model; redact passwords, payment fields, and secrets before model submission. Read-only by default; any click/type/submit requires a second explicit confirmation.
- **missing:** A pendant/USB physical-trigger event wired into the relay conversation; A focused-window contract (Safari tab id plus optional Mac window metadata); A safe screen-context redaction and citation envelope; A route that binds one spoken turn to the latest browser heartbeat without replaying queued commands

### "“Why do you believe that?” and receive a short spoken evidence trail: the exact browser snippet, Mac action receipt, memory fact, or device observation behind the last answer, with its age and confidence."
- **useful because:** Trust becomes inspectable while walking: the owner can challenge an answer without opening a dashboard. This unifies evidence that currently lives in browser results, job receipts, machine context, and captured memory, and exposes stale or contradictory facts instead of bluffing.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only for selecting and speaking a compact evidence card; use a cheaper background model to normalize snippets and compute contradiction/staleness indexes.
- **latency:** Evidence response in 2–4 s; one spoken sentence by default, expandable to detail on a second request.
- **cost:** <$0.02 for most queries; cost is dominated by retrieving/citing source payloads and optional normalization.
- **security:** Never speak or expose secret-sensitivity captures (for example credentials) unless the owner explicitly asks and the privacy policy allows it. Preserve source URLs only for authenticated tabs already owned by the browser session. Read-only.
- **missing:** A unified evidence index linking response ids to source snippets, route receipts, and fact IDs; Freshness/confidence calculation across Mac, browser, relay, and pendant observations; Spoken privacy filtering for sensitive captured facts

### "“Turn what I just did into a routine.” After I complete a multi-step task across Safari, Mac apps, and the pendant, infer the stable intent, show the recorded steps and variables, and create a disabled draft routine that I can review and enable."
- **useful because:** The owner would not have to repeatedly explain workflows they have already demonstrated. This converts real successful behavior into a reusable personal automation while keeping activation explicit and preventing accidental generalization.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheaper background model to cluster completed receipts and infer a routine; use realtime only to summarize the proposed routine and answer follow-up edits.
- **latency:** Draft available within 30 seconds after a task or on explicit request; spoken summary under 3 seconds once generated.
- **cost:** About $0.02–$0.10 per draft depending on receipt volume; storage and receipt normalization dominate.
- **security:** Routine drafts may contain private URLs, account names, or message content. Store parameterized templates with secret fields marked non-replayable; never enable or send anything without explicit confirmation. Ignore steps that contain passwords or one-time codes.
- **missing:** A workflow segmentation and variable-inference service over Mac/browser/pipeline receipts; A routine-draft schema with disabled-by-default status and redacted secret parameters; A review UI that shows each inferred step and its provenance

### "“Is this page trying to trick you?” Before any browser task continues, inspect the page for prompt injection, suspicious data-export requests, hidden redirects, and instructions that conflict with my request; warn me on the pendant and quarantine the task if risk is high."
- **useful because:** Authenticated pages can contain hostile or misleading instructions. The owner gets a security boundary between their logged-in browser and the agent, rather than relying on the model to obey whichever text it most recently read.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Cheap classifier and deterministic URL/DOM rules first; realtime only when the owner asks for an explanation or a nuanced risk judgment.
- **latency:** Low-risk pages add less than 500 ms; high-risk pages stop before extraction or action and produce a spoken warning within 2 seconds.
- **cost:** Usually under $0.01 per page using local rules; model escalation is occasional and costs roughly $0.01–$0.05.
- **security:** The detector itself must not upload full sensitive pages by default. Keep DOM scanning local to the extension where possible, send only suspicious spans and hashes, and fail closed for mutations when the browser session is uncertain.
- **missing:** A browser-extension preflight hook that runs before extraction and every mutation; A signed risk verdict consumed by relay and Mac execution gates; A quarantine and owner-visible explanation flow

### "“Do any of my sources disagree?” Compare my calendar, mail, reminders, authenticated web pages, and recent Mac jobs, then tell me only about contradictions that could cause a missed commitment—such as two locations, changed times, or an action marked complete in one place but pending in another."
- **useful because:** The owner currently receives summaries, but summaries can hide conflicts. A contradiction-focused answer prevents costly mistakes without flooding them with unchanged information.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Background model for entity/time normalization and pairwise comparison; realtime only for the final concise alert.
- **latency:** On demand in 5–15 seconds; scheduled scans may run in the background and speak only when a high-confidence conflict appears.
- **cost:** Roughly $0.03–$0.15 per scan depending on source count; authenticated reads and normalization dominate.
- **security:** Read-only access to private sources. Keep source excerpts local where possible, redact message bodies, and cite the minimum fields needed to explain each conflict. Never resolve or modify a source automatically.
- **missing:** A cross-source entity/time normalization layer; A contradiction graph with confidence, severity, and dismissal state; Connectors that expose structured Calendar/Mail/Reminders fields alongside browser extraction


## Changes it proposed to its own stack

### `interaction` — Add an explicit cross-surface handoff envelope for every pendant-originated request: requestId, utterance, physical trigger, current device link (USB/LTE), focused browser session/tab, selected context artifacts, model tier, and an expiry. Relay, Mac, and browser must acknowledge the same envelope; if any acknowledgement is missing or stale, the pendant speaks a precise pause reason rather than silently retrying.
- **owner gets:** The owner gets continuity instead of mysterious failures: a request begun with the pendant either completes with a traceable result or says exactly whether the Mac, Safari, or link went away. It also prevents a stale browser tab or old command from being mistaken for the current request.
- effort: Medium-high: shared schema and persistence in relay/D1, Mac and browser adapters, pendant acknowledgement firmware, plus fault-injection tests for USB disconnect and browser heartbeat expiry.  ·  risk: Schema rollout can strand in-flight jobs; accept both old and new envelopes temporarily and expire orphaned envelopes safely. Never replay a mutation merely because an acknowledgement was lost.
- cost: Negligible storage (one compact envelope per active/recent request); modest D1 writes. No meaningful model cost.  ·  latency: Adds one local acknowledgement round (<100 ms on USB, ~300–800 ms over relay); eliminates much larger retry ambiguity.
- security: Improves least-privilege and auditability, but the envelope must hash or redact sensitive page text and avoid persisting raw audio.
- depends on: A stable pendant USB serial event channel; Browser heartbeat/session identity from /browser/status and /browser/heartbeat; Existing job receipts and undo routes; A documented relay intent contract


## What it asked for

### `s12-ye9t` (skill) — context_snapshot_trigger
- does: On a deliberate long-press then release (or configurable double-press) of the single user button, emit a signed, monotonic event over the active USB serial/LTE link with event id, button timing, battery/link state, and a short local audio pre-roll marker. Do not record or transmit raw audio on the pendant; the server/Mac decides whether to request it. Give immediate LED/haptic-equivalent feedback via the existing LED if available.
- must be on-device because: The trigger must work while the owner is wearing the device and must distinguish an intentional request from a dropped-link or server retry. Local event sequencing and feedback remain reliable across link loss; the Mac can consume it today over USB.
- trigger: Button long-press (800–1500 ms) or double-press, whichever firmware validation shows least accidental activation.
- storage: Persist only a 16-byte rolling event counter and last-trigger timestamp in nonvolatile settings; no raw audio. Under 64 B RAM for the event record plus existing serial TX buffer.
- RAM budget: ~1–2 kB implementation including debounce/state machine and packet buffers, comfortably within 211,608 B application RAM; must not allocate an audio buffer or TLS context.

