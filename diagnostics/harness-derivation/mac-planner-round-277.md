# Harness derivation — mac-planner — round 277

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/browser reachability** — Safari browser bridge is online with two tabs; active tab is a YouTube video. Mac local agent reports full-control and vision loop enabled, but browser command capability list is empty, so read/control adapters still need explicit operation wiring.
  - evidence: discover devices: Safari on MacIntel online, 2 tabs; GET /browser/status and GET /ops/snapshot both report online=true, active YouTube tab, pendingCommands=0, capabilities=[]

## Capabilities it proposed

### "When I press the pendant button and say “save this claim,” capture the page I’m looking at as a cited evidence card in my workspace."
- **useful because:** It turns fleeting research into a durable, attributable artifact without making the owner stop and copy URLs. The pendant supplies an intentional moment marker even if the radio drops; the browser supplies authenticated page context; the Mac supplies atomic local storage.
- **path:** pendant → relay → browser → mac-bridge → dashboard
- **model tier:** Use the realtime tier only to recognize the short command and acknowledge it; use a cheaper background worker to normalize the excerpt and generate Markdown. No model is needed for URL/title extraction or hashing.
- **latency:** Acknowledge the button in under 300 ms; create the card within 5 seconds of browser response. If offline, queue the marker and finish when connectivity returns.
- **cost:** About $0.001–$0.01 per card depending on whether excerpt cleanup uses a model; browser inspection, hashing, and file staging dominate latency rather than API cost.
- **security:** The browser may expose authenticated content, so send only the active tab's title, URL, selected text, and a bounded excerpt; redact passwords/tokens and never capture cookies. Writing is local, but the policy must explicitly authorize creation under ~/AI-Pendant-Workspace; no network upload of page text by default.
- **missing:** A relay event contract that associates a pendant moment marker with the active browser tab and a deduplication key; A browser-bridge read operation that returns bounded selected text/page excerpt with redaction; A citation-card renderer and receipt linking the pendant event, URL hash, and local file

### "While I’m watching something, let me press the pendant and say “mark the last minute,” then save a private clip marker with the video, timestamp, and my spoken note."
- **useful because:** A physical mark is faster and more reliable than scrubbing back to find an idea. It works for a browser video or podcast and produces a navigable research trail rather than another unlabelled voice memo.
- **path:** pendant → relay → browser → mac-bridge
- **model tier:** Realtime handles the short note and acknowledgement; deterministic code reads the media URL/title/current playback time and writes the marker. Use a cheap background model only to clean an optional longer note.
- **latency:** Button acknowledgement under 300 ms; marker creation under 3 seconds. If the browser is unreachable, retain the marker locally and reconcile against the tab when it returns.
- **cost:** Typically below $0.001 per marker; the cost is browser round trips and local storage, not inference.
- **security:** Only capture the active tab's URL/title and media timestamp, not the full page or cookies. Treat spoken notes as private. Do not download or copy copyrighted media; store a pointer and optional user-supplied excerpt. Require an explicit policy entry for writing marker files.
- **missing:** Browser bridge operation to report active media element, playback time, duration, and seekable URL; Relay correlation between a pendant marker and a browser tab identity with retry-safe event IDs; A workspace index that can open the marker at the exact timestamp

### "If I say “pause that” to the pendant while my Mac is acting, stop the current browser or Mac job, save exactly where it got to, and let me say “continue” later."
- **useful because:** The owner can interrupt a risky or simply mistimed automation without racing to the keyboard, then resume instead of restarting a multi-step task. The pendant is an out-of-band control surface while the Mac is busy or out of sight.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime should classify only the short pause/continue utterance; deterministic job cancellation, checkpointing, and replay should be handled by the relay and Mac agent. Use a background model only to summarize the checkpoint for the spoken receipt.
- **latency:** Begin cancellation within 500 ms of recognition and acknowledge locally immediately. Persist a checkpoint within 2 seconds; resume should report the next action before executing it.
- **cost:** Under $0.005 per interruption, mostly relay state and a small checkpoint summary; no model is required for the control path.
- **security:** Cancellation must be idempotent and scoped to the owner's active job, never a global kill. A checkpoint may contain URLs or filenames, so redact secrets and retain it briefly. “Continue” must not silently repeat non-idempotent actions; the policy should require a fresh confirmation for send/delete/purchase steps even if unattended defaults later permit ordinary actions.
- **missing:** A relay-owned active-job control channel from pendant events to Mac job cancellation; Checkpoint/resume semantics that record completed action IDs and resource hashes before cancellation; A browser command cancellation adapter and a spoken receipt showing what was stopped

