# Harness derivation — unified — round 102

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio-path constraints** — The current pendant path captures at 15,625 Hz and uploads Opus nominally 16 kHz/16 kbps; playback decodes 24 kHz/60 ms frames then resamples to a 31,250 Hz I2S wire clock. Encode+decode consumes roughly 87% of one nRF9160 core, and LTE-M is half-duplex in practice.
  - evidence: describe(audio) and discover(hardware) live responses

## Capabilities it proposed

### "“If my pendant conversation drops or the audio becomes unusable, keep the same conversation alive on the best available surface, tell me exactly what changed, and bring it back to the pendant when the link recovers.”"
- **useful because:** Today a worn-device link failure strands the live interaction or silently loses the turn. This would make the pendant, relay, Mac, and authenticated browser one continuous conversation: preserve the session and pending intent, move only the audio interaction to Mac/browser when necessary, and return without making the owner repeat themselves. It is specifically valuable while walking away from Wi‑Fi or during LTE-M half-duplex contention.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime model only for the brief handoff sentence and live conversational turns; a cheaper background model should reconcile the saved transcript, pending action, and recovery receipt.
- **latency:** Detect packet/clock failure locally within 300 ms; announce fallback in under 2 s; resume pendant playback within 3 s of a stable link. Background reconciliation may take 10–30 s.
- **cost:** Low incremental API cost during healthy sessions; roughly one short realtime turn on failure/recovery plus background summarization. Storage and relay polling dominate rather than model tokens.
- **security:** Transcript and pending action state may cross from pendant to Mac/browser. Encrypt the continuity token, bind it to the owner/session, never move browser credentials, and require confirmation again for send/delete/purchase actions after a surface change. Announce every fallback so recording is not surprising.
- **missing:** A transport-neutral conversation continuity/session token with sequence numbers and expiry; A pendant-side link-quality/failure event and bounded local turn buffer; A relay fan-out/handoff coordinator that can route the live session to Mac audio or browser text and back; An end-to-end audio acceptance test across the 24 kHz decode, 31.25 kHz I2S bridge, and LTE-M half-duplex path; An explicit owner policy for whether Mac/browser fallback may speak aloud or must be text-only

### "“Before I commit to this plan, check my calendar, mail, and logged-in reservations together and tell me what conflicts, assumptions are stale, or deadlines I would violate—with the evidence spoken briefly and a reviewable report left on my Mac.”"
- **useful because:** The owner can get isolated calendar, mail, or webpage summaries today, but cannot reliably ask whether a proposed real-world plan is jointly consistent across those private sources. This prevents missed appointments, double-bookings, expired reservations, and promises made against information that changed in another system. It is an evidence-backed decision aid, not an autonomous transaction.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheaper background model to normalize dates, entities, and constraints across sources; reserve realtime for clarifying the owner's plan and delivering the short spoken conflict summary.
- **latency:** A spoken first result in 5–10 seconds for up to three sources; a complete cited report in under 60 seconds. No source mutation or submission.
- **cost:** Moderate per invocation: private-page extraction and Mac reads dominate; normalization can use a low-cost model, with realtime limited to the final concise response. Cache immutable evidence during the session to avoid resending it.
- **security:** Private mail, calendar, and reservation data leave their respective surfaces only as minimum extracted fields. Keep raw page content and credentials local to the browser/Mac, attach source URL and timestamp to every claim, redact unrelated messages, and require confirmation before any suggested change is executed.
- **missing:** A constraint-reconciliation planner that accepts a natural-language proposed plan and emits normalized time, location, obligation, and uncertainty records; A shared evidence schema linking Mac and browser findings with source timestamps, citations, and freshness; A cross-surface report artifact with a spoken summary and a reviewable Mac view; A policy for handling ambiguous dates, time zones, and conflicting source authority


## Changes it proposed to its own stack

