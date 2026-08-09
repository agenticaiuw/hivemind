# Harness derivation — mac-planner — round 184

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What needs my attention right now?” Give me one short spoken answer based on my calendar and unread mail, the authenticated browser tabs I currently have open, and the bookmarks or alerts waiting on my pendant; optionally open the single highest-priority item on the Mac after telling me what it is."
- **useful because:** This is the first genuinely unified answer to the question the owner actually asks when overloaded: it combines obligations, work already open behind browser sessions, and things captured while away from the Mac. No one node can see all three. It should suppress bulk mail and routine tabs, cite the source surface internally, and speak only one sentence by default.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision
- **model tier:** background for periodic ranking and realtime only for the spoken query; use a cheap classifier/ranker first, escalate to realtime only when items conflict.
- **latency:** 3–5 seconds for a spoken answer; browser/session inspection and Calendar/Mail reads in parallel, then one ranking pass.
- **cost:** About $0.01–$0.04 per query; dominated by the final realtime synthesis, not source reads.
- **security:** Mail snippets, tab URLs/titles, and pendant event labels leave their surfaces and reach the relay. Redact bodies by default, never expose secrets or page contents beyond the ranked snippet, and require the owner’s existing confirmation policy before opening or acting on a destructive item.
- **missing:** A relay-side fan-in route that joins mac_read_sources results, browser session/tab inspection, and pendant inbox/bookmark events; A stable browser inspection result with title, task semantics, and redacted URL rather than only raw tab state; A priority ledger that deduplicates the same task across mail, calendar, browser, and pendant

### "“Package this work so I can pick it up tomorrow.” Save a resumable handoff in ~/AI-Pendant-Workspace containing the relevant browser links, a concise markdown summary, source timestamps, and the last pendant bookmark, then leave it open in VS Code and make it available as a spoken alert later."
- **useful because:** The owner currently loses the boundary between a browser session, a spoken thought, and the draft on disk. This creates one durable, human-readable handoff artifact without pretending to serialize private browser cookies. Tomorrow’s self can open the file and understand exactly what was decided and what remains.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** background/cheap model for extracting and formatting; realtime only if the owner asks for an immediate spoken confirmation.
- **latency:** Under 8 seconds after the command; atomic file staging should happen before VS Code opens.
- **cost:** Roughly $0.005–$0.02, mostly one short summarization call; local file staging is negligible.
- **security:** Persist only titles, explicitly selected text, redacted URLs, timestamps, and the owner’s own bookmark—not cookies, tokens, full page bodies, or mail secrets. The workspace path is allowlisted. Opening VS Code is reversible; sending or publishing the handoff is not and must never be implicit.
- **missing:** A relay handoff schema carrying browser session identity without exporting credentials; A browser command to export a redacted tab/task snapshot; A small link from the durable file to the relay receipt and pendant alert record

### "“Test the pendant audio path and file me a bug report if anything is wrong.” Run the no-microphone diagnostic fixture over the USB-connected pendant, collect its counters and the Mac-side relay timestamps, produce a pass/fail report in my workspace, and queue a short spoken result for the pendant."
- **useful because:** This turns the already-shipped diagnostic fixture into something the owner can trust, rather than requiring firmware logs and audio expertise. It catches exactly the framing, CPU, packet-loss, clipping, and preamble regressions that have repeatedly broken the product, while preserving privacy because the fixture contains no microphone content.
- **path:** pendant → mac-planner → relay-realtime
- **model tier:** No expensive model for measurement; use deterministic thresholds and a cheap formatter. Use realtime only to read the result aloud if requested during a call.
- **latency:** One to two minutes for a full fixture, with progress events and an immediate failure summary; report generation under 3 seconds after completion.
- **cost:** Near-zero model cost; only a short optional spoken rendering. USB serial capture and local report generation dominate time.
- **security:** The fixture must be explicitly diagnostic and microphone-free. Store counters and firmware version, not PCM. Do not auto-submit a public issue; create a local report and ask before filing externally.
- **missing:** A resolved mac_serial_exchange capability to arm/read the USB serial fixture on /dev/cu.usbmodem00096003658* (the request is queued and must not be re-asked this round); A relay endpoint that correlates fixture sequence numbers with pipeline events and emits a typed receipt; A deterministic threshold profile versioned alongside scripts/audio-quality-probe.mjs

