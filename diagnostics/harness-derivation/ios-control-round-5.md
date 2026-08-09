# Harness derivation — ios-control — round 5

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Tell me what on my iPhone needs my attention, and handle the safe parts.”"
- **useful because:** The pendant becomes a genuinely independent iPhone sentinel: it can passively inspect the mirrored phone when available, distinguish urgent notifications from noise, and let the owner deal with only the items that matter while commuting or working. Safe operations (opening a thread, marking read, adding a reminder) can happen without a long spoken workflow; sending messages or other consequential actions still require explicit confirmation.
- **path:** pendant → relay → mac-bridge → iOS → dashboard
- **model tier:** relay-realtime for the short spoken interaction; mac-vision/gpt-4.1-mini for OCR and stable UI classification; mac-planner/gpt-5.6-luna only for ambiguous multi-step actions; background relay summarization should use a cheaper scheduled model.
- **latency:** Ambient scan 1–2 s when mirroring is already visible; 3–8 s if Mac must bring the mirror frontmost and capture; pause cleanly when the phone is picked up, Mac is locked, or mirroring has no pixels.
- **cost:** About $0.005–$0.03 per explicit scan depending on OCR/model retries; ambient scans should be local OCR and event-triggered, not continuous cloud inference.
- **security:** Notification text and screenshots contain private data and must remain on the Mac/relay only long enough to answer. Never infer permission to send, delete, purchase, or alter account settings. Require spoken confirmation for outbound or destructive actions and return an auditable receipt.
- **missing:** A real ios_mirroring_inspect/read-only tool exposed to the Mac harness (screen capture by mirroring window id plus Vision OCR); A Mac-local ios action adapter that reports why an action refused (not frontmost, locked, or mirroring paused); A relay event schema for notification candidates and action receipts, with deduplication so the same notification is not announced repeatedly

### "“Do the thing I asked on my iPhone, but only if you can prove it worked.”"
- **useful because:** This gives the owner reliable phone automation instead of blind tapping: the system captures the pre-state, performs a foreground-only iOS action, captures the post-state, compares the intended UI change, and speaks success or a precise blocked reason. It is especially valuable for reminders, calendar edits, and navigation started from the pendant, where a silent failure is worse than no action.
- **path:** pendant → relay → mac-bridge → iOS → dashboard
- **model tier:** gpt-5.6-luna for intent decomposition and confirmation policy; gpt-4.1-mini for before/after OCR and visual diff; realtime only to collect confirmation and report the receipt.
- **latency:** 5–12 s for a normal one-screen action; up to 20 s for a multi-screen flow. Refuse rather than wait indefinitely if the Mac is locked, the owner picked up the phone, or the mirror cannot be made frontmost.
- **cost:** Roughly $0.01–$0.06 per verified action, dominated by two captures and occasional planner retry; no model call is needed for a deterministic postcondition match.
- **security:** Screenshots may include messages, health, or financial content; redact and expire them after the receipt. The proof must be tied to a specific expected UI state, not merely an action-returned success flag. Sending, deleting, purchasing, or changing permissions always requires a fresh explicit confirmation immediately before execution.
- **missing:** An iOS action contract with precondition, concrete action, expected postcondition, timeout, and refusal reason; Frontmost-window arbitration so the Mac agent cannot steal focus from the owner's work without a visible/consented handoff; A durable signed-ish receipt linking request, captures, action result, and postcondition match

