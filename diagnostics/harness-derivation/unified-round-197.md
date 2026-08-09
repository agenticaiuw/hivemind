# Harness derivation — unified — round 197

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Why didn't that work, and is it safe to try again?"
- **useful because:** This would be the single most useful recovery experience: instead of making the owner inspect relay jobs, browser state, audio telemetry, and Mac receipts, it speaks one causal diagnosis, distinguishes 'never started' from 'started but failed' from 'completed but not heard', and offers only a replay-safe next step. It uses the pendant as the report surface, the relay as the always-available correlator, the Mac/browser as evidence sources, and never guesses when evidence conflicts.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for correlation and hypothesis generation; realtime only to speak the concise result and collect a yes/no retry decision
- **latency:** Diagnosis within 3 seconds from cached snapshots; a confirmed safe retry may take the existing job latency. Never block the owner on a full model call if deterministic evidence already identifies the failure.
- **cost:** Roughly $0.005-$0.03 per diagnosis depending on whether model synthesis is needed; most cost is a small background reasoning call, not telemetry reads.
- **security:** Redact page contents, tokens, and audio by default. Bind evidence to the original job/session and report uncertainty. A retry must be limited to idempotent or additive steps; unrepeatable or unknown steps require explicit physical approval and must not be silently replayed.
- **missing:** A production correlation record joining pendant turn IDs, relay job IDs, Mac job IDs, browser command IDs, and audio pipeline IDs; A deterministic classifier for never-started/failed/not-heard states and replaySafety-gated retry planning; A spoken retry handoff that invokes the existing physical transaction approval latch for risky work

### "Before I rely on you, check whether you can still reach the accounts and apps I use, and tell me exactly what needs me."
- **useful because:** The agent often fails only when a browser tab has logged out, a bridge is stale, or a Mac permission/session has drifted. A preflight that checks bound tabs and apps without mutating them lets the owner discover that before an urgent request, and names the one human action required instead of producing another opaque timeout.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic checks first; background model only to turn multiple findings into a short prioritized explanation
- **latency:** Under 5 seconds for a named set of apps/sites; cached daily status may answer instantly. No page mutation, login attempt, or form submission during preflight.
- **cost:** Usually below $0.01 per run; browser/Mac probes dominate latency, not model tokens.
- **security:** Probe only explicitly bound tabs/apps, never read page bodies unless the owner names a target, redact account identifiers, and report 'not checked' rather than infer logged-in state. Any repair (opening settings or reauth) requires explicit owner confirmation.
- **missing:** A typed reachability contract for a bound browser tab or Mac app (reachable, session-valid, permission-blocked, stale bridge, unknown); Read-only probes that can distinguish a logged-out page from an offline browser without exposing page content; A compact persisted status with age and evidence receipt, plus owner-confirmed repair links

### "How reliable was the whole pendant system this week, and what one change would improve it most?"
- **useful because:** The owner needs a trend, not another one-off health check: percentage of turns captured, responses heard, relay jobs completed, browser actions that needed repair, and privacy-latch or offline periods. A weekly explanation can identify the dominant user-visible failure and recommend one measured intervention, rather than making the owner debug infrastructure by anecdote.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background model over deterministic weekly aggregates; realtime only when the owner asks for the already-generated summary
- **latency:** Generate during an idle scheduled window in under 60 seconds; answer from the cached report in under 1 second.
- **cost:** About $0.02-$0.10 per weekly report, dominated by one background synthesis call; aggregation should be local and cheap.
- **security:** Aggregate counts and durations by default, not utterance content, page contents, or raw audio. Keep an auditable list of source IDs and retention limits. Do not convert a correlation into a causal claim without labeling it.
- **missing:** A cross-surface time-series schema with turn, audio, relay, Mac, browser, and privacy events sharing a redacted correlation ID; Deterministic reliability metrics with explicit denominators and confidence/unknown buckets; A scheduled report and a one-change recommendation evaluator that can compare before/after measurements

### "Let me set, per app and per kind of data, what may leave my Mac, and prove that a request obeyed it."
- **useful because:** Today privacy is mostly a global latch or an implicit implementation choice. The owner should be able to say that a bank tab may be clicked but its page text, screenshots, and form fields must remain local, while a public tab may be summarized remotely. The pendant can provide a physical override/confirmation, the Mac can enforce the boundary before serialization, and the relay can return a signed policy receipt.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic policy evaluation and redaction; background model only to help translate a natural-language rule into a reviewable policy, never to decide an unlisted exception
- **latency:** Policy decision under 20 ms on the Mac before any data leaves; receipt visible within 1 second. A request that cannot be classified must fail closed rather than wait indefinitely.
- **cost:** Near-zero per request after policy compilation; occasional background translation costs under $0.01 and should require owner review.
- **security:** Policies and receipts must be tamper-evident and scoped to app/tab/session. Default deny for unknown destinations and raw audio, screenshots, secrets, and form values. The relay must receive only redacted metadata. Physical approval should be required for policy changes affecting sensitive apps.
- **missing:** A Mac-side egress enforcement point covering browser results, audio uploads, logs, and model prompts; A typed policy language with app/tab bindings, data classes, destinations, expiry, and deny-by-default semantics; A signed receipt proving what was allowed, redacted, or blocked without storing the blocked payload

