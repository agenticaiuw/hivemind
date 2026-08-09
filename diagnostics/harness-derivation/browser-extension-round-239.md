# Harness derivation — browser-extension — round 239

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser availability** — Safari 26.5.2 is online with 5 tabs and the Mac bridge is online; browser work is no longer blocked by zero tabs. The browser-specific wrapper remains resolver-ambiguous, but browser_run_actions is the canonical product tool schema.
  - evidence: discover(devices) returned Safari on MacIntel · Safari · 5 tab(s) · online and home-macbook-bridge online; describe(browser_run_actions) lists browser_list_tabs/browser_snapshot/browser_read_page and related actions.

## Capabilities it proposed

### "“What are the four newest things in my Safari Reading List, and give me a one-sentence reason to read each?”"
- **useful because:** This is an explicitly repeated owner request that currently fails. It uses the one surface with the owner's Safari state, then turns a private reading queue into a short, playable answer without exposing the whole page collection to the pendant.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use the cheap background model to rank and summarize four extracted titles; use realtime only to answer the spoken request and stream the final four sentences.
- **latency:** Under 15 seconds end to end; browser UI extraction dominates (5–10 s), summarization 2–4 s, then normal pendant playback.
- **cost:** About $0.01–$0.04 per request; model tokens dominate, while Safari extraction is local.
- **security:** Reading List titles and URLs are private. The extension should extract only title, URL, and visible snippet, never cookies or full page bodies; do not persist the list. Stop before opening links unless asked. The owner has already allowed browser reads and clicks.
- **missing:** A browser-extension action that opens Safari's Reading List/sidebar (or reads its backing UI) and returns a bounded list of title/URL/snippet records; A stable structured browser_list_reading_queue result schema; A voice intent mapping for 'Reading List' and a four-item summarizer

### "“Find deadlines on the authenticated page I’m looking at, show me the proposed reminders, and create them only after I say yes.”"
- **useful because:** It bridges the browser's private session to a durable Mac action: deadlines trapped behind a login become reminders the owner can act on, while the owner still sees a compact proposal before anything is created.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a background model to extract candidate dates and normalize them; use realtime only for the spoken confirmation exchange. The Mac tier creates reminders after explicit approval.
- **latency:** Extract and propose within 12 seconds; confirmation and reminder creation should complete within 3 seconds after 'yes'.
- **cost:** About $0.01–$0.03 per page; extraction and date normalization dominate model usage.
- **security:** The page may contain unrelated private data. Extract only deadline text, title, date, timezone, and source URL; do not save page text. Never create reminders from an ambiguous date or without the owner's explicit spoken approval. Preserve provenance so each reminder can be traced back and deleted.
- **missing:** A browser action returning bounded candidate deadline records rather than generic page text; A date/time normalization and ambiguity report (especially timezone and recurring deadlines); A compact approval transaction linking proposed records to Mac reminder creation and undo

### "“Keep a private, temporary understanding of the page I’m viewing so I can ask follow-up questions from the pendant for the next hour—even after I navigate around—and then discard it automatically.”"
- **useful because:** Today a browser read is effectively a one-shot extraction. This would let the owner investigate a logged-in dashboard, policy, or document conversationally while walking away from the Mac, without permanently storing the page or making the owner repeat context after every navigation.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a background model to build a compact, page-grounded evidence index when the tab is captured; use realtime only for the owner’s follow-up questions. Do not resend the whole page on every turn.
- **latency:** Initial capture under 10 seconds; follow-up answers under 3 seconds when grounded in the temporary index.
- **cost:** Roughly $0.02–$0.08 per captured page session, dominated by the initial indexing; follow-ups should be inexpensive retrieval plus short generation.
- **security:** The index may contain sensitive authenticated content. Keep it encrypted and local to the Mac where possible, bind it to the Safari tab/origin, expire it after one hour or immediately on request, never include it in general memory, and return 'not in the captured page' rather than infer. The pendant should speak only the selected answer, not the underlying document.
- **missing:** A tab-bound ephemeral context store with strict one-hour expiry and explicit discard; Browser capture that produces bounded evidence chunks with stable section identifiers rather than an unrestricted page dump; A relay route that retrieves only relevant chunks for a follow-up question and exposes source section/URL to the owner; A Safari event or explicit command to invalidate the context when the owner changes account or origin

