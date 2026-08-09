# Harness derivation — ios-control — round 8

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Continue what I’m looking at on my iPhone on my Mac.”"
- **useful because:** This turns the phone into a real second node rather than a remote-control toy: the owner can inspect a message, article, map, or form on the phone and continue on the larger Mac without manually finding the same state again.
- **path:** pendant → relay → mac-planner → iOS → browser → dashboard
- **model tier:** gpt-5.6-luna for the one-time semantic handoff; gpt-4.1-mini for OCR/normalization and matching, with no realtime model on ambient polling
- **latency:** 2–5 seconds after the owner says it; ambient iPhone reading remains event-triggered and capped, not continuous upload
- **cost:** About $0.01–$0.04 per handoff; dominant cost is one multimodal/semantic matching call, not OCR or the event plumbing
- **security:** Only an explicit pendant request exports a capped OCR/accessibility capsule (app name, title, visible text, URL when available); redact passwords, payment fields, message bodies by default. Opening a matched private page is allowed, but sending/submitting anything still requires confirmation.
- **missing:** A Mac-local iPhone ambient-inspect adapter that can return OCR plus app/window metadata without touching the screen; A cross-surface handoff schema with confidence and a user-visible preview; App-specific URL/deep-link resolvers for maps, messages, and document apps

### "“Use my iPhone as the final confirmation for this.”"
- **useful because:** A physical, visual approval on the owner's phone is much safer than accepting a spoken yes for purchases, messages, account changes, or destructive Mac actions—especially when the pendant is being used hands-free.
- **path:** pendant → relay → mac-planner → iOS → dashboard
- **model tier:** gpt-5.6-luna plans and summarizes the pending operation; deterministic Mac/iOS harness performs the approval challenge; realtime only speaks the short request
- **latency:** Under 3 seconds to show the challenge once mirroring is frontmost; wait indefinitely (with expiry) for the owner to tap the matching approve/reject control
- **cost:** Roughly $0.005–$0.02 per approval, mostly one planning/summarization call; iOS capture and button matching are local
- **security:** Challenge must bind operation hash, target, amount/recipient, expiry, and device session; never infer approval from a screen change or a phone pickup. If mirroring is paused, locked, or not frontmost, fail closed and keep the operation pending. Destructive operations require this by policy.
- **missing:** A signed iOS approval challenge protocol between relay and Mac-local mirror; A reliable frontmost-window lease and a semantic button target instead of raw coordinates; Operation hash display/verification and replay protection

### "“Tell me what needs my attention on my phone, but don’t interrupt me unless it’s important.”"
- **useful because:** The system can turn a phone that is otherwise isolated behind a locked or paused mirror into a quiet triage channel: surface only urgent, actionable items during a pendant conversation or a scheduled check, instead of reading every notification aloud.
- **path:** iOS → mac-planner → relay → pendant → dashboard
- **model tier:** gpt-4.1-mini class OCR/classification for a local, capped queue; gpt-5.6-luna only when the owner asks for a decision or reply; realtime speaks at most one short alert
- **latency:** Event-driven checks in 1–2 seconds when the mirror is live; no overnight promise while Mac is locked or mirroring is paused. Queue and summarize on next reconnect.
- **cost:** Under $0.01 per triage batch; local OCR and notification deduplication dominate reliability, not model spend
- **security:** Keep content on the Mac unless urgency threshold is met; redact message previews and health/financial text by default. Never auto-open, reply, call, or dismiss. Owner-configured allowlist determines apps and urgency.
- **missing:** A local iPhone notification/app-state observer that emits only hashed titles and opt-in snippets; A durable offline queue that records last-seen fingerprints across mirror pauses; Owner-configurable urgency policy and quiet-hours integration

### "“Move the verification code from my iPhone into the form on my Mac, but show me exactly what you’re moving first.”"
- **useful because:** This eliminates the most irritating two-device task—switching between a phone authenticator/message and a desktop login—while preserving a clear privacy boundary and preventing the agent from guessing which six-digit string is intended.
- **path:** iOS → mac-planner → browser → relay → pendant
- **model tier:** gpt-4.1-mini performs local OCR and candidate extraction; gpt-5.6-luna resolves which candidate and destination field only after the owner’s spoken request; realtime reads a one-sentence preview
- **latency:** 1–3 seconds to present candidates; owner confirmation before insertion; no background polling
- **cost:** $0.005–$0.02 per transfer, dominated by one semantic disambiguation call
- **security:** Treat codes as secrets: never persist, never send to general memory, redact from logs/audio, expire after one use, and require an exact preview (“482913 into example.com’s code field”). Refuse if destination origin or field is uncertain.
- **missing:** A one-shot, Mac-local iPhone OCR capsule API with field redaction; A browser field identity/fingerprint returned before insertion; An ephemeral secret channel from iOS node to browser executor

### "“When I pick up my phone, pause anything that could act on it; when I put it down, tell me what is waiting and ask whether to resume.”"
- **useful because:** The owner can use the phone normally without racing an automation. The system turns Mirroring’s real-world pause into a safe handoff: pending actions remain understandable and resumable instead of timing out or acting on stale UI.
- **path:** iOS → mac-planner → relay → pendant → dashboard
- **model tier:** Deterministic lease/state machine handles pickup, pause, and resume; gpt-4.1-mini summarizes the queue; realtime only announces the short status
- **latency:** Pause within 250 ms of mirror-state change; spoken resume summary within 2 seconds after reconnect; queued work can expire safely
- **cost:** Near-zero model cost for state changes; under $0.01 when summarization is needed
- **security:** Pause is fail-closed and cannot be overridden by voice alone for destructive actions. Resume requires a fresh screenshot/fingerprint and explicit confirmation if the UI changed. Store only operation metadata, not phone screen contents.
- **missing:** A reliable mirror-pickup/owner-present event distinct from generic window focus; An interruption-safe operation journal with UI fingerprints and resumable boundaries; Relay delivery of pause/resume events independent of mac-planner

