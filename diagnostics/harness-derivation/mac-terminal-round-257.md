# Harness derivation — mac-terminal — round 257

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live audio hardware limits** — Current prototype captures at 15,625 Hz, uplinks Opus at 16 kHz/16 kbps, decodes playback at 24 kHz in 60 ms frames, and simultaneous encode/decode uses about 87% of one nRF9160 core. ESP32 bridge resamples 31,250 Hz I2S to 44.1 kHz SBC A2DP and has tight RAM.
  - evidence: get_hardware_spec(audio), get_hardware_spec(bridge), get_hardware_spec(pendant) this round

## Capabilities it proposed

### "“Let me have a natural conversation through the pendant while the Mac is doing things, with full-bandwidth voice and no dead air.”"
- **useful because:** This is the single most useful missing experience: the owner can speak normally while walking around the Mac, hear a response at 24 kHz rather than a telephone-quality clip, interrupt a long answer, and continue after a brief USB/LTE stall. It makes the separate chips, Mac, relay, and wearable feel like one instrument instead of four demos.
- **path:** pendant → relay → mac-planner → mac-bridge → dashboard
- **model tier:** Realtime model only for turn-taking and interruption; a cheaper background model handles transcript cleanup and durable turn summaries.
- **latency:** First audio under 700 ms from the final voiced frame; 24 kHz frames paced in real time; interruption takes effect within 150 ms; reconnect resumes from a turn cursor rather than replaying stale audio.
- **cost:** Realtime audio dominates, roughly 1–3 cents per short turn depending on provider; background summaries are fractions of a cent. Bandwidth and ESP32 codec work dominate engineering, not API cost.
- **security:** Raw microphone audio leaves the pendant only for the active turn and should be discarded after the turn unless the owner explicitly asks for a transcript. Mac actions remain attributable to a turn ID; no ambient microphone mode. Require explicit confirmation for destructive actions.
- **missing:** A tested 24 kHz superwideband codec/packet path across nRF9160 ↔ relay ↔ Mac audio bridge ↔ pendant speaker; A single turn-cursor protocol shared by audio_link_truth_and_recovery and the relay audio pipeline; Actual USB serial bench harness implementation; the granted serial diagnostic schema is unresolved in the live inventory; Jitter-buffer and interruption tests with the ESP32 bridge

### "“If my Mac restarts or the link drops, finish the safe parts of what I asked and tell me exactly what did and did not happen when I press the pendant.”"
- **useful because:** Today a job can remain marked processing forever, cancellation cannot stop a running shell, and the durable ledger is not joined to the job or automatically resumed. The owner should never wonder whether a command ran twice, died halfway through, or is still running. This turns the pendant into a trustworthy continuity control rather than a remote trigger.
- **path:** pendant → mac-planner → relay → mac-bridge → dashboard
- **model tier:** A cheap deterministic recovery worker reconciles ledgers and retries only idempotent/read-only steps; use the realtime model only to phrase the final spoken explanation.
- **latency:** On Mac startup, reconcile within 5 seconds. On reconnect, pendant receives a truthful state within 1 second and a one-sentence report within 3 seconds. Never replay a non-idempotent step automatically.
- **cost:** Negligible model cost for deterministic reconciliation; at most a short realtime turn when the owner asks for an explanation. Storage is a bounded job/ledger index.
- **security:** Persist only action metadata and redacted outputs; never persist inherited environment variables or secrets. Automatic replay is limited to explicitly idempotent reads and reversible operations; destructive or ambiguous work is reported as paused and requires the owner's confirmation.
- **missing:** Boot-time reconciliation that converts stale processing jobs to interrupted and closes ledgers; A durable jobId ↔ ledgerId join and per-step idempotency key on POST /execute; Real process-group cancellation for run_shell, not only an AbortController between steps; A resume planner that classifies steps as completed, safe-to-retry, or owner-decision; Pendant query/push message carrying the job's compact outcome and age

