# Harness derivation — mac-planner — round 278

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-access-and-browser-state** — The AI Pendant Agent currently has Accessibility and Screen Recording trusted, synthesized input verified, Safari foreground, and four browser sessions. The browser tabs observed are YouTube, Google News, and two test forms; no Safari Reading List tab is exposed by the current browser session inventory.
  - evidence: mac_readonly_inspect operation=foreground_app/running_apps returned GET /observe HTTP 200 at 2026-08-09T02:03:03Z with accessibility.trusted=true, screenRecording=true, inputReachability.status=verified, foregroundApp=Safari, browser.sessions=4.

## Capabilities it proposed

### ""What are the four latest items on my Safari Reading List? Give me one short sentence, and open the newest one if I say 'open it'.""
- **useful because:** The owner has asked this repeatedly and it currently fails despite an online Safari session. It is a small, concrete demonstration that the pendant can reach a logged-in browser through the Mac without exposing page contents to the relay beyond the requested titles. The relay ranks the list and speaks only four titles; the Mac/browser node keeps URLs and session cookies local. A follow-up 'open it' becomes a separate, explicit navigation action.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for extracting and ranking four titles; realtime only for the spoken answer and the explicit follow-up command
- **latency:** Under 5 seconds for read; under 2 seconds after an explicit open-it command. Browser inspection dominates.
- **cost:** About $0.001–$0.01 per read depending on whether title extraction is deterministic or uses a small model; realtime speech is already in the call cost.
- **security:** Safari stays on the Mac/browser surface; send only title, URL host, and position to the relay by default, never cookies or page body. Opening a URL is reversible navigation but should be logged; destructive browser actions remain outside this capability.
- **missing:** A browser command/inspection adapter that can query Safari Reading List rather than only the active page; stable structured result fields (title,url,addedAt); a relay intent for 'open item N' that targets the same browser session.

### ""Run a complete pendant audio health check now, tell me whether today's hardware is trustworthy, and file a concise bug report automatically if any acceptance number fails.""
- **useful because:** The owner can test the actual pendant and ESP32 bridge attached by USB today, but currently a fixture produces measurements without turning them into an owner-level verdict or a durable report. This makes the system self-maintaining: the worn node emits the known synthetic fixture, the Mac captures bounded UART output from both chips, the relay compares results with the shipped thresholds, and the Mac writes a timestamped report into ~/AI-Pendant-Workspace. It reports 'pass' or the first actionable failure over the pendant instead of requiring firmware expertise.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Deterministic parser and threshold evaluator first; cheap background model only to summarize failures. Realtime is unnecessary except speaking the final verdict.
- **latency:** 30–90 seconds for the fixture and USB capture; under 3 seconds to speak the verdict after the logs arrive. Device playback/encoding and serial capture dominate.
- **cost:** Usually under $0.01: parsing and thresholds are local; an optional small-model summary is the only API cost.
- **security:** The fixture must generate synthetic audio only and never read microphone content. Write only inside ~/AI-Pendant-Workspace; redact serial identifiers and raw logs from spoken output. Filing means creating a local Markdown report, not sending an issue externally without a separate command.
- **missing:** A bounded, structured USB-serial read action for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; a fixture trigger/status protocol over that read-only bench channel; a threshold evaluator that understands mic_drops, tx_starved, alias rejection, decode/encode time, and clipping; a durable report receipt linked to the run.

