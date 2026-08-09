# Harness derivation — mac-terminal — round 261

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Take the document I’m looking at in Safari, save the finished copy into my active project, verify it’s complete, and tell me what changed.”"
- **useful because:** This is the single most useful cross-surface outcome: the pendant supplies intent, the browser can reach an authenticated page, and the Mac can make a durable local artifact. The system should not merely click Download; it should wait for the file to settle, compare the downloaded artifact with the page's visible title/size or checksum when available, place it in the active project, and speak a truthful result with provenance. No one node can do all three parts today.
- **path:** pendant → relay → browser → mac-planner → dashboard
- **model tier:** Use realtime only to resolve the owner's short spoken intent and announce progress; use a cheaper background model for page-vs-file semantic comparison and project filing. Keep raw page/file bytes on the Mac; send only title, path, hash, and a short diff to the relay.
- **latency:** Acknowledge on the pendant in under 500 ms; browser download and filesystem stabilization normally 2–15 s; semantic verification may take another 2–5 s. If the file remains partial, report waiting rather than claiming success.
- **cost:** About $0.01–$0.04 per invocation, dominated by one small background comparison; browser and Mac work are local.
- **security:** The browser session and downloaded document remain local. The relay receives only a bounded summary. The user must be told the exact destination and source URL; never silently overwrite an existing file—create a versioned name or report the collision.
- **missing:** A typed cross-surface workflow that binds a browser command, resulting ~/Downloads file, active project, and provenance record into one job; A file-stability/checksum verifier and a page-claim-versus-artifact comparator; A durable job join so the pendant can announce the same result after a reconnect

### "“Use what’s open on my Mac to answer me, but keep the page and files here—send only the minimum facts needed to the cloud, and show me what left the machine.”"
- **useful because:** The owner can ask questions about authenticated Safari sessions and local documents without turning the Mac into an invisible cloud upload pipe. The pendant remains conversational, while the Mac extracts only bounded claims, labels their sources, and gives the owner an inspectable egress receipt.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Run extraction and redaction locally with a small model or deterministic selectors. Use realtime only for the final conversational answer from the redacted claim capsule; do not send screenshots, DOM, cookies, or file bytes to the relay.
- **latency:** Acknowledge privacy mode immediately; extract in 1–4 s for a normal page, with a hard upper bound and a clear ‘could not answer locally’ response rather than fallback upload.
- **cost:** Near-zero API cost for selector-based extraction; $0.002–$0.01 if a local/background summarizer is needed. The dominant cost is local CPU, not tokens.
- **security:** Redaction must fail closed: URLs may contain secrets, and claim text can contain personal data. Store an append-only egress manifest with field names, byte counts, hashes, destination, and expiry; the owner can revoke the capsule. Never expose browser cookies or full page text in the manifest.
- **missing:** A local-only execution mode that prevents raw browser/file payloads from entering relay prompts; A claim capsule format with field-level redaction, TTL, and cryptographic hash; A dashboard view and pendant phrase that enumerate exactly what crossed the boundary

### "“Stop the thing you’re doing on my Mac right now.”"
- **useful because:** A pendant is the one surface the owner can reach while the Mac is across the room or showing a destructive UI. The current cancel signal is cooperative between steps and does not stop a running shell, so the spoken command can leave an active process changing files with no truthful local feedback. This is a bounded emergency stop, not a new approval gate.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** No LLM is needed after intent classification. Relay maps the command to the active job; Mac agent sends SIGTERM to the action's process group, waits briefly, then records SIGKILL if needed. Realtime only confirms the resulting state.
- **latency:** Pendant acknowledgement under 300 ms; signal the process within 1 s; settle and report within 3 s. If the process is uninterruptible, report ‘stop requested, still running’ and keep the beacon stale/error pattern.
- **cost:** <$0.001 per invocation; this is process control and receipt storage, not inference.
- **security:** Never kill unrelated user processes: every action must launch in a dedicated process group and retain its pid/pgid. A stop can leave a partially written file or half-submitted browser action; mark outcomes unknown, retain pre/post state, and never auto-replay. Record who/which pendant turn issued the stop.
- **missing:** Process-group launch and pid/pgid capture for run_shell, AppleScript, and computer-use actions; Cancellation propagation from POST /jobs/:jobId/cancel into the actual child process, with exit signal and code in the receipt; A relay intent route that resolves the owner's active job to its Mac job ID; A pendant pattern for stop-requested versus stopped, integrated with truthful_action_status_beacon

