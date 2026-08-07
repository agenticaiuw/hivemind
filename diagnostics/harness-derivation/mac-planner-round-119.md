# Harness derivation — mac-planner — round 119

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“When I’m heading into a meeting, get me ready; when I leave, turn what I captured into follow-ups.”"
- **useful because:** This closes the gap between one-shot meeting preparation and the messy aftermath. A short/double press on the pendant marks entering or leaving without opening a phone; before the meeting it combines the actual Calendar event, relevant open authenticated browser pages, and the active Mac project into a cited one-page brief plus a short audio queue. Afterward it turns locally buffered voice notes or typed scraps into proposed tasks, reminders, and a dated meeting note, with uncertain people/dates called out instead of silently inventing them.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheap background model for brief extraction, deduplication, and follow-up structuring; reserve realtime only for the pendant's immediate acknowledgement and the owner's explicit questions. Browser evidence extraction should stay on the browser/session worker, while the server model synthesizes citations.
- **latency:** Gesture acknowledgement under 300 ms locally; pre-meeting brief available within 15 s (or immediately serve the last cached event brief); post-meeting draft within 60 s of reconnection. No microphone is opened by the Mac surface.
- **cost:** Roughly $0.01–$0.05 per meeting lifecycle, dominated by synthesis and optional speech generation; most Calendar/Mac/browser reads are local or existing relay calls.
- **security:** Calendar, private tabs, and captured notes leave the Mac only as explicitly selected evidence. Store a per-meeting capsule with source URL/event IDs and short-lived audio retention; redact secrets and never include credentials in the brief. Creating reminders/notes is reversible enough for the owner's stated policy, but sending mail, submitting forms, or deleting anything remains out of scope. Dashboard must show every source and allow discard.
- **missing:** A durable meeting capsule state machine shared by pendant, relay, Mac, and browser (preparing/in-meeting/left/reconciled); A firmware gesture/event uplink and offline ring buffer for meeting markers and short follow-up notes; A browser extractor that can select relevant already-open authenticated tabs by event/project rather than scrape arbitrary pages; A post-meeting entity/date confidence pass and deduplicating reminder writer; An audio queue contract that lets the pendant fetch and resume a generated brief after link loss

### "“Save what I’m looking at so I can pick it up later.”"
- **useful because:** Today a thought, tab, and the owner's place in a document are separate. This would let a pendant gesture create a resumable, citation-backed handoff from the exact foreground Mac app or authenticated browser tab: selected text or a semantic excerpt, URL/document location, scroll position, project, and the owner's spoken label. Later, the pendant can read a short list of saved handoffs, and one command on the Mac reopens the precise document/tab and location. It is not a generic bookmark or note: it preserves where the owner was and what they meant to return to.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheap background model only to label, summarize, and resolve duplicate handoffs. Realtime handles the brief spoken label and lookup. The browser extension and Mac agent collect raw state locally; the server stores only the selected excerpt and minimal resume metadata.
- **latency:** Local marker acknowledgement under 300 ms; capture and confirmation under 3 s; lookup under 2 s; reopening the Mac/browser state within 5 s. If a tab or file is unavailable, report that explicitly rather than substituting a similar page.
- **cost:** Usually below $0.01 per save/reopen, dominated by occasional summarization; most state capture and reopening is local. Storage is small text plus metadata, with optional short retention.
- **security:** Authenticated page content and local file excerpts are sensitive. Require explicit owner gesture or phrase for capture, encrypt the handoff, redact passwords/tokens, and show source, timestamp, and retention before sharing it to another surface. Never capture an entire page by default. Reopening a tab or file is allowed, but sending, submitting, deleting, or purchasing remains outside this capability.
- **missing:** A cross-surface resumable-handoff record with versioned location anchors and expiry; A Mac read-only foreground/selection/document-location adapter that does not require screen scraping; A browser-extension capture message returning tab identity, semantic excerpt, and stable DOM/text anchors; A reopen operation that validates the original URL/file and reports anchor drift instead of silently opening the wrong place; Pendant lookup and deletion controls for saved handoffs


## Changes it proposed to its own stack

