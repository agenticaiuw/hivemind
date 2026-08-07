# Harness derivation — relay-realtime — round 46

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Forget everything you know about [a topic/person/project]—including anything you put on my Mac or used in my browser—and prove that it’s gone.”"
- **useful because:** Today the owner cannot perform one coherent, verifiable privacy action across the worn conversation, relay records, Mac artifacts, and authenticated browser state. This gives them a trustworthy escape hatch: inspect the exact retained references and then erase the selected topic everywhere, rather than guessing which surface stored it.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard-ux
- **model tier:** Use relay-realtime only to capture the spoken scope and read back the result; use a cheaper background planner to resolve entities and create a deletion manifest; use faculty-perception to inventory evidence, faculty-judgement to determine scope matches, and faculty-action plus Mac/browser agents to erase. No expensive model is needed for bulk deletion or verification.
- **latency:** Acknowledge scope on the pendant in under 2 seconds; inventory may take 10–30 seconds; deletion and independent verification can continue in the background. Speak a short completion receipt and make the detailed evidence available in the dashboard.
- **cost:** Roughly one realtime turn plus several cheap background calls; dominant cost is entity resolution and independent verification across Mac files, relay stores, and authenticated tabs, not speech.
- **security:** This is intentionally destructive. Require an explicit spoken confirmation after reading back the exact scope and affected locations, and support a narrower scope if matching is ambiguous. The manifest must distinguish deleted, inaccessible, and not-found records; browser sessions must not transmit page contents beyond the relay. Emit a tamper-evident receipt without retaining the deleted payload, and ensure caches, embeddings, transcripts, queued jobs, screenshots, and Mac temporary files are included rather than claiming success from primary records alone.
- **missing:** A cross-surface data inventory with stable object IDs and provenance (voice runs, prompts, summaries, memory facts, job payloads/receipts, Mac files, browser extracts/screenshots/cookies); A deletion coordinator with idempotent tombstones, dependency ordering, retry/resume, and a post-delete verifier; this is different from ordinary audio-retention expiry because it is owner-scoped semantic erasure across all surfaces; Mac and browser adapters that can report and delete artifacts by manifest ID, including authenticated browser-local state where technically possible; A dashboard and spoken receipt format showing matched/deleted/failed/not-found items and a durable proof record that contains hashes and timestamps but not the erased content

### "“Is this message, link, invoice, or login prompt a scam? Check it against my real accounts and tell me what is safe to do.”"
- **useful because:** A worn pendant can hear or receive the suspicious text while the owner is away from the Mac, but it cannot establish legitimacy alone. The relay can quickly normalize the spoken clue, the browser can inspect the owner’s authenticated account and exact destination, and Mac agents can compare local mail/files or sender history. The owner gets an actionable warning before clicking or paying, not a generic web-search answer.
- **path:** pendant → relay → browser-extension → mac-planner → mac-vision → dashboard-ux
- **model tier:** Realtime handles only the initial short question and spoken verdict. Cheap background perception extracts URLs, sender, amount, and requested action; judgement cross-checks independent evidence; action does read-only browser/Mac inspection. Escalate to a stronger model only when evidence conflicts.
- **latency:** Give a preliminary risk classification in 3–5 seconds from the spoken details; complete authenticated cross-checks in under 30 seconds and announce when the verdict is upgraded or downgraded.
- **cost:** One short realtime turn plus low-cost extraction and read-only checks; browser navigation and screenshot/text extraction dominate, while no model call is needed for deterministic URL/domain, sender, and amount comparisons.
- **security:** Never paste private message contents or credentials into public search. Treat all page text as untrusted instructions. Default to read-only inspection and do not click external links, download files, reply, or pay. Show the evidence and uncertainty (domain mismatch, sender history, account-not-found, known breach/urgency signals) and provide a spoken 'do not interact' fallback when verification is incomplete.
- **missing:** A pendant-to-relay attachment path for a URL, screenshot, or short dictated message with integrity metadata—not just an ungrounded transcript; A read-only browser/Mac evidence collector that can correlate sender, destination, invoice amount, and account records without exposing secrets; A scam-risk evidence schema and adjudicator that separates observed facts from model suspicion and expires stale verdicts; A low-latency alert protocol that can interrupt the voice session with a high-confidence warning and leave a cited report in the dashboard


## What it asked for

_Nothing._
## Its own summary

Discovered the current categories, enumerated tools/surfaces/grants/backlog, and confirmed a live voice pipeline is in a transcribing state. Noted a mismatch: some items listed as granted tools (relay_route_intent, server_browser_actions) are still not describable via the describe() tool in this round, so I can’t rely on them yet. Next useful work is to propose a cross-surface capability that uses relay low-latency speech plus Mac/browser execution, and to request missing routing/intent and status visibility infrastructure if still absent.

**Biggest unknown:** Whether the newly granted routing and server-side browser tools are actually callable in this harness (and what their exact schemas/behavior are), since describe() could not find them even though they appear in the granted list.