### "“While I’m looking at this authenticated booking page, tell me whether the proposed time conflicts with my calendar, and if it does, suggest the nearest free alternatives.”"
- **useful because:** It combines information that no single node can reach: Safari has the private booking details while the Mac has the owner’s calendar. The owner gets a decision before committing, rather than manually copying times between systems.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a cheap background model for extracting and normalizing the proposed event; use the Mac calendar integration for deterministic conflict checks. Use realtime only to state the result and alternatives.
- **latency:** Under 8 seconds: page extraction and calendar lookup can run in parallel; spoken answer should begin immediately after both return.
- **cost:** About $0.005–$0.02 per check; calendar and browser calls dominate latency, not model cost.
- **security:** Send only event title, start/end, timezone, and source URL from the page. Read calendar availability without exposing unrelated event titles unless needed. Do not click booking confirmation or modify the calendar. If timezone or duration is ambiguous, ask instead of guessing.
- **missing:** A browser extractor for booking-event fields with timezone and confidence; A calendar free-busy query exposed to mac-planner; A cross-surface correlation request that joins the browser event and calendar availability without persisting page content; A deterministic nearest-alternative algorithm respecting working hours and existing commitments

### "“Who is the person or company on the page I’m viewing, and what relevant context do I already have about them in my Mac notes and calendar?”"
- **useful because:** Safari can see the authenticated page and the Mac can see local notes and calendar, but neither alone can join them. This gives the owner useful context hands-free during research or a meeting without copying names between applications.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Extract only the visible entity name and page title in the browser; use a cheap local search over Notes, calendar, and permitted workspace files; use realtime to synthesize a short answer with citations and uncertainty.
- **latency:** Under 10 seconds, with browser extraction and local search parallelized; answer in one spoken sentence by default.
- **cost:** About $0.005–$0.02 per query; local search is cheap, and model cost is limited to entity resolution and synthesis.
- **security:** Never send the full page or all local notes to the model. Require exact or high-confidence entity matching, label stale context, and say when no match exists. Keep page-derived names ephemeral and do not automatically write them into memory.
- **missing:** A browser action returning the focused heading/selection or visible entity candidates; A privacy-preserving local entity search across Notes, calendar, and workspace files; A join protocol carrying only the entity and provenance between browser and Mac; A spoken answer format that distinguishes page facts from local remembered context


## Changes it proposed to its own stack

### `browser-harness` — Add a browser-side structured extraction mode that runs a declarative selector recipe inside Safari and returns only typed fields plus an evidence capsule (origin, timestamp, field labels, and short hashes), instead of shipping raw DOM/page text through POST /execute. Recipes are supplied per task and expire after one run; the Mac planner can then hand the selected fields to relay-realtime and the pendant.
- **owner gets:** Authenticated tasks become both faster and safer: the owner can ask for a specific status or date and hear exactly that answer, without the AI carrying an entire private page or unrelated account details through the system.
- effort: Medium: extension protocol, recipe validation, field extraction, evidence hashing, and a test harness for Safari pages.  ·  risk: Selectors can drift and produce stale or wrong fields. On mismatch, return 'could not verify' with the URL and timestamp rather than guessing; preserve the current raw-page path as a fallback for explicit debugging.
- cost: Negligible API change; typically lowers token cost because only selected fields cross the model boundary.  ·  latency: Improves latency by avoiding full-page transfer and summarization; extraction remains local and sub-second after page load.
- security: Strongly positive: least-data transfer and no HTML persistence. Recipe origin binding is essential so a selector intended for one site cannot be applied to another.
- depends on: A working browser_* dispatch path through POST /execute; Existing browser provenance and 24-hour browser-finding TTL; An explicit per-origin recipe configuration, initially empty


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities: temporary tab-bound conversational context for private Safari pages; booking-page versus calendar conflict checking with free alternatives; and entity/context lookup joining the current authenticated page to local Notes and Calendar. Each requires a cross-surface join and explicit privacy/expiry behavior, not merely a Mac feature.

**Biggest unknown:** Whether the existing browser and memory routes already contain enough undocumented connective behavior to implement any of these without new protocol work; the browser action resolver was still ambiguous when last tested.

