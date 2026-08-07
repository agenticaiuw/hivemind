# Harness derivation — faculty-judgement — round 115

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Am I ready to leave?” Give me a 20-second departure check from my pendant: next calendar commitment and travel buffer, current weather, battery/connectivity, and any reservation or message that makes leaving urgent. If something is missing, say exactly what—not a generic failure—and never send or change anything."
- **useful because:** This is an on-demand life decision rather than another morning digest: the pendant is available at the door, the Mac can read private calendar/mail and device state, the browser can reach logged-in reservation pages, and the relay can fetch live weather and speak one concise answer. It turns scattered facts into a go/no-go check while preserving the owner's control.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → relay-realtime → pendant
- **model tier:** Realtime model for the short spoken synthesis only; use a cheaper background planner for parallel calendar/mail/browser extraction and cache stable facts, then hand the compact evidence packet to realtime.
- **latency:** Target 5 seconds from button/phrase to first spoken sentence; private-page extraction may take up to 15 seconds, with a partial answer immediately for battery/weather and a follow-up only if the pendant is connected.
- **cost:** About $0.01–$0.04 per invocation, dominated by realtime audio tokens; background extraction and cached weather/calendar normalization should be low-cost. Do not resend full page contents to realtime—send cited fields and freshness only.
- **security:** Calendar, mail, and reservation data remain on the Mac/browser where possible; relay receives only normalized event time, travel window, urgency, and source timestamps. Never expose message bodies aloud by default. No external mutation. If a future version offers navigation, booking, or message actions, require an explicit confirmation phrase and show the exact change.
- **missing:** A durable on-demand departure-check orchestrator that fans out to Mac state, AppleScript-readable Calendar/Mail, authenticated browser tabs, and public weather, then returns a typed evidence packet.; A reliable connected pendant trigger and delivery acknowledgement; the pendant is currently absent/offline.; Owner must reconnect the Browser Bridge for private reservation/account pages; current home-chrome is offline.; A location/travel-time source (Mac location permission or a configured home/destination and public routing provider) with a privacy-preserving coarse-location policy.

### "“Let the pendant quietly tap me when something important is ready—such as a private browser result, a waiting approval, or a time-critical calendar change—and let me press once to hear the short explanation or twice to defer it. I should be able to use this in a meeting or on a noisy street without my phone speaking aloud.”"
- **useful because:** The owner currently has no dependable private, glance-free attention channel: audio is inappropriate in many settings and the single LED is easy to miss. A tactile contract would make the whole hive useful in meetings, transit, and noisy environments while keeping the Mac/browser work invisible to bystanders. The same event can be acknowledged at the body, even when the phone or screen is out of reach.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → relay-realtime
- **model tier:** No realtime model for the haptic decision itself. A cheaper background classifier maps already-structured job/calendar/browser events to a small urgency taxonomy; realtime is used only if the owner presses to ask for the spoken explanation.
- **latency:** Tactile notification within 1 second of an event reaching the relay; one-press explanation begins within 2 seconds when the pendant link is healthy. Deferral must be local and immediate, even during a dropped link.
- **cost:** Negligible model cost for event classification and compact push messages; occasional realtime audio cost only after an explicit press. Hardware prototype roughly $3–$8 in a production BOM for a coin/LRA haptic actuator and driver, plus modest battery impact (well under 1% per day for a few dozen taps).
- **security:** Patterns must not encode sensitive content—only generic classes such as approval, urgent, or ready. Do not vibrate for message bodies or secrets. Acknowledgement and deferral events are private telemetry with short retention. Any approval that causes an external mutation still requires the existing explicit confirmation policy; a double tap means defer, not send.
- **missing:** A pendant hardware revision with a haptic actuator, driver, and mechanical coupling that is perceptible on the wrist/clothing without being audible.; Firmware support for a tiny durable event ring buffer, pattern playback, local one-/two-press handling, and replay suppression across reconnects within the pendant's constrained RAM/flash budget.; A relay push protocol carrying event class, expiry, source, and opaque correlation ID, with idempotent acknowledgement/defer semantics.; A cross-surface event adapter so Mac jobs, browser results, and calendar watchers publish normalized attention events instead of each inventing notifications.; A small owner-facing pattern/quiet-hours setup and a safe default mapping, including a local universal-stop behavior for unwanted taps. 


## Changes it proposed to its own stack