### ""Use the page I'm on to draft the reply, read the exact draft to me on the pendant, and send it only after I say 'send'.""
- **useful because:** This closes the most dangerous gap in browser automation: the system can understand a logged-in page and type, but the owner needs an exact spoken checkpoint before an external message leaves. The browser keeps the authenticated session and performs the send; the relay presents a redacted preview on the pendant; the Mac agent records the draft hash and the owner's explicit second-turn intent. It is useful for email, support portals, and forms without giving the model unilateral authority to communicate.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime for extracting the requested fields and speaking the exact draft; a cheap deterministic checker for recipient/domain, attachments, and changed fields. No background model needed.
- **latency:** Draft in 5–10 seconds, spoken preview immediately, send within 2 seconds after the explicit command. Browser DOM inspection and page navigation dominate.
- **cost:** About $0.01–$0.05 per draft depending on model context; confirmation turns are cheap relative to drafting.
- **security:** Never send on the first turn. Bind confirmation to a one-time draft hash, recipient set, and browser session; expire it on page change or timeout. Keep cookies and full page body on the browser node, redact secrets from relay logs, and show recipients/attachments aloud. This honors the owner's destructive-action confirmation policy.
- **missing:** A browser-side structured draft/send transaction with a stable draft hash and recipient/attachment extraction; a relay confirmation intent that carries the hash; a Mac/browser result receipt proving what was submitted; explicit policy configuration for which domains/forms are eligible.

### ""I was away for the last two hours—what changed, what needs me, and what can wait?""
- **useful because:** Today the hive can read isolated sources, but it cannot reconstruct a trustworthy interruption summary. This capability would correlate Calendar and Mail on the Mac, browser-session changes, relay job completions, and pendant moment bookmarks into a time-bounded, deduplicated account of what actually changed while the owner was away. It would speak three buckets—needs me, FYI, and safely deferred—and preserve links back to the source so the owner can inspect one item instead of replaying every notification.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Cheap background event normalizer and deduplicator; realtime only to answer the owner's spoken question and read the short result. Use a stronger model only when sources conflict or importance is ambiguous.
- **latency:** 10 seconds after asking, with a cached rolling timeline updated continuously. Source collection and conflict resolution dominate; speech itself should be immediate.
- **cost:** $0.005–$0.03 per refresh, mostly model ranking of genuinely changed items; deterministic event collection and hashing are local.
- **security:** Do not retain a second copy of mail bodies or private page content. Store event hashes, titles, sender/domain, timestamps, and redacted snippets with source-specific retention. Exclude secure-input/browser form fields and require the owner's existing destructive-action policy before any suggested follow-up is executed.
- **missing:** A durable cross-surface event journal with source timestamps and deduplication IDs; Mac hooks that emit Calendar/Mail changes and browser navigation/title changes without scraping sensitive bodies; pendant bookmark upload attribution; relay-side interruption-window query and importance ranking; dashboard provenance view showing exactly why an item was classified as needs-me.

### ""Why are you telling me that? Show me the three pieces of evidence, and tell me which part is uncertain.""
- **useful because:** The owner cannot currently interrogate the basis of a spoken answer across surfaces. This gives every answer a compact evidence packet: source, timestamp, excerpt or redacted field, transformations applied, and an uncertainty reason. The relay speaks a one-sentence explanation; the Mac or browser opens the exact local source on request. It turns the hive from an opaque assistant into something the owner can audit without dumping all private context into the conversation.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic provenance assembly; a small model may summarize conflicting evidence, while realtime only handles the spoken follow-up.
- **latency:** Under 2 seconds for the first explanation from cached provenance; under 5 seconds to open a selected source locally. Redaction and source lookup dominate.
- **cost:** Usually below $0.005 because provenance is generated alongside each answer; model cost occurs only for conflict summaries.
- **security:** Evidence stays on its originating surface by default. The relay receives identifiers and redacted excerpts, not full mail or page bodies. Opening a source requires the same session and local permissions that created it; sensitive evidence expires and is excluded from spoken playback unless explicitly requested.
- **missing:** A provenance envelope required on every relay answer; source-span and transformation IDs in Calendar/Mail/browser/Mac readers; confidence and conflict fields; a local deep-link/open-source resolver; dashboard UI for evidence and uncertainty.

