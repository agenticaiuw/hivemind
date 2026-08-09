# Harness derivation — faculty-perception — round 173

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac input reachability** — At 2026-08-08T03:23:30Z the Mac agent reports Accessibility and Screen Recording granted, inputReachability status verified, uiActionsWillReachTheScreen true, secureInput false, and host identity com.aipendant.agent with synthesized event probe successful. Browser extension online with 9-tab Safari session; relay reachable and Mac bridge online. No pendant appears in live device discovery.
  - evidence: GET /observe HTTP 200 and GET /ops/snapshot HTTP 200 at 2026-08-08T03:23Z

## Capabilities it proposed

### "When I say “do it, but make me confirm on the pendant,” prepare a sensitive Mac/browser action, show me exactly what will change, and execute only after my physical pendant press; if I cancel or the challenge expires, leave everything untouched."
- **useful because:** A voice transcript or cloud approval is easy to trigger accidentally. A physical press on the worn device gives the owner a deliberate, local second factor for purchases, messages, deletions, and account changes while still letting the Mac and browser do the work.
- **path:** relay-realtime → pendant → mac-planner → browser-extension → mac-vision → unified
- **model tier:** Realtime handles the short spoken challenge and confirmation; a cheaper local planner/vision model computes the preview and verifies post-state; relay stores only a short-lived challenge and result.
- **latency:** Preview in 2–5 seconds; confirmation window 30 seconds; execute within 2 seconds after the press.
- **cost:** Usually <$0.01 per invocation; vision/planning dominates, and no model call is needed for the physical confirmation itself.
- **security:** The relay must bind a one-time nonce to the intended action, account/session, and expiry; never accept a generic HTTP admin ack. The pendant must use a scoped device credential rather than the shipping admin-key WebSocket path. Require explicit confirmation for irreversible or external side effects; redact secrets from previews and receipts.
- **missing:** Pendant challenge/press event with nonce and replay protection; Relay endpoint that issues and verifies a short-lived confirmation challenge; Browser/Mac executor gate that refuses execution until verified; Device-auth correction for the pendant WebSocket

### "When I reconnect after being away, say “catch me up,” and give me an interactive, evidence-linked account of what happened: what the Mac changed, what the browser saw, what the relay delivered, what the pendant actually played, and which items still need me—then let me say “open that” or “undo that” against the exact evidence."
- **useful because:** Today a completed Mac job or relay delivery can be mistaken for something the owner heard, and the existing digest has bounded/count-based coverage. This turns absence recovery into a truthful conversation with drill-down and repair instead of a vague summary.
- **path:** pendant → relay-realtime → relay → mac-planner → browser-extension → mac-vision → unified
- **model tier:** A cheap background summarizer builds the index; Realtime is used only for the owner’s spoken query and follow-up. Deterministic status joins and evidence hashes, not an LLM, decide whether an item is heard, merely delivered, or unknown.
- **latency:** Initial index incrementally maintained; first spoken answer under 3 seconds after reconnect, evidence drill-down under 2 seconds.
- **cost:** <$0.005 for a normal catch-up turn; storage/indexing dominates, not inference.
- **security:** Never claim heard from socket bytes or Mac completion. Each item needs an immutable correlation ID, source/content hash, device playback event, and explicit unknown state. Sensitive browser evidence stays local and is revealed only on request; undo requires the existing reversible receipt and a second confirmation.
- **missing:** A durable cross-surface correlation/index beyond count-capped stores; Relay-to-Mac provenance bridge for browser reads and routine output; Pendant playback completion/interruption events (audio_delivery_ack_queue exists as the accepted firmware direction); A mounted evidence/provenance read route and owner-facing drill-down contract

### "While I am wearing the pendant, let me say “what am I looking at?” or “is this safe to click?” and get a grounded spoken answer about the exact foreground window or browser tab; if I say “click it,” use the same captured screen state, refuse if it changed, and tell me precisely what was done."
- **useful because:** With input reachability and Screen Recording now verified, the system can finally connect the owner’s physical voice to the actual screen rather than guessing from app names or stale browser metadata. State-bound action prevents clicking a different element after the page changes.
- **path:** pendant → relay-realtime → mac-vision → mac-planner → browser-extension → unified
- **model tier:** A fast vision model interprets one captured frame; a cheaper deterministic layer checks foreground app, tab identity, and screenshot hash before executing; Realtime only speaks the result.
- **latency:** Capture and answer in 1–3 seconds; action confirmation and state recheck in under 2 seconds.
- **cost:** About $0.01–$0.04 per visual turn depending on image size; deterministic state checks are negligible.
- **security:** Screen frames can contain passwords and private messages: process locally by default, redact known secret fields, and require explicit consent before cloud vision. Bind any click to a frame hash, window/tab ID, and short expiry; refuse on mismatch. Never infer a successful click without a post-state observation.
- **missing:** A production screen-capture/vision route that returns a content hash and redaction metadata; Frame-bound browser/Mac action precondition and postcondition checks; Pendant online audio/gesture path; currently device discovery shows no registered pendant; Owner policy for which apps may be sent to cloud vision

