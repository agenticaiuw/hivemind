# Harness derivation — relay-realtime — round 262

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If what you’re working from doesn’t match reality, warn me before acting."
- **useful because:** Prevents bad actions when memory, cached state, or assumptions diverge from what the Mac can actually see.
- **path:** relay → mac-bridge → mac-vision → browser
- **model tier:** Realtime to warn; background to reconcile.
- **latency:** Warn within a second; reconciliation can take longer.
- **cost:** Low to medium: a status check plus targeted verification reads.
- **security:** Only compare metadata and identities needed to detect conflicts. Don’t expose sensitive content in the warning.
- **missing:** A standardized contradiction signal in the shared context; An agreed set of sources of truth and a merge strategy

### "Rewrite the text I currently have selected to be clearer, read me the proposed version, and replace it only when I say “use that.”"
- **useful because:** The pendant can hear an instruction but today cannot safely connect it to the exact selection under the owner's cursor. This makes editing hands-free while keeping the owner in control of the words that will be inserted, across Safari, Mail, Notes, VS Code, and other Mac apps.
- **path:** pendant → relay → mac-planner → mac-vision
- **model tier:** Use the realtime model only for intent and the short spoken proposal; have mac-vision obtain the focused app and selection, and a cheaper text model transform it. The Mac agent performs replacement and returns an exact diff.
- **latency:** Read selection and speak a first draft within 3 seconds; replacement under 1 second after “use that.”
- **cost:** About $0.005–$0.03 per edit, dominated by transformation tokens; no screenshot is needed when Accessibility can read the selection.
- **security:** Selected text can contain passwords, health data, or confidential mail. Send only the selection, never the whole document; mark the source app and redact obvious secrets. The preview must be spoken before insertion, and insertion must be undoable as one native edit.
- **missing:** A focused-selection read action across Accessibility and browser contexts; A pending-transform record that binds the spoken approval to the exact selection hash and app/document identity; A native undo/rollback receipt for replacement

### "What am I pointing at? Use the Mac camera to identify the object, read the label or model number, and tell me what I can safely do with it."
- **useful because:** The pendant has no camera, but the Mac can be a visual instrument. A spoken request paired with a live camera frame would let the owner identify cables, medication packaging, hardware parts, or a confusing screen without picking up a phone, then turn that observation into a useful next action.
- **path:** pendant → relay → mac-vision → mac-planner
- **model tier:** Use relay-realtime for the conversational turn; mac-vision captures and crops the camera frame; a vision model extracts identity and text; mac-planner can optionally look up documentation or prepare a reversible next step.
- **latency:** Frame capture and a concise identification in 4 seconds; documentation lookup may continue asynchronously with a pendant alert.
- **cost:** Approximately $0.02–$0.10 per visual query, dominated by image inference and optional web lookup.
- **security:** Camera frames are highly sensitive and must be processed ephemerally, never added to memory by default. Show the owner which camera was used, avoid capturing bystanders, and require an explicit second utterance before any physical or system action based on the identification.
- **missing:** A Mac camera capture route with a user-visible preview and ephemeral retention; A vision result schema that includes confidence, extracted text, and uncertainty instead of a single guess; A relay handoff from visual observation to planner lookup/action with provenance

### "What changed on my Mac since I left? Give me only new notifications, changed files, browser tabs I did not open, and tasks that finished while I was away."
- **useful because:** The owner currently gets disconnected status answers: Mac health, browser tabs, and job status are separate. A wearable-specific return summary would compress the important delta between departure and return without reading every notification or replaying every task.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Use a cheap background collector to checkpoint a privacy-filtered departure snapshot and compute structural diffs; use relay-realtime only to answer the spoken query and summarize the already-computed delta.
- **latency:** On departure/reconnect, checkpoint in under 2 seconds. On query, speak the first prioritized sentence within 1 second; full diff can follow asynchronously.
- **cost:** Low: mostly local structured diffs, around $0.001–$0.02 for summarization depending on notification volume.
- **security:** The snapshot could expose private notifications and file names. Keep it local or encrypted, retain only hashes/metadata by default, scope browser content to titles and URLs unless explicitly requested, and clearly distinguish observed changes from inferred importance.
- **missing:** A departure/return presence signal from pendant connectivity or an explicit physical gesture; A normalized checkpoint containing Mac app state, notification identifiers, browser tab identities, and relay job receipts; A diff/ranking service that can say “no evidence” separately from “nothing changed” and deliver the result to the pendant


