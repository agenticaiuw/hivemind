# Harness derivation — mac-planner — round 284

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Test the whole pendant audio path now, without recording me, and tell me whether the microphone uplink and speaker downlink are healthy.”"
- **useful because:** The pendant is physically attached to this Mac today but unregistered with LTE. A synthetic, end-to-end bench test would turn ‘it seems connected’ into a timestamped answer, catching codec, USB/serial, relay pipeline, and playback regressions before the owner relies on it. It must exercise both directions while never opening the microphone or retaining owner audio.
- **path:** pendant → mac-planner → relay-realtime → dashboard
- **model tier:** background / deterministic harness; use realtime only to summarize an already-produced receipt
- **latency:** 30–90 seconds for the fixture and receipt; spoken summary under 2 seconds after completion
- **cost:** Negligible model cost; dominant cost is one synthetic pipeline run and a small receipt. No audio transcription or audio-model tokens.
- **security:** Only a firmware-generated test vector leaves the Mac. The command must refuse if the pendant is not in diagnostic mode, and must label every artifact synthetic. Do not use the live microphone, and expire raw fixture logs after the receipt is persisted.
- **missing:** A live, bounded USB diagnostic runner that can arm the existing audio_path_diagnostic_fixture and read its result with exit status and timestamps (the accepted serial diagnostic is read-only and does not provide this orchestration).; A relay command/receipt endpoint that correlates fixture sequence numbers with POST /pipeline/audio and POST /pipeline/events, then reports pass/fail thresholds.; A small dashboard card showing codec time, drops, underruns, alias rejection, and the exact firmware/profile used.

### "“Decide whether an incoming alert should reach me now, wait until a natural break, or be silently logged—and if you defer it, tell me exactly when it will surface.”"
- **useful because:** The owner should not have to manually maintain Quiet mode. The relay can combine urgency and expiry with the Mac's actual foreground app/browser activity and Calendar/Mail load, then use the pendant as the durable final delivery channel. This is a cross-node attention decision, not another inbox: it prevents a low-value interruption during a call while guaranteeing that a time-sensitive item is not lost.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → dashboard
- **model tier:** cheap background classifier for urgency and break prediction; realtime only when the owner asks “what did I miss?”
- **latency:** Under 3 seconds to classify a new alert; deferred delivery evaluated at calendar/event boundaries or at most every 60 seconds
- **cost:** Low: short structured context and alert text, not screenshots or full mail bodies. Mac and browser observations dominate latency, not model inference.
- **security:** Send only redacted app/domain/activity class (for example, ‘video call’), never page text or keystrokes, unless the owner explicitly enables content-aware triage. Calendar/Mail snippets stay local to the Mac agent. Every alert needs an expiry and an audit trail explaining why it was deferred.
- **missing:** A relay-side attention policy with explicit owner-configured urgency, quiet hours, expiry, and break sources; it must stop rather than guess when policy is empty.; A read-only semantic activity signal from the Mac beyond foreground-app names (meeting state, playback, presentation mode) and a browser signal that reports page class without content.; A device inbox extension carrying a scheduled-at timestamp and reason code, so the existing offline_alert_inbox can surface the item at the promised break rather than merely queueing it.

### "“Stage the email/form/file on my Mac, then wait; when I press the pendant’s button, complete exactly that staged send or submission and read me the receipt.”"
- **useful because:** This gives the owner a safe physical commit control while away from the keyboard: the Mac and browser can prepare a complex, logged action, but nothing irreversible happens until the owner makes an intentional button press on the device in their hand. It is genuinely cross-node—relay correlates the pendant event, browser preserves the authenticated session, and Mac executes the prepared plan—rather than a Mac shortcut with a remote trigger.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background model prepares and explains the plan; realtime only handles the button event and concise receipt
- **latency:** Plan preview under 5 seconds; physical commit-to-result under 10 seconds, with a 30-second expiry if the target page/session changes
- **cost:** Low to moderate: one plan call and a short result summary. Browser snapshots and app execution dominate; no continuous audio/model loop is needed.
- **security:** The staged plan must bind to exact target URL/account, action hash, and resource identifiers, and invalidate on DOM/session change. Never treat a stale button event as approval. Show a distinctive pending state on the pendant, require a second local cancel path, redact secrets from receipts, and record an append-only action receipt. The owner must explicitly configure which action classes may use physical commit; an empty policy must refuse.
- **missing:** A relay-addressable, authenticated pendant button-event channel while the device is USB-attached or eventually LTE-registered.; A prepare/commit Mac API that stores an immutable action hash and rejects altered or expired plans; current FULL_CONTROL_MODE has no approval gate.; A browser result contract that returns the submitted record/receipt rather than only a success boolean.; Firmware UI for ‘staged commit waiting’ distinct from ordinary unread alerts using the existing single LED patterns.