### "Let me set a physical-presence rule such as “Only let the system send messages, approve purchases, or expose private browser pages while I have explicitly unlocked the pendant.” A short press on the pendant should establish a time-limited possession lease; if the lease expires, the relay stops sensitive delivery, the Mac agent refuses the action, and the browser hides or freezes protected sessions until I unlock again."
- **useful because:** Today the Mac, browser, and relay can remain authorized independently, and a cloud job or stale browser session can continue even when the owner is no longer attending. This gives the owner one understandable physical boundary around the whole hive: no valid pendant possession, no high-consequence action or private reveal. It is stronger than a spoken confirmation because a remote transcript cannot satisfy it.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → unified
- **model tier:** No expensive model is needed for authorization. Realtime may explain a denial or ask the owner to unlock; deterministic policy code verifies the lease, action class, session binding, and expiry. A cheap background process audits leases and closes protected sessions.
- **latency:** Unlock acknowledgement under 300 ms locally; relay propagation and action gating under 1 second; expiry enforcement must be immediate on the next sensitive operation.
- **cost:** Negligible inference cost; a few hundred bytes of lease state and an occasional audit event per session dominate.
- **security:** The lease must be a signed, single-owner, short-lived capability bound to device identity, Mac/browser session, policy version, and a monotonic counter; replay, copied voice commands, and relay-admin HTTP acks must not unlock it. Default deny on stale or ambiguous state. Do not claim it proves the pendant is worn—it proves a recent deliberate possession gesture. Protect lease metadata from routine SD writes and keep only a bounded NVS record on the device.
- **missing:** A scoped pendant unlock event and monotonic anti-replay counter; the current pendant is absent from the registry and its WebSocket path uses the admin key; Relay lease issue/revoke/introspection and policy evaluation shared by realtime, jobs, and announcements; Mac executor and browser extension preflight hooks that enforce the lease before external side effects or private reads; A protected-session state in the browser bridge that can hide/freeze tabs on lease expiry; Owner-configurable action classes (private-read, external-send, financial, destructive) and an emergency local revoke gesture

### "Let me say “this is private” or “work-only,” and have that boundary follow the conversation across the pendant, relay, Mac, and browser: redact or keep sensitive content local, block cloud browser reads and external sends that violate the boundary, and tell me exactly what was withheld and why."
- **useful because:** The owner should not have to remember which surface currently holds a secret. Today a private browser tab, a spoken request, and a Mac action can cross trust boundaries independently. A portable, visible data-boundary label would prevent accidental disclosure while preserving useful automation.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → unified
- **model tier:** Deterministic label propagation and redaction enforce the policy; a small local classifier may suggest labels. Realtime only explains a block or requests an explicit one-time override.
- **latency:** Label changes under 200 ms locally and under 1 second across the relay; blocked actions should explain themselves within 2 seconds.
- **cost:** <$0.005 for ordinary turns; local classification and policy checks dominate, with cloud inference disabled for protected content.
- **security:** Labels must be cryptographically bound to content hashes, browser session/tab, job, and expiry, not carried as untrusted prompt text. Default deny on missing provenance or classifier uncertainty. Overrides require deliberate physical confirmation and must be auditable; never store raw protected content in relay logs or announcements.
- **missing:** A shared data-classification and policy token understood by relay, Mac, and browser; Local redaction/classification before any cloud call, including screen frames and audio transcripts; Browser extension hooks that prevent protected extraction or external submission; Relay and Mac log/announcement redaction enforcement rather than prompt-only untrusted flags; Owner-visible audit of every blocked, redacted, or overridden transfer

### "Give me a durable delegation mode: “Keep working on this until it is done, but stop at every irreversible choice.” The relay should keep the goal alive while the Mac and browser work, survive a laptop or network interruption, present each checkpoint to me on the pendant, and resume only from a verified checkpoint—not from a guessed summary."
- **useful because:** Today a long task can be marked complete when only the Mac finished, while browser state, relay delivery, and owner approval remain unclear. The owner needs to delegate outcomes, not supervise every click, without allowing an automation loop to cross a purchase, send, delete, or publish boundary.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → unified
- **model tier:** A cheaper background planner maintains the state machine and retries; vision/browser models handle individual steps; Realtime is reserved for checkpoint questions and concise spoken updates.
- **latency:** Routine steps proceed without conversation; checkpoint notification under 2 seconds after reaching a boundary; resume within 3 seconds of a verified response.
- **cost:** Roughly $0.02–$0.20 for a multi-step task depending on vision calls; durable state and browser interaction dominate.
- **security:** Every checkpoint needs an immutable pre-state, intended mutation, postcondition, and idempotency key. Never resume from prose alone. Expire approvals, stop on changed browser identity or evidence hash, and require the physical unlock policy for external side effects. Keep secrets in the browser/session boundary.
- **missing:** A durable cross-surface task state machine with resumable checkpoint receipts; Relay scheduling/retry and lease ownership that survives Mac outages; Browser and Mac action preconditions/postconditions exposed to the planner; Pendant checkpoint delivery plus a real owner response/physical acknowledgement path; A policy compiler for identifying irreversible actions


## What it asked for

_Nothing._
## Its own summary

Discovered and recorded a major live-state change: the exact AI Pendant Agent now has Accessibility and Screen Recording, inputReachability=verified, uiActionsWillReachTheScreen=true, secureInput=false, and all required permissions ready. Safari/browser bridge is online with 9 tabs; relay and Mac bridge are reachable; device discovery still shows no registered pendant. I proposed three non-duplicate owner capabilities: (1) the highest-value safety feature, a nonce-bound physical pendant confirmation gate for sensitive Mac/browser actions; (2) evidence-linked interactive catch-up that never equates Mac completion or socket delivery with hearing; and (3) frame-hash-bound “what am I looking at / click it” grounded screen interaction. I also notified faculty-action and faculty-judgement of the new reachability fact and confirmation-gate design.

**Biggest unknown:** The granted read_continuity_snapshot tool still fails resolver matching (nearest live route is GET /ops/snapshot), so I cannot obtain its promised single authenticated cross-surface continuity view. Direct probes work. The pendant remains physically absent from the relay registry, so playback and challenge testing cannot be verified until it registers; the pendant WebSocket also still uses the admin key rather than scoped device authentication.