### ""Continue this on my Mac.""
- **useful because:** A spoken pendant exchange currently ends as audio; the owner has to reconstruct the subject manually on the Mac. This would create a short-lived, encrypted handoff containing the active question, selected evidence, unresolved choices, and next action, then have the Mac open the relevant local note, calendar item, browser session, or draft without replaying private conversation history. The owner gets a seamless transition from walking to desk work, while each surface retains control of its own secrets.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime to extract the handoff intent and summarize the active thread; deterministic local routing to open targets. No background model beyond optional expiry cleanup.
- **latency:** Under 4 seconds from spoken command to a prepared Mac workspace. Relay handoff creation and browser/local deep-link opening dominate.
- **cost:** $0.005–$0.02 per handoff, mostly one short realtime summary; local routing and encryption are negligible.
- **security:** Handoffs are encrypted, single-use, and expire quickly. Never copy cookies, full mail bodies, or microphone audio to the Mac handoff; pass opaque source references and redacted summaries, then resolve content locally under the existing session. Opening is non-destructive; sending or editing remains a separate explicit action.
- **missing:** A cross-surface handoff envelope and claim/expiry protocol; relay intent that binds a handoff to the current conversation; Mac resolver for opaque Calendar/Mail/browser/workspace references; browser command to focus or open a target tab; visible receipt showing what was transferred and what was intentionally omitted.


## Changes it proposed to its own stack

### `hardware` — On the next pendant revision, add a physically latching microphone/speaker privacy switch with a hardwired dual-colour privacy indicator, independent of the nRF9160 firmware and relay. Route the switch through hardware audio gating so it remains effective during firmware crashes, modem reconnects, and USB bench sessions; expose its state as a read-only GPIO event when the MCU is alive.
- **owner gets:** The owner can know by touch and sight that neither direction is active, even in a dead zone or when software is misbehaving. The current board has one LED and software privacy latch, so an accidental press or a crashed task can make privacy state ambiguous. A hardware interlock is the one trust feature that should not depend on the hive being online.
- effort: Moderate board respin: latching switch, audio-gate components, indicator, enclosure cutout, boot-state handling, and validation of pop-free gating at 24 kHz. Firmware and relay then only report state; they cannot override OFF.  ·  risk: Incorrect analog gating could click or bias the codec; validate with the existing audio-quality probe and ensure switch-off is fail-closed. If the GPIO is unreadable after reset, the physical indicator still wins. Recovery is simply switch back on; no network round trip is required.
- cost: Roughly $2–$6 BOM increase and a few mA for the indicator, with negligible runtime impact compared with modem/audio draw.  ·  latency: Immediate hardware mute, faster than any firmware or LTE command.
- security: Strongly positive: privacy OFF cannot be bypassed by relay, browser, or Mac automation. The relay receives only a boolean state transition when available.
- depends on: A board revision and enclosure change; audio-gate design compatible with the shipped 24 kHz path; firmware support for reporting, not controlling, the interlock.


## What it asked for

_Nothing._
## Its own summary

Fresh discovery found the Mac is more capable than the inherited notes said: AI Pendant Agent has Accessibility and Screen Recording, synthesized input is verified, Safari is foreground, and four browser sessions are live. I produced three forward proposals: (1) exact spoken draft plus one-time hash-bound confirmation before any browser send, (2) an end-to-end pendant audio health check that evaluates the shipped thresholds and writes a local report, and (3) a next-revision hardware privacy interlock. The Reading List idea was recorded as too close to an existing backlog item, so I will not repeat it.

**Biggest unknown:** The most valuable missing seam is still structured USB-serial bench I/O for the physically attached nRF9160 and ESP32. Without it, the accepted diagnostic fixture cannot become an owner-facing automatic trust verdict. The other concrete gap is a browser adapter for Safari Reading List and a browser draft/send transaction with a stable confirmation hash. Also, mac_readonly_inspect browser_tabs remains resolver-ambiguous between browser inspection capabilities even though GET /observe itself is working.