### "“Use the pendant to approve this.” For a sensitive Mac or authenticated-browser action, show me an exact human-readable summary on the pendant, wait for a deliberate button press, and execute only the single action whose cryptographic challenge I approved."
- **useful because:** The owner gets a physical, glance-free approval surface that cannot be accidentally triggered by a voice misunderstanding or a stale browser tab. It is materially different from a server-side confirmation prompt: the approval is bound to one action digest, one device, and one expiry, so a queued plan cannot be substituted after approval.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** No expensive model for approval; deterministic digesting and signature verification. Use realtime only to explain the action before presenting it.
- **latency:** Under 2 seconds to render the summary and under 3 seconds from button press to dispatch.
- **cost:** Negligible model cost; a few hundred bytes per approval and one signature verification.
- **security:** The pendant must never approve arbitrary hidden payloads. Display a bounded summary and risk class, sign the exact canonical action digest, expire challenges quickly, reject replay, and keep the private key on-device. Destructive actions still require the owner’s existing policy; this is a stronger approval mechanism, not permission to weaken it.
- **missing:** A pendant-keystore/signature firmware skill with a monotonic challenge counter; A relay action-challenge and verification protocol shared by Mac and browser; Mac/browser executors that accept a verified, single-use action token and return a receipt

### "“I lost the pendant—lock everything now.” Press a physical recovery sequence on the pendant, or issue the command from the Mac, to revoke its sessions and stop pending Mac/browser jobs; when it reconnects, require a fresh pairing before it can receive audio, alerts, or action challenges."
- **useful because:** A worn controller is a powerful credential. Today privacy-latch behavior can mute local paths, but it does not provide a unified, cross-node revocation and recovery operation. This gives the owner a fast response to loss, theft, or suspected compromise without hunting through browser and relay dashboards.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Deterministic security workflow; no model required except optional spoken confirmation.
- **latency:** Relay-side revocation under 2 seconds; Mac and browser acknowledgements under 10 seconds, with a durable pending state if offline.
- **cost:** Near-zero model cost; storage is a small device/session revocation record.
- **security:** The recovery command must be authenticated independently of the potentially lost pendant (Mac-local confirmation or a pre-provisioned recovery secret). It must revoke challenges, browser sessions, queued jobs, and audio delivery tokens without deleting owner data. Recovery must be idempotent and auditable.
- **missing:** A cross-node revocation registry for pendant keys, browser sessions, audio tokens, and Mac jobs; A fresh-pairing protocol and recovery code flow; Mac/browser hooks that cancel or quarantine already-queued work and emit signed receipts

### "“Let me interrupt you, but don’t lose the answer.” A button press during spoken playback should stop audio immediately, preserve the exact response position and remaining content, and let me later say “continue that” from the pendant or Mac—even after a dropped link or reboot."
- **useful because:** The owner can reclaim attention without throwing away a useful answer. This is not merely retrying an audio chunk: it preserves semantic playback position, supports interruption and resumption across the pendant, relay, and Mac, and avoids making the owner hear the beginning again.
- **path:** pendant → relay-realtime → mac-planner
- **model tier:** Realtime for the live interruption event; background/durable storage for segment indexing and resume metadata.
- **latency:** Audio mute under 100 ms; durable cursor under 1 second; continuation begins within 3 seconds.
- **cost:** Low: segment metadata is tiny, with optional reuse of already-generated audio. A later continuation may require a short synthesis call.
- **security:** Persist only the response and cursor under the existing session’s retention policy; clear it at session expiry or explicit discard. Do not persist microphone content. A resume request must be bound to the owner’s session and never replay stale private content to a newly paired device.
- **missing:** A playback protocol exposing segment IDs and played-sample/word cursors; Relay persistence for an interruptible-response capsule with expiry and idempotent resume; Pendant firmware handling a stop event locally and Mac/relay reconciliation after reconnect


## What it asked for

_Nothing._