### "“Read me the four newest things on my Safari Reading List, one at a time, and let me say ‘save this as a note’ or ‘skip’ without touching the Mac.”"
- **useful because:** The owner has repeatedly asked for this and the existing browser path has failed. The browser holds the authenticated Safari session; the relay can keep the queue and the pendant provides hands-free playback and decisions. This is a concrete daily action that no Mac-only or pendant-only node can complete reliably.
- **path:** pendant → relay → browser-extension → mac-planner → mac-bridge → dashboard
- **model tier:** Cheap extraction/summarization for each page; realtime only for spoken control and interruption. Do not send page HTML to the model when the extension can provide title, URL, and selected readable text.
- **latency:** Return the first item within 2 seconds; next/skip/save transitions under 500 ms; persist queue position immediately so a dropped link resumes on the same item without repeating a save.
- **cost:** A few cents for four long-page summaries in the worst case; near zero when title/metadata suffice. Browser extraction and audio transfer dominate latency.
- **security:** Read only the active Safari Reading List and page text the owner requested; never expose cookies or session tokens to relay/model. Saving a note writes to the owner's notes through the Mac and should be announced with the source URL; duplicate-save protection is mandatory.
- **missing:** A Safari-specific Reading List structured extractor in the browser harness (not a generic page snapshot); A relay queue protocol with item IDs, cursor, ack, and exactly-once save semantics; A pendant spoken command vocabulary for next, skip, save-note, pause, and stop; A source-preserving note writer that stores URL/title alongside the summary

### "“When you need my approval for something sensitive on the Mac or in the browser, speak me a short description and a two-word challenge through the pendant; approve it only when I press the button while that exact challenge is active.”"
- **useful because:** Today confirmation is a conversational state that can be confused with a later request, a stale browser page, or an action that changed while waiting. This gives the owner a physical, time-bounded approval channel without requiring them to return to the Mac, while preserving the owner's deliberate confirmation rule for sending, deleting, purchasing, and other high-impact actions.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-bridge → dashboard
- **model tier:** Realtime model speaks the concise explanation and challenge; deterministic code binds the button press to an immutable action digest. No model decides whether a press approves a different action.
- **latency:** Challenge arrives within 1 second of the pending action; a press is accepted only for 30 seconds; approval dispatch begins within 300 ms. If the action changes, the old challenge is invalid immediately.
- **cost:** Negligible incremental model cost because the challenge is two spoken words and a short explanation. Engineering cost is in signed action binding, replay protection, and pendant firmware integration.
- **security:** The relay signs an action digest containing job ID, action type, normalized parameters, expiry, and nonce; the Mac verifies the signed approval before execution. Never treat an arbitrary button press as approval. Reject replayed, expired, offline, or mismatched approvals and speak the rejection. Do not read secrets aloud.
- **missing:** A signed approval-token protocol shared by relay and Mac agent; A pendant button event that carries the displayed challenge nonce rather than only a generic press; An approval-pending state in the action ledger and job receipts; Browser actions must expose the same immutable digest as Mac actions; A compact spoken challenge renderer that avoids homophones

### "“Before you touch the Mac or browser, make a named checkpoint; later, when I say ‘undo the changes from Tuesday’s research,’ restore every reversible change across both surfaces and list anything that cannot be undone.”"
- **useful because:** The current system can undo only a small subset of Mac actions and has no owner-facing cross-surface checkpoint. A named checkpoint would make experimentation safe: browser tabs, downloads, notes, files, volume, and other reversible state can be restored together instead of requiring the owner to remember every change.
- **path:** pendant → relay → mac-planner → browser-extension → mac-bridge → dashboard
- **model tier:** Deterministic snapshot/diff and undo engine; use a cheap model only to map the owner's natural-language checkpoint name to a stored checkpoint. Realtime is unnecessary except for spoken confirmation.
- **latency:** Create a checkpoint in under 2 seconds for metadata and under 10 seconds when file/browser state must be hashed. Preview restoration under 3 seconds; apply reversible changes sequentially with progress on the pendant.
- **cost:** Near-zero model cost. Disk usage is bounded by metadata, hashes, browser state descriptors, and selected small backups; large files should use copy-on-write or explicit owner selection.
- **security:** Never silently delete or overwrite. A restore preview must identify irreversible items, conflict with newer edits, and secrets that were intentionally excluded. Checkpoints are local by default and must not upload file contents or browser cookies.
- **missing:** A cross-surface checkpoint schema with state adapters for Mac actions, browser tabs/downloads, and notes; Inverse operations and pre/post-state capture for more than the current small undo set; Browser tab/session snapshot and restore without copying authentication cookies; Conflict detection when the owner changed a file after the checkpoint; Pendant-readable checkpoint IDs and restore progress

