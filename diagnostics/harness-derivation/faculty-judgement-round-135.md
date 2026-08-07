# Harness derivation — faculty-judgement — round 135

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I tap the pendant and say “save this,” preserve exactly what I was looking at and thinking about: the current Mac app, selected browser tab and page excerpt, a short audio note, and a suggested next action; later say “show me my saves” and let me resume one."
- **useful because:** A fleeting thought becomes a recoverable piece of work instead of a vague note. It uniquely combines the worn microphone/button, private browser session, Mac context, and relay persistence, and is useful even while the pendant is only USB-attached today.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → unified
- **model tier:** Use realtime only to transcribe the tap-and-speak interaction; use a cheaper background model to extract the page excerpt, classify the note, and suggest a next action.
- **latency:** Acknowledge the tap locally in under 150 ms; save an initial record within 3 s; enrich it within 20 s. Playback/resume should begin within 2 s.
- **cost:** About $0.002–$0.01 per save, dominated by transcription and enrichment; browser/Mac reads are local and free.
- **security:** The capture may contain private page text or secrets. Store only the selected excerpt plus URL and a short audio clip, encrypt at rest, give each save a retention setting, and never submit or send anything without confirmation.
- **missing:** A cross-surface bookmark schema joining button/audio timestamp, active Mac app, browser tab, excerpt, and follow-up state; A safe read-only endpoint for active app and selected browser text; A spoken save-list/resume interaction and retention controls

### "When you answer a question using my private browser or Mac, let me say “why?” and hear the exact source chain in one sentence, then open the same tab and highlight the supporting text on my Mac."
- **useful because:** It makes the system trustworthy in the moment: the owner can distinguish a grounded answer from a guess without searching for the source. The pendant supplies the low-friction challenge; the browser session supplies private evidence; the Mac visibly returns to the source.
- **path:** pendant → relay-realtime → browser-extension → mac-vision → unified
- **model tier:** Realtime handles the short spoken “why?” and a small citation response; a cheaper background model normalizes evidence and chooses a stable excerpt/locator.
- **latency:** Respond to “why?” in 2 s with source title and confidence; open/highlight the source within 5 s. If the locator is stale, say so rather than pretending.
- **cost:** Under $0.005 per provenance request; most work is local DOM lookup and cached evidence, not model inference.
- **security:** Never read beyond the evidence used for the answer. Do not expose private URL parameters aloud; redact tokens and secrets from excerpts. Highlighting is reversible and read-only; any page mutation still requires the existing confirmation policy.
- **missing:** Evidence records that survive a turn with URL, tab/session id, timestamp, excerpt hash, and locator; A browser command to reopen and highlight a cited range, with stale-page detection; A spoken provenance formatter that redacts sensitive URLs

### "When my calendar, email, and a logged-in website disagree about a commitment, tell me there is a conflict, name the two competing facts, and ask one precise question on the pendant; after I answer, update the plan and leave an audit trail instead of silently choosing."
- **useful because:** The most dangerous assistant failure is confidently acting on stale or contradictory personal data. This turns disagreement into a ten-second decision for the owner and makes the resulting plan explainable across the private browser, Mac apps, and always-on relay.
- **path:** relay-realtime → pendant → mac-planner → browser-extension → unified
- **model tier:** Use a cheaper background model for periodic reconciliation and conflict clustering; reserve realtime for the one spoken clarification and the final concise answer.
- **latency:** Detect conflicts during scheduled/background scans; interrupt only high-impact conflicts. Once asked, answer within 2 s and persist the owner's clarification within 5 s.
- **cost:** Roughly $0.01–$0.05 per reconciliation, dominated by reading several private sources; clarification itself is pennies.
- **security:** This crosses highly sensitive calendar, mail, and account data. Keep raw evidence local to the Mac/relay, transmit only the minimal conflicting fields, redact unrelated message text, and require explicit confirmation before changing calendars, sending mail, or submitting forms.
- **missing:** A typed cross-source fact/conflict record with source timestamps and authority rules; Read-only Calendar/Mail connectors joined to authenticated browser evidence; A clarification state machine that pauses dependent jobs and records the owner's answer; A spoken interruption policy for urgent versus deferrable conflicts

### "Forget what I just said everywhere: remove the pendant recording, transcript, cached audio, derived notes, browser extracts, and Mac job context, then tell me exactly what was deleted and what could not be reached."
- **useful because:** A real person needs a dependable right to retract a private thought, not merely a delete button on one surface. This would make the wearable safe to use around sensitive work and would expose honest limits when a copy cannot be reached.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Use realtime only to identify the current utterance and confirm scope; use a cheap deterministic deletion worker to enumerate and erase artifacts, with no summarization model required.
- **latency:** Stop further processing locally within 200 ms; produce a deletion receipt within 5 s; continue retrying unreachable surfaces and report them explicitly.
- **cost:** Usually under $0.002 per request; cost is storage enumeration and retries, not model inference.
- **security:** Deletion itself is destructive and must require an explicit confirmation phrase unless the owner configured a narrow automatic scope. Keep an append-only minimal audit receipt containing IDs, timestamps, and deletion status—but never the deleted content. If a browser or Mac surface is offline, do not claim success; retain only an encrypted tombstone and retry policy.
- **missing:** A content-lineage graph linking raw audio, transcripts, summaries, captures, browser extracts, jobs, and derived facts; Authenticated delete endpoints on pendant storage, relay object storage, Mac pipeline/job stores, and browser session caches; A verifiable deletion receipt with unreachable-surface and retry states; A clear policy for backups, logs, and legally/technically undeletable records

