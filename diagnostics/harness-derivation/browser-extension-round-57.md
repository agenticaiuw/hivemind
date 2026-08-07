# Harness derivation — browser-extension — round 57

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser bridge health** — As of round 57, GET /browser/status reports online:false for both devices and pendingCommands=4; a POST /execute browser_navigate did not return within 20 seconds, so commands can accumulate without an extension consumer.
  - evidence: GET /browser/status response at 2026-08-07 shows Safari absent/offline, home-chrome tabId null, pendingCommands 4; POST /execute browser_navigate about:blank timed out.

## Capabilities it proposed

### "When something important changes in one of my logged-in browser pages, interrupt me only when I can actually deal with it; otherwise queue a tiny, sourced card and bring it up when I’m free."
- **useful because:** Existing page watches can detect changes, but they cannot know whether an interruption is welcome or provide a spoken, resumable handoff. This combines private browser evidence, Mac presence/context, relay scheduling, and the pendant’s low-friction attention channel so alerts become useful instead of noisy.
- **path:** browser-extension: capture the changed authenticated DOM region with URL, tab identity, timestamp, and a redacted before/after diff → mac-planner: read active app/window, calendar/meeting state, and focus mode; persist an expiring evidence card and deduplicate related changes → relay-realtime: classify urgency and decide interrupt-now versus queue, using a cheap background model for watch processing and realtime only for the spoken interaction → pendant: give a brief tone/voice card, let the owner say 'later', 'read it', or 'open it'; send the selected card back to Mac/browser for a cited follow-up
- **model tier:** Background model for extraction, semantic diff, urgency scoring, and deduplication; realtime model only if the owner asks a follow-up by voice.
- **latency:** Change detection can complete within the watch cadence (typically 1–5 minutes). Interrupt decision should be under 2 seconds after a result; queued cards can be delivered at the next focus transition.
- **cost:** Roughly $0.002–$0.02 per changed page check depending on DOM size and model; most checks should use hashing/selector extraction locally, with model spend only on meaningful diffs. Spoken follow-ups use normal realtime turn cost.
- **security:** Authenticated page snippets leave Safari only to the relay/Mac path and may contain sensitive data. Store only redacted diff plus short-lived encrypted evidence, never full page HTML by default. Require explicit per-watch domain/region selection and provide delete/export; opening a link is reversible, but any submit/send action remains outside this workflow and must stop for review.
- **missing:** A reliable implemented browser command enqueue path and an online Safari heartbeat (currently status reports offline and pending commands accumulate); A durable page-watch scheduler with semantic diff and volatile-field suppression; A shared presence/focus signal from Mac plus a relay delivery queue to the pendant; An expiring, cited evidence-card format and pendant actions for defer/read/open

### "While I’m in a browser meeting, listen for decisions, questions addressed to me, and commitments I make; quietly tell me when I need to respond, then leave a sourced action list and draft follow-ups without sending anything."
- **useful because:** A meeting assistant today can summarize audio or manipulate a browser, but it cannot combine the private meeting tab, live low-latency pendant attention, Mac-side durable notes, and post-meeting drafting while respecting the owner’s existing login. The owner gets help in the moment without constantly watching a transcript, plus an auditable record afterward.
- **path:** browser-extension: read captions/transcript and meeting metadata from the already-authenticated meeting tab, retaining only the relevant time-stamped excerpts → relay-realtime: detect direct questions, decisions, deadlines, and owner commitments with low latency; send only a short discreet prompt to the pendant → pendant: speak or display a minimal cue such as who asked and the unresolved question, with 'dismiss' and 'remind me' controls → mac-planner: maintain a rolling meeting ledger, reconcile it with Calendar and existing notes, and after the meeting create a cited action list and drafts in the appropriate app → mac-vision/mac-terminal: open the meeting notes destination and prepare drafts or links when the owner requests review
- **model tier:** Realtime model for only the live question/commitment detector and brief cues; a cheaper background model performs final transcript compression, deduplication, and draft generation after the meeting.
- **latency:** Live cues within 1–2 seconds of a caption segment; post-meeting ledger within 1 minute of leaving the call; drafts can take another 10–20 seconds.
- **cost:** Approximately $0.01–$0.10 per meeting hour depending on caption volume and whether audio fallback is needed; local caption filtering and incremental summarization should dominate savings. No cost for idle periods.
- **security:** Meeting content, participant names, and private captions are sensitive. Require an explicit per-meeting opt-in, show recording/processing state, keep raw captions ephemeral, encrypt the sourced ledger, and allow immediate purge. Never send a reply, accept a commitment, or edit a shared document without a separate owner instruction.
- **missing:** A browser extension API that can stream caption deltas and meeting-tab identity rather than one-shot page extraction; A low-latency event path from browser to relay and pendant, with interruption/dismissal semantics; A meeting-scoped encrypted ledger with source timestamps and automatic expiry; Calendar/notes correlation and draft creation wired to the Mac action layer