### "“Make a private phone-to-Mac handoff of this conversation: extract the decision, the people, and my next action, then put the draft in my notes without sending anything.”"
- **useful because:** A phone conversation can become useful work without forwarding a whole private thread or asking the owner to retype it. The owner gets a structured, reviewable draft on the Mac while the original messages stay on the phone.
- **path:** iOS → relay → mac-planner → browser → pendant → dashboard
- **model tier:** gpt-4.1-mini does local OCR/structure extraction; gpt-5.6-luna turns the selected capsule into a concise decision/next-action draft; no realtime reasoning beyond confirmation
- **latency:** 5 seconds for a selected screen or bounded scroll range; owner reviews the draft before it is saved
- **cost:** $0.01–$0.04 per handoff, dominated by structured summarization
- **security:** Only an explicit selection/request exports a bounded region; redact phone numbers, tokens, and unrelated messages; retain source text ephemerally with automatic deletion. Saving a note is allowed under owner policy; sending it is never implicit.
- **missing:** A selection-scoped iPhone capture mode (not whole-screen ambient streaming); A privacy classifier that can redact unrelated message rows before relay upload; A draft artifact route with source provenance and expiry


## Changes it proposed to its own stack

### `new-surface` — Create an iOS-mirror sidecar on the Mac as a first-class relay node. It owns the Mirroring window capture/event posting, maintains a signed lease and frontmost/locked/paused state, emits explicit inspect snapshots and approval results directly to the relay, and accepts only nonce-bound commands. mac-planner may request work, but the relay can address this node independently and receive a result without routing through the planner.
- **owner gets:** The owner gets dependable phone-aware help and honest status: “your phone is paused because you picked it up,” “I can read it but cannot tap while it is in the background,” or “approval completed.” Phone context can participate in a pendant conversation even when the Mac planner is busy.
- effort: Medium-high: local daemon plus relay registration, signed leases, snapshot redaction, and frontmost safety state machine; then a small dashboard/debug view.  ·  risk: A stale lease or replayed command could drive the wrong app. Fail closed on lock, pause, missing pixels, stale nonce, or non-frontmost state; require operation hash and expiry for every mutation. Recover by dropping the lease and requiring a fresh inspect.
- cost: Negligible API cost for event transport; roughly one local process and small D1 lease/event records. OCR/model calls remain on demand.  ·  latency: Ambient state under 250 ms locally; relay round trip typically under 1 s. Frontmost acquisition still takes human-visible time and must not be hidden.
- security: Improves isolation by making iOS a separately authenticated capability boundary; only redacted snapshots leave the Mac, and mutation commands are nonce-bound and auditable.
- depends on: A real Mac-local iPhone Mirroring capture/event adapter (currently no ios_* production tool is exposed); Relay device registration and signed lease verification; A frontmost-window arbiter shared with mac-vision/mac-planner

### `mac-harness` — Add a secret-safe cross-device transfer broker between the iPhone mirror and Safari. It accepts a single owner-authorized capture nonce, performs OCR locally, classifies candidate secrets, binds the chosen value to a browser origin and field fingerprint, injects it once, then cryptographically erases the value and evidence. The broker must never expose the raw code to relay logs, model context, clipboard history, or general Mac automation.
- **owner gets:** The owner can complete phone-mediated logins and confirmations hands-free without repeatedly switching windows, while knowing a one-time code cannot leak into the assistant’s memory or remain in the clipboard.
- effort: Medium: local privileged helper, Accessibility/browser field metadata, ephemeral memory handling, and audit tests across Mirroring pause/frontmost transitions.  ·  risk: Wrong-field injection or logging a secret is catastrophic. Require exact origin match, visible preview, one-use nonce, 30-second expiry, fail closed on ambiguous OCR or stale UI, and provide no retry that reuses the value.
- cost: Minimal API/model cost; local OCR may use existing vision stack. Small memory-only helper and test harness are the primary engineering cost.  ·  latency: Adds roughly 0.5–2 seconds for local OCR and field verification; avoids repeated manual context switching.
- security: Strongly reduces secret exposure compared with clipboard-based workflows, but requires careful TCC/Accessibility permission and zeroization validation.
- depends on: Mac-local iPhone Mirroring capture adapter; Browser field fingerprint/origin inspection; Owner-facing confirmation surface on pendant or iPhone


## What it asked for

_Nothing._
## Its own summary

Round 8 produced three new iPhone capabilities and one architectural change. The highest-value is explicit phone-to-Mac continuation: an owner request creates a redacted, confidence-scored iPhone context capsule and opens/resumes the matching Mac page. I also recorded iPhone-backed cryptographic confirmation for high-risk actions and quiet phone triage, plus the key change: make iPhone Mirroring a signed, relay-addressable Mac-local node with its own lease/state machine rather than a planner-only facet. The existing surface inventory confirms there is still no production ios_* tool, while the phone is offline as a device record and the Mac bridge is online.

**Biggest unknown:** The exact Mac-local Mirroring capture/event primitive and whether the current harness can expose it without adding a sidecar. I still need that adapter, a frontmost/locked/paused lease signal, and relay device registration with nonce-bound commands. No new grant appeared in the granted inventory this round; the previously requested ios inspection capability remains unresolved.

