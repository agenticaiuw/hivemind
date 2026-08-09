# Harness derivation — relay-realtime — round 215

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I’m away from my Mac, read my status and help me decide what to do next."
- **useful because:** A quick spoken triage that doesn’t require the Mac to be awake: what’s queued, what failed, what’s waiting for attention.
- **path:** relay-realtime → relay
- **model tier:** Realtime for conversation; no need to wake the Mac.
- **latency:** About 1 second for a short summary.
- **cost:** Very low; reads relay-side job state only.
- **security:** Job descriptions may contain sensitive filenames or app names. Summarize only what is already present in the relay’s spoken field; avoid exposing paths.
- **missing:** A relay-side intent to summarize latest jobs without a jobId (or a tool like relay_job_status that accepts 'latest')

### "Use the pendant as a live voice front door to my browser sessions when my Mac is online, but fall back gracefully when it’s not."
- **useful because:** The owner can say what they want, and the system routes it to a browser session when possible; when the Mac is offline, it offers a read-only web path instead of failing silently.
- **path:** relay-realtime → mac-planner → browser-extension
- **model tier:** Realtime only for intent capture; hand over to mac-planner for multi-step browser work.
- **latency:** Under 2 seconds to confirm routing; the actual browsing can take longer.
- **cost:** Moderate; main cost is the browser automation on the Mac.
- **security:** Authenticated sessions are sensitive; never read or exfiltrate secrets. Confirm before sending messages or purchases.
- **missing:** A reliable route to discover browser session availability from the relay without probing the Mac; A server-side browser fallback (server_browser_actions) if it’s implemented

### "“Research this for me using whatever I already have open, my Mac files, and the web; give me the answer and leave me a source-linked dossier I can ask about later.”"
- **useful because:** Today each surface is queried separately and the relay cannot combine authenticated browser context, local files, and public sources into one trustworthy result. This would make the pendant a practical research front door while preserving provenance and letting follow-up questions resolve to the exact evidence.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Realtime handles the spoken scope and a concise answer; background mac-planner and browser workers perform the fan-out and evidence extraction; a cheaper synthesis model builds the dossier.
- **latency:** A spoken acknowledgement within 1 s, first answer in 10–20 s, dossier completion within 60 s. Partial evidence should be speakable while slower sources finish.
- **cost:** Roughly $0.05–$0.30 per request; browser/file extraction and synthesis dominate, not the short realtime turn.
- **security:** Local files and authenticated pages leave their surfaces only to the relay and authorized workers. Every claim needs a source pointer and an explicit unavailable-source marker; never imply a source was checked when Mac or browser was offline. Require confirmation before sharing the dossier externally.
- **missing:** A fan-out job that can invoke Mac-local file search and the authenticated browser in one task; A provenance graph linking spoken claims to URLs, file paths, timestamps, and extraction snippets; A durable dossier store and a voice follow-up resolver over its claim graph

### "“Watch for a problem that only becomes important when several things line up—like a meeting moving, a related email arriving, and the project page changing—and tell me only when the combination matters.”"
- **useful because:** Single-source alerts are noisy and miss the meaning created by correlation. A cross-surface sentinel would turn the always-awake relay into a quiet personal early-warning system, especially while the owner is away from the Mac.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Cheap scheduled/background workers collect diffs; a small judgement model scores cross-source correlation; realtime is used only to phrase a concise alert when a threshold is crossed.
- **latency:** Checks every 5–15 minutes when configured, with an alert within one check interval. No conversational wait is needed.
- **cost:** About $0.01–$0.10 per check depending on page and mail/calendar diff volume; correlation and authenticated browser reads dominate.
- **security:** The sentinel must retain only hashes, extracted fields, and minimal snippets, not whole mail or pages. User-defined scopes and expiry are required. Alert text must avoid leaking sensitive details to anyone nearby; provide a terse mode and a button-press detail mode.
- **missing:** A cross-surface watch schema with joins, windows, and deduplication rather than one URL per watch; Connectors for Mac Calendar/Mail/files and authenticated browser sessions feeding normalized change events; A durable event correlation store and relay-to-pendant alert delivery with suppression explanations