## Changes it proposed to its own stack

### `relay` — Implement a real job completion notification pipeline: when a Mac job reaches a watched terminal state, emit a short user-facing summary to delivery targets (pendant/phone/dashboard). Use a durable registry of watches and delivery receipts, and reuse the existing inbox queue concept rather than inventing a new one.
- **owner gets:** They can start something and stop thinking about it, then hear the result later without polling.
- effort: Medium to high: requires a relay-side component plus integration with job status reads and delivery targets.  ·  risk: Duplicate or missing notifications if watches aren’t durable. Mitigate with idempotent watch ids and delivery receipts.
- cost: Low ongoing cost per watch; polling dominates. Storage cost for watch records and receipts is small.  ·  latency: Near real-time when the state transitions; otherwise bounded by poll interval.
- security: Only deliver minimal status text; avoid including sensitive content. Require confirmation for any follow-on action.
- depends on: A resolvable delivery mechanism (replacing unresolved relay_event_push); A durable store for watches and receipts

### `hardware` — Add a low-profile rotary encoder with push plus a second tactile button to the pendant, with the encoder producing detents and the second button a distinct interrupt input; expose both over the existing nRF9160 firmware event path and preserve the current single-button behavior when the new controls are absent.
- **owner gets:** The owner can currently speak or use one ambiguous button, which is poor when walking, driving, or unable to dictate. A wheel would let them silently move through queued alerts, choose a result, adjust spoken volume, or cancel a pending operation by feel; the second button gives an unambiguous “stop/next” action without waiting for speech recognition.
- effort: High: jewellery-grade mechanical design, waterproofing, debouncing, new board/enclosure, firmware input state machine, and relay gesture semantics. Prototype with an encoder breakout over USB before committing to the enclosure.  ·  risk: Accidental detents could skip or cancel work; default all new events to navigation and require a deliberate push/second-button hold for destructive operations. If the encoder fails, firmware falls back to the existing SW0/SW1 mappings and the pendant remains usable.
- cost: Approximately $8–$30 in prototype components and PCB/enclosure changes; negligible steady-state power, with brief GPIO polling/interrupt overhead.  ·  latency: Local navigation feedback under 50 ms; no network round trip for stop, replay, or volume changes.
- security: Adds physical affordances, not new network permissions. A long-press action should be logged with the device session ID so the relay can distinguish a real tactile cancel from a dropped link.
- depends on: A firmware event contract for encoder detents, push, and second-button press/hold; An interaction map that assigns non-destructive navigation before any mutation; Pendant enclosure and PCB revision


## What it asked for

_Nothing._
## Its own summary

Recorded four owner-facing proposals this round: a jewellery-grade encoder/second button for silent wearable navigation; voice-driven selected-text rewriting with spoken preview and exact approval binding; pendant-directed Mac-camera object/label identification with provenance; and a departure/return delta briefing across Mac, browser, and relay jobs. The first three are distinct capabilities/change; the last was recorded with a warning that it is close to an existing backlog item, so it should be deduplicated before implementation. The key missing pieces are cross-surface state contracts: focused-selection identity, ephemeral camera capture, and a durable departure checkpoint/diff model.

**Biggest unknown:** Whether the existing Mac Accessibility and vision routes already expose focused selection and camera capture strongly enough to implement the first two without new routes; this round was explicitly barred from further discovery.