### "“When I walk away from my Mac, protect anything private I had open; when I come back, restore exactly where I was.”"
- **useful because:** The pendant is the only device that stays with the owner, so it can act as a physical presence key rather than relying on an idle timeout. A browser session, spoken answer, or document left on screen should not remain exposed to someone who walks past the Mac. Returning should restore the owner’s work, not merely unlock a blank desktop.
- **path:** pendant → mac-planner → browser → relay → dashboard
- **model tier:** Use deterministic local presence and session bookkeeping; no model is needed for lock/unlock. A background model may summarize what was suspended for the owner's return notification, but raw page contents stay local.
- **latency:** Lock or privacy-shutter actions within 2 seconds of confirmed departure, with hysteresis to avoid false triggers. Restore within 3 seconds of a stable return signal; if confidence is insufficient, keep the Mac protected and ask through the pendant.
- **cost:** Negligible API cost. Hardware and OS integration dominate: roughly $5–$20 for a BLE/UWB presence accessory if the pendant radio cannot advertise reliably, plus implementation effort.
- **security:** Presence must not be treated as authentication by itself: require a cryptographic rotating token and invalidate it when the pendant is lost. Do not silently close or submit browser forms. Save only tab IDs, URLs, window geometry, and encrypted local session references; never transmit cookies or page content. The owner needs a visible/audible indication when protection engaged.
- **missing:** A pendant-to-Mac proximity protocol with authenticated rotating advertisements and loss detection; A Mac privacy coordinator that can lock the display, mute pending speech, obscure sensitive windows, and restore their prior state transactionally; Browser-session freeze/resume hooks that preserve tabs without replaying submissions; A recovery path when the pendant battery dies or the owner deliberately leaves it behind

### "“I lost the pendant. Revoke it everywhere now, discard anything it queued, and tell me whether any command was accepted before I revoked it.”"
- **useful because:** A wearable is a bearer of the owner's voice and queued intent. Losing it should not leave an attacker with a still-valid command channel or cause an old offline queue to execute later. The owner needs one authoritative answer spanning relay state, Mac authorization, browser sessions, and the pendant's crash-safe store.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Deterministic revocation and queue accounting; no model required. Realtime can read a short status, while a background reconciler checks any in-flight command receipts after revocation.
- **latency:** Revoke relay and Mac acceptance within 2 seconds while online. Mark the pendant locally revoked on its next contact; show ‘not yet reached’ if it remains offline. Produce an accepted-before-revocation list within 5 seconds.
- **cost:** Under $0.01 per event; cryptographic key rotation and receipt reconciliation are local operations.
- **security:** Revocation must be monotonic and survive relay restart. Queued payloads need per-device encryption and deletion/tombstoning, not merely a UI flag. Browser cookies must be invalidated separately where possible. Never claim deletion of an offline device's storage until it acknowledges a wipe.
- **missing:** Per-pendant asymmetric identity with server-side revocation epoch and key rotation; A relay-side tombstone that rejects old queued intents and reports accepted-versus-rejected sequence numbers; A Mac authorization cache that refuses commands from revoked epochs; A firmware wipe/tombstone command for the OUTBOX and a local revoked indicator

### "“Put the Mac in guest mode for the next hour: keep my work open but make sure nobody else can use my browser sessions or issue pendant commands.”"
- **useful because:** The owner can hand over the laptop without manually closing every authenticated tab or remembering to disable the wearable. Guest mode should preserve the owner's workspace while isolating credentials, browser control, voice history, and queued actions, then restore access only after an explicit owner return.
- **path:** pendant → mac-planner → browser → relay → dashboard
- **model tier:** Deterministic policy and session isolation; no model needed. Use realtime only for the owner's spoken enable/disable command and a short local confirmation.
- **latency:** Enter guest mode in under 3 seconds; deny browser/pendant actions immediately; restore in under 5 seconds after explicit owner return. Expiry should fail closed, not silently restore.
- **cost:** Near-zero inference/API cost. Engineering is mainly OS/browser session isolation and key management.
- **security:** Do not rely on hiding windows. Revoke the relay's ability to dispatch to the Mac, isolate or suspend authenticated browser sessions, mute spoken responses, and prevent guest input from being interpreted as the owner. Keep an encrypted local audit of entry, expiry, and restoration; guest activity must not enter owner memory.
- **missing:** A first-class guest/owner authorization mode shared by relay, Mac agent, and browser extension; Browser controls that suspend authenticated commands without destroying tabs or leaking page data; A pendant-visible guest indicator and owner-only re-entry challenge; Memory and job filters that exclude guest activity from owner context and queued work


## What it asked for

_Nothing._
