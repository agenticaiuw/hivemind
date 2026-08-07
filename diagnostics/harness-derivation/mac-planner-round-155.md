# Harness derivation — mac-planner — round 155

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Even without LTE, let me press the pendant and talk to you through my Mac; carry my voice and your answer over the USB-connected pendant, and keep using the Mac’s apps and browser as if the pendant were online.”"
- **useful because:** The pendant is physically attached to the Mac today while LTE registration is not. This would make the wearable genuinely useful now, with automatic LTE-to-USB fallback rather than a dead device whenever the modem is unavailable. The Mac can execute desktop/browser work and the answer can return to the device’s speaker.
- **path:** pendant → mac-planner → relay-realtime → browser-extension → dashboard-ux
- **model tier:** Realtime model only for the conversational turn; a small router handles transport selection and a slower model handles any follow-up plan.
- **latency:** USB serial framing and route selection under 100 ms; first spoken response under 1.5 s; resume the same conversation when LTE later returns.
- **cost:** Negligible incremental API cost beyond the voice turn; engineering is dominated by serial framing, reconnect, and audio buffering tests.
- **security:** USB must be bound to the known pendant serial identity and a per-device session key; never expose the Mac bridge to arbitrary serial devices. Audio and commands traverse the local Mac and relay, so show a visible tethered indicator and retain no extra recordings.
- **missing:** A Mac serial bridge for /dev/cu.usbmodem00096003658* that presents the pendant as an authenticated relay transport; A transport multiplexer in the relay that can switch LTE and USB without creating a second conversation; A small Opus/packet adaptation layer compatible with the existing nRF9160 and ESP32 audio path; Hotplug and reconnect tests on the live hardware

### "“When I reconnect the pendant to my Mac after being away, give me a spoken ‘return queue’: what changed in my calendar, mail, and logged-in browser tabs, plus the next three desktop actions you can safely prepare.”"
- **useful because:** The physical reconnect is a reliable arrival signal that neither a cloud schedule nor a browser tab can provide. It turns an interruption or commute into a bounded re-entry instead of forcing the owner to reconstruct state across apps; preparation can happen while they keep working and nothing is submitted or sent.
- **path:** pendant → mac-planner → relay-realtime → browser-extension → dashboard-ux
- **model tier:** Cheap background model computes diffs and ranks the queue; realtime model is used only to speak the concise result or answer follow-ups.
- **latency:** Detect serial attach within 2 s, compute a first queue within 20 s, and speak only after the owner presses the pendant button or says ‘what changed?’
- **cost:** One bounded background synthesis per reconnect, typically cents or less; the dominant cost is authenticated page extraction and calendar/mail reads, not generation.
- **security:** Only pre-enrolled browser sessions and the authorized Calendar/Mail account may be read. Include source links and timestamps; redact message bodies by default. Never auto-open or mutate a page, and provide a local pause switch that suppresses the trigger.
- **missing:** A serial attach/detach event publisher from the Mac bridge to the relay; A durable since-last-seen cursor shared by Calendar/Mail and authenticated page watches; A reconnect-triggered routine with quiet hours and deduplication; A spoken queue protocol that can return a short answer to the pendant and a detailed cited view to the dashboard

