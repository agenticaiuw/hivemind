# Harness derivation — mac-planner — round 190

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Don't speak over my meetings or presentations. If a pendant reply arrives while my calendar says I'm busy or the Mac is in a call, hold it, summarize urgency, and play it automatically at the first safe boundary or let me request it immediately."
- **useful because:** Today a generated reply can arrive at the worst possible moment, while a generic unread queue does not know whether the owner is presenting, in a call, or merely reading. This coordinates calendar, foreground/browser evidence, relay timing, and the pendant's existing inbox into a genuinely context-sensitive interruption policy.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension
- **model tier:** Cheap classifier/background worker for busy-state and urgency; realtime model only when the owner asks to hear or act on a held item.
- **latency:** Busy-state refresh within 2 s; no more than 300 ms added once a safe boundary is detected; immediate override begins within 1 s.
- **cost:** Near-zero for calendar/foreground polling and metadata; <$0.01 only when a long held response needs summarization or speech regeneration.
- **security:** Calendar titles, call state, and active tab metadata leave the Mac only as redacted policy facts (busy/free, app class, urgency); never transmit meeting content unless explicitly requested. A local privacy latch suppresses both microphone and playback.
- **missing:** A Mac-side call/presentation detector that combines calendar state, foreground app and browser tab metadata; Relay policy fields for defer-until, urgency, expiry, and immediate-override; A safe-boundary event from Mac to relay and a playback lease so two surfaces cannot speak simultaneously

### "When I short-press the pendant while looking at something on my Mac, save a private, timestamped context card containing the active app, browser tab, selected text or document path, and my bookmark label; later let me say 'do the thing I marked' and carry it out with a receipt."
- **useful because:** A moment bookmark currently records that something happened, but not what the owner was looking at. This turns a no-speech gesture into a reliable handoff from wearable attention to desktop action, useful when speaking would be awkward or the owner cannot stop to explain.
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay-realtime
- **model tier:** No model for capture; cheap background extraction/redaction; realtime only to resolve the later spoken reference and plan ambiguous actions.
- **latency:** Card acknowledgement under 300 ms; context capture under 2 s; later retrieval and plan under 3 s before execution.
- **cost:** Minimal storage and metadata cost; <$0.01–$0.03 for later language resolution, with action execution itself local.
- **security:** Selected text and URLs can contain secrets. Redact password fields and token-like strings locally, encrypt cards at rest, expire by default, and require the owner's existing action policy for mutations. Never capture microphone audio unless the existing opt-in memo path is active.
- **missing:** A real Mac semantic-context reader for selected text, document identity, and browser frame rather than only generic UI snapshots; A bookmark correlation protocol carrying the pendant event id into the Mac observation; A spoken-reference resolver and action receipt that can reopen the exact captured context without stale-tab surprises

### "After you change something in my browser on my behalf, tell me exactly what changed and give me a one-step way to undo it; for multi-page work, keep a before/after evidence bundle instead of just saying 'done'."
- **useful because:** A job receipt says an action completed but does not prove the resulting page state or make browser-side mutations easy to audit. This gives the owner a trustworthy spoken diff and a bounded recovery path across authenticated browser sessions, the Mac executor, and the pendant.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant
- **model tier:** Deterministic DOM/accessibility diff and URL/form-state capture first; cheap summarizer for the spoken sentence; realtime only for ambiguous follow-up or an undo request.
- **latency:** Capture before-state without delaying a simple action by more than 500 ms; after-state and receipt within 3 s; undo starts within 1 s.
- **cost:** Low: local snapshots and hashes dominate storage; <$0.01 per multi-page summary, no model call for unchanged/read-only pages.
- **security:** Authenticated pages may expose personal or financial data. Store redacted structural diffs and hashes by default, encrypt evidence, omit passwords/tokens, apply short retention, and never speak sensitive values aloud unless explicitly requested. Undo must target the exact session and page version, not blindly replay clicks.
- **missing:** Browser bridge support for deterministic before/after snapshots and semantic mutation diffs; A mutation-specific inverse plan or browser transaction journal for actions that are not naturally reversible; Relay speech payload and pendant acknowledgement tied to the receipt id

