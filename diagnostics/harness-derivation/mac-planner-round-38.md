# Harness derivation — mac-planner — round 38

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“When I’m in a meeting, keep interruptions quiet; collect anything important and give me a two-minute catch-up when it ends.”"
- **useful because:** The pendant is present but cannot know the owner’s desktop context, while the Mac cannot reliably reach them away from the screen. Combining Calendar on the Mac, foreground/browser state, the always-awake relay, and the pendant’s haptics/audio creates a genuinely useful interruption shield: urgent items still break through, everything else becomes a ranked, sourced post-meeting queue.
- **path:** mac-read-sources reads today’s Calendar and detects meeting start/end; mac-readonly-inspect observes foreground app and browser tabs as optional context → relay maintains the meeting window, ranks incoming mail/browser-watch/job events, and stores a compact deferred queue → pendant receives a discreet urgent haptic/audio signal only for configured high-priority items, then plays the short digest after the meeting → Mac writes a local review folder with the agenda, deferred items, source links, and suggested follow-ups; browser harness contributes changes from authenticated watched pages
- **model tier:** Use a cheap background model for event classification, deduplication, and the post-meeting digest; reserve realtime only for an owner interruption or a spoken request such as “catch me up.”
- **latency:** Meeting-state changes should propagate within 10 seconds; urgent escalation within 3 seconds; post-meeting digest ready within 30 seconds. Normal events can be batched every 1–5 minutes.
- **cost:** Roughly $0.01–$0.05 per meeting depending on event volume; most cost is summarizing accumulated mail/browser events, not calendar detection. Local calendar parsing and deduplication should be free.
- **security:** Calendar titles, mail snippets, and authenticated-page changes leave the Mac only as compact classified events; sensitive content must be redacted by default and source links kept local. Never expose private meeting titles over audio unless the owner has enabled it. Sending mail, submitting browser forms, deleting files, or buying remains a separate explicit action.
- **missing:** A durable cross-surface meeting-state service with quiet hours, calendar event identity, manual override, and crash-safe queue; A relay-to-pendant push contract for priority haptic/audio notifications and replay after link loss; Browser page-watch integration that emits normalized meaningful-change events rather than raw authenticated-page content; A Mac local writer for a per-meeting review bundle and a small status indicator/override (Quiet now, Resume, Catch me up)

### "“Save where I am, and when I come back, put me back into this task exactly as I left it.”"
- **useful because:** Today the owner can save files or tabs, but loses the invisible state that makes work resumable: which paragraph was selected, which browser tab and form section mattered, what was still unsaved, why the task mattered, and what the pendant conversation had already established. A cross-device checkpoint would let them move away from the Mac, use the pendant later, and return without reconstructing the task from memory.
- **path:** Mac captures a bounded checkpoint of the foreground app, accessibility/UI target, open files, selection or cursor where available, browser tab/session identifiers, and unsaved-versus-saved status without copying whole documents by default → Browser harness records authenticated tab identity, URL, semantic region, and a safe reattachment recipe, not credentials or raw page dumps → Relay stores the encrypted checkpoint, a short owner-facing summary, expiry, and an append-only version history; it can answer a pendant request while the Mac is asleep → Pendant records only the checkpoint token and offers a button/voice command to say “resume”; on reconnect it receives the summary and asks the Mac to restore the state → Mac restores apps/tabs/files non-destructively, highlights the prior target, and writes a before/after receipt if anything has changed since checkpoint
- **model tier:** Use a cheap background model to summarize intent and select stable semantic anchors; use realtime only when the owner asks the pendant to resume or clarify which checkpoint. Restoration itself should be deterministic tooling, not model improvisation.
- **latency:** Checkpoint capture under 2 seconds; pendant acknowledgment under 3 seconds when connected; restore under 15 seconds for a normal work session. If a page or app changed, return a concise conflict report rather than attempting a blind restoration.
- **cost:** About $0.001–$0.02 per checkpoint, dominated by optional intent summarization; most state capture, hashing, and restoration is local. Relay storage is small if documents remain on the Mac and checkpoints retain references plus hashes.
- **security:** Authenticated URLs, document names, and snippets are sensitive. Encrypt checkpoints at rest and in transit, redact content by default, keep full text local, expire checkpoints, and never persist cookies, passwords, or form secrets. Restoring a draft must not submit, send, delete, or overwrite; any destructive follow-up remains a separate owner command.
- **missing:** A versioned checkpoint schema with stable semantic anchors, content hashes, expiry, and conflict states; A Mac read/restore adapter that can capture and reapply app UI state without stealing focus or overwriting unsaved edits; A browser session checkpoint/reattachment API that can identify the correct authenticated tab after restart; Relay storage and reconnect protocol for encrypted checkpoint tokens and pendant replay; A pendant-local token store and resume gesture/voice intent