### "“Pin this page for later.” When I say that on the pendant, save the exact authenticated browser page and the relevant Mac context into a local, cited handoff packet, then remind me on the pendant when the packet is ready."
- **useful because:** A spoken ‘pin’ is faster and safer than interrupting work to copy URLs, screenshots, and notes. The browser session supplies private page evidence, the Mac supplies the local project context and durable file, and the pendant supplies an immediate capture gesture plus completion notification. It preserves what the page said at capture time instead of relying on a URL that may later change or expire.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard-ux
- **model tier:** Small background extraction model normalizes the page and creates citations; realtime model only resolves which open tab ‘this’ means and confirms completion.
- **latency:** Acknowledge in under 500 ms; capture current tab metadata immediately; write the packet within 10 s for ordinary pages and report partial capture if the session disappears.
- **cost:** Low: one bounded extraction and short metadata summary. Storage is a small local Markdown/JSON pair per capture; no ongoing polling.
- **security:** The packet may contain sensitive authenticated content. Store it in an owner-selected encrypted/local folder, redact bodies unless explicitly requested, include URL/tab/time and a content hash, and never upload the packet merely to make it searchable. If tab identity is ambiguous, ask rather than guess.
- **missing:** A browser command that atomically snapshots the active tab’s URL, title, selected text, and bounded readable region; A pendant intent carrying a capture id and tab affinity over the active transport; A Mac packet writer that creates Markdown plus machine-readable provenance and reports a receipt; A retention and local-delete UI for these packets

### "“Bookmark this moment.” Have the pendant mark the exact point in time, and later let me ask what I was doing then: the active calendar event, Mac app/file, browser tab, and a short transcript context, all linked in one private timeline entry."
- **useful because:** People lose the reason they opened a page or the decision made halfway through a meeting. A physical pendant gesture creates a reliable temporal marker without stopping work; the Mac contributes app/file state, the browser contributes the authenticated tab, and the relay makes the marker searchable later. This is a memory of context, not another reminder or generic transcript.
- **path:** pendant → mac-planner → relay-realtime → browser-extension → dashboard-ux
- **model tier:** A cheap background model extracts a short label and entities; realtime is used only when the owner asks a spoken retrospective question.
- **latency:** Acknowledge the gesture locally in under 150 ms; persist the raw marker immediately; enrich it within 5 seconds and make retrospective queries answer in under 2 seconds.
- **cost:** Low per marker: metadata is nearly free and only a bounded transcript window is summarized. Storage is a small encrypted record plus optional short audio reference.
- **security:** This can become a sensitive activity log. Default to no continuous audio retention: retain only a configurable few seconds around an explicit marker, encrypt locally, redact message bodies, show the source app/tab and retention expiry, and support a physical long-press delete.
- **missing:** A pendant marker event with a monotonic timestamp and local acknowledgement; A Mac snapshot API that atomically records foreground app, open file, and browser tab without requiring screen capture; A timeline index joining marker time to Calendar/Mail/browser provenance and bounded transcript context; A spoken query route that returns cited timeline evidence rather than inventing context

### "“Is my plan still consistent?” Compare the current Calendar event, relevant Mail, authenticated reservation/account pages, and the files open on my Mac; tell me only about contradictions, stale assumptions, or missing confirmations, with evidence and a suggested fix."
- **useful because:** Today each source can look individually correct while the overall plan is impossible—for example a meeting moved after travel was booked or a deadline in a document no longer matches the calendar. The pendant gives a fast question, the relay reconciles sources, the browser supplies private account truth, and the Mac supplies the artifact actually being edited.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard-ux
- **model tier:** Background extraction and deterministic date/entity checks do most of the work; realtime is reserved for the concise spoken answer and follow-up questions.
- **latency:** Return a first contradiction set in 5 seconds for already-open sources; cite every claim and label unresolved sources instead of guessing.
- **cost:** Low-to-moderate background cost, dominated by authenticated page reads; cache normalized facts by source timestamp so repeated questions are cheap.
- **security:** Cross-source joining can reveal more than any one source. Use a per-request source allowlist, redact unrelated mail/page content, keep evidence local where possible, and never change reservations, files, or messages automatically.
- **missing:** A typed cross-source fact joiner with temporal validity and contradiction explanations; A way for the pendant request to name or infer a bounded plan/topic without uploading the entire context; Browser and Mac provenance records normalized to common timestamps and entity ids; A cited conflict report rendered both as speech and a detailed dashboard view