### "Where did I see that thing about [topic]? Search the moments I marked on the pendant, my browser pages, and my Mac notes, then tell me the best match and reopen it."
- **useful because:** Today the owner’s fleeting physical bookmarks, authenticated browsing, and local notes are separate silos. This would make the pendant a recall surface for lived context: it can recover the source, not merely generate a guess, even when the original tab is gone.
- **path:** pendant → relay → browser → mac-bridge → dashboard
- **model tier:** Use a cheap background indexing model to create embeddings and compact entity/time summaries; use realtime only for the short spoken query and answer. Retrieval should be deterministic and quote-backed, with no model-invented sources.
- **latency:** Spoken acknowledgement under 300 ms; return top matches in 3 seconds for the local index, with a longer search allowed when the browser is online. Reopen only after presenting the selected source.
- **cost:** A few cents per day for incremental indexing and near-zero per query after indexing; storage and browser-history extraction dominate, not inference.
- **security:** The index must remain local/encrypted and partition sensitive browser domains, secrets, and private notes. Never upload full history to the relay; send only query plus candidate IDs/snippets. Reopening an authenticated page is a side effect and needs an explicit owner policy entry; deletion must propagate to every derived index.
- **missing:** A durable cross-surface event index joining pendant bookmarks, browser page identity, and Mac note/file provenance; Read-only browser-history/session export and bounded Mac note/file search with source IDs; A retrieval protocol that returns verifiable quotes and supports deletion propagation across relay and Mac

### "Tell me when something I saved on the pendant or in my notes conflicts with a later email, calendar change, or source page, and show me both evidence items before suggesting a correction."
- **useful because:** The owner’s personal record currently accumulates stale commitments and claims silently. A contradiction monitor would catch changed meeting times, superseded decisions, and research corrections without pretending to rewrite the owner’s memory automatically.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Run incremental extraction and contradiction candidates on a background/cheap model; use deterministic timestamps, source URLs, and calendar/mail metadata to rank evidence. Use realtime only if the owner asks for an explanation aloud.
- **latency:** Process new or changed sources within 10 minutes; alert the pendant only for high-confidence, time-sensitive conflicts. Present a two-source comparison in under 3 seconds when opened.
- **cost:** A few cents per day for incremental entity/date extraction; most work is local diffing and hashing. Do not repeatedly resend unchanged mail or pages.
- **security:** Contradiction detection touches private mail and authenticated pages. Keep raw content on the Mac, send only redacted claims and provenance to the relay, and never auto-edit notes, calendar, or mail. Alerts need expiry and suppression controls to avoid exposing sensitive topics aloud.
- **missing:** A local claim/provenance index spanning pendant bookmarks, notes, calendar/mail, and browser pages; Incremental change feeds or hashes for browser pages and Mac sources; A conflict record format with evidence pairs, confidence, expiry, and owner resolution state


## Changes it proposed to its own stack

### `hardware` — Add a small secure element with monotonic counter and device-bound signing key to the next pendant revision, and have the firmware sign moment bookmarks, privacy-latch transitions, and diagnostic records before they leave the device.
- **owner gets:** The owner could trust that a saved research marker or privacy event was actually created by their worn device at a particular sequence/time, rather than being silently fabricated or duplicated by a reconnecting Mac or relay. This matters when the system is used as a durable personal log.
- effort: Moderate hardware spin plus firmware key provisioning, signed-event framing, relay verification, and a UI that distinguishes verified from unverifiable records. Existing one-button/one-LED interaction can remain unchanged.  ·  risk: Key loss or flash corruption could make new events unverifiable; use a factory recovery certificate and accept unsigned legacy records as explicitly unverified. Signing must not include microphone content or page text. Provisioning must prevent the development USB path from extracting the private key.
- cost: Roughly $0.50–$2 in components and negligible runtime power; firmware adds perhaps 8–20 KB flash and under 2 KB RAM depending on the cryptographic library.  ·  latency: A short signature operation adds tens of milliseconds to event enqueueing, hidden behind the existing local acknowledgement; no impact on the audio codec path if signing is deferred from the audio thread.
- security: Improves provenance and replay resistance, but creates a high-value device secret. Requires secure provisioning, monotonic-counter persistence, key rotation/revocation, and relay-side rejection of duplicate counters.
- depends on: A signed event envelope shared by pendant, relay, and Mac; Persistent monotonic-counter storage that survives reboot and offline queue retries; A provenance indicator in evidence cards and diagnostics


## What it asked for

_Nothing._
## Its own summary

This round I established the live surface (Safari bridge online with two tabs, active YouTube; Mac full-control/vision enabled) and recorded three owner-facing capabilities: (1) pendant “save this claim” creates a cited browser-page evidence card atomically in the workspace; (2) pendant “mark the last minute” records the active video’s exact timestamp and private note; (3) pendant “pause that” cancels the active Mac/browser job, checkpoints completed work, and supports later continuation. The first is the strongest new capability: it turns an intentional physical moment into durable, attributable research without requiring keyboard interaction. I also told faculty-action about it.

**Biggest unknown:** The missing connective contracts are now clear: browser media/page-context extraction with redaction, relay correlation/idempotency between pendant events and browser identity, and checkpoint semantics that distinguish completed from unsafe-to-repeat actions. The current browser bridge advertises capabilities=[] despite being online, so these are not blocked by hardware; they need implementation. I do not need Accessibility permission for the read-oriented versions. The owner still needs to explicitly configure which workspace writes and which unattended action classes are allowed, because FULL_CONTROL_MODE currently has no real policy gate.