### "“Take whatever I’m looking at on my iPhone and make it useful later.”"
- **useful because:** A spoken “save this” turns the current iPhone screen into a durable, actionable handoff: extract the visible URL/title/contact/date, preserve a small evidence snippet, and create the right Mac-side note, reminder, or browser task. The owner no longer has to copy links or remember which app they saw something in. The later Mac/browser node can resume the exact page or task.
- **path:** iOS → pendant → relay → mac-bridge → browser → dashboard
- **model tier:** gpt-4.1-mini for OCR and field extraction; gpt-5.6-luna only when the screen is ambiguous or choosing between note/reminder/task; realtime for the one-sentence capture command and confirmation. Use a cheap background model to normalize titles and dates.
- **latency:** 2–4 s to acknowledge and capture the current mirrored screen; 5–15 s to create the handoff and optionally open it on the Mac. If mirroring is paused or the Mac is locked, cache the request and explain that capture is deferred rather than pretending it succeeded.
- **cost:** $0.005–$0.03 per capture, mostly OCR/normalization; browser resume is local and cheap.
- **security:** Do not upload raw screenshots by default; retain only extracted fields and a short encrypted evidence hash/snippet, with a user-visible delete action. Treat passwords, banking, health, and private messages as non-exportable unless the owner explicitly says to save them. Creating a reminder/note is allowed by the owner's policy, but sharing or sending anything requires confirmation.
- **missing:** A Mac-local read-only iOS screen/OCR adapter that can return the current app, URL, and confidence; A structured handoff object (source app, title, URL, entities, timestamp, confidence, retention) shared by relay, Mac, and browser; A browser resume action that consumes the handoff and verifies the destination before opening it

### "“Use my iPhone as the final approval for this, then finish it on the Mac.”"
- **useful because:** The owner can authorize a consequential Mac or browser action without speaking a sensitive confirmation aloud or hunting for a dialog: the pendant describes the pending action, the iPhone mirror presents a one-time approval card, and Face ID/tap approval releases the Mac/browser execution. This makes the phone a physically present, biometric approval node rather than merely another screen the Mac controls.
- **path:** pendant → relay → iOS → mac-bridge → browser → dashboard
- **model tier:** gpt-5.6-luna for action summary and policy classification; relay-realtime for the brief spoken request; deterministic local code for nonce generation, expiry, and approval binding. No model should decide that a biometric approval means consent to a different action.
- **latency:** Approval card in 2–5 s; execution and receipt in another 2–8 s. Expire the nonce after 60 s, cancel if the mirrored phone is picked up or the Mac locks, and require a fresh request after any material change.
- **cost:** Under $0.01 per approval beyond the underlying action; most work is local UI and cryptographic verification, with model cost only for summarizing an ambiguous action.
- **security:** Never treat an arbitrary tap or an OCR-visible Face ID prompt as proof by itself. Bind a signed, human-readable action hash, destination, account, and amount to a one-time nonce; show those fields on the phone; reject stale/replayed approvals; keep biometric data entirely in iOS. Destructive, financial, or outbound actions still need the owner's explicit approval, and the receipt must state exactly what was released.
- **missing:** A native or controlled iOS approval surface capable of displaying the canonical action summary and receiving a trustworthy Face ID-backed result; iPhone Mirroring alone cannot attest biometric identity; A relay approval protocol with nonce, action hash, expiry, cancellation, and replay protection; Mac/browser executors that accept only a verified approval token and return a post-execution receipt

### "“Move this call from my iPhone to my Mac, keep the context, and tell the other person only what I approve.”"
- **useful because:** The owner can start a call on the phone while away from the desk, then transfer it to the Mac when they sit down without losing the contact, notes, or intended follow-up. The pendant can capture a private action plan while the call is live, while the Mac handles the larger conversation view. It unifies a real-time phone surface with Mac execution without exposing private call audio to an unnecessary model.
- **path:** iOS → pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime only for owner-directed spoken capture and interruption; local deterministic routing for call handoff; gpt-5.6-luna afterward to turn the owner's private notes into a draft follow-up. Never transcribe or summarize the other party by default.
- **latency:** Handoff initiation under 3 s, with a visible progress state and cancel button; notes acknowledge under 1 s and can be finalized after the call.
- **cost:** Near-zero model cost for routing; optional post-call drafting costs roughly $0.01–$0.05 and should be opt-in.
- **security:** Call audio, contact identity, and notes are highly sensitive. Default to metadata-only handoff, require explicit opt-in before recording/transcription, do not send private pendant notes to the other caller, and require confirmation before sending any follow-up. Abort if the phone is picked up, locked, or the call state cannot be verified.
- **missing:** An iOS call-state and audio-route adapter with an officially supported handoff mechanism; OCR/taps cannot safely establish or transfer a call; A cross-node call-session object carrying contact, route, owner-private notes, and explicit recording consent; Mac audio routing and a verified post-handoff state/rollback path