### `firmware` — Add a local meeting-marker protocol using the existing single button: double-press emits ENTER_MEETING, long-press emits LEAVE_MEETING, and a short press during the active capsule starts/stops a tiny follow-up memo buffer. Persist only an event ID, monotonic timestamps, and encrypted compressed audio chunks in a bounded ring; on reconnect send an idempotent capsule event with sequence numbers, then delete acknowledged chunks.
- **owner gets:** The owner can mark the moment without touching the Mac or trusting a fragile network connection, and can leave a thought immediately after a meeting while walking away. If the link drops, the handoff is not lost or duplicated.
- effort: Medium firmware plus relay protocol work; test button debounce, reconnect, duplicate delivery, and flash wear on the prototype before committing product hardware.  ·  risk: False enter/leave gestures and ring overflow. Recover by LED/haptic confirmation, an undo gesture within a few seconds, explicit overflow indication, and server-side sequence deduplication. Never auto-send captured content to third parties.
- cost: Negligible API cost; flash writes and occasional LTE-M transfer increase battery use modestly. On the current prototype, budget about 20–35 kB RAM for one compressed chunk plus protocol buffers, and reserve flash for a bounded queue; product hardware should include secure storage and ideally a second tactile control.  ·  latency: Local marker acknowledgement is sub-second; upload is deferred when radio is unavailable and should not block playback or button handling.
- security: Encrypt queued audio at rest and bind capsule uploads to the device identity; expose retention and deletion state in the dashboard. Do not log raw audio in UART diagnostics.
- depends on: A relay meeting-capsule endpoint with idempotent event sequencing; An audio codec/queue contract compatible with the owner's 24 kHz superwideband path; A Mac/browser evidence collector that can attach sources to the same capsule

### `integration` — Add a resumable-handoff envelope shared by the pendant, Mac harness, and browser extension. It should contain an owner label, source surface, tab/file identifier, URL or path, excerpt hash, semantic text anchor, optional character/scroll range, project context, created/expiry timestamps, and a reopen result. On reopen, validate the source identity and anchor hash; if content moved, present the nearest cited match for review instead of guessing.
- **owner gets:** The owner can reliably stop reading or editing on one surface and resume later at the same place, without hunting through tabs, files, or memory. It turns a fleeting “I need to come back to this” moment into a dependable physical-to-desktop handoff.
- effort: Medium integration work across the browser extension, Mac read-only inspection, relay storage, and pendant command protocol; substantial testing is needed for document edits, closed tabs, renamed files, and expired links.  ·  risk: A stale anchor could reopen the wrong content, or a sensitive excerpt could persist too long. Use identity/hash validation, bounded retention, explicit stale-state errors, encryption, and a one-command delete-all control. Never fall back to an unverified location.
- cost: Low API and storage cost: typically a few KB per handoff, with model calls optional and background-priced. No meaningful pendant RAM increase if the envelope remains server-side and only IDs/status are cached locally.  ·  latency: Capture is immediate locally; synchronization can be asynchronous. Reopen adds one validation round trip, targeted at under five seconds.
- security: This creates a new sensitive-data store, so encrypt excerpts, minimize retention, redact credentials, scope records to the owner, and include a complete audit trail of capture and reopen operations.
- depends on: A browser extension message for selected/semantic content and stable anchors; A Mac adapter exposing foreground document or selection metadata without requiring the Mac microphone; A durable relay record and pendant lookup/delete protocol


## What it asked for

### `t15-un54` (tool) — meeting_capsule_api
- why: The proposed meeting lifecycle needs one durable, idempotent record shared by pendant marker events, Mac/browser evidence, generated brief/audio, and post-meeting follow-ups. Existing capture and briefing routes are separate and cannot safely correlate enter/leave events or deduplicate reconnects.

```json
{
  "operation": "string enum: open|append_event|attach_source|set_brief|append_followup|close|discard",
  "capsule_id": "string optional for open, required otherwise",
  "device_event_id": "string optional, idempotency key for pendant events",
  "event_type": "string optional enum: enter|leave|memo_start|memo_chunk|memo_stop|reconnect",
  "event_seq": "integer optional monotonic per device",
  "source": {
    "kind": "calendar|browser|mac|pendant",
    "id": "string",
    "url": "string",
    "title": "string",
    "snippet": "string",
    "captured_at": "string"
  },
  "payload": "object optional structured event or extracted text",
  "retention_hours": "integer optional, bounded server policy"
}
```

