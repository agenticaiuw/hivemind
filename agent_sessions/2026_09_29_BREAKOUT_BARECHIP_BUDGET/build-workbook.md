# build-workbook working log (2026-09-29)

- v1: 4-sheet full workbook (Components 150 rows, Manufacturing, Development, Summary). Superseded by owner override; script kept at scratchpad build_workbook_v1_full.py.
- v2 (current): minimal 2-sheet workbook. `build_workbook.py` reads components.json, compute-options.json, manufacturing.json; re-run to refresh. Recalc + PDF render done through Microsoft Excel (no LibreOffice on this Mac); openpyxl formulas checked: 24 formulas, 0 errors.
- Build 07:1x — Components total $4,068.13 (Actual else Estimate x units). Manufacturing total $4,920.51 incl. 5% contingency = $164.02 per device (< $200: pass). Per-device components $79.71 (core bare @qty-100 incl. nRF9151, nRF54LM20B, CSNP1GCR01 SD NAND, TPS22916C x3, + $9 allowance).
- Deviation: added one Manufacturing row "SIM + data plan, magnet, test fixture" ($610) from manufacturing.json so cost is not understated; remove if unwanted (-$20/device).
- Assumptions: "Agentic coding subscriptions" = $180/month bundle x 4 months; "Prototype PCBs" = per-spin fees + 3 populated boards x 3 spins; Speaker/Flash Actual left blank (out of stock).