### "“I had you doing something on my iPhone, picked it up, and lost the workflow—resume it safely.”"
- **useful because:** The owner gets durable, resumable phone workflows instead of starting over whenever iPhone Mirroring pauses. The system records the intended goal and last verified state, notices owner takeover, then re-observes after mirroring returns and asks only about conflicts. This is particularly valuable for long forms, itinerary changes, and multi-step setup where interruption is normal.
- **path:** pendant → relay → iOS → mac-bridge → dashboard
- **model tier:** Deterministic workflow state machine for checkpoints, leases, and conflict detection; gpt-4.1-mini for before/after screen matching; gpt-5.6-luna only to resolve a genuine semantic conflict. Realtime reports pause/resume in one short sentence.
- **latency:** Detect owner takeover or mirroring pause within 1–2 s; resume check within 3–6 s after pixels return. Never continue automatically after a changed screen or expired checkpoint.
- **cost:** Usually below $0.01 per resume because state matching is local; planner escalation is roughly $0.02–$0.06 only for ambiguous screens.
- **security:** Persist goals and minimal structured state, not raw private screenshots. Treat any owner interaction as an override; never replay taps based solely on stale coordinates. Expire sensitive checkpoints, require confirmation for changed recipients/amounts, and provide cancel/undo for every resumed workflow.
- **missing:** A durable iOS workflow/checkpoint protocol with semantic preconditions rather than coordinates; An owner-takeover signal from the mirroring bridge and a lease that is revoked immediately on that signal; A re-observation/postcondition adapter that can distinguish the same state from a changed form or account


## Changes it proposed to its own stack

### `integration` — Make ios-control a relay-addressable capability boundary rather than an internal mac-planner prompt: the relay sends a typed iOS observation or action request to the Mac bridge, the bridge executes only while the mirroring window is safely frontmost, and it returns a structured state (pixels available, owner using phone, Mac locked, refusal reason, OCR confidence, postcondition). Add leases so only one request can own foreground focus, plus receipts that the relay can speak directly to the owner.
- **owner gets:** They can ask the pendant about or act on their real phone without waiting for the Mac planner to reinterpret the request, and failures become honest (“your phone is in use” or “Mac is locked”) instead of silent. This is the concrete meaning of an independent iOS node despite the hardware remaining physically Mac-local.
- effort: Medium-high: define the typed protocol, add a bridge worker/queue and focus lease, wrap existing capture/event posting, and test paused mirroring, locked Mac, and owner foreground use.  ·  risk: Foreground theft could disrupt the owner's Mac or phone. Default to read-only, never steal focus without a visible lease/short timeout, and cancel on owner input. Recover by expiring the lease and returning the last known state; never retry a refused tap blindly.
- cost: Negligible runtime/API cost for local routing; modest model cost only for OCR/ambiguity. No new hardware required.  ·  latency: Adds ~100–500 ms relay/bridge overhead; action verification remains 5–12 s. Ambient read-only observation can remain near-local.
- security: Creates a new authenticated command path to the phone mirror. Bind requests to the owner's session, redact screenshots, expire evidence, log every action and receipt, and require confirmation for consequential operations.
- depends on: ios_mirroring_inspect/read-only capture tool grant (currently requested); typed iOS observation/action protocol in the Mac bridge; foreground focus lease and postcondition verifier; relay routing for a new iOS capability namespace


## What it asked for

_Nothing._
## Its own summary

Produced three distinct iPhone capabilities and one architectural change. The highest-value one is verified phone action: every iOS action gets a pre-state, foreground-safe execution, postcondition proof, and an honest receipt/refusal. Also proposed an attention triage sentinel and a “save what I’m looking at” cross-node handoff. The key architectural step is making ios-control relay-addressable while keeping capture/events Mac-local, with focus leases and owner-input cancellation. Still needed: the pending read-only ios_mirroring_inspect adapter, confirmed concrete ios_* action names in mac-planner, typed relay↔Mac iOS request/receipt schema, and focus arbitration. I notified mac-planner rather than re-requesting queued grants.

**Biggest unknown:** Whether the newly granted/implemented harness exposes any iOS read-only inspection or action adapter yet; the capability manifest still reports no granted tools, and the owner’s real mirroring state can change when the phone is picked up, the Mac locks, or the mirror loses pixels.

