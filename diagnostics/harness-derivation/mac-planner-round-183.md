# Harness derivation — mac-planner — round 183

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “approve this” on the pendant, show me exactly what the Mac is about to do, let me confirm with the physical button, and only then carry it out; tell me on the pendant whether it succeeded."
- **useful because:** This makes the wearable a real physical presence key for consequential desktop work. A malicious or stale server plan cannot silently send mail, delete files, or publish a browser form: the owner confirms the exact preflighted action hash on the device, while ordinary low-risk work can remain unattended.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Realtime only for turning the owner's spoken request into a plan; deterministic hashing, challenge/response, preflight comparison, and receipt verification should be firmware/relay code with no model call.
- **latency:** Under 2 seconds from spoken approval to button challenge, under 5 seconds from button press to Mac execution for a short action list.
- **cost:** Under $0.01 per invocation when the request already has a plan; dominant cost is the initial realtime planning turn, not the confirmation handshake.
- **security:** The Mac must execute only the exact action hash that was displayed and confirmed, with nonce, expiry, and replay protection. The pendant should display a compact risk summary rather than sensitive content. A lost pendant must be revocable. Today FULL_CONTROL_MODE has no live gate, so this must be an explicit opt-in policy entry and produce an immutable receipt.
- **missing:** USB serial challenge/response transport between the Mac agent and nRF9160 pendant (the requested mac_serial_exchange capability is still unavailable); firmware support for a nonce-bound confirmation and cancel state using the existing button/LED; relay-side action-hash binding and a policy configuration that the owner explicitly enables; a compact pendant-safe rendering of preflight summaries

### "When I press the bookmark button during a call or while working, make one private “moment card” that joins what the pendant heard in this conversation with the active Mac context (calendar event, app, browser tab, and file), then put a dated follow-up card in my workbench without interrupting me."
- **useful because:** A bookmark is currently just a timestamp. This would turn the only physical gesture the pendant can reliably sense into a durable, searchable anchor: weeks later the owner can recover what “that thing” referred to without remembering which app, meeting, or browser tab was open. It works with the pendant tethered by USB today and does not require opening the microphone on the Mac.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic capture and joins first; use a cheap background model only to produce a short title and action items from the already-authorized transcript/context. Do not invoke the realtime tier for each bookmark.
- **latency:** LED acknowledgement immediately; Mac context card within 3 seconds; title/action-item enrichment within 30 seconds in the background.
- **cost:** About $0.001–$0.01 per card depending on transcript length; the dominant cost is optional background summarization. Metadata-only cards cost essentially nothing.
- **security:** Cards must be private by default, redact message bodies and passwords, and retain only the minimum transcript window around the marker. Browser URLs may contain tokens, so normalize and redact query strings before storage. The card needs an explicit retention period and a delete action that removes relay and Mac copies.
- **missing:** a relay event consumer that correlates offline_moment_bookmark IDs with the active voice transcript and call session; a typed Mac context-at-bookmark endpoint that atomically reads calendar/app/tab/file identity rather than sampling later; URL secret redaction and a durable cross-node card identifier; a workbench search/index view for cards

### "When I latch privacy on the pendant, make the whole hive go private: stop relay transcription, stop Mac/browser observation and queued automation, mute generated playback, and show me one clear private-state indicator; when I unlatch, resume only the explicitly resumable work and report anything that was dropped."
- **useful because:** The owner should not have to trust that muting one microphone silences every other observation path. This is the strongest cross-node safety feature: one local physical action establishes a fail-closed privacy boundary across the pendant, relay, Mac bridge, and authenticated browser, including work already queued for execution.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** No model call for entering or enforcing privacy. A cheap background model may summarize dropped work after privacy ends, but only after the owner requests it.
- **latency:** Local pendant mute and playback stop immediately; relay acknowledgement under 500 ms when connected; Mac/browser cancellation and indicator under 2 seconds. Offline behavior must still be fully private locally.
- **cost:** Negligible per toggle; this is state propagation and cancellation, not inference.
- **security:** Privacy entry must be fail-closed and durable across link loss/reboot. No transcript/audio may be buffered while latched. Existing queued plans need a cancellation policy: abort mutations, preserve only opaque job IDs, and never replay automatically after unlatch. The dashboard must show last-seen state and stale-node warnings so the owner knows if a surface is disconnected.
- **missing:** relay-wide privacy epoch and durable state fan-out to all connected surfaces; Mac bridge and browser handlers that cancel polling/queued jobs and suppress observation while the epoch is active; a privacy-state indicator in the dashboard and a stale-surface watchdog; firmware event plumbing from local_privacy_latch into the relay and USB-tethered Mac path