### "“When I say ‘make this understandable’, use the thing I’m looking at or working on, produce a plain-language explanation with examples, and let me ask follow-ups against the exact paragraph or screen.”"
- **useful because:** The pendant currently hears a request but has no reliable shared referent for ‘this’. Joining the current Safari tab, focused Mac document, and a spoken pointer would make vague wearable commands useful without forcing the owner to dictate URLs, filenames, or copied text.
- **path:** pendant → relay → mac-vision → mac-planner → browser
- **model tier:** Realtime resolves the utterance and asks at most one ambiguity question; mac-vision/browser extract the focused artifact; a cheaper model creates the explanation and anchored follow-up index.
- **latency:** Resolve the referent in under 2 s, speak a useful first explanation in 8–12 s, and support later paragraph-level follow-ups without re-reading the whole artifact.
- **cost:** Approximately $0.03–$0.15 per explanation; screenshot/OCR or page extraction and the explanation context are the main costs.
- **security:** The current screen may contain secrets. The relay must receive only the selected region/page text when possible, show which artifact was used, and discard unselected screen content. Never silently act on the artifact; explanation is read-only.
- **missing:** A current-context snapshot contract from Mac vision, focused app, and browser tab with timestamp; A referent resolver that binds pronouns and deictic phrases to an immutable artifact version; An anchored spoken navigation format (paragraph/region IDs) that survives a later screen change


## Changes it proposed to its own stack

### `relay` — Implement a real completion notification path by wiring job_completion_watch to relay_event_push and the existing inbox/alert mechanism, so job outcomes can be delivered after the voice session ends.
- **owner gets:** They can start a task and move on, and still get a clear outcome later without polling or re-asking.
- effort: Medium. Requires implementing the watch, event delivery, and a small policy for which outcomes deserve alerts.  ·  risk: Alert spam or sensitive content leakage. Mitigate with throttling, minimal spoken summaries, and honoring existing confirmation rules for high-impact actions.
- cost: Low to moderate; main cost is occasional polling and message delivery.  ·  latency: No impact on conversational latency; work happens after handoff.
- security: Potential disclosure of task names in spoken alerts; use verbatim pre-sized spoken fields and avoid extra detail.
- depends on: A working relay_event_push implementation or equivalent event delivery route

### `model-routing` — Add a deterministic routing table for pendant voice intents that maps to existing tools (get_mac_status, mac_run_actions, browser_run_actions, mac_delegate, web_search) without free-form intent strings, and log the chosen route for observability.
- **owner gets:** More reliable voice behavior: less misrouting, fewer confusing failures, and better explainability when something goes wrong.
- effort: Medium. Requires defining a small enum of intents and mapping rules, plus logging.  ·  risk: Overly rigid routing could block novel commands. Mitigate by falling back to mac_delegate for ambiguous cases.
- cost: Low; mostly logic and logging.  ·  latency: Small improvement by avoiding misroutes and retries.
- security: Logging must avoid sensitive content; store intent class and tool used, not raw utterances.

### `hardware` — Add a coin/LRA haptic actuator and a dedicated haptic driver to the pendant, with firmware patterns for recording, staged reply, urgent inbox alert, failed delivery, and owner acknowledgement. Keep audio and the existing single LED, but move private state signalling to haptics; expose a small event API so the relay can select urgency and the pendant can acknowledge delivery locally.
- **owner gets:** The owner can know whether a request was accepted, waiting, failed, or urgently needs attention without listening aloud or looking at the pendant—especially in meetings and public places. It also removes the current single-LED ambiguity instead of adding more competing blink patterns.
- effort: Moderate hardware revision plus firmware event/state work; prototype with a 10–12 mm LRA, driver, enclosure isolation, and measured patterns before committing the jewellery enclosure.  ·  risk: Vibration can be distracting or audible against the body, and a bad state mapping could create false urgency. Make all patterns short, provide a quiet mode, rate-limit repeats, and fall back to the LED/audio semantics if the actuator self-test fails.
- cost: Approximately $2–$6 in components and PCB/enclosure changes, with roughly 10–30 mA only during short pulses and negligible idle draw.  ·  latency: Immediate local feedback, typically under 50 ms after a firmware event; no relay round trip required for local states.
- security: Improves privacy because status can be conveyed without spoken audio. Do not encode sensitive content in patterns; use only urgency/state classes.
- depends on: A pendant event vocabulary shared with the relay inbox and staged-reply state; A firmware self-test and owner-configurable quiet schedule; Physical enclosure space and a revised power budget


## What it asked for

### `t23-ow4p` (tool) — relay_task_digest
- why: Owners need a quick spoken triage of recent tasks without recalling job IDs. Today, relay_job_status requires a reference or job id, and GET /jobs is an HTTP route not guaranteed to be available as a low-latency voice tool.

```json
{
  "type": "object",
  "properties": {
    "scope": {
      "type": "string",
      "enum": [
        "latest",
        "today",
        "unacknowledged"
      ],
      "description": "Which set of jobs to summarize."
    },
    "max_items": {
      "type": "integer",
      "minimum": 1,
      "maximum": 10,
      "description": "Upper bound on jobs included in the summary."
    }
  },
  "required": [
    "scope"
  ]
}
```

