# research-manufacturing working log (2026-09-29)

Owner: manufacturing research subagent. Files: `manufacturing.json`, this log. Read-only research, no purchases, sign-ins or form submits. No token telemetry available. Reused 2026-09-23 research (JLCPCB fee structure, UW DI Lab $100/kg nylon-12) and `research-components.md` (nRF chip and battery prices).

## Result
- Development: $4,973.31 (Testing $2,027.84, Subscriptions $1,674.00, Tools $763.47, Prototype enclosures $508.00).
- Manufacturing (36 starts for 30 accepted): $5,668.68 + 5% contingency $283.43 = $5,952.11 = **$198.40 per accepted unit** ($165.34 per start). Under $200, but only barely.
- Grand total $10,925.42 (ask ~$11,000).
- CNC aluminum shell (~$35 each) instead of MJF nylon pushes it to ~$233/accepted unit: cut it.
- Sensitivity: each +$10 on the BOM = +$12 per accepted unit, so the BOM must stay at or below ~$100. Other levers: only activate 30 SIMs, drop spare chargers, keep contingency at 5% because the 6 spare starts already cover yield.
- Cert flag: nRF9160 SiP is pre-certified, but the end product needs its own FCC/PTCRB work (third-party estimates ~$20k PTCRB, $1.5-8k+ FCC). NOT in budget; pilot units must stay internal, confirm with UW compliance.

## Prices seen today (2026-09-29)
- Claude: Pro $20/mo ($17 annual), Max 5x $100, Max 20x "from $100" (claude.com/pricing). Cursor Pro $20, Teams $40, no student discount on page. Copilot: Free $0, Pro $10, Pro+ $39, Max $100; free Pro for verified students. ChatGPT/OpenAI pages returned 403: Plus $20, Go $8, Pro $100/$200 and gpt-realtime-2.1 ($32/$64 per 1M audio tokens; mini $10/$20) come from third-party summaries only (aipricing.guru, marktechpost, forasoft), so actual_price_usd left null.
- ElevenLabs Free/Starter $6/Creator $11 first month/Pro $99. Deepgram Nova-3 $0.0048/min, Aura-2 $0.03/1k chars, Voice Agent $0.075/min, $200 free credit. Hologram $3 SIM, $1/mo, $0.03/MB. 1NCE $14 10-yr flat, SIM $1.
- KiCad free (10.0.6 stable). Altium student license free (terms not shown). Onshape education free signup. Autodesk Fusion page 403: unverified.
- Adafruit: breadboard 239 $5.95; jumpers 758 $3.95 (out of stock); helping hands 291 $6.95; ESD tweezers 421 $3.95; USB tester 4232 $24.95; PPK2 5048 $99.95; magnetic USB cable 5412 $4.95 ($4.46 @10); 3-pin magnetic connector 5360 $5.95; 1200 mAh LiPo 258 $9.95; Hakko FX888DX 1204 out of stock; Quick 861DW and ATEN ST-862D out of stock.
- DigiKey: nRF9160 DK $179.80 (221 stock), nRF9161-DK $158.86, nRF9151-DK $102.43, nRF52840-DK $48.95, PPK2 $107.30, Hakko FX888DX-010BY $133.81, Adafruit 1869 hot air $156.19, SMD291 flux $15.95. SEGGER J-Link EDU Mini $76.00 (edu/NPO only). Pinecil V2 $35.99 retail.
- JLCPCB: PCBA setup economic $8.18 / standard $25.56 single, $51.12 double side; stencil $1.53 / $8.21 / $16.42; SMT $0.0016/joint; manual $0.0164/joint; extended $3.07/feeder (economic), feeder loading $1.53 (standard); X-ray $1.64-$0.082/component. 4-layer board charge $70.60/m2 (100x100 x100 pcs = $106.30). Tariff FAQ: DDP rates changed 2026-03-17. JLC3DP from SLA $0.30, MJF/SLS/FDM $1, SLM $8. JLCCNC from $5, MOQ 1.
- MagSafe ring: totalelement 5-pack $31.99 (54x46mm phone size).

## Not verifiable
Logic analyzer (Saleae price not shown, Mouser timed out), microscope (no price on Andonstar page), bench PSU (US price), multimeter/solder wire/paste (search snippets only), JLCPCB 4-layer small-lot price (needs Gerber upload), enclosure/CNC/casting/strap quotes, custom round battery, fume extractor. All left null with estimates flagged.

## Caveats
- Hot air station: DigiKey $156.19 conflicted with a $349.94 search snippet; DigiKey used.
- Real-time voice cost: token-per-minute figures (600 user / 1,200 assistant tokens) are from third-party sources; x3 context multiplier is an assumption.
- Many tools and enclosure prints may be free at UW ECE labs / DI Lab (`campus_may_cover`); not subtracted.