### "Why did you tell me that, and what exactly did you use? Give me a concise spoken provenance trail linking the pendant moment, Mac or browser evidence, relay reasoning, and the action receipt; let me inspect or revoke any source afterward."
- **useful because:** The owner currently receives answers and desktop actions without a unified, human-readable chain of evidence across nodes. A provenance trail would make the hive trustworthy: it distinguishes observed facts from inference, exposes stale or missing sources, and lets the owner revoke a captured browser or calendar source without deleting unrelated history.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Deterministic event/provenance graph construction and source hashing; use a cheap summarizer for the spoken explanation, reserving realtime only for follow-up questions during an active conversation.
- **latency:** Attach provenance asynchronously without delaying ordinary responses; spoken explanation under 2 seconds for a small chain and under 5 seconds for a multi-node chain.
- **cost:** Low storage and hashing overhead; typically <$0.01 for a generated spoken explanation, with no model call when the owner only opens the structured trace.
- **security:** A provenance graph can itself reveal sensitive calendar titles, URLs, mail subjects, and voice-event timing. Store redacted typed facts plus encrypted source pointers, enforce per-source retention and revocation, never expose bearer tokens or raw audio, and require explicit owner intent before reading sensitive source details aloud.
- **missing:** A cross-node provenance envelope with immutable event ids, timestamps, source classifications, confidence, and transformation links; Relay APIs to answer provenance queries and revoke or tombstone a specific source contribution without corrupting the resulting audit history; Mac/browser adapters that attach redacted evidence hashes and action receipts to the same envelope; A pendant response format for a short spoken explanation plus an optional dashboard detail view

### "Before you act across my Mac and authenticated browser, tell me in one short spoken preview which resources will change, what cannot be undone, and what evidence will prove success; then let me say 'go' or revise the plan."
- **useful because:** The current Mac preflight does not cover browser-side effects or explain a single cross-node plan in owner language. A unified preview would let the owner understand a desktop-plus-browser action before it crosses an authenticated session, without requiring them to inspect technical receipts.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Deterministic resource and reversibility classification first; cheap model for the short spoken rendering; realtime only for the owner's confirmation dialogue.
- **latency:** Preview under 2 seconds for ordinary plans; confirmation must bind to the exact plan hash and expire after 2 minutes.
- **cost:** Low: local classification and hashing dominate; <$0.01 for a spoken preview, with no model cost for unchanged plan templates.
- **security:** Previews must not leak page contents or secrets; use resource classes and redacted labels. Bind confirmation to plan hash, browser session, page version, and destination. Never treat a stale confirmation as authorization.
- **missing:** Browser-side deterministic preflight with touched resources, reversibility, and exact plan hash; A relay-level cross-node plan composer joining Mac and browser actions; Pendant confirmation protocol and durable plan receipt that survives a dropped link; Dashboard rendering of the same preview and final evidence

### "For a small set of actions I choose—such as sending a message, publishing, or placing an order—use a physical press on my pendant as the final proof that I am present, showing me the exact target and amount on the Mac first."
- **useful because:** A spoken confirmation can be triggered accidentally or become ambiguous while the owner is multitasking. A deliberate physical gesture on the worn device provides a distinct presence signal while the Mac/browser supplies the detailed preview, making high-consequence actions safer without requiring the owner to reach for the keyboard.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Deterministic policy and exact-plan hash binding; no model needed for authorization, with realtime used only to explain a rejected or expired approval.
- **latency:** The approval request should reach the pendant within 1 second; a button press should authorize or reject within 500 ms; approval expires after a short configurable interval.
- **cost:** Negligible inference cost; implementation is protocol, firmware state, browser integration, and audit storage.
- **security:** The pendant must not approve a changed plan or stale browser page. Bind approval to a cryptographic plan hash, target/session/page version, and expiry; show a compact LED/state code and speak details through the Mac or pendant; preserve a tamper-evident receipt. Owner must explicitly select which action classes use this mechanism.
- **missing:** A firmware approval state machine using the existing button and LED without interfering with recording/bookmark semantics; Authenticated USB/LTE challenge-response between pendant, relay, Mac, and browser; Owner-configurable action classes and a browser/Mac enforcement hook that refuses execution without the matching physical approval


## Changes it proposed to its own stack

### `browser-harness` — Add a mutation journal around browser commands: capture a redacted structural before-state, command id/session/page version, after-state hash and a typed inverse descriptor when one exists; expose the compact diff and inverse token through the existing browser result and job receipt routes.
- **owner gets:** When the agent changes an authenticated page, the owner can hear what actually changed and recover from the exact transaction instead of trusting an opaque 'done'.
- effort: Medium: browser bridge snapshots, redaction, page-version checks, and inverse handlers for a small allowlisted set of mutations.  ·  risk: Snapshots can leak page data and inverse handlers can be wrong on dynamic sites. Default to hashes/labels, short retention, refuse undo when page version changed, and keep the current action as completed if journaling fails.
- cost: Low storage and CPU; occasional small summarization call only when the owner requests a spoken diff.  ·  latency: Adds up to 300–500 ms before and 1–2 s after a mutating browser command.
- security: Improves auditability but creates sensitive evidence; encrypt, redact secrets, scope by browser session, and never include bearer tokens or password fields.
- depends on: Browser bridge must expose stable page/session identifiers and a redacted structural snapshot; Owner-configured retention for evidence and inverse tokens


## What it asked for

_Nothing._