### "Start this Mac job and let me walk away: keep working through browser and desktop steps, send milestone updates to the pendant, let a button press cancel safely, and when it finishes leave an atomic result folder plus a short spoken receipt—even if the laptop briefly loses the relay."
- **useful because:** Today a plan is either a short immediate action or an opaque delegated job. This would make the hive useful for real multi-minute work such as exporting files, collecting authenticated browser results, or preparing a report: the pendant is the owner's remote progress display and kill switch, while the Mac produces a recoverable artifact instead of a vague success message.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the realtime tier only to interpret the initial request. Use deterministic orchestration for checkpoints, retries, cancellation, and atomic staging; use a cheap background model for the final receipt.
- **latency:** Start acknowledgement under 2 seconds, milestone delivery within 5 seconds of each checkpoint, cancellation acknowledgement under 2 seconds, final receipt within 10 seconds of artifact commit.
- **cost:** About $0.005–$0.03 per job for the final summary, depending on artifact size; desktop/browser execution dominates wall-clock time, not API tokens.
- **security:** Every job needs an idempotency key, bounded allowlisted workbench root, checkpoint receipts, and cancellation semantics that distinguish safely stopped from partially mutated external sites. Never claim success until the transaction receipt exists. Browser session data and file contents must be redacted from pendant speech and dashboard previews.
- **missing:** a durable Mac job runner that can checkpoint and resume across relay loss (mac_workbench_transaction currently stages files but is not a general executor); pendant progress/cancel event protocol over the currently live USB serial link and a relay fan-out route; browser action checkpoints and cancellation hooks for authenticated sessions; a spoken receipt generator that consumes typed receipts rather than raw desktop logs

### "When I ask “what changed while I was away?”, give me one causally ordered account across the pendant, relay, Mac, and browser: what was observed, what was decided, what action ran, which files or web records changed, and links to the exact receipts or before/after evidence."
- **useful because:** Today the owner can get isolated job status or a Mac receipt, but not an accountable explanation of the whole hive's behavior. This would make unattended automation trustworthy: the owner can distinguish an observation from an inference and an attempted action from a committed change, without reconstructing four logs by hand.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic event correlation and hashes first; a cheap background model may turn the verified timeline into a short spoken explanation. Never let the model invent missing evidence.
- **latency:** A recent window should answer in under 5 seconds; a day-long audit under 20 seconds. The pendant gets a concise digest and the dashboard exposes drill-down evidence.
- **cost:** About $0.002–$0.02 per query; indexing and receipt storage dominate, not inference.
- **security:** Use immutable event IDs, monotonic timestamps plus wall-clock uncertainty, content hashes, and explicit “unknown” gaps. Redact message bodies, URL query secrets, and audio by default. The owner must be able to export or delete the audit record, while preserving only the minimum tamper evidence.
- **missing:** a shared cross-node event envelope and causal correlation IDs; before/after snapshots for browser and Mac mutations, not only completion receipts; a relay query that joins pipeline, device, browser, and Mac ledgers; dashboard drill-down and a spoken renderer for verified evidence

### "Before carrying out a request that touches more than one surface, tell me if the sources disagree: for example, a calendar time versus a browser deadline, a downloaded file versus the latest authenticated page, or a draft versus what was actually sent. Ask one precise clarification that cites the conflicting evidence instead of guessing."
- **useful because:** The most dangerous automation failure is a confident action based on stale or contradictory context. A cross-node contradiction check would prevent wrong bookings, wrong attachments, and obsolete browser submissions while keeping routine, consistent requests fast.
- **path:** relay → mac-bridge → browser → dashboard → pendant
- **model tier:** Cheap background model for extracting candidate claims; deterministic timestamps, hashes, and source authority rules decide whether a contradiction exists. Realtime is used only when the owner must answer the clarification immediately.
- **latency:** Under 3 seconds for common calendar/file/browser checks; clarification should reach the pendant in under 1 second once detected.
- **cost:** About $0.003–$0.02 per guarded request; source reads and page parsing dominate.
- **security:** Never transmit full private documents to the model when hashes, metadata, or selected snippets suffice. Treat authenticated web content as untrusted input. Preserve the conflicting evidence and the owner's resolution as a decision record so the same ambiguity is not silently reintroduced.
- **missing:** a typed claim-extraction and contradiction service spanning Calendar/Mail, local files, and authenticated browser sessions; source freshness and authority metadata on context-graph entities; a planner interception point before POST /execute or browser mutation; a compact evidence card and answer path over the pendant

