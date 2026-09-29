# Orchestrator log — 2026-09-29

User asked for breakout vs bare-chip pricing, extra component ideas, and a 2-sheet Excel. Prior workbook exists (2026_09_23_ECE_CLUB_BUDGET, $11,500 ask). Asking questions first per user request.

## User answers (2026-09-29)
- Main chip: nRF (nRF9160 SiP, cellular+GPS). ESP32 NOT needed — it was only a BLE stand-in. BLE needs a Nordic companion (nRF52840/nRF5340); Wi-Fi via nRF7002 companion.
- Many parts are test-only / exploratory (e.g. fingerprint may not ship). E-ink + stylus belong to a separate agentic AI study-tool (e-note) project.
- New workbook, totals should fit the email: ~$5k dev/testing + ~$6k manufacturing ≈ $11k.
- Sheet1 needs Estimate column AND Actual price column (live, close to estimate) with links.

## Delegation
- research-components (opus): breakout + bare-chip prices for every component → components.json
- research-manufacturing (sonnet): PCB/PCBA/enclosure/band/tools/subscriptions/tokens + extra component ideas → manufacturing.json
- then build-workbook agent assembles xlsx.

## Extra components — first principles (from owner's kickoff slides)
Value V = Σ f·(T_manual − T_agent)·w − C. Levers → parts: trigger friction (wake-word/VAD chip, VM3011 mic, squeeze), accuracy+own-voice (bone-conduction VPU, acoustic vents), context (ALS/proximity, optional UWB), offline capture (PSRAM), eyes-free feedback (RGB LED driver), privacy (2-pole mute switch, hardwired mic LED, secure element, NFC), energy (load switches), dev tools (PPK2, NanoVNA, Tag-Connect, pogo jig). Sent to research-components.

## Owner correction
No always-on wake word (battery). Removed NDP120 + VM3011. Added solar harvesting (cell + MPPT harvester: BQ25570 / AEM10941 / LTC3105) — goal weeks of battery, ideally never charge.

## research-manufacturing done (149k tokens, 92 tools)
Dev $4,973 / Mfg $5,952 (36 starts) → $198.40 per accepted unit; BOM placeholder $100/start must hold. Cert (FCC/PTCRB) not budgeted — keep pilot internal. Waiting on components.

## On-device commands (owner ask)
Button-gated local small-vocab recognition (apps, features, numbers) — check RAM/compute/energy; re-evaluate MCU choice on value, not incumbency. Delegated research-kws-compute (opus) → kws-compute.md, compute-options.json.

## Knob typing idea (owner Discord 2026-09-25)
A..Z dial, dwell = letter, lexicon decoder. Delegated research-knob-typing (opus): Python simulator of accuracy vs noise/vocab, WPM, on-device memory/compute, absolute-angle sensor pricing → knob-typing.md, knob-sim/, knob-options.json.

## research-components done (223k tokens, 203 tools)
100 rows. Core bare BOM ~$91/device @100 (excl PCB/passives/enclosure). Breakouts ~$2,818 (+$105 bench bare parts). Flags: nRF9160 SICA-R7 obsolete→B1A; W25N02KV/nRF5340 stock outs; Qi2 NDA; NanoVNA-H4 <1.5GHz; 1NCE 500MB too small; solar 2xKXOB25 ~60mW sun. Starting workbook builder now; compute/knob rows merged later.

## research-knob-typing done (133k tokens)
Apps 99.8-100% top1, commands 95-99%, numbers 97-99.7%, 20k words 85-88% (T9 95%). ~13-19 WPM. 83KB flash/6.7KB RAM/≈40ms @20k on M33. TMAG5273 recommended; 5mm encoder too small. Removed .venv from repo folder. Sent to builder.

## Owner decision
Cellular SiP → nRF9151 (replaces obsolete nRF9160-SICA-R7). Told kws-compute (price bare + DK) and builder (mark nRF9160 Replaced, placeholder until real rows).

## Owner: ignore already-bought parts (told builder). Asked about 16GB flash → research-components resumed for SD NAND/eMMC/microSD. Explained VNA + MagSafe (flag: MagSafe magnets vs TMAG5273 hall knob sensor + BMI270). Draft xlsx exists (builder still running).

## research-kws-compute done (229k tokens)
nRF9160/9151 app RAM full (6.2KB free) → local commands on BLE chip. Recommend nRF54LM20B (NPU, 512KB, $4.49@100, 16wk lead) over nRF5340; pair saves ~$7.58/device. Local ~8-12mJ vs BLE 20-30mJ vs LTE-M 1.9-4.6J per command. No PSRAM. Told builder to merge.

## Owner feedback: too many rows/cols
Rebuild to 2 sheets. Components = 5 cols (Name generic e.g. "Processing chip" | Estimate | Units | Link | Actual), only original items. Manufacturing ≤5 cols. Sent override to builder.

## Storage follow-up done (255k tokens total)
16GB not worth it (battery limits capture ~660MB/charge; no 16GB SD NAND in stock). Use SD NAND LGA-8 over SPI, 128MB CSNP1GCR01 $5.81@100 behind TPS22916 switch; eMMC ruled out (no host). Told builder.

## Builder done (166k tokens). Components $4,068.13; Manufacturing $4,920.51 ($164.02/device). Grand $8,988.64 vs $11k ask. Committing session folder.
Tokens (subagents): components 256k, manufacturing 149k, kws 229k, knob 133k, builder 166k. Orchestrator tokens not exposed.