### "“Before you send, buy, delete, or publish anything, show me a faithful dry-run of the resulting world: the exact browser/API mutation, files changed, notifications generated, and what I could undo—then let me ask questions about that preview from the pendant.”"
- **useful because:** Today a plan preview describes actions, but it cannot show the cross-surface consequences. The owner needs to understand the effect of a complex operation before committing, especially when one request touches a logged-in browser, Mac files, and a relay job. This is a consequence simulator, not another approval prompt or action ledger.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** background deterministic diff engine for resource accounting; realtime model explains the already-computed diff conversationally
- **latency:** 5 seconds for local/browser read-only inspection and a preview; spoken follow-up under 1 second if it remains within the generated diff
- **cost:** Low-to-moderate; browser snapshots and file metadata dominate, with small model prompts. No page bodies or secrets need leave the Mac.
- **security:** Simulation must run in an isolated browser transaction or cloned request context and never rely on actually submitting then undoing. Redact tokens, passwords, and private page text. Mark effects that cannot be simulated (email delivery, third-party side effects) as uncertain rather than inventing reversibility.
- **missing:** A browser harness that can produce a deterministic mutation diff without submitting the form or changing the authenticated session.; A Mac resource-impact planner that maps each action to files, apps, URLs, notifications, and a reversibility class.; A shared consequence schema consumed by the pendant renderer and dashboard, including explicit unknown/irreversible effects.

### "“Find the best appointment or reservation that fits my real calendar, hold the top three options without committing, and ask me on the pendant which one to take before any booking is finalized.”"
- **useful because:** The owner currently has to shuttle between an authenticated booking site, Calendar, and a device for the final choice. A coordinated hold-and-compare workflow would do the tedious search while preserving agency at the point where a slot, fee, or cancellation policy becomes real. It needs all nodes because the browser owns the session, the Mac owns Calendar, the relay arbitrates expiry, and the pendant is the mobile decision surface.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** background model extracts availability and compares constraints; realtime only reads the short candidate list and captures the owner’s choice
- **latency:** Under 30 seconds to produce candidates; refresh holds every 60 seconds and warn at least 2 minutes before expiry
- **cost:** Moderate browser interaction cost; low model cost if pages are reduced to structured slot/policy records. Calendar read is local and bounded.
- **security:** Never book or pay during search. Bind each hold to the exact account, service, timezone, price, cancellation terms, and expiry. Treat a changed price or policy as a new decision. Do not expose authenticated page content to the relay beyond the structured candidates.
- **missing:** Browser primitives for temporary holds, expiry monitoring, and extracting cancellation/price terms as structured data.; A calendar constraint evaluator that understands travel/buffer time and conflicts across time zones, not just overlapping events.; An explicit owner-choice protocol that expires on stale candidates and speaks the exact final terms before booking.

### "“After I finish a web purchase, application, or support case, make me a tamper-evident proof packet containing what I submitted, the confirmation, relevant files, and the exact time—without saving passwords or full page history.”"
- **useful because:** The owner often needs evidence later but today must manually collect a confirmation page, downloaded receipt, email, and local files. A provenance packet would turn a fragile browser moment into a searchable, privacy-bounded record that can be handed to an accountant, employer, or support agent. The pendant can mark the moment; the browser and Mac can collect the authoritative artifacts; the relay can summarize and index them.
- **path:** pendant → browser-extension → mac-planner → relay-realtime → dashboard
- **model tier:** background extraction and hashing; realtime only answers where a packet is or reads a concise receipt
- **latency:** Create the packet within 10 seconds of the owner’s bookmark or browser completion; indexing can continue in the background
- **cost:** Low model cost; dominant cost is local hashing and bounded artifact collection. Store hashes and selected snippets by default, not raw pages.
- **security:** Use a local redaction policy before anything leaves the Mac. Exclude credentials, cookies, payment numbers, and unrelated tabs. Hash artifacts before upload, preserve source URL/account/time, encrypt the packet, and require explicit owner policy for sharing or retention.
- **missing:** A browser completion hook that emits a signed confirmation artifact and selected receipt fields rather than a mutable screenshot.; A Mac collector that atomically gathers only the declared downloads/files and computes hashes with a manifest.; A relay index and retrieval UI with retention, redaction, and export controls; the pendant bookmark event needs correlation to the browser transaction.


## What it asked for

_Nothing._
## Its own summary

This round produced three non-duplicate cross-node capabilities: (1) a synthetic, no-microphone end-to-end pendant audio bench test with correlated relay/Mac receipts; (2) attention-aware alert timing that predicts a natural break using Mac/browser context and guarantees expiry; and (3) a physical pendant-button commit for an exact, expiring staged Mac/browser submission. I also checked the live production tool list: there is no ios_* tool or route exposed to this agent, so iOS control remains generic Mac UI automation and is blocked by the owner's Accessibility/TCC decision. The new grants are not fully wired as named: mac_workbench_transaction currently resolves to a read-only handoff route, and mac_readonly_inspect is currently reported unresolved despite its intended schema.

**Biggest unknown:** Whether the relay has a real authenticated pendant-event ingress and whether the browser bridge can return durable submission receipts; neither is discoverable from this Mac agent's exposed tools. The audio bench feature additionally needs a bounded USB diagnostic runner, while semantic activity (meeting/presentation state) is still absent without Accessibility or a new Mac route.

