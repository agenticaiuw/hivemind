# Harness derivation — mac-planner — round 265

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-accessibility** — AI Pendant Agent has live Accessibility and Screen Recording permission; synthesized input probe succeeds and UI actions will reach screen. Foreground app is Claude; 14 apps running; 4 browser sessions persisted.
  - evidence: mac_readonly_inspect(operation=running_apps) resolved GET /observe at 2026-08-09T00:57:19Z, accessibility.trusted=true, eventsPost=true, screenRecording=true.

## Capabilities it proposed

### "“When I press the pendant bookmark button, make a reliable ‘come back here’ marker: capture what I was looking at on the Mac, where I was in the browser or document, and the time; later say ‘take me back to that moment’ and reopen the exact context.”"
- **useful because:** A moment bookmark currently records only a local event. The useful interruption workflow is closing the loop: the worn button captures the Mac/browser state while it is still available, and a later spoken request restores it instead of forcing the owner to remember which tab, file, or meeting they abandoned.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → faculty-perception → faculty-action
- **model tier:** Realtime only for the short spoken lookup/confirmation; deterministic Mac/browser capture and restore, with a cheap background model for labeling and deduplication.
- **latency:** Bookmark acknowledgement under 300 ms locally; Mac context receipt within 2 s; spoken restore response under 3 s, with reopening allowed to continue asynchronously.
- **cost:** About $0.01–$0.05 per spoken restore depending on summary length; capture and reopening are local. Storage is a small event plus redacted URL/document identity and optional screenshot hash.
- **security:** Context may contain sensitive document titles, URLs, or screen pixels. Store a redacted semantic receipt by default, encrypt sync, never capture password fields, and make screenshot capture an explicit owner setting. Reopening a URL or file is an external side effect and should be reported before execution under the owner’s eventual policy.
- **missing:** A durable cross-surface context-marker schema joining pendant bookmark IDs to Mac/browser receipts; A semantic browser/document identity read (selected text, document path, scroll position) beyond current tab URL/title; A restore operation that accepts the marker and returns an idempotent Mac job receipt

### "“Use my voice and pendant to complete a browser task safely: inspect the authenticated page, tell me exactly what will change, wait for my spoken confirmation, perform it in the browser, and read back proof of the resulting state.”"
- **useful because:** The browser is the one surface that holds sessions the relay and Mac cannot independently possess. Combining the wearable’s confirmation, relay judgement, browser inspection, and Mac/browser execution turns vague voice requests into auditable, state-verified actions rather than blind clicks.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Realtime for intent extraction and confirmation dialogue; a cheaper structured planner for DOM/state diff and postcondition checks; no model for allowlisted browser primitives.
- **latency:** Initial inspection 2–4 s; confirmation response under 500 ms; action and postcondition receipt under 5 s for ordinary pages. If the page changes, stop and regenerate the preview rather than guessing.
- **cost:** Roughly $0.03–$0.15 per task, dominated by one or two model calls and page-state serialization; browser inspection and receipts are local/relay work.
- **security:** Authenticated page contents and session state must never leave the browser bridge except redacted DOM fields needed for the plan. Confirmation must bind to a hash of the exact preview and target account. Never expose passwords or payment details; destructive, financial, or external-message operations require an explicit confirmation phrase and a durable receipt.
- **missing:** A browser action plan/preview route that returns a normalized state diff and preview hash; A confirmation token bound to that hash and the pendant utterance, not merely a generic approval; A postcondition verifier that compares the resulting page state and emits a human-readable receipt

