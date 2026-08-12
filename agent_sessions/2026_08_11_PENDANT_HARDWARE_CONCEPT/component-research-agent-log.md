# Component-research agent log

**2026-08-11 — `/root/component_research`**

- Read repository `AGENTS.md`; claimed only `component-research.md` and this agent log in the active pendant session folder.
- Broadly searched repository hardware records. Located current hardware authority in `docs/hardware/pendant-v2.md`; it supersedes `hardware/design/Design_Package_v1.md` and says it is a specification for build. Located respin details in `docs/hardware/respin-speaker-mute-secure-element.md`; it says the board has not been ordered, fabricated, or built.
- Separated exact design MPNs from generic requirements and retained explicit open items (round battery supplier, pogo part, RGB LED, squeeze sensing, membranes). Did not characterize any specified BOM part as purchased.
- Rejected ESP32 from the visual configuration: repository says it was a legacy Bluetooth-classic/AirPods bridge and v2 selects nRF5340 BLE / phone relay instead. nRF9151 was retained only as an optional DNP cellular footprint.
- Verified relevant package dimensions against primary vendor documentation: Nordic nRF5340/nPM1304, Bosch BMI270, Winbond W25N02K family, ADI MAX98357A, and TI DRV2605L. Added inline Markdown citations in `component-research.md`.
- Produced a dimension-aware exterior/exploded image handoff with a 34 mm × 12.5 mm nominal envelope, Ø32 mm PCB, Ø30 mm × 4.7 mm semi-custom cell, and explicit statement that the 12.5 mm stack is tight and still requires mechanical/DFM validation.
- No source hardware record, tasks file, orchestrator log, or application source was edited. No tests were applicable because this is research documentation only.
