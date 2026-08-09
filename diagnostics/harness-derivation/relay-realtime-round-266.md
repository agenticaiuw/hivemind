# Harness derivation — relay-realtime — round 266

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“When I’m on a call, translate what the other person says into my ear, and translate my reply back in their language.”"
- **useful because:** This would turn the worn pendant into a private, low-latency interpreter for calls and in-person conversations: the Mac supplies the active call or meeting audio, while the pendant supplies the owner’s speech and discreet translated playback. The owner can participate without staring at a screen or handing a phone around.
- **path:** pendant → relay → mac-planner → mac-vision
- **model tier:** Realtime for speech segmentation, translation, and short turn-taking; a cheaper background model may detect language and maintain a glossary between turns.
- **latency:** Under 1.5 seconds from the end of the other speaker’s utterance to translated playback; under 800 ms for language identification after the first phrase.
- **cost:** Roughly $0.01–$0.05 per minute depending on realtime audio-token pricing; Mac audio capture and Opus transport dominate bandwidth, not model context.
- **security:** Call audio and the owner’s replies leave the Mac and relay. The active call identity, language pair, and a visible/on-device listening indicator must be explicit; never keep raw call audio after the turn unless the owner asks. Translation can be wrong, so the owner needs a button interruption path and a short confidence caveat for uncertain phrases.
- **missing:** A Mac system-audio capture and source-selection action that can feed the active call into the relay without recording unrelated applications; A duplex low-latency audio stream distinct from the current press-to-speak request/response turn; A translation session state machine with language detection, glossary, interruption, and echo suppression; A relay-to-pendant audio channel that can interleave translated speech with the owner’s normal assistant reply

### "“Make this a handoff: I’ll start explaining on the pendant, then put the full context and the next step on my Mac so I can continue there without repeating myself.”"
- **useful because:** The owner can begin a thought while walking and continue at the desk with the exact transcript, unresolved entities, decisions, and proposed next action visible in the right Mac app. This removes the costly failure mode where a useful wearable conversation disappears when the owner reaches the computer.
- **path:** pendant → relay → mac-planner → mac-vision
- **model tier:** Realtime handles the spoken capture and a compact handoff summary; a cheaper background model extracts entities, open questions, and app-specific placement after the turn.
- **latency:** A spoken acknowledgement in under 500 ms; a usable Mac handoff within 3 seconds of the owner releasing the button.
- **cost:** About $0.005–$0.03 per handoff, dominated by transcription and the summary; the stable memory projection should avoid resending the whole history.
- **security:** The handoff may contain private speech and must be scoped to the owner’s selected destination. Show the source transcript and generated action separately so an invented detail cannot silently become a task. Do not place secrets into an app chosen only by inference.
- **missing:** A first-class handoff object tying a voice run to transcript, summary, destination, and acknowledgement; A Mac action that opens or focuses the selected destination and presents the handoff atomically rather than typing fragments into whichever app is frontmost; A pendant command or button gesture to request handoff completion and a durable failure notice if the Mac is asleep

### "“What am I looking at on my Mac right now? Read the important part, explain the error, and tell me the next click.”"
- **useful because:** The owner can ask while standing away from the desk or with hands occupied. The pendant supplies the question and spoken answer; the Mac supplies a fresh screenshot and active-window context; vision identifies the relevant region and the planner can optionally perform the single next reversible action. This is more useful than a generic screen reader because it answers the owner’s question about the current visual state and can recover from an unfamiliar UI.
- **path:** pendant → relay → mac-vision → mac-planner
- **model tier:** Realtime handles the short question and spoken answer. A cheaper vision model handles screenshot OCR/layout grounding; mac-planner is invoked only when the owner explicitly asks to act, not for every question.
- **latency:** Screenshot and concise answer within 2 seconds; an optional next action should return a receipt within 5 seconds.
- **cost:** Approximately $0.01–$0.08 per query depending on screenshot resolution and vision tokens; compressing/cropping to the active window dominates savings.
- **security:** Screenshots can contain passwords, private mail, and unrelated windows. Capture only the frontmost window or an owner-selected region, discard the image after the answer, and redact known credential fields before relay upload. Acting must be separately represented from describing, with an explicit spoken “do it” turn.
- **missing:** A live Mac screenshot/active-window capture endpoint reachable by the relay while the owner is away; A vision-loop result contract that returns grounded regions, OCR text, and uncertainty rather than only free-form prose; A low-latency correlation between the owner’s pendant turn and the exact screenshot timestamp; A way for the pendant to interrupt a long visual explanation and request only the next actionable sentence


## Changes it proposed to its own stack

### `integration` — Build a cross-device 'presence and intent lease' shared by the pendant, relay, Mac planner, and browser harness. A voice turn receives a short-lived lease containing the owner’s explicit target (active call, selected browser tab, named app, or no target), origin timestamp, and cancellation state. Mac/browser actions must report which lease they consumed, and the pendant must be able to cancel it with one press. On reconnect, the relay reconciles leases and emits one truthful outcome instead of replaying stale actions.
- **owner gets:** The owner can say “use this tab” or “stop that” while away from the keyboard and know the action applies to the intended screen—not a later tab or a different app—and that a dropped connection will not cause a stale command to fire hours afterward.
- effort: High: protocol and storage changes in relay, Mac planner, browser command queue, and pendant firmware, plus race-condition tests for sleep, reconnect, and cancellation.  ·  risk: A lease could expire while an action is mid-flight or cancellation could arrive after a mutation. Every action needs a visible consumed/expired/cancelled receipt, and existing undo paths must remain available. Recovery is to surface the uncertain state rather than claim success.
- cost: Low API cost; one small lease record and receipt per turn. Engineering cost is concentrated in concurrency and integration testing.  ·  latency: Adds under 100 ms for lease validation locally; reconnect reconciliation may take seconds and must be spoken as pending rather than hidden.
- security: Improves isolation by binding actions to an explicit target and expiry, but the target metadata itself can reveal app/site usage. Encrypt it in transit and redact it from general logs.
- depends on: A real relay capability manifest so lease consumers can be validated rather than inferred; A Mac/browser acknowledgement route carrying action receipts and target identity; Pendant firmware support for a cancel event without ending or corrupting the current audio session


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities and one cross-stack change: private duplex call translation, pendant-to-Mac visual handoff, question-and-explain current Mac screen, and an expiring presence/intent lease binding pendant, relay, Mac, and browser actions. The highest-value missing capability is the visual screen question path: fresh, privacy-scoped Mac capture correlated to the pendant turn, grounded vision results, and optional planner action. The translation and handoff proposals were accepted but flagged as near existing backlog ideas, so their differentiators are the duplex call audio path and explicit target/context preservation rather than generic translation or session transfer.

**Biggest unknown:** Whether the newly observed /vision-loop/plan route already returns grounded screenshots/regions and whether /ops/voice-runs/latest and /ops/history are sufficient primitives for a real cross-device handoff; no further discovery was available this round.