### "“Run a pendant health check now and tell me whether the microphone, 24 kHz speaker path, codec CPU budget, and USB-connected bridge are actually healthy; if something fails, save a diagnostic bundle I can hand to you.”"
- **useful because:** The hardware is physically attached to this Mac today, but a healthy-looking conversation can hide packet loss, decode overruns, or a bridge fault. One spoken command should turn the existing diagnostic fixture into a repeatable end-to-end verdict instead of requiring firmware logs and ad-hoc bench work.
- **path:** pendant → mac-planner → relay-realtime → faculty-perception → faculty-action
- **model tier:** No expensive realtime reasoning for measurements: deterministic fixture execution and threshold checks; use a cheap model only to turn the numeric receipt into a concise spoken diagnosis.
- **latency:** Begin within 1 s of the request and return a pass/fail summary within 20 s; bundle writing may continue asynchronously, with a durable job receipt.
- **cost:** Negligible model cost (under $0.01); local serial/fixture execution dominates. A bundle is typically under a few MB and contains synthetic audio and counters, never microphone content.
- **security:** The fixture must be synthetic-only and stop immediately on button press. USB serial writes are bench control, not a normal product transport. Redact host paths and identifiers in the uploaded report; require an explicit ‘run health check’ utterance because it occupies the audio path.
- **missing:** A bounded Mac bench runner that can invoke the fixture over the two known USB serial ports and collect framed output with timeouts; A relay endpoint that correlates pendant fixture counters, Mac bridge counters, and acceptance thresholds into one signed receipt; A user-facing spoken/result artifact that distinguishes ‘not run’, ‘failed measurement’, and ‘failed hardware’

### "“If my Mac restarts or the browser bridge disconnects halfway through a task, tell me what was completed, what was not, and offer to resume from the last safe checkpoint without repeating anything.”"
- **useful because:** Long browser and desktop tasks currently span a wearable, relay, authenticated browser sessions, and a Mac that can disappear. Durable, idempotent handoff lets the owner trust overnight or interrupted work instead of wondering whether a retry sent a duplicate message, moved a file twice, or silently stopped.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → faculty-perception → faculty-action
- **model tier:** Cheap background state machine for checkpoint matching and deduplication; realtime only to explain the checkpoint and ask for a resume command over the pendant.
- **latency:** Persist a checkpoint after every externally visible step (under 1 s); on reconnect, reconcile within 5 s and speak a compact status. Resume should begin only after deterministic idempotency checks.
- **cost:** Under $0.02 per resumed task; storage and hashing dominate, not model inference. Receipts should be compact and retained only for the configured job TTL.
- **security:** Checkpoint data can include private URLs, filenames, and account identifiers. Encrypt it, redact values, bind resume to the same authenticated browser session/account, and never infer that a partially sent external message is safe to repeat. Any ambiguous postcondition must stop and be reported.
- **missing:** A cross-surface checkpoint schema with step id, precondition hash, postcondition hash, and idempotency key; A reconnect reconciler that reads Mac workbench handoff and browser command results before issuing a retry; A pendant-facing status/continue command that can distinguish resume, inspect, and abandon

### "“When I am working at my Mac, let the pendant act as a private audio cursor: say ‘read the control under my pointer’, ‘what changed on this screen?’, or ‘follow the next link’, and have it identify the exact UI element and perform only that narrowly described operation without taking over the screen.”"
- **useful because:** Today the owner must either stare at the screen and operate it manually or issue broad computer-use commands. A wearable audio cursor would make dense interfaces, dialogs, and visual changes accessible while preserving the owner’s foreground app and avoiding blind coordinate clicks.
- **path:** pendant → mac-planner → mac-vision → relay-realtime → faculty-perception → faculty-action
- **model tier:** Realtime handles the short utterance; a fast local vision/accessibility model resolves the pointer-relative element and computes a bounded action; use the larger model only when the UI tree and pixels disagree.
- **latency:** Element description in 1.5 s; a requested bounded action in 3 s. Never move focus or pointer merely to inspect; return ‘ambiguous’ instead of guessing.
- **cost:** About $0.01–$0.08 per interaction depending on whether a screenshot is needed; accessibility-tree reads are local and cheap, while occasional pixel understanding dominates.
- **security:** Screen content may contain secrets. Keep raw pixels on the Mac, redact password/financial fields before any relay upload, and bind actions to the element identity plus a screenshot/tree hash so a changed page cannot receive a stale click. The owner must be able to say ‘stop’ on the pendant.
- **missing:** A pointer-relative semantic UI query returning role, label, bounds, state, and stable identity; A Mac vision/accessibility fusion loop that can observe without stealing focus and can target the stable identity; A pendant command protocol for element descriptions, ambiguity, cancellation, and short spoken responses