## Changes it proposed to its own stack

### `integration` — Add a cross-surface Attention Window protocol. The relay owns a durable state machine (NORMAL, QUIET_MEETING, URGENT_ONLY, CATCHUP_READY) keyed by calendar event ID and timezone. Mac emits signed lifecycle events (meeting detected, ended, manually overridden) plus redacted candidate notifications; browser watchers and scheduled jobs emit normalized event envelopes with source, priority, dedupe key, expiry, and local deep link. The relay deduplicates by envelope ID, queues during QUIET_MEETING, pushes only URGENT_ONLY items to the pendant, and emits one compact catch-up bundle to Mac and pendant at end. Persist an append-only receipt so reconnects replay safely without duplicate speech.
- **owner gets:** The owner stops being interrupted by five surfaces separately, yet does not miss the one thing that matters. When the meeting ends, the catch-up is coherent and actionable rather than a pile of notifications, even if the Mac, browser, or pendant briefly went offline.
- effort: Medium-high: relay state machine and durable queue, Mac calendar/event adapter, browser/job event adapters, pendant push/replay framing, and a small local review-bundle writer. Add simulator tests for overlapping meetings, timezone changes, reconnects, and duplicate events.  ·  risk: A stale calendar event could suppress useful alerts, or a misclassified urgent item could interrupt. Recover with a pendant “resume all” gesture, a Mac menu override, hard expiry on quiet windows, and a visible queue count. If relay storage is unavailable, default to NORMAL rather than silently suppressing alerts.
- cost: Low ongoing API cost (event envelopes and mostly local filtering); roughly $0.01–$0.05 per meeting for background summarization. Storage is small: metadata plus redacted snippets, with configurable short retention.  ·  latency: Calendar transitions under 10 seconds, urgent push under 3 seconds, catch-up generation under 30 seconds after meeting end.
- security: Only redacted event summaries and opaque source IDs cross the relay by default; full mail/page content stays on Mac unless explicitly requested. Calendar titles and links need sensitivity labels. No new destructive authority is introduced.
- depends on: relay-to-pendant push and reconnect replay protocol; Mac calendar lifecycle adapter and local review-bundle writer; normalized event emission from browser watches and long-running jobs; owner-configurable urgency rules and quiet-window overrides


## What it asked for

### `s13-qumu` (skill) — offline_attention_window_toggle
- does: A long press on the pendant’s existing control button toggles QUIET/URGENT-ONLY/NORMAL locally, gives distinct haptic feedback, and timestamps the change. While disconnected it suppresses nonurgent queued playback, preserves urgent alerts, and syncs the mode transition and missed-event cursor to the relay when the link returns. A short press during QUIET requests the pending catch-up rather than playing arbitrary queued audio.
- must be on-device because: The owner may enter or leave a meeting away from the Mac, and the link can be down. The mode decision and suppression must work immediately and safely on the gadget; the relay can reconcile it later with calendar-derived state.
- trigger: Long button press; short button press while QUIET; server push on reconnect; optional timer expiry supplied by relay.
- storage: A small NVS record for mode, mode epoch, expiry, and last-synced cursor (under 1 KB), plus a bounded ring of perhaps 32 event headers (roughly 2–4 KB); no message bodies stored locally.
- RAM budget: About 4–8 KB transient RAM for the event-header ring, debounce state, and replay framing—well within the 211,608 B application RAM budget. Reuse the existing audio/event buffers; do not cache full text or audio.

## Its own summary

Round 38 produced a new cross-surface capability: meeting interruption shielding with a coherent post-meeting catch-up. I proposed the Attention Window protocol (relay-owned state machine, redacted event envelopes, deduped durable queue, Mac review bundle, browser-watch/job adapters, and pendant push/replay) and queued an offline pendant skill using its single button for local QUIET/URGENT-ONLY/NORMAL control during link loss. I verified the pendant is a prototype nRF9160 DK with one button/LED and 211,608 B application RAM; the skill fits comfortably without storing message bodies.

**Biggest unknown:** The relay’s actual pendant push/reconnect contract and whether browser watches/long-running jobs can emit normalized event envelopes. I still need those integration surfaces, plus an owner-defined urgency policy and privacy choices for spoken meeting titles/content. The hardware button mapping is provisional because this is explicitly a development kit.

