# Harness derivation — mac-planner — round 29

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio-path-gap** — The pendant currently captures at 15,625 Hz and sends 16 kHz/16 kbps Opus, while playback already decodes 24 kHz/60 ms frames and resamples to a 31,250 Hz I2S wire clock; both encode and decode are CPU-heavy on the nRF9160.
  - evidence: describe(audio): capture 15,625 Hz; uplink Opus 16 kHz/16 kbps; playback Opus 24 kHz/60 ms; encode ~15 ms and decode ~25.4 ms per call, ~87% one core when both run.

## Capabilities it proposed

### "When I say “bookmark this moment,” save what I’m looking at and saying so I can later say “resume that” from the pendant and have the Mac reopen the exact browser/app context and read me the short handoff."
- **useful because:** It turns an interrupted thought into a recoverable working state, not just a note. The pendant supplies the annotation anywhere, the browser supplies authenticated page identity, the Mac supplies app/window state, and the relay makes the card durable and retrievable.
- **path:** pendant → relay → mac-bridge → browser → dashboard-ux
- **model tier:** Use realtime only to capture the short spoken annotation and acknowledge it; use a cheaper background model to normalize the handoff and summarize visible page text. The Mac/browser harness should collect state deterministically rather than asking a model to infer it.
- **latency:** Acknowledge bookmark in under 1 second; persist the card in 2–5 seconds. Resume should speak a one-sentence summary within 2 seconds, then reopen the app/tab asynchronously.
- **cost:** About $0.005–$0.03 per bookmark/resume, dominated by optional page summarization; state capture and reopening are local and essentially free.
- **security:** Authenticated URLs, titles, and annotations may be sensitive. Store a redacted card by default with an encrypted local detail pointer, never upload page bodies unless explicitly requested, and require confirmation before reopening a page that could trigger a mutation. Expire cards and provide delete/export controls.
- **missing:** A typed handoff-card schema with app/window/tab identity, timestamp, annotation, redacted summary, and restoration hints; Browser-extension command to export the active tab's stable identity and restore it by tab/session affinity; Mac read/restore support that preserves the owner's focus and records whether restoration succeeded; Relay storage and pendant commands for listing, selecting, expiring, and deleting cards

### "When I say “leave this here,” preserve a resumable work capsule across my pendant, Mac, and browser: the spoken intent, the exact authenticated tab or app state, relevant local files, and the next safe step. When I later say “pick up where I left off,” restore the context and continue from that checkpoint without repeating my research."
- **useful because:** Today an interruption scatters intent across memory, browser tabs, and Mac windows. A work capsule would let the owner stop anywhere and reliably resume later, including after the Mac or browser has restarted. It is different from a note, page watch, or one-shot automation because it captures and restores a coherent cross-device execution state.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime handles only the spoken leave/resume exchange. A cheaper background model canonicalizes intent and summarizes evidence; deterministic Mac and browser adapters capture and restore state. Use a stronger model only when the next step is ambiguous.
- **latency:** Acknowledge “leave this here” within 1 second and persist a capsule within 5 seconds. Resume should identify the capsule and speak its summary within 2 seconds; restoration may continue asynchronously with progress updates.
- **cost:** Roughly $0.01–$0.06 per capsule, mostly for summarizing local/browser evidence. State capture, hashing, and restoration are local operations.
- **security:** Capsules can contain sensitive authenticated URLs, filenames, and snippets. Keep full evidence encrypted and local where possible, upload only a redacted index, bind each capsule to the originating browser session and Mac account, and automatically expire capsules. Never execute the stored next step merely because it was restored; mutations still follow the owner's existing policy.
- **missing:** A durable, versioned work-capsule protocol shared by relay, Mac, and browser extension; Atomic capture of browser session identity, Mac app/window/file state, spoken intent, and a deterministic checkpoint hash; Restoration adapters that verify the checkpoint before reopening anything and report partial restoration clearly; A pendant command and dashboard UI for naming, listing, expiring, and selecting capsules; Crash-safe checkpoint and lease semantics so two resumptions cannot execute the same pending step twice


## Changes it proposed to its own stack

### `firmware` — Complete the 24 kHz superwideband audio path as a negotiated session format: pendant advertises capture/playback rates and frame timing, relay keeps 24 kHz Opus end-to-end when link quality permits, and falls back to the current 16 kHz uplink with explicit quality telemetry. Add a bounded jitter buffer and packet-loss concealment/FEC profile coordinated with the ESP32 bridge, plus session receipts showing negotiated rate, underruns, and fallback periods.
- **owner gets:** Speech sounds noticeably more natural when the network allows it, while conversations remain intelligible instead of stalling when LTE-M is weak. The owner can tell whether a bad experience came from the pendant, bridge, or network rather than guessing.
- effort: Medium-high: firmware codec/session negotiation, relay transcode bypass and metrics, bridge clock/ring-buffer tuning, and an end-to-end test matrix for rate changes and packet loss.  ·  risk: Clock mismatch or buffer bugs could cause audio glitches or increased latency. Roll back to the existing fixed 16 kHz uplink/24 kHz playback profile on negotiation failure; keep a watchdog that tears down and restarts only the audio stream, not the whole conversation.
- cost: No meaningful per-call API increase when relay avoids transcoding; modest extra LTE bytes for higher-rate uplink when enabled. Firmware/bridge engineering effort; no new hardware required.  ·  latency: Target under 150 ms added buffering; 60 ms frames remain the scheduling unit. Avoiding relay transcoding may reduce processing latency, while FEC adds at most one frame of recovery delay.
- security: Audio remains in the existing transport and retention controls. Telemetry should contain rates and loss counts, not transcript or raw audio; negotiated capabilities must be authenticated to prevent downgrade or injection.
- depends on: A versioned audio-session capability message shared by pendant firmware, relay, and ESP32 bridge; An enabled audio-retention sweeper and per-job deletion controls before storing additional diagnostic artifacts


## What it asked for

_Nothing._