### "Let me say “make this portable” while I am in a meeting or browser session, and create a redacted handoff bundle that another person can open: the relevant files, exact URLs and page titles, decisions and open questions, with provenance and no credentials or unrelated private context."
- **useful because:** The owner currently has to manually collect tabs, files, and notes to hand work to a colleague. This would use the wearable as a context boundary and produce a useful artifact from several otherwise disconnected surfaces, without exposing the whole Mac or browser session.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Cheap background model to summarize only the selected context; deterministic collectors, secret redaction, provenance, and bundle creation must run without the realtime tier.
- **latency:** A first bundle manifest in under 5 seconds; complete bundle in under 30 seconds for ordinary meeting context. The pendant acknowledges capture immediately.
- **cost:** About $0.01–$0.05 per bundle, dominated by summarizing selected text and documents; metadata-only bundles are near-zero inference cost.
- **security:** The owner must explicitly choose recipients or a destination. Strip URL query parameters, cookies, tokens, hidden page content, unrelated files, and private mail. Show a manifest and allow deletion; never upload the bundle by default. Provenance should identify source and capture time without leaking source contents.
- **missing:** a user-selectable context scope bound to the current meeting/browser session; cross-surface collectors that can export references and selected content with secret redaction; a bundle schema with provenance, hashes, and expiration; a dashboard/relay delivery action that requires an explicit destination


## Changes it proposed to its own stack

### `integration` — Ship a live USB pendant bridge in the Mac agent that discovers /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA, exposes typed event/command streams (bookmark, privacy latch, staged-audio acknowledgement, diagnostic fixture, cancel), reconnects safely, and records per-event receipts. Keep it separate from arbitrary shell and make device identity/sequence numbers explicit.
- **owner gets:** The pendant and audio bridge are physically attached today but the Mac cannot yet treat their button presses, privacy state, or diagnostics as first-class events. This turns the hardware from a board on a desk into an immediately testable wearable surface, even before LTE registration.
- effort: Medium: serial framing, reconnect state machine, device discovery, and Mac-agent routes; then small relay fan-out adapters.  ·  risk: Bad reconnect handling could duplicate bookmarks or replay commands. Use monotonic sequence numbers, acknowledgements, and an idempotent event ledger; on uncertainty, report disconnected rather than guessing.
- cost: No API cost; roughly 1–2 engineering weeks. No hardware cost or meaningful power impact while USB tethered.  ·  latency: Local button events should reach the Mac in under 100 ms; relay delivery depends on network. Reconnect recovery should be bounded and visible.
- security: Treat serial input as untrusted until the expected USB VID/PID/device identity and framing key are verified. Do not expose raw audio over the bridge by default; privacy latch and cancellation must be accepted locally even offline.
- depends on: The queued mac_serial_exchange capability or an equivalent typed serial route; Firmware event frames for the already accepted offline_moment_bookmark, local_privacy_latch, offline_audio_delivery_retry, duplex_audio_congestion_guard, and audio_path_diagnostic_fixture skills; A relay event-push adapter and a device identity registry


## What it asked for

_Nothing._
## Its own summary

This round produced four owner-facing directions: a physical pendant approval flow for exact Mac plans, bookmark-to-context moment cards, a fail-closed privacy latch propagated across every surface, and unattended long-running Mac/browser jobs with pendant progress and cancellation. I also proposed the concrete USB integration that makes the physically attached nRF9160 and ESP32 useful before LTE registration. The recorder flagged several as near existing backlog items, so the valuable distinction is the missing cross-node wiring: exact event identity, privacy epochs, checkpointed execution, and physical USB transport—not another standalone feature.

**Biggest unknown:** The biggest blocker remains the live typed USB serial bridge. The chips are connected and testable, but no callable mac_serial_exchange capability or equivalent route is available. I still need that transport (or an orchestrator-provided serial route), plus firmware event framing, before bookmark/privacy/cancel/diagnostic events can leave the pendant reliably. Separately, the Mac lacks a durable checkpointed job runner; mac_workbench_transaction stages artifacts but does not execute or resume arbitrary multi-step browser/desktop plans.

