# Harness derivation — unified — round 209

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “continue that conversation,” resume the interrupted answer on my pendant from the exact turn boundary, without replaying audio I already heard or losing the action it was waiting on."
- **useful because:** A dropped LTE link or sleeping Mac currently turns a live exchange into a restart. This would make the pendant feel continuous: the relay remembers the last acknowledged audio boundary, the Mac/browser can finish the held work, and the next deliberate button press resumes only the missing portion.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime for the short spoken continuation decision; background tier for reconciliation and transcript stitching.
- **latency:** On reconnect, show a pending LED state within 1 s and speak a one-sentence choice within 2 s; continuation audio begins within 4 s after the owner's press.
- **cost:** Usually one short realtime turn plus background reconciliation, roughly $0.01–$0.04 depending on transcript length; dominant cost is regenerated continuation audio, not state storage.
- **security:** Persist only turn IDs, acknowledged audio sequence ranges, and redacted action receipts by default—not room audio. Never replay a browser mutation automatically; unrepeatable or unknown replaySafety steps remain blocked until physical approval. Owner confirmation is required when the interrupted step was not idempotent.
- **missing:** A durable audio acknowledgment cursor joined to the relay job and workbench context; A transport-independent continuation frame and a pendant-visible pending state over LTE; A real relay lease/requeue sweep for Mac jobs; Orchestrator closeLedger calls so completed plans are not falsely classified as interrupted

### "Read me this private browser page, but only the safe, relevant parts, and tell me exactly where each claim came from; stop immediately if the page changes or exposes a password or payment field."
- **useful because:** The browser can reach sessions the relay cannot, while the pendant is the only interface the owner can use hands-free. This turns that split into a trustworthy reading mode rather than blindly sending page text to a model: bounded extraction, sensitive-field suppression, spoken citations, and change detection make private pages usable while walking or away from the screen.
- **path:** pendant → relay → browser-extension → mac-bridge → dashboard
- **model tier:** Background model for extraction and citation selection; realtime model only for the owner's follow-up question or stop command.
- **latency:** First spoken result within 5 s for a normal page; stop request must suppress further speech within one audio frame locally and cancel browser reads within 1 s.
- **cost:** About $0.005–$0.03 per page depending on extracted text; browser extraction and hashing dominate latency, model tokens dominate cost.
- **security:** The extension must send only an allowlisted semantic slice, never raw passwords, payment values, hidden inputs, cookies, or full page HTML. Bind each citation to tab/session URL, DOM text hash, and capture time. Require explicit owner opt-in per tab and delete the relay slice after the response unless the owner asks to save it.
- **missing:** A browser-side redaction and semantic extraction contract with field-level provenance; A streaming cancel signal from pendant privacy/stop state through relay to browser commands; A signed page-version receipt so a citation cannot silently refer to a later DOM; Owner-visible retention controls for extracted page slices

### "If I long-press privacy, cancel anything you were about to do on my Mac or in my browser, then tell me when every surface is actually quiet."
- **useful because:** Muting the pendant is not enough if a browser command or Mac job is still queued to send a message, submit a form, or expose page data. This gives the physical privacy gesture a whole-system consequence: stop capture/playback, revoke pending work, prevent late browser results, and return one authenticated convergence receipt.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic control and receipt verification; no expensive model call unless the owner asks for an explanation afterward.
- **latency:** Local audio mute and mic stop remain immediate; relay cancellation fan-out starts under 250 ms, with a final spoken/LED result within 3 s or an explicit 'not yet converged' state.
- **cost:** Negligible model cost; a few authenticated control and status requests per latch. Dominant resource is cancelling and reconciling in-flight browser/Mac jobs.
- **security:** The latch must be fail-closed: late results are discarded, queued unrepeatable actions are cancelled rather than retried, and cancellation receipts contain no page contents. A cancellation race must be reported honestly if a remote side effect already committed; do not claim undo where none exists. Require the physical latch, not a spoken command, to initiate it.
- **missing:** A signed cancellation token propagated from pendant to relay, Mac, and browser; Executor hooks that check the token before dispatch and before commit; A durable tombstone preventing late browser results from being surfaced; A typed distinction between cancelled-before-dispatch and already-committed side effects

### "Only tell me a remembered fact when you can show where it came from, when it was last confirmed, and whether it may have gone stale; otherwise ask me instead of guessing."
- **useful because:** The system can currently extract facts invisibly, but the owner cannot distinguish a current fact from an old inference or see the evidence behind it. This gives every spoken memory a freshness and provenance contract: stale personal details become a question, not a confident mistake, while the owner can inspect and remove the exact derived record and its off-device copies.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic provenance, expiry, and redaction checks first; background model only to normalize a fact or explain conflicting evidence.
- **latency:** A simple freshness decision under 300 ms; a provenance-backed answer within 3 s. If evidence lookup is unavailable, say so rather than filling the gap with a model guess.
- **cost:** Low: mostly indexed hashes and timestamps; occasional background extraction costs roughly $0.002–$0.02 per fact update. Evidence retrieval and conflict resolution dominate latency.
- **security:** Store evidence references and redacted capsules, not unrestricted transcripts. Bind each fact to its source scope, extraction model/version, confidence, expiry policy, and deletion lineage. An erase must tombstone the fact, derived projections, and off-machine replicas while preserving unrelated action audit history. Never expose a browser page or private message merely to justify a fact.
- **missing:** A first-class fact record with provenance, freshness/expiry, confidence, and derivation lineage; A read-only owner-facing projection that lists facts in recognizable language before relying on them; Conflict and staleness rules that force a question instead of silent overwriting; A replicated erase workflow with pending/offline status across relay and Mac


## What it asked for

_Nothing._
## Its own summary

Round 209 produced three distinct owner-facing capabilities: (1) exact-turn conversation continuation after a dropped link, without replaying heard audio or blindly rerunning actions; (2) privacy-preserving spoken reading of an authenticated browser page with field redaction, DOM-version citations, and immediate cancellation; (3) a physical privacy-latch dead-man switch that cancels queued Mac/browser work and verifies whole-system quiet. The continuation capability is the single highest-value one: it makes link loss non-catastrophic while respecting replay safety.

**Biggest unknown:** Implementation still needs durable cross-surface audio/turn acknowledgment, real relay job leases, cancellation tokens checked before dispatch/commit, signed page-version provenance, and owner decisions on page-slice retention and what to report when cancellation races an already-committed side effect. I do not need another TCC permission request; Accessibility/Screen Recording remain owner-granted and were already denied.