### `integration` — Add a decision-oriented `departure_check` orchestration path rather than routing this through the generic briefing flow. In parallel, query Mac observation/status, AppleScript Calendar/Mail summaries, authenticated browser reservation tabs when available, and public weather; normalize each result into `{claim, source, observedAt, expiresAt, confidence, sensitivity}`; apply a 20-second-departure policy; return complete/partial/blocked sections with a reason and a next retry time. Stream the first safe facts to relay, and persist only the compact packet plus provenance for a resumable follow-up.
- **owner gets:** When standing at the door, the owner gets a useful answer even if one account or the browser is unavailable, instead of waiting or hearing an opaque failure. They can trust which facts are fresh and know exactly what must be checked manually.
- effort: Medium: new fan-out route and schema, Calendar/Mail extraction adapters, weather query, partial-result policy, and relay audio handoff; reuse existing job/receipt and browser result primitives.  ·  risk: Stale or wrongly interpreted event/travel data could cause a missed commitment. Mitigate with explicit timestamps, conservative wording ('I cannot verify'), no inferred travel time without a configured destination, and no action side effects. Recover by retaining the packet and retrying only failed sources.
- cost: Low incremental API cost: parallel cheap extraction plus one short realtime synthesis; no need to transmit raw private page or mail bodies.  ·  latency: Parallel fan-out should reduce wall-clock latency; first safe result in ~2–5 seconds, full result bounded at ~15 seconds, with a partial response if a source times out.
- security: Private data stays on Mac/browser until reduced to sensitivity-labeled fields. Weather query may reveal coarse location; use configured city or coarse region, never exact coordinates by default. Store packet with short TTL.
- depends on: Pendant reconnection and audio delivery acknowledgement; Browser Bridge online for reservation/account checks; A configured coarse location or destination/travel-time provider; Existing typed context/provenance service or equivalent compact evidence schema

### `hardware` — Replace the prototype's single LED-only notification path with a production pendant notification module: a low-power LRA haptic actuator behind the enclosure, a protected driver, and a firmware-visible event queue with one-tap acknowledge/two-tap defer. Keep the LED as a secondary visual cue and make patterns generic (not content-bearing).
- **owner gets:** They can know that an important result or approval is waiting without pulling out a phone, interrupting a conversation, or broadcasting private audio. A tap at the wrist is noticeable but discreet, and local acknowledgement still works when the network briefly drops.
- effort: Medium hardware spin plus firmware driver, enclosure vibration testing, battery characterization, and relay/event integration. Validate patterns across clothing and avoid confusing ordinary movement with a notification.  ·  risk: False or excessive taps could erode trust, and vibration may be uncomfortable or audible on hard surfaces. Bound daily notification volume, add quiet hours and a physical stop gesture, use escalating patterns sparingly, and retain a delivery/ack receipt for recovery after reconnect.
- cost: Approximately $3–$8 incremental production BOM, a small driver footprint, and roughly 0.1–0.5 mAh per tap depending on actuator and pulse; no per-event model cost.  ·  latency: Local queue and playback are sub-100 ms once an event arrives; relay delivery remains network-dependent. A queued event should expire rather than vibrate late.
- security: No message text or secret should be encoded in vibration patterns. Correlation IDs and acknowledgement state should be encrypted and short-lived; an approval gesture must never itself authorize a destructive action.
- depends on: A normalized cross-surface attention-event schema from Mac jobs, browser results, and calendar watchers; Pendant reconnectivity and a reliable relay push/ack channel; Owner-configurable quiet hours and a local universal stop latch


## What it asked for

_Nothing._
## Its own summary

Round 115 produced a new cross-surface capability and implementation change: an on-demand pendant “Am I ready to leave?” departure check that fans out across Mac private data, authenticated browser reservations, live weather, and device state, then speaks a freshness- and provenance-labeled partial or complete answer without taking actions. Current live reality still has home-macbook-bridge online, pendant absent/offline, and home-chrome/browser bridge offline. The owner must reconnect the pendant, re-enable the browser bridge manually for private-page checks, and configure a coarse location or destination/travel-time source. I did not re-request denied TCC grants or already-pending tools.

**Biggest unknown:** Whether the owner has a safe configured travel destination/location source and what their preferred departure lead-time policy is; without that, the system can report calendar times and weather but cannot honestly judge travel readiness.