## Changes it proposed to its own stack

### `browser-harness` — Add a browser-bridge circuit breaker and self-healing lifecycle: every queued command gets a lease, deadline, device affinity, and status (queued/claimed/result/expired); when Safari heartbeat disappears, stop accepting blocking execute calls, retain only explicitly durable jobs, expire stale interactive commands, and surface a reconnect/open-Safari instruction to the Mac and pendant. On heartbeat recovery, replay only unexpired idempotent jobs and never old clicks/types.
- **owner gets:** The owner should never experience a voice request hanging for 45 seconds or have an old click execute unexpectedly after Safari returns. They get a clear 'browser unavailable' answer, safe recovery when the extension reconnects, and no surprise actions from stale queue entries.
- effort: Medium: queue schema/state machine, lease sweeper, heartbeat transition events, bounded replay policy, and relay/Mac error presentation; add integration tests for offline, reconnect, duplicate result, and restart.  ·  risk: A transient Safari sleep could expire a job the owner expected to finish. Recover with an explicit retry action and preserve the original request/evidence; all interactive commands default to expiry rather than replay.
- cost: Negligible API cost; small persistent queue metadata and one periodic sweeper. No new model calls required.  ·  latency: Offline requests fail fast (sub-second to a few seconds) instead of waiting for the bridge timeout; normal online actions unchanged.
- security: Improves safety by preventing stale authenticated clicks/types from replaying. Lease tokens and device affinity must be unguessable; retain only minimal command parameters after expiry.
- depends on: A functioning Safari extension heartbeat/command transport; The durable browser job runner and result stream (chg-16bc5dee remains incomplete); A shared status event consumed by relay-realtime and mac-planner

### `new-surface` — Add a meeting-copilot event surface spanning the Safari extension, relay, Mac agent, and pendant: the extension emits redacted caption deltas and meeting lifecycle events; relay emits typed attention events (direct_question, owner_commitment, decision, deadline); Mac stores a scoped evidence ledger; pendant renders discreet cues and acknowledgements. Include a hard meeting-scope boundary so events stop when the tab/call ends.
- **owner gets:** They can participate in a meeting instead of manually monitoring captions, receive a timely cue when a response is expected, and leave with reliable action items tied to exact excerpts rather than vague AI notes.
- effort: Large: extension content-script adapters for major meeting UIs, streaming transport and backpressure, event schema, pendant cue protocol, encrypted ledger, and app-specific post-meeting draft adapters.  ·  risk: Caption errors or an accidental scope leak could create embarrassing prompts or expose confidential discussion. Recover with visible active-state indication, per-meeting start/stop, confidence thresholds, mute/dismiss controls, automatic expiry, and raw-caption purge; never auto-speak into or send to the meeting.
- cost: Caption deltas can be filtered locally; expect roughly $0.01–$0.10 per meeting hour for relay inference, plus modest encrypted storage. Realtime spend is limited to live cue detection.  ·  latency: Adds a streaming path and should target 1–2 seconds from caption to pendant cue; post-meeting work is asynchronous.
- security: Introduces a new sensitive data path. Use per-meeting ephemeral keys, tenant/device-bound channels, no raw transcript by default, explicit consent, and source-level deletion.
- depends on: Caption-delta capture from the browser extension; Low-latency relay-to-pendant event delivery; Meeting-scoped encrypted evidence storage on the Mac; A post-meeting draft/notes integration


## What it asked for

_Nothing._
## Its own summary

Round 57 established that the newly granted browser enqueue wrappers are still implementation stubs. Live status is worse than merely lacking a tab: both devices are offline and 4 commands are pending; a browser_navigate through POST /execute hung until probe timeout. I recorded this finding, notified mac-planner, and proposed (1) an adaptive cross-node authenticated-page alert that uses browser evidence, Mac focus/presence, relay delivery, and pendant controls, and (2) a browser circuit breaker with leases, expiry, reconnect recovery, and no stale click/type replay.

**Biggest unknown:** Whether Safari can be made to heartbeat and consume commands in this deployment. Until a real enqueue implementation plus an online extension heartbeat exists, I cannot inspect the owner's authenticated pages or validate any browser workflow end to end.

