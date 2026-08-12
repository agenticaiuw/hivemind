# Memory-domains agent — capability-domain memory rebuild (2026-08-12)

Owner's design: kill generic memory-text prompt stuffing; rebuild memory around
capability domains (email, calendar, files, browser, music, system) where each
domain bundles its tools, its memory accessors, and its clarification rules.
Memories are fetched when a domain's tool is selected, never spliced globally.
Explicit memory tools (memory_lookup / memory_save) on every brain. Selective
capture at run-settle (identities, accounts, connections, repeated task shapes)
with scope 'hive' (fleet-state channel) or 'node' (local). Archive the existing
generic memories + chats, then purge every store.

## Task list (this agent)
1. [x] shared/domains/* — registry + six domain modules (tools+memory+clarify) — 27 tests green
2. [x] shared/domainMemory.js — fact store logic + fleet-state hive block
3. [x] shared/domainCapture.js — run-settle capture heuristic
4. [ ] Remove generic splices: fleetContext memory.text + Recent context,
       orchestrator projection swap, conversationContext memory sections,
       bridge memoryText, pendantConverse spokenMemory writer
5. [ ] Delete dead generic-memory machinery: shared/fleetMemory.js,
       shared/spokenMemory.js, local-agent/contextProjection.js (+tests,
       + store memory-event methods)
6. [ ] Voice: memory tools + fetch-on-tool-selection + clarification
7. [ ] Mac planner: domain memory attach + memory actions + clarification +
       run-settle capture + bridge hive sync (fleet-state merge/write-back)
8. [ ] Browser brain: memory tools + clarify reply + relay domain-memory routes
9. [x] Archive + purge DONE 2026-08-12. Archive: memory-archive-2026-08-12.json
       (8.1 MB). Counts archived: 26 local facts, 57 graph entities (the
       owner's "47" had grown by 10 while agents ran), 38 relations, 100 live
       chat sessions / 169 turns (1100 rows incl. tombstones), relay D1
       1330 entities / 3426 relations / 1118 sessions / 1413 turns / 915 sync
       events / 0 memory events. Purged: local facts.json + context_graph.json
       + pendant-sessions.json reset to empty shapes; D1 DELETEs confirmed
       (3426/1330/1413/1118/915/0 changes). Subagents delegated: relay-voice,
       mac-agent, browser-brain (parallel, disjoint file sets).
10. [ ] Full test suite green; wrangler deploy; safari ship (1.7.10);
        agent restart + /health; commit/push

## Notes
- Hive sync rides FLEET_STATE_KEY ('fleet') under data.domainMemory; the relay
  merges on PUT so the Mac heartbeat cannot clobber relay-written facts, and
  the PUT response carries the merged block back to the Mac (write-back).
- browser_node deliberately lacks state:read, so the extension reaches hive
  memory through dedicated /v1/memory/domains routes with new
  memory:domains:read/write scopes.
- Production D1 counts at start: product_memory_entities=1330, relations=3426,
  product_sessions=1118, product_turns=1413, relay_memory_events=0, jobs=356.
  Local: facts.json 26 facts, context_graph 47 entities, pendant-sessions 100
  live sessions / 169 turns.