### "“For anything sensitive, let the Mac prepare the action but require a physical press on my pendant to authorize the exact preview; if the preview changes, expire it and make me confirm again.”"
- **useful because:** A spoken ‘yes’ can be triggered by a loud room, an accidental wake-up, or a model misunderstanding. A deliberate physical press on the device the owner is wearing gives high-impact Mac/browser actions a clear second factor while keeping ordinary reversible work fast.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-judgement → faculty-action
- **model tier:** No large model is needed for authorization. The planner creates a structured preview and cryptographic digest; realtime only explains it and maps the owner’s spoken confirmation to the pending digest.
- **latency:** Preview under 3 s; pendant press acknowledgement under 300 ms; execution starts within 1 s after a valid press. A stale or mismatched digest must fail closed immediately.
- **cost:** Under $0.01 per action beyond existing planning; cryptographic digest, pending state, and button event are inexpensive.
- **security:** Bind a single-use nonce to the exact action list, target URL/file identity, account/session, expiry, and preview hash. Do not treat any generic button press as authorization. Cancellation, timeout, Mac disconnect, or browser DOM change invalidates the nonce; keep an auditable redacted receipt.
- **missing:** A relay-to-pendant single-use authorization nonce and button-event return path; A planner-side digest/preview protocol that survives reconnect without allowing replay; An execution adapter that refuses any action whose preview hash or target state has changed

### "“When the agents disagree about what I meant or what the Mac/browser currently shows, do not guess: tell me the one concrete ambiguity over the pendant, show the competing interpretations on the Mac, and let me resolve it with a short spoken choice.”"
- **useful because:** The system combines perception, judgement, browser sessions, and desktop control, so disagreement is inevitable. Today an owner can receive a confident answer or a failed action without seeing whether the problem was stale UI, ambiguous speech, or a mistaken plan. Exposing disagreement as a compact, actionable question makes the hive trustworthy rather than merely forceful.
- **path:** pendant → relay-realtime → mac-vision → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** A cheap deterministic disagreement detector compares structured identities, confidence, and state hashes; realtime compresses the conflict into one spoken question. Use a larger model only to explain genuinely semantic conflicts.
- **latency:** Detect disagreement within 500 ms of each observation; ask one question within 2 s; resume within 1 s after the owner’s choice. Never emit a long diagnostic monologue during an active task.
- **cost:** Under $0.02 per conflict; most work is local structured comparison, with model cost only for wording.
- **security:** The conflict card must redact sensitive page text and preserve only the minimum competing facts. Bind the owner’s answer to the displayed alternatives and expire it if the underlying screen/browser state changes. Log the decision provenance without storing raw secrets.
- **missing:** A shared typed observation envelope carrying source, timestamp, confidence, target identity, and state hash across perception/planning/action; A conflict arbiter that chooses the smallest disambiguating question and freezes side effects while unresolved; A Mac rendering and pendant speech protocol for two or three alternatives with one-word selection


## What it asked for

_Nothing._
## Its own summary

Fresh discovery completed. The Mac is online with Claude foreground, 14 apps running, four persisted browser sessions, and—critically—AI Pendant Agent now has Accessibility and Screen Recording permission with synthesized input verified. I recorded and broadcast that changed fact. I filed four connective proposals: interruption markers that restore exact Mac/browser context; confirmation-bound browser actions with postcondition proof; an end-to-end synthetic pendant health check; and idempotent resume after Mac/browser interruption. The last three are intentionally ambitious and identify the missing seams rather than pretending existing routes already provide them.

**Biggest unknown:** The live inventory still lacks semantic document/UI identity (selected text, scroll/document position), a browser preview hash bound to confirmation, and a cross-surface checkpoint/reconciliation contract. Those are the highest-leverage missing pieces. I do not need another permission request this round; the previous Accessibility denial is no longer true on the live Mac.

