# Harness derivation — ios-control — round 7

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Use my iPhone as a second pair of eyes: tell me what is on screen, and if I say do it, carry out the safe action.""
- **useful because:** Makes the phone a genuinely independent node: the relay can request an ambient screen observation without disturbing the owner, while any tap/type is explicitly gated on the Mirroring window being frontmost. It combines pendant voice, always-awake relay, Mac-local capture/event posting, and the browser/session context no other node can see.
- **path:** pendant → relay → mac-bridge → iOS → dashboard
- **model tier:** Realtime only for interpreting the owner's short request and selecting a typed iOS operation; OCR and policy checks should be deterministic/local, with a cheaper background model for summarizing longer screens.
- **latency:** Ambient read 1–2 s; frontmost action 2–5 s including an explicit confirmation; refuse immediately if Mac locked, Mirroring paused, or target is ambiguous.
- **cost:** Roughly one realtime turn for a voice request plus local capture/OCR; <$0.02 typical, dominated by model transcription/interpretation, not screenshots.
- **security:** Screen pixels and OCR may contain private messages, banking data, or tokens; keep captures ephemeral and redact before relay storage. Never tap/type off-Space. Require confirmation for sends, purchases, deletion, permissions, or external messages; expose an audit receipt.
- **missing:** A relay-addressable iOS node identity and event protocol; Mac-local ios_mirroring_inspect plus frontmost-safe tap/type/swipe actions; Vision OCR and structured screen target extraction; Policy/approval adapter connecting /prepare and /approve to iOS execution

### ""When I start something on my phone, keep it alive while I walk away, and tell me when it can continue or needs me.""
- **useful because:** Bridges the real Mirroring failure modes instead of pretending the phone is always controllable. The relay records a resumable intent from pendant voice, the Mac watches ambient screen state, and interruption (owner picks up phone, Mac locks, or Mirroring disappears) pauses safely and resumes only when the screen is available again.
- **path:** pendant → relay → mac-bridge → iOS → dashboard
- **model tier:** Cheap background model classifies screen checkpoints and produces a short resume prompt; realtime model only handles the owner's initial intent and interruption dialogue.
- **latency:** Checkpoint within 3 s of a screen change; interruption detection under 5 s; no action while unavailable. Resume confirmation under 10 s after Mirroring returns.
- **cost:** <$0.01 per task if OCR/state diffs stay local; occasional background summarization dominates, with no continuous realtime calls.
- **security:** Persist only an encrypted task state (app, step, redacted fields), never full screenshots by default. Do not replay text or submit forms after an interruption without reconfirming. Lock/owner-presence changes invalidate approvals.
- **missing:** Mac-local Mirroring availability/pause/lock event stream; Typed iOS task checkpoint schema and idempotent resume executor; Relay queue with expiry and owner-presence/approval binding; A small dashboard showing paused reason and next safe step

### ""Before anything sensitive happens on my Mac or phone, show me exactly what will happen on my iPhone and let me approve it there.""
- **useful because:** Creates a cross-surface safety primitive no single node can provide: pendant voice initiates, relay freezes a signed transaction, Mac planner prepares it, and the iPhone Mirroring window displays a human-readable preview. Approval is a deliberate phone action while the Mac remains the only executor, with an auditable receipt and expiry.
- **path:** pendant → relay → mac-bridge → iOS → dashboard
- **model tier:** Realtime model extracts intent; deterministic renderer creates the preview and risk classification; background model can explain unusual permissions but must not decide approval.
- **latency:** Preview in 3 s; owner approval in their own time; execution starts within 2 s of approval and aborts on stale screen/session.
- **cost:** <$0.02 per approval, mostly one realtime interpretation; local UI rendering and receipts are negligible.
- **security:** Bind approval cryptographically to exact action, parameters, target account, and expiry; reject replay or changed UI. Treat phone screen as untrusted presentation until verified by Mac harness. Never display secrets unnecessarily; require a second confirmation for irreversible actions.
- **missing:** iOS Mirroring UI renderer and a safe frontmost interaction driver; Signed prepare/approve token shared between relay and Mac harness; A transaction diff format covering Mac and iOS actions; Approval receipts exposed in dashboard and /jobs/:jobId/receipts

### ""Give me a private, spoken triage of the notifications waiting on my iPhone, and let me dismiss or defer only the ones I explicitly name.""
- **useful because:** Today the owner must pick up the phone and inspect notifications one by one. This would turn the iPhone into a relay-connected inbox: Mirroring supplies the current notification surface, the relay creates a short urgency/topic digest, and the pendant lets the owner deal with one named item without exposing the whole phone screen or taking over the phone. It is deliberately a notification workflow, not general phone control or task resumption.
- **path:** pendant → relay → mac-bridge → iOS → dashboard
- **model tier:** Use deterministic local OCR and notification grouping first; use a cheaper background model for topic and urgency labels. Realtime is reserved for the owner's short spoken selection and confirmation.
- **latency:** Initial digest in 3–5 seconds; each explicitly named dismiss/defer operation in under 5 seconds. If Mirroring is paused, return the cached digest age and refuse mutation.
- **cost:** About $0.005–$0.02 per digest depending on OCR/model use; most work is local screen capture and grouping. No continuous realtime session is needed.
- **security:** Notifications can contain message previews, health data, and one-time codes. Keep raw pixels local and ephemeral, redact codes and message bodies before relay storage, and speak only sender/topic by default. Dismiss/defer must be item-ID-bound, confirmed, and auditable; never open a notification or send a reply implicitly.
- **missing:** A notification-specific iOS screen parser that tracks stable item IDs across refreshes; A local encrypted short-lived notification index shared with the relay; Safe named-item dismiss/defer operations with frontmost and freshness checks; A privacy policy for spoken notification summaries and one-time-code redaction

