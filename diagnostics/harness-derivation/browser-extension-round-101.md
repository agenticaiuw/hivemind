# Harness derivation — browser-extension — round 101

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser bridge liveness** — At Round 101, Safari 26.5.2 is no longer registered/online; only offline home-chrome remains, with 9 pending commands. Cached browser sessions point to old tab IDs and should be treated as stale until a Safari heartbeat reconciles them.
  - evidence: GET /browser/status returned online=false, devices=[home-chrome offline], pendingCommands=9; GET /browser/sessions returned old tab IDs 320512/230928/229550 last used hours earlier.

## Capabilities it proposed

### "“I’m looking at a private page in Safari. Read me the important parts through the pendant, but keep the page itself on my Mac.”"
- **useful because:** This gives the owner hands-free access to authenticated dashboards, tickets, medical/financial portals, or documents while walking, without sending raw private page contents to the cloud relay or requiring them to read the screen. It is materially different from a generic browser summary because privacy-preserving locality is part of the contract.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a cheaper local/background text model on the Mac for extraction and compression; use realtime only for the owner’s spoken request and interruption handling; use local macOS speech or a relay TTS fallback for the short audio response.
- **latency:** About 3–8 seconds for an already-open page; under 2 seconds to begin playback after the first extracted section. Longer pages should stream section summaries and allow pause/skip.
- **cost:** Usually near-zero cloud inference if local extraction and macOS speech are used; otherwise roughly one small text summarization request plus short TTS, dominated by audio generation. Raw page text should not be sent to the relay.
- **security:** The browser extension reads content under the owner’s existing login. Extraction, redaction, and summarization must happen on the Mac; only an owner-approved short summary or synthesized audio leaves the device. Never include passwords, payment numbers, tokens, hidden form values, or adjacent tabs by default. Show the source URL/title locally and provide a spoken stop command that immediately ends playback.
- **missing:** A privacy-local browser extraction route that returns bounded page regions to the Mac planner without forwarding raw content to the relay; A local redaction/classification pass for secrets and high-risk fields before audio generation; A streaming Mac-to-pendant audio handoff with cancellation and section-level progress; An explicit browser-tab target selector so “this page” cannot silently resolve to a stale session

### "“Lock my browser now.”"
- **useful because:** If the owner walks away from an unlocked Mac or misplaces the pendant, one spoken command can immediately protect every authenticated Safari tab: stop queued browser work, blur/replace private pages, and optionally sign out selected sites. Today there is no owner-controlled emergency browser lock spanning the pendant, relay, and extension.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Realtime should only authenticate the short command and dispatch it; the relay should perform deterministic routing, not an LLM judgment. The extension and Mac execute a fixed emergency-lock procedure.
- **latency:** Begin within 1 second of the spoken command and complete the local tab-lock operation within 3 seconds. It must work even if ordinary browser jobs are queued or the Mac planner is busy.
- **cost:** Negligible inference and API cost: a short realtime turn plus one relay command. Engineering work dominates; no recurring model spend is needed.
- **security:** Require a locally verified pendant pairing and an optional spoken emergency PIN, with replay protection and a visible local audit receipt. The extension must cancel queued commands, replace or hide page contents without transmitting them, and preserve only metadata needed for recovery. Site logout should be opt-in per site because it can destroy unsaved work; the default lock should stop commands and cover tabs, not submit or mutate forms.
- **missing:** A relay-to-browser emergency command channel independent of the normal planner queue; Extension support for immediate queue cancellation and privacy masking/locking of all windows; A paired-device authentication and replay-resistant emergency token; A local recovery/unlock flow that does not expose page contents to the relay; Per-site policy for mask-only versus logout


## Changes it proposed to its own stack

### `browser-harness` — Add an extension-connectivity lifecycle manager: every browser command gets an expiry/lease and cancellation state; when the bridge goes offline, pending commands are moved to a durable dead-letter queue with reason and no automatic replay of mutations. On the next Safari heartbeat, reconcile device identity and tab/session IDs, mark stale sessions as detached, and emit a compact recovery event so the Mac/relay can tell the owner exactly what was not run. Provide explicit retry of read-only commands and require the caller to re-plan any navigation/form mutation against the newly observed tab.
- **owner gets:** The owner will not get phantom hangs or accidentally replayed clicks/forms after Safari disappears. When the browser returns, private-page work can resume safely with a truthful explanation of what ran, what expired, and what needs redoing.
- effort: Medium: command-store schema/state machine, heartbeat reconciliation, expiry sweep, and session-detach events across browserBridge.js/browserSessions.js plus dashboard visibility.  ·  risk: A command may expire just before the extension returns, requiring a retry; that is safer than duplicate mutations. Recovery is explicit and read-only retries can be idempotent. Existing receipts remain the audit trail.
- cost: Negligible API cost; one small periodic sweep and a few D1/local JSON records per command.  ·  latency: No added latency while online; reconnect performs one reconciliation pass. Expired work returns promptly instead of waiting 45 seconds per command.
- security: Reduces risk of stale-tab actions and replaying sensitive mutations. Dead-letter records must redact typed form contents and obey existing retention.
- depends on: A durable browser job runner/command queue (chg-16bc5dee and chg-14accc01); Browser heartbeat and session persistence routes already present (GET /browser/status, POST /browser/heartbeat, /browser/sessions)


## What it asked for

_Nothing._
