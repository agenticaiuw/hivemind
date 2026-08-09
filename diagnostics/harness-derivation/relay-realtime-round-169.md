# Harness derivation — relay-realtime — round 169

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I’m wearing the pendant and my Mac is nearby, use the USB link to do things reliably and faster; if it’s not, fall back to the cloud path."
- **useful because:** It makes the system feel solid: when the Mac is physically available, actions are more reliable and lower latency; when it’s not, the system still works.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** Realtime for intent capture; Mac planner for execution when present; fallback to cloud-readable sources when not.
- **latency:** Local path under a couple seconds; fallback depends on network and remote sources.
- **cost:** Local path is cheap; fallback may require web search or browser actions.
- **security:** USB access can be powerful; restrict to reversible operations by default and log actions for audit.
- **missing:** Reliable detection of Mac presence and readiness over USB; Explicit routing policy in relay based on device state; Fallback capability for server-side browsing (currently unresolved)

### "Tell me what’s going on with my devices right now—pendant, bridge, and Mac—and whether anything needs attention."
- **useful because:** Quick health checks prevent confusion. The owner can understand whether a failure is audio, connectivity, or a downstream tool.
- **path:** relay → mac-bridge → pendant
- **model tier:** Realtime for spoken status; no heavy planning needed.
- **latency:** Under a second for cached state; a few seconds if polling mac status.
- **cost:** Low; dominated by a couple status calls.
- **security:** Device IDs and operational metrics are sensitive; share only what’s needed and avoid exposing tokens or internal addresses.
- **missing:** A live devices status route on the relay (previously absent); A normalized health snapshot combining relay and Mac agent status

### "When I say “show me that,” turn your spoken answer into a live visual handoff on my Mac: open the exact page, file, diff, chart, or annotated screenshot you were talking about, with the relevant passage highlighted."
- **useful because:** A speaker-only pendant can explain something but cannot point at it. This would let the owner move from a glance-free voice question to the precise visual evidence without searching or repeating the request.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime relay for intent and a concise spoken bridge; mac-vision for screenshots and highlighting; mac-planner for opening files/apps; browser-extension for authenticated page anchors; no expensive model for the handoff itself.
- **latency:** Acknowledge in under 500 ms; open the visual target within 5 seconds; if the Mac is offline, retain the handoff until it returns.
- **cost:** About $0.01–$0.05 per handoff, dominated by one vision call only when an annotated screenshot or UI target must be located; simple URLs/files are near-zero model cost.
- **security:** Screenshots and authenticated URLs remain on the owner’s Mac and relay metadata should be minimized. Never expose a private page through a public dashboard; expire handoff links and bind them to the paired device.
- **missing:** A relay-to-Mac visual-handoff message with typed targets (url, file, app, region, screenshot); A Mac action that can highlight a text range or draw an annotation and clear it afterward; A paired companion/dashboard surface that can display a returned image when the target is not on the Mac

### "Let the pendant act as a microphone for a live “decision tape”: while I talk through a problem, keep a private, timestamped chain of claims, alternatives, and decisions, then when I say “close the tape,” put the resulting decision record and follow-up actions into the right Mac files and apps."
- **useful because:** The owner often has the useful reasoning while away from the keyboard. This turns an unstructured voice session into an auditable decision artifact rather than a memo that must later be rewritten by hand.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension
- **model tier:** Realtime relay segments and acknowledges speech; a cheaper background model extracts claims and decisions after closure; mac-planner/mac-terminal writes the approved destinations and returns typed receipts.
- **latency:** Live acknowledgements under 700 ms; close-and-summarize in under 30 seconds for a 10-minute tape; writing can continue asynchronously with a spoken completion alert.
- **cost:** Roughly $0.03–$0.15 per tape, dominated by transcription and one background extraction pass; storage and Mac actions are negligible.
- **security:** Decision tapes can contain secrets and should be encrypted, retained only until closure plus a configurable period, and never sent to third-party browser pages unless explicitly named. The relay must preserve quotations versus inferred decisions.
- **missing:** A session-scoped append-only transcript/claim stream distinct from the existing offline memo outbox; A background extraction job that emits typed claim/decision/action objects with source timestamps; A destination resolver for Notes, Markdown/project files, Reminders, and issue trackers plus an owner-visible receipt


## Changes it proposed to its own stack

### `interaction` — Add a low-latency “question fork” protocol: when the owner says “hold that thought,” freeze the current spoken response and assign it a fork id; the owner can ask a side question, say “return to fork,” and resume at the exact sentence with no re-generation. Persist only the short audio/text cursor and fork metadata, not ambient audio.
- **owner gets:** The owner can interrupt a long explanation without losing their place. Today a single-button interruption can request a shorter report, but it cannot preserve multiple conversational threads or return precisely to the abandoned point.
- effort: Medium: relay session state, pendant cursor control, and a small resume contract in the audio stream; no new model is required.  ·  risk: A stale fork could resume an outdated answer or reveal private context to the wrong session. Expire forks quickly, bind them to the device/session, and fall back to a spoken restatement when the source is gone.
- cost: Near-zero API cost; a few hundred bytes of session metadata per fork.  ·  latency: Fork and return should be sub-200 ms locally; resumption may take one streaming chunk if audio was not retained.
- security: Only short-lived encrypted cursor/context identifiers leave the relay; do not persist raw audio beyond the existing delivery policy.
- depends on: A typed audio-stream cursor/resume event between relay and pendant; Session-scoped fork storage in the relay; Integration with the existing spoken_status_interrupt behavior

### `context` — Create an owner-invoked “current moment capsule” that atomically captures the focused Mac app/window title, selected text or clipboard, active browser tab plus readable page excerpt, and a timestamped screenshot, then gives the relay one short-lived capsule id. The relay can answer a pendant question against that exact moment instead of mixing stale machine-context, browser state, and conversation history.
- **owner gets:** “What am I looking at?” and “fix the thing I just selected” would finally refer to the same concrete state across the pendant, Mac, and authenticated browser. It eliminates the frustrating need to describe a screen the owner cannot see while speaking.
- effort: Medium-high: a Mac harness collector, browser inspection join, encrypted relay capsule store, and strict expiry; mac-vision should fill gaps only when the deterministic collectors cannot read the UI.  ·  risk: The capsule may contain passwords, private messages, or clipboard secrets. Capture must be explicitly invoked, redact known secret fields where possible, encrypt in transit and at rest, expire within minutes, and never be silently sampled.
- cost: One small storage record and optional screenshot per invocation; model cost is near zero for deterministic collection, with vision cost only for unreadable UI.  ·  latency: Target under 1.5 seconds while the Mac is online; relay answers can begin streaming immediately after the capsule arrives.
- security: This is a high-sensitivity context surface. Bind capsule ids to the paired pendant/session, prevent URL sharing, audit reads, and delete on expiry.
- depends on: A Mac collector for focused-window, selection, clipboard, and screenshot state; The existing browser inspection/read-page path joined into the same snapshot; A short-lived encrypted relay context store and a typed capsule reference accepted by the voice turn


## What it asked for

_Nothing._
