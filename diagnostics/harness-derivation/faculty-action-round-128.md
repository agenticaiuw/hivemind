# Harness derivation — faculty-action — round 128

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I press the pendant button while looking at something, save a complete 'context card' of what I was doing—active Mac app/document, current browser tab and selected text if available, timestamp, and my short dictated label later—and leave it as a searchable follow-up."
- **useful because:** The owner loses thoughts and web context during transitions. A physical button is faster and more reliable than switching to an app; combining the worn device with Mac and browser state captures the surrounding evidence, not just a vague note.
- **path:** pendant → mac-bridge → browser → relay → dashboard
- **model tier:** Realtime only for the tiny label/confirmation; background model extracts and normalizes the card cheaply.
- **latency:** Button acknowledgment under 500 ms; context card visible within 3 seconds.
- **cost:** <$0.01 per card when unlabeled; <$0.03 if a background model summarizes selected text. Dominant cost is optional summarization.
- **security:** Cards may contain private page text and document names. Keep raw capture on the Mac by default, encrypt relay sync, show source URLs/apps, and require explicit confirmation before sharing or sending.
- **missing:** Pendant button event over the existing USB serial path; A Mac endpoint that atomically snapshots active app plus browser tab/selection; Searchable card schema and retention controls

### "When the pendant disconnects from my Mac or I press its 'leaving' gesture, package the work I was doing into a departure handoff: save open project state and URLs, create a prioritized resume checklist, and read me the first item when I reconnect."
- **useful because:** Leaving the desk currently destroys working context. The pendant is the only surface that can notice the transition and later restore the thread, while the Mac can gather concrete state and the relay can retain the handoff.
- **path:** pendant → mac-bridge → browser → relay → dashboard
- **model tier:** Use a cheap background model for checklist synthesis; realtime only for the short reconnect announcement.
- **latency:** Capture starts within 2 seconds of disconnect; handoff ready within 15 seconds; reconnect announcement under 2 seconds.
- **cost:** $0.01–$0.05 per departure depending on number of open tabs and document metadata; most cost is checklist synthesis.
- **security:** Open documents, URLs, and project names are sensitive. Default to local encrypted storage, omit page bodies unless explicitly enabled, expire handoffs after 7 days, and never alter or close apps during capture.
- **missing:** USB serial disconnect event exposed to the relay/Mac agent; Read-only active-window/project/browser inventory with stable identifiers; Reconnect association to the same pendant identity and a resumable handoff store

### "Let me use the pendant's button and audio bridge to work through a spoken queue of pending briefings and receipts: next, repeat, mark heard, and open the referenced item on the Mac, without touching the keyboard."
- **useful because:** The owner can consume accumulated work while walking or away from the screen. The pendant provides the low-friction controls, the bridge provides playback, and the Mac supplies links and action receipts; no single surface can offer this continuity.
- **path:** pendant → mac-bridge → browser → relay → dashboard
- **model tier:** Pre-render summaries with a cheap background model; realtime handles only button commands and short playback control.
- **latency:** Button-to-next audio under 700 ms; first queue item under 3 seconds; opening a referenced Mac item under 5 seconds.
- **cost:** <$0.02 per item for generated speech/summary; playback and queue navigation are local.
- **security:** Briefings and receipts may reveal private data in public spaces. Require a long-press to start playback, support immediate mute, avoid page bodies in spoken text by default, and keep open-on-Mac as a separate explicit command.
- **missing:** Pendant button command protocol and queue cursor persistence; Audio bridge playback control/status and resumable audio segments; A unified queue API joining /briefing/latest, job receipts, and browser references

### "Move an active conversation and its unfinished plan between my pendant, Mac, and browser without starting over: say 'continue on my Mac' or press the handoff control, and resume with the transcript, evidence, pending approvals, and exactly the next safe step."
- **useful because:** Today a conversation is effectively trapped in the surface that started it. This would let the owner begin hands-free, inspect private browser evidence on the Mac, and return to the pendant with the same state rather than repeating themselves.
- **path:** pendant → relay-realtime → mac-bridge → browser → dashboard
- **model tier:** No expensive model for transfer; reuse the existing session state. Use a cheap model only to compress a long transcript for the receiving surface.
- **latency:** Transfer acknowledgment under 1 second; receiving surface resumes within 3 seconds.
- **cost:** Near-zero for short sessions; <$0.02 for optional transcript compression. Storage and context transfer dominate.
- **security:** A handoff must not leak private browser content into audio or another surface. Carry sensitivity labels and consent scope with every evidence item; require a fresh spoken/button confirmation when the destination is less private.
- **missing:** A first-class portable session envelope containing transcript, plan, evidence references, approvals, and next step; Relay-to-Mac and Mac-to-pendant transfer routes with idempotent versioning; Destination-specific redaction and consent enforcement