### "“Find the thing I saw last week about [topic], whether it was a Safari page, a downloaded file, or a note, and read me the best match with its original source and the exact next step I left myself.”"
- **useful because:** Today browser history, Downloads, notes, and project context are separate islands. The owner should be able to recover a half-remembered item from the pendant without guessing which surface held it. Source and timestamp make the answer verifiable instead of another plausible model recollection.
- **path:** pendant → relay → browser-extension → mac-planner → mac-bridge → dashboard
- **model tier:** Cheap local/index retrieval first; use a background model to rank and summarize only the top few matches. Realtime handles the spoken query and follow-up clarification, not bulk indexing.
- **latency:** Return candidate titles and dates within 2 seconds; read the selected evidence within 5 seconds. Index updates happen incrementally in the background and never block Mac actions.
- **cost:** Low ongoing cost if indexing and hashing stay local; occasional small summarization calls for selected documents. Storage is bounded by metadata, excerpts, hashes, and source pointers rather than full browser pages.
- **security:** Search stays on the Mac/relay boundary with per-source permissions. Browser cookies and private page bodies never enter the model unless the owner explicitly chooses a result. Every spoken claim includes a source label and confidence; exclude secrets and unrelated private files from ranking.
- **missing:** A unified local index spanning browser provenance, Downloads/files, notes, and project/session records; Stable source pointers that survive browser tab closure and file moves; Incremental change watching with deletion and privacy exclusions; A retrieval response format containing evidence excerpt, source URL/path, timestamp, and owner's next-action metadata; A pendant follow-up protocol for ‘open it,’ ‘save this,’ and ‘that's not it’


## Changes it proposed to its own stack

### `firmware` — Make the 24 kHz path an explicit negotiated audio mode rather than an accidental decode-only feature: advertise capture/playback rates and frame duration at session start, keep the current 16 kHz uplink as compatibility fallback, and add relay/bridge counters for source rate, resample ratio, underruns, decode time, and end-to-end frame age. On the current DK, do not raise capture rate blindly: the microphone is 15,625 Hz and simultaneous Opus encode/decode already consumes about 87% of one core.
- **owner gets:** The owner gets a voice link that is honestly wideband when it is wideband, instead of a 24 kHz label on a narrow or starving path. If the bridge or relay falls back, the pendant can say so and recover without silence or distorted speech.
- effort: Medium-high: protocol negotiation, relay transcoder, ESP32 resampler/queue instrumentation, pendant firmware counters, and a bench test matrix across USB and LTE. The current prototype hardware may require a product audio codec or a faster MCU for true 24 kHz capture.  ·  risk: A bad negotiation could produce mismatched sample rates or increase underruns. Version the capability exchange, retain the 16 kHz fallback, and refuse a mode when measured encode/decode budget is exceeded. Recover by restarting only the audio stream, preserving the turn cursor.
- cost: No per-turn API increase if transcoding stays in the relay. Engineering and test cost is substantial; product hardware may add roughly $5–15 for an audio-capable MCU/codec, with modest additional power draw.  ·  latency: Counters and negotiation add under 20 ms. A larger jitter buffer may add 60–120 ms under poor links; stable USB should remain under the 700 ms first-audio target.
- security: Capability frames contain rates, counters, and turn IDs only. Avoid retaining PCM; encrypt transport as today.
- depends on: POST /pipeline/audio and /pipeline/events must carry negotiated audio metadata; A real host-side USB serial bench reader, since the granted mac_usb_serial_diagnostics schema is still unresolved; Relay opusTranscode.js and ESP32 bridge changes; Audio-link truth/recovery must consume the new counters without inventing completion


## What it asked for

_Nothing._