### ""Tell me, through the pendant, whether my iPhone is reachable, silenced, in Focus, low on battery, or likely to miss an important call—without making me pick it up.""
- **useful because:** The owner currently has no dependable ambient answer about phone availability while it is in a pocket or bag. A small iOS status witness would let the relay combine phone state with Mac and pendant presence and answer practical questions before the owner misses a call or assumes a message was delivered. This is read-only status telemetry, not screen automation.
- **path:** pendant → relay → mac-bridge → iOS → dashboard
- **model tier:** No realtime model needed for collection; deterministic state normalization and a cheap background model only for human-friendly explanations. Realtime handles an on-demand spoken query.
- **latency:** On-demand answer within 2 seconds from a fresh observation; stale state must be labeled with its age. Optional event alerts should be rate-limited and quiet by default.
- **cost:** Near-zero API cost for local state collection; under $0.005 for occasional natural-language explanation.
- **security:** Treat notification previews, contact names, location, and Focus state as private. Publish coarse booleans and age rather than raw screen data; encrypt telemetry, retain briefly, and require explicit opt-in for proactive alerts.
- **missing:** iOS status extraction for battery, reachability, ringer/silent, Focus, and call availability; Relay device-state schema and freshness/heartbeat handling; A user-configurable alert policy with quiet hours; A Mac-local observer that can read status while Mirroring is ambient

### ""If an iPhone screen has an icon or control I do not understand, explain what it is through the pendant, but do not touch it unless I ask.""
- **useful because:** OCR cannot interpret unlabeled icons, which leaves the owner stranded in unfamiliar apps or accessibility settings. A dedicated visual-explanation mode would combine the Mirroring pixels with app/context clues, speak a concise explanation, and preserve a strict read-only boundary. It is useful even when the owner is holding the phone and Mirroring cannot safely act.
- **path:** pendant → relay → mac-bridge → iOS → dashboard
- **model tier:** Use a vision-capable model only on a cropped, owner-selected region; a cheaper model handles wording and confidence. Realtime is appropriate for the short question, but no model should be allowed to issue an action from this mode.
- **latency:** 3–6 seconds per explanation; return uncertainty rather than guessing. No background monitoring or unsolicited interpretation.
- **cost:** Approximately $0.01–$0.05 per cropped visual query, dominated by vision inference; local OCR and crop selection are negligible.
- **security:** Crops may contain private content. Process in memory, discard after the answer, avoid uploading the full screen, and visibly state when the model is uncertain. This mode must be capability-isolated from tap/type execution.
- **missing:** A crop/region selector addressed through the pendant or a safe Mac gesture; Vision inference route with image retention disabled; App/context metadata to disambiguate common icons; A strict read-only policy boundary preventing explanation requests from becoming actions


## Changes it proposed to its own stack

### `integration` — Install a signed Mac-local iOS companion daemon that owns the relay-facing `ios` node identity, subscribes to Mirroring window/screen availability, performs capture+OCR while ambient, and exposes a strict frontmost-only action broker. The relay addresses this node directly; mac-planner is only its local transport delegate, not the planner for every phone request.
- **owner gets:** The owner can ask the relay about or approve phone actions even when the main Mac planner is busy, without unsafe blind taps. It turns the phone from an accidental mirrored window into a dependable hive member while honestly refusing during lock, off-Space, or pickup pauses.
- effort: Medium-high: daemon, authenticated relay channel, window-id/OCR adapter, frontmost activation guard, typed action schema, receipts, and integration tests for lock/pause/owner pickup.  ·  risk: A daemon bug could mis-target a tap or leak screen content. Default to read-only, require a fresh frontmost proof and user approval for mutating actions, expire commands quickly, and retain only redacted OCR. Recovery is kill switch plus existing Mac job undo where available.
- cost: Negligible runtime API cost for local observation; <$0.02 for occasional realtime interpretation. Engineering cost is the main cost; no new hardware required.  ·  latency: Ambient observation 1–2 s; action 2–5 s due to frontmost proof and confirmation. Relay independence removes planner queue delay.
- security: Adds a new relay endpoint and device credential; use per-device keys, TLS, nonce-bound commands, and separate read/action scopes. Screen data must be ephemeral and redacted.
- depends on: ios_mirroring_inspect tool grant; Mac-local safe frontmost activation and event posting; Relay node registration/authentication; Signed prepare/approve transaction protocol


## What it asked for

_Nothing._