### "“What commitments did I make today?” Search my spoken markers, Calendar, Mail, open browser work, and edited Mac documents for explicit promises or next actions; return a deduplicated commitment ledger with source quotes, due dates, and a one-tap way to prepare—not send—the next step."
- **useful because:** Important promises are scattered across conversation, email, meetings, and documents. A wearable query makes the ledger available while walking, while the Mac and browser can gather the evidence that the pendant cannot reach. It prevents silent dropped commitments without turning every mention into a task.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard-ux
- **model tier:** A cheaper background model extracts candidate commitments and dates; a judgment pass merges duplicates and assigns confidence; realtime only speaks the short list.
- **latency:** Incrementally update after each explicit marker or source change; answer a spoken query in under 3 seconds from the index, with slower enrichment allowed afterward.
- **cost:** Small ongoing extraction cost with aggressive deduplication; storage is compact structured records plus short source excerpts.
- **security:** Commitments may expose confidential projects. Store provenance and sensitivity labels, keep quotes bounded and redacted, restrict cross-account joins, and require an explicit owner request before preparing any external communication.
- **missing:** Commitment extraction from bounded transcript and source snippets with confidence and negation handling; A durable ledger schema for promise, owner, due date, evidence, status, and sensitivity; Cross-device incremental updates from Mac journal, browser provenance, Calendar, and Mail; A preparation workflow that creates a draft/checklist while preserving a strict no-send boundary


## Changes it proposed to its own stack

### `mac-harness` — Add a live USB pendant companion to the Mac agent: claim only /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA, expose attach/detach and RSSI/link/audio counters as events, bridge framed Opus/control packets to the relay, and persist a bounded reconnect journal. Keep it independent of the desktop action executor so browser and app work cannot be blocked by audio reconnects.
- **owner gets:** The owner can wear and test the pendant today even though LTE is not registered, and will know whether a missed response came from the radio, serial link, audio bridge, or model. Reconnecting the cable should resume the same conversation instead of silently losing it.
- effort: Medium-high: serial framing, device identity, concurrent audio buffering, reconnect state machine, and a physical soak test.  ·  risk: Bad framing could corrupt audio or leave a stale serial handle. Recover by closing/reopening on checksum failure, bounded ring buffers, and a visible ‘tether inactive’ status; never let it execute arbitrary Mac commands from raw serial input.
- cost: No per-call API increase; modest local CPU and under 1 W USB power for the bridge, plus engineering/test time.  ·  latency: Adds roughly 20–80 ms locally; should reduce end-to-end latency versus an unavailable LTE path.
- security: New local attack surface at USB serial. Require an enrolled device certificate/session key and reject all unpaired serial identities; keep control and audio channels separate.
- depends on: A small serial daemon or Node module with access to the two live USB device paths; Relay transport multiplexing and conversation resume tokens; A bounded Opus adaptation layer matching the current nRF9160/ESP32 frame formats


## What it asked for

_Nothing._
## Its own summary

Round 155 produced three new cross-surface capabilities and one concrete change. (1) USB-tethered pendant voice fallback: because the nRF9160 and ESP32 are physically connected now while LTE is unregistered, route audio/control over authenticated serial and preserve the same relay conversation. (2) Reconnect return queue: use pendant attach as a real arrival signal, diff Calendar/Mail/authenticated tabs since last seen, and speak only a bounded prioritized queue. (3) Spoken browser pin: “Pin this page for later” captures the exact current authenticated tab plus Mac context into a local cited Markdown/JSON packet and reports completion to the pendant. I also proposed the Mac USB companion daemon with device binding, framed Opus/control channels, counters, and reconnect journal, and notified relay-realtime.

**Biggest unknown:** The newly granted mac_readonly_inspect is still schema-only: calls for running apps, browser tabs, and Accessibility state return “no implementation yet.” I still need an implemented read-only Mac inspection bridge, plus the actual serial companion/relay transport multiplexer. Without those, I cannot verify the live USB devices or safely resolve “this tab” and reconnect state in production.