### "Is the pendant physically positioned well enough for you to hear me and for me to hear you right now?"
- **useful because:** A healthy codec and relay can still produce a bad conversation when the pendant microphone is covered, the speaker is pointed away, the bridge has the wrong channel, or the owner is wearing it loosely. A short, deliberate fit check would distinguish hardware placement from network/model failure before the owner spends time retrying a conversation.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** deterministic acoustic measurements plus a small background classifier; realtime speech is unnecessary except for one prompted phrase
- **latency:** 15-30 seconds, with immediate local tone/LED guidance and a final result under 2 seconds after the phrase ends
- **cost:** Under $0.01 per check; the cost is a short 24 kHz test exchange and no large model call
- **security:** Use synthetic tones and one discarded spoken calibration phrase; never retain or upload the phrase. Require a deliberate local start, and clearly indicate when the speaker emits test audio. Do not alter normal gain permanently without confirmation.
- **missing:** A calibrated local loopback/echo measurement across the nRF microphone, Opus path, ESP32 bridge, and speaker; A per-device baseline for mic level, clipping, noise floor, channel routing, and round-trip delay; A user-facing verdict that separates fit/occlusion, bridge wiring, codec, and link faults


## Changes it proposed to its own stack

### `hardware` — Add a dedicated, physically obvious privacy control to the production pendant: a normally-open microphone power disconnect (or equivalent hard mute) with a separate two-state indicator that is not multiplexed with recording/reply status. Firmware should read the switch state, refuse to power the mic while open, and emit the existing privacy-latch state when the link returns. Treat the physical state as authoritative across reboot and software faults; do not rely on a server command or the single overloaded LED.
- **owner gets:** The owner can know, by touch and by sight, that the pendant cannot hear him—even if firmware is wedged, LTE is unavailable, or the Mac/relay is compromised. This turns privacy from a software promise into a property he can verify before entering a sensitive room.
- effort: High for a production enclosure revision and low-level board/firmware integration: add a hard mic-rail gate or analog mute, a switch/detent that cannot be triggered accidentally, a dedicated indicator, and manufacturing tests for both switch states. Preserve the current firmware privacy latch as the remote/software companion, not its replacement.  ·  risk: A failed switch or noisy contact could disable intended capture or falsely indicate privacy. Use a pull-up/pull-down with debounce, a power-on self-test, fail-closed behavior for ambiguous states, and a clear degraded indication. A hard mic cutoff cannot stop audio already buffered elsewhere, so firmware must flush volatile capture on entry.
- cost: Roughly $2-$8 in board/enclosure parts at low volume, plus PCB and mechanical NRE; a hard analog gate draws negligible steady-state power, while an indicator may add under a few mA only while being viewed.  ·  latency: Mic cutoff should be electrical within one audio frame and independent of radio or model latency; state reporting can remain asynchronous.
- security: Strongly improves the security boundary by making microphone capture impossible in the latched state. It does not by itself erase previously transmitted audio, so pair it with the existing privacy-convergence receipt and explicit remote-data retention policy.
- depends on: Production pendant electrical and enclosure decisions; A firmware GPIO/ADC input and hard mic mute path; A dedicated privacy indicator distinct from the current single LED; Validation that the audio bridge cannot keep an already-open capture path alive after the gate changes


## What it asked for

_Nothing._
## Its own summary

This round produced three non-duplicate capabilities: (1) a spoken cross-surface failure diagnosis with replay-safe recovery, (2) an owner-facing preflight that checks whether named browser accounts/apps are reachable before relying on them, and (3) a weekly whole-system reliability report that identifies the single highest-impact improvement. The attempted fact-erasure UI and approval-loop wiring collided with existing backlog items, so I did not restate them.

**Biggest unknown:** The remaining blocker is not another model feature: the system still lacks a typed, privacy-preserving correlation contract joining pendant turn IDs to relay jobs, Mac jobs, browser commands, and audio pipeline IDs. Without that, diagnosis and reliability trends can report symptoms but cannot prove which user-visible turn they belong to. I still need that schema plus read-only reachability probes for explicitly bound browser tabs/apps.

