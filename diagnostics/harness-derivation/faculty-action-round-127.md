# Harness derivation — faculty-action — round 127

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-action-surface** — Mac bridge and Safari extension are online; relay reachable and has durable audio/state. Browser currently has 3 tabs but active tab is a failed example.com page. Computer-use loop is disabled and vision upload consent is false; Accessibility and Screen Recording remain ungranted even though AppleScript automation grants are present.
  - evidence: GET /ops/status and GET /browser/status returned 200 at 2026-08-07T17:58Z.

## Capabilities it proposed

### "“Use the details in my logged-in accounts to complete this booking or purchase, but require me to press the pendant’s physical button immediately before the final Submit—and then tell me exactly what was sent.”"
- **useful because:** This is the first safe path from spoken intent to a genuinely completed transaction: browser gathers private details, Mac handles local context, relay survives disconnects, and a physical button provides an unmistakable final authorization that malware or an accidental voice command cannot silently forge.
- **path:** relay-realtime → browser-extension → mac-planner → mac-terminal → faculty-judgement → faculty-action
- **model tier:** Use realtime only to understand the request and summarize the final diff; use a cheaper background planner for field gathering and validation; deterministic relay/job code performs the final submission after the pendant proof.
- **latency:** Draft and evidence in 10–30 seconds; final submit within 2 seconds after the button press; receipt delivered even if the conversation drops.
- **cost:** Roughly $0.01–$0.08 per transaction depending on private-page extraction; most cost is one planning/reconciliation call, not the button or deterministic execution.
- **security:** Private account data remains on the Mac/browser bridge where possible. Never submit credentials or payment secrets to the model. Show before/after field values, destination, amount, and tab URL; require a short-lived physical confirmation nonce, reject stale/replayed presses, and emit an immutable receipt. Accessibility/frame access and a pendant confirmation protocol are missing.
- **missing:** A serial/LTE pendant confirmation event with nonce and timeout; A browser transaction executor that can pause at the final submit and return field-level proof; A relay-side confirmation gate joining browser job ID to the physical button press

### "“While the pendant is USB-tethered to my Mac, let its button and tiny status light control my current action: press once to capture a thought, press twice to mark it urgent, and hold to cancel the last unsent capture—then read the result back to me.”"
- **useful because:** The pendant is physically testable now even without LTE. It turns a worn button into a dependable, low-friction action surface: no phone unlock, no microphone kept open, and cancellation remains available when speech or connectivity is unreliable.
- **path:** pendant → mac-terminal → mac-planner → relay-realtime → faculty-action
- **model tier:** No expensive model for button routing; use deterministic firmware/serial framing and the cheap background tier only for optional transcription, classification, and reminder wording.
- **latency:** LED acknowledgement under 100 ms, capture persisted under 500 ms, spoken result when the Mac is reachable within 3 seconds; queued locally when it is not.
- **cost:** Near-zero for routing; optional transcription/classification is about $0.002–$0.02 per capture and dominates cost.
- **security:** USB serial is local, but must authenticate the device and sequence frames to prevent duplicate actions. Captures are sensitive: encrypt local spool, expose deletion, and never interpret a long hold as a destructive action without a visible cancellation acknowledgement. This is distinct from LTE/offline intent because it is a tethered, immediately executable physical control channel.
- **missing:** A Mac serial harness for /dev/cu.usbmodem00096003658* and a small pendant event protocol; Button gesture firmware and LED acknowledgement state machine; A capture-to-transcription handoff that uses POST /capture and optionally POST /reminders

### "“Save the useful thing I’m looking at in Safari to this project.”"
- **useful because:** The owner can turn a private, logged-in webpage into a durable local artifact without copying URLs, switching apps, or losing provenance. The browser supplies authenticated page evidence, the Mac creates a searchable Markdown/PDF note in the active project, and the pendant confirms completion or reports exactly why extraction was blocked.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-terminal → faculty-perception → faculty-action
- **model tier:** Use a cheap background model to extract title, claims, and tags; use realtime only for the spoken request and concise confirmation. Deterministic code writes the artifact and source manifest.
- **latency:** Capture current tab and acknowledge in 1 second; produce the local artifact in under 8 seconds; if the extension cannot access an iframe, report that specific limitation and offer a top-level-page retry rather than fabricating content.
- **cost:** About $0.003–$0.02 per save for extraction; browser transfer and local file creation dominate latency, not model cost.
- **security:** Authenticated page contents stay on the Mac/bridge and are not uploaded unless the owner explicitly permits it. Store URL, timestamp, tab ID, selected text hash, and extraction confidence; redact passwords, tokens, and hidden form fields. Never overwrite an existing project file without a versioned diff.
- **missing:** A browser command that snapshots the active tab with cited regions and detects inaccessible frames; A Mac project-artifact writer with atomic create/versioning and source manifest; A relay action that binds the pendant request to the active Safari tab and active project