### "Put the whole hive into a physical 'do not act' mode with one deliberate pendant gesture: stop speech and outbound actions, cancel or pause queued work where safe, and hold only a small urgent queue until I explicitly release it."
- **useful because:** The owner needs a dependable interruption boundary in a meeting, while driving, or when lending the Mac to someone. A server-side preference is too slow and too easy to forget; the worn control can cut across every surface.
- **path:** pendant → relay-realtime → mac-bridge → browser → dashboard
- **model tier:** Pure deterministic policy; no model call for engaging, holding, or releasing the mode.
- **latency:** Local LED acknowledgment under 300 ms; relay and Mac enforcement under 2 seconds; no new outbound action after the fence is observed.
- **cost:** Negligible API cost; a few durable state events per transition.
- **security:** A bad gesture could suppress a needed alert, so use a long press plus distinct LED/audio confirmation, allow emergency alerts through, and make release equally deliberate. Persist an auditable mode timeline.
- **missing:** Device-originated global policy event with monotonic sequence number; Enforcement middleware in relay, Mac jobs, and browser command execution; Clear emergency-alert classification and durable release acknowledgment

### "Tell the hive 'erase the last hour' and have it actually remove the selected conversation's audio, transcripts, browser extracts, Mac snapshots, generated speech, and job-context links across every store, then return a verifiable deletion receipt."
- **useful because:** The owner cannot safely use an always-listening, always-connected assistant without a trustworthy way to retract a sensitive moment. One command should not require knowing which device cached which artifact.
- **path:** pendant → relay-realtime → mac-bridge → browser → dashboard
- **model tier:** Deterministic deletion and verification; use no model except optional natural-language time-range parsing.
- **latency:** Stop new propagation immediately; deletion receipt within 10 seconds for normal stores, with explicit pending status for offline devices.
- **cost:** Negligible model cost; storage-provider deletion/listing calls dominate.
- **security:** Deletion is irreversible. Require a deliberate confirmation, show exact time range and affected stores, retain only a non-content tombstone, and distinguish confirmed deletion from an offline device that has not checked in.
- **missing:** Cross-store artifact manifest with lineage from audio to transcript to TTS/job/browser evidence; Authenticated delete-and-verify routes on relay, Mac, and browser bridge; Offline-device purge command and cryptographic deletion receipt


## Changes it proposed to its own stack

### `integration` — Add a pendant–Mac transition broker that consumes USB serial connect/disconnect and button events, assigns a monotonic device-event ID, snapshots the Mac/browser state once per event, and publishes a durable correlation record linking event, capture card, briefing, and later job receipt. Deduplicate reconnect storms and expose an explicit expiry/forget operation.
- **owner gets:** The owner gets one trustworthy thread for 'what I was doing when I left/pressed this' instead of disconnected notes, browser state, and job history that cannot be resumed together.
- effort: Medium: serial watcher, event schema, browser/Mac snapshot adapters, and a small durable index.  ·  risk: USB noise or stale browser state could create misleading cards; debounce events, label every source timestamp, and allow deletion of a whole correlated thread.
- cost: Negligible API cost; local storage under a few MB/month unless raw page text is retained.  ·  latency: 100–300 ms event detection, 1–3 s snapshot completion.
- security: Increases concentration of sensitive context; encrypt at rest, redact page bodies by default, and scope relay replication per thread.
- depends on: Pendant USB serial event reader; Stable browser tab/session identifiers; A retention/deletion policy for correlated context

### `interaction` — Create a tactile receipt protocol: after a Mac or browser action completes, the relay emits a compact result class to the pendant (success, waiting, needs-owner, failed), with distinct LED/audio patterns and a short spoken item ID on request. The pendant acknowledges receipt locally and the acknowledgement is attached to the existing job receipt without executing anything.
- **owner gets:** The owner can know whether a long-running action actually finished while away from the Mac, and can later ask about the exact item instead of guessing which notification was real.
- effort: Medium: map job lifecycle to a four-state device protocol, add resumable acknowledgement records, and implement bridge playback/LED patterns.  ·  risk: A misleading success pattern could cause the owner to trust an incomplete action; only emit success from durable receipt state, use timeout-to-waiting, and retain the full textual receipt for verification.
- cost: Near-zero model cost; small local/relay event volume.  ·  latency: Under 1 s after receipt commit; reconnect replay within 2 s.
- security: Patterns should not encode sensitive content; spoken text requires explicit button request and local volume/mute handling.
- depends on: Pendant/bridge bidirectional event protocol; Durable job receipt lifecycle; Device identity and reconnect replay


## What it asked for

_Nothing._
## Its own summary

Round 128 produced three new cross-surface capabilities: button-triggered context cards, disconnect/reconnect departure handoffs, and tactile/audio navigation of briefings and job receipts. It also recorded two implementation changes: a USB transition broker that correlates device events with Mac/browser state, and a pendant tactile receipt protocol for durable job outcomes. Live discovery: Mac bridge and Safari extension are online; the pipeline already carries 24 kHz TTS and has durable receipt stages, including an approval-waiting state. Accessibility and Screen Recording remain ungranted, while AppleScript automation is granted.

**Biggest unknown:** Whether the physically connected nRF9160 and ESP32 are currently visible to the Mac and what serial protocol/firmware event framing they expose. The device table still does not list a registered pendant, and no granted tool can inspect serial devices without building/flashing.