### `hardware` — Use the existing ESP32 HUZZAH32 bridge as a dedicated audio coprocessor: move Opus decode and 24 kHz→31.25 kHz resampling off the nRF9160 application core, with a framed, sequence-numbered PCM/Opus stream over the bridge link and a hardware watchdog fallback to the current nRF path. Keep capture and LTE-M control on the nRF9160 until measurements prove an analogous uplink offload is safe.
- **owner gets:** The owner gets fewer dropouts, lower heat and battery drain, and headroom for the 24 kHz superwideband path instead of audio consuming nearly the entire nRF9160 core while LTE-M is active.
- effort: Medium-high: define the inter-chip framing and clock contract, port/test fixed-point libopus on ESP32, add drift/jitter buffering, synchronize firmware versions, and run long LTE-M plus audio soak tests. Prototype first with a compile-time route switch and retain rollback.  ·  risk: Clock drift, bridge resets, or malformed frames could produce silence or loud artifacts. Use bounded buffers, CRC/sequence checks, gain limiting, watchdog mute on invalid audio, and a boot-time capability handshake; recover by reverting to the nRF decoder. This does not solve the currently low 15.625 kHz microphone capture by itself.
- cost: No new hardware if the existing ESP32 has sufficient measured headroom; engineering and power profiling are the main costs. If it is not electrically suitable, a small audio-DSP/codec would be roughly $3–$12 in volume and add tens of mW.  ·  latency: Potentially reduces nRF scheduling contention; adds one inter-chip frame hop, expected under 10 ms if DMA/framing is used. The 60 ms packetization remains the dominant floor.
- security: The bridge becomes part of the trusted audio path. Authenticate firmware/version in the handshake, reject unknown codec parameters, and ensure raw PCM is never persisted by the bridge.
- depends on: A measured bridge transport bandwidth/error rate and clock accuracy; The pending 24 kHz end-to-end acceptance thresholds and production pendant constraints; A fault-injection test for bridge reset, sequence loss, and LTE-M contention

### `dashboard-ux` — Add a decision-conflict canvas rather than a plain briefing: each proposed plan is shown as normalized commitments (time, place, people, deadline), with source cards from Calendar, Mail, and authenticated pages, a freshness timestamp, authority ranking, and explicit unresolved contradictions. Let the owner edit an assumption and rerun reconciliation, but provide no submit/send control in this view.
- **owner gets:** The owner can see why the assistant says a plan is unsafe or uncertain, correct a mistaken assumption without repeating the whole request, and distinguish a true conflict from stale or ambiguous data. This turns private-source checking into something trustworthy enough to use before making commitments.
- effort: Medium: define a compact commitment/evidence model, build the matrix and source citations in the shared SvelteKit dashboard, add rerun/edit endpoints, and test time zones and stale pages.  ·  risk: A visually persuasive but wrong authority ranking could mislead the owner. Show raw supporting snippets, confidence, age, and an 'insufficient evidence' state; never collapse disagreement into a single definitive answer. Recover by discarding the generated canvas, leaving source data untouched.
- cost: Small dashboard/API cost; reruns incur extraction and low-cost reconciliation calls. No new persistent raw-content storage should be required beyond hashes and selected snippets.  ·  latency: Initial render can stream source cards as they arrive; edits trigger a 1–5 second incremental reconciliation rather than a full voice turn.
- security: The canvas must inherit per-source sensitivity and avoid copying unrelated private content into a broadly visible dashboard. Expire cached snippets and require the existing action confirmation gates for any later mutation.
- depends on: The new constraint-reconciliation planner and shared evidence schema; A source-authority and freshness policy for Calendar, Mail, and browser reservations; Authenticated browser inspection and Mac read results with stable citations


## What it asked for

_Nothing._
## Its own summary

I continued discovery and recorded two concrete next steps. The live hardware facts are important: 15,625 Hz capture, Opus uplink at 16 kHz/16 kbps, 24 kHz playback decode resampled to a 31,250 Hz I2S clock, with encode+decode using about 87% of one nRF9160 core; LTE-M is practically half-duplex. I proposed (1) preserving one conversation across pendant→Mac/browser→pendant on link failure, with explicit re-authorization after surface changes, and (2) evaluating the existing ESP32 bridge as an audio coprocessor with rollback. The proposal recorder flagged both as somewhat close to prior backlog, so implementation should consolidate rather than duplicate them.

**Biggest unknown:** I still need authoritative production pendant constraints, the 24 kHz end-to-end acceptance thresholds, bridge transport bandwidth/clock/error measurements, and the owner's privacy policy for Mac/browser audio fallback. The requested workspace-edit, audio-validation, fault-injection, and device skills are not visible as granted this round (granted category reports 0), so I cannot implement or verify the path from here. Accessibility/Screen Recording also remains owner-blocked; AppleScript and browser routes remain usable without it.