### "“Close out my last meeting.”"
- **useful because:** The owner gets the work after the meeting, not merely a calendar briefing: the Mac finds the latest meeting note and related email, the browser supplies any private follow-up context, the system extracts decisions and owners, creates reminders, and prepares clearly separated follow-up drafts for review. The pendant gives a concise spoken recap while the Mac keeps the evidence packet.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a background text model for note/email extraction and task clustering; use realtime only for the spoken command and short recap. Deterministic Mac actions create reminders and drafts but never send them.
- **latency:** Return an initial meeting artifact in 10 seconds and finish extraction in under 30 seconds; pendant recap under 5 seconds after completion.
- **cost:** About $0.01–$0.06 per meeting, dominated by summarizing several notes/messages; reminder and draft creation are deterministic.
- **security:** Meeting notes, mail, and private tabs may contain sensitive information. Keep source content on the Mac, pass only bounded excerpts to the model, preserve citations and confidence, and never send follow-ups automatically. Require review for every external draft.
- **missing:** A unified meeting-time correlation across Calendar, Notes, Mail, and browser tabs; A structured decision/action extractor with source spans and owner attribution; A Mac writer that creates grouped reminders and review-only drafts with provenance

### "“Make a safe-to-share version of this private page and put it in my project.”"
- **useful because:** The owner can turn sensitive authenticated material into a redacted artifact without manually hunting for passwords, account numbers, tokens, or personal details. The browser provides the private source, a background model proposes redactions with highlighted evidence, the Mac writes a separate version, and the pendant reads a short disclosure summary before any sharing step.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-terminal → faculty-perception → faculty-action
- **model tier:** Cheap background model for candidate entity detection and redaction suggestions; deterministic pattern scanners for credentials and identifiers; realtime only for the owner’s request and disclosure recap.
- **latency:** Candidate scan in under 8 seconds for a normal page; redacted artifact and side-by-side change list under 20 seconds.
- **cost:** About $0.005–$0.04 per artifact; local deterministic scanning should handle most secrets and keep model usage low.
- **security:** The unredacted source must remain local. Never upload raw page contents by default. Write a separate output, preserve a non-sensitive source hash, show every proposed removal, and require explicit approval before export or sharing. False negatives must be called out rather than implied safe.
- **missing:** A local redaction scanner for browser text and screenshots; A provenance-preserving artifact/diff writer; A share-safety policy that distinguishes local save, clipboard, email attachment, and external upload


## Changes it proposed to its own stack

### `integration` — Add an action-proof bridge that correlates every cross-surface operation into one human-readable timeline: spoken intent, evidence gathered from each private tab, exact proposed mutations, pendant confirmation event (or explicit refusal), execution result, and undo/receipt links. Render the timeline as a local review card and make the relay able to answer “what did you actually do?” without rerunning the Mac or browser.
- **owner gets:** After delegating a real-world task, the owner can trust and audit it in seconds instead of reconstructing scattered browser tabs, Mac logs, and voice turns. It also makes failures actionable: they see whether the problem was missing evidence, no confirmation, a dropped device, or a rejected submit.
- effort: Medium: define an append-only operation schema, adapters for browser results, Mac jobs, relay turns, and pendant events, plus a compact local UI/voice renderer.  ·  risk: Incorrect correlation could mix two similar jobs; use cryptographic operation IDs, explicit parent/child jobs, and never claim completion without a receipt. Recover by showing ‘unknown/unverified’ and linking raw evidence rather than guessing.
- cost: Low storage and near-zero inference cost; optional summarization can use the cheap background tier. No new per-action model call required.  ·  latency: No impact on execution; timeline writes are asynchronous. Voice lookup should return in under 1 second from relay storage.
- security: The timeline contains sensitive URLs and values. Encrypt at rest, redact secrets/payment fields, enforce per-owner authorization, and offer per-operation deletion.
- depends on: A stable cross-surface operation ID propagated through POST /execute, browser jobs, and relay jobs; The pending physical confirmation protocol from the transaction capability

### `interaction` — Add a pendant-led interruption and resumption contract for delegated work: every long-running Mac/browser operation publishes a compact next-step capsule (goal, current checkpoint, required owner input, expiry, and safe cancellation state). A button gesture or spoken “resume that” retrieves the capsule and resumes only from the last verified checkpoint, rather than replaying earlier actions.
- **owner gets:** The owner can walk away from a task, return hours later, and continue without remembering which tab, form, or step was in progress. The pendant communicates waiting/error/completed states without opening the Mac, while stale or ambiguous work stops safely instead of silently repeating an action.
- effort: High: define checkpoint semantics across browser and Mac jobs, persist capsules in the relay, implement pendant status gestures, and make every executor idempotent at checkpoint boundaries.  ·  risk: A bad checkpoint could skip a prerequisite or duplicate a mutation. Require explicit checkpoint receipts, short leases for irreversible steps, and default to reopening for review when proof is missing. Recovery is a visible paused state with raw job links.
- cost: Small durable-state cost; background summarization is optional and inexpensive. No realtime model call is needed for status or resume routing.  ·  latency: Button acknowledgement under 200 ms; resume decision under 2 seconds; no added latency to ordinary actions.
- security: Capsules may reveal private task names and URLs. Encrypt relay storage, minimize contents, expire them, and require the same owner/device pairing for resume.
- depends on: A stable operation/checkpoint identifier shared by Mac jobs, browser sessions, and relay state; A pendant event channel and local status/acknowledgement protocol; Idempotent browser and Mac execution at checkpoint boundaries


## What it asked for

_Nothing._