### "Put the pendant and Mac into guest mode for the next hour: answer general questions, but do not read my mail, calendar, browser sessions, saved notes, or personal memory, and give me a receipt when private mode is restored."
- **useful because:** The owner can safely use the assistant around another person or while demonstrating it without gambling that a private account or memory will leak into speech. This is a hard boundary across wearable, relay, Mac, and browser—not a prompt telling the model to behave.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** A deterministic policy gate should enforce guest mode; use realtime only for the spoken status and general questions. No model should be allowed to override the gate.
- **latency:** Enter guest mode locally in under 200 ms and acknowledge it before accepting speech; restore private mode only after an explicit owner gesture or phrase and verify each surface within 3 s.
- **cost:** Negligible per invocation; the cost is engineering and verification, not inference.
- **security:** Guest mode must deny private reads at the tool layer, close or quarantine authenticated browser tabs, suppress personal memory/context projections, and prevent queued jobs from speaking private results. Restoration must be fail-closed if any surface cannot confirm its state; expose a visible/audio status and a tamper-resistant event receipt.
- **missing:** A capability-scoped policy token propagated from pendant to relay, Mac, and browser bridge; Tool-layer deny enforcement and session quarantine rather than model-level instructions; A restore handshake with per-surface attestations and a fail-closed timeout; A non-private general-knowledge route usable while personal tools are disabled


## Changes it proposed to its own stack

### `hardware` — Replace the prototype's single LED-only feedback with a small coin haptic motor driven by a spare GPIO/PWM channel, plus a real battery fuel-gauge IC on the currently free I2C bus. Define three local patterns: short pulse for captured note, double pulse for a clarification question, long pulse for urgent alert; report battery percentage and low-power state to the Mac/relay.
- **owner gets:** The owner can notice and control the assistant without looking at a screen or hearing an interruption in public. Reliable battery state prevents the pendant silently dying during an important conversation, and haptics make the cross-device system feel present rather than like a phone app.
- effort: Prototype wiring and firmware: 1–2 weeks; product enclosure/PCB and power tuning: 3–6 weeks. Must reserve GPIO and integrate I2C fuel-gauge driver with suspend/wake behavior.  ·  risk: Motor noise can leak into the microphone, current spikes can brown out the prototype, and poor patterns can become annoying. Isolate mechanically, gate motor duty cycle, test audio during haptics, and retain LED fallback. If gauge fails, report unknown rather than inventing a percentage.
- cost: Approximately $2–$6 in components at volume, plus PCB/enclosure revision; haptic bursts are tens of milliwatts and the gauge is sub-milliwatt, with negligible steady-state draw.  ·  latency: Local haptic acknowledgement under 100 ms; no network latency. Battery telemetry adds only periodic I2C polling.
- security: No new data leaves the device beyond battery/health telemetry; do not encode private content in vibration patterns.
- depends on: A firmware feedback API shared by recording, audio buffering, conflict clarification, and delivery acknowledgement; A relay/Mac health schema that treats battery as measured or unknown; Audio isolation tests on the full-duplex I2S pendant-to-ESP32 path

### `hardware` — Design the wearable around two independent physical controls instead of the current single sw0 button: a recessed, latching microphone privacy switch that electrically disables mic power, and a separate momentary action button. Add a visible mechanical color indicator for mute state. The action button should support tap, double-tap, and hold; the privacy switch must work with the Mac/relay completely disconnected.
- **owner gets:** The owner gets an unmistakable promise that private speech is not being captured, and a reliable cancel/mark/interrupt control that cannot be confused with ending a conversation. This is a human trust feature, not a UI refinement, and it remains usable in a pocket or in public.
- effort: Product PCB and enclosure redesign, GPIO/ADC firmware changes, electrical mic-power gating, and an end-to-end test matrix for every audio state; roughly 4–8 weeks for a defensible prototype.  ·  risk: A hard mic cutoff can create audio pop or leave the relay believing a stream is live; firmware must emit a local mute transition, flush/close the stream, and recover cleanly on unmute. A recessed switch may be hard to operate; test glove and pocket use. Retain the current button as an input fallback on the dev kit.
- cost: Roughly $1–$4 incremental components and a new enclosure/PCB spin; mic-power gating reduces standby draw, while no always-on sensor is added.  ·  latency: Mute is electrical and effectively immediate; action gestures are locally acknowledged without network round trips.
- security: Strongly positive: the owner has a hardware-enforced capture boundary. The relay must reject audio frames while muted and record only a coarse mute/unmute event, never raw audio.
- depends on: Firmware audio state machine with an explicit muted state; Relay protocol carrying authenticated mute transitions and rejecting post-mute frames; Mac UI/voice responses that never imply recording while the physical switch is muted


## What it asked for

_Nothing._
## Its own summary

This round produced four recorded items. The most valuable is a “save this” gesture: pendant tap/audio + active Mac/browser context become a durable, resumable work item. I also proposed spoken provenance (“why?” reopens and highlights the exact private source) and conflict clarification (calendar/mail/browser disagreement becomes one precise pendant question rather than a silent guess). Finally I proposed hardware feedback and battery telemetry, though it was flagged as somewhat close to an existing haptic/fuel-gauge idea, so I would not repeat it. What I still need is not another permission request: I need the cross-surface bookmark/evidence schemas, a read-only active-selection endpoint, stale-safe browser highlight, and conflict authority/clarification semantics. The current accessibility grant remains unavailable; these designs should work through AppleScript, browser bridge, and USB-attached pendant first.

**Biggest unknown:** Whether the Mac/browser surfaces can expose a stable active-tab selection and DOM locator without Accessibility/Screen Recording. If they cannot, contextual saves and provenance must degrade to URL/title plus a timestamped audio note rather than claim exact evidence.

