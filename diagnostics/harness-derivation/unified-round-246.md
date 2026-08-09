# Harness derivation — unified — round 246

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “recover the failed task,” show me what actually happened across the pendant, relay, Mac, and browser, then safely continue only the steps that can be replayed without duplication; ask me on the pendant for anything ambiguous."
- **useful because:** A dropped link or dead browser currently turns a real-world task into guesswork. This would give the owner one truthful recovery path instead of rerunning actions blindly or hunting through logs.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for correlation and replay classification; realtime only to explain the result in the next conversation
- **latency:** Initial diagnosis under 5 seconds; resume plan under 2 seconds after evidence is available; no action is dispatched until the physical approval latch confirms required steps.
- **cost:** Roughly $0.01–$0.05 per recovery, dominated by background correlation and any planner call; deterministic ledger classification should be near-zero.
- **security:** Never replay unrepeatable or unknown steps. Redact page contents and sensitive parameters from the owner-facing report. Physical approval is required for off-machine, irreversible-write, or uncontained actions; retain the audit trail even if a task is undone.
- **missing:** orchestrator must close ordinary ledgers; relay job lease_until and requeue sweep; production caller that invokes planResume/resumeLedger; relay implementation of approvalHandoff storage and delivery readback; distinct authorization boundary between approval and execution

### "Tell me what needs my attention when I am free: combine queued pendant alerts, unfinished Mac jobs, browser commands awaiting results, and commitments due soon, then let me defer or open one item without losing its evidence."
- **useful because:** Each surface already knows about a different kind of unfinished work, but the owner has no single truthful queue. A bounded attention digest prevents silent failures and avoids interrupting an active conversation.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background deterministic merger and priority rules; realtime only when the owner asks for the digest
- **latency:** Refresh in under 10 seconds on a routine or explicit request; never barge in during active speech; a deferred item must remain visible until resolved or dismissed.
- **cost:** Under $0.01 per refresh if evidence is merged deterministically; an optional planner summary is the dominant cost and should be cached.
- **security:** Expose only opaque identifiers and minimal summaries until the owner opens an item. Do not execute anything from the digest. Preserve source receipts and require existing physical approval for staged actions.
- **missing:** one typed cross-surface attention schema with source, urgency, expiry, and disposition; read/write deferral state durable on relay and Mac; browser result freshness and stale-command reconciliation; a pendant delivery path for owner-requested digest playback

### "Make me a sealed, redacted proof packet for a task: what I asked, what the relay dispatched, what the Mac/browser did, what the pendant physically received, and which parts are still unknown. Let me save or share that packet without exposing secrets."
- **useful because:** Today evidence is split across job receipts, browser results, pipeline records, and device acknowledgements. When something matters—an appointment, purchase, or failed automation—the owner cannot establish a trustworthy boundary between accepted, executed, and physically delivered.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background deterministic assembly and hashing; realtime only to answer the owner’s request and summarize unknowns
- **latency:** Generate a small packet in under 5 seconds for a single job; never block the original action on packet generation.
- **cost:** Usually under $0.01; hashing and redaction are local/deterministic, with model cost only for an optional natural-language summary.
- **security:** Use opaque IDs, hashes, timestamps, and status codes rather than raw page contents, audio, secrets, or form values. Mark missing attestations explicitly instead of inferring success. Sharing requires a second confirmation and should produce a new, scoped export receipt; retain the internal audit record.
- **missing:** common event envelope linking job, browser command, audio artifact, and pendant delivery receipt; signed relay receipt over the assembled event root; redaction and export endpoint with expiry; a real pendant/bridge delivery attestation feed

### "Let me set standing boundaries for you—such as “never send messages or buy anything without my physical approval,” “you may organize files only inside this folder,” and “never expose private browser content”—then show me whenever a request is blocked or escalated because of one of my boundaries."
- **useful because:** The current system classifies individual actions and has one-off approval machinery, but the owner cannot express durable personal boundaries that apply consistently across the relay, Mac, browser, and pendant. This would make the system predictable instead of requiring the owner to remember which dangerous action might slip through.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic policy evaluation on every action; background model only compiles a new spoken policy into a reviewable rule and explains conflicts
- **latency:** Under 20 ms for an already-compiled rule during planning/execution; policy creation can take a few seconds but must remain inactive until reviewed and physically confirmed.
- **cost:** Near-zero per action after compilation; roughly $0.01–$0.05 when a natural-language rule must be translated and tested against representative actions.
- **security:** Policies must default deny on ambiguity, be versioned and tamper-evident, and never be silently weakened by a planner. A policy change requires a physical approval ceremony and shows affected action classes. Sensitive rules stay local where possible; diagnostics expose rule IDs, not private content.
- **missing:** first-class policy schema with scope, effect, precedence, and version; enforcement hook before every Mac/browser/relay action rather than only post-hoc classification; conflict detector and representative dry-run simulator; durable policy storage replicated to relay and Mac; physical approval binding for policy changes; owner-facing policy review and rollback UI

### "Put the system into a temporary guest mode when I hand someone the pendant: let them ask harmless questions, but prevent access to my memory, browser sessions, files, messages, and pending actions; end it with a physical gesture and show me exactly what guest mode exposed."
- **useful because:** A wearable assistant is physically shareable, but today its identity and authority are effectively tied to the owner’s active session. This would let the owner lend or demonstrate it without leaking private context or allowing actions under their identity.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic capability sandbox and redaction; realtime model handles the guest conversation only within the sandbox
- **latency:** Enter/exit under 1 second after the physical gesture; each guest request should be denied or scoped before any Mac/browser action is generated.
- **cost:** Negligible policy overhead; normal realtime conversation cost applies, with no extra model call for enforcement.
- **security:** Guest mode must use a separate ephemeral principal, deny inherited cookies/tokens/files/memory by default, prevent browser navigation into existing sessions, and emit an exposure log. Exit must revoke all guest leases and queued work. Physical exit confirmation is mandatory; link loss should expire the guest session automatically.
- **missing:** ephemeral guest principal and scoped credentials; capability sandbox enforced before relay, Mac, and browser dispatch; memory/context projection that excludes owner data; pendant gesture and durable guest-state indicator; automatic expiry and revocation of guest leases; owner-readable exposure log

### "I lost my pendant—revoke it immediately, show me what data and queued actions are still safe, and transfer only the recoverable items to a replacement pendant after I verify it. Nothing from the old device should regain access if it reconnects later."
- **useful because:** The pendant is an identity-bearing endpoint with offline queues and staged actions, yet there is no owner-facing lost-device workflow. A lost device could retain queued data or reconnect with stale authority, while replacing it risks duplicating or losing work.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** deterministic key revocation, queue reconciliation, and transfer; background model only summarizes recoverable versus discarded items
- **latency:** Revocation must take effect at the relay within seconds; inventory within 5 seconds; replacement transfer may run in the background but must expose per-item receipts.
- **cost:** Low deterministic storage and cryptographic cost; under $0.01 for a summary, with no realtime model requirement.
- **security:** Revoke the old device before displaying sensitive inventory. Use a new device key and owner-held recovery ceremony, not a copied secret. Never transfer raw audio or private context by default; require item-by-item consent for queued material. Mark uncertain delivery states rather than replaying them automatically, and retain revocation audit history.
- **missing:** device identity and key lifecycle service; relay-side revocation list checked on every connection and command; queue reconciliation that distinguishes delivered, pending, and potentially duplicated items; replacement enrollment bound to owner confirmation; secure, scoped transfer protocol with per-item receipts; lost-device dashboard state and pendant-side revoked indicator


## What it asked for

_Nothing._
